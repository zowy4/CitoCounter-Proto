"""
Módulo de Sistema de Bitácora y Versionado para CitoCounter-Proto (Fase 7.1).
Registra experimentos, hiperparámetros, métricas y artefactos con trazabilidad completa.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import subprocess

@dataclass
class RegistroExperimento:
    """
    Contrato de datos para un registro de experimento en la bitácora.
    """
    experimento_id: str
    nombre_modelo: str
    hiperparametros: Dict[str, Any] = field(default_factory=dict)
    metricas: Dict[str, float] = field(default_factory=dict)
    artefactos: List[str] = field(default_factory=list)
    git_commit: str = ""
    fecha_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    observaciones: str = ""


class SistemaBitacora:
    """
    Gestor de bitácora y versionado de experimentos para trazabilidad clínica e investigativa.
    """
    def __init__(self, ruta_bitacora: str = "data/results/bitacora_experimentos.json") -> None:
        """:param ruta_bitacora: Ruta al archivo JSON donde se persiste la bitácora.
        :type ruta_bitacora: str
        """
        self.ruta_bitacora = ruta_bitacora
        self._asegurar_directorio()

    def _asegurar_directorio(self) -> None:
        """Crea el directorio contenedor de la bitácora si no existe."""
        dir_name = os.path.dirname(self.ruta_bitacora)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

    def _obtener_git_commit(self) -> str:
        """Obtiene el hash del commit actual de Git si es posible."""
        try:
            resultado = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return resultado.stdout.strip()
        except Exception:
            return "desconocido"

    def registrar_experimento(
        self,
        experimento_id: str,
        nombre_modelo: str,
        hiperparametros: Dict[str, Any],
        metricas: Dict[str, float],
        artefactos: Optional[List[str]] = None,
        observaciones: str = ""
    ) -> RegistroExperimento:
        """
        Registra un nuevo experimento en la bitácora con control de versiones y metadatos.

        :param experimento_id: Identificador único del experimento.
        :type experimento_id: str
        :param nombre_modelo: Nombre o configuración del modelo/pipeline.
        :type nombre_modelo: str
        :param hiperparametros: Diccionario de hiperparámetros (ej. umbrales, sigmas).
        :type hiperparametros: dict
        :param metricas: Diccionario de métricas obtenidas (ej. F1, precisión, recall).
        :type metricas: dict
        :param artefactos: Lista de rutas a artefactos generados.
        :type artefactos: list, optional
        :param observaciones: Notas adicionales sobre la ejecución.
        :type observaciones: str
        :rtype: RegistroExperimento
        """
        # Validación simple de tamaño de datos (seguridad estilo OWASP/STRIDE)
        if len(str(hiperparametros)) > 65536 or len(str(metricas)) > 65536:
            raise ValueError("El tamaño de hiperparámetros o métricas excede el límite permitido de 64 KiB.")

        registro = RegistroExperimento(
            experimento_id=experimento_id,
            nombre_modelo=nombre_modelo,
            hiperparametros=hiperparametros,
            metricas=metricas,
            artefactos=artefactos or [],
            git_commit=self._obtener_git_commit(),
            observaciones=observaciones
        )

        self._guardar_registro(registro)
        return registro

    def _guardar_registro(self, registro: RegistroExperimento) -> None:
        """Agrega y persiste el registro en el archivo JSON de la bitácora."""
        registros_actuales = self.cargar_bitacora()
        
        # Reemplazar si ya existe el experimento_id
        registros_actuales = [r for r in registros_actuales if r["experimento_id"] != registro.experimento_id]
        registros_actuales.append(asdict(registro))

        with open(self.ruta_bitacora, "w", encoding="utf-8") as f:
            json.dump(registros_actuales, f, indent=4, ensure_ascii=False)

    def cargar_bitacora(self) -> List[Dict[str, Any]]:
        """
        Carga todos los registros almacenados en la bitácora.

        :rtype: list
        """
        if not os.path.exists(self.ruta_bitacora):
            return []
        try:
            with open(self.ruta_bitacora, "r", encoding="utf-8") as f:
                contenido = f.read().strip()
                if not contenido:
                    return []
                return json.loads(contenido)
        except Exception:
            return []

    def buscar_por_id(self, experimento_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca un experimento por su identificador único.

        :param experimento_id: Identificador del experimento.
        :type experimento_id: str
        :rtype: dict or None
        """
        registros = self.cargar_bitacora()
        for reg in registros:
            if reg.get("experimento_id") == experimento_id:
                return reg
        return None
