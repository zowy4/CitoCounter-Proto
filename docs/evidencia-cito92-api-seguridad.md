# CITO-92: Autenticacion y rate limiting

`POST /api/v1/analyze` admite proteccion por clave de API:

```text
set CITO_API_KEY=clave-segura-no-versionada
```

Cuando la variable esta configurada, el cliente debe enviar
`X-API-Key`; una clave ausente o incorrecta devuelve `401`. El endpoint de
salud permanece publico. La API limita cada IP a 30 solicitudes por 60
segundos y devuelve `429` al excederlo.

No se almacenan claves en el repositorio. Estos controles son locales al
prototipo; JWT, roles persistentes y HTTPS quedan sujetos a infraestructura
de despliegue y a CITO-93.
