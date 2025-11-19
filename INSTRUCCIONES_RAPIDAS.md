# 🎯 INSTRUCCIONES RÁPIDAS - Primer Disparo

## Objetivo Inmediato
Ejecutar la primera prueba con una imagen de Papanicolaou de internet para validar que el sistema funciona **ANTES** de usar imágenes reales del hospital.

---

## ✅ Checklist Rápido (5 minutos)

### [ ] 1. Verificar Instalación
```powershell
cd "C:\Users\zowya\OneDrive\Escritorio\zowy\TALLER 1\Software\CitoCounter_Proto"
python verificar_entorno.py
```

**Esperado:** Ver todos ✓ en verde  
**Si hay errores:** Ejecutar `pip install -r requirements.txt`

---

### [ ] 2. Descargar Imagen de Prueba

**Opción A - Google Images:**
1. Buscar: `"Pap smear microscopy image"` o `"cervical cytology high resolution"`
2. Descargar una imagen con núcleos visibles
3. Guardar como: `data/raw/muestra_prueba.jpg`

**Opción B - Recursos académicos:**
- NIH Image Gallery
- PubMed Central (artículos con imágenes)
- Atlas de Citología online

**Requisitos de la imagen:**
- ✅ Formato: JPG o PNG
- ✅ Mínimo: 800×600 píxeles
- ✅ Debe tener células con núcleos visibles
- ✅ NO usar dibujos/esquemas (necesitamos fotos reales)

---

### [ ] 3. Ejecutar Primera Prueba
```powershell
python main.py
```

**Duración:** ~5-10 segundos

---

### [ ] 4. Observar Resultados

Se abrirán 2-3 ventanas:

#### **Ventana 1: "Filtro DoG (Bordes Detectados)"**
**✅ BUENO:** Imagen negra con bordes blancos brillantes  
**❌ MALO:** Imagen gris/ruidosa

#### **Ventana 2: "Resultado Final"**
**✅ ESPERADO:** Algunas cajas verdes/rojas (puede ser impreciso)  
**⚠️ NORMAL:** Muchas cajas rojas (descalibración esperada)

#### **Ventana 3: "Panel Comparativo Completo"**
**📸 CAPTURAR ESTA VENTANA** (Win+Shift+S)

---

### [ ] 5. Registrar Observaciones

Editar `bitacora_experimentos.csv` (última línea):
- **Calidad_DoG:** ¿Excelente/Buena/Regular/Mala?
- **Observaciones_Cualitativas:** ¿Qué viste?
  - Ejemplo: "DoG detectó bordes bien. Detectó 45 células, pero muchas son polvo."

---

### [ ] 6. Guardar Screenshot

Guardar en `data/results/screenshots/`:
- `T-001_panel_comparativo.png`

---

## 📧 Qué Enviar

**Asunto:** [CitoCounter] Primera Prueba T-001

**Contenido:**
```
Resultados de la primera prueba de humo:

- Células detectadas: [X]
- Calidad del filtro DoG: [Excelente/Buena/Regular/Mala]
- Observaciones: [Describir brevemente lo que viste]

Adjunto: Screenshot del panel 2×2

Próximo paso propuesto: [Qué ajustarás]
```

**Adjunto:** Screenshot del panel comparativo

---

## 🔍 Interpretación Rápida

| Lo que ves | Qué significa | Acción |
|------------|---------------|---------|
| DoG negra con bordes blancos nítidos | ✅ Filtro funciona bien | Pasar a calibración |
| DoG muy gris/ruidosa | ⚠️ Sigmas incorrectas | Ajustar SIGMA1/SIGMA2 |
| Detecta 0 células | ❌ Problema de umbralización | Revisar UMBRAL_DOG |
| Detecta cientos de células | ⚠️ Detecta ruido como células | Aumentar AREA_MINIMA |
| Solo cajas rojas | ⚠️ AREA_PROMEDIO muy baja | Esperar calibración real |

---

## ⏭️ Próximos Pasos

### Si TODO salió bien:
1. ✅ Probar con 2-3 imágenes más de internet
2. ✅ Documentar cada prueba (T-002, T-003)
3. ✅ Coordinar con la Dra. Rangel para obtener imágenes reales

### Si hubo problemas:
1. ⚠️ Revisar `docs/GUIA_PRIMER_DISPARO.md` (guía detallada)
2. ⚠️ Ajustar parámetros según la tabla de interpretación
3. ⚠️ Ejecutar `python analizar_bitacora.py` para diagnóstico

---

## 🆘 Problemas Comunes

### "No se encontró la imagen"
→ Verifica que `data/raw/muestra_prueba.jpg` existe

### "ModuleNotFoundError: No module named 'cv2'"
→ Ejecuta: `pip install opencv-python`

### Ventanas no se muestran
→ Presiona cualquier tecla para que aparezcan

### CSV no se actualiza
→ Cierra Excel/Google Sheets si está abierto

---

## 💡 Recordatorios

- 🎯 **Objetivo:** Ver si el filtro DoG funciona, NO obtener detecciones perfectas
- 📊 **Documentar TODO:** Cada prueba es un dato para la tesis
- 🔬 **Un parámetro a la vez:** No cambies Sigma1 Y Sigma2 simultáneamente
- 📸 **Screenshots son clave:** Necesitarás las imágenes para el documento final

---

## ⏱️ Tiempo Estimado

- Descargar imagen: ~2 min
- Ejecutar prueba: ~10 seg
- Observar resultados: ~3 min
- Documentar: ~5 min

**TOTAL: ~10 minutos**

---

*¡Buena suerte con la primera prueba! 🚀*
