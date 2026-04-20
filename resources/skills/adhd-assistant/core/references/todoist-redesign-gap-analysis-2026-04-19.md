# ADHD Assistant · Benchmark de Todoist y dirección de rediseño

Fecha: 2026-04-19

## 1. Conclusión corta

Todoist no destaca por tener muchas features, sino por un loop diario muy claro:

**capturar rápido → mandar a Inbox → decidir qué va hoy → replanificar fácil → completar → revisar sin fricción**

La webapp actual de `adhd-assistant` todavía no es eso. Hoy funciona como **monitor de runtime / mockup de calendario**, no como una app operativa de tareas para uso diario.

La dirección correcta para `adhd-assistant` no es clonar Todoist entero. Es copiar su **loop de baja fricción** y combinarlo con principios ADHD-friendly:

- la home debe responder **"qué hago ahora"**
- el backlog no debe comerse la pantalla principal
- capturar debe requerir muy pocas decisiones
- posponer / replanificar debe ser fácil y sin castigo
- la review debe existir, pero separada del foco diario

---

## 2. Qué funcionalidades de Todoist importan de verdad

### Core de uso diario

1. **Quick Add ubicuo**
   - captura inmediata
   - lenguaje natural para fecha y contexto
   - baja fricción al crear

2. **Inbox como landing zone por defecto**
   - todo entra rápido
   - organizar queda para después
   - evita perder tareas por querer clasificarlas demasiado pronto

3. **Today view**
   - lista solo lo relevante para hoy
   - reduce carga mental
   - permite destacar prioridades reales

4. **Upcoming view**
   - da visibilidad de próximos días/semanas
   - facilita replanificación
   - separa planificación de ejecución inmediata

5. **Task view / drawer**
   - detalle de una tarea sin abandonar el contexto
   - editar descripción, fecha, prioridad, subtareas, recordatorios

6. **Projects + sections + subtasks**
   - organización suficiente sin forzar complejidad desde el minuto uno

7. **Prioridades, recurrencia y recordatorios**
   - son las palancas más útiles para operación real del día a día

### Advanced, pero no MVP

- labels
- filters con query syntax
- board view completo
- calendar avanzado multi-layout
- activity history rica
- templates

### Team / enterprise

Esto **no debe contaminar el MVP** de `adhd-assistant`:

- workspaces compartidos
- roles y permisos
- comentarios colaborativos
- asignaciones de equipo
- sharing por link

---

## 3. Qué hace bien la UX de Todoist

## 3.1 Navegación estable y predecible

Todoist repite pocos anclajes principales:

- Inbox
- Today
- Upcoming
- Projects
- Add task

Eso crea memoria muscular. El usuario no tiene que pensar dónde está cada cosa.

## 3.2 Jerarquía visual tranquila

Patrones observados en las capturas oficiales y en la página de features:

- sidebar persistente
- un CTA principal claro para añadir tarea
- filas de tareas compactas pero legibles
- metadatos mínimos por tarea
- buen uso de espacio en blanco
- progresión visual clara entre navegación → lista → detalle

## 3.3 Progressive disclosure

La pantalla principal no intenta enseñarlo todo. Primero enseña la lista. El detalle vive en la task view.

Eso es especialmente importante para ADHD: menos decisión al principio, más detalle solo cuando hace falta.

## 3.4 Replanificación sin drama

El valor de Todoist no es solo planificar. Es **replanificar rápido**:

- mover tareas a otro día
- posponer
- ajustar recurrencia
- reorganizar Upcoming

La UX transmite que cambiar el plan es normal, no un fallo moral.

## 3.5 La unidad real de trabajo es la tarea, no el dashboard

Todoist organiza alrededor de una tarea accionable:

- checkbox
- título
- fecha
- prioridad
- proyecto / sección
- detalle opcional

No alrededor de logs, archivos, políticas o estado interno.

---

## 4. Estado actual de `adhd-assistant`

### 4.1 Qué hay hoy

Inspección del repo y de la webapp actual:

- `manifest.yaml` declara el modo de la webapp como **`read-only-monitoring`**
- `webapp/templates/index.html` es un dashboard de observabilidad
- `webapp/templates/calendar.html` es un mockup local de calendario/backlog
- la UI principal prioriza:
  - runtime path
  - skill path
  - estado de archivos
  - políticas activas
  - logs
  - hindsight queue

Es decir: hoy el producto principal es un **monitor técnico**.

### 4.2 Qué soporta ya el modelo de datos

El modelo actual ya tiene bastante materia prima reutilizable:

- `commitments.tasks`
- `commitments.appointments`
- `support.reminders`
- prioridades
- deadline
- status
- proyecto
- tags
- notas / descripción
- `postponed_count`
- vínculo tarea ↔ recordatorio

Además, `engine/reconcile.py` ya migra tareas de `~/.hermes/tasks/tasks.json` hacia `state.json`.

### 4.3 Qué no existe aún como producto

No hay todavía:

- quick add
- inbox operativa
- today view real
- upcoming view real con replanificación
- edición de tarea
- completar tarea desde UI
- posponer desde UI
- drawer / detalle de tarea
- flujo de review
- navegación centrada en ejecución

### 4.4 Hallazgo de UX importante

La webapp actual muestra además un problema práctico de base path:

- `http://127.0.0.1:8765/static/styles.css` → `200`
- `http://127.0.0.1:8765/adhd-assistant/static/styles.css` → `404`
- `http://127.0.0.1:8765/calendar` → `200`
- `http://127.0.0.1:8765/adhd-assistant/calendar` → `404`

Es decir: la versión servida bajo subruta funciona bien vía Tailscale, pero el acceso local directo no queda consistente cuando el proceso arranca con `ADHD_WEBAPP_ROOT_PATH=/adhd-assistant`.

No es el problema principal del rediseño, pero conviene resolverlo cuando se rehaga la shell de navegación.

---

## 5. Gap analysis real

| Área | Todoist | ADHD Assistant hoy | Gap | Severidad |
|---|---|---|---|---|
| Captura | Quick Add ubicuo y muy rápido | No hay alta de tareas en UI | Falta el punto de entrada principal | Crítica |
| Inbox | Bandeja de entrada por defecto | No existe vista de triage | Falta el buffer de captura | Crítica |
| Hoy | Vista enfocada en hoy | No existe; hay monitor + mockup | Falta la home diaria | Crítica |
| Próximos | Vista de planificación y replanificación | Calendario mockup solo lectura | Falta planificación operativa | Alta |
| Operaciones básicas | Completar, editar, mover, posponer | No disponibles | La app no es operativa | Crítica |
| Detalle de tarea | Task view rica y contextual | No existe | Falta profundidad sin saturar lista | Alta |
| Organización | Proyectos, secciones, subtareas | Hay proyecto en datos, no en UX | La estructura existe pero no aflora | Alta |
| Priorización | P1-P4 visible y accionable | Prioridad existe en datos y mockup | Falta surfacing coherente | Media-Alta |
| Recordatorios | Integrados en la tarea | Existen en datos | Falta UX y acciones | Media-Alta |
| Revisión | Today/Upcoming permiten limpiar y cerrar ciclo | No hay review operativa | El sistema no ayuda a cerrar el día | Alta |
| Dashboard técnico | Secundario | Hoy es la pantalla principal | El producto está invertido | Crítica |

---

## 6. Qué conviene copiar y qué no

### Conviene copiar

1. **Loop Inbox → Today → Upcoming**
2. **Quick Add como acción primaria global**
3. **Task rows simples con pocos metadatos**
4. **Task detail drawer**
5. **Replanificación rápida**
6. **Projects / sections como estructura ligera**
7. **Prioridades visibles pero no invasivas**
8. **Recurrencia y recordatorios integrados**
9. **Empty states que cierran el loop del día**

### No conviene copiar

1. **Complejidad de equipo / workspaces**
2. **Labels y filters como centro del MVP**
3. **Query syntax avanzada demasiado pronto**
4. **Board/calendar completos antes de dominar la lista diaria**
5. **Karma/gamificación como eje principal**
6. **Exceso de taxonomía que convierta la app en meta-trabajo**

Para `adhd-assistant`, el riesgo mayor no es quedarse corto. Es acabar construyendo una herramienta que obliga a organizar demasiado y ejecutar poco.

---

## 7. Loop objetivo para `adhd-assistant`

El loop recomendado no es exactamente el de Todoist. Debe ser este:

**capturar en 2 segundos → caer en Inbox → elegir pocas cosas para Hoy → ver claramente “qué hago ahora” → completar o posponer sin fricción → revisar backlog en otro momento**

Ese loop es más apropiado para uso ADHD-friendly porque:

- separa captura de organización
- separa ejecución de planificación
- limita la sobreexposición al backlog
- reduce culpa al replanificar

---

## 8. Navegación propuesta

## 8.1 Navegación primaria

Propuesta de navegación principal:

- **Hoy**
- **Inbox**
- **Próximos**
- **Proyectos**
- **Revisar**
- **+ Añadir** (acción global, siempre visible)

### Por qué así

- **Hoy** debe ser la home real
- **Inbox** es donde aterriza todo lo no procesado
- **Próximos** resuelve planificación sin ensuciar Hoy
- **Proyectos** ordena por áreas
- **Revisar** agrupa overdue, backlog viejo, tareas estancadas, limpieza y acceso a progreso

El monitor técnico actual debe pasar a una ruta secundaria tipo:

- `/monitor`
- `/admin`
- o una pestaña técnica no principal

Nunca debe seguir siendo la home de producto.

---

## 9. Pantallas propuestas

## 9.1 Hoy

**Objetivo:** responder qué hacer ahora y qué queda hoy.

### Contenido mínimo

1. **Card principal “Ahora”**
   - una sola tarea destacada
   - CTA: completar / empezar / posponer / abrir detalle

2. **Lista “Hoy”**
   - tareas de hoy
   - orden por prioridad + hora + estado

3. **Bloques próximos**
   - citas / recordatorios cercanos

4. **Sección colapsable “Aplazadas / vencidas”**
   - visible pero no dominando la pantalla

### Principio UX

La home no debe empezar con “tienes 57 cosas”.
Debe empezar con “haz esto”.

## 9.2 Inbox

**Objetivo:** triage rápido.

### Acciones principales por tarea

- asignar a proyecto
- poner fecha
- marcar prioridad
- dividir en subtareas
- eliminar

### Regla

Inbox no es para vivir ahí. Es para vaciarla.

## 9.3 Próximos

**Objetivo:** planificar próximos 7-14 días.

### MVP

- lista agrupada por día
- mover tarea a otra fecha
- ver citas y recordatorios juntos
- toggle lista / calendario simple si compensa

No hace falta drag-and-drop completo en v1 si botones rápidos cubren el 80% del caso.

## 9.4 Proyectos

**Objetivo:** mantener contexto sin meterlo todo en Hoy.

### Estructura

- proyectos = áreas grandes
- secciones = etapas o buckets dentro del proyecto
- subtareas = desglose de ejecución

## 9.5 Revisar

**Objetivo:** limpiar el sistema sin contaminar el foco diario.

### Debe concentrar

- overdue
- tareas sin fecha viejas
- tareas con muchos postpones
- tareas huérfanas
- backlog por triage

### Estructura recomendada

Revisar no debería ser una sola lista caótica, sino un módulo con dos zonas:

1. **Limpieza**
   - overdue
   - Inbox envejecida
   - tareas sin bucket temporal
   - tareas con demasiados postpones

2. **Progreso**
   - métricas de cumplimiento
   - métricas de posposición
   - tendencias semanales / mensuales
   - insights para aprender a planificar mejor

## 9.6 Progreso y aprendizaje

**Objetivo:** convertir el historial de ejecución en aprendizaje práctico, no en culpa.

### Qué debe responder

- cuántas tareas se completan
- cuántas se completan dentro del momento comprometido
- cuántas se posponen
- cuántas veces se posponen antes de completarse
- si el usuario está mejorando semana a semana
- qué buckets temporales funcionan mejor
- qué contextos / hashtags acumulan más fricción

### Principio UX

Esto no debe sentirse como un panel de control corporativo ni como un sistema de castigo.

Debe sentirse como un espejo útil que ayude al usuario a detectar cosas como:

- “estoy metiendo demasiadas cosas en hoy”
- “las tareas con `#legal` se me atascan”
- “cuando marco `próximas 4 horas` sí suelo cumplir”
- “he reducido el número medio de postpones por tarea”

### Vistas recomendadas

1. **Resumen**
   - completadas hoy / semana / mes
   - completadas en plazo comprometido
   - pospuestas hoy / semana / mes
   - media de postpones por tarea completada

2. **Tendencias**
   - cumplimiento por semana
   - ratio de posposición
   - reducción de backlog vencido

3. **Análisis por contexto**
   - por proyecto
   - por hashtag
   - por bucket temporal

4. **Insights accionables**
   - recomendaciones cortas
   - alertas de sobreplanificación
   - detección de buckets poco realistas

---

## 10. Modelo de interacción recomendado

## 10.1 Tarjeta de tarea minimizada

La unidad visual base no debería ser una fila plana, sino una **tarjeta plegable**.

Cuando está minimizada, debería mostrar solo lo esencial:

- checkbox
- título corto
- 2-5 hashtags descriptivos
- indicador pequeño de prioridad si aplica
- botón visible de **cuándo lo haré**
- affordance clara para expandir / contraer

Nada de ruido técnico.

El objetivo es que, con muchas tareas en pantalla, la lista siga siendo escaneable.

## 10.2 Tarjeta expandida / detalle de tarea

Al desplegar la tarjeta o abrir su detalle:

- título
- descripción
- proyecto
- fecha exacta si existe
- bucket temporal si no hay fecha exacta
- prioridad
- hashtags
- recordatorios
- subtareas
- notas
- historial simple de postpones

La versión expandida sirve para editar sin perder el contexto de la lista.

## 10.3 Quick actions obligatorias

Desde tarjeta minimizada y desde detalle:

- completar
- abrir / cerrar detalle
- cambiar **cuándo lo haré**
- posponer a mañana
- posponer a esta tarde / próxima semana
- cambiar fecha exacta
- mover a Inbox
- editar

Para una app ADHD-friendly, **posponer bien** es tan importante como completar.

## 10.4 Buckets temporales en vez de exigir fecha exacta

El control de planificación principal no debe obligar siempre a poner una hora concreta.

Buckets recomendados:

- próxima hora
- próximas 4 horas
- hoy
- mañana
- pasado mañana
- esta semana
- este mes
- sin definir

Este control debe verse incluso con la tarjeta minimizada.

### Semántica de cumplimiento

Para poder medir “se hizo cuando se dijo”, cada bucket debe tener una ventana explícita:

- **próxima hora** → dentro de los 60 minutos siguientes a asignarlo
- **próximas 4 horas** → dentro de las 4 horas siguientes
- **hoy** → antes de terminar el día local
- **mañana** → durante el día siguiente local
- **pasado mañana** → durante el segundo día siguiente
- **esta semana** → antes del cierre de la semana local
- **este mes** → antes del cierre del mes local
- **sin definir** → no computa como compromiso temporal hasta que se planifique

Esto es importante porque, sin esa semántica, la analítica de cumplimiento se vuelve ambigua.

## 10.5 Hashtags automáticos y ontología flexible

Aquí conviene pensar en **hashtags**, no en una ontología rígida cerrada.

Principio UX:

- el sistema propone hashtags automáticamente
- el usuario puede borrarlos, editarlos o añadir otros
- el sistema aprende de ese feedback
- la lista puede filtrarse por hashtag

Ejemplos de uso:

- `#familia`
- `#emma`
- `#legal`
- `#psicologia`

La idea no es imponer una taxonomía perfecta al principio, sino dejar que emerja una **ontología flexible** a partir del uso real.

## 10.6 Orden de abordaje ≠ prioridad

Hay que separar dos conceptos:

1. **prioridad**: importancia relativa
2. **orden de abordaje**: secuencia en la que el usuario cree que va a atacar las tareas

Una tarea menos prioritaria puede ir antes en el orden real de ejecución.

Por eso el usuario debe poder, en cualquier vista o filtro, reordenar tareas manualmente y decir en esencia:

- esta va antes
- esta va después

Ese orden no tiene que ser una ley dura para el motor de recomendación, pero sí una **señal fuerte**.

## 10.7 Recomendación inteligente como capa, no como sustituto

El sistema ADHD puede a veces sugerir otra tarea distinta de la primera del orden manual:

- porque es más pequeña
- porque encaja mejor con la energía actual
- porque reduce fricción de arranque

Pero eso debe ocurrir **encima** del orden de usuario, no borrándolo ni sustituyéndolo.

---

## 11. MVP por fases

## V1 — “App operativa diaria”

Objetivo: dejar de ser un monitor y pasar a ser una app usable.

### Incluir

- Home = **Hoy**
- Quick Add global
- Inbox
- Lista de Hoy
- tarjetas plegables minimizadas / expandidas
- selector visible de bucket temporal (`próxima hora`, `hoy`, `mañana`, etc.)
- completar tarea
- posponer a mañana
- editar tarea
- crear / editar fecha
- reordenación manual de tareas como orden de abordaje
- sugerencia básica de hashtags automáticos
- filtro básico por hashtag
- módulo básico de progreso:
  - completadas
  - completadas en compromiso temporal
  - pospuestas
  - media de postpones
- task detail básico
- proyectos básicos
- recordatorios visibles
- ruta técnica separada para monitor

### No incluir aún

- filtros avanzados con query language
- board
- workspaces
- colaboración
- ontología rígida formal

## V1.5 — “Planificación práctica”

- Próximos agrupado por día
- replanificación rápida
- recurrencia básica
- subtareas
- sección Revisar
- aprendizaje de hashtags a partir de aceptación / borrado / edición
- mejor lógica de recomendación usando orden de abordaje + contexto
- tendencias de progreso por semana / mes
- insights automáticos sobre sobreplanificación y buckets poco realistas

## V2 — “Potencia sin romper simplicidad”

- secciones
- vistas guardadas sencillas
- calendario mejorado
- integración más rica con Google Calendar
- campos ADHD específicos mejor surfacados (`energy`, fricción, contexto)
- modelo semántico más sólido encima de hashtags sin obligar ontología rígida

## V3 — “Capas avanzadas”

Solo si el uso real lo pide:

- filtros complejos
- automatismos avanzados
- visualizaciones históricas
- capas colaborativas

---

## 12. Implicaciones técnicas recomendadas

## 12.1 Mantener el estado actual como base

No hace falta otra base de datos para empezar.

Recomendación:

- seguir usando `state.json`
- reutilizar `state_store.save()` para persistencia atómica
- exponer APIs write-capable nuevas para tareas
- dejar el monitor actual como vista secundaria

## 12.2 Reestructurar la webapp

Dirección sugerida:

- mover el monitor técnico a `/monitor`
- convertir `/` en la app de tareas real
- separar API de lectura técnica y API de producto

APIs candidatas para la app nueva:

- `GET /api/today`
- `GET /api/inbox`
- `GET /api/upcoming`
- `GET /api/projects`
- `GET /api/tasks/{id}`
- `POST /api/tasks`
- `PATCH /api/tasks/{id}`
- `POST /api/tasks/{id}/complete`
- `POST /api/tasks/{id}/postpone`
- `POST /api/tasks/{id}/schedule-bucket`
- `POST /api/tasks/reorder`
- `GET /api/hashtags`
- `POST /api/tasks/{id}/hashtags/suggest`
- `POST /api/tasks/{id}/hashtags/feedback`
- `GET /api/insights/summary`
- `GET /api/insights/trends`
- `GET /api/insights/context-breakdown`
- `GET /api/insights/postpones`

## 12.3 Campos reutilizables ya existentes

Ya están o casi están:

- `title`
- `description`
- `status`
- `priority`
- `deadline`
- `project`
- `tags`
- `notes`
- `postponed_count`
- `history.recent_completions`
- `history.recent_postponements`
- reminders vinculados

### Posibles campos nuevos para más adelante

- `section`
- `scheduled_for`
- `schedule_bucket`
- `schedule_bucket_assigned_at`
- `schedule_window_end`
- `completed_at`
- `estimate_minutes`
- `recurrence`
- `focus_score`
- `energy_cost`
- `user_order`
- `suggested_hashtags`
- `accepted_hashtags`
- `rejected_hashtags`
- `hashtag_feedback_history`
- `completion_commitment_hit`
- `postpone_events`

Pero no son requisito para V1.

---

## 13. Decisiones estratégicas para no perdernos

1. **La home deja de ser el monitor**
2. **El producto se organiza alrededor de tarjetas de tarea, no de runtime**
3. **La captura manda a Inbox por defecto**
4. **Hoy es una vista de ejecución, no de análisis**
5. **Review va aparte**
6. **Separar prioridad de orden de abordaje**
7. **Usar hashtags flexibles antes que ontología rígida**
8. **La recomendación inteligente es una capa encima del orden del usuario**
9. **Medir cumplimiento y posposición para mejorar la planificación**
10. **Primero lista + quick actions + buckets temporales; luego sofisticación**
11. **No convertir esto en un clon de Todoist con taxonomía de sobra**

---

## 14. Siguiente paso recomendado

Siguiente paso práctico:

1. diseñar la IA definitiva de navegación
2. redefinir `/` como **Hoy**
3. mover el monitor actual a `/monitor`
4. diseñar el componente base de **tarjeta plegable**
5. definir el modelo de bucket temporal y su semántica de cumplimiento
6. diseñar el módulo **Progreso** dentro de Revisar
7. implementar primero el loop mínimo:
   - añadir
   - ver Inbox
   - planificar con bucket temporal
   - reordenar manualmente
   - completar
   - posponer
   - filtrar por hashtag
   - medir cumplimiento / posposición

Ese sería el primer corte que ya cambia el producto de verdad.

---

## 15. Fuentes usadas

Fuentes oficiales de Todoist:

- [Todoist Features](https://www.todoist.com/features)
- [Use the Inbox in Todoist](https://www.todoist.com/help/articles/use-the-inbox-in-todoist-HwHvYErS)
- [Plan your day with the Todoist Today view](https://www.todoist.com/help/articles/plan-your-day-with-the-todoist-today-view-UVUXaiSs)
- [Use the task view to manage tasks in Todoist](https://www.todoist.com/help/articles/use-the-task-view-to-manage-tasks-in-todoist-eDeRDO0C)
- [Introduction to sections](https://www.todoist.com/help/articles/introduction-to-sections-rOrK0aEn)
- [Introduction to labels](https://www.todoist.com/help/articles/introduction-to-labels-dSo2eE)
- [Introduction to filters](https://www.todoist.com/help/articles/introduction-to-filters-V98wIH)
- [Introduction to recurring dates](https://www.todoist.com/help/articles/introduction-to-recurring-dates-YUYVJJAV)
- [Customize views in Todoist](https://www.todoist.com/help/articles/customize-views-in-todoist-AoHhBxFdZ)
- [Todoist on Google Play](https://play.google.com/store/apps/details?id=com.todoist)

Fuentes inspeccionadas en `adhd-assistant`:

- `hermes/skills/adhd-assistant/manifest.yaml`
- `hermes/skills/adhd-assistant/webapp/app.py`
- `hermes/skills/adhd-assistant/webapp/templates/index.html`
- `hermes/skills/adhd-assistant/webapp/templates/calendar.html`
- `hermes/skills/adhd-assistant/webapp/static/dashboard.js`
- `hermes/skills/adhd-assistant/webapp/services/runtime_monitor.py`
- `hermes/skills/adhd-assistant/engine/reconcile.py`
- `hermes/skills/adhd-assistant/engine/state_store.py`
