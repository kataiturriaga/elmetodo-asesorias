# Caso de estudio: Asesorías V2

**Producto:** El Metodo — tier coached (asesorías personalizadas)
**Rol:** Product Designer + PM
**Período:** Abril–Mayo 2026
**Estado:** En curso

---

## El problema

La app de asesorías existía como producto separado, con una experiencia muy por debajo del nivel de calidad de la app de suscripción (Automática). Los usuarios del tier coached pagaban más pero recibían una experiencia peor.

## El contexto

- Equipo: 2 personas (diseñadora/PM + desarrollador)
- Tres canales de entrada al tier: link externo, WhatsApp, upgrade desde la app
- Sin IAP — el pago ocurre fuera de la app
- Benchmark de calidad: Automática (ya en producción)
- Deadline: handoff 30 mayo 2026

## Decisiones

### 1. Rediseño de la pantalla de Progreso → Revisiones

**Fecha:** Mayo 2026  
**Área:** Retención / experiencia del cliente de asesoría

#### De dónde veníamos

La pantalla `Progreso` original tenía cuatro problemas críticos:

**1. Gráfica que comunica fracaso cuando el peso se estanca.**
La gráfica mostraba solo el peso corporal. Si el peso no varía entre revisiones, la línea es plana y el área verde rellena debajo queda visualmente vacía. El diseño no tenía mecanismo para comunicar "sin variación de peso ≠ sin progreso" — si el peso se estanca mientras la composición corporal mejora, el usuario solo ve estancamiento.

**2. Memes en los estados vacíos.**
Cuando el usuario no tenía fotos subidas, la sección "Tus fotos" mostraba imágenes tipo meme con texto sarcástico ("Yo buscando tu revisión inexistente", "Bueno, ¿dónde está tu revisión?"). El intento de humor aligeraba la fricción pero introducía disonancia: en el momento de mayor vulnerabilidad del usuario (todavía no ha completado ninguna revisión), el tono era burlón. Además mezclaba el objetivo de la sección — comparar transformación física — con entretenimiento.

**3. Solo peso.**
Un único dato numérico no cuenta la historia completa de una transformación. El peso puede estancarse mientras el porcentaje de grasa baja y la masa muscular sube. Mostrar solo peso es potencialmente desmotivante y engañoso.

**4. Sin jerarquía ni narrativa.**
La pantalla trataba todos los elementos con el mismo peso visual: el header con el CTA de revisión, los datos del perfil, la gráfica y las fotos competían en igualdad. No había un dato protagonista, ni una dirección emocional clara.

---

#### Qué decidimos y por qué

**Decisión 1 — Renombrar la pantalla de "Progreso" a "Revisiones"**

El nombre "Progreso" promete una narrativa que la pantalla no podía cumplir si los datos eran planos o escasos. "Revisiones" es más honesto: nombra el ritual (la revisión quincenal) sin hacer una promesa sobre su contenido. Reduce la presión semántica y abre la puerta a un estado vacío más digno.

**Decisión 2 — El comparador primera/última como hero**

En lugar de una gráfica de evolución como elemento principal, pusimos el comparador fotográfico primera revisión vs. última revisión como primera zona de la pantalla. Razón: la fotografía es el dato más visceral y el que tiene mayor impacto emocional. Es también el que el usuario más quiere mostrar a alguien. Una imagen de uno mismo hace 6 meses comparada con hoy dice más que cualquier curva de datos.

El delta calculado debajo del comparador ("−4.2% grasa corporal · 18 semanas · 9 revisiones") convierte la foto en argumento: no solo "me veo diferente" sino "estos son los números que lo explican".

**Decisión 3 — Añadir % de grasa corporal como segunda métrica**

Se añadió análisis de composición corporal por IA (% grasa) a partir de las fotos de cada revisión. Esta métrica se muestra en la gráfica junto al peso, en series separadas. El motivo: desacoplar el peso de la narrativa de progreso. Si el peso está estancado pero el % de grasa baja, la gráfica lo hace visible — el usuario no puede interpretar estancamiento como fracaso.

El % de grasa no entra en el score del ciclo (margen de error de IA ~1-3% lo hace poco fiable como input de puntuación) pero sí se muestra como dato informativo.

**Decisión 4 — Score del ciclo como sistema de gamificación**

Se introdujo un score por ciclo (cada 2 semanas) basado en dos métricas de actividad: % de entrenos completados y % de días con objetivo de pasos cumplido. A esto se suma un bonus de racha con progresión Fibonacci (racha 1→+1, 2→+2, 3→+4, 4→+8...) que premia la consistencia acumulada.

El score permite que el carrete de revisiones comunique progreso incluso cuando el peso no se mueve: el usuario puede ver que su score 142 en R1 subió a 172 en R7. Eso es evidencia de mejora en hábitos aunque el cuerpo tarde en responder.

**Decisión 5 — Carrete de fotos como timeline cronológico**

En lugar de una lista vertical de tarjetas (que escalaría mal con 20+ revisiones), el histórico se presenta como un scroll horizontal de fotos frontales con el score y el peso de cada ciclo. Esto permite escanear toda la historia visualmente sin scrollear páginas.

**Decisión 6 — Racha como dato de primer nivel**

La racha de revisiones consecutivas (sin saltarse ninguna) se muestra junto al título del carrete. Motivo: la racha es el indicador más directo de compromiso con el método. Un cliente con racha 9 es un cliente retenido. Hacerla visible refuerza el hábito.

---

#### Estructura final

```
Pantalla Revisiones
  ├── Hero: Comparador primera revisión vs última + delta
  ├── Composición corporal: Gráfica dual peso + % grasa
  └── Historial: Carrete horizontal de revisiones + racha
```

Detalle de revisión individual (accesible desde gráfica o carrete):
- 3 fotos (frontal, lateral, espalda)
- Score con desglose (base + bonus racha)
- Autopuntuación del ciclo (Dieta / Entreno / Pasos)

---

#### Decisión adicional — Dos elementos añadidos tras la primera versión

La primera versión de la pantalla incluía hero comparador, curva de composición corporal e historial de fotos. Al revisarla quedaron fuera dos elementos que estaban en la definición original:

**1. Evolución del score por ciclo**

El carrete mostraba el score en cada card, pero no había ningún elemento que comunicara la trayectoria del score a lo largo del tiempo — que el usuario es más consistente hoy que hace 4 meses. Se añadió una sección con un gráfico de barras ("EVOLUCIÓN SCORE") donde cada barra representa un ciclo, con progresión de opacidad de la primera a la última y la más reciente en verde completo. Debajo, una insight card con un mensaje contextual que interpreta el dato para el usuario ("Mejoraste un 24% respecto al primer ciclo").

El título usa Open Sans Condensed ExtraBold en tamaño grande — mismo tono visual agresivo que el resto de la app.

**2. Card de próxima revisión**

La revisión quincenal es un ritual. Sin un recordatorio de cuándo toca la siguiente, el usuario no tiene ninguna señal de anticipación entre ciclos. Se añadió una card compacta con el número de días restantes como dato prominente, una barra de progreso que muestra en qué día del ciclo de 14 está, y el texto "día X de 14". El objetivo no es informar — es crear la sensación de que algo está por pasar.

---

#### Decisión adicional — Evolución del score: estático, no interactivo

Durante el diseño se evaluó si el componente de score por ciclo (barras) debería ser interactivo: tocar una barra actualizaría el número prominente en la parte superior con el score de ese ciclo.

Se descartó por dos razones:

1. **Duplica al carrete.** El historial de fotos ya muestra el score de cada ciclo. Añadir una segunda vía de acceso al mismo dato fragmenta la atención sin añadir valor.
2. **El trabajo de esta sección es la tendencia, no el detalle.** El número grande muestra el score más reciente — el más relevante para el usuario. El gráfico comunica el arco de mejora. Ninguno de los dos necesita interacción para cumplir su función.

Si en el futuro se añade interacción a las barras, el destino correcto sería el **detalle completo de esa revisión** (fotos + desglose de score), no solo el número. Pero eso es exactamente lo que ya hace el carrete, así que habría que justificar tener dos puntos de entrada al mismo lugar.

---

#### Lo que quedó pendiente de validar

- ¿El usuario quiere poder comparar cualquier par de revisiones (no solo primera vs última)? Si sí, el comparador pasa de estático a interactivo — mayor complejidad de implementación.
- Gestión del estado de 1 sola revisión: el hero no puede ser comparador todavía. Se muestra como "Tu punto de partida" con la primera foto centrada.

---

### 2. Rediseño del histórico de marcas por ejercicio

**Fecha:** Mayo 2026
**Área:** Retención / motivación / progreso de entrenamiento

#### De dónde veníamos

La sección `LastTrainingBestLogsSection` mostraba todos los ejercicios de la última sesión con su última marca registrada: un snapshot estático del día anterior. El dato respondía a "¿qué hice ayer?" pero no a "¿estoy mejorando?".

Cada ejercicio aparecía como una fila con nombre y valor numérico, sin ningún elemento temporal. Era útil como referencia de carga para la sesión actual, pero no tenía valor narrativo ni motivacional — no existía ninguna señal de tendencia.

#### Qué decidimos y por qué

**Decisión — Cambiar de granularidad sesión → ejercicio, y de última marca → evolución histórica**

Se sustituyó la sección por el componente `GraficoEjerciciosEjemplo`: una tarjeta por ejercicio con una línea de progreso a lo largo de las sesiones completadas.

El cambio de modelo es conceptual: en lugar de preguntarse "¿cuánto hice ayer?", la pantalla ahora responde "¿cómo ha evolucionado este ejercicio en el tiempo?". La diferencia no es de datos — ambos tienen acceso al historial — sino de qué pregunta se considera más relevante para el usuario.

Motivo de la decisión: la última marca es útil operativamente (preparar la sesión), pero lo que retiene al usuario es la evidencia de mejora. Una curva ascendente en hip thrust a lo largo de 8 semanas es un argumento visual que ninguna fila de tabla puede dar.

#### Cómo funciona el componente

El componente cubre 7 tipos de entrenamiento con métricas distintas:

| Tipo | Métrica |
|---|---|
| Default (fuerza) | Peso en kg |
| Superserie | Peso en kg, dos ejercicios combinados |
| Circuito | Peso en kg, lista de ejercicios |
| Hyrox For Time | Tiempo (mm:ss) |
| Hyrox EMOM | Tiempo, con selector de ronda |
| Hyrox Rondas | Tiempo, delta vs sesión anterior |
| Hyrox AMRAP | Rounds (ej. "4,2 rondas") |

La propiedad `CompletedSesions` (0–4) controla cuántos puntos aparecen en la línea. En 0 sesiones, el área del gráfico se reemplaza por un empty state ("Sin marcas que mostrar aún / ¡Realiza tu primer entrenamiento!") — actualmente implementado solo para el tipo Default.

El header de cada tarjeta muestra el valor métrico actual y el delta respecto a la sesión anterior en `brand/primary`, de forma que la mejora es el dato protagonista, no el valor absoluto.

#### Lo que quedó pendiente

- El empty state para `CompletedSesions=0` solo existe en el tipo `Default`. Los 6 tipos restantes (Superserie, Circuito, Hyrox×4) no tienen este estado implementado.
- Los colores del gráfico (verde `rgb(0,238,0)`, grid lines, labels de ejes) están hardcodeados sin variable de design token — deuda técnica a limpiar antes del handoff.

---

### 3. Diseño de la pantalla principal de dieta

**Fecha:** Mayo 2026
**Área:** Consulta de dieta / experiencia diaria del cliente

#### De dónde veníamos

La pantalla de dieta existente separaba las dos decisiones del usuario en dos pantallas distintas: primero elegías el número de comida, luego veías las opciones de esa comida. Dos taps, dos momentos de orientación.

El problema de fondo: el 58% de los usuarios abre la app justo antes de cada comida. Cada pantalla extra en ese momento es fricción real.

Además, el modelo de uso de la app es puramente de consulta — la app no registra qué opción elige el usuario. No hay selección explícita. La pantalla debe ser una referencia rápida, no un flujo de acción.

---

#### El espacio del problema

Los datos de frecuencia de uso definían tres segmentos:

| Segmento | Frecuencia | Lo que necesita |
|---|---|---|
| 58% | Antes de cada comida (3–5x/día) | Ver opciones de la comida actual inmediatamente |
| 35% | Una vez al día (probablemente mañana) | Hojear todas las comidas del día |
| 30% | Una vez a la semana | Planificar y hacer la compra |

> ⚠️ Los comportamientos del 35% y 30% son hipótesis — solo tenemos dato de frecuencia de apertura, no de contexto de uso.

Los perfiles del 58% y 35% tienen necesidades **compatibles**: el primero necesita la comida actual con sus opciones, el segundo necesita ver el día entero. Un mismo diseño puede cubrir ambos si jerarquiza bien.

El 30% semanal se descartó como caso primario — su comportamiento es demasiado diferente. Se cubre con funcionalidad secundaria (vista semanal) sin contaminar el diseño principal.

---

#### Patrones explorados

Se evaluaron cuatro patrones con prototipos en Figma antes de tomar decisiones:

**Chips + opciones verticales** — Chips scrolleables para navegar comidas. Al cambiar de chip, las opciones aparecen debajo. Simple y conocido. Cubrió bien los dos perfiles principales.

**Tabs fijos** — Tab bar con las comidas como tabs, opciones debajo. Más limpio visualmente pero las abreviaturas (C.2, C.3) perdían contexto.

**Lista + bottom sheet** — Todas las comidas del día como lista con hora visible. Al tocar una se abre un panel inferior con las opciones. Comunica el día entero pero requería definir el comportamiento del sheet.

**Timeline** — Línea de tiempo vertical con la comida actual expandida y las demás colapsadas. El punto verde como "estás aquí" era inmediatamente legible. Las comidas pasadas y futuras tenían jerarquía visual clara.

La decisión final combinó la navegación por chips del primer patrón con cards visuales enriquecidas.

---

#### Qué decidimos y por qué

**Decisión 1 — Chips para navegar comidas, imagen como protagonista de la card**

En lugar de texto puro, cada opción tiene una fotografía del plato a ancho completo con un badge de "Opción 1/2/3" superpuesto. Debajo: nombre del plato y número de recetas asociadas.

Motivo: la comida es altamente visual. Ver el plato reduce la carga cognitiva de la decisión más que cualquier texto descriptivo. El badge superpuesto identifica la opción sin añadir una línea de texto adicional.

**Decisión 2 — Accordion de ingredientes dentro de la card**

Cada card tiene un link "Ingredientes ↑" que expande la card inline mostrando la lista de cantidades. Solo una card expandida a la vez (acordeón exclusivo).

El motivo de esta decisión fue dar acceso rápido a los ingredientes sin cambiar de pantalla — el 58% que consulta antes de comer puede verificar cantidades en el mismo contexto sin perder de vista las otras opciones.

La imagen permanece visible en la card expandida para mantener coherencia visual y evitar el salto de alineación que ocurre cuando el área de ingredientes arranca desde un punto diferente al del texto.

**Decisión 3 — "Ver recetas y detalle" como botón secundario, no CTA primario**

Junto al link de ingredientes aparece un botón outlined "Ver recetas y detalle". Se eligió peso visual secundario (outlined, no relleno) porque la pantalla es de consulta — no hay acción primaria. Un botón verde sólido comunicaría "acción principal de la pantalla" cuando no la hay.

**Decisión 4 — Pantalla de detalle con tabs por opción**

Al entrar al detalle desde una card, se llega a una pantalla con:
- Tabs 1/2/3 para navegar entre opciones sin volver atrás
- Imagen grande del plato
- Toggle Raciones/Unidades para ver los ingredientes en el formato preferido
- Lista completa de ingredientes con cantidades
- "Ver equivalencias de ingredientes" para sustituciones
- Recetas asociadas como cards horizontales

Los tabs en el detalle resuelven la comparación en profundidad: si entras por Opción 1 y quieres ver los ingredientes de Opción 2 en modo unidades, lo tienes con dos taps sin volver a la pantalla principal.

El estado de entrada al detalle (qué tab queda activo) debe mapear a la opción desde la que se navegó.

---

#### Estructura final

```
Pantalla principal — dieta
  ├── Chips scrolleables → navegar entre comidas del día
  └── Cards por opción (imagen full-width + badge + nombre)
        └── [tap Ingredientes] → accordion con cantidades
              └── "Ver recetas y detalle" → Pantalla de detalle

Pantalla de detalle
  ├── Tabs 1/2/3 → navegar opciones sin volver atrás
  ├── Imagen grande del plato
  ├── Toggle Raciones / Unidades
  ├── Lista de ingredientes
  ├── Ver equivalencias de ingredientes
  └── Recetas para esta opción (cards horizontales)
```

---

#### Lo que quedó pendiente de validar

- Las hipótesis de perfil de usuario — solo tenemos frecuencia de apertura, no contexto ni motivación. El diseño asume que el 35% planifica de mañana, pero podría abrir a mediodía para ver qué queda del día.
- Comportamiento del chip activo al abrir la app — ¿siempre la primera comida del día, o la más cercana en el tiempo?
- Estado vacío — qué ve el usuario si una comida no tiene opciones asignadas aún.
- Cards con nombres de plato largos — el nombre puede wrappear y romper la proporción de la card.
- Máximo de opciones por comida — actualmente se asumen 3. Si puede haber 4 o más, la pantalla necesita adaptarse.

---

### 4. Cálculo del % graso corporal: IA pura vs. IA + validación del coach

**Fecha:** Mayo–Junio 2026
**Área:** Composición corporal / diferenciación del tier coached

#### De dónde veníamos

El flujo de revisión quincenal incluye análisis de % de grasa corporal a partir de las fotos del cliente. La decisión de diseño que quedó abierta: ¿quién firma ese número?

Dos rutas técnicamente viables, con implicaciones de producto muy distintas.

---

#### Opciones exploradas

**Opción A — 100% IA (resultado al momento)**

El cliente sube las fotos y recibe su % graso en el instante, con una etiqueta de "cálculo automático". Sin espera, sin intermediarios.

| Ventajas | Inconvenientes |
|---|---|
| Experiencia inmediata | Valor percibido bajo ("estimación de app") |
| Sin carga operativa para coaches | Menos diferenciación frente a otras apps de IA |
| Implementación simple | Difícil de empaquetar como servicio premium |

**Opción B — IA + validación del coach**

La IA genera un % propuesto en cuanto suben las fotos. El coach ve ese número en su dashboard junto a las fotos y una guía visual, y lo confirma, ajusta o pide nuevas fotos. El cliente recibe el número ya revisado por una persona, con un mensaje en tono de marca ("Inazio ha revisado tu composición").

| Ventajas | Inconvenientes |
|---|---|
| Valor percibido alto — encaja con "mi coach me ha evaluado" | Más superficie de diseño: flujo de espera + dashboard de coaches |
| Refuerza el modelo coached y la marca personal | Requiere definir operación: quién revisa, en cuánto tiempo, con qué volumen |
| Abre la puerta a ofrecerlo como add-on de pago | Sin SLA claro, la espera puede frustrar al cliente |
| Honesto: hay revisión humana real, no solo marketing | — |

---

#### Estado de la decisión

**Pendiente de decisión en reunión de equipo.** Las preguntas abiertas que desbloquean el camino:

1. **Scope:** ¿Para toda la base de usuarios o solo para el tier coached?
2. **Modelo de negocio:** ¿Feature incluida o servicio de pago (add-on)?
3. **Capacidad operativa:** Si se elige la Opción B, ¿cuántas revisiones al mes puede revisar el equipo y cuántos minutos cuesta cada una?

La Opción B tiene mejor alineación con la propuesta de valor del tier coached ("tu coach evalúa tu progreso") y mayor potencial de monetización. Pero no es viable sin definir primero el SLA y la operación. Diseñar los flujos antes de cerrar eso sería construir sobre una premisa no validada.

---

#### Lo que quedó pendiente de diseñar (si se elige Opción B)

- **Flujo cliente:** pantalla de espera post-revisión + notificación de entrega del resultado
- **Dashboard coaches:** vista de revisión pendiente, % sugerido por IA, control para confirmar/ajustar/rechazar fotos
- **SLA visible:** cómo comunicar al cliente cuándo recibirá el resultado y qué pasa si se pasa del plazo

---

## Materiales

- Figma: (añadir link cuando esté disponible)
- Docs relacionados: `asesorias/`
