"""Métricas clave del rendimiento del sistema (CITO-28 / ACT-07).

Proporciona funciones para calcular y reportar los indicadores de rendimiento
del pipeline CitoCounter Proto, tanto a nivel de imagen individual como de
conjunto de ejecuciones históricas.

Disponibles tanto para el dashboard Streamlit como para la API REST y la CLI.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .historial_resultados import cargar_historial, agregar_historial, filas_para_tabla


# ---------------------------------------------------------------------------
# Métricas por imagen
# ---------------------------------------------------------------------------

def calcular_metricas_imagen(
    total_celulas: int,
    normales: int,
    sospechosas: int,
    frontera: int,
    porcentaje_riesgo: float,
    umbral_sospechoso: float = 900.0,
) -> Dict[str, Any]:
    """Calcula las métricas normalizadas para una sola ejecución.

    Args:
        total_celulas: Número total de núcleos detectados.
        normales: Núcleos clasificados como normales.
        sospechosas: Núcleos clasificados como sospechosos.
        frontera: Núcleos en zona de frontera (cerca del umbral).
        porcentaje_riesgo: Porcentaje experimental de riesgo (0-100).
        umbral_sospechoso: Umbral de área que clasifica como sospechoso.

    Returns:
        Dict con las métricas calculadas.
    """
    total = max(total_celulas, 1)

    precision = normales / total if total else 0.0
    recall = normales / normales if normales else 1.0  # "recall" sobre normales vs total
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    # Razón de sospechosas sobre total
    razon_sospechosas = sospechosas / total if total else 0.0

    # Indicador de "riesgo elevado"
    riesgo_elevado = porcentaje_riesgo > 10.0

    # Índice de consistencia: qué tan cerca están las sospechosas del umbral
    if frontera > 0 and umbral_sospechoso > 0:
        desviacion_promedio = abs(porcentaje_riesgo - umbral_sospechoso) / umbral_sospechoso
        consistencia = max(0.0, 1.0 - desviacion_promedio)
    else:
        consistencia = 1.0 if frontera == 0 else 0.5

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "razon_sospechosas": round(razon_sospechosas, 4),
        "porcentaje_riesgo": round(porcentaje_riesgo, 2),
        "frontera": frontera,
        "riesgo_elevado": riesgo_elevado,
        "consistencia": round(consistencia, 4),
    }


# ---------------------------------------------------------------------------
# Métricas de conjunto / históricas
# ---------------------------------------------------------------------------

def metricas_conjunto(historial: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Calcula indicadores agregados sobre el historial de ejecuciones.

    Si no se pasa `historial` (None), se carga el de `bitacora_experimentos.csv`.
    Pase `historial=[]` explícitamente para obtener un conjunto vacío.
    """
    if historial is None:
        hist = cargar_historial()
    else:
        hist = historial or []
    if not hist:
        return {
            "total_ejecuciones": 0,
            "imagenes_unicas": 0,
            "total_celulas_promedio": 0.0,
            "normales_promedio": 0.0,
            "sospechosas_promedio": 0.0,
            "riesgo_promedio": 0.0,
            "tasa_riesgo_alto": 0.0,
            "evolucion": [],
        }

    total = len(hist)
    imagenes_unicas = len({h.get("imagen", "") for h in hist if h.get("imagen")})

    total_celulas = sum(h.get("total_celulas", 0) or 0 for h in hist)
    normales = sum(h.get("normales", 0) or 0 for h in hist)
    sospechosas = sum(h.get("sospechosas", 0) or 0 for h in hist)
    riesgos = [h.get("porcentaje_riesgo", 0) or 0 for h in hist if h.get("porcentaje_riesgo") is not None]

    return {
        "total_ejecuciones": total,
        "imagenes_unicas": imagenes_unicas,
        "total_celulas_promedio": round(total_celulas / total, 2) if total else 0.0,
        "normales_promedio": round(normales / total, 2) if total else 0.0,
        "sospechosas_promedio": round(sospechosas / total, 2) if total else 0.0,
        "riesgo_promedio": round(sum(riesgos) / len(riesgos), 2) if riesgos else 0.0,
        "tasa_riesgo_alto": round(sum(1 for r in riesgos if r > 10.0) / len(riesgos) * 100, 1) if riesgos else 0.0,
        "evolucion": _evolucion_metricas(hist),
    }


def _evolucion_metricas(historial: List[Dict]) -> List[Dict[str, Any]]:
    """Devuelve una serie temporal ordenada por fecha de las métricas clave."""
    # Ordenar por fecha (formato T-XXX-YY-MM-DD o similar)
    ordenado = sorted(
        historial,
        key=lambda h: h.get("fecha", ""),
    )
    series = []
    for h in ordenado:
        series.append(
            {
                "fecha": h.get("fecha", ""),
                "imagen": h.get("imagen", ""),
                "total_celulas": h.get("total_celulas", 0),
                "porcentaje_riesgo": h.get("porcentaje_riesgo", 0.0),
                "frontera": h.get("frontera", 0),
            }
        )
    return series


# ---------------------------------------------------------------------------
# Utilidades de reporte
# ---------------------------------------------------------------------------

def reporte_resumen(historial: Optional[List[Dict]] = None) -> str:
    """Genera un reporte de texto legible con los indicadores clave."""
    m = metricas_conjunto(historial)

    lineas = [
        "=== REPORTE DE MÉTRICAS SISTEMA CITOCOUNTER ===",
        f"Ejecuciones registradas: {m['total_ejecuciones']}",
        f"Imágenes únicas procesadas: {m['imagenes_unicas']}",
        "",
        "Métricas promedio:",
        f"  - Células detectadas por imagen: {m['total_celulas_promedio']}",
        f"  - Normales promedio: {m['normales_promedio']}",
        f"  - Sospechosas promedio: {m['sospechosas_promedio']}",
        f"  - Riesgo experimental promedio: {m['riesgo_promedio']}%",
        f"  - Tasa de riesgo elevado (>10%): {m['tasa_riesgo_alto']}%",
        "",
        "Serie temporal (últimas ejecuciones):",
    ]

    for entry in m.get("evolucion", [])[:10]:
        lineas.append(
            f"  - {entry['fecha']} | {entry['imagen']} | "
            f"células={entry['total_celulas']} | riesgo={entry['porcentaje_riesgo']}% | "
            f"frontera={entry['frontera']}"
        )

    lineas.append("")
    lineas.append("=== FIN DEL REPORTE ===")
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Integración con la API y el dashboard (público)
# ---------------------------------------------------------------------------

__all__ = [
    "calcular_metricas_imagen",
    "metricas_conjunto",
    "reporte_resumen",
]