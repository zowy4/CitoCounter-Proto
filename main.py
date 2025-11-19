"""
main.py - Ejecutable Principal de CitoCounter Proto

Este es el punto de entrada del sistema de análisis.
Une todos los módulos en un pipeline de procesamiento secuencial.

USO:
    python main.py

El programa procesará las imágenes en data/raw/ y generará:
- Resultados visuales en data/results/
- Estadísticas en consola
- Ventanas interactivas para análisis

PIPELINE:
    1. Cargar imagen del microscopio
    2. Preprocesamiento (gris + mejora de contraste)
    3. Aplicar filtro DoG
    4. Análisis y clasificación (regla del 3x)
    5. Visualización y generación de reportes
"""

import cv2
import os
import sys
import csv
from datetime import datetime

# Importar módulos del proyecto
from src.preprocessing import preprocesar_imagen, verificar_calidad_imagen
from src.dog_filter import aplicar_filtro_dog, calcular_sigmas_optimas
from src.analysis import analizar_nucleos, generar_reporte_estadistico
from src.visualization import (
    crear_panel_comparativo,
    dibujar_estadisticas_en_imagen,
    guardar_imagen_resultado,
    mostrar_ventanas_analisis,
    crear_vista_deteccion
)


# ============================================================================
# PARÁMETROS DE CONFIGURACIÓN
# ============================================================================
# Estos valores deben ajustarse durante la fase de calibración

# Ruta de la imagen a procesar
RUTA_IMAGEN = "data/raw/image.png"

# Parámetros del filtro DoG (AJUSTAR según tamaño de núcleos)
SIGMA1 = 3.0  # Desenfoque fino - captura detalles pequeños
SIGMA2 = 5.0  # Desenfoque grueso - estructura general
# REGLA: sigma2 debería ser ~1.6x sigma1
# AJUSTE: Si los núcleos miden ~30px de diámetro, usar sigma1=5, sigma2=10

# Opciones de preprocesamiento
MEJORAR_CONTRASTE = True   # Activar si la iluminación es irregular
REDUCIR_RUIDO = False      # Activar solo si hay mucho ruido

# Archivo de bitácora para trazabilidad científica
ARCHIVO_BITACORA = "bitacora_experimentos.csv"


def registrar_en_bitacora(id_prueba, imagen, sigma1, sigma2, resultados, observaciones=""):
    """
    Registra automáticamente los resultados en la bitácora de experimentación.
    
    Esto asegura trazabilidad para justificar parámetros en la tesis (BM5).
    """
    from src.analysis import AREA_PROMEDIO_NUCLEO_NORMAL, FACTOR_RIESGO, AREA_MINIMA_NUCLEO
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    hora_actual = datetime.now().strftime("%H:%M")
    
    # Crear entrada de bitácora
    nueva_fila = [
        id_prueba,
        fecha_actual,
        hora_actual,
        os.path.basename(imagen),
        sigma1,
        sigma2,
        AREA_PROMEDIO_NUCLEO_NORMAL,
        FACTOR_RIESGO,
        AREA_MINIMA_NUCLEO,
        resultados.get('total_celulas', 0),
        resultados.get('normales', 0),
        resultados.get('sospechosas', 0),
        f"{resultados.get('porcentaje_riesgo', 0.0):.1f}",
        "",  # Falsos positivos (manual)
        "",  # Falsos negativos (manual)
        "",  # Precisión estimada (manual)
        observaciones,
        "",  # Calidad DoG (manual)
        "",  # Ajuste siguiente (manual)
        "Sistema"  # Responsable
    ]
    
    # Escribir en CSV
    try:
        with open(ARCHIVO_BITACORA, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(nueva_fila)
        print(f"   ✅ Resultados registrados en bitácora: {id_prueba}")
    except Exception as e:
        print(f"   ⚠️  No se pudo escribir en bitácora: {e}")


def obtener_siguiente_id_prueba():
    """
    Genera el siguiente ID de prueba secuencial (T-001, T-002, etc.).
    """
    try:
        with open(ARCHIVO_BITACORA, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            if len(lineas) <= 1:  # Solo header
                return "T-001"
            ultima_linea = lineas[-1]
            ultimo_id = ultima_linea.split(',')[0]
            if ultimo_id.startswith('T-'):
                numero = int(ultimo_id.split('-')[1]) + 1
                return f"T-{numero:03d}"
    except:
        pass
    return "T-001"


def main():
    """
    Función principal que ejecuta el pipeline completo de análisis.
    """
    
    print("=" * 70)
    print("  CitoCounter Proto - Sistema de Análisis de Células")
    print("  Algoritmo: Diferencia de Gaussiana (DoG)")
    print("  Regla: Núcleos > 3x tamaño promedio = Sospechosos")
    print("=" * 70)
    print()
    
    # ========================================================================
    # FASE 1: CARGA Y PREPROCESAMIENTO
    # ========================================================================
    print("📂 FASE 1: Cargando y preprocesando imagen...")
    print(f"   Archivo: {RUTA_IMAGEN}")
    
    # Verificar que existe la imagen
    if not os.path.exists(RUTA_IMAGEN):
        print(f"\n❌ ERROR: No se encontró la imagen en {RUTA_IMAGEN}")
        print("\n💡 INSTRUCCIONES:")
        print("   1. Coloca tus imágenes de microscopio en la carpeta data/raw/")
        print("   2. Actualiza la variable RUTA_IMAGEN en main.py")
        print("   3. O usa el nombre 'muestra_prueba.jpg' para tu imagen")
        print()
        return
    
    try:
        imagen_gris, imagen_original = preprocesar_imagen(
            RUTA_IMAGEN,
            mejorar_contraste_flag=MEJORAR_CONTRASTE,
            reducir_ruido_flag=REDUCIR_RUIDO
        )
        print("   ✅ Imagen cargada correctamente")
        
        # Verificar calidad de la imagen
        metricas = verificar_calidad_imagen(imagen_gris)
        print(f"   📊 Calidad de imagen:")
        print(f"      - Contraste: {metricas['contraste']:.1f}")
        print(f"      - Brillo promedio: {metricas['brillo_promedio']:.1f}")
        print(f"      - Saturación: {metricas['saturacion']:.1f}%")
        
        if not metricas['es_aceptable']:
            print("   ⚠️  ADVERTENCIAS:")
            for advertencia in metricas['advertencias']:
                print(f"      {advertencia}")
            print()
        
    except Exception as e:
        print(f"\n❌ ERROR en preprocesamiento: {e}")
        return
    
    print()
    
    # ========================================================================
    # FASE 2: APLICAR FILTRO DoG
    # ========================================================================
    print("🔬 FASE 2: Aplicando Filtro de Diferencia de Gaussiana (DoG)...")
    print(f"   Parámetros: σ₁={SIGMA1}, σ₂={SIGMA2}")
    
    try:
        imagen_dog = aplicar_filtro_dog(imagen_gris, sigma1=SIGMA1, sigma2=SIGMA2)
        print("   ✅ Filtro DoG aplicado correctamente")
        print(f"   💡 Resalta estructuras de ~{int((SIGMA2-SIGMA1)*3)} píxeles")
        
    except Exception as e:
        print(f"\n❌ ERROR en filtro DoG: {e}")
        return
    
    print()
    
    # ========================================================================
    # FASE 3: ANÁLISIS Y CLASIFICACIÓN
    # ========================================================================
    print("🧬 FASE 3: Analizando núcleos celulares...")
    print("   Aplicando regla de la Dra. Rangel: Área > 3x = Sospechoso")
    
    try:
        resultados = analizar_nucleos(imagen_dog, imagen_original, mostrar_debug=False)
        print("   ✅ Análisis completado")
        
    except Exception as e:
        print(f"\n❌ ERROR en análisis: {e}")
        return
    
    print()
    
    # ========================================================================
    # FASE 4: GENERACIÓN DE REPORTES
    # ========================================================================
    print("📊 FASE 4: Generando reportes y visualizaciones...")
    
    # Imprimir reporte estadístico
    reporte = generar_reporte_estadistico(resultados)
    print(reporte)
    print()
    
    # Registrar en bitácora de experimentación (para la tesis)
    id_prueba = obtener_siguiente_id_prueba()
    registrar_en_bitacora(
        id_prueba, 
        RUTA_IMAGEN, 
        SIGMA1, 
        SIGMA2, 
        resultados,
        observaciones="Ejecución automática - Revisar manualmente"
    )
    print()
    
    # ========================================================================
    # FASE 5: VISUALIZACIÓN
    # ========================================================================
    print("🖼️  FASE 5: Preparando visualizaciones...")
    
    try:
        # Crear imagen con estadísticas
        imagen_con_stats = dibujar_estadisticas_en_imagen(
            resultados['imagen_procesada'],
            resultados,
            posicion='inferior'
        )
        
        # Crear vista de detección detallada
        imagen_deteccion = crear_vista_deteccion(
            imagen_original,
            resultados['contornos_normales'],
            resultados['contornos_sospechosos'],
            dibujar_contornos=True
        )
        
        # Crear panel comparativo
        panel = crear_panel_comparativo(
            imagenes_dict={
                'original': imagen_original,
                'gris': imagen_gris,
                'dog': imagen_dog,
                'resultado': imagen_con_stats
            },
            titulos_dict={
                'original': '1. Original',
                'gris': '2. Escala de Grises',
                'dog': '3. Filtro DoG',
                'resultado': '4. Deteccion Final'
            },
            filas=2,
            columnas=2
        )
        
        print("   ✅ Visualizaciones creadas")
        
    except Exception as e:
        print(f"\n⚠️  Error en visualización: {e}")
        print("   Continuando sin visualización completa...")
        imagen_con_stats = resultados['imagen_procesada']
        panel = None
    
    print()
    
    # ========================================================================
    # FASE 6: GUARDAR RESULTADOS
    # ========================================================================
    print("💾 FASE 6: Guardando resultados...")
    
    try:
        # Guardar imagen principal
        ruta_guardada = guardar_imagen_resultado(
            imagen_con_stats,
            "resultado_analisis.png"
        )
        print(f"   ✅ Imagen guardada: {ruta_guardada}")
        
        # Guardar panel comparativo
        if panel is not None:
            ruta_panel = guardar_imagen_resultado(
                panel,
                "panel_comparativo.png"
            )
            print(f"   ✅ Panel guardado: {ruta_panel}")
        
    except Exception as e:
        print(f"\n⚠️  Error guardando archivos: {e}")
    
    print()
    
    # ========================================================================
    # FASE 7: VISUALIZACIÓN INTERACTIVA
    # ========================================================================
    print("🖥️  FASE 7: Mostrando ventanas interactivas...")
    print("   (Presiona cualquier tecla para cerrar)")
    print()
    
    ventanas = {
        "Filtro DoG (Bordes Detectados)": imagen_dog,
        "Resultado Final (Verde=Normal | Rojo=Sospechoso)": imagen_con_stats
    }
    
    if panel is not None:
        ventanas["Panel Comparativo Completo"] = panel
    
    mostrar_ventanas_analisis(ventanas, esperar_tecla=True)
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print()
    print("=" * 70)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 70)
    print()
    print("📌 PRÓXIMOS PASOS:")
    print("   1. Revisa las imágenes guardadas en data/results/")
    print("   2. Si hay muchos falsos positivos/negativos, ajusta:")
    print(f"      - SIGMA1 y SIGMA2 (actuales: {SIGMA1}, {SIGMA2})")
    print("      - AREA_PROMEDIO_NUCLEO_NORMAL en src/analysis.py")
    print("   3. Para calibrar con imágenes reales:")
    print("      - Usa imágenes de células 100% normales")
    print("      - Ejecuta la función calibrar_area_promedio()")
    print()


def analizar_carpeta_completa(carpeta_entrada="data/raw", 
                               carpeta_salida="data/results"):
    """
    Función auxiliar para procesar múltiples imágenes en lote.
    
    Útil cuando tienes muchas muestras que analizar.
    
    Args:
        carpeta_entrada (str): Carpeta con las imágenes a procesar
        carpeta_salida (str): Carpeta donde guardar los resultados
    """
    
    print(f"\n🔄 MODO LOTE: Procesando todas las imágenes en {carpeta_entrada}")
    
    # Buscar todas las imágenes
    extensiones_validas = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp']
    archivos_imagen = [
        f for f in os.listdir(carpeta_entrada)
        if os.path.splitext(f)[1].lower() in extensiones_validas
    ]
    
    if len(archivos_imagen) == 0:
        print(f"❌ No se encontraron imágenes en {carpeta_entrada}")
        return
    
    print(f"📁 Encontradas {len(archivos_imagen)} imágenes")
    print()
    
    resultados_totales = []
    
    for i, archivo in enumerate(archivos_imagen, 1):
        print(f"[{i}/{len(archivos_imagen)}] Procesando: {archivo}")
        
        try:
            ruta_completa = os.path.join(carpeta_entrada, archivo)
            
            # Procesar
            imagen_gris, imagen_original = preprocesar_imagen(
                ruta_completa,
                mejorar_contraste_flag=MEJORAR_CONTRASTE
            )
            imagen_dog = aplicar_filtro_dog(imagen_gris, SIGMA1, SIGMA2)
            resultados = analizar_nucleos(imagen_dog, imagen_original)
            
            # Guardar
            imagen_anotada = dibujar_estadisticas_en_imagen(
                resultados['imagen_procesada'],
                resultados
            )
            guardar_imagen_resultado(imagen_anotada, f"resultado_{archivo}")
            
            # Acumular estadísticas
            resultados_totales.append({
                'archivo': archivo,
                'total': resultados['total_celulas'],
                'sospechosas': resultados['sospechosas'],
                'porcentaje': resultados['porcentaje_riesgo']
            })
            
            print(f"   ✅ {resultados['total_celulas']} células, "
                  f"{resultados['sospechosas']} sospechosas "
                  f"({resultados['porcentaje_riesgo']:.1f}%)")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Resumen final
    print("=" * 70)
    print("RESUMEN DEL ANÁLISIS EN LOTE")
    print("=" * 70)
    for res in resultados_totales:
        print(f"{res['archivo']:30s} | "
              f"Total: {res['total']:4d} | "
              f"Sospechosas: {res['sospechosas']:4d} | "
              f"Riesgo: {res['porcentaje']:5.1f}%")
    print("=" * 70)


if __name__ == "__main__":
    """
    Punto de entrada del programa.
    
    Para procesar una imagen: python main.py
    Para procesar múltiples: descomentar analizar_carpeta_completa()
    """
    
    # Modo por defecto: procesar una imagen
    main()
    
    # Modo alternativo: procesar todas las imágenes en data/raw/
    # Descomentar la siguiente línea para activar modo lote:
    # analizar_carpeta_completa()
