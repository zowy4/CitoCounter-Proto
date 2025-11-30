# 📦 Zona de Importación de Imágenes

Esta carpeta es la "bandeja de entrada" para nuevas imágenes del microscopio.

## 🎯 ¿Cómo usarla?

1. **Copia aquí** todas tus imágenes desordenadas (no importa el nombre actual)
2. **Ejecuta** el script de organización:
   ```powershell
   python crear_dataset.py
   ```
3. Las imágenes se **mueven automáticamente** a `data/raw/` con nombres estandarizados

## ✅ Formatos Aceptados

- JPG / JPEG
- PNG
- TIF / TIFF
- BMP

## 📋 Resultado

Tus imágenes serán:
- ✨ Renombradas secuencialmente: `MUESTRA_001.jpg`, `MUESTRA_002.jpg`, ...
- 📁 Movidas a: `data/raw/`
- 📊 Catalogadas en: `data/dataset_index.csv`
- ✓ Verificadas y convertidas a JPG de alta calidad

## 🚀 Ejemplo

**ANTES (en esta carpeta):**
```
IMG_20231105_paciente1.png
foto_microscopio_v2.jpg
scan_cervical_001.tif
```

**DESPUÉS (en data/raw/):**
```
MUESTRA_001.jpg
MUESTRA_002.jpg
MUESTRA_003.jpg
```

---

💡 **Tip:** Esta carpeta se vacía automáticamente después de procesar las imágenes.
