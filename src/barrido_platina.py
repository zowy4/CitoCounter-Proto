"""
src/barrido_platina.py - Simulación y guía de barrido de platina en patrón serpiente/Zelanda (Fase 4.1).

Genera un mapa de cobertura visual en pantalla para guiar al citotecnólogo u operador
durante el escaneo sistemático de la laminilla, asegurando que no queden zonas sin explorar.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import cv2


class SimuladorBarridoPlatina:
    """Gestiona el patrón de escaneo en zigzag (Zelanda) y calcula el mapa de cobertura visual."""

    def __init__(self, filas: int = 5, columnas: int = 5) -> None:
        self.filas: int = filas
        self.columnas: int = columnas
        # Matriz de cobertura: 0 = no visitado, 1 = visitado/escaneado
        self.matriz_cobertura: np.ndarray = np.zeros((filas, columnas), dtype=np.uint8)
        self.posicion_actual: Tuple[int, int] = (0, 0)
        self.camino_zigzag: List[Tuple[int, int]] = self._generar_patron_zigzag(filas, columnas)
        self.indice_camino: int = 0

    def _generar_patron_zigzag(self, filas: int, columnas: int) -> List[Tuple[int, int]]:
        """Genera la secuencia de coordenadas (fila, columna) en patrón serpiente."""
        camino = []
        for f in range(filas):
            if f % 2 == 0:
                cols = range(columnas)
            else:
                cols = range(columnas - 1, -1, -1)
            for c in cols:
                camino.append((f, c))
        return camino

    def avanzar(self) -> Optional[Tuple[int, int]]:
        """Avanza a la siguiente posición en el patrón de barrido."""
        if self.indice_camino < len(self.camino_zigzag) - 1:
            self.indice_camino += 1
            self.posicion_actual = self.camino_zigzag[self.indice_camino]
            f, c = self.posicion_actual
            self.matriz_cobertura[f, c] = 1
            return self.posicion_actual
        return None

    def reiniciar(self) -> None:
        """Reinicia el recorrido de barrido."""
        self.matriz_cobertura.fill(0)
        self.indice_camino = 0
        self.posicion_actual = self.camino_zigzag[0]
        f, c = self.posicion_actual
        self.matriz_cobertura[f, c] = 1

    def generar_mapa_visual(self, tamano_celda: int = 80) -> np.ndarray:
        """
        Genera una representación visual (imagen BGR) del mapa de cobertura de la laminilla.

        :param tamano_celda: Tamaño en píxeles de cada celda de la cuadrícula.
        :type tamano_celda: int
        :return: Imagen BGR con el mapa de calor/cobertura de la platina.
        :rtype: numpy.ndarray
        """
        h = self.filas * tamano_celda
        w = self.columnas * tamano_celda
        mapa = np.ones((h, w, 3), dtype=np.uint8) * 240  # Fondo gris claro

        for f in range(self.filas):
            for c in range(self.columnas):
                x1 = c * tamano_celda
                y1 = f * tamano_celda
                x2 = x1 + tamano_celda
                y2 = y1 + tamano_celda

                # Color según estado
                if (f, c) == self.posicion_actual:
                    color = (0, 165, 255)  # Naranja: Posición actual
                elif self.matriz_cobertura[f, c] == 1:
                    color = (0, 200, 0)    # Verde: Escaneado
                else:
                    color = (220, 220, 220) # Gris: Pendiente

                cv2.rectangle(mapa, (x1 + 2, y1 + 2), (x2 - 2, y2 - 2), color, -1)
                cv2.rectangle(mapa, (x1, y1), (x2, y2), (100, 100, 100), 1)

                # Texto de coordenadas
                texto = f"({f},{c})"
                cv2.putText(mapa, texto, (x1 + 10, y1 + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 50, 50), 1)

        porcentaje = (np.sum(self.matriz_cobertura) / (self.filas * self.columnas)) * 100.0
        cv2.putText(mapa, f"Cobertura: {porcentaje:.1f}%", (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        return mapa
