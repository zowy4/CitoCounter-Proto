# CITO-93: Endurecimiento de seguridad

## Evidencia local

- `python -m pip check`: sin requisitos rotos.
- La API escucha en `127.0.0.1` por defecto.
- CITO-92 agrega clave de API opcional, rate limiting, JWT HS256 y control
  de acceso por roles.
- `registrar_acceso` registra eventos de auditoría como JSON estructurado, sin
  incluir claves, contraseñas, tokens, cargas de imagen ni nombres de
  imágenes. Incluye resultados exitosos y rechazos de autenticación,
  autorización, límite de solicitudes y validación.
- La suite focalizada de API verifica el formato, el rechazo `401` auditado y
  el login sin credenciales en la bitácora (22 pruebas correctas,
  17/oct/26).

## HTTPS y despliegue

HTTPS requiere un certificado y clave privada administrados fuera del
repositorio, idealmente con terminación TLS en un proxy inverso. No se generan
ni versionan certificados de prueba para este prototipo.

Antes de exponer la API se debe configurar TLS, secretos del entorno, rotación
de claves, registro centralizado, retención y monitoreo. Las actualizaciones de
dependencias deben evaluarse con pruebas de compatibilidad antes de aplicarse.
