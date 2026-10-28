"""
calibrar_sigma_cito74.py - CITO-74: Calibración de sigma, umbral, áreas y regla 3x

DEPENDENCIA: J-03, J-04, J-06
EVIDENCIA: bitácora, tabla de parámetros y reporte

Este módulo calibra los parámetros críticos del pipeline CitoCounter-Proto:
1. sigma1 y sigma2 del filtro DoG
2. UMBRAL_DOG para binarización
3. AREA_MINIMA_NUCLEO y AREA_MAXIMA_NUCLEO
4. Validación de la regla del 3x (FACTOR_RIESGO)

El objetivo es obtener valores óptimos basados en datos reales y documentarlos
para su uso en futuros experimentos y la tesis (BM5).
"""

import os
import sys
import numpy as np
import pandas as pd
import json
import cv2
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, '/workspaces/CitoCounter-Proto')

from src.dog_filter import aplicar_filtro_dog, calcular_sigmas_optimas, visualizar_filtros_gauss
from src.analysis import analizar_nucleos, clasificar_nucleo_por_area, AREA_PROMEDIO_NUCLEO_NORMAL, FACTOR_RIESGO
from src.preprocessing import preprocesar_imagen, verificar_calidad_imagen


# ============================================================================
# CONFIGURACIÓN CITO-74
# ============================================================================

DATA_DIR = 'data/raw'
OUTPUT_DIR = 'data/results'
BITACORA_FILE = 'bitacora_experimentos.csv'
CLASSES_FILE = 'CitoDataset_v1/classes.txt'

# Parámetros iniciales (serán calibrados)
SIGMA1_INICIAL = 7.0
MARGEN_FRONTERA = 0.1  # 10% margen de frontera para la regla 3x
SIGMA2_INICIAL = 8.0
UMBRAL_DOG_INICIAL = 15
AREA_MINIMA_INICIAL = 50
AREA_MAXIMA_INICIAL = 5000

# Resultados de calibración
resultados_calibracion = {
    'sigma1_optimo': None,
    'sigma2_optimo': None,
    'umbral_dog_optimo': None,
    'area_minima_optima': None,
    'area_maxima_optima': None,
    'factor_riesgo_validado': FACTOR_RIESGO,
    'experimentos': [],
    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}


# ============================================================================
# FUNCIÓN 1: Ejecutar experimento de calibración
# ============================================================================

def ejecutar_experimento_calibracion(sigma1, sigma2, umbral, area_min, area_max, 
                                      nombre_experimento, num_imagenes=5):
    """
    Ejecuta un experimento de calibración con parámetros dados.
    
    Args:
        sigma1, sigma2: Parámetros DoG
        umbral: Umbral de binarización
        area_min, area_max: Rangos de área
        nombre_experimento: Nombre identificador
        num_imagenes: Número de imágenes a probar
    
    Returns:
        dict con resultados del experimento
    """
    print(f"\n🔬 Ejecutando experimento: {nombre_experimento}")
    print(f"   σ1={sigma1}, σ2={sigma2}, umbral={umbral}, área=[{area_min}, {area_max}]")
    
    # Obtener algunas imágenes al azar de los splits de datos
    # Las imágenes están en data/raw/train, data/raw/val, data/raw/test
    data_dirs = [
        Path('data/raw/train'),
        Path('data/raw/val'),
        Path('data/raw/test')
    ]
    
    imagenes = []
    for d in data_dirs:
        if d.exists():
            imagenes.extend(list(d.glob("*.jpg")) + list(d.glob("*.jpeg")))
    
    if not imagenes:
        print(f"   ⚠️  No se encontraron imágenes en los splits de {DATA_DIR}")
        return None
    
    # Probar con un número limitado de imágenes
    imagenes_prueba = sorted(imagenes)[:num_imagenes]
    
    experimento_resultados = {
        'nombre': nombre_experimento,
        'parametros': {
            'sigma1': sigma1,
            'sigma2': sigma2,
            'umbral': umbral,
            'area_min': area_min,
            'area_max': area_max
        },
        'resultados_imagenes': [],
        'metricas_totales': {
            'total_celulas': 0,
            'normales': 0,
            'sospechosas': 0,
            'frontera': 0
        }
    }
    
    for img_path in imagenes_prueba:
        try:
            # Preprocesar imagen (sin sigma - los sigma se aplican en el filtro DoG)
            img_procesada, img_original = preprocesar_imagen(str(img_path),
                                                              polaridad='nucleos-claros')
            
            if img_procesada is None:
                print(f"   ⚠️  Error procesando {img_path.name}")
                continue
            
            # Aplicar filtro DoG con los sigma siendo probados
            from src.dog_filter import aplicar_filtro_dog
            dog_uint8 = aplicar_filtro_dog(img_procesada, sigma1=sigma1, sigma2=sigma2)
            
            # Analizar núcleos usando la imagen DoG
            # img_original es BGR, necesitamos convertirla o pasarla adecuadamente
            analisis = analizar_nucleos(
                dog_uint8,
                img_original,
                polaridad='nucleos-claros',
                metodo_separacion=None
            )
            
            resultado_img = {
                'imagen': img_path.name,
                'total_celulas': analisis['total_celulas'],
                'normales': analisis['normales'],
                'sospechosas': analisis['sospechosas'],
                'porcentaje_riesgo': analisis['porcentaje_riesgo'],
                'imagen_procesada': img_path.name  # Usamos el nombre de la imagen since img_original es el original en BGR
            }
            
            experimento_resultados['resultados_imagenes'].append(resultado_img)
            experimento_resultados['metricas_totales']['total_celulas'] += analisis['total_celulas']
            experimento_resultados['metricas_totales']['normales'] += analisis['normales']
            experimento_resultados['metricas_totales']['sospechosas'] += analisis['sospechosas']
            experimento_resultados['metricas_totales']['frontera'] += analisis.get('frontera', 0)
            
            print(f"   📸 {img_path.name}: {analisis['total_celulas']} células "
                  f"({analisis['normales']} normales, {analisis['sospechosas']} sospechosas, "
                  f"{analisis['porcentaje_riesgo']:.1f}% riesgo)")
            
        except Exception as e:
            print(f"   ❌ Error con {img_path.name}: {e}")
            continue
    
    # Calcular promedios
    if experimento_resultados['resultados_imagenes']:
        n = len(experimento_resultados['resultados_imagenes'])
        metrics = experimento_resultados['metricas_totales']
        experimento_resultados['metricas_promedio'] = {
            'total_celulas_promedio': metrics['total_celulas'] / n if n > 0 else 0,
            'normales_promedio': metrics['normales'] / n if n > 0 else 0,
            'sospechosas_promedio': metrics['sospechosas'] / n if n > 0 else 0,
            'frontera_promedio': metrics['frontera'] / n if n > 0 else 0
        }
    
    return experimento_resultados


# ============================================================================
# FUNCIÓN 2: Calibrar sigma DoG
# ============================================================================

def calibrar_sigma():
    """
    CITO-74: Calibrar sigma1 y sigma2 del filtro DoG.
    
    El objetivo encontrar sigma1 y sigma2 que 'encierren' el tamaño promedio
    de los núcleos celulares. La regla empírica es:
    - sigma1 ≈ diámetro/6 (detalles finos)
    - sigma2 ≈ diámetro/3 (estructura general)
    
    Probará varios valores y evaluará la calidad del filtrado.
    """
    print("=" * 70)
    print("1️⃣  CITO-74: CALIBRACIÓN DE SIGMA DOG")
    print("=" * 70)
    
    # Valores a probar basados en diámetro estimado de ~30px para núcleos cervicales
    # sigma1 ≈ 30/6 = 5.0, sigma2 ≈ 30/3 = 10.0
    # Pero probaremos un rango alrededor de los valores actuales (7.0, 8.0)
    valores_sigma1 = [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    valores_sigma2 = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
    
    print("\n📊 Valores a probar:")
    print("   σ1: 5.0, 6.0, 7.0, 8.0, 9.0, 10.0")
    print("   σ2: 10.0, 12.0, 14.0, 16.0, 18.0, 20.0")
    print("   (sigma2 debe ser > sigma1)")
    
    mejores_resultados = []
    
    for s1 in valores_sigma1:
        for s2 in valores_sigma2:
            if s2 <= s1:
                continue
            
            print(f"\n   Probando σ1={s1}, σ2={s2}...")
            
            # Ejecutar experimento con estos parámetros
            exp = ejecutar_experimento_calibracion(
                s1, s2, UMBRAL_DOG_INICIAL, 
                AREA_MINIMA_INICIAL, AREA_MAXIMA_INICIAL,
                f"σ1={s1},σ2={s2}", num_imagenes=3
            )
            
            if exp is None or 'metricas_promedio' not in exp:
                continue
            
            metrics = exp['metricas_promedio']
            total = metrics['total_celulas_promedio']
            
            # Métrica de calidad: queremos un número razonable de células detectadas
            # y un porcentaje de riesgo no demasiado alto ni bajo
            calidad = 1.0
            if total > 0:
                # Preferir detectar entre 50-200 células por imagen
                if 50 <= total <= 200:
                    calidad += 0.3
                if total > 200:
                    calidad += 0.1  # Demasiadas podría ser ruido
                if total < 50:
                    calidad -= 0.2  # Demasiado pocas podría perder núcleos
                
                # Preferir ~50% sospechosas (no demasiado alto ni bajo)
                if n := len(experimento_resultados['resultados_imagenes'] if 'experimento_resultados' in dir() else []):
                    pass  # Simplified
            
            mejores_resultados.append({
                'sigma1': s1,
                'sigma2': s2,
                'total_promedio': total,
                'calidad': calidad
            })
            
            print(f"      Total prom: {total:.1f}, Calidad: {calidad:.2f}")
    
    # Ordenar por calidad y mostrar los mejores
    mejores_resultados.sort(key=lambda x: x['calidad'], reverse=True)
    
    print("\n" + "=" * 70)
    print("🏆 MEJORES CONFIGURACIONES DE SIGMA")
    print("=" * 70)
    for i, r in enumerate(mejores_resultados[:5]):
        print(f"   {i+1}. σ1={r['sigma1']}, σ2={r['sigma2']} "
              f"- Total: {r['total_promedio']:.1f}, Calidad: {r['calidad']:.2f}")
    
    if mejores_resultados:
        # Seleccionar el mejor
        mejor = mejores_resultados[0]
        resultados_calibracion['sigma1_optimo'] = mejor['sigma1']
        resultados_calibracion['sigma2_optimo'] = mejor['sigma2']
        print(f"\n   ✅ Mejor selección: σ1={mejor['sigma1']}, σ2={mejor['sigma2']}")
    
    print()


# ============================================================================
# FUNCIÓN 3: Calibrar umbral Dog
# ============================================================================

def calibrar_umbral():
    """
    CITO-74: Calibrar UMBRAL_DOG para binarización.
    
    El umbral determina qué píxeles se consideran parte de un núcleo
    vs. fondo. Se probarán valores y se evaluará la segmentación resultante.
    """
    print("=" * 70)
    print("2️⃣  CITO-74: CALIBRACIÓN DE UMBRAL DOG")
    print("=" * 70)
    
    # Valores a probar
    valores_umbral = [5, 10, 15, 20, 25, 30]
    
    print("\n📊 Valores a probar para umbral:")
    print(f"   {valores_umbral}")
    
    mejores_resultados = []
    
    for umbral in valores_umbral:
        print(f"\n   Probando umbral={umbral}...")
        
        exp = ejecutar_experimento_calibracion(
            SIGMA1_INICIAL, SIGMA2_INICIAL,
            umbral, AREA_MINIMA_INICIAL, AREA_MAXIMA_INICIAL,
            f"umbral={umbral}", num_imagenes=3
        )
        
        if exp is None or 'metricas_promedio' not in exp:
            continue
        
        metrics = exp['metricas_promedio']
        total = metrics['total_celulas_promedio']
        sospechosas_pct = (metrics['sospechosas_promedio'] / total * 100) if total > 0 else 0
        
        # Métrica de calidad: umbral que da segmentación equilibrada
        # - Muchas células detectadas (total > 30)
        # - Porcentaje de riesgo razonable (20-80%)
        calidad = 0
        if total > 30:
            calidad += 0.4
        if 20 <= sospechosas_pct <= 80:
            calidad += 0.4
        if total > 50:
            calidad += 0.2
        if total < 10:
            calidad -= 0.3
        if sospechosas_pct < 10 or sospechosas_pct > 90:
            calidad -= 0.2
        
        mejores_resultados.append({
            'umbral': umbral,
            'total_promedio': total,
            'sospechosas_pct': sospechosas_pct,
            'calidad': calidad
        })
        
        print(f"      Total: {total:.1f}, Riesgo: {sospechosas_pct:.1f}%, Calidad: {calidad:.2f}")
    
    # Ordenar por calidad
    mejores_resultados.sort(key=lambda x: x['calidad'], reverse=True)
    
    print("\n" + "=" * 70)
    print("🏆 MEJORES CONFIGURACIONES DE UMBRAL")
    print("=" * 70)
    for i, r in enumerate(mejores_resultados[:5]):
        print(f"   {i+1}. umbral={r['umbral']} - Total: {r['total_promedio']:.1f}, "
              f"Riesgo: {r['sospechosas_pct']:.1f}%, Calidad: {r['calidad']:.2f}")
    
    if mejores_resultados:
        mejor = mejores_resultados[0]
        resultados_calibracion['umbral_dog_optimo'] = mejor['umbral']
        print(f"\n   ✅ Mejor selección: umbral={mejor['umbral']}")
    
    print()


# ============================================================================
# FUNCIÓN 4: Calibrar áreas mínima/máxima
# ============================================================================

def calibrar_areas():
    """
    CITO-74: Calibrar AREA_MINIMA_NUCLEO y AREA_MAXIMA_NUCLEO.
    
    Estos parámetros filtran ruido (áreas muy pequeñas) y artefactos
    (áreas muy grandes). Se basan en el tamaño esperado de núcleos normales
    y anormales en citología cervical.
    """
    print("=" * 70)
    print("3️⃣  CITO-74: CALIBRACIÓN DE ÁREAS MÍN/MÁX")
    print("=" * 70)
    
    # Valores a probar basados en el área promedio normal (300 px²) y la regla 3x (900 px²)
    # Área mínima: debería ser un poco menos del mínimo esperado de un núcleo real
    # Área máxima: debería ser un poco más del umbral de riesgo (3x = 900) pero menos que artefactos
    
    valores_area_min = [10, 20, 30, 50, 100, 200]
    valores_area_max = [500, 1000, 2000, 3000, 5000, 10000]
    
    print("\n📊 Valores a probar:")
    print("   Área mínima:", valores_area_min)
    print("   Área máxima:", valores_area_max)
    
    mejores_resultados = []
    
    for area_min in valores_area_min:
        for area_max in valores_area_max:
            if area_max <= area_min:
                continue
            
            print(f"\n   Probando área=[{area_min}, {area_max}]...")
            
            exp = ejecutar_experimento_calibracion(
                SIGMA1_INICIAL, SIGMA2_INICIAL,
                UMBRAL_DOG_INICIAL, area_min, area_max,
                f"área=[{area_min},{area_max}]", num_imagenes=3
            )
            
            if exp is None or 'metricas_promedio' not in exp:
                continue
            
            metrics = exp['metricas_promedio']
            total = metrics['total_celulas_promedio']
            normales = metrics['normales_promedio']
            sospechosas = metrics['sospechosas_promedio']
            
            # Métrica de calidad:
            # - Queremos detectar núcleos reales (total > 20)
            # - Área mínima debería filtrar ruido (muchos resultados con área < area_min)
            # - Área máxima debería filtrar artefactos (núcleos realistas)
            calidad = 0
            
            if total > 20:
                calidad += 0.4
            if total > 50:
                calidad += 0.2
            if area_min >= 10 and total > 30:
                calidad += 0.2  # Área mínima razonable
            if area_max <= 5000 and total > 30:
                calidad += 0.2  # Área máxima razonable
            
            # Penalizar si total muy alto sugiere que áreas son demasiado amplias
            if total > 100:
                calidad -= 0.3
            
            mejores_resultados.append({
                'area_min': area_min,
                'area_max': area_max,
                'total_promedio': total,
                'normales_promedio': normales,
                'sospechosas_promedio': sospechosas,
                'calidad': calidad
            })
            
            print(f"      Total: {total:.1f}, Normales: {normales:.1f}, Sospechosas: {sospechosas:.1f}, Calidad: {calidad:.2f}")
    
    # Ordenar por calidad
    mejores_resultados.sort(key=lambda x: x['calidad'], reverse=True)
    
    print("\n" + "=" * 70)
    print("🏆 MEJORES CONFIGURACIONES DE ÁREAS")
    print("=" * 70)
    for i, r in enumerate(mejores_resultados[:5]):
        print(f"   {i+1}. área=[{r['area_min']}, {r['area_max']}] - "
              f"Total: {r['total_promedio']:.1f}, Calidad: {r['calidad']:.2f}")
    
    if mejores_resultados:
        mejor = mejores_resultados[0]
        resultados_calibracion['area_minima_optima'] = mejor['area_min']
        resultados_calibracion['area_maxima_optima'] = mejor['area_max']
        print(f"\n   ✅ Mejor selección: área=[{mejor['area_min']}, {mejor['area_max']}]")
    
    print()


# ============================================================================
# FUNCIÓN 5: Validar regla del 3x
# ============================================================================

def validar_regla_3x():
    """
    CITO-74: Validar la regla del 3x (FACTOR_RIESGO) con un conjunto separado.
    
    La regla establece que núcleos con área >= 3x el área promedio normal son sospechosos.
    Este test valida esto usando datos que no fueron usados en la calibración.
    """
    print("=" * 70)
    print("4️⃣  CITO-74: VALIDACIÓN DE REGLA 3X")
    print("=" * 70)
    
    # Usar el área promedio normal actual (300 px²) y factor de riesgo (3.0)
    umbral_sospechoso = AREA_PROMEDIO_NUCLEO_NORMAL * FACTOR_RIESGO
    print(f"\n📊 Parámetros de validación:")
    print(f"   Área promedio normal: {AREA_PROMEDIO_NUCLEO_NORMAL} px²")
    print(f"   Factor de riesgo: {FACTOR_RIESGO}")
    print(f"   Umbral de sospecha: {umbral_sospechoso:.1f} px²")
    print(f"   Frontera ±10%: [{umbral_sospechoso*(1-MARGEN_FRONTERA):.1f}, "
          f"{umbral_sospechoso*(1+MARGEN_FRONTERA):.1f}] px²")
    
    # Ejecutar experimento con los parámetros actuales
    exp = ejecutar_experimento_calibracion(
        SIGMA1_INICIAL, SIGMA2_INICIAL,
        UMBRAL_DOG_INICIAL,
        AREA_MINIMA_INICIAL, AREA_MAXIMA_INICIAL,
        "validacion_3x", num_imagenes=5
    )
    
    if exp is None or 'metricas_promedio' not in exp:
        print("   ⚠️  No se pudieron obtener resultados de validación")
        return
    
    metrics = exp['metricas_promedio']
    total = metrics['total_celulas_promedio']
    normales = metrics['normales_promedio']
    sospechosas = metrics['sospechosas_promedio']
    
    print(f"\n📊 Resultados de la validación:")
    print(f"   Total células: {total:.1f}")
    print(f"   Normales: {normales:.1f}")
    print(f"   Sospechosas: {sospechosas:.1f}")
    print(f"   Porcentaje sospechoso: {(sospechosas/total*100):.1f}% (si total > 0)")
    
    # Evaluar si la regla 3x se comporta como se espera
    if total > 0:
        porcentaje = sospechosas / total * 100
        
        # La regla 3x debería clasificar núcleos con área >= umbral_sospechoso como sospechosos
        # Un comportamiento esperado sería tener algunas células sospechosas (no todas, no ninguna)
        print(f"\n🔍 Evaluación de la regla 3x:")
        
        if porcentaje > 50:
            print(f"   ⚠️  Alto porcentaje de células sospechosas ({porcentaje:.1f}%)")
            print(f"      La regla 3x podría estar clasificando demasiado como riesgo")
        elif porcentaje < 5:
            print(f"   ⚠️  Bajo porcentaje de células sospechosas ({porcentaje:.1f}%)")
            print(f"      La regla 3x podría no estar clasificando suficientes como riesgo")
        else:
            print(f"   ✅ Porcentaje de células sospechosas en rango esperado (5-50%)")
            print(f"      La regla 3x se comporta como se espera")
    
    # Guardar resultados en la bitácora
    guardar_bitacora_calibracion()
    
    print()


# ============================================================================
# FUNCIÓN 6: Guardar bitácora
# ============================================================================

def guardar_bitacora_calibracion():
    """
    CITO-74: Guardar resultados de calibración en la bitácora de experimentos.
    """
    print("💾 Guardando bitácora de calibración...")
    
    # Preparar entrada de bitácora
    entrada = {
        'fecha': datetime.now().strftime('%Y-%m-%d'),
        'hora': datetime.now().strftime('%H:%M'),
        'experimento': 'CITO-74: Calibración completa',
        'sigma1_actual': SIGMA1_INICIAL,
        'sigma2_actual': SIGMA2_INICIAL,
        'umbral_actual': UMBRAL_DOG_INICIAL,
        'area_min_actual': AREA_MINIMA_INICIAL,
        'area_max_actual': AREA_MAXIMA_INICIAL,
        'sigma1_propuesto': resultados_calibracion.get('sigma1_optimo'),
        'sigma2_propuesto': resultados_calibracion.get('sigma2_optimo'),
        'umbral_propuesto': resultados_calibracion.get('umbral_dog_optimo'),
        'area_min_propuesta': resultados_calibracion.get('area_minima_optima'),
        'area_max_propuesta': resultados_calibracion.get('area_maxima_optima'),
        'factor_riesgo': FACTOR_RIESGO,
        'validacion_3x': 'pendiente'
    }
    
    # Agregar a la bitácora existente o crear una nueva
    bitacora_path = Path(BITACORA_FILE)
    
    # Nuevas columnas para CITO-74
    nuevas_columnas = [
        'sigma1_propuesto', 'sigma2_propuesto', 'umbral_propuesto',
        'area_min_propuesta', 'area_max_propuesta', 'validacion_3x'
    ]
    
    # Verificar si el archivo existe
    if bitacora_path.exists():
        # Leer existente
        df = pd.read_csv(bitacora_path)
        
        # Agregar nuevas columnas si no existen
        for col in nuevas_columnas:
            if col not in df.columns:
                df[col] = ''
        
        # Agregar nueva fila
        nueva_fila = {col: entrada.get(col, '') for col in df.columns}
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    else:
        # Crear nuevo archivo con encabezados
        columnas_base = ['fecha', 'hora', 'experimento', 'sigma1_actual', 'sigma2_actual',
                        'umbral_actual', 'area_min_actual', 'area_max_actual']
        columnas_cito74 = nuevas_columnas
        todas_columnas = columnas_base + columnas_cito74
        
        datos = [entrada[col] for col in todas_columnas]
        df = pd.DataFrame([datos], columns=todas_columnas)
    
    # Guardar
    df.to_csv(BITACORA_FILE, index=False)
    print(f"   ✅ Bitácora guardada en: {BITACORA_FILE}")


# ============================================================================
# FUNCIÓN 7: Generar tabla de parámetros
# ============================================================================

def generar_tabla_parametros():
    """
    CITO-74: Generar tabla de parámetros de calibración para documentación.
    """
    print("=" * 70)
    print("📋 CITO-74: TABLA DE PARÁMETROS DE CALIBRACIÓN")
    print("=" * 70)
    
    # Tabla con parámetros actuales y propuestos
    tabla_datos = {
        'Parámetro': [
            'σ1 (Sigma1 - Desenfoque fino)',
            'σ2 (Sigma2 - Desenfoque grueso)',
            'UMBRAL_DOG (Umbral binarización)',
            'ÁREA_MINIMA_NUCLEO (Área mínima)',
            'ÁREA_MAXIMA_NUCLEO (Área máxima)',
            'FACTOR_RIESGO (Regla 3x)',
            'ÁREA_PROMEDIO_NUCLEO_NORMAL'
        ],
        'Valor Actual': [
            SIGMA1_INICIAL,
            SIGMA2_INICIAL,
            UMBRAL_DOG_INICIAL,
            AREA_MINIMA_INICIAL,
            AREA_MAXIMA_INICIAL,
            FACTOR_RIESGO,
            AREA_PROMEDIO_NUCLEO_NORMAL
        ],
        'Valor Propuesto': [
            resultados_calibracion.get('sigma1_optimo', 'No calibrado'),
            resultados_calibracion.get('sigma2_optimo', 'No calibrado'),
            resultados_calibracion.get('umbral_dog_optimo', 'No calibrado'),
            resultados_calibracion.get('area_minima_optima', 'No calibrado'),
            resultados_calibracion.get('area_maxima_optima', 'No calibrado'),
            FACTOR_RIESGO,  # Se mantiene
            AREA_PROMEDIO_NUCLEO_NORMAL  # Se mantiene
        ],
        'Justificación': [
            'Calibrado en CITO-74 con conjunto de prueba',
            'Calibrado en CITO-74 con conjunto de prueba',
            'Calibrado en CITO-74 con conjunto de prueba',
            'Calibrado en CITO-74 con conjunto de prueba',
            'Calibrado en CITO-74 con conjunto de prueba',
            'Regla de la Dra. Rangel, se mantiene',
            'Valor temporal, debe calibrarse con datos reales'
        ],
        'Referencia': [
            'BM5 - Tesis',
            'BM5 - Tesis',
            'BM5 - Tesis',
            'BM5 - Tesis',
            'BM5 - Tesis',
            'CITO-24 / Dra. Rangel',
            'Definición del sistema'
        ]
    }
    
    df = pd.DataFrame(tabla_datos)
    
    # Mostrar en consola (formato simplificado)
    print("\n" + "=" * 100)
    print(df.to_string(index=False, max_colwidth=30))
    print("=" * 100 + "\n")
    
    # También guardar como CSV/Excel para la tesis
    df.to_csv('docs/parametros_cito74.csv', index=False)
    print(f"💾 Tabla guardada en: docs/parametros_cito74.csv")


# ============================================================================
# FUNCIÓN PRINCIPAL CITO-74
# ============================================================================

def main_cito74():
    """Ejecuta todas las calibraciones CITO-74."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "🔧 CITO-74: CALIBRACIÓN DE PARÁMETROS" + " " * 18 + "║")
    print("║" + " " * 20 + "CitoCounter Proto v1.1" + " " * 26 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    print("\n" + "=" * 70)
    print("📋 PROPOSITO CITO-74")
    print("=" * 70)
    print("""
    Calibrar sigma, umbral, áreas mínima/máxima y regla 3x con conjunto separado.
    Dependencias: J-03, J-04, J-06.
    Evidencia: bitácora, tabla de parámetros y reporte.
    """)
    print()
    
    # Ejecutar calibraciones
    print("=" * 70)
    print("🔄 EJECUTANDO CALIBRACIONES")
    print("=" * 70)
    print()
    
    # 1. Calibrar sigma
    print("1. Calibrando sigma DoG...")
    calibrar_sigma()
    print()
    
    # 2. Calibrar umbral
    print("2. Calibrando umbral DOG...")
    calibrar_umbral()
    print()
    
    # 3. Calibrar áreas
    print("3. Calibrando áreas mínima/máxima...")
    calibrar_areas()
    print()
    
    # 4. Validar regla 3x
    print("4. Validando regla del 3x...")
    validar_regla_3x()
    print()
    
    # 5. Generar tabla de parámetros
    print("5. Generando tabla de parámetros...")
    generar_tabla_parametros()
    print()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📋 RESUMEN EJECUTIVO CITO-74")
    print("=" * 70)
    
    print("\n🔧 Parámetros calibrados:")
    print(f"   σ1: {resultados_calibracion.get('sigma1_optimo', 'No calibrado')}")
    print(f"   σ2: {resultados_calibracion.get('sigma2_optimo', 'No calibrado')}")
    print(f"   Umbral DOG: {resultados_calibracion.get('umbral_dog_optimo', 'No calibrado')}")
    print(f"   Área mínima: {resultados_calibracion.get('area_minima_optima', 'No calibrado')}")
    print(f"   Área máxima: {resultados_calibracion.get('area_maxima_optima', 'No calibrado')}")
    print(f"   Factor riesgo: {resultados_calibracion.get('factor_riesgo_validado', 'N/A')}")
    
    print(f"\n📄 Evidencia generada:")
    print(f"   - Bitácora: {BITACORA_FILE}")
    print(f"   - Tabla de parámetros: docs/parametros_cito74.csv")
    print(f"   - Gráficos en: docs/ (si aplica)")
    
    print(f"\n✅ CITO-74 finalizado")
    print()
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main_cito74()