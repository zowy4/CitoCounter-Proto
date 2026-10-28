# CitoCounter-Proto: Guía de Usuario y Manual de Instalación

## Índice

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación](#instalación)
3. [Uso Básico](#uso-básico)
4. [Procesamiento de Imágenes](#procesamiento-de-imágenes)
5. [Parámetros Avanzados](#parámetros-avanzados)
6. [Solución de Problemas](#solución-de-problemas)
7. [Preguntas Frecuentes](#preguntas-frecuentes)

## 1. Requisitos del Sistema

### Hardware
- Computadora con procesador x86_64 o ARM64
- Memoria RAM: mínimo 4 GB (recomendado 8 GB o más para procesamiento de lotes)
- Espacio en disco: 500 MB mínimo para resultados y bitácoras

### Software
- **Sistema operativo**: Linux (Ubuntu 20.04+, Debian 10+, o equivalente)
- **Python**: Versión 3.9 o superior
- **OpenCV**: Versión 4.5.0 o superior (se instala automáticamente con las dependencias)
- **NumPy**: Versión 1.20 o superior

### Dependencias Python
El proyecto utiliza un `requirements.txt` con las siguientes dependencias principales:

```bash
numpy
opencv-python
```

### Verificación de la Instalación
Después de instalar, verifique que el sistema funciona correctamente:

```bash
python main.py --help
```

Debería mostrar la ayuda de línea de comandos sin errores.

## 2. Instalación

### Opción A: Instalación desde el repositorio (recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/tu_usuario/CitoCounter-Proto.git
cd CitoCounter-Proto

# Crear un entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar la instalación
python main.py --help
```

### Opción B: Instalación rápida (modo desarrollo)

```bash
# Clonar el repositorio
git clone https://github.com/tu_usuario/CitoCounter-Proto.git
cd CitoCounter-Proto

# Ejecutar directamente sin instalar (usa el Python del sistema)
python main.py --help
```

### Verificar Dependencias del Sistema
Algunas funcionalidades pueden requerir bibliotecas del sistema:

```bash
# En Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender1

# Verificar instalación de OpenCV
python -c "import cv2; print(cv2.__version__)"
```

## 3. Uso Básico

### Modo Interactivo (con ventana gráfica)

```bash
# Procesar una imagen individual
python main.py data/raw/MUESTRA_018.jpg

# El sistema mostrará:
# - Ventana con los núcleos detectados (semáforo: verde = normal, rojo = riesgo)
# - Resultados en consola (total, normales, sospechosas)
# - Bitácora actualizada en bitacora_experimentos.csv
# - Resultados guardados en data/results/
```

### Modo Sin Ventana Gráfica (lote)

```bash
# Procesar una carpeta completa
python main.py data/raw --lote --no-gui

# O con parámetros personalizados
python main.py data/raw --lote --no-gui --sigma1 7.0 --sigma2 8.0 --polaridad nucleos-oscuros
```

### Modo con Identificador de Bitácora

```bash
# Cada experimento debe tener un identificador único
python main.py data/raw/MUESTRA_018.jpg --bitacora CAL-001

# O en modo lote
python main.py data/raw --lote --no-gui --bitacora EXP-2024-01
```

## 3. Parámetros Avanzados

### Parámetros del Filtro DoG

| Parámetro | Descripción | Valor por defecto | Recomendación |
|-----------|-------------|-------------------|---------------|
| `sigma1` | Sigma primera Gaussian | 7.0 | 5.0 - 10.0 |
| `sigma2` | Sigma segunda Gaussian | 8.0 | 1.6-2.0 × sigma1 |

**Relación recomendada:** sigma2 debe ser aproximadamente 1.6 a 2.0 veces sigma1.
Esta relación determina el tamaño máximo de los núcleos que el sistema puede detectar.

### Parámetros de Preprocesamiento

| Parámetro | Descripción | Valor por defecto | Cuándo usar |
|-----------|-------------|-------------------|-------------|
| `--ruido` | Activar reducción de ruido bilateral | False | Imágenes con mucho ruido de fondo |
| `--no-contraste` | Desactivar mejora de contraste CLAHE | False | Iluminación ya uniforme |
| `--polaridad` | Polaridad de núcleos | 'nucleos-claros' | 'nucleos-oscuros' para imágenes de campo claro (Papanicolaou, EDF) |

### Parámetros de Bitácora

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `--bitacora` | Identificador de experimento | `CAL-001`, `EXP-2024-01`, `CITO-32` |

**Recomendación:** Cada experimento debe tener un identificador único para poder rastrear los resultados en la bitácora (`bitacora_experimentos.csv`).

## 4. Procesamiento de Imágenes

### Flujo Recomendado

1. **Probar una imagen primero:**
   ```bash
   python main.py data/raw/MUESTRA_018.jpg --no-gui
   ```

2. **Revisar la bitácora y el resultado:**
   - Consola: total de núcleos, normales, sospechosas
   - Ventana: anotaciones visuales (verde = normal, rojo = riesgo)

3. **Cambiar un solo parámetro:**
   - No cambie varios parámetros a la vez durante la calibración
   - Use `--bitacora ID` para identificar el cambio

4. **Repetir con un ID distinto:**
   ```bash
   python main.py data/raw/MUESTRA_018.jpg --bitacora CAL-002
   ```

5. **Procesar lote completo cuando esté listo:**
   ```bash
   python main.py data/raw --lote --no-gui --bitacora EXP-001
   ```

### Salidas del Sistema

#### Resultados en Consola
```
🔧 Preprocesamiento: CLAHE={'OFF' if args.no_contraste else 'ON'}, Ruido={'ON' if args.ruido else 'OFF'}
🔧 Preprocesamiento: CLAHE={'OFF'}, Ruido={'ON'}
  σ1=7.0, σ2=8.0
  📊 Contraste: 46.48
📅 22/09/2026 18:17:50 Procesando: MUESTRA_018.jpg
🏁  Preprocesamiento: CLAHE={'OFF'}, Ruido={'OFF'}
  🔢 Total: 1038
  🟢 Normales: 544
  🔴 Sospechosas: 494
```

#### Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `data/results/` | Resultados de procesamiento (imágenes anotadas, máscaras) |
| `bitacora_experimentos.csv` | Registro de todos los experimentos con parámetros y métricas |
| `data/results/graficas_tesis/` | Gráficas para tesis/informe |
| `data/results/screenshots/` | Capturas de pantalla de las ventanas de resultado |

### Bitácora de Experimentos (`bitacora_experimentos.csv`)

La bitácora se actualiza automáticamente después de cada ejecución y contiene:

| Columna | Descripción |
|---------|-------------|
| `fecha` | Fecha y hora del procesamiento |
| `ruta_imagen` | Ruta de la imagen procesada |
| `sigma1` | Sigma primera Gaussian |
| `sigma2` | Sigma segunda Gaussian |
| `polaridad` | 'nucleos-claros' o 'nucleos-oscuros' |
| `metodo_separacion` | None, 'watershed', 'maximos_locales' |
| `total_celulas` | Total de núcleos detectados |
| `normales` | Núcleos normales |
| `sospechosas` | Núcleos sospechosos |
| `contraste` | Desviación estándar de la imagen preprocesada |
| `bitacora` | Identificador de experimento |

**Ejemplo de fila en la bitácora:**
```
22/09/2024 18:17:50,data/raw/MUESTRA_018.jpg,7.0,8.0,nucleos-oscuros,None,1038,544,494,46.48,CAL-001
```

## 5. Solución de Problemas

### Problemas Comunes

| Problema | Causa Posible | Solución |
|----------|---------------|----------|
| "No se pudo cargar la imagen" | Ruta incorrecta o archivo dañado | Verifique la ruta y asegúrese de que es una imagen válida |
| "Ventana gráfica no aparece" | Modo sin `--no-gui` no especificado o entorno sin display | Use `--no-gui` o ejecute en servidor remoto |
| "Resultados muy pocos/f muchos" | Parámetros sigma1/sigma2 no adecuados | Ajuste sigma1 en rango 5.0-10.0 |
| "Muchos falsos positivos" | Ruido no filtrado | Active `--ruido` o ajuste parámetros de filtrado |
| "Muchos falsos negativos" | Contraste muy bajo | Active `--contraste` (por defecto) o ajuste polaridad |
| "Error de importación" | Dependencias faltantes | Ejecute `pip install -r requirements.txt` |

### Modos de Depuración

```bash
# Ver detalles adicionales de preprocesamiento
python main.py data/raw/MUESTRA_018.jpg --verbose

# Solo consola, sin ventanas
python main.py data/raw/MUESTRA_018.jpg --no-gui

# Probar diferentes sigmas
python main.py data/raw/MUESTRA_018.jpg --sigma1 5.0 --sigma2 8.0 --no-gui
```

### Obtener Ayuda

```bash
# Ayuda general
python main.py --help

# Ayuda específica de parámetros
python main.py --help-full  # Si está disponible
```

## 6. Preguntas Frecuentes

### P: ¿Puedo procesar imágenes de diferentes fabricantes de microscopios?
R: Sí, pero puede ser necesario ajustar los parámetros sigma1/sigma2 y la polaridad. El sistema está diseñado para funcionar con imágenes de microscopios de campo claro (Papanicolaou/EDF) y fluorescencia.

### P: ¿Por qué a veces detecto núcleos que no son células?
R: Estos pueden ser artefactos de tinción, polvo en el portaobjetos o estructuras no celulares. El sistema incluye filtrado por tamaño y circularidad para minimizar esto, pero algunos falsos positivos pueden permanecer. Se recomienda revisar los resultados sospechosos.

### P: ¿Con qué frecuencia debo calibrar los parámetros?
R: Se recomienda calibrar:
- Al comenzar un nuevo lote de muestras
- Cuando cambie el fabricante o tipo de portaobjetos
- Cuando note cambios significativos en la calidad de las imágenes
- Como mínimo, cada 10-15 experimentos diferentes

### P: ¿Puedo guardar y reutilizar configuraciones de parámetros?
R: No hay una función de guardar configuraciones explícita, pero puede:
- Registrar los parámetros en su propia bitácora externa
- Usar el identificador `--bitacora` para rastrear configuraciones
- Los valores por defecto (sigma1=7.0, sigma2=8.0) funcionan para la mayoría de los casos

### P: ¿Es necesario tener conocimientos de microscopía para usar el sistema?
R: No es obligatorio, pero útil. El sistema está diseñado para ser accesible, pero el personal clínico puede proporcionar retroalimentación valiosa sobre los resultados. Se recomienda la validación por personal calificado.

## 7. Referencias y Recursos Adicionales

### Documentación del Proyecto
- `docs/arquitectura_sistema.md` - Arquitectura general del sistema
- `docs/algoritmos_metricas.md` - Algoritmos y métricas detalladas
- `README.md` - Índice y enlaces rápidos

### Documentación de OpenCV
- https://docs.opencv.org/
- Funciones clave: `cv2.imread`, `cv2.cvtColor`, `cv2.GaussianBlur`, `cv2.threshold`, `cv2.findContours`, `cv2.distanceTransform`, `cv2.watershed`

### Recursos de Citología Cervical
- Guías de la OMS para citología cervical
- Estándares de la Colegio Americano de Patólogos (CAP)
- Publicaciones sobre detección automática de núcleos

### Soporte
- Para problemas técnicos, revise la bitácora (`bitacora_experimentos.csv`)
- Revise los archivos de log en la consola
- Asegúrese de que todas las dependencias estén instaladas

---

**Aviso Legal:** 
CitoCounter-Proto es un prototipo de investigación para detección de núcleos en citología cervical. No es software de diagnóstico ni un dispositivo médico. Los resultados deben ser validados por personal calificado antes de cualquier toma de decisiones clínicas.

**Copyright:** 2026 CitoCounter-Proto. Todos los derechos reservados.
