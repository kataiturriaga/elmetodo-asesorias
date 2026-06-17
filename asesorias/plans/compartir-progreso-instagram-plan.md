# Plan — Compartir progreso a Instagram (collage desde la app de Asesorías)

**Feature:** Compartir transformación (collage antes/después) a Instagram desde la app
**Producto:** App de Asesorías — `elmetodo_ff_asesorias` (FlutterFlow), end-user / cliente
**Repos de implementación:** `elmetodo_ff_asesorias` (app, principal) + `elmetodo_api` (cambio de datos puntual)
**Pantalla de entrada (Figma):** `App-Automatica` → nodo `4453-166774`
**Specs relacionados:** [`dashboard/generador-de-cambios.md`](../../dashboard/generador-de-cambios.md) (collage del coach, server-side) · [`asesorias/plans/generador-de-cambios-plan-tecnico.md`](generador-de-cambios-plan-tecnico.md)
**Estado:** Plan — pendiente de aprobar
**Última actualización:** 2026-06-17

---

> ⚠️ **La app está en refactor completo (Carles).** El código actual de `elmetodo_ff_asesorias` es el **antiguo** y va a reescribirse por completo — estructura, framework y nombres de clases/structs/endpoints **pueden cambiar todos**. Por eso este plan se redacta como **requisitos y contrato de datos**, no como bindings a archivos concretos. Las referencias al código actual (FlutterFlow, `ProgressReviewsStruct`, `ProgressCall`, custom widgets/actions, `pubspec`) quedan como **estado de partida / ejemplo**, marcadas con _(código antiguo — sujeto a refactor)_. Revalidar contra la nueva arquitectura antes de implementar y coordinar con Carles.

## 1. Qué es y en qué se diferencia del "Generador de Cambios" del coach

Ya existe el **Generador de Cambios** (coach, dashboard): el coach genera un collage del progreso de un cliente, renderizado **server-side con Pillow** y subido a **Google Drive**, con el cliente **anonimizado**.

Esta feature es **complementaria y distinta**: es **el propio usuario**, desde la **app de Asesorías**, quien genera el collage de **su** progreso y lo **comparte a Instagram**. Diferencias clave:

| Eje | Generador de Cambios (coach) | Compartir progreso (esta feature) |
|---|---|---|
| Actor | Coach | Usuario/cliente (dueño de los datos) |
| Superficie | Dashboard web | App móvil (FlutterFlow) |
| Render | Backend (Pillow) | **App (Flutter), preview en vivo** |
| Salida | Google Drive (link) | **Share sheet del sistema → Instagram/otras** |
| Privacidad | Anonimiza (iniciales) | Es su propio dato → puede mostrar su nombre |
| Personalización | One-tap, fijo | **Editable**: elige foto/pose y qué métricas mostrar |

> **Nota sobre consistencia visual:** los dos collages comparten el mismo lenguaje visual de marca (§4.3) pero **no es requisito** que sean idénticos: sirven audiencias distintas. Mantenerlos alineados es una decisión de marca (flywheel de UGC reconocible), no técnica.

---

## 2. Decisiones cerradas (acordadas con producto)

| Decisión | Resolución | Motivo |
|---|---|---|
| **Dónde se renderiza** | **En la app (Flutter)** | El usuario **edita/personaliza** su carta antes de postear → el preview WYSIWYG en vivo es muy superior. |
| **Cómo se comparte** | **Share sheet del sistema** (`share_plus`) | Una implementación cubre Instagram (Feed/Stories/DM) + WhatsApp + otras. Sin deep-links ni fallbacks de IG en V1. |
| **Patrón de implementación** | El collage se dibuja como **widget Flutter** capturable (`RepaintBoundary`); la captura + compartir como **acción** | Independiente del framework. _Si el refactor sigue en FlutterFlow_, mapea a Custom Widget + Custom Action (precedente: `custom_code/widgets/weight_graph_widget.dart`). _Si pasa a Flutter "puro"_, son un Widget y un service/método normales. |
| **Formato de imagen** | **1080×1350 px** (feed vertical IG) en V1 | Compatible con Feed; en Stories se muestra con margen (aceptable V1). Canvas 1080×1920 para Stories = opcional V2. |
| **Fuente del % graso** | `coach_body_fat_pct` **si existe → fallback** estimación IA (`ReviewBodyCompositionEstimate.point_estimate_bf_pct`) **→ fallback** ocultar fila | Mismo criterio que el plan del coach; funciona hoy (IA) y mañana (coach). |

---

## 3. Contrato de datos requerido (estado de partida)

Lo que el collage **necesita recibir** del cliente, y cómo está hoy. _La columna "estado de partida" refleja el **código antiguo** (FlutterFlow `ProgressReviewsStruct` / `ProgressCall`) y es solo referencia: el refactor puede renombrar todo, pero el **requisito** se mantiene._

| Dato necesario en el collage | Estado de partida (código antiguo) | Requisito para esta feature |
|---|---|---|
| Foto frontal 1ª y última review | ✅ Llega (`photoFront`, URL S3 pública) | El payload de reviews debe exponer la URL de foto frontal |
| Peso inicial / actual | ✅ Llega (`weight`) | Exponer peso por review |
| Fecha de cada review (→ días) | ✅ Llega (`reviewDate`) | Exponer fecha por review |
| **% graso inicial / actual** | ❌ **No llega** | **Exponer `body_fat_pct` por review** (cadena `coach_body_fat_pct` → estimación IA → `null`) |
| Fotos **lateral / espalda** (para elegir pose) | ❌ **No llega** (solo frontal) | Exponer `photo_back`/`photo_side` **solo si** se quiere selección de pose |

- En el código antiguo, el endpoint que sirve las reviews al cliente era **`ProgressCall`** → `ProgressReviewsStruct`. Tras el refactor habrá un equivalente; el contrato de campos de arriba es lo que importa.
- Para compartir hace falta una librería de share de ficheros (en el código antiguo **no** había `share_plus`; sí `path_provider`, `cached_network_image`, `image_picker`). Confirmar disponibilidad en el nuevo stack.

**Consecuencia (independiente del refactor):** esta feature **sí toca backend** — el `%graso` por review no se expone hoy y hay que añadirlo al payload de reviews. Conviene **coordinar este campo con Carles** para que entre en el contrato de la API nueva desde el principio.

---

## 4. Diseño (Figma)

Flujo de diseño según convención del repo (Figma Console MCP: `figma_execute` → screenshot → iterar). DS: **EMP DS Library** (memoria `figma_design_system`).

### 4.1 Punto de entrada — nodo `4453-166774`
- **Pendiente inspeccionar** ese nodo (el Desktop Bridge estaba desconectado al planear). Confirmar si es la pantalla de Progreso/Revisiones donde vive el CTA.
- Añadir CTA **"Compartir mi transformación"** (botón o card), visible solo si el usuario tiene **≥2 reviews con foto**.

### 4.2 Pantalla "Compartir progreso" (editor + preview)
Una pantalla con **preview en vivo** del collage arriba y controles debajo:
- **Selector de fotos**: para "Antes" y "Después", elegir entre las reviews disponibles y, si hay datos, entre frontal/lateral/espalda. Default: 1ª y última, frontal.
- **Toggles de métricas**: mostrar/ocultar Peso, % Graso, Días. Default: todo on (si hay dato).
- **Toggle nombre**: mostrar su nombre/inicial o no. Default según privacidad (ver §8).
- Botón primario **"Compartir"** → share sheet.

### 4.3 El collage (artefacto a compartir) — 1080×1350
Reutiliza el lenguaje visual ya especificado en [`generador-de-cambios.md` §5–6](../../dashboard/generador-de-cambios.md). Resumen de tokens:

- Fondo `#0B0F14` · Texto alto contraste `#F3F3F7` · Secundario `#8F8F97` · Acento progreso `#00EE00` · Negativo `#E64E4E` · Borde foto `#3C3E41` (2px) · Tipografía **Open Sans**.
- Layout: logo arriba; dos fotos lado a lado (Antes/Después, cover-crop); bloque de métricas (Peso inicial→actual, %Graso inicial→actual, deltas con color por signo); "N DÍAS DE TRANSFORMACIÓN" abajo.
- El **color del delta** depende del signo (verde mejora / rojo empeora / gris sin cambio).

### 4.4 Estados a diseñar
- **<2 reviews** → empty state ("Necesitas al menos 2 revisiones con foto").
- **Falta foto en una review** → mensaje específico.
- **Sin % graso** → ocultar fila de %graso (no error).
- **Generando** → spinner breve mientras se compone el PNG.
- **Compartido / cancelado** → feedback ligero.

---

## 5. Programación

### 5.1 Backend — `elmetodo_api` (cambio mínimo, alto reuso)
Enriquecer el payload que devuelve `ProgressCall` (la lista de reviews del usuario) con:

| Campo nuevo | Cómo se resuelve | Reuso |
|---|---|---|
| `body_fat_pct` por review | `Review.coach_body_fat_pct` → fallback última estimación IA exitosa → `null` | `ai_body_fat_repository` (latest successful estimate) ya existe, igual que en el plan del coach |
| `photo_back`, `photo_side` por review *(solo si se hace selección de pose)* | Columnas ya existentes en `Review` | — |

- **Sin render, sin Drive**: eso es de la feature del coach. Aquí backend solo expone datos.
- Reflejar los campos nuevos en `ProgressReviewsStruct` (FlutterFlow): `bodyFatPct` (double?), y opcionalmente `photoBack`/`photoSide`.

### 5.2 App — `elmetodo_ff_asesorias` (responsabilidades, no archivos)

> _Mapeo provisional al **código antiguo (FlutterFlow)**; tras el refactor cambian los nombres/ubicaciones pero las responsabilidades se mantienen. Si sigue en FlutterFlow → Custom Widget/Action; si pasa a Flutter "puro" → Widget + service._

| Pieza (responsabilidad) | Equiv. FlutterFlow _(antiguo)_ | Qué hace |
|---|---|---|
| Pantalla "Compartir progreso" | Page + Page State | Editor + preview; estado de selección (fotos, toggles); navega desde el CTA de §4.1 |
| Widget del collage | **Custom Widget** | Dibuja el collage data-driven (fotos vía caché de red, métricas, deltas, colores por signo, logo, Open Sans) dentro de un `RepaintBoundary` con `GlobalKey` |
| Acción capturar + compartir | **Custom Action** | `RepaintBoundary.toImage(pixelRatio)` → PNG nítido 1080×1350 → escribe a temp (`path_provider`) → share de fichero (`Share.shareXFiles`) |
| Selección 1ª/última + cálculo | Custom Function / lógica | De la lista de reviews: 1ª y última **con foto**, orden por fecha; calcula deltas y días |
| Dependencias | pubspec | Añadir lib de **share de ficheros** (`share_plus`); caché de imágenes; `path_provider` |
| Assets | — | Logo El Método y fuente Open Sans empaquetados en la app |

### 5.3 Captura PNG nítida (clave técnica)
El widget se diseña a **360×450 pt** (ratio 1080×1350) y se exporta con `pixelRatio = 3.0` → **1080×1350 px**. Cuidar:
- Que las fotos se carguen **completas** antes de capturar (precache con `cached_network_image` / esperar frame) para no exportar placeholders.
- `pixelRatio` consistente entre dispositivos (no usar el `devicePixelRatio` del device; fijarlo).
- Cover-crop de fotos a la caja sin deformar (`BoxFit.cover`).

---

## 6. Fases

1. **Diseño (Figma)** — inspeccionar nodo `4453-166774`; diseñar CTA, pantalla editor+preview, collage 1080×1350 y estados. Validar con screenshots.
2. **Backend** — añadir `body_fat_pct` (cadena coach→IA→null) al payload de `ProgressCall` (+ `photo_back`/`photo_side` si hay selección de pose). Tests.
3. **Datos en app** — actualizar `ProgressReviewsStruct`; helper de selección 1ª/última + cálculo de deltas/días; manejar `null` de %graso.
4. **Collage widget** — `ProgressCollageWidget` fiel al diseño (data-driven, colores por signo). Iterar contra Figma.
5. **Captura + compartir** — `captureAndShareCollage` (export PNG nítido + `share_plus`); precarga de fotos; estados loading/éxito/cancelado.
6. **Editor** — selección de fotos/pose y toggles de métricas con preview en vivo.
7. **Pulido** — empty states, edge cases, analytics, (opcional) canvas Stories 1080×1920.

---

## 7. Estados y edge cases

| Caso | Manejo |
|---|---|
| <2 reviews con foto | Ocultar CTA / empty state explicativo |
| Falta foto en una review elegida | Forzar elegir otra; mensaje específico |
| Sin % graso (ni coach ni IA) | Ocultar fila de %graso; no es error |
| Foto aún cargando al compartir | Bloquear "Compartir" hasta precarga completa |
| Subida de peso / empeora %graso | Delta en rojo `#E64E4E` con signo `+`/`-` correcto |
| Fechas inconsistentes (1ª > última) | Recalcular o mostrar error suave |
| Usuario cancela el share sheet | No-op; sin error |
| HEIC de iPhone en URL S3 | Confirmar que la app ya muestra esas fotos (mismo origen que Revisiones); si no, decodificar |

---

## 8. Privacidad
Es el **propio dato** del usuario → permisivo. Por defecto **sí** puede mostrar su nombre/inicial (toggle para ocultarlo). El collage es generado y compartido por el propio usuario; no se sube a ningún storage de la plataforma (vive en temp del dispositivo hasta compartir).

---

## 9. Riesgos / precondiciones
- **Refactor de la app en curso (Carles)**: el código actual es el antiguo y se reescribe entero. **Timing**: idealmente esta feature se diseña ahora (Figma + contrato de datos) y se implementa **sobre la base nueva**, no sobre la antigua, para no tirar trabajo. Coordinar con Carles para meter `body_fat_pct` (y, si aplica, `photo_back`/`photo_side`) en el contrato de la API nueva desde el principio.
- **Backend dependiente**: la feature **no sale solo con app**; requiere exponer `body_fat_pct` por review. Coordinar con quien mantiene ese endpoint.
- **`coach_body_fat_pct` hoy no se escribe** (lo añadirá Carles): el fallback a IA cubre el interín.
- **Selección de pose** (lateral/espalda) añade más cambio backend; si no es prioridad V1, limitar a **frontal** (lo único disponible hoy) y dejar pose para V2.
- **`share_plus`** en un proyecto FlutterFlow: validar que la dependencia custom compila en iOS/Android del build actual.
- **Nitidez del PNG**: el mayor riesgo técnico es exportar placeholders o baja resolución; mitigado con precarga + `pixelRatio` fijo.
- **Nodo `4453-166774` sin inspeccionar** (Desktop Bridge desconectado al planear): confirmar el punto de entrada real antes del diseño.

---

## 10. Preguntas abiertas
- [ ] **Timing vs. refactor**: ¿implementamos sobre la **base nueva** de Carles (recomendado, no tirar trabajo) o hay urgencia de sacarlo antes? ¿Para cuándo está la nueva arquitectura?
- [ ] ¿V1 solo con **foto frontal** (sin cambio extra de backend para fotos) o ya con **selección de pose**?
- [ ] ¿Mostrar nombre del usuario por defecto, o por defecto oculto?
- [ ] ¿Incluir **peso** además de %graso, o el collage es solo %graso + fotos? (la petición original menciona %graso; el spec del coach incluye peso).
- [ ] ¿Watermark/logo El Método siempre presente?
- [ ] ¿Canvas dedicado **1080×1920 Stories** en V1 o se deja para V2?
- [ ] ¿Tema solo oscuro de marca o también variante clara?

---

## 11. Métricas de éxito
- % de usuarios con ≥2 reviews que pulsan "Compartir mi transformación".
- Ratio de compartidos completados vs. iniciados (share sheet).
- Tiempo de generación del PNG (< 1s objetivo, render local).
- Tasa de error de captura (< 1%).
