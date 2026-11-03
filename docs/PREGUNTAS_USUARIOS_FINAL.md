# Preguntas para Usuarios Potenciales - Validación UI CitoCounter

## Objetivo
Recopilar feedback de citotecnólogos y personal clínico para mejorar la interfaz de CitoCounter-Proto y adaptarla a flujos de trabajo reales.

---

## Preguntas de Experiencia de Usuario

### 1. Flujo de Trabajo
1. **¿Cuál es el proceso normal de trabajo en su clínica para contar núcleos en imágenes citológicas?**
2. **¿Cómo se compara este proceso con el flujo de trabajo que ofrece CitoCounter (cargar → procesar → revisar → exportar)?**
3. **¿Qué pasos faltan o están duplicados en la interfaz actual?**

### 2. Interfaz de Usuario
4. **¿La interfaz resulta intuitiva al primer uso? ¿Qué elementos le resultaron confusos?**
5. **¿Los botones y menús están ubicados en lugares lógicos según su experiencia previa?**
6. **¿La organización de paneles (visualización, controles, resultados) es apropiada?**

### 3. Visualización de Resultados
7. **¿Las herramientas de visualización (superposición de detecciones, colores) facilitan la revisión?**
8. **¿Los colores utilizados (TP, FP, FN) son accesibles para personas con daltonismo?**
9. **¿Qué tipo de visualización preferiría para revisar resultados (imagen única, comparación lado a lado, animación)?**

### 4. Parámetros Técnicos
10. **¿Los parámetros de detección (sigma, umbrales, tamaño de núcleos) son comprensibles con su formación?**
11. **¿Necesitaría una guía o ayuda contextual para ajustar estos parámetros?**
12. **¿Qué valores de parámetros usaría típicamente en sus imágenes?**

### 5. Rendimiento
13. **¿Los tiempos de procesamiento son aceptables para su flujo de trabajo?**
14. **¿Preferiría procesamiento síncrono o con barra de progreso?**
15. **¿Debe poder procesar imágenes en lote o individualmente?**

### 6. Navegación y Gestión
16. **¿Cómo gestionaría sus imágenes y resultados (guardado, organización, historial)?**
17. **¿Qué formato de exportación necesitaría (CSV, JSON, imagen anotada, PDF)?**
18. **¿Debe poder anotar o marcar detecciones manualmente?**

### 7. Casos Especiales
19. **¿Cómo manejaría imágenes con baja calidad o artefactos?**
20. **¿Qué hacer cuando hay superposición de núcleos?**
21. **¿Cómo verificaría resultados sospechosos (detecciones muy grandes/pequeñas)?**

### 8. Validación Clínica
22. **¿Podría usar esta herramienta para validar resultados automáticos?**
23. **¿Qué métricas le resultarían útiles (precisión, recall, F1, IoU)?**
24. **¿Necesita comparar resultados entre diferentes algoritmos (DoG vs DL)?**

### 9. Entorno de Trabajo
25. **¿Trabajaría con la aplicación en una workstation específica o desde diferentes equipos?**
26. **¿Preferiría una versión de escritorio nativa o una aplicación web?**
27. **¿Debe poder usar la herramienta offline (sin internet)?**

### 10. Seguridad y Cumplimiento
28. **¿Qué consideraciones de seguridad necesita al usar esta herramienta con imágenes clínicas?**
29. **¿Cumple con los requisitos de su institución para software médico?**
30. **¿Necesita auditoría de logs o historial de cambios?**

---

## Preguntas Específicas para Mejoras

### UX/UI
31. **¿Qué elemento de la interfaz le gustaría cambiar por completo?**
32. **¿Hay algún atajo de teclado o acceso rápido que necesite?**
33. **¿Le gustaría una personalización del tema (colores oscuros/claros)?**

### Funcionalidad
34. **¿Qué casos de uso no cubre actualmente la herramienta?**
35. **¿Le gustaría poder configurar perfiles de parámetros para diferentes tipos de muestras?**
36. **¿Necesitaría integración con otros sistemas (PACS, DICOM, bases de datos)?**

### Documentación y Soporte
37. **¿Qué tipo de documentación necesitaría (manual de usuario, tutoriales, videos)?**
38. **¿Preferiría soporte vía chatbot, formularios, o documentación estática?**
39. **¿Qué nivel de detalle necesita en la documentación técnica?**

### Feedback Específico sobre Qt vs Streamlit
40. **Si se implementa una versión de escritorio con Qt, ¿qué le molestaría o le gustaría?**
41. **¿Qué funcionalidades esenciales debe tener una aplicación de escritorio?**
42. **¿Le preocupan los requisitos de instalación o dependencias?**

---

## Información Adicional Recopilada

### Características Pedidas
- [ ] Procesamiento por lotes con cola
- [ ] Vista previa de imágenes
- [ ] Comparación automática de algoritmos
- [ ] Alertas de detecciones sospechosas
- [ ] Modo nocturno
- [ ] Atajos de teclado personalizables
- [ ] Plantillas de informe
- [ ] Integración con EMR (Historia Clínica Electrónica)

### Comentarios Libres
**Espacio para comentarios adicionales del usuario:**



---

## Instrucciones para la Sesión
1. Pedir al usuario que cargue una imagen de ejemplo
2. Tome nota de su experiencia durante el primer uso
3. Preguntar específicamente sobre los puntos 1-10
4. Luego avanzar a preguntas técnicas (11-30)
5. Finalizar con preguntas de mejora (31-42)
6. Registrar tiempo total de la sesión

---

**Plantilla preparada para:** CITO-88 - Pruebas de la plataforma con usuarios potenciales