# Grupos y ranking de entreno — Spec Mayo 2026

## Contexto

El ranking actual solo tiene en cuenta los **pasos** para calcular la posición y mostrar el grupo. La propuesta es ampliar el sistema de puntuación para incluir los **entrenos** y estructurar los grupos de forma que la competición sea relevante y sostenida en el tiempo.

Esto también es el prerequisito para que la **pantalla de bloqueo post-cancelación** sea realmente efectiva: si el ranking incluye entrenos, el usuario cancelado puede ver en tiempo real cómo su posición cae mientras su grupo sigue entrenando.

---

## 1. Puntuación

### Estado actual

- Puntuación = pasos del día

### Propuesta

- Puntuación = **pasos + entrenos completados**
- Peso exacto de cada componente a definir con el equipo (sugerencia: pasos 40% / entrenos 60%, para incentivar el entrenamiento como comportamiento principal)

---

## 2. Estructura de grupos

### Opción propuesta: grupos de tamaño fijo con refresh semanal

Inspirado en el modelo de ligas de Duolingo.

**Funcionamiento:**

- Al registrarte en un programa, se te asigna automáticamente un grupo de **~20-30 personas** con nivel de actividad similar
- El ranking se resetea cada semana (lunes 00:00)
- Al final de cada semana: los X mejores del grupo **suben de liga**, los que están en la cola **bajan**
- 3 ligas propuestas: **Bronce → Plata → Oro**

**Por qué este modelo:**

- Siempre hay alguien justo por encima y por debajo → tensión competitiva constante
- El tamaño del grupo es controlado independientemente de cuántos usuarios haya en cada programa
- El reset semanal crea urgencia recurrente — no se puede acumular ventaja indefinidamente
- Subir de liga es un hito que refuerza la retención

---

## 3. Momento de unirse al grupo

**Al registrarte en un programa** — es el mejor momento porque:

- El usuario está en el punto de máxima motivación (acaba de comprometerse con un objetivo)
- Crea un sentido de "fresh start" junto con el programa
- Permite segmentar el grupo por programa para que la comparación sea relevante

### Flujo propuesto

1. Usuario elige programa
2. Pantalla: "Únete a un grupo" → se le asigna automáticamente un grupo activo con hueco
3. Ve los miembros del grupo y su posición inicial (#20 de 20, o similar)
4. A partir de ahí, el ranking de la home muestra su grupo y posición

---

## 4. Segmentación

**¿Un grupo por programa o varios segmentos?**

Segmentar por **género y edad**.

- Género: Hombre / Mujer
- Edad: franjas a definir (sugerencia: 18-29 / 30-39 / 40-49 / 50+)
- La comparación se siente justa y relevante — no es lo mismo competir con un hombre de 25 que con una mujer de 45
- Ejemplo de grupo: Mujeres - 30-39 años - Cuerpo definido Oro

---

## 5. Conexión con la pantalla de bloqueo (post-cancelación)

Cuando el usuario cancela la suscripción:

- **Conserva** acceso al ranking y cuentapasos
- **Pierde** que sus entrenos sumen puntos al ranking

Esto significa que su posición en el grupo cae activamente cada semana que no está suscrito. La pantalla de bloqueo puede mostrar este movimiento en tiempo real:

> *"Tu grupo lleva 9 sesiones esta semana. Tu posición ha bajado de #12 a #18."*

Este es el lever de re-engagement más potente porque es específico, personal, y empeora con el tiempo.

---

## Pendiente de definir

- Diseñar puntuacion de entreno
- Peso exacto de pasos vs. entrenos en la puntuación
- Número de ligas y tamaño de cada grupo
- Cuántos usuarios suben/bajan de liga cada semana (ej. top 5 suben, bottom 5 bajan)
- Qué pasa si el grupo se queda con pocos usuarios activos (merge de grupos)
- Si el grupo es por programa: ¿qué pasa cuando el usuario termina el programa y empieza otro?
- Diseño de las ligas (nombres, iconos, criterio visual)
- Notificación de fin de semana: "Quedan X horas — estás a Y puntos del siguiente puesto"

