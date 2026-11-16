"""
src/taxonomia_sipakmed.py - Módulo de Taxonomía Clínica SIPaKMeD de 5 Clases (CITO-123 / ACT-45).

Define las 5 categorías estándar del dataset SIPaKMeD para la clasificación citológica:
1. Superficial-Intermediate (Normal)
2. Parabasal (Normal)
3. Metaplastic (Benigno / Reactivo)
4. Koilocytotic (LSIL - Bajo riesgo)
5. Dyskeratotic (HSIL / Carcinoma - Alto riesgo)
"""

from __future__ import annotations

from typing import Dict, Any, List
import numpy as np


# Definición oficial de las 5 clases SIPaKMeD y sus niveles de riesgo clínico
SIPAKMED_CLASSES: Dict[str, Dict[str, Any]] = {
    "Superficial-Intermediate": {
        "id": 0,
        "nombre_espanol": "Superficial e Intermedia",
        "categoria_clinica": "Normal",
        "nivel_riesgo": "Bajo",
        "peso_score": 0.0,
        "descripcion": "Células escamosas maduras normales de las capas superficial e intermedia."
    },
    "Parabasal": {
        "id": 1,
        "nombre_espanol": "Parabasal",
        "categoria_clinica": "Normal",
        "nivel_riesgo": "Bajo",
        "peso_score": 0.1,
        "descripcion": "Células escamosas inmaduras normales de la capa parabasal."
    },
    "Metaplastic": {
        "id": 2,
        "nombre_espanol": "Metaplásica",
        "categoria_clinica": "Benigno / Reactivo",
        "nivel_riesgo": "Bajo-Moderado",
        "peso_score": 0.3,
        "descripcion": "Células de metaplasia escamosa benignas / cambios reparativos o reactivos."
    },
    "Koilocytotic": {
        "id": 3,
        "nombre_espanol": "Koilocítica",
        "categoria_clinica": "LSIL (Lesión Intraepitelial de Bajo Grado)",
        "nivel_riesgo": "Moderado",
        "peso_score": 0.7,
        "descripcion": "Células con coilocitosis característica de infección por VPH / LSIL."
    },
    "Dyskeratotic": {
        "id": 4,
        "nombre_espanol": "Disqueratósica",
        "categoria_clinica": "HSIL / Carcinoma (Lesión de Alto Grado)",
        "nivel_riesgo": "Alto",
        "peso_score": 1.0,
        "descripcion": "Células disqueratósicas o malignas asociadas a HSIL o carcinoma cervical."
    }
}


def validar_tamano_taxonomia(imagen: np.ndarray, tamano_maximo_bytes: int = 65536 * 100) -> None:
    """
    Valida el tamaño de la imagen de entrada según los controles de seguridad OWASP/STRIDE.
    
    :param imagen: Arreglo numpy de la imagen
    :type imagen: np.ndarray
    :param tamano_maximo_bytes: Límite máximo en bytes
    :type tamano_maximo_bytes: int
    :raises ValueError: Si la imagen excede el tamaño máximo permitido
    """
    if imagen is None:
        raise ValueError("La imagen de entrada es nula.")
    if imagen.nbytes > tamano_maximo_bytes:
        raise ValueError(
            f"Tamaño de imagen excede el límite OWASP/STRIDE ({imagen.nbytes} bytes > {tamano_maximo_bytes} bytes)."
        )


def clasificar_celda_sipakmed(
    area_nucleo: float,
    relacion_nc: float = 0.3,
    hipercromasia_score: float = 0.5
) -> Dict[str, Any]:
    """
    Clasifica una célula individual dentro de la taxonomía estándar SIPaKMeD de 5 clases
    empleando reglas explicables de morfometría nuclear y características de tinción.

    :param area_nucleo: Área del núcleo en píxeles cuadrados
    :type area_nucleo: float
    :param relacion_nc: Relación núcleo-citoplasma (N/C)
    :type relacion_nc: float
    :param hipercromasia_score: Puntuación de hipercromasia (0.0 a 1.0)
    :type hipercromasia_score: float
    :return: Diccionario con la clase SIPaKMeD asignada, categoría clínica y nivel de riesgo
    :rtype: Dict[str, Any]
    """
    if area_nucleo <= 0:
        raise ValueError("El área del núcleo debe ser mayor a cero.")

    # Reglas de decisión clínico-morfométricas para la taxonomía SIPaKMeD
    if area_nucleo > 250 or (hipercromasia_score > 0.75 and relacion_nc > 0.6):
        clase_asignada = "Dyskeratotic"
    elif area_nucleo > 180 or (hipercromasia_score > 0.6 and relacion_nc > 0.45):
        clase_asignada = "Koilocytotic"
    elif area_nucleo > 120 or relacion_nc > 0.35:
        clase_asignada = "Metaplastic"
    elif area_nucleo > 60:
        clase_asignada = "Parabasal"
    else:
        clase_asignada = "Superficial-Intermediate"

    info_clase = SIPAKMED_CLASSES[clase_asignada]

    return {
        "clase": clase_asignada,
        "id_clase": info_clase["id"],
        "nombre_espanol": info_clase["nombre_espanol"],
        "categoria_clinica": info_clase["categoria_clinica"],
        "nivel_riesgo": info_clase["nivel_riesgo"],
        "peso_score": info_clase["peso_score"],
        "descripcion": info_clase["descripcion"]
    }


def calcular_riesgo_global_sipakmed(predicciones_celulas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcula el riesgo clínico global de la muestra o portaobjetos agregando las predicciones
    de todas las células detectadas según la taxonomía SIPaKMeD.

    :param predicciones_celulas: Lista de diccionarios con clasificaciones de células individuales
    :type predicciones_celulas: List[Dict[str, Any]]
    :return: Resumen agregado de conteos por clase y evaluación de riesgo global
    :rtype: Dict[str, Any]
    """
    conteo_clases = {c: 0 for c in SIPAKMED_CLASSES.keys()}
    score_acumulado = 0.0
    total_celulas = len(predicciones_celulas)

    if total_celulas == 0:
        return {
            "total_celulas": 0,
            "conteo_por_clase": conteo_clases,
            "riesgo_global": "Normal",
            "score_promedio": 0.0
        }

    for celda in predicciones_celulas:
        clase = celda.get("clase", "Superficial-Intermediate")
        if clase in conteo_clases:
            conteo_clases[clase] += 1
            score_acumulado += SIPAKMED_CLASSES[clase]["peso_score"]

    score_promedio = score_acumulado / total_celulas

    # Determinar riesgo global
    if conteo_clases["Dyskeratotic"] > 0 or score_promedio > 0.5:
        riesgo_global = "Alto Riesgo (HSIL / Sospecha de Carcinoma)"
    elif conteo_clases["Koilocytotic"] > 0 or score_promedio > 0.25:
        riesgo_global = "Riesgo Moderado (LSIL / VPH)"
    elif conteo_clases["Metaplastic"] > 0 or score_promedio > 0.1:
        riesgo_global = "Bajo Riesgo / Benigno-Reactivo"
    else:
        riesgo_global = "Normal / Negativo para Lesión Intraepitelial"

    return {
        "total_celulas": total_celulas,
        "conteo_por_clase": conteo_clases,
        "riesgo_global": riesgo_global,
        "score_promedio": round(float(score_promedio), 4)
    }
