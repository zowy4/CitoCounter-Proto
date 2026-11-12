"""
evidencia_panel.py - Panel interactivo de Evidencias Académicas y Trazabilidad de Actividades (CitoCounter-Proto).
Permite explorar bitácoras, tablas formateadas (CSV/JSON/Markdown), documentos limpios y código fuente.
"""

import csv
import json
import html
import pathlib
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

ACTIVIDADES_CON_EVIDENCIAS = [
    {
        "id": "CITO-22 / CITO-97",
        "materia": "Inteligencia Artificial",
        "actividad": "Calibración del algoritmo DoG para detectar núcleos celulares",
        "tiempo": "2 a 3 semanas",
        "unidades": "Unidad 1: Intro a IA; Unidad 3: Reglas; Unidad 4: Aplicaciones",
        "archivos_fuente": ["src/dog_filter.py", "calibrar_dog.py", "calibrar_cito97.py"],
        "evidencias_archivos": [
            ("Bitácora de Calibración CITO-97 (.txt)", "data/results/CITO-97-calibracion-separada.txt"),
            ("Tabla de Parámetros Óptimos (.json)", "data/results/CITO-97-calibracion-separada.json"),
            ("Documento de Evidencia DoG (.md)", "docs/evidencia-cito97-calibracion-dog.md"),
            ("Barrido de Calibración CITO-22 (.md)", "docs/evidencia-cito22-barrido-calibracion.md")
        ],
        "metodos": "`diferencia_de_gaussianas()`, `calibrar_parametros_dog()`",
        "descripcion": "Ajuste matemático de los radios sigma 1 y sigma 2 (DoG) para maximizar la detección de núcleos celulares individuales en citología."
    },
    {
        "id": "CITO-23 / CITO-95",
        "materia": "Inteligencia Artificial",
        "actividad": "Evaluación del sistema con métricas de precisión, sensibilidad, F1-Score e IoU",
        "tiempo": "1 a 2 semanas",
        "unidades": "Unidad 2: Validación; Unidad 4: Aplicaciones con IA",
        "archivos_fuente": ["src/herlev_evaluation.py", "evaluar_cito23.py"],
        "evidencias_archivos": [
            ("CSV Evaluación Cellpose Zero-Shot (.csv)", "data/results/CITO-95-cellpose-zeroshot.csv"),
            ("Resumen de Validación Sintética (.json)", "data/results/CITO-23-validacion-sintetica.json"),
            ("Bitácora de Validación Sintética (.txt)", "data/results/CITO-23-validacion-sintetica.txt"),
            ("Evidencia Validación Congelada (.md)", "docs/evidencia-cito95-validacion-congelada.md")
        ],
        "metodos": "`evaluar_detecciones()`, `calcular_metricas_globales()`",
        "descripcion": "Comparación espacial mediante emparejamiento por centroides y cálculo estricto de TP, FP, FN, Precision, Recall, F1-Score y Jaccard."
    },
    {
        "id": "CITO-77 / CITO-159",
        "materia": "Inteligencia Artificial",
        "actividad": "Definición de un sistema basado en reglas para explicar la clasificación (normal / sospechosa)",
        "tiempo": "1 a 2 semanas",
        "unidades": "Unidad 2: Representación del conocimiento; Unidad 3: Reglas y búsqueda",
        "archivos_fuente": ["src/analysis.py", "docs/CITO-77-reglas-explicables.md"],
        "evidencias_archivos": [
            ("Documento de Reglas Explicables (.md)", "docs/CITO-77-reglas-explicables.md"),
            ("Resumen de Métricas de Reglas (.txt)", "data/results/CITO-23-metricas-resumen.txt")
        ],
        "metodos": "`clasificar_nucleo_por_area()`, `obtener_reglas_clasificacion()`",
        "descripcion": "Aplicación de la regla heurística de la Dra. Rangel (>3x el área promedio normal se clasifica como sospechosa)."
    },
    {
        "id": "CITO-25 / CITO-158",
        "materia": "Tópicos Selectos de Tecnologías Web y Móvil",
        "actividad": "Desarrollo de una API REST para procesar imágenes y devolver análisis",
        "tiempo": "1 a 2 semanas",
        "unidades": "Unidad 2: Arquitecturas orientadas a servicios; Unidad 4: Tecnologías híbridas",
        "archivos_fuente": ["api_v1.py", "qt_app/presentation/main_window.py", "qt_app/presentation/panel_ajustes.py"],
        "evidencias_archivos": [
            ("Evidencia API REST Backend (.md)", "docs/evidencia-cito25-api-rest.md"),
            ("Código Fuente API (.py)", "api_v1.py"),
            ("Código Ventana Qt Desktop (.py)", "qt_app/presentation/main_window.py"),
            ("Código Panel de Ajustes Qt (.py)", "qt_app/presentation/panel_ajustes.py")
        ],
        "metodos": "`@app.post('/api/v1/analyze')`, `analizar_imagen_endpoint()`, `MainWindow`, `PanelAjustes`",
        "descripcion": "Exposición de servicios backend mediante FastAPI para recibir imágenes y retornar análisis estructurado, integrado con la versión Qt Desktop."
    },
    {
        "id": "CITO-65 / CITO-161",
        "materia": "Tópicos Selectos de Tecnologías Web y Móvil",
        "actividad": "Implementación de una interfaz web o móvil para visualizar resultados del conteo y clasificación",
        "tiempo": "2 semanas",
        "unidades": "Unidad 3: Entornos móviles; Unidad 4: Tecnologías híbridas",
        "archivos_fuente": ["app.py", "qt_app/presentation/main_window.py"],
        "evidencias_archivos": [
            ("Guía de Usuario de la Aplicación (.md)", "docs/guia_usuario.md"),
            ("Código Aplicación Streamlit (.py)", "app.py"),
            ("Código Ventana Qt Desktop (.py)", "qt_app/presentation/main_window.py")
        ],
        "metodos": "`MainWindow`, `VisorImagen`, `PanelAjustes`, `Streamlit UI`",
        "descripcion": "Construcción de interfaces interactivas web (Streamlit) y de escritorio (Qt Desktop) para visualización en tiempo real."
    },
    {
        "id": "CITO-66 / CITO-164",
        "materia": "Tópicos Selectos de Tecnologías Web y Móvil",
        "actividad": "Integración del sistema con un dashboard para mostrar resultados y métricas",
        "tiempo": "1 a 2 semanas",
        "unidades": "Unidad 1: Patrones de diseño; Unidad 4: Desarrollo híbrido",
        "archivos_fuente": ["src/interfaz_resultados.py", "qt_app/presentation/dashboard_widget.py"],
        "evidencias_archivos": [
            ("Código Dashboard Qt (.py)", "qt_app/presentation/dashboard_widget.py"),
            ("Módulo Interfaz de Resultados (.py)", "src/interfaz_resultados.py")
        ],
        "metodos": "`DashboardWidget`, `generar_dashboard()`",
        "descripcion": "Panel visual con tarjetas KPI y tablas dinámicas que resumen el historial de ejecuciones y métricas."
    },
    {
        "id": "CITO-85 / CITO-86",
        "materia": "Tecnologías para Sistemas de Inteligencia de Negocios",
        "actividad": "Diseño de indicadores clave para medición del rendimiento del sistema",
        "tiempo": "1 a 2 semanas",
        "unidades": "Unidad 2: Modelado de datos; Unidad 5: Visualización de datos",
        "archivos_fuente": ["src/metricas_sistema.py"],
        "evidencias_archivos": [
            ("Reporte Validación Formal CITO-85 (.txt)", "data/results/CITO-85-validacion-formal.txt"),
            ("JSON Métricas Validación Formal (.json)", "data/results/CITO-85-validacion-formal.json")
        ],
        "metodos": "`metricas_conjunto()`, `calcular_porcentaje_riesgo()`",
        "descripcion": "Definición y cálculo algorítmico de KPIs analíticos para evaluar la carga patológica y porcentaje de riesgo."
    },
    {
        "id": "CITO-29 / CITO-ETL",
        "materia": "Tecnologías para Sistemas de Inteligencia de Negocios",
        "actividad": "Construcción de un flujo ETL para procesar resultados y generar reportes históricos",
        "tiempo": "1 a 2 semanas",
        "unidades": "Unidad 3: ETL; Unidad 4: Data warehouse",
        "archivos_fuente": ["src/etl_resultados.py"],
        "evidencias_archivos": [
            ("Preparación de Validación CITO-23 (.md)", "data/results/CITO-23-preparacion-validacion.md"),
            ("Código Módulo ETL (.py)", "src/etl_resultados.py")
        ],
        "metodos": "`extraer_resultados()`, `transformar_datos()`, `cargar_reporte()`",
        "descripcion": "Proceso ETL que consolida resultados experimentales en formatos estructurados para reportes históricos."
    },
    {
        "id": "CITO-30 / CITO-DB",
        "materia": "Tecnologías para Sistemas de Inteligencia de Negocios",
        "actividad": "Implementación de un data warehouse o estructura de almacenamiento para resultados",
        "tiempo": "2 semanas",
        "unidades": "Unidad 4: El Data warehouse",
        "archivos_fuente": ["src/almacenamiento.py"],
        "evidencias_archivos": [
            ("Bitácora Sanitizada CSV (.csv)", "data/results/CITO-95-bitacora-sanitizada.csv"),
            ("Código Módulo Almacenamiento DB (.py)", "src/almacenamiento.py")
        ],
        "metodos": "`guardar_experimento()`, `obtener_experimento()`",
        "descripcion": "Persistencia estructurada en base de datos SQLite con tablas normalizadas para almacenar metadatos e hiperparámetros."
    }
]


class EvidenciaPanel(QWidget):
    """Panel interactivo de Evidencias Académicas que permite consultar bitácoras, tablas (CSV/JSON/Markdown) y código."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Izquierda: Lista de actividades
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)
        
        lbl_act = QLabel("Actividades del Proyecto:")
        lbl_act.setStyleSheet("font-weight: bold; color: #1E293B; font-size: 11px;")
        left_layout.addWidget(lbl_act)

        self.tabla_actividades = QTableWidget()
        self.tabla_actividades.setColumnCount(3)
        self.tabla_actividades.setHorizontalHeaderLabels(["Materia", "ID", "Nombre de Actividad"])
        self.tabla_actividades.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_actividades.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_actividades.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla_actividades.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_actividades.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_actividades.itemSelectionChanged.connect(self._seleccionar_actividad)
        left_layout.addWidget(self.tabla_actividades)
        splitter.addWidget(left_widget)

        # Centro: Lista de archivos de evidencia específicos
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(2)

        lbl_evi = QLabel("Evidencias Específicas:")
        lbl_evi.setStyleSheet("font-weight: bold; color: #1E293B; font-size: 11px;")
        middle_layout.addWidget(lbl_evi)

        self.lista_evidencias = QListWidget()
        self.lista_evidencias.itemClicked.connect(self._cargar_contenido_evidencia)
        middle_layout.addWidget(self.lista_evidencias)
        splitter.addWidget(middle_widget)

        # Derecha: Visor enriquecido con tablas HTML nativas
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(2)

        lbl_con = QLabel("Visor de Evidencia Formateado:")
        lbl_con.setStyleSheet("font-weight: bold; color: #1E293B; font-size: 11px;")
        right_layout.addWidget(lbl_con)

        self.visor_contenido = QTextEdit()
        self.visor_contenido.setReadOnly(True)
        self.visor_contenido.setStyleSheet(
            "background-color: #F8FAFC; color: #1E293B; font-family: sans-serif; font-size: 13px; padding: 10px; border: 1px solid #CBD5E1; border-radius: 4px;"
        )
        right_layout.addWidget(self.visor_contenido)
        splitter.addWidget(right_widget)

        splitter.setSizes([450, 240, 500])

        self._poblar_tabla_actividades()

    def _poblar_tabla_actividades(self) -> None:
        self.tabla_actividades.setRowCount(len(ACTIVIDADES_CON_EVIDENCIAS))
        for row_idx, act in enumerate(ACTIVIDADES_CON_EVIDENCIAS):
            self.tabla_actividades.setItem(row_idx, 0, QTableWidgetItem(act["materia"]))
            self.tabla_actividades.setItem(row_idx, 1, QTableWidgetItem(act["id"]))
            self.tabla_actividades.setItem(row_idx, 2, QTableWidgetItem(act["actividad"]))

        if ACTIVIDADES_CON_EVIDENCIAS:
            self.tabla_actividades.selectRow(0)

    def _seleccionar_actividad(self) -> None:
        indexes = self.tabla_actividades.selectedIndexes()
        if not indexes:
            return
        row = indexes[0].row()
        if row < 0 or row >= len(ACTIVIDADES_CON_EVIDENCIAS):
            return

        act = ACTIVIDADES_CON_EVIDENCIAS[row]
        self.lista_evidencias.clear()

        for nombre_evidencia, ruta_relativa in act["evidencias_archivos"]:
            item = QListWidgetItem(nombre_evidencia)
            item.setData(Qt.UserRole, ruta_relativa)
            self.lista_evidencias.addItem(item)

        resumen_html = f"""
        <div style="font-family: sans-serif; color: #1E293B; padding: 15px;">
            <h2 style="color: #0F172A; border-bottom: 2px solid #3B82F6; padding-bottom: 8px; margin-top: 0;">{html.escape(act['actividad'])}</h2>
            <p><b>Materia:</b> {html.escape(act['materia'])}</p>
            <p><b>ID / Referencia:</b> {html.escape(act['id'])}</p>
            <p><b>Tiempo de Realización:</b> {html.escape(act['tiempo'])}</p>
            <p><b>Unidades Relacionadas:</b> {html.escape(act['unidades'])}</p>
            
            <h3 style="color: #1E293B; margin-top: 15px;">Archivos Fuente:</h3>
            <ul>{"".join([f"<li><code>{html.escape(f)}</code></li>" for f in act['archivos_fuente']])}</ul>
            
            <h3 style="color: #1E293B; margin-top: 15px;">Métodos Principales:</h3>
            <p><code>{html.escape(act['metodos'])}</code></p>
            
            <h3 style="color: #1E293B; margin-top: 15px;">Descripción:</h3>
            <p style="background: #EFF6FF; padding: 10px; border-left: 4px solid #3B82F6; border-radius: 4px;">{html.escape(act['descripcion'])}</p>
            
            <hr style="border: none; border-top: 1px solid #CBD5E1; margin: 20px 0;">
            <p style="color: #64748B; font-style: italic;">👉 Seleccione un archivo de evidencia en la columna central para visualizar su formato tabular estructurado.</p>
        </div>
        """
        self.visor_contenido.setHtml(resumen_html)
        if self.lista_evidencias.count() > 0:
            self.lista_evidencias.setCurrentRow(0)

    def _cargar_contenido_evidencia(self, item: QListWidgetItem) -> None:
        ruta_relativa = item.data(Qt.UserRole)
        if not ruta_relativa:
            return

        ruta_archivo = pathlib.Path(ruta_relativa)
        if not ruta_archivo.is_absolute():
            ruta_archivo = pathlib.Path(__file__).resolve().parent.parent.parent / ruta_relativa

        if not ruta_archivo.exists():
            self.visor_contenido.setHtml(f"<p style='color: red; font-family: sans-serif;'>El archivo de evidencia no se encontró: {html.escape(str(ruta_archivo))}</p>")
            return

        try:
            contenido_bruto = ruta_archivo.read_text(encoding="utf-8", errors="ignore")
            ext = ruta_archivo.suffix.lower()

            if ext == ".csv":
                html_contenido = self._renderizar_csv(contenido_bruto, ruta_relativa)
                self.visor_contenido.setHtml(html_contenido)
            elif ext == ".json":
                html_contenido = self._renderizar_json(contenido_bruto, ruta_relativa)
                self.visor_contenido.setHtml(html_contenido)
            elif ext in [".md", ".txt"]:
                html_contenido = self._renderizar_markdown_o_txt(contenido_bruto, ruta_relativa, ext)
                self.visor_contenido.setHtml(html_contenido)
            elif ext == ".py":
                codigo_html = f"""
                <div style="font-family: sans-serif; padding: 10px;">
                    <h3 style="color: #0F172A; border-bottom: 1px solid #CBD5E1; padding-bottom: 5px;">📄 Código Fuente: {html.escape(ruta_relativa)}</h3>
                    <pre style="background-color: #0F172A; color: #F8FAFC; padding: 15px; border-radius: 6px; font-family: Consolas, monospace; font-size: 12px; overflow-x: auto;">{html.escape(contenido_bruto)}</pre>
                </div>
                """
                self.visor_contenido.setHtml(codigo_html)
            else:
                self.visor_contenido.setPlainText(contenido_bruto)
        except Exception as e:
            self.visor_contenido.setHtml(f"<p style='color: red; font-family: sans-serif;'>Error al renderizar el archivo {html.escape(ruta_relativa)}: {html.escape(str(e))}</p>")

    def _renderizar_csv(self, texto: str, titulo: str) -> str:
        lines = [l for l in texto.splitlines() if l.strip()]
        if not lines:
            return "<p>Archivo CSV vacío.</p>"
        
        reader = list(csv.reader(lines))
        html_out = [
            f"<div style='font-family: sans-serif; padding: 10px;'>",
            f"<h3 style='color: #0F172A; border-bottom: 2px solid #3B82F6; padding-bottom: 5px;'>📊 Tabla de Datos: {html.escape(titulo)}</h3>",
            f"<div style='overflow-x: auto; margin-top: 10px;'>",
            f"<table style='border-collapse: collapse; width: 100%; font-size: 12px; background: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>"
        ]
        
        for i, row in enumerate(reader):
            bg = "#1E293B" if i == 0 else ("#FFFFFF" if i % 2 == 0 else "#F8FAFC")
            color = "#FFFFFF" if i == 0 else "#1E293B"
            tag = "th" if i == 0 else "td"
            html_out.append(f"<tr style='background-color: {bg}; color: {color};'>")
            for cell in row:
                html_out.append(f"<{tag} style='border: 1px solid #CBD5E1; padding: 8px 10px; text-align: left;'>{html.escape(cell)}</{tag}>")
            html_out.append("</tr>")
            
        html_out.append("</table></div></div>")
        return "".join(html_out)

    def _renderizar_json(self, texto: str, titulo: str) -> str:
        try:
            data = json.loads(texto)
            pretty = json.dumps(data, indent=2, ensure_ascii=False)
            
            tabla_html = ""
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                keys = list(data[0].keys())
                parts = [
                    f"<h4 style='color: #334155; margin-top: 20px;'>Vista Tabular:</h4>",
                    f"<div style='overflow-x: auto;'><table style='border-collapse: collapse; width: 100%; font-size: 12px; background: #FFFFFF;'>"
                ]
                parts.append("<tr style='background-color: #1E293B; color: #FFFFFF;'>")
                for k in keys:
                    parts.append(f"<th style='border: 1px solid #CBD5E1; padding: 6px;'>{html.escape(str(k))}</th>")
                parts.append("</tr>")
                for row_idx, item in enumerate(data):
                    bg = "#FFFFFF" if row_idx % 2 == 0 else "#F8FAFC"
                    parts.append(f"<tr style='background-color: {bg}; color: #1E293B;'>")
                    for k in keys:
                        val = item.get(k, "")
                        parts.append(f"<td style='border: 1px solid #CBD5E1; padding: 6px;'>{html.escape(str(val))}</td>")
                    parts.append("</tr>")
                parts.append("</table></div>")
                tabla_html = "".join(parts)
            elif isinstance(data, dict):
                parts = []
                if "metadata" in data and isinstance(data["metadata"], dict):
                    parts.append("<h4 style='color: #334155; margin-top: 15px;'>Parámetros y Metadatos:</h4>")
                    parts.append("<div style='overflow-x: auto;'><table style='border-collapse: collapse; width: 100%; font-size: 12px; background: #FFFFFF;'>")
                    parts.append("<tr style='background-color: #1E293B; color: #FFFFFF;'><th style='border: 1px solid #CBD5E1; padding: 6px;'>Parámetro</th><th style='border: 1px solid #CBD5E1; padding: 6px;'>Valor</th></tr>")
                    for r_idx, (k, v) in enumerate(data["metadata"].items()):
                        bg = "#FFFFFF" if r_idx % 2 == 0 else "#F8FAFC"
                        parts.append(f"<tr style='background-color: {bg}; color: #1E293B;'><td style='border: 1px solid #CBD5E1; padding: 6px;'><b>{html.escape(str(k))}</b></td><td style='border: 1px solid #CBD5E1; padding: 6px;'>{html.escape(str(v))}</td></tr>")
                    parts.append("</table></div>")

                if "summary" in data and isinstance(data["summary"], dict):
                    parts.append("<h4 style='color: #334155; margin-top: 20px;'>Métricas Globales:</h4>")
                    parts.append("<div style='overflow-x: auto;'><table style='border-collapse: collapse; width: 100%; font-size: 12px; background: #FFFFFF;'>")
                    parts.append("<tr style='background-color: #1E293B; color: #FFFFFF;'><th style='border: 1px solid #CBD5E1; padding: 6px;'>Métrica</th><th style='border: 1px solid #CBD5E1; padding: 6px;'>Valor</th></tr>")
                    for r_idx, (k, v) in enumerate(data["summary"].items()):
                        bg = "#FFFFFF" if r_idx % 2 == 0 else "#F8FAFC"
                        val_str = f"{v:.4f}" if isinstance(v, float) else str(v)
                        parts.append(f"<tr style='background-color: {bg}; color: #1E293B;'><td style='border: 1px solid #CBD5E1; padding: 6px;'><b>{html.escape(str(k))}</b></td><td style='border: 1px solid #CBD5E1; padding: 6px;'>{html.escape(val_str)}</td></tr>")
                    parts.append("</table></div>")

                if "results" in data and isinstance(data["results"], list) and len(data["results"]) > 0:
                    sub_list = data["results"]
                    keys = [k for k in sub_list[0].keys() if k not in ("matches", "unmatched_dets", "unmatched_refs")]
                    parts.append("<h4 style='color: #334155; margin-top: 20px;'>Detalle por Imagen:</h4>")
                    parts.append("<div style='overflow-x: auto;'><table style='border-collapse: collapse; width: 100%; font-size: 12px; background: #FFFFFF;'>")
                    parts.append("<tr style='background-color: #1E293B; color: #FFFFFF;'>")
                    for k in keys:
                        parts.append(f"<th style='border: 1px solid #CBD5E1; padding: 6px;'>{html.escape(str(k))}</th>")
                    parts.append("</tr>")
                    for row_idx, item in enumerate(sub_list):
                        bg = "#FFFFFF" if row_idx % 2 == 0 else "#F8FAFC"
                        parts.append(f"<tr style='background-color: {bg}; color: #1E293B;'>")
                        for k in keys:
                            val = item.get(k, "")
                            if isinstance(val, float):
                                val_str = f"{val:.4f}"
                            else:
                                val_str = str(val)
                            parts.append(f"<td style='border: 1px solid #CBD5E1; padding: 6px;'>{html.escape(val_str)}</td>")
                        parts.append("</tr>")
                    parts.append("</table></div>")

                tabla_html = "".join(parts)

            return f"""
            <div style='font-family: sans-serif; padding: 10px;'>
                <h3 style='color: #0F172A; border-bottom: 2px solid #3B82F6; padding-bottom: 5px;'>📋 Estructura de Datos JSON: {html.escape(titulo)}</h3>
                {tabla_html}
                <h4 style='color: #334155; margin-top: 20px;'>Código JSON Completo:</h4>
                <pre style='background: #0F172A; color: #E2E8F0; padding: 12px; border-radius: 6px; font-family: Consolas, monospace; font-size: 12px; overflow-x: auto;'>{html.escape(pretty)}</pre>
            </div>
            """
        except Exception:
            return f"<pre>{html.escape(texto)}</pre>"

    def _renderizar_markdown_o_txt(self, texto: str, titulo: str, ext: str) -> str:
        lines = texto.splitlines()
        html_lines = [
            f"<div style='font-family: sans-serif; color: #1E293B; padding: 15px; line-height: 1.6; background: #FFFFFF; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>",
            f"<h3 style='color: #0F172A; border-bottom: 2px solid #3B82F6; padding-bottom: 6px; margin-top: 0;'>📄 Documento / Reporte: {html.escape(titulo)}</h3>"
        ]
        
        in_code_block = False
        table_rows = []
        
        def flush_table():
            nonlocal table_rows
            if not table_rows:
                return ""
            out = ["<div style='overflow-x: auto; margin: 10px 0;'><table style='border-collapse: collapse; width: 100%; font-size: 12px; background: #FFFFFF;'>"]
            for r_idx, cells in enumerate(table_rows):
                bg = "#1E293B" if r_idx == 0 else ("#FFFFFF" if r_idx % 2 == 1 else "#F8FAFC")
                color = "#FFFFFF" if r_idx == 0 else "#1E293B"
                tag = "th" if r_idx == 0 else "td"
                out.append(f"<tr style='background-color: {bg}; color: {color};'>")
                for cell in cells:
                    out.append(f"<{tag} style='border: 1px solid #CBD5E1; padding: 8px 10px; text-align: left;'>{html.escape(cell)}</{tag}>")
                out.append("</tr>")
            out.append("</table></div>")
            table_rows = []
            return "".join(out)

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                html_lines.append(flush_table())
                if in_code_block:
                    html_lines.append("</pre>")
                    in_code_block = False
                else:
                    html_lines.append("<pre style='background: #1E293B; color: #E2E8F0; padding: 12px; border-radius: 6px; font-family: Consolas, monospace; font-size: 12px; overflow-x: auto;'>")
                    in_code_block = True
                continue
            
            if in_code_block:
                html_lines.append(html.escape(line) + "\n")
                continue

            if stripped.startswith("|") and "|" in stripped[1:]:
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                if all(c.replace("-", "").replace(":", "") == "" for c in cells):
                    continue  # Línea separadora markdown (---)
                table_rows.append(cells)
                continue
            else:
                html_lines.append(flush_table())

            if stripped.startswith("# "):
                html_lines.append(f"<h1 style='color: #0F172A; border-bottom: 1px solid #E2E8F0; padding-bottom: 4px; margin-top: 16px; font-size: 18px;'>{html.escape(stripped[2:])}</h1>")
            elif stripped.startswith("## "):
                html_lines.append(f"<h2 style='color: #1E293B; margin-top: 14px; font-size: 16px;'>{html.escape(stripped[3:])}</h2>")
            elif stripped.startswith("### "):
                html_lines.append(f"<h3 style='color: #334155; margin-top: 12px; font-size: 14px;'>{html.escape(stripped[4:])}</h3>")
            elif stripped.startswith("- ") or stripped.startswith("* "):
                html_lines.append(f"<ul style='margin: 4px 0; padding-left: 20px;'><li>{html.escape(stripped[2:])}</li></ul>")
            elif not stripped:
                html_lines.append("<br>")
            else:
                html_lines.append(f"<p style='margin: 6px 0;'>{html.escape(line)}</p>")
                
        html_lines.append(flush_table())
        if in_code_block:
            html_lines.append("</pre>")
            
        html_lines.append("</div>")
        return "".join(html_lines)
