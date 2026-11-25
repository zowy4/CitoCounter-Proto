"""
src/reporte_ejecutivo_pdf.py - Motor de Reportes Ejecutivos en PDF (CITO-126 / ACT-48).

Genera informes clínicos estructurados y profesionales en formato PDF utilizando ReportLab,
incluyendo metadatos de la muestra, resumen estadístico por clase SIPaKMeD, índice de riesgo
clínico global (GCRI), gráficos tabulares y advertencias legales / experimentales.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_DISPONIBLE = True
except ImportError:
    REPORTLAB_DISPONIBLE = False


def validar_tamano_reporte(datos: Dict[str, Any], tamano_maximo_bytes: int = 65536 * 100) -> None:
    """
    Valida el tamaño de los datos de entrada según los controles de seguridad OWASP/STRIDE.

    :param datos: Diccionario con datos del reporte
    :type datos: Dict[str, Any]
    :param tamano_maximo_bytes: Límite máximo en bytes
    :type tamano_maximo_bytes: int
    :raises ValueError: Si los datos exceden el tamaño permitido
    """
    if datos is None:
        raise ValueError("Los datos del reporte son nulos.")
    import sys
    tamano = sys.getsizeof(str(datos))
    if tamano > tamano_maximo_bytes:
        raise ValueError(
            f"Tamaño de datos excede el límite OWASP/STRIDE ({tamano} bytes > {tamano_maximo_bytes} bytes)."
        )


def generar_reporte_ejecutivo_pdf(
    ruta_salida: str,
    metadatos_portaobjetos: Dict[str, Any],
    metricas_resultado: Dict[str, Any]
) -> str:
    """
    Genera un informe ejecutivo en PDF con los resultados del análisis citológico de CitoCounter-Proto.

    :param ruta_salida: Ruta absoluta o relativa donde se guardará el archivo PDF
    :type ruta_salida: str
    :param metadatos_portaobjetos: Diccionario con metadatos del paciente/portaobjetos
    :type metadatos_portaobjetos: Dict[str, Any]
    :param metricas_resultado: Diccionario con métricas agregadas y conteos por clase
    :type metricas_resultado: Dict[str, Any]
    :return: Ruta del archivo PDF generado
    :rtype: str
    """
    validar_tamano_reporte(metricas_resultado)

    if not REPORTLAB_DISPONIBLE:
        raise ImportError(
            "ReportLab no está instalado en el entorno. Instálelo con 'pip install reportlab'."
        )

    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story: List[Any] = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    estilo_titulo = ParagraphStyle(
        'TituloReporte',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        alignment=1,
        spaceAfter=10
    )

    estilo_subtitulo = ParagraphStyle(
        'SubTituloReporte',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        alignment=1,
        spaceAfter=20
    )

    estilo_seccion = ParagraphStyle(
        'SeccionReporte',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2A55E5'),
        spaceBefore=12,
        spaceAfter=6
    )

    estilo_texto = ParagraphStyle(
        'TextoReporte',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )

    estilo_alerta = ParagraphStyle(
        'AlertaReporte',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#B91C1C'),
        spaceBefore=10
    )

    # Cabecera
    story.append(Paragraph("<b>CITOCOUNTER-PROTO: INFORME CITOLÓGICO EJECUTIVO</b>", estilo_titulo))
    story.append(Paragraph(f"Fecha de emisión: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Prototipo de Investigación", estilo_subtitulo))

    # Sección 1: Metadatos
    story.append(Paragraph("1. Información del Portaobjetos y Muestra", estilo_seccion))
    datos_meta = [
        [Paragraph("<b>ID Muestra:</b>", estilo_texto), Paragraph(str(metadatos_portaobjetos.get('id_muestra', 'N/D')), estilo_texto)],
        [Paragraph("<b>Paciente / Código:</b>", estilo_texto), Paragraph(str(metadatos_portaobjetos.get('paciente', 'Anónimo')), estilo_texto)],
        [Paragraph("<b>Técnico / Analista:</b>", estilo_texto), Paragraph(str(metadatos_portaobjetos.get('analista', 'Sistema Automatizado')), estilo_texto)],
        [Paragraph("<b>Fecha de Captura:</b>", estilo_texto), Paragraph(str(metadatos_portaobjetos.get('fecha', datetime.now().strftime('%Y-%m-%d'))), estilo_texto)],
    ]
    tabla_meta = Table(datos_meta, colWidths=[120, 420])
    tabla_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tabla_meta)
    story.append(Spacer(1, 10))

    # Sección 2: Resumen de Resultados y Riesgo
    story.append(Paragraph("2. Resumen Estadístico y Clasificación SIPaKMeD", estilo_seccion))
    
    total_celulas = metricas_resultado.get("total_celulas", 0)
    gcri = metricas_resultado.get("indice_riesgo_global", 0.0)
    anormalidad = metricas_resultado.get("porcentaje_anormalidad", 0.0)
    estado = metricas_resultado.get("estado_clinico", "N/D")

    datos_resumen = [
        [Paragraph("<b>Total Células Analizadas:</b>", estilo_texto), Paragraph(str(total_celulas), estilo_texto)],
        [Paragraph("<b>Índice de Riesgo Global (GCRI):</b>", estilo_texto), Paragraph(f"<b>{gcri:.4f}</b>", estilo_texto)],
        [Paragraph("<b>Porcentaje de Anormalidad:</b>", estilo_texto), Paragraph(f"{anormalidad:.2f}%", estilo_texto)],
        [Paragraph("<b>Estado Clínico Estimado:</b>", estilo_texto), Paragraph(f"<b>{estado}</b>", estilo_texto)],
    ]
    tabla_resumen = Table(datos_resumen, colWidths=[160, 380])
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8EDF5')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#2A55E5')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tabla_resumen)
    story.append(Spacer(1, 10))

    # Sección 3: Desglose por Clase
    story.append(Paragraph("3. Desglose Detallado por Categoría SIPaKMeD", estilo_seccion))
    conteo_clases = metricas_resultado.get("conteo_por_clase", {})

    filas_clases = [
        [Paragraph("<b>Categoría / Clase SIPaKMeD</b>", estilo_texto), Paragraph("<b>Conteo</b>", estilo_texto), Paragraph("<b>Categoría Clínica</b>", estilo_texto)]
    ]
    
    nombres_es = {
        "Superficial-Intermediate": "Superficial e Intermedia",
        "Parabasal": "Parabasal",
        "Metaplastic": "Metaplásica",
        "Koilocytotic": "Koilocítica",
        "Dyskeratotic": "Disqueratósica"
    }
    cats_clinicas = {
        "Superficial-Intermediate": "Normal",
        "Parabasal": "Normal",
        "Metaplastic": "Benigno / Reactivo",
        "Koilocytotic": "LSIL (Bajo Grado)",
        "Dyskeratotic": "HSIL / Carcinoma (Alto Grado)"
    }

    for clave, nombre in nombres_es.items():
        conteo = conteo_clases.get(clave, 0)
        cat = cats_clinicas.get(clave, "")
        filas_clases.append([
            Paragraph(nombre, estilo_texto),
            Paragraph(str(conteo), estilo_texto),
            Paragraph(cat, estilo_texto)
        ])

    tabla_clases = Table(filas_clases, colWidths=[180, 80, 280])
    tabla_clases.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2A55E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(tabla_clases)
    story.append(Spacer(1, 15))

    # Sección 4: Aviso Legal / Experimental
    story.append(Paragraph("<b>AVISO LEGAL Y DE INVESTIGACIÓN:</b>", ParagraphStyle('HAlerta', parent=estilo_alerta, fontSize=9, textColor=colors.HexColor('#B91C1C'))))
    story.append(Paragraph(
        "CitoCounter-Proto es un prototipo de investigación y no constituye un dispositivo médico de diagnóstico "
        "ni reemplaza la evaluación citopatológica profesional. Los resultados, índices de riesgo y clasificaciones "
        "generados tienen fines exclusivamente experimentales y de soporte académico.",
        estilo_alerta
    ))

    doc.build(story)
    return ruta_salida

