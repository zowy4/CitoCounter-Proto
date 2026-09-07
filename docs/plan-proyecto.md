# Análisis normativo y plan de ejecución Jira

## 1. Alcance y estado actual

**Proyecto:** Implementación de Software de Conteo de Células en Citología Cervical mediante la Diferencia de Gaussiana en tiempo real.

**Unidad económica:** Centro de Inteligencia en Salud (CIS), Subdirección de Tecnología.

**Periodo:** agosto-diciembre de 2026.

CitoCounter-Proto es actualmente un **prototipo de investigación**, no un dispositivo médico ni un sistema de apoyo diagnóstico validado. El flujo existente es:

1. Carga de imagen desde CLI o Streamlit.
2. Preprocesamiento: escala de grises, CLAHE y filtro bilateral opcional.
3. Filtro Difference of Gaussians (DoG).
4. Umbralización de Otsu y contornos externos.
5. Filtro por área y clasificación por regla temporal de `3 x` el área normal.
6. Visualización y registro parcial de resultados.

### Hallazgos que deben convertirse en trabajo Jira

- `AREA_PROMEDIO_NUCLEO_NORMAL = 300` y los límites de área son valores temporales no calibrados.
- La resta DoG usa imágenes `uint8`; debe comprobarse y documentarse el manejo de diferencias negativas antes de afirmar el rendimiento del algoritmo.
- El dataset no está listo para validación: faltan `images/train`, `images/val` y `labels/val`; el CSV tiene 100 registros sin imágenes correspondientes.
- No existe una suite automatizada de pruebas ni un cálculo implementado de precisión, sensibilidad, F1 e IoU.
- La documentación contiene ejemplos CLI con `--input` y `--output`, pero la ayuda real usa una ruta posicional.
- El dashboard no tiene autenticación, autorización, auditoría, política de retención ni límites de carga; no debe exponerse con imágenes identificables.
- El nombre original de una imagen puede conservar identificadores personales en el índice del dataset.
- La regla “sospechosa” no equivale a diagnóstico. La interfaz debe mostrar explícitamente que el resultado requiere revisión experta.

## 2. Normas y marcos aplicables

La aplicabilidad final debe ser confirmada por CIS, el responsable de protección de datos, el comité de ética y, si procede, el área regulatoria. La lista siguiente sirve para el análisis de requisitos, no constituye una certificación.

### 2.1 Salud, investigación y datos personales en México

| Norma o marco | Aplicación al proyecto | Evidencia que debe planearse |
|---|---|---|
| **NOM-014-SSA2-1994** y sus actualizaciones, prevención, detección, diagnóstico, tratamiento, control y vigilancia epidemiológica del cáncer cérvico uterino | Referencia clínica para definir el contexto de citología, términos, flujo de revisión y límites de interpretación | Glosario validado por personal clínico, criterios de uso y leyenda de no diagnóstico |
| **NOM-004-SSA3-2012**, expediente clínico | Aplica si se vinculan imágenes o resultados con expedientes, pacientes o atención clínica | Catálogo mínimo de datos, control de acceso, trazabilidad, conservación y bitácora |
| **NOM-024-SSA3-2012**, sistemas de información de registro electrónico para la salud | Aplica si el sistema intercambia o administra información clínica electrónica | Requisitos de seguridad, interoperabilidad, identificación de usuarios y auditoría |
| **NOM-012-SSA3-2012**, investigación para la salud en seres humanos | Aplica si se usan muestras o datos humanos para investigación y evaluación | Protocolo, autorización institucional, consentimiento o dispensa documentada, comité de ética y plan de datos |
| **NOM-087-SEMARNAT-SSA1-2002**, residuos peligrosos biológico-infecciosos | Aplica al manejo físico de muestras o material biológico; no al procesamiento digital aislado | Procedimiento de bioseguridad y responsable designado, si el proyecto manipula muestras |
| **LFPDPPP** y su Reglamento; principios ARCO y aviso de privacidad | Aplica a imágenes, nombres de archivo, metadatos y cualquier dato que identifique o pueda identificar a una persona | Inventario de datos, base legal, minimización, anonimización, retención, eliminación y atención de derechos |
| **Ley General de Salud** y políticas institucionales del CIS | Marco superior para investigación, información de salud y uso clínico | Dictamen institucional del alcance y autorización de operación |

### 2.2 Marcos internacionales de software y dispositivo médico

Estos marcos son especialmente relevantes si el prototipo evoluciona a una herramienta clínica o comercial:

| Marco | Uso recomendado |
|---|---|
| **ISO 13485:2016** | Sistema de gestión de calidad para producto sanitario |
| **ISO 14971:2019** | Gestión de riesgos: falsos negativos, falsos positivos, datos, disponibilidad y uso indebido |
| **IEC 62304:2006+A1:2015** | Ciclo de vida del software sanitario, requisitos, arquitectura, verificación y mantenimiento |
| **IEC 62366-1:2015+A1:2020** | Ingeniería de usabilidad y reducción de errores de uso |
| **ISO 14155:2020** | Buenas prácticas para investigaciones clínicas cuando corresponda |
| **IEC 81001-5-1:2021** | Ciberseguridad del software de salud durante su ciclo de vida |
| **DICOM** | Intercambio de imágenes médicas si se integra con equipos o PACS |
| **HL7 FHIR** | Intercambio de resultados clínicos si se integra con sistemas institucionales |
| **CLAIM** | Reporte reproducible de modelos de inteligencia artificial en imagen médica |

Para el semestre, la meta razonable es documentar conformidad de proceso y riesgos del prototipo; no declarar conformidad regulatoria del producto final sin evaluación formal.

## 3. Normas de código y calidad recomendadas

1. **PEP 8**, nombres descriptivos, módulos cohesionados y funciones pequeñas.
2. **PEP 257** para docstrings y documentación de funciones públicas.
3. **Type hints** en funciones del pipeline y estructuras de resultados estables.
4. **pytest** para pruebas unitarias y de integración; cobertura mínima acordada por el equipo.
5. **Ruff** para linting y formato, o una combinación equivalente aprobada por el equipo.
6. **Git Flow ligero:** ramas por historia, pull request, revisión y etiquetas de versión.
7. **Conventional Commits** y **Semantic Versioning** para trazabilidad de cambios.
8. **OWASP ASVS** como lista de verificación para la interfaz web y futura API; secretos fuera del repositorio.
9. Validación estricta de extensiones, tamaño, contenido y errores de imágenes cargadas.
10. Datos sintéticos o anonimizados en Git; nunca nombres de pacientes ni imágenes identificables.
11. Registro reproducible de versión de código, parámetros DoG, versión del dataset, fecha, operador y resultado.
12. Separación entre código, configuración calibrada, datos de prueba y datos clínicos.

## 4. Estructura sugerida para Jira

### Épicas

- **E1. Gobierno, ética y requisitos**
- **E2. Dataset y ground truth**
- **E3. Pipeline DoG y calibración**
- **E4. Validación científica y comparación**
- **E5. Reglas explicables y clasificación**
- **E6. API REST y seguridad**
- **E7. Interfaz y experiencia de usuario**
- **E8. Dashboard, ETL y almacenamiento analítico**
- **E9. Verificación, documentación y entrega**

### Backlog priorizado

| ID | Historia o tarea Jira | Dependencia | Criterio de aceptación / evidencia | Semanas sugeridas |
|---|---|---|---|---|
| J-01 | Definir alcance clínico, usuarios, entradas, salidas y leyenda de no diagnóstico | Ninguna | Documento aprobado por CIS y responsable clínico | 1 |
| J-02 | Elaborar matriz de datos, anonimización, retención y accesos | J-01 | Matriz y procedimiento aprobados | 1-2 |
| J-03 | Completar dataset real o autorizado y estructura train/val/test | J-02 | Cada imagen tiene ID, split, etiqueta y trazabilidad | 2-5 |
| J-04 | Definir protocolo de anotación y doble revisión experta | J-03 | Guía, responsables y muestra de concordancia | 3-5 |
| J-05 | Corregir el validador para fallar cuando un split está vacío o hay archivos huérfanos | J-03 | Pruebas negativas y reporte sin falsos OK | 4-5 |
| J-06 | Corregir y probar el manejo numérico de DoG, incluyendo diferencias positivas y negativas | Ninguna | Pruebas de regresión y comparación visual documentada | 2-3 |
| J-07 | Calibrar sigma, umbral, áreas mínima/máxima y regla de clasificación | J-03, J-04, J-06 | Tabla de parámetros, protocolo y conjunto de calibración separado | 5-7 |
| J-08 | Implementar métricas de detección y segmentación: precisión, sensibilidad, F1 e IoU | J-03, J-04 | Script reproducible con casos unitarios y reporte | 6-8 |
| J-09 | Comparar DoG contra Otsu y una línea base documentada | J-07, J-08 | Tabla y gráficas por imagen y conjunto | 8-9 |
| J-10 | Diseñar reglas explicables normal/sospechosa y sus límites | J-07 | Documento de reglas, casos frontera y revisión clínica | 8-9 |
| J-11 | Extraer el pipeline a una API REST versionada | J-07 | Endpoint documentado, esquema de entrada/salida y pruebas | 9-11 |
| J-12 | Aplicar controles de seguridad a cargas, errores, acceso y eliminación temporal | J-11, J-02 | Checklist OWASP, pruebas de abuso y política de retención | 10-12 |
| J-13 | Ajustar la interfaz para mostrar parámetros, incertidumbre, advertencia clínica y exportación | J-10, J-11 | Flujo funcional probado con usuarios internos | 10-12 |
| J-14 | Diseñar almacenamiento de resultados y modelo de datos analítico | J-08, J-11 | Esquema, claves, versionado de modelo y dataset | 11-13 |
| J-15 | Construir ETL y dashboard de indicadores | J-14 | Carga reproducible, conteos, sospechosas, riesgo y comparación por muestra | 13-15 |
| J-16 | Pruebas de rendimiento y medición del objetivo de reducción de tiempo | J-11, J-13 | Comparación con protocolo manual y tamaño de muestra definido | 14-16 |
| J-17 | Auditoría de reproducibilidad, documentación y paquete de entrega | Todas | Manual, API, dataset autorizado, bitácora, informe y acta de aceptación | 17-18 |

### Orden de ejecución

`J-01 -> J-02 -> J-03/J-04 -> J-05/J-06 -> J-07 -> J-08 -> J-09/J-10 -> J-11 -> J-12/J-13 -> J-14 -> J-15/J-16 -> J-17`

El periodo de agosto a diciembre tiene aproximadamente 18 semanas. Deben reservarse al menos dos semanas para validación final, correcciones y documentación; el objetivo de F1 superior a 90 % debe tratarse como meta experimental, no como criterio garantizado.

## 5. Definición de terminado (DoD)

Una actividad se considera terminada cuando:

- Tiene criterios de aceptación verificables y evidencia adjunta.
- Cuenta con revisión de código o documento por otra persona.
- Incluye pruebas automatizadas o una prueba manual reproducible, según el riesgo.
- Registra versión de código, dataset, parámetros y fecha.
- No contiene datos personales identificables en el repositorio.
- Actualiza la documentación afectada.
- No presenta resultados clínicos como diagnóstico ni como certificación.

## 6. Riesgos prioritarios para el tablero

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Dataset insuficiente o no autorizado | Impide medir F1, IoU y generalización | Bloquear J-07/J-08 hasta completar J-02-J-04 |
| Falsos negativos en células sospechosas | Riesgo clínico alto | Evaluación por experto, análisis por subgrupos y revisión de casos fallidos |
| Imágenes identificables | Incumplimiento de privacidad | Anonimización, control de acceso y no almacenar originales en Git |
| Parámetros sobreajustados | Resultados no reproducibles | Separar calibración de prueba y congelar configuración antes de evaluar |
| Exposición no protegida de Streamlit/API | Divulgación o manipulación de datos | Uso local durante prototipo y controles de seguridad antes de desplegar |

## 7. Decisión recomendada

Registrar el proyecto en Jira como **prototipo de investigación con posible evolución a software sanitario**, con un bloqueo explícito para cualquier uso clínico. La primera iteración debe cerrar alcance, autorización de datos, dataset y corrección numérica del DoG; solamente después conviene comprometer el objetivo de F1, la API y los indicadores del dashboard.