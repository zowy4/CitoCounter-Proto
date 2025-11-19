# 📚 ÍNDICE MAESTRO - CitoCounter Proto

## 🎯 Guía de Navegación del Proyecto

---

## 🚀 INICIO RÁPIDO

### Si es tu PRIMERA VEZ:
1. **Lee primero:** [`RESUMEN_EJECUTIVO.md`](RESUMEN_EJECUTIVO.md) (5 min)
2. **Sigue:** [`INSTRUCCIONES_RAPIDAS.md`](INSTRUCCIONES_RAPIDAS.md) (10 min)
3. **Ejecuta:** `py verificar_entorno.py`
4. **Prueba:** `py main.py`

### Si ya configuraste el sistema:
1. **Descarga:** Imagen de Pap smear de Google
2. **Guarda:** En `data/raw/muestra_prueba.jpg`
3. **Ejecuta:** `py main.py`
4. **Documenta:** Completa `bitacora_experimentos.csv`

---

## 📖 DOCUMENTACIÓN POR TIPO DE USUARIO

### 👨‍🔬 Investigador (Realizando experimentos)
```
1. INSTRUCCIONES_RAPIDAS.md          ← Checklist de 10 minutos
2. CHECKLIST_IMPRIMIBLE.md           ← Para imprimir y usar al lado PC
3. docs/GUIA_PRIMER_DISPARO.md       ← Primera prueba detallada
4. docs/PLANTILLA_BITACORA.md        ← Cómo documentar experimentos
```

### 👨‍💻 Desarrollador (Modificando código)
```
1. README.md                         ← Arquitectura general
2. src/*.py                          ← Código fuente comentado
3. requirements.txt                  ← Dependencias
```

### 📝 Escritor de Tesis (BM5/BM6)
```
1. bitacora_experimentos.csv         ← Datos de experimentos
2. IMPLEMENTACION_COMPLETADA.md     ← Qué se implementó y por qué
3. analizar_bitacora.py              ← Análisis estadístico
4. data/results/screenshots/         ← Evidencia visual
```

### 🎓 Asesor/Revisor (Evaluando el proyecto)
```
1. RESUMEN_EJECUTIVO.md              ← Estado completo del proyecto
2. IMPLEMENTACION_COMPLETADA.md     ← Cumplimiento de requisitos
3. docs/                             ← Toda la documentación
```

---

## 📂 MAPA DE ARCHIVOS

### 📄 Documentos de Nivel Superior (Raíz)

| Archivo | Propósito | Cuándo Usar |
|---------|-----------|-------------|
| `RESUMEN_EJECUTIVO.md` | Vista general del proyecto | Primera lectura |
| `INSTRUCCIONES_RAPIDAS.md` | Checklist 10 minutos | Antes de cada prueba |
| `IMPLEMENTACION_COMPLETADA.md` | Qué se implementó | Para reportes/tesis |
| `CHECKLIST_IMPRIMIBLE.md` | Guía paso a paso | Durante experimentos |
| `README.md` | Documentación técnica | Referencia general |

### 🐍 Scripts Ejecutables

| Script | Función | Comando |
|--------|---------|---------|
| `main.py` | Procesar imágenes | `py main.py` |
| `verificar_entorno.py` | Diagnóstico del sistema | `py verificar_entorno.py` |
| `analizar_bitacora.py` | Análisis de experimentos | `py analizar_bitacora.py` |

### 📊 Archivos de Datos

| Archivo | Contenido | Editar |
|---------|-----------|--------|
| `bitacora_experimentos.csv` | Registro de experimentos | Sí (campos manuales) |
| `requirements.txt` | Dependencias Python | No |

### 📁 Carpetas Principales

| Carpeta | Contenido | Acción |
|---------|-----------|--------|
| `src/` | Código fuente | Leer/modificar módulos |
| `data/raw/` | Imágenes originales | Colocar imágenes aquí |
| `data/results/` | Resultados procesados | Ver outputs |
| `data/results/screenshots/` | Capturas de pantalla | Guardar evidencia |
| `docs/` | Guías detalladas | Consultar cuando necesites |

---

## 🎯 FLUJO DE TRABAJO RECOMENDADO

### Fase 1: Configuración Inicial (Una sola vez)
```
1. Leer RESUMEN_EJECUTIVO.md
2. Ejecutar: py verificar_entorno.py
3. Si hay errores: py -m pip install -r requirements.txt
4. Leer INSTRUCCIONES_RAPIDAS.md
```

### Fase 2: Primera Prueba
```
1. Descargar imagen de Pap smear de Google
2. Guardar como: data/raw/muestra_prueba.jpg
3. Leer docs/GUIA_PRIMER_DISPARO.md
4. Ejecutar: py main.py
5. Capturar screenshot del panel 2×2
6. Completar bitacora_experimentos.csv
```

### Fase 3: Experimentación Iterativa
```
Para cada nueva prueba:
1. Imprimir CHECKLIST_IMPRIMIBLE.md (opcional)
2. Decidir qué parámetro ajustar
3. Actualizar parámetros en main.py
4. Ejecutar: py main.py
5. Documentar en bitácora
6. Repetir
```

### Fase 4: Análisis de Resultados
```
Después de 10+ experimentos:
1. Ejecutar: py analizar_bitacora.py
2. Revisar estadísticas generadas
3. Identificar mejores parámetros
4. Generar gráficas para tesis
```

---

## 🔍 BÚSQUEDA RÁPIDA

### "¿Cómo hago para...?"

#### Configurar el entorno por primera vez
→ Ver: `INSTRUCCIONES_RAPIDAS.md` > Sección "Verificar Entorno"

#### Ejecutar mi primera prueba
→ Ver: `docs/GUIA_PRIMER_DISPARO.md`

#### Documentar un experimento
→ Ver: `docs/PLANTILLA_BITACORA.md`

#### Interpretar el filtro DoG
→ Ver: `docs/GUIA_PRIMER_DISPARO.md` > "Criterios de Evaluación"

#### Ajustar parámetros Sigma
→ Ver: `README.md` > "Calibración del Sistema"

#### Analizar múltiples experimentos
→ Ejecutar: `py analizar_bitacora.py`

#### Resolver errores
→ Ver: `RESUMEN_EJECUTIVO.md` > "Troubleshooting Rápido"

#### Entender el código fuente
→ Ver: `src/[modulo].py` (Código completamente comentado)

#### Preparar datos para la tesis
→ Ver: `IMPLEMENTACION_COMPLETADA.md` > "Para el Documento de Tesis"

---

## 📚 DOCUMENTACIÓN DETALLADA

### Carpeta `docs/`

| Documento | Tema | Páginas |
|-----------|------|---------|
| `GUIA_PRIMER_DISPARO.md` | Primera prueba completa | ~5 |
| `PLANTILLA_BITACORA.md` | Cómo usar la bitácora | ~4 |
| `INSTRUCCIONES_BITACORA.md` | Introducción a bitácora | ~1 |

### Carpeta `src/`

| Módulo | Contenido | LOC* |
|--------|-----------|------|
| `dog_filter.py` | Filtro DoG + utilidades | ~150 |
| `analysis.py` | Regla 3x + clasificación | ~250 |
| `preprocessing.py` | CLAHE + mejoras | ~200 |
| `visualization.py` | Paneles + gráficos | ~300 |
| `__init__.py` | Metadata del proyecto | ~10 |

*LOC = Lines of Code (con comentarios)

---

## 🎓 RECURSOS PARA LA TESIS

### Sección BM5 (Análisis de Resultados)
**Archivos clave:**
- `bitacora_experimentos.csv` → Tabla de resultados
- `data/results/screenshots/` → Figuras
- `analizar_bitacora.py` → Estadísticas

**Contenido sugerido:**
```
1. Tabla: Parámetros de los 5 mejores experimentos
2. Gráfica: Sigma1 vs. Precisión
3. Figura: Panel 2×2 del mejor experimento
4. Matriz de confusión (si validaste con experto)
```

### Sección BM6 (Reproducibilidad)
**Archivos clave:**
- `requirements.txt` → Dependencias exactas
- `main.py` → Código ejecutable
- `IMPLEMENTACION_COMPLETADA.md` → Justificación

**Contenido sugerido:**
```
1. Snippet de requirements.txt
2. Diagrama de flujo del pipeline (main.py)
3. Extracto de bitácora mostrando trazabilidad
4. Instrucciones de instalación del README
```

### Anexos
**Incluir:**
- Código completo de `src/dog_filter.py` (el más importante)
- Primera página de `bitacora_experimentos.csv`
- `CHECKLIST_IMPRIMIBLE.md` como protocolo experimental

---

## 🆘 SOPORTE POR TIPO DE PROBLEMA

### Problemas de Instalación
1. Ver: `verificar_entorno.py` output
2. Consultar: `RESUMEN_EJECUTIVO.md` > "Troubleshooting"
3. Verificar: `requirements.txt`

### Problemas de Ejecución
1. Ver: Mensajes de error en consola
2. Consultar: `README.md` > "Solución de Problemas"
3. Revisar: Logs en consola de `main.py`

### Problemas de Interpretación
1. Ver: `docs/GUIA_PRIMER_DISPARO.md` > "Interpretación"
2. Consultar: `CHECKLIST_IMPRIMIBLE.md` > "Referencia Rápida"
3. Comparar: Con screenshots de experimentos anteriores

### Problemas de Documentación
1. Ver: `docs/PLANTILLA_BITACORA.md`
2. Ejemplo: Primera fila de `bitacora_experimentos.csv`
3. Consultar: `CHECKLIST_IMPRIMIBLE.md`

---

## 📊 ESTADÍSTICAS DEL PROYECTO

### Código
- **Módulos:** 5 archivos Python
- **Scripts:** 3 ejecutables
- **LOC Total:** ~1000 líneas (sin comentarios)
- **Documentación en código:** ~1000 líneas adicionales

### Documentación
- **Guías:** 8 documentos Markdown
- **Páginas totales:** ~40 páginas
- **Instrucciones:** Paso a paso completas

### Estructura de Datos
- **Bitácora:** 20 columnas
- **Capacidad:** Ilimitados experimentos
- **Formato:** CSV (compatible con Excel/Python/R)

---

## ✅ CHECKLIST DE DOMINIO DEL SISTEMA

### Nivel 1: Principiante
- [ ] Leí RESUMEN_EJECUTIVO.md
- [ ] Ejecuté verificar_entorno.py con éxito
- [ ] Realicé primera prueba con imagen de Google
- [ ] Capturé screenshot del panel 2×2

### Nivel 2: Intermedio
- [ ] Documenté 5+ experimentos en bitácora
- [ ] Ajusté parámetros Sigma1/Sigma2
- [ ] Identifiqué falsos positivos manualmente
- [ ] Entiendo qué significa cada ventana de resultado

### Nivel 3: Avanzado
- [ ] Realicé 10+ experimentos documentados
- [ ] Ejecuté analizar_bitacora.py
- [ ] Identifiqué parámetros óptimos para mi caso
- [ ] Calculé precisión manualmente

### Nivel 4: Experto
- [ ] Calibré con imágenes reales del hospital
- [ ] Modifiqué código fuente (src/*.py)
- [ ] Generé datos para BM5 de la tesis
- [ ] Validé con matriz de confusión

---

## 🎯 OBJETIVOS POR FASE

### Esta Semana: Validación Técnica
```
✅ Confirmar que el sistema funciona
✅ Familiarizarse con el workflow
✅ Realizar 3-5 pruebas con imágenes de internet
✅ Documentar observaciones en bitácora
```

### Próximas 2 Semanas: Calibración
```
✅ Obtener imágenes reales del hospital
✅ Calibrar AREA_PROMEDIO_NUCLEO_NORMAL
✅ Optimizar Sigma1 y Sigma2
✅ Validar con anotaciones de la Dra. Rangel
```

### Mes 1: Recolección de Datos
```
✅ Procesar 50+ imágenes
✅ Acumular 20+ experimentos en bitácora
✅ Calcular métricas de validación
✅ Generar resultados para BM5
```

### Mes 2: Escritura de Tesis
```
✅ Analizar bitácora con analizar_bitacora.py
✅ Generar gráficas y tablas
✅ Escribir sección de Resultados
✅ Preparar Anexos con código
```

---

## 💡 CONSEJOS FINALES

### Para Experimentación
1. **UN parámetro a la vez** - No cambies todo simultáneamente
2. **SIEMPRE documenta** - Sin bitácora, el experimento no existe
3. **Screenshots obligatorios** - Evidencia visual para la tesis
4. **Validación manual** - Cuenta tú mismo los falsos positivos

### Para la Tesis
1. **Cita la bitácora** - "Ver Anexo A: bitacora_experimentos.csv"
2. **Incluye código clave** - Especialmente dog_filter.py
3. **Muestra evolución** - Compara T-001 vs. T-020
4. **Justifica decisiones** - "Elegimos σ₁=5.0 porque..."

### Para el Éxito
1. **Lee primero, ejecuta después** - Entiende antes de probar
2. **Documenta mientras trabajas** - No dejes para después
3. **Backup regular** - Bitácora + screenshots
4. **Comunica resultados** - Comparte con el equipo

---

## 📞 ¿PERDIDO? EMPIEZA AQUÍ

### Si es tu primera vez:
**1. Lee:** [`RESUMEN_EJECUTIVO.md`](RESUMEN_EJECUTIVO.md)  
**2. Ejecuta:** `py verificar_entorno.py`  
**3. Sigue:** [`INSTRUCCIONES_RAPIDAS.md`](INSTRUCCIONES_RAPIDAS.md)

### Si ya tienes experiencia:
**1. Ejecuta:** `py main.py`  
**2. Documenta:** `bitacora_experimentos.csv`  
**3. Analiza:** `py analizar_bitacora.py`

---

## 🏆 META FINAL

> Generar datos científicos rigurosos para validar la hipótesis de la Dra. Rangel sobre la regla del "3x tamaño del núcleo" como indicador de riesgo en células de Papanicolaou.

---

*Última actualización: 2025-11-18*  
*Versión del índice: 1.0*

---

**🚀 ¡Ahora sí, todo está listo! Empieza con RESUMEN_EJECUTIVO.md**
