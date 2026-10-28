# CITO-94: Casos especiales

**Estado:** Parcial ✅ (mejoras implementadas, limitación fundamental DoG documentada)

CITO-94 reutiliza la implementación y evidencia de CITO-86, pues ambos
describen la mitigación de superposición celular, artefactos de tinción e
iluminación irregular.

La fuente técnica y las pruebas reproducibles están en
[evidencia-cito86-casos-especiales.md](evidencia-cito86-casos-especiales.md)
y `tests/test_cito86_casos_especiales.py`.

## Mejoras implementadas en esta sesión (CITO-94)

### 1. Máscara de borde asimétrica para imágenes reales (Papanicolaou/EDF)
- **Problema**: Los artefactos DoG en bordes izquierdo/inferior son muy fuertes y se extienden 900px+ (izq) y 500px+ (inf)
- **Solución**: Nueva función `crear_mascara_borde_asimetrica()` con anchos configurables por lado
- **Default**: 500px izquierda, 300px inferior, 100px superior/derecha
- **Integración**: Aplicada automáticamente en `analizar_nucleos()` para polaridad `nucleos-oscuros`

### 2. Watershed con filtrado por máscara
- **Problema**: Watershed en imagen enmascarada trata regiones negras como fondo, creando componentes gigantes
- **Solución**: `watershed_separar_nucleos()` ahora acepta parámetro `mascara` para filtrar resultados **después** de la segmentación
- **Integración**: `analizar_nucleos()` pasa máscara asimétrica para `metodo_separacion='watershed'`

### 3. Máximos locales con filtrado por máscara
- **Problema**: Máximos locales detectados en imagen enmascarada encuentran bordes de la máscara
- **Solución**: `_maximos_locales()` detecta en imagen original y filtra resultados por máscara
- **Integración**: `analizar_nucleos()` usa máscara asimétrica para `metodo_separacion='maximos_locales'`

### 4. HSV y CLAHE (ya existentes, validados)
- HSV segmentation: `segmentar_por_hsv()` con métodos `saturation`/`value`
- CLAHE auto: `mejorar_contraste(metodo="auto")` selecciona estrategia según contraste
- Filtro bilateral: `reducir_ruido(nivel="medio")` para ruido de alta frecuencia

## Limitación fundamental documentada (CITO-97)

**DoG no es adecuado para imágenes Papanicolaou/EDF 2048x1536** sin preprocesamiento avanzado que no existe actualmente:

| Métrica | Datos sintéticos | Imágenes reales (Papanicolaou/EDF) |
|---------|------------------|-----------------------------------|
| F1-Score | **0.9315** ✅ | **0.0000** ❌ |
| Precision | 1.0000 | 0.0000 |
| Recall | 0.8718 | 0.0000 |

### Causa raíz
Los **artefactos de borde del DoG dominan la respuesta** en imágenes reales:
- **Artefactos DoG en bordes**: 150-255 (dominan la imagen)
- **Núcleos reales**: 87-113 (respuesta más débil)
- **Extensión de artefactos**: 900px+ desde borde izquierdo, 500px+ desde inferior
- **Máscara asimétrica requerida**: >80% de la imagen (inviable)

### Evidencia experimental
```
MUESTRA_014: Basic=6, Watershed=111, MaxLoc=0 (TP=0 en todos)
MUESTRA_056: Basic=7, Watershed=83, MaxLoc=0 (TP=0 en todos)  
MUESTRA_001: Basic=34, Watershed=29, MaxLoc=0 (TP=0 en todos)
```

## Pruebas reproducibles
```bash
python -m pytest tests/test_cito86_casos_especiales.py tests/test_cito90_hsv.py tests/test_cito91_lotes.py -v
```
Resultado: 10 pruebas correctas (5 CITO-86 + 3 CITO-90 + 2 CITO-91).

## Conclusión
Las estrategias para casos especiales (watershed, HSV, CLAHE, bilateral, máscara asimétrica) están **implementadas y probadas**, pero la **limitación fundamental del DoG en imágenes reales Papanicolaou/EDF impide alcanzar métricas clínicas**. Para desbloquear CITO-95 (F1≥90% en imágenes reales) se requiere migración a Deep Learning (Cellpose/StarDist/U-Net).

## Evidencia relacionada
- [evidencia-cito86-casos-especiales.md](evidencia-cito86-casos-especiales.md) - Implementación base
- [evidencia-cito97-calibracion-dog.md](evidencia-cito97-calibracion-dog.md) - Calibración y limitación DoG
- [evidencia-cito95-validacion-congelada.md](evidencia-cito95-validacion-congelada.md) - Plan Deep Learning

**Fecha de actualización:** 2026-10-20
