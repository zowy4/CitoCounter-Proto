# CITO-94: Casos especiales

CITO-94 reutiliza la implementación y evidencia de CITO-86, pues ambos
describen la mitigación de superposición celular, artefactos de tinción e
iluminación irregular.

La fuente técnica y las pruebas reproducibles están en
[evidencia-cito86-casos-especiales.md](evidencia-cito86-casos-especiales.md)
y `tests/test_cito86_casos_especiales.py`.

No se duplicó código ni se alteraron los parámetros validados. La evidencia
incluye `watershed_picos`, máscara de borde, filtro bilateral, CLAHE adaptativo
y advertencias de calidad. Estas estrategias continúan siendo experimentales y
requieren revisión experta para uso con imágenes reales.
