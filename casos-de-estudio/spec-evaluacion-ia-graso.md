# Spec: Sistema de evaluación de precisión — IA % graso

## Contexto

El dashboard tiene una herramienta de IA (`/ai/tester`) que estima el % de grasa corporal de clientes a partir de fotos. Actualmente tenemos métricas de comparación entre modelos (spread, repetibilidad) pero no tenemos una métrica de **precisión real** — es decir, no sabemos cuánto se equivoca el modelo respecto al % graso verdadero.

Disponemos de un dataset de referencia: ~100 fotos de clientes donde el % graso real está verificado (rango 8%–38%). Este dataset es el "ground truth" que permite calcular el error real del modelo.

**El objetivo de esta spec es construir la infraestructura para ejecutar esa evaluación de forma permanente y reproducible, desde cualquier sitio.**

---

## Parte 1 — Endpoint de fotos directas

### `POST /api/admin/ai-tester/run-photo`

**Qué hace:** recibe hasta 3 fotos directamente (sin necesidad de que sean de ningún cliente del sistema), las pasa por los modelos de IA configurados, y devuelve las estimaciones. No persiste nada en base de datos.

Hay un borrador de implementación en el repositorio local para revisión. Los cambios afectan solo a dos archivos, ambos aditivos:
- `app/schemas/ai_body_fat.py` — dos schemas nuevos (`AiTesterEvalResult`, `AiTesterEvalResponse`)
- `app/api/routes/dashboard/ai_tester.py` — el endpoint y una función helper de renderizado de texto

**Request:** `multipart/form-data`

| Campo | Tipo | Obligatorio | Default | Descripción |
|-------|------|-------------|---------|-------------|
| `photos` | file(s) | Sí | — | 1–3 imágenes JPG/PNG/HEIC |
| `gender` | string | No | `"unknown"` | `"male"` / `"female"` / `"unknown"` |
| `weight_kg` | float | No | `70.0` | Peso en kg |
| `height_cm` | float | No | `170.0` | Altura en cm |
| `config_ids` | string | No | `""` | IDs de modelos separados por coma (ej. `"1,2"`). Si vacío, usa el modelo por defecto |

**Response:** `200 OK`
```json
{
  "results": [
    {
      "model_identifier": "gemini-2.5-flash-lite",
      "status": "success",
      "point_estimate_bf_pct": 18.5,
      "range_low": 16.0,
      "range_high": 21.0,
      "confidence": "medium",
      "confidence_pct": 72.0,
      "gender_observed": "male",
      "limiting_factors": ["lighting"],
      "visible_cues": ["abdominal definition"],
      "cost_usd": 0.00018,
      "latency_ms": 1850
    }
  ]
}
```

**Auth:** admin-only (`require_admin`), igual que el resto de `/admin/ai-tester/*`.

---

## Parte 2 — Dataset de ground truth en la nube

El dataset de referencia son ~100 fotos locales organizadas por % graso real (nombres como `18.JPG`, `18_a.JPG`, etc.). Para que el sistema de evaluación sea permanente y no dependa del disco de nadie, las fotos deben vivir en S3 y estar registradas en la base de datos.

### Tabla nueva: `ai_eval_dataset`

```sql
CREATE TABLE ai_eval_dataset (
    id          SERIAL PRIMARY KEY,
    photo_url   TEXT NOT NULL,           -- URL S3 pública
    bf_pct_true FLOAT NOT NULL,          -- % graso real verificado
    label       TEXT,                    -- ej. "18_a" (nombre original del archivo)
    gender      TEXT DEFAULT 'unknown',
    notes       TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

**Migración Alembic:** crear esta tabla. No toca ninguna tabla existente.

**Carga inicial:** subir las ~100 fotos de la carpeta `samples-%-graso/` a S3 (bucket existente de revisiones o uno nuevo dedicado a eval) e insertar las filas correspondientes. Se puede hacer con un script one-shot sin necesitar endpoints de gestión todavía.

### Endpoints de gestión (admin-only, bajo `/api/admin/ai-tester/eval-dataset`)

| Método | Path | Descripción |
|--------|------|-------------|
| `GET` | `/eval-dataset` | Lista todas las fotos del dataset (con paginación) |
| `POST` | `/eval-dataset` | Añade una foto: sube a S3, inserta fila |
| `DELETE` | `/eval-dataset/{id}` | Elimina una entrada |

El `POST` acepta `multipart/form-data` con `photo` (archivo), `bf_pct_true` (float), `gender` (string opcional), `notes` (string opcional).

---

## Parte 3 — Endpoint de evaluación completa

Una vez el dataset esté en la nube, añadir un endpoint que ejecute la evaluación automáticamente:

### `POST /api/admin/ai-tester/run-eval`

**Qué hace:**
1. Lee todas las fotos del dataset (`ai_eval_dataset`)
2. Pasa cada foto por los modelos especificados (usando la misma lógica que `/run-photo`)
3. Calcula métricas agregadas
4. Devuelve el informe completo

**Request:**
```json
{
  "config_ids": [1, 2],
  "sample_size": null
}
```
`sample_size: null` = dataset completo. Un número = muestra aleatoria de ese tamaño.

**Response:** `200 OK`
```json
{
  "total_photos": 98,
  "per_model": [
    {
      "model_identifier": "gemini-2.5-flash-lite",
      "mae": 2.3,
      "bias": -0.8,
      "rmse": 3.1,
      "within_2pct": 0.61,
      "within_5pct": 0.89,
      "by_range": [
        { "range": "8–15%",  "mae": 1.9, "bias": -1.2, "n": 22 },
        { "range": "16–24%", "mae": 2.1, "bias": -0.5, "n": 41 },
        { "range": "25–38%", "mae": 3.2, "bias": -0.9, "n": 35 }
      ],
      "cost_usd_total": 0.018,
      "avg_latency_ms": 1850
    }
  ],
  "photo_results": [
    {
      "eval_dataset_id": 12,
      "photo_url": "https://...",
      "bf_pct_true": 18.0,
      "estimates": [
        { "model_identifier": "gemini-2.5-flash-lite", "point_estimate_bf_pct": 19.5, "error": 1.5 }
      ]
    }
  ]
}
```

**Nota de implementación:** este endpoint puede tardar varios minutos. Considerar si debe ser síncrono (timeout alto) o disparar una tarea Celery y devolver un `job_id` para consultar después.

---

## Orden de ejecución recomendado

1. **Parte 1** — endpoint `/run-photo`. Ya hay un borrador para revisar. Útil por sí solo para pruebas manuales.
2. **Parte 2** — migración + carga inicial del dataset en S3. La carga inicial puede hacerse con un script sin necesitar los endpoints de gestión.
3. **Parte 3** — endpoint `/run-eval`.
4. **Endpoints de gestión del dataset** (Parte 2, sección gestión) — lo menos urgente.

---

## Notas

- Todos los endpoints son admin-only. Sin impacto en usuarios ni coaches.
- La única tabla nueva es `ai_eval_dataset`. No se modifica ninguna tabla existente.
- El dataset de fotos está disponible localmente en `samples-%-graso/` (8%–38% de grasa, ~100 fotos).
