# Generador de Cambios

**Feature Name:** Generador de Cambios  
**Product Area:** Coach Dashboard  
**Status:** Especificación de Producto  
**Last Updated:** 2026-06-12

---

## 1. Visión

Permitir que los coaches generen una **comparativa visual del progreso** de sus clientes en una única imagen optimizada para compartir (redes sociales, WhatsApp, email). 

La imagen captura el antes/después de forma clara y motivante, mostrando métricas clave (peso, % graso) y el tiempo transcurrido entre revisiones.

---

## 2. Objetivo

Facilitar que los coaches documenten y compartan el progreso tangible de sus clientes de forma visual, mejorando:

- **Motivación del cliente** — visualizar cambios reales
- **Confianza en el proceso** — validación visual del programa
- **Marketing del coach** — contenido para redes sociales

---

## 3. Casos de Uso Principales

### Caso 1: Coach visualiza progreso de un cliente

**Actor:** Coach  
**Trigger:** Coach entra al perfil del cliente y quiere ver su progreso  
**Flujo:**

1. Coach abre perfil del cliente en el dashboard
2. Ve un botón **"Generar Comparativa"** o **"Ver Progreso"**
3. Hace click
4. El sistema genera la imagen y la guarda en Drive
5. Coach ve un modal/preview con opción de descargar o compartir

### Caso 2: Coach comparte progreso en redes sociales

**Actor:** Coach  
**Trigger:** Coach quiere mostrar éxito de cliente en Instagram  
**Flujo:**

1. Genera comparativa (caso 1)
2. Descarga imagen desde link en Drive
3. Sube a Instagram, con breve descripción del cliente (sin doxxing)

### Caso 3: Coach envía progreso al cliente

**Actor:** Coach  
**Trigger:** Coach quiere motivar al cliente con su progreso  
**Flujo:**

1. Genera comparativa
2. Obtiene link público de Drive
3. Envía vía WhatsApp/Email al cliente

---

## 4. Flujo de Usuario

```
Coach entra perfil cliente
         ↓
       [Botón "Generar Comparativa"]
         ↓
   Sistema consulta BD:
   - Primera review (inicial)
   - Última review (más reciente)
   - Fotos, peso, % graso
         ↓
   ¿Hay al menos 2 reviews?
   ├─ NO → Error: "Cliente debe tener al menos 2 revisiones"
   └─ SÍ → ¿Ambas tienen foto frontal?
      ├─ NO → Error: "Faltan fotos de una de las revisiones"
      └─ SÍ → Generar imagen → Subir a Drive
              → Mostrar modal con preview + link
```

---

## 5. Contenido del Collage

### 5.1 Elementos visuales obligatorios


| Elemento                      | Contenido                        | Notas                                               |
| ----------------------------- | -------------------------------- | --------------------------------------------------- |
| **Foto 1 (Antes)**            | Foto frontal review inicial      | Tamaño: ver layout                                  |
| **Foto 2 (Después)**          | Foto frontal review más reciente | Tamaño: ver layout                                  |
| **Logo**                      | Logo de El Método                | Pequeño, arriba                                     |
| **Peso inicial**              | Ej: "89.5 kg"                    | Con label "Peso Inicial"                            |
| **Peso actual**               | Ej: "76.2 kg"                    | Con label "Peso Actual"                             |
| **Cambio de peso**            | Ej: "-13.3 kg"                   | En color de progreso (verde)                        |
| **% Graso inicial**           | Ej: "32%."                       | Con label "% Graso Inicial"                         |
| **% Graso actual**            | Ej: "22%"                        | Con label "% Graso Actual"                          |
| **Cambio de graso**           | Ej: "-10%"                       | En color de progreso (verde)                        |
| **Tiempo transcurrido**       | Ej: "142 días"                   | Centrado abajo                                      |
| **Nombre cliente (opcional)** | Ej: "Juan P."                    | Si el coach lo permite (sin último nombre completo) |


### 5.2 Elementos que NO se muestran

- Datos personales completos del cliente (privacidad)
- Redes sociales
- Email o teléfono
- Histórico completo de cambios (solo inicial vs actual)

---

## 6. Especificaciones Visuales

### 6.1 Dimensiones y layout

**Tamaño final:** 1080 × 1350 px (Instagram feed vertical)

**Layout:** Dos columnas, con datos superpuestos

```
┌─────────────────────────────────────┐
│         Logo El Método              │  ← 60px altura, arriba centro
├─────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐   │
│  │   Foto 1    │  │   Foto 2    │   │
│  │ (Antes)     │  │ (Después)   │   │
│  │             │  │             │   │
│  │ 440 x 720   │  │ 440 x 720   │   │  ← Lado a lado
│  │             │  │             │   │
│  │             │  │             │   │
│  └─────────────┘  └─────────────┘   │
│                                     │
│  Padding: 20px entre fotos          │
├─────────────────────────────────────┤
│                                     │
│   Peso Inicial        Peso Actual   │
│     89.5 kg   →          76.2 kg    │
│                                     │
│   % Graso Inicial    % Graso Actual │
│      32%       →          22%       │
│                                     │
│      Cambio: -13.3 kg | -10%        │
│                                     │
│       142 DÍAS DE TRANSFORMACIÓN    │
│                                     │
└─────────────────────────────────────┘
```

### 6.2 Tipografía


| Elemento                           | Estilo Design System | Peso | Tamaño    | Color                      |
| ---------------------------------- | -------------------- | ---- | --------- | -------------------------- |
| Logo                               | -                    | -    | ~60px alt | -                          |
| "Peso Inicial" / "% Graso Inicial" | `Body/sm`            | 400  | 14px      | `#8F8F97` (lowlowContrast) |
| "89.5 kg" / "32%"                  | `Titles/H1-stats`    | 700  | 24px      | `#F3F3F7` (highContrast)   |
| Flecha "→"                         | `Body/md`            | 700  | 16px      | `#00EE00` (activo)         |
| "Cambio: -13.3 kg | -10%"          | `Body/md-bold`       | 700  | 16px      | `#00EE00` (activo)         |
| "142 DÍAS DE TRANSFORMACIÓN"       | `Titles/H1-sección`  | 700  | 28px      | `#00EE00` (activo)         |


### 6.3 Colores

**Paleta:**

- **Fondo:** `#0B0F14` (negro-profundo, full bleed)
- **Fotos frontal/back:** Bordes sutiles `#3C3E41` (Stroke-Divider), 2px
- **Texto primario:** `#F3F3F7` (highContrast)
- **Texto secundario:** `#8F8F97` (lowlowContrast)
- **Accent (cambios positivos):** `#00EE00` (activo/verde marca)
- **Accent (cambios negativos):** `#E64E4E` (destructive, si el cliente subió de peso)

### 6.4 Espacios y paddings


| Área                  | Padding                        | Notas              |
| --------------------- | ------------------------------ | ------------------ |
| Canvas general        | 40px (arriba, abajo, izq, der) | Margen externo     |
| Entre fotos           | 20px                           | Espacio horizontal |
| Sección de datos      | 30px (arriba), 20px (izq/der)  | Bajo las fotos     |
| Entre líneas de datos | 16px                           | Vertical spacing   |


### 6.5 Efectos (sutiles)

- **Fotos:** Border `2px #3C3E41`, sin sombra (limpio)
- **Texto de cambio (verde):** Leve glow opcional `box-shadow: 0 0 2px #00EE00`
- **Logo:** Sin efectos, simple

---

## 7. Estados y Variantes

### 7.1 Estado exitoso

Imagen generada correctamente, datos completos, foto de ambas revisiones.

**Mostrar:**

- Preview de la imagen en modal
- Botones: "Descargar", "Copiar link", "Cerrar"

### 7.2 Estado: Cliente sin segunda review

**Condición:** Cliente solo tiene 1 revisión  
**Mostrar:** Mensaje de error  

```
❌ No hay suficientes datos
Este cliente necesita al menos 2 revisiones 
para generar una comparativa de progreso.
```

### 7.3 Estado: Cliente con reviews pero sin foto frontal

**Condición:** Una o ambas reviews no tienen foto frontal  
**Mostrar:** Mensaje de error específico

```
❌ Foto faltante
La revisión inicial/actual no tiene foto frontal.
Pide al cliente que suba la foto o captura una manualmente.
```

### 7.4 Estado: Cliente con datos incompletos

**Condición:** Una review no tiene peso o % graso  
**Mostrar:** Advertencia + usar último valor conocido o "N/A"

```
⚠️ Datos parciales
Usaremos los datos disponibles. Verifica los valores.
```

### 7.5 Variante: Cambio negativo (subida de peso)

Si el cliente subió de peso:

- El número en rojo: `#E64E4E`
- Cambio con "+": Ej: "+5.2 kg"
- Verde solo si hay cambio positivo en % graso

---

## 8. Edge Cases


| Caso                                                        | Manejo                                                           |
| ----------------------------------------------------------- | ---------------------------------------------------------------- |
| Cliente con datos extremos (Ej: 150kg → 50kg en 30 días)    | Mostrar datos tal cual — validación está en BD                   |
| Cliente sin nombre completo                                 | Mostrar solo iniciales "J.P." o "Coach [ID]"                     |
| Foto muy borrosa o de mala calidad                          | Mostrar como está — coach debe validar antes de generar          |
| Foto inicial es más nueva que la final (data inconsistency) | Error: "Datos inconsistentes. Contacta a soporte."               |
| Collage tarda >5s en generarse                              | Mostrar loading spinner, mensaje: "Generando tu comparativa..."  |
| Error al subir a Drive                                      | Fallback: Permitir descargar imagen localmente sin subir a Drive |


---

## 9. Interacción Post-Generación

### Modal de resultado exitoso

```
┌─────────────────────────────────────┐
│        ✓ Comparativa Generada       │
├─────────────────────────────────────┤
│                                     │
│    [Preview de imagen 400x500px]    │
│                                     │
├─────────────────────────────────────┤
│ Enlace: https://drive.google.com/.. │
│ [📋 Copiar enlace]                  │
│                                     │
│ [⬇️ Descargar]  [Cerrar]            │
└─────────────────────────────────────┘
```

### Acciones disponibles:

1. **Copiar enlace** → Link público de Drive al portapapeles
2. **Descargar** → Descarga directa de la imagen (PNG o JPG)
3. **Cerrar** → Cierra el modal

---

## 10. Restricciones y Consideraciones

### 10.1 Privacidad

- No mostrar nombre completo del cliente
- Usar iniciales o generar alias ("Cliente #123")
- Las imágenes en Drive son privadas al coach (carpeta personal)

### 10.2 Performance

- Generación max 10 segundos (incluye descarga de fotos + render + upload)
- Caché: Si el coach genera 2 veces la misma comparativa en 1 hora, reutilizar imagen

### 10.3 Almacenamiento

- Carpeta Drive coach: `/El Método/Comparativas de Progreso/[Fecha]/`
- Nombrado: `{nombre_cliente}_{fecha}.png`
- Retention: 1 año (borrar automáticamente después)

### 10.4 Acceso

- Solo el coach propietario ve el link
- Imagen es compartible vía link, pero no listable en Drive (solo coach y quien tenga link)

---

## 11. Variaciones Futuras (Nice-to-have)

Estos NO se incluyen en V1, pero son ideas para después:

- [ ] Múltiples poses (frontal, lateral, espalda) en un collage
- [ ] Comparativa de más de 2 revisiones (timeline visual)
- [ ] Exportar como video / GIF animado
- [ ] Personalizar colores del collage (brand del coach)
- [ ] Incluir otros datos (circunferencia cintura, fuerza, etc.)
- [ ] Plantillas de diseño diferentes (minimalista, colorida, etc.)
- [ ] Compartir directo a Instagram / TikTok

---

## 12. Métricas de Éxito


| Métrica                                                    | Target   | Notas         |
| ---------------------------------------------------------- | -------- | ------------- |
| % coaches que generan al menos 1 comparativa en primer mes | 40%      | Adopción      |
| Tiempo promedio de generación                              | < 5s     | Performance   |
| Tasa de error en generación                                | < 2%     | Confiabilidad |
| Comparativas compartidas (vía link Click-through)          | Trackear | Engagement    |
| Descargas de imagen                                        | Trackear | Uso           |


---

## 13. Implementación (High-level)

### Endpoint

```
POST /api/dashboard/coach/me/users/{user_id}/progress-collage
Response:
{
  "success": true,
  "image_url": "https://drive.google.com/...",
  "download_url": "https://lh3.googleusercontent.com/...",
  "generated_at": "2026-06-12T14:30:00Z",
  "expires_at": "2027-06-12T14:30:00Z"
}
```

### Backend tasks

1. Obtener 1ª y última review del usuario
2. Descargar fotos desde **S3** (las URLs están en la BD propia: `reviews.photo_front` / `photo_back` / `photo_side`). Reutilizar el patrón de fetch de `app/services/photo_prepare_service.py`.
3. Generar imagen con Pillow (Python)
4. Subir a Google Drive (carpeta coach)
5. Retornar URLs

> **Nota de almacenamiento:** las fotos de review NO están en Firebase. El binario vive en **AWS S3** (región `eu-west-3`, URLs públicas) y la BD propia (tabla `reviews`) solo guarda la URL. En `elmetodo_api`, Firebase se usa únicamente para push (FCM) y GA4, no para storage de imágenes.

### Frontend

- Botón en perfil del cliente (prominente)
- Modal con preview y opciones
- Loading state mientras se genera

---

## Apéndice A: Ejemplos de diseño (texto)

### Ejemplo 1: Éxito positivo (pérdida de peso)

```
┌─────────────────────────────────────┐
│    🏋️ EL MÉTODO                      │
├─────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐   │
│  │             │  │             │   │
│  │  Foto 1     │  │  Foto 2     │   │
│  │  (Inicial)  │  │  (Actual)   │   │
│  │             │  │             │   │
│  └─────────────┘  └─────────────┘   │
│                                     │
│  Peso Inicial        Peso Actual    │
│    89.5 kg    →        76.2 kg      │
│                                     │
│  % Graso Inicial    % Graso Actual  │
│     32%       →         22%         │
│                                     │
│      ✓ -13.3 kg  |  ✓ -10%          │
│                                     │
│    142 DÍAS DE TRANSFORMACIÓN       │
└─────────────────────────────────────┘
```

### Ejemplo 2: Cliente sin cambio (mantenimiento)

```
[Ídem, pero]
│      = 0 kg   |  ✓ -2%              │
│  "Mantenimiento de peso, mejora composición"
```

### Ejemplo 3: Cambio negativo (subida)

```
[Ídem, pero con color rojo para el número]
│      + 5.2 kg  |  - 3%               │
│  "Revisión necesaria. Habla con el cliente."
```

---

## Apéndice B: Flujo técnico simplificado

```
[Coach] → [Click Botón]
           ↓
         [Validar que user_id pertenece a coach]
           ↓
         [Obtener review_inicial y review_final]
           ↓
         [¿Ambas tienen foto_frontal?]
         ├─ NO → Error 400
         └─ SÍ → [Descargar foto 1 y foto 2 desde S3 (URLs en BD: reviews.photo_front)]
                   ↓
                [Generar imagen con Pillow]
                   ↓
                [Subir a Drive (carpeta /coach/comparativas/)]
                   ↓
                [Guardar metadata en BD (opcional)]
                   ↓
                [Retornar URLs + preview]
                   ↓
         [Coach ve modal con opción descargar/copiar link]
```

---

## Preguntas Abiertas

- [ ] ¿El coach puede regenerar la misma comparativa? ¿O se reutiliza?
- [ ] ¿El cliente puede ver su propia comparativa desde la app?
- [ ] ¿Incluir nombre del coach en la imagen?
- [ ] ¿Watermark de El Método?
- [ ] ¿Opción de editar datos manualmente antes de generar?