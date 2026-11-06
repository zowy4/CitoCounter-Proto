"""
main_window.py - Ventana principal de la aplicación Qt (CITO-42).

Presentación construida con PySide6, separada de la lógica de negocio.
Muestra la interfaz gráfica y permite visualizar imágenes y conteos.
"""

import sys
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from qt_app.logic.image_controller import ImageController


class MainWindow(QMainWindow):
    """Ventana principal de CitoCounter Qt App."""

    def __init__(self, controller: ImageController = None) -> None:
        super().__init__()
        self.controller = controller if controller is not None else ImageController()

        self.setWindowTitle("CitoCounter-Proto - Interfaz Qt (CITO-42)")
        self.resize(900, 700)

        self._init_ui()
        self._cargar_imagen_inicial()

    def _init_ui(self) -> None:
        """Inicializa los componentes visuales de la ventana."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Panel izquierdo: Controles
        control_layout = QVBoxLayout()
        
        self.btn_cargar = QPushButton("Cargar Imagen...")
        self.btn_cargar.clicked.connect(self.cargar_imagen_dialogo)
        control_layout.addWidget(self.btn_cargar)

        self.btn_demo = QPushButton("Cargar Imagen Sintética")
        self.btn_demo.clicked.connect(self.cargar_demo)
        control_layout.addWidget(self.btn_demo)

        self.lbl_info = QLabel("Estado: Listo\nImagen: Ninguna")
        self.lbl_info.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        control_layout.addWidget(self.lbl_info)

        control_layout.addStretch()
        main_layout.addLayout(control_layout, stretch=1)

        # Panel derecho: Visualización de imagen
        self.lbl_imagen = QLabel("No hay imagen cargada")
        self.lbl_imagen.setAlignment(Qt.AlignCenter)
        self.lbl_imagen.setStyleSheet("background-color: #2b2b2b; color: #ffffff; border: 1px solid #555;")
        self.lbl_imagen.setMinimumSize(512, 512)
        main_layout.addWidget(self.lbl_imagen, stretch=3)

    def _cargar_imagen_inicial(self) -> None:
        """Carga una imagen de demostración al iniciar para que la app no abra vacía."""
        try:
            img = self.controller.obtener_imagen_demostracion()
            self.mostrar_imagen(img, "Imagen Sintética Inicial")
        except Exception as e:
            self.lbl_info.setText(f"Error al cargar imagen inicial: {e}")

    def cargar_demo(self) -> None:
        """Carga la imagen sintética de demostración."""
        img = self.controller.obtener_imagen_demostracion()
        self.mostrar_imagen(img, "Imagen Sintética de Demostración")

    def cargar_imagen_dialogo(self) -> None:
        """Abre un diálogo de archivos para seleccionar y cargar una imagen."""
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen de Citología", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.tif)"
        )
        if ruta:
            try:
                img = self.controller.cargar_y_validar_imagen(ruta)
                self.mostrar_imagen(img, ruta)
            except Exception as e:
                QMessageBox.critical(self, "Error de Carga", str(e))

    def mostrar_imagen(self, img: np.ndarray, titulo: str) -> None:
        """
        Convierte un arreglo numpy en QPixmap y lo muestra en la interfaz.

        :param img: Arreglo numpy de la imagen (grayscale o RGB).
        :type img: numpy.ndarray
        :param titulo: Descripción o ruta de la imagen.
        :type titulo: str
        """
        if img is None:
            return

        if len(img.shape) == 2:
            height, width = img.shape
            bytes_per_line = width
            q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        else:
            height, width, channel = img.shape
            bytes_per_line = 3 * width
            q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        pixmap = QPixmap.fromImage(q_img)
        self.lbl_imagen.setPixmap(pixmap.scaled(self.lbl_imagen.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.lbl_info.setText(f"Estado: OK\nOrigen: {titulo}\nDimensiones: {width}x{height}")
