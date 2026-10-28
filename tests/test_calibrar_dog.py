import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from calibrar_dog import ejecutar_barrido, evaluar_configuracion


class CalibrarDogTests(unittest.TestCase):
    def test_rechaza_sigma_invalido(self):
        with self.assertRaises(ValueError):
            evaluar_configuracion([Path("muestra.png")], 3.0, 3.0)

    def test_barrido_omite_parejas_invalidas_y_escribe_csv(self):
        with tempfile.TemporaryDirectory() as directorio:
            raiz = Path(directorio)
            entrada = raiz / "imagenes"
            entrada.mkdir()
            (entrada / "muestra.png").touch()
            salida = raiz / "resultados.csv"
            evidencia = {
                "sigma1": 2.0,
                "sigma2": 5.0,
                "ratio": 2.5,
                "imagenes": 1,
                "imagenes_sin_detecciones": 0,
                "detecciones": 2,
                "area_media": 100.0,
                "area_std": 10.0,
                "coeficiente_variacion_area": 0.1,
            }
            with patch("calibrar_dog.evaluar_configuracion", return_value=evidencia):
                resultados = ejecutar_barrido(
                    entrada, [2.0, 5.0], [3.0, 5.0], salida
                )

            self.assertEqual(len(resultados), 2)
            self.assertTrue(salida.exists())
            self.assertIn("sigma1,sigma2", salida.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
