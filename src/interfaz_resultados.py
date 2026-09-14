"""Utilidades de presentación y exportación para la interfaz local."""

import csv
from io import StringIO

from src.analysis import obtener_reglas_clasificacion


AVISO_USO_EXPERIMENTAL = (
    "Prototipo de investigación. Este resultado no equivale a un diagnóstico clínico "
    "y requiere revisión experta."
)


def generar_csv_resultados(resultados, sigma1, sigma2, usar_clahe, reducir_ruido):
    """Genera un CSV reproducible con los resultados mostrados en la interfaz."""
    reglas = obtener_reglas_clasificacion()
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Metrica", "Valor"])
    writer.writerow(["Total de celulas", resultados["total_celulas"]])
    writer.writerow(["Celulas normales", resultados["normales"]])
    writer.writerow(["Celulas sospechosas", resultados["sospechosas"]])
    writer.writerow(["Celulas en frontera", resultados.get("frontera", 0)])
    writer.writerow(["Porcentaje de riesgo experimental", f"{resultados['porcentaje_riesgo']:.1f}%"])
    writer.writerow(["Sigma 1", sigma1])
    writer.writerow(["Sigma 2", sigma2])
    writer.writerow(["CLAHE", "Si" if usar_clahe else "No"])
    writer.writerow(["Reduccion de ruido", "Si" if reducir_ruido else "No"])
    writer.writerow(["Umbral de sospecha", f"{reglas['umbral_sospechoso']:.1f} px2"])
    writer.writerow(["Aviso", AVISO_USO_EXPERIMENTAL])
    return buffer.getvalue()


def resumen_resultado_experimental(resultados):
    """Devuelve un mensaje de revisión para detecciones en zona frontera."""
    frontera = resultados.get("frontera", 0)
    if frontera:
        return (
            f"{frontera} detección(es) se encuentran cerca del umbral de clasificación "
            "y requieren revisión experta."
        )
    return "No se detectaron objetos en la zona frontera de clasificación."