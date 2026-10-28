# CITO-87: Documentacion tecnica completa

**Estado:** Finalizado tecnicamente

## Manual tecnico consolidado

| Tema | Fuente de verdad |
|---|---|
| Arquitectura, componentes y flujo de datos | [arquitectura_sistema.md](arquitectura_sistema.md) |
| Algoritmo DoG, reglas y metricas | [algoritmos_metricas.md](algoritmos_metricas.md) |
| Contratos del pipeline | [`src/contracts/pipeline_contract.py`](../src/contracts/pipeline_contract.py) |
| CLI, instalacion y desarrollo | [guide/cli.md](guide/cli.md), [guide/inicio.md](guide/inicio.md) y [guide/desarrollo.md](guide/desarrollo.md) |
| Dataset, anotaciones y experimentos | [guide/dataset.md](guide/dataset.md), [guide/etiquetado.md](guide/etiquetado.md) y [guide/experimentos.md](guide/experimentos.md) |
| API REST v1 | [evidencia-cito25-api-rest.md](evidencia-cito25-api-rest.md) |
| Interfaz y dashboard | [evidencia-cito26-interfaz.md](evidencia-cito26-interfaz.md) y [evidencia-cito27-dashboard.md](evidencia-cito27-dashboard.md) |
| Indicadores operativos | [evidencia-cito28-indicadores.md](evidencia-cito28-indicadores.md) |
| Validacion espacial y casos especiales | [evidencia-cito85-validacion.md](evidencia-cito85-validacion.md) y [evidencia-cito86-casos-especiales.md](evidencia-cito86-casos-especiales.md) |
| Seguridad, privacidad y alcance | [seguridad_privacidad.md](seguridad_privacidad.md), [CITO-68-alcance-clinico.md](CITO-68-alcance-clinico.md) y [CITO-69-privacidad.md](CITO-69-privacidad.md) |

## Decisiones de mantenimiento

- La documentacion se organiza por responsabilidad; este indice no duplica las
  guias especializadas.
- Todo cambio de pipeline debe actualizar la referencia tecnica correspondiente
  y añadir evidencia reproducible bajo `docs/`.
- Precision, sensibilidad, F1 e IoU solo se documentan como validacion cuando
  existe ground truth espacial valido y matching reproducible.
- El sistema es un prototipo de investigacion y no ofrece diagnostico clinico.
