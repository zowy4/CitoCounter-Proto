# CITO-86: Manejo de casos especiales

**Estado:** Finalizado tecnicamente
**Alcance:** Superposicion celular, artefactos de tincion e iluminacion irregular.

## Estrategias integradas

| Caso | Estrategia | Implementacion | Evidencia automatizada |
|---|---|---|---|
| Nucleos en contacto | `watershed_picos` usa maximos locales de la transformada de distancia como marcadores | `src.analysis.watershed_separar_nucleos(..., usar_picos_locales=True)` | Dos discos sinteticos solapados producen dos contornos |
| Superposicion habitual | `watershed` conserva marcadores por componentes conectados | `src.analysis.analizar_nucleos(..., metodo_separacion="watershed")` | La revalidacion CITO-85 preserva F1=0.9315 |
| Artefactos de borde DoG | Mascara adaptativa de borde | `src.analysis.crear_mascara_borde` | Los bordes se excluyen y el centro se conserva |
| Ruido y artefactos de tincion | Filtro bilateral configurable | `src.preprocessing.reducir_ruido` | La desviacion estandar de ruido sintetico disminuye |
| Iluminacion irregular o bajo contraste | CLAHE adaptativo y control de calidad | `src.preprocessing.mejorar_contraste(..., metodo="auto")` | El contraste sintetico bajo mejora y se emite advertencia para imagen plana |

## Decisiones de diseno

`watershed_picos` es una estrategia explicita y no reemplaza a `watershed`.
Durante la regresion, convertir los picos locales en el comportamiento por
defecto redujo el F1 del conjunto CITO-85 a 0.2524 por sobresegmentacion. Por
ello el usuario o el experimento debe seleccionar la estrategia y registrarla.

La configuracion validada en CITO-85 se mantiene en `watershed`, con
`sigma1=5.0`, `sigma2=8.0` y apertura final de 5. Su revalidacion posterior a
esta actividad conserva F1=0.9315 sobre el conjunto sintetico de evaluacion.

## Pruebas reproducibles

```text
python -m unittest tests.test_cito86_casos_especiales tests.test_cito77_reglas tests.test_validar_metricas_cito23 -q
```

Resultado: 48 pruebas correctas.

## Limites

Estas pruebas usan imagenes sinteticas controladas y no validan rendimiento
clinico. Para imagenes reales se requieren anotaciones espaciales expertas,
un conjunto de desarrollo separado para elegir la estrategia y un conjunto de
evaluacion congelado. Los resultados del prototipo no constituyen diagnostico.
