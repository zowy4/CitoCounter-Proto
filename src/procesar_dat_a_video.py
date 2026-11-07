"""
procesar_dat_a_video.py - Lee archivos .dat de contornos, los dibuja con matplotlib y genera un video MP4.
"""

from __future__ import annotations

import pathlib
import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo
import matplotlib.pyplot as plt
import numpy as np
import cv2


def procesar_dat_a_imagenes_y_video() -> None:
    base_dir = pathlib.Path(r"C:\Users\zowya\CitoCounter_Proto\data\raw\im_Dyskeratotic")
    output_img_dir = pathlib.Path(r"C:\Users\zowya\CitoCounter_Proto\data\processed\dat_images")
    output_img_dir.mkdir(parents=True, exist_ok=True)
    video_salida = pathlib.Path(r"C:\Users\zowya\CitoCounter_Proto\data\videos\im_Dyskeratotic_dat_secuencia.mp4")
    video_salida.parent.mkdir(parents=True, exist_ok=True)

    # Buscar archivos .dat y agruparlos por prefijo base (ej. 001, 002...)
    dat_files = sorted(list(base_dir.glob("*.dat")))
    if not dat_files:
        print(f"No se encontraron archivos .dat en {base_dir}")
        return

    # Agrupar por prefijo numérico (ej. "001")
    grupos: dict[str, list[pathlib.Path]] = {}
    for f in dat_files:
        # Nombre típico: 001_nuc01.dat o 001_cyt01.dat -> prefijo es los primeros 3 caracteres o antes del '_'
        prefix = f.name.split("_")[0]
        grupos.setdefault(prefix, []).append(f)

    print(f"Se encontraron {len(dat_files)} archivos .dat agrupados en {len(grupos)} muestras.")

    imagenes_generadas: list[pathlib.Path] = []

    # Generar una imagen por cada grupo usando matplotlib
    for prefix in sorted(grupos.keys()):
        fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')

        has_data = False
        for dat_path in grupos[prefix]:
            try:
                # Leer coordenadas x, y separadas por comas
                coords = np.loadtxt(dat_path, delimiter=",", ndmin=2)
                if coords.shape[0] > 0 and coords.shape[1] >= 2:
                    xs = coords[:, 0]
                    ys = coords[:, 1]
                    # Diferenciar color si es núcleo o citoplasma
                    if "nuc" in dat_path.name:
                        ax.plot(xs, ys, color='cyan', linewidth=1.5, label='Núcleo' if '01' in dat_path.name else "")
                        ax.fill(xs, ys, color='cyan', alpha=0.3)
                    else:
                        ax.plot(xs, ys, color='lime', linewidth=1.2, linestyle='--', label='Citoplasma' if '01' in dat_path.name else "")
                    has_data = True
            except Exception as e:
                print(f"Error leyendo {dat_path.name}: {e}")

        if not has_data:
            plt.close(fig)
            continue

        ax.set_xlim(0, 1024)
        ax.set_ylim(1024, 0)  # Invertir eje Y típico de imagen microscópica
        ax.axis('off')

        img_path = output_img_dir / f"sample_{prefix}.png"
        plt.savefig(img_path, bbox_inches='tight', pad_inches=0, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        imagenes_generadas.append(img_path)

    if not imagenes_generadas:
        print("No se pudieron generar imágenes a partir de los archivos .dat.")
        return

    print(f"Se generaron {len(imagenes_generadas)} imágenes con matplotlib. Creando video MP4...")

    # Crear video con OpenCV a partir de las imágenes generadas
    primer_img = cv2.imread(str(imagenes_generadas[0]))
    alto, ancho, _ = primer_img.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 5
    writer = cv2.VideoWriter(str(video_salida), fourcc, fps, (ancho, alto))

    if not writer.isOpened():
        print(f"Error al abrir VideoWriter para {video_salida}")
        return

    for img_p in imagenes_generadas:
        img = cv2.imread(str(img_p))
        if img is not None:
            if img.shape[0] != alto or img.shape[1] != ancho:
                img = cv2.resize(img, (ancho, alto))
            writer.write(img)

    writer.release()
    print(f"Video generado exitosamente desde coordenadas .dat en: {video_salida.absolute()}")


if __name__ == "__main__":
    procesar_dat_a_imagenes_y_video()
