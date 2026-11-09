"""
Módulo de Gestión y Alcance de Objetivos para la Fase 8 (Definición de Objetivos y Alcance Inicial).
"""

from typing import Dict, Any, List

def obtener_alcance_fase8() -> Dict[str, Any]:
    """
    Retorna los objetivos y el alcance inicial definido para la Fase 8 del proyecto CitoCounter-Proto.

    :return: Diccionario con objetivos, hitos semanales y entregables.
    :rtype: dict
    """
    return {
        "fase": "Fase 8: Cronograma y Planificación por Fases",
        "actividad": "ACT-30",
        "clave_jira": "CITO-101",
        "estado": "Finalizado",
        "objetivos_principales": [
            "Establecer hitos temporales para el desarrollo, integración y calibración (Semanas 1 a 12).",
            "Garantizar la trazabilidad entre el cronograma temporal y las incidencias en Jira.",
            "Definir entregables reproducibles por fase."
        ],
        "hitos_semanales": [
            "Semana 1-2: Arquitectura base y contratos de datos",
            "Semana 3-5: Captura en tiempo real, pipeline asíncrono y overlays",
            "Semana 6-7: Optimización de preprocesamiento y motor de inferencia",
            "Semana 8-9: Calibración de escala µm/píxel y normalización de color",
            "Semana 10-12: Barrido de platina, tracking, división de dataset y validación clínica"
        ]
    }
