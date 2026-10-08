# Cuestionario de evaluación de usabilidad — CitoCounter Proto

## Antes de empezar

Este cuestionario recoge comentarios sobre la interfaz y un prototipo experimental de análisis de imágenes. No es una evaluación diagnóstica ni una solicitud de validar resultados clínicos. La sesión no debe incluir nombres, identificadores, datos sensibles ni imágenes de pacientes sin autorización y anonimización aprobada. Usa un código de sesión, no el nombre del participante.

El sistema no es un dispositivo médico ni sustituye el criterio profesional. Sus etiquetas “normal” y “sospechosa” describen exclusivamente una regla experimental de área; no constituyen un hallazgo clínico.

## 1. Datos generales de la sesión

| Campo | Respuesta |
|---|---|
| Código de sesión | ______________________________ |
| Fecha | ______________________________ |
| Rol profesional | ______________________________ |
| Años de experiencia | ☐ <2 ☐ 2–5 ☐ 6–10 ☐ >10 |
| Familiaridad con herramientas de imagen | ☐ Ninguna ☐ Básica ☐ Intermedia ☐ Avanzada |
| Facilitador (código) | ______________________________ |

## 2. Impresión inicial

Califique de **1 (muy en desacuerdo) a 5 (muy de acuerdo)**.

| Afirmación | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|
| Entiendo qué tarea realiza el prototipo | ☐ | ☐ | ☐ | ☐ | ☐ |
| El aviso de uso experimental es visible y comprensible | ☐ | ☐ | ☐ | ☐ | ☐ |
| Puedo identificar dónde cargar o elegir una imagen | ☐ | ☐ | ☐ | ☐ | ☐ |
| Puedo distinguir la imagen original de las vistas procesadas | ☐ | ☐ | ☐ | ☐ | ☐ |

¿Qué entendió que hace el sistema?
____________________________________________________________________

¿Qué esperaba encontrar y no encontró?
____________________________________________________________________

## 3. Prueba de tareas

Para cada tarea, anote si pudo completarla sin ayuda. No puntúe la concordancia clínica de las etiquetas.

| Tarea | Sin ayuda | Con ayuda | No completada | Comentario |
|---|---:|---:|---:|---|
| Elegir una imagen de prueba autorizada | ☐ | ☐ | ☐ | __________ |
| Encontrar los controles Sigma 1 y Sigma 2 | ☐ | ☐ | ☐ | __________ |
| Comparar original, preprocesamiento y DoG | ☐ | ☐ | ☐ | __________ |
| Cambiar polaridad o contraste y describir qué cambió | ☐ | ☐ | ☐ | __________ |
| Encontrar el conteo y los criterios por área | ☐ | ☐ | ☐ | __________ |
| Encontrar las opciones de exportación | ☐ | ☐ | ☐ | __________ |

¿En qué paso necesitó más ayuda y qué habría hecho más claro ese paso?
____________________________________________________________________

## 4. Comprensión de controles

Califique la **claridad** y la **utilidad para revisar el procesamiento** de cada opción: 1 (muy baja) a 5 (muy alta). “No lo probé” es una respuesta válida.

| Control | Claridad 1–5 / No probado | Utilidad 1–5 / No probado | Comentarios |
|---|---|---|---|
| Sigma 1 y Sigma 2 | __________ | __________ | __________________ |
| Polaridad: `nucleos-claros` / `nucleos-oscuros` | __________ | __________ | __________________ |
| Mejorar Contraste (CLAHE) | __________ | __________ | __________________ |
| Modo: `clahe`, `auto`, `histogram`, `normalize` | __________ | __________ | __________________ |
| Reducir Ruido y nivel | __________ | __________ | __________________ |
| Segmentación HSV (saturation/value y umbral) | __________ | __________ | __________________ |
| Separación: sin separación / watershed / máximos locales | __________ | __________ | __________________ |
| Dibujar Contornos Reales | __________ | __________ | __________________ |
| Mostrar Áreas en Imagen | __________ | __________ | __________________ |

### Preguntas abiertas sobre los controles

1. Con sus propias palabras, ¿qué cree que cambia al modificar Sigma 1 o Sigma 2?
   ____________________________________________________________________
2. ¿Qué señales usaría para elegir entre polaridad de núcleos claros u oscuros?
   ____________________________________________________________________
3. ¿En qué tipo de imagen probaría contraste, reducción de ruido o segmentación HSV? ¿Qué efecto adverso vigilaría?
   ____________________________________________________________________
4. ¿Qué método de separación le resultó más fácil de interpretar? ¿Qué cambio observó en el conteo?
   ____________________________________________________________________
5. ¿Qué información visual le ayudaría a revisar cada detección?
   ____________________________________________________________________

> **Nota del facilitador sobre “Mostrar Áreas en Imagen”:** en la versión evaluada, el control está visible, pero no está conectado al dibujo de la imagen. No dibuja etiquetas de área al activarlo. Explique este hecho si la persona intenta probarlo; registre si desea esa función, pero no atribuya el comportamiento a un error del participante.

## 5. Interpretación de resultados

El prototipo usa una regla de área provisional: referencia 300 px² × factor 3 = umbral 900 px²; la zona frontera es 810–990 px². Una región que supera el umbral se etiqueta “sospechosa” **por esa regla**, no por diagnóstico. Contornos y máscaras son predicciones del programa, no ground truth.

| Pregunta | Respuesta |
|---|---|
| ¿Puede explicar qué significa “sospechosa” en esta interfaz? | ☐ Sí ☐ Parcialmente ☐ No |
| ¿Puede distinguir etiqueta por área de un diagnóstico? | ☐ Sí ☐ Parcialmente ☐ No |
| ¿Le queda claro qué significa “zona frontera”? | ☐ Sí ☐ Parcialmente ☐ No |
| ¿Qué visualización o explicación le falta para interpretar el umbral? | ______________________________ |
| ¿Qué riesgo de malinterpretación ve en las etiquetas o los colores? | ______________________________ |

¿Qué pregunta le surge sobre la regla de área o sus límites?
____________________________________________________________________

## 6. Métricas, calidad y exportación

| Elemento | Lo entiendo | Me resulta útil | Comentario |
|---|---:|---:|---|
| Total de regiones detectadas | ☐ Sí ☐ Parcial ☐ No | ☐ Sí ☐ Parcial ☐ No | __________ |
| Porcentaje de regiones “sospechosas” | ☐ Sí ☐ Parcial ☐ No | ☐ Sí ☐ Parcial ☐ No | __________ |
| Indicadores de calidad de imagen | ☐ Sí ☐ Parcial ☐ No | ☐ Sí ☐ Parcial ☐ No | __________ |
| Historial / parámetros usados | ☐ Sí ☐ Parcial ☐ No | ☐ Sí ☐ Parcial ☐ No | __________ |
| Exportación CSV / JSON / imagen | ☐ Sí ☐ Parcial ☐ No | ☐ Sí ☐ Parcial ☐ No | __________ |

¿Qué datos necesitaría que acompañaran una exportación para poder reproducir una prueba?
____________________________________________________________________

¿Qué entiende por el “% de riesgo” que muestra el prototipo?
____________________________________________________________________

> Recuerde que dicho porcentaje es la fracción de detecciones válidas etiquetadas por la regla de área; no es probabilidad de enfermedad, precisión ni sensibilidad.

## 7. Utilidad, confianza y limitaciones

1. Para tareas de investigación o comparación técnica, ¿qué utilidad tendría para usted?
   ☐ Alta ☐ Moderada ☐ Baja ☐ Ninguna ☐ No sé
2. ¿Qué limitación le parece más importante comunicar a otra persona que use el prototipo?
   ____________________________________________________________________
3. ¿Qué tipos de imagen o artefacto cree que deberían probarse antes de sacar conclusiones?
   ____________________________________________________________________
4. ¿Qué tendría que cambiar para que la interfaz fuera más comprensible?
   ____________________________________________________________________
5. ¿Hay algo en la pantalla que pueda inducir a pensar que la herramienta diagnostica?
   ____________________________________________________________________

## 8. Priorización de mejoras

Ordene hasta cinco opciones (1 = prioridad más alta); deje en blanco las que no elija.

| Mejora | Prioridad |
|---|---:|
| Explicar Sigma y la respuesta DoG en la interfaz | ____ |
| Mejorar la selección de polaridad / contraste / ruido | ____ |
| Mejorar HSV y mostrar con claridad su máscara | ____ |
| Mejorar separación de regiones superpuestas | ____ |
| Dibujar áreas numéricas junto a las detecciones | ____ |
| Mostrar origen y limitaciones de las etiquetas de área | ____ |
| Facilitar revisión de falsos positivos y falsos negativos | ____ |
| Mejorar exportación y trazabilidad de parámetros | ____ |
| Otra: ______________________________________________ | ____ |

## 9. Comentario final

**Lo más claro o útil:**
____________________________________________________________________

**Lo más confuso o prioritario de corregir:**
____________________________________________________________________

**¿Participaría en otra prueba de usabilidad del prototipo?**
☐ Sí ☐ No ☐ Tal vez

## 10. Notas del facilitador

- No solicitar ni registrar identificadores de pacientes o datos sensibles.
- Separar observaciones de usabilidad de cualquier juicio clínico.
- Si se compara detección con anotaciones, verificar antes que las imágenes y el ground truth estén emparejados y autorizados; documentar el protocolo por separado.
- Registrar incidencias reproducibles y parámetros, sin cambiar varios controles a la vez.

| Observación / incidencia | Pantalla o control | Pasos para reproducir | Prioridad |
|---|---|---|---|
| __________________________ | __________________ | ______________________________ | ☐ Alta ☐ Media ☐ Baja |
| __________________________ | __________________ | ______________________________ | ☐ Alta ☐ Media ☐ Baja |

---

**Versión:** 2.0 · **Fecha:** 2026-10-08 · **Proyecto:** CitoCounter Proto
