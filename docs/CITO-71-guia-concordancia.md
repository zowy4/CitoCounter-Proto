# Guía Rápida de Concordancia y Resolución de Discrepancias (CITO-71)

## Propósito

Esta guía proporciona instrucciones prácticas para evaluar la concordancia entre anotadores, resolver discrepancias y mantener la calidad del etiquetado en el proyecto CitoCounter-Proto. Está diseñada para ser utilizada por citotecnólogos y expertos en annotación durante el proceso de validación del dataset.

## 1. Cuándo evaluar concordancia

Evaluar la concordancia inter-anotador cuando:

- [ ] Se han etiquetado ≥ 20 imágenes por annotador
- [ ] Se identificaron discrepancias en la revisión inicial
- [ ] Se requiere validar el protocolo antes de continuar con nuevos splits
- [ ] Se está preparando el reporte para Jira (CITO-71)

## 2. Pasos para evaluar concordancia

### Paso 1: Seleccionar el conjunto de prueba

Elegir un conjunto representativo de imágenes:

- **Mínimo**: 20 imágenes
- **Recomendado**: 30-50 imágenes
- **Método**: Selección aleatoria de diferentes splits (train/val/test)
- **Ejemplo**: `python seleccionar_muestra.py --total 30 --aleatorio`

### Paso 2: Ejecutar comparación de etiquetado

Ejecutar el script de comparación entre los dos anotadores:

```bash
python comparar_etiquetado.py --conjunto prueba --archivo1 anotador1.txt --archivo2 anotador2.txt
```

**Salida esperada**:
- Lista de imágenes con acuerdo
- Lista de imágenes con desacuerdo
- Porcentaje de concordancia
- Tipos de discrepancias identificadas

### Paso 3: Calcular métricas

Las siguientes métricas se calcularán automáticamente:

| Métrica | Fórmula | Umbral de aceptación |
|---------|---------|---------------------|
| **Exactitud simple** | Acuerdos / Total de imágenes | ≥ 80% |
| **Kappa de Cohen** | (Po - Pe) / (1 - Pe) | ≥ 0.61 (Substantial) |
| **Kappa de Fleiss** | (para >2 annotadores) | ≥ 0.61 (Substantial) |

### Paso 4: Revisar discrepancias

Para cada imagen con desacuerdo, aplicar el procedimiento de la Sección 3 de CITO-71-protocolo-anotacion.md:

1. Revisar las características del núcleo visualmente
2. Aplicar criterios de desempate (conservadurismo, evidencia, experticia)
3. Registrar en la hoja de concordancia
4. Designar decisión final

### Paso 4: Generar reporte

Ejecutar la generación automática de reporte:

```bash
python generar_reporte_concordancia.py --minimo 20
```

**El reporte debe incluir**:
- Número total de imágenes evaluadas
- Número de acuerdos y desacuerdos
- Kappa de Cohen y Kappa de Fleiss (si aplica)
- Porcentaje de concordancia
- Lista de casos borderline con comentarios
- Recomendaciones para mejora del protocolo

## 2. Hoja de Concordancia Simplificada

Para documentar discrepancias rápidamente, usar esta tabla:

| # | Imagen | Anotador A | Clase A | Anotador B | Clase B | Acuerdo | Decisión final | Motivo |
|---|--------|------------|---------|----------|---------|---------|----------------|--------|
| 1 | MUESTRA_001 | Ana | 0 Normal | Carlos | 0 Normal | ✅ | 0 Normal | - |
| 2 | MUESTRA_002 | Ana | 1 Anormal | Carlos | Normal | ❌ | Anormal | Criterio 3x |
| 3 | MUESTRA_003 | Ana | 2 Artefacto | Carlos | 2 Artefacto | ✅ | 2 Artefacto | - |
| 4 | MUESTRA_004 | Ana | Normal | Carlos | Anormal | ❌ | Revisar | Bordes poco claros |
| 5 | MUESTRA_005 | Ana | 1 Anormal | Carlos | 1 Anormal | ✅ | 1 Anormal | - |

**Leyenda**: ✅ = Acuerdo, ❌ = Discrepancia

## 3. Criterios de Desempate Rápidos

Para tomar decisiones rápidas cuando hay discrepancia:

### 3.1. Criterio de conservadurismo (predeterminado)
- **Si hay duda**: Clasificar como `1 Anormal`
- **Justificación**: Prioriza la sensibilidad (no perder núcleos sospechosos)
- **Cuándo aplicar**: Cuando las características visuales no son claras o son ambiguas

### 3.2. Criterio de evidencia visual
- **Examinar**: Tamaño, forma, bordes, textura del núcleo
- **Decidir**: La clase debe estar respaldada por características observables claras
- **Cuándo aplicar**: Cuando hay suficiente información visual para tomar una decisión segura

### 3.3. Criterio de revisor senior
- **Designar**: Un experto con más experiencia o credenciales
- **Decisión**: Su decisión es final en caso de no acuerdo
- **Cuándo aplicar**: Cuando los anotadores principiante/intermedio no pueden ponerse de acuerdo

## 4. Umbrales de Aceptación para Continuar

| Nivel de concordancia | Valor | Acción recomendada |
|----------------------|-------|-------------------|
| **Alta** | ≥ 0.81 (81%+) | Protocolo validado, continuar con nuevos splits |
| **Substantial** | 0.61 - 0.80 (61-80%) | Continuar con monitoreo continuo, revisar casos borderline |
| **Moderada** | 0.41 - 0.60 (41-60%) | Capacitación adicional, reevaluar definiciones de clase, volver a etiquetar muestra |
| **Baja** | ≤ 0.40 (≤40%) | Detener proceso, reevaluar protocolo y clases, considerar re-entrenamiento |

## 4. Ejemplo de Reporte de Concordancia

**Proyecto**: CitoCounter-Proto  
**Fecha**: 05/oct/2026  
**Anotadores**: Ana y Carlos  
**Conjunto de prueba**: 30 imágenes aleatorias de split train  

### Resultados

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| Imágenes evaluadas | 30 | - |
| Acuerdos | 24 | 80% de las imágenes |
| Desacuerdos | 6 | 20% de las imágenes |
| Exactitud simple | 0.80 | - |
| Kappa de Cohen | 0.65 | Substantial |
| Kappa de Fleiss | N/A | Solo 2 annotadores |

### Desacuerdos identificados

| Imagen | Clase A | Clase B | Decisión final | Motivo |
|--------|---------|---------|----------------|--------|
| MUESTRA_004 | 1 Anormal | 0 Normal | 1 Anormal | Criterio 3x aplicado; núcleo ligeramente grande pero cumple umbral |
| MUESTRA_007 | 1 Anormal | 2 Artefacto | 1 Anormal | Después de revisión, se identificaron características nucleares sutiles |
| MUESTRA_012 | 0 Normal | 2 Artefacto | 2 Artefacto | Claramente polvo/mancha, sin características nucleares |
| MUESTRA_019 | 1 Anormal | Normal | Normal | Revisión senior: decisión revertida, núcleo dentro de rango normal |
| MUESTRA_023 | 2 Artefacto | 1 Anormal | 1 Anormal | Decisión conservadora ante posible núcleo borderline |
| MUESTRA_028 | Normal | Anormal | Anormal | Criterio de conservadurismo aplicado |

### Recomendaciones

1. **Continuar** con el protocolo actual - concordancia substantial (0.65) es aceptable
2. **Capacitación breve** para anotadores en el criterio 3x (casos MUESTRA_004, MUESTRA_019)
3. **Monitoreo continuo** en splits posteriores para asegurar consistencia
4. **Actualizar guía** con ejemplos adicionales de casos borderline
5. **Considerar** agregar más ejemplos de entrenamiento para reducir discrepancias futuras

### Firma

**Anotador A**: _______________________ Fecha: _________  
**Anotador B**: _______________________ Fecha: _________  
**Revisor senior**: _______________________ Fecha: _________  

## 5. Integración con el flujo de trabajo

### 5.1. Antes de continuar con nuevos splits

Ejecutar validación de concordancia:

```bash
# Paso 1: Seleccionar muestra
python seleccionar_muestra.py --total 30 --aleatorio

# Paso 2: Comparar anotadores
python comparar_etiquetado.py --conjunto prueba

# Paso 3: Calcular métricas
python generar_reporte_concordancia.py --minimo 20

# Paso 4: Revisar y resolver discrepancias
# (Usar hoja de concordancia manual o automática)

# Paso 5: Verificar que Kappa ≥ 0.61
# Si no, aplicar mejoras y repetir
```

### 5.2. Después de validar

1. Firmar la hoja de concordancia
2. Actualizar Jira CSV CITO-71 con el estado y evidencia
3. Continuar con CITO-72 (validaciones de dataset mejoradas)
4. Documentar lecciones aprendidas en `docs/LECCIONES_APRENDIDAS.md`
5. Actualizar `src/contracts/pipeline_contract.py` si es necesario

## 6. Dependencias

| Dependencia | Estado | Comentario |
|-------------|--------|------------|
| **CITO-71 (protocolo)** | ✅ Completo | Documento creado en docs/CITO-71-protocolo-anotacion.md |
| **CITO-71 (guía)** | ✅ Completo | Documento creado en docs/CITO-71-guia-concordancia.md |
| **CITO-72** | ⏳ Pendiente | Validaciones de dataset dependen de esta validación |
| **J-03** | 🔄 En progreso | Dependencia técnica para activación de CITO-72 |

---

**Documento generado**: 05/oct/2026  
**Proyecto**: CitoCounter-Proto  
**Versión**: 1.0  
**Para**: Citotecnólogos y expertos en annotación