"""
src/calibracion_escala.py - Rutina de calibración de micrómetros por píxel (Fase 3.1).

Permite calibrar la relación espacial entre píxeles de la cámara del microscopio
y unidades reales ($\mu m$) usando una regla micrométrica o factor de magnificación conocido.
Esto asegura que los umbrales de área nuclear sean invariantes al aumento óptico (4x, 10x, 40x, 100x).
"""

from typing import Dict, Any, Optional
import numpy as np


class CalibradorEscalaMicroscopio:
    """Gestiona la calibración y conversión de píxeles a micrómetros reales ($\mu m$)."""

    def __init__(self, um_por_pixel_default: float = 1.0) -> None:
        """
        Inicializa el calibrador con un factor predeterminado ($\mu m / px$).

        :param um_por_pixel_default: Factor inicial de escala.
        :type um_por_pixel_default: float
        """
        self.um_por_pixel: float = um_por_pixel_default
        self.aumento_actual: str = "10x"
        self.factores_por_aumento: Dict[str, float] = {
            "4x": 2.50,   # Ej: 2.5 um por píxel
            "10x": 1.00,  # Ej: 1.0 um por píxel
            "40x": 0.25,  # Ej: 0.25 um por píxel
            "100x": 0.10  # Ej: 0.10 um por píxel
        }

    def calibrar_con_regla(self, pixeles_medidos: float, micras_reales: float) -> float:
        """
        Calcula el factor $\mu m / px$ a partir de una medición sobre una regla micrométrica.

        :param pixeles_medidos: Longitud en píxeles de la marca medida en la imagen.
        :type pixeles_medidos: float
        :param micras_reales: Longitud real conocida en micrómetros ($\mu m$).
        :type micras_reales: float
        :return: Nuevo factor calculado ($\mu m / px$).
        :rtype: float
        """
        if pixeles_medidos <= 0:
            raise ValueError("Los píxeles medidos deben ser mayores a cero.")
        if micras_reales <= 0:
            raise ValueError("Las micras reales deben ser mayores a cero.")

        self.um_por_pixel = micras_reales / pixeles_medidos
        return self.um_por_pixel

    def seleccionar_aumento(self, aumento: str) -> float:
        """
        Selecciona un aumento óptico preestablecido y ajusta el factor de escala.

        :param aumento: Identificador del aumento ('4x', '10x', '40x', '100x').
        :type aumento: str
        :return: Factor $\mu m / px$ correspondiente.
        :rtype: float
        """
        if aumento not in self.factores_por_aumento:
            raise ValueError(f"Aumento no soportado: {aumento}. Opciones: {list(self.factores_por_aumento.keys())}")
        
        self.aumento_actual = aumento
        self.um_por_pixel = self.factores_por_aumento[aumento]
        return self.um_por_pixel

    def convertir_area_a_um2(self, area_pixeles: float) -> float:
        """
        Convierte un área medida en píxeles cuadrados a micrómetros cuadrados ($\mu m^2$).

        :param area_pixeles: Área en píxeles.
        :type area_pixeles: float
        :return: Área real en $\mu m^2$.
        :rtype: float
        """
        # Área en um^2 = area_pixeles * (um_por_pixel)^2
        return float(area_pixeles * (self.um_por_pixel ** 2))

    def obtener_estado(self) -> Dict[str, Any]:
        """
        Devuelve el estado actual de calibración.

        :dict: Diccionario con parámetros de escala.
        """
        return {
            "aumento_actual": self.aumento_actual,
            "um_por_pixel": self.um_por_pixel
        }
