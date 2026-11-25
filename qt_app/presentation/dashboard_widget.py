"""
dashboard_widget.py - Widget de Dashboard de métricas Qt reutilizando src/metricas_sistema.py y src/historial_resultados.py (CITO-65 / KPIs).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from src.metricas_sistema import metricas_conjunto
from src.historial_resultados import cargar_historial, filas_para_tabla


class KpiCard(QFrame):
    """Tarjeta individual para mostrar un KPI clave."""

    def __init__(self, titulo: str, valor_inicial: str = "0", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 600;")
        layout.addWidget(self.lbl_titulo)

        self.lbl_valor = QLabel(valor_inicial)
        self.lbl_valor.setStyleSheet("color: #1E293B; font-size: 20px; font-weight: bold;")
        layout.addWidget(self.lbl_valor)

    def actualizar_valor(self, valor: str) -> None:
        self.lbl_valor.setText(str(valor))


class DashboardWidget(QWidget):
    """Widget de Dashboard que consume métricas del sistema y bitácora histórica."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()
        self.actualizar_datos()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header / Acciones
        header_layout = QHBoxLayout()
        lbl_header = QLabel("Dashboard de Métricas e Historial CitoCounter")
        lbl_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        header_layout.addWidget(lbl_header)

        header_layout.addStretch()

        self.btn_actualizar = QPushButton("Actualizar Métricas")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        self.btn_actualizar.setStyleSheet(
            "background-color: #2A55E5; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600;"
        )
        header_layout.addWidget(self.btn_actualizar)

        layout.addLayout(header_layout)

        # Tarjetas KPI (Grid 2x3)
        grid_kpi = QGridLayout()
        grid_kpi.setSpacing(12)

        self.card_ejecuciones = KpiCard("Total Ejecuciones", "0")
        self.card_celulas = KpiCard("Promedio Células / Ejecución", "0.0")
        self.card_normales = KpiCard("Promedio Normales", "0.0")
        self.card_sospechosas = KpiCard("Promedio Sospechosas", "0.0")
        self.card_riesgo = KpiCard("Porcentaje Riesgo Promedio", "0.0%")
        self.card_tasa_alto = KpiCard("Tasa Riesgo Alto (>10%)", "0.0%")

        grid_kpi.addWidget(self.card_ejecuciones, 0, 0)
        grid_kpi.addWidget(self.card_celulas, 0, 1)
        grid_kpi.addWidget(self.card_normales, 0, 2)
        grid_kpi.addWidget(self.card_sospechosas, 1, 0)
        grid_kpi.addWidget(self.card_riesgo, 1, 1)
        grid_kpi.addWidget(self.card_tasa_alto, 1, 2)

        layout.addLayout(grid_kpi)

        # Tabla histórica
        lbl_tabla = QLabel("Evolución Temporal e Historial de Experimentos")
        lbl_tabla.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B; margin-top: 16px;")
        layout.addWidget(lbl_tabla)

        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(10)
        self.tabla_historial.setHorizontalHeaderLabels([
            "ID Prueba", "Fecha", "Hora", "Imagen", "Sigma 1", "Sigma 2", "Total", "Normales", "Sospechosas", "Riesgo (%)"
        ])
        self.tabla_historial.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_historial)

    def actualizar_datos(self) -> None:
        """Carga y actualiza los KPIs y la tabla consumiendo src/metricas_sistema.py y src/historial_resultados.py."""
        try:
            historial = cargar_historial()
            metricas = metricas_conjunto(historial)

            # Actualizar KPIs
            self.card_ejecuciones.actualizar_valor(str(metricas.get("total_ejecuciones", 0)))
            self.card_celulas.actualizar_valor(str(metricas.get("total_celulas_promedio", 0.0)))
            self.card_normales.actualizar_valor(str(metricas.get("normales_promedio", 0.0)))
            self.card_sospechosas.actualizar_valor(str(metricas.get("sospechosas_promedio", 0.0)))
            self.card_riesgo.actualizar_valor(f"{metricas.get('riesgo_promedio', 0.0):.1f}%")
            self.card_tasa_alto.actualizar_valor(f"{metricas.get('tasa_riesgo_alto', 0.0):.1f}%")

            # Actualizar tabla
            filas = filas_para_tabla(historial)
            self.tabla_historial.setRowCount(len(filas))
            for row_idx, fila in enumerate(filas):
                self.tabla_historial.setItem(row_idx, 0, QTableWidgetItem(str(fila.get("id_prueba", ""))))
                self.tabla_historial.setItem(row_idx, 1, QTableWidgetItem(str(fila.get("fecha", ""))))
                self.tabla_historial.setItem(row_idx, 2, QTableWidgetItem(str(fila.get("hora", ""))))
                self.tabla_historial.setItem(row_idx, 3, QTableWidgetItem(str(fila.get("imagen", ""))))
                self.tabla_historial.setItem(row_idx, 4, QTableWidgetItem(str(fila.get("sigma1", ""))))
                self.tabla_historial.setItem(row_idx, 5, QTableWidgetItem(str(fila.get("sigma2", ""))))
                self.tabla_historial.setItem(row_idx, 6, QTableWidgetItem(str(fila.get("total_celulas", ""))))
                self.tabla_historial.setItem(row_idx, 7, QTableWidgetItem(str(fila.get("normales", ""))))
                self.tabla_historial.setItem(row_idx, 8, QTableWidgetItem(str(fila.get("sospechosas", ""))))
                self.tabla_historial.setItem(row_idx, 9, QTableWidgetItem(str(fila.get("porcentaje_riesgo", ""))))
        except Exception as e:
            print(f"Error al actualizar dashboard: {e}")
