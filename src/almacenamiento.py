"""Almacenamiento de resultados de experimentación (CITO-30 / ACT-09).

Proporciona una capa de persistencia para resultados de experimentación,
basada en SQLite. Soporta operaciones CRUD y consultas comunes para
el dashboard y la API.

Esquema de la base de datos:
- experimentos: metadatos de cada ejecución (id, fecha, parámetros, resultados)
- metricas: métricas calculadas por ejecución
- imagenes: información de imágenes procesadas
"""

from __future__ import annotations

import csv
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ruta por defecto de la base de datos
DEFAULT_DB_PATH = Path("data/experimentos.db")

# Esquema de la base de datos
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS experimentos (
    id_prueba TEXT PRIMARY KEY,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    imagen TEXT NOT NULL,
    sigma1 REAL NOT NULL,
    sigma2 REAL NOT NULL,
    polaridad TEXT NOT NULL DEFAULT 'nucleos-claros',
    area_promedio_normal REAL,
    factor_riesgo REAL,
    area_minima REAL,
    total_celulas INTEGER,
    normales INTEGER,
    sospechosas INTEGER,
    frontera INTEGER,
    porcentaje_riesgo REAL,
    falsos_positivos INTEGER,
    falsos_negativos INTEGER,
    precision_estimada REAL,
    observaciones TEXT,
    calidad_dog TEXT,
    ajuste_siguiente TEXT,
    responsable TEXT,
    fecha_creacion TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_experimentos_fecha ON experimentos(fecha);
CREATE INDEX IF NOT EXISTS idx_experimentos_imagen ON experimentos(imagen);
CREATE INDEX IF NOT EXISTS idx_experimentos_sigma ON experimentos(sigma1, sigma2);
"""

# ---------------------------------------------------------------------------
# Conexión y utilidades
# ---------------------------------------------------------------------------

def get_db_path() -> Path:
    """Devuelve la ruta de la base de datos, creándola si no existe."""
    db_path = Path("data/experimentos.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


@contextmanager
def get_connection(db_path: Optional[Path] = None):
    """Context manager para conexiones SQLite con commit/rollback automático."""
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def inicializar_db(db_path: Optional[Path] = None) -> None:
    """Inicializa la base de datos creando las tablas si no existen."""
    path = db_path or get_db_path()
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


# ---------------------------------------------------------------------------
# Operaciones CRUD para experimentos
# ---------------------------------------------------------------------------

def insertar_experimento(
    datos: Dict[str, Any],
    db_path: Optional[Path] = None
) -> str:
    """Inserta un nuevo experimento en la base de datos.

    Args:
        datos: Diccionario con los campos del experimento.
               Debe incluir al menos: id_prueba, fecha, hora, imagen,
               sigma1, sigma2, total_celulas, normales, sospechosas,
               porcentaje_riesgo.
        db_path: Ruta opcional de la base de datos.

    Returns:
        El id_prueba del experimento insertado.
    """
    # Validar campos obligatorios
    campos_obligatorios = [
        "id_prueba", "fecha", "hora", "imagen",
        "sigma1", "sigma2", "total_celulas",
        "normales", "sospechosas", "porcentaje_riesgo"
    ]
    for campo in campos_obligatorios:
        if campo not in datos or datos[campo] is None:
            raise ValueError(f"Campo obligatorio faltante: {campo}")

    # Preparar datos para inserción
    campos = [
        "id_prueba", "fecha", "hora", "imagen", "sigma1", "sigma2",
        "polaridad", "area_promedio_normal", "factor_riesgo", "area_minima",
        "total_celulas", "normales", "sospechosas", "frontera",
        "porcentaje_riesgo", "falsos_positivos", "falsos_negativos",
        "precision_estimada", "observaciones", "calidad_dog",
        "ajuste_siguiente", "responsable"
    ]

    valores = []
    for campo in [
        "id_prueba", "fecha", "hora", "imagen", "sigma1", "sigma2",
        "polaridad", "area_promedio_normal", "factor_riesgo", "area_minima",
        "total_celulas", "normales", "sospechosas", "frontera",
        "porcentaje_riesgo", "falsos_positivos", "falsos_negativos",
        "precision_estimada", "observaciones", "calidad_dog",
        "ajuste_siguiente", "responsable"
    ]:
        valor = datos.get(campo)
        if campo in {"total_celulas", "normales", "sospechosas", "frontera",
                       "falsos_positivos", "falsos_negativos"}:
            valores.append(int(datos[campo]) if datos.get(campo) is not None else None)
        elif campo in {"sigma1", "sigma2", "porcentaje_riesgo",
                       "area_promedio_normal", "factor_riesgo", "area_minima",
                       "precision_estimada"}:
            valores.append(float(datos[campo]) if datos.get(campo) is not None else None)
        else:
            valores.append(datos.get(campo))

    placeholders = ", ".join(["?"] * len(campos))
    sql = f"INSERT INTO experimentos ({', '.join(campos)}) VALUES ({placeholders})"

    with sqlite3.connect(get_db_path()) as conn:
        conn.execute("INSERT OR REPLACE INTO experimentos (" +
                     ", ".join(campos) + ") VALUES (" + placeholders + ")",
                     valores)
        conn.commit()

    return datos["id_prueba"]


def obtener_experimento(id_prueba: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Obtiene un experimento por su ID."""
    with sqlite3.connect(get_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM experimentos WHERE id_prueba = ?", (id_prueba,)
        )
        fila = cursor.fetchone()
        return dict(fila) if fila else None


def listar_experimentos(
    limite: int = 100,
    offset: int = 0,
    filtro_imagen: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Lista experimentos con filtros opcionales y paginación."""
    condiciones = []
    params = []

    if filtro_imagen:
        condiciones.append("imagen LIKE ?")
        params.append(f"%{filtro_imagen}%")

    if fecha_desde:
        condiciones.append("fecha >= ?")
        params.append(fecha_desde)

    if fecha_hasta:
        condiciones.append("fecha <= ?")
        params.append(fecha_hasta)

    where_clause = "WHERE " + " AND ".join(condiciones) if condiciones else ""

    sql = f"""
        SELECT * FROM experimentos
        {where_clause}
        ORDER BY fecha DESC, hora DESC
        LIMIT ? OFFSET ?
    """
    params.extend([limite, offset])

    with sqlite3.connect(get_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql, params)
        return [dict(fila) for fila in cursor.fetchall()]


def contar_experimentos(
    filtro_imagen: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    db_path: Optional[Path] = None
) -> int:
    """Cuenta el total de experimentos con filtros opcionales."""
    condiciones = []
    params = []

    if filtro_imagen:
        condiciones.append("imagen LIKE ?")
        params.append(f"%{filtro_imagen}%")

    if fecha_desde:
        condiciones.append("fecha >= ?")
        params.append(fecha_desde)

    if fecha_hasta:
        condiciones.append("fecha <= ?")
        params.append(fecha_hasta)

    where_clause = "WHERE " + " AND ".join(condiciones) if condiciones else ""

    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.execute(
            f"SELECT COUNT(*) FROM experimentos {where_clause}", params
        )
        return cursor.fetchone()[0]


def actualizar_experimento(
    id_prueba: str,
    datos: Dict[str, Any],
    db_path: Optional[Path] = None
) -> bool:
    """Actualiza un experimento existente."""
    if not datos:
        return False

    campos_actualizables = [
        "sigma1", "sigma2", "polaridad", "area_promedio_normal",
        "factor_riesgo", "area_minima", "total_celulas", "normales",
        "sospechosas", "frontera", "porcentaje_riesgo",
        "falsos_positivos", "falsos_negativos", "precision_estimada",
        "observaciones", "calidad_dog", "ajuste_siguiente", "responsable"
    ]

    campos = []
    valores = []
    for campo in campos_actualizables:
        if campo in datos:
            campos.append(f"{campo} = ?")
            valores.append(datos[campo])

    if not campos:
        return False

    valores.append(id_prueba)
    sql = f"UPDATE experimentos SET {', '.join(campos)} WHERE id_prueba = ?"

    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.execute(sql, valores)
        conn.commit()
        return cursor.rowcount > 0


def eliminar_experimento(id_prueba: str, db_path: Optional[Path] = None) -> bool:
    """Elimina un experimento por su ID."""
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.execute("DELETE FROM experimentos WHERE id_prueba = ?", (id_prueba,))
        conn.commit()
        return cursor.rowcount > 0


def obtener_estadisticas_generales(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Obtiene estadísticas generales de la base de datos."""
    with sqlite3.connect(get_db_path()) as conn:
        conn.row_factory = sqlite3.Row

        # Total de experimentos
        total = conn.execute("SELECT COUNT(*) FROM experimentos").fetchone()[0]

        # Imágenes únicas
        imagenes_unicas = conn.execute(
            "SELECT COUNT(DISTINCT imagen) FROM experimentos"
        ).fetchone()[0]

        # Totales de células
        totales = conn.execute("""
            SELECT
                SUM(total_celulas) as total_celulas,
                SUM(normales) as total_normales,
                SUM(sospechosas) as total_sospechosas,
                AVG(porcentaje_riesgo) as riesgo_promedio
            FROM experimentos
        """).fetchone()

        # Distribución por sigma
        por_sigma = conn.execute("""
            SELECT sigma1, sigma2, COUNT(*) as count,
                   AVG(total_celulas) as avg_celulas,
                   AVG(porcentaje_riesgo) as avg_riesgo
            FROM experimentos
            GROUP BY sigma1, sigma2
            ORDER BY count DESC
        """).fetchall()

        return {
            "total_experimentos": total,
            "imagenes_unicas": imagenes_unicas,
            "total_celulas": totales["total_celulas"] or 0,
            "total_normales": totales["total_normales"] or 0,
            "total_sospechosas": totales["total_sospechosas"] or 0,
            "riesgo_promedio": round(totales["riesgo_promedio"] or 0, 2),
            "por_sigma": [dict(row) for row in por_sigma],
        }


def exportar_a_csv(ruta_salida: Path, db_path: Optional[Path] = None) -> None:
    """Exporta todos los experimentos a un archivo CSV."""
    with sqlite3.connect(get_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM experimentos ORDER BY fecha DESC, hora DESC")
        filas = cursor.fetchall()

    if not filas:
        return

    campos = list(filas[0].keys())
    with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(campos)
        for fila in filas:
            writer.writerow([fila[c] for c in campos])


def exportar_a_json(ruta_salida: Path, db_path: Optional[Path] = None) -> None:
    """Exporta todos los experimentos a un archivo JSON."""
    with sqlite3.connect(get_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM experimentos ORDER BY fecha DESC, hora DESC")
        filas = [dict(fila) for fila in cursor.fetchall()]

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(filas, f, indent=2, ensure_ascii=False, default=str)


def limpiar_experimentos_antiguos(dias: int = 365, db_path: Optional[Path] = None) -> int:
    """Elimina experimentos más antiguos que los días especificados."""
    fecha_limite = datetime.now().strftime("%Y-%m-%d")
    # Usar date() de SQLite para restar días
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.execute(
            "DELETE FROM experimentos WHERE fecha < date(?, ?)",
            (datetime.now().strftime("%Y-%m-%d"), f"-{dias} days")
        )
        conn.commit()
        return cursor.rowcount


# ---------------------------------------------------------------------------
# Inicialización automática al importar
# ---------------------------------------------------------------------------

# Inicializar la base de datos al importar el módulo
inicializar_db()

# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

__all__ = [
    "inicializar_db",
    "insertar_experimento",
    "obtener_experimento",
    "listar_experimentos",
    "contar_experimentos",
    "actualizar_experimento",
    "eliminar_experimento",
    "obtener_estadisticas_generales",
    "exportar_a_csv",
    "exportar_a_json",
    "limpiar_experimentos_antiguos",
    "get_db_path",
]