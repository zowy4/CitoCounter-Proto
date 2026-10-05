# Protocolo de Anotación y Doble Revisión Experta (CITO-71)

## Propósito

Definir el protocolo estandarizado para el etiquetado de núcleos celulares en citología cervical, establecer clases, instrucciones de anotación, mecanismos de resolución de discrepancias y procedimientos para calcular la concordancia entre anotadores. Este protocolo asegura la reproducibilidad y calidad del dataset CitoDataset_v1.

## 1. Clases de Etiquetado

Las siguientes clases están definidas para el dataset YOLO (`CitoDataset_v1`):

| ID | Clase | Descripción | Criterios de inclusión |
|----|-------|-------------|------------------------|
| 0 | **Normal** | Núcleo regular, tamaño dentro del rango esperado, citoplasma mínimo | Nuclei con contornos lisos, tamaño uniforme, sin características de sospecha |
| 1 | **Anormal** | Núcleo que cumple o supera el criterio de referencia 3x (área 3x el umbral); equivalente a sospechoso, **no a diagnóstico** | Nuclei con aumento de tamaño, variación en la forma, bordes irregulares, relación tamaño/área ≥ 3x el umbral de riesgo |
| 2 | **Artefacto** | Polvo, manchas, burbujas o estructuras que no son células | Elementos no biológicos, partículas de polvo, artefactos de tinción, burbujas de aire |

**Nota importante:** La clase "Anormal" indica sospecha y requiere revisión experta, pero **no equivale a un diagnóstico clínico**. El protocolo debe incluir el mensaje de no diagnóstico en todas las salidas.

## 2. Instrucciones de Anotación

### 2.1. Flujo de trabajo por imagen

1. **Abrir imagen** en LabelImg configurado para formato YOLO
2. **Dibujar caja** (tecla `W`) ajustada alrededor del núcleo celular, minimizando espacio vacío
3. **Seleccionar clase**:
   - `0 Normal` si el núcleo tiene tamaño y características normales
   - `1 Anormal` si el núcleo cumple el criterio 3x (área ≥ 3x umbral de riesgo)
   - `2 Artefacto` si el elemento es polvo, mancha, burbuja o no es célula
4. **Guardar** con `Ctrl+S`
5. **Avanzar** con tecla `D` a la siguiente imagen
6. **Repetir** hasta completar el split (train/val/test)

### 2.2. Atajos útiles

- `A`: Imagen anterior
- `Del`: Eliminar caja seleccionada
- `Ctrl+Z`: Deshacer última acción
- `Mayús+D`: Avanzar sin guardar (para imágenes sin núcleos relevantes)

### 2.3. Reglas de calidad

- **Etiquetar todos los núcleos visibles** que entren en el protocolo de análisis
- **No etiquetar objetos parciales** si el protocolo los excluye (mínimo 10% de la imagen visible)
- **No mezclar clases por conveniencia** ni etiquetar citoplasma
- **Revisar muestras ambiguas** con un segundo experto (doble revisión)
- **No usar metadatos clínicos identificables** en nombres de archivo o anotaciones
- **Mantener consistencia** en el umbral de área (≥ 3x) durante todo el proceso de etiquetado

### 2.4. Validación previa al envío

Ejecutar el validador antes de finalizar cada split:

```bash
python validar_consistencia_dataset.py
```

El validador debe comprobar:
- Imágenes y etiquetas emparejadas
- Clases válidas (solo 0, 1, 2)
- Splits completos (train/val/test con el número correcto de imágenes)
- Ausencia de metadatos identificables

## 3. Resolución de Discrepancias entre Anotadores

Cuando dos o más expertos etiquetan la misma imagen y hay discrepancias en la clase asignada:

### 3.1. Procedimiento de revisión

1. **Identificar discrepancias**: Ejecutar comparación entre archivos de etiquetado
   ```bash
   python comparar_etiquetado.py --imagen IMG_001 --annotator1 annotator1.txt --annotator2 annotator2.txt
   ```

2. **Clasificar el tipo de discrepancia**:
   - **Diferencia de clase**: Mismo núcleo etiquetado como distinto (ej. Normal vs Anormal)
   - **Diferencia de ubicación**: Caja delimitadora en posiciones diferentes
   - **Diferencia de cantidad**: Un anotador etiquetó más núcleos que el otro

3. **Resolver discrepancias de clase**:
   - **Caso A**: Ambos anotadores coinciden después de revisión → Aplicar la decisión consenso
   - **Caso B**: Persiste la discrepancia → Aplicar criterio de experticia:
     - Si hay duda, etiquetar como `1 Anormal` (conservador, prioriza sensibilidad)
     - Si las características son claras, seguir la definición de clase en la Sección 1
   - **Caso C**: Discrepancia técnica (artefacto vs núcleo) → Designar como `2 Artefacto`

3. **Documentar la resolución**:
   - Registrar la discrepancia en la hoja de concordancia
   - Anotar la decisión tomada y el motivo
   - Firmar ambos anotadores (o designar un revisor senior si no hay acuerdo)

### 3.2. Hoja de concordancia

Para cada imagen con discrepancias, completar:

| Imagen | Anotador 1 | Clase Anotador 1 | Anotador 2 | Clase Anotador 2 | Decisión final | Motivo | Revisor senior (opcional) |
|--------|------------|------------------|------------|------------------|----------------|--------|--------------------------|
| IMG_001 | A | 1 Anormal | B | Normal | Anormal | Criterio 3x aplicado | -- |
| IMG_002 | A | Artefacto | B | Normal | Revisar | Bordes poco claros | Dr. Pérez |

### 3.3. Criterios de desempate

1. **Criterio de conservadurismo**: Ante duda, clasificar como `1 Anormal`
2. **Criterio de evidencia visual**: La clase debe estar respaldada por características observables claras (tamaño, forma, textura)
3. **Criterio de experticia**: Si un anotador tiene mayor experiencia o credenciales, su decisión pesa más (documentar esta jerarquía)
4. **Criterio de revisor senior**: En caso de no acuerdo, un revisor senior toma la decisión final

## 4. Cálculo de Concordancia Inter-Anotador

### 4.1. Métricas reportadas

Después de la doble revisión de un conjunto de muestra (mínimo 20 imágenes), reportar:

| Métrica | Fórmula | Interpretación |
|---------|---------|----------------|
| **Exactitud simple (Simple Accuracy)** | $N_{acuerdo} / N_{total}$ | Proporción de imágenes donde ambos anotadores están de acuerdo |
| **Kappa de Cohen** | $P_o - P_e / 1 - P_e$ | Corrección de la exactitud simple por el acuerdo esperado por azar |
| **Kappa de Fleiss** | (para >2 anotadores) | Extensión de Cohen para múltiples evaluadores |

Donde:
- $N_{acuerdo}$ = número de imágenes con acuerdo entre anotadores
- $N_{total}$ = número total de imágenes evaluadas
- $P_o$ = proporción de observaciones concordantes
- $P_e$ = proporción de concordancia esperada por azar

### 4.2. Umbrales de aceptación

| Concordancia | Interpretación | Acción |
|--------------|----------------|--------|
| **≥ 0.81** | Casi perfecta | Protocolo validado, continuar |
| **0.61 - 0.80** | Substantial | Revisar casos borderline, continuar con monitoreo |
| **0.41 - 0.60** | Moderada | Capacitación adicional, reevaluar definiciones de clase |
| **≤ 0.40** | Baja | Detener proceso, reevaluar protocolo y clases |

### 4.2. Muestra de concordancia (Ejemplo)

**Conjunto de prueba**: 30 imágenes seleccionadas al azar del split de entrenamiento

| Imagen | Anotador A | Anotador B | Acuerdo | Comentario |
|--------|------------|------------|---------|------------|
| MUESTRA_001 | 0 Normal | 0 Normal | ✅ | - |
| MUESTRA_002 | 1 Anormal | 1 Anormal | ✅ | - |
| MUESTRA_003 | 2 Artefacto | 2 Artefacto | ✅ | - |
| MUESTRA_004 | 1 Anormal | 0 Normal | ❌ | Revisar criterio 3x |
| MUESTRA_005 | 1 Anormal | 1 Anormal | ✅ | - |
| ... | ... | ... | ... | ... |
| **Total** | **24/30** | **24/30** | **80%** | **Substantial** |

**Resultado Kappa de Cohen**: 0.65 (Substantial)

**Conclusión**: El protocolo de anotación tiene concordancia substantial. Se validó el procedimiento y se pueden continuar con los siguientes splits con monitoreo continuo.

### 4.3. Reporte de concordancia

Generar reporte automático:

```bash
python generar_reporte_concordancia.py --conjunto prueba --minimo 20
```

El reporte debe incluir:
- Número total de imágenes evaluadas
- Número de acuerdos y desacuerdos
- Métricas de Kappa (Cohen y/o Fleiss)
- Porcentaje de concordancia
- Casos borderline o de discrepancia
- Recomendaciones para mejora del protocolo

## 5. Entregables de CITO-71

### 5.1. Documentos creados

- `docs/CITO-71-protocolo-anotacion.md` - Protocolo completo (este documento)
- `docs/CITO-71-guia-concordancia.md` - Guía rápida de concordancia y resolución de discrepancias

### 5.2. Evidencia de validación

- Reporte de Kappa de Cohen ≥ 0.61 (Substantial) en conjunto de prueba de 30+ imágenes
- Hoja de concordancia completada para todas las discrepancias identificadas
- Acta de revisión del protocolo firmada por los anotadores involucrados

### 5.3. Actualización de infraestructura

- Actualizar `src/contracts/pipeline_contract.py` con nuevos contratos de anotación si es necesario
- Añadir validaciones adicionales a `validar_consistencia_dataset.py` para verificar consistencia de doble revisión
- Documentar en `README.md` los procedimientos de anotación y concordancia

## 6. Dependencias y Relaciones

| Dependencia | Estado | Comentario |
|-------------|--------|------------|
| **CITO-68** | ✅ Hecho | Alcance clínico definido, incluye "no diagnóstico" |
| **CITO-69** | ✅ Hecho | Privacidad y anonimización completadas |
| **CITO-70** | ✅ En curso | Splits de dataset definidos (70/20/10) |
| **J-03** | 🔄 En progreso | Dependencia activa para CITO-71 |
| **CITO-72** | ⏳ Pendiente | Validaciones de dataset dependen de CITO-71 |
| **CITO-41** | ✅ Listo | Etiquetado de imágenes completado (02/oct/26) |

## 7. Próximos pasos

1. **Ejecutar doble revisión** en conjunto de 30 imágenes seleccionadas al azar
2. **Calcular Kappa de Cohen** y reportar resultados
3. **Resolver discrepancias** usando los criterios de la Sección 3.2
4. **Actualizar Jira CSV** CITO-71 al estado apropiado
5. **Hand-off** a CITO-72 (validaciones de dataset mejoradas)
6. **Continuar** con CITO-73+ según roadmap

---

**Documento generado**: 05/oct/2026  
**Autor**: Zoé Andrés Chacón Zavala  
**Proyecto**: CitoCounter-Proto  
**Versión**: 1.0  
**Revisado por**: _________________ (Firma del revisor senior)