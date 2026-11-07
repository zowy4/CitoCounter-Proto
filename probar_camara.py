"""
probar_camara.py - Script de prueba en tiempo real para la cámara integrada o USB (Fase 1.1).

Abre la cámara predeterminada (índice 0), muestra el feed de video en vivo
y permite verificar exposición, ganancia y procesamiento en tiempo real.
Presione 'q' para salir.
"""

import cv2
from src.captura_video import CapturaVideo
from src.analysis import analizar_nucleos
from src.dog_filter import aplicar_filtro_dog


def main() -> None:
    print("Iniciando captura desde la cámara integrada (índice 0)...")
    cap_mgr = CapturaVideo(fuente=0)
    
    if not cap_mgr.abrir():
        print("Error: No se pudo abrir la cámara integrada o USB.")
        return

    print("Cámara abierta correctamente. Presione 'q' en la ventana de video para salir.")
    print("Controles: '+' / '-' para ajustar exposición (si es soportado por el driver).")

    exposicion_actual = -6.0  # Valor típico inicial

    while True:
        frame = cap_mgr.leer_frame()
        if frame is None:
            print("Advertencia: No se pudo leer el frame de la cámara.")
            break

        # Mostrar video en vivo
        display_frame = frame.copy()

        # Opcional: análisis rápido en vivo (DoG)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        try:
            dog = aplicar_filtro_dog(gray, sigma1=7.0, sigma2=8.0)
            resultado = analizar_nucleos(dog, display_frame, polaridad='nucleos-oscuros')
            display_frame = resultado["imagen_procesada"]
        except Exception:
            pass

        try:
            cv2.imshow("CitoCounter-Proto - Vista en Vivo (Cámara)", display_frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('+') or key == ord('='):
                exposicion_actual += 1.0
                cap_mgr.configurar_propiedades(exposicion=exposicion_actual)
                print(f"Exposición ajustada a: {exposicion_actual}")
            elif key == ord('-'):
                exposicion_actual -= 1.0
                cap_mgr.configurar_propiedades(exposicion=exposicion_actual)
                print(f"Exposición ajustada a: {exposicion_actual}")
        except cv2.error:
            # Entorno sin soporte GUI de OpenCV (headless). Simular unos cuantos frames y salir.
            print("Entorno sin soporte de interfaz gráfica (headless). Simulando 30 frames de prueba...")
            import time
            for _ in range(30):
                frame = cap_mgr.leer_frame()
                time.sleep(0.03)
            break

    cap_mgr.cerrar()
    try:
        cv2.destroyAllWindows()
    except cv2.error:
        pass
    print("Prueba de cámara finalizada.")


if __name__ == "__main__":
    main()
