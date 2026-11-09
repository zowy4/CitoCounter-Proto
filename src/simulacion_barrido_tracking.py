"""
Módulo de Simulación de Barrido de Platina en Zigzag y Tracking Antiduplicados (CITO-110 / ACT-39).
Fase 4: Simulación de escaneo de platina y seguimiento de celdas para evitar duplicados en celdas adyacentes.
"""

import numpy as np
from typing import List, Dict, Tuple, Any

def simular_barrido_zigzag(ancho_grid: int = 5, alto_grid: int = 5) -> List[Tuple[int, int]]:
    """
    Genera una secuencia de coordenadas (x, y) simulando un patrón de barrido en zigzag
    para la platina del microscopio.

    :param ancho_grid: Número de columnas en la cuadrícula.
    :type ancho_grid: int
    :param alto_grid: Número de filas en la cuadrícula.
    :type alto_grid: int
    :return: Lista de tuplas (x, y) con las posiciones del barrido.
    :rtype: List[Tuple[int, int]]
    """
    if ancho_grid <= 0 or alto_grid <= 0:
        raise ValueError("Las dimensiones del grid deben ser mayores a cero.")

    trayectoria = []
    for y in range(alto_grid):
        if y % 2 == 0:
            # Izquierda a derecha
            xs = range(ancho_grid)
        else:
            # Derecha a izquierda
            xs = range(ancho_grid - 1, -1, -1)
        for x in xs:
            trayectoria.append((x, y))
    return trayectoria

class TrackerAntiduplicados:
    """
    Sistema de tracking por distancia de centroides para evitar contar la misma célula
    en múltiples frames o solapamientos de campo de visión.
    """
    def __init__(self, umbral_distancia: float = 15.0, max_frames_ausente: int = 5):
        """
        Inicializa el tracker.

        :param umbral_distancia: Distancia máxima en píxeles para considerar la misma célula.
        :type umbral_distancia: float
        :param max_frames_ausente: Número máximo de frames sin detección antes de eliminar el objeto.
        :type max_frames_ausente: int
        """
        self.umbral_distancia = umbral_distancia
        self.max_frames_ausente = max_frames_ausente
        self.siguiente_id = 1
        self.objetos_activos: Dict[int, Dict[str, Any]] = {}

    def actualizar(self, detecciones: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        """
        Actualiza el estado del tracker con las nuevas detecciones de centroides (x, y).

        :param detecciones: Lista de coordenadas (x, y) de centroides detectados en el frame actual.
        :type detecciones: List[Tuple[float, float]]
        :return: Lista de objetos rastreados con su ID único y posición actual.
        :rtype: List[Dict[str, Any]]
        """
        # Incrementar contador de ausencia para objetos existentes
        for obj_id in self.objetos_activos:
            self.objetos_activos[obj_id]["frames_ausente"] += 1

        asignados_dets = set()
        asignados_objs = set()

        # Emparejar detecciones con objetos existentes basado en distancia mínima
        if self.objetos_activos and detecciones:
            for obj_id, info in list(self.objetos_activos.items()):
                pos_actual = info["centroide"]
                mejor_det_idx = -1
                min_dist = float("inf")

                for idx, det in enumerate(detecciones):
                    if idx in asignados_dets:
                        continue
                    dist = np.linalg.norm(np.array(pos_actual) - np.array(det))
                    if dist < min_dist and dist <= self.umbral_distancia:
                        min_dist = dist
                        mejor_det_idx = idx

                if mejor_det_idx != -1:
                    # Actualizar objeto existente
                    det = detecciones[mejor_det_idx]
                    self.objetos_activos[obj_id]["centroide"] = det
                    self.objetos_activos[obj_id]["frames_ausente"] = 0
                    asignados_dets.add(mejor_det_idx)
                    asignados_objs.add(obj_id)

        # Registrar nuevas detecciones como nuevos objetos
        for idx, det in enumerate(detecciones):
            if idx not in asignados_dets:
                self.objetos_activos[self.siguiente_id] = {
                    "id": self.siguiente_id,
                    "centroide": det,
                    "frames_ausente": 0
                }
                self.siguiente_id += 1

        # Eliminar objetos obsoletos
        ids_a_eliminar = [
            obj_id for obj_id, info in self.objetos_activos.items()
            if info["frames_ausente"] > self.max_frames_ausente
        ]
        for obj_id in ids_a_eliminar:
            del self.objetos_activos[obj_id]

        # Retornar objetos activos válidos
        return [
            {"id": info["id"], "centroide": info["centroide"]}
            for info in self.objetos_activos.values()
            if info["frames_ausente"] == 0
        ]
