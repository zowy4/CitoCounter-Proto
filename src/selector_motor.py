"""
Módulo de Selección y Optimización del Motor de Inferencia (Fase 2 / CITO-106 / ACT-35).
Administra la selección entre DoG optimizado y YOLOv8-nano / MobileNet según recursos disponibles.
"""

from typing import Dict, Any, Optional

class SelectorMotorInferencia:
    """
    Gestiona la selección y configuración del motor de inferencia óptimo para citología.
    """
    def __init__(self, motor_preferido: str = "dog") -> None:
        """:param motor_preferido: 'dog' (Difference of Gaussians optimizado) o 'yolov8-nano'.
        :type motor_preferido: str
        """
        self.motor_activo = motor_preferido
        self.configuracion_motor: Dict[str, Any] = {
            "dog": {"latencia_estimada_ms": 15.0, "uso_gpu": False, "precision_base": "alta"},
            "yolov8-nano": {"latencia_estimada_ms": 35.0, "uso_gpu": True, "precision_base": "media-alta"}
        }

    def cambiar_motor(self, nuevo_motor: str) -> bool:
        """
        Cambia el motor de inferencia activo si es válido.

        :param nuevo_motor: Nombre del motor ('dog' o 'yolov8-nano').
        :type nuevo_motor: str
        :return: True si el cambio fue exitoso.
        :rtype: bool
        """
        if nuevo_motor in self.configuracion_motor:
            self.motor_activo = nuevo_motor
            return True
        return False

    def obtener_info_motor(self) -> Dict[str, Any]:
        """
        Retorna la información del motor activo.

        :return: Diccionario de configuración del motor.
        :rtype: dict
        """
        return {
            "motor_activo": self.motor_activo,
            "detalles": self.configuracion_motor.get(self.motor_activo, {})
        }

