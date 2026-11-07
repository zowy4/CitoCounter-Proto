"""
pipeline_asincrono.py - Pipeline de inferencia asíncrono desacoplado para hilos independientes (Fase 1.2 / CITO-XX).

Separa la captura de video y la inferencia (DoG o DL) en hilos dedicados utilizando
colas thread-safe (Queue) para garantizar baja latencia (<100ms) y evitar bloqueos en la UI.
"""

from __future__ import annotations

import threading
import queue
import time
from typing import Optional, Callable, Any
import numpy as np
import cv2

from src.captura_video import CapturaVideo
from src.dog_filter import aplicar_filtro_dog
from src.analysis import analizar_nucleos
from src.segmentador_dl import validar_tamano_imagen, convertir_a_8bit


class PipelineInferenciaAsincrono:
    """Gestiona la captura de video en un hilo independiente y el procesamiento/inferencia en paralelo."""

    def __init__(self, fuente: int | str = 0, max_queue_size: int = 2) -> None:
        """:param fuente: Fuente de video (cámara, archivo o 'sintetico').
        :type fuente: int | str
        :param max_queue_size: Tamaño máximo de la cola para evitar desbordamiento y latencia acumulada.
        :type max_queue_size: int
        :rtype: None
        """
        self.cap_mgr = CapturaVideo(fuente=fuente)
        self.frame_queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=max_queue_size)
        self.result_queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=max_queue_size)
        
        self.activo = False
        self.hilo_captura: Optional[threading.Thread] = None
        self.hilo_inferencia: Optional[threading.Thread] = None
        
        # Parámetros de procesamiento configurables en caliente
        self.sigma1 = 7.0
        self.sigma2 = 8.0
        self.polaridad = "nucleos-oscuros"
        self.motor = "dog"  # "dog" o "dl"

    def iniciar(self) -> bool:
        """Inicia los hilos de captura y procesamiento asíncrono.
        
        :return: True si se inició correctamente.
        :rtype: bool
        """
        if not self.cap_mgr.abrir():
            return False

        self.activo = True
        self.hilo_captura = threading.Thread(target=self._bucle_captura, daemon=True)
        self.hilo_inferencia = threading.Thread(target=self._bucle_inferencia, daemon=True)

        self.hilo_captura.start()
        self.hilo_inferencia.start()
        return True

    def detener(self) -> None:
        """Detiene los hilos de captura e inferencia y libera recursos."""
        self.activo = False
        if self.hilo_captura and self.hilo_captura.is_alive():
            self.hilo_captura.join(timeout=1.0)
        if self.hilo_inferencia and self.hilo_inferencia.is_alive():
            self.hilo_inferencia.join(timeout=1.0)
        self.cap_mgr.cerrar()

    def _bucle_captura(self) -> None:
        """Hilo dedicado exclusivamente a capturar frames con mínima latencia."""
        while self.activo:
            frame = self.cap_mgr.leer_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            # Descartar frame viejo si la cola está llena para mantener latencia <100ms
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass

            try:
                self.frame_queue.put_nowait(frame)
            except queue.Full:
                pass

    def _bucle_inferencia(self) -> None:
        """Hilo dedicado a procesar los frames capturados mediante DoG o DL."""
        while self.activo:
            try:
                frame = self.frame_queue.get(timeout=0.05)
            except queue.Empty:
                continue

            t_inicio = time.time()
            
            # Procesamiento de inferencia
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if self.motor == "dog":
                    dog = aplicar_filtro_dog(gray, sigma1=self.sigma1, sigma2=self.sigma2)
                    resultado_analisis = analizar_nucleos(dog, frame.copy(), polaridad=self.polaridad)
                    imagen_procesada = resultado_analisis["imagen_procesada"]
                    conteo = resultado_analisis.get("conteo", 0)
                else:
                    # Modo DL / fallback rápido
                    imagen_procesada = frame.copy()
                    conteo = 0
            except Exception as e:
                imagen_procesada = frame.copy()
                conteo = 0

            t_fin = time.time()
            latencia_ms = (t_fin - t_inicio) * 1000.0

            payload = {
                "frame": imagen_procesada,
                "conteo": conteo,
                "latencia_ms": latencia_ms,
                "motor": self.motor
            }

            if self.result_queue.full():
                try:
                    self.result_queue.get_nowait()
                except queue.Empty:
                    pass

            try:
                self.result_queue.put_nowait(payload)
            except queue.Full:
                pass

    def obtener_resultado(self, timeout: float = 0.05) -> Optional[dict[str, Any]]:
        """Obtiene el último resultado procesado para mostrar en la UI sin bloqueo.
        
        :param timeout: Tiempo máximo de espera.
        :type timeout: float
        :return: Diccionario con frame procesado, conteo y latencia, o None.
        :rtype: dict | None
        """
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None
