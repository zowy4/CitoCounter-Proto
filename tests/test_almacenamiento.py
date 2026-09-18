import tempfile
import unittest
from pathlib import Path

from src.almacenamiento import (
    inicializar_db,
    insertar_experimento,
    obtener_experimento,
    listar_experimentos,
    contar_experimentos,
    actualizar_experimento,
    eliminar_experimento,
    obtener_estadisticas_generales,
    exportar_a_csv,
    exportar_a_json,
    get_db_path,
)


class AlmacenamientoTests(unittest.TestCase):
    def setUp(self):
        """Configura una base de datos temporal para cada test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        # Monkey-patch get_db_path para usar nuestra base de datos temporal
        import src.almacenamiento as almacenamiento
        self.original_get_db_path = almacenamiento.get_db_path
        almacenamiento.get_db_path = lambda: Path(self.temp_dir.name) / "test.db"
        inicializar_db()

    def tearDown(self):
        self.temp_dir.cleanup()
        import src.almacenamiento as almacenamiento
        almacenamiento.get_db_path = self.original_get_db_path

    def test_inicializar_db_crea_tablas(self):
        """Verifica que la base de datos se inicializa correctamente."""
        import sqlite3
        conn = sqlite3.connect(self.temp_dir.name + "/test.db")
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='experimentos'"
        )
        tabla = cursor.fetchone()
        self.assertIsNotNone(tabla)
        self.assertEqual(tabla[0], "experimentos")

    def test_insertar_y_obtener_experimento(self):
        datos = {
            "id_prueba": "T-001",
            "fecha": "2026-09-18",
            "hora": "10:00",
            "imagen": "MUESTRA_001.jpg",
            "sigma1": 7.0,
            "sigma2": 8.0,
            "total_celulas": 10,
            "normales": 6,
            "sospechosas": 2,
            "porcentaje_riesgo": 20.0,
        }
        id_prueba = insertar_experimento(datos)
        self.assertEqual(id_prueba, "T-001")

        exp = obtener_experimento("T-001")
        self.assertIsNotNone(exp)
        self.assertEqual(exp["id_prueba"], "T-001")
        self.assertEqual(exp["imagen"], "MUESTRA_001.jpg")
        self.assertEqual(exp["sigma1"], 7.0)
        self.assertEqual(exp["sigma2"], 8.0)
        self.assertEqual(exp["total_celulas"], 10)
        self.assertEqual(exp["normales"], 6)
        self.assertEqual(exp["sospechosas"], 2)
        self.assertEqual(exp["porcentaje_riesgo"], 20.0)

    def test_insertar_experimento_campos_obligatorios(self):
        """Verifica que falla si faltan campos obligatorios."""
        datos_incompletos = {
            "id_prueba": "T-001",
            "fecha": "2026-09-18",
            # falta hora, imagen, sigma1, sigma2, etc.
        }
        with self.assertRaises(ValueError):
            insertar_experimento(datos_incompletos)

    def test_listar_experimentos(self):
        # Insertar varios experimentos
        for i in range(3):
            insertar_experimento({
                "id_prueba": f"T-{i:03d}",
                "fecha": "2026-09-18",
                "hora": "10:00",
                "imagen": f"MUESTRA_{i:03d}.jpg",
                "sigma1": 7.0,
                "sigma2": 8.0,
                "total_celulas": 10 + i,
                "normales": 6,
                "sospechosas": 2,
                "porcentaje_riesgo": 20.0,
            })

        resultados = listar_experimentos(limite=10)
        self.assertEqual(len(resultados), 3)

    def test_listar_experimentos_con_filtros(self):
        insertar_experimento({
            "id_prueba": "T-001", "fecha": "2026-09-18", "hora": "10:00",
            "imagen": "MUESTRA_001.jpg", "sigma1": 7.0, "sigma2": 8.0,
            "total_celulas": 10, "normales": 6, "sospechosas": 2,
            "porcentaje_riesgo": 20.0
        })
        insertar_experimento({
            "id_prueba": "T-002", "fecha": "2026-09-19", "hora": "10:00",
            "imagen": "MUESTRA_002.jpg", "sigma1": 7.0, "sigma2": 8.0,
            "total_celulas": 10, "normales": 6, "sospechosas": 2,
            "porcentaje_riesgo": 20.0
        })

        # Filtrar por fecha
        resultados = listar_experimentos(fecha_desde="2026-09-19")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["id_prueba"], "T-002")

    def test_contar_experimentos(self):
        self.assertEqual(contar_experimentos(), 0)
        insertar_experimento({
            "id_prueba": "T-001", "fecha": "2026-09-18", "hora": "10:00",
            "imagen": "MUESTRA_001.jpg", "sigma1": 7.0, "sigma2": 8.0,
            "total_celulas": 10, "normales": 6, "sospechosas": 2,
            "porcentaje_riesgo": 20.0
        })
        self.assertEqual(contar_experimentos(), 1)

    def test_actualizar_experimento(self):
        insertar_experimento({
            "id_prueba": "T-001", "fecha": "2026-09-18", "hora": "10:00",
            "imagen": "MUESTRA_001.jpg", "sigma1": 7.0, "sigma2": 8.0,
            "total_celulas": 10, "normales": 6, "sospechosas": 2,
            "porcentaje_riesgo": 20.0
        })

        resultado = actualizar_experimento("T-001", {"sigma1": 5.0, "sigma2": 6.0})
        self.assertTrue(resultado)

        exp = obtener_experimento("T-001")
        self.assertEqual(exp["sigma1"], 5.0)
        self.assertEqual(exp["sigma2"], 6.0)

    def test_eliminar_experimento(self):
        insertar_experimento({
            "id_prueba": "T-001", "fecha": "2026-09-18", "hora": "10:00",
            "imagen": "MUESTRA_001.jpg", "sigma1": 7.0, "sigma2": 8.0,
            "total_celulas": 10, "normales": 6, "sospechosas": 2,
            "porcentaje_riesgo": 20.0
        })

        self.assertTrue(eliminar_experimento("T-001"))
        self.assertIsNone(obtener_experimento("T-001"))
        self.assertFalse(eliminar_experimento("T-001"))  # Ya no existe

    def test_obtener_estadisticas_generales(self):
        for i in range(3):
            insertar_experimento({
                "id_prueba": f"T-{i:03d}",
                "fecha": "2026-09-18",
                "hora": "10:00",
                "imagen": f"MUESTRA_{i:03d}.jpg",
                "sigma1": 7.0,
                "sigma2": 8.0,
                "total_celulas": 10 + i,
                "normales": 6,
                "sospechosas": 2,
                "porcentaje_riesgo": 20.0,
            })

        stats = obtener_estadisticas_generales()
        self.assertEqual(stats["total_experimentos"], 3)
        self.assertEqual(stats["imagenes_unicas"], 3)
        self.assertEqual(stats["total_celulas"], 33)  # 10+11+12
        self.assertEqual(stats["total_normales"], 18)
        self.assertEqual(stats["total_sospechosas"], 6)

    def test_exportar_a_csv(self):
        insertar_experimento({
            "id_prueba": "T-001", "fecha": "2026-09-18", "hora": "10:00",
            "imagen": "MUESTRA_001.jpg", "sigma1": 7.0, "sigma2": 8.0,
            "total_celulas": 10, "normales": 6, "sospechosas": 2,
            "porcentaje_riesgo": 20.0
        })

        with tempfile.TemporaryDirectory() as tmp_dir:
            ruta_salida = Path(tmp_dir) / "export.csv"
            exportar_a_csv(ruta_salida)
            self.assertTrue(ruta_salida.exists())

    def test_exportar_a_json(self):
        insertar_experimento({
            "id_prueba": "T-001", "fecha": "2026-09-18", "hora": "10:00",
            "imagen": "MUESTRA_001.jpg", "sigma1": 7.0, "sigma2": 8.0,
            "total_celulas": 10, "normales": 6, "sospechosas": 2,
            "porcentaje_riesgo": 20.0
        })

        with tempfile.TemporaryDirectory() as tmp_dir:
            ruta_salida = Path(tmp_dir) / "export.json"
            exportar_a_json(ruta_salida)
            self.assertTrue(ruta_salida.exists())


if __name__ == "__main__":
    unittest.main()