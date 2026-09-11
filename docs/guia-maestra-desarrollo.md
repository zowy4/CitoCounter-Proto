# Guía maestra de desarrollo y seguimiento

## 1. Propósito

Esta guía adapta la **Guía Maestra de Desarrollo de Software** al estado real de CitoCounter-Proto. El prototipo ya iniciado no se descarta: se toma como línea base, se documenta, se verifica y se convierte gradualmente en una plataforma reproducible para investigación.

El proyecto sigue siendo un **prototipo de investigación**. No es un dispositivo médico ni una herramienta de diagnóstico. Cualquier resultado requiere revisión experta y autorización institucional antes de usar datos clínicos.

La fuente operativa de seguimiento es Jira:

- Tareas principales: `J-01` a `J-21`.
- Actividades/subtareas: `ACT-01` a `ACT-23`.
- Claves Jira de las actividades: `CITO-22` a `CITO-44`.
- Épicas: `E1` a `E9`.
- Periodo de referencia: 18 semanas, de agosto a diciembre de 2026.
- La fuente de verdad para las incidencias es Jira; los CSV históricos de importación se eliminaron después de importar las incidencias. Las nuevas actividades se crearán y relacionarán directamente desde la extensión de Jira.

## 2. Cómo se integra el prototipo existente

El estado inicial se registra como **Fase 0: línea base**. Antes de mover una actividad a terminada, se debe conservar evidencia del estado anterior y del resultado posterior.

| Elemento actual | Línea base que se debe conservar | Evolución prevista |
|---|---|---|
| `main.py` | Ejecución CLI y parámetros usados | Pipeline versionado y reproducible |
| `app.py` | Flujo actual de Streamlit | Interfaz con estados, advertencias y validación de cargas |
| `src/` | Preprocesamiento, DoG, análisis y visualización | Módulos probados y contrato estable de resultados |
| `CitoDataset_v1/` | Estructura y archivos disponibles | Dataset autorizado con `train/val/test` y ground truth |
| `data/results/` | Salidas y capturas existentes | Resultados versionados con parámetros y dataset |
| `docs/` | Guías y bitácoras actuales | Evidencia enlazada a Jira y paquete de entrega |

La línea base se cierra con un registro de versión, fecha, entorno, parámetros, dataset usado y limitaciones conocidas. No se deben cambiar parámetros para obtener una métrica sin crear una nueva versión de experimento.

## 3. Mapa oficial de identificadores Jira

Para evitar mezclar el identificador académico con la clave real de Jira, se usarán estas reglas:

- `J-xx`: identificador interno de la tarea del plan y de la épica correspondiente.
- `ACT-xx`: identificador interno de la actividad definida en el proyecto.
- `CITO-xx`: clave real de la incidencia en Jira.
- Las tareas principales conservan sus claves Jira previamente asignadas (`CITO-1` a `CITO-21`).
- Las actividades agregadas posteriormente corresponden consecutivamente a `CITO-22` a `CITO-44`.
- Este mapa es la referencia única para abrir, actualizar y cerrar actividades desde la extensión de Jira.

| Actividad | Clave Jira | Resumen esperado en Jira | Tarea interna | Estado inicial |
|---|---|---|---|---|
| ACT-01 | CITO-22 | Calibrar el algoritmo DoG para detectar núcleos celulares | J-07 | Por hacer |
| ACT-02 | CITO-23 | Evaluar precisión, sensibilidad, F1-Score e IoU | J-08 | Por hacer |
| ACT-03 | CITO-24 | Definir reglas para clasificar células normales o sospechosas | J-10 | Por hacer |
| ACT-04 | CITO-25 | Desarrollar API REST para procesar imágenes y devolver análisis | J-11 | Por hacer |
| ACT-05 | CITO-26 | Implementar interfaz para visualizar conteo y clasificación | J-13 | Por hacer |
| ACT-06 | CITO-27 | Integrar el sistema con un dashboard de resultados y métricas | J-15 | Por hacer |
| ACT-07 | CITO-28 | Diseñar indicadores clave del rendimiento del sistema | J-15 | Por hacer |
| ACT-08 | CITO-29 | Construir flujo ETL para resultados y reportes históricos | J-15 | Por hacer |
| ACT-09 | CITO-30 | Diseñar almacenamiento para resultados de experimentación | J-14 | Por hacer |
| ACT-10 | CITO-31 | Validar F1-Score >= 90% con dataset de prueba congelado | J-18 | Por hacer |
| ACT-11 | CITO-32 | Identificar estrategias para superar superposición celular | J-19 | Por hacer |
| ACT-12 | CITO-33 | Mitigar artefactos de tinción y variaciones de iluminación | J-19 | Por hacer |
| ACT-13 | CITO-34 | Documentar arquitectura del sistema y flujo de datos | J-20 | Por hacer |
| ACT-14 | CITO-35 | Documentar algoritmos, parámetros y métricas de evaluación | J-20 | Por hacer |
| ACT-15 | CITO-36 | Crear guía de usuario y manual de instalación | J-20 | Por hacer |
| ACT-16 | CITO-37 | Documentar seguridad, privacidad y conformidad normativa | J-20 | Por hacer |
| ACT-17 | CITO-38 | Ejecutar pruebas de usabilidad con citotecnólogos | J-21 | Por hacer |
| ACT-18 | CITO-39 | Recopilar feedback de personal clínico y resolver cambios | J-21 | Por hacer |
| ACT-19 | CITO-40 | Adquirir y organizar imágenes de citología cervical | J-03 | Por hacer |
| ACT-20 | CITO-41 | Etiquetar imágenes con anotaciones de núcleos celulares | J-04 | Por hacer |
| ACT-21 | CITO-42 | Implementar y validar correcciones del filtro DoG | J-06 | En revisión |
| ACT-22 | CITO-43 | Medir tiempo de procesamiento manual vs automatizado | J-16 | Por hacer |
| ACT-23 | CITO-44 | Crear suite de pruebas para validación de dataset | J-05 | Por hacer |

La asignación `ACT-01 -> CITO-22` hasta `ACT-23 -> CITO-44` se basa en la numeración consecutiva indicada para las actividades creadas en Jira. Si una clave real difiere en Jira, se debe corregir esta tabla antes de iniciar esa actividad; no se crearán claves alternativas ni se reutilizarán CSV históricos.

### Confirmación obligatoria en la extensión de Jira

Antes de iniciar las actividades, confirmar manualmente en la extensión de Jira cada fila de la tabla anterior. La confirmación debe hacerse sobre la incidencia real, no sobre el identificador interno:

1. Buscar la clave `CITO-22` a `CITO-44` en la extensión de Jira.
2. Comprobar que el **Resumen** coincide con el nombre de la actividad `ACT-xx` correspondiente.
3. Comprobar que la incidencia tiene como padre la tarea `J-xx` indicada en la tabla, usando la clave Jira de la tarea padre (`CITO-1` a `CITO-21`) cuando Jira la muestre.
4. Confirmar que el tipo de incidencia es actividad/subtarea y que su estado inicial es `Por hacer`, salvo `CITO-42`, que queda `En revisión` por la corrección DoG ya realizada.
5. Añadir una marca en la descripción o comentario de Jira con el formato: `Mapa verificado: ACT-xx | CITO-xx | padre CITO-yy | fecha AAAA-MM-DD`.
6. Si el resumen, la clave, el padre o el tipo no coinciden, marcar la incidencia como `Bloqueada` y corregir primero esta guía o la relación en Jira.

| Clave Jira | Actividad | Resumen verificado | Padre verificado | Tipo verificado | Estado real | Fecha/revisor |
|---|---|---|---|---|---|---|
| CITO-22 | ACT-01 | Confirmado localmente | Confirmado en plan | Actividad/subtarea validada localmente | En revisión recomendado | 2026-09-11 |
| CITO-23 | ACT-02 | Evaluación espacial ejecutada; requiere corrección | Confirmado en plan | Actividad/subtarea con evaluación cuantitativa en revisión | En curso recomendado | 2026-09-11 |
| CITO-24 | ACT-03 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-25 | ACT-04 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-26 | ACT-05 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-27 | ACT-06 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-28 | ACT-07 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-29 | ACT-08 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-30 | ACT-09 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-31 | ACT-10 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-32 | ACT-11 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-33 | ACT-12 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-34 | ACT-13 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-35 | ACT-14 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-36 | ACT-15 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-37 | ACT-16 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-38 | ACT-17 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-39 | ACT-18 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-40 | ACT-19 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-41 | ACT-20 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-42 | ACT-21 | Confirmado localmente | Confirmado en plan | Actividad/subtarea pendiente de Jira | En revisión recomendado | Pendiente |
| CITO-43 | ACT-22 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| CITO-44 | ACT-23 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |

La tabla anterior registra el procedimiento y la asignación esperada; la extensión de Jira es la fuente final para confirmar el resumen real, la relación padre-hijo y el estado. No se debe marcar una actividad como `Hecha` hasta completar esta verificación y adjuntar la evidencia correspondiente.

### Acta de revisión final de Jira

| Control | Resultado local | Resultado remoto Jira | Estado |
|---|---|---|---|
| Protocolo de confirmación | Documentado en esta guía | Pendiente de ejecución en la extensión | Preparado |
| Tabla canónica con resúmenes | 23 actividades y 23 claves documentadas | Pendiente de comparar con Jira | Preparado |
| Padres y tipos de incidencia | Padres internos documentados | Pendiente de confirmar en Jira | Pendiente |
| Estados iniciales | `Por hacer` para actividades nuevas; `CITO-22` validado localmente y `CITO-23` evaluado localmente | Pendiente de confirmar en Jira | Pendiente |
| Pruebas del repositorio | 3 pruebas pasan; `git diff --check` correcto | No aplica | Confirmado localmente |
| CITO-23 | TP=0, FP=39, FN=42, Precision=0, Recall=0, F1=0, IoU medio=0 sobre 9 imágenes; requiere revisar el emparejamiento espacial | Debe corregirse y validarse en Jira antes de cerrar | En curso |
| Revisión final | No hay acceso remoto desde el repositorio | Debe ejecutarse en la extensión | Pendiente |

**Fecha de revisión local:** 2026-09-10  
**Revisor local:** equipo del proyecto  
**Cobertura esperada:** `CITO-22` a `CITO-44`  
**Criterio para liberar el inicio:** todas las filas deben tener resumen, padre, tipo, estado, fecha y revisor confirmados en Jira. Las filas con discrepancias deben pasar a `Bloqueada`.

## 4. Trazabilidad Jira

Cada actividad debe mantener la siguiente relación:

`Épica -> J-xx -> ACT-xx -> commit/PR -> evidencia -> métrica -> decisión`

En cada incidencia Jira se registrará:

| Campo | Regla |
|---|---|
| Resumen | Mantener `ACT-xx` y la clave real `CITO-xx` en la descripción, por ejemplo `ACT-01 (CITO-22)`. |
| Dependencias | No iniciar una tarea bloqueada; enlazar la incidencia predecesora. |
| Estado | `Por hacer`, `En progreso`, `En revisión`, `Bloqueada`, `Hecha`; actualizarlo en Jira al comenzar, pausar, enviar a revisión y cerrar una actividad. |
| Evidencia | Enlace a documento, commit/PR, reporte, captura o ejecución reproducible. |
| Métrica | Valor observado, unidad, dataset, versión y fecha. |
| Riesgo | Marcar impacto y mitigación, especialmente privacidad y falsos negativos. |
| Cierre | Revisión por otra persona y criterios de aceptación cumplidos. |

### Métricas de seguimiento del proyecto

Estas métricas miden avance y calidad; no sustituyen las métricas científicas del algoritmo.

| Métrica | Fórmula o criterio | Cadencia | Meta de control |
|---|---|---|---|
| Avance de tareas | Incidencias `Hechas` / incidencias planificadas x 100 | Semanal | Tendencia creciente, sin cerrar trabajo sin evidencia |
| Avance ponderado | Puntos completados / puntos planificados x 100 | Semanal | Comparar con la semana del plan |
| Trazabilidad | Actividades con evidencia y enlace Jira / actividades terminadas x 100 | Semanal | 100% |
| Calidad de entrega | Criterios cumplidos / criterios evaluados x 100 | Por revisión | 100% antes de cerrar |
| Bloqueos | Número de incidencias `Bloqueada` y días bloqueada | Dos veces por semana | Escalar cualquier bloqueo mayor a 3 días |
| Reproducibilidad | Experimentos repetibles / experimentos reportados x 100 | Por experimento | 100% de resultados publicados |
| Privacidad | Artefactos con datos identificables detectados | Por revisión | 0 en repositorio y reportes compartidos |

El porcentaje de avance nunca se calcula únicamente por código escrito. Una actividad vale como completada cuando tiene resultado verificable y evidencia.

### Actualización operativa desde la extensión de Jira

Jira es el registro operativo del proyecto. Cada vez que se trabaje en una actividad:

1. Abrir la incidencia desde la extensión de Jira usando la clave del mapa oficial, por ejemplo `ACT-01 (CITO-22)`.
2. Pasar a `En progreso` antes de modificar código o documentación.
3. Añadir en la incidencia el commit, PR, reporte o evidencia relacionada y actualizar la métrica observada.
4. Pasar a `En revisión` cuando el trabajo esté listo para comprobarse.
5. Pasar a `Hecha` únicamente después de verificar los criterios de aceptación y adjuntar la evidencia.
6. Usar `Bloqueada` si falta una dependencia, autorización de datos o revisión; describir el motivo y la siguiente acción.

La clave Jira debe aparecer en el commit o PR cuando sea posible. Si una actividad genera cambios en el repositorio, el estado de Jira se actualiza en la misma sesión de trabajo, no al final del sprint. Así el tablero refleja el estado real y no solo el avance del código.

### Estado de ejecución actual

| Incidencia | Estado recomendado | Evidencia |
|---|---|---|
| `J-06` / `ACT-21` / `CITO-42` | `En revisión` | `src/dog_filter.py`, `tests/test_dog_filter.py`, `python -m unittest discover -s tests -v` |
| `J-08` / `ACT-02` / `CITO-23` | `En curso` | `data/results/CITO-23-metricas-template.csv`, `data/results/CITO-23-metricas-resumen.txt`, `python calcular_metricas_cito23.py`; métricas espaciales aún no aprobadas |

La corrección convierte los gaussianos a `float32` antes de restarlos, evitando que `uint8` recorte las diferencias negativas. La suite actual pasa y `git diff --check` no reporta errores. La incidencia no debe pasar a `Hecha` hasta que se revisen los criterios de aceptación en Jira y se adjunte esta evidencia.

## 5. Plan por fases de la guía maestra

### Fase 0. Línea base del prototipo

**Objetivo:** conocer exactamente qué existe antes de ampliarlo.

- Ejecutar la prueba de entorno y el flujo CLI/Streamlit.
- Inventariar módulos, entradas, salidas, parámetros y limitaciones.
- Registrar dataset disponible y archivos huérfanos.
- Crear una captura o reporte de resultados iniciales.

**Jira relacionado:** `J-17`, `J-20`, `ACT-13 (CITO-34)`, `ACT-15 (CITO-36)`.

**Salida:** registro de línea base aprobado. Esta fase no altera la historia ni las métricas obtenidas previamente.

### Fase 1. Planificación y UX/UI

**Objetivo:** definir usuarios, alcance y uso responsable antes de ampliar la interfaz.

- **Personas:** operador de laboratorio/citotecnólogo, revisor clínico, investigador y administrador técnico.
- **Necesidades:** cargar una imagen autorizada, revisar detecciones, consultar parámetros, exportar resultados y distinguir claramente un resultado experimental de un diagnóstico.
- **Dispositivos:** estación de trabajo de laboratorio para la versión 1.0; el uso móvil queda fuera del alcance inicial.
- **Versión 1.0:** CLI, dashboard local, procesamiento reproducible, resultados trazables, métricas y documentación.
- **Después de 1.0:** multiusuario, integración clínica, DICOM/FHIR, despliegue público y automatización de decisiones.
- **Wireflows mínimos:** carga/análisis, revisión de resultados, exportación y consulta histórica.
- **Prototipo visual:** conservar Streamlit como prototipo funcional y documentar el diseño; no iniciar una migración a Next.js sin una decisión de alcance en Jira.

**Jira relacionado:** `J-01`, `J-10`, `J-13`, `J-21`, `ACT-03 (CITO-24)`, `ACT-05 (CITO-26)`, `ACT-17 (CITO-38)`, `ACT-18 (CITO-39)`.

**Puerta de salida:** alcance aprobado, advertencia de no diagnóstico, wireflows documentados y criterios de usabilidad definidos.

### Fase 2. Arquitectura del sistema

**Objetivo:** describir la arquitectura actual y la arquitectura objetivo sin imponer tecnologías que el prototipo todavía no necesita.

**C4 - Contexto:**

- Usuario de laboratorio/revisor: aporta imágenes autorizadas y revisa resultados.
- CitoCounter: preprocesa, ejecuta DoG, analiza objetos y genera resultados explicables.
- Dataset/almacenamiento: conserva imágenes autorizadas, anotaciones, parámetros y resultados.
- Jira/GitHub: proporciona trazabilidad de tareas, código y evidencias.
- APIs clínicas externas: fuera de la versión 1.0; cualquier integración futura requiere revisión de privacidad y seguridad.

**C4 - Contenedores actuales y objetivo:**

1. Aplicación Python de línea de comandos (`main.py`).
2. Dashboard Streamlit (`app.py`).
3. Librerías del pipeline (`src/`).
4. Dataset y resultados (`CitoDataset_v1/`, `data/`).
5. Bitácora y documentación (`docs/`).
6. API REST versionada, prevista en `J-11`, únicamente cuando el contrato del pipeline esté estable.
7. Almacenamiento analítico previsto en `J-14`; PostgreSQL/ORM son una decisión de la futura plataforma, no un requisito para fingir que el prototipo ya los usa.

**Componentes a documentar:** carga y validación, preprocesamiento, DoG, detección, clasificación, métricas, persistencia, visualización y auditoría.

**Jira relacionado:** `J-11`, `J-14`, `J-17`, `J-20`, `ACT-09 (CITO-30)`, `ACT-13 (CITO-34)`, `ACT-14 (CITO-35)`.

**Puerta de salida:** diagrama C4, contrato de datos, decisiones tecnológicas y dependencias documentadas.

### Fase 3. Seguridad y modelado de amenazas

**Objetivo:** reducir riesgos antes de exponer cargas, resultados o datos.

- **OWASP:** validar extensión, tamaño y contenido; evitar rutas arbitrarias y nombres identificables; controlar temporales; no mostrar trazas al usuario; gestionar secretos fuera del repositorio.
- **STRIDE:** suplantación de usuario, manipulación de imágenes/resultados, repudio por falta de auditoría, exposición de datos, denegación de servicio por cargas grandes y elevación de privilegios.
- **Controles:** autenticación y autorización cuando exista acceso multiusuario, rate limiting en API, logs sin datos sensibles, eliminación definida y revisión de dependencias.
- **Privacidad:** inventario, anonimización, retención, eliminación y control de acceso conforme a la matriz aprobada.

**Jira relacionado:** `J-02`, `J-12`, `J-17`, `J-20`, `ACT-16 (CITO-37)`.

**Puerta de salida:** matriz STRIDE, checklist OWASP, política de datos y pruebas de abuso. Hasta entonces, el dashboard permanece local o en un entorno controlado.

### Fase 4. Backend, lógica y datos

**Objetivo:** estabilizar el motor científico y exponerlo mediante contratos verificables.

1. Completar dataset, splits y doble revisión: `J-03`, `J-04`, `ACT-19 (CITO-40)`, `ACT-20 (CITO-41)`.
2. Corregir y probar la representación numérica del DoG: `J-06`, `ACT-21 (CITO-42)`.
3. Calibrar parámetros en un conjunto separado: `J-07`, `ACT-01 (CITO-22)`.
4. Implementar métricas precisión, sensibilidad, F1 e IoU: `J-08`, `ACT-02 (CITO-23)`.
5. Comparar contra Otsu y línea base: `J-09`.
6. Formalizar reglas explicables: `J-10`, `ACT-03 (CITO-24)`.
7. Implementar API REST versionada y validación de entradas: `J-11`, `ACT-04 (CITO-25)`.
8. Diseñar almacenamiento trazable: `J-14`, `ACT-09 (CITO-30)`.

La guía de arquitectura propone PostgreSQL, Prisma y NestJS como ejemplo. Para este repositorio se adopta una migración incremental: primero se estabiliza el pipeline Python y luego se decide si la API y el almacenamiento se implementan con FastAPI/PostgreSQL u otro stack aprobado. No se considera cumplida una actividad por crear carpetas vacías o modelos sin uso.

Si la API evoluciona a un servicio multiusuario, esta fase debe añadir login, contraseñas con bcrypt, JWT, guards/RBAC y DTOs de validación. Esas capacidades se trazan a `J-12` y a los criterios de seguridad; no se habilita acceso multiusuario solo por tener un endpoint funcionando.

La validación formal de F1, precisión, sensibilidad e IoU se ejecuta sobre el conjunto congelado mediante `J-18` y `ACT-10 (CITO-31)`. Los casos de superposición, artefactos e iluminación se analizan mediante `J-19`, `ACT-11 (CITO-32)` y `ACT-12 (CITO-33)` antes de cerrar la evaluación.

**Puerta de salida:** API probada, resultados con versión de código/dataset/parámetros y validación científica reproducible.

### Fase 5. Frontend e interfaz

**Objetivo:** convertir el dashboard actual en un flujo claro para revisión humana.

- Mostrar carga, procesamiento, éxito y error con mensajes accionables.
- Mostrar imagen, detecciones, parámetros, métricas e incertidumbre sin presentar diagnóstico.
- Permitir exportación trazable del resultado.
- Probar accesibilidad básica, tamaños de pantalla de estación de trabajo y flujo de revisión.
- Consumir la API mediante un cliente definido por el equipo (por ejemplo Axios y React Query si se separa el frontend), gestionando carga, error y reintento.
- Proteger vistas y acciones mediante rutas protegidas cuando requieran sesión o rol; en la versión local, documentar explícitamente que no existe autenticación.
- Usar componentes reutilizables si se migra a un frontend separado; la migración a Next.js/Tailwind queda condicionada a `J-11` y a una decisión registrada.
- Ejecutar pruebas con usuarios potenciales, sin usar datos identificables.

**Jira relacionado:** `J-13`, `J-15`, `J-21`, `ACT-05 (CITO-26)`, `ACT-06 (CITO-27)`, `ACT-07 (CITO-28)`, `ACT-08 (CITO-29)`, `ACT-17 (CITO-38)`, `ACT-18 (CITO-39)`.

**Puerta de salida:** flujo funcional probado, advertencias visibles, exportación correcta y feedback registrado.

### Fase 6. Infraestructura y despliegue

**Objetivo:** hacer reproducible el entorno sin desplegar prematuramente datos sensibles.

- **Docker:** empaquetar solo cuando API, almacenamiento y configuración estén definidos; incluir healthcheck y configuración por variables de entorno.
- **CI:** ejecutar sintaxis, pruebas, lint, validación de dataset y revisión de secretos en cada pull request mediante GitHub Actions.
- **Servidor:** AWS EC2 es una opción posterior. Antes se debe aprobar modelo de amenaza, HTTPS, control de acceso, copias, retención y monitoreo; solo deben abrirse los puertos necesarios para HTTPS y administración segura.
- **Entrega:** congelar versión de código, dataset, parámetros, dependencias, reportes y documentación.

**Jira relacionado:** `J-12`, `J-16`, `J-17`, `J-20`, `ACT-15 (CITO-36)`, `ACT-16 (CITO-37)`, `ACT-22 (CITO-43)`.

**Puerta de salida:** paquete reproducible, informe de rendimiento, documentación completa y acta de aceptación. El despliegue público no es criterio de éxito de la versión de investigación.

## 6. Puertas de control y orden de ejecución

El orden mínimo es:

`Línea base -> Fase 1 -> Fase 2 -> Fase 3 -> dataset/DoG -> métricas/calibración -> API -> interfaz -> CI/despliegue -> entrega`

No se debe declarar `J-18` (F1 >= 90 %) ni `J-16` (reducción de tiempo >= 70 %) como cumplido antes de congelar el dataset de prueba y el protocolo de medición. Son metas experimentales, no resultados garantizados.

| Puerta | Se habilita cuando | Incidencias clave |
|---|---|---|
| G0 Línea base | El prototipo corre y sus límites están registrados | `J-17`, `J-20` |
| G1 Alcance | Usuarios, alcance y riesgos de datos están aprobados | `J-01`, `J-02` |
| G2 Datos | Dataset autorizado, anotado y consistente | `J-03`, `J-04`, `J-05` |
| G3 Algoritmo | DoG corregido y parámetros congelados para evaluación | `J-06`, `J-07`, `J-19` |
| G4 Evidencia científica | Métricas y comparación reproducibles | `J-08`, `J-09`, `J-18` |
| G5 Producto de investigación | API, interfaz, seguridad y almacenamiento probados | `J-10` a `J-15`, `J-21` |
| G6 Entrega | Rendimiento, documentación y auditoría completos | `J-16`, `J-17`, `J-20` |

## 7. Rutina de seguimiento

**Cada inicio de semana:** revisar tablero, dependencias, capacidad y bloqueos; elegir actividades con criterios de aceptación claros.

**Durante la semana:** actualizar estado de Jira, enlazar commits/PR, registrar experimentos y anotar el valor de las métricas con su versión de dataset.

**Cada revisión semanal:** verificar avance ponderado, trazabilidad, riesgos, desviaciones y decisiones. Una métrica que no se pueda reproducir se registra como pendiente, no como éxito.

**Al cerrar una actividad:** adjuntar evidencia, solicitar revisión, comprobar criterios de aceptación y vincular el resultado con la tarea padre.

**Al final de cada fase:** completar la puerta de control correspondiente y registrar la decisión en Jira: aprobada, aprobada con riesgo o bloqueada.

## 8. Definición de terminado adaptada

Una tarea o actividad se puede mover a `Hecha` solo si:

- Cumple sus criterios de aceptación.
- Tiene evidencia enlazada y reproducible.
- Incluye pruebas automatizadas o una prueba manual documentada según su riesgo.
- Registra código, dataset, parámetros, entorno, fecha y operador cuando aplique.
- Fue revisada por otra persona.
- No introduce datos identificables en el repositorio.
- Actualiza la documentación afectada.
- Distingue resultados experimentales de diagnóstico clínico.
- Deja registrados los riesgos residuales y las tareas derivadas.

## 9. Indicadores científicos y de producto

Los indicadores se separan para no confundir avance del proyecto con rendimiento del algoritmo:

- **Algoritmo:** precisión, sensibilidad, F1, IoU, falsos positivos, falsos negativos y análisis por casos especiales.
- **Datos:** número de imágenes por split, porcentaje con anotación válida, concordancia entre revisores y archivos huérfanos.
- **Producto:** tiempo manual vs. automatizado, errores de carga, tiempo de respuesta, tareas completadas por usuario y problemas de usabilidad.
- **Gobierno:** incidencias de privacidad, hallazgos de seguridad, cobertura de evidencia y bloqueos.

Cada informe debe indicar fórmula, denominador, conjunto evaluado, versión y fecha. El resultado `F1 >= 90%` se reporta solo si el conjunto de prueba es independiente y congelado.

## 10. Documentos y archivos de apoyo

- [Plan normativo y backlog Jira](plan-proyecto.md)
- [Guía de inicio](guide/inicio.md)
- [Guía de experimentación](guide/experimentos.md)
- [Guía de desarrollo](guide/desarrollo.md)
