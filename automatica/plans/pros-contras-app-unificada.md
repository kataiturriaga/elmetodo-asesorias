# Pros y contras: app unificada vs dos apps separadas

**Fecha:** 2026-05-04
**Contexto:** Decisión sobre si unificar `elmetodo_app` (automática) y el flujo de asesorías en una sola app o mantenerlos separados.

---

## App unificada

### Pros

- Un solo codebase, un solo pipeline de releases, un solo equipo trabajando en la misma base.
- Un usuario puede empezar en automática y migrar a asesorías sin cambiar de app ni perder su historial.
- Una sola entrada en el App Store — descubrimiento más simple.
- Actualizaciones de funcionalidad compartida (auth, perfil, contenido) se hacen una sola vez.

### Contras

- **El problema de identificación**: la app necesita saber desde el primer momento si el usuario que está entrando tiene una asesoría o no, para mostrarle el flujo correcto. El problema es que no hay una forma limpia de saberlo sin añadir fricción o compromisos:
  - Preguntarle al usuario ("¿has comprado una asesoría?") → para alguien que llega por un anuncio o recomendación, la pregunta es confusa: no saben qué es una asesoría, no entienden por qué se les pregunta, y puede generar dudas justo en el momento más crítico del registro.
  - Usar el email para identificarlos → falla con frecuencia porque el email que el cliente le da al coach al comprar no siempre coincide con el que usa para registrarse en la app.
  - Mandarles un enlace por WhatsApp que abra la app directamente → en iOS este tipo de enlaces no funcionan bien, especialmente si el usuario todavía no tiene la app instalada.
  - Pedirle a todos que verifiquen su número de teléfono al registrarse → añade un paso extra innecesario para los usuarios de automática, que son la mayoría.
- **Contaminación de producto**: cualquier elemento de UI relacionado con asesorías tiene que ser invisible para usuarios de automática. Requiere lógica de feature flags en toda la app.
- **Apple IAP (§11.1)**: en una app unificada, es más fácil cometer el error de mostrar superficies de pago de asesorías cerca de flujos de IAP. El riesgo de rechazo en App Store es real.
- **Complejidad de estado**: la app tiene que manejar `is_automated`, `tier`, `subscription_status`, `coach_id`, `pending_purchase_offer` — el estado del usuario es mucho más rico y difícil de razonar.
- **Velocidad de desarrollo**: cada nueva feature hay que preguntarse "¿aplica a automática, asesorías, o ambas?". El scope de cada tarea se complica.

---

## Dos apps separadas

### Pros

- El problema de routing desaparece: cada app sabe exactamente quién es su usuario desde el primer pantalla.
- Cero riesgo de exponer asesorías a usuarios de automática.
- Cada app puede evolucionar a su ritmo sin afectar a la otra.
- Apple IAP completamente aislado en la app de automática — sin riesgo de contaminación.
- UX de cada tipo de usuario puede estar optimizada sin compromisos.
- Los clientes de asesorías son una población pequeña y controlada — el coach les dice qué app instalar, no necesitan encontrarla solos.

### Contras

- Dos pipelines de release (CI/CD, TestFlight, App Store Connect, Play Store).
- Cambios en código compartido (auth, perfil, ajustes) se hacen dos veces.
- **Distribución iOS**: si la app de asesorías es pública en el App Store, usuarios de automática pueden descargarla por error. Si es privada (TestFlight), hay límite de 10.000 usuarios y los builds expiran cada 90 días.
- Un usuario que migra de automática a asesorías tiene que desinstalar e instalar otra app — fricción y pérdida de historial si no se gestiona bien.

---

## Resumen comparativo


| Criterio                                 | App unificada                  | Dos apps                    |
| ---------------------------------------- | ------------------------------ | --------------------------- |
| Complejidad técnica de routing           | Alta                           | Ninguna                     |
| Riesgo de exponer asesorías a automática | Alto (requiere gestión activa) | Ninguno                     |
| Mantenimiento a largo plazo              | Un codebase                    | Dos pipelines               |
| Distribución iOS                         | Simple (App Store)             | Compleja si es privada      |
| Migración automática → asesorías         | Transparente                   | Requiere cambio de app      |
| Riesgo Apple IAP                         | Requiere cuidado activo        | Aislado                     |
| Velocidad de desarrollo inicial          | Lenta (más casos a cubrir)     | Rápida (cada app es simple) |


---

## Conclusión

La app unificada es la solución correcta **a largo plazo**, cuando el volumen de clientes de asesorías sea alto y la migración automática → asesorías sea un caso de uso frecuente.

Para el momento actual, donde asesorías es un producto pequeño y controlado, dos apps separadas tienen menos complejidad técnica y menos riesgo de producto. El coste operativo de dos pipelines es real pero manejable.

**La pregunta clave para decidir:** ¿con qué frecuencia se espera que un usuario empiece en automática y luego compre asesorías? Si esa migración es rara, dos apps es más simple. Si es el funnel principal de ventas de asesorías, la app unificada vale la complejidad.