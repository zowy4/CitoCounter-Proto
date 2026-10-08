# Guion de presentación y demostración — CitoCounter Proto

Este guion está pensado para presentar el prototipo y observar la usabilidad de su interfaz. No es una demostración de eficacia clínica. El facilitador puede leer en voz alta los textos entre comillas y seguir el orden de pantalla indicado.

## Preparación antes de la sesión

1. Ejecuta `streamlit run app.py` y abre la dirección local que muestra Streamlit.
2. Prepara una imagen de demostración autorizada y anonimizada, disponible desde el dataset local o para cargar. No uses datos identificables ni presupongas que una imagen se elimina automáticamente después de la sesión.
3. Comprueba que la imagen abre y que el resultado se puede mostrar. Conserva primero los parámetros iniciales para tener una línea base.
4. Ten a mano `CUESTIONARIO_CITOLOGOS.md` y registra observaciones con un código de sesión, no con datos personales.
5. No cambies varios parámetros a la vez ni presentes los resultados como diagnóstico.

## 1. Bienvenida y alcance

**Mostrar:** encabezado del dashboard y aviso visible de uso experimental.

**Decir:**

> “Gracias por participar. Hoy vamos a revisar la claridad y la usabilidad de un prototipo de investigación que procesa imágenes de citología cervical. No es un dispositivo médico ni una herramienta de diagnóstico. Sus etiquetas y conteos son resultados experimentales que necesitan revisión experta y no deben utilizarse para decisiones clínicas.”

> “La sesión se centra en cómo se entiende el sistema y qué debería mejorarse. No necesitamos nombres, identificadores ni información clínica de pacientes.”

**Preguntar:** “Antes de empezar, ¿qué espera que haga una herramienta de este tipo?”

## 2. Elegir una imagen

**Mostrar:** la barra lateral, la selección entre subir archivo(s) y el dataset local; cargar/seleccionar la imagen de demostración.

**Decir:**

> “Primero elegimos una imagen de prueba autorizada. Mantendremos la misma imagen mientras exploramos los controles para poder comparar qué cambia.”

**Preguntar:** “¿Le resulta claro dónde elegir la imagen y cuál es la fuente seleccionada?”

## 3. Explicar Sigma y el filtro DoG

**Mostrar:** controles Sigma 1 y Sigma 2 en la barra lateral. Deje inicialmente los valores que aparecen por defecto. Luego muestre la pestaña “Filtro DoG” y, si está disponible, abra la vista de G1/G2.

**Decir:**

> “Sigma es la escala del desenfoque Gaussiano y se expresa en píxeles. Sigma 1 genera un suavizado más fino y Sigma 2 uno más amplio. El programa resta ambas imágenes suavizadas: esa respuesta se llama Difference of Gaussians, o DoG. Resalta cambios de intensidad entre escalas; no mide directamente el tamaño físico del núcleo.”

> “Sigma 2 debe ser mayor que Sigma 1. Los valores iniciales de la aplicación son un punto de partida experimental, no valores clínicamente calibrados. Si probamos un cambio, modificaremos un solo sigma y compararemos las imágenes.”

**Mostrar:** cambie un único valor, observe la respuesta DoG y vuelva al original para comparar. No afirme que una configuración es mejor sin ground truth.

**Preguntar:** “¿Qué cree que cambió en la imagen al mover este control? ¿La explicación del parámetro le resulta suficiente?”

## 4. Preprocesamiento

**Mostrar:** sección “Preprocesamiento” en la barra lateral y pestaña “Preprocesamiento”.

**Decir:**

> “Antes del DoG, la imagen pasa a escala de grises. La polaridad se elige según cómo se vean los núcleos: `nucleos-claros` conserva la intensidad, mientras que `nucleos-oscuros` invierte la imagen para que el DoG pueda procesar núcleos oscuros como regiones claras.”

> “Mejorar Contraste activa el método elegido en Modo CLAHE. `clahe` mejora contraste local; `auto` selecciona un método según el contraste; `histogram` ecualiza globalmente y `normalize` remapea intensidades. Aunque el control diga Modo CLAHE, histogram y normalize no son variantes de CLAHE.”

> “Reducir Ruido aplica un filtro bilateral. Los niveles más intensos pueden suavizar detalles finos. Estas opciones pueden ayudar en algunas imágenes y perjudicar otras, así que conviene compararlas, no asumir que siempre mejoran.”

**Mostrar:** si es apropiado, active y desactive una opción cada vez y compare la vista. Restaure el punto de partida después de la demostración.

**Preguntar:** “¿Qué información necesitaría para escoger estos controles con confianza?”

## 5. Segmentación HSV y separación

**Mostrar:** “Segmentación HSV (Color)”, su método y umbral; después la pestaña “HSV / Separación”.

**Decir:**

> “HSV permite crear una máscara usando saturación —diferencia de color— o value —intensidad— y aplicarla antes del DoG. El umbral controla qué píxeles pasan. La máscara puede resaltar núcleos, pero también tinción, fondo o artefactos.”

> “La separación está desactivada por defecto. ‘Sin separación’ conserva los contornos conectados detectados. Watershed y máximos locales son métodos experimentales que intentan dividir regiones y pueden cambiar el conteo; no garantizan separar núcleos correctamente.”

**Mostrar:** la máscara y una de las opciones de separación si hay una imagen adecuada. Compare el conteo con “Sin separación”.

**Preguntar:** “¿Qué diferencia ve entre las salidas? ¿Qué advertencia necesitaría antes de interpretar un cambio en el conteo?”

## 6. Análisis, regla de área y clases

**Mostrar:** pestaña “Análisis Final”, conteos, y después “Criterios de Clasificación”.

**Decir:**

> “El programa umbraliza la respuesta DoG, extrae contornos externos y calcula el área de cada región en píxeles cuadrados. Las reglas actuales son provisionales: área de referencia 300 px², factor 3 y umbral de 900 px². Las regiones muy pequeñas o grandes pueden descartarse; las restantes se marcan normal o sospechosa según esa área.”

> “La zona frontera es ±10% alrededor de 900 px², es decir, de 810 a 990 px². Sirve para señalar casos cercanos al límite para revisión, no para indicar certeza. ‘Sospechosa’ solo describe el resultado de esta regla; no equivale a una categoría citológica ni a malignidad.”

**Mostrar:** el área, la etiqueta y el motivo que presenta la interfaz. No describa un contorno detectado como una anotación verdadera.

**Preguntar:** “¿Qué parte de esta regla se entiende bien? ¿Qué puede inducir a una interpretación incorrecta?”

## 7. Contornos y áreas dibujadas

**Mostrar:** “Dibujar Contornos Reales” y “Mostrar Áreas en Imagen”; observe las salidas.

**Decir:**

> “Los contornos son los que calculó el programa; ‘reales’ no significa confirmados por anotación experta. La opción de contornos puede mostrar los bordes detectados o una caja delimitadora.”

> “Hay una limitación conocida en esta versión: el interruptor ‘Mostrar Áreas en Imagen’ no está conectado al dibujo y no añade números sobre la imagen. Las áreas se pueden revisar en los criterios de clasificación. Lo anoto como una mejora de interfaz.”

No pida al participante que diagnostique una imagen. Registre si el control y su efecto esperado resultan claros.

## 8. Calidad, historial y exportación

**Mostrar:** advertencias/métricas de calidad, historial si hay registros y controles de descarga.

**Decir:**

> “Los indicadores de contraste, brillo y saturación describen propiedades de la imagen; no validan que las detecciones sean correctas. El historial y la exportación sirven para documentar resultados y parámetros, pero guardar una salida no la convierte en evidencia clínica.”

> “El porcentaje de riesgo es la proporción de detecciones válidas que superó el umbral de área. No es la probabilidad de enfermedad ni la precisión del detector.”

**Preguntar:** “¿Qué información querría conservar para reproducir una comparación de parámetros? ¿La exportación deja claro qué se midió?”

## 9. Si preguntan por el rendimiento

**Decir:**

> “No hay una tasa única de detección que se pueda prometer. El resumen exploratorio de CITO-23 evaluó nueve imágenes mediante emparejamiento espacial de centroides a 10 píxeles: TP=15, FP=24 y FN=27; precisión 38.46%, sensibilidad 35.71% y F1 37.04%. Es un resultado limitado y exploratorio, no una validación clínica ni una garantía para otras imágenes.”

> “Para validar el rendimiento se necesita ground truth espacial experto, imágenes autorizadas, un conjunto independiente y congelado, y un protocolo reproducible. El Jaccard de ese resumen corresponde a detección, no a la calidad de los límites de segmentación.”

**Si preguntan qué significa cada métrica:**

- **Precisión:** entre las regiones que detectó, cuántas coincidieron con una anotación.
- **Sensibilidad/recall:** entre las regiones anotadas, cuántas encontró el sistema.
- **F1:** combinación de precisión y sensibilidad.
- **TP / FP / FN:** detecciones correctas / detecciones sin coincidencia / anotaciones no detectadas.

## 10. Conversación final y cierre

**Preguntar:**

1. “¿Qué control o vista fue más difícil de entender?”
2. “¿Qué le resultó más útil para inspeccionar el procesamiento?”
3. “¿Qué limitación comunicaría a otra persona antes de mostrarle el resultado?”
4. “¿Qué mejora priorizaría para una siguiente versión?”

Completa `CUESTIONARIO_CITOLOGOS.md`, registrando la sesión con el código acordado. Distingue comentarios sobre usabilidad de métricas técnicas y de cualquier valoración clínica.

**Decir al cerrar:**

> “Gracias por ayudarnos a mejorar la claridad del prototipo. La salida de hoy sigue siendo experimental y requiere revisión profesional; no debe usarse para diagnóstico. Registraremos sus comentarios como mejoras de investigación y usabilidad.”

## Lista breve de lo que debe quedar visible en pantalla

1. Aviso experimental y barra lateral.
2. Imagen de prueba y fuente seleccionada.
3. Sigmas, DoG y componentes G1/G2 si se muestran.
4. Polaridad, contraste y ruido.
5. Máscara HSV y métodos de separación, si se prueban.
6. Análisis final y criterios/áreas por región.
7. Métricas de calidad, historial y descargas.

## Notas para el facilitador

- No llames “exactitud” al total de detecciones ni al porcentaje de riesgo.
- No ocultes que los valores del área son provisionales o que CITO-23 es exploratorio.
- No afirmes que HSV, CLAHE, watershed o máximos locales aumentan el rendimiento sin una evaluación comparativa apropiada.
- La opción “Mostrar Áreas en Imagen” no dibuja áreas en esta versión; anótala como limitación funcional, no como error del participante.
- Para criterios de protección de datos, autorizaciones y registro de experimentos, consulta la documentación del proyecto y las políticas institucionales aplicables.

---

**Versión:** 2.0 · **Fecha:** 2026-10-08
