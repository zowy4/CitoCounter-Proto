"""
demo_dataset.py - Demostración del Dataset CitoCounter v1.0

PROPÓSITO:
Visualizar cómo se ve una imagen del dataset con sus anotaciones YOLO,
para verificar que el proceso de etiquetado es correcto.

USO:
    python demo_dataset.py

MUESTRA:
    - La imagen original
    - Bounding boxes coloreados por clase
    - Estadísticas de objetos detectados
"""

import cv2
import os
import matplotlib.pyplot as plt
import numpy as np


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

DATASET_DIR = 'CitoDataset_v1'
IMAGEN_DEMO = os.path.join(DATASET_DIR, 'images', 'train', 'IMG_001.jpg')
ETIQUETA_DEMO = os.path.join(DATASET_DIR, 'labels', 'train', 'IMG_001.txt')

# Colores para cada clase (BGR para OpenCV)
COLORES_CLASE = {
    0: (0, 255, 0),      # Verde - Normal
    1: (0, 0, 255),      # Rojo - Anormal
    2: (255, 165, 0)     # Naranja - Artefacto
}

NOMBRES_CLASE = {
    0: 'Normal',
    1: 'Anormal',
    2: 'Artefacto'
}


# ============================================================================
# FUNCIONES
# ============================================================================

def leer_anotaciones_yolo(ruta_txt, ancho_img, alto_img):
    """
    Lee archivo .txt en formato YOLO y convierte a coordenadas absolutas.
    
    Formato YOLO: clase x_centro y_centro ancho alto (normalizado 0-1)
    Retorna: lista de (clase, x1, y1, x2, y2) en píxeles absolutos
    """
    anotaciones = []
    
    if not os.path.exists(ruta_txt):
        print(f"⚠️  No se encontró archivo de etiquetas: {ruta_txt}")
        return anotaciones
    
    with open(ruta_txt, 'r') as f:
        for linea in f:
            if not linea.strip():
                continue
            
            partes = linea.strip().split()
            clase = int(partes[0])
            x_centro = float(partes[1])
            y_centro = float(partes[2])
            ancho = float(partes[3])
            alto = float(partes[4])
            
            # Convertir de coordenadas normalizadas a píxeles
            x_centro_px = x_centro * ancho_img
            y_centro_px = y_centro * alto_img
            ancho_px = ancho * ancho_img
            alto_px = alto * alto_img
            
            # Calcular esquinas del bounding box
            x1 = int(x_centro_px - ancho_px / 2)
            y1 = int(y_centro_px - alto_px / 2)
            x2 = int(x_centro_px + ancho_px / 2)
            y2 = int(y_centro_px + alto_px / 2)
            
            anotaciones.append((clase, x1, y1, x2, y2))
    
    return anotaciones


def dibujar_anotaciones(imagen, anotaciones):
    """
    Dibuja bounding boxes en la imagen según las anotaciones.
    """
    imagen_anotada = imagen.copy()
    
    for clase, x1, y1, x2, y2 in anotaciones:
        color = COLORES_CLASE.get(clase, (255, 255, 255))
        nombre = NOMBRES_CLASE.get(clase, f'Clase {clase}')
        
        # Dibujar rectángulo
        cv2.rectangle(imagen_anotada, (x1, y1), (x2, y2), color, 2)
        
        # Dibujar etiqueta
        texto = f'{nombre}'
        (ancho_texto, alto_texto), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        
        # Fondo para el texto
        cv2.rectangle(imagen_anotada, 
                     (x1, y1 - alto_texto - 10), 
                     (x1 + ancho_texto + 5, y1), 
                     color, -1)
        
        # Texto
        cv2.putText(imagen_anotada, texto, (x1 + 2, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return imagen_anotada


def generar_estadisticas(anotaciones):
    """
    Genera estadísticas de las anotaciones.
    """
    conteo = {0: 0, 1: 0, 2: 0}
    
    for clase, _, _, _, _ in anotaciones:
        conteo[clase] = conteo.get(clase, 0) + 1
    
    return conteo


def crear_visualizacion_completa(imagen_original, imagen_anotada, estadisticas):
    """
    Crea un panel completo con la imagen original, anotada y estadísticas.
    """
    # Convertir de BGR a RGB para matplotlib
    img_original_rgb = cv2.cvtColor(imagen_original, cv2.COLOR_BGR2RGB)
    img_anotada_rgb = cv2.cvtColor(imagen_anotada, cv2.COLOR_BGR2RGB)
    
    # Crear figura
    fig = plt.figure(figsize=(16, 8))
    
    # Imagen original
    ax1 = plt.subplot(1, 2, 1)
    ax1.imshow(img_original_rgb)
    ax1.set_title('Imagen Original', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    # Imagen con anotaciones
    ax2 = plt.subplot(1, 2, 2)
    ax2.imshow(img_anotada_rgb)
    ax2.set_title('Imagen con Anotaciones YOLO', fontsize=14, fontweight='bold')
    ax2.axis('off')
    
    # Agregar leyenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=(0, 1, 0), label=f'Normal: {estadisticas[0]} objetos'),
        Patch(facecolor=(1, 0, 0), label=f'Anormal: {estadisticas[1]} objetos'),
        Patch(facecolor=(1, 0.65, 0), label=f'Artefacto: {estadisticas[2]} objetos')
    ]
    ax2.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    plt.tight_layout()
    
    return fig


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta la demostración."""
    
    print("=" * 70)
    print("  📊 DEMOSTRACIÓN DEL DATASET CitoCounter v1.0")
    print("  Visualización de Anotaciones en Formato YOLO")
    print("=" * 70)
    print()
    
    # Verificar que existan los archivos
    if not os.path.exists(IMAGEN_DEMO):
        print(f"❌ No se encontró la imagen: {IMAGEN_DEMO}")
        print("   Por favor, agrega al menos una imagen al dataset.")
        return
    
    if not os.path.exists(ETIQUETA_DEMO):
        print(f"⚠️  No se encontró el archivo de etiquetas: {ETIQUETA_DEMO}")
        print("   La imagen se mostrará sin anotaciones.")
    
    # Cargar imagen
    print(f"📂 Cargando imagen: {IMAGEN_DEMO}")
    imagen = cv2.imread(IMAGEN_DEMO)
    
    if imagen is None:
        print(f"❌ Error al cargar la imagen.")
        return
    
    alto, ancho = imagen.shape[:2]
    print(f"   Dimensiones: {ancho} x {alto} píxeles")
    
    # Leer anotaciones
    print(f"📋 Leyendo anotaciones: {ETIQUETA_DEMO}")
    anotaciones = leer_anotaciones_yolo(ETIQUETA_DEMO, ancho, alto)
    print(f"   Total de objetos anotados: {len(anotaciones)}")
    
    # Generar estadísticas
    estadisticas = generar_estadisticas(anotaciones)
    print()
    print("📊 ESTADÍSTICAS DE ANOTACIONES:")
    print(f"   ├─ Clase 0 (Normal):    {estadisticas[0]} objetos")
    print(f"   ├─ Clase 1 (Anormal):   {estadisticas[1]} objetos")
    print(f"   └─ Clase 2 (Artefacto): {estadisticas[2]} objetos")
    print()
    
    # Dibujar anotaciones
    print("🎨 Dibujando anotaciones...")
    imagen_anotada = dibujar_anotaciones(imagen, anotaciones)
    
    # Crear visualización
    print("📈 Generando visualización...")
    fig = crear_visualizacion_completa(imagen, imagen_anotada, estadisticas)
    
    # Guardar resultado
    output_path = 'data/results/demo_dataset_anotaciones.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"💾 Visualización guardada en: {output_path}")
    
    # Mostrar
    print()
    print("=" * 70)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("=" * 70)
    print()
    print("📌 INTERPRETACIÓN:")
    print("   - Verde:   Células normales (núcleo < 3x promedio)")
    print("   - Rojo:    Células anormales (núcleo ≥ 3x promedio)")
    print("   - Naranja: Artefactos (manchas, polvo, no células)")
    print()
    print("📝 NOTA: Las anotaciones actuales son ejemplos simulados.")
    print("   Para datos reales, usa LabelImg siguiendo GUIA_LABELIMG.md")
    print()
    
    plt.show()


if __name__ == "__main__":
    main()
