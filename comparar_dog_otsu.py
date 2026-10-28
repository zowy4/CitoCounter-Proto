#!/usr/bin/env python3
"""CITO-76: Comparar DoG contra Otsu y línea base documentada.

Ejecuta una comparación exhaustiva del filtro Difference of Gaussians (DoG)
contra umbralización Otsu y una línea base documentada, usando el conjunto de
prueba congelado de CITO-70 (70/20/10 split).

Dependencias: J-07 (calibración sigma), J-08 (métricas CITO-75).
Evidencia: tablas, gráficas por imagen y por conjunto.
"""

import argparse
import math
import os
from pathlib import Path
from typing import List, Tuple, Dict, Optional

import cv2
import numpy as np
from src.preprocessing import preprocesar_imagen
from src.dog_filter import aplicar_filtro_dog
from calcular_metricas_cito75 import (
    matching_por_centroides,
    calcular_precisión,
    calcular_recall,
    calcular_f1,
    parsear_centroides,
)


# ---------------------------------------------------------------------------
# Configuración CITO-74 (calibrado para tesis BM5)
# ---------------------------------------------------------------------------

SIGMA1_CALIBRADO = 5.0
SIGMA2_CALIBRADO = 10.0
UMBRAL_DOG_CALIBRADO = 5
AREA_MINIMA_CALIBRADA = 10
AREA_MAXIMA_CALIBRADA = 500
FACTOR_RIESGO = 3.0
MARGEN_FRONTERA = 0.1

# Rutas por conjunto (CITO-70: 70/20/10 split)
SPLITS = {
    'train': Path('data') / 'raw' / 'train',
    'val': Path('data') / 'raw' / 'val',
    'test': Path('data') / 'raw' / 'test',
}

# Umbral base fijo (de CITO-23 template / línea base documentada)
UMBRAL_BASE = 5  # px, valor documentado en plantilla CITO-23


# ---------------------------------------------------------------------------
# Helper: extraer centroides de contornos
# ---------------------------------------------------------------------------

def centroides_a_partir_contornos(contornos: List[np.ndarray]) -> List[Tuple[float, float]]:
    """Extrae centroides a partir de una lista de contornos de OpenCV."""
    centroides = []
    for cnt in contornos:
        if cnt is None or cnt.size == 0:
            continue
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]
        centroides.append((cx, cy))
    return centroides


# ---------------------------------------------------------------------------
# Helper: aplicar umbralización Otsu
# -------------------------------------------------------------------------__

def aplicar_otsu(imagen_gris: np.ndarray) -> Tuple[np.ndarray, float]:
    """Aplica umbralización Otsu a una imagen en escala de grises.

    Returns:
        (mascara_binaria, umbral_otsu_calculado)
    """
    umbral_otsu = cv2.threshold(imagen_gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0]
    _, mask = cv2.threshold(imagen_gris, umbral_otsu, 255, cv2.THRESH_BINARY)
    return mask, umbral_otsu


# ---------------------------------------------------------------------------
# Helper: aplicar línea base (umbral fijo)
# -------------------------------------------------------------------------__

def aplicar_linea_base(imagen_gris: np.ndarray, umbral: int = UMBRAL_BASE) -> np.ndarray:
    """Aplica umbralización con valor fijo (línea base documentada).

    Args:
        imagen_gris: imagen en escala de grises
        umbral: valor umbral fijo (por defecto 5, de CITO-23 plantilla)

    Returns:
        máscara binaria umbral fija
    """
    _, mask = cv2.threshold(imagen_gris, umbral, 255, cv2.THRESH_BINARY)
    return mask


# ---------------------------------------------------------------------------
# Helper: contar células y extraer centroides de una máscara
# ---------------------------------------------------------------------------

def analizar_mascara(mascara: np.ndarray) -> Dict[str, Optional[object]]:
    """Cuenta células y extrae centroides de una máscara binaria.

    Returns:
        Diccionario con conteo y centroides
    """
    # Encontrar contornos
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    total_celulas = len(contornos)
    centroides = centroides_a_partir_contornos(contornos)

    # Filtrar por área (mínima/máxima calibrada)
    centroides_filtrados = []
    for (cx, cy) in centroides:
        # Área aproximada usando distancia al origen
        area_approx = cx * cy  # simplificación
        if AREA_MINIMA_CALIBRADA <= area_approx <= AREA_MAXIMA_CALIBRADA:
            centroides_filtrados.append((cx, cy))

    return {
        'total_celulas': total_celulas,
        'centroides': centroides,
        'centroides_filtrados': centroides_filtrados,
        'total_filtrados': len(centroides_filtrados),
    }


# ---------------------------------------------------------------------------
# Comparación por imagen
# ---------------------------------------------------------------------------

def comparar_imagen(
    img_path: Path,
    match_distance: float = 10.0,
) -> Dict[str, Optional[object]]:
    """Compara tres métodos (DoG, Otsu, Línea base) en una sola imagen.

    Returns:
        Diccionario con resultados comparativos
    """
    img_name = img_path.name

    # Cargar y preprocesar imagen
    img_procesada, img_original = preprocesar_imagen(
        str(img_path), polaridad='nucleos-claros'
    )

    if img_procesada is None:
        return {
            'imagen': img_name,
            'error': f'No se pudo preprocesar {img_name}',
        }

    # --- MÉTODO 1: DoG (Difference of Gaussians) ---
    imagen_dog = aplicar_filtro_dog(
        img_procesada, sigma1=SIGMA1_CALIBRADO, sigma2=SIGMA2_CALIBRADO
    )

    # Binarizar DoG (usando umbral calibrado)
    _, mask_dog = cv2.threshold(imagen_dog, UMBRAL_DOG_CALIBRADO, 255, cv2.THRESH_BINARY)
    resultado_dog = analizar_mascara(mask_dog)

    # Extraer centroides DoG para matching
    centroides_dog = resultado_dog['centroides_filtrados']

    # --- MÉTODO 2: Otsu ---
    mask_otsu, umbral_otsu = aplicar_otsu(img_procesada)
    resultado_otsu = analizar_mascara(mask_otsu)
    centroides_otsu = resultado_otsu['centroides_filtrados']

    # --- MÉTODO 3: Línea base (umbral fijo) ---
    mask_base = aplicar_linea_base(img_procesada, umbral=UMBRAL_BASE)
    resultado_base = analizar_mascara(mask_base)
    centroides_base = resultado_base['centroides_filtrados']

    # --- Matching de centroides para cada método ---
    # Usar ground truth desde CSV CITO-23
    from calcular_metricas_cito75 import leer_csv_resultados

    # Buscar CSV de resultados para esta imagen
    csv_nombre = img_name.replace('.jpg', '.csv')
    csv_path = Path('data/results') / csv_nombre
    csv_data = leer_csv_resultados(csv_path)

    # Centroides ground truth desde CSV
    gt_centroids_str = csv_data.get('gt_centroids', '') if csv_data else ''
    gt_centroids = parsear_centroides(gt_centroids_str) if gt_centroids_str else []

    # Matching con distancia máxima
    tp_dog, fp_dog, fn_dog = matching_por_centroides(centroides_dog, gt_centroids, match_distance)
    tp_otsu, fp_otsu, fn_otsu = matching_por_centroides(centroides_otsu, gt_centroids, match_distance)
    tp_base, fp_base, fn_base = matching_por_centroides(centroides_base, gt_centroids, match_distance)

    # Métricas derivadas
    precision_dog = calcular_precisión(tp_dog, fp_dog)
    recall_dog = calcular_recall(tp_dog, fn_dog)
    f1_dog = calcular_f1(precision_dog, recall_dog) if (precision_dog + recall_dog) > 0 else 0.0

    precision_otsu = calcular_precisión(tp_otsu, fp_otsu)
    recall_otsu = calcular_recall(tp_otsu, fn_otsu)
    f1_otsu = calcular_f1(precision_otsu, recall_otsu) if (precision_otsu + recall_otsu) > 0 else 0.0

    precision_base = calcular_precisión(tp_base, fp_base)
    recall_base = calcular_recall(tp_base, fn_base)
    f1_base = calcular_f1(precision_base, recall_base) if (precision_base + recall_base) > 0 else 0.0

    # Umbral Otsu reportado
    umbral_otsu_val = umbral_otsu  # valor calculado por Otsu

    return {
        'imagen': img_name,
        # DoG results
        'dog_total_celulas': resultado_dog['total_celulas'],
        'dog_total_filtrados': resultado_dog['total_filtrados'],
        'dog_tp': tp_dog,
        'dog_fp': fp_dog,
        'dog_fn': fn_dog,
        'dog_precision': precision_dog,
        'dog_recall': recall_dog,
        'dog_f1': f1_dog,
        # Otsu results
        'otsu_total_celulas': resultado_otsu['total_celulas'],
        'otsu_total_filtrados': resultado_otsu['total_filtrados'],
        'otsu_tp': tp_otsu,
        'otsu_fp': fp_otsu,
        'otsu_fn': fn_otsu,
        'otsu_precision': precision_otsu,
        'otsu_recall': recall_otsu,
        'otsu_f1': f1_otsu,
        'otsu_umbral': umbral_otsu_val,
        # Línea base results
        'base_total_celulas': resultado_base['total_celulas'],
        'base_total_filtrados': resultado_base['total_filtrados'],
        'base_tp': tp_base,
        'base_fp': fp_base,
        'base_fn': fn_base,
        'base_precision': precision_base,
        'base_recall': recall_base,
        'base_f1': f1_base,
        # Configuración
        'sigma1': SIGMA1_CALIBRADO,
        'sigma2': SIGMA2_CALIBRADO,
        'umbral_dog': UMBRAL_DOG_CALIBRADO,
        'umbral_base': UMBRAL_BASE,
        'match_distance': match_distance,
    }


# ---------------------------------------------------------------------------
# Cálculo por conjunto
# ---------------------------------------------------------------------------

def comparar_conjunto(
    split_name: str,
    match_distance: float = 10.0,
) -> Dict[str, Optional[object]]:
    """Compara todos los métodos en un conjunto de datos completo.

    Args:
        split_name: 'train', 'val' o 'test'
        match_distance: distancia para matching de centroides

    Returns:
        Diccionario con métricas agregadas por conjunto
    """
    split_dir = SPLITS.get(split_name)
    if not split_dir or not split_dir.exists():
        print(f"⚠️  Directorio no encontrado: {split_dir}")
        return {
            'conjunto': split_name,
            'error': f'Directorio no encontrado: {split_dir}',
        }

    # Obtener todas las imágenes JPG del split
    imagenes_jpg = list(split_dir.glob("*.jpg"))
    imagenes_jpeg = list(split_dir.glob("*.jpeg"))
    imagenes = [p.name for p in (imagenes_jpg + imagenes_jpeg)]

    if not imagenes:
        print(f"⚠️  No se encontraron imágenes en {split_dir}")
        return {
            'conjunto': split_name,
            'error': f'No se encontraron imágenes en {split_dir}',
        }

    # Procesar cada imagen
    resultados = []
    for img_name in sorted(imagenes):
        img_path = split_dir / img_name
        resultado = comparar_imagen(img_path, match_distance=match_distance)
        resultados.append(resultado)

    # Calcular métricas agregadas
    n = len(resultados) if resultados else 1

    # Sumar TP/FP/FN por método
    tp_dog = sum(r['dog_tp'] for r in resultados if 'dog_tp' in r)
    fp_dog = sum(r['dog_fp'] for r in resultados if 'dog_fp' in r)
    fn_dog = sum(r['dog_fn'] for r in resultados if 'dog_fn' in r)

    tp_otsu = sum(r['otsu_tp'] for r in resultados if 'otsu_tp' in r)
    fp_otsu = sum(r['otsu_fp'] for r in resultados if 'otsu_fp' in r)
    fn_otsu = sum(r['otsu_fn'] for r in resultados if 'otsu_fn' in r)

    tp_base = sum(r['base_tp'] for r in resultados if 'base_tp' in r)
    fp_base = sum(r['base_fp'] for r in resultados if 'base_fp' in r)
    fn_base = sum(r['base_fn'] for r in resultados if 'base_fn' in r)

    # Métricas por método
    precision_dog = calcular_precisión(tp_dog, fp_dog)
    recall_dog = calcular_recall(tp_dog, fn_dog)
    f1_dog = calcular_f1(precision_dog, recall_dog)

    precision_otsu = calcular_precisión(tp_otsu, fp_otsu)
    recall_otsu = calcular_recall(tp_otsu, fn_otsu)
    f1_otsu = calcular_f1(precision_otsu, recall_otsu)

    precision_base = calcular_precisión(tp_base, fp_base)
    recall_base = calcular_recall(tp_base, fn_base)
    f1_base = calcular_f1(precision_base, recall_base)

    # Estadísticas adicionales
    total_imagenes = n
    dog_promedio_celulas = sum(r.get('dog_total_filtrados', 0) for r in resultados) / n if n > 0 else 0
    otsu_promedio_celulas = sum(r.get('otsu_total_filtrados', 0) for r in resultados) / n if n > 0 else 0
    base_promedio_celulas = sum(r.get('base_total_filtrados', 0) for r in resultados) / n if n > 0 else 0

    # Umbral Otsu promedio
    umbrales_otsu = [r.get('otsu_umbral', 0) for r in resultados if r.get('otsu_umbral') is not None]
    umbral_otsu_promedio = sum(umbrales_otsu) / len(umbrales_otsu) if umbrales_otsu else None

    return {
        'conjunto': split_name,
        'total_imagenes': total_imagenes,
        # DoG métricas
        'dog_tp': tp_dog,
        'dog_fp': fp_dog,
        'dog_fn': fn_dog,
        'dog_precision': precision_dog,
        'dog_recall': recall_dog,
        'dog_f1': f1_dog,
        'dog_promedio_celulas': dog_promedio_celulas,
        # Otsu métricas
        'otsu_tp': tp_otsu,
        'otsu_fp': fp_otsu,
        'otsu_fn': fn_otsu,
        'otsu_precision': precision_otsu,
        'otsu_recall': recall_otsu,
        'otsu_f1': f1_otsu,
        'otsu_umbral_promedio': umbral_otsu_promedio,
        'otsu_promedio_celulas': otsu_promedio_celulas,
        # Línea base métricas
        'base_tp': tp_base,
        'base_fp': fp_base,
        'base_fn': fn_base,
        'base_precision': precision_base,
        'base_recall': recall_base,
        'base_f1': f1_base,
        'base_promedio_celulas': base_promedio_celulas,
        # Configuración
        'sigma1': SIGMA1_CALIBRADO,
        'sigma2': SIGMA2_CALIBRADO,
        'umbral_dog': UMBRAL_DOG_CALIBRADO,
        'umbral_base': UMBRAL_BASE,
        'match_distance': match_distance,
    }


# ---------------------------------------------------------------------------
# Generación de reportes y tablas
# ---------------------------------------------------------------------------

def generar_tabla_comparativa(
    metricas: Dict[str, Optional[object]],
    output_path: Path,
) -> None:
    """Genera una tabla comparativa HTML/texto con los resultados."""
    lines = [
        "=" * 70,
        f"📊 TABLA COMPARATIVA CITO-76: {metricas['conjunto'].upper()}",
        "=" * 70,
        "",
        "📐 Configuración de evaluación:",
        f"   - Sigma1 (DoG): {metricas['sigma1']}",
        f"   - Sigma2 (DoG): {metricas['sigma2']}",
        f"   - Umbral DoG: {metricas['umbral_dog']}",
        f"   - Umbral base (fijo): {metricas['umbral_base']}",
        f"   - Distancia matching: {metricas['match_distance']} px",
        "",
        "📈 Métricas comparativas:",
        "",
        "   Método       | Precision | Recall   | F1-Score | Células Prom",
        "   -------------|-----------|----------|----------|-------------",
        f"   DoG          | {metricas['dog_precision']:.4f} | {metricas['dog_recall']:.4f} | {metricas['dog_f1']:.4f} | {metricas['dog_promedio_celulas']:.1f}",
        f"   Otsu         | {metricas['otsu_precision']:.4f} | {metricas['otsu_recall']:.4f} | {metricas['otsu_f1']:.4f} | {metricas['otsu_promedio_celulas']:.1f}",
        f"   Línea base   | {metricas['base_precision']:.4f} | {metricas['base_recall']:.4f} | {metricas['base_f1']:.4f} | {metricas['base_promedio_celulas']:.1f}",
        "",
        "📋 Resumen:",
        f"   - Total imágenes: {metricas['total_imagenes']}",
        f"   - Mejor F1: {'DoG' if metricas['dog_f1'] >= metricas['otsu_f1'] and metricas['dog_f1'] >= metricas['base_f1'] else 'Otsu' if metricas['otsu_f1'] >= metricas['base_f1'] else 'Línea base'}",
        f"   - Umbral Otsu promedio: {metricas['otsu_umbral_promedio']:.2f}" if metricas['otsu_umbral_promedio'] is not None else "   - Umbral Otsu promedio: N/A",
        "=" * 70,
    ]

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def generar_reporte_resumen(
    metricas_train: Dict,
    metricas_val: Dict,
    metricas_test: Dict,
    output_dir: Path,
) -> None:
    """Genera reporte consolidado con los tres conjuntos."""
    output_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "=" * 70,
        "📊 REPORTE CONSOLIDADO CITO-76: COMPARACIÓN DOG vs OTSU vs BASE",
        "=" * 70,
        "",
        "CONJUNTO TRAIN ({} imágenes):".format(metricas_train['total_imagenes']),
        "  - DoG F1: {:.4f} | Otsu F1: {:.4f} | Base F1: {:.4f}".format(
            metricas_train['dog_f1'], metricas_val['otsu_f1'], metricas_train['base_f1']
        ),
        "",
        "CONJUNTO VAL ({} imágenes):".format(metricas_val['total_imagenes']),
        "  - DoG F1: {:.4f} | Otsu F1: {:.4f} | Base F1: {:.4f}".format(
            metricas_val['dog_f1'], metricas_val['otsu_f1'], metricas_val['base_f1']
        ),
        "",
        "CONJUNTO TEST ({} imágenes):".format(metricas_test['total_imagenes']),
        "  - DoG F1: {:.4f} | Otsu F1: {:.4f} | Base F1: {:.4f}".format(
            metricas_test['dog_f1'], metricas_test['otsu_f1'], metricas_test['base_f1']
        ),
        "",
        "🏆 GANADOR POR CONJUNTO:",
        "  TRAIN: {}".format(
            'DoG' if metricas_train['dog_f1'] >= metricas_train['otsu_f1'] and metricas_train['dog_f1'] >= metricas_train['base_f1']
            else 'Otsu' if metricas_train['otsu_f1'] >= metricas_train['base_f1'] else 'Línea base'
        ),
        "  VAL: {}".format(
            'DoG' if metricas_val['dog_f1'] >= metricas_val['otsu_f1'] and metricas_val['dog_f1'] >= metricas_val['base_f1']
            else 'Otsu' if metricas_val['otsu_f1'] >= metricas_val['base_f1'] else 'Línea base'
        ),
        "  TEST: {}".format(
            'DoG' if metricas_test['dog_f1'] >= metricas_test['otsu_f1'] and metricas_test['dog_f1'] >= metricas_test['base_f1']
            else 'Otsu' if metricas_test['otsu_f1'] >= metricas_test['base_f1'] else 'Línea base'
        ),
        "=" * 70,
    ]

    with open(output_dir / "reporte_consolidado.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------

def main() -> None:
    """Punto de entrada principal para CITO-76."""
    parser = argparse.ArgumentParser(
        description='CITO-76: Comparar DoG contra Otsu y línea base documentada'
    )
    parser.add_argument(
        '--split',
        choices=['train', 'val', 'test', 'all'],
        default='all',
        help='Conjunto de datos a evaluar (default: all)',
    )
    parser.add_argument(
        '--match-distance',
        type=float,
        default=10.0,
        help='Distancia máxima (px) para matching de centroides (default: 10.0)',
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/results/comparacion_dog_otsu',
        help='Directorio de salida para reportes y tablas (default: data/results/comparacion_dog_otsu)',
    )

    args = parser.parse_args()

    # Determinar qué splits procesar
    splits_a_procesar = []
    if args.split == 'all':
        splits_a_procesar = ['train', 'val', 'test']
    else:
        splits_a_procesar = [args.split]

    # Crear directorio de salida
    output_base = Path(args.output)
    output_base.mkdir(parents=True, exist_ok=True)

    # Procesar cada split
    metricas_por_conjunto = {}
    for split_name in splits_a_procesar:
        print(f"\n🔧 Comparando split: {split_name}...")
        metricas = comparar_conjunto(
            split_name=split_name,
            match_distance=args.match_distance,
        )
        metricas_por_conjunto[split_name] = metricas

        # Generar tabla comparativa
        tabla_path = output_base / f"tabla_{split_name}.txt"
        generar_tabla_comparativa(metricas, tabla_path)
        print(f"   📄 Tabla guardada: {tabla_path}")

        # Mostrar resumen rápido
        print(f"   📊 Resumen F1:")
        print(f"     - DoG: {metricas['dog_f1']:.4f}")
        print(f"     - Otsu: {metricas['otsu_f1']:.4f}")
        print(f"     - Línea base: {metricas['base_f1']:.4f}")

        # Contar células promedio
        print(f"   📸 Células promedio:")
        print(f"       - DoG: {metricas['dog_promedio_celulas']:.1f}")
        print(f"       - Otsu: {metricas['otsu_promedio_celulas']:.1f}")
        print(f"       - Línea base: {metricas['base_promedio_celulas']:.1f}")
        if metricas['otsu_umbral_promedio'] is not None:
            print(f"       - Umbral Otsu promedio: {metricas['otsu_umbral_promedio']:.2f}")

    # Generar reporte consolidado si se pidió 'all'
    if args.split == 'all':
        print("\n" + "=" * 60)
        print("📊 REPORTE CONSOLIDADO CITO-76")
        print("=" * 60)

        metricas_train = metricas_por_conjunto.get('train', {})
        metricas_val = metricas_por_conjunto.get('val', {})
        metricas_test = metricas_por_conjunto.get('test', {})

        generar_reporte_resumen(metricas_train, metricas_val, metricas_test, output_base)

        print(f"📄 Reporte consolidado guardado: {output_base / 'reporte_consolidado.txt'}")

        # Mostrar ganador general
        print(f"\n🏆 GANADOR GENERAL:")
        f1_vals = {
            'DoG': metricas_train.get('dog_f1', 0),
            'Otsu': metricas_train.get('otsu_f1', 0),
            'Base': metricas_train.get('base_f1', 0),
        }
        ganador = max(f1_vals, key=f1_vals.get)
        print(f"   Mejor F1 general: {ganador} con F1 = {f1_vals[ganador]:.4f}")


if __name__ == '__main__':
    main()