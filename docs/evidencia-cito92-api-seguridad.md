# CITO-92: Autenticacion y rate limiting

`POST /api/v1/analyze` admite proteccion por clave de API:

```text
set CITO_API_KEY=clave-segura-no-versionada
```

Cuando la variable esta configurada, el cliente debe enviar
`X-API-Key`; una clave ausente o incorrecta devuelve `401`. El endpoint de
salud permanece publico. La API limita cada IP a 30 solicitudes por 60
segundos y devuelve `429` al excederlo.

La prueba HTTP `tests.test_api_v1.ApiV1HttpTests` verifica la respuesta `401`
sin clave y con clave incorrecta, el paso de autenticación con una clave
válida y el rechazo `429` al superar el límite. La ejecución focalizada
completó 20 pruebas correctamente el 17/oct/26.

También se implementó `POST /api/v1/auth/login` con JWT HS256 de una hora.
El despliegue debe proporcionar `CITO_JWT_SECRET` y `CITO_API_USERS` como
JSON externo con cada usuario, contraseña y rol. Solo `analista` y
`administrador` acceden a `POST /api/v1/analyze`; cualquier otro rol recibe
`403`. El secreto, las credenciales y los tokens no se almacenan en el
repositorio.

HTTPS, rotación de secretos, registro centralizado y roles persistentes
quedan sujetos a la infraestructura de despliegue y a CITO-93.
