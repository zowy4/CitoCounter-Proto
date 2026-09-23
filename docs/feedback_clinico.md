# CitoCounter-Proto: Recopilación de Feedback Clínico y Resolución de Cambios

## ACT-18 (CITO-39)

### Fecha: 2026-09-22
### Estado: PLANEADO (pending execution - depends on CITO-38 usability test results)

### Objetivo
Recopilar feedback estructurado de citotecnólogos y personal clínico después de ejecutar las pruebas de usabilidad (CITO-38), identificar problemas prioritarios y realizar mejoras iterativas al pipeline, documentación e interfaz de CitoCounter-Proto.

### Dependencias
- [x] **CITO-38 (ACT-17)**: Plan de pruebas de usabilidad creado ✅
- [ ] **Ejecutar pruebas de usabilidad**: Mínimo 2 citotecnólogos participan
- [ ] **Formularios de evaluación completados**: Feedback recopilado de usuarios reales
- [ ] **Reporte de hallazgos de usabilidad**: Problemas identificados y priorizados

### Personas para Recibir Feedback
- **Operadores de laboratorio / Citotecnólogos**: Usuarios principales del pipeline
- **Revisores clínicos**: Validan la clasificación y resultados
- **Investigadores**: Interesados en parámetros, métricas y calibración
- **Administradores técnicos**: Mantienen el entorno y resuelven problemas técnicos

### Métodos de Recopilación de Feedback

#### 1. Formularios Estructurados (Post-Test)
Después de cada sesión de usabilidad (CITO-38), completar:

| Sección | Preguntas Clave | Formato |
|---------|----------------|---------|
| **General** | "¿Recomendaría esta herramienta a colegas?" | Likert scale 1-5 |
| **Carga de imágenes** | "¿Fue intuitivo el proceso de selección de imagen?" | Escala + comentarios |
| **Clasificación** | "¿Sintió que la clasificación normal/sospechosa fue justificada?" | Escala + justificación |
| **Parámetros** | "¿Entendió el significado de los sigmas DoG (7.0, 8.0)?" | Sí/No + explicación |
| **Separación de núcleos** | "¿El método de separación (watershed/máximos_locales) fue útil?" | Escala + comentarios |
| **Exportación** | "¿Fácil exportar resultados a CSV/bitácora?" | Sí/No + problemas |
| **Global** | "¿Qué cambiaría de la interfaz o flujo de trabajo?" | Texto libre |

#### 2. Entrevistas Semi-estructuradas (30 min por participante)
- "¿Qué parte del proceso le resultó más difícil?"
- "¿Siente que los resultados son reproducibles si otro operador usa el mismo parámetros?"
- "¿Hay algún paso que considere innecesario o redundante?"
- "¿Sugeriría alguna característica nueva o mejora al pipeline?"

#### 3. Registro de Problemas Técnicos
Durante las pruebas, registrar:
- Errores del sistema (tracebacks, fallos de importación)
- Comportamientos inesperados
- Rendimiento (tiempo de procesamiento, uso de memoria)
- Problemas de usabilidad no capturados en formularios

### Criterios de Aceptación para CITO-39

Las actividades de recopilación de feedback se considerarán exitosas si:

1. **Mínimo 2 citotecnólogos** completan las pruebas de usabilidad (CITO-38)
2. **Al menos 80% de los formularios** están completos y no están vacíos
3. **Problemas críticos identificados** (bloqueantes para el flujo básico) sean 0 o se tengan plan de mitigación
4. **Feedback sobre claridad** experimental vs diagnóstico confirmado por al menos el 75% de participantes
5. **Lista de mejoras propuestas** con prioridad (alta, media, baja) creada y revisada
6. **Decision sobre continuidad** documentada: ¿Proseguir con mejoras inmediatas o esperar nueva iteración de pruebas?

### Entregables

- [ ] **Formularios de feedback completados** por cada participante (físicos o digitales)
- [ ] **Reporte consolidado de hallazgos** con problemas identificados y propuestas de solución
- [ ] **Lista de mejoras prioritarias** ordenadas por impacto y esfuerzo
- [ ] **Actualización de documentación** basada en el feedback (guía de usuario, parámetros, wireflows)
- [ ] **Mejoras al pipeline** (código) si los feedback identifican bugs o mejoras significativas
- [ ] **Decision documentada** sobre qué cambios implementar en la próxima iteración
- [ ] **Actualización del estado en Jira** de `ACT-18 (CITO-39)` a `En revisión` o `Hecha`

### Plan de Ejecución

#### Paso 1: Preparación (1 semana)
1. Notificar a citotecnólogos y personal clínico sobre las pruebas de usabilidad
2. Preparar conjunto de imágenes de prueba (mínimo 5-10 imágenes representativas)
3. Configurar estaciones de trabajo (Streamlit `streamlit run app.py`, CLI disponible)
4. Imprimir/formularios de evaluación o preparar versiones digitales
5. Revisar que todos los 66 tests unitarios pasan (`python -m unittest discover -s tests -v`)

#### Paso 2: Ejecución de Pruebas (2-3 semanas)
Para cada participante:

1. **Sesión de introducción (10 min)**:
   - Propósito de la investigación (sin fines diagnósticos)
   - Recordatorio de que es un prototipo
   - Preguntas previas sobre experiencia previa con herramientas similares

2. **Tareas guiadas (40-50 min)**:
   - Tarea 1: Cargar y procesar imagen de muestra
   - Tarea 2: Revisar clasificación de normales vs sospechosas
   - Tarea 3: Explorar parámetros (sigmas, polaridad, métodos de separación)
   - Tarea 4: Exportar resultados
   - Tarea 5: Identificar núcleos sospechosos y justificar

3. **Formulario de retroalimentación (10-15 min)**:
   - Completar cuestionario estructurado
   - Entrevista semi-estructurada (30 min)
   - Registro de problemas técnicos

4. **Observación y notas**:
   - Cronometrar cada tarea
   - Capturar capturas de pantalla de errores o confusión
   - Anotar comentarios verbatim

#### Paso 3: Análisis y Priorización (1 semana)
1. Consolidar todos los formularios y notas de entrevista
2. Identificar problemas recurrentes por categoría:
   - **Interfaz/UX**: Carga, navegación, visualización de resultados
   - **Parámetros**: Comprensión de sigmas, polaridad, métodos de separación
   - **Resultados**: Claridad de clasificación, justificación, reproducibilidad
   - **Exportación**: Formato CSV, bitácora, nombres de archivo
   - **Técnico**: Errores, rendimiento, estabilidad
3. Priorizar problemas por:
   - **Alta**: Bloquean el flujo básico, confusión crítica, errores de sistema
   - **Media**: Afectan la experiencia de usuario, parámetros poco claros
   - **Baja**: Mejoras estéticas, documentación adicional
4. Crear historias de usuario para cada mejora prioritaria

#### Paso 4: Implementación de Mejoras (2-4 semanas)
Para cada mejora prioritaria:

1. **Correcciones de bugs**: Fix any identified issues in `src/analysis.py`, `src/preprocessing.py`, `src/dog_filter.py`
2. **Mejoras de UX**: Actualizar `app.py` (Streamlit), `main.py` (CLI), o documentación
3. **Actualización de parámetros**: Ajustar valores por defecto si el feedback sugiere mejores valores
4. **Nueva documentación**: Actualizar `docs/guia_usuario.md`, `docs/algoritmos_metricas.md` según sea necesario
5. **Nuevas pruebas**: Agregar pruebas de regresión bajo `tests/` si se corrige comportamiento del pipeline

#### Paso 5: Validación y Cierre (1 semana)
1. Verificar que los fixes no rompan funcionalidad existente
2. Ejecutar `python -m unittest discover -s tests -v` - todos deben pasar
3. Revisar `git diff --check` - sin errores de formato
4. Actualizar documentación con nueva información
5. Mover `ACT-18 (CITO-39)` a `Hecha` en Jira con evidencia adjunta

### Ejemplo de Registro de Feedback

```
Fecha: 2026-09-22
Participante: [Nombre citotecnólogo]
Imágenes probadas: MUESTRA_001.jpg, MUESTRA_002.jpg, MUESTRA_003.jpg
Método de separación: watershed

Puntuaciones (1-5):
  - Facilidad de carga: 5
  - Claridad de clasificación: 3
  - Comprensión de sigmas: 2
  - Utilidad de separación: 4
  - Facilidad de exportación: 4

Comentarios principales:
  - "Los sigmas 7.0 y 8.0 son confusos, no sé por qué esos valores"
  - "El mensaje de 'no diagnóstico' al final es bueno, pero tardé en encontrarlo"
  - "Me gustaría poder guardar mis configuraciones de parámetros"
  - "El tiempo de procesamiento es razonable (~1 min)"

Problemas identificados:
  1. (Alta) Falta de explicación sobre qué son los sigmas DoG y por qué 7.0/8.0
  2. (Media) Botón de exportación no evidente en la interfaz de Streamlit
  3. (Baja) No hay forma de guardar configuraciones de parámetros entre sesiones

Mejoras propuestas:
  1. Agregar tooltips descriptivos a los controles de sigma en la interfaz
  2. Agregar sección "Mis configuraciones" para guardar parámetros
  3. Mejorar visibilidad del botón de exportación con ícono y texto
  4. Agregar sección de Preguntas Frecuentes sobre parámetros

Decisión: Implementar mejoras 1 y 2 en la próxima sprint (2 semanas). Mejoras 3 y 4 para versión posterior.
```

### Relación con Otras Actividades

| Actividad | Dependencia | Resultado Esperado |
|-----------|-------------|-------------------|
| **CITO-38 (ACT-17)** | Requiere resultados de pruebas de usabilidad | Plan de pruebas completado ✅ |
| **CITO-39 (ACT-18)** | Requiere feedback de CITO-38 | Mejoras prioritarias identificadas y planificadas |
| **CITO-40 (ACT-19)** | Depende de decisiones de CITO-39 | Adquisición de más imágenes si es necesario |
| **CITO-41 (ACT-20)** | Depende de decisiones de CITO-39 | Etiquetado de imágenes con feedback de operadores |
| **CITO-42 (ACT-21)** | Puede identificarse durante CITO-39 | Correcciones al filtro DoG si el feedback sugiere problemas |

### Checklist de Validación Pre-Feedback

- [ ] Usabilidad tests (CITO-38) completados con ≥2 participantes
- [ ] Todos los formularios de evaluación llenados
- [ ] Entreviews semi-estructuradas realizadas y grabadas (con consentimiento)
- [ ] Errores técnicos documentados durante las pruebas
- [ ] Entorno de trabajo restaurado (sin datos de prueba sensibles)
- [ ] `python -m unittest discover -s tests -v` pasa (66/66)
- [ ] `git diff --check` sin errores

### Criterios de Éxito Final

CITO-39 (ACT-18) se considerará completado cuando:

1. **Feedback recopilado** de mínimo 2 citotecnólogos/revisores clínicos
2. **Reporte consolidado** con problemas identificados y prioridad asignada
3. **Lista de mejoras** creada con historias de usuario para cada una
4. **Decision documentada** sobre qué implementar en próxima iteración
5. **Código actualizado** con correcciones de bugs críticos (si los hay)
6. **Documentación actualizada** con nueva información del feedback
7. **Estado en Jira** actualizado a `Hecha` con evidencia adjunta (commit/PR, reportes, formularios)

### Próximas Actividades Después de CITO-39

- **CITO-40 (ACT-19)**: Adquirir y organizar imágenes de citología cervical - si el feedback identifica necesidad de más datos de entrenamiento o prueba
- **CITO-41 (ACT-20)**: Etiquetar imágenes con anotaciones de núcleos celulares - si el feedback sugiere mejoras en la detección o clasificación
- **CITO-42 (ACT-21)**: Implementar y validar correcciones del filtro DoG - J-06, puede identificarse durante el análisis de feedback
- **CITO-43 (ACT-22)**: Medir tiempo de procesamiento manual vs automatizado - comparar antes/después de las mejoras implementadas