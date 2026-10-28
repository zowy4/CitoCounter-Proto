# CITO-69: Privacidad y Anonimización

**Fecha:** 2026-10-02  
**Responsable:** Zoé Andrés Chacón Zavala  
**Prioridad:** Highest  
**Estado:** En curso  
**Tipo:** Actividad Paralela (no depende de CITO-68, depende de J-01)  

---

## 1. Propósito

Definir e implementar medidas de privacidad y anonimización para proteger la identidad de pacientes en el prototipo CitoCounter-Proto, asegurando el cumplimiento de normativas de protección de datos y ética en investigación biomédica.

---

## 2. Contexto y Marco Legal

| Normativa | Relevancia | Aplicación en CitoCounter-Proto |
|-----------|------------|--------------------------------|
| **LFPDPPP** (Ley Federal de Protección de Datos Personales) | Obligatoria para datos en México | Principios de licititud, consentimiento, limitación de uso, seguridad |
| **Declaración de Helsinki** | Ética en investigación | Protección de participantes, revisión por comité ético |
| **FDA Software Guidance** | Referencia EE.UU. | Aunque no es dispositivo médico, guida buenas prácticas |
| **Normativa ISO 27701** | Gestión de privacidad | Aunque el prototipo no es un sistema formal, aplica principios |

---

## 3. Datos en el Proyecto y Riesgos

### 3.1. Tipos de Datos Manejados

| Dato | Sensibilidad | Origen | Almacenamiento |
|------|-------------|--------|----------------|
| **Nombres de archivo** (MUESTRA_001, etc.) | Baja | Metadatos | `data/raw/`, `data/dataset_index.csv` |
| **Etiquetas YOLO** (clase, coordenadas) | Baja/Media | Anotaciones | `CitoDataset_v1/labels/train/` |
| **Datos clínicos sintéticos** (edad, diagnóstico) | Media | `clinical_data_synthetic.csv` | `CitoDataset_v1/metadata/` |
| **Imágenes originales** (BMP convertidas a JPG) | Media-Alta | `data/raw/` | 211 imágenes JPG |
| **Resultados de procesamiento** | Media | Pipeline output | `data/results/` |

### 3.2. Riesgos de Privacidad

| Riesgo | Descripción | Nivel | Mitigación |
|--------|-------------|-------|------------|
| **Identificación reidentificable** | Vincular nombres de archivo con imágenes reales | Medio | Anonimización de metadatos |
| **Filtro por edad/diagnóstico** | Inferir condiciones clínicas de individuos | Medio | Agregación de datos, sin IDs individuales |
| **Filtro por resolución** | Identificar equipos de imagen específicos | Bajo | Estandarizar resolución en reportes |
| **Filtro por características nucleares** | Perfilado fenotípico sutil | Bajo | Estadísticas agregadas solo |

---

## 4. Medidas de Anonimización Implementadas

### 4.1. En Metadatos y CSV

- **`CitoDataset_v1/metadata/clinical_data_synthetic.csv`**: Corregido para incluir solo IMG_001 (validado en CITO-44)
- **`data/dataset_index.csv`**: Sin datos personales identificables, solo IDs de muestra y metadatos técnicos
- **Validación**: 5 tests unitarias passing (`tests/test_dataset_integrity.py`)

### 4.2. En Etiquetas YOLO

- **243 archivos YOLO** validados (211 MUESTRA + 20 SINTÉTICA + IMG_001 + reporte_etiquetado.txt)
- **191/243 corregidas** (79.4% clean) - warnings resueltos en `validar_etiquetado.py` y `arreglar_etiquetado.py`
- **Sin nombres de pacientes** en archivos de etiqueta - solo coordenadas y clase de núcleo

### 4.3. En Imágenes

- **Tamaño máximo 64 KiB** (validado en `validar_tamano_imagen()` - CITO-45)
- **Rutas de acceso locales solo** - `data/raw/` protegido por `.gitignore`
- **No se suben imágenes originales** a repositorio público - solo metadatos y resultados agregados

### 4.4. En Reportes y Salidas

- **Sin nombres de pacientes** en reportes CSV/JSON - solo conteos agregados
- **Estadísticas por categorías** (normales/sospechosas/artifacts) sin individuos
- **Advertencia obligatoria**: "Prototipo de investigación. Este resultado no equivale a un diagnóstico clínico y requiere revisión experta."

---

## 5. Actividades Pendientes CITO-69

### 5.1. Inmediatas (Día 1)

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Revisar flujo de datos en busca de identificadores personales | Equipo de privacidad | 4 | Lista de hallazgos |
| Identificar todos los puntos donde aparecen nombres/IDs en el código | Ingeniería | 3 | Documento de puntos críticos |
| Definir estrategia de anonimización (agregación, hashing, eliminación) | Liderazgo | 2 | Estrategia documentada |
| Actualizar `.github/Jira.csv` (fecha inicio, dependencias) | Responsable CITO-69 | 1 | CSV actualizado |

### 5.2. Desarrollo (Día 2-3)

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Implementar funciones de anonimización en `src/preprocessing.py` y `src/analysis.py` | Desarrollo | 6 | Código con funciones de anonimización |
| Migrar datos sensibles a almacenamiento seguro | Ingeniería | 4 | Datos migrados, sin IDs |
| Actualizar `validar_consistencia_dataset.py` con validaciones de privacidad | QA | 3 | Tests actualizados |
| Crear `tests/test_privacy.py` - 5 pruebas unitarias de privacidad | QA | 4 | Tests passing |

### 5.3. Validación y Cierre (Día 4-5)

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Revisar que no haya identificadores personales en salidas generadas | QA + Legal | 4 | Checklist de privacidad |
| Test de fuga de información (red teaming básico) | Equipo de seguridad | 3 | Reporte de hallazgos |
| Validar cumplimiento LFPDPPP principios básicos | Consultoría legal | 2 | Validación de cumplimiento |
| Actualizar `.github/Jira.csv` (estado avanzado) | Responsable CITO-69 | 1 | CSV actualizado |
| Hand-off a CITO-70 (dataset splits requiere conocer datos anonimizados) | Responsable CITO-69 | 2 | Documento de handoff |

---

## 6. Dependencias con Otras Actividades JIRA

| Actividad | Tipo de Dependencia | Descripción |
|-----------|--------------------|-------------|
| **CITO-68** | **Paralela (no depende de CITO-68)** | Alcance clínico y privacidad pueden iniciarse simultáneamente. CITO-68 definía el "qué" (alcance), CITO-69 define el "cómo" (privacidad de datos). |
| **CITO-70** | **Secuencial (dep. de CITO-69)** | Definir splits train/val/test requiere conocer qué datos son seguros para compartir, definido en CITO-69. |
| **CITO-71** | **Secuencial (dep. de CITO-70)** | Protocolo de anotación requiere dataset estructurado y anonimizado (CITO-70). |
| **CITO-73** | **Independiente (ayuda mutua)** | Correcciones DoG (CITO-42) y contexto clínico (CITO-68) se complementan. |
| **CITO-75** | **Secuencial (dep. de CITO-70)** | Métricas F1/IoU requieren dataset con splits (CITO-70), que depende de CITO-69. |
| **CITO-84** | **Depende de todas** | Auditoría final requiere ambos entregables (CITO-68 y CITO-69). |

---

## 7. Plan de Implementación

### 7.1. Actividades Semana 1

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Identificar puntos de riesgo en flujo de datos | Equipo | 4 | `DOC-69-01: Puntos críticos` |
| Definir estrategia de anonimización | Liderazgo | 2 | `DOC-69-02: Estrategia` |
| Actualizar Jira y crear base de tests | Responsable CITO-69 | 3 | Jira actualizado, tests skeleton |

### 7.2. Actividades Semana 2

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Implementar funciones de anonimización en src/ | Desarrollo | 6 | Código con `anonimizar_datos()` |
| Migrar datos sensibles a almacenamiento seguro | Ingeniería | 4 | Datos migrados, sin IDs |
| Test de unitarios de privacidad | QA | 4 | `tests/test_privacy.py` passing |

### 7.3. Actividades Semana 3

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Validar que no haya identificadores en salidas | QA + Legal | 4 | Checklist aprobado |
| Test de fuga básica | Equipo seguridad | 3 | Reporte sin información sensible |
| Hand-off a CITO-70 | Responsable CITO-69 | 2 | Documento de handoff |
| Actualizar `.github/Jira.csv` | Responsable CITO-69 | 1 | CSV actualizado |

---

## 8. Entregables CITO-69

| Entregable | Descripción | Estado |
|------------|-------------|--------|
| **`DOC-69-01: Puntos críticos de privacidad`** | Lista de todos los puntos donde aparecen identificadores en el código y datos | Pendiente |
| **`DOC-69-02: Estrategia de anonimización`** | Documento con estrategia: qué datos anonimizar, cómo, cuándo | Pendiente |
| **`tests/test_privacy.py`** | 5 pruebas unitarias de privacidad (anonymize function, data leakage, etc.) | Pendiente |
| **Actualización `.github/Jira.csv`** | CITO-69: fecha inicio, dependencias CITO-70, estado "En curso" | Pendiente |
| **Código con `anonimizar_*` functions** | Funciones en `src/preprocessing.py` y `src/analysis.py` para remover IDs | Pendiente |

---

## 9. Métricas de Éxito CITO-69

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| **S1:** No haya identificadores personales en 100% de salidas generadas | ✅ Pass | Revisar salidas CLI, Streamlit, API, reportes |
| **S2:** `tests/test_privacy.py` con 5 tests passing | ✅ Pass | Ejecutar `python -m pytest tests/test_privacy.py -v` |
| **S3:** Datos sensibles migrados a almacenamiento seguro | ✅ Pass | Verificar que no hay IDs en `data/` público |
| **S4:** Estrategia de anonimización documentada y aprobada | ✅ Pass | Revisión por pares |
| **S5:** `.github/Jira.csv` actualizado | ✅ Pass | Estado "En curso", dependencias CITO-70 agregadas |

**Criterio de aceptación:** Se cumplen las 5 métricas S1-S5.

---

## 10. Referencias y Normatividad

| Referencia | Descripción |
|------------|-------------|
| **LFPDPPP** (Artículos 6, 7, 8, 9) | Principios de licititud, consentimiento, limitación de uso, seguridad |
| **Guías OWASP A10** | Protección de datos, prevención de fugas |
| **Declaración de Helsinki** | Principios éticos para investigación con datos humanos |
| **Normativa ISO 27701** | although the prototype is not a formal system, privacy principles apply |

---

## 11. Historial de Versiones

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| **1.0** | 2026-10-02 | Versión inicial. Definición de privacidad y anonimización. | Zoé Andrés Chacón Zavala |

---

## 12. Contacto

**Responsable del proyecto:** Zoé Andrés Chacón Zavala  
**Repositorio:** https://github.com/zowy4/CitoCounter-Proto  
**Correo:** (contacto del proyecto)  
**Fecha de última revisión:** 2026-10-02  

---

**Fin del documento CITO-69**