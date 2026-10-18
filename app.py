"""
app.py - CitoCounter Proto Web Dashboard

Web App interactiva usando Streamlit para análisis celular en tiempo real.

EJECUCIÓN:
    streamlit run app.py

CARACTERÍSTICAS:
- Calibración de parámetros en tiempo real con sliders
- Panel de ajustes lateral que se muestra/oculta con un botón
- Visualización comparativa instantánea
- Métricas clave en dashboard
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
import csv
from io import StringIO
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

# Carpeta donde están las imágenes del dataset (ruta absoluta en esta PC).
# Se usa raw string (r"...") para que Python no interprete las "\" de Windows.
RUTA_DATASET = Path(
    r"C:\Users\zowya\OneDrive\Escritorio\zowy\TALLER 1\Software\CitoCounter_Proto\data\raw"
)
# Solo si la ruta anterior no existe (proyecto movido o ejecutado en otra PC)
# se intenta con la carpeta data/raw que esté junto a este archivo.
RUTA_DATASET_RESPALDO = Path(__file__).resolve().parent / "data" / "raw"

EXTENSIONES_IMAGEN = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}

# Valores por defecto de TODOS los ajustes del panel.
# Se guardan en st.session_state con estas mismas claves, así sobreviven
# aunque el panel esté oculto.
CONFIG_DEFAULT = {
    "fuente_imagenes": "upload",
    "sigma1": 7.0,
    "sigma2": 8.0,
    "polaridad": "nucleos-claros",
    "usar_clahe": True,
    "modo_clahe": "clahe",
    "reducir_ruido": False,
    "nivel_ruido": "medio",
    "usar_hsv": False,
    "metodo_hsv": "saturation",
    "umbral_hsv": 100,
    "metodo_separacion": "none",
    "mostrar_contornos": True,
    "mostrar_areas": False,
}

# ============================================================================
# DESIGN SYSTEM - Medical Health Dashboard
# ============================================================================
DESIGN_SYSTEM_CSS = """
<style>
:root {
  --color-bg-main-light: #F8FAFC;
  --color-bg-main-warm: #FAF8F5;
  --color-bg-card-light: #FFFFFF;
  --color-brand-primary: #2A55E5;
  --color-brand-primary-light: #E8EDF5;
  --color-text-primary-dark: #1E293B;
  --color-text-secondary-dark: #64748B;
  --color-semantic-success: #10B981;
  --color-semantic-success-bg: #ECFDF5;
  --color-semantic-warning: #F59E0B;
  --color-semantic-danger: #EF4444;
  --color-semantic-danger-bg: #FEE2E2;
  --shadow-card: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-floating: 0 4px 12px 0 rgba(0, 0, 0, 0.15);
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-pill: 9999px;
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  --font-size-xs: 10px;
  --font-size-sm: 12px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 20px;
  --font-size-2xl: 28px;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
}

html, body, [data-testid="stAppViewContainer"] {
    font-family: var(--font-family) !important;
    background-color: var(--color-bg-main-light) !important;
    color: var(--color-text-primary-dark) !important;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stHeader"] { background: transparent !important; }

/* CARDS */
.medical-card {
    background: var(--color-bg-card-light);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-card);
    padding: var(--spacing-md);
    transition: all 0.2s ease;
    border: 1px solid rgba(0, 0, 0, 0.03);
}
.medical-card:hover { box-shadow: var(--shadow-floating); }
.medical-card-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: var(--spacing-sm); padding-bottom: var(--spacing-sm);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}
.medical-card-title {
    font-size: var(--font-size-lg); font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary-dark);
    display: flex; align-items: center; gap: var(--spacing-sm);
}
.medical-card-icon {
    width: 40px; height: 40px; border-radius: var(--radius-md);
    display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.medical-card-icon.primary { background: var(--color-brand-primary-light); color: var(--color-brand-primary); }
.medical-card-content { color: var(--color-text-secondary-dark); font-size: var(--font-size-md); line-height: 1.6; }

/* METRIC CARDS (HTML) */
.metric-card {
    background: var(--color-bg-card-light);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-card);
    padding: var(--spacing-md);
    border: 1px solid rgba(0, 0, 0, 0.03);
}
.metric-value { font-size: var(--font-size-2xl); font-weight: var(--font-weight-bold); line-height: 1.2; }
.metric-label {
    font-size: var(--font-size-sm); font-weight: var(--font-weight-medium);
    color: var(--color-text-secondary-dark); margin-top: var(--spacing-xs);
    text-transform: uppercase; letter-spacing: 0.5px;
}

/* BADGES */
.badge {
    display: inline-flex; align-items: center; padding: 4px 12px;
    border-radius: var(--radius-pill); font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
}
.badge.info { background: var(--color-brand-primary-light); color: var(--color-brand-primary); }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: var(--spacing-xs); background: transparent;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: var(--radius-md) !important;
    padding: var(--spacing-sm) var(--spacing-md) !important;
    font-size: var(--font-size-sm) !important;
    font-weight: var(--font-weight-medium) !important;
    color: var(--color-text-secondary-dark) !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: var(--color-brand-primary-light) !important;
    color: var(--color-brand-primary) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--color-brand-primary) !important;
    color: white !important;
}

/* METRICS (nativas) */
[data-testid="stMetric"] {
    background: var(--color-bg-card-light) !important;
    border-radius: var(--radius-lg) !important;
    padding: var(--spacing-md) !important;
    border: 1px solid rgba(0, 0, 0, 0.03) !important;
    box-shadow: var(--shadow-card) !important;
}
[data-testid="stMetricLabel"] { text-transform: uppercase; letter-spacing: 0.5px; }

/* BOTONES */
.stButton > button[kind="primary"], .stDownloadButton > button {
    background: var(--color-brand-primary) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-weight: var(--font-weight-semibold) !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {
    background: #1E40C0 !important;
    box-shadow: var(--shadow-floating) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--color-bg-card-light) !important;
    color: var(--color-brand-primary) !important;
    border: 1px solid var(--color-brand-primary) !important;
    border-radius: var(--radius-md) !important;
    font-weight: var(--font-weight-semibold) !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--color-brand-primary-light) !important;
    box-shadow: var(--shadow-card) !important;
}

.stAlert { border-radius: var(--radius-md) !important; }

[data-testid="stDataFrame"] {
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
}

[data-testid="stFileUploader"] {
    background: var(--color-bg-card-light) !important;
    border: 2px dashed rgba(42, 85, 229, 0.3) !important;
    border-radius: var(--radius-lg) !important;
    padding: var(--spacing-lg) !important;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-up { animation: fadeInUp 0.4s ease-out forwards; }

@media (max-width: 768px) {
    .metric-value { font-size: var(--font-size-xl) !important; }
    .medical-card { padding: var(--spacing-sm) !important; }
}
</style>
"""

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="CitoCounter Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"  # El panel de ajustes ya no usa st.sidebar
)

# ============================================================================
# ESTADO DE SESIÓN
# ============================================================================
for _clave, _valor in CONFIG_DEFAULT.items():
    st.session_state.setdefault(_clave, _valor)
st.session_state.setdefault("panel_visible", True)
if "seccion" not in st.session_state:
    st.session_state.seccion = st.query_params.get("section", "dashboard")


def _ir_a_seccion(destino):
    st.session_state.seccion = destino
    if destino == "config":
        st.session_state.panel_visible = True
    elif destino in ("upload", "dataset"):
        st.session_state.fuente_imagenes = destino


def _toggle_panel():
    st.session_state.panel_visible = not st.session_state.panel_visible


def _guardar_config(clave):
    """Copia el valor del widget a la clave 'permanente' de session_state."""
    st.session_state[clave] = st.session_state[f"_w_{clave}"]


def _widget(clave):
    """
    Prepara un widget del panel. Streamlit borra el estado de los widgets que
    no se dibujan, así que el valor real vive en st.session_state[clave] y el
    widget se restaura desde ahí cada vez que el panel se vuelve a mostrar.
    """
    st.session_state[f"_w_{clave}"] = st.session_state[clave]
    return {"key": f"_w_{clave}", "on_change": _guardar_config, "args": (clave,)}


def leer_config():
    """Devuelve la configuración vigente (haya o no panel visible)."""
    cfg = {clave: st.session_state[clave] for clave in CONFIG_DEFAULT}
    if not cfg["usar_clahe"]:
        cfg["modo_clahe"] = "clahe"
    if not cfg["reducir_ruido"]:
        cfg["nivel_ruido"] = "medio"
    if not cfg["usar_hsv"]:
        cfg["metodo_hsv"] = "saturation"
        cfg["umbral_hsv"] = 100
    return cfg


st.markdown(DESIGN_SYSTEM_CSS, unsafe_allow_html=True)

seccion = st.session_state.seccion

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="medical-card" style="margin-bottom: 24px;">
    <div class="medical-card-header">
        <div class="medical-card-title">
            <span class="medical-card-icon primary">🔬</span>
            <span>CitoCounter Dashboard</span>
        </div>
        <span class="badge info">v1.1 Web</span>
    </div>
    <div class="medical-card-content">
        <p style="margin: 0;">
            Análisis experimental de núcleos con filtro DoG y regla de área de referencia.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.warning(AVISO_USO_EXPERIMENTAL, icon="⚠️")

# ============================================================================
# QUICK ACTIONS BAR
# ============================================================================
acciones = [
    ("📊 Dashboard", "dashboard"),
    ("⚙️ Configuración", "config"),
    ("📤 Subir Imagen", "upload"),
    ("📁 Dataset", "dataset"),
    ("📊 Historial", "historial"),
    ("📈 Métricas", "metricas"),
    ("📥 Exportar", "exportar"),
]

cols_acciones_principales = st.columns(4)
for col, (etiqueta, destino) in zip(cols_acciones_principales, acciones[:4]):
    with col:
        st.button(
            etiqueta,
            key=f"nav_{destino}",
            on_click=_ir_a_seccion,
            args=(destino,),
            type="primary" if seccion == destino else "secondary",
            use_container_width=True,
        )

cols_acciones_secundarias = st.columns(4)
for col, (etiqueta, destino) in zip(cols_acciones_secundarias[:3], acciones[4:]):
    with col:
        st.button(
            etiqueta,
            key=f"nav_{destino}",
            on_click=_ir_a_seccion,
            args=(destino,),
            type="primary" if seccion == destino else "secondary",
            use_container_width=True,
        )

with cols_acciones_secundarias[-1]:
    st.button(
        "◀ Ocultar panel" if st.session_state.panel_visible else "▶ Mostrar panel",
        key="toggle_panel",
        on_click=_toggle_panel,
        type="secondary",
        use_container_width=True,
    )

# ============================================================================
# QUICK STATS CARDS ROW
# ============================================================================
if seccion in ("historial", "dashboard"):
    try:
        historial = cargar_historial()
        if historial:
            resumen_historial = agregar_historial(historial)
            st.markdown("""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 16px 0 24px 0;">
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
                    <div class="metric-label">Sospechosas promedio (%)</div>
                </div>
            </div>
            """.format(
                resumen_historial["total_ejecuciones"],
                resumen_historial["imagenes_unicas"],
                resumen_historial["total_celulas"],
                f"{resumen_historial['promedio_riesgo']:.1f}"
            ), unsafe_allow_html=True)
    except Exception as e:
        st.caption(f"No se pudo cargar el historial: {e}")


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================
def obtener_ruta_dataset():
    """Devuelve la carpeta del dataset: primero RUTA_DATASET, luego el respaldo."""
    for ruta in (RUTA_DATASET, RUTA_DATASET_RESPALDO):
        if ruta.is_dir():
            return ruta
    return RUTA_DATASET  # ninguna existe: se devuelve la principal para mostrarla en el aviso


def escanear_dataset(ruta_base):
    """
    Lista las imágenes de la carpeta del dataset (sin entrar a subcarpetas).
    No usa caché a propósito: así las imágenes nuevas aparecen sin reiniciar la app.
    """
    ruta = Path(ruta_base)
    if not ruta.is_dir():
        return []

    return sorted(
        (p for p in ruta.iterdir()
         if p.is_file() and p.suffix.lower() in EXTENSIONES_IMAGEN),
        key=lambda p: p.name.lower()
    )


def procesar_imagen_individual(ruta_imagen, params):
    """Procesa una sola imagen y retorna resultados."""
    try:
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

        metricas_calidad = verificar_calidad_imagen(imagen_gris)
        imagen_dog = aplicar_filtro_dog(imagen_gris, params['sigma1'], params['sigma2'])

        metodo_sep = None if params['metodo_separacion'] == "none" else params['metodo_separacion']
        resultados = analizar_nucleos(
            imagen_dog,
            imagen_original,
            polaridad=params['polaridad'],
            metodo_separacion=metodo_sep
        )

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
    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        "Archivo", "Total_Celulas", "Normales", "Sospechosas",
        "Frontera", "Porcentaje_Sospechosas", "Sigma1", "Sigma2",
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
            writer.writerow([r['archivo'], "ERROR"] + [""] * 19)

    return buffer.getvalue()


def limpiar_temporales(rutas):
    for ruta_temp in rutas:
        try:
            if os.path.exists(ruta_temp):
                os.unlink(ruta_temp)
        except OSError:
            pass


def mostrar_bienvenida():
    st.markdown("### 🎯 ¿Cómo usar CitoCounter Dashboard?")

    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.markdown("""
        **📋 Paso a Paso:**
        1. Elige la fuente: **Subir archivo(s)** o **Dataset del proyecto**
        2. Selecciona una o varias imágenes
        3. Ajusta los parámetros en el panel de ajustes
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

    with st.expander("📸 Ver Ejemplos de Resultados"):
        st.markdown("""
        **Ejemplo de Análisis:**

        | Imagen | Total Células | Sospechosas | % Experimental | Interpretación |
        |--------|---------------|-------------|----------------|----------------|
        | EDF001.png | 261 | 36 | 13.8% | Requiere revisión experta |
        | EDF004.png | 114 | 9 | 7.9% | Requiere revisión experta |
        | EDF005.png | 272 | 25 | 9.2% | Requiere revisión experta |

        *Datos obtenidos con σ1=3.0, σ2=5.0*

        *Los ejemplos son experimentales y no constituyen diagnóstico médico.*
        """)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p><strong>CitoCounter Proto v1.1 Web Dashboard</strong></p>
        <p>Desarrollado para análisis automatizado de citologías cervicales</p>
        <p>🔬 Algoritmo DoG + Regla del 3x | 📊 Interfaz Interactiva</p>
    </div>
    """, unsafe_allow_html=True)


def mostrar_detalle(r, params, seccion_actual, expandir_calidad_por_defecto=False):
    """Muestra el análisis detallado de una imagen (usado en modo individual y lote)."""
    resultados = r['resultados']
    metricas_calidad = r['metricas_calidad']
    img_resultado = r['img_resultado']
    img_deteccion = r['img_deteccion']
    imagen_original = r['imagen_original']
    imagen_gris = r['imagen_gris']
    imagen_dog = r['imagen_dog']
    nombre_archivo = r['archivo']
    nombre_base = nombre_archivo.rsplit('.', 1)[0]

    # ---------------- MÉTRICAS ----------------
    st.markdown("### 📊 Resultados del Análisis")

    col1, col2, col3, col4, col5 = st.columns(5)

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
        st.metric(
            label="% Sospechosas",
            value=f"{porcentaje:.1f}%",
            help="Porcentaje experimental de células clasificadas como sospechosas"
        )

    st.info("Resultado experimental: el porcentaje mostrado no constituye una evaluación clínica.")
    st.warning(resumen_resultado_experimental(resultados), icon="🔎")

    if not metricas_calidad['es_aceptable']:
        st.error(
            "Calidad de imagen no aceptable: este resultado requiere revisión "
            "humana y no debe usarse para una interpretación clínica.",
            icon="⚠️",
        )

    if metricas_calidad.get('advertencias'):
        with st.expander(
            "⚠️ Advertencias de Calidad de Imagen",
            expanded=(seccion_actual != "metricas") or expandir_calidad_por_defecto
        ):
            for adv in metricas_calidad['advertencias']:
                st.warning(adv)

    with st.expander("📈 Métricas de Calidad de Imagen", expanded=(seccion_actual == "metricas")):
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

    # ---------------- VISUALIZACIÓN ----------------
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
            caption=f"Diferencia de Gaussiana (σ1={params['sigma1']}, σ2={params['sigma2']})",
            use_container_width=True,
            clamp=True
        )

        st.info(f"""
        💡 **Cómo funciona el filtro DoG:**
        - Resalta bordes y estructuras de tamaño específico
        - Rango de detección: ~{int((params['sigma2'] - params['sigma1']) * 3)} píxeles
        - Ajusta σ1 y σ2 para optimizar detección
        """)

        with st.expander("🔍 Ver componentes del DoG (G1, G2)"):
            componentes = visualizar_filtros_gauss(imagen_gris, params['sigma1'], params['sigma2'])
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.image(componentes['g1'], caption="G1 - Gaussiano σ1 (Detalle fino)", use_container_width=True)
            with col_g2:
                st.image(componentes['g2'], caption="G2 - Gaussiano σ2 (Estructura general)", use_container_width=True)

    with tab3:
        st.image(
            imagen_gris,
            caption=f"Escala de Grises {'+ CLAHE' if params['usar_clahe'] else ''} {'+ Reducción de Ruido' if params['reducir_ruido'] else ''}",
            use_container_width=True
        )

        status_prep = []
        status_prep.append("✅ Contraste mejorado (CLAHE)" if params['usar_clahe'] else "❌ Sin mejora de contraste")
        status_prep.append("✅ Reducción de ruido activa" if params['reducir_ruido'] else "❌ Sin reducción de ruido")
        if params['usar_hsv']:
            status_prep.append(f"✅ Segmentación HSV ({params['metodo_hsv']}, umbral={params['umbral_hsv']})")

        st.write("\n\n".join(status_prep))

    with tab4:
        st.image(
            imagen_original,
            channels="BGR",
            caption="Imagen Original sin Procesar",
            use_container_width=True
        )
        alto, ancho = imagen_original.shape[:2]
        st.info(f"📐 Dimensiones: {ancho} × {alto} píxeles")

    with tab5:
        if params['usar_hsv']:
            mask_hsv = segmentar_por_hsv(
                imagen_original,
                umbral_sat=params['umbral_hsv'],
                umbral_val=params['umbral_hsv'],
                metodo=params['metodo_hsv']
            )
            st.image(
                mask_hsv,
                caption=f"Máscara HSV ({params['metodo_hsv']}, umbral={params['umbral_hsv']})",
                use_container_width=True
            )
            imagen_hsv_aplicada = cv2.bitwise_and(imagen_original, imagen_original, mask=mask_hsv)
            st.image(
                imagen_hsv_aplicada,
                channels="BGR",
                caption="Imagen con máscara HSV aplicada",
                use_container_width=True
            )
        else:
            st.info("Activa 'Segmentación HSV' en el panel de ajustes para ver esta pestaña")

        if params['metodo_separacion'] != "none":
            st.markdown("---")
            st.markdown("#### Separación de Núcleos")
            if params['metodo_separacion'] == "watershed":
                st.info("Método: Watershed (Transformada de distancia)")
            elif params['metodo_separacion'] == "maximos_locales":
                st.info("Método: Máximos locales (picos DoG)")

            if resultados['total_celulas'] > 0:
                st.image(
                    img_deteccion,
                    channels="BGR",
                    caption=f"Detección con {params['metodo_separacion']}",
                    use_container_width=True
                )
        elif not params['usar_hsv']:
            st.info("Activa 'Separación de Núcleos' en el panel de ajustes para ver esta pestaña")

    with tab6:
        st.markdown("#### Reglas de Clasificación Activas")

        reglas = obtener_reglas_clasificacion(params['polaridad'])

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("Área Mínima", f"{reglas['area_minima_nucleo']} px²")
            st.metric("Área Promedio Normal", f"{reglas['area_promedio_nucleo_normal']} px²")
            st.metric("Factor de Clasificación", f"{reglas['factor_riesgo']}x")
        with col_r2:
            st.metric("Área Máxima", f"{reglas['area_maxima_nucleo']} px²")
            st.metric("Umbral Sospechoso", f"{reglas['umbral_sospechoso']:.1f} px²")
            st.metric("Margen Frontera", f"±{int(MARGEN_FRONTERA * 100)}%")

        st.markdown(f"""
        **Zona Frontera:** {reglas['limite_frontera_inferior']:.1f} - {reglas['limite_frontera_superior']:.1f} px²

        **Regla:** Núcleos con área ≥ {reglas['umbral_sospechoso']:.1f} px² → **Sospechosos**

        **Polaridad:** {params['polaridad']}
        """)

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
            st.dataframe(criterios_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay criterios de clasificación disponibles para esta ejecución")

    # ---------------- ESTADÍSTICAS ----------------
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

            st.bar_chart(areas_np)

            umbral = AREA_PROMEDIO_NUCLEO_NORMAL * FACTOR_RIESGO

            st.markdown(f"""
            **Parámetros de Clasificación:**
            - Área promedio normal: {AREA_PROMEDIO_NUCLEO_NORMAL} px²
            - Factor de riesgo: {FACTOR_RIESGO}x
            - **Umbral de sospecha: {umbral:.1f} px²**
            """)
        else:
            st.info("No se detectaron células para mostrar estadísticas.")

    # ---------------- DESCARGAS ----------------
    with st.expander("💾 Descargar Resultados", expanded=(seccion_actual == "exportar")):
        st.markdown("#### Exportar Imagen Procesada")

        _, buffer = cv2.imencode('.png', img_resultado)
        st.download_button(
            label="📥 Descargar Panel de Análisis (PNG)",
            data=buffer.tobytes(),
            file_name=f"citocounter_resultado_{nombre_base}.png",
            mime="image/png",
            key=f"dl_png_{nombre_archivo}"
        )

        st.markdown("#### Exportar Datos")

        csv_data = generar_csv_resultados(
            resultados,
            params['sigma1'],
            params['sigma2'],
            params['usar_clahe'],
            params['reducir_ruido'],
        )
        st.download_button(
            label="📥 Descargar Datos (CSV)",
            data=csv_data,
            file_name=f"citocounter_datos_{nombre_base}.csv",
            mime="text/csv",
            key=f"dl_csv_{nombre_archivo}"
        )

        json_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.1",
                "archivo_original": nombre_archivo,
                "id_anonimizado": obtener_id_sin_identificar(nombre_archivo)
            },
            "parametros": {
                "sigma1": params['sigma1'],
                "sigma2": params['sigma2'],
                "polaridad": params['polaridad'],
                "usar_clahe": params['usar_clahe'],
                "modo_clahe": params['modo_clahe'],
                "reducir_ruido": params['reducir_ruido'],
                "nivel_ruido": params['nivel_ruido'],
                "usar_hsv": params['usar_hsv'],
                "metodo_hsv": params['metodo_hsv'],
                "umbral_hsv": params['umbral_hsv'],
                "metodo_separacion": params['metodo_separacion'],
                "mostrar_contornos": params['mostrar_contornos'],
                "mostrar_areas": params['mostrar_areas']
            },
            "reglas_clasificacion": obtener_reglas_clasificacion(params['polaridad']),
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
            data=json.dumps(json_data, indent=2, ensure_ascii=False, default=str),
            file_name=f"citocounter_completo_{nombre_base}.json",
            mime="application/json",
            key=f"dl_json_{nombre_archivo}"
        )


# ============================================================================
# PANEL DE AJUSTES (columna izquierda, se muestra/oculta con el botón)
# ============================================================================
def panel_ajustes():
    with st.container(border=True):
        st.subheader("⚙️ Configuración de Análisis")

        # --- FUENTE DE IMÁGENES ---
        st.markdown("##### 📂 Fuente de Imágenes")

        st.radio(
            "Seleccionar origen",
            options=["upload", "dataset"],
            format_func=lambda x: {
                "upload": "📤 Subir archivo(s)",
                "dataset": "📁 Dataset del proyecto (data/raw/)"
            }[x],
            help="Elige entre subir tus propias imágenes o usar las del dataset del proyecto",
            **_widget("fuente_imagenes")
        )

        st.markdown("---")

        # --- PARÁMETROS DOG ---
        st.markdown("##### 1️⃣ Parámetros del Filtro DoG")

        sigma1 = st.slider(
            "Sigma 1 (Detalle fino)",
            min_value=0.5, max_value=10.0, step=0.1,
            help="Controla la detección de estructuras pequeñas",
            **_widget("sigma1")
        )

        sigma2 = st.slider(
            "Sigma 2 (Estructura general)",
            min_value=0.5, max_value=15.0, step=0.1,
            help="Controla la detección de estructuras grandes",
            **_widget("sigma2")
        )

        if sigma2 <= sigma1:
            st.error("⚠️ Sigma 2 debe ser mayor que Sigma 1")
            st.info("💡 Regla recomendada: σ2 ≈ 1.6-2.0 × σ1")
        else:
            st.info(f"Relación actual: {sigma2 / sigma1:.2f}x")

        st.markdown("---")

        # --- PREPROCESAMIENTO ---
        st.markdown("##### 2️⃣ Preprocesamiento")

        st.selectbox(
            "Polaridad de los núcleos",
            options=["nucleos-claros", "nucleos-oscuros"],
            help=(
                "Núcleos claros sobre fondo oscuro (fluorescencia) o núcleos "
                "oscuros sobre fondo claro (Papanicolaou/EDF). La opción "
                "'nucleos-oscuros' invierte la imagen antes del DoG."
            ),
            **_widget("polaridad")
        )

        usar_clahe = st.checkbox(
            "Mejorar Contraste (CLAHE)",
            help="Adaptive Histogram Equalization - mejora iluminación irregular",
            **_widget("usar_clahe")
        )

        if usar_clahe:
            st.selectbox(
                "Modo CLAHE",
                options=["clahe", "auto", "histogram", "normalize"],
                help="Auto selecciona automáticamente según el contraste de la imagen",
                **_widget("modo_clahe")
            )

        reducir_ruido = st.checkbox(
            "Reducir Ruido",
            help="Filtro bilateral - útil para imágenes con mucho ruido",
            **_widget("reducir_ruido")
        )

        if reducir_ruido:
            st.selectbox(
                "Nivel de reducción",
                options=["bajo", "medio", "alto"],
                help="Intensidad del filtro bilateral",
                **_widget("nivel_ruido")
            )

        st.markdown("---")

        # --- SEGMENTACIÓN AVANZADA ---
        st.markdown("##### 3️⃣ Segmentación Avanzada")

        usar_hsv = st.checkbox(
            "Segmentación HSV (Color)",
            help="Usa el canal de saturación/valor HSV para resaltar núcleos por color. Útil cuando el contraste de intensidad es bajo.",
            **_widget("usar_hsv")
        )

        if usar_hsv:
            st.selectbox(
                "Método HSV",
                options=["saturation", "value"],
                help="Saturation: núcleos con color distinto. Value: núcleos más brillantes/oscuros.",
                **_widget("metodo_hsv")
            )
            st.slider(
                "Umbral HSV",
                min_value=0, max_value=255, step=5,
                help="Umbral mínimo en el canal seleccionado (0-255)",
                **_widget("umbral_hsv")
            )

        st.markdown("---")

        # --- SEPARACIÓN DE NÚCLEOS ---
        st.markdown("##### 4️⃣ Separación de Núcleos Superpuestos")

        metodo_separacion = st.selectbox(
            "Método de separación",
            options=["none", "watershed", "maximos_locales"],
            format_func=lambda x: {
                "none": "Sin separación (original)",
                "watershed": "Watershed (Transformada de distancia)",
                "maximos_locales": "Máximos locales (picos DoG)"
            }[x],
            help="Watershed separa núcleos en contacto. Máximos locales detecta picos en la respuesta DoG.",
            **_widget("metodo_separacion")
        )

        if metodo_separacion != "none":
            st.info("⚠️ Experimental: puede cambiar el conteo total de células")

        st.markdown("---")

        # --- VISUALIZACIÓN ---
        st.markdown("##### 5️⃣ Opciones de Visualización")

        st.checkbox(
            "Dibujar Contornos Reales",
            help="Muestra los contornos detectados sobre las células",
            **_widget("mostrar_contornos")
        )

        st.checkbox(
            "Mostrar Áreas en Imagen",
            help="Muestra el área en píxeles² sobre cada detección",
            **_widget("mostrar_areas")
        )

        st.markdown("---")

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

            **Criterio de clasificación experimental:**
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

        st.markdown("""
        <div style='text-align: center; font-size: 0.8em; color: gray; margin-top: 12px;'>
            <p>CitoCounter Proto v1.1<br>Web Dashboard Interactivo<br>🔬 2024</p>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# DASHBOARD DE RESULTADOS HISTÓRICOS
# ============================================================================
def mostrar_dashboard_resultados(seccion_actual):
    """Muestra ejecuciones históricas y métricas agregadas por muestra."""
    historial = cargar_historial()
    if not historial:
        st.info("Aún no hay ejecuciones registradas para mostrar en el dashboard.")
        st.caption("Procesa una imagen y guarda el resultado en la bitácora para habilitar esta vista.")
        return

    metricas = metricas_conjunto(historial)
    st.markdown("## 📊 Dashboard de Resultados y Métricas")
    st.caption("Consulta histórica por muestra. Los indicadores son experimentales y requieren revisión experta.")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Ejecuciones", metricas["total_ejecuciones"])
    with col2:
        st.metric("Imágenes únicas", metricas["imagenes_unicas"])
    with col3:
        st.metric("Promedio de células", f"{metricas['total_celulas_promedio']:.1f}")
    with col4:
        st.metric("Sospechosas promedio", f"{metricas['riesgo_promedio']:.1f}%")
    with col5:
        st.metric("Sospechosas promedio", f"{metricas['sospechosas_promedio']:.1f}")

    if metricas["tasa_riesgo_alto"] > 0:
        st.warning(
            f"{metricas['tasa_riesgo_alto']:.1f}% de las ejecuciones superan el 10% de riesgo experimental.",
            icon="⚠️",
        )
    else:
        st.info("Ninguna ejecución supera el 10% de riesgo experimental.", icon="ℹ️")

    if seccion_actual == "metricas":
        st.markdown("### 📈 Evolución del riesgo por ejecución")
        evolucion = metricas.get("evolucion", [])
        if evolucion:
            st.line_chart({
                "Células sospechosas (%)": [
                    entrada["porcentaje_riesgo"] for entrada in evolucion
                ],
                "Células detectadas": [
                    entrada["total_celulas"] for entrada in evolucion
                ],
            })
        else:
            st.info("No hay suficientes datos para construir la evolución.")

        st.markdown("### 🧾 Reporte reproducible")
        st.download_button(
            "📥 Descargar reporte de métricas",
            data=reporte_resumen(historial),
            file_name="citocounter_reporte_metricas.txt",
            mime="text/plain",
        )

    st.markdown("### 📋 Resultados por muestra")
    filas = filas_para_tabla(historial)
    st.dataframe(filas, use_container_width=True, hide_index=True)
    st.warning(
        "Estos resultados no constituyen diagnóstico médico. Las muestras sospechosas "
        "o fronterizas requieren revisión experta.",
        icon="🔎",
    )


# ============================================================================
# ÁREA PRINCIPAL (selección de imágenes + procesamiento)
# ============================================================================
def pantalla_principal(cfg, seccion_actual):
    if seccion_actual in ("historial", "metricas"):
        mostrar_dashboard_resultados(seccion_actual)
        return

    params_procesamiento = {k: v for k, v in cfg.items() if k != "fuente_imagenes"}

    mostrar_progreso = True
    rutas_temporales = []
    imagenes_seleccionadas = []

    # ---------------- Selección de imágenes ----------------
    if cfg["fuente_imagenes"] == "dataset":
        ruta_dataset = obtener_ruta_dataset()

        try:
            imagenes_dataset = escanear_dataset(ruta_dataset)
        except OSError as e:
            st.error(f"❌ No se pudo leer la carpeta del dataset: {e}")
            st.info(f"Ruta: `{ruta_dataset}`")
            st.stop()

        if not imagenes_dataset:
            if ruta_dataset.is_dir():
                st.warning("⚠️ La carpeta del dataset existe pero no contiene imágenes (.jpg, .png, .tif, .bmp)")
            else:
                st.warning("⚠️ No se encontró la carpeta del dataset")
            st.info(f"Ruta buscada: `{ruta_dataset}`")
            st.info("Verifica la ruta o usa la opción 'Subir archivo(s)'")
            st.stop()

        st.markdown(f"### 📁 Dataset del proyecto: **{len(imagenes_dataset)} imágenes disponibles**")
        st.caption(f"📂 Leyendo imágenes desde: `{ruta_dataset}`")

        modo_procesamiento = st.radio(
            "Modo de procesamiento",
            options=["individual", "lote"],
            format_func=lambda x: {
                "individual": "🔍 Una imagen a la vez (vista detallada)",
                "lote": "📦 Procesamiento en lote (múltiples imágenes)"
            }[x],
            horizontal=True
        )

        nombres_imagenes = [img.name for img in imagenes_dataset]

        if modo_procesamiento == "individual":
            idx_seleccionado = st.selectbox(
                "Seleccionar imagen",
                options=range(len(nombres_imagenes)),
                format_func=lambda i: nombres_imagenes[i],
                help=f"Elige una de las {len(nombres_imagenes)} imágenes del dataset"
            )
            imagenes_seleccionadas = [imagenes_dataset[idx_seleccionado]]
        else:
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

            col_lote1, col_lote2 = st.columns(2)
            with col_lote1:
                mostrar_progreso = st.checkbox("Mostrar barra de progreso", value=True)
            with col_lote2:
                st.checkbox("Guardar resultados en bitácora", value=True)

    else:
        uploaded_files = st.file_uploader(
            "📂 Cargar imagen(es) de microscopía cervical",
            type=['jpg', 'png', 'jpeg', 'tif', 'tiff'],
            accept_multiple_files=True,
            help=(
                "Formatos soportados: JPG, PNG, TIF. Puedes seleccionar múltiples "
                "archivos; la aplicación admite hasta 10 MiB por archivo."
            )
        )
        st.caption(
            "Límite de la aplicación: 10 MiB por archivo. Los archivos mayores "
            "se rechazan antes del análisis."
        )

        if not uploaded_files:
            st.info("👆 **Carga una o varias imágenes de microscopía para comenzar el análisis**")
            mostrar_bienvenida()
            st.stop()

        for uploaded_file in uploaded_files:
            contenido_subido = uploaded_file.getvalue()

            if len(contenido_subido) > MAX_UPLOAD_BYTES:
                st.error(f"❌ {uploaded_file.name}: supera el límite de 10 MiB.")
                continue

            # Guardar con el nombre original para que los reportes lo muestren bien
            directorio_temp = tempfile.mkdtemp()
            ruta_temp = Path(directorio_temp) / uploaded_file.name
            ruta_temp.write_bytes(contenido_subido)

            imagenes_seleccionadas.append(ruta_temp)
            rutas_temporales.append(str(ruta_temp))

        if not imagenes_seleccionadas:
            st.error("No se pudieron cargar imágenes válidas.")
            st.stop()

        modo_procesamiento = "lote" if len(imagenes_seleccionadas) > 1 else "individual"
        if modo_procesamiento == "lote":
            st.info(f"📦 **{len(imagenes_seleccionadas)} imágenes cargadas** para procesamiento en lote")

    # ---------------- Procesamiento individual ----------------
    if modo_procesamiento == "individual":
        ruta_imagen = imagenes_seleccionadas[0]

        with st.spinner(f'🔬 Analizando {ruta_imagen.name}...'):
            resultado = procesar_imagen_individual(ruta_imagen, params_procesamiento)

        limpiar_temporales(rutas_temporales)

        if not resultado['exito']:
            st.error(f"❌ Error procesando {resultado['archivo']}: {resultado['error']}")
            st.stop()

        mostrar_detalle(resultado, params_procesamiento, seccion_actual)
        return

    # ---------------- Procesamiento en lote ----------------
    st.markdown("## 📦 Resultados del Procesamiento en Lote")

    if mostrar_progreso:
        progress_bar = st.progress(0)
        status_text = st.empty()
    else:
        progress_bar = None
        status_text = None

    resultados_lote = []

    for idx, ruta_imagen in enumerate(imagenes_seleccionadas):
        if progress_bar:
            progress_bar.progress(idx / len(imagenes_seleccionadas))
            status_text.text(f"Procesando {idx + 1}/{len(imagenes_seleccionadas)}: {ruta_imagen.name}")

        resultados_lote.append(procesar_imagen_individual(ruta_imagen, params_procesamiento))

    if progress_bar:
        progress_bar.progress(1.0)
        status_text.text("✅ Procesamiento completado")

    limpiar_temporales(rutas_temporales)

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
        st.metric("% Sospechosas Global", f"{pct_riesgo:.1f}%")

    if fallidos:
        with st.expander("❌ Errores en procesamiento", expanded=True):
            for f in fallidos:
                st.error(f"{f['archivo']}: {f['error']}")

    if not exitosos:
        return

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
            "% Sospechosas": f"{res['porcentaje_riesgo']:.1f}%",
            "Calidad": "✅" if r['metricas_calidad']['es_aceptable'] else "⚠️"
        })

    st.dataframe(datos_tabla, use_container_width=True, hide_index=True)

    st.markdown("### 📈 Distribución de Células Sospechosas por Imagen")
    import pandas as pd
    df_riesgo = pd.DataFrame([
        {
            "Imagen": r['archivo'][:20] + "...",
            "Sospechosas %": r['resultados']['porcentaje_riesgo'],
        }
        for r in exitosos
    ])
    st.bar_chart(df_riesgo.set_index("Imagen"))

    st.markdown("### 💾 Descargar Resultados del Lote")

    marca_tiempo = datetime.now().strftime('%Y%m%d_%H%M%S')
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📥 Descargar CSV Consolidado",
            data=generar_csv_lote(resultados_lote, params_procesamiento),
            file_name=f"citocounter_lote_{marca_tiempo}.csv",
            mime="text/csv"
        )

    with col_dl2:
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
            file_name=f"citocounter_lote_{marca_tiempo}.json",
            mime="application/json"
        )

    st.markdown("---")
    st.markdown("### 🔍 Vista Detallada de la Primera Imagen Exitosa")
    st.caption(f"Mostrando: {exitosos[0]['archivo']}")

    mostrar_detalle(exitosos[0], params_procesamiento, seccion_actual, expandir_calidad_por_defecto=True)


# ============================================================================
# LAYOUT: panel de ajustes (izquierda) + contenido principal (derecha)
# ============================================================================
# El contenido principal siempre es la 2ª columna, así su posición en la
# página no cambia al ocultar el panel (no se reinician uploader ni selectores).
panel_visible = st.session_state.panel_visible

col_panel, col_main = st.columns(
    [1, 3] if panel_visible else [0.01, 3.99],
    gap="medium" if panel_visible else "small"
)

if panel_visible:
    with col_panel:
        panel_ajustes()

with col_main:
    pantalla_principal(leer_config(), seccion)