# Análisis de precisión — IA cálculo % graso

## Qué se hizo

Se evaluó el modelo `gemini-2.5-flash-lite` contra **105 fotos de referencia** con el % graso real conocido (rango 8%–38%). Para cada foto, el modelo devolvió su estimación y se calculó el error comparando con la etiqueta real.

Script utilizado: `eval_precision_graso.py` (repo `elmetodo_asesorias`)  
Fecha de evaluación: junio 2026

---

## Resultados globales

| Métrica | Valor |
|---------|-------|
| Error medio (MAE) | **3.52 pts** |
| Sesgo (media del error con signo) | **+2.49 pts** (sobreestima) |
| RMSE | 4.67 pts |
| Fotos con error ≤ 2 pts | 38.1% |
| Fotos con error ≤ 5 pts | 81.0% |

---

## Patrón principal: el modelo sobreestima en personas delgadas

El error no es aleatorio. El modelo tiene un "centro de gravedad" desplazado hacia el rango 22–25%, que es lo que probablemente considera "normal". Esto produce un patrón sistemático:

| Franja real | Fotos | Error medio |
|-------------|-------|-------------|
| 8–15% | 34 | +2.56 pts (sobreestima) |
| 16–24% | 47 | +4.03 pts (sobreestima fuerte) |
| 25–38% | 24 | -0.65 pts (prácticamente neutro) |

**Conclusión:** a personas delgadas les añade grasa, a personas con más grasa las ve con precisión. Es el efecto clásico de un modelo que tira las predicciones hacia el valor más común de su entrenamiento.

---

## Casos con error catastrófico (> 10 puntos)

Se detectaron 5 casos con errores de 11–17 puntos. Revisadas las fotos, todos tienen la misma causa: **la foto no reúne condiciones mínimas de evaluación**.

| GT real | Estimación IA | Error | Causa |
|---------|---------------|-------|-------|
| 19% | 32% | +13 pts | Foto recortada / mala calidad |
| 20% | 35% | +15 pts | Foto recortada / mala calidad |
| 21% | 38% | +17 pts | Foto recortada / mala calidad |
| 21% | 32% | +11 pts | Persona de espaldas |
| 27% | 38% | +11 pts | Foto recortada / mala calidad |

Cuando el modelo no puede ver el cuerpo bien, no devuelve un error — inventa una estimación alta "por si acaso". Esto es peligroso en producción porque sale con el mismo formato que una estimación buena.

---

## ¿Se puede corregir?

### Opción A — Corrección numérica (sin tocar el prompt)
Restar 2.5 puntos a toda estimación que devuelva el modelo.

- MAE actual: **3.52**
- MAE con corrección: **2.81**
- Sin cambios en código de prompts ni en el modelo

Es simple pero no distingue si el error viene de la franja o de una foto mala.

### Opción B — Instrucción de calibración en el prompt (recomendada)
Añadir una nota al `system_prompt` del modelo en la base de datos:

> *"Based on validated reference photos, your estimates for lean-to-medium subjects (below 25% BF) tend to run 2–3 points high. Adjust your point estimate conservatively when in doubt."*

Esto no requiere deploy de código. El prompt ya es editable desde el dashboard.

### Opción C — Detectar y marcar fotos no evaluables
El modelo ya devuelve `limiting_factors`. Si los factores incluyen señales de foto incompleta (recortada, solo espalda, oclusión alta), el dashboard podría mostrar el resultado con un aviso "estimación poco fiable" en lugar de presentarla igual que las demás.

Esta es la solución para los errores catastróficos — no son de calibración, son de calidad de imagen.

---

## Resumen ejecutivo

El modelo funciona bien en condiciones óptimas (foto frontal completa, buena iluminación). Los problemas son de dos tipos distintos:

1. **Sesgo sistemático** (+2.5 pts de media): corregible con calibración del prompt o ajuste numérico.
2. **Fallos por foto mala**: cuando la foto está recortada o la persona sale de espaldas, el modelo no falla con gracia — sobreestima masivamente. Solución: validar calidad de foto antes de mostrar el resultado.
