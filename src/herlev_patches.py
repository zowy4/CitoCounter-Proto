
from __future__ import annotations

import argparse
import csv
import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Generator, List, Sequence, Tuple

import cv2
import numpy as np
from PIL import Image

PATCH_SIZE = 256
STRIDE = 128  # 50% superposición
AUGMENTATIONS_LIST = ["original", "rot90", "rot180", "rot270", "flip_horizontal", "flip_vertical"]


@dataclass
class PatchConfig:
    """Configuración para generación de parches."""
    patch_size: int = PATCH_SIZE
    stride: int = STRIDE
    augmentations: Sequence[str] = field(default_factory=lambda: AUGMENTATIONS_LIST)


@dataclass
class PatchInfo:
    """Información meta para cada parche."""
    patch_id: str
    image_id: str
    patch_x: int
    patch_y: int
    split: str
    augmentation: str
    rotation: int
    flip_h: bool
    flip_v: bool


def cargar_imagen_herlev(ruta_imagen: Path) -> np.ndarray:
    """Carga imagen BMP de Herlev en escala de grises.
    
    :param ruta_imagen: Ruta al archivo BMP
    :type ruta_imagen: Path
    :return: Imagen en escala de grises
    :rtype: np.ndarray
    :raises ValueError: Si la imagen no se puede cargar
    """
    img = cv2.imread(str(ruta_imagen), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"No se pudo cargar imagen: {ruta_imagen}")
    return img


def cargar_mascara_herlev(ruta_mask: Path) -> np.ndarray:
    """Carga máscara binaria Herlev.
    
    :param ruta_mask: Ruta al archivo de máscara PNG
    :type ruta_mask: Path
    :return: Máscara binaria (0= fondo, 255=núcleo)
    :rtype: np.ndarray
    :raises ValueError: Si la máscara no se puede cargar
    """
    mask = cv2.imread(str(ruta_mask), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError(f"No se pudo cargar máscara: {ruta_mask}")
    _, mask_bin = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    return mask_bin


def generar_coordenadas_patch(
    alto: int, ancho: int, config: PatchConfig
) -> Generator[Tuple[int, int], None, None]:
    """Genera coordenadas (y, x) para parches con superposición.
    
    :param alto: Altura de la imagen
    :type alto: int
    :param ancho: Ancho de la imagen
    :type ancho: int
    :param config: Configuración de parches
    :type config: PatchConfig
    :yield: Tupla (y, x) coordenadas del parche
    :yield type: Generator[Tuple[int, int], None, None]
    """
    for y in range(0, alto, config.stride):
        for x in range(0, ancho, config.stride):
            if y + config.patch_size <= alto and x + config.patch_size <= ancho:
                yield (y, x)


def extraer_patch(
    imagen: np.ndarray, y: int, x: int, config: PatchConfig
) -> np.ndarray:
    """Extrae un parche de la imagen.
    
    :param imagen: Imagen completa
    :type imagen: np.ndarray
    :param y: Coordenada y del parche
    :type y: int
    :param x: Coordenada x del parche
    :type x: int
    :param config: Configuración
    :type config: PatchConfig
    :return: Parche extraído
    :rtype: np.ndarray
    """
    return imagen[y : y + config.patch_size, x : x + config.patch_size]


def aplicar_aumentacion(
    patch: np.ndarray, augment: str
) -> Tuple[np.ndarray, int, bool, bool]:
    """Aplica una transformación de aumentación.
    
    :param patch: Parche a transformar
    :type patch: np.ndarray
    :param augment: Nombre del tipo de aumentación
    :type augment: str
    :return: Tupla (patch_transformado, rotaciones, flip_h, flip_v)
    :rtype: Tuple[np.ndarray, int, bool, bool]
    """
    rotation = 0
    flip_h = False
    flip_v = False
    
    if augment == "original":
        return (patch, rotation, flip_h, flip_v)
    
    elif augment == "rot90":
        rotation = 1
        patch = np.rot90(patch, k=1)
    elif augment == "rot180":
        rotation = 2
        patch = np.rot90(patch, k=2)
    elif augment == "rot270":
        rotation = 3
        patch = np.rot90(patch, k=3)
    elif augment == "flip_horizontal":
        flip_h = True
        patch = np.fliplr(patch)
    elif augment == "flip_vertical":
        flip_v = True
        patch = np.flipud(patch)
    
    return (patch, rotation, flip_h, flip_v)


def generar_patch_id(
    image_id: str, y: int, x: int, augment: str, patch_idx: int
) -> str:
    """Genera ID único determinístico para un parche.
    
    :param image_id: ID de la imagen original
    :type image_id: str
    :param y: Coordenada y
    :type y: int
    :param x: Coordenada x
    :type x: int
    :param augment: Tipo de aumentación
    :type augment: str
    :param patch_idx: Índice del parche
    :type patch_idx: int
    :return: ID del parche
    :rtype: str
    """
    content = f"{image_id}_{y}_{x}_{augment}_{patch_idx}"
    hash_val = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"patch_{image_id}_{augment}_{hash_val}"


def extraer_patches_herlev(
    images_dir: Path,
    masks_dir: Path,
    splits_dir: Path,
    output_dir: Path,
    config: PatchConfig,
) -> List[PatchInfo]:
    """Extrae parches de todas las imágenes con sus máscaras.
    
    :param images_dir: Directorio con imágenes BMP
    :type images_dir: Path
    :param masks_dir: Directorio con máscaras PNG
    :type masks_dir: Path
    :param splits_dir: Directorio con archivos split CSV
    :type splits_dir: Path
    :param output_dir: Directorio de salida para parches
    :type output_dir: Path
    :param config: Configuración de parches
    :type config: PatchConfig
    :return: Lista de información de parches generados
    :rtype: List[PatchInfo]
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    patches_info: List[PatchInfo] = []
    
    for split in ("train", "val", "test"):
        split_csv = splits_dir / f"{split}.csv"
        if not split_csv.exists():
            continue
        
        with split_csv.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            image_ids = [row["image_id"] for row in reader]
        
        for image_id in image_ids:
            img_path = images_dir / f"{image_id}.bmp"
            mask_path = masks_dir / f"{image_id}_nuc_mask.png"
            
            if not img_path.exists():
                continue
            
            try:
                img = cargar_imagen_herlev(img_path)
                mask = cargar_mascara_herlev(mask_path) if mask_path.exists() else np.zeros_like(img)
            except ValueError:
                continue
            
            alto, ancho = img.shape
            patch_idx = 0
            
            for y, x in generar_coordenadas_patch(alto, ancho, config):
                img_patch = extraer_patch(img, y, x, config)
                mask_patch = extraer_patch(mask, y, x, config)
                
                for augment in config.augmentations:
                    img_aug, rot, flip_h, flip_v = aplicar_aumentacion(img_patch, augment)
                    mask_aug, _, _, _ = aplicar_aumentacion(mask_patch, augment)
                    
                    patch_id = generar_patch_id(image_id, y, x, augment, patch_idx)
                    
                    img_out = output_dir / f"{patch_id}.png"
                    mask_out = output_dir / f"{patch_id}_mask.png"
                    
                    # Escritura eficiente con PIL
                    Image.fromarray(img_aug).save(str(img_out), compress_level=6)
                    Image.fromarray(mask_aug).save(str(mask_out), compress_level=6)
                    
                    patches_info.append(PatchInfo(
                        patch_id=patch_id,
                        image_id=image_id,
                        patch_x=x,
                        patch_y=y,
                        split=split,
                        augmentation=augment,
                        rotation=rot,
                        flip_h=flip_h,
                        flip_v=flip_v,
                    ))
                    patch_idx += 1
    
    return patches_info


def escribir_manifiestos(
    patches_info: Sequence[PatchInfo],
    output_dir: Path,
) -> Dict[str, int]:
    """Escribe manifiestos CSV y devuelve conteo por split y clase.
    
    :param patches_info: Información de los parches
    :type patches_info: Sequence[PatchInfo]
    :param output_dir: Directorio de salida
    :type output_dir: Path
    :return: Diccionario con conteo por split y clase
    :rtype: Dict[str, int]
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    splits_data: Dict[str, List[Dict[str, object]]] = {
        "train": [], "val": [], "test": []
    }
    
    for p in patches_info:
        splits_data[p.split].append({
            "patch_id": p.patch_id,
            "image_id": p.image_id,
            "augmentation": p.augmentation,
            "rotation": p.rotation,
            "flip_horizontal": p.flip_h,
            "flip_vertical": p.flip_v,
        })
    
    counts = {}
    for split, data in splits_data.items():
        csv_path = output_dir / f"{split}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "patch_id", "image_id", "augmentation", "rotation",
                "flip_horizontal", "flip_vertical"
            ])
            writer.writeheader()
            writer.writerows(data)
        counts[split] = len(data)
        counts[f"{split}_total_patches"] = len(data)
    
    return counts


def main() -> int:
    """Punto de entrada CLI.
    
    :return: Código de salida
    :rtype: int
    """
    parser = argparse.ArgumentParser(
        description="Extrae parches 256x256 de imágenes Herlev con aumentaciones"
    )
    parser.add_argument(
        "--images-dir", type=Path, default=Path("data/raw/im_Dyskeratotic"),
        help="Directorio con imágenes BMP"
    )
    parser.add_argument(
        "--masks-dir", type=Path, default=Path("data/ground_truth/herlev/masks"),
        help="Directorio con máscaras PNG"
    )
    parser.add_argument(
        "--splits-dir", type=Path, default=Path("data/ground_truth/herlev/splits"),
        help="Directorio con archivos split CSV"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("data/processed/herlev_patches"),
        help="Directorio de salida para parches"
    )
    parser.add_argument(
        "--patch-size", type=int, default=PATCH_SIZE,
        help="Tamaño de los parches (default: 256)"
    )
    parser.add_argument(
        "--stride", type=int, default=STRIDE,
        help="Stride para generación (default: 128 para 50%% superposición)"
    )
    args = parser.parse_args()
    
    config = PatchConfig(patch_size=args.patch_size, stride=args.stride)
    
    print(f"Extrayendo parches de {args.images_dir}...")
    patches = extraer_patches_herlev(
        args.images_dir, args.masks_dir, args.splits_dir, args.output_dir, config
    )
    
    counts = escribir_manifiestos(patches, args.output_dir)
    
    print(f"\nManifiestos escritos en {args.output_dir}")
    for split in ["train", "val", "test"]:
        print(f"  {split}: {counts.get(split, 0)} parches")
    
    total = sum(counts.get(s, 0) for s in ["train", "val", "test"])
    print(f"Total: {total} parches")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())