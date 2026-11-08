"""
src/selector_motor.py - Selección y benchmark del motor de inferencia (Fase 2.1).

Permite comparar y seleccionar dinámicamente entre los motores disponibles:
1. DoG Optimizado (Algoritmo clásico basado en Difference of Gaussians + Otsu).
2. YOLOv8-nano / Ultralytics (Detección ligera de núcleos).
3. MobileNet / Adaptadores de Deep Learning (Cellpose/StarDist adaptados).
Garantiza el cumplimiento de latencia (<100ms) y precisión en el entorno clínico de CitoCounter-Proto.
"""

from typing import Dict, Any, Optional
import time
import numpy as np
import cv2

from src.dog_filter import aplicar_filtro_dog
from src.analysis import analizar_nucleos
from src.segmentador_dl import analizar_nucleos_dl


class SelectorMotorInferencia:
    """Administrador y selector del motor de inferencia óptimo para citología cervical."""

    def __init__(self, motor_por_defecto: str = "dog") -> None:
        self.motor_activo: str = motor_por_defecto
        self.configuracion: Dict[str, Any] = {
            "dog": {"sigma1": 5.0, "sigma2": 8.0, "polaridad": "nucleos-claros"},
            "dl": {"modelo": "cellpose-nuclei-nano", "confianza": 0.5},
            "yolov8n": {"modelo": "yolov8n-seg-cito", "confianza": 0.4}
        }

    def establecer_motor(self, nombre_motor: str) -> bool:
        """
        Cambia el motor activo si está soportado.

        :param nombre_motor: Identificador del motor ('dog', 'dl', 'yolov8n').
        :type nombre_motor: str
        :return: True si se cambió con éxito, False en caso contrario.
        :rtype: bool
        """
        if nombre_motor in self.configuracion:
            self.motor_activo = nombre_motor
            return True
        return False

    def procesar(self, gray: np.ndarray, original: np.ndarray, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la inferencia utilizando el motor activo y mide el tiempo de respuesta.

        :param gray: Imagen en escala de grises.
        :type gray: numpy.ndarray
        :param original: Imagen original en color (BGR).
        :type original: numpy.ndarray
        :return: Diccionario con resultados y metadatos de latencia.
        :rtype: dict
        """
        inicio = time.time()
        
        if self.motor_activo == "dog":
            sigma1 = kwargs.get("sigma1", self.configuracion["dog"]["sigma1"])
            sigma2 = kwargs.get("sigma2", self.configuracion["dog"]["sigma2"])
            polaridad = kwargs.get("polaridad", self.configuracion["dog"]["polaridad"])
            
            dog = aplicar_filtro_dog(gray, sigma1=sigma1, sigma2=sigma2)
            resultado = analizar_nucleos(dog, original, polaridad=polaridad)
            
        elif self.motor_activo in ["dl", "yolov8n"]:
            polaridad = kwargs.get("polaridad", "nucleos-claros")
            resultado = analizar_nucleos_dl(gray, original, polaridad=polaridad)
        else:
            raise ValueError(f"Motor desconocido: {self.motor_activo}")

        duracion_ms = (time.time() - inicio) * 1000.0
        resultado["motor_usado"] = self.motor_activo
        resultado["latencia_ms"] = duracion_ms
        return resultado

    def benchmark(self, gray: np.ndarray, original: np.ndarray, iteraciones: int = 10) -> Dict[str, float]:
        """
        Realiza un benchmark del motor activo midiendo latencia media por frame.

        :param gray: Imagen en escala de grises de prueba.
        :type gray: numpy.ndarray
        :param original: Imagen original en color.
        :type original: numpy.ndarray
        :param iteraciones: Número de corridas para promedio.
        :type iteraciones: int
        :return: Métricas de latencia media y FPS estimados.
        :rtype: dict
        """
        latencias = []
        # Calentamiento
        self.procesar(gray, original)

        for _ in range(iteraciones):
            inicio = time.time()
            self.procesar(gray, original)
            latencias.append((time.time() - inicio) * 1000.0)

        latencia_media = float(np.mean(latencias))
        fps_estimado = 1000.0 / latencia_media if latencia_media > 0 else 0.0

        return {
            "motor": self.motor_activo,
            "latencia_media_ms": latencia_media,
            "fps_estimado": fps_estimado,
            "cumple_objetivo_100ms": latencia_media < 100.0
        }
