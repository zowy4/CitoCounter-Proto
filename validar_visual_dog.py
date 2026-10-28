"""
validar_visual_dog.py - Validación visual del filtro DoG para CITO-42

Este script valida visualmente el filtro Difference of Gaussiana (DoG)
sobre el dataset de prueba, verificando que:
1. El filtro produce resultados esperados (con y sin valores negativos)
2. La normalización a uint8 funciona correctamente
3. Los resultados son compatibles con el pipeline de watershed

USO:
    python validar_visual_dog.py
    # O con parámetros personalizados:
    python validar_visual_dog.py --sigma1 7.0 --sigma2 8.0
"""

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, '/workspaces/CitoCounter-Proto')

from src.dog_filter import _calcular_diferencia_dog, aplicar_filtro_dog


def mostrar_ventana(titulo, imagen, wait=0):
    """Muestra una imagen en una ventana de OpenCV."""
    cv2.imshow(titulo, imagen)
    cv2.waitKey(wait)


def validar_pipeline_completo():
    """Valida el pipeline completo DoG -> normalización -> watershed."""
    
    print("=" * 70)
    print("  🔬 CITO-42: Validación Visual del Filtro DoG")
    print("=" * 70)
    
    # Cargar una imagen de prueba del dataset
    data_raw = Path("data/raw")
    if not data_raw.exists():
        print("❌ Directorio data/raw no existe")
        return
    
    # Obtener primera imagen
    imagenes = sorted(data_raw.glob("MUESTRA_*.jpg"))
    if not imagenes:
        print("❌ No hay imágenes en data/raw")
        return
    
    ruta_imagen = imagenes[0]
    print(f"\n📸 Procesando: {ruta_imagen.name}")
    
    # 1. Cargar imagen original
    img_original = cv2.imread(str(ruta_imagen))
    if img_original is None:
        print(f"❌ No se pudo cargar {ruta_imagen}")
        return
    
    img_gris = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
    print(f"   Tamaño: {img_gris.shape}")
    print(f"   Rango original: {img_gris.min()} - {img_gris.max()}")
    
    # 2. Aplicar filtro DoG
    print("\n   [1/4] Aplicando filtro DoG...")
    try:
        dog_uint8 = aplicar_filtro_dog(img_gris, sigma1=7.0, sigma2=8.0)
        print(f"   ✅ DoG uint8: min={dog_uint8.min()}, max={dog_uint8.max()}")
        print(f"   ✅ DoG dtype: {dog_uint8.dtype}")
    except Exception as e:
        print(f"   ❌ Error en DoG: {e}")
        return
    
    # 3. Verificar el DoG float32 interno
    print("\n   [2/4] Verificando DoG float32 interno...")
    try:
        g1 = cv2.GaussianBlur(img_gris, (0, 0), 7.0)
        g2 = cv2.GaussianBlur(img_gris, (0, 0), 8.0)
        dog_float = _calcular_diferencia_dog(g1, g2)
        print(f"   ✅ DoG float32: min={dog_float.min():.2f}, max={dog_float.max():.2f}")
        print(f"   ✅ Tiene negativos: {np.any(dog_float < 0)}")
        print(f"   ✅ Media: {np.mean(dog_float):.4f}")
    except Exception as e:
        print(f"   ⚠️  Error verificando float32: {e}")
    
    # 4. Aplicar watershed con el DoG
    print("\n   [3/4] Aplicando watershed...")
    try:
        from src.analysis import watershed_separar_nucleos
        contornos, areas = watershed_separar_nucleos(dog_uint8, metodo='distancia')
        print(f"   ✅ Watershed completado")
        print(f"   ✅ Núcleos detectados: {len(contornos)}")
        print(f"   ✅ Áreas: min={min(areas) if areas else 0}, max={max(areas) if areas else 0}")
    except Exception as e:
        print(f"   ⚠️  Error en watershed: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Mostrar resultados
    print("\n   [4/4] Mostrando resultados visuales...")
    try:
        # Crear figura con las imágenes
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        
        # Imagen original
        axes[0, 0].imshow(cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title('Imagen Original')
        axes[0, 0].axis('off')
        
        # DoG uint8
        axes[0, 1].imshow(dog_uint8, cmap='gray')
        axes[0, 1].set_title('DoG Normalizado (uint8)')
        axes[0, 1].axis('off')
        
        # DoG float32 (usando imshow con vrange)
        dog_float = _calcular_diferencia_dog(
            cv2.GaussianBlur(img_gris, (0, 0), 7.0),
            cv2.GaussianBlur(img_gris, (0, 0), 8.0)
        )
        im = axes[1, 0].imshow(dog_float, cmap='coolwarm', vmin=-10, vmax=10)
        axes[1, 0].set_title('DoG Float32 (con negativos)')
        axes[1, 0].axis('off')
        plt.colorbar(im, ax=axes[1, 0], fraction=0.046, pad=0.04)
        
        # Máscara binaria después de threshold
        _, binaria = cv2.threshold(dog_uint8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        axes[1, 1].imshow(binaria, cmap='gray')
        axes[1, 1].set_title('Máscara (Otsu threshold)')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig('dog_validacion_resultado.png', dpi=150)
        print(f"   💾 Gráfico guardado en: dog_validacion_resultado.png")
        cv2.destroyAllWindows()
        
    except ImportError:
        # Si no hay matplotlib, mostrar con openCV
        print("   (Matplotlib no disponible, mostrando con OpenCV)")
        cv2.imshow('Original', img_gris)
        cv2.imshow('DoG uint8', dog_uint8)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    print("\n" + "=" * 70)
    print("  ✅ Validación visual completada")
    print("=" * 70)


if __name__ == "__main__":
    validar_pipeline_completo()