# Plantilla de Bitácora de Experimentación

## 📊 Estructura de la Bitácora

### Columnas del CSV

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **ID_Prueba** | Identificador único (formato T-XXX) | T-001, T-002 |
| **Fecha** | Fecha del experimento (YYYY-MM-DD) | 2025-11-18 |
| **Hora** | Hora del experimento (HH:MM) | 14:30 |
| **Imagen_Usada** | Nombre del archivo procesado | muestra_001.jpg |
| **Sigma1** | Valor del primer Gaussiano | 3.0 |
| **Sigma2** | Valor del segundo Gaussiano | 5.0 |
| **Umbral_Area_Promedio** | Área de referencia en px² | 300 |
| **Factor_Riesgo** | Multiplicador de la regla (normalmente 3.0) | 3.0 |
| **Area_Minima** | Filtro de ruido (px²) | 50 |
| **Total_Celulas_Detectadas** | Número total de núcleos | 245 |
| **Celulas_Normales** | Núcleos < 3x | 230 |
| **Celulas_Sospechosas** | Núcleos ≥ 3x | 15 |
| **Porcentaje_Riesgo** | % de células sospechosas | 6.1 |
| **Falsos_Positivos_Estimados** | Células normales mal clasificadas | 2 |
| **Falsos_Negativos_Estimados** | Células sospechosas no detectadas | 1 |
| **Precision_Estimada** | Detecciones correctas / Total (X/Y) | 242/245 |
| **Observaciones_Cualitativas** | Descripción del comportamiento | "DoG detectó bien núcleos grandes, pero marcó polvo como falso positivo" |
| **Calidad_DoG** | Evaluación visual del filtro | Excelente / Buena / Regular / Mala |
| **Ajuste_Siguiente** | Qué parámetro cambiar | "Aumentar Area_Minima a 75" |
| **Responsable** | Quién ejecutó el experimento | Nombre del investigador |

---

## 🔬 Protocolo de Uso

### Antes de Cada Experimento
1. Decidir qué parámetro(s) vas a modificar
2. Anotar el ID_Prueba siguiente (secuencial)
3. Documentar la hipótesis: "Si aumento Sigma1 a X, espero que..."

### Durante el Experimento
1. Actualizar los parámetros en `main.py`
2. Ejecutar: `python main.py`
3. Observar las ventanas de visualización

### Después del Experimento
1. Anotar los resultados automáticos (Total, Normales, Sospechosas)
2. **Validación Manual**: Abrir la imagen en `data/results/` y contar:
   - ¿Cuántos círculos ROJOS son realmente sospechosos? → Calcular falsos positivos
   - ¿Cuántos núcleos grandes NO fueron detectados? → Calcular falsos negativos
3. Registrar en `bitacora_experimentos.csv`
4. Tomar screenshot del panel 2×2 y guardarlo como `resultados/T-XXX_panel.png`

---

## 📈 Análisis de Resultados (Para BM5)

### Gráficas a Generar
Una vez tengas 10-20 experimentos, crear:

1. **Curva de Precisión vs. Sigma1/Sigma2**
   - Eje X: Valor de Sigma1
   - Eje Y: Precisión (%)
   - Encuentra el punto óptimo

2. **Matriz de Confusión Final**
   ```
               Predicción
               Normal | Sospechoso
   Real Normal    TN   |    FP
   Real Sospech   FN   |    TP
   ```

3. **Tabla de Sensibilidad/Especificidad**
   - Sensibilidad = TP / (TP + FN)
   - Especificidad = TN / (TN + FP)

---

## 🎯 Ejemplo de Entrada Completa

```csv
T-005,2025-11-20,10:35,pap_smear_005.jpg,5.0,8.0,450,3.0,75,198,185,13,6.6,1,2,195/198,"DoG excelente. Detectó correctamente células grandes. Un núcleo roto no fue detectado (esperado). Marcó una mancha de sangre como FP.",Excelente,"Aumentar Area_Minima a 80 para eliminar manchas",María
```

---

## 💡 Consejos para la Tesis

### Justificación de Parámetros Finales
En tu documento, incluye:

> *"Se realizaron 25 experimentos de calibración (ver Bitácora, Anexo A), variando los parámetros σ₁ entre 2.0 y 8.0 y σ₂ entre 4.0 y 12.0. Los valores óptimos identificados fueron σ₁=5.0 y σ₂=8.5, los cuales maximizaron la precisión de detección (97.3%) según la prueba T-018 con imágenes de validación anotadas por la Dra. Rangel."*

### Reproducibilidad (BM6)
> *"Todos los experimentos fueron documentados en formato CSV (bitacora_experimentos.csv) con control de versiones en Git, incluyendo parámetros de entrada, resultados cuantitativos y observaciones cualitativas. El entorno de desarrollo se preservó mediante requirements.txt con versiones específicas de librerías."*

---

## ⚠️ Advertencia

**NO EDITAR** manualmente el CSV en Excel mientras esté abierto Python o Git.  
Usa Google Sheets o cierra todos los programas antes de editar.

---

*Última actualización: 2025-11-18*
