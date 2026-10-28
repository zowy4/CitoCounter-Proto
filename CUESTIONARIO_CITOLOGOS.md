# Cuestionario para citólogos - revisión del prototipo CitoCounter Proto

## 1. Información de la sesión

| Campo | Respuesta |
|---|---|
| Fecha | __________________ |
| Hora de inicio | __________________ |
| Hora de fin | __________________ |
| Participante | __________________ |
| Rol profesional | __________________ |
| Años de experiencia | __________________ |
| Facilitador | __________________ |
| Observador | __________________ |

---

## 2. Objetivo de la sesión

1. Evaluar si la interfaz ayuda o confunde en la revisión de citologías.
2. Valorar si la regla de riesgo por área es comprensible y útil.
3. Identificar qué aspectos del prototipo necesitan mejorarse.
4. Revisar si la información mostrada tiene valor para un flujo de trabajo clínico o de investigación.

> El sistema es experimental y no sustituye la valoración profesional ni la interpretación clínica.

---

## 3. Perfil del participante

### 3.1 Especialidad

- [ ] Citología
- [ ] Patología
- [ ] Ginecología
- [ ] Citotecnología
- [ ] Otro: __________________

### 3.2 Experiencia

- [ ] Menos de 2 años
- [ ] 2-5 años
- [ ] 5-10 años
- [ ] Más de 10 años

### 3.3 Volumen de trabajo

- [ ] Menos de 50 casos/semana
- [ ] 50-100 casos/semana
- [ ] 100-200 casos/semana
- [ ] Más de 200 casos/semana

### 3.4 Familiaridad con herramientas digitales

- [ ] Ninguna
- [ ] Básica
- [ ] Intermedia
- [ ] Avanzada

---

## 4. Primera impresión de la herramienta

### 4.1 Evaluación general

| Pregunta | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|
| La interfaz parece clara y profesional | [ ] | [ ] | [ ] | [ ] | [ ] |
| El aviso experimental es suficiente | [ ] | [ ] | [ ] | [ ] | [ ] |
| La navegación es intuitiva | [ ] | [ ] | [ ] | [ ] | [ ] |
| La información es fácil de interpretar | [ ] | [ ] | [ ] | [ ] | [ ] |

### 4.2 Comentarios iniciales

- ¿Qué le llamó la atención en la primera vista?
  ____________________________________________________________

- ¿Qué le resulta confuso o poco claro?
  ____________________________________________________________

---

## 5. Carga y manejo de imágenes

| Tarea | Sí | No | Comentario |
|---|---|---|---|
| Entiende cómo cargar la imagen | [ ] | [ ] | __________________ |
| Entiende la diferencia entre imagen original y resultado | [ ] | [ ] | __________________ |
| Elige parámetros con claridad | [ ] | [ ] | __________________ |
| Entiende el uso de la polaridad | [ ] | [ ] | __________________ |
| Reconoce la utilidad del filtro DoG | [ ] | [ ] | __________________ |

### 5.1 Qué cambiaría en la carga de datos

____________________________________________________________

---

## 6. Evaluación del criterio de clasificación

### 6.1 Regla del 3x

- ¿La regla “área ≥ 3x el promedio normal = sospechoso” tiene sentido para su práctica?
  - [ ] Sí, exacta
  - [ ] Sí, aproximada
  - [ ] No, usaría otra regla

Si no, ¿cuál usaría?

____________________________________________________________

### 6.2 Zona frontera

- ¿El margen de ±10% alrededor del umbral es útil?
  - [ ] Sí
  - [ ] No
  - [ ] Debería ser ± __________ %

¿Cómo manejaría usted los casos frontera en la práctica?

____________________________________________________________

### 6.3 Colores y etiquetado

- [ ] Verde para normal y rojo para sospechoso es claro
- [ ] Cambiaría los colores por __________________
- [ ] La etiqueta “riesgo” es útil
- [ ] La etiqueta “riesgo” puede causar confusión

---

## 7. Evaluación de la interfaz y resultados

| Sección | Comprende | Útil | Comentario |
|---|---|---|---|
| Original | [ ] [ ] | [ ] [ ] | __________________ |
| DoG | [ ] [ ] | [ ] [ ] | __________________ |
| Preprocesamiento | [ ] [ ] | [ ] [ ] | __________________ |
| Clasificación por área | [ ] [ ] | [ ] [ ] | __________________ |
| Criterios por célula | [ ] [ ] | [ ] [ ] | __________________ |
| Historial | [ ] [ ] | [ ] [ ] | __________________ |
| Exportación PNG/CSV/JSON | [ ] [ ] | [ ] [ ] | __________________ |

### 7.1 Qué le parece la información mostrada

- ¿Qué datos le parecen más útiles?
  ____________________________________________________________

- ¿Qué información le falta?
  ____________________________________________________________

- ¿Qué se ve demasiado técnico o poco útil?
  ____________________________________________________________

---

## 8. Evaluación de calidad y métricas

| Métrica | Entiende | Útil | Comentario |
|---|---|---|---|
| Contraste | [ ] [ ] | [ ] [ ] | __________________ |
| Brillo | [ ] [ ] | [ ] [ ] | __________________ |
| Saturación | [ ] [ ] | [ ] [ ] | __________________ |
| % Riesgo | [ ] [ ] | [ ] [ ] | __________________ |
| Total de células detectadas | [ ] [ ] | [ ] [ ] | __________________ |

### 8.1 ¿Qué tan útil sería esta herramienta para su flujo de trabajo?

- [ ] Muy útil
- [ ] Útil
- [ ] Poco útil
- [ ] No la usaría

¿Por qué?

____________________________________________________________

---

## 9. Casos difíciles y observaciones clínicas

Marque los casos que cree que el sistema maneja mal hoy:

- [ ] Superposición celular
- [ ] Artefactos de tinción
- [ ] Iluminación irregular
- [ ] Núcleos muy pequeños
- [ ] Núcleos muy grandes
- [ ] Inflamación o leucocitos
- [ ] Sangrado o eritrocitos
- [ ] Burbujas o pliegues
- [ ] Otros: __________________

¿Qué sería lo más importante mejorar antes de considerar la herramienta útil en un entorno clínico o de revisión?

____________________________________________________________

---

## 10. Feedback final

### 10.1 Fortalezas del prototipo

1. _________________________________________________
2. _________________________________________________
3. _________________________________________________

### 10.2 Deficiencias o mejoras urgentes

1. _________________________________________________
2. _________________________________________________
3. _________________________________________________

### 10.3 Recomendación general

- [ ] Lo recomiendo para investigación
- [ ] Lo recomiendo para revisión asistida
- [ ] No lo recomendaría todavía

Comentario final:

____________________________________________________________

---

## 11. Cierre

- Fecha de la entrevista: __________________
- Nombre del facilitador: __________________
- Observaciones adicionales: __________________

_________________________________________________________________________

### 5.4 Integración con Sistemas Existentes
- **¿Usa LIS (Sistema de Información de Laboratorio)?** ☐ Sí ☐ No
  - Si sí, ¿cuál? _________________________________________________________________________
  - ¿Necesita integración HL7/FHIR? ☐ Sí ☐ No ☐ No sé
- **¿Usa visor de imágenes digitales (WSI viewer)?** ☐ Sí ☐ No
  - Si sí, ¿cuál? _________________________________________________________________________

### 5.5 Decisión de Uso
| Escenario | Lo usaría | Comentarios |
|-----------|-----------|-------------|
| Screening inicial (triage) | ☐ Sí ☐ No ☐ Tal vez | _______________ |
| Segunda opinión / Control de calidad | ☐ Sí ☐ No ☐ Tal vez | _______________ |
| Formación de residentes | ☐ Sí ☐ No ☐ Tal vez | _______________ |
| Investigación / Estudios | ☐ Sí ☐ No ☐ Tal vez | _______________ |
| Diagnóstico primario | ☐ Sí ☐ No ☐ Tal vez | _______________ |

---

## ⚠️ PARTE 6: Seguridad y Aspectos Éticos (5 min)

### 6.1 Privacidad y Datos
| Pregunta | Respuesta |
|----------|-----------|
| ¿Le preocupa que las imágenes subidas se almacenen temporalmente? | ☐ Sí ☐ No ☐ Depende |
| ¿Es aceptable el límite de 10MB por imagen? | ☐ Sí ☐ No, necesito _____ MB |
| ¿El anonimizado automático (ID muestra_XXX) es suficiente? | ☐ Sí ☐ No, falta: _______________ |

### 6.2 Responsabilidad y Aviso
| Pregunta | Respuesta |
|----------|-----------|
| ¿El aviso "No es diagnóstico clínico" es suficiente? | ☐ Sí ☐ No, debería: _______________ |
| ¿Firmaría un consentimiento para usar esta herramienta? | ☐ Sí ☐ No ☐ Con condiciones |
| ¿Quién debería validar los resultados antes de reportar? | ☐ Citólogo senior ☐ Patólogo ☐ Comité ☐ IA + Humano |

---

## 📈 PARTE 7: Puntuación Global (NPS)

### 7.1 Net Promoter Score
**En una escala de 0 a 10, ¿qué tan probable es que recomiende CitoCounter a un colega?**

☐ 0 ☐ 1 ☐ 2 ☐ 3 ☐ 4 ☐ 5 ☐ 6 ☐ 7 ☐ 8 ☐ 9 ☐ 10

- **Promotores (9-10):** _________________________________________________________________________
- **Pasivos (7-8):** _________________________________________________________________________
- **Detractores (0-6):** _________________________________________________________________________

### 7.2 Priorización de Próximos Pasos
*Ordene del 1 (más urgente) al 8:*

___ Mejorar precisión en casos superpuestos (Watershed/Máximos locales)
___ Añadir más métricas (sensibilidad, especificidad, F1, IoU)
___ Integrar con LIS / visor digital (HL7/FHIR)
___ Añadir autenticación y auditoría
___ Mejorar interfaz / experiencia de usuario
___ Validar con dataset clínico mayor
___ Documentación y manual de usuario
___ Mejorar segmentación HSV para bajo contraste
___ Mejorar separación Watershed para superposición
___ Otros: _________________________________________________________________________

---

## ✍️ PARTE 8: Firmas y Cierre

### 8.1 Compromisos de Acción
| Acción | Responsable | Fecha Límite | Prioridad |
|--------|-------------|--------------|-----------|
| ___________________________________ | ___________ | ___________ | ☐ Alta ☐ Media ☐ Baja |
| ___________________________________ | ___________ | ___________ | ☐ Alta ☐ Media ☐ Baja |
| ___________________________________ | ___________ | ___________ | ☐ Alta ☐ Media ☐ Baja |

### 8.2 Firmas

**Participante (Citólogo):**
- Nombre: ___________________________________
- Firma: ___________________________________
- Fecha: ___________________________________

**Facilitador (Equipo Técnico):**
- Nombre: ___________________________________
- Firma: ___________________________________
- Fecha: ___________________________________

---

## 📎 ANEXOS

### Anexo A: Checklist de Preparación Técnica
- [ ] Imágenes de prueba cargadas en `data/raw/` o `mis_imagenes_nuevas/`
- [ ] Ground truth disponible en `CitoDataset_v1/labels/`
- [ ] Parámetros calibrados (σ1=3.0, σ2=5.0 o valores actuales)
- [ ] Bitácora de experimentos (`bitacora_experimentos.csv`) funcional
- [ ] Exportación CSV/JSON probada
- [ ] Navegador compatible (Chrome/Firefox/Edge actualizado)
- [ ] Resolución de pantalla ≥ 1366x768
- [ ] Conexión a internet (para Streamlit cloud si aplica)

### Anexo B: Casos de Prueba Sugeridos
| ID | Descripción | Archivo | Ground Truth | Dificultad |
|----|-------------|---------|--------------|------------|
| TC-01 | Caso normal claro | EDF004.png | 114 células, 9 sospechosas (7.9%) | Fácil |
| TC-02 | Caso anormal moderado | EDF005.png | 272 células, 25 sospechosas (9.2%) | Media |
| TC-03 | Caso alto riesgo | EDF001.png | 261 células, 36 sospechosas (13.8%) | Media |
| TC-04 | Superposición nuclear | _________ | _________ | Difícil |
| TC-05 | Artefactos tinción | _________ | _________ | Difícil |
| TC-06 | Baja calidad/ruido | _________ | _________ | Difícil |
| TC-07 | Inflamación marcada | _________ | _________ | Muy difícil |
| TC-08 | Metaplasia escamosa | _________ | _________ | Muy difícil |
| TC-09 | Bajo contraste (test HSV) | _________ | _________ | Difícil |
| TC-10 | Núcleos superpuestos (test Watershed) | _________ | _________ | Muy difícil |
| TC-11 | Artefactos de tinción + ruido | _________ | _________ | Muy difícil |
| TC-12 | Metaplasia + inflamación | _________ | _________ | Muy difícil |

### Anexo C: Plantilla de Reporte de Hallazgos
```
HALLAZGO #[NÚMERO]
- Tipo: ☐ Bug ☐ Mejora ☐ Nueva funcionalidad ☐ Usabilidad ☐ Clínico
- Severidad: ☐ Crítica ☐ Alta ☐ Media ☐ Baja
- Descripción: _________________________________________________________________________
- Pasos para reproducir: _________________________________________________________________________
- Resultado esperado: _________________________________________________________________________
- Resultado actual: _________________________________________________________________________
- Evidencia (captura/log): _________________________________________________________________________
- Reportado por: ___________________________________
- Fecha: ___________________________________
```

---

## 📌 Notas del Facilitador (Post-Sesión)

### Resumen de Hallazgos Críticos
_________________________________________________________________________
_________________________________________________________________________

### Decisiones Tomadas
_________________________________________________________________________
_________________________________________________________________________

### Próximos Pasos Inmediatos
1. _________________________________________________________________________
2. _________________________________________________________________________
3. _________________________________________________________________________

### Métricas de la Sesión
- Duración total: ______ minutos
- Imágenes evaluadas: ______
- Acuerdo global: ______%
- NPS: ______
- ¿Sesión grabada? ☐ Sí ☐ No
- ¿Consentimiento firmado? ☐ Sí ☐ No

---

**Versión del cuestionario:** 1.0  
**Fecha:** 2026-10-07  
**Proyecto:** CitoCounter Proto  
**Basado en:** CITO-38, CITO-39, CITO-88 (Pruebas de usabilidad y feedback clínico)