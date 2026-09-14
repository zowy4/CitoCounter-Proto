"""Lectura y agregación de ejecuciones para CITO-27."""

import csv
from pathlib import Path


CAMPOS_BITACORA = [
    "id_prueba",
    "fecha",
    "hora",
    "imagen",
    "sigma1",
    "sigma2",
    "area_promedio_normal",
    "factor_riesgo",
    "area_minima",
    "total_celulas",
    "normales",
    "sospechosas",
    "porcentaje_riesgo",
    "falsos_positivos",
    "falsos_negativos",
    "precision_estimada",
    "observaciones",
    "calidad_dog",
    "ajuste_siguiente",
    "responsable",
]


CAMPOS_NUMERICOS = {
    "sigma1",
    "sigma2",
    "area_promedio_normal",
    "factor_riesgo",
    "area_minima",
    "total_celulas",
    "normales",
    "sospechosas",
    "porcentaje_riesgo",
}


def _convertir_campo(nombre, valor):
    valor = (valor or "").strip()
    if nombre not in CAMPOS_NUMERICOS:
        return valor
    if not valor:
        return None
    try:
        numero = float(valor)
    except ValueError:
        return None
    return int(numero) if nombre in {"total_celulas", "normales", "sospechosas"} else numero


def cargar_historial(ruta=Path("bitacora_experimentos.csv")):
    """Carga filas válidas de la bitácora, que puede no tener encabezado."""
    ruta = Path(ruta)
    if not ruta.is_file():
        return []

    historial = []
    with ruta.open("r", newline="", encoding="utf-8") as archivo:
        reader = csv.reader(archivo)
        for fila in reader:
            if not fila or not fila[0].strip().startswith("T-"):
                continue
            valores = fila[: len(CAMPOS_BITACORA)]
            valores.extend([""] * (len(CAMPOS_BITACORA) - len(valores)))
            historial.append({
                nombre: _convertir_campo(nombre, valor)
                for nombre, valor in zip(CAMPOS_BITACORA, valores)
            })
    return historial


def agregar_historial(historial):
    """Calcula indicadores consolidados para la vista histórica."""
    total_ejecuciones = len(historial)
    total_celulas = sum(fila["total_celulas"] or 0 for fila in historial)
    normales = sum(fila["normales"] or 0 for fila in historial)
    sospechosas = sum(fila["sospechosas"] or 0 for fila in historial)
    riesgos = [
        fila["porcentaje_riesgo"]
        for fila in historial
        if fila["porcentaje_riesgo"] is not None
    ]
    return {
        "total_ejecuciones": total_ejecuciones,
        "imagenes_unicas": len({fila["imagen"] for fila in historial if fila["imagen"]}),
        "total_celulas": total_celulas,
        "normales": normales,
        "sospechosas": sospechosas,
        "promedio_riesgo": sum(riesgos) / len(riesgos) if riesgos else 0.0,
    }


def filas_para_tabla(historial):
    """Reduce filas a las columnas útiles para la tabla del dashboard."""
    columnas = [
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
    return [{columna: fila[columna] for columna in columnas} for fila in historial]
