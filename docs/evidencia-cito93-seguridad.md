# CITO-93: Endurecimiento de seguridad

## Evidencia local

- `python -m pip check`: sin requisitos rotos.
- La API escucha en `127.0.0.1` por defecto.
- CITO-92 agrega clave de API opcional, rate limiting, JWT HS256 y control
  de acceso por roles.
- `registrar_acceso` registra eventos de auditoría como JSON estructurado, sin
  incluir claves, contraseñas ni tokens. La prueba focalizada comprueba el
  formato del evento.

## HTTPS y despliegue

HTTPS requiere un certificado y clave privada administrados fuera del
repositorio, idealmente con terminación TLS en un proxy inverso. No se generan
ni versionan certificados de prueba para este prototipo.

Antes de exponer la API se debe configurar TLS, secretos del entorno, rotación
de claves, registro centralizado, retención y monitoreo. Las actualizaciones de
dependencias deben evaluarse con pruebas de compatibilidad antes de aplicarse.
