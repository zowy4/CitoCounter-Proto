# CitoCounter-Proto: Pruebas de Usabilidad con Citotecnólogos

## ACT-17 (CITO-37) - CITO-38

### Fecha: 2026-09-22
### Estado: PLANEADO (pending execution)

### Objetivo
Evaluar la usabilidad del prototipo CitoCounter-Proto con citotecnólogos operadores de laboratorio, identificando problemas de interfaz, flujo de trabajo y claridad en la distinción entre resultados experimentales vs diagnósticos.

### Personas Participantes
- **Operador de laboratorio / Citotecnólogo**: Usuario principal que ejecuta el análisis de imágenes
- **Revisor clínico**: Valida resultados y clasificación de núcleos
- **Investigador**: Interesado en métricas y parámetros del pipeline
- **Administrador técnico**: Mantiene el entorno y configuración del sistema

### Requisitos Previos (Checklist)
- [x] **Pipeline estable**: CITO-36 completado, todos los 66 tests passing ✅
- [x] **Documentación disponible**: Arquitectura, algoritmos, guía de usuario y seguridad ✅
- [x] **Entorno listo**: CLI y Streamlit disponibles en la estación de trabajo ✅
- [ ] **Imágenes de prueba**: Conjunto de imágenes representativo (mixto de núcleos claros/oscuros, superpuestos y separados)
- [ ] **Parámetros por defecto**: Configuración estándar lista para usar
- [ ] **Formularios de evaluación**: Listos para capturar feedback del usuario

### Wireflows Mínimos a Probar

#### 1. Carga y Análisis de Imagen
- [ ] Iniciar Streamlit (`streamlit run app.py`)
- [ ] Seleccionar imagen de prueba desde el explorador de archivos
- [ ] Verificar que la imagen se carga correctamente sin errores
- [ ] Observar el progreso del preprocesamiento (gris, CLAHE, ruido)
- [ ] Confirmar la aplicación del filtro DoG con los sigmas por defecto (7.0, 8.0)
- [ ] Ver la aparición de contornos y clasificación inicial

#### 2. Revisión de Resultados
- [ ] Revisar el panel de resultados con clasificación de normales (verde) vs sospechosas (rojo)
- [ ] Contar el total de núcleos detectados
- [ ] Verificar las áreas calculadas para cada núcleo
- [ ] Comprobar el método de separación utilizado (ningún/watershed/máximos_locales)
- [ ] Distinguir claramente entre resultado experimental vs diagnóstico

#### 3. Exportación y Consulta Histórica
- [ ] Exportar resultados a CSV/bitácora
- [ ] Revisar el archivo bitacora_experimentos.csv generado
- [ ] Confirmar que los nombres de archivo de salida son genéricos (MUESTRA_001, etc.)
- [ ] Verificar que no hay datos identificables de paciente en la salida

### Criterios de Usabilidad a Evaluar

| Criterio | Indicador de Éxito | Método de Medición |
|----------|-------------------|-------------------|
| **Facilidad de carga** | Imagen cargada exitosamente en < 30 segundos | Cronómetro + observación |
| **Claridad de clasificación** | El operador puede identificar por qué un núcleo es "normal" vs "sospechoso" | Pregunta post-tarea |
| **Interpretación de parámetros** | El operador entiende el significado de sigmas DoG y polaridad | Entrevista breve |
| **Distinción experimental/diagnóstico** | El operador distingue claramente el mensaje de "no diagnóstico" | Pregunta de escenificación |
| **Exportación de resultados** | Los resultados se pueden exportar sin errores | Prueba de flujo |
| **Tiempo de procesamiento** | Tiempo total desde carga hasta resultados < 2 minutos | Cronómetro |

### Plan de Ejecución

#### Paso 1: Preparación (30 minutos)
1. Verificar que el entorno está configurado:
   ```bash
   python -m pip install -r requirements.txt
   python verificar_entorno.py
   ```
2. Preparar conjunto de imágenes de prueba (mínimo 5-10 imágenes):
   - Mezcla de imágenes con núcleos claros y oscuros
   - Incluir casos de núcleos superpuestos y separados
   - Variedad de condiciones de iluminación
3. Configurar parámetros por defecto:
   - `--sigma1 7.0 --sigma2 8.0 --polaridad nucleos-claros`
   - O usar la interfaz de Streamlit con valores por defecto

#### Paso 2: Ejecución de Pruebas (60-90 minutos por citotecnólogo)
Para cada participante:

1. **Sesión de introducción (10 min)**:
   - Presentar el propósito de la prueba (sin fines diagnósticos)
   - Explicar que es un prototipo de investigación
   - Firmar el formulario de consentimiento/aviso

2. **Tareas guiadas (40 min)**:
   - **Tarea 1**: Cargar y procesar una imagen de muestra
   - **Tarea 2**: Revisar los resultados de clasificación
   - **Tarea 3**: Explorar los parámetros (sigmas, polaridad, separación)
   - **Tarea 4**: Exportar los resultados a CSV
   - **Tarea 5**: Identificar qué núcleos considera sospechosos y por qué

3. **Preguntas post-tarea (15 min)**:
   - "¿Qué parte del proceso le resultó más intuitiva?"
   - "¿Qué parte le resultó confusa o difícil?"
   - "¿Sugeriría algún cambio en el interfaz o flujo de trabajo?"
   - "¿Siente que puede distinguir claramente entre resultados experimentales vs diagnósticos?"

4. **Observación y registro**:
   - Anotar tiempo de cada tarea
   - Capturar capturas de pantalla de cualquier error o confusión
   - Registrar comentarios verbatim del participante

#### Paso 3: Análisis de Resultados (30 minutos)
1. Consolidar todos los formularios de evaluación
2. Identificar problemas de usabilidad recurrentes
3. Priorizar problemas por impacto y frecuencia
4. Crear reporte de hallazgos

### Entregables

- [ ] **Formularios de evaluación de usabilidad** completados por cada participante
- [ ] **Reporte de hallazgos** con problemas identificados y prioritarios
- [ ] **Wireflows actualizados** basados en la retroalimentación del usuario
- [ ] **Lista de mejoras propuestas** ordenadas por impacto
- [ ] **Registro de sesión** que no altere las métricas o historial existente
- [ ] **Decisión sobre continuidad**: ¿Proseguir con CITO-39 (recopilación de feedback clínico)?

### Consideraciones Éticas y de Seguridad

- **Aviso claro**: El sistema es un prototipo de investigación, no un dispositivo médico de diagnóstico
- **Sin datos de paciente**: Usar imágenes de prueba sintéticas o anonimizadas
- **Retención de datos**: Los resultados de la prueba se guardan temporalmente para análisis, no se commitean al repositorio
- **Confidencialidad**: Los comentarios del participante son confidenciales y se anonimizan en reportes

### Éxito y Criterios de Aceptación

Las pruebas de usabilidad se considerarán exitosas si:

1. **Mínimo 2 citotecnólogos** participan en las pruebas
2. **Al menos 80% de las tareas** se completan sin asistencia técnica
3. **Problemas críticos** (bloqueantes) sean 0 - el sistema debe permitir completar el flujo básico sin errores
4. **Claridad de distinción** experimental/diagnóstico sea confirmada por al menos el 75% de los participantes
5. **Tiempo promedio** de procesamiento sea razonable (< 2 minutos para el flujo completo)
6. **Feedback recopilado** documentado en un reporte estructurado

### Próximas Actividades Dependientes

- **CITO-39 (ACT-18)**: Recopilar feedback de personal clínico y resolver cambios - depende de los resultados de esta actividad
- **CITO-40 (ACT-19)**: Adquirir y organizar imágenes de citología cervical - si las pruebas identifican necesidad de más datos
- **CITO-41 (ACT-20)**: Etiquetar imágenes con anotaciones de núcleos celulares - si el feedback sugiere mejoras en la detección

### Registro de Sesión (ejemplo)

```
Fecha: 2026-09-22
Participante: [Nombre citotecnólogo]
Imágenes probadas: MUESTRA_001.jpg, MUESTRA_002.jpg, MUESTRA_003.jpg
Método de separación: watershed
Tiempo total promedio: 1 minuto 45 segundos
Hallazgos principales:
  - El operador encontró intuitiva la sección de parámetros
  - Sugerencia: agregar descripciones tooltips a los controles de sigma
  - El mensaje de "no diagnóstico" fue claro para el 100% de participantes
  - Tiempo de carga de imagen: ~8 segundos
Problemas identificados:
  - [Por registrar durante las pruebas]
Mejoras sugeridas:
  - [Por registrar durante las pruebas]
```

### Checklist de Validación Pre-Test

- [ ] Streamlit corriendo sin errores (`streamlit run app.py`)
- [ ] Al menos 5 imágenes de prueba cargables
- [ ] Parámetros por defecto configurados y documentados
- [ ] Formularios de evaluación listos (paper o digital)
- [ ] Entorno de prueba aislado (sin afectar producción/datos reales)
- [ ] Aviso de "prototipo de investigación, no diagnóstico" visible para el usuario