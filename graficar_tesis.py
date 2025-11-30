"""
graficar_tesis.py - Generador de Gráficas para BM5

DESCRIPCIÓN:
    Script automatizado para generar visualizaciones científicas de alta calidad
    a partir de los resultados experimentales almacenados en bitácora_experimentos.csv

SALIDA:
    - data/results/graficas_tesis/figura1_riesgo_por_muestra.png
    - data/results/graficas_tesis/figura2_correlacion.png

EJECUCIÓN:
    python graficar_tesis.py

REQUISITOS:
    - matplotlib (ya incluido en requirements.txt)
    - bitacora_experimentos.csv con datos previos

AUTORES:
    CitoCounter Proto v1.1 - 2024
"""

import csv
import matplotlib.pyplot as plt
import os
from datetime import datetime

ARCHIVO_BITACORA = "bitacora_experimentos.csv"
CARPETA_SALIDA = "data/results/graficas_tesis"

def leer_datos():
    """Lee el CSV y extrae las columnas necesarias."""
    datos = {
        "ids": [],
        "imagenes": [],
        "total_celulas": [],
        "riesgo_pct": [],
        "sigmas": []  # Tupla (s1, s2)
    }
    
    if not os.path.exists(ARCHIVO_BITACORA):
        print(f"❌ No se encontró {ARCHIVO_BITACORA}")
        return None

    with open(ARCHIVO_BITACORA, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Filtrar filas vacías o errores
                if not row['ID_Prueba']: 
                    continue
                
                datos['ids'].append(row['ID_Prueba'])
                datos['imagenes'].append(row['Imagen_Usada'])
                datos['total_celulas'].append(int(row['Total_Celulas_Detectadas']))
                datos['riesgo_pct'].append(float(row['Porcentaje_Riesgo']))
                datos['sigmas'].append(f"σ1={row['Sigma1']}, σ2={row['Sigma2']}")
            except ValueError:
                continue
                
    return datos

def graficar_riesgo_por_imagen(datos):
    """Figura 1: Porcentaje de Riesgo por Muestra."""
    plt.figure(figsize=(12, 6))
    
    # Crear barras
    barras = plt.bar(datos['ids'], datos['riesgo_pct'], color='#3498db', alpha=0.7)
    
    # Línea de referencia (ejemplo: 10% umbral crítico)
    plt.axhline(y=10, color='r', linestyle='--', label='Umbral Crítico (10%)')
    
    # Etiquetas
    plt.title('Porcentaje de Células Sospechosas por Experimento', fontsize=14)
    plt.xlabel('ID de Prueba', fontsize=12)
    plt.ylabel('% Riesgo Detectado', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Añadir valores sobre las barras
    for bar in barras:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.1f}%',
                 ha='center', va='bottom')
    
    plt.tight_layout()
    ruta = os.path.join(CARPETA_SALIDA, "figura1_riesgo_por_muestra.png")
    plt.savefig(ruta, dpi=300)
    print(f"✅ Gráfica guardada: {ruta}")
    plt.close()

def graficar_dispersion(datos):
    """Figura 2: Relación Total Células vs Riesgo."""
    plt.figure(figsize=(10, 6))
    
    plt.scatter(datos['total_celulas'], datos['riesgo_pct'], 
                c='green', alpha=0.6, s=100, edgecolors='black')
    
    plt.title('Correlación: Densidad Celular vs. Riesgo Detectado', fontsize=14)
    plt.xlabel('Total de Células en la Muestra', fontsize=12)
    plt.ylabel('% de Riesgo', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Etiquetar puntos interesantes (ej. riesgo alto)
    for i, txt in enumerate(datos['ids']):
        if datos['riesgo_pct'][i] > 12:  # Etiquetar solo los altos
            plt.annotate(txt, (datos['total_celulas'][i], datos['riesgo_pct'][i]),
                         xytext=(5, 5), textcoords='offset points')
    
    plt.tight_layout()
    ruta = os.path.join(CARPETA_SALIDA, "figura2_correlacion.png")
    plt.savefig(ruta, dpi=300)
    print(f"✅ Gráfica guardada: {ruta}")
    plt.close()

def main():
    print(f"📊 Generando gráficas para tesis desde {ARCHIVO_BITACORA}...")
    
    # Crear carpeta si no existe
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    
    datos = leer_datos()
    if datos and len(datos['ids']) > 0:
        graficar_riesgo_por_imagen(datos)
        graficar_dispersion(datos)
        print(f"\n✨ Proceso completado. Revisa la carpeta '{CARPETA_SALIDA}'")
    else:
        print("⚠️ No hay suficientes datos en la bitácora para graficar.")

if __name__ == "__main__":
    main()
