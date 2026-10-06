#!/usr/bin/env python3
"""
API REST v1 para CitoCounter Proto (CITO-25 / J-11).
"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from src.analysis import analizar_nucleos
from src.dog_filter import aplicar_filtro_dog
from src.preprocessing import preprocesar_imagen, POLARIDADES_VALIDAS


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
MAX_REQUEST_BODY_BYTES = 64 * 1024
PROJECT_ROOT = Path(__file__).resolve().parent
ALLOWED_IMAGE_ROOTS = {
    "raw": PROJECT_ROOT / "data" / "raw",
    "ground_truth": PROJECT_ROOT / "data" / "ground_truth",
}
# CITO-79: Security validation constants
MAX_IMAGE_BYTES = 64 * 1024  # 64 KiB OWASP limit
PROHIBITED_PATH_PATTERNS = ["/", "\\", ".."]
ERROR_CODES = {
    "invalid_extension": "invalid_extension",
    "invalid_size": "invalid_size",
    "invalid_content": "invalid_content",
    "unsafe_path": "unsafe_path",
}


def error_response(message, status_code=400):
    return {
        "ok": False,
        "error": {
            "code": status_code,
            "message": message,
        },
    }, status_code


def validar_booleano(payload, field_name, default):
    """Obtiene un booleano JSON o devuelve un error de validación."""
    value = payload.get(field_name, default)
    if not isinstance(value, bool):
        return None, error_response(f"`{field_name}` debe ser booleano.")
    return value, None


def validate_payload(payload):
    if not isinstance(payload, dict):
        return error_response("El cuerpo JSON debe ser un objeto.")

    image_name = payload.get("image_name")
    if not image_name or not isinstance(image_name, str):
        return error_response("`image_name` es obligatorio y debe ser string.")
    if "/" in image_name or "\\" in image_name or ".." in image_name:
        return error_response("`image_name` no debe contener rutas o '..'.")

    image_dir = payload.get("image_dir", "raw")
    if image_dir not in ALLOWED_IMAGE_ROOTS:
        return error_response("`image_dir` debe ser `raw` o `ground_truth`.")

    if Path(image_name).suffix.lower() not in ALLOWED_EXTENSIONS:
        return error_response(
            f"Extensión no permitida: {Path(image_name).suffix}. Usa {sorted(ALLOWED_EXTENSIONS)}."
        )
    path = ALLOWED_IMAGE_ROOTS[image_dir] / image_name
    if not path.exists() or not path.is_file():
        return error_response(f"Imagen no encontrada: {image_name} en {image_dir}")

    try:
        sigma1 = float(payload.get("sigma1", 7.0))
        sigma2 = float(payload.get("sigma2", 8.0))
    except (TypeError, ValueError):
        return error_response("`sigma1` y `sigma2` deben ser valores numéricos.")
    if sigma1 <= 0 or sigma2 <= 0:
        return error_response("`sigma1` y `sigma2` deben ser mayores que 0.")
    if sigma2 <= sigma1:
        return error_response("`sigma2` debe ser mayor que `sigma1`.")

    reducir_ruido, error = validar_booleano(payload, "noise_reduction", False)
    if error:
        return error
    mejorar_contraste, error = validar_booleano(payload, "enhance_contrast", True)
    if error:
        return error

    polaridad = payload.get("polarity", "nucleos-claros")
    if polaridad not in POLARIDADES_VALIDAS:
        return error_response(
            f"`polarity` debe ser uno de: {sorted(POLARIDADES_VALIDAS)}."
        )

    return {
        "path": path,
        "sigma1": sigma1,
        "sigma2": sigma2,
        "reducir_ruido": reducir_ruido,
        "mejorar_contraste": mejorar_contraste,
        "polaridad": polaridad,
    }, 200


def analyze_from_payload(payload):
    validated, status = validate_payload(payload)
    if status != 200:
        return validated, status

    try:
        imagen_gris, imagen_original = preprocesar_imagen(
            str(validated["path"]),
            mejorar_contraste_flag=validated["mejorar_contraste"],
            reducir_ruido_flag=validated["reducir_ruido"],
            polaridad=validated["polaridad"],
        )
        imagen_dog = aplicar_filtro_dog(
            imagen_gris,
            sigma1=validated["sigma1"],
            sigma2=validated["sigma2"],
        )
        resultados = analizar_nucleos(imagen_dog, imagen_original, polaridad=validated["polaridad"])
    except Exception as exc:
        return error_response(f"Error procesando imagen: {exc}", status_code=500)

    data = {
        "ok": True,
        "api_version": "v1",
        "warning": (
            "Prototipo de investigación. El resultado no equivale a diagnóstico clínico."
        ),
        "input": {
            "image_name": validated["path"].name,
            "image_dir": next(k for k, v in ALLOWED_IMAGE_ROOTS.items() if validated["path"].is_relative_to(v)),
            "sigma1": validated["sigma1"],
            "sigma2": validated["sigma2"],
            "noise_reduction": validated["reducir_ruido"],
            "enhance_contrast": validated["mejorar_contraste"],
            "polarity": validated["polaridad"],
        },
        "result": {
            "total_cells": resultados["total_celulas"],
            "normal_cells": resultados["normales"],
            "suspicious_cells": resultados["sospechosas"],
            "borderline_cells": resultados.get("frontera", 0),
            "risk_percent": resultados["porcentaje_riesgo"],
        },
    }
    return data, 200


class CitoCounterApiHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/v1/health":
            self._send_json({"ok": True, "api_version": "v1", "status": "healthy"}, 200)
            return
        self._send_json(
            {"ok": False, "error": {"code": 404, "message": "Endpoint no encontrado"}},
            404,
        )

    def do_POST(self):
        if self.path != "/api/v1/analyze":
            self._send_json(
                {"ok": False, "error": {"code": 404, "message": "Endpoint no encontrado"}},
                404,
            )
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(
                {"ok": False, "error": {"code": 400, "message": "Content-Length inválido"}},
                400,
            )
            return
        if content_length <= 0:
            self._send_json(
                {"ok": False, "error": {"code": 400, "message": "Cuerpo JSON vacío"}},
                400,
            )
            return
        if content_length > MAX_REQUEST_BODY_BYTES:
            self._send_json(
                {"ok": False, "error": {"code": 413, "message": "Cuerpo JSON demasiado grande"}},
                413,
            )
            return

        raw = self.rfile.read(content_length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(
                {"ok": False, "error": {"code": 400, "message": "JSON inválido"}},
                400,
            )
            return

        # CITO-79: Additional security validations
        if not validar_ruta_segura(payload.get("image_name", "")):
            self._send_json(
                {"ok": False, "error": {"code": 400, "message": "`image_name` contiene rutas prohibidas."}},
                400,
            )
            return
        
        image_name = payload.get("image_name", "")
        if not validar_extension(image_name):
            self._send_json(
                {"ok": False, "error": {"code": 400, "message": f"Extensión no permitida: {Path(image_name).suffix}. Usa {sorted(ALLOWED_EXTENSIONS)}."}},
                400,
            )
            return
        
        image_dir = payload.get("image_dir", "raw")
        path = ALLOWED_IMAGE_ROOTS[image_dir] / image_name
        if not validar_tamaño(path):
            self._send_json(
                {"ok": False, "error": {"code": 400, "message": "Imagen excede el límite de 64 KiB."}},
                400,
            )
            return
        
        import cv2
        import os
        if not validar_contenido(path):
            self._send_json(
                {"ok": False, "error": {"code": 400, "message": "Imagen corrupta o vacía."}},
                400,
            )
            return
        
        registrar_acceso("/api/v1/analyze", "POST", True)
        
        response, status = analyze_from_payload(payload)
        self._send_json(response, status)


def run_api(host="127.0.0.1", port=8000):
    server = HTTPServer((host, port), CitoCounterApiHandler)
    print(f"API CitoCounter v1 escuchando en http://{host}:{port}")
    print("Endpoints: GET /api/v1/health, POST /api/v1/analyze")
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API REST v1 de CitoCounter Proto.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    run_api(host=args.host, port=args.port)


# CITO-79: Security validation functions
def validar_extension(image_name):
    """Validate file extension is allowed (CITO-79)."""
    if not image_name:
        return True
    suffix = Path(image_name).suffix.lower()
    return suffix in ALLOWED_EXTENSIONS


def validar_tamaño(ruta_path):
    """Validate file size is within OWASP 64 KiB limit (CITO-79)."""
    try:
        size = ruta_path.stat().st_size
        return size <= MAX_IMAGE_BYTES
    except OSError:
        return False


def validar_contenido(ruta_path):
    """Validate image content is not empty and has valid format (CITO-79)."""
    try:
        import cv2
        imagen = cv2.imread(str(ruta_path), cv2.IMREAD_UNCHANGED)
        if imagen is None:
            return False
        # Check if image is completely empty (all zeros)
        if imagen.size == 0:
            return False
        return True
    except Exception:
        return False


def validar_ruta_segura(image_name):
    """Validate path does not contain traversal patterns (OWASP CITO-79)."""
    if not image_name:
        return True
    for patron in PROHIBITED_PATH_PATTERNS:
        if patron in image_name:
            return False
    return True


def limpiar_archivos_temporales():
    """Clean temporary files older than 1 hour (CITO-79)."""
    import time
    import glob
    import os
    temp_dir = os.path.join(PROJECT_ROOT, "data", "results", "temp")
    if not os.path.exists(temp_dir):
        return
    ahora = time.time()
    for archivo in glob.glob(os.path.join(temp_dir, "*")):
        try:
            if ahora - os.path.getmtime(archivo) > 3600:
                os.remove(archivo)
        except OSError:
            pass


def registrar_acceso(endpoint, metodo, exito, detalles=None):
    """Log API access for audit purposes (CITO-79)."""
    import logging
    logger = logging.getLogger("cito-api")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] cito-api: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    mensaje = f"endpoint={endpoint}, metodo={metodo}, exito={exito}"
    if detalles:
        mensaje += f", detalles={detalles}"
    logger.info(mensaje)


def exito_response(data, mensaje="Operación exitosa"):
    """Standardized success response (CITO-78/CITO-79)."""
    return {
        "ok": True,
        "api_version": "v1",
        "mensaje": mensaje,
        "data": data,
    }, 200
