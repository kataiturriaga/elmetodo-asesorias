# Contexto de trabajo — Asesorías V2

> Actualizar al final de cada sesión. Es el punto de partida para la siguiente.

---

## Qué es este proyecto

**Asesorías V2** — tier de coaching personalizado sobre la app Automática. El coach vende el servicio a través de la plataforma. Entregable: diseño Figma completo + handoff a Carles antes del **30 mayo 2026**.

Archivo Figma activo: `App Automatica` — file key `629ryw0MF7hzDxIFiZJ5Un`

---

## Estado actual (mayo 2026)

### En curso: flujo cuestionario onboarding V2
15 pantallas en total. Estructura de secciones:
- **B** — Datos básicos
- **C** — Dieta
- **D** — Entreno
- Cada sección tiene una pantalla intro (C0, D0…) y luego las preguntas

#### Lo que está hecho en Figma
| Frame | Node ID | Estado |
|-------|---------|--------|
| C0 — Intro: Dieta [v2 stats] | `4426:13834` | ✅ Diseñado con bolt + glow |
| D0 — Intro: Entreno [v2 stats] | `4424:12060` | ✅ Diseñado |
| Exploración figuras (8 shapes flat) | `4426:12960` (Section 2) | ✅ Creado |

#### Decisiones de diseño tomadas
- Las pantallas intro tienen **stats con count-up** (no ilustración) + elemento gráfico central
- Elemento central elegido: **rayo (bolt)** — mismo shape que anim-figuras card 5
- El bolt convive con un **glow radial** de fondo (no anillos con stroke)
- Botones con `border-radius: 8px` (no pill)
- Stats cards sin divider separándolas de los botones

---

## Prototipos HTML animados

Todos en `asesorias/animaciones/`:

| Archivo | Qué es |
|---------|--------|
| `anim-intro-dieta.html` | Intro dieta — versión con anillos + dot (original) |
| `anim-intro-dieta-bolt.html` | **Versión activa** — bolt + glow + stroke giratoria con degradado |
| `anim-intro-entreno.html` | Intro entreno — versión con anillos + dot |
| `anim-figuras.html` | 8 shapes animados (exploración) |
| `procesando-composicion*.html` | Animación pantalla de carga |

### Detalles técnicos del bolt (`anim-intro-dieta-bolt.html`)
- Bolt: SVG 180×180, viewBox 160×160, points `88,18 52,88 74,88 65,148 108,78 86,78`
- Animación: `bolt-enter` (spring in 550ms delay 420ms) + `bolt-pulse` (parpadeo cada 2.8s)
- Stroke giratoria: `conic-gradient(#00ee00 → #666666 → #00ee00)`, 230×230px, 5s linear
- Glow: 210×210, radial verde, sin anillos
- Fondo: `#0b0f14`
- Count-up stats: 100%/0 restricciones/3x

---

## Pendiente
- [ ] Replicar el bolt + stroke giratoria en `anim-intro-entreno.html`
- [ ] Decidir si el mismo tratamiento visual (bolt) aplica a todas las pantallas intro o si cada sección tiene su propio icono
- [ ] Continuar diseñando pantallas del cuestionario (más allá de los intros)
- [ ] Handoff a Carles — fecha límite 30 mayo

---

## Archivos de referencia
- `asesorias/01-product/00_coached_app_overview.md` — overview completo del producto
- `asesorias/fase2-arquitectura-informacion.md` — arquitectura de información
- `asesorias/pantalla-revision-ux.md` — UX de pantalla de revisión
