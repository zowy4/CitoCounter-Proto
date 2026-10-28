import csv
import os

# Leer el dataset index existente
with open('data\sintetico\dataset_index.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

# Agregar nuevas imágenes sintéticas (SINTETICA_006 a SINTETICA_015)
# Las 001-005 son de "calibracion", las 011-015 serán de "evaluacion"
# Las 006-010 serán de "evaluacion" con sigma variables

nueva_fila_template = "SINTETICA_{id:03d}.png,SINTETICA_{id:03d}.png,evaluacion,{nucleos}"

# Agregar SINTETICA_006 a SINTETICA_010 (sigma 5.0-7.0, nucleos variables)
for i in range(6, 11):
    nucleos = 14 + (i - 6)  # 14, 15, 16, 17, 18
    nueva_fila = nueva_fila_template.format(id=i, nucleos=nucleos)
    rows.append([nueva_fila])

# Agregar SINTETICA_011 a SINTETICA_015 (sigma 8.0-9.2, nucleos variables)
for i in range(11, 16):
    nucleos = 16 + (i - 11)  # 16, 17, 18, 19, 20
    nueva_fila = nueva_fila_template.format(id=i, nucleos=nucleos)
    rows.append([nueva_fila])

# Escribir el dataset actualizado
with open('data\sintetico\dataset_index.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print('✅ Dataset index actualizado')
print(f'Total de imágenes: {len(rows) - 1} (excluyendo header)')

# Mostrar contenido
with open('data\sintetico\dataset_index.csv', 'r', encoding='utf-8') as f:
    print('\\nContenido actualizado:')
    print(f.read())