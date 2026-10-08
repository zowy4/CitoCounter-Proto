# Guía de estudio del proyecto CitoCounter Proto

## 1. Qué es y para qué sirve

CitoCounter Proto es un prototipo de investigación en Python que procesa imágenes de citología cervical para localizar regiones candidatas a núcleo, estimar su área y mostrar una clasificación experimental basada en tamaño. Su propósito es explorar y comparar métodos de visión por computadora, no emitir diagnósticos.

El programa detecta **regiones que parecen núcleos**: no segmenta ni clasifica células completas según Bethesda, no determina malignidad y no sustituye la revisión de un citólogo, citotecnólogo o patólogo. “Sospechoso” significa únicamente que la región detectada superó la regla de área configurada; no es una probabilidad de cáncer ni una conclusión clínica.

> **Límite de uso:** es un prototipo de investigación, no un dispositivo médico ni un sistema validado para diagnóstico. Todo resultado requiere revisión experta. No uses imágenes identificables o datos de pacientes sin autorización y controles adecuados.

## 2. Cómo funciona el análisis

El flujo principal de la interfaz y del CLI es:

1. Cargar una imagen y conservar la original para compararla con el resultado.
2. Convertirla a escala de grises.
3. Aplicar opcionalmente reducción de ruido y mejora de contraste.
4. Ajustar la polaridad; opcionalmente crear y aplicar una máscara HSV.
5. Calcular la respuesta Difference of Gaussians (DoG).
6. Umbralizar la respuesta con Otsu y extraer contornos externos.
7. Aplicar filtros de área y, según la polaridad y el método elegido, filtros adicionales de forma.
8. Asignar a cada contorno válido una etiqueta basada en el área.
9. Mostrar la imagen anotada, los conteos y datos de análisis; la interfaz permite exportar resultados.

Un contorno es una detección algorítmica, no una anotación de referencia (“ground truth”). Una coincidencia visual o un conteo parecido tampoco demuestra que cada núcleo se haya localizado correctamente.

## 3. Qué es sigma y cómo se usa

Sigma (σ) es la desviación estándar del desenfoque Gaussiano, expresada en píxeles. Controla la escala espacial del suavizado: cuanto mayor es σ, más se extiende el desenfoque y más estructuras pequeñas se suavizan.

El filtro calcula dos versiones suavizadas de la imagen y resta una de la otra:

- `G1 = GaussianBlur(imagen, σ1)`: escala más fina.
- `G2 = GaussianBlur(imagen, σ2)`: escala más amplia.
- `DoG = G1 - G2`: resalta cambios de intensidad que difieren entre esas escalas.

La resta se conserva primero en `float32` para no perder valores negativos por el tipo `uint8`. Después se normaliza para mostrarla como imagen de 8 bits. Por eso el DoG es una **respuesta de contraste a una escala**, no una medición directa del diámetro físico de un núcleo.

### Guía práctica

- La aplicación y el CLI parten actualmente de `σ1=7.0` y `σ2=8.0`. Se exige `σ2 > σ1`.
- La guía de algoritmos incluye como heurística experimental una relación `σ2/σ1` aproximada de 1.6–2.0. No es un requisito del programa ni una garantía; además, los valores iniciales actuales 7 y 8 no cumplen esa relación (8/7 ≈ 1.14).
- Aumentar ambos sigmas cambia la escala de respuesta; no significa simplemente que el detector acepte núcleos de un diámetro fijo. Un sigma demasiado pequeño puede conservar ruido y uno demasiado grande puede suavizar o unir detalles.
- Compara primero la imagen DoG y la salida con un conjunto autorizado y anotaciones espaciales. Cambia **un solo parámetro cada vez**, anota los valores y conserva el resultado para poder reproducirlo.
- En la interfaz, la relación `σ2/σ1` se muestra como orientación y aparece un error cuando `σ2 ≤ σ1`. El rango recomendado no se fuerza automáticamente.

**No presentes los sigmas como parámetros clínicos calibrados.** La elección debe comprobarse experimentalmente para cada conjunto de imágenes y protocolo.

## 4. Opciones de la interfaz, una por una

Los controles están en la barra lateral. El efecto observado puede variar con la tinción, iluminación, resolución, polaridad y calidad de la imagen.

### 4.1 Preprocesamiento

| Opción visible | Qué hace | Cuándo podría servir / precaución |
|---|---|---|
| **Polaridad de los núcleos** | `nucleos-claros` deja la intensidad como está; `nucleos-oscuros` invierte la imagen en gris antes del DoG para que los núcleos oscuros se comporten como regiones claras. | Elige según la apariencia real de los núcleos y el fondo. La inversión no clasifica la muestra y una polaridad incorrecta puede cambiar sustancialmente las detecciones. |
| **Mejorar Contraste (CLAHE)** | Activa el paso de mejora de contraste. Si se desactiva, no se aplica el método seleccionado en “Modo CLAHE”. | Puede ayudar con contraste local débil o iluminación desigual. También puede hacer más visibles artefactos o ruido. Compara con y sin mejora. |
| **Modo CLAHE** | Selector de método: `clahe`, `auto`, `histogram` o `normalize`. | `clahe` mejora contraste local con límite de amplificación; `auto` escoge según la desviación estándar (CLAHE suave/básico o ecualización global); `histogram` ecualiza globalmente; `normalize` remapea el mínimo y máximo al intervalo 0–255. Aunque el control se llama “Modo CLAHE”, las dos últimas opciones no son CLAHE. |
| **Reducir Ruido** | Aplica un filtro bilateral antes de mejorar contraste. | Puede reducir variaciones pequeñas preservando parte de los bordes. Los niveles bajo/medio/alto aumentan la intensidad; un nivel alto puede borrar detalles finos. Activarlo no garantiza menos falsos positivos. |

El orden del preprocesamiento en el código es: gris → ruido opcional → contraste opcional → inversión de polaridad, si aplica → máscara HSV opcional.

### 4.2 Segmentación avanzada

| Opción visible | Qué hace | Cuándo podría servir / precaución |
|---|---|---|
| **Segmentación HSV (Color)** | Convierte la imagen de color a HSV y crea una máscara a partir del canal seleccionado: `saturation` (saturación) o `value` (brillo). La máscara se aplica a la imagen en gris antes del DoG. | Puede ayudar si los núcleos se distinguen del entorno por color o brillo. No reconoce tipos celulares: umbralizar S o V también puede seleccionar tinción, fondo y artefactos. |
| **Método HSV** | `saturation` selecciona por intensidad de color; `value` selecciona por intensidad/brillo. | Mira la máscara HSV antes de interpretar el conteo. La opción `value` usa un umbral de intensidad, no una regla clínica de oscuridad nuclear. |
| **Umbral HSV** | Fija el corte, de 0 a 255, para el canal S o V seleccionado. | El código aplica umbral binario; después realiza apertura morfológica y una dilatación ligera. Ajustarlo puede incluir o excluir regiones enteras. No hay un valor universal. |

### 4.3 Separación de núcleos superpuestos

| Método | Qué hace | Precaución |
|---|---|---|
| **Sin separación (original)** | Detecta directamente contornos conectados en la máscara binaria. Es el modo inicial. Dos núcleos unidos pueden aparecer como una sola región. | Úsalo como referencia para comparar los métodos experimentales. |
| **Watershed (Transformada de distancia)** | Usa regiones/marcadores y el algoritmo watershed de OpenCV para intentar dividir regiones. | La implementación actual calcula la transformada de distancia, pero genera los marcadores con componentes conectados; no usa esa transformada para construir los marcadores. Por ello, no debe suponerse que separará correctamente núcleos en contacto. Puede alterar el conteo. |
| **Máximos locales (picos DoG)** | Busca picos en la respuesta DoG y estima regiones alrededor de cada pico. | Es heurístico y experimental; puede duplicar, omitir o asignar mal regiones. |

La separación está desactivada por defecto. Compara siempre el mismo caso con “Sin separación” y el método alternativo; el aviso experimental de la interfaz existe porque los conteos pueden cambiar.

### 4.4 Opciones de visualización

| Opción visible | Qué hace actualmente |
|---|---|
| **Dibujar Contornos Reales** | Muestra los contornos calculados por el detector sobre la imagen. “Reales” no significa ground truth: son contornos predichos por el algoritmo. Si se desactiva, la vista usa cajas delimitadoras. |
| **Mostrar Áreas en Imagen** | El control está en la interfaz, pero actualmente no se conecta a la función de dibujo y no cambia la imagen mostrada. No esperes etiquetas de área al activarlo. Las áreas sí aparecen en la sección de criterios/clasificación y en los datos exportados cuando están disponibles. |

Los colores de resultado identifican las etiquetas del prototipo (verde: normal según regla de área; rojo: sospechoso según regla de área). No expresan un diagnóstico.

## 5. Cómo calcula y etiqueta las regiones

La detección convierte la respuesta DoG en una máscara binaria mediante umbralización de Otsu, extrae contornos externos y calcula cada área con `cv2.contourArea`, en píxeles cuadrados. Según el modo, las regiones se filtran y/o se separan.

Los valores actuales en `src/analysis.py` son reglas provisionales:

- Área mínima de referencia normal: **300 px²**.
- Factor de riesgo: **3**; umbral: `300 × 3 = 900 px²`.
- Zona frontera: **±10%**, o **810–990 px²**, marcada para revisión. Estar en esta zona no cambia la regla subyacente: las áreas desde 900 px² pueden seguir etiquetándose como sospechosas.
- Límites para descartar por área dependen de la polaridad: `nucleos-claros` 50–5000 px²; `nucleos-oscuros` 200–300000 px².
- Para `nucleos-oscuros`, en el modo sin separación también se aplican filtros de circularidad y relación de aspecto.

Una región menor al mínimo se descarta como ruido; una mayor al máximo se descarta como posible artefacto; las regiones dentro del rango se marcan normal o sospechosa por el umbral de área. Estas reglas no analizan cromatina, forma nuclear completa, relación núcleo/citoplasma, contexto celular ni criterios Bethesda. El área de referencia y sus límites no deben describirse como calibrados clínicamente.

## 6. Tecnologías y archivos principales

| Tecnología / componente | Uso en el proyecto |
|---|---|
| **Python** | Lenguaje del pipeline, CLI, interfaz y herramientas de evaluación. |
| **OpenCV (`cv2`)** | Lectura y transformación de imágenes, Gaussian blur, DoG, HSV, umbralización, contornos, filtros y visualización. |
| **NumPy** | Arreglos de imagen y cálculos numéricos. |
| **Streamlit** | Interfaz web local para cargar imágenes, ajustar controles e inspeccionar resultados. |
| **Matplotlib** | Gráficas y herramientas de análisis/calibración. |
| **CSV y JSON** | Bitácoras, reportes y exportación/intercambio de resultados. |
| **unittest** | Pruebas automatizadas del repositorio. |

Archivos para orientarse:

- `main.py`: ejecución desde terminal.
- `app.py`: interfaz Streamlit.
- `src/preprocessing.py`: lectura, gris, contraste, ruido, polaridad y HSV.
- `src/dog_filter.py`: DoG y visualización de gaussianas.
- `src/analysis.py`: umbralización, contornos, separación y regla por área.
- `src/visualization.py`: vistas y anotaciones.
- `calcular_metricas_cito23.py`: cálculo exploratorio de métricas con emparejamiento espacial.

## 7. Cómo probarlo

Instala y verifica el entorno:

```bash
python -m pip install -r requirements.txt
python verificar_entorno.py
```

Prueba la interfaz:

```bash
streamlit run app.py
```

Luego abre la dirección local que indica Streamlit, selecciona una imagen autorizada o una imagen disponible en el dataset, deja los valores iniciales como referencia y compara primero original, preprocesamiento, DoG y análisis final. Repite cambiando un único control.

Prueba CLI con una imagen:

```bash
python main.py data/raw/imagen.jpg --no-gui --sigma1 7.0 --sigma2 8.0
```

Procesa una carpeta:

```bash
python main.py data/raw --lote --no-gui --sigma1 7.0 --sigma2 8.0
```

Ejecuta comprobaciones del proyecto:

```bash
python -m unittest discover -s tests -v
python validar_consistencia_dataset.py
```

La comprobación del dataset requiere que los datos y anotaciones estén disponibles localmente. No agregues al repositorio imágenes originales, datos identificables o anotaciones brutas.

Para una evaluación experimental, utiliza un conjunto autorizado, congelado y separado del usado para ajustar parámetros; consigue anotaciones espaciales expertas, documenta la versión/dataset/parámetros/fecha y calcula TP, FP y FN por emparejamiento espacial. Cambia un parámetro por experimento. Un conteo o porcentaje mostrado por la app por sí solo no sustituye esa evaluación.

## 8. Rendimiento reportado y validez

No existe un único “porcentaje de detección” que describa toda la validez del sistema. El conteo de detecciones es distinto de la precisión de las detecciones, la sensibilidad y la calidad de segmentación.

El resumen guardado para **CITO-23** reporta un experimento exploratorio sobre **9 imágenes**, con emparejamiento de centroides a una distancia de **10 px**:

| Medida | Resultado del resumen |
|---|---:|
| Verdaderos positivos (TP) | 15 |
| Falsos positivos (FP) | 24 |
| Falsos negativos (FN) | 27 |
| Precisión `TP/(TP+FP)` | 38.46% |
| Sensibilidad/recall `TP/(TP+FN)` | 35.71% |
| F1 | 37.04% |
| Jaccard de detección | 22.73% |

Estos valores son un resultado exploratorio concreto, no una tasa de acierto garantizada ni validación clínica. La precisión no es “el porcentaje total de células detectadas”; sensibilidad responde qué fracción de las anotadas se encontró; el F1 combina precisión y sensibilidad. El Jaccard reportado es de **detección**, no una validación de límites/segmentación.

El repositorio también contiene una salida distinta de un validador que no encontró archivos de etiquetas y produjo ceros. Esos ceros no miden el rendimiento del detector: indican que no se pudo hacer esa evaluación con las anotaciones esperadas. Antes de repetir o citar métricas, verifica que el ground truth corresponda a las mismas imágenes y coordenadas, y reporta el protocolo, versión y denominadores. Hasta completar validación independiente con ground truth experto y datos autorizados, la validez es **experimental y limitada**.

El “% de riesgo” de la interfaz se calcula a partir de regiones etiquetadas sospechosas entre las regiones válidas. **No es probabilidad de enfermedad**, sensibilidad ni precisión.

## 9. Preguntas que pueden hacerte y respuestas breves

**¿Qué hace el proyecto?**  
Resalta regiones con DoG, obtiene contornos y cuenta/clasifica candidatos a núcleo usando principalmente su área. Permite inspeccionar el procesamiento y comparar parámetros.

**¿Detecta células o diagnostica cáncer?**  
No. Trabaja con regiones candidatas a núcleo y una regla experimental por área. No determina diagnóstico, tipo celular ni lesión.

**¿Qué significa sigma?**  
Es la escala, en píxeles, del desenfoque Gaussiano. DoG resta dos escalas para resaltar ciertas variaciones de tamaño/intensidad. Los sigmas cambian la respuesta; no son una medida directa del tamaño de una célula.

**¿Por qué hay dos sigmas?**  
La resta entre un desenfoque más fino y uno más amplio conserva cambios que difieren entre escalas. `σ2` debe ser mayor que `σ1`.

**¿Cómo decide que algo es sospechoso?**  
Por área: referencia provisional 300 px² × factor 3 = 900 px². No usa un modelo clínico; las detecciones cerca del límite tienen una marca de frontera de ±10%.

**¿Qué porcentaje de detección tiene?**  
No hay un porcentaje universal. El resumen exploratorio de nueve imágenes reportó precisión 38.46%, recall 35.71% y F1 37.04% con emparejamiento espacial a 10 px. No está validado clínicamente ni permite prometer ese resultado en otras imágenes.

**¿Qué significan falsos positivos y falsos negativos?**  
Un FP es una detección que no coincide con una anotación de referencia; un FN es una anotación que no fue detectada. Ambos dependen de tener ground truth espacial correcto.

**¿CLAHE, HSV o Watershed garantizan mejores resultados?**  
No. Son opciones experimentales que cambian la imagen/máscara o intentan separar regiones. Pueden ayudar en algunos casos y empeorar otros; se comparan sobre datos etiquetados.

**¿Qué es “Dibujar Contornos Reales”?**  
Son contornos extraídos por el programa, no contornos verdaderos confirmados por una persona.

**¿Qué ocurre con “Mostrar Áreas en Imagen”?**  
El control aparece, pero no está conectado a la visualización actual. Las áreas se consultan en los criterios de clasificación; el interruptor no dibuja sus números sobre la imagen.

**¿Se puede usar para tomar decisiones clínicas?**  
No. Es un prototipo de investigación; todas las salidas deben ser revisadas por profesionales y no deben usarse como diagnóstico.

## 10. Documentación relacionada

Usa [README.md](README.md) como índice del proyecto y consulta las guías existentes, sin duplicar sus instrucciones:

- [Importar y organizar el dataset](docs/guide/dataset.md)
- [Registrar y evaluar experimentos](docs/guide/experimentos.md)
- [Plan del proyecto](docs/plan-proyecto.md)
- [Seguimiento Jira](docs/guia-maestra-desarrollo.md)
- [Algoritmos y métricas](docs/algoritmos_metricas.md)

---

**Versión de esta guía:** 2.0 · **Fecha:** 2026-10-08
