# Caso de estudio: Asesorías V2

**Producto:** El Metodo — tier coached (asesorías personalizadas)
**Rol:** Product Designer + PM
**Período:** Abril–Junio 2026
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

#### Decisión tomada: Opción B — IA + validación del coach

Se elige la Opción B. La IA genera el % propuesto y el coach lo revisa antes de enviarlo al cliente.

**Flujo definitivo:**

```
Cliente sube fotos
  → IA calcula % graso automáticamente
  → Cliente recibe: "Gracias, en 1–2 días te daré el resultado"
  → Coach revisa en dashboard
       ├── Primera revisión: contrasta estimación IA con biblioteca de referencia visual
       └── Revisiones siguientes: contrasta + usa evaluaciones anteriores del cliente
              para calibrar el número considerando la tendencia
  → Cliente recibe resultado firmado por el coach
```

El delay de 1–2 días no es solo operativo — elimina la percepción de automatización y mantiene el valor percibido del tier coached ("mi coach me ha evaluado").

---

#### Investigación técnica: precisión del modelo de IA

Para tomar la decisión con datos reales, se realizó un análisis completo de precisión antes de comprometer el flujo. Hallazgos clave que informaron el diseño:

**Sesgo sistemático identificado:**
- Error medio (MAE): **3.43 pts** sobre 90 fotos de referencia (dataset limpio, rango 8–38%)
- Sesgo global: **+2.44 pts** — el modelo sobreestima de media
- El sesgo no es uniforme: sobreestima en personas lean, subestima en personas con más grasa (regresión hacia el centro)

**Sesgo de género crítico:**
- Mujeres: sesgo **+4.72 pts** (el modelo usa referencias de hombre por defecto)
- Hombres: sesgo **+1.18 pts**
- Solución: prompts diferenciados por género (escala Henselmans para hombres, escala distribución femenina para mujeres) → sesgo femenino cae a **+0.89 pts**

**Mejor configuración encontrada (prompt género + corrección bidireccional por tramos):**

| Configuración | MAE | Sesgo | ≤2 pts |
|---|---|---|---|
| Prompt universal, sin corrección | 3.43 | +2.44 | 40% |
| Prompt universal −2.5 flat | 2.69 | −0.06 | 58% |
| Prompt por género, sin corrección | 2.81 | +0.16 | 48% |
| Prompt género + tramos bidireccional | **2.10** | ~0 | **65%** |

La corrección bidireccional responde al patrón de regresión hacia el centro: baja las estimaciones lean, sube las estimaciones altas.

**Fotos no evaluables:** el modelo no falla con gracia ante fotos malas (recortadas, de espaldas) — inventa una estimación alta con el mismo formato que una estimación correcta. Solución de producto: clasificar calidad de foto antes de mostrar el resultado, y marcar las estimaciones poco fiables en el dashboard del coach.

---

#### Integración en el flujo de revisión existente (pendiente de confirmar con Inazio y Jorge)

**Hipótesis:** el % graso no requiere un flujo de revisión propio — se integra como un campo más dentro de la revisión quincenal que el coach ya realiza.

El coach ya entra a revisar cada cliente con sus fotos, peso y notas del ciclo. Añadir el % graso supone una comprobación adicional de ~30 segundos en ese mismo contexto: ver la estimación de la IA, compararla con el historial del cliente y ajustarla si lo considera necesario antes de confirmar la revisión.

Esto implica:
- **Sin SLA nuevo** — usa el mismo plazo que la revisión (1-2 días)
- **Sin notificación extra** — llega junto con el aviso de revisión pendiente existente
- **Sin flujo de espera separado** — el cliente ya sabe que espera el resultado de su revisión
- **El coach es el algoritmo de suavizado** — tiene el criterio y el contexto del cliente para ajustar el número mejor que cualquier regla automática

En el dashboard del coach, dentro de la pantalla de revisión, se necesita:
- Estimación IA del % graso
- Histórico de los últimos 2-3 valores del cliente
- Campo editable para confirmar o ajustar el valor
- Flag si la foto no es evaluable (recortada, de espaldas)

#### Lo que quedó pendiente de diseñar

- **Dashboard coaches:** campo de % graso dentro de la pantalla de revisión existente → *resuelto en la sección 5*
- **Flujo cliente:** cómo y cuándo se muestra el resultado en la pantalla de Revisiones
- **Deploy del endpoint `/run-photo`:** en revisión por dev, pendiente de merge a producción

---

#### Propuesta de hoja de ruta — De Gemini a modelo propio

*Propuesta para presentar a Inazio y Jorge.*

El lanzamiento con Gemini no es el destino — es el punto de partida. Cada revisión que el coach realice genera un ejemplo etiquetado de forma gratuita (foto + % graso validado por un experto). En un mes, eso son ~4.000 ejemplos: suficiente para plantearse entrenar un modelo propio.

```
AHORA → MES 1 → MES 2–3 → FUTURO
```

**AHORA — Lanzamiento**
- Prompts ♂/♀ diferenciados
- Peso + altura como contexto biométrico
- Coach ajusta en la revisión existente (sin flujo nuevo)
- *MAE actual: ~2.1 pts*

**MES 1 — Acumulación de datos**
- Cada revisión = 1 foto etiquetada con el % validado por el coach
- ~4.000 ejemplos en el primer mes, coste 0€
- El workflow de negocio genera el dataset de entrenamiento como subproducto

**MES 2–3 — Fine-tuning**
- Entrenar un modelo sobre los datos acumulados
- Coste estimado: ~500€ de GPU
- Comparar MAE resultante vs. Gemini para decidir si el salto vale
- *MAE objetivo: ~1.5 pts*

**FUTURO — Modelo propio**
- Un modelo que replica el criterio específico de Inazio, no el de un modelo genérico
- Ventaja competitiva difícil de replicar por competidores
- Sin dependencia de la API de Google
- *MAE objetivo: ~1.0–1.5 pts*

El argumento clave: ningún competidor tiene un dataset etiquetado por el criterio de un coach específico con cientos de clientes reales. Ese dataset es el moat, y se construye solo con lanzar.

---

### 5. Dashboard del coach: validación del % graso (card + comparador)

**Fecha:** Junio 2026
**Área:** Dashboard coaches / composición corporal

#### De dónde veníamos

La sección 4 dejó decidido el flujo (IA propone, coach valida) y pendiente su diseño en el dashboard. El primer boceto asumía que habría que crear un bloque nuevo dentro de la revisión. Al revisar la pantalla real del dashboard (`Ficha cliente - revisiones-v3`), el problema se redujo solo:

- El **% GRASO ya existía como card** en la revisión nueva, junto a peso y rendimiento, con un badge de "75% precisión".
- Las **fotos del cliente están en la misma vista**, justo debajo.
- Ya existe un **gesto de cierre global ("Mandar cambios")** que envía la revisión al cliente.

Conclusión: no hace falta ninguna pantalla nueva ni botón de confirmación propio. El diseño se reduce a **intervenir la card existente + un overlay de comparación**, y colgar la validación del envío que el coach ya hace.

---

#### Qué decidimos y por qué

**Decisión 1 — La card % GRASO con 4 estados, no un flujo aparte**

| Estado | Qué muestra |
|---|---|
| Por validar (default) | Badge ámbar "IA · Por validar", valor pre-rellenado editable, delta, género detectado, acciones Comparar / Editar |
| Confianza baja | Lo mismo + borde ámbar y los `limiting_factors` visibles ("No se ve el abdomen · Iluminación pobre") |
| Fotos no evaluables | Estimación **oculta por completo**, aviso con motivo, CTA "Pedir nuevas fotos", escape "Estimar manualmente" |
| Validado | Badge verde "✓ Validado", valor confirmado, traza de auditoría ("Estimación IA: 34% · ajustada por ti"), sin acciones |

El valor llega pre-rellenado con la estimación IA (corregida por género): el happy path es 1 clic. Así la promesa de "~30 segundos extra por revisión" se cumple — el coste marginal del caso de acuerdo es casi cero.

En el estado "no evaluable" la estimación se oculta, no se atenúa: el research demostró que el modelo inventa números con apariencia fiable ante fotos malas, y un número visible —aunque sea en gris— ancla al coach.

**Decisión 2 — Estado de validación en lugar de "% de precisión"**

El badge "75% precisión" se sustituye por el estado ("IA · Por validar" → "Validado"). Razones:

- La confianza numérica del modelo es **autoevaluación verbalizada, no probabilidad calibrada** — "75%" sugiere "acierta el 75% de las veces" y no significa eso.
- Entre 72% y 78% el coach no puede actuar distinto; entre "por validar" y "validado" sí.
- La parte útil de la confianza **se conserva como semáforo con motivos**: el nivel discreto (alta/media/baja) escala visualmente la card, y los `limiting_factors` le dicen al coach *qué* mirar, no solo *cuánto* desconfiar. Eso es lo que induce la revisión exhaustiva cuando hace falta.

**Decisión 3 — El género detectado es dato visible de primer nivel en la card**

El sesgo de género fue el mayor error sistemático del research (+4.72 pts en mujeres con prompt universal). El "♀/♂ detectado" en la card permite al coach detectar de un vistazo cuando la IA clasificó mal — el peor fallo posible se vuelve visible con una palabra.

**Decisión 4 — El comparador se abre ya posicionado, no como galería**

El overlay "Comparar" (biblioteca de referencia visual) tiene una idea central: el coach no busca en una galería — **el comparador se abre ya posicionado en la estimación de la IA**, filtrado por género. Su tarea pasa de "¿cuánto es?" a "¿más arriba o más abajo que esto?", una tarea perceptiva mucho más rápida y fiable.

Mecánica:
- Foto del cliente **fija a la izquierda** (segmented frontal/lateral/espalda) — la comparación nunca es de memoria.
- Stepper de % en pasos de 2 pts a la derecha, con fotos de referencia verificadas (dataset 8–38%).
- El chip donde apunta la IA lleva un **tag "IA"** permanente; el chip seleccionado (oscuro) marca dónde está mirando el coach. Se distingue "lo que dice la máquina" de "lo que estoy evaluando yo", y se ve si el coach se alejó de la estimación.
- CTA dinámico "Usar X%" vuelca el valor a la card y cierra.

**Decisión 5 — Validar = parte del "Mandar cambios" existente**

Sin botón de confirmación propio. Si la revisión tiene el % graso sin validar, "Mandar cambios" avisa (o bloquea — por decidir con Inazio). La validación se integra en el ritual que el coach ya tiene, que era exactamente la hipótesis de la sección 4.

---

#### Decisión adicional — El rango: de mostrarlo a quitarlo (dos pivotes)

El proceso del rango es un buen ejemplo de matar un elemento propio dos veces:

**v1 — Mostrar el rango de la IA** ("Rango IA 31–36"). Argumentos: expresa la incertidumbre en la unidad de la decisión (pts de grasa, no un % abstracto), reduce el anclaje del número único, y da margen legítimo al coach para ajustar sin sentir que contradice a la máquina.

**Pivote 1 — ¿Es fiable ese rango?** Al auditar la evaluación se descubrió que `range_low`/`range_high` se capturaron en los runs pero **nunca se analizaron**: no hay dato de cobertura. Y los indicios apuntan en contra: los LLMs son sistemáticamente sobreconfiados en su incertidumbre verbalizada, el modelo devuelve rangos típicos de ±2.5 pts mientras el within-2pts real fue 40–65%, y el rango crudo ni siquiera pasa por la corrección por tramos que sí se aplica al punto. Alternativa: rango **empírico** (punto ± MAE medido), calibrado por construcción.

**Pivote 2 — Un rango constante no es información.** Si el rango empírico es siempre ±2, no informa sobre *esta* estimación — informa sobre el sistema. Eso se comunica una vez (onboarding, tooltip en el badge), no en cada card. A partir de la segunda revisión sería ruido. **Se quitó de la card.**

Lo que queda del proceso:
- El **±2 pts vive en el onboarding** de coaches y como tooltip del badge IA.
- El **género detectado se queda** en la card — es la parte de aquella línea que sí varía por estimación.
- **Se persiste `range_low`/`range_high`/`confidence_pct` con cada revisión** junto al valor validado por el coach. Cuando la sample de producción sea suficientemente grande, la calibración del rango IA sale gratis y retroactiva — mismo mecanismo del roadmap (cada validación = ejemplo etiquetado) aplicado a la incertidumbre, no solo al punto. Coste para dev en v1: 3 campos de almacenamiento.
- **Condición de retorno:** si el rango pasa a ser adaptativo por foto (calibrado con esa sample), vuelve a la card como línea — entonces sí sería información sobre la estimación concreta.

---

#### Estructura final

```
Pantalla de revisión (existente) — Ficha cliente
  ├── Card % GRASO (intervenida)
  │     ├── Badge de estado: IA · Por validar → Validado
  │     ├── Valor pre-rellenado editable + delta vs revisión anterior
  │     ├── Género detectado (♀/♂)
  │     ├── [confianza baja] limiting factors visibles
  │     ├── [no evaluable] estimación oculta + Pedir nuevas fotos
  │     └── "Comparar" → Overlay
  ├── Overlay — Comparar composición
  │     ├── Foto cliente fija (frontal/lateral/espalda)
  │     ├── Stepper de % con tag "IA" + fotos de referencia por género
  │     └── CTA "Usar X%" → vuelca a la card
  └── "Mandar cambios" (existente) = confirmación de la validación
```

Detalles de microsemántica: el delta de % graso en verde solo cuando baja (+2% va en rojo — subir grasa no es buena noticia); en estado Validado la card vuelve a ser solo lectura, como peso.

---

#### Lo que quedó pendiente

- **Biblioteca de referencia:** el dataset de ~108 fotos verificadas (8–38%) ya existe como dataset de evaluación; usarlo como biblioteca del comparador requiere un endpoint de lectura filtrado por % y género, y **etiquetar el género** de las fotos (la columna `gender` está mayoritariamente en `unknown`).
- **Modo horquilla** del comparador (referencia del límite bajo y alto simultáneas) — evaluar si aporta sobre el stepper.
- Montar card + overlay **en contexto** sobre una copia de la ficha de cliente, con fotos reales del dataset en los placeholders.
- ¿"Mandar cambios" avisa o bloquea con % sin validar? — decidir con Inazio.
- Medir la **cobertura del rango IA** cuando exista la sample de producción (los campos ya se persisten desde v1).

---

### 6. Top bar de la ficha de cliente: centralización de acciones

**Fecha:** Junio 2026
**Área:** Dashboard coaches / arquitectura de información

#### De dónde veníamos

El top bar de la ficha de cliente (`Ficha cliente - revisiones-v3`) tenía cuatro acciones, ya mezclando dos tipos distintos:

- **Ver paneles:** Cuestionario, Notas
- **Acciones:** Mandar cambios (primaria), Siguiente cliente (navegación)

Sobre esa barra había que **añadir cuatro acciones más** sin que reventara: pausar cliente, cancelar cliente, generar comparativa de progreso (el [Generador de Cambios](../dashboard/generador-de-cambios.md)) y cambiar la modalidad de suscripción (dieta / entreno / completo).

El problema de fondo no era de espacio sino de **arquitectura de información**: la barra estaba a punto de mezclar cinco tipos de acción con jerarquías y riesgos muy distintos, tratándolos todos por igual. Meter ocho botones en fila habría saturado la barra y, peor, habría expuesto acciones destructivas (cancelar) al mismo nivel visual que un toggle de panel.

---

#### Qué decidimos y por qué

**Decisión 1 — Jerarquizar por frecuencia y riesgo, no por "todo visible"**

Se clasificaron las acciones en cinco grupos y se les asignó nivel de jerarquía según cuán frecuentes y cuán peligrosas son:

| Tipo | Acciones | Frecuencia | Riesgo | Destino |
|---|---|---|---|---|
| Ver paneles | Cuestionario, Notas | Alta | Nulo | Visibles (toggle) |
| Acción primaria | Mandar cambios | Altísima | Bajo | Botón primario lleno |
| Generar / compartir | Generar comparativa | Media | Nulo | Menú "Acciones" |
| Ciclo de vida / config | Cambiar modalidad, Pausar, Cancelar | Baja | Alto (cancelar) | Menú "Acciones" |
| Navegación de cola | Siguiente cliente | Alta | Nulo | Aislada a la derecha |

La regla: lo frecuente y seguro se ve siempre; lo raro, de gestión o destructivo se repliega en un overflow para no saturar y evitar el clic accidental.

**Decisión 2 — Un único menú "Acciones ▾" para todo lo no-primario**

Se evaluaron tres patrones: (a) comparativa visible + kebab `⋮` solo para gestión, (b) un único menú "Acciones" etiquetado con todo lo secundario, (c) todo como botones sueltos. Se eligió **(b)**: un solo punto de entrada, etiquetado con palabra (no un kebab anónimo), que agrupa comparativa + cambiar modalidad + pausar + cancelar. Más limpio y predecible que repartir las acciones entre la barra y un icono. El coste asumido: "Generar comparativa" pierde algo de descubribilidad respecto a tenerlo como botón propio — se acepta a cambio de una barra que no crece cada vez que aparece una acción nueva.

El menú se ordena por intención y seguridad: generar arriba, gestión en medio, **destructivo (Cancelar) abajo, aislado por divisor y en rojo** (`#E64E4E`).

**Decisión 3 — Chip de modalidad + estado bajo el nombre**

Al volverse la modalidad y el estado cosas que el coach puede *cambiar* desde el menú, la ficha necesita *mostrarlos* de un vistazo. Se añadieron dos chips bajo el nombre del cliente: modalidad (`Completo`) y estado (`● Activo`). El menú es el control; los chips son el espejo de ese estado. Sin ese espejo, el coach cambiaría algo a ciegas.

**Decisión 4 — "Cambiar modalidad" como nombre, no "Cambiar plan"**

Las opciones dieta / entreno / completo son modalidades del servicio. Se evitó "Cambiar plan" porque en contexto fitness "plan" se lee como *plan de entrenamiento* y chocaría con "Mandar cambios" (que justamente edita ese plan). El ítem muestra la modalidad actual como sub-label para dar contexto.

**Decisión 5 — Ítems contextuales según estado**

Las acciones de ciclo de vida no son estáticas: si el cliente está pausado, `Pausar` se convierte en `Reanudar`; si está cancelado, el estado pasa a gris/rojo y el menú ofrece `Reactivar`. La acción refleja el estado actual en lugar de ofrecer siempre la misma etiqueta.

**Decisión 6 — "Siguiente cliente" aislada como navegación de cola**

"Siguiente cliente" no es una acción *sobre* el cliente sino navegación de la cola de trabajo del coach. Se separó del bloque de acciones con un divisor vertical para reforzar que es de otra naturaleza.

---

#### Estructura final

```
Top bar (una fila)
  ← │ [Avatar] Nombre              │ Email │ N Tlf │ [Cuestionario][Notas] │ [Acciones ▾] [Mandar cambios] │ [Siguiente cliente]
        Modalidad · ● Estado

Menú "Acciones ▾" (abierto)
  ├── Generar comparativa
  ├── Cambiar modalidad — {modalidad actual}
  ├── Pausar cliente            (→ Reanudar si pausado)
  ──────────────────────────────
  └── Cancelar cliente          (rojo, destructivo)
```

Se montó como propuesta v4 en Figma sobre una copia desvinculada del header real (estilo, tokens y componentes heredados del original), sin tocar la ficha en producción.

---

#### Decisión adicional — "Cambiar modalidad": acordeón inline, no submenú

"Cambiar modalidad" (dieta / entreno / completo) necesitaba un selector dentro del menú. Se evaluaron tres patrones:

- **Submenú flyout** — rápido, pero frágil: un flyout no lleva el mismo *gap* que el menú raíz (el gap rompe el "puente" del cursor y lo cierra al moverse en diagonal), es problemático en táctil, y permite cambiar una **suscripción de pago** con un clic accidental sin confirmación.
- **Modal de confirmación** — el más seguro para una acción con impacto de facturación, pero saca al coach del flujo del menú.
- **Acordeón inline** (elegido) — el ítem se expande dentro del propio menú mostrando las 3 modalidades, con la activa marcada (check), empujando Pausar/Cancelar hacia abajo.

Se eligió el **acordeón** porque esquiva por completo el problema del gap del flyout (no hay segunda capa flotante), es robusto en táctil, y mantiene al coach en un único contexto. Regla fijada: **máximo un nivel de profundidad** y un solo acordeón abierto a la vez.

**Modelado en el design system** (el matiz que evita deuda): el "abierto/cerrado" **no** es un valor más del eje `State` del `Nav/MenuItem` — se modela como un **boolean `Expanded`** independiente, porque es ortogonal a la interacción (un ítem puede estar *expandido* y con *hover* a la vez; meterlo en `State` impide esa combinación y multiplica variants). Las modalidades son un componente distinto (`Nav/SubMenuItem` con boolean `Active`), que en código mapea a `role="menuitemradio"` + `aria-checked`, frente al `role="menuitem"` de las acciones. El revelado de las opciones es composición del menú, no estado del ítem: el item solo sabe hacia dónde apunta su chevron.

---

#### Lo que quedó pendiente

- **Variantes de estado** del top bar y del menú: Pausado (`Reanudar`) y Cancelado (`Reactivar` + estado en gris/rojo).
- **Modal de confirmación de "Cancelar cliente"** — acción destructiva sin paso de confirmación todavía.
- **Comportamiento de "Generar comparativa"** ante datos insuficientes (< 2 revisiones o sin foto frontal) — el menú lanza el flujo, pero los estados de error viven en el [spec del generador](../dashboard/generador-de-cambios.md).
- **¿Cuestionario / Notas como segmented toggle conectado** en vez de dos botones sueltos? — pendiente de decidir.
- **Hover states** de los ítems del menú.

---

## Materiales

- Figma — pantalla de revisión del dashboard: [Ficha cliente - revisiones-v3](https://www.figma.com/design/629ryw0MF7hzDxIFiZJ5Un/App-Automatica?node-id=4737-39579)
- Figma — top bar v4, acciones centralizadas (exploración): [Propuesta — Top bar v4](https://www.figma.com/design/629ryw0MF7hzDxIFiZJ5Un/App-Automatica?node-id=4817-118253)
- Figma (Dashboard - DS) — patrón con componentes reales: [Top bar — Menú Acciones (acordeón)](https://www.figma.com/design/E6H45ej75HO6fL2SOnQNL5/Dashboard---DS?node-id=142-14509)
- Figma (Dashboard - DS) — spec del componente: [Nav/MenuItem · Spec](https://www.figma.com/design/E6H45ej75HO6fL2SOnQNL5/Dashboard---DS?node-id=142-14315)
- Figma (Dashboard - DS) — comportamiento del patrón (interacción · teclado · a11y): [Menú Acciones — Comportamiento](https://www.figma.com/design/E6H45ej75HO6fL2SOnQNL5/Dashboard---DS?node-id=142-14914)
- Figma — card % GRASO, 4 estados: [propuesta en Rediseño - Junio](https://www.figma.com/design/629ryw0MF7hzDxIFiZJ5Un/App-Automatica?node-id=4769-19948)
- Figma — overlay comparador: [propuesta en Rediseño - Junio](https://www.figma.com/design/629ryw0MF7hzDxIFiZJ5Un/App-Automatica?node-id=4774-20036)
- Docs relacionados: `asesorias/`, `asesorias/calculo-%-graso/`, `casos-de-estudio/spec-evaluacion-ia-graso.md`
