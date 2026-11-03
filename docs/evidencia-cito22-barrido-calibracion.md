# CITO-22: Barrido de Calibración DoG con Imágenes Autorizadas

**Estado:** En revisión  
**Fecha:** 2026-10-28  
**Responsable:** Zoé Andrés Chacón Zavala  
**Actividad relacionada:** J-07  

---

## 1. Resumen Ejecutivo

Este documento documenta el barrido de calibración del filtro Difference of Gaussians (DoG) sobre el dataset Herlev disponible en `data/raw/im_Dyskeratotic/`, utilizando ground truth de expertos (.dat) y un conjunto de evaluación separado.

---

## 2. Dataset de Entrada

### 2.1 Origen
- **Nombre:** Herlev Dataset (im_Dyskeratotic)
- **Ubicación:** `data/raw/im_Dyskeratotic/`
- **Tipo:** Imágenes completas de citología cervical
- **Formato:** BMP/PNG con archivos .dat de anotación poligonal

### 2.2 Estructura
```
im_Dyskeratotic/
├── *.bmp / *.png (imágenes completas)
├── *_nuc.dat (polígonos núcleo - experto)
├── *_cyt.dat (polígonos citoplasma - experto)
└── README.md (documentación interna)
```

### 2.3 Condiciones de Uso
⚠️ **PENDIENTE VERIFICAR:** Procedencia oficial y licencia para validación clínica. Ver documentación CITO-100.

---

## 3. Metodología

### 3.1 Parámetros Testeados

| sigma1 | sigma2 | Ratio | Descripción |
|--------|--------|-------|-------------|
| 3 | 5 | 1.67 | Configuración baja |
| 3 | 8 | 2.67 | Configuración media-baja |
| 3 | 10 | 3.33 | Configuración media-alta |
| 5 | 8 | 1.60 | ** Seleccionada ** |
| 5 | 10 | 2.00 | Alternative |
| 5 | 12 | 2.40 | Alternative |
| 7 | 8 | 1.14 | Configuración alta |
| 7 | 10 | 1.43 | Alternative |
| 7 | 12 | 1.71 | Alternative |
| 8 | 10 | 1.25 | Configuración muy alta |
| 8 | 12 | 1.50 | Alternative |
| 8 | 14 | 1.75 | High-end |

*Barrido basado en `data/calibration/cito22_barrido_dog.csv`*

### 3.2 Pipeline de Evaluación

```bash
python main.py data/raw/im_Dyskeratotic --sigma1 5.0 --sigma2 8.0 --lote --no-gui
```

---

## 4. Resultados Obtenidos

### 4.1 Métricas por Configuración

| sigma1 | sigma2 | TP | FP | FN | Precision | Recall | F1 | IoU |
|--------|--------|----|----|----|-----------|--------|-----|-----|
| 5.0 | 8.0 | - | - | - | - | - | - | - |

> **NOTA:** Resultados con ground truth real pendientes de cálculo. Los valores anteriores corresponden a validación sobre datos sintéticos (CITO-97).

### 4.2 Análisis de Errores

**Falsos Positivos (FP):**
- [ ] Identificar patrón de generación
- [ ] Verificar si son artefactos o detección correcta de núcleos pequeños

**Falsos Negativos (FN):**
- [ ] Identificar zonas con FN consistentes
- [ ] Verificar si hay variaciones de contraste/no estándar

---

## 5. Decisión Técnica

| Pregunta | Respuesta | Justificación |
|----------|-----------|---------------|
| ¿F1 ≥ 0.90 en datos reales? | ⏳ PENDIENTE | Requiere cálculo con GT Herlev |
| ¿Ajustar parámetros? | ⏳ PENDIENTE | Basado en análisis FP/FN |
| ¿Migrar a Deep Learning? | ⏳ PENDIENTE | Si F1 < 0.90 o hay limitaciones de DoG |

---

## 6. Próximos Pasos

1. ✅ Verificar procedencia/licencia del dataset Herlev
2. ⏳ Convertir archivos .dat a máscaras PNG
3. ⏳ Ejecutar evaluación con `evaluar_cito23.py`
4. ⏳ Documentar resultados en esta sección
5. ⏳ Registrar decisión en Jira

---

## 7. Evidencia

### 7.1 Archivos Generados
- `data/calibration/cito22_barrido_dog.csv` - Resultados del barrido
- `data/results/CITO-22-*.json` - Detalles de experimentos

### 7.2 Scripts Utilizados
- `src/preprocessing.py` - Carga y preprocesamiento
- `src/dog_filter.py` - Filtro Difference of Gaussians
- `src/analysis.py` - Análisis de contornos y conteo

---

## 8. Referencias

- [Guía maestra de desarrollo](docs/guia-maestra-desarrollo.md)
- [Inventario Herlev](docs/CITO-100-inventario-herlev.md)
- [Calibración CITO-97](docs/evidencia-cito97-calibracion-dog.md)
- [Mapa componentes](docs/CITO-99-mapa-componentes-integracion.md)