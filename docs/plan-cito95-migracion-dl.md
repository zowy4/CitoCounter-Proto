# Plan CITO-95: Integración incremental de Deep Learning y actualización de CitoCounter

**Actualizado:** 2026-10-28
**Propósito:** evolucionar el prototipo existente integrando un motor de segmentación DL evaluado y actualizando sus superficies actuales (CLI, Streamlit y API); mantener DoG como motor de referencia y añadir Qt/PySide6 solo como una nueva interfaz reutilizando la lógica existente.
**Límite:** CitoCounter-Proto continúa siendo un prototipo de investigación, no un dispositivo médico ni una herramienta diagnóstica. F1 ≥ 90 % es una meta experimental, no un resultado garantizado ni un criterio de validación clínica.

## 1. Enfoque: integrar y actualizar, no reconstruir

El trabajo parte del código que ya existe. Las actividades Jira deben cerrar brechas y conectar componentes, no volver a implementar funcionalidades disponibles.

| Capacidad existente que se conserva | Referencia en el proyecto | Tratamiento en CITO-95 |
|---|---|---|
| Preprocesamiento y pipeline DoG | `src/preprocessing.py`, `src/dog_filter.py`, `src/analysis.py`, `main.py` | Mantener como baseline y fallback. Añadir una selección de motor compatible, sin cambiar el comportamiento DoG predeterminado. |
| Contrato de algoritmos | `src/contracts/pipeline_contract.py` | Reutilizar `AlgoritmoSegmentacionBase`, `ParametrosAnalisis` y `ResultadoSegmentacion`; no crear otro contrato paralelo. |
| Reglas explicables de clasificación | `src/analysis.py`, pruebas CITO-77 | Aplicar las reglas existentes a las salidas DL; no duplicar ni recalibrar reglas como parte de la integración. |
| Interfaz local | `app.py`, `src/interfaz_resultados.py` | Actualizar con un selector de motor conservando flujos, avisos y exportaciones actuales. |
| API v1 | `api_v1.py` | Extender el contrato de análisis con un motor opcional; conservar autenticación, límites y validación actuales. |
| Historial, almacenamiento, reportes y métricas del sistema | `src/historial_resultados.py`, `src/almacenamiento.py`, `src/etl_resultados.py`, `src/metricas_sistema.py` | Reutilizar módulos en UI/Qt; evitar persistencias o KPI duplicados. |
| Evidencia sintética y pruebas existentes | `tests/`, `data/sintetico/` | Conservar como smoke tests; no presentar las métricas sintéticas como rendimiento en imágenes reales. |
| Datos y salidas Herlev locales | `data/raw/im_Dyskeratotic/`, `data/ground_truth/herlev/` | El checkout revisado tiene 223 BMP, 1.626 `.dat`, 223 CSV de células, 223 máscaras y tres manifiestos locales. Estos artefactos requieren trazabilidad y auditoría; no sustituirlos ni sobrescribirlos a ciegas. |

### Estado que debe verificarse antes de cerrar tareas

En el checkout revisado, `src/herlev_dataset.py`, `src/herlev_evaluation.py`, `preparar_herlev.py`, `evaluar_herlev.py` y sus dos pruebas existen como archivos vacíos. Los artefactos bajo `data/ground_truth/herlev/` son locales y no están bajo seguimiento de Git. Por tanto:

- No dar por terminada la preparación del ground truth porque existan archivos generados.
- Antes de regenerar, inventariar entradas, salidas y hashes; preservar las salidas existentes.
- Completar y probar la generación determinista desde `.dat` hasta máscaras, CSV y manifiestos.
- Validar visualmente correspondencia entre anotaciones, imagen y máscara antes de calcular o publicar métricas.
- No versionar imágenes originales ni anotaciones brutas; respetar `.gitignore` y las restricciones del dataset.

## 2. Alcance y criterios de integración

1. **Compatibilidad:** `dog` continúa como motor predeterminado. Un modelo opcional o no instalado no debe impedir importar ni usar el pipeline DoG.
2. **Una única lógica de negocio:** CLI, Streamlit, API y Qt delegan en `src/`; ninguna interfaz implementa su propio algoritmo.
3. **Contrato común:** el adaptador DL usa los contratos existentes y entrega resultados que las reglas, visualización, almacenamiento y métricas ya puedan consumir.
4. **Evaluación comparable:** DoG, Cellpose y StarDist usan las mismas imágenes, anotaciones, protocolo de emparejamiento y cálculo de métricas.
5. **Separación de datos:** validation sirve para comparar y elegir; test queda congelado y se ejecuta una sola vez cuando modelo y parámetros estén fijados.
6. **Trazabilidad:** registrar commit/versión, hash del manifiesto, dataset, modelo/pesos, dependencias, parámetros, fecha, dispositivo, semillas, exclusiones y limitaciones.
7. **Seguridad y límites:** conservar controles actuales de carga, autenticación, autorización, límites de procesamiento y privacidad. Acordar límites compatibles con imágenes reales antes de integrar modelos; no introducir silenciosamente un límite incompatible con el dataset.
8. **Migración gradual:** no retirar DoG, Streamlit ni la API existente. Qt es una interfaz adicional, no un reemplazo que bloquee la validación del motor.

## 3. Actividades Jira y ruta de trabajo

La lista importable completa y sus dependencias están en [JIRA_IMPORT_CITO95_DL.csv](./JIRA_IMPORT_CITO95_DL.csv). Al importar, se deben crear las actividades como subtareas de la épica E9 y conservar la referencia `J-xx`; las claves reales CITO asignadas por Jira deben añadirse al mapa después de la importación.

### Fase A — Preservar y entender la línea base (J-40–J-42)

- **J-40:** inventariar rama, estado Git, cambios locales y artefactos; proteger cualquier trabajo sin seguimiento antes de modificarlo.
- **J-41:** mapear componentes implementados y contratos para identificar las extensiones mínimas por interfaz.
- **J-42:** documentar procedencia, cobertura, estructura y restricciones del Herlev local.

**Salida:** alcance de actualización confirmado, sin duplicar funciones existentes ni perder artefactos locales.

### Fase B — Ground truth reproducible y auditado (J-43–J-50)

- **J-43–J-47:** completar lector de polígonos, rasterizado, conversión al esquema CSV existente, splits por grupo sin fuga y CLI determinista. Reproducir en una ubicación temporal y comparar hashes; no sobrescribir la salida local hasta validar diferencias.
- **J-48:** auditar una muestra de imágenes completas y cobertura de anotaciones; documentar que el repositorio solo contiene `im_Dyskeratotic` y que no representa las clases Herlev ausentes.
- **J-49:** ampliar el validador del dataset con pruebas de integridad para máscaras, coordenadas, CSV y manifiestos.
- **J-50:** adaptar/reutilizar el evaluador y probar el protocolo de métricas con fixtures conocidos antes de medir rendimiento.

**Salida:** conjunto de evaluación versionado por manifiesto, generado de forma determinista, con auditoría y exclusiones documentadas.

### Fase C — Baseline DoG y prueba de candidatos (J-51–J-55)

- **J-51:** congelar parámetros y medir el baseline DoG únicamente después de validar el ground truth.
- **J-52:** instalar dependencias DL en un entorno separado; no alterar dependencias base ni descomentar paquetes masivos en `requirements.txt`.
- **J-53–J-54:** evaluar Cellpose y StarDist zero-shot **sobre validation**, no sobre test.
- **J-55:** comparar resultados con el mismo protocolo y decidir si procede fine-tuning, otro candidato o detener la ruta DL por evidencia insuficiente.

**Salida:** decisión documentada y comparable. Si no se puede validar la correspondencia espacial del GT, detener la evaluación DL y resolver la calidad de datos primero.

### Fase D — Modelo e integración del pipeline existente (J-56–J-67)

- **J-56–J-57:** implementar adaptador y carga/configuración versionada del modelo elegido mediante los contratos existentes.
- **J-58–J-60:** solo si los resultados justifican entrenamiento: generar parches desde train, entrenar usando validation y variar un hiperparámetro por vez.
- **J-61:** ejecutar evaluación final en test una vez, con modelo y configuración congelados; si no alcanza la meta, reportar el resultado y limitaciones honestamente.
- **J-62:** documentar falsos positivos/negativos y límites del dataset.
- **J-63–J-66:** integrar el motor en CLI, Streamlit y API y pasar las áreas por las reglas CITO-77 existentes.
- **J-67:** ejecutar regresión de compatibilidad; verificar que el modo DoG, autenticación, límites, formatos y resultados existentes no cambien inadvertidamente.

**Salida:** DL optativo detrás de una selección explícita, con DoG funcional como fallback y comportamiento coherente entre interfaces.

### Fase E — Qt como interfaz adicional (J-68–J-73)

Esta fase no bloquea la validación científica ni justifica duplicar el pipeline.

- **J-68–J-71:** crear esqueleto, visor, controles y dashboard Qt consumiendo `src/` y módulos de historial/métricas existentes.
- **J-72:** probar paridad sobre fixtures compartidos; Streamlit y CLI continúan como referencias existentes.
- **J-73:** empaquetar solo después de comprobar el modo offline, dependencias, carga segura de modelos y avisos de uso experimental.

**Salida:** interfaz adicional reproducible que consume las capacidades existentes.

### Fase F — Evidencia, documentación y entrega (J-74–J-77)

- **J-74–J-75:** publicar reporte y gráficas reproducibles que identifiquen claramente validation/test, DoG/DL, clases disponibles y limitaciones.
- **J-76:** actualizar README y plan del proyecto con enlaces y estado real, sin copiar contenido entre documentos.
- **J-77:** preparar PR con commits convencionales, evidencia, pruebas y revisión; no hacer merge automático ni ignorar desfases de la rama de destino.

## 4. Reglas para los datos y la evaluación

- Los splits se asignan por imagen/grupo de origen; crops o anotaciones relacionadas nunca pueden quedar en splits distintos.
- Como el checkout solo contiene una clase fuente (`im_Dyskeratotic`), los splits actuales no pueden considerarse estratificados por las siete clases de Herlev.
- El conjunto de test no se usa para selección de modelo, umbrales, hiperparámetros ni iteraciones de rasterizado.
- Reportar número de imágenes y núcleos, clases disponibles, datos excluidos, versión del protocolo y resultados por imagen; evitar generalizar desde una clase.
- Un F1 sintético o un resultado sobre una sola categoría no es validación clínica ni prueba de desempeño poblacional.

## 5. Criterios de aceptación global

- El ground truth puede reconstruirse desde entradas permitidas con hashes estables, manifiestos sin solapamiento y validación automatizada.
- Las anotaciones/máscaras pasan auditoría visual documentada y el protocolo de matching tiene pruebas de regresión.
- El baseline DoG y cualquier candidato DL comparten datos y protocolo; test permanece cerrado hasta la evaluación final.
- La integración preserva el comportamiento predeterminado DoG y reutiliza clasificación, contratos, almacenamiento y métricas existentes.
- Las superficies CLI/API/Streamlit/Qt respetan sus contratos, controles de seguridad y avisos experimentales.
- La suite dirigida y la suite de regresión del proyecto pasan; las limitaciones y resultados negativos también quedan documentados.

## 6. Fuera de alcance y guardarraíles

- No presentar CitoCounter como sistema clínico, diagnóstico o dispositivo médico.
- No incorporar pesos o descargas de modelos sin registrar origen, licencia, versión, hash y condiciones de uso.
- No subir imágenes originales, datos de pacientes, anotaciones brutas ni artefactos prohibidos por el dataset.
- No modificar en bloque `requirements.txt`; separar dependencias opcionales DL y Qt.
- No hacer una reescritura completa del pipeline ni retirar DoG/Streamlit/API como parte de esta migración.
- No asegurar F1 ≥ 90 % antes de obtener evidencia de test válida; informar la métrica observada aunque no alcance la meta.

## 7. Orden de inicio inmediato

1. Completar J-40/J-41 y preservar los artefactos locales existentes.
2. Implementar J-43/J-44 con fixtures sintéticos pequeños y casos borde; no comenzar con cambios de modelo o UI.
3. Completar J-45–J-50 y comparar una generación temporal con las salidas locales para identificar discrepancias.
4. Ejecutar J-48 antes de aceptar cualquier métrica; si hay anotaciones incompletas, dejarlo como limitación o detener baseline.
5. Congelar el baseline DoG en J-51; después instalar entorno DL y correr zero-shot en validation.
6. Integrar solo el candidato respaldado por evidencia. Qt permanece en una rama paralela y opcional.

La asignación de estados debe reflejar Jira y evidencia comprobable; tener código o salidas locales no equivale por sí mismo a actividad terminada.
