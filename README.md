# CitoCounter Proto

Prototipo de investigación para detectar y clasificar núcleos celulares en imágenes de citología mediante el filtro Difference of Gaussians (DoG) y una regla de área de referencia.

> **Aviso:** no es un dispositivo médico ni una herramienta de diagnóstico. Los resultados requieren revisión experta.

## Inicio rápido

```bash
python -m pip install -r requirements.txt
python verificar_entorno.py
python main.py data/raw/imagen.jpg --no-gui
```

Para abrir el dashboard:

```bash
streamlit run app.py
```

## Documentación

| Necesidad | Documento |
|---|---|
| Primera ejecución y prueba de humo | [Guía de inicio](docs/guide/inicio.md) |
| Analizar imágenes o lotes desde terminal | [Guía CLI](docs/guide/cli.md) |
| Importar y organizar imágenes | [Guía de dataset](docs/guide/dataset.md) |
| Registrar y evaluar experimentos | [Guía de experimentación](docs/guide/experimentos.md) |
| Etiquetar imágenes en formato YOLO | [Guía de etiquetado](docs/guide/etiquetado.md) |
| Contribuir o preparar GitHub | [Guía de desarrollo](docs/guide/desarrollo.md) |
| Riesgos, normativa y plan Jira | [Plan del proyecto](docs/plan-proyecto.md) |
| Índice de carpetas y scripts | [Mapa del proyecto](docs/README.md) |

## Estructura esencial

- `main.py`: pipeline CLI de análisis.
- `app.py`: dashboard Streamlit.
- `src/`: preprocesamiento, DoG, análisis y visualización.
- `crear_dataset.py`: importa y estandariza imágenes.
- `data/raw/`: imágenes de entrada; no subir imágenes sensibles.
- `data/results/`: resultados generados.
- `CitoDataset_v1/`: dataset de ejemplo y anotaciones.

## Estado y límites

El proyecto es un prototipo experimental. Los parámetros de detección deben calibrarse con datos autorizados y anotaciones expertas antes de comparar métricas o considerar cualquier uso clínico. Consulta el [plan de riesgos y requisitos](docs/plan-proyecto.md) para las limitaciones conocidas.

## Licencia

MIT. Consulta [LICENSE](LICENSE).
