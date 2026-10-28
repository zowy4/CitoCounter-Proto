"""Barrido reproducible de parametros sigma para la calibracion CITO-22.

El script genera evidencia para comparar configuraciones DoG sobre un conjunto
de calibracion. No selecciona automaticamente un valor clinico: la decision
requiere revisar las detecciones contra anotaciones autorizadas.
"""

import argparse
import csv
from pathlib import Path

import numpy as np

from src.analysis import analizar_nucleos
from src.dog_filter import aplicar_filtro_dog
from src.preprocessing import preprocesar_imagen


EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}


def obtener_imagenes(directorio: Path) -> list[Path]:
    """Devuelve las imagenes compatibles ordenadas por nombre."""
    if not directorio.is_dir():
        raise ValueError(f"No existe el directorio de calibracion: {directorio}")
    imagenes = sorted(
        path for path in directorio.iterdir()
        if path.is_file() and path.suffix.lower() in EXTENSIONES_IMAGEN
    )
    if not imagenes:
        raise ValueError(f"No hay imagenes compatibles en: {directorio}")
    return imagenes


def evaluar_configuracion(
    rutas: list[Path], sigma1: float, sigma2: float
) -> dict[str, float | int]:
    """Evalua una pareja sigma sin afirmar que sea la mejor clinicamente."""
    if sigma1 <= 0 or sigma2 <= sigma1:
        raise ValueError("Se requiere 0 < sigma1 < sigma2")

    totales: list[int] = []
    areas: list[float] = []
    for ruta in rutas:
        imagen_gris, imagen_original = preprocesar_imagen(str(ruta))
        imagen_dog = aplicar_filtro_dog(imagen_gris, sigma1, sigma2)
        resultado = analizar_nucleos(imagen_dog, imagen_original, polaridad='nucleos-claros')
        totales.append(int(resultado["total_celulas"]))
        areas.extend(float(area) for area in resultado["areas"])

    areas_array = np.asarray(areas, dtype=float)
    media_area = float(np.mean(areas_array)) if areas_array.size else 0.0
    desviacion_area = float(np.std(areas_array)) if areas_array.size else 0.0
    cv_area = desviacion_area / media_area if media_area else float("inf")

    return {
        "sigma1": sigma1,
        "sigma2": sigma2,
        "ratio": sigma2 / sigma1,
        "imagenes": len(rutas),
        "imagenes_sin_detecciones": sum(total == 0 for total in totales),
        "detecciones": sum(totales),
        "area_media": media_area,
        "area_std": desviacion_area,
        "coeficiente_variacion_area": cv_area,
    }


def ejecutar_barrido(
    directorio: Path,
    sigmas1: list[float],
    sigmas2: list[float],
    salida: Path,
) -> list[dict[str, float | int]]:
    """Evalua todas las parejas validas y guarda el CSV de evidencia."""
    rutas = obtener_imagenes(directorio)
    resultados = []
    for sigma1 in sigmas1:
        for sigma2 in sigmas2:
            if sigma2 <= sigma1:
                continue
            resultados.append(evaluar_configuracion(rutas, sigma1, sigma2))

    if not resultados:
        raise ValueError("El barrido no contiene parejas sigma validas")

    salida.parent.mkdir(parents=True, exist_ok=True)
    campos = list(resultados[0])
    with salida.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(resultados)
    return resultados


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera evidencia de calibracion DoG para CITO-22"
    )
    parser.add_argument("directorio", type=Path)
    parser.add_argument("--sigma1", nargs="+", type=float, default=[2.0, 3.0, 4.0])
    parser.add_argument("--sigma2", nargs="+", type=float, default=[3.0, 5.0, 6.0, 8.0])
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("data/calibration/cito22_barrido_dog.csv"),
    )
    args = parser.parse_args()

    resultados = ejecutar_barrido(
        args.directorio, args.sigma1, args.sigma2, args.salida
    )
    print(f"Configuraciones evaluadas: {len(resultados)}")
    print(f"Evidencia guardada en: {args.salida}")
    print("La seleccion final requiere revision experta y ground truth autorizado.")


if __name__ == "__main__":
    main()
