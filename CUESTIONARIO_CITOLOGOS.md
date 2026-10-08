# Cuestionario/Guion para Sesión de Revisión con Citólogos
## CitoCounter Proto v1.1 - Evaluación de Usabilidad y Validación Clínica

---

## 📋 Información de la Sesión

| Campo | Detalle |
|-------|---------|
| **Fecha** | _________________ |
| **Hora inicio** | _________________ |
| **Hora fin** | _________________ |
| **Participante** | _________________ |
| **Rol/Experiencia** | _________________ |
| **Años de experiencia** | _________________ |
| **Facilitador** | _________________ |
| **Observador** | _________________ |

---

## 🎯 Objetivos de la Sesión

1. **Evaluar usabilidad** de la interfaz web (Streamlit) para análisis de citologías
2. **Validar criterios de clasificación** (Regla del 3x, zonas frontera)
3. **Recolectar feedback** sobre utilidad clínica y flujo de trabajo
4. **Identificar mejoras** prioritarias para versión de producción
5. **Documentar casos frontera** y escenarios no cubiertos
6. **Evaluar nuevas funcionalidades**: HSV, Watershed, métricas de calidad, exportación JSON

---

## 📝 PARTE 1: Cuestionario Pre-Sesión (5 min)

### 1.1 Perfil del Participante
- **Especialidad:** ☐ Citología ☐ Patología ☐ Ginecología ☐ Otro: ________
- **Años de experiencia en citología cervical:** ☐ <2 ☐ 2-5 ☐ 5-10 ☐ >10
- **Volumen aproximado de casos/semana:** ☐ <50 ☐ 50-100 ☐ 100-200 ☐ >200
- **Familiaridad con herramientas digitales/IA:** ☐ Ninguna ☐ Básica ☐ Intermedia ☐ Avanzada

### 1.2 Expectativas
- **¿Qué espera de una herramienta de apoyo al diagnóstico?**
  _________________________________________________________________________
  
- **¿Cuáles son sus mayores retos actuales en el conteo/clasificación manual?**
  _________________________________________________________________________

---

## 🖥️ PARTE 2: Evaluación de la Interfaz (25 min)

### 2.1 Primera Impresión (3 min)
*El facilitador muestra la pantalla de bienvenida sin cargar imagen*

| Pregunta | Puntuación (1-5) | Comentarios |
|----------|------------------|-------------|
| ¿La interfaz parece profesional y confiable? | ☐1 ☐2 ☐3 ☐4 ☐5 | _______________ |
| ¿El aviso experimental es claro y visible? | ☐1 ☐2 ☐3 ☐4 ☐5 | _______________ |
| ¿La navegación parece intuitiva? | ☐1 ☐2 ☐3 ☐4 ☐5 | _______________ |

### 2.2 Carga de Imagen (3 min)
*El participante carga una imagen de prueba*

| Tarea | Completada | Tiempo | Dificultad (1-5) | Observaciones |
|-------|------------|--------|------------------|---------------|
| Seleccionar archivo | ☐ Sí ☐ No | ____s | ☐1 ☐2 ☐3 ☐4 ☐5 | _______________ |
| Ver imagen original | ☐ Sí ☐ No | ____s | ☐1 ☐2 ☐3 ☐4 ☐5 | _______________ |
| Entender formatos aceptados | ☐ Sí ☐ No | ____s | ☐1 ☐2 ☐3 ☐4 ☐5 | _______________ |

### 2.3 Ajuste de Parámetros (8 min)
*El participante explora la barra lateral*

| Control | Entendido | Útil | Comentarios |
|---------|-----------|------|-------------|
| **Fuente de Imágenes** (Upload/Dataset) | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Sigma 1 (Detalle fino) | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Sigma 2 (Estructura general) | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Polaridad (Claros/Oscuros) | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| CLAHE (Contraste) + Modo Auto | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Reducción de Ruido + Nivel | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Segmentación HSV (Saturation/Value) | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Separación Watershed / Máximos Locales | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Modo Lote (Múltiples imágenes) | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |

**Pregunta clave:** *¿Los rangos de los sliders (0.5-15.0) son adecuados para su práctica?*
Respuesta: _________________________________________________________________________

### 2.4 Visualización de Resultados (8 min)
*El participante revisa las pestañas de resultados*

| Pestaña | Clara | Informativa | Acciones sugeridas |
|---------|-------|-------------|-------------------|
| 🎯 Análisis Final | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| 🔬 Filtro DoG (+ G1/G2) | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| ⚙️ Preprocesamiento | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| 📷 Original | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| 🎨 HSV / Separación | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| 📋 Criterios Clasificación | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |

**¿Los colores (Verde=Normal, Rojo=Sospechoso) son adecuados?**
☐ Sí, perfectos ☐ Cambiaría: _______________________________________________

**¿La información de "Zona Frontera" es útil?**
☐ Muy útil ☐ Útil ☐ Poco útil ☐ No necesaria
Comentario: _________________________________________________________________________

**¿La tabla de "Criterios por Célula" (área, clasificación, frontera, motivo) es útil?**
☐ Muy útil ☐ Útil ☐ Poco útil ☐ No necesaria
Comentario: _________________________________________________________________________

**¿Las métricas de calidad de imagen (contraste, brillo, saturación) son útiles?**
☐ Muy útil ☐ Útil ☐ Poco útil ☐ No necesaria
Comentario: _________________________________________________________________________

---

## 🔬 PARTE 3: Validación Clínica de Resultados (25 min)

### 3.1 Casos de Prueba Preparados
*Se presentan 5-10 imágenes con ground truth conocido*

| Imagen | Tipo Esperado | Células GT | % Riesgo GT | Resultado Sistema | Acuerdo |
|--------|---------------|------------|-------------|-------------------|---------|
| IMG_001 | Normal | ___ | ___% | ___ / ___ / ___% | ☐ Sí ☐ No ☐ Parcial |
| IMG_002 | Anormal | ___ | ___% | ___ / ___ / ___% | ☐ Sí ☐ No ☐ Parcial |
| IMG_003 | Artefactos | ___ | ___% | ___ / ___ / ___% | ☐ Sí ☐ No ☐ Parcial |
| IMG_004 | Superposición | ___ | ___% | ___ / ___ / ___% | ☐ Sí ☐ No ☐ Parcial |
| IMG_005 | Baja calidad | ___ | ___% | ___ / ___ / ___% | ☐ Sí ☐ No ☐ Parcial |

*GT = Ground Truth (verdad de terreno anotada por experto)*

### 3.2 Evaluación Detallada por Caso
*Para cada imagen donde NO hay acuerdo total:*

**Imagen: _______________**
- **Discrepancia principal:** ☐ Conteo total ☐ Clasificación Normal/Sospechosa ☐ Zona frontera ☐ Falsos positivos ☐ Falsos negativos
- **Causa percibida:** _________________________________________________________________________
- **¿Cómo lo clasificaría usted?:** _________________________________________________________________________
- **Parámetros a ajustar:** σ1=____ σ2=____ Polaridad=____ Otros: _______________

### 3.3 Regla del 3x y Zona Frontera
| Pregunta | Respuesta |
|----------|-----------|
| ¿La regla "área ≥ 3x promedio = sospechoso" coincide con su criterio clínico? | ☐ Sí, exacta ☐ Aproximada ☐ No, uso otro criterio |
| ¿Qué factor usaría usted? | ______ x |
| ¿El margen de ±10% (zona frontera) es apropiado? | ☐ Sí ☐ No, debería ser ±____% |
| ¿Cómo maneja casos frontera en su práctica? | _________________________________________________________________________ |

### 3.4 Casos Específicos Problemáticos
*Marque los que el sistema maneja MAL actualmente:*

☐ **Superposición celular** (núcleos en contacto)
☐ **Artefactos de tinción** (precipitados, manchas)
☐ **Variaciones de iluminación** (sombras, viñeteo)
☐ **Núcleos muy pequeños** (células basales/parabásicas)
☐ **Núcleos muy grandes** (células columnares, metaplasia)
☐ **Inflamación** (leucocitos, moco)
☐ **Sangrado** (eritrocitos, coágulos)
☐ **Artefactos de preparación** (burbujas, pliegues)
☐ **Otros:** _________________________________________________________________________

---

## 📊 PARTE 4: Métricas y Reportes (15 min)

### 4.1 Dashboard de Métricas
*El facilitador muestra la sección "Historial" e "Indicadores clave"*

| Métrica | Comprensible | Útil para seguimiento | Comentarios |
|---------|--------------|----------------------|-------------|
| Total ejecuciones | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Imágenes únicas | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Células detectadas promedio | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| % Riesgo promedio | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Tasa riesgo alto (>10%) | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Evolución temporal | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |

### 4.2 Métricas de Calidad de Imagen
*El facilitador muestra el expander "Métricas de Calidad de Imagen"*

| Métrica | Comprensible | Útil | Comentarios |
|---------|--------------|------|-------------|
| Contraste | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Brillo Promedio | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Saturación | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |
| Estado (Aceptable/No Aceptable) | ☐ Sí ☐ No | ☐ Sí ☐ No | _______________ |

### 4.3 Exportación de Resultados
*El participante prueba la descarga*

| Formato | Funciona | Completo | Formato útil |
|---------|----------|----------|--------------|
| PNG (Panel visual) | ☐ Sí ☐ No | ☐ Sí ☐ No | ☐ Sí ☐ No |
| CSV (Datos tabulares) | ☐ Sí ☐ No | ☐ Sí ☐ No | ☐ Sí ☐ No |
| JSON (Completo con metadatos, parámetros, criterios por célula) | ☐ Sí ☐ No | ☐ Sí ☐ No | ☐ Sí ☐ No |

**¿Qué campos FALTAN en la exportación para su reporte de laboratorio?**
_________________________________________________________________________

**¿Qué campos SOBRAN o son confusos?**
_________________________________________________________________________

---

## 💬 PARTE 5: Feedback Cualitativo (15 min)

### 5.1 Fortalezas (Top 3)
1. _________________________________________________________________________
2. _________________________________________________________________________
3. _________________________________________________________________________

### 5.2 Debilidades / Mejoras Urgentes (Top 3)
1. _________________________________________________________________________
2. _________________________________________________________________________
3. _________________________________________________________________________

### 5.3 Flujo de Trabajo Ideal
*Describa cómo le gustaría que fuera el flujo completo en su laboratorio:*

_________________________________________________________________________
_________________________________________________________________________
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