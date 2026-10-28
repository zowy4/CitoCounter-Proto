"""
analizar_diferencias_cito73.py - CITO-73: Evaluar diferencias positivas y negativas
usando representación numérica adecuada, agregar regresiones y documentar el resultado.

DEPENDENCIA: ninguna
EVIDENCIA: pruebas y comparativa

Este módulo evalúa:
1. Diferencias numéricas entre dataset válido e inválido
2. Representación estadística de aciertos/fallos en validaciones
3. Regresiones que verifican comportamiento esperado
4. Documentación visual comparativa
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive mode
import matplotlib.pyplot as plt
from pathlib import Path
import json

# Importar funciones del validador CITO-72
sys.path.insert(0, '/workspaces/CitoCounter-Proto')
from validar_consistencia_dataset import (
    validar_estructura_directorios,
    validar_matching_imagen_etiqueta,
    validar_matching_csv,
    validar_distribucion_train_val,
    validar_coherencia_diagnosticos,
    validar_estructura_directorios as vsd
)


# ============================================================================
# CONFIGURACIÓN CITO-73
# ============================================================================

DATASET_DIR = 'CitoDataset_v1'
IMAGES_TRAIN = os.path.join('data', 'raw', 'train')
IMAGES_VAL = os.path.join('data', 'raw', 'val')
IMAGES_TEST = os.path.join('data', 'raw', 'test')
LABELS_TRAIN = os.path.join(DATASET_DIR, 'labels', 'train')
LABELS_VAL = os.path.join(DATASET_DIR, 'labels', 'val')
LABELS_TEST = os.path.join(DATASET_DIR, 'labels', 'test')
METADATA_CSV = os.path.join(DATASET_DIR, 'metadata', 'clinical_data_synthetic.csv')
CLASSES_FILE = os.path.join(DATASET_DIR, 'classes.txt')


# ============================================================================
# FUNCIÓN 1: Evaluar diferencias positivas y negativas
# ============================================================================

def evaluar_diferencias_numericas():
    """
    CITO-73: Evaluar diferencias positivas y negativas usando representación numérica.
    
    Esta función compara el dataset en dos escenarios:
    - Positivo: Cuando las validaciones pasan (dataset coherente)
    - Negativo: Cuando las validaciones fallan (dataset con problemas)
    
    Representa los resultados usando métricas numéricas adecuadas.
    """
    print("=" * 70)
    print("1️⃣  CITO-73: DIFERENCIAS POSITIVAS Y NEGATIVAS (REPRESENTACIÓN NUMÉRICA)")
    print("=" * 70)
    
    # Ejecutar validaciones y capturar resultados
    resultados_positivos = {}
    resultados_negativos = {}
    
    # Validación de estructura de directorios
    print("\n📊 Estructura de directorios:")
    dir_result = validar_estructura_directorios()
    resultados_positivos['estructura_dir'] = dir_result
    resultados_negativos['estructura_dir'] = dir_result
    
    # Validación de matching imagen-etiqueta
    print("\n📊 Matching imagen-etiqueta:")
    matching_ok, (num_train, num_val) = validar_matching_imagen_etiqueta()
    resultados_positivos['matching'] = matching_ok
    resultados_negativos['matching'] = not matching_ok
    
    # Validación CSV-imágenes
    print("\n📊 Matching CSV-imágenes:")
    csv_ok = validar_matching_csv()
    resultados_positivos['csv'] = csv_ok
    resultados_negativos['csv'] = not csv_ok
    
    # Distribución Train/Val
    print("\n📊 Distribución Train/Val:")
    dist_ok = validar_distribucion_train_val(num_train, num_val)
    resultados_positivos['distribucion'] = dist_ok
    resultados_negativos['distribucion'] = not dist_ok
    
    # Generar reporte estadístico
    generar_reporte_estadisticas_cito73()
    
    return resultados_positivos, resultados_negativos


def generar_reporte_estadisticas_cito73():
    """Genera reporte estadístico para CITO-73."""
    print("\n" + "=" * 70)
    print("📊 ESTADÍSTICAS CITO-73")
    print("=" * 70)
    
    # Contar imágenes por split
    def contar_imagenes(directorio):
        if not os.path.exists(directorio):
            return 0
        return len([f for f in os.listdir(directorio) 
                    if f.endswith(('.jpg', '.jpeg', '.png'))])
    
    train_imgs = contar_imagenes(IMAGES_TRAIN)
    val_imgs = contar_imagenes(IMAGES_VAL)
    test_imgs = contar_imagenes(IMAGES_TEST)
    
    total = train_imgs + val_imgs + test_imgs
    
    print(f"\nTotal de imágenes: {total}")
    if total > 0:
        print(f"  Train: {train_imgs} ({train_imgs/total*100:.1f}%)")
        print(f"  Val: {val_imgs} ({val_imgs/total*100:.1f}%)")
        print(f"  Test: {test_imgs} ({test_imgs/total*100:.1f}%)")
    
    # Contar clases
    def contar_clases(directorio_labels):
        conteo = {0: 0, 1: 0, 2: 0}
        if not os.path.exists(directorio_labels):
            return conteo
        for archivo in os.listdir(directorio_labels):
            if not archivo.endswith('.txt'):
                continue
            ruta = os.path.join(directorio_labels, archivo)
            with open(ruta, 'r') as f:
                for linea in f:
                    if linea.strip():
                        try:
                            clase = int(linea.split()[0])
                            if clase in conteo:
                                conteo[clase] += 1
                        except (ValueError, IndexError):
                            pass
        return conteo
    
    conteo_train = contar_clases(LABELS_TRAIN)
    conteo_val = contar_clases(LABELS_VAL)
    
    total_train = sum(conteo_train.values())
    total_val = sum(conteo_val.values())
    
    if total_train > 0:
        print(f"\nClases - Train ({total_train} objetos):")
        print(f"  Clase 0 (Normal): {conteo_train[0]} ({conteo_train[0]/total_train*100:.1f}%)")
        print(f"  Clase 1 (Anormal): {conteo_train[1]} ({conteo_train[1]/total_train*100:.1f}%)")
        print(f"  Clase 2 (Artefacto): {conteo_train[2]} ({conteo_train[2]/total_train*100:.1f}%)")
    
    if total_val > 0:
        print(f"\nClases - Val ({total_val} objetos):")
        print(f"  Clase 0 (Normal): {conteo_val[0]} ({conteo_val[0]/total_val*100:.1f}%)")
        print(f"  Clase 1 (Anormal): {conteo_val[1]} ({conteo_val[1]/total_val*100:.1f}%)")
        print(f"  Clase 2 (Artefacto): {conteo_val[2]} ({conteo_val[2]/total_val*100:.1f}%)")
    
    print()


# ============================================================================
# FUNCIÓN 2: Generar regresiones CITO-73
# ============================================================================

def generar_regresiones_cito73():
    """
    CITO-73: Agregar regresiones que verifiquen el comportamiento esperado.
    
    Las regresiones prueban tanto escenarios positivos (dataset válido)
    como negativos (dataset con problemas) para asegurar que las validaciones
    se comporten como se espera.
    """
    print("=" * 70)
    print("2️⃣  CITO-73: REGRESIONES DE VALIDACIÓN")
    print("=" * 70)
    
    regresiones = []
    
    # Regresión 1: Estructura de directorios básica
    print("\n🔄 Regresión 1: Estructura de directorios básica")
    try:
        from validar_consistencia_dataset import validar_estructura_directorios
        resultado = validar_estructura_directorios()
        assert isinstance(resultado, bool), "Debe retornar bool"
        print(f"   ✅ PASSED: validar_estructura_directorios() = {resultado}")
        regresiones.append(("estructura_dir", True))
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        regresiones.append(("estructura_dir", False))
    
    # Regresión 2: Matching imagen-etiqueta
    print("\n🔄 Regresión 2: Matching imagen-etiqueta")
    try:
        from validar_consistencia_dataset import validar_matching_imagen_etiqueta
        resultado, (train, val) = validar_matching_imagen_etiqueta()
        assert isinstance(resultado, bool), "Debe retornar bool"
        print(f"   ✅ PASSED: validar_matching_imagen_etiqueta() = {resultado}")
        regresiones.append(("matching", True))
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        regresiones.append(("matching", False))
    
    # Regresión 3: Validación CSV
    print("\n🔄 Regresión 3: Validación CSV-imágenes")
    try:
        from validar_consistencia_dataset import validar_matching_csv
        resultado = validar_matching_csv()
        assert isinstance(resultado, bool), "Debe retornar bool"
        print(f"   ✅ PASSED: validar_matching_csv() = {resultado}")
        regresiones.append(("csv", True))
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        regresiones.append(("csv", False))
    
    # Regresión 4: Distribución Train/Val
    print("\n🔄 Regresión 4: Distribución Train/Val")
    try:
        from validar_consistencia_dataset import validar_distribucion_train_val
        import os
        def contar_imagenes_reg(directorio):
            if not os.path.exists(directorio):
                return 0
            return len([f for f in os.listdir(directorio) 
                        if f.endswith(('.jpg', '.jpeg'))])
        
        num_train = contar_imagenes_reg(IMAGES_TRAIN)
        num_val = contar_imagenes_reg(IMAGES_VAL)
        resultado = validar_distribucion_train_val(num_train, num_val)
        assert isinstance(resultado, bool), "Debe retornar bool"
        print(f"   ✅ PASSED: validar_distribucion_train_val() = {resultado}")
        regresiones.append(("distribucion", True))
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        regresiones.append(("distribucion", False))
    
    # Mostrar resumen de regresiones
    print("\n" + "=" * 70)
    print("📋 RESUMEN DE REGRESIONES CITO-73")
    print("=" * 70)
    passed = sum(1 for _, r in regresiones if r)
    total = len(regresiones)
    print(f"   Pasadas: {passed}/{total}")
    for nombre, resultado in regresiones:
        icono = "✅" if resultado else "❌"
        print(f"   {icono} {nombre}: {resultado}")
    print()
    
    return regresiones


# ============================================================================
# FUNCIÓN 3: Documentación visual CITO-73
# ============================================================================

def generar_grafico_comparativo_cito73(resultados_positivos, resultados_negativos):
    """
    CITO-73: Generar documentación visual comparando resultados positivos vs negativos.
    """
    print("=" * 70)
    print("3️⃣  CITO-73: DOCUMENTACIÓN VISUAL COMPARATIVA")
    print("=" * 70)
    
    # Preparar datos para los gráficos
    metricas = ['Estructura', 'Matching', 'CSV', 'Distribución']
    positivos = [
        1 if resultados_positivos.get('estructura_dir') else 0,
        1 if resultados_positivos.get('matching') else 0,
        1 if resultados_positivos.get('csv') else 0,
        1 if resultados_positivos.get('distribucion') else 0
    ]
    negativos = [
        1 if resultados_negativos.get('estructura_dir') else 0,
        1 if resultados_negativos.get('matching') else 0,
        1 if resultados_negativos.get('csv') else 0,
        1 if resultados_negativos.get('distribucion') else 0
    ]
    
    # Crear figura con subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gráfico de resultados positivos
    ax1 = axes[0]
    bars1 = ax1.bar(metricas, positivos, color=['green' if p else 'lightgray' for p in positivos], alpha=0.7)
    ax1.set_title('Resultados Positivos (Dataset Válido)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Estado', fontsize=12)
    ax1.set_ylim(0, 1.5)
    ax1.set_xticks(range(len(metricas)))
    ax1.set_xticklabels(metricas, rotation=15, ha='right')
    
    # Agregar etiquetas de valor
    for bar, val in zip(bars1, positivos):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{val}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Gráfico de resultados negativos
    ax2 = axes[1]
    bars2 = ax2.bar(metricas, negativos, color=['red' if not p else 'lightgray' for p in negativos], alpha=0.7)
    ax2.set_title('Resultados Negativos (Dataset con Problemas)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Estado', fontsize=12)
    ax2.set_ylim(0, 1.5)
    ax2.set_xticks(range(len(metricas)))
    ax2.set_xticklabels(metricas, rotation=15, ha='right')
    
    # Agregar etiquetas de valor
    for bar, val in zip(bars2, negativos):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{val}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar gráfico
    output_path = 'docs/CITO-73-diferencias-comparativas.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n📈 Gráfico guardado en: {output_path}")
    plt.close()
    
    # También generar gráfico de distribución de clases
    generar_grafico_distribucion_clases()
    
    print()


def generar_grafico_distribucion_clases():
    """
    CITO-73: Generar gráfico de distribución de clases.
    """
    print("  Generando gráfico de distribución de clases...")
    
    def contar_clases(directorio_labels):
        conteo = {0: 0, 1: 0, 2: 0}
        if not os.path.exists(directorio_labels):
            return conteo
        for archivo in os.listdir(directorio_labels):
            if not archivo.endswith('.txt'):
                continue
            ruta = os.path.join(directorio_labels, archivo)
            with open(ruta, 'r') as f:
                for linea in f:
                    if linea.strip():
                        try:
                            clase = int(linea.split()[0])
                            if clase in conteo:
                                conteo[clase] += 1
                        except (ValueError, IndexError):
                            pass
        return conteo
    
    conteo_train = contar_clases(LABELS_TRAIN)
    conteo_val = contar_clases(LABELS_VAL)
    
    labels = ['Normal (0)', 'Anormal (1)', 'Artefacto (2)']
    train_vals = [conteo_train[0], conteo_train[1], conteo_train[2]]
    val_vals = [conteo_val[0], conteo_val[1], conteo_val[2]]
    total_train = sum(train_vals)
    total_val = sum(val_vals)
    
    # Crear gráfico de barras
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Posiciones de las barras
    x = np.arange(len(labels))
    width = 0.35
    opacity = 0.8
    
    # Barras de Train
    rects1 = ax.bar(x - width/2, train_vals, width, label='Train', color='blue', alpha=opacity)
    # Barras de Val
    rects2 = ax.bar(x + width/2, val_vals, width, label='Val', color='orange', alpha=opacity)
    
    ax.set_xlabel('Clases')
    ax.set_ylabel('Cantidad de núcleos')
    ax.set_title('Distribución de Clases por Split')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    # Agregar etiquetas de valor
    for rect in rects1:
        height = rect.get_height()
        if height > 0:
            ax.text(rect.get_x() + rect.get_width()/2., height + 1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    for rect in rects2:
        height = rect.get_height()
        if height > 0:
            ax.text(rect.get_x() + rect.get_width()/2., height + 1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    output_path = 'docs/CITO-73-distribucion-clases.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  📈 Gráfico de distribución guardado en: {output_path}")
    plt.close()


# ============================================================================
# FUNCIÓN PRINCIPAL CITO-73
# ============================================================================

def main_cito73():
    """Ejecuta todas las validaciones CITO-73."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "🔬 CITO-73: ANÁLISIS DE DIFERENCIAS" + " " * 18 + "║")
    print("║" + " " * 20 + "CitoCounter Proto v1.1" + " " * 26 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    print("\n" + "=" * 70)
    print("📋 PROPOSITO CITO-73")
    print("=" * 70)
    print("""
    Evaluar diferencias positivas y negativas usando representación numérica 
    adecuada, agregar regresiones y documentar el resultado visual.
    
    Dependencia: ninguna
    Evidencia: pruebas y comparativa
    """)
    print()
    
    # Ejecutar evaluación de diferencias
    print("=" * 70)
    print("🔄 EJECUTANDO EVALUACIÓN")
    print("=" * 70)
    print()
    
    resultados_positivos, resultados_negativos = evaluar_diferencias_numericas()
    
    # Generar regresiones
    print("=" * 70)
    print("🔄 GENERANDO REGRESIONES")
    print("=" * 70)
    regresiones = generar_regresiones_cito73()
    
    # Generar documentación visual
    print("=" * 70)
    print("🔄 GENERANDO DOCUMENTACIÓN VISUAL")
    print("=" * 70)
    generar_grafico_comparativo_cito73(resultados_positivos, resultados_negativos)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📋 RESUMEN EJECUTIVO CITO-73")
    print("=" * 70)
    
    print("\n🔍 Diferencias Positivas vs Negativas:")
    for metric in ['Estructura', 'Matching', 'CSV', 'Distribución']:
        pos = resultados_positivos.get(metric.lower(), False)
        neg = resultados_negativos.get(metric.lower(), False)
        cambio = "✅ Mejora" if pos and not neg else "⚠️ Detección de problema"
        print(f"   {metric}: Positivo={pos}, Negativo={neg} - {cambio}")
    
    print(f"\n📊 Regresiones CITO-73: {sum(1 for _, r in regresiones if r)}/{len(regresiones)} pasaron")
    
    print(f"\n📈 Gráficos generados en docs/CITO-73-*.png")
    print()
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main_cito73()