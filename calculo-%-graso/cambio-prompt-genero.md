# Cambio de prompt: diferenciación por género + contexto biométrico

**Fecha:** Junio 2026  
**Área:** Cálculo de % graso corporal por IA  
**Estado:** Pendiente de aplicar en dashboard (`/ai/models/1/edit`)  
**Quién lo aplica:** Kata (cambio de configuración, sin tocar código)

---

## Por qué se hace este cambio

El prompt anterior usaba una única referencia visual para todos los clientes. El problema: esa referencia está basada en el cuerpo masculino (escala Henselmans), y el modelo la aplicaba también a mujeres.

El resultado medido en 90 fotos de referencia con % graso real conocido:

| | Sesgo (error medio) |
|---|---|
| Hombres | +1.18 pts |
| Mujeres | **+4.72 pts** |

La IA sobreestimaba el % graso de las mujeres en casi 5 puntos de media. La causa: en hombres, la grasa se lee principalmente en el abdomen. En mujeres, se distribuye en cadera y muslos — y el modelo, sin instrucciones específicas, ignoraba eso.

Con el nuevo prompt diferenciado por género, el sesgo femenino baja de **+4.72 a +0.89 pts**.

---

## Qué cambia exactamente

### Antes

Un único system prompt genérico que mencionaba el género como dato secundario. No tenía escala de referencia femenina ni instrucciones sobre cómo leer la grasa en cuerpos femeninos.

### Ahora

Un único system prompt que contiene dos bloques de instrucciones — uno para hombre y uno para mujer — y el modelo selecciona el bloque correcto según el género que recibe en el user prompt.

El user prompt ya incluía `{gender}`, `{weight_kg}` y `{height_cm}` como placeholders. No hay cambio de código — solo se actualiza el texto del system prompt en el dashboard.

---

## Configuración completa

### System prompt (nuevo)

```
You are a body-composition analyst for certified fitness coaches. Estimate body-fat percentage from the physique photos provided.

IF THE SUBJECT IS MALE:
Anchor to the Henselmans male visual reference scale: 5% (contest lean), 10% (visible abs), 15% (soft abs outline), 20% (no ab definition), 25% (love handles), 30% (rounded belly), 35% (prominent belly).
Primary cues: 1. Abdominal definition 2. Oblique/serratus visibility 3. Vascularity 4. Deltoid striations 5. Lower-back/lat detail 6. Love-handle fat 7. Glute/leg fat
Calibration: estimates tend to run 1–2 points high. Shade conservative.
Uncertainty: ±3% range for a clear photo.

IF THE SUBJECT IS FEMALE:
Use the female body fat scale: 14–17% (athletic, visible abs), 18–22% (fit, defined waist), 23–27% (soft midsection, moderate hip/thigh fat), 28–32% (rounder lower body, waist less defined), 33–38% (pronounced curves, significant hip/thigh mass).
Primary cues: 1. Hip-to-waist ratio (MOST diagnostic) 2. Thigh/inner-thigh fat 3. Lower-ab roundness 4. Upper-arm fullness 5. Glute shape 6. Face/neck leanness
NOTE: visible abs in women only at ≤18% — do NOT use ab absence as a high BF indicator.
Critical: female fat distributes to hips/thighs, not abs. Weigh lower body heavily.
Calibration: estimates tend to run 4–5 points high for women. Apply a firm downward adjustment.
Uncertainty: ±4% minimum range for women.

BIOMETRIC CONTEXT: Use the subject's stated gender, weight and height as supporting context — the photos are the primary evidence. Use BMI to cross-check plausibility (e.g. a BMI of 30 with an estimated 15% BF is a red flag).

LIMITING FACTORS: Treat loose clothing, poor lighting, flexed/posed shots, distance or low resolution as limiting_factors that widen the range.

Return ONLY valid JSON: point_estimate_bf_pct, range_low, range_high, confidence ("low"|"medium"|"high"), confidence_pct (0–100), limiting_factors (array), visible_cues (array), gender_observed ("male"|"female"|"unclear"). Never return null for numeric fields.
```

### User prompt template (sin cambios, ya estaba bien)

```
Subject gender: {gender}. Bodyweight: {weight_kg} kg. Height: {height_cm} cm. Three physique photos follow in this order: front, back, side. Use all three.
```

### Resto de configuración (no tocar)

| Parámetro | Valor |
|---|---|
| Modelo | Gemini 2.5 Flash-Lite |
| Temperatura | 0.2 |
| Imagen lado máximo | 768px |

---

## Resultados del experimento que valida el cambio

Validado sobre 90 fotos con % graso real conocido (dataset `samples-%-graso/`):

| Configuración | MAE | Sesgo | ≤ 2 pts |
|---|---|---|---|
| Prompt universal (original) | 3.43 pts | +2.44 | 40% |
| Prompt universal −2.5 flat | 2.69 pts | −0.06 | 58% |
| Prompt por género (este cambio) | 2.81 pts | +0.16 | 48% |
| Prompt por género + corrección por tramos | **2.10 pts** | ~0 | **65%** |

El prompt por género solo ya es mejor que el original en sesgo global. Combinado con la corrección por tramos (pendiente de implementar en backend) llega al mejor resultado medido.

**Test en 100 clientes reales de producción:**
- 54 hombres, 44 mujeres
- El género declarado en el cuestionario coincidió con el observado en foto en el 100% de los casos → la selección automática del prompt por género es robusta
- Media hombres: 21.6% BF — Media mujeres: 28.8% BF (diferencia fisiológicamente correcta con IMC similar)

---

## Qué queda pendiente

### Corrección bidireccional por tramos (siguiente paso, requiere código)

El modelo tiene un patrón de regresión hacia el centro: tira las estimaciones hacia ~22-25% independientemente del cliente real. La corrección por tramos ajusta el resultado después de que el modelo responde:

| Rango estimado | Corrección |
|---|---|
| < 15% | −1.7 pts |
| 15–20% | +0.9 pts |
| 20–25% | −1.6 pts |
| 25–30% | +4.0 pts |

Esto requiere un cambio en backend (5 líneas de código), no en el prompt. Validado con leave-one-out cross-validation → MAE 2.81 → **2.10 pts**.

### Validación del coach

El % estimado por la IA no se muestra directamente al cliente — el coach lo revisa dentro del flujo de revisión quincenal existente y lo ajusta antes de confirmarlo. Ver decisión completa en `casos-de-estudio/asesorias-v2.md`.
