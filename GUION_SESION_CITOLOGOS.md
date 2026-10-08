# Guion de Sesión para Facilitador
## CitoCounter Proto - Revisión con Citólogos (CITO-38, CITO-39, CITO-88)

---

## ⏱️ Cronograma Estimado (100 minutos)

| Fase | Duración | Actividad |
|------|----------|-----------|
| **Bienvenida y Consentimiento** | 5 min | Presentación, firma de consentimiento, explicación del objetivo |
| **Cuestionario Pre-Sesión** | 5 min | Perfil del participante y expectativas |
| **Demo Guiada** | 15 min | Facilitador muestra flujo completo con caso conocido |
| **Exploración Libre** | 15 min | Participante prueba con sus propias imágenes/casos |
| **Validación Clínica** | 30 min | Evaluación de 8-12 casos de prueba con ground truth |
| **Métricas y Exportación** | 15 min | Revisión de dashboard histórico, métricas calidad, exportaciones |
| **Feedback Cualitativo** | 15 min | Fortalezas, debilidades, flujo ideal, NPS |
| **Seguridad y Ética** | 5 min | Privacidad, responsabilidad, aviso legal |
| **Cierre y Compromisos** | 5 min | Resumen, acciones, firmas |

---

## 🎬 Guion Detallado

### 1. BIENVENIDA Y CONSENTIMIENTO (5 min)

**Facilitador:** *"Gracias por participar. Esta sesión dura ~100 minutos. Evaluaremos CitoCounter Proto v1.1, una herramienta experimental de apoyo al análisis de citologías cervicales. **No es un dispositivo médico ni sustituye su criterio diagnóstico.** Sus respuestas son confidenciales y se usarán solo para mejorar el prototipo. ¿Firma el consentimiento?"*

- [ ] Entregar formulario de consentimiento
- [ ] Explicar que puede retirarse en cualquier momento
- [ ] Confirmar grabación (audio/pantalla) si aplica
- [ ] Presentar al observador (si hay)

---

### 2. CUESTIONARIO PRE-SESIÓN (5 min)

**Facilitador:** *"Antes de ver la herramienta, unas preguntas rápidas sobre su perfil."*

- Entregar Parte 1 del cuestionario (papel o digital)
- Dar 3-4 minutos para completar
- No influir en respuestas

---

### 3. DEMO GUIADA (15 min)

**Facilitador:** *"Voy a mostrarle el flujo completo con un caso de referencia."*

**Pasos a demostrar:**
1. **Pantalla de bienvenida** - Señalar aviso experimental, formatos, guía
2. **Fuente de imágenes** - Seleccionar "Dataset del proyecto" (2000 imágenes, splits train/val/test)
3. **Parámetros DoG** - σ1=7.0, σ2=8.0, explicar ratio 1.14x, validación visual
4. **Polaridad + CLAHE** - "Claros=fluorescencia, Oscuros=Papanicolaou/EDF. CLAHE auto adapta contraste"
5. **HSV + Watershed** - "HSV para color, Watershed para superposición. Experimentales"
6. **Modo Lote** - "Procesa múltiples imágenes a la vez con barra de progreso"
7. **Cargar EDF004.png** - "Caso normal, bajo riesgo. Ver pestañas"
8. **Pestañas 1-3** - "Análisis Final (Verde/Rojo), DoG (G1/G2), Preprocesamiento"
9. **Pestañas 4-6** - "Original, HSV/Separación, Criterios por célula"
10. **Métricas + Expandibles** - "4 métricas clave, advertencias calidad, estadísticas, descargas"
11. **Historial + Indicadores** - "Bitácora automática, indicadores CITO-28, evolución temporal"

**NO dejar que el participante interactúe aún.** Solo observar.

---

### 4. EXPLORACIÓN LIBRE (15 min)

**Facilitador:** *"Ahora es su turno. Tiene 15 minutos para explorar libremente. Cargue sus propias imágenes o use las de prueba. Ajuste parámetros, pruebe las opciones avanzadas. Piensen en voz alta: ¿qué espera ver? ¿Qué le sorprende?"*

**Observador toma notas de:**
- Dudas / preguntas frecuentes
- Errores / comportamientos inesperados
- Comentarios espontáneos
- Tiempo en cada tarea
- Uso de controles avanzados (HSV, Watershed, Modo Lote, Modo CLAHE Auto)

**Casos sugeridos para probar:**
- `EDF004.png` - Normal, buena calidad
- `EDF001.png` - Alto riesgo
- `EDF005.png` - Moderado
- Imagen propia del participante (si trae)
- Imagen con artefactos/ruido (si disponible)
- Probar modo lote con 3-5 imágenes

---

### 5. VALIDACIÓN CLÍNICA (30 min) ⭐ PARTE MÁS IMPORTANTE

**Facilitador:** *"Ahora evaluaremos casos específicos donde conocemos la 'verdad' (ground truth anotado por experto). Para cada imagen, compararemos su criterio con el del sistema."*

**Metodología:**
1. Mostrar imagen **SIN** resultados del sistema
2. Preguntar: *"¿Cuántas células ve? ¿Cuáles son sospechosas? ¿% riesgo?"*
3. Mostrar resultado del sistema
4. Comparar y registrar en **Parte 3.1** del cuestionario
5. Si hay discrepancia → **Parte 3.2** (análisis detallado)

**Casos preparados (orden sugerido):**

| Orden | Imagen | Tipo | Por qué |
|-------|--------|------|---------|
| 1 | EDF004.png | Normal claro | Baseline, fácil acuerdo |
| 2 | EDF005.png | Moderado | Zona frontera típica |
| 3 | EDF001.png | Alto riesgo | Validar detección de sospechosas |
| 4 | [Superposición] | Difícil | Test Watershed |
| 5 | [Artefactos] | Difícil | Test robustez |
| 6 | [Baja calidad] | Difícil | Test métricas calidad |
| 7 | [Inflamación] | Muy difícil | Caso real complejo |
| 8 | [Metaplasia] | Muy difícil | Caso real complejo |
| 9 | [Bajo contraste] | Difícil | Test HSV |
| 10 | [Superposición + artefactos] | Muy difícil | Test combinado |

**Preguntas clave durante discrepancias:**
- *"¿Qué ve usted que el sistema no ve?"*
- *"¿Por qué clasificaría esta célula diferente?"*
- *"¿El umbral de 3x tiene sentido aquí?"*
- *"¿Cambiaría σ1/σ2 para este caso?"*
- *"¿El modo Watershed mejora la superposición?"*
- *"¿El modo HSV ayuda en bajo contraste?"*

**¡Registre TODOS los parámetros sugeridos por el citólogo!**

---

### 6. MÉTRICAS Y EXPORTACIÓN (15 min)

**Facilitador:** *"Veamos el seguimiento histórico y las opciones de reporte."*

1. Abrir expander "📈 Historial de ejecuciones"
2. Abrir expander "📊 Indicadores clave (CITO-28)"
3. Abrir expander "📈 Métricas de Calidad de Imagen"
3. Probar exportación PNG, CSV, JSON
4. Completar **Parte 4** del cuestionario

**Preguntas guía:**
- *"¿Estas métricas le sirven para control de calidad del laboratorio?"*
- *"¿Qué gráfico/reporte le falta?"*
- *"El JSON, ¿se lo daría a TI para integrar en el LIS?"*
- *"Las métricas de calidad (contraste, brillo, saturación), ¿le ayudan a decidir si la imagen es apta?"*

---

### 7. FEEDBACK CUALITATIVO (15 min)

**Facilitador:** *"Ahora sus impresiones generales. No hay respuestas correctas."*

- Completar **Partes 5, 6, 7** del cuestionario
- Para NPS (Parte 7.1): *"En escala 0-10, ¿recomendaría esto a un colega?"*
- Para priorización (Parte 7.2): *"Ordene lo que más le urge"*

**Escuchar activamente. No defender el sistema. Preguntar "¿por qué?" frecuentemente.**

---

### 8. SEGURIDAD Y ÉTICA (5 min)

**Facilitador:** *"Unas preguntas finales sobre aspectos legales y éticos."*

- Completar **Parte 6** del cuestionario
- Aclarar: *"El sistema anonimiza automáticamente (muestra_XXX), no guarda imágenes permanentemente, y el aviso legal está en cada resultado."*

---

### 9. CIERRE Y COMPROMISOS (5 min)

**Facilitador:** *"Resumamos lo más importante."*

1. Leer hallazgos críticos en voz alta
2. Acordar **3 acciones máximas** con responsable y fecha
3. Completar **Parte 8** (firmas)
4. Agradecer y entregar incentivo si corresponde
5. Explicar seguimiento: *"Recibirá resumen de mejoras en 2 semanas"*

---

## 📋 Checklist del Facilitador (Durante la Sesión)

### Técnico
- [ ] Streamlit corriendo (`streamlit run app.py`)
- [ ] Imágenes de prueba accesibles
- [ ] Navegador en pantalla completa
- [ ] Grabación iniciada (si aplica)
- [ ] Plan B si falla la app (capturas de pantalla impresas)

### Metodológico
- [ ] No liderar al participante ("¿Le gusta este botón?" → "¿Qué opina de este botón?")
- [ ] Permitir silencio (dar tiempo a pensar)
- [ ] Registrar citas textuales ("Me confunde que...")
- [ ] No explicar/justificar el diseño durante la prueba
- [ ] Anotar lenguaje corporal (frustración, satisfacción, confusión)

### Ético
- [ ] Recordar aviso experimental antes de cada caso clínico
- [ ] No presionar para usar la herramienta en casos reales
- [ ] Respetar si no quiere firmar/ser grabado
- [ ] Anonimizar datos en reportes (usar "Participante 1", "Citólogo A")

---

## 🚨 Señales de Alerta (Detener y Profundizar)

| Señal | Acción |
|-------|--------|
| "Esto es peligroso" | Detener, entender por qué, documentar como **Crítico** |
| "No confío en esto" | Explorar causa raíz (falsos negativos? UX? Falta de validación?) |
| "Esto me ralentiza" | Medir tiempo real vs manual, comparar |
| "No entiendo qué hace" | Problema de UX / terminología / onboarding |
| Silencio prolongado + ceño fruncido | Preguntar "¿Qué está pensando?" |

---

## 📊 Plantilla de Resumen Post-Sesión (Rellenar en caliente)

```
SESION #[NÚMERO] - RESUMEN EJECUTIVO
=====================================
Participante: [Iniciales/Rol]
Fecha: [DD/MM/AAAA]
Duración real: [XX] min

NPS: [0-10] → [Promotor/Pasivo/Detractor]

ACUERDO CLÍNICO GLOBAL: [XX]% (X/Y casos coincidentes)

TOP 3 FORTALEZAS:
1. 
2. 
3. 

TOP 3 DEBILIDADES CRÍTICAS:
1. [Severidad: Crítica/Alta] 
2. [Severidad: Crítica/Alta]
3. [Severidad: Media]

HALLAZGOS CLÍNICOS CLAVE:
- Regla 3x: [Apropiada / Ajustar a ___x / No válida]
- Zona frontera ±10%: [Apropiada / Ajustar a ±___%]
- Casos superpuestos: [Sistema falla / Watershed ayuda / Necesita más trabajo]
- Artefactos: [Maneja bien / Falsos positivos en ___]
- Bajo contraste: [HSV ayuda / No ayuda / No probado]

PARÁMETROS SUGERIDOS POR CITÓLOGO:
- σ1 óptimo: ____
- σ2 óptimo: ____
- Polaridad preferida: ____
- CLAHE: [Sí/No/Auto]
- Watershed: [Sí/No/Mejorar]
- HSV: [Sí/No/Mejorar]

ACCIONES COMPROMETIDAS:
1. [Acción] → [Responsable] → [Fecha] → [Prioridad]
2. [Acción] → [Responsable] → [Fecha] → [Prioridad]
3. [Acción] → [Responsable] → [Fecha] → [Prioridad]

¿VOLVERÍA A PARTICIPAR? ☐ Sí ☐ No ☐ Con condiciones
```

---

## 📁 Entregables Post-Sesión

1. **Cuestionario completado** (PDF/escaneo) → `docs/sesiones/citologo_[iniciales]_[fecha]_cuestionario.pdf`
2. **Resumen ejecutivo** (arriba) → `docs/sesiones/citologo_[iniciales]_[fecha]_resumen.md`
3. **Grabación** (si aplica) → almacenamiento seguro, borrar a 30 días
4. **Issues en Jira/GitHub** creados desde hallazgos → etiquetar `citologo-feedback`, `CITO-38/39/88`
5. **Actualización de guía maestra** con decisiones tomadas

---

## 🔗 Trazabilidad Jira

| Actividad | Clave Jira | Estado Esperado Post-Sesión |
|-----------|------------|----------------------------|
| Ejecutar pruebas de usabilidad con citotecnólogos | CITO-38 | **Hecha** (con evidencia) |
| Recopilar feedback de personal clínico y resolver cambios | CITO-39 | **En progreso** (acciones comprometidas) |
| Pruebas de la plataforma con usuarios potenciales | CITO-88 | **Hecha** (mínimo 5 citotecnólogos) |

---

**Versión:** 1.1  
**Fecha:** 2026-10-08  
**Facilitador asignado:** ___________________________________