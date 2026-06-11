# Pantalla Dieta — Spec UX

**Estado:** Tab Diario documentado — Tab Semanal pendiente de diseño  
**Fecha inicio:** 2026-05-25  
**Próximo paso:** Diseñar Tab Semanal (lista de la compra + resumen semana)

---

## Contexto

Pantalla principal de alimentación del usuario. Acceso desde el bottom nav (ítem "Dieta"). El objetivo es que en menos de 1 minuto el usuario sepa qué tiene que comer hoy o qué tiene que comprar esta semana. La pantalla debe ser funcional y directa — no es un destino de exploración.

---

## Navegación y estructura

**Ubicación:** Bottom nav → "Dieta"  
**Patrón de tabs superior:** Diario | Semanal  

El tab superior actúa como selector de modo de vista (similar al toggle Diario/Semanal de Home), no como navegación entre secciones distintas. Los dos tabs son vistas complementarias del mismo contexto: la dieta del usuario.

| Tab | Propósito | Estado |
|-----|-----------|--------|
| Diario | Qué como hoy | Diseñado |
| Semanal | Qué tengo que comprar esta semana + resumen del plan | Pendiente |

---

## Tab Diario

### Objetivo

El usuario abre la app y en un vistazo sabe qué come en la próxima comida. No requiere navegación adicional salvo que quiera ver detalle o recetas.

### Estructura de la pantalla

```
[Tu dieta]  [Semanal]          ← Tab superior

📅 Martes, 29 abril            ← Fecha con navegación (← →)

[Desayuno] Media mañana Comida Merienda Cena   ← Tabs de comida (scroll horizontal)

─────────────────────────────
  [Imagen]            Opción 1
  Nombre del plato
  X recetas asociadas
  [Ingredientes ↑]  [Ver recetas y detalle]
─────────────────────────────
  [Imagen]            Opción 2
  ...
─────────────────────────────
  [Imagen]            Opción 3
  ...
─────────────────────────────
```

### Componentes

**Header de fecha**
- Muestra el día y fecha actual
- Permite navegar al día anterior/siguiente (flechas o swipe)
- Icono de calendario para saltar a una fecha específica

**Tabs de comida (scroll horizontal)**
- Comidas del día: Desayuno, Media mañana, Comida, Merienda, Cena
- Tab activo: resaltado en verde (pill style)
- Scroll horizontal si no caben todas en pantalla

**Card de opción (estado colapsado — estado por defecto)**
- Imagen de la comida a ancho completo, altura fija (~180px)
- Badge "Opción 1 / 2 / 3" en esquina superior derecha
- Nombre del plato (título grande)
- Subtítulo: "X recetas asociadas"
- Dos CTAs secundarios:
  - `Ingredientes ↑` — expande la lista de ingredientes inline
  - `Ver recetas y detalle` — navega a la pantalla de detalle

**Card de opción (estado expandido — ingredientes visibles)**
- Misma estructura que colapsado
- Debajo del header de la card aparece la lista de ingredientes en texto plano:
  `cantidad  Nombre ingrediente`
- El botón cambia a `Ingredientes ↓` para colapsar
- Solo una opción puede estar expandida a la vez (colapsa la anterior al abrir una nueva)

---

## Estado 1 — Vista por defecto (sin ingredientes)

Todas las opciones colapsadas. El usuario ve un scroll de cards con imagen, nombre y los dos CTAs. Lectura rápida del plan del día.

**Comportamiento:**
- Al cargar, se posiciona en la comida más próxima en el tiempo según la hora actual
- Si ya pasó la hora de una comida, aparece ligeramente atenuada (no bloqueada)

---

## Estado 2 — Ingredientes expandidos

El usuario toca `Ingredientes ↑` en una card. La lista de ingredientes aparece inline bajo la imagen, con formato:

```
4       Torta de arroz
2 lonchas  Jamón serrano
80 gr   Huevo(s)
```

Útil para el momento de la compra o para preparar la comida. No requiere salir de la pantalla.

**Comportamiento:**
- Accordion: abrir uno cierra el anterior
- El botón cambia de flecha ↑ a ↓
- La card se expande verticalmente, el resto del scroll se desplaza hacia abajo

---

## Estado 3 — Pantalla de detalle de opción

Al tocar `Ver recetas y detalle`, se navega a una pantalla de detalle a pantalla completa.

**Header:**
- Botón atrás (←)
- Título: nombre de la comida del día (ej. "Desayuno")
- Tabs numerados: 1 / 2 / 3 — para cambiar entre las opciones sin volver atrás

**Contenido:**
- Imagen grande a ancho completo
- Toggle Raciones | Unidades — cambia el formato de cantidades de los ingredientes
- Nombre del plato
- Lista de ingredientes con cantidades (en el modo seleccionado)
- CTA secundario: `¿Quieres sustituir algún ingrediente? → Ver equivalencias`
- Sección: `Recetas para esta opción` — carrusel horizontal de tarjetas de receta con imagen, etiqueta de comida y tiempo de preparación

**Navegación entre opciones:**
- Los tabs numerados (1, 2, 3) arriba permiten cambiar de opción sin volver a la lista
- La opción activa tiene el indicador verde debajo del número

---

## Tab Semanal

**Estado:** Por definir

**Intención:** Vista de la semana completa + lista de la compra generada automáticamente a partir del plan. Permite al usuario prepararse con antelación y hacer la compra una sola vez.

Contenido previsto:
- Resumen de comidas de los 7 días
- Lista de ingredientes consolidada (todos los platos de la semana, agrupados y con cantidades sumadas)
- Opción de exportar / compartir la lista

---

## Decisiones de diseño cerradas

| Decisión | Respuesta | Motivo |
|----------|-----------|--------|
| ¿Tab superior o navegación por separado? | Tab superior Diario/Semanal | Son dos vistas del mismo contexto, no secciones distintas |
| ¿Dónde va "Consejos"? | Fuera de esta pantalla | Distinto tipo de contenido; mezclar con funcionalidad de dieta confunde el objetivo de la pantalla |
| ¿Dónde va la lista de la compra? | Tab Semanal | La compra es una vista de la dieta semanal, no una herramienta independiente |
| ¿Cuántas opciones por comida? | 3 opciones (Opción 1, 2, 3) | Flexibilidad sin abrumar |
| ¿Accordion o expandir todas? | Accordion (una a la vez) | Reduce ruido visual; el objetivo es consulta rápida |
| ¿Qué comida se muestra al entrar? | La más próxima según hora actual | Reduce fricción — el usuario no tiene que navegar para encontrar lo relevante |

---

## Preguntas pendientes

- **¿El usuario puede marcar una opción como "elegida"?** — ¿Hay un estado de selección por comida o solo consulta?
- **¿Qué pasa si el plan no está asignado para ese día?** — Estado vacío a definir.
- **¿La navegación entre días tiene límite?** — ¿Puede ver días futuros ilimitados o solo la semana en curso?
- **Tab Semanal:** formato del resumen semanal y formato de la lista de la compra.

---

## UX Context

**Usuario objetivo:** Cliente del plan — en el contexto de la cocina o el supermercado, con poco tiempo.  
**Contexto de uso:** Móvil, rápido, modo consulta. No es un momento de exploración.  
**Insight central:** La pantalla de dieta compite con abrir el WhatsApp del coach para preguntar "¿qué como hoy?". Si no da la respuesta en 10 segundos, ha fallado.
