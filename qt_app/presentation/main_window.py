"""
main_window.py - Ventana principal de la aplicación Qt (CITO-42 / CITO-65).

Presentación construida con PySide6, separada de la lógica de negocio.
Muestra la interfaz gráfica y permite visualizar imágenes y overlays de clasificación.
"""

import sys
import cv2
import numpy as np
from PySide6.QtCore import Qt
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
    QComboBox,
    QTabWidget,
)

from qt_app.logic.image_controller import ImageController
from qt_app.presentation.visor_imagen import VisorImagen
from qt_app.presentation.panel_ajustes import PanelAjustes
from qt_app.presentation.dashboard_widget import DashboardWidget
from src.analysis import analizar_nucleos
from src.dog_filter import aplicar_filtro_dog
from src.segmentador_dl import analizar_nucleos_dl


class MainWindow(QMainWindow):
    """Ventana principal de CitoCounter Qt App con VisorImagen y overlays."""

    def __init__(self, controller: ImageController = None) -> None:
        super().__init__()
        self.controller = controller if controller is not None else ImageController()

        self.setWindowTitle("CitoCounter-Proto - Visor con Overlays (CITO-65)")
        self.resize(1000, 750)

        self._init_ui()
        self._cargar_imagen_inicial()

    def _init_ui(self) -> None:
        """Inicializa los componentes visuales de la ventana con pestañas (Análisis y Dashboard)."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Pestaña 1: Análisis y Visor
        tab_analisis = QWidget()
        analisis_layout = QHBoxLayout(tab_analisis)

        # Panel izquierdo: Controles y análisis
        control_layout = QVBoxLayout()
        
        self.btn_cargar = QPushButton("Cargar Imagen...")
        self.btn_cargar.clicked.connect(self.cargar_imagen_dialogo)
        control_layout.addWidget(self.btn_cargar)

        self.btn_demo = QPushButton("Cargar Imagen Sintética")
        self.btn_demo.clicked.connect(self.cargar_demo)
        control_layout.addWidget(self.btn_demo)

        # Panel de ajustes (CITO-66)
        self.panel_ajustes = PanelAjustes()
        self.panel_ajustes.parametros_cambiados.connect(self.ejecutar_analisis)
        control_layout.addWidget(self.panel_ajustes)

        self.btn_analizar = QPushButton("Ejecutar Análisis y Overlays")
        self.btn_analizar.clicked.connect(self.ejecutar_analisis)
        control_layout.addWidget(self.btn_analizar)

        self.lbl_info = QLabel("Estado: Listo\nImagen: Ninguna\nCélulas: 0")
        self.lbl_info.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        control_layout.addWidget(self.lbl_info)

        control_layout.addStretch()
        analisis_layout.addLayout(control_layout, stretch=1)

        # Panel derecho: Visor gráfico con overlays
        self.visor = VisorImagen(self)
        self.visor.setMinimumSize(600, 600)
        analisis_layout.addWidget(self.visor, stretch=3)

        self.tabs.addTab(tab_analisis, "Análisis y Visor")

        # Pestaña 2: Dashboard de Métricas
        self.dashboard_widget = DashboardWidget()
        self.tabs.addTab(self.dashboard_widget, "Dashboard de Métricas")

    def _cargar_imagen_inicial(self) -> None:
        """Carga una imagen de demostración al iniciar."""
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
        Establece la imagen en el visor.

        :param img: Arreglo numpy de la imagen.
        :type img: numpy.ndarray
        :param titulo: Descripción o ruta de la imagen.
        :type titulo: str
        """
        if img is None:
            return

        self.controller.current_image = img
        self.visor.establecer_imagen(img)
        h, w = img.shape[:2]
        self.lbl_info.setText(f"Estado: OK\nOrigen: {titulo}\nDimensiones: {w}x{h}\nCélulas: 0")

    def ejecutar_analisis(self) -> None:
        """Ejecuta el análisis con el motor seleccionado y parámetros en vivo (CITO-65 / CITO-66)."""
        if self.controller.current_image is None:
            QMessageBox.warning(self, "Advertencia", "No hay ninguna imagen cargada para analizar.")
            return

        params = self.panel_ajustes.obtener_parametros()
        motor = params["motor"]
        sigma1 = params["sigma1"]
        sigma2 = params["sigma2"]
        polaridad = params["polaridad"]
        metodo_separacion = params["metodo_separacion"]
        if metodo_separacion == "none":
            metodo_separacion = None

        img = self.controller.current_image

        try:
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                imagen_original = img
            else:
                gray = img
                imagen_original = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            if motor == "dl":
                resultado = analizar_nucleos_dl(gray, imagen_original, polaridad=polaridad)
            else:
                dog = aplicar_filtro_dog(gray, sigma1=sigma1, sigma2=sigma2)
                resultado = analizar_nucleos(
                    dog,
                    imagen_original,
                    polaridad=polaridad,
                    metodo_separacion=metodo_separacion
                )

            self.visor.renderizar_resultados(resultado)

            total = resultado.get("total_celulas", 0)
            normales = resultado.get("normales", 0)
            sospechosas = resultado.get("sospechosas", 0)
            frontera = resultado.get("frontera", 0)
            riesgo = resultado.get("porcentaje_riesgo", 0.0)

            info_txt = (
                f"Estado: Análisis completado ({motor.upper()})\n"
                f"Total Células: {total}\n"
                f" - Normales: {normales}\n"
                f" - Sospechosas: {sospechosas}\n"
                f" - Frontera: {frontera}\n"
                f"Riesgo: {riesgo:.1f}%"
            )
            self.lbl_info.setText(info_txt)
        except Exception as e:
            QMessageBox.critical(self, "Error en Análisis", f"Ocurrió un error al ejecutar el motor {motor}: {e}")
