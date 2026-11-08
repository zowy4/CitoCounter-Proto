"""
tests/test_tracking_celular.py - Pruebas unitarias para el seguimiento antiduplicados (Fase 4.2).
"""

import unittest
from src.tracking_celular import RastreadorCelular


class TestRastreadorCelular(unittest.TestCase):
    """Casos de prueba para el rastreador de células basado en centroides."""

    def test_inicializacion_rastreador(self) -> None:
        """Verifica el estado inicial del rastreador."""
        rastreador = RastreadorCelular(umbral_distancia=30.0)
        self.assertEqual(len(rastreador.obtener_tracks_activos()), 0)
        self.assertEqual(rastreador.conteo_total_acumulado, 0)

    def test_asociacion_y_antiduplicados(self) -> None:
        """Verifica que objetos estáticos o en movimiento cercano mantengan su ID y no dupliquen conteo."""
        rastreador = RastreadorCelular(umbral_distancia=30.0)

        # Frame 1: Célula en (50, 50)
        det1 = [{"centroide": (50.0, 50.0), "caja": [40, 40, 20, 20]}]
        tracks1 = rastreador.actualizar(det1)
        self.assertEqual(len(tracks1), 1)
        id_celula = tracks1[0]["id"]
        self.assertEqual(rastreador.conteo_total_acumulado, 1)

        # Frame 2: La misma célula se desplaza ligeramente a (52, 51) -> Mismo ID, sin duplicar conteo
        det2 = [{"centroide": (52.0, 51.0), "caja": [42, 41, 20, 20]}]
        tracks2 = rastreador.actualizar(det2)
        self.assertEqual(len(tracks2), 1)
        self.assertEqual(tracks2[0]["id"], id_celula)
        self.assertEqual(rastreador.conteo_total_acumulado, 1)


if __name__ == "__main__":
    unittest.main()
