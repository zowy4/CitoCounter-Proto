"""
evidencia_panel.py - Panel de Evidencias Académicas y Actividades del Proyecto (CitoCounter-Proto).
Muestra el mapeo detallado de actividades, archivos, métodos, líneas de evidencia y reportes reproducibles.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QTextEdit,
    QSplitter,
)


ACTIVIDADES_PROYECTO = [
    {
        "id": "CITO-22 / CITO-74 / CITO-97",
        "materia": "Inteligencia Artificial",
        "actividad": "Calibración del algoritmo DoG para detectar núcleos celulares en imágenes de citología cervical",
        "tiempo": "2 a 3 semanas",
        "evidencias": "Bitácora de prueba, comparativas de imágenes, tablas de parámetros, reportes de rendimiento",
        "unidad": "Unidad 1: Intro a IA; Unidad 3: Reglas y búsqueda; Unidad 4: Aplicaciones con IA",
        "archivos": "[src/dog_filter.py](/c:/Users/zowya/CitoCounter_Proto/src/dog_filter.py), [calibrar_dog.py](/c:/Users/zowya/CitoCounter_Proto/calibrar_dog.py), [calibrar_cito97.py](/c:/Users/zowya/CitoCounter_Proto/calibrar_cito97.py)",
        "metodos": "`diferencia_de_gaussianas()`, `calibrar_parametros_dog()`, `aplicar_filtro_dog()`",
        "descripcion": "Ajuste matemático de los radios sigma 1 y sigma 2 (DoG) para maximizar la detección de núcleos celulares individuales en imágenes de citología de campo claro (Papanicolaou) y sintéticas, reduciendo falsos positivos por detritos y artefactos."
    },
    {
        "id": "CITO-23 / CITO-95 / CITO-96",
        "materia": "Inteligencia Artificial",
        "actividad": "Evaluación del sistema con métricas de precisión, sensibilidad, F1-Score e IoU",
        "tiempo": "1 a 2 semanas",
        "evidencias": "Gráficas de métricas, análisis comparativo, documento de validación",
        "unidad": "Unidad 2: Representación del conocimiento; Unidad 4: Aplicaciones con IA",
        "archivos": "[src/herlev_evaluation.py](/c:/Users/zowya/CitoCounter_Proto/src/herlev_evaluation.py), [evaluar_cito23.py](/c:/Users/zowya/CitoCounter_Proto/evaluar_cito23.py)",
        "metodos": "`evaluar_detecciones()`, `calcular_metricas_globales()`, `emparejamiento_por_centroides()`",
        "descripcion": "Comparación espacial de las detecciones del algoritmo frente al ground truth mediante emparejamiento por centroides y cálculo estricto de TP, FP, FN, Precision, Recall, F1-Score y Jaccard (IoU)."
    },
    {
        "id": "CITO-77 / CITO-159",
        "materia": "Inteligencia Artificial",
        "actividad": "Definición de un sistema basado en reglas para explicar la clasificación de una célula como normal o sospechosa",
        "tiempo": "1 a 2 semanas",
        "evidencias": "Documento de reglas, casos de prueba, explicación de decisiones del sistema",
        "unidad": "Unidad 2: Representación del conocimiento; Unidad 3: Reglas y búsqueda",
        "archivos": "[src/analysis.py](/c:/Users/zowya/CitoCounter_Proto/src/analysis.py), [docs/CITO-77-reglas-explicables.md](/c:/Users/zowya/CitoCounter_Proto/docs/CITO-77-reglas-explicables.md)",
        "metodos": "`clasificar_nucleo_por_area()`, `obtener_reglas_clasificacion()`",
        "descripcion": "Aplicación de la regla heurística de la Dra. Rangel (>3x el área promedio normal se clasifica como sospechosa), con validación de circularidad, solidez y filtrado de ruido."
    },
    {
        "id": "CITO-25 / CITO-158",
        "materia": "Tópicos Selectos de Tecnologías Web y Móvil",
        "actividad": "Desarrollo de una API REST para procesar imágenes y devolver análisis",
        "tiempo": "1 a 2 semanas",
        "evidencias": "Documentación de endpoints, pruebas de API, capturas del flujo de uso",
        "unidad": "Unidad 2: Arquitecturas orientadas a servicios; Unidad 4: Tecnologías híbridas",
        "archivos": "[api_v1.py](/c:/Users/zowya/CitoCounter_Proto/api_v1.py)",
        "metodos": "`@app.post('/api/v1/analyze')`, `analizar_imagen_endpoint()`",
        "descripcion": "Exposición de servicios backend mediante FastAPI para recibir imágenes en base64 o archivo, procesarlas con el pipeline DoG o DL, y retornar JSON estructurado con conteos y clasificaciones."
    },
    {
        "id": "CITO-65 / CITO-161",
        "materia": "Tópicos Selectos de Tecnologías Web y Móvil",
        "actividad": "Implementación de una interfaz web o móvil para visualizar resultados del conteo y clasificación",
        "tiempo": "2 semanas",
        "evidencias": "Capturas de pantalla, prototipo funcional, manual de uso",
        "unidad": "Unidad 3: Entornos de desarrollo móviles; Unidad 4: Tecnologías híbridas",
        "archivos": "[app.py](/c:/Users/zowya/CitoCounter_Proto/app.py) (Streamlit), [qt_app/presentation/main_window.py](/c:/Users/zowya/CitoCounter_Proto/qt_app/presentation/main_window.py) (Qt Desktop)",
        "metodos": "`MainWindow`, `VisorImagen`, `PanelAjustes`, `Streamlit UI`",
        "descripcion": "Construcción de interfaces de usuario interactivas tanto web (Streamlit) como de escritorio (PySide6 / Qt), permitiendo control de parámetros en tiempo real, visor con overlays y reproducción de video en vivo."
    },
    {
        "id": "CITO-66 / CITO-164",
        "materia": "Tópicos Selectos de Tecnologías Web y Móvil",
        "actividad": "Integración del sistema con un dashboard para mostrar resultados y métricas",
        "tiempo": "1 a 2 semanas",
        "evidencias": "Dashboard funcional, reportes, pantallas de visualización",
        "unidad": "Unidad 1: Patrones de diseño; Unidad 4: Desarrollo híbrido",
        "archivos": "[src/interfaz_resultados.py](/c:/Users/zowya/CitoCounter_Proto/src/interfaz_resultados.py), [qt_app/presentation/dashboard_widget.py](/c:/Users/zowya/CitoCounter_Proto/qt_app/presentation/dashboard_widget.py)",
        "metodos": "`DashboardWidget`, `generar_dashboard()`",
        "descripcion": "Panel visual con tarjetas KPI y tablas dinámicas que resumen el historial de ejecuciones, promedio de células detectadas, normales, sospechosas y porcentaje de riesgo."
    },
    {
        "id": "CITO-85 / KPIs",
        "materia": "Tecnologías para Sistemas de Inteligencia de Negocios",
        "actividad": "Diseño de indicadores clave para medición del rendimiento del sistema (células detectadas, sospechosas, porcentaje de riesgo, comparación por muestra)",
        "tiempo": "1 a 2 semanas",
        "evidencias": "Dashboard de indicadores, tablas de resultados, documento de métricas",
        "unidad": "Unidad 2: Organización y modelado de datos; Unidad 5: Visualización de datos",
        "archivos": "[src/metricas_sistema.py](/c:/Users/zowya/CitoCounter_Proto/src/metricas_sistema.py)",
        "metodos": "`metricas_conjunto()`, `calcular_porcentaje_riesgo()`",
        "descripcion": "Definición y cálculo algorítmico de KPIs analíticos para evaluar la carga patológica y la distribución de células sospechosas por lote o paciente."
    },
    {
        "id": "CITO-29 / CITO-ETL",
        "materia": "Tecnologías para Sistemas de Inteligencia de Negocios",
        "actividad": "Construcción de un flujo ETL para procesar resultados y generar reportes históricos",
        "tiempo": "1 a 2 semanas",
        "evidencias": "Diagrama ETL, archivos transformados, reportes generados",
        "unidad": "Unidad 3: ETL; Unidad 4: Data warehouse",
        "archivos": "[src/etl_resultados.py](/c:/Users/zowya/CitoCounter_Proto/src/etl_resultados.py)",
        "metodos": "`extraer_resultados()`, `transformar_datos()`, `cargar_reporte()`",
        "descripcion": "Proceso de Extracción, Transformación y Carga (ETL) que consolida los resultados experimentales en formatos estructurados (CSV/JSON) para la generación de reportes gerenciales."
    },
    {
        "id": "CITO-30 / CITO-DB",
        "materia": "Tecnologías para Sistemas de Inteligencia de Negocios",
        "actividad": "Implementación de un data warehouse o estructura de almacenamiento para resultados de experimentación",
        "tiempo": "2 semanas",
        "evidencias": "Esquema de base de datos, tablas de resultados, documentación técnica",
        "unidad": "Unidad 4: El Data warehouse",
        "archivos": "[src/almacenamiento.py](/c:/Users/zowya/CitoCounter_Proto/src/almacenamiento.py)",
        "metodos": "`guardar_experimento()`, `obtener_experimento()`, esquemas SQLite",
        "descripcion": "Persistencia estructurada en base de datos SQLite con tablas normalizadas para almacenar metadatos de corridas, hiperparámetros (sigmas, polaridad) y contadores celulares."
    }
]


class EvidenciaPanel(QWidget):
    """Panel interactivo de Evidencias Académicas que detalla las 9 actividades del proyecto."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QLabel("Panel de Trazabilidad y Evidencias Académicas (CitoCounter-Proto)")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        layout.addWidget(header)

        sub = QLabel("Seleccione una actividad para inspeccionar sus archivos fuente, métodos, unidades de estudio y evidencias reproducibles.")
        sub.setStyleSheet("color: #64748B; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(sub)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Tabla izquierda con actividades
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID / Ref", "Materia", "Actividad del Proyecto"])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.itemSelectionChanged.connect(self._mostrar_detalle)
        splitter.addWidget(self.tabla)

        # Panel derecho con detalles e inspección
        self.detalle_text = QTextEdit()
        self.detalle_text.setReadOnly(True)
        self.detalle_text.setStyleSheet(
            "background-color: #F8FAFC; color: #1E293B; font-size: 13px; padding: 12px; border: 1px solid #CBD5E1; border-radius: 6px;"
        )
        splitter.addWidget(self.detalle_text)

        splitter.setSizes([450, 550])

        self._poblar_tabla()

    def _poblar_tabla(self) -> None:
        self.tabla.setRowCount(len(ACTIVIDADES_PROYECTO))
        for row_idx, act in enumerate(ACTIVIDADES_PROYECTO):
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(act["id"]))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(act["materia"]))
            self.tabla.setItem(row_idx, 2, QTableWidgetItem(act["actividad"]))

        if ACTIVIDADES_PROYECTO:
            self.tabla.selectRow(0)

    def _mostrar_detalle(self) -> None:
        selected_rows = self.tabla.selectedRowList() if hasattr(self.tabla, "selectedRowList") else []
        indexes = self.tabla.selectedIndexes()
        if not indexes:
            return
        row = indexes[0].row()
        if row < 0 or row >= len(ACTIVIDADES_PROYECTO):
            return

        act = ACTIVIDADES_PROYECTO[row]

        html = f"""
        <h2 style="color: #2A55E5; margin-top: 0;">{act['actividad']}</h2>
        <p><b>Referencia / ID Jira:</b> <span style="background-color: #E2E8F0; padding: 2px 6px; border-radius: 4px;">{act['id']}</span></p>
        <p><b>Materia / Asignatura:</b> {act['materia']}</p>
        <p><b>Tiempo de Realización:</b> {act['tiempo']}</p>
        <p><b>Unidad / Temas Relacionados:</b> {act['unidad']}</p>
        <hr style="border: 0; border-top: 1px solid #CBD5E1; margin: 12px 0;">
        <h3 style="color: #1E293B;">Archivos Fuente de Evidencia</h3>
        <p>{act['archivos']}</p>
        <h3 style="color: #1E293B;">Métodos y Funciones Clave</h3>
        <p>{act['metodos']}</p>
        <h3 style="color: #1E293B;">Evidencias de la Actividad</h3>
        <p style="background-color: #FEF3C7; padding: 8px; border-radius: 4px; border: 1px solid #FCD34D;"><b>📦 {act['evidencias']}</b></p>
        <h3 style="color: #1E293B;">Descripción Técnica</h3>
        <p>{act['descripcion']}</p>
        """
        self.detalle_text.setHtml(html)

