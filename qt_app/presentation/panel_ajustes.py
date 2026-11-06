"""
panel_ajustes.py - Widget de panel de parámetros para CitoCounter Qt App (CITO-66).
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSlider,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt


class PanelAjustes(QWidget):
    """Panel de ajustes con sliders sigma1/sigma2, polaridad, motor y separación."""

    parametros_cambiados = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Parámetros de Análisis")
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
        self.spin_sigma1.setValue(7.0)
        self.spin_sigma1.valueChanged.connect(self._emitir_cambios)
        form_layout.addRow("Sigma 1:", self.spin_sigma1)

        # Sigma 2
        self.spin_sigma2 = QDoubleSpinBox()
        self.spin_sigma2.setRange(0.5, 40.0)
        self.spin_sigma2.setSingleStep(0.5)
        self.spin_sigma2.setValue(8.0)
        self.spin_sigma2.valueChanged.connect(self._emitir_cambios)
        form_layout.addRow("Sigma 2:", self.spin_sigma2)

        # Polaridad
        self.combo_polaridad = QComboBox()
        self.combo_polaridad.addItems(["nucleos-claros", "nucleos-oscuros"])
        self.combo_polaridad.currentIndexChanged.connect(self._emitir_cambios)
        form_layout.addRow("Polaridad:", self.combo_polaridad)

        # Método de separación
        self.combo_separacion = QComboBox()
        self.combo_separacion.addItems(["none", "watershed", "maximos"])
        self.combo_separacion.currentIndexChanged.connect(self._emitir_cambios)
        form_layout.addRow("Separación:", self.combo_separacion)

        layout.addWidget(group)

    def _emitir_cambios(self) -> None:
        params = {
            "motor": self.combo_motor.currentText(),
            "sigma1": self.spin_sigma1.value(),
            "sigma2": self.spin_sigma2.value(),
            "polaridad": self.combo_polaridad.currentText(),
            "metodo_separacion": self.combo_separacion.currentText(),
        }
        self.parametros_cambiados.emit(params)

    def obtener_parametros(self) -> dict:
        """Devuelve el diccionario actual de parámetros."""
        return {
            "motor": self.combo_motor.currentText(),
            "sigma1": self.spin_sigma1.value(),
            "sigma2": self.spin_sigma2.value(),
            "polaridad": self.combo_polaridad.currentText(),
            "metodo_separacion": self.combo_separacion.currentText(),
        }
