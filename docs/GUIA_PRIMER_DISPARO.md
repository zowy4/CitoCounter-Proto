# 🧪 Guía de "Primer Disparo" - Prueba de Humo

## Objetivo
Validar que el pipeline completo funciona ANTES de procesar imágenes reales del hospital.

---

## 📋 Checklist de Preparación

### 1. Descargar Imagen de Prueba
- **Fuente**: Google Images
- **Búsqueda**: `"Pap smear microscopy image"` o `"cervical cytology microscopy"`
- **Requisitos**:
  - ✅ Imagen con núcleos celulares visibles
  - ✅ Fondo relativamente limpio
  - ✅ Resolución mínima: 800×600 px
  - ✅ Formato: JPG o PNG

### 2. Guardar Imagen
```
CitoCounter_Proto/
└── data/
    └── raw/
        └── muestra_prueba.jpg  ← Guardar aquí
```

### 3. Verificar Entorno
```powershell
# Activar entorno virtual
cd "C:\Users\zowya\OneDrive\Escritorio\zowy\TALLER 1\Software\CitoCounter_Proto"
.\venv\Scripts\Activate.ps1

# Verificar instalación
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
```

---

## 🚀 Ejecutar Primera Prueba

```powershell
python main.py
```

---

## 🔍 Criterios de Evaluación

### A. Ventana "Filtro DoG (Bordes Detectados)"
**✅ ESPERADO (BUENO):**
- Imagen predominantemente NEGRA
- Bordes de núcleos en BLANCO BRILLANTE
- Contornos circulares/ovalados claros
- Fondo oscuro o gris muy oscuro

**❌ PROBLEMÁTICO (REQUIERE AJUSTE):**
- Imagen completamente gris → Sigmas muy cercanas
- Demasiado ruido blanco → Necesita reducción de ruido
- Bordes muy gruesos → Sigma2 muy alto
- Bordes muy tenues → Sigmas muy bajos o contraste pobre

### B. Ventana "Resultado Final"
**✅ ESPERADO (NORMAL para primera prueba SIN calibración):**
- Detecta ALGUNOS núcleos (puede ser impreciso)
- Muchos cuadros ROJOS (sobreestimación, esperado)
- Algunos falsos positivos de polvo/ruido (esperado)

**⚠️ ATENCIÓN SI:**
- NO detecta ninguna célula → Umbral DoG muy alto
- Detecta CIENTOS de objetos → Area_Minima muy baja
- Solo cajas verdes o solo rojas → Descalibración de áreas

### C. Panel Comparativo 2×2
**Tomar screenshot de esta ventana** para:
1. Documentar en bitácora como prueba T-001
2. Enviar para revisión
3. Comparar con pruebas futuras

---

## 📊 Registro en Bitácora

Después de la prueba, actualizar `bitacora_experimentos.csv`:

```csv
T-001,2025-11-18,14:30,muestra_prueba.jpg,3.0,5.0,300,3.0,50,[TOTAL],[NORMALES],[SOSPECHOSAS],[%],-,-,-/10,"[TUS OBSERVACIONES AQUÍ]","[Excelente/Buena/Regular/Mala]","[Qué ajustarás]","[Tu nombre]"
```

**Campos a completar manualmente:**
- Total de células detectadas (de la consola)
- Observaciones cualitativas (¿qué viste?)
- Calidad del DoG (tu evaluación visual)

---

## 📸 Capturas Requeridas

Guardar en `data/results/screenshots/`:

1. **`T-001_panel_2x2.png`** → Panel comparativo completo
2. **`T-001_dog_filter.png`** → Solo ventana de filtro DoG (para análisis detallado)
3. **`T-001_resultado.png`** → Solo ventana de resultado final

---

## 🎯 Interpretación de Resultados

### Escenario 1: "DoG se ve perfecto, pero detecta mal"
**Diagnóstico**: Problema de SEGMENTACIÓN, no de filtro  
**Solución**: Ajustar `UMBRAL_DOG` en `src/analysis.py`

### Escenario 2: "DoG se ve gris/ruidoso"
**Diagnóstico**: Sigmas incorrectas o imagen de baja calidad  
**Solución**: 
- Aumentar diferencia entre Sigma1 y Sigma2
- Activar `MEJORAR_CONTRASTE = True`

### Escenario 3: "Detecta todo como sospechoso"
**Diagnóstico**: `AREA_PROMEDIO_NUCLEO_NORMAL` muy baja (esperado en primera prueba)  
**Solución**: Esto se resuelve en la calibración con la Dra. Rangel

### Escenario 4: "No detecta nada"
**Diagnóstico**: Imagen demasiado diferente a lo esperado o sigmas muy altas  
**Solución**: Probar con otra imagen o reducir sigmas a 2.0 y 3.5

---

## ✅ Checklist Post-Prueba

- [ ] Ejecuté `python main.py` sin errores
- [ ] Guardé screenshot del panel 2×2
- [ ] Registré resultados en `bitacora_experimentos.csv`
- [ ] Evalué visualmente la calidad del filtro DoG
- [ ] Identifiqué al menos UN ajuste para la próxima prueba
- [ ] Guardé imágenes resultado en `data/results/`

---

## 📧 Reporte a Enviar

**Asunto**: [CitoCounter] Prueba de Humo T-001 Completada

**Contenido**:
```
Hola,

Completé la primera prueba de humo del sistema CitoCounter Proto.

RESULTADOS:
- Imagen usada: [Nombre]
- Células detectadas: [X]
- Calidad del filtro DoG: [Excelente/Buena/Regular/Mala]

OBSERVACIONES:
[Descripción de qué funcionó y qué necesita ajuste]

Adjunto screenshot del panel 2×2 para revisión.

Próximo paso: [Tu plan de ajuste]

Saludos,
[Tu nombre]
```

**Adjuntar**: Screenshot del panel comparativo

---

## 🔄 Siguiente Iteración

Según los resultados de T-001, ajustar UNO de estos parámetros:

| Si observas... | Ajustar... | Dirección |
|----------------|------------|-----------|
| DoG muy ruidoso | SIGMA1, SIGMA2 | Aumentar ambos |
| Bordes muy tenues | SIGMA1, SIGMA2 | Disminuir ambos |
| Muchos falsos positivos | AREA_MINIMA | Aumentar |
| No detecta células grandes | UMBRAL_DOG | Disminuir |

**REGLA DE ORO**: Cambiar UN parámetro a la vez para entender su efecto.

---

*Documento preparado: 2025-11-18*
