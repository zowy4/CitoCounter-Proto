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
    QGroupBox,
)

from qt_app.logic.image_controller import ImageController
from qt_app.presentation.visor_imagen import VisorImagen
from qt_app.presentation.panel_ajustes import PanelAjustes
from qt_app.presentation.dashboard_widget import DashboardWidget
from qt_app.presentation.evidencia_panel import EvidenciaPanel
from src.analysis import analizar_nucleos
from src.dog_filter import aplicar_filtro_dog
from src.segmentador_dl import analizar_nucleos_dl
from src.preprocessing import preprocesar_imagen


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

        # Aviso de uso experimental (J-69)
        self.lbl_aviso = QLabel(
            "⚠️ AVISO DE USO EXPERIMENTAL: Prototipo de investigación. "
            "Este resultado no equivale a un diagnóstico clínico y requiere revisión experta."
        )
        self.lbl_aviso.setStyleSheet(
            "background-color: #FEF3C7; color: #92400E; padding: 8px; "
            "font-weight: bold; border-radius: 4px; border: 1px solid #FCD34D;"
        )
        self.lbl_aviso.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_aviso)

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

        # Selector de cámara y video en vivo
        self.group_camara = QGroupBox("Captura en Vivo / Microscopio (CITO-103)")
        cam_layout = QVBoxLayout(self.group_camara)

        self.combo_camaras = QComboBox()
        self.poblar_camaras()
        cam_layout.addWidget(self.combo_camaras)

        self.btn_iniciar_camara = QPushButton("Iniciar Cámara / Microscopio")
        self.btn_iniciar_camara.clicked.connect(self.toggle_camara_en_vivo)
        cam_layout.addWidget(self.btn_iniciar_camara)

        self.btn_cargar_video = QPushButton("Analizar Archivo de Video...")
        self.btn_cargar_video.clicked.connect(self.cargar_video_dialogo)
        cam_layout.addWidget(self.btn_cargar_video)

        self.lbl_velocidad = QLabel("Velocidad de Reproducción:")
        cam_layout.addWidget(self.lbl_velocidad)

        self.combo_velocidad = QComboBox()
        self.combo_velocidad.addItem("Normal (1x - 33ms)", 33)
        self.combo_velocidad.addItem("Lento (0.5x - 66ms)", 66)
        self.combo_velocidad.addItem("Muy Lento (0.25x - 133ms)", 133)
        self.combo_velocidad.addItem("Cámara Lenta (0.1x - 250ms)", 250)
        self.combo_velocidad.addItem("Cuadro por Cuadro (500ms)", 500)
        self.combo_velocidad.currentIndexChanged.connect(self.actualizar_velocidad_timer)
        cam_layout.addWidget(self.combo_velocidad)

        control_layout.addWidget(self.group_camara)

        # Panel de ajustes de parámetros
        self.panel_ajustes = PanelAjustes(self)
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

        # Pestaña 3: Panel de Evidencias Académicas
        self.evidencia_panel = EvidenciaPanel()
        self.tabs.addTab(self.evidencia_panel, "Evidencias y Actividades")

    def _cargar_imagen_inicial(self) -> None:
        """Carga una imagen de demostración al iniciar."""
        try:
            img = self.controller.obtener_imagen_demostracion()
            self.mostrar_imagen(img, "Imagen Sintética Inicial")
        except Exception as e:
            self.lbl_info.setText(f"Error al cargar imagen inicial: {e}")

    def poblar_camaras(self) -> None:
        """Detecta cámaras disponibles en el sistema (índices 0 a 3)."""
        self.combo_camaras.clear()
        for i in range(4):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.combo_camaras.addItem(f"Cámara / USB / C-mount #{i}", i)
                cap.release()
        if self.combo_camaras.count() == 0:
            self.combo_camaras.addItem("No se detectaron cámaras", -1)

    def toggle_camara_en_vivo(self) -> None:
        """Inicia o detiene la captura de video en vivo."""
        if getattr(self, "en_vivo", False):
            self.detener_camara_en_vivo()
        else:
            self.iniciar_camara_en_vivo()

    def actualizar_velocidad_timer(self) -> None:
        """Actualiza el intervalo del temporizador de reproducción según la velocidad seleccionada."""
        if hasattr(self, "timer_camara") and self.timer_camara.isActive():
            intervalo = self.combo_velocidad.currentData()
            if intervalo:
                self.timer_camara.setInterval(intervalo)

    def iniciar_camara_en_vivo(self) -> None:
        idx = self.combo_camaras.currentData()
        if idx is None or idx < 0:
            QMessageBox.warning(self, "Advertencia", "No hay ninguna cámara válida seleccionada.")
            return

        from src.captura_microscopio import GestorCapturaMicroscopio
        from PySide6.QtCore import QTimer

        self.gestor_camara = GestorCapturaMicroscopio(fuente_id=idx)
        if not self.gestor_camara.iniciar_captura():
            QMessageBox.critical(self, "Error", f"No se pudo abrir la cámara #{idx}")
            return

        self.en_vivo = True
        self.btn_iniciar_camara.setText("Detener Cámara en Vivo")
        self.btn_cargar.setEnabled(False)
        self.btn_demo.setEnabled(False)

        intervalo = self.combo_velocidad.currentData() or 33
        self.timer_camara = QTimer(self)
        self.timer_camara.timeout.connect(self.procesar_frame_en_vivo)
        self.timer_camara.start(intervalo)

    def detener_camara_en_vivo(self) -> None:
        if hasattr(self, "timer_camara"):
            self.timer_camara.stop()
        if hasattr(self, "gestor_camara"):
            self.gestor_camara.liberar()

        self.en_vivo = False
        self.btn_iniciar_camara.setText("Iniciar Cámara / Microscopio")
        self.btn_cargar.setEnabled(True)
        self.btn_demo.setEnabled(True)
        self.lbl_info.setText("Estado: Cámara detenida")

    def procesar_frame_en_vivo(self) -> None:
        ret, frame = self.gestor_camara.leer_frame()
        if not ret or frame is None:
            return

        # Procesar análisis en tiempo real con los parámetros avanzados (CLAHE, ruido, HSV, polaridad, separación)
        params = self.panel_ajustes.obtener_parametros()
        motor = params["motor"]
        sigma1 = params["sigma1"]
        sigma2 = params["sigma2"]
        polaridad = params["polaridad"]
        usar_clahe = params["usar_clahe"]
        modo_clahe = params["modo_clahe"]
        reducir_ruido = params["reducir_ruido"]
        nivel_ruido = params["nivel_ruido"]
        usar_hsv = params["usar_hsv"]
        metodo_hsv = params["metodo_hsv"]
        metodo_separacion = params["metodo_separacion"]
        if metodo_separacion == "none":
            metodo_separacion = None
        mostrar_contornos = params["mostrar_contornos"]
        mostrar_areas = params["mostrar_areas"]

        try:
            gray, imagen_original = preprocesar_imagen(
                frame,
                mejorar_contraste_flag=usar_clahe,
                reducir_ruido_flag=reducir_ruido,
                metodo_contraste=modo_clahe,
                nivel_ruido=nivel_ruido,
                polaridad=polaridad,
                usar_hsv=usar_hsv,
                metodo_hsv=metodo_hsv
            )
            self.visor.establecer_imagen(imagen_original)

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

            self.visor.renderizar_resultados(
                resultado,
                mostrar_contornos=mostrar_contornos,
                mostrar_areas=mostrar_areas
            )
            total = resultado.get("total_celulas", 0)
            self.lbl_info.setText(f"Estado: En Vivo (Cámara #{self.combo_camaras.currentData()})\nCélulas detectadas: {total}")
        except Exception as e:
            pass

    def cargar_video_dialogo(self) -> None:
        """Abre un diálogo para seleccionar y analizar un archivo de video."""
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Archivo de Video", "", "Videos (*.mp4 *.avi *.mov *.mkv)"
        )
        if ruta:
            from src.captura_microscopio import GestorCapturaMicroscopio
            from PySide6.QtCore import QTimer

            self.detener_camara_en_vivo()
            self.gestor_camara = GestorCapturaMicroscopio(fuente_id=ruta)
            if not self.gestor_camara.iniciar_captura():
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo de video: {ruta}")
                return

            self.en_vivo = True
            self.btn_iniciar_camara.setText("Detener Reproducción Video")
            self.btn_cargar.setEnabled(False)
            self.btn_demo.setEnabled(False)

            intervalo = self.combo_velocidad.currentData() or 33
            self.timer_camara = QTimer(self)
            self.timer_camara.timeout.connect(self.procesar_frame_en_vivo)
            self.timer_camara.start(intervalo)
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
        """Ejecuta el análisis con el motor seleccionado y parámetros avanzados en vivo."""
        if self.controller.current_image is None:
            QMessageBox.warning(self, "Advertencia", "No hay ninguna imagen cargada para analizar.")
            return

        params = self.panel_ajustes.obtener_parametros()
        motor = params["motor"]
        sigma1 = params["sigma1"]
        sigma2 = params["sigma2"]
        polaridad = params["polaridad"]
        usar_clahe = params["usar_clahe"]
        modo_clahe = params["modo_clahe"]
        reducir_ruido = params["reducir_ruido"]
        nivel_ruido = params["nivel_ruido"]
        usar_hsv = params["usar_hsv"]
        metodo_hsv = params["metodo_hsv"]
        metodo_separacion = params["metodo_separacion"]
        if metodo_separacion == "none":
            metodo_separacion = None
        mostrar_contornos = params["mostrar_contornos"]
        mostrar_areas = params["mostrar_areas"]

        img = self.controller.current_image

        try:
            gray, imagen_original = preprocesar_imagen(
                img,
                mejorar_contraste_flag=usar_clahe,
                reducir_ruido_flag=reducir_ruido,
                metodo_contraste=modo_clahe,
                nivel_ruido=nivel_ruido,
                polaridad=polaridad,
                usar_hsv=usar_hsv,
                metodo_hsv=metodo_hsv
            )
            self.visor.establecer_imagen(imagen_original)

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

            self.visor.renderizar_resultados(
                resultado,
                mostrar_contornos=mostrar_contornos,
                mostrar_areas=mostrar_areas
            )

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
