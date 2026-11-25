"""
Pruebas unitarias para el motor de reportes ejecutivos en PDF (CITO-126).
"""

import unittest
import os
import tempfile
from src.reporte_ejecutivo_pdf import validar_tamano_reporte, generar_reporte_ejecutivo_pdf, REPORTLAB_DISPONIBLE


class TestReporteEjecutivoPdf(unittest.TestCase):
    def test_validar_tamano_reporte_valido(self):
        datos = {"total_celulas": 10, "indice_riesgo_global": 0.2}
        # No debe lanzar excepción
        validar_tamano_reporte(datos)

    def test_validar_tamano_reporte_nulo(self):
        with self.assertRaises(ValueError):
            validar_tamano_reporte(None)

    def test_generar_reporte_pdf(self):
        if not REPORTLAB_DISPONIBLE:
            self.skipTest("ReportLab no está instalado en el entorno.")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            ruta_tmp = tmp.name

        try:
            meta = {
                "id_muestra": "TEST-001",
                "paciente": "Paciente de Prueba",
                "analista": "Sistema",
                "fecha": "2026-11-16"
            }
            metricas = {
                "total_celulas": 5,
                "indice_riesgo_global": 0.45,
                "porcentaje_anormalidad": 20.0,
                "estado_clinico": "RIESGO MODERADO - Lesión de Bajo Grado (LSIL / VPH)",
                "conteo_por_clase": {
                    "Superficial-Intermediate": 2,
                    "Parabasal": 1,
                    "Metaplastic": 1,
                    "Koilocytotic": 1,
                    "Dyskeratotic": 0
                }
            }

            ruta_generada = generar_reporte_ejecutivo_pdf(ruta_tmp, meta, metricas)
            self.assertTrue(os.path.exists(ruta_generada))
            self.assertGreater(os.path.getsize(ruta_generada), 0)
        finally:
            if os.path.exists(ruta_tmp):
                os.remove(ruta_tmp)


if __name__ == "__main__":
    unittest.main()

