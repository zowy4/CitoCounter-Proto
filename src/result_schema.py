"""
CITO-81: Esquema de almacenamiento de resultados

Define el esquema canónico para el almacenamiento, versionado y trazabilidad
de resultados del prototipo CitoCounter. Este módulo provee:

1. Esquema de resultados (campos obligatorios/opcionales)
2. Versionado de modelo y dataset
3. Fechas y marcas de tiempo
4. Parámetros de experimento
5. Trazabilidad y metadatos de auditoría
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict


# ============================================================================
# Versionado de Modelo y Dataset
# ============================================================================

MODEL_VERSION = "v1.0.0"
DATASET_VERSION = "CitoDataset_v1"
PROJECT_VERSION = "CitoCounter-Proto v1.0"

# Fecha de creación del prototipo
PROJECT_START_DATE = datetime(2024, 1, 1)


# ============================================================================
# Esquema Canónico de Resultados
# ============================================================================

class ResultadoNucleo(TypedDict, total=False):
    """Schema canónico para un resultado de clasificación de núcleo."""
    id_prueba: str
    fecha: str
    hora: str
    imagen: str
    sigma1: float
    sigma2: float
    polaridad: str
    total_celulas: int
    normales: int
    sospechosas: int
    frontera: int
    porcentaje_riesgo: float
    umbral_sospechoso: float
    area_promedio_normal: float
    factor_riesgo: float
    area_minima: float
    area_maxima: float
    calidad_dog: float
    falsos_positivos: int
    falsos_negativos: int
    precision_estimada: float
    aviso_experimento: str
    responsable: str
    comentarios: str


class MetricasResumen(TypedDict):
    """Schema para métricas resumidas de un experimento."""
    total_ejecuciones: int
    imagenes_unicas: int
    total_celulas_promedio: float
    normales_promedio: float
    sospechosas_promedio: float
    riesgo_promedio: float


# ============================================================================
# Metadatos de Trazabilidad
# ============================================================================

class MetadatosTrazabilidad(TypedDict):
    """Metadatos de trazabilidad para auditoría."""
    modelo_version: str
    dataset_version: str
    proyecto_version: str
    fecha_creacion: str
    fecha_ejecucion: str
    identificador_experimento: str
    dependencias: List[str]  # J-08, J-11, etc.


# ============================================================================
# Constantes de Campo
# ============================================================================

# Campos obligatorios en todo resultado
CAMPOS_OBLIGATORIOS = [
    "id_prueba",
    "fecha",
    "hora",
    "imagen",
    "sigma1",
    "sigma2",
    "total_celulas",
    "normales",
    "porcentaje_riesgo",
]

# Campos de parámetros experimentales
CAMPOS_PARAMETROS = [
    "sigma1",
    "sigma2",
    "polaridad",
    "usar_clahe",
    "reducir_ruido",
]

# Campos de trazabilidad
CAMPOS_TRASABILIDAD = [
    "modelo_version",
    "dataset_version",
    "responsable",
    "comentarios",
]


# ============================================================================
# Helper Functions
# ============================================================================


def ahora_str(formato: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Retorna la fecha/hora actual formateada."""
    return datetime.now().strftime(formato)


def generar_id_prueba(prefix: str = "T") -> str:
    """Genera un identificador de prueba con timestamp."""
    ahora = datetime.now()
    timestamp = ahora.strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"


def validar_esquema(resultado: Dict[str, Any], campos_requeridos: Optional[List[str]] = None) -> bool:
    """Valida que un diccionario de resultado tenga los campos requeridos."""
    if campos_requeridos is None:
        campos_requeridos = CAMPOS_OBLIGATORIOS
    return all(campo in resultado and resultado[campo] is not None for campo in campos_requeridos)


def crear_metadata_por_defecto(responsable: str = "sistema") -> MetadatosTrazabilidad:
    """Crea metadatos de trazabilidad por defecto."""
    ahora = datetime.now()
    return {
        "modelo_version": MODEL_VERSION,
        "dataset_version": DATASET_VERSION,
        "proyecto_version": PROJECT_VERSION,
        "fecha_creacion": PROJECT_START_DATE.strftime("%Y-%m-%d"),
        "fecha_ejecucion": ahora.strftime("%Y-%m-%d"),
        "identificador_experimento": generar_id_prueba(),
        "dependencias": ["J-08", "J-11"],
    }