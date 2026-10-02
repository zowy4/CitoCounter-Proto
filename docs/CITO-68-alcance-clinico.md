# CITO-68: Definir Alcance Clínico y Requisitos

**Fecha:** 2026-10-02  
**Responsable:** Zoé Andrés Chacón Zavala  
**Prioridad:** Highest  
**Estado:** En curso  

---

## 1. Propósito

Definir los límites, usuarios, entradas, salidas y restricciones del prototipo **CitoCounter-Proto** para establecerlo formalmente como:

- **Herramienta de investigación** y **apoyo al análisis**, **no** software de diagnóstico ni dispositivo médico.
- Sistema que genera **información de apoyo** para citotecnólogos y investigadores, cuya salida requiere **revisión experta** antes de cualquier conclusión clínica.

---

## 2. Contexto Actual del Proyecto

El prototipo CitoCounter-Proto implementa un pipeline de procesamiento de imágenes citológicas usando:

- **Filtro Difference of Gaussians (DoG)** para realce de núcleos
- **Segmentación por watershed** para separación de núcleos superpuestos
- **Análisis de características** (área, morfología, clasificación)
- **Visualización** de resultados y generación de reportes

**Tecnologías:** Python 3.x, OpenCV 4.x, NumPy, argparse, Streamlit  
**Arquitectura:** Modular - preprocessing → DoG → análisis → separación → clasificación → visualización  

**Estado actual (después de CITO-22 a CITO-44):**
- 211 imágenes JPG estandarizadas en `data/raw/`
- 71/71 tests unitarias passing
- 243 etiquetas YOLO validadas (71,431 núcleos etiquetados)
- Benchmark de rendimiento completado
- 5 pruebas de integridad de dataset

---

## 2.1. Alcance del Prototipo

| Aspecto | Definición |
|---------|------------|
| **Tipo de software** | Prototipo de investigación, código abierto |
| **Dominio** | Procesamiento de imágenes citológicas cervicales |
| **Finalidad** | Análisis cuantitativo de características nucleares |
| **Usuarios objetivo** | Investigadores, citotecnólogos, personal de laboratorio |
| **Distribución** | Uso local, sin instalación en servidores de producción clínica |

---

## 3. Definición de Entradas y Salidas

### 3.1. Entradas (Inputs)

| Campo | Formato | Restricciones | Validación |
|-------|---------|---------------|------------|
| **Imagen** | JPG, máximo 64 KiB (65536 bytes) | `cv2.imread()` falla > 64 KiB | `validar_tamano_imagen()` en `src/analysis.py` |
| **Parámetros DoG** | σ1, σ2 > 0 | Default: σ1=7.0, σ2=8.0 | Argumentos CLI `--sigma1`, `--sigma2` |
| **Polaridad** | 'nucleos-claros' | 'nucleos-oscuros' (tipo Papanicolaou/EDF) | Argumento `--polaridad` |
| **Reducción de ruido** | Booleano | Default: False | Argumento `--ruido` |
| **Mejora de contraste** | Booleano | Default: True | Argumento `--no-contraste` |

**Validaciones OWASP/STRIDE (CITO-45):**
- Tamaño de imagen ≤ 64 KiB antes de procesamiento
- No procesar imágenes vacías o nulas
- Límites en parámetros numéricos para evitar desbordamientos

### 3.2. Salidas (Outputs)

| Campo | Formato | Descripción | Advertencia |
|-------|---------|-------------|-------------|
| **Panel comparativo** | Imagen PNG (8-bit) | Original → Gris (CLAHE) → DoG → Detección | **"No diagnóstico clínico"** |
| **Reporte estadístico** | CSV / JSON | Total, normales, sospechosas, porcentaje riesgo | **"Solo apoyo al diagnóstico"** |
| **Métricas** | Números | F1, IoU, precisión, sensibilidad (experimental) | **"Valores experimentales, no validados clínicamente"** |
| **Núcleos detectados** | Count | Cantidad de núcleos identificados por algoritmo | **"Requiere validación experta"** |
| **Mapa de calor / contornos** | Imagen PNG | Representación visual de áreas analizadas | **"Para revisión experta solo"** |

**Advertencia obligatoria en todas las salidas:**
> *"Prototipo de investigación. Este resultado no equivale a un diagnóstico clínico. Requiere revisión experta."*

---

## 4. Definición de Usuarios y Roles

| Rol | Permisos | Restricciones |
|-----|----------|---------------|
| **Investigador / Desarrollador** | Acceso completo, modificación de parámetros, generación de reportes | Uso en entornos de laboratorio o investigación |
| **Citotecnólogo** | Visualización de resultados, análisis de contornos, exportación de datos | Debe leer y aceptar advertencia "no diagnóstico" |
| **Estudiante / Aprendiz** | Visualización y educación sobre pipeline | Debe estar supervisado por rol citotecnólogo o investigador |
| **Público en general** | **No autorizado** | El software no está dirigido al público general |

**Nota:** El software **no** está certificado para uso médico, no debe usarse para toma de decisiones clínicas sin supervisión experta.

---

## 5. Restricciones y Limitaciones

### 5.1. Limitaciones Técnicas

| Limitación | Descripción | Impacto |
|------------|-------------|---------|
| **Tamaño de imagen** | Máximo 64 KiB (65536 bytes) | Evita ataques DoS, limita resolución |
| **Resolución** | Imágenes originales BMP 2048×1536, convertidas a JPG | Calidad estándarizada, no alta resolución |
| **Parámetros DoG** | σ1=7.0, σ2=8.0 por defecto | Valores experimentales, no óptimos clínicamente |
| **Clasificación** | Normal / Anomalía (regla del 3x) | Parámetro provisional, requiere calibración |
| **Distribución de clases** | 99.5% Normal, 0.5% Anormal, 0% Artefacto | Dataset sesgado, no representativo poblacional |

### 5.2. Limitaciones Clínicas

| Limitación | Descripción | Riesgo si se omite |
|------------|-------------|-------------------|
| **No es herramienta de diagnóstico** | Los resultados son cuantitativos, no diagnósticos | Interpretación errónea como diagnóstico médico |
| **Dataset limitado** | 211 imágenes, sin validación en poblaciones clínicas | Resultados no generalizables |
| **Parámetros provisionales** | σ1, σ2, umbral_3x son valores iniciales | Pueden no ser óptimos para todos los tipos de muestra |
| **Sin validación en tiempo real** | Procesamiento por lotes, no diagnóstico instantáneo | Retraso en retroalimentación |

### 5.3. Restricciones de Uso

- **No usar para:** Diagnóstico médico, toma de decisiones clínicas, derivación de pacientes
- **Usar solo para:** Análisis de investigación, educación, preparación de datos, apoyo a revisión experta
- **Citar como:** "CitoCounter-Proto v1.1, prototipo de investigación, no dispositivo médico"
- **Distribuir con:** Este documento (CITO-68) y la advertencia de no diagnóstico

---

## 6. Advertencias y Mensajes Obligatorios

### 6.1. En Interfaz CLI (`main.py`)

```python
print("\n" + "="*60)
print("⚠️  AVISO IMPORTANTE:")
print("   Este resultado es de apoyo a la investigación.")
print("   No equivale a diagnóstico clínico.")
print("   Requiere revisión por citotecnólogo experto.")
print("="*60 + "\n")
```

### 6.2. En Interfaz Streamlit (`app.py`)

```python
st.caption(
    "📋 **CitoCounter-Proto:** Prototipo de investigación. "
    "Los porcentajes son experimentales y no equivalen a diagnóstico clínico."
)
```

### 6.3. En Reportes y Exportaciones (`interfaz_resultados.py`)

```python
AVISO_USO_EXPERIMENTAL = (
    "Prototipo de investigación. Este resultado no equivale a un diagnóstico clínico "
    "y requiere revisión experta."
)
```

### 6.4. En Respuestas API (`api_v1.py`)

```python
"warning": (
    "Prototipo de investigación. El resultado no equivale a diagnóstico clínico."
),
```

---

## 7. Dependencias con Otras Actividades JIRA

| Actividad | Tipo de Dependencia | Descripción |
|-----------|--------------------|-------------|
| **CITO-69** | **Paralela (no depende de CITO-68)** | Privacidad y anonimización (depende de J-01, no de CITO-68). Pueden iniciarse simultáneamente. |
| **CITO-70** | **Secuencial (dep. de CITO-68)** | Definir splits train/val/test requiere saber qué datos son "clínicos" vs "sintéticos", definido en CITO-68. |
| **CITO-71** | **Secuencial (dep. de CITO-70)** | Protocolo de anotación requiere dataset estructurado (CITO-70). |
| **CITO-73** | **Independiente (aunque ayuda)** | Correcciones DoG ya hechas (CITO-42), pero CITO-68 define el contexto de validez clínica de los parámetros. |
| **CITO-75** | **Secuencial (dep. de CITO-70)** | Métricas F1/IoU requieren dataset con splits (CITO-70), que depende de CITO-68. |
| **CITO-84** | **Depende de todas** | Auditoría final y cierre del proyecto requiere todos los entregables previos, inicia con CITO-68. |

---

## 8. Plan de Implementación

### 8.1. Actividades Inmediatas (Día 1)

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Revisar código en busca de indicaciones de diagnóstico | Equipo de desarrollo | 4 | Lista de hallazgos |
| Crear `DOC-68-01: Alcance clínico` (borrador) | Responsable CITO-68 | 4 | Markdown |
| Actualizar `.github/Jira.csv` (fecha inicio, dependencias) | Responsable CITO-68 | 1 | CSV actualizado |
| Verificar que todas las salidas tengan advertencia "no diagnóstico" | QA interno | 2 | Checklist |

### 8.2. Actividades Semana 1

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Revisar y validar matriz de requisitos | Equipo | 4 | `DOC-68-02` |
| Definir roles de usuario y permisos | Liderazgo | 2 | Política de roles |
| Validar limitaciones técnicas (64 KiB, parámetros) | Ingeniería | 3 | Documentación |
| Revisión por pares de DOC-68-01 | Equipo | 3 | Aprobado |

### 8.3. Actividades Semana 2

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Finalizar `DOC-68-03: Restricciones y advertencias` | Responsable CITO-68 | 3 | Markdown |
| Implementar avisos en todas las interfaces (CLI, Streamlit, API) | Desarrollo | 4 | Código actualizado |
| Test de verificación: asegurar que advertencia aparezca en todas las salidas | QA | 3 | Test cases |
| Plan de transición a CITO-69 | Gerencia | 2 | Plan de ruta |

### 8.4. Actividades Semana 3

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Hand-off a CITO-69 (privacidad/anonimización) | Responsable CITO-68 | 2 | Documento de handoff |
| Actualizar `.github/Jira.csv` (estado avanzado) | Responsable CITO-68 | 1 | CSV actualizado |
| Preparar hand-off a CITO-70 (dataset splits) | Responsable CITO-68 | 2 | Documento de handoff |

---

## 9. Métricas de Éxito CITO-68

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| **S1:** Advertencia "no diagnóstico" presente en 100% de salidas | ✅ Pass | Verificar en CLI, Streamlit, API, reportes |
| **S2:** Matriz de requisitos sin contradicciones | ✅ Pass | Revisión interna |
| **S3:** Usuarios autorizados identificados y documentados | ✅ Pass | Lista de roles |
| **S4:** Límites de entrada (64 KiB, formato) validados | ✅ Pass | Test de validación |
| **S5:** `.github/Jira.csv` actualizado | ✅ Pass | Estado "En curso", dependencias agregadas |
| **S5:** Hand-off a CITO-69 planificado | ✅ Pass | Documento de handoff |

**Criterio de aceptación:** Se cumplen las 5 métricas S1-S5.

---

## 10. Referencias y Normatividad

| Referencia | Descripción |
|------------|-------------|
| **LFPDPPP** (Ley Federal de Protección de Datos Personales) | Privacidad de datos, retención, eliminación |
| **Guías OWASP/STRIDE** | Seguridad de aplicaciones, validación de entradas |
| **FDA Software Guidance** | Aunque EE.UU., referencia sobre software de apoyo diagnóstico |
| **Normativa ISO 14971** | Gestión de riesgos en dispositivos médicos (aunque el prototipo no es dispositivo médico) |
| **Declaración de Helsinki** | Principios éticos para investigación médica |

---

## 11. Historial de Versiones

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| **1.0** | 2026-10-02 | Versión inicial. Definición de alcance clínico. | Zoé Andrés Chacón Zavala |

---

## 12. Contacto

**Responsable del proyecto:** Zoé Andrés Chacón Zavala  
**Repositorio:** https://github.com/zowy4/CitoCounter-Proto  
**Correo:** (contacto del proyecto)  
**Fecha de última revisión:** 2026-10-02  

---

**Fin del documento CITO-68**