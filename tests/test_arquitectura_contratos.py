"""
Pruebas unitarias para la Arquitectura Base y Contratos de Datos (CITO-102).
"""

import unittest
from src.arquitectura_contratos import ContratoDatosPipeline, obtener_especificacion_arquitectura

class TestArquitecturaContratos(unittest.TestCase):
    """Casos de prueba para contratos de datos y arquitectura base."""

    def test_contrato_datos_pipeline(self):
        """Verifica la instanciación y campos del contrato de datos."""
        contrato = ContratoDatosPipeline(
            imagen_id="test_01.png",
            ancho=512,
            alto=512,
            conteo_celulas=15,
            elementos_sospechosos=2,
            metadatos={"sigma": 7.0}
        )
        self.assertEqual(contrato.imagen_id, "test_01.png")
        self.assertEqual(contrato.conteo_celulas, 15)
        self.assertEqual(contrato.estado, "PROCESADO")

    def test_especificacion_arquitectura(self):
        """Verifica la obtención de la especificación de arquitectura."""
        spec = obtener_especificacion_arquitectura()
        self.assertEqual(spec["clave_jira"], "CITO-102")
        self.assertEqual(spec["estado"], "Finalizado")
        self.assertTrue(len(spec["componentes"]) > 0)

if __name__ == "__main__":
    unittest.main()
