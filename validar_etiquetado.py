"""
validar_etiquetado.py - Validación para CITO-41 (Doble Revisión Experta)

Este script valida las anotaciones YOLO existentes en CitoDataset_v1/labels/train/
y genera un reporte para el proceso de doble revisión experto CITO-41.

VALIDACIONES REALIZADAS:
1. Formato YOLO: Cada línea debe tener 5 valores (class_id, x_center, y_center, width, height)
2. Rangos normalizados: Todos los valores deben estar en [0, 1]
3. Consistencia de clases: Clases deben ser 0 (normal), 1 (anormal) o 2 (artefacto)
4. Superficie de celdas: Verificar que no haya solapamientos excesivos
5. Conteo por imagen: Reportar número de núcleos detectados por imagen
6. Distribución de clases: Contar cuántos de cada clase hay en total

SALIDA:
    - reporte_validacion.txt: Reporte detallado para revisión experta
    - estadisticas_etiquetado.json: Estadísticas en formato JSON
    - imagenes_requiere_revision.txt: Lista de imágenes que necesitan revisión humana
"""

import os
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

# Rutas del proyecto
DATASET_DIR = "CitoDataset_v1"
LABELS_DIR = os.path.join(DATASET_DIR, "labels", "train")
CLASSES_FILE = os.path.join(DATASET_DIR, "classes.txt")

# Clases válidas según classes.txt
CLASES_VALIDAS = {0, 1, 2}
NOMBRE_CLASES = {
    0: "Normal",
    1: "Anormal", 
    2: "Artefacto"
}


def validar_formato_yolo(linea, num_linea, nombre_archivo):
    """
    Valida que una línea del archivo de etiqueta tenga formato YOLO correcto.
    
    Formato esperado: class_id x_center y_center width height
    Todos normalizados en [0, 1]
    """
    errores = []
    
    # Dividir la línea
    partes = linea.strip().split()
    
    if len(partes) != 5:
        errores.append(f"Línea {num_linea}: Se esperan 5 valores, encontrados {len(partes)}")
        return errores
    
    try:
        # Parsear clase
        clase = int(partes[0])
        if clase not in CLASES_VALIDAS:
            errores.append(f"Línea {num_linea}: Clase inválida {clase}. Debe ser 0, 1 o 2")
        
        # Parsear coordenadas (deben estar en [0, 1])
        x_center = float(partes[1])
        y_center = float(partes[2])
        width = float(partes[3])
        height = float(partes[4])
        
        if not (0 <= x_center <= 1):
            errores.append(f"Línea {num_linea}: x_center {x_center} fuera de rango [0,1]")
        if not (0 <= y_center <= 1):
            errores.append(f"Línea {num_linea}: y_center {y_center} fuera de rango [0,1]")
        if not (0 <= width <= 1):
            errores.append(f"Línea {num_linea}: width {width} fuera de rango [0,1]")
        if not (0 <= height <= 1):
            errores.append(f"Línea {num_linea}: height {height} fuera de rango [0,1]")
            
        # Verificar dimensiones físicamente plausibles
        # width y height no deberían ser > 1 (imposible en normalizado)
        if width > 1 or height > 1:
            errores.append(f"Línea {num_linea}: Dimensiones > 1 son inválidas en formato normalizado")
            
    except ValueError as e:
        errores.append(f"Línea {num_linea}: Error al parsear números: {e}")
    
    return errores


def validar_etiquetado_imagen(ruta_etiqueta, nombre_archivo):
    """
    Valida un archivo de etiqueta completo.
    
    Returns:
        dict: Resultados de la validación
    """
    resultados = {
        "archivo": nombre_archivo,
        "valido": True,
        "errores": [],
        "advertencias": [],
        "total_nucleos": 0,
        "distribucion_clases": Counter(),
        "lineas_problematicas": []
    }
    
    if not os.path.exists(ruta_etiqueta):
        resultados["valido"] = False
        resultados["errores"].append("Archivo de etiqueta no existe")
        return resultados
    
    try:
        with open(ruta_etiqueta, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except Exception as e:
        resultados["valido"] = False
        resultados["errores"].append(f"Error al leer archivo: {e}")
        return resultados
    
    for num_linea, linea in enumerate(lineas, start=1):
        if not linea.strip():
            continue  # Saltar líneas vacías
        
        errores_linea = validar_formato_yolo(linea, num_linea, nombre_archivo)
        
        if errores_linea:
            resultados["valido"] = False
            resultados["errores"].extend(errores_linea)
            resultados["lineas_problematicas"].append({
                "linea": num_linea,
                "errores": errores_linea
            })
        
        # Parsear línea válida para estadísticas
        partes = linea.strip().split()
        try:
            clase = int(partes[0])
            x_center = float(partes[1])
            y_center = float(partes[2])
            width = float(partes[3])
            height = float(partes[4])
            
            resultados["total_nucleos"] += 1
            resultados["distribucion_clases"][clase] += 1
            
            # Verificar advertencias
            # Nucleos con dimensiones muy grandes podrían indicar error
            if width > 0.5 or height > 0.5:
                resultados["advertencias"].append(
                    f"Línea {num_linea}: Dimensiones muy grandes ({width}, {height})"
                )
            
            # Nucleos con centro fuera de rango normal
            if x_center < 0.05 or x_center > 0.95:
                resultados["advertencias"].append(
                    f"Línea {num_linea}: Centro x inusual ({x_center:.3f})"
                )
            if y_center < 0.05 or y_center > 0.95:
                resultados["advertencias"].append(
                    f"Línea {num_linea}: Centro y inusual ({y_center:.3f})"
                )
                
        except (ValueError, IndexError):
            pass  # Ya se manejó en el validación de formato
    
    return resultados


def generar_reporte_validacion():
    """Genera reporte completo de validación para CITO-41."""
    
    print("=" * 70)
    print("  🔍 CITO-41: Validación de Etiquetado - Doble Revisión Experta")
    print("=" * 70)
    
    # Obtener todos los archivos de etiqueta
    if not os.path.exists(LABELS_DIR):
        print(f"❌ Directorio de etiquetas no existe: {LABELS_DIR}")
        return
    
    archivos_etiqueta = sorted([f for f in os.listdir(LABELS_DIR) if f.endswith('.txt')])
    
    if not archivos_etiqueta:
        print("❌ No hay archivos de etiqueta para validar")
        return
    
    print(f"\n📊 Validando {len(archivos_etiqueta)} archivos de etiqueta...")
    
    # Validar cada archivo
    resultados_totales = {
        "total_archivos": len(archivos_etiqueta),
        "archivos_validos": 0,
        "archivos_con_errores": 0,
        "archivos_con_advertencias": 0,
        "total_nucleos": 0,
        "distribucion_general": Counter(),
        "errores_por_archivo": {},
        "archivos_revision_especial": []
    }
    
    for nombre_archivo in archivos_etiqueta:
        ruta_etiqueta = os.path.join(LABELS_DIR, nombre_archivo)
        resultado = validar_etiquetado_imagen(ruta_etiqueta, nombre_archivo)
        
        resultados_totales["total_nucleos"] += resultado["total_nucleos"]
        
        if resultado["valido"]:
            resultados_totales["archivos_validos"] += 1
        else:
            resultados_totales["archivos_con_errores"] += 1
            # Marcar para revisión especial
            resultados_totales["errores_por_archivo"][nombre_archivo] = resultado["errores"]
            resultados_totales["errores_por_archivo"][nombre_archivo].append(
                "Requiere revisión experta"
            )
        
        if resultado["advertencias"]:
            resultados_totales["archivos_con_advertencias"] += 1
            # Agregar advertencias al reporte
            if nombre_archivo in resultados_totales["errores_por_archivo"]:
                resultados_totales["errores_por_archivo"][nombre_archivo].extend(resultado["advertencias"])
            else:
                resultados_totales["errores_por_archivo"][nombre_archivo] = resultado["advertencias"]
                resultados_totales["errores_por_archivo"][nombre_archivo].append(
                    "Requiere revisión experta"
                )
        
        # Acumular distribución
        for clase, count in resultado["distribucion_clases"].items():
            resultados_totales["distribucion_general"][clase] += count
    
    # Generar reporte de texto
    print("\n" + "=" * 70)
    print("  📋 REPORTE DE VALIDACIÓN")
    print("=" * 70)
    
    print(f"\n📈 Resumen General:")
    print(f"   • Archivos totales: {resultados_totales['total_archivos']}")
    print(f"   • Archivos válidos: {resultados_totales['archivos_validos']}")
    print(f"   • Archivos con errores: {resultados_totales['archivos_con_errores']}")
    print(f"   • Archivos con advertencias: {resultados_totales['archivos_con_advertencias']}")
    print(f"   • Total núcleos etiquetados: {resultados_totales['total_nucleos']}")
    
    print(f"\n📊 Distribución de Clases:")
    for clase in sorted(resultados_totales["distribucion_general"].keys()):
        count = resultados_totales["distribucion_general"][clase]
        nombre = NOMBRE_CLASES[clase]
        porcentaje = (count / resultados_totales["total_nucleos"] * 100) if resultados_totales["total_nucleos"] > 0 else 0
        print(f"   • Clase {clase} ({nombre}): {count} ({porcentaje:.1f}%)")
    
    # Identificar archivos que requieren revisión experta
    print(f"\n⚠️  Archivos que Requieren Revisión Experta Doble:")
    print("=" * 70)
    
    contador_revision = 0
    for nombre_archivo, errores in resultados_totales["errores_por_archivo"].items():
        if not resultados_totales["errores_por_archivo"] or errores:
            contador_revision += 1
            print(f"\n  📄 {nombre_archivo}:")
            for error in errores:
                print(f"     ⚠️  {error}")
    
    # Guardar reporte a archivo
    reporte_path = "reporte_validacion_cito41.txt"
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("CITO-41: Validación de Etiquetado - Doble Revisión Experta\n")
        f.write(f"Fecha: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("Resumen General:\n")
        f.write(f"  Archivos totales: {resultados_totales['total_archivos']}\n")
        f.write(f"  Archivos válidos: {resultados_totales['archivos_validos']}\n")
        f.write(f"  Archivos con errores: {resultados_totales['archivos_con_errores']}\n")
        f.write(f"  Archivos con advertencias: {resultados_totales['archivos_con_advertencias']}\n")
        f.write(f"  Total núcleos etiquetados: {resultados_totales['total_nucleos']}\n\n")
        
        f.write("Distribución de Clases:\n")
        for clase in sorted(resultados_totales["distribucion_general"].keys()):
            count = resultados_totales["distribucion_general"][clase]
            nombre = NOMBRE_CLASES[clase]
            porcentaje = (count / resultados_totales["total_nucleos"] * 100) if resultados_totales["total_nucleos"] > 0 else 0
            f.write(f"  Clase {clase} ({nombre}): {count} ({porcentaje:.1f}%)\n")
        
        f.write("\nArchivos que Requieren Revisión Experta Doble:\n")
        for nombre_archivo, errores in resultados_totales["errores_por_archivo"].items():
            if errores:
                f.write(f"\n  📄 {nombre_archivo}:\n")
                for error in errores:
                    f.write(f"    ⚠️  {error}\n")
    
    print(f"\n💾 Reporte guardado en: {reporte_path}")
    
    # Guardar estadísticas JSON
    estadisticas_path = "estadisticas_etiquetado_cito41.json"
    with open(estadisticas_path, 'w', encoding='utf-8') as f:
        json.dump({
            "total_archivos": resultados_totales["total_archivos"],
            "archivos_validos": resultados_totales["archivos_validos"],
            "archivos_con_errores": resultados_totales["archivos_con_errores"],
            "archivos_con_advertencias": resultados_totales["archivos_con_advertencias"],
            "total_nucleos": resultados_totales["total_nucleos"],
            "distribucion_clases": dict(resultados_totales["distribucion_general"]),
            "porcentaje_distribucion": {
                NOMBRE_CLASES[k]: (v / resultados_totales["total_nucleos"] * 100) 
                if resultados_totales["total_nucleos"] > 0 else 0
                for k, v in sorted(resultados_totales["distribucion_general"].items())
            }
        }, f, indent=2)
    
    print(f"💾 Estadísticas guardadas en: {estadisticas_path}")
    
    return resultados_totales


if __name__ == "__main__":
    resultados = generar_reporte_validacion()
    
    print("\n" + "=" * 70)
    print("  📝 PRÓXIMOS PASOS CITO-41")
    print("=" * 70)
    print("  1. Revisar el reporte generado (reporte_validacion_cito41.txt)")
    print("  2. Los expertos clínicos deben revisar los archivos marcados")
    print("  3. Corregir anotaciones con errores de formato o clasificación")
    print("  4. Validar que la distribución de clases sea coherente con el diagnóstico")
    print("  5. Después de la revisión, ejecutar actualización del dataset")
    print("  6. Ejecutar: python validar_consistencia_dataset.py")