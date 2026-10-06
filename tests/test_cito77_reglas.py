"""Tests para CITO-77: Reglas explicables, umbrales, casos frontera y limitaciones.

Valida la lógica de clasificación documentada en docs/CITO-77-reglas-explicables.md
"""

import unittest
import numpy as np
from src.analysis import (
    clasificar_nucleo_por_area,
    obtener_reglas_clasificacion,
    AREA_PROMEDIO_NUCLEO_NORMAL,
    FACTOR_RIESGO,
    MARGEN_FRONTERA,
    AREA_MINIMA_NUCLEO,
    AREA_MAXIMA_NUCLEO,
    UMBRAL_DOG,
)


class TestReglasClasificacion(unittest.TestCase):
    """Tests para las reglas de clasificación de núcleos."""

    def setUp(self):
        """Configuración común para tests."""
        self.polaridad_clara = 'nucleos-claros'
        self.polaridad_oscura = 'nucleos-oscuros'
        self.umbral_sospechoso = AREA_PROMEDIO_NUCLEO_NORMAL * FACTOR_RIESGO  # 900
        self.limite_inferior = self.umbral_sospechoso * (1 - MARGEN_FRONTERA)  # 810
        self.limite_superior = self.umbral_sospechoso * (1 + MARGEN_FRONTERA)  # 990

    # ============================================================
    # Tests de umbrales y constantes
    # ============================================================

    def test_constantes_calibradas_cito74(self):
        """Verifica que las constantes coinciden con la calibración CITO-74."""
        self.assertEqual(AREA_PROMEDIO_NUCLEO_NORMAL, 300)
        self.assertEqual(FACTOR_RIESGO, 3.0)
        self.assertEqual(MARGEN_FRONTERA, 0.10)
        self.assertEqual(UMBRAL_DOG, 15)

    def test_umbrales_polaridad_clara(self):
        """Verifica umbrales para polaridad 'nucleos-claros'."""
        reglas = obtener_reglas_clasificacion(self.polaridad_clara)
        self.assertEqual(reglas["area_minima_nucleo"], 50)
        self.assertEqual(reglas["area_maxima_nucleo"], 5000)
        self.assertEqual(reglas["umbral_sospechoso"], 900.0)
        self.assertEqual(reglas["limite_frontera_inferior"], 810.0)
        self.assertAlmostEqual(reglas["limite_frontera_superior"], 990.0, places=10)

    def test_umbrales_polaridad_oscura(self):
        """Verifica umbrales para polaridad 'nucleos-oscuros'."""
        reglas = obtener_reglas_clasificacion(self.polaridad_oscura)
        self.assertEqual(reglas["area_minima_nucleo"], 200)
        self.assertEqual(reglas["area_maxima_nucleo"], 300000)
        self.assertEqual(reglas["umbral_sospechoso"], 900.0)  # Mismo umbral de riesgo

    # ============================================================
    # Tests de casos frontera (edge cases) - Tabla 4.1 del documento
    # ============================================================

    def test_area_ruido_minimo(self):
        """Área 10 px² → descartada (ruido)."""
        resultado = clasificar_nucleo_por_area(10, self.polaridad_clara)
        self.assertFalse(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "descartada")
        self.assertFalse(resultado["es_frontera"])
        self.assertIn("ruido", resultado["motivo"].lower())

    def test_area_ruido_limite_inferior(self):
        """Área 49 px² → descartada (ruido)."""
        resultado = clasificar_nucleo_por_area(49, self.polaridad_clara)
        self.assertFalse(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "descartada")

    def test_area_minima_valida(self):
        """Área 50 px² → normal (mínimo válido)."""
        resultado = clasificar_nucleo_por_area(50, self.polaridad_clara)
        self.assertTrue(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "normal")
        self.assertFalse(resultado["es_frontera"])

    def test_area_promedio_normal(self):
        """Área 300 px² → normal (promedio)."""
        resultado = clasificar_nucleo_por_area(300, self.polaridad_clara)
        self.assertTrue(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "normal")
        self.assertFalse(resultado["es_frontera"])

    def test_area_frontera_inferior(self):
        """Área 810 px² → normal PERO frontera (900 × 0.9)."""
        resultado = clasificar_nucleo_por_area(810, self.polaridad_clara)
        self.assertTrue(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "normal")
        self.assertTrue(resultado["es_frontera"])

    def test_area_umbral_exacto(self):
        """Área 900 px² → sospechosa Y frontera (umbral exacto 3×300)."""
        resultado = clasificar_nucleo_por_area(900, self.polaridad_clara)
        self.assertTrue(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "sospechosa")
        self.assertTrue(resultado["es_frontera"])

    def test_area_frontera_superior(self):
        """Área 990 px² → sospechosa Y frontera (900 × 1.1)."""
        resultado = clasificar_nucleo_por_area(990, self.polaridad_clara)
        self.assertTrue(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "sospechosa")
        self.assertTrue(resultado["es_frontera"])

    def test_area_sospechosa_clara(self):
        """Área 1500 px² → sospechosa (lejos del umbral)."""
        resultado = clasificar_nucleo_por_area(1500, self.polaridad_clara)
        self.assertTrue(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "sospechosa")
        self.assertFalse(resultado["es_frontera"])

    def test_area_artefacto_limite(self):
        """Área 4999 px² → sospechosa (dentro de máximo)."""
        resultado = clasificar_nucleo_por_area(4999, self.polaridad_clara)
        self.assertTrue(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "sospechosa")

    def test_area_maxima_valida(self):
        """Área 5000 px² → normal (límite máximo inclusive, >5000 se descarta)."""
        resultado = clasificar_nucleo_por_area(5000, self.polaridad_clara)
        self.assertTrue(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "normal")

    def test_area_artefacto_grande(self):
        """Área 5001 px² → descartada (artefacto grande, > máximo)."""
        resultado = clasificar_nucleo_por_area(5001, self.polaridad_clara)
        self.assertFalse(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "descartada")
        self.assertIn("artefacto", resultado["motivo"].lower())

    # ============================================================
    # Tests de polaridad oscura (umbrales diferentes)
    # ============================================================

    def test_polaridad_oscura_area_minima(self):
        """Polaridad oscura: área 199 → descartada (mínimo 200)."""
        resultado = clasificar_nucleo_por_area(199, self.polaridad_oscura)
        self.assertFalse(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "descartada")

    def test_polaridad_oscura_area_valida(self):
        """Polaridad oscura: área 200 → normal (mínimo válido)."""
        resultado = clasificar_nucleo_por_area(200, self.polaridad_oscura)
        self.assertTrue(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "normal")

    def test_polaridad_oscura_area_maxima(self):
        """Polaridad oscura: área 300000 → normal (límite máximo inclusive)."""
        resultado = clasificar_nucleo_por_area(300000, self.polaridad_oscura)
        self.assertTrue(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "normal")

    def test_polaridad_oscura_area_artefacto(self):
        """Polaridad oscura: área 300001 → descartada (artefacto, > máximo)."""
        resultado = clasificar_nucleo_por_area(300001, self.polaridad_oscura)
        self.assertFalse(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "descartada")

    # ============================================================
    # Tests de estructura de retorno
    # ============================================================

    def test_estructura_retorno_completa(self):
        """Verifica que el dict de retorno tiene todas las claves requeridas."""
        resultado = clasificar_nucleo_por_area(300, self.polaridad_clara)
        claves_requeridas = {
            "es_valida", "clasificacion", "es_frontera",
            "umbral_sospechoso", "motivo"
        }
        self.assertEqual(set(resultado.keys()), claves_requeridas)
        self.assertIsInstance(resultado["es_valida"], bool)
        self.assertIsInstance(resultado["es_frontera"], bool)
        self.assertIsInstance(resultado["umbral_sospechoso"], float)
        self.assertIsInstance(resultado["motivo"], str)
        self.assertIn(resultado["clasificacion"], ["normal", "sospechosa", "descartada"])

    def test_motivo_legible(self):
        """Verifica que el motivo es legible y explicativo."""
        resultado_normal = clasificar_nucleo_por_area(300, self.polaridad_clara)
        resultado_sospechosa = clasificar_nucleo_por_area(1000, self.polaridad_clara)
        resultado_descartada = clasificar_nucleo_por_area(10, self.polaridad_clara)

        self.assertIn("umbral", resultado_normal["motivo"].lower())
        self.assertIn("riesgo", resultado_sospechosa["motivo"].lower())
        self.assertIn("ruido", resultado_descartada["motivo"].lower())

    # ============================================================
    # Tests de consistencia de umbrales
    # ============================================================

    def test_umbral_sospechoso_consistente(self):
        """El umbral sospechoso debe ser consistente en todas las clasificaciones."""
        for area in [100, 300, 810, 900, 990, 1500]:
            resultado = clasificar_nucleo_por_area(area, self.polaridad_clara)
            self.assertEqual(resultado["umbral_sospechoso"], 900.0)

    def test_frontera_simetrica_alrededor_umbral(self):
        """La zona frontera debe ser simétrica ±10% alrededor del umbral."""
        self.assertEqual(self.limite_inferior, 810.0)
        self.assertAlmostEqual(self.limite_superior, 990.0, places=10)
        # Verificar que 810 y 990 están a la misma distancia relativa
        self.assertAlmostEqual(
            (self.umbral_sospechoso - self.limite_inferior) / self.umbral_sospechoso,
            MARGEN_FRONTERA
        )
        self.assertAlmostEqual(
            (self.limite_superior - self.umbral_sospechoso) / self.umbral_sospechoso,
            MARGEN_FRONTERA
        )

    # ============================================================
    # Tests de validación de entrada
    # ============================================================

    def test_area_negativa(self):
        """Área negativa debe ser descartada."""
        resultado = clasificar_nucleo_por_area(-10, self.polaridad_clara)
        self.assertFalse(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "descartada")

    def test_area_cero(self):
        """Área cero debe ser descartada."""
        resultado = clasificar_nucleo_por_area(0, self.polaridad_clara)
        self.assertFalse(resultado["es_valida"])
        self.assertEqual(resultado["clasificacion"], "descartada")

    def test_area_float(self):
        """Área como float debe funcionar correctamente."""
        resultado = clasificar_nucleo_por_area(810.5, self.polaridad_clara)
        self.assertTrue(resultado["es_valida"])
        self.assertTrue(resultado["es_frontera"])


class TestObtenerReglasClasificacion(unittest.TestCase):
    """Tests para la función obtener_reglas_clasificacion."""

    def test_retorna_dict_completo(self):
        """Verifica que retorna un dict con todas las claves esperadas."""
        reglas = obtener_reglas_clasificacion('nucleos-claros')
        claves_esperadas = {
            "area_minima_nucleo", "area_maxima_nucleo",
            "area_promedio_nucleo_normal", "factor_riesgo",
            "umbral_sospechoso", "limite_frontera_inferior",
            "limite_frontera_superior"
        }
        self.assertEqual(set(reglas.keys()), claves_esperadas)

    def test_valores_numericos(self):
        """Verifica que todos los valores son numéricos."""
        reglas = obtener_reglas_clasificacion('nucleos-claros')
        for clave, valor in reglas.items():
            self.assertIsInstance(valor, (int, float), f"Clave {clave} no es numérica: {valor}")

    def test_polaridad_invalida_lanza_error(self):
        """Polaridad inválida debe lanzar KeyError (dict access)."""
        with self.assertRaises(KeyError):
            obtener_reglas_clasificacion('polaridad-inexistente')


class TestLimitacionesConocidas(unittest.TestCase):
    """Tests que documentan limitaciones conocidas del sistema."""

    def test_regla_3x_fija_no_adaptativa(self):
        """La regla 3x usa factor fijo, no se adapta a población."""
        # Esto es una limitación documentada, no un bug
        self.assertEqual(FACTOR_RIESGO, 3.0)
        # TODO: En producción, calibrar por población/etnia/edad

    def test_area_promedio_temporal(self):
        """AREA_PROMEDIO_NUCLEO_NORMAL = 300 es valor temporal (CITO-74)."""
        # Documentado en analysis.py: "¡CALIBRAR CON DATOS REALES!"
        self.assertEqual(AREA_PROMEDIO_NUCLEO_NORMAL, 300)
        # En producción, usar calibrar_area_promedio() con ground truth real

    def test_umbral_dog_fijo(self):
        """UMBRAL_DOG = 15 es fijo antes de Otsu; puede fallar en imágenes uniformes."""
        self.assertEqual(UMBRAL_DOG, 15)
        # Limitación: Otsu asume distribución bimodal

    def test_watershed_requiere_8bit_3channel(self):
        """Watershed requiere conversión que puede perder precisión."""
        # Documentado en analysis.py: conversión a uint8 3-channel
        # Limitación conocida de OpenCV

    def test_no_distingue_tipos_celulares(self):
        """El sistema clasifica todo como 'núcleo' sin distinción morfológica."""
        # Limitación: requiere etapa posterior de clasificación
        # No es un test que falle, sino documentación de limitación
        pass


class TestMensajeRevisionExperta(unittest.TestCase):
    """Tests para verificar que el mensaje de revisión experta está presente."""

    def test_mensaje_experta_en_documentacion(self):
        """Verifica que el mensaje de revisión experta está en la documentación."""
        import os
        doc_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'CITO-77-reglas-explicables.md')
        self.assertTrue(os.path.exists(doc_path), "Documento CITO-77 no existe")

        with open(doc_path, 'r', encoding='utf-8') as f:
            contenido = f.read()

        # Verificar elementos clave del mensaje
        self.assertIn("REVISIÓN EXPERTA", contenido.upper())
        self.assertIn("PROTOTIPO DE INVESTIGACIÓN", contenido.upper())
        self.assertIn("NO CONSTITUYE DIAGNÓSTICO", contenido.upper())
        self.assertIn("FALSOS NEGATIVOS", contenido.upper())
        self.assertIn("FALSOS POSITIVOS", contenido.upper())


if __name__ == '__main__':
    unittest.main()