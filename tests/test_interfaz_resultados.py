import unittest

from src.interfaz_resultados import (
    AVISO_USO_EXPERIMENTAL,
    generar_csv_resultados,
    resumen_resultado_experimental,
)


class InterfazResultadosTests(unittest.TestCase):
    def setUp(self):
        self.resultados = {
            "total_celulas": 10,
            "normales": 6,
            "sospechosas": 2,
            "frontera": 2,
            "porcentaje_riesgo": 20.0,
        }

    def test_csv_incluye_parametros_incertidumbre_y_aviso(self):
        contenido = generar_csv_resultados(
            self.resultados,
            sigma1=7.0,
            sigma2=8.0,
            usar_clahe=True,
            reducir_ruido=False,
        )

        self.assertIn("Celulas en frontera,2", contenido)
        self.assertIn("Sigma 1,7.0", contenido)
        self.assertIn("Umbral de sospecha", contenido)
        self.assertIn(AVISO_USO_EXPERIMENTAL, contenido)

    def test_resumen_indica_revision_cuando_existe_frontera(self):
        mensaje = resumen_resultado_experimental(self.resultados)

        self.assertIn("2 detección(es)", mensaje)
        self.assertIn("revisión experta", mensaje)


if __name__ == "__main__":
    unittest.main()