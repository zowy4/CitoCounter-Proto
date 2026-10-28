# Inicio y primera prueba

Esta guía sirve para comprobar el entorno y ejecutar una prueba de humo antes de usar imágenes reales. El resultado de la primera prueba no es una validación clínica.

## 1. Preparar el entorno

```bash
python -m pip install -r requirements.txt
python verificar_entorno.py
```

La comprobación debe confirmar Python, dependencias, carpetas y archivos del proyecto.

## 2. Preparar una imagen de prueba

Usa una imagen autorizada o una fuente académica pública con núcleos visibles. Debe ser JPG o PNG y tener, preferentemente, al menos 800 x 600 píxeles. Para datos reales, elimina identificadores y sigue el protocolo institucional.

Coloca la imagen en `data/raw/`. Por ejemplo: `data/raw/muestra_prueba.jpg`.

## 3. Ejecutar el análisis

```bash
python main.py data/raw/muestra_prueba.jpg
```

Para una ejecución sin ventanas:

```bash
python main.py data/raw/muestra_prueba.jpg --no-gui
```

## 4. Revisar el resultado

- **DoG:** debe mostrar bordes de los núcleos con contraste suficiente; ruido excesivo indica que hay que revisar sigmas o preprocesamiento.
- **Detecciones:** algunos falsos positivos o una clasificación desbalanceada pueden ser normales antes de calibrar el área de referencia.
- **Panel y bitácora:** revisa los archivos en `data/results/` y la entrada generada en `bitacora_experimentos.csv`.

La salida ayuda a evaluar el pipeline; no confirma que una célula sea normal o anormal desde el punto de vista clínico.

## 5. Registrar evidencia

Para cada prueba conserva:

- imagen y parámetros usados;
- total de detecciones, normales y sospechosas;
- calidad visual del DoG;
- falsos positivos y negativos estimados;
- panel comparativo en `data/results/screenshots/`;
- siguiente ajuste y responsable.

## Interpretación rápida

| Observación | Siguiente comprobación |
|---|---|
| DoG gris o ruidoso | Ajustar `--sigma1`, `--sigma2` o probar `--ruido` |
| Cero detecciones | Revisar imagen, umbral y área mínima en `src/analysis.py` |
| Demasiadas detecciones | Revisar reducción de ruido y área mínima |
| Todo queda sospechoso | Calibrar `AREA_PROMEDIO_NUCLEO_NORMAL` con datos autorizados |

Cambia un parámetro cada vez y registra el motivo para conservar trazabilidad.
