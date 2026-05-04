# Dilema: Onboarding diferenciado asesorías vs automática

**Fecha:** 2026-05-04
**Contexto:** App unificada `elmetodo_app` — ver plan completo en `unified-app-manual-flow-2026-05-03.md`

---

## El problema

Para que la app unificada funcione, el servidor necesita saber **antes de que empiece el onboarding** si un usuario es de automática o de asesorías, porque los flujos son incompatibles:

- Usuario de **automática**: no debe ver nada relacionado con asesorías, hace su onboarding estándar.
- Usuario de **asesorías**: no debe pasar por el onboarding de automática (incluye pasos que no aplican, posiblemente IAP, etc.).

---

## Restricciones que eliminan las soluciones obvias

| Solución | Por qué no funciona |
|---|---|
| Preguntar "¿has comprado una asesoría?" | Añade un paso Y revela a usuarios de automática que el servicio de asesorías existe |
| Código de acceso en el signup | Misma razón: todos los usuarios ven el campo, aunque sea opcional |
| Deep link desde WhatsApp | WhatsApp usa su propio WebView y rompe Universal Links en iOS. Si el usuario no tiene la app instalada, el contexto del link se pierde en la instalación (iOS no tiene deferred deep links nativos) |
| Verificación de teléfono obligatoria en signup | Añade pasos innecesarios a todos los usuarios de automática |
| Coach asigna después del signup | El usuario de asesorías ya pasó por el onboarding equivocado |

---

## La contradicción central

Para enrutar al usuario al onboarding correcto, el servidor necesita una señal **antes** de que el onboarding comience. Esa señal solo puede venir de tres lugares:

```
1. El propio usuario   → cualquier input añade un paso o revela asesorías
2. El servidor         → necesita conectar la identidad de auth con la compra (¿cómo?)
3. Fuera de la app     → deep link (falla iOS) o flujo web previo (añade pasos fuera de la app)
```

No hay una cuarta opción.

---

## Alternativas evaluadas

### A. Match silencioso por email *(recomendada para arrancar)*

Después del auth (Google/Apple/email), el servidor busca silenciosamente en `asesorias_purchases` si existe una compra con ese email. Si hay match → onboarding manual directo. Si no → onboarding automático. El usuario no ve ningún paso extra.

**Pros:**
- Cero fricción para ambos tipos de usuario.
- No revela asesorías a nadie.
- Sin dependencias técnicas adicionales.

**Contras:**
- El email no es 100% confiable como clave de matching (ver plan principal §4):
  - Apple Private Relay → el email que ve la API ≠ el que registró el coach.
  - Cliente usa email distinto al que el coach anotó.
  - Typos del coach al registrar.
- Estos casos de falla requieren intervención manual del coach (asigna desde el dashboard).

**Conclusión:** Funciona para la gran mayoría de casos. Los edge cases se resuelven manualmente, lo cual es aceptable a la escala actual.

---

### B. Verificación web antes de instalar la app

El coach manda un link que abre una **página web** (no la app). El usuario verifica su teléfono vía OTP en el browser. Luego descarga la app. Al autenticarse, la app pregunta solo su número (sin OTP, ya verificado en web). El servidor conecta → onboarding correcto.

Los usuarios de automática nunca reciben ese link, nunca ven la pantalla de número.

**Pros:**
- Separación limpia: automática no toca ningún flujo de asesorías.
- Verificación de teléfono ocurre fuera de la app (no afecta el onboarding de automática).
- No depende de deep links.

**Contras:**
- Añade pasos **fuera** de la app (aunque solo para usuarios de asesorías).
- Requiere buildear un flujo web de verificación.
- Complejidad de conectar la sesión web con la identidad de auth de la app (¿cómo sabe el servidor que el "usuario web verificado" y el "usuario que se autenticó con Google" son la misma persona?).

---

### C. Coach asigna manualmente después del signup *(más simple, peor UX)*

El usuario de asesorías se registra como automático. El coach lo encuentra en el dashboard por nombre/email y lo asigna manualmente. El usuario recibe una notificación.

**Pros:** Cero complejidad técnica. No requiere ningún flujo nuevo en la app.

**Contras:** El usuario pasó por el onboarding equivocado. Experiencia rota hasta que el coach lo asigna.

---

## Decisión pendiente

La opción **A (match por email)** es la más pragmática para el estado actual del producto:

- Bajo volumen de clientes por coach → los edge cases son manejables manualmente.
- La tabla `asesorias_purchases` ya incluye `phone_e164` → cuando el volumen lo justifique, se agrega matching por teléfono sin rediseño.
- No bloquea el rollout de la app unificada.

**Pregunta abierta para el boss:** ¿Es aceptable que un porcentaje pequeño de usuarios de asesorías (Apple Private Relay, email distinto) tenga que ser asignado manualmente por el coach?
