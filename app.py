"""
app.py - CitoCounter Proto Web Dashboard

Web App interactiva usando Streamlit para análisis celular en tiempo real.

EJECUCIÓN:
    streamlit run app.py

CARACTERÍSTICAS:
- Calibración de parámetros en tiempo real con sliders
- Visualización comparativa instantánea
- Métricas clave en dashboard
- Interfaz profesional para presentaciones
- Separación de núcleos superpuestos (Watershed/Máximos locales)
- Segmentación HSV por color
- Verificación de calidad de imagen
- Exportación JSON/CSV
"""

import streamlit as st
import cv2
import numpy as np
import tempfile
import os
import json
from pathlib import Path
from datetime import datetime

# Importar módulos existentes de CitoCounter Proto
from src.preprocessing import (
    preprocesar_imagen, 
    verificar_calidad_imagen,
    segmentar_por_hsv,
    anonimizar_metadata,
    obtener_id_sin_identificar
)
from src.dog_filter import aplicar_filtro_dog, visualizar_filtros_gauss
from src.analysis import (
    analizar_nucleos, 
    obtener_reglas_clasificacion,
    AREA_PROMEDIO_NUCLEO_NORMAL,
    FACTOR_RIESGO,
    MARGEN_FRONTERA
)
from src.visualization import dibujar_estadisticas_en_imagen, crear_vista_deteccion
from src.interfaz_resultados import (
    AVISO_USO_EXPERIMENTAL,
    generar_csv_resultados,
    resumen_resultado_experimental,
)
from src.metricas_sistema import (
    calcular_metricas_imagen,
    metricas_conjunto,
    reporte_resumen,
)

from src.historial_resultados import (
    cargar_historial,
    agregar_historial,
    filas_para_tabla,
)

from src.etl_resultados import (
    extraer_bitacora,
    transformar_a_esquema_unificado,
    agregado_por_imagen,
    agregado_por_sigma,
    exportar_csv,
    exportar_json,
)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024

# ============================================================================
# DESIGN SYSTEM - Medical Health Dashboard
# ============================================================================
DESIGN_SYSTEM_CSS = """
<style>
/* ============================================================================
   DESIGN SYSTEM - Medical Health Dashboard
   ============================================================================ */

/* CSS Custom Properties (Design Tokens) */
:root {
  /* Colors - Medical Health Dashboard Design System */
  /* Backgrounds */
  --color-bg-main-light: #F8FAFC;
  --color-bg-main-warm: #FAF8F5;
  --color-bg-panel-dark: #22252A;
  --color-bg-card-light: #FFFFFF;
  --color-bg-card-hover: #F5F7FA;
  
  /* Primary Brand */
  --color-brand-primary: #2A55E5;
  --color-brand-primary-light: #E8EDF5;
  --color-brand-primary-dark: #1E3A8A;
  
  /* Text Colors - Enhanced Contrast */
  --color-text-primary-dark: #1E293B;
  --color-text-primary-light: #FFFFFF;
  --color-text-on-warm: #1E293B;
  --color-text-subtle: #64748B;
  --color-text-caption: #94A3B8;
  
  /* Semantic Colors */
  --color-semantic-success: #10B981;
  --color-semantic-success-bg: #ECFDF5;
  --color-semantic-warning: #F59E0B;
  --color-semantic-warning-bg: #FFFBEB;
  --color-semantic-danger: #EF4444;
  --color-semantic-danger-bg: #FEE2E2;
  
  /* Elevation */
  --shadow-card: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-floating: 0 4px 12px 0 rgba(0, 0, 0, 0.15);
  --shadow-input: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  
  /* Border Radius */
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-pill: 9999px;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Typography */
  --font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  --font-size-xs: 10px;
  --font-size-sm: 12px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 20px;
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
}

/* ============================================================================
   BASE STYLES
   ============================================================================ */

html, body, [data-testid="stAppViewContainer"] {
    font-family: var(--font-family, 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif) !important;
    background-color: var(--color-bg-main-light) !important;
    color: var(--color-text-primary-dark) !important;
}

/* Hide Streamlit default elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Main container */
[data-testid="stAppViewContainer"] > .main {
    padding-top: var(--spacing-lg) !important;
    padding-bottom: var(--spacing-lg) !important;
}

/* ============================================================================
   CARD COMPONENTS
   ============================================================================ */

.medical-card {
    background: var(--color-bg-card-light);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-card);
    padding: var(--spacing-md);
    transition: all 0.2s ease;
    border: 1px solid rgba(0, 0, 0, 0.03);
}

.medical-card:hover {
    box-shadow: var(--shadow-floating);
    transform: translateY(-2px);
}

.medical-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-sm);
    padding-bottom: var(--spacing-sm);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.medical-card-title {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary-dark);
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
}

.medical-card-icon {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}

.medical-card-icon.primary { background: var(--color-brand-primary-light); color: var(--color-brand-primary); }
.medical-card-icon.success { background: var(--color-semantic-success-bg); color: var(--color-semantic-success); }
.medical-card-icon.warning { background: #FEF3C7; color: var(--color-semantic-warning); }
.medical-card-icon.danger { background: var(--color-semantic-danger-bg); color: var(--color-semantic-danger); }
.medical-card-icon.info { background: var(--color-brand-primary-light); color: var(--color-brand-primary); }

.medical-card-content {
    color: var(--color-text-secondary-dark);
    font-size: var(--font-size-md);
    line-height: 1.6;
}

/* ============================================================================
   METRIC CARDS
   ============================================================================ */

.metric-card {
    background: var(--color-bg-card-light);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-card);
    padding: var(--spacing-md);
    border: 1px solid rgba(0, 0, 0, 0.03);
    transition: all 0.2s ease;
}

.metric-card:hover {
    box-shadow: var(--shadow-floating);
    transform: translateY(-2px);
}

.metric-value {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-primary-dark);
    line-height: 1.2;
}

.metric-label {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-secondary-dark);
    margin-top: var(--spacing-xs);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-delta {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    margin-top: var(--spacing-xs);
}

.metric-delta.positive { color: var(--color-semantic-success); }
.metric-delta.negative { color: var(--color-semantic-danger); }
.metric-delta.neutral { color: var(--color-text-secondary-dark); }

/* ============================================================================
   BUTTONS
   ============================================================================ */

.btn-primary {
    background: var(--color-brand-primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
}

.btn-primary:hover {
    background: #1E40C0;
    box-shadow: var(--shadow-floating);
    transform: translateY(-1px);
}

.btn-secondary {
    background: var(--color-bg-main-light);
    color: var(--color-text-primary-dark);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: var(--radius-md);
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
}

.btn-secondary:hover {
    background: var(--color-bg-main-warm);
    border-color: var(--color-brand-primary);
}

.btn-pill {
    background: var(--color-brand-primary-light);
    color: var(--color-brand-primary);
    border: none;
    border-radius: var(--radius-pill);
    padding: var(--spacing-xs) var(--spacing-md);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
}

.btn-pill:hover {
    background: var(--color-brand-primary);
    color: white;
}

.btn-pill.success { background: var(--color-semantic-success-bg); color: var(--color-semantic-success); }
.btn-pill.success:hover { background: var(--color-semantic-success); color: white; }
.btn-pill.warning { background: #FEF3C7; color: var(--color-semantic-warning); }
.btn-pill.warning:hover { background: var(--color-semantic-warning); color: white; }
.btn-pill.danger { background: var(--color-semantic-danger-bg); color: var(--color-semantic-danger); }
.btn-pill.danger:hover { background: var(--color-semantic-danger); color: white; }

/* ============================================================================
   BADGES & PILLS
   ============================================================================ */

.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: var(--radius-pill);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    gap: var(--spacing-xs);
}

.badge.primary { background: var(--color-brand-primary-light); color: var(--color-brand-primary); }
.badge.success { background: var(--color-semantic-success-bg); color: var(--color-semantic-success); }
.badge.warning { background: #FEF3C7; color: var(--color-semantic-warning); }
.badge.danger { background: var(--color-semantic-danger-bg); color: var(--color-semantic-danger); }
.badge.info { background: var(--color-brand-primary-light); color: var(--color-brand-primary); }

/* ============================================================================
   NAVIGATION SIDEBAR
   ============================================================================ */

.sidebar-nav {
    background: var(--color-bg-card-light);
    border-radius: var(--radius-pill);
    box-shadow: var(--shadow-card);
    padding: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
}

.nav-section {
    margin-bottom: var(--spacing-md);
}

.nav-section-title {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-secondary-dark);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: var(--spacing-xs) var(--spacing-sm);
    margin-bottom: var(--spacing-xs);
}

.nav-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-md);
    color: var(--color-text-primary-dark);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    cursor: pointer;
    transition: all 0.2s ease;
    margin-bottom: var(--spacing-xs);
}

.nav-item:hover {
    background: var(--color-brand-primary-light);
    color: var(--color-brand-primary);
}

.nav-item.active {
    background: var(--color-brand-primary);
    color: white;
}

.nav-item-icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* ============================================================================
   QUICK ACTION BUTTONS
   ============================================================================ */

.quick-actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
    margin: var(--spacing-md) 0;
}

.quick-action-btn {
    background: var(--color-bg-card-light);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: var(--radius-md);
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-primary-dark);
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
}

.quick-action-btn:hover {
    border-color: var(--color-brand-primary);
    background: var(--color-brand-primary-light);
    color: var(--color-brand-primary);
    box-shadow: var(--shadow-floating);
    transform: translateY(-1px);
}

.quick-action-btn.primary {
    background: var(--color-brand-primary);
    color: white;
    border-color: var(--color-brand-primary);
}

.quick-action-btn.primary:hover {
    background: #1E40C0;
}

/* ============================================================================
   TABS
   ============================================================================ */

.stTabs [data-baseweb="tab-list"] {
    gap: var(--spacing-xs);
    background: transparent;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    padding-bottom: 0;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: var(--radius-md) !important;
    padding: var(--spacing-sm) var(--spacing-md) !important;
    font-size: var(--font-size-sm) !important;
    font-weight: var(--font-weight-medium) !important;
    color: var(--color-text-secondary-dark) !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--color-brand-primary-light) !important;
    color: var(--color-brand-primary) !important;
}

.stTabs [aria-selected="true"] {
    background: var(--color-brand-primary) !important;
    color: white !important;
    box-shadow: var(--shadow-floating) !important;
}

/* ============================================================================
   METRICS
   ============================================================================ */

[data-testid="stMetric"] {
    background: var(--color-bg-card-light) !important;
    border-radius: var(--radius-lg) !important;
    padding: var(--spacing-md) !important;
    border: 1px solid rgba(0, 0, 0, 0.03) !important;
    box-shadow: var(--shadow-card) !important;
}

[data-testid="stMetricValue"] {
    font-size: var(--font-size-2xl) !important;
    font-weight: var(--font-weight-bold) !important;
    color: var(--color-text-primary-dark) !important;
}

[data-testid="stMetricLabel"] {
    font-size: var(--font-size-sm) !important;
    font-weight: var(--font-weight-medium) !important;
    color: var(--color-text-secondary-dark) !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

[data-testid="stMetricDelta"] {
    font-size: var(--font-size-xs) !important;
    font-weight: var(--font-weight-medium) !important;
}

/* ============================================================================
   EXPANDERS
   ============================================================================ */

.streamlit-expanderHeader {
    background: var(--color-bg-card-light) !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    font-weight: var(--font-weight-semibold) !important;
    color: var(--color-text-primary-dark) !important;
    font-size: var(--font-size-md) !important;
}

.streamlit-expanderContent {
    background: var(--color-bg-main-light) !important;
    border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    border-top: none !important;
    padding: var(--spacing-md) !important;
}

/* ============================================================================
   SIDEBAR
   ============================================================================ */

[data-testid="stSidebar"] {
    background: var(--color-bg-main-warm) !important;
    border-right: 1px solid rgba(0, 0, 0, 0.06) !important;
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--color-text-primary-dark) !important;
}

[data-testid="stSidebar"] .stRadio > label {
    font-weight: var(--font-weight-semibold) !important;
    color: var(--color-text-primary-dark) !important;
}

[data-testid="stSidebar"] .stSlider > div > div > div > div {
    background: var(--color-brand-primary) !important;
}

[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--color-bg-card-light) !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
}

/* ============================================================================
   BUTTONS (Streamlit native)
   ============================================================================ */

.stButton > button {
    background: var(--color-brand-primary) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: var(--spacing-sm) var(--spacing-md) !important;
    font-size: var(--font-size-sm) !important;
    font-weight: var(--font-weight-semibold) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: #1E40C0 !important;
    box-shadow: var(--shadow-floating) !important;
    transform: translateY(-1px) !important;
}

.stButton > button[kind="secondary"] {
    background: var(--color-bg-main-light) !important;
    color: var(--color-text-primary-dark) !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: var(--color-bg-main-warm) !important;
    border-color: var(--color-brand-primary) !important;
}

/* ============================================================================
   ALERTS
   ============================================================================ */

.stAlert {
    border-radius: var(--radius-md) !important;
    border: none !important;
    padding: var(--spacing-md) !important;
}

.stAlert[data-baseweb="notification"][kind="info"] {
    background: var(--color-brand-primary-light) !important;
    color: var(--color-brand-primary) !important;
    border-left: 4px solid var(--color-brand-primary) !important;
}

.stAlert[data-baseweb="notification"][kind="success"] {
    background: var(--color-semantic-success-bg) !important;
    color: var(--color-semantic-success) !important;
    border-left: 4px solid var(--color-semantic-success) !important;
}

.stAlert[data-baseweb="notification"][kind="warning"] {
    background: #FEF3C7 !important;
    color: var(--color-semantic-warning) !important;
    border-left: 4px solid var(--color-semantic-warning) !important;
}

.stAlert[data-baseweb="notification"][kind="error"] {
    background: var(--color-semantic-danger-bg) !important;
    color: var(--color-semantic-danger) !important;
    border-left: 4px solid var(--color-semantic-danger) !important;
}

/* ============================================================================
   DATAFRAME
   ============================================================================ */

[data-testid="stDataFrame"] {
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    box-shadow: var(--shadow-card) !important;
}

[data-testid="stDataFrame"] table {
    font-size: var(--font-size-sm) !important;
}

[data-testid="stDataFrame"] th {
    background: var(--color-bg-main-warm) !important;
    font-weight: var(--font-weight-semibold) !important;
    color: var(--color-text-primary-dark) !important;
    padding: var(--spacing-sm) var(--spacing-md) !important;
}

[data-testid="stDataFrame"] td {
    padding: var(--spacing-sm) var(--spacing-md) !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.04) !important;
}

/* ============================================================================
   FILE UPLOADER
   ============================================================================ */

[data-testid="stFileUploader"] {
    background: var(--color-bg-card-light) !important;
    border: 2px dashed rgba(42, 85, 229, 0.3) !important;
    border-radius: var(--radius-lg) !important;
    padding: var(--spacing-lg) !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--color-brand-primary) !important;
    background: var(--color-brand-primary-light) !important;
}

/* ============================================================================
   PROGRESS BAR
   ============================================================================ */

.stProgress > div > div > div > div {
    background: var(--color-brand-primary) !important;
    border-radius: var(--radius-pill) !important;
}

/* ============================================================================
   SELECTBOX / MULTISELECT
   ============================================================================ */

.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--color-bg-card-light) !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
}

/* ============================================================================
   SLIDER
   ============================================================================ */

.stSlider > div > div > div > div {
    background: var(--color-brand-primary) !important;
}

.stSlider > div > div > div > div::after {
    background: var(--color-brand-primary) !important;
    border-color: var(--color-brand-primary) !important;
}

/* ============================================================================
   CHECKBOX
   ============================================================================ */

.stCheckbox > label > div:first-child {
    background: var(--color-bg-card-light) !important;
    border: 2px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: var(--radius-sm) !important;
}

.stCheckbox > label > div:first-child[data-checked="true"] {
    background: var(--color-brand-primary) !important;
    border-color: var(--color-brand-primary) !important;
}

/* ============================================================================
   RADIO
   ============================================================================ */

.stRadio > label > div:first-child {
    background: var(--color-bg-card-light) !important;
    border: 2px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: var(--radius-sm) !important;
}

.stRadio > label > div:first-child[data-checked="true"] {
    background: var(--color-brand-primary) !important;
    border-color: var(--color-brand-primary) !important;
}

/* ============================================================================
   RESPONSIVE
   ============================================================================ */

@media (max-width: 768px) {
    .stMetric {
        padding: var(--spacing-sm) !important;
    }
    
    .metric-value {
        font-size: var(--font-size-xl) !important;
    }
    
    .medical-card {
        padding: var(--spacing-sm) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: var(--spacing-xs) var(--spacing-sm) !important;
        font-size: var(--font-size-xs) !important;
    }
}

/* ============================================================================
   ANIMATIONS
   ============================================================================ */

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.animate-fade-in-up {
    animation: fadeInUp 0.4s ease-out forwards;
}

.animate-pulse {
    animation: pulse 2s ease-in-out infinite;
}

/* Staggered animation for cards */
.medical-card:nth-child(1) { animation-delay: 0ms; }
.medical-card:nth-child(2) { animation-delay: 50ms; }
.medical-card:nth-child(3) { animation-delay: 100ms; }
.medical-card:nth-child(4) { animation-delay: 150ms; }
.medical-card:nth-child(5) { animation-delay: 200ms; }
.medical-card:nth-child(6) { animation-delay: 250ms; }

</style>
"""

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="CitoCounter Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Design System CSS
st.markdown(DESIGN_SYSTEM_CSS, unsafe_allow_html=True)

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="CitoCounter Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="medical-card" style="margin-bottom: var(--spacing-lg);">
    <div class="medical-card-header">
        <div class="medical-card-title">
            <span class="medical-card-icon primary">🔬</span>
            <span>CitoCounter Dashboard</span>
        </div>
        <span class="badge info">v1.1 Web</span>
    </div>
    <div class="medical-card-content">
        <p style="margin: 0; color: var(--color-text-secondary-dark);">
            Análisis experimental de núcleos con filtro DoG y regla de área de referencia.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.warning(AVISO_USO_EXPERIMENTAL, icon="⚠️")

# ============================================================================
# QUICK ACTIONS BAR
# ============================================================================
# Set section from query params if available
seccion = st.query_params.get("section", "dashboard")

st.markdown("""
<div class="quick-actions">
    <button class="quick-action-btn primary" onclick="window.location.search='?section=config'">
        ⚙️ Configuración
    </button>
    <button class="quick-action-btn" onclick="window.location.search='?section=upload'">
        📤 Subir Imagen
    </button>
    <button class="quick-action-btn" onclick="window.location.search='?section=dataset'">
        📁 Dataset
    </button>
    <button class="quick-action-btn" onclick="window.location.search='?section=historial'">
        📊 Historial
    </button>
    <button class="quick-action-btn" onclick="window.location.search='?section=metricas'">
        📊 Métricas
    </button>
    <button class="quick-action-btn" onclick="window.location.search='?section=exportar'">
        📥 Exportar
    </button>
</div>
""", unsafe_allow_html=True)

st.warning(AVISO_USO_EXPERIMENTAL, icon="⚠️")

# ============================================================================
# QUICK STATS CARDS ROW
# ============================================================================
if seccion == "historial" or seccion == "dashboard":
    historial = cargar_historial()
    if historial:
        resumen_historial = agregar_historial(historial)
        m = metricas_conjunto(historial)
        
        st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--spacing-md); margin-bottom: var(--spacing-lg);">
            <div class="metric-card animate-fade-in-up">
                <div class="metric-value">{}</div>
                <div class="metric-label">Ejecuciones Totales</div>
            </div>
            <div class="metric-card animate-fade-in-up" style="animation-delay: 50ms;">
                <div class="metric-value">{}</div>
                <div class="metric-label">Imágenes Únicas</div>
            </div>
            <div class="metric-card animate-fade-in-up" style="animation-delay: 100ms;">
                <div class="metric-value">{}</div>
                <div class="metric-label">Células Detectadas</div>
            </div>
            <div class="metric-card animate-fade-in-up" style="animation-delay: 150ms;">
                <div class="metric-value">{}%</div>
                <div class="metric-label">Riesgo Promedio</div>
            </div>
        </div>
        """.format(
            resumen_historial["total_ejecuciones"],
            resumen_historial["imagenes_unicas"],
            resumen_historial["total_celulas"],
            f"{resumen_historial['promedio_riesgo']:.1f}"
        ), unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT LAYOUT
# ============================================================================
main_col, side_col = st.columns([7, 3], gap="large")

with main_col:
    # Main content area will be rendered based on processing mode
    pass

with side_col:
    # Sidebar content will be rendered here
    pass

# ============================================================================
# FUNCIONES AUXILIARES PARA DATASET Y PROCESAMIENTO EN LOTE
# ============================================================================

@st.cache_data
def escanear_dataset(ruta_base="data/raw"):
    """Escanea el directorio del dataset y retorna lista de imágenes disponibles."""
    ruta = Path(ruta_base)
    if not ruta.exists():
        return []
    
    extensiones = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}
    imagenes = []
    for ext in extensiones:
        imagenes.extend(ruta.glob(f"*{ext}"))
        imagenes.extend(ruta.glob(f"*{ext.upper()}"))
    
    # Ordenar por nombre
    imagenes.sort(key=lambda x: x.name.lower())
    return imagenes


def procesar_imagen_individual(ruta_imagen, params):
    """Procesa una sola imagen y retorna resultados."""
    try:
        # Preprocesar
        imagen_gris, imagen_original = preprocesar_imagen(
            str(ruta_imagen),
            mejorar_contraste_flag=params['usar_clahe'],
            reducir_ruido_flag=params['reducir_ruido'],
            metodo_contraste=params['modo_clahe'],
            nivel_ruido=params['nivel_ruido'],
            polaridad=params['polaridad'],
            usar_hsv=params['usar_hsv'],
            metodo_hsv=params['metodo_hsv'],
            umbral_hsv=params['umbral_hsv']
        )
        
        # Verificar calidad
        metricas_calidad = verificar_calidad_imagen(imagen_gris)
        
        # DoG
        imagen_dog = aplicar_filtro_dog(imagen_gris, params['sigma1'], params['sigma2'])
        
        # Análisis
        metodo_sep = None if params['metodo_separacion'] == "none" else params['metodo_separacion']
        resultados = analizar_nucleos(
            imagen_dog, 
            imagen_original, 
            polaridad=params['polaridad'],
            metodo_separacion=metodo_sep
        )
        
        # Visualizaciones
        img_resultado = dibujar_estadisticas_en_imagen(
            resultados['imagen_procesada'], 
            resultados, 
            posicion='superior'
        )
        
        img_deteccion = crear_vista_deteccion(
            imagen_original,
            resultados['contornos_normales'],
            resultados['contornos_sospechosos'],
            dibujar_contornos=params['mostrar_contornos']
        )
        
        return {
            'exito': True,
            'archivo': ruta_imagen.name,
            'ruta': str(ruta_imagen),
            'resultados': resultados,
            'metricas_calidad': metricas_calidad,
            'img_resultado': img_resultado,
            'img_deteccion': img_deteccion,
            'imagen_original': imagen_original,
            'imagen_gris': imagen_gris,
            'imagen_dog': imagen_dog
        }
    except Exception as e:
        return {
            'exito': False,
            'archivo': ruta_imagen.name,
            'ruta': str(ruta_imagen),
            'error': str(e)
        }


def generar_csv_lote(resultados_lote, params):
    """Genera CSV consolidado para procesamiento en lote."""
    import csv
    from io import StringIO
    
    buffer = StringIO()
    writer = csv.writer(buffer)
    
    # Encabezados
    writer.writerow([
        "Archivo", "Total_Celulas", "Normales", "Sospechosas", 
        "Frontera", "Porcentaje_Riesgo", "Sigma1", "Sigma2",
        "Polaridad", "CLAHE", "Modo_CLAHE", "Reducir_Ruido",
        "Nivel_Ruido", "HSV", "Metodo_HSV", "Umbral_HSV",
        "Separacion", "Contraste", "Brillo", "Saturacion", "Calidad_Aceptable"
    ])
    
    for r in resultados_lote:
        if r['exito']:
            res = r['resultados']
            cal = r['metricas_calidad']
            writer.writerow([
                r['archivo'],
                res['total_celulas'],
                res['normales'],
                res['sospechosas'],
                res.get('frontera', 0),
                f"{res['porcentaje_riesgo']:.1f}%",
                params['sigma1'],
                params['sigma2'],
                params['polaridad'],
                "Si" if params['usar_clahe'] else "No",
                params['modo_clahe'],
                "Si" if params['reducir_ruido'] else "No",
                params['nivel_ruido'],
                "Si" if params['usar_hsv'] else "No",
                params['metodo_hsv'],
                params['umbral_hsv'],
                params['metodo_separacion'],
                f"{cal['contraste']:.1f}",
                f"{cal['brillo_promedio']:.1f}",
                f"{cal['saturacion']:.1f}%",
                "Si" if cal['es_aceptable'] else "No"
            ])
        else:
            writer.writerow([r['archivo'], "ERROR", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    
    return buffer.getvalue()


# ============================================================================
# ÁREA PRINCIPAL
# ============================================================================

# Barra lateral con configuración
with st.sidebar:
    st.header("⚙️ Configuración de Análisis")
    
    # --- FUENTE DE IMÁGENES ---
    st.subheader("📂 Fuente de Imágenes")
    
    fuente_imagenes = st.radio(
        "Seleccionar origen",
        options=["upload", "dataset"],
        format_func=lambda x: {
            "upload": "📤 Subir archivo(s)",
            "dataset": "📁 Dataset del proyecto (data/raw/)"
        }[x],
        help="Elige entre subir tus propias imágenes o usar las del dataset del proyecto"
    )
    
    st.markdown("---")
    
    # --- PARÁMETROS DOG ---
    st.subheader("1️⃣ Parámetros del Filtro DoG")
    
    sigma1 = st.slider(
        "Sigma 1 (Detalle fino)", 
        min_value=0.5, 
        max_value=10.0, 
        value=7.0,
        step=0.1,
        help="Controla la detección de estructuras pequeñas"
    )
    
    sigma2 = st.slider(
        "Sigma 2 (Estructura general)", 
        min_value=0.5, 
        max_value=15.0, 
        value=8.0,
        step=0.1,
        help="Controla la detección de estructuras grandes"
    )
    
    # Validación de parámetros
    if sigma2 <= sigma1:
        st.error("⚠️ Sigma 2 debe ser mayor que Sigma 1")
        st.info("💡 Regla recomendada: σ2 ≈ 1.6-2.0 × σ1")
    else:
        ratio = sigma2 / sigma1
        st.info(f"Relación actual: {ratio:.2f}x")
    
    st.markdown("---")
    
    # --- PREPROCESAMIENTO ---
    st.subheader("2️⃣ Preprocesamiento")
    
    polaridad = st.selectbox(
        "Polaridad de los núcleos",
        options=["nucleos-claros", "nucleos-oscuros"],
        index=0,
        help=(
            "Núcleos claros sobre fondo oscuro (fluorescencia) o núcleos "
            "oscuros sobre fondo claro (Papanicolaou/EDF). La opción "
            "'nucleos-oscuros' invierte la imagen antes del DoG."
        )
    )
    
    usar_clahe = st.checkbox(
        "Mejorar Contraste (CLAHE)", 
        value=True,
        help="Adaptive Histogram Equalization - mejora iluminación irregular"
    )
    
    # Modo automático de CLAHE
    if usar_clahe:
        modo_clahe = st.selectbox(
            "Modo CLAHE",
            options=["clahe", "auto", "histogram", "normalize"],
            index=0,
            help="Auto selecciona automáticamente según el contraste de la imagen"
        )
    else:
        modo_clahe = "clahe"
    
    reducir_ruido = st.checkbox(
        "Reducir Ruido", 
        value=False,
        help="Filtro bilateral - útil para imágenes con mucho ruido"
    )
    
    if reducir_ruido:
        nivel_ruido = st.selectbox(
            "Nivel de reducción",
            options=["bajo", "medio", "alto"],
            index=1,
            help="Intensidad del filtro bilateral"
        )
    else:
        nivel_ruido = "medio"
    
    st.markdown("---")
    
    # --- SEGMENTACIÓN AVANZADA (CITO-33, CITO-32) ---
    st.subheader("3️⃣ Segmentación Avanzada")
    
    usar_hsv = st.checkbox(
        "Segmentación HSV (Color)", 
        value=False,
        help="Usa el canal de saturación/valor HSV para resaltar núcleos por color. Útil cuando el contraste de intensidad es bajo."
    )
    
    if usar_hsv:
        metodo_hsv = st.selectbox(
            "Método HSV",
            options=["saturation", "value"],
            index=0,
            help="Saturation: núcleos con color distinto. Value: núcleos más brillos/oscuros."
        )
        umbral_hsv = st.slider(
            "Umbral HSV",
            min_value=0,
            max_value=255,
            value=100,
            step=5,
            help="Umbral mínimo en el canal seleccionado (0-255)"
        )
    else:
        metodo_hsv = "saturation"
        umbral_hsv = 100
    
    st.markdown("---")
    
    # --- SEPARACIÓN DE NÚCLEOS (CITO-32) ---
    st.subheader("4️⃣ Separación de Núcleos Superpuestos")
    
    metodo_separacion = st.selectbox(
        "Método de separación",
        options=["none", "watershed", "maximos_locales"],
        index=0,
        format_func=lambda x: {
            "none": "Sin separación (original)",
            "watershed": "Watershed (Transformada de distancia)",
            "maximos_locales": "Máximos locales (picos DoG)"
        }[x],
        help="Watershed separa núcleos en contacto. Máximos locales detecta picos en la respuesta DoG."
    )
    
    if metodo_separacion != "none":
        st.info("⚠️ Experimental: puede cambiar el conteo total de células")
    
    st.markdown("---")
    
    # --- VISUALIZACIÓN ---
    st.subheader("5️⃣ Opciones de Visualización")
    
    mostrar_contornos = st.checkbox(
        "Dibujar Contornos Reales", 
        value=True,
        help="Muestra los contornos detectados sobre las células"
    )
    
    mostrar_areas = st.checkbox(
        "Mostrar Áreas en Imagen", 
        value=False,
        help="Muestra el área en píxeles² sobre cada detección"
    )
    
    st.markdown("---")
    
    # --- INFORMACIÓN ---
    with st.expander("ℹ️ Acerca de CitoCounter"):
        st.markdown("""
        **Versión:** 1.1 Web
        
        **Algoritmo:**
        - Filtro DoG (Difference of Gaussians)
        - Regla del 3x (Dr. Rangel)
        
        **Pipeline:**
        1. Preprocesamiento (CLAHE)
        2. Filtro DoG
        3. Segmentación
        4. Clasificación (Normal/Sospechoso)
        
        **Criterio de Riesgo:**
        Núcleos con área ≥ 3× promedio → Sospechosos
        """)
    
    with st.expander("📚 Guía de Uso"):
        st.markdown("""
        **Pasos:**
        1. Selecciona la fuente de imágenes (subir o dataset)
        2. Elige una o varias imágenes
        3. Ajusta los sliders de Sigma
        4. Observa los resultados en tiempo real
        5. Compara en las pestañas visuales
        
        **Tips:**
        - Aumenta σ1 si detecta mucho ruido
        - Disminuye σ1 para captar más detalles
        - σ2 controla el tamaño de estructuras
        - Usa HSV si los núcleos tienen color distintivo
        - Watershed ayuda con núcleos superpuestos
        - Modo lote: procesa múltiples imágenes a la vez
        """)

# ============================================================================
# ÁREA PRINCIPAL
# ============================================================================

# Escanear dataset si se selecciona esa fuente
if fuente_imagenes == "dataset":
    imagenes_dataset = escanear_dataset("data/raw")
    
    if not imagenes_dataset:
        st.warning("⚠️ No se encontraron imágenes en data/raw/")
        st.info("Asegúrate de que el dataset esté en data/raw/ o usa la opción 'Subir archivo(s)'")
        st.stop()
    
    st.markdown(f"### 📁 Dataset del proyecto: **{len(imagenes_dataset)} imágenes disponibles**")
    
    # Selector de modo
    modo_procesamiento = st.radio(
        "Modo de procesamiento",
        options=["individual", "lote"],
        format_func=lambda x: {
            "individual": "🔍 Una imagen a la vez (vista detallada)",
            "lote": "📦 Procesamiento en lote (múltiples imágenes)"
        }[x],
        horizontal=True
    )
    
    if modo_procesamiento == "individual":
        # Selector individual
        nombres_imagenes = [img.name for img in imagenes_dataset]
        idx_seleccionado = st.selectbox(
            "Seleccionar imagen",
            options=range(len(nombres_imagenes)),
            format_func=lambda i: nombres_imagenes[i],
            help=f"Elige una de las {len(nombres_imagenes)} imágenes del dataset"
        )
        imagenes_seleccionadas = [imagenes_dataset[idx_seleccionado]]
    else:
        # Selector múltiple para lote
        nombres_imagenes = [img.name for img in imagenes_dataset]
        indices_seleccionados = st.multiselect(
            "Seleccionar imágenes para procesar en lote",
            options=range(len(nombres_imagenes)),
            format_func=lambda i: nombres_imagenes[i],
            default=[0, 1, 2] if len(nombres_imagenes) >= 3 else list(range(len(nombres_imagenes))),
            help=f"Elige múltiples imágenes (máx. {len(nombres_imagenes)} disponibles). Se procesarán secuencialmente."
        )
        imagenes_seleccionadas = [imagenes_dataset[i] for i in indices_seleccionados]
        
        if not imagenes_seleccionadas:
            st.info("👆 Selecciona al menos una imagen para procesar en lote")
            st.stop()
        
        st.info(f"📦 **{len(imagenes_seleccionadas)} imágenes seleccionadas** para procesamiento en lote")
        
        # Opciones de lote
        col_lote1, col_lote2 = st.columns(2)
        with col_lote1:
            mostrar_progreso = st.checkbox("Mostrar barra de progreso", value=True)
        with col_lote2:
            guardar_resultados_lote = st.checkbox("Guardar resultados en bitácora", value=True)

else:
    # Modo upload (original)
    uploaded_files = st.file_uploader(
        "📂 Cargar imagen(es) de microscopía cervical", 
        type=['jpg', 'png', 'jpeg', 'tif', 'tiff'],
        accept_multiple_files=True,
        help="Formatos soportados: JPG, PNG, TIF. Puedes seleccionar múltiples archivos."
    )
    
    if not uploaded_files:
        st.info("👆 **Carga una o varias imágenes de microscopía para comenzar el análisis**")
        st.stop()
    
    # Convertir uploaded_files a lista de rutas temporales
    imagenes_seleccionadas = []
    rutas_temporales = []
    
    for uploaded_file in uploaded_files:
        contenido_subido = uploaded_file.getvalue()
        extension = Path(uploaded_file.name).suffix.lower()
        
        if len(contenido_subido) > MAX_UPLOAD_BYTES:
            st.error(f"❌ {uploaded_file.name}: supera el límite de 10 MiB.")
            continue
        
        archivo_temporal = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
        archivo_temporal.write(contenido_subido)
        archivo_temporal.close()
        
        imagenes_seleccionadas.append(Path(archivo_temporal.name))
        rutas_temporales.append(archivo_temporal.name)
    
    if not imagenes_seleccionadas:
        st.error("No se pudieron cargar imágenes válidas.")
        st.stop()
    
    modo_procesamiento = "lote" if len(imagenes_seleccionadas) > 1 else "individual"
    if modo_procesamiento == "lote":
        st.info(f"📦 **{len(imagenes_seleccionadas)} imágenes cargadas** para procesamiento en lote")

# Parámetros comunes para procesamiento
params_procesamiento = {
    'sigma1': sigma1,
    'sigma2': sigma2,
    'polaridad': polaridad,
    'usar_clahe': usar_clahe,
    'modo_clahe': modo_clahe,
    'reducir_ruido': reducir_ruido,
    'nivel_ruido': nivel_ruido,
    'usar_hsv': usar_hsv,
    'metodo_hsv': metodo_hsv,
    'umbral_hsv': umbral_hsv,
    'metodo_separacion': metodo_separacion,
    'mostrar_contornos': mostrar_contornos,
    'mostrar_areas': mostrar_areas
}

# ============================================================================
# PROCESAMIENTO
# ============================================================================

if modo_procesamiento == "individual":
    # Procesamiento individual (vista detallada original)
    ruta_imagen = imagenes_seleccionadas[0]
    
    with st.spinner(f'🔬 Analizando {ruta_imagen.name}...'):
        resultado = procesar_imagen_individual(ruta_imagen, params_procesamiento)
    
    if not resultado['exito']:
        st.error(f"❌ Error procesando {resultado['archivo']}: {resultado['error']}")
        st.stop()
    
    # Extraer resultados para compatibilidad con código existente
    resultados = resultado['resultados']
    metricas_calidad = resultado['metricas_calidad']
    img_resultado = resultado['img_resultado']
    img_deteccion = resultado['img_deteccion']
    imagen_original = resultado['imagen_original']
    imagen_gris = resultado['imagen_gris']
    imagen_dog = resultado['imagen_dog']
    
    # ====================================================================
    # MOSTRAR RESULTADOS INDIVIDUALES
    # ====================================================================
    
    # ====================================================================
    # SECCIÓN DE MÉTRICAS
    # ====================================================================
    st.markdown("### 📊 Resultados del Análisis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Células", 
            value=resultados['total_celulas'],
            help="Número total de núcleos detectados"
        )
    
    with col2:
        st.metric(
            label="Normales", 
            value=resultados['normales'],
            delta=None,
            help="Células con área < 3x promedio"
        )
    
    with col3:
        st.metric(
            label="Sospechosas", 
            value=resultados['sospechosas'],
            delta=f"{resultados['sospechosas']} detectadas",
            delta_color="inverse",
            help="Células con área ≥ 3x promedio (Regla del 3x)"
        )
    
    with col4:
        porcentaje = resultados['porcentaje_riesgo']
        color_riesgo = "🟢" if porcentaje < 5 else "🟡" if porcentaje < 10 else "🔴"
        st.metric(
            label="% Riesgo", 
            value=f"{porcentaje:.1f}%",
            delta=f"{color_riesgo}",
            help="Porcentaje de células sospechosas respecto al total"
        )
    
    st.info("Resultado experimental: el porcentaje mostrado no constituye una evaluación clínica.")
    st.warning(resumen_resultado_experimental(resultados), icon="🔎")
    
    # Métricas de calidad de imagen
    if metricas_calidad.get('advertencias'):
        with st.expander("⚠️ Advertencias de Calidad de Imagen", expanded=(seccion != "metricas")):
            for adv in metricas_calidad['advertencias']:
                st.warning(adv)
    
    with st.expander("📈 Métricas de Calidad de Imagen", expanded=(seccion == "metricas")):
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        with col_q1:
            st.metric("Contraste", f"{metricas_calidad['contraste']:.1f}")
        with col_q2:
            st.metric("Brillo Promedio", f"{metricas_calidad['brillo_promedio']:.1f}")
        with col_q3:
            st.metric("Saturación", f"{metricas_calidad['saturacion']:.1f}%")
        with col_q4:
            estado = "✅ Aceptable" if metricas_calidad['es_aceptable'] else "❌ No Aceptable"
            st.metric("Estado", estado)
    
    st.markdown("---")
    
    # ====================================================================
    # SECCIÓN DE VISUALIZACIÓN
    # ====================================================================
    st.markdown("### 🖼️ Comparativa Visual")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Análisis Final", 
        "🔬 Filtro DoG", 
        "⚙️ Preprocesamiento",
        "📷 Original",
        "🎨 HSV / Separación",
        "📋 Criterios de Clasificación"
    ])
    
    with tab1:
        st.image(
            img_resultado, 
            channels="BGR", 
            caption="Detección y Clasificación (Verde=Normal | Rojo=Sospechoso)", 
            use_container_width=True
        )
        
        if resultados['total_celulas'] > 0:
            col_a, col_b = st.columns(2)
            with col_a:
                st.info(f"✅ **{resultados['normales']}** células normales detectadas")
            with col_b:
                st.error(f"⚠️ **{resultados['sospechosas']}** células sospechosas detectadas")
    
    with tab2:
        st.image(
            imagen_dog, 
            caption=f"Diferencia de Gaussiana (σ1={params_procesamiento['sigma1']}, σ2={params_procesamiento['sigma2']})", 
            use_container_width=True,
            clamp=True
        )
        
        st.info(f"""
        💡 **Cómo funciona el filtro DoG:**
        - Resalta bordes y estructuras de tamaño específico
        - Rango de detección: ~{int((params_procesamiento['sigma2']-params_procesamiento['sigma1'])*3)} píxeles
        - Ajusta σ1 y σ2 para optimizar detección
        """)
        
        # Mostrar componentes del DoG
        with st.expander("🔍 Ver componentes del DoG (G1, G2)"):
            componentes = visualizar_filtros_gauss(imagen_gris, params_procesamiento['sigma1'], params_procesamiento['sigma2'])
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.image(componentes['g1'], caption="G1 - Gaussiano σ1 (Detalle fino)", use_container_width=True)
            with col_g2:
                st.image(componentes['g2'], caption="G2 - Gaussiano σ2 (Estructura general)", use_container_width=True)
    
    with tab3:
        st.image(
            imagen_gris, 
            caption=f"Escala de Grises {'+ CLAHE' if params_procesamiento['usar_clahe'] else ''} {'+ Reducción de Ruido' if params_procesamiento['reducir_ruido'] else ''}", 
            use_container_width=True
        )
        
        status_prep = []
        if params_procesamiento['usar_clahe']:
            status_prep.append("✅ Contraste mejorado (CLAHE)")
        else:
            status_prep.append("❌ Sin mejora de contraste")
        
        if params_procesamiento['reducir_ruido']:
            status_prep.append("✅ Reducción de ruido activa")
        else:
            status_prep.append("❌ Sin reducción de ruido")
        
        if params_procesamiento['usar_hsv']:
            status_prep.append(f"✅ Segmentación HSV ({params_procesamiento['metodo_hsv']}, umbral={params_procesamiento['umbral_hsv']})")
        
        st.write("\n".join(status_prep))
    
    with tab4:
        st.image(
            imagen_original, 
            channels="BGR", 
            caption="Imagen Original sin Procesar", 
            use_container_width=True
        )
        
        # Información de la imagen
        alto, ancho = imagen_original.shape[:2]
        st.info(f"📐 Dimensiones: {ancho} × {alto} píxeles")
    
    with tab5:
        if params_procesamiento['usar_hsv']:
            # Mostrar máscara HSV
            mask_hsv = segmentar_por_hsv(imagen_original, umbral_sat=params_procesamiento['umbral_hsv'], umbral_val=params_procesamiento['umbral_hsv'], metodo=params_procesamiento['metodo_hsv'])
            st.image(mask_hsv, caption=f"Máscara HSV ({params_procesamiento['metodo_hsv']}, umbral={params_procesamiento['umbral_hsv']})", use_container_width=True)
            
            # Imagen con máscara aplicada
            imagen_hsv_aplicada = cv2.bitwise_and(imagen_original, imagen_original, mask=mask_hsv)
            st.image(imagen_hsv_aplicada, channels="BGR", caption="Imagen con máscara HSV aplicada", use_container_width=True)
        else:
            st.info("Activa 'Segmentación HSV' en la barra lateral para ver esta pestaña")
        
        if params_procesamiento['metodo_separacion'] != "none":
            st.markdown("---")
            st.markdown("#### Separación de Núcleos")
            if params_procesamiento['metodo_separacion'] == "watershed":
                st.info("Método: Watershed (Transformada de distancia)")
            elif params_procesamiento['metodo_separacion'] == "maximos_locales":
                st.info("Método: Máximos locales (picos DoG)")
            
            # Mostrar imagen con contornos de separación
            if resultados['total_celulas'] > 0:
                st.image(
                    img_deteccion, 
                    channels="BGR", 
                    caption=f"Detección con {params_procesamiento['metodo_separacion']}", 
                    use_container_width=True
                )
        else:
            if not params_procesamiento['usar_hsv']:
                st.info("Activa 'Segmentación HSV' o 'Separación de Núcleos' en la barra lateral para ver esta pestaña")
    
    with tab6:
        st.markdown("#### Reglas de Clasificación Activas")
        
        reglas = obtener_reglas_clasificacion(params_procesamiento['polaridad'])
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("Área Mínima", f"{reglas['area_minima_nucleo']} px²")
            st.metric("Área Promedio Normal", f"{reglas['area_promedio_nucleo_normal']} px²")
            st.metric("Factor de Riesgo", f"{reglas['factor_riesgo']}x")
        with col_r2:
            st.metric("Área Máxima", f"{reglas['area_maxima_nucleo']} px²")
            st.metric("Umbral Sospechoso", f"{reglas['umbral_sospechoso']:.1f} px²")
            st.metric("Margen Frontera", f"±{int(MARGEN_FRONTERA*100)}%")
        
        st.markdown(f"""
        **Zona Frontera:** {reglas['limite_frontera_inferior']:.1f} - {reglas['limite_frontera_superior']:.1f} px²
        
        **Regla:** Núcleos con área ≥ {reglas['umbral_sospechoso']:.1f} px² → **Sospechosos**
        
        **Polaridad:** {params_procesamiento['polaridad']}
        """)
        
        # Mostrar criterios de clasificación por célula
        if resultados.get('criterios_clasificacion'):
            st.markdown("#### Detalle por Célula")
            criterios_df = []
            for i, c in enumerate(resultados['criterios_clasificacion']):
                criterios_df.append({
                    "Célula": i + 1,
                    "Área (px²)": f"{c.get('area', 0):.1f}",
                    "Clasificación": c.get('clasificacion', 'N/A'),
                    "Frontera": "⚠️ Sí" if c.get('es_frontera', False) else "No",
                    "Motivo": c.get('motivo', 'N/A')
                })
            
            if criterios_df:
                st.dataframe(criterios_df, use_container_width=True, hide_index=True)
            else:
                st.info("No hay criterios de clasificación disponibles")
        else:
            st.info("No hay criterios de clasificación disponibles para esta ejecución")
    
    # ====================================================================
    # SECCIÓN DE DATOS DETALLADOS
    # ====================================================================
    with st.expander("📊 Ver Estadísticas Detalladas"):
        if resultados['areas']:
            st.markdown("#### Distribución de Áreas Celulares")
            
            areas_np = np.array(resultados['areas'])
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Área Mínima", f"{np.min(areas_np):.1f} px²")
            with col_stat2:
                st.metric("Área Promedio", f"{np.mean(areas_np):.1f} px²")
            with col_stat3:
                st.metric("Área Máxima", f"{np.max(areas_np):.1f} px²")
            
            # Gráfico de distribución
            st.bar_chart(areas_np)
            
            # Umbral de clasificación
            from src.analysis import AREA_PROMEDIO_NUCLEO_NORMAL, FACTOR_RIESGO
            umbral = AREA_PROMEDIO_NUCLEO_NORMAL * FACTOR_RIESGO
            
            st.markdown(f"""
            **Parámetros de Clasificación:**
            - Área promedio normal: {AREA_PROMEDIO_NUCLEO_NORMAL} px²
            - Factor de riesgo: {FACTOR_RIESGO}x
            - **Umbral de sospecha: {umbral:.1f} px²**
            """)
        else:
            st.info("No se detectaron células para mostrar estadísticas.")
    
    # ====================================================================
    # SECCIÓN DE DESCARGA
    # ====================================================================
    with st.expander("💾 Descargar Resultados", expanded=(seccion == "exportar")):
        st.markdown("#### Exportar Imagen Procesada")
        
        # Convertir a bytes para descarga
        import io
        _, buffer = cv2.imencode('.png', img_resultado)
        bytes_data = buffer.tobytes()
        
        st.download_button(
            label="📥 Descargar Panel de Análisis (PNG)",
            data=bytes_data,
            file_name=f"citocounter_resultado_{ruta_imagen.name}",
            mime="image/png"
        )
        
        st.markdown("#### Exportar Datos")
        
        # CSV
        csv_data = generar_csv_resultados(
            resultados,
            params_procesamiento['sigma1'],
            params_procesamiento['sigma2'],
            params_procesamiento['usar_clahe'],
            params_procesamiento['reducir_ruido'],
        )
        st.download_button(
            label="📥 Descargar Datos (CSV)",
            data=csv_data,
            file_name=f"citocounter_datos_{ruta_imagen.name.split('.')[0]}.csv",
            mime="text/csv"
        )
        
        # JSON completo con todos los metadatos
        json_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.1",
                "archivo_original": ruta_imagen.name,
                "id_anonimizado": obtener_id_sin_identificar(ruta_imagen.name)
            },
            "parametros": {
                "sigma1": params_procesamiento['sigma1'],
                "sigma2": params_procesamiento['sigma2'],
                "polaridad": params_procesamiento['polaridad'],
                "usar_clahe": params_procesamiento['usar_clahe'],
                "modo_clahe": params_procesamiento['modo_clahe'],
                "reducir_ruido": params_procesamiento['reducir_ruido'],
                "nivel_ruido": params_procesamiento['nivel_ruido'],
                "usar_hsv": params_procesamiento['usar_hsv'],
                "metodo_hsv": params_procesamiento['metodo_hsv'],
                "umbral_hsv": params_procesamiento['umbral_hsv'],
                "metodo_separacion": params_procesamiento['metodo_separacion'],
                "mostrar_contornos": params_procesamiento['mostrar_contornos'],
                "mostrar_areas": params_procesamiento['mostrar_areas']
            },
            "reglas_clasificacion": obtener_reglas_clasificacion(params_procesamiento['polaridad']),
            "metricas_calidad_imagen": metricas_calidad,
            "resultados": {
                "total_celulas": resultados['total_celulas'],
                "normales": resultados['normales'],
                "sospechosas": resultados['sospechosas'],
                "frontera": resultados.get('frontera', 0),
                "porcentaje_riesgo": resultados['porcentaje_riesgo'],
                "areas": resultados.get('areas', []),
                "criterios_clasificacion": resultados.get('criterios_clasificacion', [])
            }
        }
        
        st.download_button(
            label="📥 Descargar Datos Completos (JSON)",
            data=json.dumps(json_data, indent=2, ensure_ascii=False),
            file_name=f"citocounter_completo_{ruta_imagen.name.split('.')[0]}.json",
            mime="application/json"
        )
    
    # Detener aquí para no caer en el procesamiento en lote
    st.stop()

else:
    # PROCESAMIENTO EN LOTE
    st.markdown("## 📦 Resultados del Procesamiento en Lote")
    
    # Barra de progreso
    if 'mostrar_progreso' in locals() and mostrar_progreso:
        progress_bar = st.progress(0)
        status_text = st.empty()
    else:
        progress_bar = None
        status_text = None
    
    resultados_lote = []
    
    for idx, ruta_imagen in enumerate(imagenes_seleccionadas):
        if progress_bar:
            progress_bar.progress((idx) / len(imagenes_seleccionadas))
            status_text.text(f"Procesando {idx+1}/{len(imagenes_seleccionadas)}: {ruta_imagen.name}")
        
        resultado = procesar_imagen_individual(ruta_imagen, params_procesamiento)
        resultados_lote.append(resultado)
    
    if progress_bar:
        progress_bar.progress(1.0)
        status_text.text("✅ Procesamiento completado")
    
    # Limpiar archivos temporales si vienen de upload
    if fuente_imagenes == "upload" and 'rutas_temporales' in locals():
        for ruta_temp in rutas_temporales:
            try:
                if os.path.exists(ruta_temp):
                    os.unlink(ruta_temp)
            except:
                pass
    
    # ====================================================================
    # RESUMEN CONSOLIDADO LOTE
    # ====================================================================
    exitosos = [r for r in resultados_lote if r['exito']]
    fallidos = [r for r in resultados_lote if not r['exito']]
    
    st.markdown("### 📊 Resumen Consolidado")
    
    col_res1, col_res2, col_res3, col_res4, col_res5 = st.columns(5)
    with col_res1:
        st.metric("Total Procesadas", len(resultados_lote))
    with col_res2:
        st.metric("✅ Exitosas", len(exitosos))
    with col_res3:
        st.metric("❌ Fallidas", len(fallidos))
    with col_res4:
        total_celulas = sum(r['resultados']['total_celulas'] for r in exitosos)
        st.metric("Total Células", total_celulas)
    with col_res5:
        total_sospechosas = sum(r['resultados']['sospechosas'] for r in exitosos)
        pct_riesgo = (total_sospechosas / total_celulas * 100) if total_celulas > 0 else 0
        st.metric("% Riesgo Global", f"{pct_riesgo:.1f}%")
    
    if fallidos:
        with st.expander("❌ Errores en procesamiento", expanded=True):
            for f in fallidos:
                st.error(f"{f['archivo']}: {f['error']}")
    
    # Tabla de resultados
    if exitosos:
        st.markdown("### 📋 Detalle por Imagen")
        
        datos_tabla = []
        for r in exitosos:
            res = r['resultados']
            datos_tabla.append({
                "Archivo": r['archivo'],
                "Células": res['total_celulas'],
                "Normales": res['normales'],
                "Sospechosas": res['sospechosas'],
                "Frontera": res.get('frontera', 0),
                "% Riesgo": f"{res['porcentaje_riesgo']:.1f}%",
                "Calidad": "✅" if r['metricas_calidad']['es_aceptable'] else "⚠️"
            })
        
        st.dataframe(datos_tabla, use_container_width=True, hide_index=True)
        
        # Gráfico de distribución de riesgo
        st.markdown("### 📈 Distribución de Riesgo por Imagen")
        import pandas as pd
        df_riesgo = pd.DataFrame([
            {"Imagen": r['archivo'][:20] + "...", "Riesgo %": r['resultados']['porcentaje_riesgo']}
            for r in exitosos
        ])
        st.bar_chart(df_riesgo.set_index("Imagen"))
        
        # Descargas en lote
        st.markdown("### 💾 Descargar Resultados del Lote")
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_lote = generar_csv_lote(resultados_lote, params_procesamiento)
            st.download_button(
                label="📥 Descargar CSV Consolidado",
                data=csv_lote,
                file_name=f"citocounter_lote_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col_dl2:
            # JSON consolidado
            json_lote = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.1",
                    "modo": "lote",
                    "total_imagenes": len(resultados_lote),
                    "exitosas": len(exitosos),
                    "parametros": params_procesamiento
                },
                "resultados": [
                    {
                        "archivo": r['archivo'],
                        "exito": r['exito'],
                        "total_celulas": r['resultados']['total_celulas'] if r['exito'] else 0,
                        "normales": r['resultados']['normales'] if r['exito'] else 0,
                        "sospechosas": r['resultados']['sospechosas'] if r['exito'] else 0,
                        "porcentaje_riesgo": r['resultados']['porcentaje_riesgo'] if r['exito'] else 0,
                        "error": r.get('error', None)
                    }
                    for r in resultados_lote
                ]
            }
            st.download_button(
                label="📥 Descargar JSON Consolidado",
                data=json.dumps(json_lote, indent=2, ensure_ascii=False),
                file_name=f"citocounter_lote_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Si hay exitosos, mostrar la primera imagen en detalle
    if exitosos:
        st.markdown("---")
        st.markdown("### 🔍 Vista Detallada de la Primera Imagen Exitosa")
        
        primer_exitoso = exitosos[0]
        resultados = primer_exitoso['resultados']
        metricas_calidad = primer_exitoso['metricas_calidad']
        img_resultado = primer_exitoso['img_resultado']
        img_deteccion = primer_exitoso['img_deteccion']
        imagen_original = primer_exitoso['imagen_original']
        imagen_gris = primer_exitoso['imagen_gris']
        imagen_dog = primer_exitoso['imagen_dog']
        
        st.caption(f"Mostrando: {primer_exitoso['archivo']} | Usa el selector arriba para cambiar de imagen")
        
        # ====================================================================
        # SECCIÓN DE MÉTRICAS
        # ====================================================================
        st.markdown("### 📊 Resultados del Análisis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Células", 
                value=resultados['total_celulas'],
                help="Número total de núcleos detectados"
            )
        
        with col2:
            st.metric(
                label="Normales", 
                value=resultados['normales'],
                delta=None,
                help="Células con área < 3x promedio"
            )
        
        with col3:
            st.metric(
                label="Sospechosas", 
                value=resultados['sospechosas'],
                delta=f"{resultados['sospechosas']} detectadas",
                delta_color="inverse",
                help="Células con área ≥ 3x promedio (Regla del 3x)"
            )
        
        with col4:
            porcentaje = resultados['porcentaje_riesgo']
            color_riesgo = "🟢" if porcentaje < 5 else "🟡" if porcentaje < 10 else "🔴"
            st.metric(
                label="% Riesgo", 
                value=f"{porcentaje:.1f}%",
                delta=f"{color_riesgo}",
                help="Porcentaje de células sospechosas respecto al total"
            )
        
        st.info("Resultado experimental: el porcentaje mostrado no constituye una evaluación clínica.")
        st.warning(resumen_resultado_experimental(resultados), icon="🔎")
        
        # Métricas de calidad de imagen
        if metricas_calidad.get('advertencias'):
            with st.expander("⚠️ Advertencias de Calidad de Imagen", expanded=True):
                for adv in metricas_calidad['advertencias']:
                    st.warning(adv)
        
        with st.expander("📈 Métricas de Calidad de Imagen", expanded=False):
            col_q1, col_q2, col_q3, col_q4 = st.columns(4)
            with col_q1:
                st.metric("Contraste", f"{metricas_calidad['contraste']:.1f}")
            with col_q2:
                st.metric("Brillo Promedio", f"{metricas_calidad['brillo_promedio']:.1f}")
            with col_q3:
                st.metric("Saturación", f"{metricas_calidad['saturacion']:.1f}%")
            with col_q4:
                estado = "✅ Aceptable" if metricas_calidad['es_aceptable'] else "❌ No Aceptable"
                st.metric("Estado", estado)
        
        st.markdown("---")
        
        # ====================================================================
        # SECCIÓN DE VISUALIZACIÓN
        # ====================================================================
        st.markdown("### 🖼️ Comparativa Visual")
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🎯 Análisis Final", 
            "🔬 Filtro DoG", 
            "⚙️ Preprocesamiento",
            "📷 Original",
            "🎨 HSV / Separación",
            "📋 Criterios de Clasificación"
        ])
        
        with tab1:
            st.image(
                img_resultado, 
                channels="BGR", 
                caption="Detección y Clasificación (Verde=Normal | Rojo=Sospechoso)", 
                use_container_width=True
            )
            
            if resultados['total_celulas'] > 0:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.info(f"✅ **{resultados['normales']}** células normales detectadas")
                with col_b:
                    st.error(f"⚠️ **{resultados['sospechosas']}** células sospechosas detectadas")
        
        with tab2:
            st.image(
                imagen_dog, 
                caption=f"Diferencia de Gaussiana (σ1={sigma1}, σ2={sigma2})", 
                use_container_width=True,
                clamp=True
            )
            
            st.info(f"""
            💡 **Cómo funciona el filtro DoG:**
            - Resalta bordes y estructuras de tamaño específico
            - Rango de detección: ~{int((sigma2-sigma1)*3)} píxeles
            - Ajusta σ1 y σ2 para optimizar detección
            """)
            
            # Mostrar componentes del DoG
            with st.expander("🔍 Ver componentes del DoG (G1, G2)"):
                componentes = visualizar_filtros_gauss(imagen_gris, sigma1, sigma2)
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.image(componentes['g1'], caption="G1 - Gaussiano σ1 (Detalle fino)", use_container_width=True)
                with col_g2:
                    st.image(componentes['g2'], caption="G2 - Gaussiano σ2 (Estructura general)", use_container_width=True)
        
        with tab3:
            st.image(
                imagen_gris, 
                caption=f"Escala de Grises {'+ CLAHE' if usar_clahe else ''} {'+ Reducción de Ruido' if reducir_ruido else ''}", 
                use_container_width=True
            )
            
            status_prep = []
            if usar_clahe:
                status_prep.append("✅ Contraste mejorado (CLAHE)")
            else:
                status_prep.append("❌ Sin mejora de contraste")
            
            if reducir_ruido:
                status_prep.append("✅ Reducción de ruido activa")
            else:
                status_prep.append("❌ Sin reducción de ruido")
            
            if usar_hsv:
                status_prep.append(f"✅ Segmentación HSV ({metodo_hsv}, umbral={umbral_hsv})")
            
            st.write("\n".join(status_prep))
        
        with tab4:
            st.image(
                imagen_original, 
                channels="BGR", 
                caption="Imagen Original sin Procesar", 
                use_container_width=True
            )
            
            # Información de la imagen
            alto, ancho = imagen_original.shape[:2]
            st.info(f"📐 Dimensiones: {ancho} × {alto} píxeles")
        
        with tab5:
            if usar_hsv:
                # Mostrar máscara HSV
                mask_hsv = segmentar_por_hsv(imagen_original, umbral_sat=umbral_hsv, umbral_val=umbral_hsv, metodo=metodo_hsv)
                st.image(mask_hsv, caption=f"Máscara HSV ({metodo_hsv}, umbral={umbral_hsv})", use_container_width=True)
                
                # Imagen con máscara aplicada
                imagen_hsv_aplicada = cv2.bitwise_and(imagen_original, imagen_original, mask=mask_hsv)
                st.image(imagen_hsv_aplicada, channels="BGR", caption="Imagen con máscara HSV aplicada", use_container_width=True)
            else:
                st.info("Activa 'Segmentación HSV' en la barra lateral para ver esta pestaña")
            
            if metodo_separacion != "none":
                st.markdown("---")
                st.markdown("#### Separación de Núcleos")
                if metodo_separacion == "watershed":
                    st.info("Método: Watershed (Transformada de distancia)")
                elif metodo_separacion == "maximos_locales":
                    st.info("Método: Máximos locales (picos DoG)")
                
                # Mostrar imagen con contornos de separación
                if resultados['total_celulas'] > 0:
                    st.image(
                        img_deteccion, 
                        channels="BGR", 
                        caption=f"Detección con {metodo_separacion}", 
                        use_container_width=True
                    )
            else:
                if not usar_hsv:
                    st.info("Activa 'Separación de Núcleos' en la barra lateral para ver esta pestaña")
        
        with tab6:
            st.markdown("#### Reglas de Clasificación Activas")
            
            reglas = obtener_reglas_clasificacion(polaridad)
            
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.metric("Área Mínima", f"{reglas['area_minima_nucleo']} px²")
                st.metric("Área Promedio Normal", f"{reglas['area_promedio_nucleo_normal']} px²")
                st.metric("Factor de Riesgo", f"{reglas['factor_riesgo']}x")
            with col_r2:
                st.metric("Área Máxima", f"{reglas['area_maxima_nucleo']} px²")
                st.metric("Umbral Sospechoso", f"{reglas['umbral_sospechoso']:.1f} px²")
                st.metric("Margen Frontera", f"±{int(MARGEN_FRONTERA*100)}%")
            
            st.markdown(f"""
            **Zona Frontera:** {reglas['limite_frontera_inferior']:.1f} - {reglas['limite_frontera_superior']:.1f} px²
            
            **Regla:** Núcleos con área ≥ {reglas['umbral_sospechoso']:.1f} px² → **Sospechosos**
            
            **Polaridad:** {polaridad}
            """)
            
            # Mostrar criterios de clasificación por célula
            if resultados.get('criterios_clasificacion'):
                st.markdown("#### Detalle por Célula")
                criterios_df = []
                for i, c in enumerate(resultados['criterios_clasificacion']):
                    criterios_df.append({
                        "Célula": i + 1,
                        "Área (px²)": f"{c.get('area', 0):.1f}",
                        "Clasificación": c.get('clasificacion', 'N/A'),
                        "Frontera": "⚠️ Sí" if c.get('es_frontera', False) else "No",
                        "Motivo": c.get('motivo', 'N/A')
                    })
                
                if criterios_df:
                    st.dataframe(criterios_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No hay criterios de clasificación disponibles")
            else:
                st.info("No hay criterios de clasificación disponibles para esta ejecución")
        
        # ====================================================================
        # SECCIÓN DE DATOS DETALLADOS
        # ====================================================================
        with st.expander("📊 Ver Estadísticas Detalladas"):
            if resultados['areas']:
                st.markdown("#### Distribución de Áreas Celulares")
                
                areas_np = np.array(resultados['areas'])
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Área Mínima", f"{np.min(areas_np):.1f} px²")
                with col_stat2:
                    st.metric("Área Promedio", f"{np.mean(areas_np):.1f} px²")
                with col_stat3:
                    st.metric("Área Máxima", f"{np.max(areas_np):.1f} px²")
                
                # Gráfico de distribución
                st.bar_chart(areas_np)
                
                # Umbral de clasificación
                from src.analysis import AREA_PROMEDIO_NUCLEO_NORMAL, FACTOR_RIESGO
                umbral = AREA_PROMEDIO_NUCLEO_NORMAL * FACTOR_RIESGO
                
                st.markdown(f"""
                **Parámetros de Clasificación:**
                - Área promedio normal: {AREA_PROMEDIO_NUCLEO_NORMAL} px²
                - Factor de riesgo: {FACTOR_RIESGO}x
                - **Umbral de sospecha: {umbral:.1f} px²**
                """)
            else:
                st.info("No se detectaron células para mostrar estadísticas.")
        
        # ====================================================================
        # SECCIÓN DE DESCARGA
        # ====================================================================
        with st.expander("💾 Descargar Resultados"):
            st.markdown("#### Exportar Imagen Procesada")
            
            # Convertir a bytes para descarga
            import io
            _, buffer = cv2.imencode('.png', img_resultado)
            bytes_data = buffer.tobytes()
            
            st.download_button(
                label="📥 Descargar Panel de Análisis (PNG)",
                data=bytes_data,
                file_name=f"citocounter_resultado_{ruta_imagen.name}",
                mime="image/png"
            )
            
            st.markdown("#### Exportar Datos")
            
            # CSV
            csv_data = generar_csv_resultados(
                resultados,
                params_procesamiento['sigma1'],
                params_procesamiento['sigma2'],
                params_procesamiento['usar_clahe'],
                params_procesamiento['reducir_ruido'],
            )
            st.download_button(
                label="📥 Descargar Datos (CSV)",
                data=csv_data,
                file_name=f"citocounter_datos_{ruta_imagen.name.split('.')[0]}.csv",
                mime="text/csv"
            )
            
            # JSON completo con todos los metadatos
            json_data = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.1",
                    "archivo_original": ruta_imagen.name,
                    "id_anonimizado": obtener_id_sin_identificar(ruta_imagen.name)
                },
                "parametros": {
                    "sigma1": params_procesamiento['sigma1'],
                    "sigma2": params_procesamiento['sigma2'],
                    "polaridad": params_procesamiento['polaridad'],
                    "usar_clahe": params_procesamiento['usar_clahe'],
                    "modo_clahe": params_procesamiento['modo_clahe'],
                    "reducir_ruido": params_procesamiento['reducir_ruido'],
                    "nivel_ruido": params_procesamiento['nivel_ruido'],
                    "usar_hsv": params_procesamiento['usar_hsv'],
                    "metodo_hsv": params_procesamiento['metodo_hsv'],
                    "umbral_hsv": umbral_hsv,
                    "metodo_separacion": metodo_separacion,
                    "mostrar_contornos": mostrar_contornos
                },
                "reglas_clasificacion": obtener_reglas_clasificacion(polaridad),
                "metricas_calidad_imagen": metricas_calidad,
                "resultados": {
                    "total_celulas": resultados['total_celulas'],
                    "normales": resultados['normales'],
                    "sospechosas": resultados['sospechosas'],
                    "frontera": resultados.get('frontera', 0),
                    "porcentaje_riesgo": resultados['porcentaje_riesgo'],
                    "areas": resultados.get('areas', []),
                    "criterios_clasificacion": resultados.get('criterios_clasificacion', [])
                }
            }
            
            st.download_button(
                label="📥 Descargar Datos Completos (JSON)",
                data=json.dumps(json_data, indent=2, ensure_ascii=False),
                file_name=f"citocounter_completo_{ruta_imagen.name.split('.')[0]}.json",
                mime="application/json"
            )

# ========================================================================
# PANTALLA DE BIENVENIDA (cuando no hay imágenes seleccionadas)
# ========================================================================
if 'imagenes_seleccionadas' not in locals() or not imagenes_seleccionadas:
    st.info("👆 **Selecciona una fuente de imágenes y carga/elige imágenes para comenzar el análisis**")
    
    st.markdown("### 🎯 ¿Cómo usar CitoCounter Dashboard?")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        **📋 Paso a Paso:**
        1. Elige la fuente: **Subir archivo(s)** o **Dataset del proyecto**
        2. Selecciona una o varias imágenes
        3. Ajusta los parámetros en la barra lateral
        4. Observa los resultados instantáneos
        5. Descarga los resultados si lo deseas
        
        **📦 Modo Lote:** Selecciona múltiples imágenes para procesarlas todas a la vez
        """)
    
    with col_info2:
        st.markdown("""
        **🔬 Formatos Aceptados:**
        - JPG / JPEG
        - PNG
        - TIF / TIFF
        
        **💡 Recomendaciones:**
        - Imágenes de buena calidad
        - Iluminación uniforme preferible
        - Resolución mínima: 500×500 px
        """)
    
    st.markdown("---")
    
    # Nuevas características
    with st.expander("✨ Nuevas Características v1.1"):
        st.markdown("""
        **🎨 Segmentación HSV (CITO-33):**
        - Resalta núcleos por color (saturación/valor)
        - Útil cuando el contraste de intensidad es bajo
        
        **🔬 Separación de Núcleos (CITO-32):**
        - Watershed: Transformada de distancia para núcleos en contacto
        - Máximos locales: Detección de picos en respuesta DoG
        
        **📊 Métricas de Calidad:**
        - Verificación automática de contraste, brillo, saturación
        - Advertencias para imágenes problemáticas
        
        **📋 Criterios de Clasificación Explicables:**
        - Detalle por célula: área, clasificación, zona frontera
        - Reglas ajustables por polaridad
        
        **💾 Exportación Completa:**
        - CSV: Resumen de resultados
        - JSON: Metadatos completos, parámetros, criterios por célula
        """)
    
    # Ejemplos de uso
    with st.expander("📸 Ver Ejemplos de Resultados"):
        st.markdown("""
        **Ejemplo de Análisis:**
        
        | Imagen | Total Células | Sospechosas | % Riesgo | Interpretación |
        |--------|---------------|-------------|----------|----------------|
        | EDF001.png | 261 | 36 | 13.8% | Riesgo elevado ⚠️ |
        | EDF004.png | 114 | 9 | 7.9% | Bajo riesgo ✅ |
        | EDF005.png | 272 | 25 | 9.2% | Riesgo moderado 🟡 |
        
        *Datos obtenidos con σ1=3.0, σ2=5.0*
        """)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p><strong>CitoCounter Proto v1.1 Web Dashboard</strong></p>
        <p>Desarrollado para análisis automatizado de citologías cervicales</p>
        <p>🔬 Algoritmo DoG + Regla del 3x | 📊 Interfaz Interactiva</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# FOOTER
# ============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; font-size: 0.8em; color: gray;'>
    <p>CitoCounter Proto v1.1</p>
    <p>Web Dashboard Interactivo</p>
    <p>🔬 2024</p>
</div>
""", unsafe_allow_html=True)
