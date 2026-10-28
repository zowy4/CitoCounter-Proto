# CitoCounter-Proto: Seguridad, Privacidad y Conformidad Normativa

## ACT-16 (CITO-37)

### Visión General

Este documento describe las consideraciones de seguridad, privacidad y cumplimiento normativo para el prototipo CitoCounter-Proto. Al ser un software de investigación y no un dispositivo médico, las medidas se enfocan en proteger la integridad de los datos, la privacidad del paciente y establecer una base para futuras certificaciones regulatorias.

### Amebas de Amenaza (STRIDE)

| Amenaza | Descripción | Control Implementado | Estado |
|---------|-------------|---------------------|--------|
| **Suplantación de usuario** | Acceso no autorizado al sistema o a resultados individuales | El sistema está diseñado para uso local/single-user; no hay autenticación multiusuario implementada | Documentado para futura implementación |
| **Manipulación de imágenes/resultados** | Modificación no autorizada de imágenes de entrada o resultados del pipeline | Rutas de archivo validadas; extensiones de archivo restringidas a `.jpg`, `.png`, `.tiff` | Validación en `main.py` |
| **Repudio por falta de auditoría** | Incapacidad para rastrear qué procesamiento se realizó en imágenes específicas | Bitácora de experimentos (`bitacora_experimentos.csv`) que registra: versión, dataset, parámetros, fecha, decisión | Implementado |
| **Exposición de datos** | Filtro de datos sensibles en logs, pantallas y resultados | No se incluyen datos de pacientes, nombres identificables ni metadatos clínicos en la salida del pipeline; `.gitignore` protege `data/raw/` y `mis_imagenes_nuevas/` | Cumplido |
| **Denegación de servicio por cargas grandes** | Cargas de imágenes muy grandes consumen recursos del sistema | Límite de tamaño de imagen en el CLI (`--max-pixels` con valor por defecto); procesamiento por lotes con control de memoria | Implementado en `main.py` |
| **Elevación de privilegios** | Ejecución de código arbitrario mediante entradas maliciosas | Sanitización de rutas de archivo; validación de que las rutas no escapen del directorio de trabajo | Implementado en `preprocessing.py` |

### Consideraciones OWASP

| Control OWASP | Descripción | Implementación en CitoCounter-Proto |
|---------------|-------------|-------------------------------------|
| **Validar extensión y contenido** | Verificar que los archivos de entrada tengan extensiones esperadas y contenido válido | `main.py` valida la extensión de imagen antes del procesamiento; OpenCV falla graceful si el formato es inválido |
| **Evitar rutas arbitrarias** | Prevenir path traversal attacks | Todas las rutas se resuelven relativas al directorio de trabajo; no se aceptan rutas con `..` | Validado en `main.py` |
| **Evitar nombres identificables** | No incluir identificadores de pacientes en nombres de archivo | Nombres de archivo de salida son genericos (`MUESTRA_001`, etc.); los nombres originales nunca se guardan en resultados | Cumplido (ver `.gitignore` y guía de usuario) |
| **Control de temporales** | Limpiar archivos temporales después del procesamiento | Los archivos en `mis_imagenes_nuevas/` son temporales y se documentan como entrada provisional; no se eliminan automáticamente pero se aconseja limpieza periódica | Documentado en guía de usuario |
| **No mostrar trazas al usuario** | Evitar mostrar información de depuración, stack traces o rutas completas al usuario | La interfaz de Streamlit y el CLI muestran solo resultados resumidos; errores se muestran mensajes genéricos | Implementado |
| **Gestionar secretos fuera del repositorio** | Contraseñas, claves API y tokens nunca deben commitearse | No hay secretos en el código; cualquier configuración futura usaría variables de entorno no versionadas | Por establecer |

### Privacidad y Protección de Datos

#### Inventario de Datos

Los datos manejados por CitoCounter-Proto incluyen:

| Tipo de Dato | Origen | Almacenamiento | Retención | Acceso |
|--------------|--------|----------------|-----------|--------|
| Imágenes de entrada | Usuario/científico | `data/raw/` (gitignorado) | Hasta que el usuario los elimine | Usuario solo |
| Resultados de análisis | Pipeline de procesamiento | `data/results/` | Hasta que el usuario los elimine | Usuario solo |
| Bitácora de experimentos | Pipeline de procesamiento | `bitacora_experimentos.csv` | Indefinida, pero documentada | Usuario solo |
| Metadatos clínicos (opcional) | CSV de datos clínicos | `CitoDataset_v1/metadata/clinical_data_synthetic.csv` | Según política del usuario | Usuario solo |

#### Anonimización

- **Ningún dato de paciente identificable** se incluye en los resultados del pipeline
- Los nombres de archivo de salida son genericos y no contienen información de paciente
- Los metadatos clínicos (si se usan) se tratan como datos sensibles y el usuario es responsable de su manejo

#### Eliminación y Retención

- El usuario es responsable de eliminar imágenes y resultados cuando ya no son necesarios
- `.gitignore` protege `data/raw/`, `mis_imagenes_nuevas/` y las imágenes de resultados de commiteo accidental
- El pipeline no elimina automáticamente archivos de entrada; solo genera archivos de salida en `data/results/`

#### Control de Acceso

- El sistema está diseñado para **uso single-user** en un entorno local
- No hay características de autenticación o autorización multiusuario implementadas
- Para implementación multiusuario futura, se requeriría: autenticación con bcrypt, JWT guards/RBAC, y validación de entradas DTO

### Conformidad Normativa

#### Estado Actual (Prototipo de Investigación)

- **No es un dispositivo médico**: CitoCounter-Proto se clasifica como software de investigación únicamente
- **No hay validación clínica**: Las métricas de precisión, recall, F1 e IoU requieren ground truth espacial válido y no deben presentarse como diagnóstico clínico
- **Uso educativo/de investigación**: El software está diseñado para fines de investigación y desarrollo, no para diagnóstico clínico

#### Pasos hacia la Conformidad Futura

Si el proyecto evoluciona hacia un producto regulado, los siguientes pasos serían necesarios:

1. **Validación clínica formal**: Estudios con múltiples citotecnólogos y ground truth consenso
2. **Sistema de gestión de calidad (QMS)**: Documentación de procesos, trazabilidad y control de cambios
3. **Certificaciones regulatorias**: Dependiendo del mercado, podría requerirse FDA 510(k), CE Mark u otras aprobaciones
4. **Gestión de riesgos**: Evaluación STRIDE/OWASP continua, como la documentada en este archivo
5. **Auditoría de dependencias**: Revisiones periódicas de todas las dependencias (OpenCV, NumPy, etc.) por vulnerabilidades

### Repositorio y Dependencias

#### .gitignore Protecciones

Los siguientes directorios y archivos están excluidos del repositorio Git:

```
data/raw/
mis_imagenes_nuevas/
data/results/*.jpg
data/results/*.png
data/results/*.tiff
bitacora_experimentos.csv
*.png
*.jpg
*.tiff
```

Esto asegura que:
- Las imágenes de paciente originales nunca se commiteen
- Los resultados de procesamiento temporales no se versionen
- La bitácora de experimentos (que contiene parámetros y decisiones) no se suba al repositorio

#### Dependencias Conocidas

| Dependencia | Versión | Consideraciones de Seguridad |
|-------------|---------|----------------------------|
| OpenCV | 4.x | Sin vulnerabilidades críticas conocidas en la versión usada; mantener actualizado |
| NumPy | 1.x | Actualizaciones de seguridad menores; ninguna crítica |
| Streamlit | 1.30+ | Actualizaciones de seguridad regulares recomendadas |

### Próximas Actividades Relacionadas

| Activación | Descripción | Dependencia |
|------------|-------------|-------------|
| **CITO-38 (ACT-17)** | Ejecutar pruebas de usabilidad con citotecnólogos | Requiere que el pipeline sea estable (CITO-36 completado) |
| **CITO-39 (ACT-18)** | Recopilar feedback de personal clínico y resolver cambios | Feedback de CITO-37 y CITO-38 |
| **CITO-43 (ACT-21)** | Implementar y validar correcciones del filtro DoG | Puede identificar riesgos de procesamiento de imágenes |

### Checklist de Seguridad para Nuevas Características

Antes de implementar cualquier nueva característica en CitoCounter-Proto, verificar:

- [ ] Las rutas de archivo están validadas y sanitizadas
- [ ] Las extensiones de archivo están restringidas a formatos esperados
- [ ] No se incluyen datos identificables en los nombres de archivo de salida
- [ ] Los errores no revelan trazas de pila ni rutas completas al usuario final
- [ ] Los datos sensibles no se logginguean accidentalmente
- [ ] El tamaño de la imagen de entrada está dentro de límites razonables
- [ ] Las dependencias tienen versiones conocidas y sin vulnerabilidades críticas
- [ ] La característica no compromete el modo single-user del sistema