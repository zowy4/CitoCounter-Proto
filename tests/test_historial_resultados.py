import tempfile
import unittest
from pathlib import Path

from src.historial_resultados import agregar_historial, cargar_historial, filas_para_tabla


class HistorialResultadosTests(unittest.TestCase):
    def test_carga_bitacora_sin_encabezado_y_agrega_metricas(self):
        contenido = (
            "T-001,2026-09-14,10:00,MUESTRA_001.jpg,7.0,8.0,300,3.0,50,10,6,2,20.0,,,,obs,,,Sistema\n"
            "T-002,2026-09-14,10:01,MUESTRA_002.jpg,7.0,8.0,300,3.0,50,5,4,1,10.0,,,,obs,,,Sistema\n"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            ruta = Path(tmp_dir) / "bitacora.csv"
            ruta.write_text(contenido, encoding="utf-8")
            historial = cargar_historial(ruta)

        resumen = agregar_historial(historial)
        self.assertEqual(len(historial), 2)
        self.assertEqual(resumen["total_ejecuciones"], 2)
        self.assertEqual(resumen["imagenes_unicas"], 2)
        self.assertEqual(resumen["total_celulas"], 15)
        self.assertEqual(resumen["sospechosas"], 3)
        self.assertEqual(resumen["promedio_riesgo"], 15.0)

    def test_ignora_filas_invalidas_y_prepara_tabla(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            ruta = Path(tmp_dir) / "bitacora.csv"
            ruta.write_text("cabecera\nT-001,2026-09-14,10:00,img.jpg,7,8,300,3,50,1,1,0,0\n", encoding="utf-8")
            filas = filas_para_tabla(cargar_historial(ruta))

        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["imagen"], "img.jpg")
        self.assertEqual(filas[0]["total_celulas"], 1)


if __name__ == "__main__":
    unittest.main()
