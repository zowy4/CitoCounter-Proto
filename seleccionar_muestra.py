#!/usr/bin/env python3
"""
Script para seleccionar un conjunto de muestra aleatorio de imágenes
para evaluar la concordancia inter-anotador (CITO-71).

Uso: python seleccionar_muestra.py --total 30 --aleatorio
"""

import argparse
import os
import random
import csv

def main():
    parser = argparse.ArgumentParser(description='Seleccionar muestra de imágenes para concordancia')
    parser.add_argument('--total', type=int, default=30, help='Número total de imágenes a seleccionar')
    parser.add_argument('--aleatorio', action='store_true', help='Seleccionar aleatoriamente')
    parser.add_argument('--por-split', action='store_true', help='Seleccionar por split')
    args = parser.parse_args()
    
    # Definir rutas
    data_raw = '/workspaces/CitoCounter-Proto/data/raw'
    dataset_labels = '/workspaces/CitoCounter-Proto/CitoDataset_v1/labels'
    
    # Collect all image names from all splits
    all_images = []
    splits = ['train', 'val', 'test']
    
    for split in splits:
        split_dir = os.path.join(data_raw, split)
        if os.path.exists(split_dir):
            for fname in os.listdir(split_dir):
                if fname.endswith('.jpg'):
                    # Extraer nombre base (sin extensión)
                    base_name = fname.replace('.jpg', '')
                    all_images.append((base_name, split))
    
    print(f"Total de imágenes disponibles: {len(all_images)}")
    
    if args.aleatorio:
        # Seleccionar aleatoriamente
        sample = random.sample(all_images, min(args.total, len(all_images)))
        sample.sort(key=lambda x: x[0])
        
        print(f"\nMuestra aleatoria de {len(sample)} imágenes:")
        for name, split in sample:
            print(f"  {name} ({split})")
        
        # Guardar en archivo
        with open('muestra_seleccionada.csv', 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['imagen', 'split'])
            for name, split in sample:
                writer.writerow([name, split])
        print("\nGuardado en: muestra_seleccionada.csv")
    
    elif args.por_split:
        # Seleccionar por split (ej. 10 de cada uno)
        if args.total % 3 != 0:
            print("Advertencia: --total debe ser divisible por 3 para distribución equitativa")
            return
        
        per_split = args.total // 3
        sample = []
        for split in splits:
            split_dir = os.path.join(data_raw, split)
            if os.path.exists(split_dir):
                split_images = [f.replace('.jpg', '') for f in os.listdir(split_dir) if f.endswith('.jpg')]
                selected = random.sample(split_images, min(per_split, len(split_images)))
                sample.extend([(name, split) for name in selected])
        
        sample.sort(key=lambda x: x[0])
        
        print(f"\nMuestra por split ({per_split} de cada uno, total {len(sample)}):")
        for name, split in sample:
            print(f"  {name} ({split})")
        
        # Guardar en archivo
        with open('muestra_seleccionada.csv', 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['imagen', 'split'])
            for name, split in sample:
                writer.writerow([name, split])
        print("\nGuardado en: muestra_seleccionada.csv")

if __name__ == '__main__':
    main()