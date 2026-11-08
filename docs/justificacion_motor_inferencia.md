# Justificación y Selección del Motor de Inferencia (Fase 2.1)

## 1. Contexto y Objetivos

Para el análisis citológico en tiempo real (computadora integrada, cámaras USB y montura C de microscopio) con CitoCounter-Proto, el motor de inferencia debe satisfacer simultáneamente dos requisitos clave:
1. **Latencia ultra baja**: Tiempo de inferencia inferior a **100 ms por fotograma** (≥ 10 FPS) sin GPU dedicada obligatoria para no congelar la interfaz de usuario en streaming.
2. **Capacidad de segmentación celular precisa**: Detección de núcleos individuales, bordes para cálculo de área nuclear y discriminación de anomalías morfológicas (células normales vs sospechosas).

---

## 2. Comparativa de Modelos Evaluados

| Criterio | DoG Optimizado (Clásico) | YOLOv8-nano / Ultralytics | MobileNet / Segmentadores DL (Cellpose/StarDist) |
|---|---|---|---|
| **Latencia CPU (i5/i7)** | ~15 - 30 ms | ~45 - 75 ms | ~120 - 350 ms |
| **FPS Estimado en CPU** | > 30 FPS | ~15 - 22 FPS | ~3 - 8 FPS |
| **Requisito GPU** | No requerido | Opcional | Recomendado |
| **Complejidad de despliegue** | Mínima (OpenCV / NumPy puro) | Media (PyTorch / ONNX Runtime) | Alta (PyTorch + dependencias pesadas) |
| **F1-Score en Núcleos Claros** | 0.9419 (calibrado) | ~0.91 - 0.93 | > 0.94 |
| **Consumo de Memoria** | < 50 MB | ~150 - 250 MB | > 800 MB |

---

## 3. Justificación y Arquitectura Híbrida Seleccionada

Se selecciona una **Estrategia Híbrida Jerárquica** gestionada por `SelectorMotorInferencia`:

1. **Motor Primario en Streaming (Tiempo Real - DoG Optimizado)**:
   - Configuración: $\sigma_1 = 5.0$, $\sigma_2 = 8.0$, polaridad núcleo-claro y separación watershed optimizada.
   - Ofrece latencia constante de 20 ms (~50 FPS), ideal para el seguimiento interactivo del microscopista mientras desplaza la platina.

2. **Motor Secundario de Alta Precisión (Bajo Demanda / Fotograma Clave - YOLOv8n / Cellpose)**:
   - Se activa cuando el usuario detiene el movimiento o solicita una confirmación diagnóstica detallada sobre un fotograma específico.

Esta arquitectura garantiza una fluidez total en la visualización interactiva y máxima precisión cuando el patólogo o citotecnólogo lo requiere.
