# Mejoras Identificadas — CongresoGT

> Análisis desde la perspectiva de un ciudadano que quiere votar informado.
> Prioridad: **Alta 🔴 / Media 🟡 / Baja 🟢**

---

## 1. Página de Inicio (`/`)

| Prio | Mejora |
|------|--------|
| 🔴 | **Falta contexto temporal.** El usuario no sabe a qué legislatura corresponden los datos. Agregar el período legislativo activo (ej. "Legislatura 2024–2028") en el hero. |
| 🔴 | **El nombre del sitio no comunica valor.** "Audita a tu Congreso" es bueno pero no hay ninguna explicación de *qué datos* tenemos ni *hasta cuándo* están actualizados. Agregar una línea con la última fecha de actualización de datos. |
| 🟡 | **No hay acceso rápido a los diputados por mi departamento.** Un botón "Encuentra a tu diputado" con un select de distritos llevaría directamente a los representantes del ciudadano. |
| 🟡 | **Las métricas de la home no dicen nada por sí solas.** "160 Diputados / 22 Bancadas / 120 Sesiones" son números fríos. Agregar indicadores de tendencia, ej. la sesión más reciente, el diputado más ausente, la votación más polémica. |
| 🟢 | **El sitio no tiene navegación de breadcrumbs.** En páginas de detalle es fácil perderse. |

---

## 2. Listado de Diputados (`/congressmen`)

| Prio | Mejora |
|------|--------|
| 🔴 | **Las tarjetas no muestran ningún dato de rendimiento.** El ciudadano ve foto + nombre + bancada pero no sabe si el diputado asiste o no. Agregar un indicador visual de asistencia (badge de color o barra pequeña) por tarjeta. |
| 🔴 | **No se puede ordenar.** No hay forma de ordenar por "más ausente", "más votaciones en contra", etc. Al menos un select de ordenamiento ("Ordenar por: Nombre / Asistencia / Ausencias") sería de gran valor. |
| 🟡 | **El status del diputado no se muestra.** Si un diputado ya no está en funciones (renunció, fallecido, reemplazado), aún aparece sin ningún indicador de estado. |
| 🟡 | **Falta filtro por estado (activo/inactivo).** |
| 🟢 | **Sin contador de resultados visibles.** Al filtrar no aparece cuántos diputados cumplen el criterio. |

---

## 3. Perfil Individual del Diputado (`/congressman/[id]`)

| Prio | Mejora |
|------|--------|
| 🔴 | **El "Calendario de Sesiones" es un mosaico de íconos sin estructura temporal.** No comunica cuándo fue cada ausencia. Un gráfico de tipo heatmap por mes/año (tipo GitHub contribution graph) sería mucho más efectivo para detectar rachas de ausencia. |
| 🔴 | **Solo se muestran los últimos 5 votos.** Un ciudadano quiere buscar cómo votó en una ley específica. Mostrar todos los votos con paginación o una lista extendida con búsqueda por tema. |
| 🔴 | **No hay desglose de asistencia por año.** La asistencia puede ser excelente al inicio del mandato pero pésima al final. Un gráfico de barras agrupadas por año (o por semestre) mostraría la evolución del comportamiento. |
| 🔴 | **Las votaciones no tienen contexto.** En "Últimos Votos" el texto se corta a 60 caracteres y no se muestra el resultado de la votación ni si el diputado votó con la mayoría o en minoría. |
| 🟡 | **Falta el cargo/rol del diputado.** Si es presidente del Congreso, vicepresidente de comisión, etc., esa información es ausente. |
| 🟡 | **No se sabe cuándo fue electo / en qué período está.** El perfil no indica si es primer mandato, reelecto, etc. |
| 🟡 | **No hay indicador de "alineamiento con bancada".** Cuántas veces votó diferente a su propio partido revela independencia o disidencia. Un porcentaje de cohesión de voto vs. partido daría información política valiosa. |
| 🟡 | **La tendencia de votación global (donut) mezcla todos los votos sin ponderar por importancia.** Una ley de presupuesto vale igual que una votación de trámite. Podría segmentarse en "votaciones ordinarias" vs. "votaciones clave". |
| 🟢 | **No hay enlace al perfil oficial del diputado** en el sitio web del Congreso. |
| 🟢 | **Las tarjetas del listado no tienen `title` en los badges de sesión** — el tooltip sí aparece pero solo en pantallas no táctiles. |

---

## 4. Listado de Bancadas (`/parties`)

| Prio | Mejora |
|------|--------|
| 🔴 | **Solo muestra nombre y número de diputados, sin ninguna métrica de desempeño.** Agregar el porcentaje promedio de asistencia y el porcentaje de votos "a favor" al listado permitiría comparar bancadas de un vistazo. |
| 🟡 | **No hay ordenamiento.** Ordenar por asistencia promedio, por número de diputados, por cohesión interna. |
| 🟢 | **Sin descripción ni ideología resumida de cada bancada.** |

---

## 5. Perfil de Bancada (`/party/[id]`)

| Prio | Mejora |
|------|--------|
| 🔴 | **La lista de integrantes no muestra su asistencia individual.** Al ver los miembros de una bancada, el ciudadano no sabe cuáles son los que más faltan. Agregar un pequeño badge o barra de asistencia por cada diputado en la grilla. |
| 🔴 | **No hay historial de votaciones de la bancada.** ¿En qué leyes importantes votó esta bancada? Una tabla/lista de las últimas 10 votaciones con el resultado de la bancada sería muy valioso. |
| 🟡 | **No hay indicador de cohesión interna.** ¿Cuántas veces votaron todos juntos vs. divididos? Un % de unidad de voto es un dato político clave. |
| 🟡 | **La asistencia se muestra como total absoluto, no como promedio por diputado por sesión.** Los números grandes en bancadas numerosas distorsionan la comparación. Mostrar el promedio de asistencia por diputado (%). |

---

## 6. Perfil de Distrito (`/district/[id]`)

| Prio | Mejora |
|------|--------|
| 🔴 | **Es la página más importante para el ciudadano promedio y está casi vacía.** Actualmente solo muestra la misma estructura que la bancada. Necesita un enfoque geográfico: los diputados que representa SI son de mi departamento, su asistencia, y sus votos más recientes. |
| 🔴 | **No hay datos sobre representación proporcional.** Cuántos diputados le corresponden al distrito vs. cuántos tiene, la relación habitantes/diputado. |
| 🟡 | **No hay filtro de bancadas dentro del distrito.** Un departamento puede estar representado por múltiples partidos; una distribución visual (pie chart de bancadas en el distrito) sería útil. |

---

## 7. Listado de Sesiones (`/sessions`)

| Prio | Mejora |
|------|--------|
| 🟡 | **No hay filtro por año o tipo de sesión.** Con muchas sesiones, el listado se vuelve difícil de navegar. Un filtro por año y por tipo (ordinaria/extraordinaria) ayudaría. |
| 🟡 | **La barra de asistencia no colorea por umbral.** Si la asistencia está bajo el quórum (ej. <80%) debería marcarse en rojo. |
| 🟢 | **No aparece el número de votaciones realizadas en cada sesión en el listado.** |

---

## 8. Detalle de Sesión (`/session/[id]`)

| Prio | Mejora |
|------|--------|
| 🔴 | **No se muestra quiénes estuvieron ausentes.** El ciudadano quiere saber: ¿quién faltó a esta sesión? Una lista colapsable de ausentes (con link a su perfil) sería el dato más buscado. |
| 🔴 | **Las votaciones no muestran su resultado (aprobada/rechazada) en el listado.** El ciudadano entra a la sesión y ve una lista de temas, pero no sabe el resultado de ninguno sin hacer click. Agregar un badge "APROBADO / RECHAZADO" a cada votación del listado. |
| 🟡 | **No se muestra la duración de la sesión** (hora inicio - hora fin si está disponible). |

---

## 9. Listado de Votaciones (`/votations`)

| Prio | Mejora |
|------|--------|
| 🔴 | **No hay indicador de resultado en el listado.** Cada tarjeta muestra el tema pero no si fue aprobada o rechazada. Un badge color verde/rojo es esencial para que el ciudadano escanee la lista. |
| 🔴 | **La búsqueda es solo por texto exacto.** No hay filtro por fecha, por resultado (aprobada/rechazada), ni por bancada. Un filtro por resultado sería el más valioso ("Ver solo votaciones rechazadas"). |
| 🟡 | **No hay un sistema de "votaciones destacadas" o etiquetas temáticas.** El ciudadano no sabe cuáles son las más importantes (presupuesto, salud, educación). Un sistema de tags manuales o categorizados haría el listado mucho más accionable. |
| 🟢 | **El identificador numérico (`#N`) del listado no corresponde al número de expediente oficial.** Podría causar confusión. |

---

## 10. Detalle de Votación (`/votation/[id]`)

| Prio | Mejora |
|------|--------|
| 🟡 | **No se muestra el margen de victoria.** "APROBADO" no dice nada sin el margen (ej. "105 a 55"). Un subtítulo con el conteo exacto debajo del badge de resultado sería muy claro. |
| 🟡 | **La lógica de APROBADO/RECHAZADO es una heurística simple** (`favor > contra`). El quórum real del Congreso guatemalteco requiere mayoría absoluta de 160 (81 votos). Esto puede generar información incorrecta. |
| 🟡 | **No se indica si la votación requirió mayoría calificada.** Algunas leyes requieren 2/3. Esto cambiaría la interpretación del resultado. |
| 🟢 | **Los votos individuales no muestran el distrito del diputado** al hacer hover/ver la tarjeta, solo el nombre y la bancada. |

---

## 11. Navegación General

| Prio | Mejora |
|------|--------|
| 🔴 | **No existe una página de "Comparar Diputados"** que permita al ciudadano poner dos o más diputados lado a lado (asistencia, votos a favor, en contra). Esta es una de las funcionalidades más pedidas en herramientas de transparencia legislativa. |
| 🔴 | **No hay un "Ranking de Diputados"** — una tablita ordenada por asistencia o por coherencia de voto con una barra visual sería extremadamente útil para que el ciudadano identifique a los mejores y peores. |
| 🟡 | **Sin página de "Acerca de"** que explique metodología, fuente de datos, limitaciones del crawler, y quiénes mantienen el proyecto. La transparencia sobre la herramienta genera confianza. |
| 🟡 | **Sin modo de compartir.** El ciudadano quiere compartir el perfil de un diputado en WhatsApp/redes. Agregar meta tags Open Graph con foto, nombre y estadística principal mejoraría enormemente la viralidad orgánica. |
| 🟢 | **Sin modo de impresión / exportar a PDF.** Para uso en medios o grupos cívicos. |

---

## 12. Mejoras de UX/Diseño

| Prio | Mejora |
|------|--------|
| 🟡 | **El calendario de sesiones del diputado** (mosaico de cuadritos) no está ordenado en filas por mes/año, por lo que es difícil identificar rachas. Reordenar en una grilla de 12 columnas (una por mes) aclararía el patrón estacional. |
| 🟡 | **Los colores de partidos son todos azules.** Asignar un color distinto a cada bancada (ej. generado deterministamente del nombre) mejoraría la diferenciación visual en los gráficos de barras apiladas. |
| 🟢 | **Accesibilidad:** los colores rojo/verde no son suficientes para daltonismo. Agregar íconos (✔ / ✘) además de color en los indicadores de asistencia y voto. |
| 🟢 | **Sin indicador de "datos en tiempo real vs. histórico"** — el usuario no sabe si lo que ve es el período completo o solo el año actual. |
