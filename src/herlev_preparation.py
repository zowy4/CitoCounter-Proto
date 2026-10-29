"""Preparación determinista de anotaciones y manifiestos Herlev."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import struct
import tempfile
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import cv2

from src.herlev_dataset import (
    MAX_MASCARA_BYTES,
    cargar_poligonos_nucleo,
    guardar_csv_celulas,
    mapear_elementos_a_grupo_por_prefijo,
    poligonos_a_registros,
    propagar_splits_por_grupo,
    rasterizar_mascara,
)

SPLITS = ("train", "val", "test")
CAMPOS_SPLIT = ("image_id", "image_name")
MAX_ARCHIVO_IMAGEN_BYTES = 16 * 1024 * 1024


def _leer_dimensiones_bmp(ruta_imagen: Path) -> Tuple[int, int]:
    """Lee dimensiones BMP desde su cabecera sin decodificar los píxeles.

    Parameters
    ----------
    ruta_imagen : pathlib.Path
        Ruta a una imagen BMP.

    Returns
    -------
    tuple[int, int]
        Alto y ancho, en ese orden.

    Raises
    ------
    OSError
        Si no es posible leer la cabecera.
    ValueError
        Si el encabezado no es BMP, las dimensiones son inválidas o superan
        el límite de píxeles de las máscaras.
    """
    with ruta_imagen.open("rb") as archivo:
        cabecera = archivo.read(26)
    if len(cabecera) < 26 or cabecera[:2] != b"BM":
        raise ValueError(f"Cabecera BMP inválida: {ruta_imagen.name}")

    tamano_dib = struct.unpack_from("<I", cabecera, 14)[0]
    if tamano_dib == 12:
        ancho, alto = struct.unpack_from("<HH", cabecera, 18)
    elif tamano_dib >= 40:
        ancho, alto_firmado = struct.unpack_from("<ii", cabecera, 18)
        alto = abs(alto_firmado)
    else:
        raise ValueError(f"Cabecera BMP no compatible: {ruta_imagen.name}")

    if ancho <= 0 or alto <= 0:
        raise ValueError(f"Dimensiones BMP inválidas: {ruta_imagen.name}")
    if ancho * alto > MAX_MASCARA_BYTES:
        raise ValueError(
            f"Las dimensiones de {ruta_imagen.name} exceden el límite "
            "permitido para máscaras."
        )
    return alto, ancho


def _leer_splits(
    ruta_splits: Path,
    imagenes_origen: Sequence[Path],
) -> Dict[str, List[str]]:
    """Lee y valida manifiestos de grupos de origen.

    Parameters
    ----------
    ruta_splits : pathlib.Path
        Directorio con `train.csv`, `val.csv` y `test.csv`.
    imagenes_origen : Sequence[pathlib.Path]
        Imágenes completas que deben estar asignadas exactamente una vez.

    Returns
    -------
    dict[str, list[str]]
        Grupos de origen asignados a cada split, ordenados por archivo.

    Raises
    ------
    FileNotFoundError
        Si falta el directorio o alguno de los manifiestos.
    ValueError
        Si el esquema, identificadores o asignaciones son inconsistentes.
    """
    if not ruta_splits.is_dir():
        raise FileNotFoundError(f"No existe el directorio de splits: {ruta_splits}")

    grupos_por_split: Dict[str, List[str]] = {}
    ids_vistos: set[str] = set()
    ids_origen = {imagen.stem for imagen in imagenes_origen}

    for split in SPLITS:
        ruta = ruta_splits / f"{split}.csv"
        if not ruta.is_file():
            raise FileNotFoundError(f"No existe el manifiesto requerido: {ruta}")
        with ruta.open("r", newline="", encoding="utf-8-sig") as archivo:
            lector = csv.DictReader(archivo)
            if tuple(lector.fieldnames or ()) != CAMPOS_SPLIT:
                raise ValueError(
                    f"El manifiesto {ruta} debe tener columnas "
                    f"{', '.join(CAMPOS_SPLIT)}."
                )
            grupos: List[str] = []
            for fila in lector:
                image_id_original = fila.get("image_id")
                image_name_original = fila.get("image_name")
                if not isinstance(image_id_original, str) or not isinstance(
                    image_name_original, str
                ):
                    raise ValueError(f"Fila inválida en el manifiesto {ruta}.")
                image_id = image_id_original.strip()
                image_name = image_name_original.strip()
                if (
                    not image_id
                    or not image_name
                    or Path(image_name).name != image_name
                    or Path(image_name).stem != image_id
                ):
                    raise ValueError(f"Fila inválida en el manifiesto {ruta}.")
                if image_id not in ids_origen:
                    raise ValueError(
                        f"El manifiesto {ruta} contiene una imagen fuente desconocida."
                    )
                if image_id in ids_vistos:
                    raise ValueError(
                        "Cada imagen fuente debe aparecer en un solo manifiesto."
                    )
                ids_vistos.add(image_id)
                grupos.append(image_id)
        grupos_por_split[split] = grupos

    ids_esperados = ids_origen
    if ids_vistos != ids_esperados:
        raise ValueError(
            "Los manifiestos deben asignar exactamente todas las imágenes completas."
        )
    return grupos_por_split


def _guardar_manifiestos(
    directorio: Path,
    elementos_por_split: Mapping[str, Sequence[str]],
    rutas_por_id: Mapping[str, Path],
) -> None:
    """Escribe manifiestos CSV ordenados de forma determinista.

    Parameters
    ----------
    directorio : pathlib.Path
        Directorio de salida para los tres manifiestos.
    elementos_por_split : Mapping[str, Sequence[str]]
        Identificadores de imágenes/crops asignados por split.
    rutas_por_id : Mapping[str, pathlib.Path]
        Ruta fuente de cada identificador.

    Returns
    -------
    None
        Escribe archivos CSV en el directorio indicado.

    Raises
    ------
    OSError
        Si no es posible crear o escribir un manifiesto.
    """
    directorio.mkdir()
    for split in SPLITS:
        ruta = directorio / f"{split}.csv"
        with ruta.open("x", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=CAMPOS_SPLIT)
            escritor.writeheader()
            for image_id in elementos_por_split[split]:
                escritor.writerow(
                    {
                        "image_id": image_id,
                        "image_name": rutas_por_id[image_id].name,
                    }
                )


def preparar_dataset_herlev(
    directorio_fuente: str | Path,
    directorio_splits: str | Path,
    directorio_salida: str | Path,
    clasificacion: str,
    max_archivo_imagen_bytes: int = MAX_ARCHIVO_IMAGEN_BYTES,
) -> Dict[str, int]:
    """Genera CSV de células, máscaras y splits heredados sin sobrescribir.

    Solo escribe las anotaciones derivadas y manifiestos; no copia imágenes
    fuente ni archivos `.dat`. El directorio final debe ser nuevo. Los
    resultados se construyen en un directorio temporal hermano y se publican
    al final para evitar dejar una salida parcial ante errores de validación.

    Parameters
    ----------
    directorio_fuente : str | pathlib.Path
        Directorio con imágenes completas y subdirectorio opcional `CROPPED`.
    directorio_splits : str | pathlib.Path
        Directorio con manifiestos train/val/test de imágenes completas.
    directorio_salida : str | pathlib.Path
        Nuevo directorio de destino; si existe, la operación falla.
    clasificacion : str
        Etiqueta fuente explícita que se conserva en las filas CSV.
    max_archivo_imagen_bytes : int, optional
    Tamaño máximo de archivo BMP antes de leer su cabecera. Por defecto
        16 MiB para incluir las imágenes locales observadas.

    Returns
    -------
    dict[str, int]
        Conteos de imágenes procesadas, células y elementos por split.

    Raises
    ------
    FileNotFoundError
        Si faltan fuentes, anotaciones o manifiestos.
    FileExistsError
        Si el destino existe.
    ValueError
        Si los datos no cumplen el esquema, exceden límites o hay fuga de split.
    OSError
        Si falla la lectura o escritura de archivos.
    """
    fuente = Path(directorio_fuente)
    splits = Path(directorio_splits)
    salida = Path(directorio_salida)
    if not fuente.is_dir():
        raise FileNotFoundError(f"No existe el directorio fuente: {fuente}")
    if (
        not isinstance(max_archivo_imagen_bytes, int)
        or isinstance(max_archivo_imagen_bytes, bool)
        or max_archivo_imagen_bytes <= 0
    ):
        raise ValueError("max_archivo_imagen_bytes debe ser un entero positivo.")
    if not isinstance(clasificacion, str) or not clasificacion.strip():
        raise ValueError("clasificacion debe ser una etiqueta fuente no vacía.")
    if salida.exists() or salida.is_symlink():
        raise FileExistsError(f"El directorio de salida ya existe: {salida}")
    if not salida.parent.is_dir():
        raise FileNotFoundError(
            f"No existe el directorio padre de salida: {salida.parent}"
        )

    imagenes_origen = sorted(
        (ruta for ruta in fuente.glob("*.bmp") if ruta.is_file()),
        key=lambda ruta: ruta.name.lower(),
    )
    if not imagenes_origen:
        raise ValueError(f"No se encontraron imágenes BMP en {fuente}.")

    imagenes_crop = sorted(
        (ruta for ruta in (fuente / "CROPPED").glob("*.bmp") if ruta.is_file()),
        key=lambda ruta: ruta.name.lower(),
    )
    imagenes = imagenes_origen + imagenes_crop
    rutas_por_id = {imagen.stem: imagen for imagen in imagenes}
    if len(rutas_por_id) != len(imagenes):
        raise ValueError("Hay identificadores de imagen repetidos entre origen y crops.")

    splits_por_grupo = _leer_splits(splits, imagenes_origen)
    grupo_por_elemento = mapear_elementos_a_grupo_por_prefijo(
        [imagen.stem for imagen in imagenes],
        [imagen.stem for imagen in imagenes_origen],
    )
    elementos_por_split = propagar_splits_por_grupo(
        splits_por_grupo,
        grupo_por_elemento,
    )

    with tempfile.TemporaryDirectory(
        prefix=f".{salida.name}.tmp-",
        dir=salida.parent,
    ) as directorio_temporal:
        salida_temporal = Path(directorio_temporal)
        try:
            cells = salida_temporal / "cells"
            masks = salida_temporal / "masks"
            cells.mkdir()
            masks.mkdir()
            total_celulas = 0

            for imagen in imagenes:
                tamano = imagen.stat().st_size
                if tamano > max_archivo_imagen_bytes:
                    raise ValueError(
                        f"Imagen excede el límite de {max_archivo_imagen_bytes} "
                        f"bytes: {imagen.name}"
                    )
                alto, ancho = _leer_dimensiones_bmp(imagen)
                poligonos = cargar_poligonos_nucleo(imagen)
                registros = poligonos_a_registros(
                    poligonos,
                    (alto, ancho),
                    clasificacion=clasificacion,
                )
                guardar_csv_celulas(cells / f"{imagen.stem}_cells.csv", registros)
                mascara = rasterizar_mascara(poligonos, (alto, ancho))
                exito, png = cv2.imencode(
                    ".png",
                    mascara,
                    [cv2.IMWRITE_PNG_COMPRESSION, 9],
                )
                if not exito:
                    raise OSError(f"No se pudo codificar la máscara {imagen.stem}.")
                (masks / f"{imagen.stem}_mask.png").write_bytes(png.tobytes())
                total_celulas += len(registros)

            _guardar_manifiestos(
                salida_temporal / "splits",
                elementos_por_split,
                rutas_por_id,
            )
            if salida.exists() or salida.is_symlink():
                raise FileExistsError(f"El directorio de salida ya existe: {salida}")
            os.rename(salida_temporal, salida)
        finally:
            if salida_temporal.exists():
                shutil.rmtree(salida_temporal)

    return {
        "imagenes": len(imagenes),
        "celulas": total_celulas,
        "train": len(elementos_por_split["train"]),
        "val": len(elementos_por_split["val"]),
        "test": len(elementos_por_split["test"]),
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Ejecuta la interfaz de línea de comandos de preparación Herlev.

    Parameters
    ----------
    argv : Sequence[str] | None, optional
        Argumentos de CLI; `None` usa los argumentos del proceso.

    Returns
    -------
    int
        Código de salida cero si la preparación termina correctamente.

    Raises
    ------
    SystemExit
        Si argparse detecta argumentos incorrectos o la preparación falla.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Genera anotaciones derivadas y manifiestos Herlev en un destino nuevo. "
            "No copia imágenes fuente."
        )
    )
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--splits-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--classification", required=True)
    parser.add_argument(
        "--max-image-bytes",
        type=int,
        default=MAX_ARCHIVO_IMAGEN_BYTES,
        help=(
            "máximo por archivo BMP (default: "
            f"{MAX_ARCHIVO_IMAGEN_BYTES})"
        ),
    )
    args = parser.parse_args(argv)
    try:
        conteos = preparar_dataset_herlev(
            args.source_dir,
            args.splits_dir,
            args.output_dir,
            args.classification,
            args.max_image_bytes,
        )
    except (FileNotFoundError, FileExistsError, OSError, ValueError) as exc:
        parser.error(str(exc))
    for clave, valor in conteos.items():
        print(f"{clave}: {valor}")
    return 0


__all__ = [
    "MAX_ARCHIVO_IMAGEN_BYTES",
    "preparar_dataset_herlev",
    "main",
]
