# ✅ CHECKLIST DE EXPERIMENTACIÓN
## Para imprimir y usar durante cada prueba

---

## 📋 ANTES DE EJECUTAR

### Preparación
- [ ] Imagen copiada a `data/raw/`
- [ ] Nombre de archivo anotado: ___________________________
- [ ] Parámetros decididos:
  - [ ] Sigma1 = ______
  - [ ] Sigma2 = ______
- [ ] Hipótesis de esta prueba: _________________________
      ___________________________________________________

---

## 🚀 DURANTE LA EJECUCIÓN

### Comando
```
py main.py
```

### Observar Consola
- [ ] Se cargó la imagen correctamente
- [ ] Calidad de imagen aceptable (contraste > 15)
- [ ] Filtro DoG aplicado sin errores
- [ ] Análisis completado

### Anotar Resultados Automáticos
- Total células detectadas: _______
- Células normales: _______
- Células sospechosas: _______
- Porcentaje de riesgo: _______%

---

## 🔍 EVALUACIÓN VISUAL

### Ventana "Filtro DoG"
- [ ] ¿Se ve predominantemente NEGRA?
- [ ] ¿Los bordes están BLANCOS y nítidos?
- [ ] ¿Se distinguen estructuras circulares?

**Calidad del DoG:** ⬜ Excelente ⬜ Buena ⬜ Regular ⬜ Mala

### Ventana "Resultado Final"
- [ ] ¿Detectó al menos algunas células?
- [ ] ¿Los círculos VERDES coinciden con células normales?
- [ ] ¿Los círculos ROJOS coinciden con células grandes?

---

## 📊 VALIDACIÓN MANUAL

### Contar Manualmente
1. Abrir imagen en `data/results/`
2. Comparar con detección automática

- Falsos POSITIVOS (marcados pero no son células): _______
- Falsos NEGATIVOS (no detectados pero son células): _______
- CORRECTOS (bien detectados): _______

**Precisión Estimada:** _______ / _______ células

---

## 📸 CAPTURAR EVIDENCIA

- [ ] Screenshot del Panel 2×2
- [ ] Guardado como: `T-___  _panel.png`
- [ ] Copiado a: `data/results/screenshots/`

---

## 📝 DOCUMENTAR EN BITÁCORA

### Abrir: bitacora_experimentos.csv

Completar en última fila:
- [ ] `Calidad_DoG`: _______________
- [ ] `Falsos_Positivos_Estimados`: _______________
- [ ] `Falsos_Negativos_Estimados`: _______________
- [ ] `Precision_Estimada`: _______________
- [ ] `Observaciones_Cualitativas`: 
      ___________________________________________________
      ___________________________________________________
- [ ] `Ajuste_Siguiente`: ___________________________

---

## 🎯 DECISIÓN PARA PRÓXIMA PRUEBA

### ¿Qué funcionó bien?
___________________________________________________
___________________________________________________

### ¿Qué necesita mejorar?
___________________________________________________
___________________________________________________

### Parámetro a ajustar:
⬜ Sigma1 → Nuevo valor: ______
⬜ Sigma2 → Nuevo valor: ______
⬜ Area_Promedio → Nuevo valor: ______
⬜ Area_Minima → Nuevo valor: ______
⬜ Otro: _________________

### Razón del ajuste:
___________________________________________________
___________________________________________________

---

## ✅ FINALIZACIÓN

- [ ] Bitácora actualizada
- [ ] Screenshot guardado
- [ ] Archivos respaldados
- [ ] Próxima prueba planificada

---

**ID de esta prueba:** T-_____  
**Fecha:** _____ / _____ / _____  
**Hora:** _____:_____  
**Responsable:** _____________________

---

## 💡 REGLAS DE ORO

1. **UN parámetro a la vez** - No cambies todo simultáneamente
2. **SIEMPRE documentar** - Sin registro = experimento perdido
3. **Screenshot OBLIGATORIO** - Para la tesis y análisis
4. **Validar manualmente** - No confiar ciegamente en el algoritmo
5. **Comparar con anterior** - ¿Mejoró o empeoró?

---

## 🆘 REFERENCIA RÁPIDA

| Problema | Solución |
|----------|----------|
| DoG gris/ruidoso | Aumentar Sigma1 y Sigma2 |
| Bordes muy tenues | Disminuir ambos Sigmas |
| Detecta polvo | Aumentar Area_Minima |
| No detecta nada | Disminuir Umbral_DoG |
| Todo es rojo | Aumentar Area_Promedio |
| Todo es verde | Disminuir Area_Promedio |

---

_Versión 1.0 - CitoCounter Proto - 2025-11-18_
