"""
generar_groundtruth_sintetico.py - Fase 2.1 del diagnóstico de ground truth (CITO-23)

Genera un dataset SINTÉTICO de imágenes tipo citología con núcleos de
geometría conocida y sus anotaciones YOLO generadas automáticamente.

PROPÓSITO Y LÍMITES (integridad científica):
- Este dataset valida únicamente el PIPELINE DE MÉTRICAS (TP/FP/FN,
  precisión, recall, F1, IoU) contra verdad conocida al 100%.
- NO sustituye la anotación experta citológica. Ninguna conclusión
  clínica puede derivarse de resultados sobre datos sintéticos.
- El cierre de CITO-22/CITO-23 sigue requiriendo anotaciones de la
  experta sobre imágenes reales (ver data/results/FASE2-diagnostico-groundtruth.md).

Salida (por defecto en data/sintetico/):
    calibracion/images/SINTETICA_001.png   (conjunto de calibración)
    calibracion/labels/SINTETICA_001.txt
    evaluacion/images/SINTETICA_101.png    (conjunto de evaluación SEPARADO)
    evaluacion/labels/SINTETICA_101.txt
    dataset_index.csv                      (ID_Imagen, Nombre_Original, Origen, Nucleos)

Formato de etiqueta YOLO: "clase cx cy w h" normalizado a [0,1].
Clases: 0 = normal, 1 = sospechosa.

POLARIDAD (hallazgo Fase 2.1, ver data/results/FASE2-diagnostico-groundtruth.md):
- 'nucleos-claros' (default): núcleos claros sobre fondo oscuro, tipo
  fluorescencia. Es el dominio que el pipeline DoG+Otsu detecta
  (verificado: 16/16 núcleos en imagen sintética invertida).
- 'nucleos-oscuros': núcleos oscuros sobre fondo claro, tipo campo claro
  (Papanicolaou, como las imágenes reales EDF). El pipeline actual NO
  los detecta (0 detecciones); útil para documentar ese modo de fallo.
Las etiquetas YOLO son puramente geométricas: idénticas en ambas polaridades.

Reproducibilidad: misma semilla => mismo dataset (posiciones idénticas).
"""

import argparse
import csv
import math
import sys
from pathlib import Path

import cv2
import numpy as np

# Coherentes con src/analysis.py (reglas CITO-24)
AREA_PROMEDIO_NUCLEO_NORMAL = 300.0   # px^2
FACTOR_RIESGO = 3.0
UMBRAL_SOSPECHOSO = AREA_PROMEDIO_NUCLEO_NORMAL * FACTOR_RIESGO  # 900 px^2
AREA_MINIMA_NUCLEO = 50.0
AREA_MAXIMA_NUCLEO = 5000.0

CLASE_NORMAL = 0
CLASE_SOSPECHOSA = 1

# Rangos de área de diseño (dentro de los filtros de validez del pipeline)
AREA_NORMAL_MIN = 220.0    # < umbral 900 => clasificable como normal
AREA_NORMAL_MAX = 420.0
AREA_SOSPECHOSA_MIN = 950.0   # > umbral 900 => clasificable como sospechosa
AREA_SOSPECHOSA_MAX = 1500.0  # < AREA_MAXIMA_NUCLEO 5000 => válida

# Colores aproximados de tinción Papanicolaou (BGR)
COLOR_FONDO = np.array([190.0, 185.0, 215.0])     # citoplasma rosado
COLOR_NUCLEO = np.array([120.0, 95.0, 130.0])    # núcleo púrpura oscuro

MARGEN_BORDE = 30      # px de distancia mínima al borde de la imagen
SEPARACION_MIN = 8.0   # px extra entre elipses (sin solapamiento)
INTENTOS_COLOCACION = 300

POLARIDADES = ('nucleos-claros', 'nucleos-oscuros')


def _generar_fondo(rng: np.random.Generator, ancho: int, alto: int) -> np.ndarray:
    """Fondo tipo citología: base rosada + manchas suaves de citoplasma + ruido."""
    imagen = np.empty((alto, ancho, 3), dtype=np.float32)
    imagen[:] = COLOR_FONDO

    # Manchas suaves de citoplasma (bajo contraste)
    for _ in range(int(rng.integers(8, 14))):
        cx = float(rng.uniform(0, ancho))
        cy = float(rng.uniform(0, alto))
        radio = float(rng.uniform(40, 130))
        delta = float(rng.uniform(-18, 18))
        yy, xx = np.mgrid[0:alto, 0:ancho]
        mascara = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * radio ** 2)))
        imagen += delta * mascara[..., None]

    # Ruido de adquisición
    imagen += rng.normal(0.0, 5.0, (alto, ancho, 1)).astype(np.float32)
    return np.clip(imagen, 0, 255)


def _dimensiones_elipse(rng: np.random.Generator, area: float) -> "tuple[float, float]":
    """Semiejes (rx, ry) para un área objetivo, con ligera elipticidad."""
    relacion = float(rng.uniform(0.85, 1.0))  # ry = relacion * rx
    rx = math.sqrt(area / (math.pi * relacion))
    ry = relacion * rx
    return rx, ry


def _colocar_nucleos(rng: np.random.Generator, ancho: int, alto: int,
                     n_normales: int, n_sospechosos: int) -> list:
    """Coloca núcleos sin solaparse ni salirse de la imagen.

    Devuelve lista de dicts: {clase, cx, cy, rx, ry, area}.
    Si no cabe un núcleo tras INTENTOS_COLOCACION intentos, se omite.
    """
    nucleos = []
    for clase, n, a_min, a_max in (
        (CLASE_NORMAL, n_normales, AREA_NORMAL_MIN, AREA_NORMAL_MAX),
        (CLASE_SOSPECHOSA, n_sospechosos, AREA_SOSPECHOSA_MIN, AREA_SOSPECHOSA_MAX),
    ):
        for _ in range(n):
            area = float(rng.uniform(a_min, a_max))
            rx, ry = _dimensiones_elipse(rng, area)
            colocado = False
            for _ in range(INTENTOS_COLOCACION):
                cx = float(rng.uniform(MARGEN_BORDE + max(rx, ry), ancho - MARGEN_BORDE - max(rx, ry)))
                cy = float(rng.uniform(MARGEN_BORDE + max(rx, ry), alto - MARGEN_BORDE - max(rx, ry)))
                valido = True
                for previo in nucleos:
                    dist = math.hypot(cx - previo['cx'], cy - previo['cy'])
                    if dist < (max(rx, ry) + max(previo['rx'], previo['ry'])) + SEPARACION_MIN:
                        valido = False
                        break
                if valido:
                    nucleos.append({'clase': clase, 'cx': cx, 'cy': cy,
                                     'rx': rx, 'ry': ry, 'area': area})
                    colocado = True
                    break
            if not colocado:
                # Imagen saturada: se omite este núcleo (el GT refleja lo colocado)
                continue
    return nucleos


def generar_imagen_sintetica(rng: np.random.Generator, ancho: int, alto: int,
                             n_normales: int, n_sospechosos: int,
                             polaridad: str = 'nucleos-claros'):
    """Genera una imagen sintética y sus núcleos de verdad conocida.

    La geometría (y por tanto el GT YOLO) es idéntica en ambas polaridades;
    solo cambia la intensidad de la imagen final.
    """
    if polaridad not in POLARIDADES:
        raise ValueError(f"polaridad debe ser una de {POLARIDADES}, no {polaridad!r}")

    imagen = _generar_fondo(rng, ancho, alto)
    nucleos = _colocar_nucleos(rng, ancho, alto, n_normales, n_sospechosos)

    for nucleo in nucleos:
        cv2.ellipse(
            imagen,
            (int(round(nucleo['cx'])), int(round(nucleo['cy']))),
            (int(round(nucleo['rx'])), int(round(nucleo['ry']))),
            float(rng.uniform(0, 180)),
            0, 360,
            tuple(COLOR_NUCLEO),
            thickness=-1,
        )

    # Suavizado leve: bordes realistas y detectables por DoG
    imagen = cv2.GaussianBlur(imagen, (3, 3), 1.0)
    imagen = np.clip(imagen, 0, 255)

    if polaridad == 'nucleos-claros':
        # Invertir: núcleos claros sobre fondo oscuro (dominio detectable
        # por el pipeline DoG+Otsu actual; ver hallazgo Fase 2.1)
        imagen = 255.0 - imagen

    return imagen.astype(np.uint8), nucleos


def _linea_yolo(nucleo: dict, ancho: int, alto: int) -> str:
    """Convierte un núcleo a línea YOLO 'clase cx cy w h' normalizada."""
    cx = nucleo['cx'] / ancho
    cy = nucleo['cy'] / alto
    w = (2 * nucleo['rx']) / ancho
    h = (2 * nucleo['ry']) / alto
    return f"{nucleo['clase']} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}"


def generar_conjunto(rng: np.random.Generator, dir_salida: Path, prefijo: str,
                     inicio: int, cantidad: int, ancho: int, alto: int,
                     polaridad: str = 'nucleos-claros') -> list:
    """Genera un conjunto (images/ + labels/) y devuelve filas para el índice."""
    dir_imagenes = dir_salida / 'images'
    dir_etiquetas = dir_salida / 'labels'
    dir_imagenes.mkdir(parents=True, exist_ok=True)
    dir_etiquetas.mkdir(parents=True, exist_ok=True)

    filas = []
    for i in range(cantidad):
        nombre = f"{prefijo}_{inicio + i:03d}.png"
        n_normales = int(rng.integers(10, 17))
        n_sospechosos = int(rng.integers(2, 5))
        imagen, nucleos = generar_imagen_sintetica(rng, ancho, alto,
                                                   n_normales, n_sospechosos,
                                                   polaridad=polaridad)
        cv2.imwrite(str(dir_imagenes / nombre), imagen)
        with (dir_etiquetas / f"{Path(nombre).stem}.txt").open('w', encoding='utf-8') as f:
            for nucleo in nucleos:
                f.write(_linea_yolo(nucleo, ancho, alto) + "\n")
        filas.append({
            'ID_Imagen': nombre,
            'Nombre_Original': nombre,
            'Origen': dir_salida.name,
            'Nucleos': len(nucleos),
        })
    return filas


def generar_dataset(salida: Path, n_calibracion: int, n_evaluacion: int,
                    semilla: int, ancho: int = 512, alto: int = 512,
                    polaridad: str = 'nucleos-claros') -> Path:
    """Genera calibración + evaluación (SEPARADOS) y el índice del dataset."""
    rng = np.random.default_rng(semilla)

    filas_cal = generar_conjunto(rng, salida / 'calibracion', 'SINTETICA',
                                 inicio=1, cantidad=n_calibracion, ancho=ancho,
                                 alto=alto, polaridad=polaridad)
    filas_eval = generar_conjunto(rng, salida / 'evaluacion', 'SINTETICA',
                                  inicio=101, cantidad=n_evaluacion, ancho=ancho,
                                  alto=alto, polaridad=polaridad)

    salida.mkdir(parents=True, exist_ok=True)
    with (salida / 'dataset_index.csv').open('w', encoding='utf-8', newline='') as f:
        escritor = csv.DictWriter(f, fieldnames=['ID_Imagen', 'Nombre_Original', 'Origen', 'Nucleos'])
        escritor.writeheader()
        escritor.writerows(filas_cal + filas_eval)
    return salida / 'dataset_index.csv'


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Genera dataset sintético con GT conocido (Fase 2.1, CITO-23). '
                    'SOLO para validar el pipeline de métricas; no tiene valor clínico.')
    parser.add_argument('--salida', default='data/sintetico',
                        help='Carpeta de salida (default: data/sintetico)')
    parser.add_argument('--calibracion', type=int, default=5,
                        help='Número de imágenes de calibración (default: 5)')
    parser.add_argument('--evaluacion', type=int, default=5,
                        help='Número de imágenes de evaluación (default: 5)')
    parser.add_argument('--semilla', type=int, default=42,
                        help='Semilla para reproducibilidad (default: 42)')
    parser.add_argument('--ancho', type=int, default=512)
    parser.add_argument('--alto', type=int, default=512)
    parser.add_argument('--polaridad', choices=POLARIDADES, default='nucleos-claros',
                        help='nucleos-claros: dominio detectable por el pipeline '
                             '(default); nucleos-oscuros: tipo campo claro real (EDF)')
    args = parser.parse_args()

    if args.calibracion < 1 or args.evaluacion < 1:
        parser.error('--calibracion y --evaluacion deben ser >= 1')

    salida = Path(args.salida)
    indice = generar_dataset(salida, args.calibracion, args.evaluacion,
                             args.semilla, args.ancho, args.alto,
                             polaridad=args.polaridad)

    total = args.calibracion + args.evaluacion
    print(f"Dataset sintético generado en: {salida}")
    print(f"  Calibración: {args.calibracion} imágenes (SINTETICA_001..)")
    print(f"  Evaluación:  {args.evaluacion} imágenes (SINTETICA_101..)")
    print(f"  Semilla:     {args.semilla} (reproducible)")
    print(f"  Polaridad:   {args.polaridad}")
    print(f"  Índice:      {indice}")
    print("ADVERTENCIA: datos sintéticos; validan el pipeline de métricas, "
          "no sustituyen anotación experta.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
