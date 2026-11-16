"""
src/panel_metricas_portaobjetos.py - Panel de Métricas y Estadísticas de Portaobjetos (CITO-125 / ACT-47).

Calcula y consolida estadísticas agregadas por portaobjetos citológico, incluyendo conteos
por clase SIPaKMeD, índice de riesgo clínico global (GCRI) y porcentajes de anormalidad.
"""

from __future__ import annotations

from typing import Dict, Any, List
import numpy as np


def calcular_metricas_portaobjetos(resultados_celdas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcula métricas agregadas y estadísticas de riesgo para un portaobjetos completo.

    :param resultados_celdas: Lista de resultados de clasificación de células individuales
    :type resultados_celdas: List[Dict[str, Any]]
    :return: Diccionario con métricas agregadas, conteos por clase y índice de riesgo global
    :rtype: Dict[str, Any]
    """
    total_celulas = len(resultados_celdas)
    if total_celulas == 0:
        return {
            "total_celulas": 0,
            "conteo_por_clase": {},
            "porcentaje_anormalidad": 0.0,
            "indice_riesgo_global": 0.0,
            "estado_clinico": "Sin células detectadas"
        }

    conteo_clases: Dict[str, int] = {
        "Superficial-Intermediate": 0,
        "Parabasal": 0,
        "Metaplastic": 0,
        "Koilocytotic": 0,
        "Dyskeratotic": 0
    }

    pesos_riesgo = {
        "Superficial-Intermediate": 0.0,
        "Parabasal": 0.1,
        "Metaplastic": 0.3,
        "Koilocytotic": 0.7,
        "Dyskeratotic": 1.0
    }

    suma_riesgo = 0.0
    anormalidades = 0

    for celda in resultados_celdas:
        clase = celda.get("clase", "Superficial-Intermediate")
        if clase in conteo_clases:
            conteo_clases[clase] += 1
        else:
            conteo_clases["Superficial-Intermediate"] += 1

        suma_riesgo += pesos_riesgo.get(clase, 0.0)
        if clase in ["Koilocytotic", "Dyskeratotic"]:
            anormalidades += 1

    porcentaje_anormalidad = (anormalidades / total_celulas) * 100.0
    indice_riesgo_global = suma_riesgo / total_celulas

    if indice_riesgo_global > 0.6 or conteo_clases["Dyskeratotic"] > 0:
        estado_clinico = "ALTO RIESGO - Revisión Citológica Prioritaria (HSIL+)"
    elif indice_riesgo_global > 0.3 or conteo_clases["Koilocytotic"] > 0:
        estado_clinico = "RIESGO MODERADO - Lesión de Bajo Grado (LSIL / VPH)"
    elif indice_riesgo_global > 0.1:
        estado_clinico = "BENIGNO / REACTIVO - Cambios inflamatorios o metaplásicos"
    else:
        estado_clinico = "NORMAL - Sin alteraciones citológicas significativas"

    return {
        "total_celulas": total_celulas,
        "conteo_por_clase": conteo_clases,
        "porcentaje_anormalidad": round(porcentaje_anormalidad, 2),
        "indice_riesgo_global": round(indice_riesgo_global, 4),
        "estado_clinico": estado_clinico
    }
