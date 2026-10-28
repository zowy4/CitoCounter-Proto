# Guia de desarrollo para plataforma medica

## 1. Proposito y estado

Esta guia es la referencia viva para evolucionar CitoCounter-Proto de
prototipo de investigacion a una plataforma de apoyo clinico potencialmente
formal. Complementa, sin reemplazar, la
[guia maestra de desarrollo](guia-maestra-desarrollo.md), el
[plan del proyecto](plan-proyecto.md), la
[guia de experimentos](guide/experimentos.md) y la
[guia de dataset](guide/dataset.md).

**Estado actual:** CitoCounter-Proto no es un dispositivo medico ni una
herramienta de diagnostico. Sus salidas requieren revision experta y no deben
usarse para emitir diagnosticos, priorizar pacientes o tomar decisiones
terapeuticas.

Esta guia no constituye certificacion ni asesoria regulatoria. Antes de un uso
clinico debe participar personal de citopatologia, calidad, seguridad,
privacidad y regulacion de la jurisdiccion de despliegue.

## 2. Uso previsto y limites obligatorios

Antes de agregar una funcion que afecte resultados clinicos, se debe aprobar
un documento de uso previsto que incluya:

1. Usuario objetivo y nivel de capacitacion.
2. Tipo de muestra, equipo de adquisicion, tincion y entorno operativo.
3. Datos de entrada permitidos y controles de calidad requeridos.
4. Salida exacta del sistema y su interpretacion permitida.
5. Rol de la revision humana, incluidos los casos en que es obligatoria.
6. Poblacion objetivo, exclusiones y limitaciones conocidas.

Hasta que exista validacion clinica aprobada, la interfaz, la API y la CLI
deben mantener la advertencia de investigacion y distinguir claramente entre
un resultado algoritmico y un dictamen profesional.

## 3. Roles y responsabilidades

| Rol | Responsabilidad |
|---|---|
| Responsable clinico | Aprueba uso previsto, anotaciones, protocolo clinico y limites de interpretacion. |
| Responsable de calidad | Mantiene trazabilidad, revisiones, no conformidades y liberaciones. |
| Responsable tecnico | Implementa cambios en `src/`, pruebas, contratos y evidencia reproducible. |
| Responsable de datos | Autoriza fuentes, separa conjuntos, verifica privacidad y conserva procedencia. |
| Seguridad y privacidad | Revisa acceso, secretos, auditoria, retencion y respuesta a incidentes. |
| Revisor independiente | Comprueba criterios de aceptacion y evidencia antes de una liberacion. |

Una misma persona puede cubrir mas de un rol en investigacion, pero no debe
aprobar sin revision independiente un cambio que altere seguridad, datos,
metricas o comportamiento clinico.

## 4. Flujo obligatorio de una actividad

1. **Definir.** Crear o actualizar la incidencia Jira con objetivo, alcance,
   criterios de aceptacion, riesgos y dependencias.
2. **Evaluar riesgos.** Relacionar el cambio con peligros conocidos: falso
   negativo, falso positivo, imagen de baja calidad, fuga de datos, acceso no
   autorizado o indisponibilidad.
3. **Disenar.** Documentar contratos, entradas invalidas, salida segura y
   comportamiento ante error antes de editar codigo.
4. **Implementar.** Mantener la logica de negocio en `src/`; CLI, API y
   Streamlit solo orquestan y muestran resultados.
5. **Probar.** Agregar una prueba de regresion que cubra comportamiento
   nominal, entrada invalida y borde relevante. Ejecutar la prueba mas
   especifica y despues las pruebas relacionadas.
6. **Evidenciar.** Registrar version, dataset, parametros, fecha, comandos,
   metricas y limitaciones. No incluir imagenes, anotaciones o datos de
   pacientes.
7. **Revisar.** Un revisor confirma que requisitos, riesgos, pruebas y
   evidencia son consistentes.
8. **Liberar o bloquear.** Solo entonces actualizar Jira a `Finalizado`.
   Si falta una autorizacion, anotacion experta o evidencia, usar `Bloqueado`
   o `En revision`.

## 5. Controles de datos y experimentacion

- Usar datos autorizados, con procedencia y finalidad documentadas.
- Separar por origen o paciente los conjuntos de calibracion, validacion y
  prueba para impedir fuga de datos.
- No modificar una anotacion clinica automaticamente. Las incoherencias se
  registran y regresan a revision experta.
- Congelar el conjunto de prueba antes de ajustar parametros. No seleccionar
  parametros a partir de sus resultados.
- Exigir ground truth espacial valido para precision, sensibilidad, F1 e IoU.
  Un conteo aproximado no es validacion clinica.
- Conservar resultados reproducibles sin publicar datos sensibles. Consultar
  [la guia de experimentacion](guide/experimentos.md) para la bitacora.

## 6. Seguridad, privacidad y operacion

- Mantener secretos, tokens, credenciales y certificados fuera de Git.
- Para despliegue, usar TLS/HTTPS, control de acceso con minimo privilegio,
  rotacion de secretos, auditoria estructurada y monitoreo.
- Registrar accesos, cambios de configuracion, version del algoritmo y
  resultado operativo, sin registrar informacion clinica innecesaria.
- Definir retencion, copias de seguridad cifradas, eliminacion segura y
  respuesta ante incidentes antes de manejar datos reales.
- Tratar fallas, entradas malformadas y calidad insuficiente como estados
  explicitos. Nunca presentar una falla como resultado normal.

## 7. Requisitos de interfaz y experiencia clinica

- Mostrar advertencias de investigacion, calidad de imagen y necesidad de
  revision humana de forma visible.
- Exponer parametros, version, fecha y fuente de cada resultado reproducible.
- Evitar que color sea el unico indicador; combinar texto, iconos y valores.
- Confirmar acciones irreversibles y conservar trazabilidad de exportaciones.
- Realizar pruebas de usabilidad con participantes reales y protocolo
  aprobado; no simular retroalimentacion clinica.

## 8. Puertas de avance

| Puerta | Criterio minimo | Evidencia requerida |
|---|---|---|
| Datos para desarrollo | Origen autorizado, estructura valida y anotaciones revisadas | Inventario, validacion de dataset y aprobacion experta |
| Cambio de algoritmo | Riesgo analizado y comportamiento definido | Pruebas de regresion y bitacora de parametros |
| Evaluacion tecnica | Conjuntos separados y protocolo congelado | Metricas espaciales, configuracion y reporte |
| Evaluacion clinica | Protocolo, datos y revisores autorizados | Revision clinica documentada y analisis estadistico |
| Despliegue controlado | Seguridad, privacidad, respaldo y operacion definidos | Revision de seguridad, plan de incidentes y evidencia TLS |
| Uso clinico | Requisitos regulatorios y de calidad aplicables cumplidos | Aprobaciones institucionales y paquete de liberacion |

No se puede saltar una puerta por tener una metrica alta sobre datos sinteticos
o de desarrollo.

## 9. Linea base y prioridades actuales

| Prioridad | Estado y siguiente accion |
|---|---|
| Ground truth trazable | CITO-96 esta bloqueada por una anotacion HSIL inconsistente; requiere revision experta. |
| Validacion clinica | CITO-85 y CITO-97 son evidencia sintetica experimental; falta un conjunto real autorizado e independiente. |
| Seguridad de despliegue | CITO-93 requiere completar TLS, gestion externa de secretos y operacion monitorizada. |
| Usabilidad | CITO-88 requiere sesiones reales con citotecnologos o personal clinico. |

Los estados vigentes y evidencias se actualizan en Jira y se reflejan en
[ACTIVIDADES_PROYECTO.md](../ACTIVIDADES_PROYECTO.md).

## 10. Lista de verificacion para cada pull request

- [ ] El cambio tiene incidencia Jira, criterio de aceptacion y riesgo asociado.
- [ ] No se incluyeron secretos, imagenes de pacientes ni anotaciones brutas.
- [ ] La logica esta en `src/` y los adaptadores conservan responsabilidades.
- [ ] Hay pruebas de regresion relevantes y pasan.
- [ ] El experimento o comportamiento usa datos y parametros trazables.
- [ ] La interfaz/API informa errores y limitaciones explicitamente.
- [ ] `git diff --check` no informa errores.
- [ ] La documentacion y evidencia relacionada fueron actualizadas.
- [ ] Un revisor independiente aprobo el cambio cuando afecta datos,
      algoritmo, seguridad o resultados clinicos.

## 11. Mantenimiento de esta guia

Actualizar esta guia cuando cambie el uso previsto, se identifique un nuevo
riesgo, se apruebe un protocolo clinico, se modifique una puerta de avance o
se complete una capacidad de despliegue. Los procedimientos detallados deben
permanecer en sus guias especializadas para evitar duplicacion.
