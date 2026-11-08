"""
tests/test_division_dataset.py - Pruebas unitarias para la división estricta de dataset (Fase 5.1).
"""

import unittest
from src.division_dataset import GestorDivisionDataset


class TestGestorDivisionDataset(unittest.TestCase):
    """Casos de prueba para la partición por paciente y prevención de fuga de datos."""

    def test_particionamiento_estricto(self) -> None:
        """Verifica que las muestras del mismo paciente no se distribuyan en splits distintos."""
        gestor = GestorDivisionDataset(seed=42)
        
        # Crear muestras simuladas con 10 pacientes distintos
        muestras = []
        for p in range(10):
            pid = f"PACIENTE_{p:03d}"
            for m in range(5):  # 5 imágenes por paciente
                muestras.append({
                    "paciente_id": pid,
                    "ruta": f"img_{p}_{m}.png",
                    "clase": "normal" if m % 2 == 0 else "sospechosa"
                })

        splits = gestor.particionar_por_grupo(muestras, proporciones=(0.7, 0.2, 0.1))

        self.assertIn("train", splits)
        self.assertIn("val", splits)
        self.assertIn("test", splits)

        # Verificar que ningún paciente esté en más de un split
        pids_train = {m["paciente_id"] for m in splits["train"]}
        pids_val = {m["paciente_id"] for m in splits["val"]}
        pids_test = {m["paciente_id"] for m in splits["test"]}

        self.assertTrue(pids_train.isdisjoint(pids_val))
        self.assertTrue(pids_train.isdisjoint(pids_test))
        self.assertTrue(pids_val.isdisjoint(pids_test))


if __name__ == "__main__":
    unittest.main()
