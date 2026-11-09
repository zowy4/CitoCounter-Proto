"""
src/protocolo_microscopio_real.py - Protocolo de validación en microscopio real (Fase 6.1).

Gestiona el registro de metadatos, calibración óptica, configuración de cámara
y bitácora de pruebas con laminillas físicas en microscopio óptico con cámara acoplada.
"""

from typing import Dict, Any, List, Optional
import datetime
import json
import os


class ProtocoloMicroscopioReal:
    """Gestiona el protocolo de validación experimental con muestras físicas de microscopía."""

    def __init__(self, ruta_bitacora: str = "data/results/bitacora_microscopio.json") -> None:
        """
        Inicializa el protocolo de validación en microscopio real.

        :param ruta_bitacora: Ruta al archivo JSON donde se registran las pruebas físicas.
        :type ruta_bitacora: str
        """
        self.ruta_bitacora: str = ruta_bitacora
        self._asegurar_directorio()

    def _asegurar_directorio(self) -> None:
        """Crea el directorio de resultados si no existe."""
        dir_name = os.path.dirname(self.ruta_bitacora)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

    def registrar_prueba_fisica(
        self,
        laminilla_id: str,
        aumento: str,
        tiempo_exposicion_ms: float,
        ganancia: float,
        conteo_manual: int,
        conteo_sistema: int,
        observaciones: str = ""
    ) -> Dict[str, Any]:
        """
        Registra una prueba realizada con laminilla física en el microscopio.

        :param laminilla_id: Identificador único de la laminilla física.
        :type laminilla_id: str
        :param aumento: Aumento óptico utilizado ('4x', '10x', '40x', '100x').
        :type aumento: str
        :param tiempo_exposicion_ms: Tiempo de exposición de la cámara en milisegundos.
        :type tiempo_exposicion_ms: float
        :param ganancia: Ganancia configurada en la cámara USB/C-mount.
        :type ganancia: float
        :param conteo_manual: Conteo de referencia realizado por el citólogo experto.
        :type conteo_manual: int
        :param conteo_sistema: Conteo obtenido por el algoritmo CitoCounter-Proto.
        :type conteo_sistema: int
        :param observaciones: Notas adicionales sobre la calidad de la muestra o tinción.
        :type observaciones: str
        :return: Diccionario con el registro consolidado y error relativo.
        :rtype: Dict[str, Any]
        """
        if conteo_manual < 0 or conteo_sistema < 0:
            raise ValueError("Los conteos no pueden ser negativos.")

        error_absoluto = abs(conteo_sistema - conteo_manual)
        error_relativo_pct = (error_absoluto / float(conteo_manual) * 100.0) if conteo_manual > 0 else (0.0 if conteo_sistema == 0 else 100.0)

        registro = {
            "timestamp": datetime.datetime.now().isoformat(),
            "laminilla_id": laminilla_id,
            "aumento": aumento,
            "tiempo_exposicion_ms": tiempo_exposicion_ms,
            "ganancia": ganancia,
            "conteo_manual": conteo_manual,
            "conteo_sistema": conteo_sistema,
            "error_absoluto": error_absoluto,
            "error_relativo_pct": round(error_relativo_pct, 2),
            "observaciones": observaciones
        }

        self._guardar_registro(registro)
        return registro

    def _guardar_registro(self, registro: Dict[str, Any]) -> None:
        """Agrega y guarda el registro en el archivo JSON de bitácora."""
        registros = []
        if os.path.exists(self.ruta_bitacora):
            try:
                with open(self.ruta_bitacora, "r", encoding="utf-8") as f:
                    registros = json.load(f)
            except Exception:
                registros = []

        registros.append(registro)
        with open(self.ruta_bitacora, "w", encoding="utf-8") as f:
            json.dump(registros, f, indent=4, ensure_ascii=False)

    def obtener_resumen(self) -> Dict[str, Any]:
        """
        Obtiene un resumen estadístico de las pruebas físicas registradas.

        :return: Diccionario con total de pruebas y error relativo promedio.
        :rtype: Dict[str, Any]
        """
        if not os.path.exists(self.ruta_bitacora):
            return {"total_pruebas": 0, "error_relativo_promedio_pct": 0.0}

        try:
            with open(self.ruta_bitacora, "r", encoding="utf-8") as f:
                registros = json.load(f)
        except Exception:
            return {"total_pruebas": 0, "error_relativo_promedio_pct": 0.0}

        total = len(registros)
        if total == 0:
            return {"total_pruebas": 0, "error_relativo_promedio_pct": 0.0}

        promedio_error = sum(r["error_relativo_pct"] for r in registros) / float(total)
        return {
            "total_pruebas": total,
            "error_relativo_promedio_pct": round(promedio_error, 2)
        }
