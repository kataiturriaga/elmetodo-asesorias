# Rutinas que comprobar (superseries pendientes)

**Fecha original:** 11/06/2026 · **Resuelto:** 19/06/2026

## ✅ Estado: RESUELTO (19/06/2026)

Las **6 superseries en 2 rutinas** que quedaron pendientes tras la corrección masiva (tenían posiciones duplicadas de origen) ya están corregidas vía API. Las 17 operaciones `PATCH` se aplicaron con éxito y se verificó que los 10 días afectados quedan con posiciones distintas y contiguas, cumpliendo el invariante `posición_superserie = min(posiciones de sus miembros)`.

El criterio de orden lo decidió Claude a partir del nombre del día (orden de grupos musculares) y de la consistencia con los días hermanos de cada rutina; el detalle está más abajo.

---

## Rutina 1021 — RECOMPOSICION-CHICAS-GIMNASIO-FULLBODY DESCEN-MES 4-AVANZADO-5 DIAS

Programa: `recomposicion-chicas-gimnasio-avanzado-5 dias` (ID 152), fase "mes 4". Afecta a los 5 días.

**Situación:** cada día tenía 2 sueltos (pos 1,2), la superserie A (miembros 3,4, correcta) y la superserie B (miembros 5,6) chocando con 2 sueltos que también estaban en 5,6. La superserie B tenía además una posición basura (4) del import.

**Decisión:** la superserie B se queda en 5,6 y los 2 sueltos finales pasan a 7,8. Razón: en cada día los sueltos finales son justo el **último** grupo muscular del nombre del día (p. ej. en "Glúteo-Hombro-Pecho" los sueltos son Hombro y Pecho), mientras que la superserie B es el mismo grupo del bloque inicial. Agrupar la superserie con su grupo muscular y dejar los sueltos al final respeta el orden del nombre del día en los 5 días.

Por día se aplicó: superserie B `position 4→5`; suelto en pos 5 `→7`; suelto en pos 6 `→8`. Resultado: secuencia limpia 1–8 con superseries en pos 3 y 5.

## Rutina 1027 — RECOMPOSICION-CHICOS-MANCUERNAS Y GOMAS-EMPUJES Y TRACCIONES-MES 2-AVANZADO-5 DIAS

Programa: `recomposicion-chicos-mancuernas y gomas-avanzado-5 dias` (ID 192), fase "mes 2". Afecta solo al día 2.

**Situación:** todos los días hermanos (1, 3, 4, 5) son "4 sueltos (pos 1–4) + superserie al final (pos 5, miembros en 5,6)". En el día 2 los miembros de la superserie se habían corrompido a las posiciones 1,2 (la posición propia de la superserie, 5, ya era correcta), solapándose con los sueltos.

**Decisión:** mover los 2 miembros de la superserie de 1,2 → 5,6 para que el día 2 quede idéntico a sus hermanos. Resultado: 4 sueltos en 1–4 y superserie en 5,6.

## Trazabilidad

- Backup del estado previo (posiciones de todas las superseries y ejercicios de ambas rutinas, por si hace falta revertir): [hecho/superset_fix_backup_19062026.json](hecho/superset_fix_backup_19062026.json).
- Auditoría completa: [hecho/auditoria-superseries-consultancy.md](hecho/auditoria-superseries-consultancy.md).
