"""
src/aumentacion_datos.py - Robustecimiento y aumentación de datos para microscopía (Fase 3.3).

Simula condiciones reales de captura en microscopía cervical:
1. Desenfoque (Blur por movimiento o focalización imperfecta).
2. Ruido gaussiano y sal y pimienta (imperfecciones de sensor).
3. Variaciones de brillo, contraste y saturación.
4. Compresión JPEG o artefactos de digitalización.
"""

from typing import Optional
import numpy as np
import cv2


class AumentadorMicroscopia:
    """Aplica transformaciones de aumentación de datos simulando condiciones de microscopio."""

    def __init__(self, semilla: Optional[int] = None) -> None:
        if semilla is not None:
            np.random.seed(semilla)

    def aplicar_desenfoque(self, imagen: np.ndarray, intensidad: float = 1.0) -> np.ndarray:
        """Aplica desenfoque gaussiano para simular pérdida de foco en el microscopio."""
        ksize = int(3 + 2 * round(abs(intensidad)))
        if ksize % 2 == 0:
            ksize += 1
        return cv2.GaussianBlur(imagen, (ksize, ksize), 0)

    def aplicar_ruido(self, imagen: np.ndarray, desviacion_estandar: float = 15.0) -> np.ndarray:
        """Aplica ruido gaussiano simulando ruido electrónico del sensor."""
        ruido = np.random.normal(0, desviacion_estandar, imagen.shape).astype(np.float32)
        noisy_img = imagen.astype(np.float32) + ruido
        return np.clip(noisy_img, 0, 255).astype(np.uint8)

    def ajustar_brillo_contraste(self, imagen: np.ndarray, alfa: float = 1.0, beta: float = 0.0) -> np.ndarray:
        """Ajusta brillo (beta) y contraste (alfa) de la imagen."""
        ajustada = cv2.convertScaleAbs(imagen, alpha=alfa, beta=beta)
        return ajustada

    def simular_condiciones_reales(self, imagen: np.ndarray) -> np.ndarray:
        """
        Aplica un pipeline combinado de aumentación simulando condiciones difíciles de microscopía.

        :param imagen: Imagen BGR o en grises.
        :type imagen: numpy.ndarray
        :return: Imagen aumentada.
        :rtype: numpy.ndarray
        """
        img_out = imagen.copy()

        # Variación aleatoria de brillo y contraste
        alfa = np.random.uniform(0.85, 1.15)
        beta = np.random.uniform(-15.0, 15.0)
        img_out = self.ajustar_brillo_contraste(img_out, alfa=alfa, beta=beta)

        # Ruido de sensor moderado
        if np.random.rand() > 0.5:
            img_out = self.aplicar_ruido(img_out, desviacion_estandar=np.random.uniform(5.0, 20.0))

        # Desenfoque leve ocasional
        if np.random.rand() > 0.6:
            img_out = self.aplicar_desenfoque(img_out, intensidad=np.random.uniform(0.5, 1.5))

        return img_out
