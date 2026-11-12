# CitoCounter-Proto: Guía de Usuario y Manual de Instalación

## Índice

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación](#instalación)
3. [Uso Básico y Línea de Comandos (CLI)](#uso-básico-y-línea-de-comandos-cli)
4. [Interfaz Gráfica de Escritorio (Qt Desktop)](#interfaz-gráfica-de-escritorio-qt-desktop)
5. [Interfaz Web Interactiva (Streamlit)](#interfaz-web-interactiva-streamlit)
6. [Procesamiento de Imágenes y Parámetros DoG](#procesamiento-de-imágenes-y-parámetros-dog)
7. [Solución de Problemas](#solución-de-problemas)
8. [Preguntas Frecuentes](#preguntas-frecuentes)

## 1. Requisitos del Sistema

### Hardware
- Computadora con procesador x86_64 o ARM64
- Memoria RAM: mínimo 4 GB (recomendado 8 GB o más para procesamiento de lotes y video en vivo)
- Espacio en disco: 500 MB mínimo para resultados y bitácoras
- Cámara web USB o fuente de video C-mount (opcional para modo en vivo)

### Software
- **Sistema operativo**: Linux, macOS, o Windows 10/11
- **Python**: Versión 3.9 o superior
- **OpenCV**: Versión 4.5.0 o superior
- **PySide6**: Versión 6.5.0 o superior (para Qt Desktop)
- **Streamlit**: Versión 1.28.0 o superior (para interfaz web)

### Dependencias Python
El proyecto utiliza un `requirements.txt` con las dependencias necesarias.

## 2. Instalación

```bash
# Clonar el repositorio
git clone https://github.com/zowy4/CitoCounter-Proto.git
cd CitoCounter-Proto

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 3. Uso Básico y Línea de Comandos (CLI)

```bash
# Procesar una imagen individual
python main.py data/raw/MUESTRA_018.jpg

# Procesar lote sin interfaz gráfica
python main.py data/raw --lote --no-gui --sigma1 5.0 --sigma2 10.0
```

---

## 4. Interfaz Gráfica de Escritorio (Qt Desktop)

La versión de escritorio está desarrollada en **PySide6** y ofrece una experiencia nativa y fluida para entornos clínicos e investigación.

### Lanzamiento
```bash
python qt_app/main.py
```

### Arquitectura de Pestañas de la Aplicación Qt
La ventana principal (`qt_app/presentation/main_window.py`) organiza las herramientas en tres pestañas principales:

1. **Visor en Vivo y Cámara C-mount (`qt_app/presentation/visor_widget.py`)**:
   - Selección de dispositivos de captura de video (Cámaras USB, microscopio C-mount o archivos de video locales).
   - Controles de reproducción (Play/Pause/Stop) y previsualización de fotogramas en tiempo real.
   - Aplicación instantánea del pipeline DoG sobre el fotograma activo.

2. **Dashboard de Métricas e Indicadores (`qt_app/presentation/dashboard_widget.py`)**:
   - Tarjetas KPI dinámicas (Total de células, porcentaje de riesgo patológico, células normales vs. sospechosas).
   - Gráficas y tablas resumen del historial de ejecuciones.

3. **Panel de Trazabilidad y Evidencias Académicas (`qt_app/presentation/evidencia_panel.py`)**:
   - Listado estructurado de las 9 actividades académicas del proyecto organizadas por materia, tiempo de realización y unidades temáticas.
   - Visor enriquecido con renderizado tabular avanzado (HTML, CSV, JSON, Markdown y código fuente) sin viñetas informales.
   - Permite consultar directamente bitácoras de prueba, tablas de parámetros óptimos y reportes de rendimiento.

---

## 5. Interfaz Web Interactiva (Streamlit)

Para experimentación rápida y visualización web:

```bash
streamlit run app.py
```

- Permite cargar imágenes de citología cervical (`.jpg`, `.png`, `.tif`), ajustar deslizadores de Sigma 1, Sigma 2, CLAHE y polaridad, y visualizar de forma inmediata las detecciones normales (verde) y sospechosas (rojo).

---

## 6. Procesamiento de Imágenes y Parámetros DoG

- **Sigma 1 y Sigma 2**: Controlan el radio del filtro Difference of Gaussians (DoG). Valores recomendados: $\sigma_1 = 3.0$ a $5.0$, $\sigma_2 = 8.0$ a $10.0$.
- **Polaridad**: Seleccionar `nucleos-oscuros` para tinciones donde el núcleo es más oscuro que el fondo o citoplasma, o `nucleos-claros` según el contraste de la muestra.
- **Seguridad**: Se aplica un límite OWASP/STRIDE de 16 MiB para imágenes de microscopía de alta resolución (2048x1536 píxeles).

---

## 7. Solución de Problemas

- **Error de cámara no encontrada**: Verifique que la cámara USB / C-mount esté conectada y no esté siendo utilizada por otra aplicación.
- **Error al cargar PySide6**: Asegúrese de ejecutar `pip install -r requirements.txt` dentro del entorno virtual activo.
- **Rendimiento lento en video en vivo**: Reduzca la resolución de captura de la cámara en el panel de ajustes.

---

## 8. Preguntas Frecuentes

### P: ¿Puedo alternar entre la versión web y la versión de escritorio?
R: Sí, ambas versiones comparten los mismos módulos analíticos en `src/` y pueden utilizarse según las necesidades del usuario.

### P: ¿Cómo se guardan las evidencias de las actividades académicas?
R: Todas las evidencias, bitácoras y reportes se encuentran en `data/results/` y `docs/`, y son accesibles de forma interactiva desde la pestaña de Trazabilidad en la aplicación Qt.

---

**Aviso Legal:** CitoCounter-Proto es un prototipo de investigación académica en citología cervical. No constituye dispositivo médico ni software de diagnóstico clínico.

**Copyright:** 2026 CitoCounter-Proto. Todos los derechos reservados.
