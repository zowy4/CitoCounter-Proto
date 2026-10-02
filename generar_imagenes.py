import cv2
import numpy as np
import os

# Crear directorio para nuevas imágenes
os.makedirs('data/raw', exist_ok=True)

# Generar 5 imágenes sintéticas adicionales con diferentes condiciones
# SINTETICA_006 a SINTETICA_010 con sigma1=5.0, sigma2=6.0 (diferente al baseline)
# Y SINTETICA_011 a SINTETICA_015 con sigma1=8.0, sigma2=9.0 y polaridad nucleos-oscuros

for i in range(6, 11):
    # Imagen sintética con gaussian blur y DoG
    sigma1 = 5.0 + (i - 6) * 0.5
    sigma2 = sigma1 + 1.0
    
    # Crear imagen con ruido gaussiano y blobs simulados
    img = np.random.normal(128, 20, (1024, 1024, 3)).astype(np.uint8)
    
    # Aplicar filtro DoG simulado (suavizado con dos sigmas diferentes)
    img_blur1 = cv2.GaussianBlur(img, (0, 0), sigma1)
    img_blur2 = cv2.GaussianBlur(img, (0, 0), sigma2)
    dog = img_blur1.astype(np.float32) - img_blur2.astype(np.float32)
    
    # Normalizar a 0-255
    dog = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # Guardar imagen
    nombre = f'data/raw/SINTETICA_{i:03d}.png'
    cv2.imwrite(nombre, dog)
    print(f'Generada: {nombre} con sigma1={sigma1}, sigma2={sigma2}')

# Generar 5 imágenes con sigma más alto y polaridad oscura
for i in range(11, 16):
    sigma1 = 8.0 + (i - 11) * 0.3
    sigma2 = sigma1 + 1.2
    
    img = np.random.normal(128, 20, (1024, 1024, 3)).astype(np.uint8)
    img_blur1 = cv2.GaussianBlur(img, (0, 0), sigma1)
    img_blur2 = cv2.GaussianBlur(img, (0, 0), sigma2)
    dog = img_blur1.astype(np.float32) - img_blur2.astype(np.float32)
    dog = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    nombre = f'data/raw/SINTETICA_{i:03d}.png'
    cv2.imwrite(nombre, dog)
    print(f'Generada: {nombre} con sigma1={sigma1:.1f}, sigma2={sigma2:.1f}')

print('\n✅ Imágenes sintéticas adicionales generadas')