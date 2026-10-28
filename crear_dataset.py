"""
crear_dataset.py - Herramienta de Estandarización de Datos

DESCRIPCIÓN:
    Script automatizado para organizar, renombrar y catalogar imágenes de microscopía
    en un formato estandarizado para análisis científico y reproducibilidad.

FUNCIONALIDADES:
    - Renombrado secuencial automático (MUESTRA_001, MUESTRA_002, ...)
    - Verificación de integridad de imágenes
    - Conversión a formato JPG estándar (calidad 95%)
    - Generación de índice CSV con metadata
    - Preservación de nombres originales en registro

ESTRUCTURA DE SALIDA:
    data/raw/MUESTRA_001.jpg, MUESTRA_002.jpg, ...
    data/dataset_index.csv (catálogo maestro)

USO:
    1. Crear carpeta "mis_imagenes_nuevas" en raíz del proyecto
    2. Copiar imágenes desordenadas allí
    3. Ejecutar: python crear_dataset.py
    4. Las imágenes se organizarán automáticamente

AUTORES:
    CitoCounter Proto v1.1 - 2024
"""

import os
import shutil
import cv2
import csv
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
CARPETA_ORIGEN = "mis_imagenes_nuevas"  # ¡Pon aquí tus fotos desordenadas!
CARPETA_DESTINO = "data/raw"
PREFIJO_ARCHIVO = "MUESTRA"             # Resultado: MUESTRA_001.jpg
FORMATO_SALIDA = ".jpg"
ARCHIVO_INDICE = "data/dataset_index.csv"

def inicializar_dataset():
    """Crea las carpetas y el CSV si no existen."""
    Path(CARPETA_DESTINO).mkdir(parents=True, exist_ok=True)
    
    # Crear CSV si no existe
    if not os.path.exists(ARCHIVO_INDICE):
        with open(ARCHIVO_INDICE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID_Imagen", "Nombre_Original", "Fecha_Agregado", "Resolucion", "Etiqueta_Inicial"])

def obtener_siguiente_numero():
    """Busca cuál es el siguiente número disponible (ej. 005)."""
    existentes = list(Path(CARPETA_DESTINO).glob(f"{PREFIJO_ARCHIVO}_*{FORMATO_SALIDA}"))
    if not existentes:
        return 1
    
    # Extraer números: MUESTRA_005.jpg -> 5
    numeros = []
    for archivo in existentes:
        try:
            num = int(archivo.stem.split('_')[1])
            numeros.append(num)
        except:
            continue
    
    return max(numeros) + 1 if numeros else 1

def procesar_imagenes():
    print(f"🔄 Iniciando creación de dataset desde: {CARPETA_ORIGEN}")
    
    origen = Path(CARPETA_ORIGEN)
    if not origen.exists():
        print(f"❌ La carpeta origen '{CARPETA_ORIGEN}' no existe. Créala y pon tus imágenes ahí.")
        return

    inicializar_dataset()
    contador = obtener_siguiente_numero()
    imagenes_procesadas = 0

    # Extensiones válidas
    exts = ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff', '*.bmp']
    archivos = []
    for ext in exts:
        archivos.extend(origen.glob(ext))
        archivos.extend(origen.glob(ext.upper()))

    if not archivos:
        print("⚠️ No se encontraron imágenes en la carpeta de origen.")
        return

    print(f"📸 Encontradas {len(archivos)} imágenes. Procesando...")

    with open(ARCHIVO_INDICE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        for archivo in archivos:
            try:
                # 1. Leer imagen para verificar integridad y obtener metadata
                img = cv2.imread(str(archivo))
                if img is None:
                    print(f"   ⚠️ Saltando archivo corrupto: {archivo.name}")
                    continue
                
                alto, ancho = img.shape[:2]
                resolucion = f"{ancho}x{alto}"

                # 2. Generar nuevo nombre estandarizado
                nuevo_nombre = f"{PREFIJO_ARCHIVO}_{contador:03d}{FORMATO_SALIDA}"
                ruta_final = os.path.join(CARPETA_DESTINO, nuevo_nombre)

                # 3. Copiar y convertir (asegurar formato JPG estándar)
                cv2.imwrite(ruta_final, img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

                # 4. Registrar en el índice CSV
                writer.writerow([
                    nuevo_nombre,
                    archivo.name,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    resolucion,
                    "Sin Clasificar"  # Etiqueta por defecto
                ])

                print(f"   ✅ {archivo.name} -> {nuevo_nombre}")
                contador += 1
                imagenes_procesadas += 1
                
            except Exception as e:
                print(f"   ❌ Error con {archivo.name}: {e}")

    print("-" * 50)
    print(f"🎉 Dataset actualizado exitosamente.")
    print(f"📁 Imágenes agregadas: {imagenes_procesadas}")
    print(f"📍 Ubicación: {CARPETA_DESTINO}")
    print(f"📋 Índice: {ARCHIVO_INDICE}")

if __name__ == "__main__":
    procesar_imagenes()
