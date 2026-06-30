# Auditoría de superseries — rutinas consultancy (producción)

**Fecha:** 11/06/2026 · **Alcance:** las 396 rutinas con `zone=consultancy` (vía API dashboard, `training-days` de cada una).

## ✅ Estado: CORREGIDO (11/06/2026) · 6 restantes RESUELTAS (19/06/2026)

Se aplicó la corrección vía `PATCH` (posición = mínima posición de los miembros) y se re-auditaron las 396 rutinas: **1.133 de 1.139 superseries quedaron en su posición correcta**. Las 6 restantes estaban en días con posiciones duplicadas (dato ambiguo de origen) y requerían decisión manual:

| Rutina | Días | Superseries pendientes | Estado |
|---|---|---|---|
| 1021 — RECOMPOSICION-CHICAS-GIMNASIO-FULLBODY DESCEN-MES 4-AVANZADO-5 DIAS | 1, 2, 3, 4, 5 | pos=4 con otro ítem también en 4 (miembros en 5) | ✅ resuelto 19/06 |
| 1027 — RECOMPOSICION-CHICOS-MANCUERNAS Y GOMAS-EMPUJES Y TRACCIONES-MES 2-AVANZADO-5 DIAS | 2 | pos=5 con miembros en 1 (posiciones solapadas) | ✅ resuelto 19/06 |

Las 6 se corrigieron el 19/06/2026 (17 `PATCH`, día limpio 1–N en los 10 días). Criterio de orden y detalle en [rutinas-que-comprobar.md](../rutinas-que-comprobar.md).

El resto del documento refleja el diagnóstico original previo a la corrección.

## Conclusión

El coach tiene razón: **1.117 de las 1.139 superseries (98%) tienen la posición mal guardada**. Afecta a **323 de las 326 rutinas que usan superseries**.

## Causa

En las rutinas creadas por el flujo normal del dashboard (zona subscription, usadas como referencia), la superserie ocupa su propia posición en la secuencia del día (ej.: ejercicios sueltos en 1–4, superserie en 5). En el import de las rutinas consultancy la posición de la superserie **no se calculó**: quedó en `0` (854 casos) o en valores que no corresponden (263 casos). Como la app ordena el día por posición, las superseries se renderizan al principio del día en vez de en su sitio.

Los ejercicios miembros sí conservan su posición correcta a nivel de día (ej. miembros en 5 y 6), por lo que **la posición correcta de cada superserie es recuperable**: es la posición mínima de sus miembros.

## Números

| Métrica | Valor |
|---|---|
| Rutinas auditadas | 396 |
| Rutinas con superseries | 326 |
| Superseries totales | 1139 |
| Superseries con posición incorrecta | 1117 |
| — con posición 0 | 854 |
| — con otra posición errónea | 263 |
| Rutinas afectadas | 323 |
| Días con posiciones duplicadas (caso especial) | 9 |

## Casos especiales: días con posiciones duplicadas

En estos 9 días hay dos ítems compartiendo la misma posición (error de origen en los datos, no del import). Requieren revisión manual del coach:

| Rutina | Día | Secuencia de posiciones |
|---|---|---|
| 1014 — RECOMPOSICION-CHICAS-GIMNASIO-EMPUJES Y TRACCIONES-MES 2-AVANZADO-4 DIAS | 1 | 1, 2, 3, 4, 4, 5, 6 |
| 1016 — RECOMPOSICION-CHICAS-GIMNASIO-EMPUJES Y TRACCIONES-MES 2-AVANZADO-2 DIAS | 1 | 1, 2, 3, 4, 4, 5, 6 |
| 1016 — RECOMPOSICION-CHICAS-GIMNASIO-EMPUJES Y TRACCIONES-MES 2-AVANZADO-2 DIAS | 2 | 1, 2, 3, 4, 4, 5, 6 |
| 1021 — RECOMPOSICION-CHICAS-GIMNASIO-FULLBODY DESCEN-MES 4-AVANZADO-5 DIAS | 1 | 1, 2, 3, 4, 5, 5, 6, 6 |
| 1021 — RECOMPOSICION-CHICAS-GIMNASIO-FULLBODY DESCEN-MES 4-AVANZADO-5 DIAS | 2 | 1, 2, 3, 4, 5, 5, 6, 6 |
| 1021 — RECOMPOSICION-CHICAS-GIMNASIO-FULLBODY DESCEN-MES 4-AVANZADO-5 DIAS | 3 | 1, 2, 3, 4, 5, 5, 6, 6 |
| 1021 — RECOMPOSICION-CHICAS-GIMNASIO-FULLBODY DESCEN-MES 4-AVANZADO-5 DIAS | 4 | 1, 2, 3, 4, 5, 5, 6, 6 |
| 1021 — RECOMPOSICION-CHICAS-GIMNASIO-FULLBODY DESCEN-MES 4-AVANZADO-5 DIAS | 5 | 1, 2, 3, 4, 5, 5, 6, 6 |
| 1027 — RECOMPOSICION-CHICOS-MANCUERNAS Y GOMAS-EMPUJES Y TRACCIONES-MES 2-AVANZADO-5 DIAS | 2 | 1, 1, 2, 2, 3, 4 |

## Mapeo completo

El detalle superserie a superserie (1.139 filas: posición actual, posición esperada, posiciones de miembros y de ejercicios sueltos) está en [auditoria-superseries-consultancy.csv](auditoria-superseries-consultancy.csv).

## Corrección propuesta

Para cada superserie mal posicionada: `PATCH /api/dashboard/routines-v2/{routine_id}/training-days/{day_id}/supersets/{superset_id}` con `position = min(posiciones de sus miembros)`. Es un cambio mecánico y verificable; los 9 días con duplicados se revisarían aparte.
