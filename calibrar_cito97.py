#!/usr/bin/env python3
"""
calibrar_cito97.py - CITO-97: Calibración de parámetros DoG para imágenes REALES (2048x1536)

Este script calibra los parámetros del filtro DoG específicamente para imágenes reales
de citología cervical (Papanicolaou/EDF) con resolución 2048x1536, donde los núcleos
son oscuros sobre fondo claro (polaridad 'nucleos-oscuros').

Dependencias: CITO-22, CITO-23, CITO-74
Evidencia: bitácora, tabla de parámetros y reporte
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

from src.dog_filter import aplicar_filtro_dog
from src.analysis import analizar_nucleos, clasificar_nucleo_por_area, AREA_PROMEDIO_NUCLEO_NORMAL, FACTOR_RIESGO
from src.preprocessing import preprocesar_imagen, verificar_calidad_imagen


# ============================================================================
# CONFIGURACIÓN CITO-97
# ============================================================================

DATA_DIR = 'data/raw'
OUTPUT_DIR = 'data/results'
BITACORA_FILE = 'bitacora_experimentos.csv'
CLASSES_FILE = 'CitoDataset_v1/classes.txt'

# Parámetros base (calibrados en CITO-74 para sintéticas)
SIGMA1_BASE = 5.0
SIGMA2_BASE = 10.0
UMBRAL_DOG_BASE = 5
AREA_MIN_BASE = 100
AREA_MAX_BASE = 300000

# Resultados de calibración
resultados_calibracion = {
    'sigma1_optimo': None,
    'sigma2_optimo': None,
    'umbral_dog_optimo': None,
    'area_minima_optima': None,
    'area_maxima_optima': None,
    'factor_riesgo_validado': 3.0,
    'experimentos': [],
    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}


# ============================================================================
# FUNCIÓN 1: Obtener imágenes reales para calibración
# ============================================================================

def obtener_imagenes_reales(directorio: Path, max_imagenes: int = 20) -> list:
    """Obtiene imágenes reales (2048x1536) de un directorio."""
    if not directorio.is_dir():
        return []
    
    imagenes = []
    for path in directorio.iterdir():
        if path.is_file() and path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}:
            img = cv2.imread(str(path))
            if img is not None:
                h, w = img.shape[:2]
                if w >= 2000 and h >= 1500:  # Imágenes reales 2048x1536
                    imagenes.append(path)
                    if len(imagenes) >= max_imagenes:
                        break
    return imagenes


def obtener_todas_imagenes_reales(max_total: int = 50) -> list:
    """Obtiene imágenes reales de todos los splits."""
    imagenes = []
    for split in ['train', 'val', 'test']:
        split_dir = Path('data/raw') / split
        if split_dir.exists():
            imgs = obtener_imagenes_reales(split_dir, max_imagenes=20)
            imagenes.extend(imgs)
            if len(imagenes) >= max_total:
                break
    return imagenes[:max_total]


# ============================================================================
# FUNCIÓN 2: Evaluar configuración en imágenes reales
# ============================================================================

def evaluar_configuracion_real(
    rutas: list[Path], 
    sigma1: float, 
    sigma2: float,
    umbral: int,
    area_min: int,
    area_max: int,
    polaridad: str = 'nucleos-oscuros'
) -> dict:
    """Evalúa una configuración en imágenes reales."""
    if sigma2 <= sigma1:
        raise ValueError("sigma2 debe ser mayor que sigma1")
    
    totales = []
    areas_todas = []
    tp_total = fp_total = fn_total = 0
    
    for ruta in rutas:
        try:
            imagen_gris, imagen_original = preprocesar_imagen(str(ruta), polaridad='nucleos-oscuros')
            imagen_dog = aplicar_filtro_dog(imagen_gris, sigma1=sigma1, sigma2=sigma2)
            
            # Temporalmente sobrescribir constantes
            import src.analysis as analysis_module
            old_umbral = analysis_module.UMBRAL_DOG
            old_area_min = analysis_module.AREA_MINIMA_NUCLEO
            old_area_max = analysis_module.AREA_MAXIMA_NUCLEO
            
            analysis_module.UMBRAL_DOG = umbral
            analysis_module.AREA_MINIMA_NUCLEO = {'nucleos-claros': 10, 'nucleos-oscuros': 100}
            analysis_module.AREA_MAXIMA_NUCLEO = {'nucleos-claros': 1000, 'nucleos-oscuros': 300000}
            
            resultados = analizar_nucleos(
                imagen_dog, 
                imagen_original, 
                polaridad='nucleos-oscuros',
                usar_mascara_borde=True,
                ancho_borde=50
            )
            
            # Restaurar constantes
            analysis_module.UMBRAL_DOG = 5
            analysis_module.AREA_MINIMA_NUCLEO = {'nucleos-claros': 10, 'nucleos-oscuros': 100}
            analysis_module.AREA_MAXIMA_NUCLEO = {'nucleos-claros': 1000, 'nucleos-oscuros': 300000}
            
            # Obtener ground truth
            label_path = Path('CitoDataset_v1/labels') / 'train' / f"{ruta.stem}.txt"
            if not label_path.exists():
                label_path = Path('CitoDataset_v1/labels') / 'val' / f"{ruta.stem}.txt"
            if not label_path.exists():
                label_path = Path('CitoDataset_v1/labels') / 'test' / f"{ruta.stem}.txt"
            
            gt_centroids = []
            if label_path.exists():
                imagen = cv2.imread(str(ruta))
                h, w = imagen.shape[:2]
                with open(label_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            x_center = float(parts[1]) * w
                            y_center = float(parts[2]) * h
                            gt_centroids.append((x_center, y_center))
            
            # Extraer centroides predichos
            pred_centroids = []
            for contorno in resultados.get('contornos_normales', []) + resultados.get('contornos_sospechosos', []):
                M = cv2.moments(contorno)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    pred_centroids.append((cx, cy))
            
            # Calcular TP, FP, FN por emparejamiento espacial
            tp = fp = fn = 0
            if pred_centroids and gt_centroids:
                usados_gt = set()
                for px, py in pred_centroids:
                    mejor_dist = float('inf')
                    mejor_idx = -1
                    for i, (gx, gy) in enumerate(gt_centroids):
                        if i in usados_gt:
                            continue
                        dist = np.sqrt((px - gx)**2 + (py - gy)**2)
                        if dist < mejor_dist:
                            mejor_dist = dist
                            mejor_idx = i
                    if mejor_dist <= 20:  # 20 píxeles de tolerancia
                        tp += 1
                        usados_gt.add(mejor_idx)
                    else:
                        fp += 1
                fn = len(gt_centroids) - len(usados_gt)
            else:
                fp = len(pred_centroids)
                fn = len(gt_centroids)
            
            totales.append({
                'imagen': ruta.name,
                'tp': tp,
                'fp': fp,
                'fn': fn,
                'pred_count': len(pred_centroids),
                'gt_count': len(gt_centroids)
            })
            
        except Exception as e:
            print(f"   ⚠️  Error procesando {ruta.name}: {e}")
            continue
    
    # Calcular métricas globales
    tp_total = sum(r['tp'] for r in totales)
    fp_total = sum(r['fp'] for r in totales)
    fn_total = sum(r['fn'] for r in totales)
    
    precision = tp_total / (tp_total + fp_total) if (tp_total + fp_total) > 0 else 0
    recall = tp_total / (tp_total + fn_total) if (tp_total + fn_total) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'tp': tp_total,
        'fp': fp_total,
        'fn': fn_total,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'imagenes_procesadas': len(totales),
        'detalles': totales
    }


# ============================================================================
# FUNCIÓN 2: Calibrar sigma para imágenes reales
# ============================================================================

def calibrar_sigma_real():
    """
    CITO-97: Calibrar sigma1 y sigma2 para imágenes reales (2048x1536).
    
    Los núcleos en imágenes reales son más grandes que en sintéticas.
    Regla empírica: sigma1 ≈ diámetro/6, sigma2 ≈ diámetro/3
    Para núcleos de ~60-100px: sigma1 ≈ 10-16, sigma2 ≈ 20-33
    """
    print("=" * 70)
    print("1️⃣  CITO-97: CALIBRACIÓN DE SIGMA PARA IMÁGENES REALES")
    print("=" * 70)
    
    # Obtener imágenes reales de calibración
    imagenes_cal = obtener_todas_imagenes_reales(max_total=20)
    print(f"📸 Imágenes de calibración: {len(imagenes_cal)}")
    
    if len(imagenes_cal) < 5:
        print("   ⚠️  Pocas imágenes para calibración")
        return
    
    # Valores a probar - núcleos reales son más grandes
    valores_sigma1 = [8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
    valores_sigma2 = [15.0, 20.0, 25.0, 30.0, 35.0, 40.0]
    
    print("\n📊 Valores a probar:")
    print(f"   σ1: {valores_sigma1}")
    print(f"   σ2: {valores_sigma2}")
    print("   (sigma2 debe ser > sigma1)")
    
    mejores_resultados = []
    
    for s1 in valores_sigma1:
        for s2 in valores_sigma2:
            if s2 <= s1:
                continue
            
            print(f"\n   Probando σ1={s1}, σ2={s2}...")
            
            resultado = evaluar_configuracion_real(
                rutas=[Path(r) for r in [str(p) for p in imagenes_cal[:5]]],  # Usar 5 imágenes
                sigma1=s1,
                sigma2=s2,
                umbral=5,
                area_min=100,
                area_max=300000
            )
            
            if resultado['imagenes_procesadas'] == 0:
                continue
            
            f1 = resultado['f1']
            recall = resultado['recall']
            precision = resultado['precision']
            
            # Métrica de calidad: priorizar recall alto y F1 alto
            calidad = 0
            if resultado['recall'] > 0.5:
                calidad += 0.4
            if resultado['recall'] > 0.7:
                calidad += 0.3
            if resultado['precision'] > 0.3:
                calidad += 0.2
            if resultado['f1'] > 0.5:
                calidad += 0.1
            
            mejores_resultados.append({
                'sigma1': s1,
                'sigma2': s2,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'calidad': calidad
            })
            
            print(f"      P={precision:.3f}, R={recall:.3f}, F1={f1:.3f}, Calidad={calidad:.2f}")
    
    # Ordenar por calidad
    mejores_resultados.sort(key=lambda x: x['calidad'], reverse=True)
    
    print("\n" + "=" * 70)
    print("🏆 MEJORES CONFIGURACIONES DE SIGMA PARA IMÁGENES REALES")
    print("=" * 70)
    for i, r in enumerate(mejores_resultados[:5]):
        print(f"   {i+1}. σ1={r['sigma1']}, σ2={r['sigma2']} "
              f"- P={r['precision']:.3f}, R={r['recall']:.3f}, F1={r['f1']:.3f}, Calidad={r['calidad']:.2f}")
    
    if mejores_resultados:
        mejor = mejores_resultados[0]
        resultados_calibracion['sigma1_optimo'] = mejor['sigma1']
        resultados_calibracion['sigma2_optimo'] = mejor['sigma2']
        print(f"\n   ✅ Mejor selección: σ1={mejor['sigma1']}, σ2={mejor['sigma2']}")
    
    print()


# ============================================================================
# FUNCIÓN 3: Calibrar umbral para imágenes reales
# ============================================================================

def calibrar_umbral_real():
    """
    CITO-97: Calibrar UMBRAL_DOG para imágenes reales.
    """
    print("=" * 70)
    print("2️⃣  CITO-97: CALIBRACIÓN DE UMBRAL DOG PARA IMÁGENES REALES")
    print("=" * 70)
    
    imagenes_cal = obtener_todas_imagenes_reales(max_total=10)
    print(f"📸 Imágenes de calibración: {len(imagenes_cal)}")
    
    # Usar los mejores sigma encontrados
    sigma1 = resultados_calibracion.get('sigma1_optimo', 10.0)
    sigma2 = resultados_calibracion.get('sigma2_optimo', 20.0)
    
    print(f"\n📊 Usando σ1={sigma1}, σ2={sigma2}")
    
    valores_umbral = [3, 5, 8, 10, 12, 15, 20, 25, 30]
    
    print("\n📊 Valores a probar para umbral:")
    print(f"   {valores_umbral}")
    
    mejores_resultados = []
    
    for umbral in valores_umbral:
        print(f"\n   Probando umbral={umbral}...")
        
        resultado = evaluar_configuracion_real(
            rutas=[Path(r) for r in [str(p) for p in imagenes_cal[:5]]],
            sigma1=sigma1,
            sigma2=sigma2,
            umbral=umbral,
            area_min=100,
            area_max=300000
        )
        
        if resultado['imagenes_procesadas'] == 0:
            continue
        
        precision = resultado['precision']
        recall = resultado['recall']
        f1 = resultado['f1']
        
        calidad = 0
        if resultado['recall'] > 0.5:
            calidad += 0.4
        if resultado['recall'] > 0.7:
            calidad += 0.3
        if resultado['precision'] > 0.3:
            calidad += 0.2
        if resultado['f1'] > 0.5:
            calidad += 0.1
        
        mejores_resultados.append({
            'umbral': umbral,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'calidad': calidad
        })
        
        print(f"      P={precision:.3f}, R={recall:.3f}, F1={f1:.3f}, Calidad={calidad:.2f}")
    
    mejores_resultados.sort(key=lambda x: x['calidad'], reverse=True)
    
    print("\n" + "=" * 70)
    print("🏆 MEJORES CONFIGURACIONES DE UMBRAL")
    print("=" * 70)
    for i, r in enumerate(mejores_resultados[:5]):
        print(f"   {i+1}. umbral={r['umbral']} - P={r['precision']:.3f}, R={r['recall']:.3f}, F1={r['f1']:.3f}, Calidad={r['calidad']:.2f}")
    
    if mejores_resultados:
        mejor = mejores_resultados[0]
        resultados_calibracion['umbral_dog_optimo'] = mejor['umbral']
        print(f"\n   ✅ Mejor selección: umbral={mejor['umbral']}")
    
    print()


# ============================================================================
# FUNCIÓN 3: Calibrar áreas para imágenes reales
# ============================================================================

def calibrar_areas_real():
    """
    CITO-97: Calibrar AREA_MINIMA_NUCLEO y AREA_MAXIMA_NUCLEO para imágenes reales.
    """
    print("=" * 70)
    print("3️⃣  CITO-97: CALIBRACIÓN DE ÁREAS PARA IMÁGENES REALES")
    print("=" * 70)
    
    imagenes_cal = obtener_todas_imagenes_reales(max_total=10)
    print(f"📸 Imágenes de calibración: {len(imagenes_cal)}")
    
    sigma1 = resultados_calibracion.get('sigma1_optimo', 10.0)
    sigma2 = resultados_calibracion.get('sigma2_optimo', 20.0)
    umbral = resultados_calibracion.get('umbral_dog_optimo', 5)
    
    print(f"\n📊 Usando σ1={sigma1}, σ2={sigma2}, umbral={umbral}")
    
    valores_area_min = [50, 100, 150, 200, 300, 500]
    valores_area_max = [5000, 10000, 20000, 50000, 100000, 200000, 300000]
    
    print("\n📊 Valores a probar:")
    print("   Área mínima:", valores_area_min)
    print("   Área máxima:", valores_area_max)
    
    mejores_resultados = []
    
    for area_min in valores_area_min:
        for area_max in valores_area_max:
            if area_max <= area_min:
                continue
            
            print(f"\n   Probando área=[{area_min}, {area_max}]...")
            
            resultado = evaluar_configuracion_real(
                rutas=[Path(r) for r in [str(p) for p in imagenes_cal[:5]]],
                sigma1=sigma1,
                sigma2=sigma2,
                umbral=umbral,
                area_min=area_min,
                area_max=area_max
            )
            
            if resultado['imagenes_procesadas'] == 0:
                continue
            
            precision = resultado['precision']
            recall = resultado['recall']
            f1 = resultado['f1']
            
            calidad = 0
            if resultado['recall'] > 0.5:
                calidad += 0.4
            if resultado['recall'] > 0.7:
                calidad += 0.3
            if resultado['precision'] > 0.3:
                calidad += 0.2
            if resultado['f1'] > 0.5:
                calidad += 0.1
            
            mejores_resultados.append({
                'area_min': area_min,
                'area_max': area_max,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'calidad': calidad
            })
            
            print(f"      P={precision:.3f}, R={recall:.3f}, F1={f1:.3f}, Calidad={calidad:.2f}")
    
    mejores_resultados.sort(key=lambda x: x['calidad'], reverse=True)
    
    print("\n" + "=" * 70)
    print("🏆 MEJORES CONFIGURACIONES DE ÁREAS")
    print("=" * 70)
    for i, r in enumerate(mejores_resultados[:5]):
        print(f"   {i+1}. área=[{r['area_min']}, {r['area_max']}] - "
              f"P={r['precision']:.3f}, R={r['recall']:.3f}, F1={r['f1']:.3f}, Calidad={r['calidad']:.2f}")
    
    if mejores_resultados:
        mejor = mejores_resultados[0]
        resultados_calibracion['area_minima_optima'] = mejor['area_min']
        resultados_calibracion['area_maxima_optima'] = mejor['area_max']
        print(f"\n   ✅ Mejor selección: área=[{mejor['area_min']}, {mejor['area_max']}]")
    
    print()


# ============================================================================
# FUNCIÓN 4: Validar con conjunto de prueba separado
# ============================================================================

def validar_con_test_set():
    """
    CITO-97: Validar parámetros calibrados con conjunto de prueba separado.
    """
    print("=" * 70)
    print("4️⃣  CITO-97: VALIDACIÓN CON CONJUNTO DE PRUEBA SEPARADO")
    print("=" * 70)
    
    # Usar imágenes de test reales
    test_dir = Path('data/raw/test')
    test_images = []
    for f in test_dir.iterdir():
        if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}:
            img = cv2.imread(str(f))
            if img is not None:
                h, w = img.shape[:2]
                if w >= 2000 and h >= 1500:
                    test_images.append(f)
    
    print(f"📸 Imágenes de test reales: {len(test_images)}")
    
    if len(test_images) == 0:
        print("   ⚠️  No hay imágenes de test reales")
        return
    
    # Usar mejores parámetros calibrados
    sigma1 = resultados_calibracion.get('sigma1_optimo', 10.0)
    sigma2 = resultados_calibracion.get('sigma2_optimo', 20.0)
    umbral = resultados_calibracion.get('umbral_dog_optimo', 5)
    area_min = resultados_calibracion.get('area_minima_optima', 100)
    area_max = resultados_calibracion.get('area_maxima_optima', 300000)
    
    print(f"\n📊 Parámetros finales:")
    print(f"   σ1={sigma1}, σ2={sigma2}, umbral={umbral}")
    print(f"   área=[{area_min}, {area_max}]")
    
    # Evaluar en todas las imágenes de test
    resultados = evaluar_configuracion_real(
        rutas=[Path(r) for r in [str(p) for p in test_images]],
        sigma1=sigma1,
        sigma2=sigma2,
        umbral=umbral,
        area_min=area_min,
        area_max=area_max
    )
    
    print(f"\n📊 RESULTADOS EN CONJUNTO DE PRUEBA:")
    print(f"   Imágenes procesadas: {resultados['imagenes_procesadas']}")
    print(f"   TP: {resultados['tp']}, FP: {resultados['fp']}, FN: {resultados['fn']}")
    print(f"   Precision: {resultados['precision']:.4f}")
    print(f"   Recall: {resultados['recall']:.4f}")
    print(f"   F1-Score: {resultados['f1']:.4f}")
    print(f"   Jaccard: {resultados['jaccard']:.4f}")
    
    # Guardar resultados
    resultados_calibracion['validacion_test'] = {
        'precision': resultados['precision'],
        'recall': resultados['recall'],
        'f1': resultados['f1'],
        'jaccard': resultados['jaccard'],
        'tp': resultados['tp'],
        'fp': resultados['fp'],
        'fn': resultados['fn']
    }
    
    print()


# ============================================================================
# FUNCIÓN 5: Generar tabla de parámetros finales
# ============================================================================

def generar_tabla_parametros_final():
    """
    CITO-97: Generar tabla final de parámetros calibrados para imágenes reales.
    """
    print("=" * 70)
    print("📋 CITO-97: TABLA FINAL DE PARÁMETROS PARA IMÁGENES REALES")
    print("=" * 70)
    
    tabla_datos = {
        'Parámetro': [
            'σ1 (Sigma1 - Desenfoque fino)',
            'σ2 (Sigma2 - Desenfoque grueso)',
            'UMBRAL_DOG (Umbral binarización)',
            'AREA_MINIMA_NUCLEO (nucleos-oscuros)',
            'AREA_MAXIMA_NUCLEO (nucleos-oscuros)',
            'FACTOR_RIESGO (Regla 3x)',
            'AREA_PROMEDIO_NUCLEO_NORMAL'
        ],
        'Valor Base (CITO-74)': [
            5.0,
            10.0,
            5,
            10,
            500,
            3.0,
            300
        ],
        'Valor Calibrado (CITO-97)': [
            resultados_calibracion.get('sigma1_optimo', 'No calibrado'),
            resultados_calibracion.get('sigma2_optimo', 'No calibrado'),
            resultados_calibracion.get('umbral_dog_optimo', 'No calibrado'),
            resultados_calibracion.get('area_minima_optima', 'No calibrado'),
            resultados_calibracion.get('area_maxima_optima', 'No calibrado'),
            3.0,  # Se mantiene
            300  # Temporal, pendiente CITO-97 completo
        ],
        'Justificación': [
            'Calibrado en CITO-97 con imágenes reales 2048x1536',
            'Calibrado en CITO-97 con imágenes reales 2048x1536',
            'Calibrado en CITO-97 con imágenes reales 2048x1536',
            'Calibrado en CITO-97 para núcleos reales más pequeños',
            'Calibrado en CITO-97 para artefactos reales',
            'Regla de la Dra. Rangel, se mantiene',
            'Valor temporal, debe calibrarse con CITO-97 completo'
        ],
        'Referencia': [
            'CITO-97 / BM5 - Tesis',
            'CITO-97 / BM5 - Tesis',
            'CITO-97 / BM5 - Tesis',
            'CITO-97 / BM5 - Tesis',
            'CITO-97 / BM5 - Tesis',
            'CITO-24 / Dra. Rangel',
            'Pendiente CITO-97 completo'
        ]
    }
    
    df = pd.DataFrame(tabla_datos)
    
    print("\n" + "=" * 100)
    print(df.to_string(index=False, max_colwidth=40))
    print("=" * 100 + "\n")
    
    # Guardar como CSV
    df.to_csv('docs/parametros_cito97.csv', index=False)
    print(f"💾 Tabla guardada en: docs/parametros_cito97.csv")


# ============================================================================
# FUNCIÓN PRINCIPAL CITO-97
# ============================================================================

def main_cito97():
    """Ejecuta todas las calibraciones CITO-97 para imágenes reales."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "🔧 CITO-97: CALIBRACIÓN PARA IMÁGENES REALES" + " " * 18 + "║")
    print("║" + " " * 20 + "CitoCounter Proto v1.1" + " " * 26 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    print("\n" + "=" * 70)
    print("📋 PROPÓSITO CITO-97")
    print("=" * 70)
    print("""
    Calibrar el filtro DoG para imágenes reales de citología cervical (2048x1536).
    Imágenes Papanicolaou/EDF: núcleos oscuros sobre fondo claro.
    Dependencias: CITO-22, CITO-23, CITO-74 completados.
    Evidencia: bitácora, tabla de parámetros y reporte.
    """)
    print()
    
    print("=" * 70)
    print("🔄 EJECUTANDO CALIBRACIONES CITO-97")
    print("=" * 70)
    print()
    
    # 1. Calibrar sigma para imágenes reales
    print("1. Calibrando sigma DoG para imágenes reales...")
    calibrar_sigma_real()
    print()
    
    # 2. Calibrar umbral
    print("2. Calibrando umbral DOG para imágenes reales...")
    calibrar_umbral_real()
    print()
    
    # 3. Calibrar áreas
    print("3. Calibrando áreas mínima/máxima...")
    calibrar_areas_real()
    print()
    
    # 4. Validar con conjunto de prueba
    print("4. Validando con conjunto de prueba separado...")
    validar_con_test_set()
    print()
    
    # 5. Generar tabla de parámetros
    print("5. Generando tabla de parámetros finales...")
    generar_tabla_parametros_final()
    print()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📋 RESUMEN EJECUTIVO CITO-97")
    print("=" * 70)
    
    print("\n🔧 Parámetros calibrados para imágenes reales (2048x1536):")
    print(f"   σ1: {resultados_calibracion.get('sigma1_optimo', 'No calibrado')}")
    print(f"   σ2: {resultados_calibracion.get('sigma2_optimo', 'No calibrado')}")
    print(f"   Umbral DOG: {resultados_calibracion.get('umbral_dog_optimo', 'No calibrado')}")
    print(f"   Área mínima (nucleos-oscuros): {resultados_calibracion.get('area_minima_optima', 'No calibrado')}")
    print(f"   Área máxima (nucleos-oscuros): {resultados_calibracion.get('area_maxima_optima', 'No calibrado')}")
    print(f"   Factor riesgo: 3.0 (regla Dra. Rangel)")
    
    print(f"\n📄 Evidencia generada:")
    print(f"   - Bitácora: {BITACORA_FILE}")
    print(f"   - Tabla de parámetros: docs/parametros_cito97.csv")
    
    print(f"\n✅ CITO-97 finalizado")
    print()
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main_cito97()