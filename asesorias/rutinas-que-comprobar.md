# Rutinas que comprobar (superseries pendientes)

**Fecha:** 11/06/2026

Tras la corrección masiva de posiciones de superseries en las rutinas consultancy (1.133 de 1.139 corregidas y verificadas), quedan **6 superseries en 2 rutinas** que no se pudieron corregir automáticamente: tienen posiciones duplicadas de origen (dos ítems del día comparten la misma posición), así que el orden correcto lo tiene que decidir el coach mirando la rutina.

## Rutina 1021 — RECOMPOSICION-CHICAS-GIMNASIO-FULLBODY DESCEN-MES 4-AVANZADO-5 DIAS

Programa: `recomposicion-chicas-gimnasio-avanzado-5 dias` (ID 152), fase "mes 4".

| Día | Problema |
|---|---|
| 1 | La superserie está en posición 4 y hay un ejercicio suelto también en la 4 (secuencia del día: 1, 2, 3, 4, 5, 5, 6, 6) |
| 2 | Igual que el día 1 |
| 3 | Igual que el día 1 |
| 4 | Igual que el día 1 |
| 5 | Igual que el día 1 |

**Qué decidir:** si la superserie va antes o después del ejercicio suelto que comparte posición con ella.

## Rutina 1027 — RECOMPOSICION-CHICOS-MANCUERNAS Y GOMAS-EMPUJES Y TRACCIONES-MES 2-AVANZADO-5 DIAS

Programa: `recomposicion-chicos-mancuernas y gomas-avanzado-5 dias` (ID 192), fase "mes 2".

| Día | Problema |
|---|---|
| 2 | La superserie está en posición 5 pero sus ejercicios miembros están en la posición 1, solapados con otros ejercicios del día |

**Qué decidir:** en qué punto del día va realmente la superserie (¿al inicio, donde están sus miembros, o al final, donde está su posición actual?).

## Cómo proceder

Revisar estas dos rutinas en el dashboard y reordenar los ejercicios del día a mano, o pasarle a Kata el orden correcto y se aplica vía API. El detalle completo de la auditoría está en [auditoria-superseries-consultancy.md](auditoria-superseries-consultancy.md).
