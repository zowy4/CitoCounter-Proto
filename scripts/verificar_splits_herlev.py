"""Verifica manifiestos Herlev y ausencia de fuga entre grupos."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Set
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.herlev_dataset import mapear_elementos_a_grupo_por_prefijo


def _leer_ids(ruta: Path) -> List[str]:
    with ruta.open(newline="", encoding="utf-8") as archivo:
        return [fila["image_id"] for fila in csv.DictReader(archivo)]


def verificar_splits(directorio_fuente: Path, directorio_splits: Path) -> Dict[str, object]:
    """Verifica cobertura, proporciones y fuga de grupos en manifiestos Herlev.

    Parameters
    ----------
    directorio_fuente : pathlib.Path
        Directorio con las imágenes completas y `CROPPED/`.
    directorio_splits : pathlib.Path
        Directorio con `train.csv`, `val.csv` y `test.csv`.

    Returns
    -------
    dict[str, object]
        Conteos por split, clase disponible y grupos compartidos.

    Raises
    ------
    ValueError
        Si hay IDs duplicados, faltantes, desconocidos o grupos compartidos.
    """
    origenes = sorted(p.stem for p in directorio_fuente.glob("*.bmp"))
    elementos = origenes + sorted(p.stem for p in (directorio_fuente / "CROPPED").glob("*.bmp"))
    grupos = mapear_elementos_a_grupo_por_prefijo(elementos, origenes)
    por_split = {nombre: _leer_ids(directorio_splits / f"{nombre}.csv") for nombre in ("train", "val", "test")}
    vistos: Dict[str, str] = {}
    for split, ids in por_split.items():
        for image_id in ids:
            if image_id not in grupos or image_id in vistos:
                raise ValueError(f"ID duplicado o desconocido: {image_id}")
            vistos[image_id] = split
    if set(vistos) != set(origenes):
        raise ValueError("Los manifiestos no cubren exactamente las imágenes completas.")
    elementos_por_split = {
        split: [elemento for elemento in elementos if vistos[grupos[elemento]] == split]
        for split in por_split
    }
    grupos_por_split: Dict[str, Set[str]] = {s: {grupos[i] for i in ids} for s, ids in por_split.items()}
    if any(grupos_por_split[a] & grupos_por_split[b] for a in grupos_por_split for b in grupos_por_split if a < b):
        raise ValueError("Hay grupos de origen repartidos entre splits.")
    return {"elementos": {s: len(ids) for s, ids in elementos_por_split.items()}, "imagenes_completas": {s: len(ids) for s, ids in por_split.items()}, "grupos": {s: len(v) for s, v in grupos_por_split.items()}, "clases": {"Dyskeratotic": len(origenes)}, "total_elementos": len(elementos)}


if __name__ == "__main__":
    resultado = verificar_splits(Path("data/raw/im_Dyskeratotic"), Path("data/ground_truth/herlev/splits"))
    for clave, valor in resultado.items():
        print(f"{clave}: {valor}")
