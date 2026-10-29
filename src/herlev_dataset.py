"""Lectura validada de polígonos de anotación del dataset Herlev."""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import cv2
import numpy as np

Coordenada = Tuple[float, float]
Poligono = List[Coordenada]
RegistroCelula = Dict[str, str]

MAX_TAMANO_DAT_BYTES = 1_048_576
MAX_MASCARA_BYTES = 64 * 1024 * 1024
CAMPOS_CSV_CELULAS = (
    "Cell_ID",
    "X",
    "Y",
    "Width",
    "Height",
    "Classification",
    "Notes",
)


def cargar_poligono_dat(ruta_dat: str | Path) -> Poligono:
    """Lee un polígono Herlev almacenado como pares x,y separados por coma.

    Parameters
    ----------
    ruta_dat : str | pathlib.Path
        Ruta del archivo de anotación `.dat`.

    Returns
    -------
    Poligono
        Lista ordenada de coordenadas `(x, y)` como números flotantes.

    Raises
    ------
    FileNotFoundError
        Si la ruta no existe o no es un archivo.
    ValueError
        Si el archivo excede el límite, está vacío, contiene coordenadas
        inválidas o no define al menos tres vértices.
    """
    ruta = Path(ruta_dat)
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de anotación: {ruta}")

    tamano = ruta.stat().st_size
    if tamano > MAX_TAMANO_DAT_BYTES:
        raise ValueError(
            f"El archivo de anotación excede el límite de "
            f"{MAX_TAMANO_DAT_BYTES} bytes: {ruta}"
        )
    if tamano == 0:
        raise ValueError(f"El archivo de anotación está vacío: {ruta}")

    poligono: Poligono = []
    with ruta.open("r", newline="", encoding="utf-8-sig") as archivo:
        lector = csv.reader(archivo, skipinitialspace=True)
        for numero_linea, fila in enumerate(lector, start=1):
            if not fila or all(not campo.strip() for campo in fila):
                continue
            if len(fila) != 2:
                raise ValueError(
                    f"Formato inválido en {ruta}, línea {numero_linea}: "
                    "se esperaban dos coordenadas separadas por coma."
                )

            try:
                x, y = (float(campo.strip()) for campo in fila)
            except ValueError as exc:
                raise ValueError(
                    f"Coordenada inválida en {ruta}, línea {numero_linea}."
                ) from exc

            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError(
                    f"Coordenada no finita en {ruta}, línea {numero_linea}."
                )
            poligono.append((x, y))

    if len(poligono) < 3:
        raise ValueError(
            f"El polígono en {ruta} debe contener al menos tres vértices."
        )
    return poligono


def _cargar_poligonos_por_tipo(
    ruta_imagen: str | Path, tipo: str
) -> List[Poligono]:
    """Carga en orden determinista los polígonos asociados con una imagen."""
    imagen = Path(ruta_imagen)
    if not imagen.is_file():
        raise FileNotFoundError(f"No se encontró la imagen de referencia: {imagen}")

    patron = re.compile(
        rf"^{re.escape(imagen.stem)}_{tipo}\d*\.dat$",
        flags=re.IGNORECASE,
    )
    archivos = sorted(
        (ruta for ruta in imagen.parent.iterdir() if patron.fullmatch(ruta.name)),
        key=lambda ruta: ruta.name.lower(),
    )
    if not archivos:
        raise FileNotFoundError(
            f"No se encontraron anotaciones {tipo} para la imagen {imagen.name}."
        )
    return [cargar_poligono_dat(ruta) for ruta in archivos]


def cargar_poligonos_nucleo(ruta_imagen: str | Path) -> List[Poligono]:
    """Carga los polígonos de núcleo asociados a una imagen Herlev.

    Parameters
    ----------
    ruta_imagen : str | pathlib.Path
        Ruta a la imagen completa o crop. Las anotaciones deben estar junto a
        ella y seguir el patrón `<stem>_nuc*.dat`.

    Returns
    -------
    list[Poligono]
        Polígonos de núcleo en orden determinista.

    Raises
    ------
    FileNotFoundError
        Si la imagen o sus archivos de anotación no existen.
    ValueError
        Si alguna anotación asociada no contiene un polígono válido.
    """
    return _cargar_poligonos_por_tipo(ruta_imagen, "nuc")


def cargar_poligonos_citoplasma(ruta_imagen: str | Path) -> List[Poligono]:
    """Carga los polígonos de citoplasma asociados a una imagen Herlev.

    Parameters
    ----------
    ruta_imagen : str | pathlib.Path
        Ruta a la imagen completa o crop. Las anotaciones deben estar junto a
        ella y seguir el patrón `<stem>_cyt*.dat`.

    Returns
    -------
    list[Poligono]
        Polígonos de citoplasma en orden determinista.

    Raises
    ------
    FileNotFoundError
        Si la imagen o sus archivos de anotación no existen.
    ValueError
        Si alguna anotación asociada no contiene un polígono válido.
    """
    return _cargar_poligonos_por_tipo(ruta_imagen, "cyt")


def rasterizar_mascara(
    poligonos: Sequence[Sequence[Coordenada]],
    dimensiones: Tuple[int, int],
) -> np.ndarray:
    """Rasteriza polígonos a una máscara binaria uint8 con OpenCV.

    Parameters
    ----------
    poligonos : Sequence[Sequence[Coordenada]]
        Polígonos en coordenadas `(x, y)`. Una colección vacía es válida y
        produce una máscara completamente negra.
    dimensiones : tuple[int, int]
        Alto y ancho de la máscara, en ese orden.

    Returns
    -------
    numpy.ndarray
        Máscara de forma `(alto, ancho)`, dtype `uint8`, con valores 0 y 255.

    Raises
    ------
    ValueError
        Si las dimensiones no son enteros positivos, la máscara excede el
        límite de memoria, o un polígono tiene forma/coordenadas inválidas o
        menos de tres vértices.
    """
    if (
        not isinstance(dimensiones, (tuple, list))
        or len(dimensiones) != 2
        or any(
            isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0
            for valor in dimensiones
        )
    ):
        raise ValueError("dimensiones debe contener alto y ancho enteros positivos.")

    alto, ancho = dimensiones
    if alto * ancho > MAX_MASCARA_BYTES:
        raise ValueError(
            f"La máscara excede el límite de {MAX_MASCARA_BYTES} bytes."
        )

    mascara = np.zeros((alto, ancho), dtype=np.uint8)
    if not poligonos:
        return mascara

    poligonos_cv: List[np.ndarray] = []
    limites_int32 = np.iinfo(np.int32)
    for indice, poligono in enumerate(poligonos):
        try:
            puntos = np.asarray(poligono, dtype=np.float64)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"El polígono en la posición {indice} tiene coordenadas inválidas."
            ) from exc

        if puntos.ndim != 2 or puntos.shape[1] != 2 or puntos.shape[0] < 3:
            raise ValueError(
                f"El polígono en la posición {indice} debe tener al menos "
                "tres pares (x, y)."
            )
        if not np.isfinite(puntos).all():
            raise ValueError(
                f"El polígono en la posición {indice} contiene coordenadas no finitas."
            )
        if (
            (puntos < limites_int32.min).any()
            or (puntos > limites_int32.max).any()
        ):
            raise ValueError(
                f"El polígono en la posición {indice} excede el rango de coordenadas."
            )

        puntos_enteros = np.rint(puntos).astype(np.int32).reshape((-1, 1, 2))
        poligonos_cv.append(puntos_enteros)

    cv2.fillPoly(mascara, poligonos_cv, color=255)
    return mascara


def poligonos_a_registros(
    poligonos: Sequence[Sequence[Coordenada]],
    dimensiones: Tuple[int, int],
    clasificacion: str,
    notas: str = "",
) -> List[RegistroCelula]:
    """Convierte polígonos a registros del CSV de ground truth existente.

    X/Y representan la esquina superior izquierda de la caja delimitadora
    (coordenadas de píxel base cero); Width/Height incluyen ambos extremos
    después de redondear vértices al entero más cercano como en el rasterizador.
    Las cajas se limitan al lienzo. Se asignan Cell_ID secuenciales por imagen;
    no se infieren clases clínicas ni notas.

    Parameters
    ----------
    poligonos : Sequence[Sequence[Coordenada]]
        Polígonos nucleares ordenados de una imagen.
    dimensiones : tuple[int, int]
        Alto y ancho de la imagen, en ese orden.
    clasificacion : str
        Etiqueta fuente conocida, por ejemplo `Dyskeratotic`; se conserva tal cual.
    notas : str, optional
        Nota explícita común a los registros. Por defecto es una cadena vacía.

    Returns
    -------
    list[RegistroCelula]
        Filas con las columnas Cell_ID, X, Y, Width, Height, Classification y Notes.
        Los valores se serializan como cadenas para escribirlos directamente en CSV.

    Raises
    ------
    ValueError
        Si las dimensiones, clasificación, notas o polígonos no son válidos,
        o si una caja delimitadora queda completamente fuera de la imagen.
    """
    if (
        not isinstance(dimensiones, (tuple, list))
        or len(dimensiones) != 2
        or any(
            isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0
            for valor in dimensiones
        )
    ):
        raise ValueError("dimensiones debe contener alto y ancho enteros positivos.")
    if not isinstance(clasificacion, str) or not clasificacion.strip():
        raise ValueError("clasificacion debe ser una etiqueta fuente no vacía.")
    if not isinstance(notas, str):
        raise ValueError("notas debe ser una cadena.")

    alto, ancho = dimensiones
    if alto * ancho > MAX_MASCARA_BYTES:
        raise ValueError(
            f"Las dimensiones exceden el límite de {MAX_MASCARA_BYTES} píxeles."
        )

    registros: List[RegistroCelula] = []
    limites_int32 = np.iinfo(np.int32)
    for indice, poligono in enumerate(poligonos, start=1):
        try:
            puntos = np.asarray(poligono, dtype=np.float64)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"El polígono {indice} tiene coordenadas inválidas."
            ) from exc

        if puntos.ndim != 2 or puntos.shape[1] != 2 or puntos.shape[0] < 3:
            raise ValueError(
                f"El polígono {indice} debe tener al menos tres pares (x, y)."
            )
        if not np.isfinite(puntos).all():
            raise ValueError(f"El polígono {indice} contiene coordenadas no finitas.")
        if (
            (puntos < limites_int32.min).any()
            or (puntos > limites_int32.max).any()
        ):
            raise ValueError(f"El polígono {indice} excede el rango de coordenadas.")

        puntos_enteros = np.rint(puntos).astype(np.int64)
        x_min = max(int(puntos_enteros[:, 0].min()), 0)
        y_min = max(int(puntos_enteros[:, 1].min()), 0)
        x_max = min(int(puntos_enteros[:, 0].max()), ancho - 1)
        y_max = min(int(puntos_enteros[:, 1].max()), alto - 1)
        if x_min > x_max or y_min > y_max:
            raise ValueError(
                f"La caja delimitadora del polígono {indice} queda fuera de la imagen."
            )

        registros.append(
            {
                "Cell_ID": str(indice),
                "X": str(x_min),
                "Y": str(y_min),
                "Width": str(x_max - x_min + 1),
                "Height": str(y_max - y_min + 1),
                "Classification": clasificacion,
                "Notes": notas,
            }
        )
    return registros


def guardar_csv_celulas(
    ruta_salida: str | Path,
    registros: Sequence[Mapping[str, str]],
) -> None:
    """Escribe registros de células en el esquema CSV existente sin sobrescribir.

    Parameters
    ----------
    ruta_salida : str | pathlib.Path
        Archivo CSV nuevo dentro de un directorio ya existente.
    registros : Sequence[Mapping[str, str]]
        Filas con exactamente las claves de `CAMPOS_CSV_CELULAS`.

    Returns
    -------
    None
        Escribe el archivo UTF-8 y no devuelve valor.

    Raises
    ------
    FileExistsError
        Si el archivo destino ya existe; no se reemplazan salidas locales.
    FileNotFoundError
        Si el directorio destino no existe.
    ValueError
        Si los registros no cumplen el esquema de columnas.
    """
    ruta = Path(ruta_salida)
    campos_esperados = set(CAMPOS_CSV_CELULAS)
    for indice, registro in enumerate(registros, start=1):
        if set(registro) != campos_esperados:
            raise ValueError(
                f"El registro {indice} debe contener exactamente las columnas "
                "del esquema cells.csv."
            )
        if any(not isinstance(registro[campo], str) for campo in CAMPOS_CSV_CELULAS):
            raise ValueError(f"El registro {indice} contiene valores no textuales.")

    with ruta.open("x", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS_CSV_CELULAS)
        escritor.writeheader()
        escritor.writerows(registros)


def propagar_splits_por_grupo(
    grupos_por_split: Mapping[str, Sequence[str]],
    grupo_por_elemento: Mapping[str, str],
) -> Dict[str, List[str]]:
    """Asigna elementos relacionados al split de su grupo de origen.

    Parameters
    ----------
    grupos_por_split : Mapping[str, Sequence[str]]
        Grupos de origen asignados a cada split, por ejemplo `train`, `val`
        y `test`.
    grupo_por_elemento : Mapping[str, str]
        Mapa de cada identificador de imagen/elemento a su grupo de origen.

    Returns
    -------
    dict[str, list[str]]
        Identificadores ordenados por split. Todos los elementos del mismo
        grupo se asignan juntos.

    Raises
    ------
    ValueError
        Si un grupo aparece en más de un split, hay identificadores vacíos,
        o la asignación de grupos y elementos no coincide exactamente.
    """
    split_por_grupo: Dict[str, str] = {}
    for split, grupos in grupos_por_split.items():
        if not isinstance(split, str) or not split.strip():
            raise ValueError("Cada split debe tener un nombre no vacío.")
        for grupo in grupos:
            if not isinstance(grupo, str) or not grupo.strip():
                raise ValueError("Los identificadores de grupo no pueden estar vacíos.")
            if grupo in split_por_grupo:
                raise ValueError(
                    f"El grupo {grupo!r} está asignado a más de un split."
                )
            split_por_grupo[grupo] = split

    elementos_por_split: Dict[str, List[str]] = {
        split: [] for split in grupos_por_split
    }
    grupos_en_elementos: set[str] = set()
    for elemento, grupo in grupo_por_elemento.items():
        if not isinstance(elemento, str) or not elemento.strip():
            raise ValueError("Los identificadores de elemento no pueden estar vacíos.")
        if not isinstance(grupo, str) or not grupo.strip():
            raise ValueError("Los identificadores de grupo no pueden estar vacíos.")
        split = split_por_grupo.get(grupo)
        if split is None:
            raise ValueError(
                f"El grupo del elemento {elemento!r} no está asignado a un split."
            )
        grupos_en_elementos.add(grupo)
        elementos_por_split[split].append(elemento)

    grupos_sin_elementos = set(split_por_grupo) - grupos_en_elementos
    if grupos_sin_elementos:
        raise ValueError("Hay grupos asignados sin elementos asociados.")

    return {
        split: sorted(elementos)
        for split, elementos in elementos_por_split.items()
    }


def mapear_elementos_a_grupo_por_prefijo(
    elementos: Sequence[str],
    grupos_origen: Sequence[str],
) -> Dict[str, str]:
    """Asocia imágenes y crops con el grupo de origen por prefijo de nombre.

    Se selecciona el prefijo coincidente más largo para permitir que un
    identificador de origen sea prefijo de otro. Este criterio solo debe
    usarse en conjuntos cuya convención de nombres haya sido verificada.

    Parameters
    ----------
    elementos : Sequence[str]
        Identificadores de imágenes completas y/o crops.
    grupos_origen : Sequence[str]
        Identificadores de imágenes fuente que definen grupos independientes.

    Returns
    -------
    dict[str, str]
        Mapa de cada elemento a su identificador de grupo de origen.

    Raises
    ------
    ValueError
        Si los identificadores están vacíos, hay grupos repetidos, algún
        elemento no coincide con un grupo o el prefijo más largo es ambiguo.
    """
    if any(not isinstance(grupo, str) or not grupo for grupo in grupos_origen):
        raise ValueError("Los identificadores de origen deben ser no vacíos.")
    if len(set(grupos_origen)) != len(grupos_origen):
        raise ValueError("Los identificadores de origen deben ser únicos.")
    if not grupos_origen:
        raise ValueError("Se requiere al menos un identificador de origen.")

    resultado: Dict[str, str] = {}
    for elemento in elementos:
        if not isinstance(elemento, str) or not elemento:
            raise ValueError("Los identificadores de elemento deben ser no vacíos.")
        candidatos = [
            grupo for grupo in grupos_origen if elemento.startswith(grupo)
        ]
        if not candidatos:
            raise ValueError(
                f"No se encontró grupo de origen para el elemento {elemento!r}."
            )
        resultado[elemento] = max(candidatos, key=len)
    return resultado


__all__ = [
    "Coordenada",
    "Poligono",
    "RegistroCelula",
    "CAMPOS_CSV_CELULAS",
    "MAX_TAMANO_DAT_BYTES",
    "MAX_MASCARA_BYTES",
    "cargar_poligono_dat",
    "cargar_poligonos_nucleo",
    "cargar_poligonos_citoplasma",
    "rasterizar_mascara",
    "poligonos_a_registros",
    "guardar_csv_celulas",
    "propagar_splits_por_grupo",
    "mapear_elementos_a_grupo_por_prefijo",
]