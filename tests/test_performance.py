"""Tests para el módulo de medición de rendimiento (CITO-83)."""

import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.performance import (
    MedicionRendimiento,
    ReporteRendimiento,
    EstadisticasRendimiento,
    MedidorRendimiento,
    medir_pipeline_completo,
    calcular_estadisticas,
    generar_informe_rendimiento,
    exportar_reporte_csv,
    TIEMPO_MANUAL_POR_IMAGEN_SEGUNDOS,
    OBJETIVO_REDUCCION_PORCENTAJE,
    TIEMPO_OBJETIVO_AUTOMATIZADO_SEGUNDOS,
)


class TestConstantes(unittest.TestCase):
    """Tests para las constantes de rendimiento."""

    def test_tiempo_manual_referencia(self):
        """El tiempo manual de referencia debe ser 180 segundos (3 min)."""
        self.assertEqual(TIEMPO_MANUAL_POR_IMAGEN_SEGUNDOS, 180.0)

    def test_objetivo_reduccion(self):
        """El objetivo de reducción debe ser 70%."""
        self.assertEqual(OBJETIVO_REDUCCION_PORCENTAJE, 70.0)

    def test_tiempo_objetivo_automatizado(self):
        """El tiempo objetivo automatizado debe ser 30% del manual = 54 segundos."""
        self.assertAlmostEqual(TIEMPO_OBJETIVO_AUTOMATIZADO_SEGUNDOS, 54.0, places=1)


class TestMedicionRendimiento(unittest.TestCase):
    """Tests para la clase MedicionRendimiento."""

    def test_creacion_basica(self):
        """Creación básica de una medición."""
        m = MedicionRendimiento("etapa_test", 1.5)
        self.assertEqual(m.nombre_etapa, "etapa_test")
        self.assertEqual(m.tiempo_segundos, 1.5)
        self.assertIsNone(m.memoria_mb)
        self.assertEqual(m.metadata, {})

    def test_creacion_con_metadata(self):
        """Creación con metadata adicional."""
        m = MedicionRendimiento("etapa_test", 1.5, metadata={"param": "valor"})
        self.assertEqual(m.metadata, {"param": "valor"})


class TestReporteRendimiento(unittest.TestCase):
    """Tests para la clase ReporteRendimiento."""

    def test_reporte_cumple_objetivo(self):
        """Reporte con tiempo menor al objetivo debe cumplir."""
        reporte = ReporteRendimiento(
            imagen_procesada="test.jpg",
            tiempo_total_segundos=30.0,  # Menor a 54s objetivo
            mediciones_etapas=[],
        )
        self.assertTrue(reporte.cumple_objetivo)
        self.assertGreaterEqual(reporte.reduccion_lograda_porcentaje, 70.0)

    def test_reporte_no_cumple_objetivo(self):
        """Reporte con tiempo mayor al objetivo no debe cumplir."""
        reporte = ReporteRendimiento(
            imagen_procesada="test.jpg",
            tiempo_total_segundos=100.0,  # Mayor a 54s objetivo
            mediciones_etapas=[],
        )
        self.assertFalse(reporte.cumple_objetivo)
        self.assertLess(reporte.reduccion_lograda_porcentaje, 70.0)

    def test_reporte_calculo_reduccion(self):
        """Verificar cálculo correcto de reducción."""
        # 90 segundos = 50% de reducción (180 -> 90)
        reporte = ReporteRendimiento(
            imagen_procesada="test.jpg",
            tiempo_total_segundos=90.0,
            mediciones_etapas=[],
        )
        self.assertAlmostEqual(reporte.reduccion_lograda_porcentaje, 50.0, places=1)

    def test_reporte_tiempo_cero(self):
        """Tiempo cero debe dar 100% reducción."""
        reporte = ReporteRendimiento(
            imagen_procesada="test.jpg",
            tiempo_total_segundos=0.0,
            mediciones_etapas=[],
        )
        self.assertEqual(reporte.reduccion_lograda_porcentaje, 100.0)
        self.assertTrue(reporte.cumple_objetivo)


class TestMedidorRendimiento(unittest.TestCase):
    """Tests para la clase MedidorRendimiento."""

    def test_medir_etapa_simple(self):
        """Medir una etapa simple."""
        medidor = MedidorRendimiento()
        medidor.iniciar_etapa("test_etapa")
        time.sleep(0.01)  # Pequeña pausa
        medicion = medidor.finalizar_etapa()

        self.assertEqual(medicion.nombre_etapa, "test_etapa")
        self.assertGreater(medicion.tiempo_segundos, 0.0)
        self.assertLess(medicion.tiempo_segundos, 1.0)

    def test_medir_multiples_etapas(self):
        """Medir múltiples etapas secuenciales."""
        medidor = MedidorRendimiento()

        medidor.iniciar_etapa("etapa1")
        time.sleep(0.01)
        medidor.finalizar_etapa()

        medidor.iniciar_etapa("etapa2")
        time.sleep(0.01)
        medidor.finalizar_etapa()

        self.assertEqual(len(medidor.mediciones), 2)
        self.assertEqual(medidor.mediciones[0].nombre_etapa, "etapa1")
        self.assertEqual(medidor.mediciones[1].nombre_etapa, "etapa2")

    def test_medir_funcion(self):
        """Medir ejecución de una función."""
        medidor = MedidorRendimiento()

        def funcion_lenta(x):
            time.sleep(0.01)
            return x * 2

        resultado = medidor.medir_funcion("doble", funcion_lenta, 5)
        self.assertEqual(resultado, 10)
        self.assertEqual(len(medidor.mediciones), 1)
        self.assertEqual(medidor.mediciones[0].nombre_etapa, "doble")

    def test_medir_funcion_con_excepcion(self):
        """Medir función que lanza excepción debe registrar tiempo."""
        medidor = MedidorRendimiento()

        def funcion_falla():
            time.sleep(0.01)
            raise ValueError("Error de prueba")

        with self.assertRaises(ValueError):
            medidor.medir_funcion("falla", funcion_falla)

        # Debe haber registrado la medición aunque falle
        self.assertEqual(len(medidor.mediciones), 1)

    def test_obtener_reporte(self):
        """Generar reporte a partir de mediciones."""
        medidor = MedidorRendimiento()
        medidor.iniciar_etapa("etapa1")
        time.sleep(0.01)
        medidor.finalizar_etapa({"info": "test"})

        reporte = medidor.obtener_reporte("imagen_test.jpg", {"sigma1": 3.0})

        self.assertEqual(reporte.imagen_procesada, "imagen_test.jpg")
        self.assertEqual(len(reporte.mediciones_etapas), 1)
        self.assertEqual(reporte.parametros, {"sigma1": 3.0})
        self.assertGreater(reporte.tiempo_total_segundos, 0.0)

    def test_reiniciar_medidor(self):
        """Reiniciar medidor debe limpiar mediciones."""
        medidor = MedidorRendimiento()
        medidor.iniciar_etapa("etapa1")
        time.sleep(0.01)
        medidor.finalizar_etapa()

        medidor.reiniciar()
        self.assertEqual(len(medidor.mediciones), 0)

    def test_finalizar_sin_iniciar_error(self):
        """Finalizar sin iniciar debe lanzar error."""
        medidor = MedidorRendimiento()
        with self.assertRaises(RuntimeError):
            medidor.finalizar_etapa()


class TestMedirPipelineCompleto(unittest.TestCase):
    """Tests para medir_pipeline_completo."""

    def test_medir_pipeline_mock(self):
        """Medir pipeline con función mock."""
        def pipeline_mock(img_path):
            time.sleep(0.01)
            return {"total_celulas": 10, "normales": 8, "sospechosas": 2}

        reporte = medir_pipeline_completo(
            Path("test.jpg"),
            pipeline_mock,
            {"sigma1": 3.0, "sigma2": 5.0}
        )

        self.assertEqual(reporte.imagen_procesada, "test.jpg")
        self.assertEqual(reporte.parametros, {"sigma1": 3.0, "sigma2": 5.0})
        self.assertGreater(reporte.tiempo_total_segundos, 0.0)
        self.assertEqual(len(reporte.mediciones_etapas), 1)
        self.assertEqual(reporte.mediciones_etapas[0].nombre_etapa, "pipeline_completo")


class TestCalcularEstadisticas(unittest.TestCase):
    """Tests para calcular_estadisticas."""

    def test_estadisticas_lista_vacia(self):
        """Lista vacía debe retornar ceros."""
        stats = calcular_estadisticas([])
        self.assertEqual(stats.total_ejecuciones, 0)
        self.assertEqual(stats.tiempo_promedio_segundos, 0.0)
        self.assertEqual(stats.porcentaje_cumplen_objetivo, 0.0)

    def test_estadisticas_un_elemento(self):
        """Un solo reporte."""
        reportes = [
            ReporteRendimiento(
                imagen_procesada="test1.jpg",
                tiempo_total_segundos=30.0,
                mediciones_etapas=[],
            )
        ]
        stats = calcular_estadisticas(reportes)
        self.assertEqual(stats.total_ejecuciones, 1)
        self.assertEqual(stats.tiempo_promedio_segundos, 30.0)
        self.assertEqual(stats.tiempo_mediano_segundos, 30.0)
        self.assertEqual(stats.ejecuciones_cumplen_objetivo, 1)
        self.assertEqual(stats.porcentaje_cumplen_objetivo, 100.0)

    def test_estadisticas_multiples(self):
        """Múltiples reportes con variación."""
        reportes = [
            ReporteRendimiento(imagen_procesada="t1.jpg", tiempo_total_segundos=30.0, mediciones_etapas=[]),
            ReporteRendimiento(imagen_procesada="t2.jpg", tiempo_total_segundos=40.0, mediciones_etapas=[]),
            ReporteRendimiento(imagen_procesada="t3.jpg", tiempo_total_segundos=50.0, mediciones_etapas=[]),
            ReporteRendimiento(imagen_procesada="t4.jpg", tiempo_total_segundos=100.0, mediciones_etapas=[]),
        ]
        stats = calcular_estadisticas(reportes)
        self.assertEqual(stats.total_ejecuciones, 4)
        self.assertAlmostEqual(stats.tiempo_promedio_segundos, 55.0, places=1)
        self.assertEqual(stats.tiempo_min_segundos, 30.0)
        self.assertEqual(stats.tiempo_max_segundos, 100.0)
        # 30, 40, 50 cumplen (≤54), 100 no cumple
        self.assertEqual(stats.ejecuciones_cumplen_objetivo, 3)
        self.assertEqual(stats.porcentaje_cumplen_objetivo, 75.0)


class TestGenerarInformeRendimiento(unittest.TestCase):
    """Tests para generar_informe_rendimiento."""

    def test_informe_vacio(self):
        """Informe con lista vacía."""
        informe = generar_informe_rendimiento([])
        self.assertIn("No hay reportes", informe)

    def test_informe_con_datos(self):
        """Informe con datos reales."""
        reportes = [
            ReporteRendimiento(
                imagen_procesada="test1.jpg",
                tiempo_total_segundos=30.0,
                mediciones_etapas=[
                    MedicionRendimiento("preprocesamiento", 5.0),
                    MedicionRendimiento("dog", 10.0),
                    MedicionRendimiento("analisis", 15.0),
                ],
            ),
            ReporteRendimiento(
                imagen_procesada="test2.jpg",
                tiempo_total_segundos=40.0,
                mediciones_etapas=[
                    MedicionRendimiento("preprocesamiento", 6.0),
                    MedicionRendimiento("dog", 12.0),
                    MedicionRendimiento("analisis", 22.0),
                ],
            ),
        ]

        informe = generar_informe_rendimiento(reportes)

        self.assertIn("INFORME DE RENDIMIENTO", informe)
        self.assertIn("CITO-83", informe)
        self.assertIn("test1.jpg", informe)
        self.assertIn("test2.jpg", informe)
        self.assertIn("preprocesamiento", informe)
        self.assertIn("dog", informe)
        self.assertIn("analisis", informe)
        self.assertIn("CUMPL", informe)  # CUMPLE o NO CUMPLE

    def test_informe_guardado_en_archivo(self):
        """Informe debe guardarse en archivo si se especifica ruta."""
        import tempfile

        reportes = [
            ReporteRendimiento(imagen_procesada="test.jpg", tiempo_total_segundos=30.0, mediciones_etapas=[])
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            ruta = Path(f.name)

        try:
            generar_informe_rendimiento(reportes, ruta)
            contenido = ruta.read_text(encoding="utf-8")
            self.assertIn("INFORME DE RENDIMIENTO", contenido)
        finally:
            ruta.unlink(missing_ok=True)


class TestExportarReporteCSV(unittest.TestCase):
    """Tests para exportar_reporte_csv."""

    def test_exportar_csv_basico(self):
        """Exportar CSV básico."""
        import tempfile

        reportes = [
            ReporteRendimiento(
                imagen_procesada="test1.jpg",
                tiempo_total_segundos=30.0,
                mediciones_etapas=[
                    MedicionRendimiento("etapa1", 10.0),
                    MedicionRendimiento("etapa2", 20.0),
                ],
                timestamp="2024-01-01 12:00:00",
                version_codigo="1.0",
            ),
            ReporteRendimiento(
                imagen_procesada="test2.jpg",
                tiempo_total_segundos=40.0,
                mediciones_etapas=[
                    MedicionRendimiento("etapa1", 15.0),
                    MedicionRendimiento("etapa2", 25.0),
                ],
                timestamp="2024-01-01 12:01:00",
                version_codigo="1.0",
            ),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            ruta = Path(f.name)

        try:
            exportar_reporte_csv(reportes, ruta)

            # Verificar contenido
            import csv
            with ruta.open("r", encoding="utf-8") as f:
                reader = csv.reader(f)
                filas = list(reader)

            self.assertEqual(len(filas), 3)  # Header + 2 datos
            self.assertIn("timestamp", filas[0])
            self.assertIn("imagen", filas[0])
            self.assertIn("tiempo_total_segundos", filas[0])
            self.assertIn("etapa_etapa1_segundos", filas[0])
            self.assertIn("etapa_etapa2_segundos", filas[0])
            self.assertEqual(filas[1][1], "test1.jpg")
            self.assertEqual(filas[2][1], "test2.jpg")
        finally:
            ruta.unlink(missing_ok=True)


class TestIntegracionRendimiento(unittest.TestCase):
    """Tests de integración para medición de rendimiento."""

    def test_benchmark_simulado(self):
        """Simular benchmark completo."""
        # Simular 5 imágenes con tiempos variables
        reportes = []
        for i in range(5):
            tiempo = 30.0 + i * 5.0  # 30, 35, 40, 45, 50
            reporte = ReporteRendimiento(
                imagen_procesada=f"img_{i}.jpg",
                tiempo_total_segundos=tiempo,
                mediciones_etapas=[
                    MedicionRendimiento("preprocesamiento", tiempo * 0.2),
                    MedicionRendimiento("dog", tiempo * 0.5),
                    MedicionRendimiento("analisis", tiempo * 0.3),
                ],
            )
            reportes.append(reporte)

        stats = calcular_estadisticas(reportes)

        # Todos deben cumplir objetivo (≤54s)
        self.assertEqual(stats.ejecuciones_cumplen_objetivo, 5)
        self.assertEqual(stats.porcentaje_cumplen_objetivo, 100.0)
        self.assertAlmostEqual(stats.tiempo_promedio_segundos, 40.0, places=1)

    def test_benchmark_parcial_cumple(self):
        """Benchmark donde solo algunos cumplen."""
        reportes = []
        tiempos = [30.0, 40.0, 50.0, 60.0, 100.0]  # 3 cumplen, 2 no
        for i, t in enumerate(tiempos):
            reporte = ReporteRendimiento(
                imagen_procesada=f"img_{i}.jpg",
                tiempo_total_segundos=t,
                mediciones_etapas=[],
            )
            reportes.append(reporte)

        stats = calcular_estadisticas(reportes)
        self.assertEqual(stats.ejecuciones_cumplen_objetivo, 3)
        self.assertEqual(stats.porcentaje_cumplen_objetivo, 60.0)


if __name__ == "__main__":
    unittest.main()