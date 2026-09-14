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
  "image_name": "MUESTRA_001.jpg",
  "image_dir": "raw",
  "sigma1": 7.0,
  "sigma2": 8.0,
  "noise_reduction": false,
  "enhance_contrast": true
}
```

- `image_name` obligatorio (solo nombre de archivo, sin rutas).
- `image_dir` opcional: `raw` (default) o `ground_truth`.
- `sigma2` debe ser mayor que `sigma1`.
- `sigma1` y `sigma2` deben ser valores numéricos positivos.
- `noise_reduction` y `enhance_contrast` deben ser booleanos JSON.
- Se validan existencia de archivo, extensión permitida y ruta dentro de `data/raw` o `data/ground_truth`.
- El cuerpo JSON está limitado a 64 KiB. La API se mantiene ligada a `127.0.0.1` por defecto.

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
  - valida rechazo sin `image_name`
  - valida error con sigmas inválidos
  - valida tipos booleanos y flujo exitoso con mocks del pipeline
  - valida `/health`, JSON inválido y cuerpo de solicitud excesivo mediante HTTP local

## Ejecución local

```bash
python api_v1.py --host 127.0.0.1 --port 8000
```

## Evidencia de prueba manual

Fecha: 2026-09-14

- `GET /api/v1/health` devolvió `200` con `ok=true`.
- `POST /api/v1/analyze` procesó `MUESTRA_001.jpg` con `sigma1=7.0` y `sigma2=8.0`, devolviendo `200` y un resultado de 2 detecciones normales.
- Una solicitud con `noise_reduction` como cadena (`"false"`) devolvió `400`, confirmando la validación estricta del contrato JSON.

La API se mantiene como prototipo de investigación y no sustituye evaluación clínica experta.
