"""
Pruebas unitarias para el Pipeline Asíncrono (CITO-104 / ACT-33).
"""

import unittest
import numpy as np
from src.pipeline_asincrono import PipelineInferenciaAsincrono

class TestPipelineAsincrono(unittest.TestCase):
    """Casos de prueba para PipelineInferenciaAsincrono."""

    def test_pipeline_sintetico(self):
        """Verifica el arranque y detención con fuente sintética."""
        pipeline = PipelineInferenciaAsincrono(fuente="sintetico", max_queue_size=2)
        iniciado = pipeline.iniciar()
        self.assertTrue(iniciado)
        self.assertTrue(pipeline.activo)

        # Esperar un momento a que procese algún frame sintético
        import time
        time.sleep(0.2)

        res = pipeline.obtener_resultado(timeout=1.0)
        self.assertIsNotNone(res)
        self.assertIn("conteo", res)
        self.assertIn("latencia_ms", res)

        pipeline.detener()
        self.assertFalse(pipeline.activo)

if __name__ == "__main__":
    unittest.main()

