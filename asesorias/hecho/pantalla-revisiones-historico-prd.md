# PRD — Pantalla de Revisiones (Histórico)

**Estado:** En definición  
**Fecha:** 2026-05-19  
**Relacionado con:** [pantalla-revision-ux.md](pantalla-revision-ux.md) — flow del cuestionario quincenal

---

## Problema

El cliente de asesoría paga por un servicio caro y mantiene un esfuerzo sostenido durante meses. Cada dos semanas completa una revisión: se pesa, se fotografía, responde preguntas. Ese ritual genera datos.

El problema es que esos datos no vuelven a aparecer. El usuario vive el reveal en el momento y después no tiene ningún lugar al que volver cuando lo necesita de verdad: cuando el peso se estanca, cuando la motivación baja, cuando se pregunta si merece la pena seguir.

La decisión de continuar o abandonar la toma en ese momento de duda — y la app no tiene nada que decirle.

---

## Objetivo

Crear una pantalla dedicada que convierta el histórico de revisiones quincenales en **evidencia tangible de transformación** — el argumento más poderoso para que el cliente continúe en el programa.

---

## Usuario objetivo

Cliente de asesoría con al menos 2 revisiones completadas.  
Estado emocional: quiere validación de que el esfuerzo está valiendo la pena.  
Contexto de uso: móvil, en casa, probablemente después de completar una revisión o cuando necesita motivación.

---

## Alcance

**IN — esta pantalla**
- Visualización histórica de todas las revisiones del cliente
- Comparador de fotos primera revisión vs última
- Curva de composición corporal (peso + % grasa)
- Carrete de fotos frontales con score por revisión
- Detalle completo de una revisión individual

**OUT — no incluido aquí**
- Flujo de captura del cuestionario quincenal → ver [pantalla-revision-ux.md](pantalla-revision-ux.md)
- Vista del coach (dashboard de asesoría)
- Notificaciones de revisión pendiente

---

## Estructura de la pantalla

### Zona 1 — El arco completo (hero)

Comparador **primera revisión vs última**, actualizado automáticamente con cada nueva revisión.

- Foto frontal de revisión 1 | Foto frontal de revisión N (más reciente)
- Delta calculado debajo: `−4.2% grasa corporal · 18 semanas · 9 revisiones`
- El delta prioriza % grasa sobre peso (más representativo de composición corporal)

**Propósito:** Dar al usuario la visión más impactante de su transformación en el primer vistazo. Es el dato que quiere mostrar a alguien.

---

### Zona 2 — Las curvas

Gráfica dual con dos series sobre el mismo eje temporal:
- Línea 1: peso corporal (kg)
- Línea 2: % grasa corporal

Cada punto = una revisión.  
**Los puntos son interactivos** — tap abre el [detalle de revisión](#detalle-de-revisión-individual).

**Comportamiento de la gráfica:**
- Eje X: revisiones (no fechas exactas — espaciado uniforme)
- Si el peso está estancado pero el % grasa baja, la gráfica lo hace evidente visualmente
- Mínimo 2 puntos para renderizar la curva; con 1 punto solo se muestra el punto aislado

---

### Zona 3 — El carrete

Scroll horizontal de **fotos frontales** de todas las revisiones, ordenadas de más antigua a más reciente (izquierda → derecha).

Cada elemento del carrete:
- Foto frontal (thumbnail)
- Score del ciclo debajo
- Peso de esa revisión

**Tap en cualquier elemento** → abre el [detalle de revisión](#detalle-de-revisión-individual).

**Propósito:** Narrativa visual cronológica. El usuario puede ver su transformación física de un vistazo sin abrir cada revisión.

---

### Detalle de revisión individual

Modal o pantalla de detalle, accesible desde la gráfica o el carrete.

Contenido:
- Fecha de la revisión
- Las 3 fotos (frontal, lateral, espalda)
- Peso + % grasa
- Score del ciclo con desglose (base + bonus racha)
- Autopuntuación del ciclo (Dieta / Entreno / Pasos)
- Racha en ese momento

---

## Modelo de datos por revisión

| Dato | Fuente | Notas |
|------|--------|-------|
| Fecha | Sistema | |
| Peso corporal (kg) | Usuario | Input en el cuestionario |
| % grasa corporal | IA (análisis fotos) | Margen de error ~1-3% |
| Foto frontal | Usuario | |
| Foto lateral | Usuario | |
| Foto espalda | Usuario | |
| Autopuntuación Dieta | Usuario | 1–5 |
| Autopuntuación Entreno | Usuario | 1–5 |
| Autopuntuación Pasos | Usuario | 1–5 |
| % entrenos completados | Sistema | Últimas 2 semanas |
| % días pasos objetivo | Sistema | Sobre 14 días |
| Racha | Sistema | Revisiones consecutivas |
| Score del ciclo | Sistema | Ver fórmula abajo |

**Fórmula del score:**
```
Score base  = % entrenos completados (0–100)
            + % días pasos objetivo (0–100)

Bonus racha = Fibonacci: racha 1→+1, 2→+2, 3→+4, 4→+8, 5→+16...

Score final = Score base + Bonus racha
```

---

## Estados y edge cases

| Estado | Comportamiento |
|--------|---------------|
| 0 revisiones | No aplica — el usuario no llega a esta pantalla |
| 1 revisión | Sin comparador (no hay "antes"). Hero = "Tu punto de partida". Sin curva (un solo punto). Carrete con una sola foto. |
| 2 revisiones | Comparador aparece. Curva con 2 puntos (línea). Carrete con 2 fotos. |
| Curva de peso plana | Priorizar % grasa como métrica principal en el hero delta |
| Revisión sin fotos | El carrete muestra placeholder. El comparador no aparece hasta tener fotos en revisión 1 y última. |
| Score muy bajo en un ciclo | Se muestra sin editar — la honestidad es parte del método |

---

## Preguntas abiertas

| Pregunta | Impacto |
|----------|---------|
| ¿El cliente puede comparar cualquier par de revisiones (no solo primera vs última)? | Cambia el comparador de estático a interactivo — mayor complejidad |
| ¿El coach ve la misma pantalla o tiene una vista diferente? | Define si el diseño necesita variantes |
| ¿Hay un límite de revisiones almacenadas? | Afecta al carrete y la gráfica a largo plazo |

---

## Orden de diseño

```
1. Zona 1 — Comparador hero
      ↓
2. Zona 3 — Carrete de fotos
      ↓
3. Zona 2 — Curvas
      ↓
4. Detalle de revisión individual
```

Se empieza por el comparador porque es el elemento más impactante y define el tono visual de la pantalla.
