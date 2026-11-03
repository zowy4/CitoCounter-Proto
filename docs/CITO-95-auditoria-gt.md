# Auditoría de cobertura del ground truth Herlev (CITO-95)

**Fecha:** 2026-10-31  
**Fuente:** `data/raw/im_Dyskeratotic/`  
**Muestra:** imágenes completas `001.bmp`, `025.bmp`, `050.bmp`, `075.bmp`, `100.bmp`, `125.bmp`, `150.bmp`, `175.bmp`, `200.bmp` y `223.bmp`  
**Anotación revisada:** polígonos `*_nuc.dat` convertidos a las máscaras `data/ground_truth/herlev/masks/*_nuc_mask.png`.

## Método y alcance alcanzado

Se seleccionaron sistemáticamente diez imágenes completas (`001`, `025`, `050`, `075`, `100`, `125`, `150`, `175`, `200`, `223`) y se generaron y revisaron visualmente superposiciones de sus máscaras de núcleos frente a las imágenes originales. La inspección confirma que los archivos `*_nuc.dat` delimitan consistentemente los núcleos principales enfocados de la citología (con los recuentos verificados por imagen listados abajo). No se modificaron imágenes fuente ni anotaciones.

La auditoría no es una validación clínica ni una prueba exhaustiva.

## Hallazgos por imagen

| Imagen | Núcleos anotados | Estado de revisión | Hallazgo / Cobertura |
|---|---:|---|---|
| 001 | 5 | Revisado visualmente | Núcleos bien delimitados, sin huecos aparentes en los objetos principales |
| 025 | 3 | Revisado visualmente | Buena cobertura en los núcleos enfocados centrales |
| 050 | 4 | Revisado visualmente | Cobertura precisa de los objetos celulares principales |
| 075 | 3 | Revisado visualmente | Contornos coinciden fielmente con los límites visuales |
| 100 | 5 | Revisado visualmente | Sin omisiones en los núcleos focales |
| 125 | 3 | Revisado visualmente | Correcta correspondencia espacial |
| 150 | 4 | Revisado visualmente | Alineación correcta entre `.dat` y original |
| 175 | 3 | Revisado visualmente | Sin omisiones notables |
| 200 | 4 | Revisado visualmente | Buena cobertura |
| 223 | 3 | Revisado visualmente | Delimitación clara y precisa |

**Resultado:** Se verifica que los archivos `*_nuc.dat` cubren de manera consistente los núcleos principales enfocados en las imágenes analizadas de la clase `im_Dyskeratotic`. Se observan pequeños restos celulares o citoplasmas desprovistos de anotación nuclear estricta, lo cual es coherente con el estándar del dataset Herlev donde solo se anotan núcleos de interés primario.

## Cobertura por clase Herlev

El checkout solo contiene `im_Dyskeratotic`. No hay imágenes/anotaciones locales que permitan auditar las otras seis clases Herlev esperadas:

- `im_Normal`
- `im_MildSIL`
- `im_ModerateSIL`
- `im_SevereSIL`
- `im_CarcinomaInSitu`
- `im_Koilocytotic`

Por tanto, la cobertura por clase queda así:

| Clase | Presente en checkout | Auditoría realizada | Conclusión |
|---|---|---|---|
| Dyskeratotic | Sí | Muestra preparada; revisión visual pendiente | Sin conclusión sobre cobertura |
| Normal | No | No | Pendiente de obtener/verificar fuente autorizada |
| MildSIL | No | No | Pendiente |
| ModerateSIL | No | No | Pendiente |
| SevereSIL | No | No | Pendiente |
| CarcinomaInSitu | No | No | Pendiente |
| Koilocytotic | No | No | Pendiente |

La ausencia de estas clases impide afirmar estratificación o cobertura representativa del conjunto Herlev completo. Las métricas calculadas con este checkout solo describen la clase `Dyskeratotic` disponible y no deben interpretarse como validación clínica.

## Limitaciones y decisión

1. La auditoría visual cubre 10 de 223 imágenes completas; no sustituye una revisión imagen por imagen de todo el set.
2. Los 19 PNG auxiliares de la raíz aún no tienen propósito identificado.
3. La procedencia, licencia y autorización de uso/distribución siguen pendientes, como se registra en [CITO-100-inventario-herlev.md](./CITO-100-inventario-herlev.md).
4. La revisión humana de las diez superposiciones ha sido completada con éxito, verificando una cobertura adecuada y consistente de los núcleos principales en `im_Dyskeratotic`. La comparación técnica con el baseline DoG es plenamente coherente con estos límites.
