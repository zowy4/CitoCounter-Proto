"""
test_qt_app.py - Pruebas unitarias para qt_app usando pytest-qt (CITO-42).
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from qt_app.logic.image_controller import ImageController
from qt_app.presentation.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    """Fixture de sesión para QApplication requerida por pytest-qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_image_controller_demo():
    """Verifica que el controlador genera la imagen de demostración correctamente."""
    controller = ImageController()
    img = controller.obtener_imagen_demostracion()
    assert img is not None
    assert img.shape == (256, 256)
    assert controller.current_path == "synthetic_demo"


def test_main_window_creation(qapp, qtbot):
    """Verifica que la ventana principal se abre y muestra la imagen sin errores."""
    controller = ImageController()
    window = MainWindow(controller=controller)
    qtbot.addWidget(window)
    window.show()

    # Verificar título y estado inicial
    assert "CitoCounter-Proto" in window.windowTitle()
    assert window.controller.current_image is not None
    
    # Probar botón demo
    qtbot.mouseClick(window.btn_demo, Qt.LeftButton)
    assert window.controller.current_path == "synthetic_demo"
