# Plan técnico COMPLETO (multi-plataforma) — GPS y Wearables (asesorías V2)

> **Nota:** Este es un plan de valoración técnica, no un plan de implementación final. El objetivo es acotar complejidad, dependencias y estimaciones de tiempo antes de comprometer recursos. Los flujos de UI están fuera de scope (pendientes de Figma).

> **⚠️ Versión COMPLETA — referencia, no la recomendada.** Este documento contiene las integraciones directas con **Strava + Garmin + Polar**. Para V1 se decidió ir **solo con Strava** (que como agregador ya cubre Garmin/Polar/Coros/etc. vía auto-sync), evitando la aprobación de Garmin y dos integraciones extra. La versión recomendada y acotada está en [`2026-06-30-gps-wearables-plan-tecnico.md`](2026-06-30-gps-wearables-plan-tecnico.md). Este archivo se conserva por si en el futuro hace falta API directa de fabricante (p. ej. sueño/HRV, que Strava no expone).

**Repos afectados:** `elmetodo_ff_asesorias` (rama `feat/asesorias-v2-flow`) · `elmetodo_api`
**Coordinación necesaria:** Carles (app Flutter) para contratos de API y ubicación de nuevos features
**Última actualización:** 2026-06-30

---

## Estado de partida

Lo que ya existe y **no hay que construir:**

| Qué | Dónde |
|-----|-------|
| Paquete `health: ^13.2.1` (HealthKit iOS + Health Connect Android) | `pubspec.yaml` |
| `HealthService` — lee pasos, calorías, minutos activos, distancia diaria | `lib/v2/auto/core/services/health_service.dart` |
| `PedometerSyncService` + `PedometerData` backend | `lib/v2/auto/core/services/` + `app/models/pedometer.py` |
| `permission_handler: ^11.3.1` | `pubspec.yaml` |
| Patrón clean architecture: data/domain/presentation + Riverpod + Freezed + Dio | Todo `lib/v2/` |

Lo que **ya existe y solapa parcialmente** (⚠️ ver sección "Reconciliación con `activities`"):

| Qué | Dónde |
|-----|-------|
| Modelo `Activity` (logging manual: `activity_type`, `duration_minutes`, `calories_burned`, `distance_km`, `notes`, `activity_date`) | `app/models/activity.py` |
| Router de actividades manuales montado en **`prefix="/activities"`** → `/api/mobile/activities/` | `app/api/router.py:145` |
| Feature de actividades en la app (logging manual, `activity_log_item`, `pending_activities_service`) | `lib/v2/auto/features/activities/` |

Lo que **no existe:**

- Paquete GPS (`geolocator` o similar)
- SDKs / clientes OAuth para Strava, Garmin Connect, Polar
- Modelo backend para sesiones de actividad con ruta GPS, ritmo y HR (el `Activity` actual es solo logging manual, sin ruta ni tracking en vivo)
- Webhooks de terceros en el backend (existe `app/api/routes/webhooks/` con `apple.py` y `google.py` como patrón a seguir)

---

## ⚠️ Reconciliación con la feature `activities` existente (decisión de Carles)

**Antes de tocar el backend hay que resolver esto.** Ya existe una feature `activities` (modelo `Activity`, router en `/api/mobile/activities`, feature Flutter en `lib/v2/auto/features/activities/`) para **logging manual** de actividades. La sesión GPS + wearable es un concepto solapado pero distinto: tiene ruta, tracking en vivo, métricas de wearable y origen externo.

**El prefijo `/api/mobile/activities/` ya está ocupado** y el nombre `Activity` ya está tomado. Hay dos caminos:

### Opción A — Extender el modelo `Activity` existente

La sesión GPS es una `Activity` enriquecida: se añaden columnas opcionales al modelo y router actuales.

```python
# Columnas añadidas a Activity (todas nullable, no rompen el logging manual)
started_at      = Column(TIMESTAMP(timezone=True), nullable=True)
ended_at        = Column(TIMESTAMP(timezone=True), nullable=True)
source          = Column(String(50), nullable=True)   # "manual"|"gps_app"|"strava"|"garmin"|"polar"
external_id     = Column(String(200), nullable=True)
avg_speed_mps   = Column(Float, nullable=True)
max_speed_mps   = Column(Float, nullable=True)
avg_heart_rate  = Column(Integer, nullable=True)
max_heart_rate  = Column(Integer, nullable=True)
route_points    = Column(JSONB, nullable=True)
```

| Pros | Contras |
|------|---------|
| Sin duplicación de modelo ni de feature Flutter | Mezcla logging manual y tracking GPS en una tabla; campos `nullable` que solo aplican a unos registros |
| Reutiliza el router, repo y servicio de `activities` | El servicio de actividades crece y mezcla responsabilidades |
| Una sola lista de "actividades" en la app (manual + GPS + wearable juntas) | `distance_km` (existente) vs `distance_meters` (nuevo): hay que unificar unidad |

### Opción B — Modelo nuevo `WorkoutSession` con prefijo propio

Modelo y feature separados. El plan abajo está escrito asumiendo esta opción (renombrando `ActivitySession` → `WorkoutSession` y el prefijo a `/api/mobile/workout-sessions`).

```
POST   /api/mobile/workout-sessions/
GET    /api/mobile/workout-sessions/
GET    /api/mobile/workout-sessions/{id}
DELETE /api/mobile/workout-sessions/{id}
```

| Pros | Contras |
|------|---------|
| Separación conceptual limpia: logging manual ≠ tracking GPS/wearable | Dos features de "actividad" conviviendo → posible confusión de UX |
| Servicio/repo enfocados solo en GPS+wearable | Duplicación parcial de CRUD |
| Ciclo de vida y UI propios (tracking en vivo, ruta, conexiones OAuth) | Hay que decidir si la app muestra ambas listas juntas o separadas |

**Recomendación del plan:** Opción B (separación), porque el logging manual y el tracking GPS+wearable tienen UIs y ciclos de vida muy distintos. **Pero la decisión es de Carles** — controla la arquitectura de la app y la coherencia de UX. El resto del plan usa el nombre `WorkoutSession` / prefijo `/api/mobile/workout-sessions`; si se elige la Opción A, sustituir por `Activity` / `/api/mobile/activities` y convertir los archivos "Create" en "Modify" sobre los existentes.

---

## Arquitectura general propuesta

El núcleo compartido es un modelo **`WorkoutSession`** en el backend (nombre provisional — ver "Reconciliación con `activities`") que unifica:
- Sesiones GPS grabadas en la app
- Actividades importadas de Strava / Garmin / Polar

Todos los datos fluyen hacia ese modelo. El cliente los ve en la app (historial de sesiones). El coach los ve en el dashboard (scope futuro).

```
App (GPS tracker)  ──POST /workout-sessions──►  WorkoutSession (backend)
Strava webhook     ──normaliza ───────────────►      "
Garmin webhook     ──normaliza ───────────────►      "
Polar webhook      ──normaliza ───────────────►      "
```

---

## Subsistemas

El trabajo se divide en **4 subsistemas independientes**. Se recomienda implementarlos en este orden.

---

### Subsistema 0 — Backend: modelo WorkoutSession (prerequisito de todo)

**Estimación:** 2–3 días de backend
**⚠️ Depende de:** la decisión A/B de la sección "Reconciliación con `activities`". Lo de abajo asume **Opción B** (modelo nuevo). Si se elige A, estos "Create" pasan a ser "Modify" sobre los archivos de `activities`.

#### Qué se construye

Nuevo modelo SQLAlchemy y endpoints REST para registrar y consultar sesiones de entreno con GPS/wearable.

#### Archivos a crear/modificar (backend `elmetodo_api`)

| Archivo | Acción |
|---------|--------|
| `app/models/workout_session.py` | Nuevo modelo SQLAlchemy |
| `app/schemas/workout_session.py` | Pydantic schemas (request/response) |
| `app/repositories/workout_session_repository.py` | CRUD |
| `app/services/workout_session_service.py` | Lógica de negocio |
| `app/api/routes/mobile/workout_sessions.py` | Endpoints REST |
| `app/api/router.py` | Registrar router con `prefix="/workout-sessions"` (patrón de la línea 145) |
| `migrations/versions/xxxx_add_workout_session.py` | Migración (Alembic vive en `migrations/`, no `alembic/`) |
| `tests/services/test_workout_session_service.py` | Tests (la estructura de tests es `tests/services/`, no existe `tests/api/`) |

#### Modelo de datos

```python
class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Cuándo
    started_at      = Column(TIMESTAMP(timezone=True), nullable=False)
    ended_at        = Column(TIMESTAMP(timezone=True), nullable=False)
    duration_seconds = Column(Integer, nullable=False)       # ended_at - started_at

    # Qué
    activity_type   = Column(String(50), nullable=False)     # "running", "cycling", "walking"
    source          = Column(String(50), nullable=False)     # "gps_app", "strava", "garmin", "polar"
    external_id     = Column(String(200), nullable=True)     # ID en la plataforma de origen

    # Métricas principales
    distance_meters = Column(Float, nullable=True)
    avg_speed_mps   = Column(Float, nullable=True)           # m/s → calcular pace en cliente
    max_speed_mps   = Column(Float, nullable=True)
    calories        = Column(Integer, nullable=True)
    avg_heart_rate  = Column(Integer, nullable=True)         # bpm
    max_heart_rate  = Column(Integer, nullable=True)

    # Ruta GPS (solo para source="gps_app" y plataformas que la proporcionen)
    # Array de puntos: [{lat, lng, ts, accuracy_m, altitude_m}]
    # Almacenado como JSONB — simple para V1, suficiente para <1h de carrera (~3600 puntos a 1pt/s)
    route_points    = Column(JSONB, nullable=True)

    # Metadatos
    title           = Column(String(200), nullable=True)     # Nombre de la actividad (Strava lo tiene)
    notes           = Column(String(1000), nullable=True)
    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())
```

#### Endpoints

```
POST   /api/mobile/workout-sessions/        # Crear sesión (GPS grabado en app)
GET    /api/mobile/workout-sessions/        # Listar las del usuario (paginado)
GET    /api/mobile/workout-sessions/{id}    # Detalle de una sesión (incluye route_points)
DELETE /api/mobile/workout-sessions/{id}    # Borrar (solo el propio usuario)
```

#### Decisiones de diseño

- `route_points` como JSONB: simple para V1. Una carrera de 60 min a 1 punto/seg = 3.600 puntos × ~60 bytes = ~216 KB por sesión. Aceptable. Si crece: mover a tabla separada o comprimir.
- `source` como string libre permite añadir nuevas plataformas sin migración.
- `external_id` + índice único `(user_id, source, external_id)` evita duplicados al importar de Strava/Garmin.

#### Tests mínimos necesarios

```python
# tests/services/test_workout_session_service.py
def test_create_gps_session_returns_201()
def test_list_sessions_only_returns_own_user_data()
def test_get_session_includes_route_points()
def test_duplicate_external_id_returns_409()
def test_delete_session_removes_from_db()
```

---

### Subsistema 1 — Flutter GPS: métricas en tiempo real (sin mapa)

**Estimación:** 4–5 días de Flutter
**Prerequisito:** Subsistema 0

Esto es la versión mínima: grabar la sesión con GPS para calcular distancia, ritmo y velocidad sin mostrar mapa. Es el MVP más rápido de validar con usuarios.

#### Paquetes a añadir en `pubspec.yaml`

```yaml
geolocator: ^13.0.4        # GPS: posición actual, stream de posiciones, permisos
```

`geolocator` incluye su propio manejo de permisos iOS/Android. No necesitamos paquete de mapas en este subsistema.

#### Permisos a configurar

**iOS** (`ios/Runner/Info.plist`):
```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>Necesitamos tu ubicación para calcular la distancia y el ritmo durante tus entrenamientos.</string>
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>Para continuar grabando tu ruta si bloqueas la pantalla durante el entreno.</string>
```
Capabilities: `Background Modes → Location updates`

**Android** (`android/app/src/main/AndroidManifest.xml`):
```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
<!-- Para tracking con pantalla bloqueada: -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION"/>
```

> ⚠️ **Riesgo iOS:** Apple revisa con lupa el permiso "Always". Si la app solo necesita ubicación mientras está abierta, usar `WhenInUse` y documentarlo explícitamente en la review. Si el usuario bloquea la pantalla durante la carrera y la app va a segundo plano, se necesita `Always` + Background Mode — esto requiere justificación clara en el App Store.

#### Archivos Flutter (nuevo feature `lib/v2/features/workout_session/`)

La convención del repo es `lib/v2/features/<nombre>/data|domain|presentation/`. ⚠️ Ojo: ya existe `lib/v2/auto/features/activities/` (logging manual); este feature es distinto. Si se elige la Opción A de reconciliación, integrar aquí en vez de crear feature nuevo.

| Archivo | Responsabilidad |
|---------|----------------|
| `domain/entities/workout_session.dart` | Entidad Freezed (refleja backend) |
| `domain/entities/gps_point.dart` | `{lat, lng, timestamp, accuracy, altitude}` |
| `domain/entities/live_tracking_state.dart` | Estado en tiempo real durante la sesión |
| `domain/repositories/workout_session_repository.dart` | Interfaz abstracta |
| `data/models/workout_session_model.dart` | JSON ↔ entidad (Freezed + json_serializable) |
| `data/datasources/workout_session_remote_datasource.dart` | Llamadas Dio a `/api/mobile/workout-sessions/` |
| `data/repositories/workout_session_repository_impl.dart` | Impl del repository |
| `data/services/gps_tracking_service.dart` | Start/stop grabación, emite stream de `GpsPoint` |
| `presentation/providers/workout_session_providers.dart` | Riverpod: lista de sesiones, crear |
| `presentation/providers/gps_tracking_provider.dart` | Riverpod: estado de la sesión en curso |

#### `GpsTrackingService` — contrato clave

```dart
class GpsTrackingService {
  // Stream de puntos GPS mientras la sesión está activa
  Stream<GpsPoint> get pointStream;

  // Estado actual: parado / grabando / pausado
  TrackingStatus get status;

  // Inicia grabación. Lanza GpsPermissionException si no hay permisos.
  Future<void> startTracking();

  // Pausa sin perder los puntos grabados.
  Future<void> pauseTracking();

  // Reanuda.
  Future<void> resumeTracking();

  // Detiene y devuelve el resumen de la sesión.
  Future<CompletedSession> stopTracking();
}

class CompletedSession {
  final List<GpsPoint> points;
  final Duration duration;
  final double distanceMeters;
  final double avgSpeedMps;
  final double maxSpeedMps;
}
```

#### `GpsTrackingProvider` — estado Riverpod durante la sesión

```dart
@riverpod
class GpsTracking extends _$GpsTracking {
  @override
  LiveTrackingState build() => LiveTrackingState.idle();

  Future<void> start() async { ... }
  Future<void> pause() async { ... }
  Future<void> stop() async { ... }  // guarda en backend al terminar
}

@freezed
class LiveTrackingState with _$LiveTrackingState {
  const factory LiveTrackingState.idle() = _Idle;
  const factory LiveTrackingState.tracking({
    required Duration elapsed,
    required double distanceMeters,
    required double currentSpeedMps,
  }) = _Tracking;
  const factory LiveTrackingState.paused({
    required Duration elapsed,
    required double distanceMeters,
  }) = _Paused;
  const factory LiveTrackingState.saving() = _Saving;
  const factory LiveTrackingState.done({
    required WorkoutSession saved,
  }) = _Done;
  const factory LiveTrackingState.error(String message) = _Error;
}
```

#### Tracking en background (pantalla bloqueada)

En iOS: con Background Mode `Location updates` activado, `geolocator` sigue emitiendo mientras la app está en background. La app mantiene un timer y acumula puntos en memoria.

En Android: hay que levantar un `ForegroundService` (notificación persistente del tipo "Grabando entreno — 2.3 km · 5:32/km"). Sin esto, Android mata el proceso en ~1 min. El paquete `geolocator` no lo hace automáticamente — hay que implementarlo con un canal de plataforma o usando `flutter_background_service` (paquete adicional).

> ⚠️ **Complejidad añadida (Android background):** Si el usuario necesita bloquear la pantalla durante la carrera, el foreground service añade ~2 días de trabajo. Para MVP se puede omitir y mostrar un aviso: "mantén la pantalla activa durante el entreno".

#### Tests mínimos

```dart
// test/features/activity/gps_tracking_service_test.dart
test('stopTracking returns zero distance when no points recorded')
test('stopTracking calculates correct distance from two points')
test('pauseTracking stops emitting points')
test('resumeTracking resumes emitting points')
```

---

### Subsistema 2 — Flutter GPS: mapa de ruta

**Estimación:** 5–7 días adicionales sobre Subsistema 1
**Prerequisito:** Subsistema 1

Añade visualización de la ruta grabada sobre un mapa (vista en tiempo real durante la sesión + vista en el historial).

#### Decisión de paquete de mapas

| Opción | Pros | Contras |
|--------|------|---------|
| `google_maps_flutter` | Calidad, tiles suaves, documentación excelente | API Key obligatoria; billing si >25k MAU; restricciones de uso en apps privadas |
| `flutter_map` (OpenStreetMap) | Gratis, sin API key, open source | Tiles ligeramente peores; menos soporte de capas avanzadas |

**Recomendación:** `flutter_map` para V1. Sin coste, sin llaves que gestionar, suficiente para mostrar una polilínea. Si la UX no convence, migrar a Google Maps es refactor de UI, no de datos.

```yaml
# pubspec.yaml (añadir)
flutter_map: ^7.0.2
latlong2: ^0.9.1          # Tipo LatLng compatible con flutter_map
```

#### Qué se construye

1. **Widget `RouteMapWidget`** — muestra un `FlutterMap` con:
   - Tile layer de OpenStreetMap
   - `PolylineLayer` con los puntos de la ruta
   - Marcadores de inicio/fin
   - Auto-fit de bounds para encuadrar la ruta completa

2. **Uso en tiempo real** (durante la sesión activa): mapa que se actualiza con cada nuevo punto GPS. Simplemente pasar el stream de `GpsTrackingProvider` al widget.

3. **Uso en historial** (sesión ya grabada): cargar `route_points` desde el backend y mostrarlos estáticos.

#### Archivos adicionales

| Archivo | Responsabilidad |
|---------|----------------|
| `presentation/widgets/route_map_widget.dart` | Widget de mapa reutilizable |
| `presentation/widgets/live_metrics_overlay.dart` | Overlay con distancia/ritmo sobre el mapa |

#### Consideraciones de rendimiento

Con 3.600 puntos (60 min a 1/seg), renderizar la polilínea completa en cada frame es pesado. Estrategia: decimar los puntos para display (cada 5m de distancia real) y guardar la densidad completa solo en backend. Algoritmo Ramer-Douglas-Peucker disponible en Dart, o simplemente filtrar por distancia mínima entre puntos al acumular.

---

### Subsistema 3 — Integraciones con plataformas de wearables

**Estimación total: 15–25 días** (varía mucho por plataforma y proceso de aprobación)

Esta es la parte más compleja y con más incertidumbre externa. Se divide en 3 plataformas.

#### Arquitectura general (igual para las tres)

```
Usuario en app ──► OAuth2 flow (webview) ──► Backend guarda tokens
Backend ──► Registra webhook en plataforma
Plataforma ──► POST webhook al backend cuando hay actividad nueva
Backend ──► Llama API plataforma, descarga datos, normaliza ──► WorkoutSession
```

El backend actúa como intermediario: guarda tokens OAuth, recibe webhooks, importa y normaliza. La app solo necesita:
1. Iniciar el flujo OAuth (abrir URL en webview)
2. Listar las actividades importadas (ya son `WorkoutSession` normales)

#### Archivos backend compartidos para las tres integraciones

| Archivo | Responsabilidad |
|---------|----------------|
| `app/models/wearable_connection.py` | Tokens OAuth por usuario + plataforma |
| `app/schemas/wearable_connection.py` | Pydantic |
| `app/repositories/wearable_connection_repository.py` | CRUD de tokens |
| `app/api/routes/mobile/wearable_connections.py` | `/wearable-connections/{platform}/connect`, `/disconnect`, `/status` |

```python
class WearableConnection(Base):
    __tablename__ = "wearable_connections"

    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform        = Column(String(50), nullable=False)  # "strava"|"garmin"|"polar"
    access_token    = Column(Text, nullable=False)
    refresh_token   = Column(Text, nullable=True)
    token_expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    platform_user_id = Column(String(200), nullable=True)
    scope           = Column(String(500), nullable=True)
    connected_at    = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_sync_at    = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'platform', name='uq_wearable_user_platform'),
    )
```

---

#### Plataforma 3A — Strava

**Estimación:** 6–8 días
**Proceso de aprobación:** Ninguno para desarrollo. Para producción: API Rate Limits, Terms of Service (no revender datos). Sin aprobación especial requerida.
**Documentación:** [developers.strava.com](https://developers.strava.com)

##### Qué proporciona Strava
- Actividades: running, cycling, swimming, etc. con GPS route, HR, cadencia, potencia
- Webhook: push cuando el usuario crea/modifica una actividad
- Rate limit: 100 req/15min, 1000 req/día (gratuito)

##### Archivos backend

| Archivo | Responsabilidad |
|---------|----------------|
| `app/services/strava_service.py` | OAuth exchange, refresh, fetch activity |
| `app/api/routes/webhooks/strava.py` | `GET` (verificación) + `POST` (evento nuevo) |
| `app/tasks/strava_sync_task.py` | Celery task (opcional: si el webhook llega cuando el server está reiniciando) |

##### Flujo OAuth

```
1. App llama GET /wearable-connections/strava/auth-url
   Backend devuelve: https://www.strava.com/oauth/authorize?client_id=...&redirect_uri=...&scope=activity:read_all

2. App abre URL en webview
   Usuario autoriza → Strava redirige a: https://api.elmetodoapp.com/webhooks/strava/callback?code=XYZ

3. Backend hace POST https://www.strava.com/oauth/token con el code
   Guarda access_token + refresh_token en WearableConnection

4. Backend registra webhook de Strava (una sola vez por app):
   POST https://www.strava.com/api/v3/push_subscriptions
   → Strava enviará POST a /webhooks/strava cuando haya nueva actividad
```

##### Normalización Strava → WorkoutSession

```python
def strava_activity_to_session(strava_activity: dict, user_id: int) -> WorkoutSession:
    return WorkoutSession(
        user_id=user_id,
        started_at=parse_datetime(strava_activity["start_date"]),
        ended_at=parse_datetime(strava_activity["start_date"]) + timedelta(seconds=strava_activity["elapsed_time"]),
        duration_seconds=strava_activity["elapsed_time"],
        activity_type=map_strava_type(strava_activity["type"]),  # "Run"→"running"
        source="strava",
        external_id=str(strava_activity["id"]),
        distance_meters=strava_activity.get("distance"),
        avg_speed_mps=strava_activity.get("average_speed"),
        max_speed_mps=strava_activity.get("max_speed"),
        calories=strava_activity.get("calories"),
        avg_heart_rate=strava_activity.get("average_heartrate"),
        max_heart_rate=strava_activity.get("max_heartrate"),
        route_points=decode_polyline(strava_activity.get("map", {}).get("polyline")),
        title=strava_activity.get("name"),
    )
```

Strava devuelve rutas como polyline codificado (Google Polyline Algorithm) — hay que decodificarlo a `[{lat, lng}]`.

---

#### Plataforma 3B — Garmin Connect

**Estimación:** 8–12 días (desarrollo) + **tiempo de aprobación de API: 2–8 semanas** (variable, fuera de control)
**⚠️ Bloqueante mayor:** Garmin Health API requiere partnership y aprobación de Garmin. No se puede usar en producción sin que Garmin apruebe la aplicación. El proceso implica rellenar un formulario describiendo el caso de uso y esperar revisión manual.

**Alternativa inmediata:** Garmin sincroniza con Apple Health (iOS) y Google Fit/Health Connect (Android). Los datos ya llegan por el paquete `health` que está instalado. Si el usuario tiene un Garmin y sincroniza con el teléfono, los pasos y calorías ya fluyen. La ruta GPS y la frecuencia cardíaca **no** fluyen por esta vía.

##### Dos vías posibles

| Vía | Qué datos | Proceso | Tiempo |
|-----|-----------|---------|--------|
| Health/HealthKit (ya existe) | Pasos, calorías, distancia diaria | Ninguno | Ya funciona |
| Garmin Health API (directa) | Todo: HR, ruta, actividades completas, sueño, HRV | Aprobación Garmin | 2–8 semanas aprobación + 2 semanas dev |

**Recomendación:** Diferir la integración directa con Garmin hasta tener aprobación. Priorizar Strava (que Garmin también puede sincronizar automáticamente si el usuario lo configura).

##### Proceso si se decide implementar

1. Registrar cuenta de developer en [developer.garmin.com/health-api](https://developer.garmin.com/health-api)
2. Solicitar acceso a la API (formulario con descripción de la app y número de usuarios esperados)
3. Garmin aprueba → proporciona `Consumer Key` + `Consumer Secret`
4. Flujo OAuth 1.0a (Garmin usa OAuth 1.0, no 2.0 — requiere firma HMAC-SHA1)
5. Webhook: Garmin envía actividades en formato FIT (binario propietario) — necesita `fitdecode` Python para parsear

---

#### Plataforma 3C — Polar

**Estimación:** 5–7 días
**Proceso de aprobación:** Registro gratuito en [flow.polar.com/oauth2](https://flow.polar.com/oauth2). Acceso inmediato para desarrollo. Para producción: solicitud de "production access" (menos restrictivo que Garmin, típicamente en días).

##### Qué proporciona Polar AccessLink API v3
- Actividades con HR, GPS, calorías, distancia
- Sueño + recuperación (Recovery Pro, Nightly Recharge)
- Webhook: notificación push de nueva actividad
- OAuth 2.0 estándar

##### Normalización similar a Strava — adaptar activity endpoint response a `WorkoutSession`

---

#### Flutter: pantalla de conexión de wearables

Independientemente de la plataforma, la app necesita una sola pantalla de configuración:

```
┌────────────────────────────────┐
│  Conectar dispositivos          │
├────────────────────────────────┤
│  [Strava]        ● Conectado   │
│  Desconectar                   │
├────────────────────────────────┤
│  [Garmin]        ○ No conectado│
│  Conectar                      │
├────────────────────────────────┤
│  [Polar]         ○ No conectado│
│  Conectar                      │
└────────────────────────────────┘
```

Archivos Flutter:
- `lib/v2/features/wearables/presentation/screens/wearable_connections_screen.dart`
- `lib/v2/features/wearables/presentation/providers/wearable_providers.dart`
- `lib/v2/features/wearables/data/datasources/wearable_remote_datasource.dart`

El flujo OAuth se abre con `url_launcher` (ya en pubspec) o `webview_flutter` (ya en pubspec).

---

## Resumen de estimaciones

| Subsistema | Qué incluye | Estimación | Dependencias |
|-----------|-------------|------------|--------------|
| **0 — Backend WorkoutSession** | Modelo, migraciones, 4 endpoints REST, tests (+decisión A/B `activities`) | **2–3 días** | — |
| **1 — GPS métricas (sin mapa)** | `geolocator`, permisos, GpsTrackingService, providers, guardar en backend | **4–5 días** | Sub. 0 |
| **2 — GPS mapa de ruta** | `flutter_map`, RouteMapWidget, overlay métricas, historial con mapa | **+5–7 días** | Sub. 1 |
| **3A — Strava** | OAuth2, webhook, normalización, pantalla conexión | **6–8 días** | Sub. 0 |
| **3B — Garmin** | OAuth 1.0a, FIT parsing, webhook, normalización | **8–12 días** + **2–8 sem aprobación** | Sub. 0 |
| **3C — Polar** | OAuth2, webhook, normalización | **5–7 días** | Sub. 0 |

**GPS completo (Sub 0+1+2):** ~3 semanas
**Wearables completo (Sub 0+3A+3B+3C):** ~4–6 semanas de desarrollo + tiempo de aprobación Garmin

---

## Riesgos y decisiones abiertas

### Riesgos técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Apple rechaza permiso `NSLocationAlways` en App Store review | Media | Alto | Diseñar el MVP con `WhenInUse` (pantalla no se bloquea durante el entreno); añadir `Always` solo si la UX lo requiere y con justificación clara |
| Android mata el tracking en background sin foreground service | Alta | Alto | Para MVP: avisar al usuario que no bloquee pantalla. Para V2: añadir `flutter_background_service` (~2 días extra) |
| Garmin aprobación de API tarda más de lo esperado | Alta | Medio | Diferir Garmin; priorizar Strava (Garmin → Strava sync ya funciona para muchos usuarios) |
| `route_points` JSONB crece mucho con sesiones largas | Baja | Bajo | Decimación de puntos antes de guardar (filtrar a 1 punto cada 10m) |
| Rate limits de Strava (1000 req/día) con muchos usuarios | Media | Medio | Cachear respuestas, procesar webhooks async con Celery |

### Decisiones abiertas que hay que tomar antes de implementar

1. **¿Background tracking en el MVP?** Define si añadir el foreground service Android o advertir al usuario.
2. **¿`flutter_map` o `google_maps_flutter`?** Ver arriba.
3. **¿Qué plataformas de wearables en V1?** Recomendación: solo Strava. Garmin vía Strava sync ya cubre la mayoría de usuarios de Garmin.
4. **¿Extender `activities` o crear `WorkoutSession`? (Opción A vs B)** — decisión de Carles, ver sección "Reconciliación con `activities`". Bloquea el Subsistema 0.
5. **¿Dónde vive el feature en la arquitectura de Carles?** Asumiendo Opción B, el feature `workout_session` va en `lib/v2/features/workout_session/`, pero Carles debe decidir si el tracking activo se integra en la pantalla de entreno existente o es un flujo separado.
6. **Frecuencia de muestreo GPS:** 1 punto/segundo (estándar) vs. por distancia mínima (mejor batería). Impacta tamaño de `route_points`.

---

## Orden de implementación recomendado

```
Semana 1–2:   Subsistema 0 (backend) + Subsistema 1 (GPS métricas, sin mapa)
              → Validar con usuarios: ¿quieren el mapa o solo las métricas?

Semana 3:     Subsistema 2 (mapa) — solo si el feedback lo confirma

Paralelo con semanas 1–3:
              Solicitar acceso Garmin (empieza el reloj de aprobación)
              Registrar app en Strava Developer Portal

Semana 3–4:   Subsistema 3A (Strava)
Semana 5–6:   Subsistema 3C (Polar)
Cuando llegue aprobación Garmin: Subsistema 3B
```
