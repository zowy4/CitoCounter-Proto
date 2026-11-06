"""
visor_imagen.py - Widget de visualización con QGraphicsView y overlays de clasificación (CITO-65).

Renderiza contornos celulares sobre la imagen original codificados por color:
- Verde: Normal
- Rojo: Sospechosa
- Amarillo: Zona frontera (CITO-77)
Soporta salidas tanto del motor DoG como del motor DL.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QImage, QPixmap, QPen, QColor, QPainterPath, QPainter
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsPathItem


class VisorImagen(QGraphicsView):
    """Widget de visor de imagen basado en QGraphicsView con soporte para overlays de clasificación."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self.pixmap_item: Optional[QGraphicsPixmapItem] = None
        self.overlay_items: List[QGraphicsPathItem] = []

    def establecer_imagen(self, img: np.ndarray) -> None:
        """
        Carga una imagen numpy en la escena gráfica.

        :param img: Arreglo numpy de la imagen (grises o RGB).
        :type img: numpy.ndarray
        """
        self.scene.clear()
        self.overlay_items.clear()

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
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.setSceneRect(0, 0, width, height)

    def renderizar_resultados(self, resultado_analisis: Dict[str, Any]) -> None:
        """
        Renderiza sobre la imagen los contornos y clasificaciones obtenidos
        de analizar_nucleos() (DoG) o analizar_nucleos_dl() (Deep Learning).

        El diccionario de resultado debe contener al menos 'contornos' y 'areas'
        o bien 'clasificaciones' / decisiones por contorno.

        :param resultado_analisis: Diccionario con salidas del segmentador.
        :type resultado_analisis: dict
        """
        # Limpiar overlays anteriores
        for item in self.overlay_items:
            self.scene.removeItem(item)
        self.overlay_items.clear()

        contornos = resultado_analisis.get("contornos", [])
        clasificaciones = resultado_analisis.get("clasificaciones", [])

        for i, c in enumerate(contornos):
            if c is None or len(c) == 0:
                continue

            # Determinar color según clasificación y zona frontera (CITO-77)
            # Por defecto verde (normal)
            color = QColor(0, 255, 0) # Verde normal
            
            if i < len(clasificaciones):
                dec = clasificaciones[i]
                if isinstance(dec, dict):
                    if dec.get("es_frontera", False):
                        color = QColor(255, 255, 0) # Amarillo frontera
                    elif dec.get("clasificacion") == "sospechosa":
                        color = QColor(255, 0, 0) # Rojo sospechosa
                elif isinstance(dec, str) and dec == "sospechosa":
                    color = QColor(255, 0, 0)

            # Construir QPainterPath desde el contorno numpy (Nx1x2 o Nx2)
            path = QPainterPath()
            points = c.reshape(-1, 2)
            if len(points) > 0:
                path.moveTo(float(points[0][0]), float(points[0][1]))
                for pt in points[1:]:
                    path.lineTo(float(pt[0]), float(pt[1]))
                path.closeSubpath()

            pen = QPen(color, 2)
            pen.setCosmetic(True)
            path_item = QGraphicsPathItem(path)
            path_item.setPen(pen)
            
            self.scene.addItem(path_item)
            self.overlay_items.append(path_item)
