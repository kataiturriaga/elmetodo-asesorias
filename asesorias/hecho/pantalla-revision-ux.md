# Pantalla de Revisión — UX Strategy

**Estado:** Modelo de datos cerrado — listo para diseñar en Figma  
**Fecha inicio:** 2026-05-12  
**Próximo paso:** Diseñar cuestionario en Figma → diseñar pantalla de progreso

---

## Contexto

Rediseño de la pantalla de revisión periódica del cliente de asesoría. La pantalla actual (`Progreso`) tiene problemas de jerarquía, solo muestra peso, y las fotos tienen un UX confuso.

Screenshots de referencia: pantalla actual de Diego Martínez (usuario de prueba).

---

## Qué debe mostrar la pantalla

1. Progreso de peso corporal
2. Progreso de % de grasa corporal
3. Fotos de las revisiones (histórico)
4. Cómo cumplió las semanas previas a cada revisión (autopuntuación)
5. Score de actividad calculado por el sistema (entrenos + pasos)

---

## Modelo de datos de una revisión

| Dato | Fuente | Periodicidad |
|------|--------|-------------|
| Peso corporal | Usuario (input manual) | Por revisión (cada 2 semanas) |
| % grasa corporal | IA (análisis de fotos) | Por revisión |
| Fotos (3 ángulos) | Usuario (cámara) | Por revisión |
| Autopuntuación del ciclo | Usuario (slider 1-5) | Por revisión — visible al coach + histórico usuario |
| % entrenos completados | Sistema | Últimas 2 semanas |
| % días pasos objetivo completados | Sistema | Últimas 2 semanas (de 14 días) |
| Racha de revisiones | Sistema | Revisiones consecutivas sin saltarse ninguna |
| Score total del ciclo | Sistema (fórmula) | Por revisión |

---

## Fórmula del score de ciclo

```
Score base  = % entrenos completados (0–100)
            + % días pasos objetivo completados (0–100)
            → máximo base: 200

Bonus racha = Fibonacci por revisiones consecutivas:
              racha 1 → +1
              racha 2 → +2
              racha 3 → +4
              racha 4 → +8
              racha 5 → +16 ...

Score final = Score base + Bonus racha
```

**Notas:**
- % grasa corporal se muestra en el reveal pero NO entra en la fórmula (margen de error de IA ~1-3% lo hace poco fiable como input de score)
- La autopuntuación del ciclo no entra en el score — es señal cualitativa para el coach
- La racha se rompe si se salta una revisión (no hay revisión parcial)

---

## Flow del cuestionario — decisiones cerradas

**Frecuencia:** cada 2 semanas  
**Tono:** ritual tipo Spotify Wrapped — momento de revelación, no formulario

### Fase 1 — Capture (5 pasos, uno por pantalla)

| Paso | Acción | Detalle |
|------|--------|---------|
| 1 | Peso corporal | Input numérico grande, referencia del ciclo anterior |
| 2 | Foto frontal | Con guía de postura |
| 3 | Foto lateral | Con guía de postura |
| 4 | Foto espalda | Con guía de postura |
| 5 | Slider autopuntuación | "¿Cómo fue el ciclo?" — 1–5 |

### Fase 2 — Reveal (5 pantallas, una por dato)

| Pantalla | Dato | Tipo |
|----------|------|------|
| 1 | % grasa corporal | Informativo (IA) |
| 2 | % entrenos completados | Componente del score |
| 3 | % días pasos objetivo | Componente del score |
| 4 | Racha + bonus Fibonacci | El multiplicador dramático |
| 5 | Score total del ciclo | El clímax |

---

## Orden de diseño

```
1. Definir modelo de datos  ← HECHO
      ↓
2. Diseñar cuestionario de revisión  ← SIGUIENTE
      ↓
3. Diseñar pantalla de progreso  ← PENDIENTE
```

---

## Problemas críticos de la pantalla actual

1. **Gráfica plana** — visualmente comunica "nada ha pasado". Hay que gestionar el estado de datos escasos (pocas revisiones, sin variación).
2. **Fotos con memes encima** — entretenido pero confunde el objetivo de la sección.
3. **Sin jerarquía** — el gráfico, las fotos y el header compiten igual.
4. **Solo peso** — si se añade % grasa corporal, el peso puede estancarse mientras la composición mejora. Mostrar solo peso es potencialmente desmotivante y engañoso.

---

## Preguntas cerradas

| Pregunta | Respuesta |
|----------|-----------|
| Frecuencia de revisión | Cada 2 semanas |
| Autopuntuación | Slider 1–5, visible al coach + en histórico del usuario, no entra en el score |
| Activity score | Dos métricas separadas: % entrenos + % días pasos (0–100 cada una) |
| % grasa en score | No — margen de error de IA lo hace poco fiable |
| Reveal format | Una pantalla por dato (Spotify Wrapped puro) |
| Racha | Revisiones consecutivas sin saltarse ninguna |

## Preguntas pendientes

- **¿El cliente ve todas sus revisiones pasadas o solo la última?** — Define si la pantalla de progreso es "histórico" o "estado actual".

---

## UX Context

**Usuario objetivo:** Cliente de asesoría — estado emocional mixto: esperanzado pero ansioso. Quiere ver si su esfuerzo está dando resultados.  
**Contexto de uso:** Móvil, en casa, ritual periódico.  
**Insight central:** La revisión es el momento de verdad del coaching. Un mal UX aquí erosiona la confianza en el método aunque los resultados sean buenos.
