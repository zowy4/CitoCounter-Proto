"""
main.py - Punto de entrada para la aplicación Qt de CitoCounter (CITO-42).

Inicializa la aplicación PySide6 y muestra la ventana principal.
"""

import os
import sys
import cv2

os.environ["OPENCV_VIDEOIO_DEBUG"] = "0"
os.environ["OPENCV_LOG_LEVEL"] = "FATAL"

from PySide6.QtWidgets import QApplication

from qt_app.presentation.main_window import MainWindow



def main() -> None:
    """Función principal para ejecutar la interfaz Qt."""
    try:
        cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_FATAL)
    except Exception:
        pass

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
