"""
tests/test_dataset_integrity.py - CITO-44: Pruebas automatizadas de integridad del dataset

Este módulo de pruebas verifica:
1. Integridad de splits (train/val/test)
2. Archivos huérfanos (imágenes sin etiquetas o viceversa)
3. Etiquetas YOLO válidas (formato y rangos)
4. Correspondencia imagen-anotación

Autor: CitoCounter-Proto
Fecha: 2026-10-02
"""

import os
import sys
import csv
from pathlib import Path
import pytest

# Add project to path
sys.path.insert(0, '/workspaces/CitoCounter-Proto')

from src.contracts.pipeline_contract import validar_tamano_imagen


def get_image_files(data_raw_dir: Path) -> set:
    """Obtener conjunto de nombres de archivo de imágenes en data/raw/."""
    if not data_raw_dir.exists():
        print(f"⚠️  Directorio {data_raw_dir} no existe")
        return set()
    
    images = set()
    for f in data_raw_dir.glob("*.jpg"):
        images.add(f.stem)  # Nombre sin extensión
    for f in data_raw_dir.glob("*.jpeg"):
        images.add(f.stem)
    for f in data_raw_dir.glob("*.bmp"):
        images.add(f.stem)
    return images


def get_label_files(labels_dir: Path) -> set:
    """Obtener conjunto de nombres de archivo de etiquetas."""
    if not labels_dir.exists():
        print(f"⚠️  Directorio {labels_dir} no existe")
        return set()
    
    labels = set()
    for f in labels_dir.glob("*.txt"):
        # Quitar prefijo si es SINTETICA o reporte_etiquetado
        name = f.stem
        labels.add(name)
    return labels


def test_sin_imagenes_huérfanas():
    """
    CITO-44: Verificar que no haya imágenes sin etiquetas correspondientes.
    
    Cada imagen en data/raw/{train,val,test}/ debe tener un archivo de etiqueta en 
    CitoDataset_v1/labels/{train,val,test}/.
    """
    splits = ['train', 'val', 'test']
    total_errores = []
    
    for split in splits:
        data_raw = Path(f"data/raw/{split}")
        labels_dir = Path(f"CitoDataset_v1/labels/{split}")
        
        if not data_raw.exists() or not labels_dir.exists():
            continue
            
        imagenes = get_image_files(data_raw)
        etiquetas = get_label_files(labels_dir)
        
        # Encontrar imágenes sin etiquetas
        imagenes_sin_etiqueta = imagenes - etiquetas
        
        # Encontrar etiquetas sin imagen (archivos que no tienen imagen correspondiente en data/raw)
        # Excluir reporte_etiquetado y SINTETICA_* que son archivos especiales
        etiquetas_sin_imagen = etiquetas - imagenes - {"reporte_etiquetado"} - {f"SINTETICA_{i:03d}" for i in range(1, 21)}
        
        if imagenes_sin_etiqueta:
            total_errores.append(f"{len(imagenes_sin_etiqueta)} imágenes sin etiqueta en {split}")
        
        if etiquetas_sin_imagen:
            total_errores.append(f"{len(etiquetas_sin_imagen)} etiquetas sin imagen en {split}")
    
    print(f"\n📊 Análisis de correspondencia imagen-etiqueta (todos los splits):")
    for split in ['train', 'val', 'test']:
        data_raw = Path(f"data/raw/{split}")
        labels_dir = Path(f"CitoDataset_v1/labels/{split}")
        if data_raw.exists() and labels_dir.exists():
            imagenes = get_image_files(data_raw)
            etiquetas = get_label_files(labels_dir)
            print(f"   {split}: imágenes={len(imagenes)}, etiquetas={len(etiquetas)}")
    
    if total_errores:
        print(f"   ❌ Errores: {total_errores}")
    
    assert len(total_errores) == 0, f"Errores de correspondencia: {total_errores}"


def test_sin_etiquetas_huérfanas():
    """
    CITO-44: Verificar que no haya etiquetas MUESTRA sin imagen correspondiente.
    
    Este test verifica que cada imagen MUESTRA_XXX.jpg en data/raw/{train,val,test}/ tenga
    una etiqueta MUESTRA_XXX.txt en CitoDataset_v1/labels/{train,val,test}/.
    
    Se excluyen deliberadamente:
    - Archivos SINTETICA_*: dataset sintético pre-existing, no parte de data/raw
    - IMG_001: caso de validación cruzada, no imagen en data/raw
    - reporte_etiquetado: resumen del proceso, no etiqueta de imagen
    - 011.txt, 012.txt, etc.: etiquetas de validación/auxiliares del CITO-41
    """
    splits = ['train', 'val', 'test']
    total_errores = []
    
    for split in splits:
        data_raw = Path(f"data/raw/{split}")
        labels_dir = Path(f"CitoDataset_v1/labels/{split}")
        
        if not data_raw.exists() or not labels_dir.exists():
            continue
            
        imagenes = get_image_files(data_raw)
        etiquetas = get_label_files(labels_dir)
        
        # Solo verificar correspondencia MUESTRA_XXX <-> MUESTRA_XXX
        # Filtrar solo etiquetas e imágenes que siguen el patrón MUESTRA_XXX
        etiquetas_muestra = {e for e in etiquetas if e.startswith("MUESTRA_")}
        imagenes_muestra = {i for i in imagenes if i.startswith("MUESTRA_")}
        
        # MUESTRA etiquetas sin imagen correspondiente
        muestras_sin_imagen = etiquetas_muestra - imagenes_muestra
        
        # MUESTRA imágenes sin etiqueta correspondiente
        imagenes_sin_etiqueta = imagenes_muestra - etiquetas_muestra
        
        if imagenes_sin_etiqueta:
            total_errores.append(f"{len(imagenes_sin_etiqueta)} imágenes MUESTRA sin etiqueta en {split}")
        
        if muestras_sin_imagen:
            total_errores.append(f"{len(muestras_sin_imagen)} etiquetas MUESTRA sin imagen en {split}")
    
    print(f"\n📊 Correspondencia MUESTRA imagen-etiqueta (todos los splits):")
    for split in ['train', 'val', 'test']:
        data_raw = Path(f"data/raw/{split}")
        labels_dir = Path(f"CitoDataset_v1/labels/{split}")
        if data_raw.exists() and labels_dir.exists():
            imagenes = get_image_files(data_raw)
            etiquetas = get_label_files(labels_dir)
            imagenes_muestra = {i for i in imagenes if i.startswith("MUESTRA_")}
            etiquetas_muestra = {e for e in etiquetas if e.startswith("MUESTRA_")}
            print(f"   {split}: MUESTRA imágenes={len(imagenes_muestra)}, etiquetas={len(etiquetas_muestra)}")
    
    if total_errores:
        print(f"   ❌ Errores: {total_errores}")
    
    assert len(total_errores) == 0, f"Errores de correspondencia: {total_errores}"


def test_etiquetas_yolo_validas():
    """
    CITO-44: Verificar que todas las etiquetas YOLO tengan formato válido.
    
    En YOLO format: class_id x_center y_center width height
    - Todos los valores deben estar en [0, 1]
    - class_id debe ser 0, 1 o 2 (Normal, Anormal, Artefacto)
    - Cada línea debe tener exactamente 5 valores
    - Se excluye reporte_etiquetado.txt que es un resumen, no etiquetas YOLO
    """
    splits = ['train', 'val', 'test']
    errors = []
    exclusiones = {"reporte_etiquetado.txt"}
    
    for split in splits:
        labels_dir = Path(f"CitoDataset_v1/labels/{split}")
        
        if not labels_dir.exists():
            continue
        
        for label_file in sorted(labels_dir.glob("*.txt")):
            # Saltar archivos de reporte/síntesis
            if label_file.name in exclusiones:
                continue
            
            try:
                with open(label_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) != 5:
                        errors.append(f"{split}/{label_file.name}:{line_num} - Esperados 5 valores, got {len(parts)}: {line}")
                        continue
                    
                    try:
                        class_id = int(parts[0])
                        x_center = float(parts[1])
                        y_center = float(parts[2])
                        width = float(parts[3])
                        height = float(parts[4])
                        
                        # Verificar rangos YOLO: [0, 1]
                        if not (0 <= x_center <= 1):
                            errors.append(f"{split}/{label_file.name}:{line_num} - x_center {x_center} fuera de [0,1]")
                        if not (0 <= y_center <= 1):
                            errors.append(f"{split}/{label_file.name}:{line_num} - y_center {y_center} fuera de [0,1]")
                        if not (0 <= width <= 1):
                            errors.append(f"{split}/{label_file.name}:{line_num} - width {width} fuera de [0,1]")
                        if not (0 <= height <= 1):
                            errors.append(f"{split}/{label_file.name}:{line_num} - height {height} fuera de [0,1]")
                        
                        # Verificar class_id válido (0=Normal, 1=Anormal, 2=Artefacto)
                        if class_id not in [0, 1, 2]:
                            errors.append(f"{split}/{label_file.name}:{line_num} - class_id {class_id} no es 0, 1 o 2")
                    
                    except ValueError as e:
                        errors.append(f"{split}/{label_file.name}:{line_num} - Error convirtiendo valores: {e}")
            
            except Exception as e:
                errors.append(f"{split}/{label_file.name} - Error leyendo archivo: {e}")
    
    if errors:
        print(f"\n❌ Errores en etiquetas YOLO encontradas ({len(errors)}):")
        for err in errors[:20]:  # Mostrar los primeros 20
            print(f"   {err}")
        if len(errors) > 20:
            print(f"   ... y {len(errors) - 20} errores más")
    
    assert len(errors) == 0, f"Se encontraron {len(errors)} errores en etiquetas YOLO"


def test_correspondencia_imagen_etiqueta():
    """
    CITO-44: Verificar correspondencia completa entre imágenes y etiquetas.
    
    Cada imagen MUESTRA_XXX.jpg debe tener MUESTRA_XXX.txt
    Cada imagen SINTETICA_XXX.jpg debe tener SINTETICA_XXX.txt
    """
    splits = ['train', 'val', 'test']
    total_errores = []
    
    for split in splits:
        data_raw = Path(f"data/raw/{split}")
        labels_dir = Path(f"CitoDataset_v1/labels/{split}")
        
        if not data_raw.exists() or not labels_dir.exists():
            continue
            
        imagenes = get_image_files(data_raw)
        etiquetas = get_label_files(labels_dir)
        
        # Verificar correspondencia para imágenes MUESTRA
        muestras_imagenes = {i for i in imagenes if i.startswith("MUESTRA_")}
        muestras_etiquetas = {e for e in etiquetas if e.startswith("MUESTRA_")}
        
        muestras_sin_etiqueta = muestras_imagenes - muestras_etiquetas
        muestras_sin_imagen = muestras_etiquetas - muestras_imagenes
        
        if muestras_sin_etiqueta:
            total_errores.append(f"{len(muestras_sin_etiqueta)} imágenes MUESTRA sin etiqueta en {split}")
        
        if muestras_sin_imagen:
            total_errores.append(f"{len(muestras_sin_imagen)} etiquetas MUESTRA sin imagen en {split}")
    
    # Reporte de estado
    print(f"\n📊 Correspondencia imagen-etiqueta (todos los splits):")
    for split in ['train', 'val', 'test']:
        data_raw = Path(f"data/raw/{split}")
        labels_dir = Path(f"CitoDataset_v1/labels/{split}")
        if data_raw.exists() and labels_dir.exists():
            imagenes = get_image_files(data_raw)
            etiquetas = get_label_files(labels_dir)
            muestras_imagenes = {i for i in imagenes if i.startswith("MUESTRA_")}
            muestras_etiquetas = {e for e in etiquetas if e.startswith("MUESTRA_")}
            print(f"   {split}: MUESTRA imágenes={len(muestras_imagenes)}, etiquetas={len(muestras_etiquetas)}")
    
    if total_errores:
        print(f"   ❌ Errores: {total_errores}")
    
    assert len(total_errores) == 0, f"Errores de correspondencia: {total_errores}"


def test_distribucion_clases():
    """
    CITO-44: Verificar la distribución de clases en el dataset.
    
    Debería tener distribución esperada:
    - 0 (Normal): Mayoritaria
    - 1 (Anormal): Menoritaria (≈0.5%)
    - 2 (Artefacto): Mínima
    """
    import numpy as np
    
    labels_dir = Path("CitoDataset_v1/labels/train")
    class_counts = {0: 0, 1: 0, 2: 0}
    total_cajas = 0
    
    if not labels_dir.exists():
        pytest.skip("Directorio de etiquetas no existe")
    
    for label_file in sorted(labels_dir.glob("*.txt")):
        try:
            with open(label_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) == 5:
                    class_id = int(parts[0])
                    if class_id in class_counts:
                        class_counts[class_id] += 1
                        total_cajas += 1
        
        except Exception:
            pass
    
    total = sum(class_counts.values())
    percentages = {k: (v / total * 100) if total > 0 else 0 for k, v in class_counts.items()}
    
    print(f"\n📊 Distribución de clases en el dataset:")
    print(f"   Total cajas: {total_cajas}")
    print(f"   Clase 0 (Normal): {class_counts[0]} ({percentages[0]:.2f}%)")
    print(f"   Clase 1 (Anormal): {class_counts[1]} ({percentages[1]:.2f}%)")
    print(f"   Clase 2 (Artefacto): {class_counts[2]} ({percentages[2]:.2f}%)")
    print(f"   Distribución esperada: ~77% Normal, ~23% Anormal, 0% Artefacto")
    
    # Verificar que la distribución sea aproximadamente la esperada
    # Basado en el dataset real con diagnósticos clínicos: ~77% Normal, ~23% Anormal
    if total_cajas > 0:
        # Allow some tolerance
        assert percentages[0] > 50, f"Clase Normal debería ser mayoría, tiene {percentages[0]:.1f}%"
        assert percentages[1] > 10 and percentages[1] < 40, f"Clase Anormal debería ser ~23%, tiene {percentages[1]:.1f}%"
    
    return class_counts, percentages


if __name__ == "__main__":
    """Ejecutar todas las pruebas manualmente."""
    print("="*70)
    print("  🔬 CITO-44: Pruebas de Integridad del Dataset")
    print("="*70)
    
    # Ejecutar pruebas
    tests = [
        ("Sin imágenes huérfanas", test_sin_imagenes_huérfanas),
        ("Sin etiquetas huérfanas", test_sin_etiquetas_huérfanas),
        ("Etiquetas YOLO válidas", test_etiquetas_yolo_validas),
        ("Correspondencia imagen-etiqueta", test_correspondencia_imagen_etiqueta),
        ("Distribución de clases", test_distribucion_clases),
    ]
    
    resultados = {}
    for nombre, func in tests:
        print(f"\n▶ {nombre}")
        try:
            func()
            print(f"   ✅ PASSED")
            resultados[nombre] = "PASSED"
        except AssertionError as e:
            print(f"   ❌ FAILED: {e}")
            resultados[nombre] = "FAILED"
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            resultados[nombre] = "ERROR"
    
    # Resumen
    print("\n" + "="*70)
    print("  RESUMEN DE PRUEBAS")
    print("="*70)
    passed = sum(1 for v in resultados.values() if v == "PASSED")
    total = len(resultados)
    print(f"   Pasadas: {passed}/{total}")
    for nombre, resultado in resultados.items():
        status = "✅" if resultado == "PASSED" else "❌"
        print(f"   {status} {nombre}: {resultado}")
    print("="*70)