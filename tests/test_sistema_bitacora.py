"""
Pruebas unitarias para el Sistema de Bitácora y Versionado (Fase 7.1).
"""

import unittest
import os
import json
from src.sistema_bitacora import SistemaBitacora, RegistroExperimento

class TestSistemaBitacora(unittest.TestCase):
    """Casos de prueba para SistemaBitacora."""

    def setUp(self):
        self.ruta_test = "data/results/test_bitacora.json"
        if os.path.exists(self.ruta_test):
            os.remove(self.ruta_test)
        self.sistema = SistemaBitacora(ruta_bitacora=self.ruta_test)

    def tearDown(self):
        if os.path.exists(self.ruta_test):
            os.remove(self.ruta_test)

    def test_registrar_y_cargar_experimento(self):
        """Verifica que se registre correctamente un experimento y se persista."""
        hp = {"sigma1": 7.0, "sigma2": 8.0, "umbral": 0.5}
        metricas = {"f1": 0.88, "precision": 0.91, "recall": 0.85}
        artefactos = ["data/results/test_artefacto.png"]

        reg = self.sistema.registrar_experimento(
            experimento_id="EXP-TEST-001",
            nombre_modelo="DoG_Clasificador",
            hiperparametros=hp,
            metricas=metricas,
            artefactos=artefactos,
            observaciones="Prueba unitaria de bitácora"
        )

        self.assertEqual(reg.experimento_id, "EXP-TEST-001")
        self.assertEqual(reg.nombre_modelo, "DoG_Clasificador")
        self.assertEqual(reg.metricas["f1"], 0.88)

        # Cargar y verificar persistencia
        bitacora = self.sistema.cargar_bitacora()
        self.assertEqual(len(bitacora), 1)
        self.assertEqual(bitacora[0]["experimento_id"], "EXP-TEST-001")

    def test_buscar_por_id(self):
        """Verifica la búsqueda de experimentos por ID."""
        self.sistema.registrar_experimento(
            experimento_id="EXP-TEST-002",
            nombre_modelo="Modelo_B",
            hiperparametros={"a": 1},
            metricas={"f1": 0.75}
        )

        encontrado = self.sistema.buscar_por_id("EXP-TEST-002")
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado["nombre_modelo"], "Modelo_B")

        no_encontrado = self.sistema.buscar_por_id("EXP-NO-EXISTE")
        self.assertIsNone(no_encontrado)

    def test_validacion_tamano_excesivo(self):
        """Verifica el control de tamaño de hiperparámetros (seguridad OWASP/STRIDE)."""
        hp_grande = {"datos": "x" * 70000}
        with self.assertRaises(ValueError):
            self.sistema.registrar_experimento(
                experimento_id="EXP-FAIL",
                nombre_modelo="Modelo_Grande",
                hiperparametros=hp_grande,
                metricas={"f1": 0.5}
            )

if __name__ == "__main__":
    unittest.main()
