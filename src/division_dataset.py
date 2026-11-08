"""
src/division_dataset.py - Organización y división estricta de dataset por paciente/laminilla (Fase 5.1).

Implementa la división (train/val/test - 70/20/10) particionando por identificador de paciente
o laminilla para prevenir la fuga de datos (data leakage) en el entrenamiento y evaluación de modelos.
"""

from typing import Dict, List, Tuple, Any
import os
import random
import shutil
import numpy as np


class GestorDivisionDataset:
    """Administra la partición y organización estricta del dataset de citología cervical."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def particionar_por_grupo(
        self,
        lista_muestras: List[Dict[str, Any]],
        proporciones: Tuple[float, float, float] = (0.7, 0.2, 0.1)
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Particiona una lista de muestras agrupándolas estrictamente por paciente/laminilla
        para evitar fuga de datos entre train, val y test.

        :param lista_muestras: Lista de diccionarios con metadatos de las muestras (debe incluir 'paciente_id').
        :type lista_muestras: list
        :param proporciones: Tupla de proporciones (train, val, test) que suman 1.0.
        :type proporciones: tuple
        :return: Diccionario con los splits {"train": [...], "val": [...], "test": [...]}.
        :rtype: dict
        """
        assert abs(sum(proporciones) - 1.0) < 1e-5, "Las proporciones deben sumar 1.0"

        # Agrupar muestras por paciente_id
        grupos: Dict[str, List[Dict[str, Any]]] = {}
        for muestra in lista_muestras:
            pid = muestra.get("paciente_id", "desconocido")
            if pid not in grupos:
                grupos[pid] = []
            grupos[pid].append(muestra)

        p_train, p_val, _ = proporciones
        lista_pids = list(grupos.keys())
        random.shuffle(lista_pids)

        n_total = len(lista_pids)
        n_train = int(n_total * p_train)
        n_val = int(n_total * p_val)

        pids_train = lista_pids[:n_train]
        pids_val = lista_pids[n_train:n_train + n_val]
        pids_test = lista_pids[n_train + n_val:]

        splits: Dict[str, List[Dict[str, Any]]] = {
            "train": [],
            "val": [],
            "test": []
        }

        for pid, muestras in grupos.items():
            if pid in pids_train:
                splits["train"].extend(muestras)
            elif pid in pids_val:
                splits["val"].extend(muestras)
            else:
                splits["test"].extend(muestras)

        return splits
