# Plan técnico — Generador de Cambios (collage de progreso)

**Feature:** Generador de Cambios — Coach Dashboard
**Spec de producto:** [`dashboard/generador-de-cambios.md`](../../dashboard/generador-de-cambios.md)
**Repo de implementación:** `elmetodo_api` (FastAPI / Python)
**Estado:** Plan aprobado — pendiente de implementar
**Última actualización:** 2026-06-17

---

## 1. Decisiones de arquitectura (cerradas)

| Decisión | Resolución | Motivo |
|---|---|---|
| **Motor de render** | **Pillow** | Ya es dependencia del repo (lo usa `photo_prepare_service.py`). Sin infra nueva. El layout es fijo y está validado en Figma, así que se traduce 1:1. Alternativa HTML/CSS (Playwright/Chromium o Satori/Node) se descartó por coste de infra en un stack Python puro. |
| **Ejecución** | **Síncrona** en el request (~2-4 s: 2 descargas + render + upload) | Acción puntual del coach, 1 imagen. Casi todos los endpoints del repo son sync. Si se vuelve lento → mover a Celery (`app/tasks/` ya existe). |
| **Storage del resultado** | **Google Drive** vía **service-account**, subiendo a una **Unidad compartida (Shared Drive)** | El equipo necesita un entorno conocido y navegable. ⚠️ La "My Drive" de una service-account NO es visitable por humanos: hay que usar un Shared Drive de Workspace con la SA como miembro (o una carpeta de cuenta real compartida con la SA). |
| **Fuente del % graso** | `Review.coach_body_fat_pct` **si existe → fallback** a la última estimación IA exitosa (`ReviewBodyCompositionEstimate.point_estimate_bf_pct`) **→ fallback** sin fila de % graso | El campo del coach existe en el modelo pero **hoy no se escribe** (lo añadirá Carles pronto). La cadena con fallback funciona hoy (IA) y mañana (coach) sin cambiar código. |
| **Foto frontal** | Siempre presente (la app la obliga al usuario) → solo *guard* defensivo | Nota del equipo: `photo_front` es campo obligatorio en la app. Se elimina el estado de error "foto faltante" del flujo principal (spec §7.3). |
| **Encuadre de fotos** | Cover-crop centrado a 440×720, **sin normalizar** | Riesgo de inconsistencia asumido para V1. |

---

## 2. Componentes a construir (`elmetodo_api`)

| Archivo | Responsabilidad |
|---|---|
| `app/services/collage_service.py` | **Núcleo.** Orquesta: selecciona reviews → calcula métricas/deltas → resuelve % graso (cadena con fallback) → descarga fotos → render → sube a Drive → devuelve URLs |
| `app/services/collage_renderer.py` | Solo el render Pillow (layout fijo 1080×1350, data-driven). Aislado para testear el dibujo sin red |
| `app/services/drive_service.py` | **Nuevo.** Auth service-account, upload del PNG a Shared Drive, permisos de link compartible, devuelve `webViewLink` + `download_url` |
| `app/repositories/review_repository.py` | **Añadir** `get_first_last_with_photo(user_id)` (reusa el `order_by(Review.review_date.asc())` ya existente) |
| `app/repositories/ai_body_fat_repository.py` | **Reusar** "latest successful estimate for a review" (ya existe) para el fallback de % graso |
| `app/schemas/collage.py` | `CollageResponse` (image_url, download_url, generated_at, métricas usadas) + errores tipados |
| `app/api/routes/dashboard/coach.py` | Endpoint `POST /me/users/{user_id}/progress-collage` |
| `app/services/image_service.py` | **Extender** con `upload_bytes(data, key) -> url` (hoy solo acepta `UploadFile`) — útil si en algún momento se duplica copia a S3 |
| `app/config/settings.py` | `GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH`, `GOOGLE_DRIVE_SHARED_DRIVE_ID` |
| `pyproject.toml` | `google-api-python-client`, `google-auth` |
| `tests/` | Unit del renderer + integración del endpoint |

### Reutilizar tal cual
- **Validación coach↔user**: patrón de `coach.py:630` → `user.coach_id != current_coach.id and not current_coach.is_admin`.
- **Descarga + decode de fotos** (incl. **HEIC de iPhone** vía `pillow-heif`): patrón de `app/services/photo_prepare_service.py`. ⚠️ Imprescindible para no fallar con fotos de iPhone.
- **Datos de review**: `Review.weight`, `Review.coach_body_fat_pct`, `Review.photo_front`, `Review.review_date`.

---

## 3. Fases de implementación

### Fase 1 — Datos y validaciones (sin imagen)
1. `get_first_last_with_photo`: primera y última review *confirmada* con `photo_front`. Excluir `coach_generated` (fake) si procede.
2. Resolución de % graso con la cadena de fallback (coach → IA → sin dato).
3. Endpoint que valida ownership + regla "≥2 reviews" y devuelve métricas en JSON (peso inicial/actual, % graso inicial/actual, deltas, días). Sin imagen aún → testeable rápido.
4. Errores tipados (400 con `code`): `not_enough_reviews`, `inconsistent_dates`, `partial_data`.

### Fase 2 — Renderer Pillow
5. `collage_renderer.render(data) -> bytes(PNG)`: traducir el frame de Figma (1080×1350, tokens DS, fotos cover-crop 440×720, pill, glow verde, logo, Open Sans).
6. Lógica de color por signo de cada delta (verde/rojo/gris) — spec §7.5.
7. Iterar contra el Figma como referencia visual.

### Fase 3 — Drive y wiring
8. `drive_service`: upload a Shared Drive, key/carpeta tipo `/El Método/Comparativas de Progreso/[Fecha]/`, permisos link.
9. Conectar todo en `collage_service` + exponer en el endpoint. Respuesta: `{ image_url, download_url, generated_at, metrics }`.

### Fase 4 — Robustez (opcional V1)
10. Caché <1h por clave `(user_id, first_review_id, last_review_id)` — spec §10.2.
11. Privacidad: iniciales en vez de nombre completo — spec §10.1.

---

## 4. Tests
- **Renderer (unit, sin red):** datos mock → PNG 1080×1350; no peta con valores extremos, delta 0, % graso ausente.
- **Selección de reviews:** 1 review → error; fechas invertidas → error; sin estimación IA ni coach → collage sin fila de % graso.
- **Endpoint (integración):** coach ajeno → 403; happy path → 200 + URL Drive válida. Reusar fixtures de coach/usuario de `tests/`.

---

## 5. Riesgos / precondiciones
- **Shared Drive de Workspace** creado y con la service-account añadida como miembro (precondición de infra; sin esto el equipo no ve las carpetas).
- Empaquetar **Open Sans `.ttf`** en la imagen/repo para Pillow.
- **Dependencia temporal**: escritura de `coach_body_fat_pct` que añadirá Carles. El fallback a IA cubre el interín sin bloquear la feature.
- **Bucket/permisos**: confirmar que el link de Drive es compartible (anyone-with-link) según política de privacidad del spec §10.

---

## 6. Desviaciones respecto al spec de producto
- **§13 / Apéndice B** decían "Firebase Storage" como fuente de fotos → es **incorrecto**: las fotos están en **S3** y su URL en la BD (tabla `reviews`). Firebase en `elmetodo_api` es solo FCM/push. (Ya corregido en el spec.)
- El spec asume Drive para guardar → **confirmado** (service-account + Shared Drive).
- El spec no especificaba la fuente del % graso → **resuelto** aquí (cadena coach → IA → sin dato).
