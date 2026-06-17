# Auditoría y plan de reorganización — Librería de componentes del Dashboard (Figma)

**Archivo:** `Dashboard - DS` · fileKey `E6H45ej75HO6fL2SOnQNL5`
**Fecha:** 2026-06-15
**Alcance:** Auditoría de solo lectura + propuesta. **No se modificó, movió, renombró ni borró nada en Figma.**

> **Nota de método / limitación:** la API REST de Figma respondió `401/403 — Token has expired`, por lo que las rutas REST (`figma_get_styles` REST, `figma_get_design_system_kit` componentes/styles) no estuvieron disponibles. Todo el inventario se obtuvo por el **Desktop Bridge (Plugin API)**, que devuelve datos completos en cualquier plan. Si quieres regenerar el kit completo vía REST, hay que renovar el `FIGMA_ACCESS_TOKEN`.

---

## 1. Resumen ejecutivo

La librería **no está vacía ni mal cimentada**: la capa de **tokens de color está bien diseñada** (primitivos → semánticos con alias, y modos Light/Dark). El problema real está en **dos frentes**:

1. **Estructura física**: todo vive en **una sola página** (`Page 1`) con **una única sección** (`Icons`). Los **47 componentes y component sets restantes flotan sueltos** sobre el canvas, sin agrupar.
2. **Naming y duplicación**: convenciones mezcladas (PascalCase, kebab-case, espacios), **typos** (`Buttom`), **duplicados por iteración** (`-2`, `-s2`, `-v3`) y **casi-duplicados por casing** (`Card-entreno` vs `Card-Entreno`, `Menu-item` vs `MenuItem`).

| Métrica | Valor |
|---|---|
| Páginas | 1 (`Page 1`) |
| Secciones | 1 (`Icons`) |
| Componentes sueltos (fuera de sección) | 47 |
| Componentes totales | 37 |
| Component sets | 24 |
| Iconos | 14 (`Icons/*`) |
| Variables / tokens | 76 en 4 colecciones |
| Modos | Light / Dark (solo en colección `Colors`) |
| Estilos de texto | 15 (`Open Sans`) |
| Hallazgos lint (design-system) | 9 colores hardcodeados · 71 nodos con nombre por defecto |

**Salud global estimada:** Tokens 🟢 buena base · Estructura 🔴 desordenada · Naming 🔴 inconsistente · Componentes 🟠 con duplicados.

---

## 2. Inventario

### 2.1 Tokens / Variables (76 vars · 4 colecciones)

| Colección | Modos | Vars | Contenido | Veredicto |
|---|---|---|---|---|
| **Primitives** | `Value` (1) | 27 | `neutral/*`, `green/*`, `red/*`, `chart/{blue,amber,pink,purple}/{light,dark}` + tintes `… light 100` | 🟠 base correcta, naming irregular |
| **Colors** | `Light`, `Dark` (2) | 34 | Semánticos: `text/*`, `bg/*`, `border/*`, `brand/*`, `state/*`, `sidebar/*`, `accents/*` — **todos por alias a Primitives** | 🟢 bien diseñada |
| **Spacing** | `Default` (1) | 10 | `1`=4 · `2`=8 · `3`=12 · `4`=16 · `5`=20 · `6`=24 · `8`=32 · `10`=40 · `12`=48 · `16`=64 | 🟠 nombre ≠ px, escala con huecos |
| **Radius** | `Default` (1) | 5 | `sm`=4 · `md`=8 · `lg`=12 · `xl`=16 · `full`=9999 | 🟢 correcta |

**Primitivos de color (valores):**
`neutral/0 #ffffff · 50 #fbfbfb · 100 #f9f9f8 · 200 #dbdae0 · 300 #8f8f97 · 500 #61656c · 600 #3c3e41 · 800 #1d1f23 · 900 #15171c · 950 #0b0f14`
`green/50 #f0fdf4 · 200 #88d98e · 500 #1bb11b · 600 #11dc11` ·  `red/500 #ef4444 · 900 #7f1d1d`
`chart/{blue,amber,pink,purple}/{light,dark}` + 3 tintes `… light 100`.

**Semánticos (Colors) — todos resuelven por alias** (ejemplos):
`text/primary` → neutral/950 (L) / neutral/50 (D) · `bg/card` → neutral/0 (L) / neutral/900 (D) · `brand/primary` → green/500 (L) / green/600 (D) · `state/destructive` → red/500 (L) / red/900 (D).

### 2.2 Estilos de texto (15 · `Open Sans`)

`heading/h1` (36/ExtraBold) · `h2` (30/Bold) · `h3` (24/SemiBold) · `h4` (20/SemiBold) · `body/lg` · `body/lg-bold` · `body/md` · `body/md-semibold` · `body/md-bold` · `body/sm` · `body/sm-bold` · `label/md` (14) · `label/sm` (12) · `label/xs` (12) · `caption` (11).

Nomenclatura con slash, coherente. **Sin colección de variables tipográficas** (viven como text styles — aceptable en Figma).

### 2.3 Componentes (37 componentes + 24 sets = 61)

**Iconos (14, dentro de la sección `Icons`)** — `Icons/Cuestionario, Notas, Drag, add, remove, training, Weight, calendar, Cancelar, Pausar, CambiarMod, GenerarComparativa, Arrow-down, Check`. Tamaños mezclados (12/16/20 px), cada icono es un componente independiente (no hay un set `Icon` con variante de glifo).

**Component sets (24):** Menu-item (2) · Tab (4) · Chip (2) · Dropdown (2) · EditableDataContainer (2) · Button-2 (2) · **Buttom (14)** · Badge (8) · Radio (2) · Configuracion-dieta (3) · Configuracion-entreno (3) · RevisionSelector (2) · CardEjercicio (3) · CardEjercicio-s2 (3) · CardHyrox (12) · CardEjercicio-superserie (2) · StepChart7dias (4) · CardProgresoFichaCliente (2) · Card revisión (5) · RendimientoDot (3) · ChipGroupRevisiones (3) · Card%Graso (4) · MenuItem (4) · Sub-MenuItem (4).

**Componentes sueltos (no-set, 23):** sidebar-section · Sidebar · Main-logo · CardNota · TabGroup-S · TabGroup-M · ChipGroup · header modo revision · Card-notas · Fotos revision · Card-dieta · Card-entreno · Tabs-secondary · Card-Entreno · ModalEdicionRutina · Buscador ejercicios · EjercicioBibliotecaEjercicios · TextInput · TablaMejoresMarcas · MejoresMarcasEntrenoCard · RevisionSelector-v3 · «Overlay A — Foco + tira de miniaturas» · «Acciones — menú (abierto)».

---

## 3. Diagnóstico — problemas priorizados

| # | Prio | Problema | Por qué importa | Ejemplo concreto |
|---|---|---|---|---|
| 1 | **P0** | **47 componentes flotando sin sección.** Solo existe la sección `Icons`. | Imposible navegar/onboarding; los consumidores no saben qué es canónico; se duplican porque no se ven. | Toda `Page 1` salvo `Icons`. |
| 2 | **P0** | **Duplicados funcionales de componentes base.** | Quien consume no sabe cuál usar; el DS pierde la "fuente única de verdad". | Botón: `Buttom` (14 var, typo) **+** `Button-2` (2 var). Menú: `Menu-item` (2) **+** `MenuItem` (4) **+** `Sub-MenuItem`. Tabs: `Tab` set + `Tabs-secondary` + `TabGroup-S` + `TabGroup-M`. |
| 3 | **P1** | **Versiones-iteración dejadas en la librería** (`-2`, `-s2`, `-v3`). | Ruido; riesgo de instanciar la versión vieja. | `Button-2`, `CardEjercicio` vs `CardEjercicio-s2`, `RevisionSelector` vs `RevisionSelector-v3`. |
| 4 | **P1** | **Casi-duplicados por casing.** | Confusión y divergencia silenciosa entre dos componentes "iguales". | `Card-entreno` vs `Card-Entreno` (solo cambia mayúscula). |
| 5 | **P1** | **Typo en componente base.** | `Buttom` (≠ Button) es el botón principal con 14 variantes; afecta búsquedas y credibilidad del DS. | Set `Buttom`. |
| 6 | **P1** | **Naming sin convención única.** PascalCase, kebab-case, espacios y slash conviven. | No se puede agrupar por categoría ni buscar de forma fiable. | `CardEjercicio` · `Card-dieta` · `Card revisión` · `header modo revision` · `Acciones — menú (abierto)`. |
| 7 | **P2** | **Componentes "de feature" mezclados con primitivos del DS.** | Cards muy específicas (one-off de pantalla) inflan la librería como si fueran sistema. | `Card%Graso`, `CardHyrox`, `MejoresMarcasEntrenoCard`, `ModalEdicionRutina`, `Buscador ejercicios`. |
| 8 | **P2** | **Naming irregular en primitivos de color.** Tintes con **espacio** y sufijo `100`; escala numérica con huecos; añadidos al final fuera de grupo. | Rompe el orden alfabético/numérico y la generación de tokens a código. | `chart/amber/light 100` (espacio) · `green/200`, `green/600`, `neutral/100` añadidos al final. |
| 9 | **P2** | **`green/600` (#11dc11) es más claro/saturado que `green/500` (#1bb11b).** | Escala invertida: rompe la convención "número mayor = más oscuro" y confunde al elegir. | `green/500` vs `green/600`. |
| 10 | **P2** | **`Spacing` nombrado por índice, no por px, con huecos** (falta 7, 9, 11, 13–15). | `2` = 8px no es intuitivo; los huecos invitan a valores ad-hoc. | colección `Spacing`. |
| 11 | **P2** | **Estilos de texto duplicados.** `label/sm` y `label/xs` son idénticos (12px SemiBold). | Dos estilos para lo mismo → drift. | `label/sm` ≡ `label/xs`. |
| 12 | **P3** | **9 colores hardcodeados** (sin variable/estilo). | Pequeñas fugas de tokens; sobre todo en logo e inner-shadows. | `Main-logo` `#000000`; varios `inner-shadow` `#FFFFFF`. |
| 13 | **P3** | **71 nodos con nombre por defecto** (`Frame 2`, `Vector`, `Line 93`). | Higiene interna; afecta la lectura/handoff de capas. | dentro de Sidebar, Badge, TabGroup, etc. |
| 14 | **P3** | **Todas las variables con `ALL_SCOPES`.** | Sin scoping, Figma ofrece spacing donde debería ir color, etc. Peor experiencia al aplicar tokens. | las 76 variables. |
| 15 | **P3** | **Redundancia de alias semánticos.** Varios semánticos colapsan al mismo primitivo. | No es un bug, pero conviene revisar si `accents/1` aporta sobre `brand/primary`. | `brand/primary` = `border/ring` = `sidebar/ring` = `sidebar/primary` = `accents/1` = green/500. |

---

## 4. Propuesta de arquitectura de tokens

La base ya sigue el patrón correcto (primitivos → semánticos con alias + modos). Se trata de **consolidar y limpiar**, no de rehacer.

### 4.1 Capas recomendadas

```
1) Primitives  (sin modo, "Value")     → la paleta cruda. NUNCA se usa directo en componentes.
2) Semantic    (modos: Light / Dark)   → intención de uso. Es lo que consumen los componentes.
3) Component   (opcional, por modo)    → tokens específicos si un componente lo necesita (button/bg, etc.)
```

- **Primitives** — corregir naming a escala consistente y completa:
  - `neutral/{0,50,100,200,300,400,500,600,700,800,900,950}` (rellenar huecos o documentar por qué faltan).
  - `green/{50,100,200,300,400,500,600,700}` y **arreglar la inversión**: el valor más oscuro debe tener el número mayor. Hoy `green/600` (#11dc11) es más claro que `green/500` (#1bb11b).
  - Tintes de chart: renombrar `chart/amber/light 100` → `chart/amber/100` (sin espacios; el "light/dark" ya es el modo o un sufijo coherente). Idealmente convertir los pares `…/light` + `…/dark` en **modos** de la propia variable de chart, en vez de codificarlos en el nombre.
- **Semantic (Colors)** — mantener tal cual (está bien). Acciones menores:
  - Revisar `accents/1` (= brand/primary): si no aporta semántica distinta, deprecar.
  - Renombrar la colección `Colors` → `Semantic` (o `Theme`) para que la capa quede explícita.
- **Spacing** — migrar de índice a px o a paso explícito: `space/4, space/8, space/12, …` (o `space/1=4` documentado). Rellenar o eliminar huecos. Añadir `0` y `2` (2px) si se usan.
- **Radius** — correcto. Solo añadir `none`=0 si aplica.
- **Scopes** — asignar scope a cada variable: Spacing → `GAP`, `WIDTH_HEIGHT`, paddings; Radius → `CORNER_RADIUS`; colores de texto → `TEXT_FILL`; fondos → `FRAME_FILL`, etc. Mejora la UX de aplicación y evita errores.
- **Tipografía** — mantener como text styles; **fusionar `label/sm` y `label/xs`** (son idénticos) dejando uno.

### 4.2 Valores hoy hardcodeados que deberían ser variable

- Negro del logo `#000000` y los `#FFFFFF` de inner-shadow → enlazar a `neutral/950` / `neutral/0` o a un token de sombra dedicado.
- Auditar, una vez ordenado, con `figma_lint_design rules:["design-system"]` hasta dejar `hardcoded-color` en 0 (excluyendo logo si es intencional).

---

## 5. Propuesta de estructura de la librería

### 5.1 Páginas (separar sistema de features)

| Página | Contenido |
|---|---|
| `🎨 Foundations` | Muestra de tokens: color (light/dark), tipografía, spacing, radius. Documentación visual. |
| `🧩 Components` | Componentes **de sistema** reutilizables, en secciones por categoría (ver 5.3). |
| `🧱 Patterns` | Composiciones reutilizables (TabGroup, ChipGroup, Sidebar, cabeceras). |
| `📦 Feature / App-specific` | Cards y módulos one-off de pantalla (Card%Graso, CardHyrox, ModalEdicionRutina, Buscador ejercicios…). Aislados del núcleo del DS. |
| `🗄️ Archive` | Versiones viejas antes de borrar (`-2`, `-s2`, `-v3`). Zona de cuarentena no publicada. |

### 5.2 Convención de nombres (única)

- **`Categoria/Componente/Subparte`** con slash, en **PascalCase** por segmento. Sin espacios, sin guiones, sin acentos, sin sufijos de versión.
- Variantes → **propiedades del set** (no en el nombre): `Type`, `Size`, `State`, etc.
- Ejemplos de migración:
  - `Buttom` + `Button-2` → **`Button`** (un set; props `Type`, `Size`, `State`).
  - `Menu-item` + `MenuItem` + `Sub-MenuItem` → **`Navigation/MenuItem`** (prop `Level: Item|Sub`).
  - `Card-entreno` / `Card-Entreno` → **`Card/Entreno`** (un solo componente).
  - `Card revisión` → `Card/Revision` · `header modo revision` → `Pattern/HeaderRevision`.

### 5.3 Taxonomía (átomos → moléculas → organismos)

| Nivel | Sección | Candidatos actuales |
|---|---|---|
| **Atoms** | `Atoms` | Button, Badge, Chip, Radio, TextInput, Icons/*, RendimientoDot |
| **Molecules** | `Molecules` | Tab, TabGroup, ChipGroup, Dropdown, Menu/Sub-Menu, EditableDataContainer, RevisionSelector |
| **Organisms** | `Organisms` | Sidebar, Cards (Nota, Dieta, Entreno…), TablaMejoresMarcas, StepChart7dias, Buscador |
| **Templates/Feature** | página `Feature` | ModalEdicionRutina, CardHyrox, Card%Graso, Overlay/Acciones |

> Cada componente **dentro de una Section nombrada** (regla del MCP: nunca flotando). Component sets organizados en grilla con cabeceras (`figma_arrange_component_set`).

---

## 6. Componentes — acciones concretas

| Acción | Componentes | Resultado |
|---|---|---|
| **Consolidar botón** | `Buttom` (14) + `Button-2` (2) | 1 set `Button` con props limpias; corregir typo. |
| **Consolidar menú** | `Menu-item`, `MenuItem`, `Sub-MenuItem` | 1 set `Navigation/MenuItem` (prop `Level`). |
| **Consolidar tabs** | `Tab`, `Tabs-secondary`, `TabGroup-S`, `TabGroup-M` | `Tab` (átomo) + `TabGroup` (molécula con prop `Size`). |
| **Unificar versiones** | `CardEjercicio` vs `-s2`; `RevisionSelector` vs `-v3` | Elegir canónica, archivar la otra. |
| **Resolver casing** | `Card-entreno` vs `Card-Entreno` | Fusionar en `Card/Entreno`. |
| **Mover a Feature** | `Card%Graso`, `CardHyrox`, `ModalEdicionRutina`, `Buscador ejercicios`, `MejoresMarcasEntrenoCard`, `Overlay A…`, `Acciones — menú…` | Salen del núcleo del DS. |
| **Iconos como set** | `Icons/*` (14) | Evaluar set `Icon` con prop `Glyph` + tamaños estándar (16/20/24). |
| **Documentar** | Button, Badge, Tab, Card, Sidebar | `description` + doc por componente (`figma_generate_component_doc`). |

---

## 7. Plan de migración por fases (de menor a mayor riesgo)

> Regla: empezar por lo **no destructivo** (renombrar/mover/agrupar/documentar) y dejar los **borrados** para el final, tras una zona de archivo.

**Fase 0 — Preparación (no destructiva)**
1. Crear una **versión/snapshot** del archivo (history) como punto de retorno.
2. Renovar el `FIGMA_ACCESS_TOKEN` para reactivar las rutas REST.
3. Crear páginas vacías: `Foundations`, `Components`, `Patterns`, `Feature`, `Archive`.

**Fase 1 — Estructura física (bajo riesgo, no rompe instancias)**
4. Crear las **Sections** por categoría dentro de `Components`/`Patterns`.
5. **Mover** los 47 componentes sueltos a su sección/página (mover no rompe instancias).
6. Mover los componentes de feature a `Feature`.

**Fase 2 — Tokens (bajo riesgo, reversible)**
7. Arreglar naming de primitivos (`chart/… 100` → sin espacio; rellenar escala; corregir inversión `green/500↔600`).
8. Renombrar colección `Colors` → `Semantic`; revisar `accents/1` redundante.
9. Migrar `Spacing` a nombres por px/paso explícito.
10. Asignar **scopes** a las 76 variables.
11. Fusionar text styles duplicados (`label/sm` ≡ `label/xs`).

**Fase 3 — Naming de componentes (riesgo medio: rompe búsquedas, no instancias)**
12. Renombrar a `Categoria/Componente` PascalCase. Renombrar **no** rompe instancias, pero sí libraries publicadas → comunicar.
13. Corregir typo `Buttom` → dentro de la consolidación de Button.
14. Limpiar nombres por defecto (`Frame 2`, `Vector`) en los componentes nucleares.

**Fase 4 — Consolidación de duplicados (riesgo alto: afecta instancias)**
15. Para cada par duplicado: elegir canónico, **reapuntar instancias** al canónico, mover el viejo a `Archive`.
16. Unir variantes sueltas en component sets (Button, MenuItem, Tab/TabGroup).
17. Enlazar los 9 colores hardcodeados a variables.

**Fase 5 — Documentación y verificación**
18. Añadir `description` y docs a los componentes núcleo.
19. Re-correr `figma_lint_design` y `figma_audit_design_system`; objetivo: `hardcoded-color` ≈ 0, default-names limpios en el núcleo.
20. Tras 1–2 sprints sin uso, **borrar** lo de `Archive`.

---

## 8. Próximo paso

Este documento es **solo auditoría + plan**. No ejecutaré ningún cambio en Figma hasta que apruebes el plan. Cuando quieras, podemos:
- Empezar por la **Fase 1** (mover y agrupar — cero riesgo sobre instancias), o
- Atacar primero los **tokens (Fase 2)**, o
- Que detalle a nivel variante la propuesta de `Button`/`MenuItem`/`Tab` antes de tocar nada.
