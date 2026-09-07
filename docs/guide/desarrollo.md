# Desarrollo, contribución y GitHub

## Entorno local

```bash
python -m pip install -r requirements.txt
python verificar_entorno.py
```

Prueba los cambios con el flujo afectado y evita incluir imágenes clínicas, resultados personales o secretos.

## Estilo y cambios

- Sigue PEP 8 y usa nombres descriptivos.
- Mantén módulos pequeños y documenta funciones públicas.
- Haz cambios enfocados y revisables.
- Usa ramas por cambio y pull requests.
- Describe en el commit qué cambió y por qué.

## Contribuir

1. Abre un issue si reportas un bug o una mejora.
2. Incluye pasos reproducibles, entorno y comportamiento esperado/observado.
3. Crea una rama, implementa y prueba el cambio.
4. Abre un pull request con el alcance y la evidencia de validación.

Los cambios en el algoritmo DoG, parámetros de clasificación, datos o seguridad requieren revisión antes de integrarse.

## Publicar en GitHub

Si el remoto aún no existe:

```bash
git remote add origin https://github.com/USUARIO/CitoCounter-Proto.git
git branch -M main
git push -u origin main
```

Antes de publicar, revisa `git status`, `.gitignore`, historial y archivos staged. Nunca subas imágenes identificables, tokens ni bitácoras con datos sensibles.

## Alcance científico

CitoCounter Proto es un prototipo de investigación. Las contribuciones deben conservar la advertencia de no diagnóstico y documentar dataset, parámetros y limitaciones cuando afecten resultados.
