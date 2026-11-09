"""
Pruebas unitarias para el módulo de simulación de barrido y tracking antiduplicados (CITO-110 / ACT-39).
"""

import unittest
from src.simulacion_barrido_tracking import simular_barrido_zigzag, TrackerAntiduplicados

class SimulacionBarridoTrackingTests(unittest.TestCase):
    """Casos de prueba para el barrido en zigzag y el tracker de células."""

    def test_simular_barrido_zigzag(self):
        """Verifica que el barrido genere la trayectoria correcta en zigzag."""
        trayectoria = simular_barrido_zigzag(ancho_grid=3, alto_grid=3)
        self.assertEqual(len(trayectoria), 9)
        # Fila 0 (izq a der): (0,0), (1,0), (2,0)
        self.assertEqual(trayectoria[0], (0, 0))
        self.assertEqual(trayectoria[2], (2, 0))
        # Fila 1 (der a izq): (2,1), (1,1), (0,1)
        self.assertEqual(trayectoria[3], (2, 1))
        self.assertEqual(trayectoria[5], (0, 1))

    def test_simular_barrido_zigzag_invalido(self):
        """Verifica que se lance ValueError con dimensiones inválidas."""
        with self.assertRaises(ValueError):
            simular_barrido_zigzag(ancho_grid=0, alto_grid=3)

    def test_tracker_antiduplicados(self):
        """Verifica el funcionamiento del tracker asignando IDs y evitando duplicados."""
        tracker = TrackerAntiduplicados(umbral_distancia=10.0, max_frames_ausente=2)

        # Frame 1: Dos células detectadas
        activos_f1 = tracker.actualizar([(50.0, 50.0), (100.0, 100.0)])
        self.assertEqual(len(activos_f1), 2)
        id1 = activos_f1[0]["id"]
        id2 = activos_f1[1]["id"]

        # Frame 2: Células se mueven ligeramente (dentro del umbral)
        activos_f2 = tracker.actualizar([(52.0, 50.0), (101.0, 99.0)])
        self.assertEqual(len(activos_f2), 2)
        # Deben conservar los mismos IDs
        ids_f2 = {obj["id"] for obj in activos_f2}
        self.assertIn(id1, ids_f2)
        self.assertIn(id2, ids_f2)

if __name__ == "__main__":
    unittest.main()
