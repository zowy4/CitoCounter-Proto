# Evidencia CITO-25 - API REST v1

## Objetivo

Desarrollar una API REST versionada para procesar imágenes y devolver análisis del pipeline DoG.

## Implementación

- Archivo: `api_v1.py`
- Endpoints:
  - `GET /api/v1/health`
  - `POST /api/v1/analyze`

## Esquema de entrada (`POST /api/v1/analyze`)

```json
{
  "image_path": "data/raw/MUESTRA_001.jpg",
  "sigma1": 7.0,
  "sigma2": 8.0,
  "noise_reduction": false,
  "enhance_contrast": true
}
```

- `image_path` obligatorio.
- `sigma2` debe ser mayor que `sigma1`.
- Se validan existencia de archivo, extensión permitida y ruta dentro de `data/raw` o `data/ground_truth`.

## Esquema de salida

```json
{
  "ok": true,
  "api_version": "v1",
  "warning": "Prototipo de investigación. El resultado no equivale a diagnóstico clínico.",
  "input": { "...": "..." },
  "result": {
    "total_cells": 0,
    "normal_cells": 0,
    "suspicious_cells": 0,
    "borderline_cells": 0,
    "risk_percent": 0.0
  }
}
```

## Pruebas

- `tests/test_api_v1.py`
  - valida rechazo sin `image_path`
  - valida error con sigmas inválidos
  - valida flujo exitoso con mocks del pipeline

## Ejecución local

```bash
python api_v1.py --host 127.0.0.1 --port 8000
```

La API se mantiene como prototipo de investigación y no sustituye evaluación clínica experta.
