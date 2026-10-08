# Guion integral de presentación y demostración — CitoCounter Proto

Este guion combina la explicación de estudio del proyecto con la demostración de la interfaz. La idea es que quien presenta pueda explicar el sistema completo, no solo recorrer sus botones. Los textos entre comillas se pueden leer tal cual; las indicaciones en **Mostrar** describen qué hacer en pantalla.

> **Mensaje que debe mantenerse durante toda la sesión:** CitoCounter Proto es un prototipo de investigación. No es un dispositivo médico, no establece diagnósticos y no debe usarse para tomar decisiones clínicas. “Normal”, “sospechosa” y “% de riesgo” son etiquetas de una regla técnica experimental, no conclusiones sobre una paciente.

## 1. Preparación antes de presentar

1. Instala las dependencias del repositorio y verifica el entorno:

   ```bash
   python -m pip install -r requirements.txt
   python verificar_entorno.py
   ```

2. Inicia la interfaz:

   ```bash
   streamlit run app.py
   ```

   Abre en el navegador la dirección local que indique Streamlit.

3. Prepara una imagen de demostración autorizada y anonimizada que esté disponible localmente o se pueda cargar. Verifica que abre y que el procesamiento termina antes de la sesión. No uses datos identificables ni presupongas que la aplicación borra automáticamente los archivos cargados.
4. Ten a mano este guion y `CUESTIONARIO_CITOLOGOS.md`. Registra comentarios con un código de sesión, sin datos personales ni información identificable de pacientes.
5. Mantén los valores iniciales al principio; cambia un solo control a la vez y anota qué cambiaste. No presentes ninguna salida como ground truth.

## 2. Apertura: qué es el proyecto y para qué sirve

**Tiempo orientativo:** 3–5 minutos.

**Mostrar:** encabezado del dashboard, aviso experimental y vista general de la interfaz.

**Decir:**

> “Gracias por participar. Voy a presentar CitoCounter Proto, un prototipo de investigación escrito en Python para procesar imágenes de citología cervical. El proyecto explora cómo técnicas de visión por computadora pueden resaltar y localizar regiones que parecen núcleos, estimar su área y facilitar la inspección visual de esas detecciones.”

> “La función del prototipo es experimental: permite cargar imágenes, probar distintos parámetros de procesamiento, observar las regiones candidatas y comparar resultados. Nos interesa tanto entender el flujo técnico como saber si la interfaz es clara y qué limitaciones habría que mejorar.”

> “Es importante precisar qué no hace: no analiza una paciente ni una citología completa, no clasifica lesiones según Bethesda, no determina malignidad y no sustituye el criterio profesional. La palabra ‘sospechosa’ en pantalla significa únicamente que una región detectada superó un umbral de área programado. No es un diagnóstico, ni una probabilidad de cáncer, ni una recomendación clínica.”

> “La sesión de hoy evalúa la explicación y la usabilidad del prototipo. No estamos pidiendo que valide un diagnóstico. Usaremos solo una imagen de demostración autorizada y no anotaremos datos personales.”

**Preguntar:** “Antes de ver el flujo, ¿qué esperaría que hiciera un sistema de detección de núcleos?”

**Aclaración si preguntan por el objetivo del proyecto:**

> “El objetivo técnico es estudiar detección y conteo automatizado de regiones nucleares y producir resultados reproducibles para investigación. Para afirmar qué tan bien funciona, se necesita comparar cada detección con anotaciones espaciales expertas en datos autorizados. El conteo por sí solo no basta.”

## 3. Qué tecnologías y componentes tiene

**Mostrar:** primero el panel general de la app; si se desea, mostrar brevemente los nombres de archivos del repositorio, sin salir de la sesión de demostración.

**Decir:**

> “La lógica principal está desarrollada en Python. OpenCV se usa para leer y transformar imágenes, aplicar desenfoques y filtros, crear máscaras, umbralizar y extraer contornos. NumPy maneja los arreglos de píxeles y los cálculos numéricos. Streamlit proporciona este dashboard local para elegir imágenes, cambiar parámetros y comparar resultados.”

> “El proyecto también tiene una ejecución por terminal, una bitácora y exportaciones en formatos como CSV y JSON. Las pruebas automatizadas comprueban partes del código, pero pasar pruebas de software no equivale a demostrar precisión clínica.”

**Si preguntan dónde vive cada parte, decir:**

- `main.py`: ejecuta el pipeline desde la terminal.
- `app.py`: implementa esta interfaz Streamlit.
- `src/preprocessing.py`: prepara la imagen, cambia polaridad y puede hacer HSV.
- `src/dog_filter.py`: calcula la respuesta DoG.
- `src/analysis.py`: umbraliza, extrae y filtra contornos y aplica la regla de área.
- `src/visualization.py`: dibuja las vistas y anotaciones.
- `calcular_metricas_cito23.py`: calcula métricas experimentales cuando hay correspondencia espacial con anotaciones.

**Decir para cerrar esta parte:**

> “No es una red neuronal que haya aprendido diagnósticos de pacientes. La parte principal de detección es un pipeline explícito de procesamiento de imágenes y reglas, aunque algunas de esas reglas y opciones aún son experimentales.”

## 4. Cómo se usa el sistema: recorrido general

**Mostrar:** barra lateral desde arriba hacia abajo.

**Decir:**

> “El flujo de uso es: seleccionamos una imagen o fuente de imágenes; configuramos el preprocesamiento y la escala de detección; observamos la imagen original y las vistas intermedias; y finalmente revisamos contornos, áreas, conteos y criterios. La imagen original se conserva para poder compararla con las transformaciones.”

> “Para una comparación responsable, primero revisamos la salida inicial. Después modificamos una sola opción, repetimos sobre la misma imagen y registramos qué cambió. Si modificáramos sigma, polaridad, contraste y separación a la vez, no podríamos atribuir el cambio a una causa concreta.”

**Mostrar:** selección de fuente (“Subir archivo(s)” o “Dataset del proyecto”) y seleccionar la imagen de demostración.

**Preguntar:** “¿Es claro de dónde viene la imagen seleccionada y qué debería hacer para comenzar el análisis?”

## 5. Explicar la escala: Sigma y filtro DoG

**Mostrar:** controles “Sigma 1 (Detalle fino)” y “Sigma 2 (Estructura general)”; después la pestaña “Filtro DoG” y las imágenes G1/G2 si se desea.

**Decir:**

> “Sigma, escrito con la letra griega σ, indica la desviación estándar del desenfoque Gaussiano y se expresa en píxeles. No es un factor de riesgo ni el tamaño de una célula. Sigma controla cuánto se suaviza la imagen: a mayor valor, mayor escala de suavizado.”

> “El filtro Difference of Gaussians, o DoG, crea dos imágenes suavizadas. G1 usa Sigma 1, que representa la escala más fina; G2 usa Sigma 2, que representa una escala más amplia. Luego calcula G1 menos G2. Esa diferencia resalta cambios de intensidad que se comportan de manera distinta entre ambas escalas y reduce parte del fondo común.”

> “En esta implementación, la resta se conserva primero como `float32` para no perder valores negativos por una conversión temprana a 8 bits. Después se normaliza para mostrarla. La respuesta DoG ayuda a resaltar ciertas estructuras, pero no mide directamente el diámetro físico de un núcleo.”

> “Sigma 2 tiene que ser mayor que Sigma 1. Los valores iniciales de la aplicación son 7 y 8: son valores de partida, no una calibración clínica. En documentación aparece también una relación experimental orientativa de 1.6 a 2 veces entre sigmas, pero no es una regla que el programa fuerce; de hecho, 8 dividido entre 7 es aproximadamente 1.14.”

> “Si Sigma es demasiado pequeño, pueden conservarse detalles y ruido que no interesan; si es demasiado grande, pueden suavizarse detalles o juntarse respuestas cercanas. No hay un valor universal: se compara con imágenes y anotaciones apropiadas, cambiando un valor por vez.”

**Mostrar:** mover solo un control de sigma, volver a mirar la respuesta DoG y comparar con la salida anterior.

**Preguntar:** “¿Qué le parece que cambió? ¿El control y la diferencia entre G1, G2 y DoG se entienden?”

**No afirmar:** que cierto sigma detecta todos los núcleos, corresponde a un diámetro celular exacto o mejora la precisión sin medición.

## 6. Explicar cada opción de preprocesamiento

**Mostrar:** sección “2️⃣ Preprocesamiento” de la barra lateral y la pestaña “Preprocesamiento”.

### Polaridad de los núcleos

**Decir:**

> “El pipeline DoG y la umbralización están planteados para trabajar con respuestas claras. En `nucleos-claros` se conserva la imagen tal como está; en `nucleos-oscuros` se invierte la imagen en escala de grises para que los núcleos oscuros se comporten como regiones claras. La elección depende de cómo aparecen los núcleos respecto del fondo en esta imagen. Elegirla mal puede cambiar las detecciones.”

### Mejorar Contraste (CLAHE) y Modo CLAHE

**Decir:**

> “Mejorar Contraste activa o desactiva el paso de contraste. CLAHE significa ecualización adaptativa del histograma con límite de contraste: intenta mejorar diferencias locales y limita cuánto puede amplificar. Puede ayudar con iluminación desigual o contraste local bajo, aunque también puede resaltar ruido o artefactos.”

> “El selector ‘Modo CLAHE’ ofrece `clahe`, `auto`, `histogram` y `normalize`. `clahe` aplica CLAHE; `auto` elige una opción según el contraste medido; `histogram` hace una ecualización global y `normalize` remapea intensidades al rango 0–255. Aunque el nombre del selector dice CLAHE, `histogram` y `normalize` son métodos distintos.”

### Reducir Ruido

**Decir:**

> “Reducir Ruido activa un filtro bilateral antes de mejorar el contraste. Busca suavizar variaciones pequeñas conservando parte de los bordes. Bajo, medio y alto ajustan la intensidad; una reducción fuerte también puede borrar detalles que sí interesan. No garantiza que baje el número de falsos positivos.”

**Mostrar:** comparar una opción cada vez, si hay tiempo; restaurar los valores de inicio.

**Resumir orden de procesamiento:**

> “En el código, primero se convierte a gris, luego se aplica ruido opcional, contraste opcional, inversión si se eligió `nucleos-oscuros` y, al final, la máscara HSV opcional.”

**Preguntar:** “¿Qué indicios usaría para decidir si la imagen necesita contraste o reducción de ruido? ¿Qué efecto no deseado vigilaría?”

## 7. Segmentación avanzada: HSV (Color)

**Mostrar:** control “Segmentación HSV (Color)”; activar solo si es útil para el ejemplo y mostrar su máscara en la pestaña “HSV / Separación”.

**Decir:**

> “HSV es otra forma de representar el color: H es tono, S es saturación y V es valor o brillo. Este control usa el canal de saturación o el de valor para construir una máscara binaria. El umbral de 0 a 255 decide qué píxeles pasan; luego se aplican operaciones morfológicas sencillas para eliminar regiones pequeñas y conectar algunas cercanas. Esa máscara se aplica a la imagen en gris antes del DoG.”

> “La opción `saturation` puede resultar útil cuando hay diferencia de color; `value` trabaja con la intensidad. HSV no identifica tipos celulares ni entiende tinciones: podría seleccionar también fondo coloreado, precipitados o artefactos. La máscara sirve para inspeccionar qué píxeles se conservaron, no para certificar una detección.”

**Preguntar:** “¿La máscara deja claro por qué una región se incluiría? ¿Qué elementos podría seleccionar además de núcleos?”

## 8. Separación de regiones superpuestas

**Mostrar:** selector “Método de separación”; comparar en la misma imagen “Sin separación” y un método experimental cuando tenga sentido.

**Decir:**

> “Sin separación es el modo original: si dos núcleos están unidos en la máscara, el detector puede contarlos como una sola región. Watershed y máximos locales intentan dividir regiones conectadas, pero están desactivados por defecto y pueden modificar el conteo.”

> “Watershed de OpenCV utiliza marcadores para dividir regiones. En la implementación presente se calcula una transformada de distancia, pero los marcadores se construyen con componentes conectados; la transformada calculada no se usa para crear esos marcadores. Por ello, no debemos asumir que Watershed separará correctamente cada par de núcleos.”

> “Máximos locales busca picos en la respuesta DoG y estima una región alrededor de cada pico. Como método heurístico puede duplicar, perder o estimar mal detecciones. Si el conteo cambia, ese cambio no significa por sí solo que la salida sea mejor.”

**Preguntar:** “¿Qué diferencia nota frente a ‘Sin separación’? ¿Qué evidencia necesitaría para decidir cuál resultado es más fiel?”

## 9. Cómo pasa de la imagen al conteo

**Mostrar:** pestaña “Análisis Final”, luego “Criterios de Clasificación”.

**Decir:**

> “Una vez calculado el DoG, el sistema usa una umbralización automática de Otsu para crear una máscara en blanco y negro. Después OpenCV busca contornos externos. Para cada contorno calcula el área en píxeles cuadrados. Según el método elegido puede filtrar por límites de área, y en algunos casos por circularidad o relación de aspecto.”

> “Esto genera candidatos geométricos. Un contorno no es una célula confirmada, ni una anotación verdadera. El algoritmo no analiza todos los rasgos que revisaría un especialista: por ejemplo, no interpreta cromatina, contexto celular, relación núcleo/citoplasma o criterios Bethesda.”

### Regla de área actual

**Decir:**

> “La clasificación es una regla sencilla y explicable, pero provisional. La referencia de área normal está fijada en 300 píxeles cuadrados y el factor es 3; por eso el umbral es 900 píxeles cuadrados. Las áreas menores al mínimo permitido se descartan como ruido; las superiores al máximo se descartan como posible artefacto. Las regiones que quedan se etiquetan según estén debajo o desde el umbral.”

> “La zona frontera equivale a más o menos diez por ciento alrededor de 900: de 810 a 990 píxeles cuadrados. Es una marca para señalar proximidad al límite, no una tercera categoría diagnóstica ni una medida de confianza. Una región de 900 a 990 puede seguir recibiendo la etiqueta de sospechosa por la regla subyacente, a la vez que queda marcada como frontera.”

> “Los límites mínimo y máximo dependen de la polaridad. Además, en modo sin separación y con núcleos oscuros se aplican filtros de forma. Estos valores deben considerarse experimentales; no están calibrados clínicamente.”

**Mostrar:** una fila o ejemplo de área, etiqueta y motivo en criterios.

## 10. Qué significan las visualizaciones y las métricas de pantalla

**Mostrar:** resultado final y su leyenda; expander de calidad; historial si hay datos; opciones de descarga.

**Decir:**

> “En la vista final, verde significa que el contorno válido quedó por debajo del umbral según la regla actual; rojo significa que superó ese umbral de área. Los colores representan la salida del programa, no un diagnóstico.”

> “Dibujar Contornos Reales muestra los contornos que calculó el algoritmo. ‘Reales’ en el texto del control no significa que estén confirmados por un experto; al desactivarlo, la vista usa cajas delimitadoras.”

> “Hay una limitación funcional que quiero señalar: el control ‘Mostrar Áreas en Imagen’ aparece en la barra lateral, pero actualmente no está conectado al dibujo y no imprime el valor del área sobre la imagen. Las áreas sí pueden revisarse en criterios de clasificación. Lo registramos como mejora de la interfaz.”

> “Los indicadores de contraste, brillo y saturación describen la imagen y pueden ayudar a revisar su calidad; no son métricas de exactitud del detector. El historial y la exportación a CSV o JSON ayudan a guardar parámetros y resultados, pero no convierten una salida experimental en evidencia clínica.”

> “El porcentaje de riesgo es la proporción de regiones detectadas y válidas que la regla clasificó como sospechosas. No es probabilidad de cáncer, precisión ni sensibilidad.”

**Preguntar:** “¿Qué información le ayuda a entender el resultado y cuál podría inducir a error?”

## 11. Uso desde terminal y cómo probar el proyecto

**Mostrar:** si el contexto lo permite, una terminal con los comandos; de lo contrario, dejar esta sección como explicación verbal.

**Decir:**

> “Además de la interfaz existe una línea de comandos. Para analizar una imagen se proporciona su ruta; para procesar una carpeta se usa el modo lote. La terminal permite una prueba reproducible con los mismos parámetros.”

```bash
python main.py data/raw/imagen.jpg --no-gui --sigma1 7.0 --sigma2 8.0
python main.py data/raw --lote --no-gui --sigma1 7.0 --sigma2 8.0
```

> “El repositorio también incluye pruebas unitarias y un validador de consistencia del dataset. Son controles de software y de integridad de archivos; no reemplazan la evaluación científica del detector.”

```bash
python -m unittest discover -s tests -v
python validar_consistencia_dataset.py
```

> “Para medir rendimiento hay que usar un conjunto autorizado, separado del usado para ajustar parámetros, anotaciones espaciales de referencia y un protocolo reproducible. Se registran versión, imágenes, parámetros, fecha y criterios de emparejamiento. Cambiamos una variable por experimento.”

## 12. Rendimiento disponible y qué tan válido es

**Mostrar:** opcionalmente una tabla preparada con el resumen guardado. No presentar como métrica en vivo de la imagen que se acaba de mostrar.

**Decir:**

> “Si me preguntan por un porcentaje de detección, la respuesta honesta es que no hay un porcentaje universal que describa cualquier imagen. El resumen experimental de CITO-23 evaluó nueve imágenes y emparejó centroides a una distancia de diez píxeles. Reportó 15 verdaderos positivos, 24 falsos positivos y 27 falsos negativos.”

> “A partir de esos totales, la precisión fue 38.46 por ciento, la sensibilidad o recall 35.71 por ciento, y el F1 37.04 por ciento. El Jaccard de detección informado fue 22.73 por ciento. Son resultados exploratorios y limitados, no una garantía de rendimiento para otros casos ni validación clínica.”

> “La precisión indica qué fracción de las detecciones tuvo correspondencia; la sensibilidad, qué fracción de las anotaciones fue detectada; y F1 combina ambas. Falsos positivos son detecciones sin coincidencia; falsos negativos, anotaciones que no se detectaron.”

> “El Jaccard reportado es para emparejamiento de detecciones, no mide la calidad geométrica de los bordes segmentados. Además, si el archivo de etiquetas esperado falta o no corresponde con las imágenes, una salida de ceros no significa que el sistema haya obtenido cero rendimiento medido: significa que no había referencias válidas para comparar.”

> “La conclusión es que hoy el sistema sirve como prototipo de investigación y herramienta para explorar el procesamiento. Aún no es válido para uso diagnóstico. Hace falta ground truth experto, datos autorizados y una evaluación independiente, amplia y reproducible antes de hacer afirmaciones de rendimiento clínico.”

## 13. Preguntas frecuentes y respuestas listas

### “¿Cuál es la función principal del proyecto?”

> “Procesar imágenes de citología, resaltar regiones candidatas a núcleo, estimar sus áreas y mostrar conteos y etiquetas experimentales para estudiar el pipeline.”

### “¿Detecta células completas?”

> “No necesariamente. La unidad principal que detecta el pipeline es una región delimitada por contorno que parece un núcleo; no realiza una interpretación celular completa.”

### “¿Es inteligencia artificial?”

> “La función principal implementada aquí usa procesamiento clásico de imagen y reglas explícitas —DoG, umbralización, contornos y área—. No debe confundirse con un sistema entrenado y validado para diagnosticar.”

### “¿Qué son Sigma 1 y Sigma 2?”

> “Son escalas del desenfoque Gaussiano en píxeles. El DoG resta dos imágenes suavizadas para resaltar cambios que difieren entre esas escalas. No representan el tamaño exacto de un núcleo.”

### “¿Qué significa ‘sospechosa’?”

> “Solo que el área de esa región superó el umbral experimental programado. No significa que un profesional la haya diagnosticado ni que sea una lesión.”

### “¿Qué significa el porcentaje de riesgo?”

> “La fracción de regiones válidas etiquetadas por la regla de área. No es una probabilidad de enfermedad.”

### “¿El resultado actual tiene 90% de precisión?”

> “No. La meta mencionada en documentación no es un resultado alcanzado. El resumen exploratorio de nueve imágenes reportó F1 de 37.04%, precisión de 38.46% y sensibilidad de 35.71%; estos datos son limitados y no son validación clínica.”

### “¿CLAHE, HSV o Watershed siempre mejoran el conteo?”

> “No. Son opciones experimentales que pueden ayudar o perjudicar según la imagen. Para afirmar una mejora se necesita comparar con anotaciones espaciales apropiadas.”

### “¿Por qué los contornos no coinciden con lo que veo?”

> “La umbralización puede unir núcleos, fragmentar regiones o incluir artefactos. El resultado depende del contraste, polaridad, escala, tinción y parámetros; el contorno debe revisarse contra una referencia experta.”

### “¿Cómo se valida de forma adecuada?”

> “Con imágenes autorizadas, ground truth espacial experto, un conjunto independiente y congelado, emparejamiento definido de antemano, métricas como precisión, recall y F1, y registro de versión y parámetros. La evaluación debe poder repetirse.”

### “¿Se puede usar para apoyar o sustituir el diagnóstico?”

> “No debe utilizarse para diagnóstico ni para decisiones clínicas. Es un prototipo de investigación que requiere supervisión profesional.”

## 14. Conversación con participantes y cuestionario

**Decir:**

> “Ahora me gustaría escuchar cómo interpretó el sistema. No hay respuestas correctas o incorrectas sobre la interfaz: queremos detectar qué resulta claro, confuso o incompleto.”

**Preguntar:**

1. “¿Qué parte del proyecto entiende que hace el sistema?”
2. “¿Qué control o pantalla fue más difícil de interpretar?”
3. “¿Qué diferencia observó entre original, preprocesamiento y DoG?”
4. “¿Qué información le gustaría ver junto a cada detección?”
5. “¿Qué limitación considera más importante explicar a otra persona?”
6. “¿Qué mejora priorizaría para una siguiente versión?”

Completa `CUESTIONARIO_CITOLOGOS.md`. Registra por separado comentarios de usabilidad, comportamiento observado y cualquier discrepancia con anotaciones expertas. No solicites datos sensibles ni conviertas la conversación en una consulta diagnóstica.

## 15. Cierre de la presentación

**Mostrar:** vuelve al análisis final o al aviso experimental del encabezado.

**Decir:**

> “Para resumir: CitoCounter Proto es un prototipo de investigación que usa Python, OpenCV y un pipeline DoG para explorar la detección de regiones candidatas a núcleo. La aplicación permite inspeccionar cómo polaridad, contraste, ruido, HSV y separación afectan la salida. La clasificación actual depende de reglas temporales de área y los resultados disponibles aún son exploratorios.”

> “El valor de esta sesión es comprender el sistema, identificar mejoras y documentar límites. Ninguna etiqueta o porcentaje de esta interfaz constituye un diagnóstico. Gracias por ayudarnos a mejorar el prototipo.”

## 16. Lista de pantallas para la demo

1. Encabezado y aviso experimental.
2. Selección de fuente e imagen autorizada.
3. Sigma 1, Sigma 2, DoG y G1/G2.
4. Polaridad, contraste, modo y reducción de ruido.
5. HSV, máscara y umbral.
6. Separación sin método, Watershed o máximos locales.
7. Análisis final y criterios de área.
8. Indicadores de calidad, historial y exportaciones.
9. Resumen exploratorio CITO-23, si se necesita responder sobre rendimiento.
10. Cuestionario y cierre con el límite de uso experimental.

## Referencias del repositorio

- [Guía de estudio del proyecto](GUIA_ESTUDIO_PROYECTO.md)
- [README e inicio rápido](README.md)
- [Guía de dataset](docs/guide/dataset.md)
- [Guía de experimentos y métricas](docs/guide/experimentos.md)
- [Algoritmos y métricas](docs/algoritmos_metricas.md)
- [Plan del proyecto](docs/plan-proyecto.md)
- [Seguimiento Jira](docs/guia-maestra-desarrollo.md)

---

**Versión:** 3.0 · **Fecha:** 2026-10-08
