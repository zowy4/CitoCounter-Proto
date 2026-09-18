import unittest

from src.analysis import (
    AREA_MINIMA_NUCLEO,
    AREA_MAXIMA_NUCLEO,
    obtener_reglas_clasificacion,
    clasificar_nucleo_por_area,
)


class AnalysisRulesTests(unittest.TestCase):
    def test_descarta_area_menor_a_minima(self):
        # Usar el valor para polaridad por defecto (nucleos-claros)
        area_min = AREA_MINIMA_NUCLEO['nucleos-claros']
        decision = clasificar_nucleo_por_area(area_min - 1, 'nucleos-claros')
        self.assertFalse(decision["es_valida"])
        self.assertEqual(decision["clasificacion"], "descartada")

    def test_descarta_area_mayor_a_maxima(self):
        area_max = AREA_MAXIMA_NUCLEO['nucleos-claros']
        decision = clasificar_nucleo_por_area(area_max + 1, 'nucleos-claros')
        self.assertFalse(decision["es_valida"])
        self.assertEqual(decision["clasificacion"], "descartada")

    def test_clasifica_sospechosa_en_umbral(self):
        reglas = obtener_reglas_clasificacion()
        decision = clasificar_nucleo_por_area(reglas["umbral_sospechoso"], 'nucleos-claros')
        self.assertTrue(decision["es_valida"])
        self.assertEqual(decision["clasificacion"], "sospechosa")

    def test_marca_frontera_en_rango(self):
        reglas = obtener_reglas_clasificacion()
        area_frontera = reglas["limite_frontera_inferior"] + 1
        decision = clasificar_nucleo_por_area(area_frontera, 'nucleos-claros')
        self.assertTrue(decision["es_frontera"])
        self.assertEqual(decision["clasificacion"], "normal")


if __name__ == "__main__":
    unittest.main()
