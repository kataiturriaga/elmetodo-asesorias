# FASE 2 — Arquitectura de Información

> Esta fase ocurre **antes de abrir Figma en modo diseño**. Su objetivo es definir la estructura completa de la app — qué pantallas existen, cómo se organizan, y por qué caminos se mueve el usuario — sin dibujar ni una sola pantalla.

---

## 01 — MAPA DE CONTENIDOS

### ¿Qué secciones existen en la app?

**Qué busca definir**
La lista exhaustiva de módulos funcionales de la app y cómo se agrupan. No es un sitemap de webs — es una vista de qué contenido necesita existir antes de decidir cómo organizarlo en navegación.

**Por qué importa**
Si no sabés qué existe, tomás decisiones de navegación sin información completa. El mapa de contenidos es la materia prima de la que sale la jerarquía de navegación. Sin él, diseñás pantallas que no tienen dónde vivir o descubrís en wireframes que te falta un módulo entero.

**Para tu rol**

- 🎨 Diseñadora → el mapa de contenidos te dice cuántas pantallas hay que diseñar. Es el scope real del trabajo visual.
- 📋 PM → cada módulo del mapa es una unidad de trabajo de desarrollo. Cuanto más claro esté, más fácil estimar el esfuerzo.
- ⭐ Para crecer → aprende a separar contenido de navegación. Puedes tener el mismo contenido organizado de tres formas diferentes. Primero definis qué existe; después decides dónde va.

**Mapa de contenidos — Asesorías V2 (tier coached)**

```
APP COACHED
│
├── ESTADO DEL PLAN (estados especiales)
│   ├── Login / Sign up
│   ├── Cuestionario de onboarding  ← nuevo
│   ├── Plan en creación (pantalla de espera post-cuestionario)
│   └── Plan asignado → acceso al resto de la app
│
├── HOME / HOY
│   ├── Cuenta pasos
│   ├── Estadisticas del ranking
│   └── Notificaciones / recordatorios / check-ins
│
├── ENTRENAMIENTO
│   ├── Plan de entrenamiento del ciclo actual (info secundaria)
│   ├── Sesión de hoy (ejercicios + series + reps) (info primaria)
│   ├── Calendario de sesiones completas (por definir)
│   ├── Peso anterior visible in-line por ejercicio  ← validado por encuesta (petición más concreta)
│   ├── Detalle de ejercicio (instrucciones + video)
│   ├── Alternativas de ejercicio  ← peticion encuesta (podria hablar con el coach para cambio, mencionar)
│   ├── Registro de sesión (peso levantado, RPE)
│   └── Gráficos de progreso (por ejercicio / global)
│
├── DIETA
│   ├── Plan de dieta del ciclo actual
│   ├── Comidas del día (desayuno, comida, cena, snacks)
│   ├── Recetas conectadas a las opciones
│   ├── Funcionalidad de imprimir dieta
│   ├── Equivalencias de alimentos  ← nuevo, petición más recurrente en encuesta
│   └── Lista de la compra (generada automáticamente)
│
├── CHECK-IN
│   ├── Aviso de check-in (notificación / recordatorio)
│   ├── Fotos de progreso (frontal, lateral, trasera)
│   ├── Peso actual
│   ├── Medidas corporales  ← nuevo, validado por encuesta, por validar con jorge
│   ├── Porcentaje graso  ← nuevo, validado por encuesta, por validar con jorge
│   ├── Sensaciones y emociones  ← nuevo, validado por encuesta, por validar con jorge
│   ├── Nota libre para el coach
│   └── Confirmación de envío
│
├── PROGRESO / PERFIL
│   ├── Evolución de peso
│   ├── Fotos de progreso (comparativa)
│   └── Historial de check-ins
│   └── Datos persolaes
│   ├── Conexión con wearable
│   ├── Preferencias de notificaciones
│   └── Info de suscripción / tier
│
└── COMUNIDAD / RANKING
    ├── Ranking (valorar si hacerla solo de pasos o introducir puntuacion de entreno)
    ├── Muro?

```

---

## 02 — JERARQUÍA DE NAVEGACIÓN

### ¿Cómo se organiza lo que existe?

**Qué busca definir**
La estructura de navegación principal: qué vive en el bottom nav, qué es pantalla de detalle, qué es un flujo modal. No todos los módulos del mapa de contenidos merecen un tab propio — hay que decidir qué es de acceso inmediato y qué está un nivel más abajo.

**Por qué importa**
La navegación define el peso cognitivo de la app. Cada tab del bottom nav es una promesa: "esto es tan importante que siempre está a un tap de distancia". Si ponés demasiadas cosas ahí, el usuario no sabe dónde ir. Si ponés muy pocas, ocultas funcionalidad que necesita.

**Para tu rol**

- 🎨 Diseñadora → la jerarquía de navegación es la columna vertebral de todos los wireframes. Definirla mal aquí genera rediseños en Fase 3.
- 📋 PM → cada decisión de navegación es una decisión de prioridad de producto. "¿Dieta merece tab propio?" es una pregunta de producto, no solo de diseño.
- ⭐ Para crecer → una buena heurística: el bottom nav refleja los JTBDs críticos. Si un JTBD es 🔴 Crítico, probablemente necesita tab propio.

**Principio guía para este proyecto**
El coached tiene poco tiempo y la cabeza llena (proto-persona). La navegación debe ser **inmediata y sin ambigüedad**: llega a la app y sabe al instante qué hacer hoy. Eso pesa más que la completitud o la elegancia.

**Propuesta de navegación — Asesorías V2**

```
BOTTOM NAV (5 tabs)
├── 🏠 Hoy          → Home con resumen del día
├── 💪 Entreno      → Plan de entrenamiento activo
├── 🥗 Dieta        → Plan de dieta + lista de la compra
├── 📊 Progreso     → Gráficos + historial de check-ins + perfil
└── 👤 Comunidad    → Pasos, entreno, muro
```

**El check-in no es tab** — es un flujo que se inicia desde una notificación o desde el tab Progreso. El coached no necesita acceso constante al check-in; solo cuando toca (cada 14 días).

**Niveles de profundidad**

```
Nivel 0 → Bottom nav (acceso inmediato)
Nivel 1 → Pantallas principales de cada tab
Nivel 2 → Detalle (ejercicio concreto, día de dieta, check-in histórico)
Modal   → Flujos temporales (registrar sesión, enviar check-in)
```

---

## 03 — FLUJOS DE USUARIO PRINCIPALES

### ¿Por qué caminos se mueve el usuario?

**Qué busca definir**
Los recorridos concretos que hace el usuario para completar sus JTBDs principales. Un flujo de usuario no es una lista de pantallas — es una secuencia con decisiones, estados vacíos, y puntos de error.

**Por qué importa**
Los flujos revelan complejidad oculta. Un flujo que parece simple ("ver el entreno de hoy") tiene más de una docena de estados posibles: primer uso, plan no asignado, sesión ya completada, wearable conectado vs no conectado. Mapearlos en papel evita descubrirlos en Figma o — peor — en desarrollo.

**Para tu rol**

- 🎨 Diseñadora → cada nodo del flujo es al menos una pantalla o un estado. El flujo te da el inventario real de pantallas a diseñar.
- 📋 PM → los flujos te permiten identificar dependencias técnicas antes de que el equipo de dev empiece.
- ⭐ Para crecer → cuando hagas un flujo, pregúntate siempre: *"¿qué pasa si esto falla?"* Los estados de error son tan importantes como el happy path.

---

### Flujo 1 — Onboarding y primer acceso

> JTBD: Sentir que Inazio me sigue / No complicarme la vida

```
Utiliza social login o email
    ↓
¿Usuario ya registrado?
    │
    ├── Sí → ¿Email pre-registrado por el coach en asesorías?
    │             │
    │             ├── No → Login → ¿Usuario automática?
    │             │                   ├── Sí → Flujo automática
    │             │                   └── No → Flujo asesorías (usuario coached existente,
    │             │                            ya tiene plan asignado → Home / Hoy ✅)
    │             └── Sí ↓
    │                    ↓
    └── No → ¿Email pre-registrado por el coach en asesorías?
                  │
                  ├── No → Flujo automática (sign up normal)
                  └── Sí ↓
                         ↓ (ambos caminos Sí convergen aquí)
                  ¿Fecha de inicio ≤ hoy?
                      ├── No → Login → Flujo automática (sin aviso, sin banner)
                      └── Sí ↓
                             ↓
                  Usuario hace cuestionario
                  (objetivo, historial, lesiones, disponibilidad, preferencias de dieta)
                             ↓
                  Pantalla de espera ("Tu plan se está creando")
                             ↓
                  [Coach valida y asigna dieta y entreno — proceso offline]
                             ↓
                  Notificación push: "Tu plan está listo"
                             ↓
                  Home / Hoy  ✅
```

**Decisiones tomadas:**

- El acceso al flujo coached lo controla el coach: añade el email del cliente y una fecha de inicio en el dashboard.
- Un usuario de automática que pasa a asesorías sigue viendo automática hasta la fecha de inicio, sin ningún aviso. Opción elegida por simplicidad — no genera expectativas rotas si el usuario abre la app antes de tiempo.
- El mismo flujo aplica tanto a usuarios nuevos (sign up) como a usuarios existentes de automática (login). El check de email es la única puerta.

**Dependencia del dashboard del coach:**
Para que este flujo funcione, el dashboard necesita una pantalla donde el coach pueda añadir un cliente con email + fecha de inicio. Sin eso, el flujo no tiene trigger. Tener en cuenta al diseñar el dashboard.

**Estados a diseñar:**

- Cuestionario de onboarding (multi-paso)
- Pantalla de espera post-cuestionario — puede durar días
- Notificación de "plan listo"

---

### Flujo 2 — Ver y registrar el entreno del día

> JTBD: Saber qué hacer hoy (🔴 Crítico)

```
Tab "Entreno"
    ↓
Pantalla principal
    ├── Sesión de hoy
    ├── Sesiones pasadas (semana / iteracion)
    └── Pesos de la sesion(es) de la semana pasada (modo numerico o grafico)
    └── Sensaciones de la sesion(es) pasadas (quizas incluirlo en el grafico)

Sesión de hoy (siguiente sesión)
    ├── Lista de ejercicios del día
    ├── Por ejercicio: series × reps × peso sugerido
    └── Peso anterior visible por ejercicio

         ↓
Tap en ejercicio → Detalle
    ├── Video / instrucciones
    └── Historial de pesos anteriores
         ↓
Registrar sesión (modal)
    ├── Peso levantado por serie
    ├── RPE (opcional)
    └── ¿Wearable conectado? → datos importados automáticamente
         ↓
Sesión completada ✅
    ↓
Feedback de cierre (micro-celebración)
    ↓
Entreno Hoy  (entreno marcado como completado)
```

**Estados a diseñar:**

- Sin wearable conectado (registro manual)
- Sesión ya completada (modo lectura)
- Ejercicio sin peso anterior (primera vez)

---

### Flujo 3 — Consultar el plan de dieta

> JTBD: Consultar mi plan de dieta (🔴 Crítico)

> Validado por encuesta: el 58% consulta la dieta antes de cada comida. La pantalla debe ser accesible y legible de un vistazo, mostrar información clara para rapida elección — es un flujo de consulta rápida, no de exploración.

```
Tab Dieta
    ↓
Vista de la comida actual 
    ├── Opcion 1 / 2 / 3 (con nombre de plato + imagen)
    ├── Macros totales de cada opcion (comida) (por decidir)
    ├── Opcion elegida (si/cuando hacemos la lista de la compra)
    ├── Recetas asociadas (a la comida)
    └── [acceso rápido a funcionalidad generacion de lista de la compra] 
         ↓
Tap en comida → Vista detallada
    ├── Ingredientes + cantidades + raciones
    ├── Macros por comida (por decidir)
    └── "Sustituir alimento" → Equivalencias 
         ↓
         Pantalla de equivalencias
             ├── Lista de alternativas para ese alimento
         ↓
Tap "Lista de la compra"
    ↓
Lista semanal generada a traves de elección de opciones
    ├── Selección de opciones
    ├── Agrupada por categoría
    └── Marcar como comprado (opcional)
```

**Estados a diseñar:**

- Dieta no asignada aún (estado vacío)
- Cambio de ciclo (dieta actualizada cada 4 semanas)
- Alimento sin equivalencias disponibles
- Lista de la compra vacía

---

### Flujo 4 — Check-in periódico

> JTBD: Hacer el check-in cuando toca (🟡 Importante)

```
Notificación push: "Es momento de tu check-in"
    ↓
Tap → App abre en flujo de check-in
    ↓
Pantalla de inicio de check-in
    ├── Recordatorio de qué incluir
    └── CTA "Empezar"
         ↓
Paso 1: Fotos de progreso
    ├── Foto frontal
    ├── Foto lateral
    └── Foto trasera (opcional)
         ↓
Paso 2: Métricas corporales  ← expandido por encuesta
    ├── Peso actual
    ├── Medidas corporales (cintura, cadera, pecho — opcional)
    └── Porcentaje graso (opcional)
         ↓
Paso 3: Sensaciones y emociones  ← nuevo, validado por encuesta
    ├── ¿Cómo te has sentido esta semana? (escala o selección)
    └── Nota libre para Inazio (opcional)
         ↓
Revisión y envío
    ↓
Confirmación: "Inazio lo recibirá y ajustará tu plan"  ✅
    ↓
Home / Hoy
```

**Estados a diseñar:**

- Check-in fuera de ciclo (enviado antes o después)
- Check-in ya enviado en este ciclo (modo lectura)
- Fallo de subida de fotos (reintento sin perder los datos ya introducidos)

---

### Flujo 5 — Ver progreso

> JTBD: Ver que mi inversión vale (🟡 Importante)

```
Tab Progreso
    ↓
Vista de resumen
    ├── Gráfico de peso (evolución)
    ├── Comparativa de fotos (antes / ahora)
    └── Resumen de check-ins completados
         ↓
Tap en gráfico → Detalle expandido
    ├── Filtro por período (4 semanas, 3 meses, total)
    └── Datos por check-in
         ↓
Tap en foto → Comparativa detallada
    └── Slider antes / después
```

**Estados a diseñar:**

- Sin datos aún (primer check-in no completado)
- Solo un check-in (sin suficiente data para gráfico)

---

## 04 — INVENTARIO DE PANTALLAS

### Lista completa de pantallas a diseñar

**Qué busca definir**
El número real de pantallas únicas que hay que diseñar. Es la base para estimar el esfuerzo de diseño en Fase 3 y 4.

**Por qué importa**
Sin inventario, el scope de Figma es infinito. Con inventario, podés priorizar: "de estas 40 pantallas, ¿cuáles son las 15 que debemos tener en el primer build?"


| ID  | Pantalla                                                        | Flujo      | Prioridad | Origen     |
| --- | --------------------------------------------------------------- | ---------- | --------- | ---------- |
| 01  | Cuestionario de onboarding (multi-paso)                         | Onboarding | 🔴 Alta   | Flujo real |
| 02  | Pantalla de espera — plan en creación                           | Onboarding | 🔴 Alta   | —          |
| 03  | Home / Hoy (resumen del día)                                    | Hoy        | 🔴 Alta   | —          |
| 04  | Pantalla de sesión de entreno (con peso anterior in-line)       | Entreno    | 🔴 Alta   | Encuesta   |
| 05  | Detalle de ejercicio                                            | Entreno    | 🔴 Alta   | —          |
| 06  | Modal de registro de sesión (peso + RPE)                        | Entreno    | 🔴 Alta   | Encuesta   |
| 07  | Sesión completada (cierre)                                      | Entreno    | 🔴 Alta   | —          |
| 08  | Vista del día — dieta                                           | Dieta      | 🔴 Alta   | —          |
| 09  | Inicio de check-in                                              | Check-in   | 🔴 Alta   | —          |
| 10  | Check-in paso 1: fotos                                          | Check-in   | 🔴 Alta   | —          |
| 11  | Check-in paso 2: métricas corporales (peso + medidas + % graso) | Check-in   | 🔴 Alta   | Encuesta   |
| 12  | Check-in paso 3: sensaciones y emociones                        | Check-in   | 🔴 Alta   | Encuesta   |
| 13  | Confirmación de check-in enviado                                | Check-in   | 🔴 Alta   | —          |
| 14  | Detalle de comida + acceso a equivalencias                      | Dieta      | 🔴 Alta   | Encuesta   |
| 15  | Pantalla de equivalencias de alimentos                          | Dieta      | 🔴 Alta   | Encuesta   |
| 16  | Tab Progreso — resumen                                          | Progreso   | 🟡 Media  | —          |
| 17  | Gráfico de peso expandido                                       | Progreso   | 🟡 Media  | —          |
| 18  | Comparativa de fotos                                            | Progreso   | 🟡 Media  | —          |
| 19  | Lista de la compra                                              | Dieta      | 🟡 Media  | —          |
| 20  | Plan de entrenamiento del ciclo                                 | Entreno    | 🟡 Media  | —          |
| 21  | Alternativas de ejercicio                                       | Entreno    | 🟡 Media  | Encuesta   |
| 22  | Historial de check-ins                                          | Progreso   | 🟡 Media  | —          |
| 23  | Perfil / Ajustes                                                | Perfil     | 🟡 Media  | —          |
| 24  | Conexión con wearable                                           | Perfil     | 🟡 Media  | —          |
| 25  | Preferencias de notificaciones                                  | Perfil     | 🟢 Baja   | —          |
| 26  | Nota libre para el coach (paso 4 del check-in)                  | Check-in   | 🟢 Baja   | —          |
| 27  | Intro slides (onboarding)                                       | Onboarding | 🟢 Baja   | —          |


**Total: 28 pantallas únicas** — 3 añadidas por encuesta (equivalencias, alternativas de ejercicio, sensaciones en check-in), 1 expandida en scope (métricas corporales). Los estados vacíos y de error se definen en Fase 3.

---

## 05 — ESTADOS ESPECIALES Y VACÍOS

### Pantallas que no son flujo pero son críticas

Los estados vacíos y de error son los que más se olvidan en diseño y los que más frustran al usuario cuando faltan.


| Estado                   | Dónde aparece      | Qué mostrar                                  |
| ------------------------ | ------------------ | -------------------------------------------- |
| Plan en creación         | Onboarding         | Pantalla de espera con expectativa de tiempo |
| Sin entreno hoy          | Home / Hoy         | Mensaje de descanso activo                   |
| Sesión ya completada     | Tab Entreno        | Modo lectura + celebración                   |
| Sin datos de progreso    | Tab Progreso       | Estado vacío motivador                       |
| Solo un check-in         | Gráfico de peso    | Explicación de por qué no hay gráfico aún    |
| Dieta no asignada        | Tab Dieta          | Estado de espera                             |
| Error de subida de fotos | Check-in           | Reintento sin perder datos                   |
| Wearable no conectado    | Registro de sesión | Registro manual habilitado                   |


---

## Checklist de salida — ¿Cuándo paso a Fase 3?

- Mapa de contenidos validado con el equipo técnico (¿existe todo esto en el sistema, o hay cosas que dependen de desarrollo nuevo?)
- Jerarquía de navegación acordada (5 tabs confirmados)
- Flujos principales revisados con el equipo — sin preguntas abiertas de lógica
- Inventario de pantallas priorizado — decidido qué entra en V2.0 y qué queda para V2.1
- Estados vacíos y de error listados
- Encuesta analizada e integrada en la arquitectura

