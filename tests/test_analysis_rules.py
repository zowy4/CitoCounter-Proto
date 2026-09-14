import unittest

from src.analysis import (
    AREA_MINIMA_NUCLEO,
    AREA_MAXIMA_NUCLEO,
    obtener_reglas_clasificacion,
    clasificar_nucleo_por_area,
)


class AnalysisRulesTests(unittest.TestCase):
    def test_descarta_area_menor_a_minima(self):
        decision = clasificar_nucleo_por_area(AREA_MINIMA_NUCLEO - 1)
        self.assertFalse(decision["es_valida"])
        self.assertEqual(decision["clasificacion"], "descartada")

    def test_descarta_area_mayor_a_maxima(self):
        decision = clasificar_nucleo_por_area(AREA_MAXIMA_NUCLEO + 1)
        self.assertFalse(decision["es_valida"])
        self.assertEqual(decision["clasificacion"], "descartada")

    def test_clasifica_sospechosa_en_umbral(self):
        reglas = obtener_reglas_clasificacion()
        decision = clasificar_nucleo_por_area(reglas["umbral_sospechoso"])
        self.assertTrue(decision["es_valida"])
        self.assertEqual(decision["clasificacion"], "sospechosa")

    def test_marca_frontera_en_rango(self):
        reglas = obtener_reglas_clasificacion()
        area_frontera = reglas["limite_frontera_inferior"] + 1
        decision = clasificar_nucleo_por_area(area_frontera)
        self.assertTrue(decision["es_frontera"])
        self.assertEqual(decision["clasificacion"], "normal")


if __name__ == "__main__":
    unittest.main()
