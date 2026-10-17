# CITO-96: Splits y ground truth trazable

## Verificacion ejecutada

Con `PYTHONIOENCODING=utf-8 python validar_consistencia_dataset.py`:

- Train: 1400 imagenes y 1400 etiquetas (70%).
- Validacion: 400 imagenes y 400 etiquetas (20%).
- Test: 200 imagenes y 200 etiquetas (10%).
- El manifiesto CSV contiene 2000 registros, todos presentes como archivos.

## Bloqueo de cierre

El validador detecto `MUESTRA_197` con diagnostico HSIL sin etiqueta de clase
anormal. La estructura, el matching y la distribucion pasan, pero esta
incoherencia impide afirmar ground truth completamente trazable.

La anotacion no se modifica automaticamente: requiere revision de la persona
experta responsable antes de corregirla y repetir el validador.
