"""
Módulo de Pipeline de Inferencia Asíncrono (Fase 1 / CITO-104 / ACT-33).
Separa la captura de video y la inferencia en hilos independientes para evitar bloqueo de UI.
"""

import threading
import queue
import time
from typing import Callable, Optional, Any

class PipelineAsincrono:
    """
    Administra la ejecución asíncrona del pipeline de procesamiento e inferencia en hilos separados.
    """
    def __init__(self, funcion_inferencia: Callable[[Any], Any], max_cola: int = 10) -> None:
        """:param funcion_inferencia: Función encargada de procesar cada frame.
        :type funcion_inferencia: callable
        :param max_cola: Capacidad máxima de la cola de frames.
        :type max_cola: int
        """
        self.funcion_inferencia = funcion_inferencia
        self.cola_entrada: queue.Queue = queue.Queue(maxsize=max_cola)
        self.cola_salida: queue.Queue = queue.Queue(maxsize=max_cola)
        self._hilo: Optional[threading.Thread] = None
        self._activo = False

    def iniciar(self) -> None:
        """Inicia el hilo de procesamiento asíncrono."""
        if not self._activo:
            self._activo = True
            self._hilo = threading.Thread(target=self._bucle_procesamiento, daemon=True)
            self._hilo.start()

    def _bucle_procesamiento(self) -> None:
        """Bucle interno que extrae frames de la cola y ejecuta la inferencia."""
        while self._activo:
            try:
                frame_data = self.cola_entrada.get(timeout=0.1)
            except queue.Empty:
                continue

            try:
                resultado = self.funcion_inferencia(frame_data)
                if self.cola_salida.full():
                    try:
                        self.cola_salida.get_nowait()
                    except queue.Empty:
                        pass
                self.cola_salida.put(resultado)
            except Exception as e:
                pass
            self.cola_entrada.task_done()

    def enviar_frame(self, frame: Any) -> bool:
        """
        Envía un frame para su procesamiento asíncrono.

        :param frame: Imagen o datos a procesar.
        :return: True si se encoló con éxito, False si la cola está llena.
        :rtype: bool
        """
        if not self._activo:
            return False
        try:
            self.cola_entrada.put_nowait(frame)
            return True
        except queue.Full:
            return False

    def obtener_resultado(self, timeout: float = 0.1) -> Optional[Any]:
        """
        Obtiene el resultado procesado más reciente.

        :param timeout: Tiempo máximo de espera.
        :type timeout: float
        :return: Resultado de la inferencia o None.
        """
        try:
            return self.cola_salida.get(timeout=timeout)
        except queue.Empty:
            return None

    def detener(self) -> None:
        """Detiene el hilo de procesamiento asíncrono."""
        self._activo = False
        if self._hilo and self._hilo.is_alive():
            self._hilo.join(timeout=1.0)

