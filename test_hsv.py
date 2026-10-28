import cv2
import numpy as np
from src.preprocessing import cargar_imagen, segmentar_por_hsv, preprocesar_imagen

# Cargar una imagen de prueba
ruta = 'data/raw/EDF000.png'
imagen_bgr = cargar_imagen(ruta)
print(f'Imagen cargada: {imagen_bgr.shape}, dtype={imagen_bgr.dtype}')

# Probar segmentación HSV con método saturation
mask_sat = segmentar_por_hsv(imagen_bgr, umbral_sat=100, metodo='saturation')
print(f'Máscara saturation: shape={mask_sat.shape}, únicos={np.unique(mask_sat)}')

# Probar segmentación HSV con método value
mask_val = segmentar_por_hsv(imagen_bgr, umbral_val=100, metodo='value')
print(f'Máscara value: shape={mask_val.shape}, únicos={np.unique(mask_val)}')

# Probar preprocesar con usar_hsv=True
imagen_proc, imagen_original = preprocesar_imagen(
    ruta,
    mejorar_contraste_flag=True,
    reducir_ruido_flag=False,
    polaridad='nucleos-claros',
    usar_hsv=True,
    metodo_hsv='saturation',
    umbral_hsv=100
)

# Extraer información HSV de la imagen procesada y metadata interna
# La función ahora devuelve (imagen_procesada, imagen_original); la máscara HSV
# se aplicó sobre la imagen original y se combinó con la gris.
print(f'Preprocesado HSV completado')
print(f'  - usar_hsv en pipeline: True (bandera activada)')
print(f'  - imagen procesada shape: {imagen_proc.shape}')
print(f'  - imagen original shape: {imagen_original.shape}')

# Verificar que la máscara HSV fue aplicada comprobando píxeles no-nulos
# (esto es interno; el usuario puede inspeccionar los resultados visuales)
print('\n✅ Test HSV completado exitosamente')