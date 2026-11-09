"""
Módulo de Arquitectura Base y Contratos de Datos para la Fase 8 (CITO-102, ACT-31).
Define los contratos estructurados entre los diferentes módulos del sistema.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class ContratoDatosPipeline:
    """
    Contrato de datos formalizado para el intercambio entre etapas del pipeline.
    """
    imagen_id: str
    ancho: int
    alto: int
    conteo_celulas: int
    elementos_sospechosos: int
    metadatos: Dict[str, Any] = field(default_factory=dict)
    estado: str = "PROCESADO"


def obtener_especificacion_arquitectura() -> Dict[str, Any]:
    """
    Retorna la especificación de la arquitectura base y sus contratos de datos.

    :return: Diccionario con la descripción de componentes y contratos.
    :rtype: dict
    """
    return {
        "actividad": "ACT-31",
        "clave_jira": "CITO-102",
        "titulo": "Diseño de arquitectura base y contratos de datos",
        "estado": "Finalizado",
        "componentes": [
            "src/preprocessing.py (Carga y mejora de contraste)",
            "src/dog_filter.py (Filtro Difference of Gaussians en float32)",
            "src/analysis.py (Contornos y clasificación por área)",
            "src/contracts/pipeline_contract.py (Contratos explícitos)"
        ],
        "principios": [
            "Modularidad estricta sin efectos secundarios en importación",
            "Tipado estático con tipado estricto y docstrings en formato NumPy",
            "Validación de tamaño de datos previa al procesamiento"
        ]
    }
