# CITO-99: Mapa de componentes y contratos de integración

**Proyecto:** CitoCounter-Proto
**Rama de trabajo:** `MIGRACION`
**Propósito:** documentar la línea base implementada y los cambios mínimos para integrar un motor DL en las superficies existentes, sin reconstruir ni duplicar capacidades.
**Alcance:** inspección estática del código y las pruebas existentes; no se modificó el pipeline ni se afirma que la suite se haya ejecutado en esta actividad.

## 1. Resumen de arquitectura observada

El pipeline DoG funciona, pero su orquestación está repetida en los puntos de entrada. `main.py`, `app.py` y `api_v1.py` llaman directamente a preprocesamiento, DoG y análisis. Existe un contrato abstracto de segmentación en `src/contracts/pipeline_contract.py`, pero el flujo DoG actual no lo implementa ni es consumido por esos puntos de entrada.

Para incorporar motores sin divergencia entre interfaces, la ruta mínima recomendada es:

1. Conservar `preprocesamiento`, DoG, `analizar_nucleos` y las reglas CITO-77.
2. Añadir adaptadores para exponer DoG y el candidato DL mediante el contrato existente.
3. Centralizar la selección/configuración del motor en una única capa de aplicación dentro de `src/`; CLI, Streamlit y API delegan en ella.
4. Mantener los formatos de salida actuales de cada superficie mediante adaptaciones en sus bordes, no mediante una segunda implementación del análisis.
5. Reutilizar la persistencia, el historial y los reportes actuales; añadir solo los metadatos de motor/modelo que falten para trazabilidad.

```text
CLI main.py ─────┐
Streamlit app.py ├──> servicio común en src/ ──> adaptador DoG o adaptador DL
API v1 ──────────┘                               └──> contrato existente
                                                      └──> clasificación CITO-77
                                                          └──> resultado compartido
Interfaces/reportes <── almacenamiento, historial y métricas existentes
```

La capa de aplicación común es una extensión justificada: hoy los tres puntos de entrada repiten la orquestación DoG. No se debe trasladar lógica de UI o HTTP a `src/`, ni crear otra implementación de reglas, almacenamiento o indicadores.

## 2. Matriz actual → extensión mínima → pruebas

| Componente | Implementado y evidencia en código | Extensión mínima para migración | Pruebas existentes / cobertura que falta |
|---|---|---|---|
| **Preprocesamiento + DoG** | `src/preprocessing.py` prepara la imagen; `src/dog_filter.py` implementa DoG; `src/analysis.py` analiza contornos. `main.py`, `app.py` y `api_v1.py` llaman estas funciones. | Envolver el flujo DoG existente como motor compatible con el contrato. Mantener DoG como valor por defecto y fallback; no reescribir filtros ni calibración. | `tests/test_dog_filter.py`, `tests/test_analysis_rules.py`, `tests/test_cito90_hsv.py`, `tests/test_cito91_lotes.py`. Añadir prueba de contrato y paridad del motor DoG antes/después de centralizar. |
| **Contrato de segmentación** | `src/contracts/pipeline_contract.py` define `ParametrosAnalisis`, `ResultadoSegmentacion`, `AlgoritmoSegmentacionBase.procesar()` y `validar_tamano_imagen()`. | Usar estas definiciones para los adaptadores. Revisar la forma de representar múltiples contornos y clases: `ResultadoSegmentacion.mapa_contornos` es un `np.ndarray` opcional y no expone directamente las listas/estadísticas del resultado actual. Resolver esa traducción sin crear un contrato competidor. | No se encontró una prueba dedicada al contrato/adaptador en `tests/`. Agregar pruebas para implementación, salida vacía, errores, dimensiones y equivalencia con el resultado DoG legado. |
| **Análisis y reglas CITO-77** | `src/analysis.py` contiene `analizar_nucleos()`, `obtener_reglas_clasificacion()` y `clasificar_nucleo_por_area()`. La clasificación contempla áreas, polaridad y zona frontera. | Mantener una única implementación de clasificación. El adaptador DL debe entregar las áreas/contornos compatibles y pasar por las reglas actuales; no copiar umbrales al modelo ni recalibrarlos en esta integración. | `tests/test_cito77_reglas.py`, `tests/test_analysis_rules.py`. Añadir integración que pase resultados del adaptador por las reglas y conserve casos frontera. |
| **CLI** | `main.py` procesa imagen/lote y expone parámetros DoG, polaridad, ruido, contraste, GUI y bitácora; genera visualización y puede registrar resultados. La orquestación es directa, no usa el contrato. En `procesar_una_imagen()`, `analizar_nucleos()` recibe actualmente polaridad fija `'nucleos-claros'` aunque el preprocesamiento recibe `args.polaridad`. | Añadir `--motor dog|dl` con `dog` como default. Delegar en la capa común y conservar flags, paneles, lotes y bitácora. Al integrar, cubrir explícitamente la polaridad que llega al analizador; no alterar silenciosamente el modo legado. | `tests/test_cito91_lotes.py` cubre lotes, pero no se identificó un test CLI para parser, selección de motor o compatibilidad de opciones. Añadir pruebas CLI: default DoG, motor DL explícito/no disponible, sigma/polaridad y lote. |
| **Streamlit** | `app.py` dispone de controles de procesamiento, carga, visualización, historial, métricas y exportación. `procesar_imagen_individual()` ejecuta preprocesamiento → DoG → análisis directamente; el límite de carga declarado es 10 MiB. | Añadir selector de motor que llame al servicio común. Conservar flujos de carga, estados, avisos, calidad, contornos y exportaciones. Mantener visible el error si DL no está instalado; DoG sigue disponible. | `tests/test_interfaz_resultados.py`, `tests/test_privacy.py`, `tests/test_historial_resultados.py`. No se identificó prueba de paridad de la UI con el pipeline. Añadir pruebas de la capa de parámetros/servicio y smoke/paridad con fixtures, evitando depender de una sesión interactiva de Streamlit. |
| **API REST v1** | `api_v1.py` expone salud, autenticación y análisis. Valida payload, rutas autorizadas, contenido/tamaño de imagen, autorización por rol y límite de solicitudes; la ruta de análisis llama directamente a DoG y devuelve contadores agregados. | Añadir campo opcional `engine` con whitelist `dog|dl`; default `dog`. Delegar al servicio común y mapear la salida al JSON v1 existente. Preservar autenticación/autorización antes del análisis, límites, auditoría y esquema de errores. | `tests/test_api_v1.py` cubre validación y HTTP. Añadir casos de whitelist, default DoG, DL disponible/no disponible, respuesta compatible, autenticación/rol/rate limit sin regresiones. |
| **Historial** | `src/historial_resultados.py` lee `bitacora_experimentos.csv`, normaliza campos de ejecuciones `T-` y agrega conteos/riesgo histórico. `app.py` lo presenta. | Reutilizarlo. Si las ejecuciones DL se registran en la bitácora, extender el esquema de manera compatible para motor/modelo/versión; lectores antiguos deben seguir aceptando filas actuales. | `tests/test_historial_resultados.py`. Añadir compatibilidad de lectura de filas históricas y nuevas columnas opcionales. |
| **Almacenamiento** | `src/almacenamiento.py` implementa persistencia SQLite, CRUD y exportación. El esquema registra imagen, sigma, polaridad, conteos y observaciones, pero no campos explícitos de motor, identificador/versión de modelo ni pesos. | Extender el almacenamiento existente solo para metadatos de trazabilidad del motor/modelo, con migración compatible de SQLite. No crear una segunda base de datos ni persistencia en la UI. | `tests/test_almacenamiento.py`. Añadir prueba de migración desde esquema anterior, alta/consulta/exportación de motor y modelo; conservar CRUD existente. |
| **Esquema de resultado/trazabilidad** | `src/result_schema.py` declara `ResultadoNucleo`, `MetricasResumen`, versiones y `MetadatosTrazabilidad`; la versión de modelo y dataset por defecto son constantes. | Ampliar el esquema de forma aditiva para distinguir motor, modelo/pesos y versión del pipeline, evitando que el campo `modelo_version` represente ambiguamente DoG y DL. Sin modificar resultados históricos ya serializados. | No se identificó un archivo de pruebas dedicado a `result_schema.py`. Agregar validación de campos existentes y nuevos, con compatibilidad de registros previos. |
| **Métricas de sistema e historial** | `src/metricas_sistema.py` calcula indicadores resumidos de las ejecuciones; se consume desde Streamlit y ETL. Estos KPI son descriptivos y no son métricas espaciales de validación del detector. | Reutilizar para los dashboards. Mantener separados los KPI históricos de precision/recall/F1/IoU contra ground truth; no cambiar su significado para presentar resultados DL. | `tests/test_metricas_sistema.py`, `tests/test_historial_resultados.py`. Añadir caso de agregación/filtrado por motor solo si se requiere comparación en dashboard. |
| **ETL y exportaciones** | `src/etl_resultados.py` extrae bitácora, transforma, agrega y exporta CSV/JSON; el dashboard también produce resultados/exportaciones. | Extender el esquema de transformación para incluir los metadatos nuevos sin romper CSV/JSON actuales. Reutilizar exportadores. | `tests/test_etl_resultados.py`, `tests/test_interfaz_resultados.py`. Añadir fixture antiguo y nuevo, verificar encabezados y campos opcionales. |
| **Métricas de detección** | Hay utilidades CITO-23/CITO-75 para matching, precision, recall, F1 e IoU, además de evaluación de datos sintéticos. Esto es distinto de `metricas_sistema.py`. | Usar el evaluador espacial existente con el mismo protocolo para DoG y DL; no duplicar métricas en el motor ni usar test para seleccionar. | `tests/test_cito23_metrics.py`, `tests/test_cito75_metrics.py`, `tests/test_validar_metricas_cito23.py`. Falta validar que el formato de GT Herlev auditado se conecte al protocolo antes de reportar cifras. |

## 3. Contratos y diferencias que hay que resolver

### Entrada del motor

El contrato existente define `ParametrosAnalisis` con sigma, umbral, polaridad y tamaño máximo, mientras que los puntos de entrada tienen parámetros adicionales (ruido, CLAHE, HSV y separación). Antes de ampliar el objeto, acordar qué parámetros pertenecen al preprocesamiento común y cuáles son específicos de cada motor. Evitar meter opciones de interfaz dentro del contrato de segmentación.

### Salida del motor

`analizar_nucleos()` retorna un diccionario rico con `total_celulas`, `normales`, `sospechosas`, `porcentaje_riesgo`, `areas`, contornos e imagen anotada. `ResultadoSegmentacion` actualmente ofrece `exitoso`, `total_nucleos`, `mapa_contornos`, `metricas_detalle` y `errores`. El adaptador debe traducir de forma explícita entre ambos y conservar las claves públicas ya consumidas por CLI/Streamlit/API. Evitar almacenar imágenes anotadas como si fueran contornos o métricas.

### Persistencia/trazabilidad

El almacenamiento SQLite, la bitácora CSV y `result_schema.py` no comparten hoy un campo canónico de motor/modelo. Decidir un conjunto mínimo y aditivo de metadatos (por ejemplo motor, modelo, versión/hash de pesos y versión de pipeline), actualizar lectores/exportadores y comprobar registros antiguos. No etiquetar inferencia DL como modelo `v1.0.0` de forma ambigua.

### Políticas de carga

La interfaz Streamlit define `MAX_UPLOAD_BYTES = 10 MiB`; la evidencia de API v1 documenta límite de archivo y cuerpo de 64 KiB. La CLI procesa rutas locales mediante sus propias funciones. La integración no debe asumir que estos límites son iguales ni reemplazarlos globalmente sin una decisión de alcance y pruebas por superficie.

## 4. Secuencia mínima de integración

1. **Contrato y fixtures:** crear pruebas de contrato para las salidas DoG actuales y cerrar el mapeo de campos requerido por los consumidores.
2. **Servicio común/adaptador DoG:** encapsular la orquestación repetida sin cambiar resultados, valores por defecto, mensajes ni formatos públicos.
3. **Regresión de superficies:** conectar primero CLI, Streamlit y API al servicio DoG común; ejecutar pruebas y comparar resultados fijos con la línea base.
4. **Adaptador DL opcional:** implementar el contrato seleccionado usando las mismas salidas de aplicación; reportar errores explícitos si el modelo/dependencia no está disponible.
5. **Persistencia aditiva:** guardar la identidad del motor/modelo mediante los módulos existentes y probar lectura/exportación de datos anteriores.
6. **Selección DL por superficie:** añadir las opciones CLI/UI/API con defaults DoG y whitelist en API; preservar controles de seguridad actuales.
7. **Comparación científica:** conectar los resultados al evaluador espacial existente y solo usar GT validado con validation/test separados.

## 5. Criterios de aceptación para el mapa

- Cada capacidad existente tiene ubicación, contrato, consumidor y pruebas localizables.
- Las diferencias entre contrato abstracto y resultados actuales están documentadas antes de definir el adaptador DL.
- No se crea una segunda implementación de DoG, CITO-77, historial, SQLite, ETL o KPI de sistema.
- El cambio de motor puede centralizarse sin que CLI, Streamlit y API diverjan.
- La integración preserva defaults/formatos actuales y añade pruebas en las brechas identificadas.
- Las métricas de sistema se distinguen expresamente de las métricas espaciales de detección.

## 6. Referencias inspeccionadas

- [Contrato del pipeline](../src/contracts/pipeline_contract.py)
- [Preprocesamiento](../src/preprocessing.py)
- [Filtro DoG](../src/dog_filter.py)
- [Análisis y reglas CITO-77](../src/analysis.py)
- [CLI](../main.py)
- [Dashboard Streamlit](../app.py)
- [API v1](../api_v1.py)
- [Esquema de resultados](../src/result_schema.py)
- [Almacenamiento SQLite](../src/almacenamiento.py)
- [Historial](../src/historial_resultados.py)
- [Métricas de sistema](../src/metricas_sistema.py)
- [ETL de resultados](../src/etl_resultados.py)
- [Pruebas de API](../tests/test_api_v1.py)
- [Pruebas de reglas CITO-77](../tests/test_cito77_reglas.py)
- [Pruebas de almacenamiento](../tests/test_almacenamiento.py)
- [Pruebas de historial](../tests/test_historial_resultados.py)
- [Pruebas de métricas del sistema](../tests/test_metricas_sistema.py)
- [Pruebas de ETL](../tests/test_etl_resultados.py)
- [Pruebas de métricas espaciales](../tests/test_cito23_metrics.py), [CITO-75](../tests/test_cito75_metrics.py)
