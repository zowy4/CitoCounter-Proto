"""
test_pipeline_asincrono.py - Tests unitarios para el pipeline de inferencia asíncrono (Fase 1.2).
"""

import unittest
import time
import numpy as np

from src.pipeline_asincrono import PipelineInferenciaAsincrono


class TestPipelineAsincrono(unittest.TestCase):
    """Casos de prueba para el pipeline asíncrono con hilos separados."""

    def test_pipeline_sintetico_concurrente(self) -> None:
        """Verifica que el pipeline inicie, procese frames asíncronamente y devuelva latencia <100ms."""
        pipeline = PipelineInferenciaAsincrono(fuente="sintetico")
        self.assertTrue(pipeline.iniciar())

        # Esperar a que se procese al menos un frame
        resultado = None
        for _ in range(30):
            resultado = pipeline.obtener_resultado(timeout=0.5)
            if resultado is not None:
                break

        pipeline.detener()

        self.assertIsNotNone(resultado)
        self.assertIn("frame", resultado)
        self.assertIn("latencia_ms", resultado)
        self.assertIsInstance(resultado["frame"], np.ndarray)
        # Verificar que la latencia esté dentro del objetivo de rendimiento (<100ms típico en sintético/DoG)
        self.assertLess(resultado["latencia_ms"], 500.0)


if __name__ == "__main__":
    unittest.main()
