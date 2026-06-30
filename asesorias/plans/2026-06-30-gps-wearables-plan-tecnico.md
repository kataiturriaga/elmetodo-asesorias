# Plan técnico — GPS y Wearables (asesorías V2)

> **Nota:** Este es un plan de valoración técnica, no un plan de implementación final. El objetivo es acotar complejidad, dependencias y estimaciones de tiempo antes de comprometer recursos. Los flujos de UI están fuera de scope (pendientes de Figma).


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

Lo que **no existe:**

- Paquete GPS (`geolocator` o similar)
- SDK / cliente OAuth para Strava (agregador de wearables — ver Subsistema 3)
- Modelo backend para sesiones de actividad con ruta GPS, ritmo y HR
- Webhooks de terceros en el backend (existe `app/api/routes/webhooks/` con `apple.py` y `google.py` como patrón a seguir)

---

## Arquitectura general propuesta

El núcleo compartido es un modelo **`WorkoutSession`** en el backend que unifica:
- Sesiones GPS grabadas en la app
- Actividades importadas de Strava (que a su vez agrega Garmin, Polar, Apple Watch, etc. — ver Subsistema 3)

Todos los datos fluyen hacia ese modelo. El cliente los ve en la app (historial de sesiones). El coach los ve en el dashboard (scope futuro).

```
App (GPS tracker)  ──POST /workout-sessions──►  WorkoutSession (backend)
Strava webhook     ──normaliza ───────────────►      "
(Garmin/Polar/Apple Watch → Strava → llegan por la vía de arriba)
```

---

## Subsistemas

El trabajo se divide en **4 subsistemas independientes**. Se recomienda implementarlos en este orden.

---

### Subsistema 0 — Backend: modelo WorkoutSession (prerequisito de todo)

**Estimación:** ~1 día

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

    # Ejecución guiada por plan (Runna-like) — nullable: solo cuando la sesión parte de un plan asignado
    plan_session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True, index=True)
    # [{step_index, step_type, target_distance_m, target_duration_s, target_speed_mps,
    #   actual_distance_m, actual_duration_s, actual_avg_speed_mps, on_target}]
    step_results    = Column(JSONB, nullable=True)

    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())
```

#### Endpoints

```
POST   /api/mobile/workout-sessions/        # Crear sesión (GPS grabado en app)
GET    /api/mobile/workout-sessions/        # Listar las del usuario (paginado)
GET    /api/mobile/workout-sessions/{id}    # Detalle de una sesión (incluye route_points)
DELETE /api/mobile/workout-sessions/{id}    # Borrar (solo el propio usuario)
PATCH  /api/mobile/workout-sessions/{id}/step-results  # Guardar desglose por paso al terminar
```

#### Decisiones de diseño

- `route_points` como JSONB: simple para V1. Una carrera de 60 min a 1 punto/seg = 3.600 puntos × ~60 bytes = ~216 KB por sesión. Aceptable. Si crece: mover a tabla separada o comprimir.
- `source` como string libre permite añadir nuevas plataformas sin migración.
- `external_id` + índice único `(user_id, source, external_id)` evita duplicados al importar de Strava.

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

**Estimación:** ~2 días
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

La convención del repo es `lib/v2/features/<nombre>/data|domain|presentation/`.

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
    StepContext? currentStep,  // null si sesión libre sin plan (ver Subsistema 4)
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

**Estimación:** ~2 días adicionales sobre Subsistema 1
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

### Subsistema 3 — Integración con Strava (agregador de wearables)

**Estimación:** ~2 días
**Proceso de aprobación:** Ninguno para desarrollo. Para producción: API Rate Limits, Terms of Service (no revender datos). Sin aprobación especial requerida.
**Documentación:** [developers.strava.com](https://developers.strava.com)

#### Por qué solo Strava (decisión de scope V1)

Strava **no es un wearable, es un agregador**: Garmin, Polar, Coros, Suunto, Wahoo, Apple Watch, Fitbit, etc. sincronizan automáticamente con Strava. Con **una sola integración** recibimos datos de actividad de cualquier dispositivo que el usuario ya tenga conectado a Strava, sin integrar cada fabricante por separado.

```
Garmin  ─┐
Polar   ─┤
Coros   ─┼──auto-sync──►  Strava  ──(1 integración)──►  El Método (WorkoutSession)
Apple W ─┤
Wahoo   ─┘
```

Esto evita el peor bloqueante del proyecto (la aprobación de la Garmin Health API, 2–8 semanas) y dos integraciones extra. **Lo que Strava-only NO cubre** y queda fuera de scope V1:
- Usuarios sin cuenta de Strava o que no han conectado su reloj a Strava.
- Métricas de salud pasiva (sueño, HRV, recuperación) — Strava no las expone; requerirían API directa de fabricante.

> La integración directa con Garmin/Polar (API de fabricante) está documentada como referencia en [`2026-06-30-gps-wearables-plan-tecnico-completo.md`](2026-06-30-gps-wearables-plan-tecnico-completo.md), por si en el futuro hace falta sueño/HRV o cubrir usuarios sin Strava.

#### Arquitectura general

```
Usuario en app ──► OAuth2 flow (webview) ──► Backend guarda tokens
Backend ──► Registra webhook en Strava
Strava ──► POST webhook al backend cuando hay actividad nueva
Backend ──► Llama API Strava, descarga datos, normaliza ──► WorkoutSession
```

El backend actúa como intermediario: guarda tokens OAuth, recibe webhooks, importa y normaliza. La app solo necesita:
1. Iniciar el flujo OAuth (abrir URL en webview)
2. Listar las actividades importadas (ya son `WorkoutSession` normales)

#### Archivos backend para la conexión OAuth

El modelo `WearableConnection` se mantiene genérico (campo `platform`) para no cerrar la puerta a futuras integraciones, aunque en V1 solo se use con `"strava"`.

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
    platform        = Column(String(50), nullable=False)  # V1: "strava" (genérico para el futuro)
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

#### Qué proporciona Strava
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

#### Flutter: pantalla de conexión

La app necesita una sola pantalla de configuración para conectar/desconectar Strava:

```
┌────────────────────────────────┐
│  Conectar dispositivos          │
├────────────────────────────────┤
│  [Strava]        ● Conectado   │
│  Desconectar                   │
│                                │
│  Conecta tu reloj (Garmin,     │
│  Polar, Apple Watch…) a Strava │
│  y tus entrenos aparecerán     │
│  aquí automáticamente.         │
└────────────────────────────────┘
```

Archivos Flutter:
- `lib/v2/features/wearables/presentation/screens/wearable_connections_screen.dart`
- `lib/v2/features/wearables/presentation/providers/wearable_providers.dart`
- `lib/v2/features/wearables/data/datasources/wearable_remote_datasource.dart`

El flujo OAuth se abre con `url_launcher` (ya en pubspec) o `webview_flutter` (ya en pubspec).

---

### Subsistema 4 — Ejecución guiada por plan (Runna-like)

**Estimación:** ~2 días Flutter + 0.5 día backend
**Prerequisito:** Subsistemas 0 y 1
**Objetivo:** Convertir la sesión GPS en la ejecución del plan asignado por el coach. El usuario sabe en qué paso del workout está, cuánto le queda y si va al ritmo objetivo. Al terminar, el sistema compara real vs. planificado paso a paso.

Sin este subsistema, el GPS funciona como Strava (grabación libre). Con él, funciona como Runna (ejecución guiada).

#### Qué añade al backend (extensión de Subsistema 0)

Los campos `plan_session_id` y `step_results` ya están en el modelo `WorkoutSession` (ver arriba). El backend **no ejecuta la lógica de pasos** — eso vive en el cliente. Solo persiste:
1. El vínculo con el plan (`plan_session_id`)
2. El desglose de resultados al terminar (`step_results` vía el PATCH endpoint)

Tests adicionales para el backend:
```python
def test_create_session_with_plan_session_id_stores_fk()
def test_patch_step_results_updates_field_correctly()
def test_patch_step_results_rejects_wrong_user()
```

#### Entidades Flutter nuevas

```dart
@freezed
class WorkoutStep with _$WorkoutStep {
  const factory WorkoutStep({
    required int index,
    required String type,           // "warmup"|"interval"|"recovery"|"cooldown"
    required StepTarget target,     // distancia O duración (mutuamente excluyentes)
    double? targetMinSpeedMps,      // límite inferior del ritmo objetivo
    double? targetMaxSpeedMps,      // límite superior del ritmo objetivo
  }) = _WorkoutStep;
}

@freezed
class StepTarget with _$StepTarget {
  const factory StepTarget.distance(double meters) = _DistanceTarget;
  const factory StepTarget.duration(Duration duration) = _DurationTarget;
}

@freezed
class StepExecutionResult with _$StepExecutionResult {
  const factory StepExecutionResult({
    required int stepIndex,
    required String stepType,
    required double actualDistanceM,
    required Duration actualDuration,
    required double actualAvgSpeedMps,
    required bool onTarget,
  }) = _StepExecutionResult;
}
```

#### `StepContext` — contexto del paso en tiempo real

Se usa en `LiveTrackingState.tracking.currentStep` (campo ya añadido en Subsistema 1):

```dart
@freezed
class StepContext with _$StepContext {
  const factory StepContext({
    required int stepIndex,
    required int totalSteps,
    required String stepType,         // "warmup"|"interval"|"recovery"|"cooldown"
    required double targetSpeedMps,   // punto medio del rango objetivo
    required double remainingInStep,  // metros (si target.distance) o segundos (si target.duration)
    required bool targetByDistance,   // true → metros, false → segundos
    required PaceStatus paceStatus,
  }) = _StepContext;
}

enum PaceStatus { onTarget, tooFast, tooSlow }
```

#### Lógica de avance automático entre pasos

El `GpsTrackingService` acepta una lista opcional de pasos. Si se pasa, activa la lógica de avance; si no, se comporta como sesión libre:

```dart
// En GpsTrackingService — extensión, no ruptura de la interfaz existente
Future<void> startTracking({int? planSessionId, List<WorkoutStep>? steps});

// Al recibir cada nuevo punto GPS:
void _onNewPoint(GpsPoint point) {
  _accumulate(point);

  if (_steps == null) return; // sesión libre, sin guía de pasos

  final step = _steps![_currentStepIndex];
  final completed = step.target.when(
    distance: (m) => _currentStepDistanceM >= m,
    duration: (d) => _currentStepElapsed >= d,
  );
  if (completed) _advanceToNextStep();

  _updatePaceStatus(point.speedMps, step);
  _emitState(); // LiveTrackingState.tracking con currentStep actualizado
}
```

Al avanzar de paso: vibración corta + (si hay audio cues activos) TTS con el nombre del siguiente paso.

#### Flujo completo de la sesión guiada

```
1. Usuario abre la sesión del día (plan asignado por el coach)
   → PlannedWorkoutProvider carga los steps desde la sesión del plan

2. Pantalla pre-sesión muestra el resumen del workout:
   "Warmup 10 min → 5× [400m a 4:30/km + 90s recuperación] → Cooldown 5 min"

3. Usuario pulsa "Iniciar"
   → GpsTrackingProvider.start(planSessionId: X, steps: [...])

4. Durante la carrera — la UI muestra:
   ┌─────────────────────────────┐
   │  Intervalo 2 / 5            │
   │  200m restantes             │
   │  4:42 /km  ← objetivo 4:30  │
   │  ● Demasiado lento          │
   ├─────────────────────────────┤
   │  1.8 km  ·  12:34           │
   └─────────────────────────────┘

5. Al completar un paso: vibración + avance automático al siguiente
   (sin que el usuario tenga que pulsar nada)

6. Usuario pulsa "Terminar" (o se completa el último paso)
   → GpsTrackingProvider.stop() recoge List<StepExecutionResult>
   → POST /api/mobile/workout-sessions/ con plan_session_id
   → PATCH /api/mobile/workout-sessions/{id}/step-results

7. Pantalla de resumen post-sesión:
   ┌──────────┬──────────┬──────────┬────────┐
   │ Paso     │ Objetivo │ Real     │        │
   ├──────────┼──────────┼──────────┼────────┤
   │ Warmup   │ 10 min   │ 10:12    │ ✅     │
   │ Inter. 1 │ 4:30/km  │ 4:28/km  │ ✅     │
   │ Inter. 2 │ 4:30/km  │ 4:51/km  │ ❌     │
   │ Recup. 1 │ 90 s     │ 92 s     │ ✅     │
   │ ...      │ ...      │ ...      │        │
   └──────────┴──────────┴──────────┴────────┘
```

#### Archivos Flutter nuevos / modificados

| Archivo | Acción |
|---------|--------|
| `domain/entities/workout_step.dart` | Nuevo: `WorkoutStep`, `StepTarget`, `StepExecutionResult` |
| `domain/entities/step_context.dart` | Nuevo: `StepContext`, `PaceStatus` |
| `data/services/gps_tracking_service.dart` | Modificar: añadir parámetro `steps?` en `startTracking`, lógica de avance |
| `presentation/providers/gps_tracking_provider.dart` | Modificar: propagar `StepContext` al emitir `LiveTrackingState.tracking` |
| `presentation/widgets/step_progress_overlay.dart` | Nuevo: overlay de paso actual (número, metros restantes, pace vs. target) |
| `presentation/screens/session_summary_screen.dart` | Nuevo: tabla paso a paso (target vs. real) |

#### Tests mínimos

```dart
test('avanza al siguiente paso cuando se alcanza la distancia objetivo')
test('avanza al siguiente paso cuando se agota el tiempo objetivo')
test('paceStatus es tooSlow cuando speed < targetMinSpeedMps')
test('paceStatus es onTarget cuando speed está dentro del rango')
test('step_results recoge todos los pasos al terminar')
test('sesión libre (sin steps) funciona sin StepContext en el estado')
```

---

## Resumen de estimaciones

| Subsistema | Qué incluye | Estimación | Dependencias |
|-----------|-------------|------------|--------------|
| **0 — Backend WorkoutSession** | Modelo, migraciones, 5 endpoints REST, tests | **~1 día** | — |
| **1 — GPS métricas (sin mapa)** | `geolocator`, permisos, GpsTrackingService, providers, guardar en backend | **~2 días** | Sub. 0 |
| **2 — GPS mapa de ruta** | `flutter_map`, RouteMapWidget, overlay métricas, historial con mapa | **~2 días** | Sub. 1 |
| **3 — Strava (agregador)** | OAuth2, webhook, normalización, pantalla conexión | **~2 días** | Sub. 0 |
| **4 — Ejecución guiada (Runna-like)** | `WorkoutStep` entities, step tracking en vivo, auto-avance entre pasos, comparativa post-sesión | **~2 días Flutter + 0.5 día backend** | Sub. 0 + 1 |


**GPS completo (Sub 0+1+2):** ~5 días
**Wearables vía Strava (Sub 0+3):** ~3 días, sin bloqueantes externos
**Todo (GPS + Strava):** ~7 días (~1.5 semanas)
**Todo con ejecución guiada (Sub 0+1+2+3+4):** ~9–10 días (~2 semanas)

> Garmin/Polar directos quedan fuera de scope V1 (cubiertos por Strava como agregador). Estimación de referencia en [`...-completo.md`](2026-06-30-gps-wearables-plan-tecnico-completo.md): +13–19 días + 2–8 semanas de aprobación Garmin.

---

## Casuísticas GPS — tres niveles de alcance

Hay dos ejes **independientes** que hay que no mezclar:

- **Eje 1: background tracking** (pantalla bloqueada) — **caro de retrofitear** si no se hace desde el principio, porque cambia el núcleo de cómo vive el tracking.
- **Eje 2: mapa** — **barato de añadir después**, es aditivo sobre los datos que ya guardas.

La consecuencia: **las tres casuísticas incluyen background desde el día 1**. Lo que varía entre ellas es únicamente cuándo y cómo entra el mapa. Un foreground-only sin background (wakelock + "no bloquees la pantalla") es una solución chapucera en cualquiera de los tres niveles y no se contempla.

> **Sobre el coste de tiles del mapa:** `flutter_map` es el widget, no el servidor. Para producción hay que contratar un proveedor de tiles (MapTiler, Stadia, etc.). Con ~4.000 usuarios y mapa solo en historial el coste es bajo (probablemente tier gratuito o ~$20–50/mes). Con mapa en vivo durante la carrera sube a ~$50–250/mes. El OSM público prohíbe uso comercial a escala.

---

### 🔴 Casuística 1 — Mínima (recomendada para V1)

Solo números: distancia, ritmo, duración. Sin mapa en ningún momento. La base técnica es completa (background + datos guardados), la UI es intencionalmente austera para validar primero si el usuario usa el GPS antes de invertir en el mapa.

**Incluye:**
- Background tracking capaz desde el día 1: foreground service Android + Background Mode iOS (pantalla bloqueada: sigue grabando)
- Métricas core en vivo durante la carrera: distancia, ritmo actual, tiempo transcurrido
- Pausa/reanudar manual
- Resumen post-sesión: distancia total, duración, ritmo medio, velocidad media
- Historial como lista de sesiones con números (sin mapa)
- **`route_points` guardados en backend igualmente** — la ruta no se muestra pero se almacena, así cuando se añada el mapa en fase 2 las sesiones antiguas ya tienen datos para pintar

**Deja fuera:** mapa (en ningún punto), splits por km, desnivel, FC, compartir, auto-pausa.

| | |
|---|---|
| **Estimación** | **~3 días** |
| **Coste tiles/mes** | **$0** — sin mapa, sin tiles |
| **Riesgo principal** | Review de Apple por `NSLocationAlways`; testing de batería en dispositivo real |

---

### 🟡 Casuística 2 — Intermedia

Añade el mapa al historial: después de terminar la carrera puedes ver tu ruta. Durante la carrera sigues viendo solo números (sin mapa en vivo).

**Incluye todo lo de la Mínima, más:**
- Mapa con ruta en el **resumen post-sesión** y en el **historial** (estático, no en vivo)
- `flutter_map` + tile provider (MapTiler/Stadia) con caché de tiles en dispositivo
- Marcadores de inicio/fin, polilínea de la ruta
- Splits básicos por km en el resumen

**Deja fuera:** mapa en vivo durante la carrera, desnivel, FC, compartir, auto-pausa.

| | |
|---|---|
| **Estimación** | **~5 días total** — +2 días sobre la Mínima |
| **Coste tiles/mes** | **Bajo** — mapa solo al revisar; probablemente tier gratis o ~$20–50/mes a 4k users |
| **Riesgo principal** | Coste de tiles si el volumen crece; elección del proveedor de tiles |

---

### 🟢 Casuística 3 — Completa

La experiencia tipo Strava: el mapa te sigue en vivo durante la carrera, ves la ruta trazándose en tiempo real.

**Incluye todo lo de la Intermedia, más:**
- Mapa en **vivo durante la carrera** (sigue la posición en tiempo real, tile streaming)
- Métricas enriquecidas: splits por km, desnivel acumulado, overlay de FC (si hay wearable)
- Auto-pausa (detecta paradas en semáforos)
- Tarjeta de compartir post-sesión (reutilizando `transformation_share_service` ya en el repo)

**Deja fuera:** nada relevante de GPS.

| | |
|---|---|
| **Estimación** | **~7 días total** — +2 días sobre la Intermedia |
| **Coste tiles/mes** | **~$50–250/mes** — el mapa en vivo es lo que dispara el consumo de tiles |
| **Riesgo principal** | Rendimiento del mapa en vivo (decimación de puntos, batería); coste de tiles |

---

### Comparativa

| | Mínima 🔴 | Intermedia 🟡 | Completa 🟢 |
|---|---|---|---|
| Background (pantalla bloqueada) | ✅ | ✅ | ✅ |
| Mapa en historial | ❌ | ✅ | ✅ |
| Mapa en vivo durante la carrera | ❌ | ❌ | ✅ |
| Splits / desnivel / FC | ❌ | splits básicos | ✅ |
| Auto-pausa | ❌ | ❌ | ✅ |
| Compartir | ❌ | ❌ | ✅ |
| `route_points` guardados | ✅ | ✅ | ✅ |
| **Estimación** | **~3 días** | **~5 días** | **~7 días** |
| **Coste tiles/mes** | $0 | ~tier gratis | ~$50–250 |

**Recomendación:** empezar por la **Mínima** — construye el background bien desde el día 1 (el único componente caro de retrofitear), guarda `route_points` en backend, y difiere el mapa. El salto de Mínima → Intermedia son solo 4–5 días adicionales y cero refactor.

---

## Riesgos y decisiones abiertas

### Riesgos técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Apple rechaza `NSLocationAlways` en App Store review | Media | Alto | Justificación clara en la review: "grabación de entrenamiento con pantalla bloqueada". Patrón establecido en apps de fitness (Strava, Nike Run Club). Preparar capturas del flujo de permisos |
| Android mata el foreground service en dispositivos agresivos (Xiaomi, Huawei) | Media | Alto | Testing en dispositivos problemáticos; guía en-app de exempciones de batería; usar `WorkManager` como fallback |
| Usuario no tiene Strava o no conectó su reloj → no llegan actividades | Media | Medio | El tracking GPS propio funciona sin Strava; Strava es complemento, no único origen. Comunicar en la pantalla de conexión |
| `route_points` JSONB crece en sesiones largas | Baja | Bajo | Decimación de puntos antes de guardar (1 punto cada 10m mínimo) |
| Rate limits de Strava (1.000 req/día) con muchos usuarios | Media | Medio | Procesar webhooks async con Celery; cachear |

### Decisiones abiertas que hay que tomar antes de implementar

1. **¿Qué casuística GPS para V1?** Recomendada: Mínima 🔴 (background desde día 1, mapa en fase 2).
2. **¿Dónde vive el feature en la arquitectura de Carles?** Feature `workout_session` en `lib/v2/features/workout_session/`; Carles decide si el tracking se integra en la pantalla de entreno existente o es flujo separado.
4. **Proveedor de tiles** (solo relevante si se entra en Casuística 2 o 3): MapTiler, Stadia Maps o Protomaps self-hosted. Decidir antes de implementar el mapa.
5. **Frecuencia de muestreo GPS:** 1 punto/segundo (estándar) vs. por distancia mínima (~5–10m, mejor batería). Impacta tamaño de `route_points` y duración de batería.
6. **¿Steps por distancia o por tiempo?** (Solo relevante si se implementa Sub. 4.) Los intervalos pueden medirse en metros (400m) o en duración (90s de recuperación). La entidad `StepTarget` soporta ambos; hay que confirmar cuál es el formato que usa el modelo de plan de El Metodo para los entrenos outdoor.
7. **¿Audio cues para la guía de pasos?** (Solo Sub. 4.) Al avanzar entre pasos, vibración es suficiente o se añade TTS (`flutter_tts`) con texto tipo "Intervalo completado, empieza la recuperación". TTS añade ~1 día de trabajo y un paquete adicional.

---

## Orden de implementación recomendado (asumiendo Casuística 1 Mínima para V1)

```
Día 1:        Subsistema 0 (backend WorkoutSession + decisión A/B con Carles)

Días 2–3:     Subsistema 1 (GPS tracking service con background desde el día 1)
              → UI mínima: pantalla de carrera con números + historial como lista

Paralelo con días 1–3:
              Registrar app en Strava Developer Portal

Días 4–5:     Subsistema 3 (Strava)

Días 5–7:     Subsistema 4 (ejecución guiada por plan — Runna-like)

Fase 2 (cuando el feedback lo confirme):
              Subsistema 2 (mapa en historial, Casuística 2) — ~2 días, cero refactor
              Casuística 3 (mapa en vivo) si se valida la necesidad — ~2 días adicionales
```
