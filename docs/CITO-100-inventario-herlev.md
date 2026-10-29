# CITO-100: Inventario de procedencia y cobertura Herlev local

**Actividad relacionada:** J-42, inventariar procedencia y cobertura de Herlev
**Rama revisada:** `MIGRACION`
**Fecha de revisión:** 2026-10-28
**Método:** inventario de rutas, extensiones, nombres estructurales, conteos y estado de seguimiento Git. Se revisó la forma textual de las anotaciones resumiendo su sintaxis, sin mostrar coordenadas; no se decodificaron ni reprodujeron imágenes.

## 1. Resumen ejecutivo

El checkout contiene un directorio `data/raw/im_Dyskeratotic/` con imágenes completas, imágenes recortadas, anotaciones de núcleo/citoplasma y 19 PNG cuyo propósito no se ha identificado en esta inspección. Todos los archivos encontrados en el directorio fuente están rastreados por Git. En cambio, las salidas convertidas a `data/ground_truth/herlev/` son artefactos locales sin seguimiento.

No se encontró documentación local que pruebe la procedencia oficial, licencia aplicable, autorización para redistribuir o utilizar el dataset, ni correspondencia completa de los recortes con los grupos de origen. La evidencia CITO-89 ya señala expresamente que licencia, acceso oficial y compatibilidad de etiquetas deben verificarse antes de usar Herlev. Por ello, **este inventario no aprueba la distribución, publicación ni evaluación científica del dataset**.

## 2. Inventario estructural

Conteos reproducidos en el checkout:

| Ubicación | BMP | DAT de núcleo | DAT de citoplasma | PNG | Total de archivos |
|---|---:|---:|---:|---:|---:|
| `data/raw/im_Dyskeratotic/` (raíz) | 223 | 813 | 813 | 19 | 1.868 |
| `data/raw/im_Dyskeratotic/CROPPED/` | 813 | 813 | 813 | 0 | 2.439 |
| **Total** | **1.036** | **1.626** | **1.626** | **19** | **4.307** |

Hallazgos de cobertura por nombre:

- La raíz tiene 223 identificadores de imagen completa con BMP; los archivos `.dat` de raíz usan esos mismos 223 identificadores.
- En la raíz se cuentan 813 polígonos de núcleo y 813 de citoplasma.
- `CROPPED/` contiene 813 BMP, 813 anotaciones de núcleo y 813 de citoplasma.
- Para cada identificador de imagen completa, los conteos de `.dat` de núcleo y citoplasma coinciden. El número de polígonos varía entre imágenes; no se ha probado que cada polígono corresponda a una célula visible ni que no existan anotaciones omitidas.
- Las 223 BMP de la raíz comparten dimensiones de 2048 × 1536 según los encabezados BMP. Esta comprobación no valida legibilidad, contenido ni integridad visual.
- Los 19 PNG de la raíz no fueron clasificados por propósito ni incluidos en los conteos de cobertura.

Los conteos de archivos y nombres son comprobaciones estructurales, **no una auditoría visual ni una validación de calidad de las anotaciones**.

## 3. Salidas de ground truth ya presentes en el entorno

En `data/ground_truth/herlev/` hay 450 archivos locales sin seguimiento por Git:

- 223 CSV en `cells/`.
- 223 máscaras PNG en `masks/`.
- 3 manifiestos CSV en `splits/` (`train`, `val`, `test`).

La estructura de los CSV, las cabeceras PNG y la falta de intersección de IDs entre los tres manifiestos se comprobaron por separado. Después de implementar el rasterizador J-44 se compararon, en memoria y sin escribir, las 223 máscaras de núcleos actuales contra las salidas locales:

- Todas tienen dimensión 1536 × 2048 y valores binarios `uint8`.
- Ninguna de las 223 máscaras coincide píxel a píxel con una rasterización nueva de los `.dat`.
- El IoU medio no ponderado entre máscaras existentes y nuevas es aproximadamente 0,9851.

La similitud agregada no explica ni valida la discrepancia. El origen puede ser una convención de conversión de coordenadas o un proceso de generación distinto; queda por investigar. Los controles estructurales tampoco demuestran que los CSV/máscaras sean visualmente correctos o libres de fuga entre imágenes completas y crops relacionados. No regenerar ni sobrescribir estos archivos hasta completar la actividad de preparación reproducible, documentar la convención del rasterizado y revisar diferencias.

### Conversión al esquema de cajas CSV (J-45)

Se implementó en `src/herlev_dataset.py` una conversión pura de polígonos nucleares a filas `Cell_ID,X,Y,Width,Height,Classification,Notes`, más un escritor que rechaza destinos existentes. La convención de salida queda definida así: X/Y son la esquina superior izquierda de la caja, en píxeles base cero; Width/Height incluyen ambos extremos después de redondear vértices al entero más cercano, igual que el rasterizador. Las cajas se limitan a las dimensiones de la imagen. Los IDs se numeran en el orden determinista de los polígonos; la clasificación debe entregarse explícitamente y las notas quedan vacías salvo que el llamador proporcione una.

La comparación exploratoria de las 813 filas locales contra cajas derivadas de los polígonos emparejados por imagen y orden no encontró coincidencias exactas con las convenciones de caja en coordenadas originales, caja redondeada ni centro de caja. Esto **no identifica la convención con la que se generaron los CSV existentes**. Por tanto, la nueva definición es una convención de salida documentada, no una reproducción de esos artefactos. No se escribieron ni modificaron CSV locales; primero deben investigarse las diferencias y auditarse visualmente.

### Agrupación para splits sin fuga (J-46)

Los manifiestos locales existentes asignan las 223 imágenes completas: train 156, val 33 y test 34. En una comprobación en memoria, los `image_id` coincidieron con los stems de `image_name` y cada imagen completa se encontró en el directorio fuente. Los 813 nombres de crops tuvieron exactamente un stem de imagen completa como prefijo; la asociación por prefijo más largo quedó implementada en `src/herlev_dataset.py` junto con la propagación de asignaciones y la validación para rechazar grupos ausentes, grupos sin elementos o grupos repartidos entre splits.

Al heredar, sin volver a sortear, la asignación actual de cada imagen completa, los crops quedan distribuidos en train 564, val 109 y test 140. Estos conteos prueban la aplicación estructural de la regla de agrupación para los nombres presentes, no la ausencia de parentescos biológicos no reflejados en nombres ni una auditoría de datos. El chequeo se hizo en memoria: no se escribieron manifiestos nuevos ni se cambiaron los archivos locales. La CLI de J-47 deberá exportar los manifiestos derivados de forma determinista a un destino nuevo.

### CLI determinista de preparación (J-47)

La lógica de preparación está en `src/herlev_preparation.py`; el punto de entrada `preparar_herlev.py` requiere rutas explícitas de fuente, splits y destino, además de la etiqueta fuente explícita. Produce `cells/`, `masks/` y manifiestos `splits/` deterministas, y conserva la asignación de cada imagen completa para sus crops. Rechaza destinos existentes y construye primero en un temporal hermano; no copia las imágenes fuente ni los `.dat`. Las pruebas usan fixtures sintéticos para confirmar hashes estables, manifiestos sin solapamiento, rechazo de salidas preexistentes y ausencia de resultados parciales ante errores.

El límite de archivo por imagen es 16 MiB. En el inventario local, 1.036 BMP miden entre 12.798 y 9.437.238 bytes; un máximo de 64 KiB impediría procesar 306 imágenes. La opción de CLI permite cambiar el máximo para otras fuentes. No se ejecutó una generación sobre el dataset local ni se crearon CSV/máscaras/manifiestos nuevos; la discrepancia J-45 y la auditoría visual J-48 siguen siendo bloqueantes para tratar sus salidas como ground truth aprobado.

## 4. Procedencia, permisos y estado Git

- No hay README de procedencia dentro de `data/raw/im_Dyskeratotic/` ni en `CROPPED/`.
- [La evidencia CITO-89 sobre datasets](./evidencia-cito89-datasets.md) mantiene pendiente verificar licencia, acceso oficial y compatibilidad de etiquetas de Herlev.
- Se encontraron 4.307 archivos fuente rastreados por Git bajo `data/raw/im_Dyskeratotic/`, incluidos BMP y `.dat`. Esto es un hallazgo de estado existente, no una recomendación para añadir más datos.
- El `.gitignore` actual no presenta una regla específica para esta ruta de subdirectorio Herlev. Los artefactos convertidos bajo `data/ground_truth/herlev/` permanecen sin seguimiento.
- No se modificaron ni se añadieron datos fuente en esta actividad. No publicar ni añadir imágenes originales, anotaciones brutas ni nuevos artefactos sensibles a commits/PR hasta resolver autorización y reglas de distribución.

**Riesgo:** el estado actual de Git contradice la intención documentada de no publicar imágenes originales. El seguimiento del proyecto debe decidir cómo contener este riesgo y preservar el historial/evidencia sin una eliminación o reescritura automática de datos.

## 5. Qué queda pendiente para cerrar la auditoría de datos

1. Registrar fuente oficial, versión/fecha de descarga, condiciones de uso y licencia verificables.
2. Confirmar autorización institucional y restricciones para almacenamiento, procesamiento y distribución.
3. Identificar qué representan los 19 PNG y registrar su origen.
4. Verificar el vínculo entre las imágenes completas y sus 813 crops; formar grupos de origen antes de aceptar los splits.
5. Realizar la auditoría visual definida en J-48/J-49 sobre una muestra de imágenes, polígonos y máscaras, documentando selección, cobertura y exclusiones sin adjuntar imágenes fuente.
6. Acordar con el responsable del repositorio cómo evitar futuras publicaciones indebidas de los archivos fuente rastreados. No retirar ni reescribir los datos existentes sin autorización explícita y un plan de preservación.

## 6. Conclusión para CITO-95

Herlev está disponible estructuralmente para investigación en el checkout, con anotaciones espaciales de núcleo/citoplasma en 223 imágenes completas y 813 crops. Sin embargo, la procedencia/licencia y la correspondencia visual no están acreditadas por la documentación local. La clase fuente observada es `im_Dyskeratotic`; el conjunto no demuestra cobertura de las demás clases Herlev ni permite generalización a ellas.

Hasta cerrar permisos, relación imagen-crop, auditoría visual y generación reproducible del ground truth, los artefactos locales no deben tratarse como conjunto de evaluación aprobado y no se debe reportar una métrica de rendimiento sobre ellos como evidencia validada.
