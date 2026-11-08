"""
src/tracking_celular.py - Seguimiento antiduplicados (Tracking) para secuencias de video (Fase 4.2).

Implementa un rastreador basado en distancia euclidiana de centroides (estilo SORT simplificado)
para asociar detecciones entre fotogramas adyacentes y evitar contar la misma célula múltiples veces.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np


class RastreadorCelular:
    """Rastreador de objetos (células) basado en centroides para streaming de video."""

    def __init__(self, umbral_distancia: float = 35.0, max_frames_ausente: int = 5) -> None:
        self.umbral_distancia: float = umbral_distancia
        self.max_frames_ausente: int = max_frames_ausente
        self.siguiente_id: int = 1
        # Diccionario de tracks activos: id -> {"centroide": (x, y), "caja": [x,y,w,h], "ausente": 0, "contado": bool}
        self.tracks: Dict[int, Dict[str, Any]] = {}
        self.conteo_total_acumulado: int = 0

    def actualizar(self, detecciones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Actualiza el estado del rastreador con las detecciones del nuevo fotograma.

        :param detecciones: Lista de diccionarios con 'centroide' (x, y) y 'caja' [x, y, w, h].
        :type detecciones: list
        :return: Lista de tracks activos con su ID asignado.
        :rtype: list
        """
        # Si no hay tracks activos, registrar todas las detecciones como nuevos IDs
        if len(self.tracks) == 0:
            for det in detecciones:
                centroide = det.get("centroide")
                caja = det.get("caja", [0, 0, 0, 0])
                if centroide is None:
                    cx = caja[0] + caja[2] / 2.0
                    cy = caja[1] + caja[3] / 2.0
                    centroide = (cx, cy)

                self.tracks[self.siguiente_id] = {
                    "centroide": centroide,
                    "caja": caja,
                    "ausente": 0,
                    "contado": True,
                    "clasificacion": det.get("clasificacion", "normal")
                }
                self.siguiente_id += 1
                self.conteo_total_acumulado += 1
            return self.obtener_tracks_activos()

        # Si hay detecciones vacías, incrementar contador de ausencia para todos
        if len(detecciones) == 0:
            ids_a_borrar = []
            for tid, tdata in self.tracks.items():
                tdata["ausente"] += 1
                if tdata["ausente"] > self.max_frames_ausente:
                    ids_a_borrar.append(tid)
            for tid in ids_a_borrar:
                del self.tracks[tid]
            return self.obtener_tracks_activos()

        # Asociar detecciones con tracks existentes mediante matriz de distancias
        centroides_existentes = [tdata["centroide"] for tdata in self.tracks.values()]
        ids_existentes = list(self.tracks.keys())

        centroides_nuevos = []
        for det in detecciones:
            c = det.get("centroide")
            if c is None:
                box = det.get("caja", [0, 0, 0, 0])
                c = (box[0] + box[2] / 2.0, box[1] + box[3] / 2.0)
            centroides_nuevos.append((c, det))

        # Matriz de distancias euclidianas
        matriz_dist = np.zeros((len(ids_existentes), len(centroides_nuevos)), dtype=np.float32)
        for i, ce in enumerate(centroides_existentes):
            for j, (cn, _) in enumerate(centroides_nuevos):
                matriz_dist[i, j] = np.linalg.norm(np.array(ce) - np.array(cn))

        asignados_existentes = set()
        asignados_nuevos = set()

        # Emparejamiento voraz por menor distancia
        if matriz_dist.size > 0:
            while True:
                min_val = np.min(matriz_dist)
                if min_val > self.umbral_distancia:
                    break
                i, j = np.unravel_index(np.argmin(matriz_dist), matriz_dist.shape)
                if i in asignados_existentes or j in asignados_nuevos:
                    matriz_dist[i, j] = 1e9
                    continue

                tid = ids_existentes[i]
                cn, det_info = centroides_nuevos[j]

                # Actualizar track
                self.tracks[tid]["centroide"] = cn
                self.tracks[tid]["caja"] = det_info.get("caja", self.tracks[tid]["caja"])
                self.tracks[tid]["ausente"] = 0
                self.tracks[tid]["clasificacion"] = det_info.get("clasificacion", self.tracks[tid]["clasificacion"])

                asignados_existentes.add(i)
                asignados_nuevos.add(j)
                matriz_dist[i, :] = 1e9
                matriz_dist[:, j] = 1e9

        # Manejar no asignados (nuevos tracks)
        for j, (cn, det_info) in enumerate(centroides_nuevos):
            if j not in asignados_nuevos:
                self.tracks[self.siguiente_id] = {
                    "centroide": cn,
                    "caja": det_info.get("caja", [0, 0, 0, 0]),
                    "ausente": 0,
                    "contado": True,
                    "clasificacion": det_info.get("clasificacion", "normal")
                }
                self.siguiente_id += 1
                self.conteo_total_acumulado += 1

        # Manejar tracks ausentes
        ids_a_borrar = []
        for i, tid in enumerate(ids_existentes):
            if i not in asignados_existentes:
                self.tracks[tid]["ausente"] += 1
                if self.tracks[tid]["ausente"] > self.max_frames_ausente:
                    ids_a_borrar.append(tid)

        for tid in ids_a_borrar:
            del self.tracks[tid]

        return self.obtener_tracks_activos()

    def obtener_tracks_activos(self) -> List[Dict[str, Any]]:
        """Devuelve la lista actual de tracks activos con su ID y estado."""
        resultado = []
        for tid, tdata in self.tracks.items():
            resultado.append({
                "id": tid,
                "centroide": tdata["centroide"],
                "caja": tdata["caja"],
                "clasificacion": tdata["clasificacion"]
            })
        return resultado
