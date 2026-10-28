"""Módulo de medición de rendimiento y tiempo de procesamiento (CITO-83).

Proporciona funciones para medir el tiempo de ejecución del pipeline,
comparar con procesamiento manual y generar informes de rendimiento.
"""

from __future__ import annotations

import time
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np


# ---------------------------------------------------------------------------
# Constantes y configuración
# ---------------------------------------------------------------------------

# Tiempo estimado de procesamiento manual por imagen (segundos)
# Basado en estudios de tiempo-movimiento en citología cervical
TIEMPO_MANUAL_POR_IMAGEN_SEGUNDOS = 180.0  # 3 minutos por imagen

# Objetivo de reducción de tiempo (70% = 30% del tiempo manual)
OBJETIVO_REDUCCION_PORCENTAJE = 70.0
TIEMPO_OBJETIVO_AUTOMATIZADO_SEGUNDOS = TIEMPO_MANUAL_POR_IMAGEN_SEGUNDOS * (1 - OBJETIVO_REDUCCION_PORCENTAJE / 100)


# ---------------------------------------------------------------------------
# Estructuras de datos
# ---------------------------------------------------------------------------

@dataclass
class MedicionRendimiento:
    """Resultado de una medición de rendimiento individual."""
    nombre_etapa: str
    tiempo_segundos: float
    memoria_mb: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReporteRendimiento:
    """Reporte completo de rendimiento del pipeline."""
    imagen_procesada: str
    tiempo_total_segundos: float
    mediciones_etapas: List[MedicionRendimiento]
    tiempo_manual_estimado_segundos: float = TIEMPO_MANUAL_POR_IMAGEN_SEGUNDOS
    reduccion_lograda_porcentaje: float = 0.0
    cumple_objetivo: bool = False
    timestamp: str = ""
    version_codigo: str = "1.0"
    parametros: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.tiempo_manual_estimado_segundos > 0:
            self.reduccion_lograda_porcentaje = round(
                (1 - self.tiempo_total_segundos / self.tiempo_manual_estimado_segundos) * 100, 2
            )
        self.cumple_objetivo = self.reduccion_lograda_porcentaje >= OBJETIVO_REDUCCION_PORCENTAJE


@dataclass
class EstadisticasRendimiento:
    """Estadísticas agregadas de múltiples ejecuciones."""
    total_ejecuciones: int
    tiempo_promedio_segundos: float
    tiempo_mediano_segundos: float
    tiempo_min_segundos: float
    tiempo_max_segundos: float
    desviacion_estandar_segundos: float
    reduccion_promedio_porcentaje: float
    ejecuciones_cumplen_objetivo: int
    porcentaje_cumplen_objetivo: float


# ---------------------------------------------------------------------------
# Funciones de medición
# ---------------------------------------------------------------------------

class MedidorRendimiento:
    """Clase para medir el rendimiento del pipeline paso a paso."""

    def __init__(self):
        self.mediciones: List[MedicionRendimiento] = []
        self._inicio_actual: Optional[float] = None
        self._etapa_actual: Optional[str] = None

    def iniciar_etapa(self, nombre_etapa: str) -> None:
        """Inicia la medición de una etapa."""
        self._etapa_actual = nombre_etapa
        self._inicio_actual = time.perf_counter()

    def finalizar_etapa(self, metadata: Optional[Dict[str, Any]] = None) -> MedicionRendimiento:
        """Finaliza la medición de la etapa actual."""
        if self._inicio_actual is None or self._etapa_actual is None:
            raise RuntimeError("No hay etapa en curso para finalizar")

        tiempo = time.perf_counter() - self._inicio_actual
        medicion = MedicionRendimiento(
            nombre_etapa=self._etapa_actual,
            tiempo_segundos=tiempo,
            metadata=metadata or {}
        )
        self.mediciones.append(medicion)
        self._inicio_actual = None
        self._etapa_actual = None
        return medicion

    def medir_funcion(self, nombre: str, func: Callable, *args, **kwargs) -> Any:
        """Mide el tiempo de ejecución de una función."""
        self.iniciar_etapa(nombre)
        try:
            resultado = func(*args, **kwargs)
            return resultado
        finally:
            self.finalizar_etapa()

    def obtener_reporte(self, imagen: str, parametros: Optional[Dict[str, Any]] = None) -> ReporteRendimiento:
        """Genera un reporte de rendimiento a partir de las mediciones."""
        tiempo_total = sum(m.tiempo_segundos for m in self.mediciones)
        return ReporteRendimiento(
            imagen_procesada=imagen,
            tiempo_total_segundos=round(tiempo_total, 4),
            mediciones_etapas=self.mediciones.copy(),
            parametros=parametros or {},
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

    def reiniciar(self) -> None:
        """Reinicia el medidor para una nueva medición."""
        self.mediciones.clear()
        self._inicio_actual = None
        self._etapa_actual = None


def medir_pipeline_completo(
    imagen_path: Path,
    funcion_pipeline: Callable[[Path], Dict[str, Any]],
    parametros: Optional[Dict[str, Any]] = None
) -> ReporteRendimiento:
    """
    Mide el rendimiento completo del pipeline para una imagen.

    Args:
        imagen_path: Ruta a la imagen a procesar.
        funcion_pipeline: Función que ejecuta el pipeline completo y retorna resultados.
        parametros: Parámetros usados en el procesamiento (sigma1, sigma2, etc.).

    Returns:
        ReporteRendimiento con todas las mediciones.
    """
    medidor = MedidorRendimiento()

    # Ejecutar pipeline con medición
    medidor.iniciar_etapa("pipeline_completo")
    resultados = funcion_pipeline(imagen_path)
    medidor.finalizar_etapa({"total_celulas": resultados.get("total_celulas", 0)})

    return medidor.obtener_reporte(str(imagen_path), parametros)


def medir_pipeline_por_etapas(
    imagen_path: Path,
    etapas: Dict[str, Callable],
    parametros: Optional[Dict[str, Any]] = None
) -> ReporteRendimiento:
    """
    Mide el rendimiento del pipeline desglosado por etapas.

    Args:
        imagen_path: Ruta a la imagen.
        etapas: Diccionario con nombre de etapa -> función que ejecuta esa etapa.
                Las funciones deben aceptar la imagen (o resultado anterior) y retornar el resultado.
        parametros: Parámetros usados.

    Returns:
        ReporteRendimiento con mediciones por etapa.
    """
    medidor = MedidorRendimiento()
    resultado_anterior = None

    for nombre_etapa, funcion_etapa in etapas.items():
        medidor.iniciar_etapa(nombre_etapa)
        if resultado_anterior is None:
            resultado_anterior = funcion_etapa(imagen_path)
        else:
            resultado_anterior = funcion_etapa(resultado_anterior)
        medidor.finalizar_etapa()

    return medidor.obtener_reporte(str(imagen_path), parametros)


# ---------------------------------------------------------------------------
# Análisis estadístico
# ---------------------------------------------------------------------------

def calcular_estadisticas(reportes: List[ReporteRendimiento]) -> EstadisticasRendimiento:
    """Calcula estadísticas agregadas a partir de múltiples reportes."""
    if not reportes:
        return EstadisticasRendimiento(
            total_ejecuciones=0,
            tiempo_promedio_segundos=0.0,
            tiempo_mediano_segundos=0.0,
            tiempo_min_segundos=0.0,
            tiempo_max_segundos=0.0,
            desviacion_estandar_segundos=0.0,
            reduccion_promedio_porcentaje=0.0,
            ejecuciones_cumplen_objetivo=0,
            porcentaje_cumplen_objetivo=0.0
        )

    tiempos = [r.tiempo_total_segundos for r in reportes]
    reducciones = [r.reduccion_lograda_porcentaje for r in reportes]
    cumplen = sum(1 for r in reportes if r.cumple_objetivo)

    return EstadisticasRendimiento(
        total_ejecuciones=len(reportes),
        tiempo_promedio_segundos=round(statistics.mean(tiempos), 4),
        tiempo_mediano_segundos=round(statistics.median(tiempos), 4),
        tiempo_min_segundos=round(min(tiempos), 4),
        tiempo_max_segundos=round(max(tiempos), 4),
        desviacion_estandar_segundos=round(statistics.stdev(tiempos), 4) if len(tiempos) > 1 else 0.0,
        reduccion_promedio_porcentaje=round(statistics.mean(reducciones), 2),
        ejecuciones_cumplen_objetivo=cumplen,
        porcentaje_cumplen_objetivo=round(cumplen / len(reportes) * 100, 1)
    )


# ---------------------------------------------------------------------------
# Generación de informes
# ---------------------------------------------------------------------------

def generar_informe_rendimiento(
    reportes: List[ReporteRendimiento],
    ruta_salida: Optional[Path] = None
) -> str:
    """
    Genera un informe de rendimiento en formato texto.

    Args:
        reportes: Lista de reportes de rendimiento.
        ruta_salida: Ruta opcional para guardar el informe.

    Returns:
        String con el informe formateado.
    """
    if not reportes:
        return "No hay reportes de rendimiento para generar informe."

    stats = calcular_estadisticas(reportes)

    lineas = [
        "=" * 60,
        "INFORME DE RENDIMIENTO - CITOCOUNTER PROTO (CITO-83)",
        "=" * 60,
        "",
        f"Total de ejecuciones analizadas: {stats.total_ejecuciones}",
        f"Tiempo manual de referencia: {TIEMPO_MANUAL_POR_IMAGEN_SEGUNDOS:.1f} segundos/imagen",
        f"Objetivo de reducción: {OBJETIVO_REDUCCION_PORCENTAJE:.0f}% (≤{TIEMPO_OBJETIVO_AUTOMATIZADO_SEGUNDOS:.1f} seg/imagen)",
        "",
        "ESTADÍSTICAS DE TIEMPO AUTOMATIZADO:",
        f"  Promedio:     {stats.tiempo_promedio_segundos:.4f} segundos",
        f"  Mediano:      {stats.tiempo_mediano_segundos:.4f} segundos",
        f"  Mínimo:       {stats.tiempo_min_segundos:.4f} segundos",
        f"  Máximo:       {stats.tiempo_max_segundos:.4f} segundos",
        f"  Desv. Est.:   {stats.desviacion_estandar_segundos:.4f} segundos",
        "",
        "REDUCCIÓN DE TIEMPO LOGRADA:",
        f"  Promedio:     {stats.reduccion_promedio_porcentaje:.2f}%",
        f"  Cumplen objetivo (≥{OBJETIVO_REDUCCION_PORCENTAJE:.0f}%): {stats.ejecuciones_cumplen_objetivo}/{stats.total_ejecuciones} ({stats.porcentaje_cumplen_objetivo:.1f}%)",
        "",
        "DETALLE POR EJECUCIÓN:",
    ]

    for i, reporte in enumerate(reportes, 1):
        estado = "✅ CUMPLE" if reporte.cumple_objetivo else "❌ NO CUMPLE"
        lineas.append(
            f"  {i:2d}. {reporte.imagen_procesada:30s} | "
            f"{reporte.tiempo_total_segundos:8.4f}s | "
            f"{reporte.reduccion_lograda_porcentaje:6.2f}% | {estado}"
        )

    lineas.extend([
        "",
        "ANÁLISIS POR ETAPAS (promedio):",
    ])

    # Calcular promedios por etapa
    if reportes[0].mediciones_etapas:
        nombres_etapas = set()
        for r in reportes:
            for m in r.mediciones_etapas:
                nombres_etapas.add(m.nombre_etapa)

        for nombre in sorted(nombres_etapas):
            tiempos_etapa = []
            for r in reportes:
                for m in r.mediciones_etapas:
                    if m.nombre_etapa == nombre:
                        tiempos_etapa.append(m.tiempo_segundos)
                        break
            if tiempos_etapa:
                prom = statistics.mean(tiempos_etapa)
                pct = (prom / stats.tiempo_promedio_segundos * 100) if stats.tiempo_promedio_segundos > 0 else 0
                lineas.append(f"  - {nombre:25s}: {prom:.4f}s ({pct:.1f}% del total)")

    lineas.extend([
        "",
        "=" * 60,
        f"CONCLUSIÓN: {'✅ OBJETIVO CUMPLIDO' if stats.porcentaje_cumplen_objetivo >= 50 else '❌ OBJETIVO NO CUMPLIDO'} "
        f"({stats.porcentaje_cumplen_objetivo:.1f}% de ejecuciones cumplen ≥{OBJETIVO_REDUCCION_PORCENTAJE:.0f}% reducción)",
        "=" * 60,
    ])

    informe = "\n".join(lineas)

    if ruta_salida:
        ruta_salida.write_text(informe, encoding="utf-8")

    return informe


def exportar_reporte_csv(reportes: List[ReporteRendimiento], ruta_salida: Path) -> None:
    """Exporta los reportes de rendimiento a CSV."""
    import csv

    campos = [
        "timestamp", "imagen", "tiempo_total_segundos",
        "tiempo_manual_estimado_segundos", "reduccion_lograda_porcentaje",
        "cumple_objetivo", "version_codigo"
    ]

    # Agregar campos para cada etapa
    if reportes and reportes[0].mediciones_etapas:
        for m in reportes[0].mediciones_etapas:
            campos.append(f"etapa_{m.nombre_etapa}_segundos")

    with ruta_salida.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(campos)

        for r in reportes:
            fila = [
                r.timestamp,
                r.imagen_procesada,
                r.tiempo_total_segundos,
                r.tiempo_manual_estimado_segundos,
                r.reduccion_lograda_porcentaje,
                r.cumple_objetivo,
                r.version_codigo
            ]
            # Agregar tiempos por etapa
            if r.mediciones_etapas:
                tiempos_etapa = {m.nombre_etapa: m.tiempo_segundos for m in r.mediciones_etapas}
                for m in reportes[0].mediciones_etapas:
                    fila.append(tiempos_etapa.get(m.nombre_etapa, 0.0))
            writer.writerow(fila)


# ---------------------------------------------------------------------------
# Utilidades para benchmarking
# ---------------------------------------------------------------------------

def benchmark_pipeline(
    imagenes: List[Path],
    funcion_pipeline: Callable[[Path], Dict[str, Any]],
    parametros: Optional[Dict[str, Any]] = None,
    repeticiones: int = 3
) -> List[ReporteRendimiento]:
    """
    Ejecuta benchmark del pipeline sobre múltiples imágenes y repeticiones.

    Args:
        imagenes: Lista de rutas a imágenes.
        funcion_pipeline: Función del pipeline a medir.
        parametros: Parámetros del pipeline.
        repeticiones: Número de veces que se repite cada imagen.

    Returns:
        Lista de reportes de rendimiento.
    """
    reportes = []

    for img_path in imagenes:
        for rep in range(repeticiones):
            parametros_rep = (parametros or {}).copy()
            parametros_rep["repeticion"] = rep + 1
            reporte = medir_pipeline_completo(img_path, funcion_pipeline, parametros_rep)
            reportes.append(reporte)

    return reportes


# ---------------------------------------------------------------------------
# Función principal para uso desde CLI
# ---------------------------------------------------------------------------

def main():
    """Función principal para ejecutar benchmark desde línea de comandos."""
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark de rendimiento CitoCounter (CITO-83)")
    parser.add_argument("directorio", type=Path, help="Directorio con imágenes a procesar")
    parser.add_argument("--repeticiones", type=int, default=3, help="Repeticiones por imagen")
    parser.add_argument("--salida", type=Path, default=Path("data/results/rendimiento_report.txt"), help="Archivo de salida")
    parser.add_argument("--csv", type=Path, default=Path("data/results/rendimiento_data.csv"), help="Archivo CSV de salida")
    parser.add_argument("--sigma1", type=float, default=7.0, help="Sigma1 para DoG")
    parser.add_argument("--sigma2", type=float, default=8.0, help="Sigma2 para DoG")

    args = parser.parse_args()

    # Importar pipeline
    from src.preprocessing import preprocesar_imagen
    from src.dog_filter import aplicar_filtro_dog
    from src.analysis import analizar_nucleos

    def pipeline_completo(img_path: Path) -> Dict[str, Any]:
        # preprocesar_imagen retorna tupla (gris, original)
        img_gris, img_original = preprocesar_imagen(img_path)
        dog = aplicar_filtro_dog(img_gris, args.sigma1, args.sigma2)
        resultados = analizar_nucleos(dog, img_original)
        return resultados

    imagenes = list(args.directorio.glob("*.jpg")) + list(args.directorio.glob("*.png"))
    if not imagenes:
        print(f"No se encontraron imágenes en {args.directorio}")
        return

    print(f"Ejecutando benchmark en {len(imagenes)} imágenes x {args.repeticiones} repeticiones...")
    reportes = benchmark_pipeline(imagenes, pipeline_completo, {"sigma1": args.sigma1, "sigma2": args.sigma2}, args.repeticiones)

    # Generar informe
    informe = generar_informe_rendimiento(reportes, args.salida)
    print(informe)

    # Exportar CSV
    exportar_reporte_csv(reportes, args.csv)
    print(f"\nDatos exportados a: {args.csv}")


if __name__ == "__main__":
    main()