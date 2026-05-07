# Nuevo onboarding Automática — Mayo 2026

## Contexto

Rediseño completo del flujo de onboarding/embudo de conversión de la app Automática (tier suscripción). El flujo anterior (v1) tenía 22 pantallas con problemas críticos: contador de pasos inconsistente, imágenes AI-generated, banner amarillo fuera del DS, y pantallas con 60%+ de espacio vacío.

El objetivo del nuevo flujo es doble:
1. **Convertir** — llevar al usuario desde que abre la app hasta que paga
2. **Activar** — una vez pagado, hacer que el usuario entienda el Método y configure la app

**Archivo Figma:** `App Automatica` → página `auto-onboarding-exploracion` → `Section 2`

---

## Flujo completo aprobado

| # | Pantalla | Figma ID | Estado |
|---|----------|----------|--------|
| 1 | Hero — "Llega a resultados reales. Sin obsesiones" | `4016:79595` | ✅ Diseñado |
| 2–7 | Cuestionario (6 preguntas) | `4020:79720` + otros | ✅ Diseñado |
| 8 | Tu programa recomendado | `4038:369` | ✅ Diseñado |
| 9 | Metodología — "El Método no es solo entrenar" | `4108:31985` | ✅ Diseñado |
| 10 | Health permissions — "Activa tu cuentapasos" | `4110:31990` | ✅ Diseñado |
| 11 | Pricing — 7 días de prueba gratis + 3 tiers | `4096:32487` | ✅ Diseñado |
| 12 | Registration — "No pierdas tu progreso" | `4108:31922` | ✅ Diseñado |

**Total: 12 pantallas** (vs. 22 del v1)

---

## Cuestionario — 6 preguntas

Las preguntas están pensadas para dos objetivos simultáneos: personalizar el programa recomendado y crear inversión progresiva (efecto IKEA) antes del precio.

| Paso | Pregunta | Opciones |
|------|----------|----------|
| 1 | ¿Cuál es tu objetivo? | Perder grasa / Ganar músculo / Tonificar el cuerpo / Construir fuerza / Estar saludable / Aumentar la resistencia |
| 2 | Género | Hombre / Mujer |
| 3 | Tipo de entreno | Físico / Carrera / Híbrido / Hyrox |
| 4 | ¿Dónde sueles entrenar? | Gimnasio / Casa con material / Casa |
| 5 | ¿Cuál es tu nivel? | Principiante / Avanzado |
| 6 | ¿Cuántos días a la semana? | 2 / 3 / 4 / 5 |

Las respuestas determinan el programa que aparece en la pantalla 8 ("Tu programa recomendado").

---

## Decisiones de diseño clave

### Orden de las pantallas 9-11

**Decisión:** Metodología → Health permissions → Pricing (en ese orden).

**Por qué:** La pantalla de health permissions pide al usuario conectar Apple/Google Health **antes de pagar**. Esto hace que el cuentapasos esté activo cuando llega al precio. El usuario no está pagando por una promesa — el cuentapasos ya está funcionando en su teléfono.

Es el mismo principio que usa Duolingo: hacer que el usuario complete una acción real antes del paywall aumenta significativamente la conversión.

Técnicamente viable: los permisos de Health ya se piden sin registro en el flujo actual de producción.

---

### Pantalla de Metodología (Frame 555)

**Concepto:** "El Método no es solo entrenar" — una pantalla que explica los 3 pilares antes del precio para que este parezca justificado.

**Estructura:**
- Badge: "⚡ Más recomendado"
- Headline: "EL MÉTODO NO ES SOLO ENTRENAR"
- Subtítulo: filosofía general
- 3 cards con icono + título + descripción:
  - 💪 **Entrena** — Programas adaptados a tu objetivo, lugar y nivel
  - 👣 **Anda** — Cada paso del día suma. El cuentapasos convierte tu rutina en progreso
  - 🏆 **Compite** — Ranking semanal con tu grupo para mantenerse activo
- Social proof: "⭐ 4.8 · +25.000 personas ya han transformado su cuerpo"
- CTA: "Continuar"

**Decisión de formato:** Una sola pantalla (no 2). Los 3 conceptos son cortos y relacionados — verlos juntos comunica la filosofía completa de un golpe.

---

### Pantalla de Health permissions (Frame 556)

**Concepto:** No pedir permisos como un trámite — mostrar el cuentapasos ya en acción con datos reales del teléfono.

**Estructura:**
- Widget visual con número de pasos del día (p.ej. 7.500 pasos)
- Tabs de actividad: Calorías / Racha / Pasos / Tiempo / Distancia
- Headline: "ACTIVA TU CONTADOR DE PASOS"
- Descripción: "Tus pasos del día cuentan como actividad..."
- Nota de privacidad: "Sólo usamos tu información de pasos para mostrarte tu actividad. No compartimos esta información con terceros."
- CTA primario: "Conectar con Apple Health"
- CTA secundario: "Conectar con Google Health"
- Escape: "Quizás más tarde" (sutil, en texto)

---

### Pricing screen

**Estructura final:**
- Hook "Hoy 0€ / Día 7 si te encaja" — elimina el riesgo percibido
- 3 tiers con Trimestral destacado como "Más popular"
- Social proof: "⭐ 4.8 · +25.000 personas ya lo están usando" — justo antes del CTA, como último refuerzo
- CTA: "Activar prueba gratis"
- "Cancela cuando quieras" — quita la última fricción

**Decisión:** se eliminó la sección de bullets de beneficios ("Programas premium completos / Progresión por fases / Acceso completo a explora"). El usuario que llega al pricing ya ha pasado por la metodología y los health perms — repetir los beneficios en lista genérica rompe el momentum. La pantalla se focaliza en hacer la decisión fácil, no en convencer.

---

## Diferencias clave con el v1

| Issue | v1 | v2 |
|-------|----|----|
| Contador pasos inconsistente | "Paso 1 de 11" → "Paso 2 de 13" | Numeración fija desde el inicio |
| Imágenes AI-generated | Fotos de cuerpos AI en género y objetivo | Iconografía neutral |
| Banner amarillo fuera del DS | En pantalla de revisión | Eliminado |
| Pantallas con espacio vacío | 60%+ negro en radio buttons | Preguntas agrupadas |
| Longitud | 22 pantallas | 12 pantallas |
| Lógica de flujo | Solo cuestionario | Embudo completo (quiz → proof → pago) |
| Health perms | Post-registro | Pre-pago (cuentapasos activo antes de pagar) |

---

## Pendiente

- [x] Quitar bullets de beneficios del PricingScreen — reemplazados por línea de social proof justo antes del CTA
- [ ] Confirmar con dev el flujo de Health perms sin registro (ya confirmado que funciona en prod, falta integrar en nuevo flujo)
- [ ] Diseñar variante del programa recomendado para cada combinación de objetivo × tipo de entreno
- [ ] Decidir si mostrar 1 o 2 programas recomendados en pantalla 8
- [ ] Social proof dinámica: mostrar before/after que coincida con el objetivo + género seleccionados (hay exploración en Figma con grid organizado por segmentos)
