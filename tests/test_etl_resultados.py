import tempfile
import unittest
from pathlib import Path

from src.etl_resultados import (
    extraer_bitacora,
    normalizar_registro,
    transformar_a_esquema_unificado,
    cargar_a_dataframe,
    agregado_por_imagen,
    agregado_por_sigma,
    exportar_csv,
    exportar_json,
)


class ETLResultadosTests(unittest.TestCase):
    def test_extraer_bitacora_vacia(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            ruta = Path(tmp_dir) / "bitacora.csv"
            ruta.write_text("", encoding="utf-8")
            resultado = extraer_bitacora(ruta)
            self.assertEqual(resultado, [])

    def test_extraer_bitacora_con_datos(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            ruta = Path(tmp_dir) / "bitacora.csv"
            contenido = (
                "T-001,2026-09-14,10:00,MUESTRA_001.jpg,7.0,8.0,300,3.0,50,10,6,2,20.0,,,,obs,,,Sistema\n"
                "T-002,2026-09-14,10:01,MUESTRA_002.jpg,7.0,8.0,300,3.0,50,5,4,1,10.0,,,,obs,,,Sistema\n"
            )
            Path(tmp_dir).joinpath("bitacora.csv").write_text(contenido, encoding="utf-8")
            resultado = extraer_bitacora(Path(tmp_dir) / "bitacora.csv")
            self.assertEqual(len(resultado), 2)
            self.assertEqual(resultado[0]["id_prueba"], "T-001")
            self.assertEqual(resultado[0]["imagen"], "MUESTRA_001.jpg")
            self.assertEqual(resultado[0]["sigma1"], 7.0)
            self.assertEqual(resultado[0]["total_celulas"], 10)

    def test_ignora_filas_invalidas(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            ruta = Path(tmp_dir) / "bitacora.csv"
            contenido = (
                "cabecera\n"
                "T-001,2026-09-14,10:00,MUESTRA_001.jpg,7.0,8.0,300,3.0,50,10,6,2,20.0,,,,obs,,,Sistema\n"
                "fila_invalida\n"
            )
            Path(tmp_dir).joinpath("bitacora.csv").write_text(contenido, encoding="utf-8")
            resultado = extraer_bitacora(Path(tmp_dir) / "bitacora.csv")
            self.assertEqual(len(resultado), 1)

    def test_normalizar_registro(self):
        registro = {
            "fecha": "2026-09-14",
            "sigma1": "7.0",
            "sigma2": "8.0",
            "total_celulas": "10",
            "normales": "6",
            "sospechosas": "2",
            "porcentaje_riesgo": "20.0",
        }
        normalizado = normalizar_registro(registro)
        self.assertEqual(normalizado["sigma1"], 7.0)
        self.assertEqual(normalizado["sigma2"], 8.0)
        self.assertEqual(normalizado["total_celulas"], 10)
        self.assertEqual(normalizado["normales"], 6)
        self.assertEqual(normalizado["sospechosas"], 2)
        self.assertEqual(normalizado["porcentaje_riesgo"], 20.0)

    def test_transformar_a_esquema_unificado(self):
        registros = [
            {
                "id_prueba": "T-001",
                "fecha": "2026-09-14",
                "hora": "10:00",
                "imagen": "MUESTRA_001.jpg",
                "sigma1": 7.0,
                "sigma2": 8.0,
                "total_celulas": 10,
                "normales": 6,
                "sospechosas": 2,
                "porcentaje_riesgo": 20.0,
            }
        ]
        resultado = transformar_a_esquema_unificado(registros)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["id_prueba"], "T-001")
        self.assertEqual(resultado[0]["sospechosas"], 2)

    def test_cargar_a_dataframe(self):
        registros = [
            {"id_prueba": "T-001", "fecha": "2026-09-14", "hora": "10:00",
             "imagen": "MUESTRA_001.jpg", "sigma1": 7.0, "sigma2": 8.0,
             "total_celulas": 10, "normales": 6, "sospechosas": 2, "porcentaje_riesgo": 20.0}
        ]
        csv_str = cargar_a_dataframe(registros)
        self.assertIn("id_prueba,fecha,hora,imagen,sigma1,sigma2,total_celulas,normales,sospechosas,porcentaje_riesgo", csv_str)
        self.assertIn("T-001", csv_str)

    def test_agregado_por_imagen(self):
        registros = [
            {"total_celulas": 10, "normales": 6, "sospechosas": 2, "porcentaje_riesgo": 20.0, "imagen": "img1.jpg"},
            {"total_celulas": 8, "normales": 5, "sospechosas": 1, "porcentaje_riesgo": 12.5, "imagen": "img2.jpg"},
        ]
        agg = agregado_por_imagen(registros)
        self.assertEqual(agg["total_ejecuciones"], 2)
        self.assertEqual(agg["imagenes_unicas"], 2)
        self.assertAlmostEqual(agg["total_celulas_promedio"], 9.0)
        self.assertAlmostEqual(agg["riesgo_promedio"], 16.25)

    def test_agregado_por_sigma(self):
        registros = [
            {"sigma1": 7.0, "sigma2": 8.0, "total_celulas": 10, "normales": 6, "sospechosas": 2, "porcentaje_riesgo": 20.0},
            {"sigma1": 7.0, "sigma2": 8.0, "total_celulas": 8, "normales": 5, "sospechosas": 1, "porcentaje_riesgo": 12.5},
            {"sigma1": 5.0, "sigma2": 6.0, "total_celulas": 5, "normales": 4, "sospechosas": 1, "porcentaje_riesgo": 10.0},
        ]
        agg = agregado_por_sigma([{"sigma1": 7.0, "sigma2": 8.0, "total_celulas": 10, "normales": 6, "sospechosas": 2, "porcentaje_riesgo": 20.0},
                                   {"sigma1": 7.0, "sigma2": 8.0, "total_celulas": 8, "normales": 5, "sospechosas": 1, "porcentaje_riesgo": 12.5}])
        self.assertIn("sigma1=7.0_sigma2=8.0", agg)
        self.assertEqual(agg["sigma1=7.0_sigma2=8.0"]["ejecuciones"], 2)

    def test_exportar_csv(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            ruta = Path(tmp_dir) / "salida.csv"
            registros = [{"id_prueba": "T-001", "fecha": "2026-09-14", "hora": "10:00",
                          "imagen": "MUESTRA_001.jpg", "sigma1": 7.0, "sigma2": 8.0,
                          "total_celulas": 10, "normales": 6, "sospechosas": 2, "porcentaje_riesgo": 20.0}]
            exportar_csv(Path(tmp_dir) / "salida.csv", registros)
            self.assertTrue(Path(tmp_dir).joinpath("salida.csv").exists())

    def test_exportar_json(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            ruta = Path(tmp_dir) / "salida.json"
            registros = [{"id_prueba": "T-001", "fecha": "2026-09-14", "hora": "10:00",
                          "imagen": "MUESTRA_001.jpg", "sigma1": 7.0, "sigma2": 8.0,
                          "total_celulas": 10, "normales": 6, "sospechosas": 2, "porcentaje_riesgo": 20.0}]
            exportar_json(Path(tmp_dir) / "salida.json", registros)
            self.assertTrue(Path(tmp_dir).joinpath("salida.json").exists())


if __name__ == "__main__":
    unittest.main()