"""
probar_video_dataset.py - Script para probar el módulo de captura de video (Fase 1.1)
reproduciendo los videos generados a partir del dataset en data/videos/.
"""

from __future__ import annotations

import pathlib
import cv2
from src.captura_video import CapturaVideo
from src.analysis import analizar_nucleos
from src.dog_filter import aplicar_filtro_dog


def main() -> None:
    # Seleccionar uno de los videos generados a partir de los datasets de citología
    videos_disponibles = [
        r"C:\Users\zowya\CitoCounter_Proto\data\videos\im_Dyskeratotic_dat_secuencia.mp4",
        r"C:\Users\zowya\CitoCounter_Proto\data\videos\im_Dyskeratotic_secuencia.mp4",
        r"C:\Users\zowya\CitoCounter_Proto\data\videos\im_Dyskeratotic_CROPPED_secuencia.mp4"
    ]

    ruta_video = None
    for v in videos_disponibles:
        if pathlib.Path(v).exists():
            ruta_video = v
            break

    if ruta_video is None:
        print("No se encontró ningún video en data/videos/. Ejecute primero los conversores de dataset.")
        return

    print(f"Reproduciendo video de prueba del dataset: {pathlib.Path(ruta_video).name}")
    print("Ubicación: " + ruta_video)
    print("Presione 'q' para salir, o 'espacio' para pausar/reanudar.")

    cap_mgr = CapturaVideo(fuente=ruta_video)
    if not cap_mgr.abrir():
        print(f"Error al abrir el video: {ruta_video}")
        return

    while True:
        frame = cap_mgr.leer_frame()
        if frame is None:
            print("Fin del video o error de lectura. Reiniciando bucle de video...")
            # Reiniciar video cerrando y abriendo
            cap_mgr.cerrar()
            cap_mgr = CapturaVideo(fuente=ruta_video)
            cap_mgr.abrir()
            continue

        display_frame = frame.copy()

        # Análisis opcional en tiempo real con DoG
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            dog = aplicar_filtro_dog(gray, sigma1=7.0, sigma2=8.0)
            resultado = analizar_nucleos(dog, display_frame, polaridad='nucleos-oscuros')
            display_frame = resultado["imagen_procesada"]
        except Exception:
            pass

        try:
            cv2.imshow("CitoCounter-Proto - Fase 1.1 Dataset Video Stream", display_frame)
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
        except cv2.error:
            # Modo headless (sin GUI de OpenCV)
            print("Entorno headless detectado. Reproduciendo 50 frames de prueba...")
            import time
            for _ in range(50):
                cap_mgr.leer_frame()
                time.sleep(0.05)
            break

    cap_mgr.cerrar()
    try:
        cv2.destroyAllWindows()
    except cv2.error:
        pass
    print("Prueba de video finalizada correctamente.")


if __name__ == "__main__":
    main()
