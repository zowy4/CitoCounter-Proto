"""
validar_consistencia_dataset.py - Validador de Integridad del Dataset

PROPÓSITO:
Verificar que el dataset CitoDataset_v1 esté completo y coherente antes de usarlo
para entrenamiento o validación.

VALIDACIONES:
1. Matching imagen-etiqueta: Cada .jpg debe tener su .txt
2. Matching imagen-CSV: Cada ID_Imagen debe existir como archivo
3. Coherencia de clases: Diagnósticos graves deben tener etiquetas de clase 1
4. Distribución: Train/Val tienen proporciones similares

USO:
    python validar_consistencia_dataset.py

SALIDA:
    Reporte de validación con OK/ERROR para cada criterio
"""

import os
import pandas as pd
from pathlib import Path


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

DATASET_DIR = 'CitoDataset_v1'
IMAGES_TRAIN = os.path.join(DATASET_DIR, 'images', 'train')
IMAGES_VAL = os.path.join(DATASET_DIR, 'images', 'val')
LABELS_TRAIN = os.path.join(DATASET_DIR, 'labels', 'train')
LABELS_VAL = os.path.join(DATASET_DIR, 'labels', 'val')
METADATA_CSV = os.path.join(DATASET_DIR, 'metadata', 'clinical_data_synthetic.csv')
CLASSES_FILE = os.path.join(DATASET_DIR, 'classes.txt')


# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def validar_estructura_directorios():
    """Verifica que existan todos los directorios necesarios."""
    print("=" * 70)
    print("1️⃣  VALIDACIÓN DE ESTRUCTURA DE DIRECTORIOS")
    print("=" * 70)
    
    directorios_requeridos = [
        DATASET_DIR,
        IMAGES_TRAIN,
        IMAGES_VAL,
        LABELS_TRAIN,
        LABELS_VAL,
        os.path.dirname(METADATA_CSV)
    ]
    
    errores = []
    for directorio in directorios_requeridos:
        if os.path.exists(directorio):
            print(f"   ✓ {directorio}")
        else:
            print(f"   ✗ FALTA: {directorio}")
            errores.append(directorio)
    
    if not os.path.exists(CLASSES_FILE):
        print(f"   ⚠️  ADVERTENCIA: No existe {CLASSES_FILE}")
    else:
        print(f"   ✓ {CLASSES_FILE}")
    
    print()
    return len(errores) == 0


def obtener_imagenes(directorio):
    """Obtiene lista de imágenes en un directorio."""
    if not os.path.exists(directorio):
        return []
    extensiones_validas = ['.jpg', '.jpeg', '.png', '.tif', '.tiff']
    imagenes = [f for f in os.listdir(directorio) 
                if os.path.splitext(f)[1].lower() in extensiones_validas]
    return sorted(imagenes)


def obtener_etiquetas(directorio):
    """Obtiene lista de archivos .txt en un directorio."""
    if not os.path.exists(directorio):
        return []
    etiquetas = [f for f in os.listdir(directorio) if f.endswith('.txt')]
    return sorted(etiquetas)


def validar_matching_imagen_etiqueta():
    """Verifica que cada imagen tenga su archivo de etiqueta."""
    print("=" * 70)
    print("2️⃣  VALIDACIÓN DE MATCHING IMAGEN-ETIQUETA")
    print("=" * 70)
    
    errores = []
    
    # Validar TRAIN
    print("\n📁 Conjunto de ENTRENAMIENTO:")
    imgs_train = obtener_imagenes(IMAGES_TRAIN)
    lbls_train = obtener_etiquetas(LABELS_TRAIN)
    
    print(f"   Imágenes encontradas: {len(imgs_train)}")
    print(f"   Etiquetas encontradas: {len(lbls_train)}")
    
    for img in imgs_train:
        nombre_base = os.path.splitext(img)[0]
        etiqueta_esperada = nombre_base + '.txt'
        
        if etiqueta_esperada not in lbls_train:
            print(f"   ✗ FALTA ETIQUETA: {img} → {etiqueta_esperada}")
            errores.append(('train', img))
        else:
            # Verificar que el archivo de etiqueta no esté vacío
            ruta_etiqueta = os.path.join(LABELS_TRAIN, etiqueta_esperada)
            if os.path.getsize(ruta_etiqueta) == 0:
                print(f"   ⚠️  ETIQUETA VACÍA: {etiqueta_esperada}")
    
    if len(imgs_train) > 0 and len(errores) == 0:
        print(f"   ✓ Todas las {len(imgs_train)} imágenes tienen etiquetas")
    
    # Validar VAL
    print("\n📁 Conjunto de VALIDACIÓN:")
    imgs_val = obtener_imagenes(IMAGES_VAL)
    lbls_val = obtener_etiquetas(LABELS_VAL)
    
    print(f"   Imágenes encontradas: {len(imgs_val)}")
    print(f"   Etiquetas encontradas: {len(lbls_val)}")
    
    errores_val_inicial = len(errores)
    for img in imgs_val:
        nombre_base = os.path.splitext(img)[0]
        etiqueta_esperada = nombre_base + '.txt'
        
        if etiqueta_esperada not in lbls_val:
            print(f"   ✗ FALTA ETIQUETA: {img} → {etiqueta_esperada}")
            errores.append(('val', img))
        else:
            ruta_etiqueta = os.path.join(LABELS_VAL, etiqueta_esperada)
            if os.path.getsize(ruta_etiqueta) == 0:
                print(f"   ⚠️  ETIQUETA VACÍA: {etiqueta_esperada}")
    
    if len(imgs_val) > 0 and len(errores) == errores_val_inicial:
        print(f"   ✓ Todas las {len(imgs_val)} imágenes tienen etiquetas")
    
    print()
    return len(errores) == 0, (len(imgs_train), len(imgs_val))


def validar_matching_csv():
    """Verifica que cada ID_Imagen en CSV tenga su archivo."""
    print("=" * 70)
    print("3️⃣  VALIDACIÓN DE MATCHING CSV-IMÁGENES")
    print("=" * 70)
    
    if not os.path.exists(METADATA_CSV):
        print(f"   ✗ No se encontró {METADATA_CSV}")
        print()
        return False
    
    # Cargar CSV
    df = pd.read_csv(METADATA_CSV)
    print(f"   Registros en CSV: {len(df)}")
    
    if 'ID_Imagen' not in df.columns:
        print("   ✗ CSV no tiene columna 'ID_Imagen'")
        print()
        return False
    
    # Obtener todas las imágenes del dataset
    imgs_train = obtener_imagenes(IMAGES_TRAIN)
    imgs_val = obtener_imagenes(IMAGES_VAL)
    todas_imagenes = set([os.path.splitext(img)[0] for img in imgs_train + imgs_val])
    
    print(f"   Imágenes en dataset: {len(todas_imagenes)}")
    
    # Verificar que cada ID_Imagen exista como archivo
    errores = []
    for idx, row in df.iterrows():
        id_imagen = row['ID_Imagen']
        if id_imagen not in todas_imagenes:
            print(f"   ✗ CSV tiene '{id_imagen}' pero no existe el archivo")
            errores.append(id_imagen)
    
    # Verificar el inverso: que cada imagen tenga su entrada en CSV
    ids_en_csv = set(df['ID_Imagen'].values)
    for img_id in todas_imagenes:
        if img_id not in ids_en_csv:
            print(f"   ⚠️  Imagen '{img_id}' existe pero no está en CSV")
    
    if len(errores) == 0:
        print("   ✓ Todos los ID_Imagen del CSV existen como archivos")
    
    print()
    return len(errores) == 0


def validar_coherencia_diagnosticos():
    """Verifica coherencia entre diagnósticos y etiquetas."""
    print("=" * 70)
    print("4️⃣  VALIDACIÓN DE COHERENCIA DIAGNÓSTICO-ETIQUETAS")
    print("=" * 70)
    
    if not os.path.exists(METADATA_CSV):
        print("   ⚠️  No se puede validar sin CSV de metadatos")
        print()
        return True  # No es error crítico
    
    df = pd.read_csv(METADATA_CSV)
    
    # Revisar casos con diagnósticos graves
    diagnosticos_graves = ['LSIL', 'HSIL', 'ASC-US']
    casos_graves = df[df['Diagnostico_Ref_Bethesda'].isin(diagnosticos_graves)]
    
    print(f"   Casos con diagnósticos graves: {len(casos_graves)}")
    
    if len(casos_graves) == 0:
        print("   ✓ No hay casos graves para validar")
        print()
        return True
    
    # Para cada caso grave, verificar que tenga etiquetas de clase 1
    advertencias = []
    for idx, row in casos_graves.iterrows():
        id_imagen = row['ID_Imagen']
        diagnostico = row['Diagnostico_Ref_Bethesda']
        
        # Buscar el archivo de etiqueta
        ruta_label_train = os.path.join(LABELS_TRAIN, f"{id_imagen}.txt")
        ruta_label_val = os.path.join(LABELS_VAL, f"{id_imagen}.txt")
        
        ruta_label = None
        if os.path.exists(ruta_label_train):
            ruta_label = ruta_label_train
        elif os.path.exists(ruta_label_val):
            ruta_label = ruta_label_val
        
        if ruta_label is None:
            print(f"   ⚠️  {id_imagen} ({diagnostico}): Falta archivo de etiqueta")
            advertencias.append(id_imagen)
            continue
        
        # Leer etiquetas
        with open(ruta_label, 'r') as f:
            lineas = f.readlines()
        
        clases_detectadas = set([int(linea.split()[0]) for linea in lineas if linea.strip()])
        
        # Esperar que haya al menos una clase 1 (Anormal)
        if 1 not in clases_detectadas:
            print(f"   ⚠️  {id_imagen} ({diagnostico}): No tiene etiquetas de clase 1 (Anormal)")
            advertencias.append(id_imagen)
    
    if len(advertencias) == 0:
        print("   ✓ Casos graves tienen etiquetas coherentes")
    else:
        print(f"   ⚠️  {len(advertencias)} casos con posible incoherencia")
    
    print()
    return len(advertencias) == 0


def validar_distribucion_train_val(num_train, num_val):
    """Verifica que la división Train/Val sea razonable."""
    print("=" * 70)
    print("5️⃣  VALIDACIÓN DE DISTRIBUCIÓN TRAIN/VAL")
    print("=" * 70)
    
    total = num_train + num_val
    
    if total == 0:
        print("   ⚠️  No hay imágenes en el dataset")
        print()
        return False
    
    proporcion_train = num_train / total
    proporcion_val = num_val / total
    
    print(f"   Total de imágenes: {total}")
    print(f"   Entrenamiento: {num_train} ({proporcion_train*100:.1f}%)")
    print(f"   Validación: {num_val} ({proporcion_val*100:.1f}%)")
    
    # Validar que esté cerca de 70/30
    if 0.65 <= proporcion_train <= 0.75:
        print("   ✓ Distribución adecuada (~70/30)")
        resultado = True
    elif num_train > 0 and num_val > 0:
        print("   ⚠️  Distribución atípica (recomendado: 70% train / 30% val)")
        resultado = True
    else:
        print("   ✗ Uno de los conjuntos está vacío")
        resultado = False
    
    print()
    return resultado


def generar_reporte_estadisticas():
    """Genera reporte final con estadísticas del dataset."""
    print("=" * 70)
    print("📊 ESTADÍSTICAS DEL DATASET")
    print("=" * 70)
    
    # Contar etiquetas por clase
    def contar_clases(directorio_labels):
        conteo = {0: 0, 1: 0, 2: 0}
        if not os.path.exists(directorio_labels):
            return conteo
        
        for archivo in os.listdir(directorio_labels):
            if not archivo.endswith('.txt'):
                continue
            
            ruta = os.path.join(directorio_labels, archivo)
            with open(ruta, 'r') as f:
                for linea in f:
                    if linea.strip():
                        clase = int(linea.split()[0])
                        conteo[clase] = conteo.get(clase, 0) + 1
        
        return conteo
    
    conteo_train = contar_clases(LABELS_TRAIN)
    conteo_val = contar_clases(LABELS_VAL)
    
    print("\n📦 Entrenamiento:")
    print(f"   Clase 0 (Normal): {conteo_train[0]} núcleos")
    print(f"   Clase 1 (Anormal): {conteo_train[1]} núcleos")
    print(f"   Clase 2 (Artefacto): {conteo_train[2]} núcleos")
    print(f"   TOTAL: {sum(conteo_train.values())} objetos")
    
    print("\n📦 Validación:")
    print(f"   Clase 0 (Normal): {conteo_val[0]} núcleos")
    print(f"   Clase 1 (Anormal): {conteo_val[1]} núcleos")
    print(f"   Clase 2 (Artefacto): {conteo_val[2]} núcleos")
    print(f"   TOTAL: {sum(conteo_val.values())} objetos")
    
    # Estadísticas de metadatos
    if os.path.exists(METADATA_CSV):
        df = pd.read_csv(METADATA_CSV)
        print("\n📋 Metadatos clínicos:")
        print(f"   Registros totales: {len(df)}")
        if 'Diagnostico_Ref_Bethesda' in df.columns:
            print("\n   Distribución de diagnósticos:")
            for diag, count in df['Diagnostico_Ref_Bethesda'].value_counts().items():
                print(f"      {diag}: {count} ({count/len(df)*100:.1f}%)")
    
    print()


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta todas las validaciones."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "🔍 VALIDADOR DE CONSISTENCIA DE DATASET" + " " * 18 + "║")
    print("║" + " " * 20 + "CitoCounter Proto v1.0" + " " * 26 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    resultados = []
    
    # Ejecutar validaciones
    resultados.append(("Estructura de directorios", validar_estructura_directorios()))
    resultado_matching, (num_train, num_val) = validar_matching_imagen_etiqueta()
    resultados.append(("Matching imagen-etiqueta", resultado_matching))
    resultados.append(("Matching CSV-imágenes", validar_matching_csv()))
    resultados.append(("Coherencia diagnósticos", validar_coherencia_diagnosticos()))
    resultados.append(("Distribución Train/Val", validar_distribucion_train_val(num_train, num_val)))
    
    # Generar estadísticas
    generar_reporte_estadisticas()
    
    # Resumen final
    print("=" * 70)
    print("📋 RESUMEN DE VALIDACIÓN")
    print("=" * 70)
    
    for nombre, resultado in resultados:
        icono = "✅" if resultado else "❌"
        print(f"   {icono} {nombre}")
    
    print()
    
    if all([r[1] for r in resultados]):
        print("🎉 TODAS LAS VALIDACIONES PASARON")
        print("   El dataset está listo para usarse")
    else:
        print("⚠️  ALGUNAS VALIDACIONES FALLARON")
        print("   Revisar los errores arriba y corregir antes de usar el dataset")
    
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
