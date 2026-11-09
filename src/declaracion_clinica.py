"""
Módulo de Verificación de Exención y Declaración de Uso Clínico (Fase 9.1).
Proporciona avisos legales, normativos y clínicos obligatorios para CitoCounter-Proto.
"""

from typing import Dict, Any

TEXTO_EXENCION_CLINICA = (
    "ATENCIÓN: CitoCounter-Proto es un prototipo de investigación y herramienta educativa "
    "en citología cervical. NO es un dispositivo médico certificado ni un sistema de diagnóstico "
    "clínico autónomo. Todos los resultados, conteos y clasificaciones generados por este software "
    "deben ser revisados, validados e interpretados exclusivamente por personal médico o citotecnólogo "
    "calificado antes de cualquier toma de decisión clínica."
)

def obtener_declaracion_exencion() -> Dict[str, Any]:
    """
    Retorna los metadatos y el texto oficial de la declaración de exención clínica.

    :return: Diccionario con el estado normativo y la exención.
    :rtype: dict
    """
    return {
        "proyecto": "CitoCounter-Proto",
        "estado_regulatorio": "Prototipo de Investigación / No diagnóstico clínico",
        "advertencia_legal": TEXTO_EXENCION_CLINICA,
        "uso_autorizado": ["Educación", "Investigación", "Prototipado algorítmico"]
    }
