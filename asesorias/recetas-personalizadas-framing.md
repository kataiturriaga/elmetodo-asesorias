# Recetas personalizadas por opción de dieta — Entendimiento del problema

> Estado: **framing** (solo definición del problema, sin soluciones). Destinado a crecer como caso de estudio de Asesorías V2.

---

## 01 — PROBLEM STATEMENT

### ¿Qué problema estamos resolviendo?

Queremos asociar **una receta a cada opción de cada comida** que ofrecemos al cliente, para que no solo reciba una lista de ingredientes sino una guía de cómo cocinar el plato.

El problema es que una receta, tal como se entiende hoy en el sistema, es un objeto con **valores predeterminados y absolutos**, desconectado de los ingredientes y las cantidades que el cliente tiene realmente en esa opción. Esto produce dos desajustes al mostrar la receta:

1. **Conjunto de ingredientes distinto** — la receta puede incluir ingredientes que la opción no tiene (ej.: la opción es "arroz con carne y verduras" y la receta asociada "paella de carne" añade marisco) y/u omitir alguno que sí tiene.
2. **Cantidades distintas** — la receta usa cantidades aproximadas/genéricas, no la porción personalizada del cliente (ej.: 200 g de carne picada, verdura "al gusto").

El objetivo es que la receta sea **lo más personalizada posible** respecto a lo que el cliente tiene en su opción, con **el menor cambio de código posible**.

---

## 02 — CÓMO ESTÁ MONTADO HOY (modelo de datos)

Verificado contra el API de producción (`api.apps.elmetodoapp.com`). La BD directa por puerto está bloqueada por firewall; los datos de abajo salen del API.

### Lado dieta v2 — lo que recibe el cliente

`Dieta → Comida (meal) → Opción (meal_option)`

Una opción puede existir en dos formas:

- **Texto libre (lo que hay HOY en prod):** el campo `ingredients` es un string, p. ej.:
  `"4 Rebanadas pan tostado\n6 Lonchas salmón, jamón serrano o lomo\nTomate triturado al gusto\n10ml Aove"` + fotos. `dish_id = null`.
- **Estructurada (existe en el API, 0% poblada):** tabla `OptionIngredient` con `ingredient_id` + `override_quantity_portion` / `override_measure_portion` + unidades + grupos de elección (sustituciones), y `dish_id` apuntando a un `Dish`.

**Dato medido:** las 60 dietas master son `schema_version 1`; sus **669 opciones son 100% texto libre** y **ninguna tiene `dish_id`** ni ingredientes estructurados. El catálogo de ingredientes sí está estructurado (**564 ingredientes**) y la capacidad de estructurar opciones ya existe (`POST /api/ingredients/options/{option_id}/ingredients`), pero no se usa todavía.

### Lado receta — dashboard

`Dish ⇄ Recetas` (muchos-a-muchos vía `recipe_ids`). Cada **Receta** tiene:

- Modos `ligero / normal / bestia`.
- `RecipeIngredient` **por modo**, con cantidades **absolutas** (ej.: `180g Tofu`, `3u Patata`, `2 cucharadas soja`, `Sal al_gusto`). Referencian `ingredient_id` del mismo catálogo de 564.
- Nutrición por modo + pasos (prosa).

### Vía de asociación opción ↔ receta (en el modelo actual)

`Opción → dish_id → Dish → recetas`. La UX del detalle de opción con "recetas asociadas" ya está diseñada en el caso de estudio Asesorías V2.

---

## 03 — REENCUADRE: la receta se construye desde los ingredientes de la dieta

> Corrección importante sobre el planteamiento inicial.

Las recetas que vamos a usar **no son las recetas genéricas que ya están en la BD**. Las recetas se **construyen con los `ingredient_id` de las dietas** — el mismo vocabulario de ingredientes que usa la opción.

Implicación: el match receta ↔ opción es **por construcción**, no hay que cruzarlo a posteriori ni inferirlo. La receta se arma sobre los ingredientes que esa opción ya tiene.

Implicación crítica: para que la receta se construya desde los `ingredient_id` de la opción, **la opción tiene que estar estructurada** (tener `ingredient_id`s). Hoy en prod está todo en texto libre. Este es el verdadero condicionante del problema.

---

## 04 — SUPOSICIONES Y RIESGOS

- **Prerrequisito de datos:** cualquier personalización por ingrediente exige opciones estructuradas. Hoy: 0/669. Riesgo de coste oculto (migración / re-autoría de dietas).
- **Pasos en prosa:** los pasos de la receta mencionan ingredientes y cantidades concretas ("añade los 180g de tofu"); no se auto-actualizan al cambiar la porción del cliente. Desajuste cosmético que persiste salvo plantillizar los pasos.
- **Unidades:** receta en g/ml vs. opción que el cliente puede ver en raciones/unidades. Posible conversión necesaria.
- **Modos** `ligero / normal / bestia`: la cantidad real la manda la opción; el modo solo afectaría a pasos/nutrición.
- **Grupos de elección** ("salmón, jamón serrano o lomo"): qué asume la receta cuando la opción ofrece varias alternativas.
- **Ingredientes "al gusto":** no tienen cantidad que personalizar.

---

## 05 — PREGUNTAS A RESOLVER (antes de pasar a soluciones)

1. ¿La receta se **autora a la vez** que se estructura la opción (mismo flujo en el dashboard) o se **genera automáticamente** a partir de los ingredientes ya estructurados de la opción?
2. ¿Estructuramos opciones **solo hacia delante** (nuevas dietas de asesorías) o hay **backfill** de las opciones de texto existentes?
3. ¿Qué hacemos con los **pasos en prosa** para que no contradigan la porción del cliente?
4. ¿Cómo se resuelven **grupos de elección** y unidades (raciones/unidades) en la receta personalizada?
5. _(Pendiente de tu frase cortada: "ya puede haber un man…")._

---

## Checklist de salida — ¿cuándo pasamos a soluciones?

- [ ] Confirmado el modelo de autoría de recetas (manual junto a opción vs. generación automática).
- [ ] Decidido el alcance de estructuración de opciones (forward-only vs. backfill).
- [ ] Acordado el tratamiento de pasos, unidades y grupos de elección.
