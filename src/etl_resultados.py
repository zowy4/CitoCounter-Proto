"""ETL (Extract, Transform, Load) para resultados e historial del prototipo CitoCounter.

Este módulo:
- Extrae datos de bitacora_experimentos.csv y otros orígenes
- Normaliza y transforma los datos a un esquema unificado
- Proporciona funciones de agregación y reporte
- Soporta exportación a CSV/JSON para dashboards y análisis externos
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .historial_resultados import (
    CAMPOS_BITACORA,
    CAMPOS_NUMERICOS,
    cargar_historial,
    filas_para_tabla,
    agregar_historial,
)
from .metricas_sistema import metricas_conjunto, reporte_resumen

# Rutas por defecto
DEFAULT_BITACORA = Path("bitacora_experimentos.csv")
DEFAULT_RESULTS_DIR = Path("data/results")


# ---------------------------------------------------------------------------
# Extracción (Extract)
# ---------------------------------------------------------------------------

def extraer_bitacora(ruta: Path = DEFAULT_BITACORA) -> List[Dict[str, Any]]:
    """Extrae todas las filas de la bitácora de experimentación.

    La bitácora puede o no tener encabezado; el lector es tolerante a ambos
    casos y ignora filas que no empiezan con 'T-'.

    Returns:
        Lista de dicts con los campos normalizados del CAMPOS_BITACORA.
    """
    if not ruta.is_file():
        return []

    registros: List[Dict[str, Any]] = []
    with ruta.open("r", newline="", encoding="utf-8") as f:
        lector = csv.reader(f)
        for fila in lector:
            if not fila or not fila[0].strip().startswith("T-"):
                continue
            # Asegurar el número justo de campos
            valores = fila[: len(CAMPOS_BITACORA)]
            valores.extend([""] * (len(CAMPOS_BITACORA) - len(valores)))
            registro: Dict[str, Any] = {}
            for nombre, valor in zip(CAMPOS_BITACORA, valores):
                registro[nombre] = _convertir_campo(nombre, valor)
            registros.append(registro)
    return registros


def _convertir_campo(nombre: str, valor: Any) -> Any:
    """Convierte un campo de la bitácora al tipo esperado."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None
    if nombre in CAMPOS_NUMERICOS:
        try:
            return int(valor) if nombre in {"total_celulas", "normales", "sospechosas"} else float(valor)
        except ValueError:
            return None
    return valor


# ---------------------------------------------------------------------------
# Transformación (Transform)
# ---------------------------------------------------------------------------

def normalizar_registro(registro: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza un registro extraído a un esquema canónico para el ETL.

    Garantiza que los campos numéricos sean del tipo correcto y que los
    campos de fecha/hora tengan formato estandarizado.
    """
    # Estandarizar fecha/hora
    fecha = registro.get("fecha")
    hora = registro.get("hora")
    if fecha:
        try:
            # Formato esperado: YYYY-MM-DD
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            # Intentar formato alternativo: DD/MM/YYYY
            try:
                datetime.strptime(fecha, "%d/%m/%Y")
            except ValueError:
                pass  # Mantener el valor original si no coincide

    # Asegurar tipos numéricos
    for campo in CAMPOS_NUMERICOS:
        if campo in registro and registro[campo] is not None:
            try:
                if campo in {"total_celulas", "normales", "sospechosas"}:
                    registro[campo] = int(registro[campo])
                else:
                    registro[campo] = float(registro[campo])
            except (ValueError, TypeError):
                registro[campo] = None

    return registro


def transformar_a_esquema_unificado(registros: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transforma registros extraídos al esquema unificado del ETL.

    El esquema unificado incluye solo los campos relevantes para métricas
    y reportes, omitiendo observaciones libres y metadatos internos.
    """
    campos_unificados = [
        "id_prueba",
        "fecha",
        "hora",
        "imagen",
        "sigma1",
        "sigma2",
        "total_celulas",
        "normales",
        "sospechosas",
        "porcentaje_riesgo",
    ]

    resultado: List[Dict[str, Any]] = []
    for reg in registros:
        registro_unificado: Dict[str, Any] = {}
        for campo in campos_unificados:
            registro_unificado[campo] = reg.get(campo)
        # Calcular campos derivados solo si no vienen en el registro original
        total = registro_unificado.get("total_celulas") or 0
        normales = registro_unificado.get("normales") or 0
        # Solo derivar sospechosas si no viene en el registro original
        if registro_unificado.get("sospechosas") is None:
            registro_unificado["sospechosas"] = (registro_unificado.get("total_celulas") or 0) - (registro_unificado.get("normales") or 0)
        resultado.append(registro_unificado)
    return resultado


# ---------------------------------------------------------------------------
# Carga (Load) y Agregación
# ---------------------------------------------------------------------------

def cargar_a_dataframe(registros: List[Dict[str, Any]]) -> str:
    """Devuelve una representación CSV lista para ser guardada como dataframe.

    Args:
        registros: Lista de dicts normalizados (salida de
            transformar_a_esquema_unificado o extraer_bitacora).

    Returns:
        String con contenido CSV listo para escribirse en un archivo.
    """
    if not registros:
        return "id_prueba,fecha,hora,imagen,sigma1,sigma2,total_celulas,normales,sospechosas,porcentaje_riesgo\n"

    campos = ["id_prueba", "fecha", "hora", "imagen", "sigma1", "sigma2",
              "total_celulas", "normales", "sospechosas", "porcentaje_riesgo"]
    filas = [campos]
    for reg in registros:
        fila = [str(reg.get(c, "")) for c in campos]
        filas.append(fila)
    return "\n".join(",".join(fila) for fila in filas)


def agregado_por_imagen(registros: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Agrega métricas por imagen a partir de los registros extraídos.

    Devuelve totales y promedios simples sobre el conjunto.
    """
    if not registros:
        return {
            "total_ejecuciones": 0,
            "imagenes_unicas": 0,
            "total_celulas_promedio": 0.0,
            "normales_promedio": 0.0,
            "sospechosas_promedio": 0.0,
            "riesgo_promedio": 0.0,
        }

    total = len(registros)
    imagenes_unicas = len({r.get("imagen", "") for r in registros if r.get("imagen")})
    total_celulas = sum(r.get("total_celulas", 0) or 0 for r in registros)
    normales = sum(r.get("normales", 0) or 0 for r in registros)
    sospechosos = sum(r.get("sospechosas", 0) or 0 for r in registros)
    riesgos = [r.get("porcentaje_riesgo", 0) or 0 for r in registros if r.get("porcentaje_riesgo") is not None]

    return {
        "total_ejecuciones": total,
        "imagenes_unicas": imagenes_unicas,
        "total_celulas_promedio": round(total_celulas / total, 2) if total else 0.0,
        "normales_promedio": round(normales / total, 2) if total else 0.0,
        "sospechosas_promedio": round(sospechosos / total, 2) if total else 0.0,
        "riesgo_promedio": round(sum(riesgos) / len(riesgos), 2) if riesgos else 0.0,
    }


def agregado_por_sigma(registros: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Agrega métricas agrupadas por valores de sigma1 y sigma2."""
    from collections import defaultdict

    grupos: Dict[Tuple[float, float], List[Dict[str, Any]]] = defaultdict(list)
    for r in registros:
        s1 = r.get("sigma1") or 0.0
        s2 = r.get("sigma2") or 0.0
        grupos[(s1, s2)].append(r)

    resultado: Dict[str, Any] = {}
    for (s1, s2), registros_grupo in sorted(grupos.items()):
        total = len(registros_grupo)
        total_celulas = sum(r.get("total_celulas", 0) or 0 for r in registros_grupo)
        normales = sum(r.get("normales", 0) or 0 for r in registros_grupo)
        sospechosos = sum(r.get("sospechosas", 0) or 0 for r in registros_grupo)
        riesgos = [r.get("porcentaje_riesgo", 0) or 0 for r in registros_grupo if r.get("porcentaje_riesgo") is not None]

        resultado[f"sigma1={s1}_sigma2={s2}"] = {
            "ejecuciones": total,
            "total_celulas_promedio": round(total_celulas / total, 2) if total else 0.0,
            "normales_promedio": round(normales / total, 2) if total else 0.0,
            "sospechosas_promedio": round(sospechosos / total, 2) if total else 0.0,
            "riesgo_promedio": round(sum(riesgos) / len(riesgos), 2) if riesgos else 0.0,
        }
    return resultado


# ---------------------------------------------------------------------------
# Exportación
# ---------------------------------------------------------------------------

def exportar_csv(ruta_salida: Path, registros: Optional[List[Dict[str, Any]]] = None) -> None:
    """Exporta registros a un archivo CSV.

    Args:
        ruta_salida: Ruta del archivo CSV de salida.
        registros: Lista de dicts a exportar (usa los extraídos de la bitácora
            si no se proveen).
    """
    registros = registros or extraer_bitacora()
    contenido = cargar_a_dataframe(registros)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text(contenido, encoding="utf-8")


def exportar_json(ruta_salida: Path, registros: Optional[List[Dict[str, Any]]] = None) -> None:
    """Exporta registros a un archivo JSON.

    Args:
        ruta_salida: Ruta del archivo JSON de salida.
        registros: Lista de dicts a exportar (usa los extraídos de la bitácora
            si no se proveen).
    """
    registros = registros or extraer_bitacora()
    # Filtrar a campos unificados para el JSON
    campos_unificados = [
        "id_prueba", "fecha", "hora", "imagen", "sigma1", "sigma2",
        "total_celulas", "normales", "sospechosas", "porcentaje_riesgo",
    ]
    filtrados = [{c: r.get(c) for c in campos_unificados} for r in registros]
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text(json.dumps(filtrados, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Integración con dashboard y API (público)
# ---------------------------------------------------------------------------

__all__ = [
    "extraer_bitacora",
    "normalizar_registro",
    "transformar_a_esquema_unificado",
    "cargar_a_dataframe",
    "agregado_por_imagen",
    "agregado_por_sigma",
    "exportar_csv",
    "exportar_json",
]