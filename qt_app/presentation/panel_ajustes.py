"""
panel_ajustes.py - Widget de panel de parámetros avanzado para CitoCounter Qt App (CITO-66 / CITO-163).
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QCheckBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt


class PanelAjustes(QWidget):
    """Panel de ajustes avanzado con controles de preprocesamiento, sigma, polaridad, separación y visualización."""

    parametros_cambiados = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Parámetros de Análisis y Preprocesamiento")
        form_layout = QFormLayout(group)

        # Motor
        self.combo_motor = QComboBox()
        self.combo_motor.addItems(["dog", "dl"])
        self.combo_motor.currentIndexChanged.connect(self._emitir_cambios)
        form_layout.addRow("Motor:", self.combo_motor)

        # Sigma 1
        self.spin_sigma1 = QDoubleSpinBox()
        self.spin_sigma1.setRange(0.5, 30.0)
        self.spin_sigma1.setSingleStep(0.5)
        self.spin_sigma1.setValue(1.5)
        self.spin_sigma1.valueChanged.connect(self._emitir_cambios)
        form_layout.addRow("Sigma 1:", self.spin_sigma1)

        # Sigma 2
        self.spin_sigma2 = QDoubleSpinBox()
        self.spin_sigma2.setRange(0.5, 40.0)
        self.spin_sigma2.setSingleStep(0.5)
        self.spin_sigma2.setValue(3.0)
        self.spin_sigma2.valueChanged.connect(self._emitir_cambios)
        form_layout.addRow("Sigma 2:", self.spin_sigma2)

        # Polaridad
        self.combo_polaridad = QComboBox()
        self.combo_polaridad.addItems(["nucleos-claros", "nucleos-oscuros"])
        self.combo_polaridad.currentIndexChanged.connect(self._emitir_cambios)
        form_layout.addRow("Polaridad:", self.combo_polaridad)

        # Contraste CLAHE
        self.chk_clahe = QCheckBox("Mejorar Contraste (CLAHE)")
        self.chk_clahe.setChecked(True)
        self.chk_clahe.stateChanged.connect(self._emitir_cambios)
        form_layout.addRow("CLAHE:", self.chk_clahe)

        self.combo_modo_clahe = QComboBox()
        self.combo_modo_clahe.addItems(["clahe", "histogram", "normalize", "auto"])
        self.combo_modo_clahe.currentIndexChanged.connect(self._emitir_cambios)
        form_layout.addRow("Modo Contraste:", self.combo_modo_clahe)

        # Reducción de ruido
        self.chk_ruido = QCheckBox("Reducir Ruido (Bilateral)")
        self.chk_ruido.setChecked(False)
        self.chk_ruido.stateChanged.connect(self._emitir_cambios)
        form_layout.addRow("Filtro Ruido:", self.chk_ruido)

        self.combo_nivel_ruido = QComboBox()
        self.combo_nivel_ruido.addItems(["medio", "bajo", "alto"])
        self.combo_nivel_ruido.currentIndexChanged.connect(self._emitir_cambios)
        form_layout.addRow("Nivel Ruido:", self.combo_nivel_ruido)

        # Segmentación HSV
        self.chk_hsv = QCheckBox("Segmentación por Color HSV")
        self.chk_hsv.setChecked(False)
        self.chk_hsv.stateChanged.connect(self._emitir_cambios)
        form_layout.addRow("HSV:", self.chk_hsv)

        self.combo_metodo_hsv = QComboBox()
        self.combo_metodo_hsv.addItems(["hue", "saturation", "value"])
        self.combo_metodo_hsv.setCurrentText("hue")
        self.combo_metodo_hsv.currentIndexChanged.connect(self._emitir_cambios)
        form_layout.addRow("Método HSV:", self.combo_metodo_hsv)

        # Método de separación
        self.combo_separacion = QComboBox()
        self.combo_separacion.addItems(["none", "watershed", "maximos"])
        self.combo_separacion.currentIndexChanged.connect(self._emitir_cambios)
        form_layout.addRow("Separación:", self.combo_separacion)

        # Visualización
        self.chk_contornos = QCheckBox("Dibujar Contornos Reales")
        self.chk_contornos.setChecked(True)
        self.chk_contornos.stateChanged.connect(self._emitir_cambios)
        form_layout.addRow("Contornos:", self.chk_contornos)

        self.chk_areas = QCheckBox("Mostrar Áreas en Imagen")
        self.chk_areas.setChecked(False)
        self.chk_areas.stateChanged.connect(self._emitir_cambios)
        form_layout.addRow("Áreas:", self.chk_areas)

        layout.addWidget(group)

    def _emitir_cambios(self) -> None:
        self.parametros_cambiados.emit(self.obtener_parametros())

    def obtener_parametros(self) -> dict:
        """Devuelve el diccionario actual de parámetros y preprocesamiento."""
        return {
            "motor": self.combo_motor.currentText(),
            "sigma1": self.spin_sigma1.value(),
            "sigma2": self.spin_sigma2.value(),
            "polaridad": self.combo_polaridad.currentText(),
            "usar_clahe": self.chk_clahe.isChecked(),
            "modo_clahe": self.combo_modo_clahe.currentText(),
            "reducir_ruido": self.chk_ruido.isChecked(),
            "nivel_ruido": self.combo_nivel_ruido.currentText(),
            "usar_hsv": self.chk_hsv.isChecked(),
            "metodo_hsv": self.combo_metodo_hsv.currentText(),
            "metodo_separacion": self.combo_separacion.currentText(),
            "mostrar_contornos": self.chk_contornos.isChecked(),
            "mostrar_areas": self.chk_areas.isChecked(),
        }
