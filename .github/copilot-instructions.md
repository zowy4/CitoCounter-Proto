# CitoCounter-Proto: instrucciones para Copilot

## Contexto

- Es un prototipo de investigacion en Python para detectar y clasificar nucleos en citologia cervical con OpenCV, DoG y reglas de area. No es software de diagnostico ni un dispositivo medico.
- Punto de entrada CLI: `main.py`. Interfaz local: `app.py` con Streamlit. La logica del pipeline vive en `src/`:
  - `preprocessing.py`: carga, gris, contraste y calidad de imagen.
  - `dog_filter.py`: filtro Difference of Gaussians; conservar la resta en `float32` antes de normalizar.
  - `analysis.py`: contornos, filtros de area y clasificacion.
  - `visualization.py`: paneles y salidas visuales.
- Consulta [README.md](../../README.md) como indice y enlaza, no dupliques, las guias de [dataset](../docs/guide/dataset.md), [experimentos](../docs/guide/experimentos.md), [plan del proyecto](../docs/plan-proyecto.md) y [seguimiento Jira](../docs/guia-maestra-desarrollo.md).

## Comandos de trabajo

```bash
python -m pip install -r requirements.txt
python verificar_entorno.py
python -m unittest discover -s tests -v
python validar_consistencia_dataset.py
python main.py data/raw --lote --no-gui --sigma1 7.0 --sigma2 8.0
python calcular_metricas_cito23.py
streamlit run app.py
```

- Ejecuta la prueba mas especifica disponible despues de cada cambio. Para cambios en datos o anotaciones, ejecuta tambien `python validar_consistencia_dataset.py`.
- Ejecuta `git diff --check` antes de preparar cambios para revision o commit.

## Datos, evidencia y seguridad

- No añadas ni publiques imagenes originales, anotaciones brutas, datos de pacientes o resultados individuales. `.gitignore` protege `data/raw/`, `mis_imagenes_nuevas/` y las imagenes de resultados.
- `mis_imagenes_nuevas/` es entrada temporal; `crear_dataset.py` estandariza imagenes en `data/raw/`; `data/results/` conserva evidencia reproducible.
- Las metricas de precision, recall, F1 e IoU requieren ground truth espacial valido. No presentes conteos aproximados o resultados sin correspondencia espacial como validacion clinica.
- Conserva para cada experimento: version, dataset, parametros, fecha, evidencia y decision. No cambies varios parametros a la vez durante una calibracion.

## Convenciones de implementacion

- Mantener Python sencillo y modular; seguir el estilo existente con funciones en espanol y docstrings descriptivos.
- Los valores en `src/analysis.py` son provisionales hasta una calibracion respaldada por datos y ground truth. No afirmar que estan clinicamente validados.
- Agrega una prueba de regresion bajo `tests/` al corregir comportamiento del pipeline o validadores de dataset.
- Evita refactors no relacionados y no reviertas cambios no realizados en la sesion.

## Git y Jira

- Trabaja en una rama de actividad `CITO-xx-...`. Antes de editar, ejecuta `git fetch origin --prune`, `git status -sb` y comprueba la rama de seguimiento.
- Si la rama remota esta eliminada (`[gone]`) o `origin/main` tiene cambios nuevos, no hagas push ni merge automatico: informa el desfase y pide una rama de destino o una decision de integracion.
- Usa commits convencionales e incluye la clave Jira, por ejemplo: `feat(CITO-23): ...`.
- Jira es la fuente de verdad para estados. Adjunta evidencia reproducible antes de pasar a `En revision`; usa `Hecha` solo tras revision y criterios de aceptacion cumplidos.