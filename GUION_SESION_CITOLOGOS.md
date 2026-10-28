# Guion de sesión para facilitador - CitoCounter Proto

## 1. Objetivo de la sesión

La sesión tiene dos metas:

1. explicar de forma clara qué hace el sistema y qué no hace;
2. mostrar una demo guiada del flujo, con énfasis en la lógica de detección, clasificación y limitaciones.

La clave es no presentar el sistema como diagnóstico clínico. Debe quedar claro que es un prototipo experimental para investigación y apoyo visual.

---

## 2. Duración sugerida

| Fase | Duración |
|---|---:|
| Bienvenida y aviso de uso experimental | 5 min |
| Cuestionario breve | 5 min |
| Demo guiada | 15 min |
| Exploración libre | 15 min |
| Validación de una o dos imágenes | 15 min |
| Revisión de métricas y exportación | 10 min |
| Feedback cualitativo | 10 min |
| Cierre | 5 min |

Total estimado: 80-90 minutos.

---

## 3. Guion completo: qué decir y qué mostrar

### 3.1 Bienvenida y aviso experimental

**Lo que digo:**

> “Gracias por acompañarnos. Esta sesión tiene como objetivo revisar un prototipo experimental de apoyo en citología cervical. Lo importante es entender que no es un dispositivo médico ni una herramienta de diagnóstico. Es una herramienta de investigación para estudiar detección automática de núcleos, y su salida requiere revisión profesional.”

**Lo que muestro en pantalla:**

- pantalla principal de `streamlit run app.py`
- aviso experimental visible arriba de todo
- detalle de la app con barra lateral y pestañas

**Objetivo:** dejar claro el marco legal y de uso antes de mostrar resultados.

---

### 3.2 Explicación rápida del proyecto

**Lo que digo:**

> “El proyecto analiza imágenes de citología cervical. Primero procesa la imagen, luego aplica un filtro Difference of Gaussians para resaltar estructuras del tamaño de un núcleo, después detecta contornos y clasifica cada posible núcleo por área. La regla actual es simple y explicable: si el área supera el umbral de riesgo, se marca como sospechosa; si está por debajo, se marca como normal.”

**Lo que muestro en pantalla:**

- pestaña “Original”
- pestaña “Preprocesamiento”
- pestaña “Filtro DoG”
- explicación de la relación entre imagen original y imagen tratada

**Objetivo:** que el citólogo comprenda que el sistema no “adivina”, sino que sigue un flujo técnico transparente.

---

### 3.3 Mostrar cómo se configura la imagen

**Lo que digo:**

> “La parte de configuración permite elegir la fuente de la imagen, la polaridad de los núcleos, la mejora de contraste y la reducción de ruido. Esto importa porque no todas las preparaciones se ven igual: algunas muestran núcleos claros sobre fondo oscuro y otras muestran núcleos oscuros sobre fondo claro.”

**Lo que muestro en pantalla:**

- sidebar “Fuente de Imágenes”
- `Polaridad: nucleos-claros / nucleos-oscuros`
- `CLAHE` y `Reducir Ruido`
- slider de `Sigma 1` y `Sigma 2`

**Objetivo:** explicar que la preparación y la configuración afectan la detección.

---

### 3.4 Mostrar DoG y la lógica de detección

**Lo que digo:**

> “El filtro DoG utiliza dos versiones suavizadas de la imagen: una más fina y otra más gruesa. La resta resalta estructuras con un tamaño parecido al núcleo. En otras palabras, no se está buscando todo lo que sea oscuro o brillante; se busca lo que encaja en la escala del núcleo.”

**Lo que muestro en pantalla:**

- pestaña `Filtro DoG`
- imagen original comparada con imagen DoG
- G1/G2 si está disponible en el dashboard

**Objetivo:** hacer tangible el concepto de escala y detección.

---

### 3.5 Mostrar clasificación por área

**Lo que digo:**

> “La clasificación actual se basa en área. El proyecto usa un umbral temporal. En la versión actual, el área promedio normal se toma como 300 px² y el factor de riesgo es 3x. Eso implica un umbral de riesgo de aproximadamente 900 px². Si la célula supera esa zona, se marca como sospechosa; si está por debajo, como normal; si está muy cercana al umbral, se considera zona frontera.”

**Lo que muestro en pantalla:**

- pestaña “Criterios de Clasificación”
- tabla por célula con área, clase y motivo
- verde = normal, rojo = sospechosa

**Objetivo:** que se entienda que el sistema usa reglas explicables, no una caja negra completa.

---

### 3.6 Mostrar resultado final sobre una imagen

**Lo que digo:**

> “Aquí vemos el resultado final. Las células normales aparecen en verde y las sospechosas en rojo. También se calcula un porcentaje de riesgo y se muestran métricas del análisis.”

**Lo que muestro en pantalla:**

- `Análisis Final`
- imagen con contornos y etiquetas
- métricas principales: total, normales, sospechosas, % riesgo

**Objetivo:** mostrar la lectura del resultado sin convertirlo en diagnóstico.

---

### 3.7 Mostrar la parte de calidad y advertencias

**Lo que digo:**

> “Además del conteo, el sistema evalúa calidad de imagen. Esto puede ayudar a determinar si la preparación tiene variaciones de brillo, contraste o saturación. Si la imagen está muy degradada, la detección puede ser menos fiable.”

**Lo que muestro en pantalla:**

- expanders de “Advertencias de calidad”
- “Métricas de calidad”
- contrastes, brillo y saturación

**Objetivo:** separar calidad de imagen de la clasificación del núcleo.

---

### 3.8 Mostrar historial y métricas del proyecto

**Lo que digo:**

> “El proyecto también guarda un historial de ejecuciones y consolida indicadores. Esto ayuda a comparar resultados entre imágenes y entre configuraciones, aunque se trata de un prototipo experimental.”

**Lo que muestro en pantalla:**

- historial de ejecuciones
- métricas de conjunto
- indicadores de riesgo promedio

**Objetivo:** explicar la utilidad del seguimiento y la reproducibilidad.

---

### 3.9 Mostrar exportación

**Lo que digo:**

> “Finalmente, el sistema puede exportar resultados como PNG, CSV o JSON. Esto permite mantener evidencia y facilitar revisión posterior o integración con otros sistemas.”

**Lo que muestro en pantalla:**

- botón de descarga
- ejemplo de CSV/JSON

**Objetivo:** que se vea la utilidad real para documentación y trazabilidad.

---

### 3.10 Cerrar con la limitación clínica

**Lo que digo:**

> “El valor del sistema no está en sustituir la decisión clínica, sino en apoyar la revisión, la trazabilidad y la comparación técnica. La validación real requiere ground truth experto y datasets adecuados. Por ahora, la herramienta debe usarse como apoyo experimental.”

**Lo que muestro en pantalla:**

- aviso experimental
- última vista del dashboard

**Objetivo:** dejar una conclusión honesta y clara.

---

## 4. Preguntas clave para hacer durante la demo

- “¿Le parece claro el objetivo del sistema?”
- “¿Entiende la diferencia entre normal, sospechoso y zona frontera?”
- “¿Qué le parece la regla de 3x?”
- “¿Qué le falta para confiar más en la herramienta?”
- “¿Qué criterio clínico le gustaría que apareciera en la interfaz?”
- “¿Qué debería cambiar para que la herramienta le resulte más útil?”

---

## 5. Observaciones del facilitador

Durante la sesión, anotar:

- dónde titubea el participante,
- qué parámetros le resultan más difíciles,
- qué parte entiende mejor,
- qué dice literalmente sobre la confianza o la utilidad del sistema,
- si percibe la herramienta como apoyo o como riesgo.

---

## 6. Cierre recomendado

**Lo que digo:**

> “Resumen: el sistema ayuda a detectar y contar núcleos, pero aún no tiene la validación clínica necesaria para sustituir la revisión profesional. Lo más valioso de esta prueba es escuchar qué parte del flujo necesita cambiar para que sea realmente útil para la práctica.”

---

## 7. Plantilla breve de notes de sesión

| Tema | Observación |
|---|---|
| Entendimiento general | __________________ |
| Claridad de la regla de riesgo | __________________ |
| Confusión en interfaz | __________________ |
| Comentarios sobre calidad de imagen | __________________ |
| Comentarios sobre métricas | __________________ |
| Sugerencia principal | __________________ |
| Recomendación final | __________________ |


NPS: [0-10] → [Promotor/Pasivo/Detractor]

ACUERDO CLÍNICO GLOBAL: [XX]% (X/Y casos coincidentes)

TOP 3 FORTALEZAS:
1. 
2. 
3. 

TOP 3 DEBILIDADES CRÍTICAS:
1. [Severidad: Crítica/Alta] 
2. [Severidad: Crítica/Alta]
3. [Severidad: Media]

HALLAZGOS CLÍNICOS CLAVE:
- Regla 3x: [Apropiada / Ajustar a ___x / No válida]
- Zona frontera ±10%: [Apropiada / Ajustar a ±___%]
- Casos superpuestos: [Sistema falla / Watershed ayuda / Necesita más trabajo]
- Artefactos: [Maneja bien / Falsos positivos en ___]
- Bajo contraste: [HSV ayuda / No ayuda / No probado]

PARÁMETROS SUGERIDOS POR CITÓLOGO:
- σ1 óptimo: ____
- σ2 óptimo: ____
- Polaridad preferida: ____
- CLAHE: [Sí/No/Auto]
- Watershed: [Sí/No/Mejorar]
- HSV: [Sí/No/Mejorar]

ACCIONES COMPROMETIDAS:
1. [Acción] → [Responsable] → [Fecha] → [Prioridad]
2. [Acción] → [Responsable] → [Fecha] → [Prioridad]
3. [Acción] → [Responsable] → [Fecha] → [Prioridad]

¿VOLVERÍA A PARTICIPAR? ☐ Sí ☐ No ☐ Con condiciones
```

---

## 📁 Entregables Post-Sesión

1. **Cuestionario completado** (PDF/escaneo) → `docs/sesiones/citologo_[iniciales]_[fecha]_cuestionario.pdf`
2. **Resumen ejecutivo** (arriba) → `docs/sesiones/citologo_[iniciales]_[fecha]_resumen.md`
3. **Grabación** (si aplica) → almacenamiento seguro, borrar a 30 días
4. **Issues en Jira/GitHub** creados desde hallazgos → etiquetar `citologo-feedback`, `CITO-38/39/88`
5. **Actualización de guía maestra** con decisiones tomadas

---

## 🔗 Trazabilidad Jira

| Actividad | Clave Jira | Estado Esperado Post-Sesión |
|-----------|------------|----------------------------|
| Ejecutar pruebas de usabilidad con citotecnólogos | CITO-38 | **Hecha** (con evidencia) |
| Recopilar feedback de personal clínico y resolver cambios | CITO-39 | **En progreso** (acciones comprometidas) |
| Pruebas de la plataforma con usuarios potenciales | CITO-88 | **Hecha** (mínimo 5 citotecnólogos) |

---

**Versión:** 1.1  
**Fecha:** 2026-10-08  
**Facilitador asignado:** ___________________________________