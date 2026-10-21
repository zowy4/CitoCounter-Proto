#!/usr/bin/env python3
"""
API REST v1 para CitoCounter Proto (CITO-25 / J-11).
"""

import argparse
import base64
import binascii
import hashlib
import hmac
import json
import os
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Mapping

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
RATE_LIMIT_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 60
REQUEST_TIMESTAMPS = defaultdict(deque)
JWT_EXPIRATION_SECONDS = 3600
JWT_REFRESH_EXPIRATION_SECONDS = 86400 * 7  # 7 days
ROLES_ANALISIS = {"analista", "administrador"}
ALGORITHM_REVISION = "dog-otsu-contours-area-experimental-v1"

# CITO-92/CITO-93: Additional security constants
LOGIN_ATTEMPTS = defaultdict(deque)
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_WINDOW_SECONDS = 300  # 5 minutes
LOGIN_LOCKOUT_DURATION_SECONDS = 900  # 15 minutes
LOCKED_ACCOUNTS = {}

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}

# CORS configuration
CORS_ALLOWED_ORIGINS = os.environ.get("CITO_CORS_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501").split(",")
CORS_ALLOWED_METHODS = ["GET", "POST", "OPTIONS"]
CORS_ALLOWED_HEADERS = ["Content-Type", "Authorization", "X-API-Key"]
CORS_MAX_AGE = 86400

# Password complexity requirements
MIN_PASSWORD_LENGTH = 12
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_DIGITS = True
REQUIRE_SPECIAL_CHARS = True


def _base64url_codificar(data: bytes) -> str:
    """Codifica bytes para una sección JWT sin relleno.

    :param data: Datos a codificar.
    :type data: bytes
    :return: Texto codificado en base64 URL-safe.
    :rtype: str
    """
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decodificar(data: str) -> bytes:
    """Decodifica una sección JWT codificada en base64 URL-safe.

    :param data: Sección JWT sin relleno.
    :type data: str
    :return: Datos decodificados.
    :rtype: bytes
    :raises ValueError: Si la sección no tiene codificación válida.
    """
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def crear_token_jwt(usuario: str, rol: str, now: float | None = None) -> str:
    """Crea un JWT HS256 de duración limitada para un usuario configurado.

    :param usuario: Identificador del usuario autenticado.
    :type usuario: str
    :param rol: Rol autorizado para el usuario.
    :type rol: str
    :param now: Tiempo UNIX opcional para pruebas deterministas.
    :type now: float | None
    :return: JWT firmado con el secreto configurado.
    :rtype: str
    :raises RuntimeError: Si falta el secreto JWT de entorno.
    """
    secreto = os.environ.get("CITO_JWT_SECRET")
    if not secreto:
        raise RuntimeError("CITO_JWT_SECRET no está configurado.")
    issued_at = int(time.time() if now is None else now)
    encabezado = _base64url_codificar(
        json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode("utf-8")
    )
    carga = _base64url_codificar(
        json.dumps(
            {"sub": usuario, "role": rol, "iat": issued_at, "exp": issued_at + JWT_EXPIRATION_SECONDS},
            separators=(",", ":"),
        ).encode("utf-8")
    )
    firma = hmac.new(
        secreto.encode("utf-8"), f"{encabezado}.{carga}".encode("ascii"), hashlib.sha256
    ).digest()
    return f"{encabezado}.{carga}.{_base64url_codificar(firma)}"


def validar_token_jwt(token: str, now: float | None = None) -> dict[str, str] | None:
    """Valida firma, algoritmo, caducidad y reclamos mínimos de un JWT HS256.

    :param token: JWT proporcionado en la cabecera Authorization.
    :type token: str
    :param now: Tiempo UNIX opcional para pruebas deterministas.
    :type now: float | None
    :return: Reclamos seguros del token o None cuando es inválido.
    :rtype: dict[str, str] | None
    """
    secreto = os.environ.get("CITO_JWT_SECRET")
    if not secreto:
        return None
    try:
        encabezado, carga, firma = token.split(".")
        header = json.loads(_base64url_decodificar(encabezado).decode("utf-8"))
        if header != {"alg": "HS256", "typ": "JWT"}:
            return None
        expected_signature = hmac.new(
            secreto.encode("utf-8"), f"{encabezado}.{carga}".encode("ascii"), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_base64url_decodificar(firma), expected_signature):
            return None
        claims = json.loads(_base64url_decodificar(carga).decode("utf-8"))
        if not isinstance(claims, dict) or not isinstance(claims.get("sub"), str):
            return None
        if not isinstance(claims.get("role"), str) or not isinstance(claims.get("exp"), int):
            return None
        if claims["exp"] <= int(time.time() if now is None else now):
            return None
    except (binascii.Error, UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return None
    return {"sub": claims["sub"], "role": claims["role"]}


def validar_autenticacion(headers: Mapping[str, str]) -> tuple[dict[str, str] | None, tuple[dict[str, Any], int] | None]:
    """Valida la clave API opcional o un JWT Bearer configurado.

    :param headers: Cabeceras HTTP entrantes.
    :type headers: Mapping[str, str]
    :return: Identidad autenticada y, en caso de error, la respuesta HTTP.
    :rtype: tuple[dict[str, str] | None, tuple[dict[str, Any], int] | None]
    """
    expected_key = os.environ.get("CITO_API_KEY")
    supplied_key = headers.get("X-API-Key", "")
    if expected_key and supplied_key:
        if hmac.compare_digest(supplied_key, expected_key):
            return {"sub": "api-key", "role": "administrador"}, None
        return None, error_response("Clave de API ausente o inválida.", 401)

    secreto_jwt = os.environ.get("CITO_JWT_SECRET")
    if secreto_jwt:
        authorization = headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        claims = validar_token_jwt(token) if scheme == "Bearer" and token else None
        if claims:
            return claims, None
        return None, error_response("Token de acceso ausente o inválido.", 401)

    if expected_key:
        return None, error_response("Clave de API ausente o inválida.", 401)
    return {"sub": "local", "role": "administrador"}, None


def autenticar_usuario(payload: object) -> tuple[dict[str, Any], int]:
    """Autentica credenciales de entorno y devuelve un JWT temporal.

    :param payload: Cuerpo JSON con username y password.
    :type payload: object
    :return: Respuesta de autenticación y código HTTP.
    :rtype: tuple[dict[str, Any], int]
    """
    if not isinstance(payload, dict):
        return error_response("El cuerpo JSON debe ser un objeto.")
    username = payload.get("username")
    password = payload.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return error_response("`username` y `password` son obligatorios.", 400)
    
    # Check if account is locked (CITO-92)
    now = time.time()
    if username in LOCKED_ACCOUNTS:
        lockout_until = LOCKED_ACCOUNTS[username]
        if now < lockout_until:
            remaining = int(lockout_until - now)
            return error_response(f"Cuenta bloqueada. Intente de nuevo en {remaining} segundos.", 429)
        else:
            # Lockout expired, remove from locked accounts
            del LOCKED_ACCOUNTS[username]
            # Also clear login attempts
            if username in LOGIN_ATTEMPTS:
                del LOGIN_ATTEMPTS[username]
    
    # Check login attempts (CITO-92)
    if username in LOGIN_ATTEMPTS:
        attempts = LOGIN_ATTEMPTS[username]
        # Remove old attempts outside the window
        while attempts and now - attempts[0] >= LOGIN_LOCKOUT_WINDOW_SECONDS:
            attempts.popleft()
        if len(attempts) >= MAX_LOGIN_ATTEMPTS:
            # Lock the account
            LOCKED_ACCOUNTS[username] = now + LOGIN_LOCKOUT_DURATION_SECONDS
            return error_response(f"Demasiados intentos fallidos. Cuenta bloqueada por {LOGIN_LOCKOUT_DURATION_SECONDS // 60} minutos.", 429)
    
    try:
        usuarios = json.loads(os.environ.get("CITO_API_USERS", ""))
    except json.JSONDecodeError:
        return error_response("Configuración de usuarios inválida.", 503)
    if not isinstance(usuarios, dict) or not os.environ.get("CITO_JWT_SECRET"):
        return error_response("Autenticación JWT no configurada.", 503)
    usuario = usuarios.get(username)
    if not isinstance(usuario, dict):
        # Record failed attempt (CITO-92)
        LOGIN_ATTEMPTS[username].append(now)
        return error_response("Credenciales inválidas.", 401)
    password_configurada = usuario.get("password")
    rol = usuario.get("role")
    if (
        not isinstance(password_configurada, str)
        or not isinstance(rol, str)
        or not hmac.compare_digest(password, password_configurada)
    ):
        # Record failed attempt (CITO-92)
        LOGIN_ATTEMPTS[username].append(now)
        return error_response("Credenciales inválidas.", 401)
    
    # Successful login - clear attempts
    if username in LOGIN_ATTEMPTS:
        del LOGIN_ATTEMPTS[username]
    
    access_token = crear_token_jwt(username, rol)
    refresh_token = crear_refresh_token(username, rol)
    return {
        "ok": True,
        "token_type": "Bearer",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": JWT_EXPIRATION_SECONDS,
        "role": rol,
    }, 200


def crear_refresh_token(usuario: str, rol: str, now: float | None = None) -> str:
    """Crea un refresh token JWT HS256 de larga duración.

    :param usuario: Identificador del usuario autenticado.
    :type usuario: str
    :param rol: Rol autorizado para el usuario.
    :type rol: str
    :param now: Tiempo UNIX opcional para pruebas deterministas.
    :type now: float | None
    :return: JWT firmado con el secreto configurado.
    :rtype: str
    :raises RuntimeError: Si falta el secreto JWT de entorno.
    """
    secreto = os.environ.get("CITO_JWT_SECRET")
    if not secreto:
        raise RuntimeError("CITO_JWT_SECRET no está configurado.")
    issued_at = int(time.time() if now is None else now)
    encabezado = _base64url_codificar(
        json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode("utf-8")
    )
    carga = _base64url_codificar(
        json.dumps(
            {"sub": usuario, "role": rol, "type": "refresh", "iat": issued_at, "exp": issued_at + JWT_REFRESH_EXPIRATION_SECONDS},
            separators=(",", ":"),
        ).encode("utf-8")
    )
    firma = hmac.new(
        secreto.encode("utf-8"), f"{encabezado}.{carga}".encode("ascii"), hashlib.sha256
    ).digest()
    return f"{encabezado}.{carga}.{_base64url_codificar(firma)}"


def validar_refresh_token(token: str, now: float | None = None) -> dict[str, str] | None:
    """Valida un refresh token y devuelve los claims si es válido.

    :param token: Refresh token JWT.
    :type token: str
    :param now: Tiempo UNIX opcional para pruebas deterministas.
    :type now: float | None
    :return: Claims del token o None si es inválido.
    :rtype: dict[str, str] | None
    """
    secreto = os.environ.get("CITO_JWT_SECRET")
    if not secreto:
        return None
    try:
        encabezado, carga, firma = token.split(".")
        header = json.loads(_base64url_decodificar(encabezado).decode("utf-8"))
        if header != {"alg": "HS256", "typ": "JWT"}:
            return None
        expected_signature = hmac.new(
            secreto.encode("utf-8"), f"{encabezado}.{carga}".encode("ascii"), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_base64url_decodificar(firma), expected_signature):
            return None
        claims = json.loads(_base64url_decodificar(carga).decode("utf-8"))
        if not isinstance(claims, dict) or not isinstance(claims.get("sub"), str):
            return None
        if not isinstance(claims.get("role"), str) or not isinstance(claims.get("exp"), int):
            return None
        if claims.get("type") != "refresh":
            return None
        if claims["exp"] <= int(time.time() if now is None else now):
            return None
    except (binascii.Error, UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return None
    return {"sub": claims["sub"], "role": claims["role"]}


def validar_complejidad_password(password: str) -> tuple[bool, str]:
    """Valida la complejidad de la contraseña (CITO-93).

    :param password: Contraseña a validar.
    :type password: str
    :return: Tupla (es_válida, mensaje_error).
    :rtype: tuple[bool, str]
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres."
    if REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "La contraseña debe contener al menos una letra mayúscula."
    if REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "La contraseña debe contener al menos una letra minúscula."
    if REQUIRE_DIGITS and not any(c.isdigit() for c in password):
        return False, "La contraseña debe contener al menos un dígito."
    if REQUIRE_SPECIAL_CHARS and not any(not c.isalnum() for c in password):
        return False, "La contraseña debe contener al menos un carácter especial."
    return True, ""


def permitir_solicitud(cliente, now=None):
    """Aplica límite fijo de solicitudes por cliente en una ventana temporal."""
    now = time.monotonic() if now is None else now
    requests = REQUEST_TIMESTAMPS[cliente]
    while requests and now - requests[0] >= RATE_LIMIT_WINDOW_SECONDS:
        requests.popleft()
    if len(requests) >= RATE_LIMIT_REQUESTS:
        return False
    requests.append(now)
    return True


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


def crear_identificador_configuracion(parametros: Mapping[str, Any]) -> str:
    """Crea un identificador estable para la configuración efectiva del análisis.

    :param parametros: Parámetros validados del análisis.
    :type parametros: Mapping[str, Any]
    :return: Identificador de revisión y huella corta de configuración.
    :rtype: str
    """
    configuracion = {
        "algorithm_revision": ALGORITHM_REVISION,
        "enhance_contrast": parametros["mejorar_contraste"],
        "noise_reduction": parametros["reducir_ruido"],
        "polarity": parametros["polaridad"],
        "sigma1": parametros["sigma1"],
        "sigma2": parametros["sigma2"],
    }
    serializada = json.dumps(configuracion, sort_keys=True, separators=(",", ":"))
    huella = hashlib.sha256(serializada.encode("utf-8")).hexdigest()[:12]
    return f"{ALGORITHM_REVISION}:{huella}"


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

    configuration_id = crear_identificador_configuracion(validated)
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
            "algorithm_revision": ALGORITHM_REVISION,
            "configuration_id": configuration_id,
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
    def _send_security_headers(self):
        """Add security headers to all responses (CITO-93)."""
        for header, value in SECURITY_HEADERS.items():
            self.send_header(header, value)
        # CORS headers
        origin = self.headers.get("Origin", "")
        if origin in CORS_ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", ", ".join(CORS_ALLOWED_METHODS))
        self.send_header("Access-Control-Allow-Headers", ", ".join(CORS_ALLOWED_HEADERS))
        self.send_header("Access-Control-Max-Age", str(CORS_MAX_AGE))

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_audited_response(self, payload, status, exito, detalles):
        """Envía una respuesta JSON y registra el evento operativo sin secretos."""
        registrar_acceso(self.path, self.command, exito, detalles)
        self._send_json(payload, status)

    def do_OPTIONS(self):
        """Handle CORS preflight requests (CITO-93)."""
        self.send_response(204)
        self._send_security_headers()
        self.end_headers()

    def _handle_refresh_token(self):
        """Handle refresh token endpoint (CITO-92)."""
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return error_response("Content-Length inválido", 400)
        if content_length <= 0:
            return error_response("Cuerpo JSON vacío", 400)
        if content_length > MAX_REQUEST_BODY_BYTES:
            return error_response("Cuerpo JSON demasiado grande", 413)

        raw = self.rfile.read(content_length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return error_response("JSON inválido", 400)

        refresh_token = payload.get("refresh_token")
        if not refresh_token or not isinstance(refresh_token, str):
            return error_response("`refresh_token` es obligatorio y debe ser string.", 400)

        claims = validar_refresh_token(refresh_token)
        if not claims:
            return error_response("Refresh token inválido o expirado.", 401)

        # Generate new access token and refresh token
        access_token = crear_token_jwt(claims["sub"], claims["role"])
        new_refresh_token = crear_refresh_token(claims["sub"], claims["role"])

        return {
            "ok": True,
            "token_type": "Bearer",
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "expires_in": JWT_EXPIRATION_SECONDS,
            "role": claims["role"],
        }, 200

    def do_GET(self):
        if self.path == "/api/v1/health":
            self._send_json({"ok": True, "api_version": "v1", "status": "healthy"}, 200)
            return
        self._send_json(
            {"ok": False, "error": {"code": 404, "message": "Endpoint no encontrado"}},
            404,
        )

    def do_POST(self):
        # Check body size first for endpoints that accept a body (CITO-79)
        if self.path in {"/api/v1/analyze", "/api/v1/auth/login", "/api/v1/auth/refresh"}:
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send_audited_response(
                    {"ok": False, "error": {"code": 400, "message": "Content-Length inválido"}},
                    400,
                    False,
                    "status=400,motivo=content_length_invalido",
                )
                return
            if content_length <= 0:
                self._send_audited_response(
                    {"ok": False, "error": {"code": 400, "message": "Cuerpo JSON vacío"}},
                    400,
                    False,
                    "status=400,motivo=cuerpo_vacio",
                )
                return
            if content_length > MAX_REQUEST_BODY_BYTES:
                self._send_audited_response(
                    {"ok": False, "error": {"code": 413, "message": "Cuerpo JSON demasiado grande"}},
                    413,
                    False,
                    "status=413,motivo=cuerpo_excesivo",
                )
                return

        if self.path not in {"/api/v1/analyze", "/api/v1/auth/login", "/api/v1/auth/refresh"}:
            self._send_audited_response(
                {"ok": False, "error": {"code": 404, "message": "Endpoint no encontrado"}},
                404,
                False,
                "status=404,motivo=endpoint_desconocido",
            )
            return

        if self.path == "/api/v1/auth/refresh":
            response, status = self._handle_refresh_token()
            self._send_audited_response(
                response,
                status,
                status == 200,
                f"status={status},motivo=refresh_token",
            )
            return

        # Read and parse JSON body for endpoints that need it
        raw = b""
        payload = None
        if self.path in {"/api/v1/analyze", "/api/v1/auth/login"}:
            raw = self.rfile.read(content_length)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                self._send_audited_response(
                    {"ok": False, "error": {"code": 400, "message": "JSON inválido"}},
                    400,
                    False,
                    "status=400,motivo=json_invalido",
                )
                return

            if not isinstance(payload, dict):
                self._send_audited_response(
                    {"ok": False, "error": {"code": 400, "message": "El cuerpo JSON debe ser un objeto."}},
                    400,
                    False,
                    "status=400,motivo=json_no_es_objeto",
                )
                return

        if self.path == "/api/v1/auth/refresh":
            response, status = self._handle_refresh_token()
            self._send_audited_response(
                response,
                status,
                status == 200,
                f"status={status},motivo=refresh_token",
            )
            return

        if self.path == "/api/v1/auth/login":
            response, status = autenticar_usuario(payload)
            self._send_audited_response(
                response,
                status,
                status == 200,
                f"status={status},motivo=login",
            )
            return

        if self.path == "/api/v1/analyze":
            # Check authentication FIRST (tests expect 401 before 400)
            identidad, authentication_error = validar_autenticacion(self.headers)
            if authentication_error:
                response, status = authentication_error
                self._send_audited_response(
                    response,
                    status,
                    False,
                    f"status={status},motivo=autenticacion",
                )
                return
            rol = identidad["role"] if identidad is not None else "desconocido"
            if rol not in ROLES_ANALISIS:
                self._send_audited_response(
                    {"ok": False, "error": {"code": 403, "message": "Rol sin acceso al análisis."}},
                    403,
                    False,
                    f"status=403,motivo=rol_no_autorizado,rol={rol}",
                )
                return

            # Check rate limit (tests expect 429 after 30 requests)
            if not permitir_solicitud(self.client_address[0]):
                self._send_audited_response(
                    {"ok": False, "error": {"code": 429, "message": "Demasiadas solicitudes."}},
                    429,
                    False,
                    "status=429,motivo=limite_solicitudes",
                )
                return

            # Now validate payload
            validated, validation_status = validate_payload(payload)
            if validation_status != 200:
                self._send_audited_response(
                    validated,
                    validation_status,
                    False,
                    f"status={validation_status},motivo=payload_invalido",
                )
                return

            # CITO-79: Additional security validations
            image_name = payload["image_name"]
            if not validar_ruta_segura(image_name):
                self._send_audited_response(
                    {"ok": False, "error": {"code": 400, "message": "`image_name` contiene rutas prohibidas."}},
                    400,
                    False,
                    "status=400,motivo=ruta_no_segura",
                )
                return

            path = validated["path"]
            if not validar_tamaño(path):
                self._send_audited_response(
                    {"ok": False, "error": {"code": 400, "message": "Imagen excede el límite de 64 KiB."}},
                    400,
                    False,
                    "status=400,motivo=imagen_excede_tamano",
                )
                return
            if not validar_contenido(path):
                self._send_audited_response(
                    {"ok": False, "error": {"code": 400, "message": "Imagen corrupta o vacía."}},
                    400,
                    False,
                    "status=400,motivo=contenido_invalido",
                )
                return

            response, status = analyze_from_payload(payload)
            configuracion = (
                response["input"]["configuration_id"] if status == 200 else "no_aplica"
            )
            self._send_audited_response(
                response,
                status,
                status == 200,
                f"status={status},rol={identidad['role']},configuracion={configuracion}",
            )
            return

        # Should not reach here
        self._send_audited_response(
            {"ok": False, "error": {"code": 404, "message": "Endpoint no encontrado"}},
            404,
            False,
            "status=404,motivo=endpoint_desconocido",
        )


def run_api(host="127.0.0.1", port=8000):
    server = HTTPServer((host, port), CitoCounterApiHandler)
    print(f"API CitoCounter v1 escuchando en http://{host}:{port}")
    print(
        "Endpoints: GET /api/v1/health, POST /api/v1/auth/login, "
        "POST /api/v1/analyze"
    )
    server.serve_forever()


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
    logger.info(
        json.dumps(
            {
                "endpoint": endpoint,
                "metodo": metodo,
                "exito": exito,
                "detalles": detalles,
            },
            ensure_ascii=False,
        )
    )


def exito_response(data, mensaje="Operación exitosa"):
    """Standardized success response (CITO-78/CITO-79)."""
    return {
        "ok": True,
        "api_version": "v1",
        "mensaje": mensaje,
        "data": data,
    }, 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API REST v1 de CitoCounter Proto.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    run_api(host=args.host, port=args.port)
