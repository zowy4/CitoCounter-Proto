# Experimentación y bitácora

La bitácora documenta parámetros, resultados automáticos y revisión manual. Es una herramienta de trazabilidad, no sustituye un protocolo de validación científica.

## Antes de ejecutar

- Copia la imagen a `data/raw/` o usa una ruta válida.
- Define una hipótesis y cambia un solo parámetro.
- Anota `Sigma1`, `Sigma2`, área mínima y área de referencia.

## Ejecutar y observar

```bash
python main.py data/raw/muestra.jpg --sigma1 3.0 --sigma2 5.0 --bitacora T-001
```

Comprueba que el pipeline termina sin errores y guarda el resultado. Evalúa visualmente el DoG, las detecciones y el panel comparativo.

## Registrar después

Completa la fila correspondiente en `bitacora_experimentos.csv` con:

- total, normales, sospechosas y porcentaje de riesgo;
- falsos positivos y falsos negativos estimados;
- precisión estimada y calidad del DoG;
- observaciones y siguiente ajuste;
- responsable y fecha.

No abras el CSV con un editor que lo bloquee mientras Python esté escribiendo.

## Evidencia

Guarda como mínimo un panel comparativo en `data/results/screenshots/` siguiendo la nomenclatura de [capturas](../../data/results/screenshots/README.md). Conserva también la configuración usada y la versión del código.

## Métricas para validación

Con anotaciones expertas separadas del conjunto de calibración, calcula:

- precisión = TP / (TP + FP);
- sensibilidad = TP / (TP + FN);
- F1 = media armónica de precisión y sensibilidad;
- IoU para evaluar solapamiento de cajas o regiones.

El script `analizar_bitacora.py` resume la bitácora; no debe interpretarse como cálculo de métricas clínicas si no existe ground truth válido.

## Lista imprimible

- [ ] Imagen, ID y fecha registrados.
- [ ] Hipótesis y parámetros anotados.
- [ ] Ejecución completada sin errores.
- [ ] DoG y detecciones revisados visualmente.
- [ ] Falsos positivos y negativos estimados.
- [ ] Panel guardado.
- [ ] Bitácora actualizada.
- [ ] Próximo ajuste definido.
