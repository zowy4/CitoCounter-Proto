# CITO-25: Evidencia de API REST v1

**Estado:** Finalizado técnicamente; publicado para revisión del proyecto  
**Módulo:** [`api_v1.py`](../api_v1.py)  
**Pruebas:** [`tests/test_api_v1.py`](../tests/test_api_v1.py)

## Contrato

La API escucha por defecto en `127.0.0.1:8000` y expone:

| Método | Ruta | Propósito |
|---|---|---|
| `GET` | `/api/v1/health` | Comprobar disponibilidad y versión |
| `POST` | `/api/v1/analyze` | Procesar una imagen autorizada y devolver el análisis |

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

- `image_name` es obligatorio, solo admite el nombre del archivo y extensiones
  `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff` o `.bmp`.
- `image_dir` solo puede ser `raw` o `ground_truth`.
- `sigma1` y `sigma2` deben ser positivos y `sigma2` debe ser mayor que `sigma1`.
- `noise_reduction` y `enhance_contrast` deben ser booleanos JSON.
- `polarity` debe ser una polaridad soportada por el preprocesamiento.
- La imagen debe existir dentro del directorio autorizado, ser legible y no
  superar 64 KiB. El cuerpo JSON también está limitado a 64 KiB.

La carga se realiza de forma controlada mediante `image_name` más un directorio
autorizado; no se aceptan rutas arbitrarias ni carga de archivos fuera de los
directorios del proyecto.

### Respuesta exitosa

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

### Errores

Los errores usan una respuesta JSON estable:

```json
{
  "ok": false,
  "error": {
    "code": 400,
    "message": "Descripción del error"
  }
}
```

Se cubren, como mínimo, JSON inválido o no objeto (`400`), parámetros
inconsistentes (`400`), rutas o extensiones no permitidas (`400`), imágenes
ausentes, corruptas o demasiado grandes (`400`), cuerpo excesivo (`413`) y
rutas no existentes (`404`).

## Evidencia reproducible

```text
python -m unittest tests.test_api_v1 -v
Ran 12 tests ... OK
```

Las pruebas cubren disponibilidad, flujo válido con respuesta estructurada,
validación de sigma y booleanos, rutas/directorios inválidos, JSON inválido o
no objeto y límite de tamaño HTTP.

La API es un componente experimental: sus resultados no constituyen diagnóstico
clínico y requieren revisión experta.
