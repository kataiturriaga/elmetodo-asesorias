# Caso de estudio: Dashboard interno de coaches

**Producto:** El Metodo — herramienta interna para coaches
**Rol:** Product Designer + PM
**Estado:** En producción

---

## El problema

La ficha de cliente del dashboard estaba diseñada únicamente como herramienta de asignación y gestión: el coach la usaba para montar planes (revisiones, dieta, entreno) y editarlos. No existía ninguna capa de seguimiento del progreso del cliente ni de su adherencia.

Necesitábamos añadir información de progreso físico y de comportamiento que permitiera al coach evaluar cómo está yendo cada cliente, no solo gestionar qué tiene asignado.

---

## El contexto

El dashboard es la herramienta de trabajo diario del coach. Cada cliente tiene una ficha individual con:

- **Contenido principal** (pestañas): Revisiones / Dieta / Entreno — organizado por iteraciones
- **Panel lateral fijo**: Cuestionario del cliente (base para dieta y entreno) + Notas del coach
- **Header**: identidad del cliente, tipo de usuario, acciones principales (mandar cambios, siguiente cliente)

El dashboard tiene también un menú de sección "Mi Cartera" con vistas transversales: Activos, Rendimiento, Inactivos, Engagement, Notas.

---

## Decisiones clave

### 1. Qué datos nuevos había que incorporar

Identificamos dos grupos de información a añadir a la ficha:

**Progreso físico** — evolución del cuerpo del cliente, extraído de revisiones y entrenos:

- % graso por revisión
- Evolución del % graso (numérico + gráfico)
- Pesos y marcas registradas (numérico + gráfico)

**Adherencia / engagement** — comportamiento diario del cliente:

- Entrenos realizados
- Pasos diarios (numérico + gráfico)
- Tendencia de pasos + alertas de cambio de ritmo (posible señal de churn)

### 2. Separar progreso físico de adherencia

Los dos grupos tienen naturaleza, frecuencia y propósito distintos:


|            | Progreso físico       | Adherencia             |
| ---------- | --------------------- | ---------------------- |
| Origen     | Revisiones + entrenos | Actividad diaria (app) |
| Frecuencia | Mensual               | Diaria / semanal       |
| Pregunta   | ¿Está mejorando?      | ¿Está cumpliendo?      |


Mezclarlos en un mismo bloque hubiera creado ruido. Se trataron como capas independientes.

### 3. Dónde vive cada grupo

**Adherencia → fuera de la ficha individual.**
El dashboard ya tiene (o tendrá) una vista "Engagement" en el menú de Mi Cartera, donde el coach puede escanear todos sus clientes y detectar quién está en riesgo. Las alertas de pasos y entrenos viven ahí, no en la ficha. En la ficha pueden aparecer como contexto/detalle, pero sin función de alerta.

**Progreso físico → nueva pestaña "Progreso" en la ficha.**
Los datos de progreso físico requieren cruzar varias revisiones (el % graso de una sola revisión no dice nada; la tendencia de 4 revisiones sí). Esa capa de agregación no encaja dentro de la pestaña Revisiones ni dentro de Entreno — necesita su propio espacio.

Se decidió crear una pestaña "Progreso" que sea la **primera pestaña al abrir la ficha**, antes que Revisiones. El razonamiento: el coach entra a ver cómo está yendo el cliente antes de decidir si ajusta algo. La vista de progreso como punto de entrada refleja ese orden natural.

La pestaña Revisiones sigue existiendo y se enriquece con el % graso inline en cada tarjeta de revisión (dato puntual por revisión), mientras que la evolución agregada vive en Progreso.

### 4. Selector de revisiones: carousel con chips agrupados

El selector original mostraba todos los meses como pills planas al mismo nivel — con clientes de 12+ meses esto generaba 20+ elementos clicables sin jerarquía visual.

**El problema tenía dos capas:**
1. Demasiados elementos en horizontal — desbordan el espacio disponible
2. Dos dimensiones mezcladas (mes × tipo de revisión) sin distinción visual

**Solución final: grupos por mes con chips de tipo + carousel con flechas**

Cada mes tiene su propia cabecera ("Mes 6") con dos chips debajo: `[Mes]` (revisión mensual) y `[1/2]` (revisión quincenal). El contenedor clipa el contenido y navega con flechas. Por defecto se posiciona en el mes más reciente.

```
←  Mes 10  Mes 11  Mes 12  →          (el mes más reciente visible por defecto)
   [M][½]   [M][½]  [M][½]
```

- **Verde** = revisión seleccionada (activa en pantalla)
- **Outlined** = existe, no seleccionada
- El mes 1 no se ve porque el selector arranca al final — la flecha izquierda aparece al navegar hacia atrás

**Por qué funciona:**
La agrupación mes → tipo crea jerarquía visual sin añadir texto innecesario. El carousel con clipping evita el overflow sin recurrir a scroll horizontal dentro de un contenedor (que se siente atrapado). El coach casi siempre trabaja con los meses recientes, que son los que aparecen por defecto.

**Cards en grid en lugar de lista vertical**

Además del selector, las tarjetas de revisión pasaron de apilarse verticalmente a mostrarse en un grid de 3 columnas. Esto permite comparar varias revisiones en paralelo sin scroll, que es el caso de uso principal (el coach selecciona Mes 6M + Mes 5M + Mes 4½ y las ve lado a lado).

---

## Fases del proyecto

### Fase 1 — Arquitectura y reorganización ✅
Definición de qué información nueva había que incorporar, reorganización de lo existente con lo nuevo, nueva arquitectura de información y nuevo sidebar. Resultado: mapa claro de qué vive dónde antes de tocar ninguna pantalla.

### Fase 2 — Rediseño de la ficha de cliente 🔄 (en curso)
Rediseño de todas las partes de la ficha individual del cliente: header, tabs, selector de revisiones, cards de contenido, paneles laterales. Las decisiones de diseño de esta fase están documentadas arriba.

### Fase 3 — Tab "Progreso" 📋
Nueva pestaña dentro de la ficha del cliente. Contendrá:
- Evolución de peso y marcas registradas en entreno
- Pasos realizados
- Performance general del cliente

### Fase 4 — Nuevas páginas del dashboard 📋
Diseño de todas las páginas nuevas definidas en el sidebar (vistas transversales de Mi Cartera: Activos, Rendimiento, Inactivos, Engagement, Notas).

---

## El resultado

- En construcción

## Materiales

- Capturas: (añadir)
- Figma: (añadir si existe)

