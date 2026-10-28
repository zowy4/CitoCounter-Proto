import cv2
import numpy as np
import sys
sys.path.insert(0, 'src')
from preprocessing import cargar_imagen, segmentar_por_hsv, preprocesar_imagen

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
print(f'Preprocesado HSV: imagen_proc shape={imagen_proc.shape}, dtype={imagen_proc.dtype}')
print(f'  - usar_hsv activado en pipeline: True')
print(f'  - imagen original shape: {imagen_original.shape}')

print('\n✅ Test HSV completado exitosamente')