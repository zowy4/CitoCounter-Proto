"""
convertir_imagenes_a_video.py - Módulo para convertir colecciones y datasets de imágenes en videos MP4.

Cumple con los principios de tipado estricto, docstrings en formato NumPy y validaciones de seguridad.
"""

from __future__ import annotations

import pathlib
from typing import List, Optional
import cv2
import numpy as np

from src.segmentador_dl import validar_tamano_imagen, convertir_a_8bit


def convertir_carpeta_a_video(
    carpeta_imagenes: str | pathlib.Path,
    ruta_salida_video: str | pathlib.Path,
    fps: int = 5,
    extensiones: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".bmp", ".tif")
) -> bool:
    """Convierte una secuencia de imágenes en un archivo de video MP4.

    :param carpeta_imagenes: Ruta de la carpeta que contiene las imágenes.
    :type carpeta_imagenes: str | pathlib.Path
    :param ruta_salida_video: Ruta del archivo de video MP4 de salida.
    :type ruta_salida_video: str | pathlib.Path
    :param fps: Fotogramas por segundo del video resultante.
    :type fps: int
    :param extensiones: Extensiones de archivo válidas a buscar.
    :type extensiones: tuple[str, ...]
    :return: True si la conversión fue exitosa, False en caso contrario.
    :rtype: bool
    """
    dir_path = pathlib.Path(carpeta_imagenes)
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: La carpeta de imágenes {dir_path} no existe o no es un directorio.")
        return False

    # Buscar imágenes ordenadas por nombre
    archivos_imagen = sorted(
        [p for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() in extensiones]
    )

    if not archivos_imagen:
        print(f"Advertencia: No se encontraron imágenes con extensiones {extensiones} en {dir_path}.")
        return False

    out_path = pathlib.Path(ruta_salida_video)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Leer primera imagen para determinar dimensiones
    primer_img = cv2.imread(str(archivos_imagen[0]))
    if primer_img is None:
        print(f"Error: No se pudo leer la primera imagen: {archivos_imagen[0]}")
        return False

    alto, ancho, _ = primer_img.shape

    # Configurar VideoWriter con códec MP4V
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (ancho, alto))

    if not writer.isOpened():
        print(f"Error: No se pudo inicializar el VideoWriter para {out_path}")
        return False

    print(f"Convirtiendo {len(archivos_imagen)} imágenes desde '{dir_path.name}' -> '{out_path.name}' (FPS={fps})...")

    for img_path in archivos_imagen:
        img = cv2.imread(str(img_path))
        if img is None:
            continue

        # Redimensionar si las dimensiones difieren de la primera imagen
        if img.shape[0] != alto or img.shape[1] != ancho:
            img = cv2.resize(img, (ancho, alto))

        # Asegurar 8-bit
        img_8bit = convertir_a_8bit(img)
        writer.write(img_8bit)

    writer.release()
    print(f"Video guardado exitosamente en: {out_path.absolute()}")
    return True


def convertir_datasets_principales() -> None:
    """Convierte los datasets estándar del proyecto (como data/raw/ y otros) en videos en data/videos/."""
    base_dir = pathlib.Path("data")
    videos_dir = base_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    # 1. Dataset raw / muestras
    raw_dir = base_dir / "raw"
    if raw_dir.exists():
        convertir_carpeta_a_video(
            carpeta_imagenes=raw_dir,
            ruta_salida_video=videos_dir / "dataset_raw_secuencia.mp4",
            fps=2
        )

    # 2. Si existe otra carpeta relevante (ej. parches o procesados)
    processed_dir = base_dir / "processed" / "herlev_patches"
    if processed_dir.exists():
        convertir_carpeta_a_video(
            carpeta_imagenes=processed_dir,
            ruta_salida_video=videos_dir / "herlev_patches_secuencia.mp4",
            fps=5
        )


if __name__ == "__main__":
    convertir_datasets_principales()
