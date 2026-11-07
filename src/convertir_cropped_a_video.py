"""
convertir_cropped_a_video.py - Script específico para convertir imágenes .bmp de im_Dyskeratotic/CROPPED en un video MP4 sin saltos negros.
"""

from __future__ import annotations

import pathlib
import cv2
import numpy as np

from src.segmentador_dl import convertir_a_8bit


def convertir_cropped() -> None:
    carpeta_cropped = pathlib.Path(r"C:\Users\zowya\CitoCounter_Proto\data\raw\im_Dyskeratotic\CROPPED")
    salida_video = pathlib.Path(r"C:\Users\zowya\CitoCounter_Proto\data\videos\im_Dyskeratotic_CROPPED_secuencia.mp4")

    if not carpeta_cropped.exists():
        print(f"Error: La carpeta {carpeta_cropped} no existe.")
        return

    # Filtrar estrictamente archivos .bmp
    archivos_bmp = sorted(
        [p for p in carpeta_cropped.iterdir() if p.is_file() and p.suffix.lower() == ".bmp"]
    )

    if not archivos_bmp:
        print(f"Advertencia: No se encontraron archivos .bmp en {carpeta_cropped}")
        return

    salida_video.parent.mkdir(parents=True, exist_ok=True)

    # Leer primera imagen para dimensiones estándar
    primer_img = cv2.imread(str(archivos_bmp[0]))
    if primer_img is None:
        print(f"Error: No se pudo leer la primera imagen BMP: {archivos_bmp[0]}")
        return

    alto, ancho, _ = primer_img.shape

    # Configurar VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 5
    writer = cv2.VideoWriter(str(salida_video), fourcc, fps, (ancho, alto))

    if not writer.isOpened():
        print(f"Error: No se pudo inicializar el VideoWriter para {salida_video}")
        return

    print(f"Convirtiendo {len(archivos_bmp)} archivos .bmp desde 'im_Dyskeratotic/CROPPED' -> '{salida_video.name}'...")

    for img_path in archivos_bmp:
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Advertencia: Omitiendo archivo corrupto o ilegible: {img_path.name}")
            continue

        # Redimensionar al frame base si las dimensiones difieren
        if img.shape[0] != alto or img.shape[1] != ancho:
            img = cv2.resize(img, (ancho, alto), interpolation=cv2.INTER_LANCZOS4)

        img_8bit = convertir_a_8bit(img)
        writer.write(img_8bit)

    writer.release()
    print(f"Video de CROPPED guardado exitosamente en: {salida_video.absolute()}")


if __name__ == "__main__":
    convertir_cropped()
