# Plan técnico — CMS de Consejos (tab dieta)

**Feature:** Consejos — gestión de contenido desde el Dashboard, consumo en la app
**Contenido fuente:** [`asesorias/consejos-dieta-contenido.md`](../consejos-dieta-contenido.md)
**Pantallas app (Figma):** [Home Consejos](https://www.figma.com/design/629ryw0MF7hzDxIFiZJ5Un/App-Automatica?node-id=4450-155957) · [Lista de categoría](https://www.figma.com/design/629ryw0MF7hzDxIFiZJ5Un/App-Automatica?node-id=4480-40180) · [Detalle de artículo](https://www.figma.com/design/629ryw0MF7hzDxIFiZJ5Un/App-Automatica?node-id=4500-155458)
**Repos de implementación:** `elmetodo_api` (FastAPI) · `elmetodo_dashboard` (Next.js) · `elmetodo_ff_asesorias` (Flutter)
**Estado:** Borrador de plan — pendiente de validar
**Última actualización:** 2026-06-17

---

## 1. Qué construimos

Una sección de **Contenido → Consejos** en el dashboard que permite al equipo de El Método **crear, editar, ordenar y publicar** el contenido de la pantalla "Consejos" de la tab de dieta de la app. Hoy ese contenido no existe en BD: hay que **crear las tablas**, las **APIs** (dashboard de gestión + móvil de lectura) y la **UI del dashboard**.

El modelo es de **dos niveles**, idéntico al que la app ya muestra:

| Nivel | En la app | En el dashboard |
|---|---|---|
| **Categoría** | Tarjeta del grid "Aprende a comer mejor" (portada + título + nº de artículos) y hero de la pantalla de categoría | Entidad editable: nombre, portada, orden, estado |
| **Artículo** | Fila de la lista dentro de una categoría (thumbnail + título + "X min de lectura") y pantalla de detalle (hero + cuerpo) | Entidad editable: título, resumen, portada, cuerpo (Markdown), tiempo de lectura, destacado, orden, estado |

El **"Destacado de la semana"** (home) es un artículo con flag `is_featured`.

> **Decisión de alcance (confirmada):** contenido **global**, gestionado por el equipo de El Método (no por-coach). Las tablas **no llevan `coach_id`**; todas las asesorías ven la misma biblioteca. La sección del dashboard va bajo **Contenido**, junto a Recetas / Guías rápidas.

---

## 2. Patrón de referencia (lo copiamos casi 1:1)

Este feature es estructuralmente **el mismo que el CMS de Guías Rápidas** ya en producción (categoría → hijo), y comparte la mecánica de edición de Recetas. Reutilizamos el patrón entero en vez de inventar nada:

| Pieza | Referencia a copiar |
|---|---|
| Modelo categoría → hijo + enum de estado | `quick_guide_categories` / `quick_guide_videos` → [`migrations/versions/create_quick_guides.py`](../../../elmetodo_api/migrations/versions/create_quick_guides.py) |
| Migración (helper de enums por SQL crudo) | `create_recipes_cms.py` / `create_quick_guides.py` |
| Rutas dashboard CRUD + status + imagen | `app/api/routes/dashboard/recipe.py`, `guide_category.py`, `guide_video.py` |
| Servicio create_full / update_full + validate_for_publish | `app/services/recipe_service.py` |
| Endpoint móvil read-only (solo `published`) | `app/api/routes/mobile/recipes.py`, `mobile/guides.py` |
| Modelos / servicios / páginas del dashboard | `src/models/guide.ts`, `src/models/recipe.ts`, `src/services/recipe-services.ts`, `src/features/recipes/*`, `src/features/guides/*`, rutas en `(private)/(sidebar)/contenido/*` |

**Diferencia principal con recetas/guías:** el artículo tiene un **cuerpo de texto largo enriquecido** (negritas, bullets, listas numeradas, tablas). Lo guardamos como **Markdown en una columna `Text`** y lo editamos con un `Textarea` + preview (mismo stack que los pasos de receta, sin dependencia WYSIWYG nueva). La app lo renderiza con `flutter_markdown`. Ver §7.

---

## 3. Decisiones de arquitectura (cerradas)

| Decisión | Resolución | Motivo |
|---|---|---|
| **Alcance / propiedad** | **Global** (sin `coach_id`), editado por el equipo | Confirmado por producto. El contenido es genérico y único (un solo doc fuente). |
| **Modelo de datos** | 2 tablas: `advice_categories` → `advice_articles` | Calca `quick_guide_categories` → `quick_guide_videos`. |
| **Formato del cuerpo** | **Markdown** en columna `Text`, editado con `Textarea` + preview | "Mismo modelo que recetas": los pasos de receta ya se editan con `Textarea` plano. Sin nueva dependencia. La app renderiza Markdown. |
| **Destacado de la semana** | Flag `is_featured` en el artículo; el servicio garantiza **uno solo activo** | Más simple que una tabla de settings. El endpoint móvil devuelve ese artículo. |
| **Tiempo de lectura** | `reading_time_minutes`, autocalculado (~200 palabras/min, mínimo 1) y editable | Coincide con "X min de lectura" del Figma. Evita pedir el dato a mano. |
| **Imágenes** | S3 vía `ImageService.upload_image` (endpoint `/{id}/image`) | Patrón idéntico al de la portada de receta. Coincide con `[[reference_almacenamiento_fotos_review]]` (fotos en S3). |
| **Estados** | enum `advice_status` = `draft` / `published` / `archived` | Igual que `recipe_status` / `quick_guide_status`. La app solo lee `published`. |
| **Nomenclatura** | dominio `advice_*` (no `tip_*`) | Ya existe un placeholder "Tips y Posts" en `/contenido/tips` que es **otra cosa**; usamos `advice`/"Consejos" para no colisionar. |

---

## 4. Modelo de datos (BD nueva)

### 4.1 Enum

```sql
CREATE TYPE advice_status AS ENUM ('draft', 'published', 'archived');
```

### 4.2 Tabla `advice_categories`

| Columna | Tipo | Null | Notas |
|---|---|---|---|
| `id` | Integer PK | no | |
| `name` | String(255) | no | Ej. "Técnicas de cocinado" |
| `description` | String(500) | sí | Subtítulo opcional |
| `cover_image_url` | String(500) | sí | Portada de la tarjeta + hero de la categoría (S3) |
| `position` | Integer | no | Orden en el grid (default 0) |
| `status` | `advice_status` | no | default `draft` |
| `created_at` / `updated_at` | TIMESTAMPTZ | no | `func.now()` |

Índices: `ix_advice_categories_status`, `ix_advice_categories_position`.
**`article_count`** (nº de artículos publicados) es **derivado** — no se persiste; se calcula en la query (como `video_count` en guías). Los números del Figma (6/8/5/3) son placeholders.

### 4.3 Tabla `advice_articles`

| Columna | Tipo | Null | Notas |
|---|---|---|---|
| `id` | Integer PK | no | |
| `category_id` | Integer FK → `advice_categories.id` `ON DELETE CASCADE` | no | |
| `title` | String(255) | no | Ej. "Cómo preparar pollo jugoso sin perder proteína" |
| `summary` | String(500) | sí | Intro corta (para lista / SEO interno) |
| `hero_image_url` | String(500) | sí | Hero del detalle; si es `null`, la app cae a `cover_image_url` de la categoría |
| `body` | Text | no | **Markdown** (negritas, bullets, listas numeradas, tablas) |
| `reading_time_minutes` | Integer | sí | "X min de lectura"; autocalculado, editable |
| `is_featured` | Boolean | no | default `false` — "Destacado de la semana" |
| `position` | Integer | no | Orden dentro de la categoría (default 0) |
| `status` | `advice_status` | no | default `draft` |
| `created_at` / `updated_at` | TIMESTAMPTZ | no | |

Índices: `ix_advice_articles_category_id`, `ix_advice_articles_status`, `ix_advice_articles_is_featured`.

### 4.4 Migración Alembic

Nuevo archivo `migrations/versions/create_advice_cms.py`, `down_revision` = última cabeza actual. Copiar el patrón de `create_quick_guides.py`:
- helper `_create_enum_if_not_exists(conn, 'advice_status', ['draft','published','archived'])`,
- `ENUM(..., create_type=False)` para referenciar el tipo,
- `op.create_table(...)` para las dos tablas + índices,
- `downgrade()` que dropea tablas y `DROP TYPE IF EXISTS advice_status`.

---

## 5. Backend (`elmetodo_api`)

Archivos nuevos, calcando `guide_category` / `guide_video` / `recipe`:

| Archivo | Responsabilidad |
|---|---|
| `app/models/advice.py` | `AdviceCategory`, `AdviceArticle` (SQLAlchemy) + enum `advice_status_enum` |
| `app/schemas/advice.py` | Pydantic `Create` / `Update` / `Response` / `ListResponse` / `StatusUpdate` + `AdviceStatus` |
| `app/repositories/advice_category_repository.py` | CRUD + `get_all_with_count` (incluye `article_count`) + reorder |
| `app/repositories/advice_article_repository.py` | CRUD + filtro por `category_id`/`status`/`search` + reorder + `set_featured` (single) |
| `app/services/advice_service.py` | `compute_reading_time(body)`, `set_featured` (apaga los demás), `validate_for_publish` |
| `app/api/routes/dashboard/advice_category.py` | CRUD categorías (auth `get_current_coach`) |
| `app/api/routes/dashboard/advice_article.py` | CRUD artículos + status + feature + imagen |
| `app/api/routes/mobile/advice.py` | Lectura para la app (auth `get_current_user`, solo `published`) |
| `app/api/router.py` | Montar los 3 routers (ver prefijos abajo) |

**Reutilizar tal cual:** `ImageService` (subida a S3), dependencia `get_app_name`, patrón de paginación/filtros de `recipe.py`.

### 5.1 Endpoints — Dashboard (gestión)

Prefijos nuevos en `router.py` (junto a las líneas 119-123):

```
/api/dashboard/advice-categories   → dashboard_advice_category_router
/api/dashboard/advice-articles      → dashboard_advice_article_router
```

**Categorías** (`/dashboard/advice-categories`):

| Método | Ruta | Acción |
|---|---|---|
| GET | `/` | Listar (con `article_count`, filtros `search`/`status`, paginación) |
| POST | `/` | Crear |
| GET | `/{id}` | Detalle |
| PUT | `/{id}` | Editar |
| DELETE | `/{id}` | Borrar (cascada a artículos) |
| PATCH | `/{id}/status` | Cambiar estado (valida `validate_for_publish`) |
| POST | `/{id}/image` | Subir portada (S3) |
| PATCH | `/reorder` | Reordenar (lista de `{id, position}`) |

**Artículos** (`/dashboard/advice-articles`):

| Método | Ruta | Acción |
|---|---|---|
| GET | `/?category_id=&status=&search=` | Listar artículos de una categoría |
| POST | `/` | Crear (calcula `reading_time_minutes` si no viene) |
| GET | `/{id}` | Detalle (con `body`) |
| PUT | `/{id}` | Editar (recalcula tiempo de lectura) |
| DELETE | `/{id}` | Borrar |
| PATCH | `/{id}/status` | Cambiar estado |
| PATCH | `/{id}/feature` | Marcar destacado (apaga los demás) |
| POST | `/{id}/image` | Subir hero (S3) |
| PATCH | `/reorder` | Reordenar dentro de la categoría |

`validate_for_publish(article)`: exige `title`, `body` no vacío y `category` publicada.

### 5.2 Endpoints — Móvil (lectura, solo `published`)

Prefijo: `/api/mobile/advice` (junto a `mobile/recipes` y `mobile/guides`, líneas 143-145). Calca `mobile/recipes.py`: respuestas slim, filtra `status == 'published'`, `joinedload`.

| Método | Ruta | Pantalla Figma |
|---|---|---|
| GET | `/categories` | Home: grid de categorías con `article_count` + portada |
| GET | `/featured` | Home: "Destacado de la semana" (artículo `is_featured` publicado + tag de su categoría) |
| GET | `/categories/{id}` | Pantalla categoría: hero + lista de artículos (título, `reading_time_minutes`, thumbnail) |
| GET | `/articles/{id}` | Detalle: hero + `body` (Markdown) |

> Si la app de asesorías usa scoping por `X-Client-ID`, añadir `Depends(get_app_name)` como en el resto de rutas. Confirmar el `app_name` de asesorías antes de cerrar (`valid_app_names` hoy es `["elmetodo", "golds"]`).

---

## 6. Dashboard (`elmetodo_dashboard`)

Calca Recetas + Guías Rápidas (Next.js App Router, server-action services sobre el `client` OpenAPI tipado).

### 6.1 Rutas / navegación

| Ruta | Pantalla |
|---|---|
| `/contenido/consejos` | Lista de **categorías** (tabla: portada, nombre, nº artículos, estado, acciones) + botón "Nueva categoría" |
| `/contenido/consejos/[categoryId]` | Detalle de categoría: editar campos + **lista de artículos** (reordenable) + "Nuevo artículo" |
| `/contenido/consejos/[categoryId]/articulos/new` | Crear artículo |
| `/contenido/consejos/[categoryId]/articulos/[articleId]/edit` | Editar artículo |

- Añadir entradas a `src/constants/routes.ts` bajo `contenido` (`consejos`, `consejosCategoria(id)`, `consejosArticuloNew(id)`, `consejosArticuloEdit(catId, id)`).
- Añadir item "Consejos" al sidebar (`(private)/(sidebar)/layout.tsx`), junto a Recetas / Guías rápidas.
- **Nota:** existe `/contenido/tips` ("Tips y Posts — Próximamente"), feature distinta. Decidir si "Consejos" es entrada nueva (recomendado) o si reutiliza ese hueco.

### 6.2 Archivos (espejo de `guide.ts` + `recipe-services.ts` + `features/recipes/*`)

| Archivo | Responsabilidad |
|---|---|
| `src/models/advice.ts` | Enums + interfaces `AdviceCategory*` / `AdviceArticle*` (calca `guide.ts`) |
| `src/services/advice-services.ts` | Llamadas CRUD + status + feature + `uploadImage` (calca `recipe-services.ts`) |
| `src/features/advice/AdviceCategoriesPage.tsx` + `AdviceCategoriesTable.tsx` | Lista de categorías |
| `src/features/advice/AdviceCategoryForm.tsx` | Form de categoría (nombre, descripción, portada, estado) |
| `src/features/advice/AdviceArticlesList.tsx` | Lista reordenable de artículos de la categoría |
| `src/features/advice/AdviceArticleForm.tsx` | Form de artículo: título, resumen, hero, **editor de cuerpo Markdown**, tiempo de lectura (auto, override), toggle "Destacado", estado |
| `src/features/advice/MarkdownBodyEditor.tsx` | `Textarea` + tab de **preview** (render Markdown) + barra de atajos (negrita/lista/tabla) |
| Páginas `app/(private)/(sidebar)/contenido/consejos/...` | Wiring de las rutas de §6.1 |

**Editor de cuerpo:** seguimos el patrón de `RecipeStepsEditor` (shadcn `Textarea`). Para el preview de Markdown basta `react-markdown` (+ `remark-gfm` para tablas) si no hubiera ya un renderer; es la única dependencia candidata y es opcional para V1 (se puede shippear sin preview y añadirlo después).

---

## 7. App (`elmetodo_ff_asesorias`)

Solo **consume** los 4 endpoints móviles de §5.2 (read-only). Mapeo a pantallas:

1. **Home Consejos** → `GET /mobile/advice/categories` (grid) + `GET /mobile/advice/featured` (destacado).
2. **Lista de categoría** → `GET /mobile/advice/categories/{id}`.
3. **Detalle de artículo** → `GET /mobile/advice/articles/{id}`; render del `body` con **`flutter_markdown`** (soporta negritas, bullets, listas numeradas y tablas con la extensión GFM). Hero: `hero_image_url` con fallback a la portada de la categoría.

No hay cambios de esquema en la app; sí trabajo de UI/integración (fuera del alcance de este plan de backend+dashboard, pero listado para coordinar).

---

## 8. Mapeo del contenido fuente → datos (seed inicial)

[`consejos-dieta-contenido.md`](../consejos-dieta-contenido.md) se traduce a 4 categorías y sus artículos. Cada `###` del doc es un artículo; su párrafo intro va a `summary` y el resto a `body` (Markdown):

| Categoría (`name`) | Artículos (`title`) |
|---|---|
| **Técnicas de cocinado** | Cómo cocinar proteína sin que quede seca · Técnicas para verdura (que no te la saltes) · Meal prep en 1 hora |
| **Salsas y aderezos** | Salsas bajas en calorías que dan sabor · Especias que cambian todo |
| **Fuera de casa** | Cómo pedir en un restaurante sin romper la dieta · Opciones rápidas en supermercado · Qué llevar al trabajo |
| **Mentalidad** | Qué hacer cuando no tienes ganas · Cómo gestionar comidas sociales · Por qué no tienes que ser perfecta |

Recomendado: un **script de seed idempotente** (o data-migration) que cargue esto en `draft`, para revisar y publicar desde el dashboard. Las portadas/heros se suben después desde la UI.

---

## 9. Fases de implementación

**Fase 1 — BD + backend de gestión**
1. Migración `create_advice_cms.py` (enum + 2 tablas + índices).
2. Modelos, schemas, repositorios, servicio (`compute_reading_time`, `set_featured`, `validate_for_publish`).
3. Routers dashboard (categorías + artículos) con CRUD/status/feature/imagen. Tests de endpoint.

**Fase 2 — Dashboard UI**
4. `models/advice.ts` + `services/advice-services.ts`.
5. Lista de categorías + form de categoría + subida de portada.
6. Detalle de categoría con lista de artículos + form de artículo + editor Markdown. Nav + rutas.

**Fase 3 — API móvil + seed**
7. Endpoints `/mobile/advice/*` (solo `published`).
8. Script de seed desde el doc fuente (en `draft`).

**Fase 4 — App + publicación**
9. Integración Flutter de las 3 pantallas (equipo app).
10. Revisar contenido en dashboard, subir imágenes, marcar destacado y publicar.

---

## 10. Tests
- **Servicio (unit):** `compute_reading_time` (texto corto → 1 min; redondeo); `set_featured` apaga los demás; `validate_for_publish` (body vacío → error).
- **Dashboard endpoints (integración):** CRUD categoría/artículo; `article_count` correcto; cascada al borrar categoría; subida de imagen devuelve URL S3.
- **Móvil (integración):** solo devuelve `published`; `featured` devuelve el artículo flag-eado + tag de categoría; fallback de hero a portada de categoría.

---

## 11. Decisiones abiertas (a confirmar antes de cerrar)
1. **Editor de cuerpo:** ¿`Textarea` + preview Markdown (V1, sin dependencias nuevas salvo `react-markdown`) o invertir en un WYSIWYG? Recomendado: empezar con Markdown + preview.
2. **`app_name` de asesorías:** confirmar el valor de `X-Client-ID` para la app de asesorías y si las rutas móviles deben filtrar por él (`valid_app_names` hoy no incluye asesorías).
3. **Entrada de navegación:** ¿nueva "Consejos" en el sidebar o reutilizar el placeholder `/contenido/tips`? Recomendado: entrada nueva.
4. **Thumbnails de la lista (Figma screen 2):** en el diseño aparecen como placeholders grises. ¿La lista usa el `hero_image_url` del artículo como thumbnail o un campo aparte? Recomendado: reutilizar `hero_image_url` (sin columna extra).
```
