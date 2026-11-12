# CITO-25: Evidencia de API REST v1 e Integración Qt / Web

**Estado:** Finalizado técnicamente; publicado para revisión del proyecto  
**Módulo Backend:** [`api_v1.py`](../api_v1.py)  
**Módulo Qt Desktop:** [`qt_app/presentation/main_window.py`](../qt_app/presentation/main_window.py)  
**Interfaz Web:** [`app.py`](../app.py)  
**Pruebas:** [`tests/test_api_v1.py`](../tests/test_api_v1.py)

## Contrato de Servicios

La API escucha por defecto en `127.0.0.1:8000` y expone los siguientes endpoints para el procesamiento de imágenes clínicas y citología cervical:

| Método | Ruta | Propósito |
|---|---|---|
| `GET` | `/api/v1/health` | Comprobar disponibilidad y versión del servicio |
| `POST` | `/api/v1/analyze` | Procesar una imagen autorizada y retornar el análisis celular estructurado |

### Entrada de `POST /api/v1/analyze`

```json
{
  "image_name": "muestra.jpg",
  "image_dir": "raw",
  "sigma1": 5.0,
  "sigma2": 10.0,
  "noise_reduction": false,
  "enhance_contrast": true,
  "polarity": "nucleos-claros"
}
```

- `image_name` es obligatorio, solo admite el nombre del archivo y extensiones `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff` o `.bmp`.
- `image_dir` solo puede ser `raw` o `ground_truth`.
- `sigma1` y `sigma2` deben ser positivos y `sigma2` debe ser mayor que `sigma1`.
- `noise_reduction` y `enhance_contrast` deben ser booleanos JSON.
- `polarity` debe ser una polaridad soportada por el preprocesamiento (`nucleos-oscuros` o `nucleos-claros`).
- La imagen debe existir dentro del directorio autorizado, ser legible y cumplir con los límites de seguridad OWASP/STRIDE (hasta 16 MiB para microscopía clínica).

### Respuesta Exitosa

```json
{
  "ok": true,
  "api_version": "v1",
  "warning": "Prototipo de investigación. El resultado no equivale a diagnóstico clínico.",
  "input": {
    "image_name": "muestra.jpg",
    "image_dir": "raw",
    "sigma1": 5.0,
    "sigma2": 10.0,
    "noise_reduction": false,
    "enhance_contrast": true,
    "polarity": "nucleos-claros"
  },
  "result": {
    "total_cells": 10,
    "normal_cells": 7,
    "suspicious_cells": 3,
    "borderline_cells": 2,
    "risk_percent": 30.0
  }
}
```

### Manejo de Errores

Los errores utilizan una respuesta JSON estable:

```json
{
  "ok": false,
  "error": {
    "code": 400,
    "message": "Descripción detallada del error"
  }
}
```

Se cubren validaciones de JSON inválido (`400`), parámetros inconsistentes (`400`), extensiones no permitidas (`400`), imágenes ausentes o corruptas (`400`), cuerpo excesivo (`413`) y rutas no existentes (`404`).

---

## Integración con la Interfaz Qt Desktop y Web

La arquitectura del proyecto permite desacoplar el motor analítico (`src/`) y la API REST (`api_v1.py`) de las interfaces de usuario:

1. **Qt Desktop (`qt_app/`)**: Permite la interacción nativa con la cámara en vivo, previsualización de video y control deslizante de parámetros DoG / CLAHE / HSV.
2. **Interfaz Web (`app.py`)**: Desarrollada en Streamlit para experimentación rápida y visualización de dashboards.

### Referencia Visual de la Interfaz Qt Desktop

| Componente UI | Archivo Responsable | Descripción Funcional |
|---|---|---|
| Ventana Principal | [`qt_app/presentation/main_window.py`](../qt_app/presentation/main_window.py) | Orquestador de pestañas (Visor en vivo, Dashboard, Trazabilidad) |
| Panel de Ajustes | [`qt_app/presentation/panel_ajustes.py`](../qt_app/presentation/panel_ajustes.py) | Controles de Sigma 1/2, CLAHE, bilateral, HSV y polaridad |
| Panel de Trazabilidad | [`qt_app/presentation/evidencia_panel.py`](../qt_app/presentation/evidencia_panel.py) | Visualizador tabular enriquecido de actividades académicas y evidencias |

> *Nota de Arquitectura:* Las capturas de pantalla de la interfaz Qt y los diagramas de flujo de la API pueden consultarse directamente ejecutando la aplicación Qt con `python qt_app/main.py`.

---

## Evidencia Reproducible

```text
python -m unittest tests.test_api_v1 -v
Ran 12 tests ... OK
```

Las pruebas unitarias automatizadas cubren la disponibilidad del servicio, flujos válidos con respuestas estructuradas, validación estricta de hiperparámetros y límites de tamaño de carga HTTP.

*Advertencia:* Este software es un prototipo de investigación académica en citología cervical. Sus resultados no constituyen diagnóstico clínico y requieren validación por personal médico experto.
