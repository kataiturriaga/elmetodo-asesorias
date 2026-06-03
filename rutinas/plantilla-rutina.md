# Plantilla de Rutina — El Metodo

> **Instrucciones para el entrenador**
> 1. Rellena los metadatos de la rutina en la sección `## DATOS DE LA RUTINA`.
> 2. Añade tantos días (workouts) como necesites, copiando el bloque `### DÍA X`.
> 3. Dentro de cada día, añade los ejercicios en la tabla. Usa el nombre **exacto** del catálogo (`rutinas/catalogo-ejercicios.md`).
> 4. Para supersets: pon el mismo valor en la columna `Superset` para los ejercicios que van juntos (ej. `A`, `B`, `C`…). Déjalo vacío si es ejercicio individual.
> 5. Cuando hayas terminado, avisa a Claude y leerá este documento para subirlo a producción.

---

## DATOS DE LA RUTINA

| Campo | Valor |
|-------|-------|
| **Nombre** | _(ej. CHICOS-GIMNASIO-MES1-PRINCIPIANTE-5DIAS)_ |
| **Género** | _(male / female)_ |
| **Ubicación** | _(gym / home / home_with_material)_ |
| **Nivel** | _(principiante / avanzado)_ |
| **Objetivo** | físico |
| **Subobjetivo** | _(definición / ganancia muscular)_ |
| **Iteración** | _(número del mesociclo: 1, 2, 3…)_ |
| **Es rutina por defecto** | _(sí / no)_ |
| **Número de días** | _(número total de días de entrenamiento)_ |

---

## DÍAS DE ENTRENAMIENTO

> **TUT** = Tempo: [segundos excéntrica, segundos concéntrica]. Ej. `[2, 1]` = bajar en 2s, subir en 1s.
> **RIR** = Repeticiones en reserva. Ej. `2` = parar 2 reps antes del fallo.
> **Descanso** = segundos entre series.
> **Técnica** = drop set, rest-pause, oclusión… (dejar vacío si ninguna).
> **Info** = notas adicionales para el usuario (dejar vacío si no hay).

---

### DÍA 1 — [Nombre del día, ej. Pecho + Tríceps]

| Campo | Valor |
|-------|-------|
| **TUT** | `[2, 1]` |
| **RIR** | `2` |

| # | Ejercicio | Series | Reps | Descanso (s) | Superset | Técnica | Info |
|---|-----------|--------|------|--------------|----------|---------|------|
| 1 | _(nombre exacto del catálogo)_ | 3 | 12 | 90 | | | |
| 2 | _(nombre exacto del catálogo)_ | 3 | 12 | 90 | | | |
| 3 | _(nombre exacto del catálogo)_ | 3 | 15 | 60 | | | |
| 4 | _(nombre exacto del catálogo)_ | 3 | 15 | 60 | | | |

---

### DÍA 2 — [Nombre del día, ej. Espalda + Bíceps]

| Campo | Valor |
|-------|-------|
| **TUT** | `[2, 1]` |
| **RIR** | `2` |

| # | Ejercicio | Series | Reps | Descanso (s) | Superset | Técnica | Info |
|---|-----------|--------|------|--------------|----------|---------|------|
| 1 | _(nombre exacto del catálogo)_ | 3 | 12 | 90 | | | |
| 2 | _(nombre exacto del catálogo)_ | 3 | 12 | 90 | | | |
| 3 | _(nombre exacto del catálogo)_ | 3 | 15 | 60 | | | |
| 4 | _(nombre exacto del catálogo)_ | 3 | 15 | 60 | | | |

---

### DÍA 3 — [Nombre del día, ej. Pierna]

| Campo | Valor |
|-------|-------|
| **TUT** | `[2, 1]` |
| **RIR** | `2` |

| # | Ejercicio | Series | Reps | Descanso (s) | Superset | Técnica | Info |
|---|-----------|--------|------|--------------|----------|---------|------|
| 1 | _(nombre exacto del catálogo)_ | 3 | 12 | 90 | | | |
| 2 | _(nombre exacto del catálogo)_ | 3 | 12 | 90 | | | |
| 3 | _(nombre exacto del catálogo)_ | 3 | 15 | 60 | | | |
| 4 | _(nombre exacto del catálogo)_ | 3 | 15 | 60 | | | |

---

### DÍA 4 — [Nombre del día]

| Campo | Valor |
|-------|-------|
| **TUT** | `[2, 1]` |
| **RIR** | `2` |

| # | Ejercicio | Series | Reps | Descanso (s) | Superset | Técnica | Info |
|---|-----------|--------|------|--------------|----------|---------|------|
| 1 | _(nombre exacto del catálogo)_ | 3 | 12 | 90 | | | |
| 2 | _(nombre exacto del catálogo)_ | 3 | 12 | 90 | | | |
| 3 | _(nombre exacto del catálogo)_ | 3 | 15 | 60 | | | |
| 4 | _(nombre exacto del catálogo)_ | 3 | 15 | 60 | | | |

---

### DÍA 5 — [Nombre del día]

| Campo | Valor |
|-------|-------|
| **TUT** | `[2, 1]` |
| **RIR** | `2` |

| # | Ejercicio | Series | Reps | Descanso (s) | Superset | Técnica | Info |
|---|-----------|--------|------|--------------|----------|---------|------|
| 1 | _(nombre exacto del catálogo)_ | 3 | 12 | 90 | | | |
| 2 | _(nombre exacto del catálogo)_ | 3 | 12 | 90 | | | |
| 3 | _(nombre exacto del catálogo)_ | 3 | 15 | 60 | | | |
| 4 | _(nombre exacto del catálogo)_ | 3 | 15 | 60 | | | |

---

## EJEMPLO RELLENO (para referencia)

### Ejemplo — DÍA 1 — Hombro

| Campo | Valor |
|-------|-------|
| **TUT** | `[2, 1]` |
| **RIR** | `2` |

| # | Ejercicio | Series | Reps | Descanso (s) | Superset | Técnica | Info |
|---|-----------|--------|------|--------------|----------|---------|------|
| 1 | Press Militar sentado | 3 | 12 | 90 | | | |
| 2 | Remo al mentón barra Z | 3 | 15 | 60 | | | |
| 3 | Elevaciones laterales sentado | 3 | 15 | 60 | | | |
| 4 | Elevación frontal polea 1 mano | 3 | 12 | 60 | | | |
| 5 | Deltoides posterior en máquina | 3 | 15 | 60 | | | |

### Ejemplo — DÍA 2 — Pecho + Tríceps (con superset)

| Campo | Valor |
|-------|-------|
| **TUT** | `[2, 1]` |
| **RIR** | `2` |

| # | Ejercicio | Series | Reps | Descanso (s) | Superset | Técnica | Info |
|---|-----------|--------|------|--------------|----------|---------|------|
| 1 | Press banca con mancuernas | 4 | 10 | 90 | | | |
| 2 | Aperturas en polea sentado | 3 | 15 | 60 | | | |
| 3 | Extensión en polea cuerda | 3 | 15 | 0 | A | | |
| 4 | Press francés con mancuernas | 3 | 12 | 90 | A | | Superset con el anterior |
