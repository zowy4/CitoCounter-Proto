"""
benchmark_cito43.py - Medir tiempo de procesamiento CITO-43

Objetivo: Comparar tiempo de procesamiento manual (uno por uno con GUI)
vs automatizado (lote sin GUI) para el pipeline completo de CitoCounter.

Ejecución:
    python benchmark_cito43.py
    # O con parámetros personalizados:
    python benchmark_cito43.py --sigma1 7.0 --sigma2 8.0 --lotes 5
"""

import os
import sys
import time
import argparse
from pathlib import Path
import cv2
import numpy as np

# Add project to path
sys.path.insert(0, '/workspaces/CitoCounter-Proto')

from src.preprocessing import preprocesar_imagen
from src.dog_filter import aplicar_filtro_dog
from src.analysis import analizar_nucleos
from src.visualization import (
    dibujar_estadisticas_en_imagen,
    crear_panel_comparativo,
    mostrar_ventanas_analisis,
    guardar_imagen_resultado
)


def medir_procesamiento_unico(ruta_imagen, sigma1, sigma2, usar_gui=True):
    """
    Mide el tiempo de procesamiento de una imagen individual.
    
    Args:
        ruta_imagen: Path object a la imagen
        sigma1, sigma2: Parámetros DoG
        usar_gui: Si True, muestra ventanas (modo manual); si False, modo lote
    
    Returns:
        dict con tiempos y resultados
    """
    print(f"\n{'='*60}")
    print(f"  Procesando: {ruta_imagen.name}")
    print(f"{'='*60}")
    
    tiempos = {
        'carga': 0,
        'preprocesamiento': 0,
        'dog_filter': 0,
        'analisis': 0,
        'visualizacion': 0,
        'total': 0
    }
    
    # 1. Cargar imagen
    inicio = time.time()
    img_original = cv2.imread(str(ruta_imagen))
    if img_original is None:
        print(f"❌ No se pudo cargar {ruta_imagen}")
        return None
    tiempos['carga'] = time.time() - inicio
    
    # 2. Preprocesamiento
    inicio = time.time()
    imagen_gris, _ = preprocesar_imagen(
        str(ruta_imagen),
        mejorar_contraste_flag=True,
        reducir_ruido_flag=False,
        polaridad='nucleos-claros'
    )
    tiempos['preprocesamiento'] = time.time() - inicio
    
    # 3. Filtro DoG
    inicio = time.time()
    imagen_dog = aplicar_filtro_dog(imagen_gris, sigma1=sigma1, sigma2=sigma2)
    tiempos['dog_filter'] = time.time() - inicio
    
    # 4. Análisis
    inicio = time.time()
    resultados = analizar_nucleos(imagen_dog, img_original, polaridad='nucleos-claros')
    tiempos['analisis'] = time.time() - inicio
    
    # 5. Visualización (solo en modo manual)
    inicio = time.time()
    if usar_gui:
        try:
            panel = crear_panel_comparativo(
                {
                    'original': img_original,
                    'gris': imagen_gris,
                    'dog': imagen_dog,
                    'resultado': dibujar_estadisticas_en_imagen(
                        resultados['imagen_procesada'], resultados
                    )
                },
                {
                    'original': 'Original',
                    'gris': 'Gris (CLAHE)',
                    'dog': f'DoG (σ1={sigma1}, σ2={sigma2})',
                    'resultado': 'Detección'
                }
            )
            # Mostrar ventana (solo modo manual)
            if usar_gui:
                mostrar_ventanas_analisis({"Panel Comparativo": panel})
            tiempos['visualizacion'] = time.time() - inicio
        except Exception as e:
            print(f"⚠️  Error en visualización: {e}")
            tiempos['visualizacion'] = time.time() - inicio
    else:
        # Modo lote: solo generar panel y guardar, sin mostrar
        try:
            panel = crear_panel_comparativo(
                {
                    'original': img_original,
                    'gris': imagen_gris,
                    'dog': imagen_dog,
                    'resultado': dibujar_estadisticas_en_imagen(
                        resultados['imagen_procesada'], resultados
                    )
                },
                {
                    'original': 'Original',
                    'gris': 'Gris (CLAHE)',
                    'dog': f'DoG (σ1={sigma1}, σ2={sigma2})',
                    'resultado': 'Detección'
                }
            )
            # Guardar en lugar de mostrar
            carpeta_salida = Path("data/results/benchmark_cito43")
            carpeta_salida.mkdir(parents=True, exist_ok=True)
            nombre_base = ruta_imagen.stem
            ruta_salida = carpeta_salida / f"PANEL_{nombre_base}.png"
            cv2.imwrite(str(ruta_salida), panel)
            tiempos['visualizacion'] = time.time() - inicio
        except Exception as e:
            print(f"⚠️  Error generando panel: {e}")
            tiempos['visualizacion'] = time.time() - inicio
    
    tiempos['total'] = sum(tiempos.values())
    
    # Mostrar resultados
    print(f"\n⏱️  Tiempos de procesamiento:")
    print(f"   Carga:      {tiempos['carga']*1000:.1f} ms")
    print(f"   Preproc:    {tiempos['preprocesamiento']*1000:.1f} ms")
    print(f"   DoG Filter: {tiempos['dog_filter']*1000:.1f} ms")
    print(f"   Análisis:   {tiempos['analisis']*1000:.1f} ms")
    print(f"   Visualización: {tiempos['visualizacion']*1000:.1f} ms")
    print(f"   TOTAL:      {tiempos['total']*1000:.1f} ms")
    
    return {'tiempos': tiempos, 'resultados': resultados}


def benchmark_lote(ruta_carpeta, sigma1, sigma2, num_imagenes=None, usar_gui=False):
    """
    Ejecuta benchmark en lote sobre múltiples imágenes.
    
    Args:
        ruta_carpeta: Carpeta con imágenes
        sigma1, sigma2: Parámetros DoG
        num_imagenes: Número de imágenes a procesar (None = todas)
        usar_gui: Si True, modo manual con GUI; si False, modo lote
    
    Returns:
        lista de resultados por imagen
    """
    print(f"\n{'='*60}")
    print(f"  BENCHMARK LOTE CITO-43")
    print(f"{'='*60}")
    print(f"Modo: {'Manual (con GUI)' if usar_gui else 'Automatizado (sin GUI)'}")
    print(f"Imágenes: {num_imagenes if num_imagenes else 'todas'}")
    print(f"σ1={sigma1}, σ2={sigma2}")
    
    data_dir = Path(ruta_carpeta)
    if not data_dir.exists():
        print(f"❌ Directorio {ruta_carpeta} no existe")
        return []
    
    # Obtener imágenes
    imagenes = sorted(data_dir.glob("MUESTRA_*.jpg"))
    if not imagenes:
        print(f"❌ No hay imágenes en {ruta_carpeta}")
        return []
    
    if num_imagenes:
        imagenes = imagenes[:num_imagenes]
    
    print(f"\n📸 Procesando {len(imagenes)} imágenes...")
    print()
    
    resultados = []
    for i, ruta_imagen in enumerate(imagenes, 1):
        print(f"[{i}/{len(imagenes)}] ", end="")
        resultado = medir_procesamiento_unico(ruta_imagen, sigma1, sigma2, usar_gui=usar_gui)
        if resultado:
            resultados.append(resultado)
        print()
    
    return resultados


def generar_reporte(resultados_manual, resultados_automatizado, sigma1, sigma2):
    """Genera un reporte comparativo de los benchmarks."""
    print("\n" + "="*70)
    print("  📊 REPORTE COMPARATIVO CITO-43")
    print("="*70)
    
    # Calcular promedios
    if resultados_manual and resultados_automatizado:
        # Tomar el primer resultado de cada uno (usando misma imagen)
        manual_total = resultados_manual[0]['tiempos']['total']
        auto_total = resultados_automatizado[0]['tiempos']['total']
        
        print(f"\nConfiguración: σ1={sigma1}, σ2={sigma2}")
        print(f"\nTiempos por imagen (promedio):")
        print(f"   Modo Manual (con GUI):     {manual_total*1000:.1f} ms")
        print(f"   Modo Automatizado (lote):  {auto_total*1000:.1f} ms")
        print(f"   Ahorro:                    {((manual_total - auto_total)/manual_total*100):.1f}%")
        
        # Desglose por etapa
        print(f"\nDesglose de tiempo (modo automatizado):")
        for etapa in ['carga', 'preprocesamiento', 'dog_filter', 'analisis', 'visualizacion']:
            if etapa in resultados_automatizado[0]['tiempos']:
                t = resultados_automatizado[0]['tiempos'][etapa]
                print(f"   {etapa:15s}: {t*1000:8.1f} ms")
        
        # Eficiencia
        print(f"\n📈 Eficiencia del procesamiento automatizado:")
        print(f"   • Sin overhead de GUI: ~{manual_total*1000 - auto_total*1000:.0f} ms ahorrados por imagen")
        print(f"   • Ideal para procesamiento por lotes de >10 imágenes")
        print(f"   • Modo manual recomendado para depuración y validación")
        
    else:
        print("⚠️  No hay suficientes resultados para comparar")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark de procesamiento CITO-43: Manual vs Automatizado"
    )
    parser.add_argument('--sigma1', type=float, default=7.0, help='Sigma1 para DoG (default: 7.0)')
    parser.add_argument('--sigma2', type=float, default=8.0, help='Sigma2 para DoG (default: 8.0)')
    parser.add_argument('--lotes', type=int, default=3, help='Número de imágenes a probar (default: 3)')
    parser.add_argument('--modo', choices=['manual', 'automatizado', 'ambos'], default='ambos', help='Modo de ejecución')
    
    args = parser.parse_args()
    
    print("="*70)
    print("  🚀 CITO-43: Benchmark de Procesamiento")
    print("="*70)
    print(f"Parámetros: σ1={args.sigma1}, σ2={args.sigma2}")
    print(f"Imágenes a probar: {args.lotes}")
    print(f"Modo: {args.modo}")
    print()
    
    # Ejecutar benchmarks según modo
    resultados_manual = []
    resultados_automatizado = []
    
    if args.modo in ['manual', 'ambos']:
        print("▶ Ejecutando benchmark MANUAL (con GUI)...")
        resultados_manual = benchmark_lote(
            'data/raw', 
            args.sigma1, 
            args.sigma2, 
            num_imagenes=args.lotes,
            usar_gui=True
        )
        print()
    
    if args.modo in ['automatizado', 'ambos']:
        print("▶ Ejecutando benchmark AUTOMATIZADO (lote sin GUI)...")
        resultados_automatizado = benchmark_lote(
            'data/raw', 
            args.sigma1, 
            args.sigma2, 
            num_imagenes=args.lotes,
            usar_gui=False
        )
        print()
    
    # Generar reporte comparativo
    generar_reporte(resultados_manual, resultados_automatizado, args.sigma1, args.sigma2)
    
    # Guardar resultados en JSON para análisis posterior
    import json
    from datetime import datetime
    
    reporte = {
        'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'sigma1': args.sigma1,
        'sigma2': args.sigma2,
        'modo_manual': len(resultados_manual),
        'modo_automatizado': len(resultados_automatizado),
        'resultados_manual': [r['tiempos'] for r in resultados_manual],
        'resultados_automatizado': [r['tiempos'] for r in resultados_automatizado]
    }
    
    archivo_salida = Path("data/results/benchmark_cito43.json")
    archivo_salida.parent.mkdir(parents=True, exist_ok=True)
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados guardados en: {archivo_salida}")
    print("="*70)


if __name__ == "__main__":
    main()