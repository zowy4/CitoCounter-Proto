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
"""

import streamlit as st
import cv2
import numpy as np
import tempfile
import os
from pathlib import Path

# Importar módulos existentes de CitoCounter Proto
from src.preprocessing import preprocesar_imagen
from src.dog_filter import aplicar_filtro_dog
from src.analysis import analizar_nucleos
from src.visualization import dibujar_estadisticas_en_imagen, crear_vista_deteccion

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="CitoCounter Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.title("🔬 CitoCounter Proto - Panel de Control Interactivo")
st.markdown("**Análisis celular automatizado con algoritmo DoG + Regla del 3x**")
st.markdown("---")

# ============================================================================
# BARRA LATERAL (CONTROLES)
# ============================================================================
with st.sidebar:
    st.header("⚙️ Configuración de Análisis")
    
    # --- PARÁMETROS DOG ---
    st.subheader("1️⃣ Parámetros del Filtro DoG")
    
    sigma1 = st.slider(
        "Sigma 1 (Detalle fino)", 
        min_value=0.5, 
        max_value=10.0, 
        value=3.0, 
        step=0.1,
        help="Controla la detección de estructuras pequeñas"
    )
    
    sigma2 = st.slider(
        "Sigma 2 (Estructura general)", 
        min_value=0.5, 
        max_value=15.0, 
        value=5.0, 
        step=0.1,
        help="Controla la detección de estructuras grandes"
    )
    
    # Validación de parámetros
    if sigma2 <= sigma1:
        st.error("⚠️ Sigma 2 debe ser mayor que Sigma 1")
        st.info("💡 Regla recomendada: σ2 ≈ 1.6-2.0 × σ1")
    else:
        ratio = sigma2 / sigma1
        if 1.6 <= ratio <= 2.0:
            st.success(f"✅ Ratio óptimo: {ratio:.2f}x")
        else:
            st.warning(f"⚠️ Ratio: {ratio:.2f}x (recomendado: 1.6-2.0x)")
    
    st.markdown("---")
    
    # --- PREPROCESAMIENTO ---
    st.subheader("2️⃣ Preprocesamiento")
    
    usar_clahe = st.checkbox(
        "Mejorar Contraste (CLAHE)", 
        value=True,
        help="Adaptive Histogram Equalization - mejora iluminación irregular"
    )
    
    reducir_ruido = st.checkbox(
        "Reducir Ruido", 
        value=False,
        help="Filtro bilateral - útil para imágenes con mucho ruido"
    )
    
    st.markdown("---")
    
    # --- VISUALIZACIÓN ---
    st.subheader("3️⃣ Opciones de Visualización")
    
    mostrar_contornos = st.checkbox(
        "Dibujar Contornos Reales", 
        value=True,
        help="Muestra los contornos detectados sobre las células"
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
        1. Carga una imagen de microscopio
        2. Ajusta los sliders de Sigma
        3. Observa los resultados en tiempo real
        4. Compara en las pestañas visuales
        
        **Tips:**
        - Aumenta σ1 si detecta mucho ruido
        - Disminuye σ1 para captar más detalles
        - σ2 controla el tamaño de estructuras
        """)

# ============================================================================
# ÁREA PRINCIPAL
# ============================================================================

uploaded_file = st.file_uploader(
    "📂 Cargar imagen de microscopía cervical", 
    type=['jpg', 'png', 'jpeg', 'tif', 'tiff'],
    help="Formatos soportados: JPG, PNG, TIF"
)

if uploaded_file is not None:
    # Guardar archivo temporalmente (los módulos esperan una ruta de archivo)
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    tfile.write(uploaded_file.read())
    ruta_temp = tfile.name
    
    try:
        # --- PROCESAMIENTO ---
        with st.spinner('🔬 Analizando células... Esto puede tardar unos segundos.'):
            
            # A. Preprocesar
            imagen_gris, imagen_original = preprocesar_imagen(
                ruta_temp,
                mejorar_contraste_flag=usar_clahe,
                reducir_ruido_flag=reducir_ruido
            )
            
            # B. Filtro DoG
            imagen_dog = aplicar_filtro_dog(imagen_gris, sigma1, sigma2)
            
            # C. Análisis y clasificación
            resultados = analizar_nucleos(imagen_dog, imagen_original)
            
            # D. Preparar visualizaciones
            img_resultado = dibujar_estadisticas_en_imagen(
                resultados['imagen_procesada'], 
                resultados, 
                posicion='superior'
            )
            
            img_deteccion = crear_vista_deteccion(
                imagen_original,
                resultados['contornos_normales'],
                resultados['contornos_sospechosos'],
                dibujar_contornos=mostrar_contornos
            )
        
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
        
        # Interpretación clínica
        if porcentaje < 5:
            st.success("✅ **Interpretación:** Bajo riesgo - Perfil mayormente normal")
        elif porcentaje < 10:
            st.warning("⚠️ **Interpretación:** Riesgo moderado - Revisar células marcadas")
        else:
            st.error("🔴 **Interpretación:** Riesgo elevado - Requiere revisión detallada")
        
        st.markdown("---")
        
        # ====================================================================
        # SECCIÓN DE VISUALIZACIÓN
        # ====================================================================
        st.markdown("### 🖼️ Comparativa Visual")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Análisis Final", 
            "🔬 Filtro DoG", 
            "⚙️ Preprocesamiento",
            "📷 Original"
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
                file_name=f"citocounter_resultado_{uploaded_file.name}",
                mime="image/png"
            )
            
            # Datos CSV
            import csv
            from io import StringIO
            
            csv_buffer = StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(['Métrica', 'Valor'])
            writer.writerow(['Total Células', resultados['total_celulas']])
            writer.writerow(['Células Normales', resultados['normales']])
            writer.writerow(['Células Sospechosas', resultados['sospechosas']])
            writer.writerow(['Porcentaje de Riesgo', f"{resultados['porcentaje_riesgo']:.1f}%"])
            writer.writerow(['Sigma 1', sigma1])
            writer.writerow(['Sigma 2', sigma2])
            writer.writerow(['CLAHE', 'Sí' if usar_clahe else 'No'])
            writer.writerow(['Reducción Ruido', 'Sí' if reducir_ruido else 'No'])
            
            st.download_button(
                label="📥 Descargar Datos (CSV)",
                data=csv_buffer.getvalue(),
                file_name=f"citocounter_datos_{uploaded_file.name.split('.')[0]}.csv",
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"❌ **Error al procesar la imagen:**")
        st.exception(e)
        st.info("💡 Verifica que la imagen sea válida y que los módulos estén correctamente instalados.")
    
    finally:
        # Limpieza: eliminar archivo temporal
        try:
            if os.path.exists(ruta_temp):
                os.unlink(ruta_temp)
        except:
            pass

else:
    # ========================================================================
    # PANTALLA DE BIENVENIDA
    # ========================================================================
    st.info("👆 **Carga una imagen de microscopía para comenzar el análisis**")
    
    st.markdown("### 🎯 ¿Cómo usar CitoCounter Dashboard?")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        **📋 Paso a Paso:**
        1. Haz clic en "Browse files" arriba
        2. Selecciona tu imagen de citología
        3. Ajusta los parámetros en la barra lateral
        4. Observa los resultados instantáneos
        5. Descarga los resultados si lo deseas
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
