# EMP DS Library — Design System Reference

Archivo Figma: `LOFKz4g6bswukPAJfWR0Ts`  
Archivo de trabajo: `629ryw0MF7hzDxIFiZJ5Un` (App Automática)

---

## Identidad visual

**Tema:** Dark-first — fondo casi negro con verde neón como color de acción.  
**Tipografía:** Open Sans (Regular, SemiBold, Bold, ExtraBold, Light + Italic / Condensed)  
**Frame móvil:** 393 × 852 px | Grid: 8 columnas

---

## Colores

### Primitivos

| Token | Hex | Descripción |
|-------|-----|-------------|
| `brand/500` | `#00ee00` | Verde neón primario — CTAs, badges, activos |
| `brand/400` | `#84f44c` | Verde neón secundario — más suave |
| `neutral/950` | `#0b0f14` | Negro más profundo |
| `neutral/900` | `#15171c` | Fondo base de la app |
| `neutral/800` | `#1d1f23` | Surface / cards |
| `neutral/600` | `#3c3e41` | Divisores |
| `neutral/500` | `#61656c` | Bordes fuertes |
| `neutral/300` | `#8f8f97` | Texto terciario / muted |
| `neutral/200` | `#dbdae0` | Texto secundario |
| `neutral/50` | `#f2f2f7` | Texto primario |
| `neutral/0` | `#ffffff` | Blanco puro |

### Semánticos

| Token semántico | Hex | Uso |
|-----------------|-----|-----|
| `bg/app` | `#0b0f14` | Fondo general de la app |
| `bg/surface-1` | `#15171c` | Primera capa de superficie |
| `bg/surface-2` | `#1d1f23` | Segunda capa / cards |
| `bg/elevated` | `#1d1f23` | Elementos elevados |
| `text/primary` | `#f2f2f7` | Texto principal |
| `text/secondary` | `#dbdae0` | Texto secundario |
| `text/tertiary` | `#8f8f97` | Texto de soporte / muted |
| `brand/primary` | `#00ee00` | Acción principal |
| `stroke/divider` | `#3c3e41` | Separadores |
| `stroke/stronge` | `#61656c` | Bordes con más peso |

### Estilos de color adicionales (47 total en Figma)

- `color/accent/` — highContrast, lowContrast, lowlowContrast
- `color/surface/` — gradientes, text-fields, superficies
- `color/neutral/` — Stroke-Divider, Stroke-Activo
- `color/ranking/` — plata, bronce
- `color/semantic/` — error, destructive, ranking-2, ranking-3
- `bg/light`

---

## Tipografía

**Fuente:** Open Sans

### Títulos

| Estilo | Uso |
|--------|-----|
| `H0-stats` | Estadísticas grandes / héroe |
| `H1-stats` | Valores numéricos destacados |
| `H1-sección` | Encabezado de sección |
| `H2-cards` | Título de card |

### Body

| Estilo | |
|--------|-|
| `lg` | Texto largo, lectura |
| `lg-bold-underline` | |
| `md` | Texto estándar |
| `md-bold` | Énfasis |
| `md-bold-underline` | |
| `sm` | Texto pequeño |
| `sm-bold` | |
| `sm-bold-underline` | |

### Labels

| Estilo | |
|--------|-|
| `sm` | Label estándar |
| `sm-bold` | Label con peso |
| `xs` | Label mínimo |

---

## Espaciado

| Token | px |
|-------|----|
| `S-4` | 4 |
| `S-6` | 6 |
| `S-8` | 8 |
| `S-16` | 16 |
| `S-24` | 24 |
| `S-32` | 32 |
| `S-48` | 48 |
| `S-72` | 72 |
| `Max` | 1000 |
| `--touch-size` | 48 (mínimo toque) |

---

## Radius

| Token | px | Forma |
|-------|----|-------|
| `R-4` | 4 | Esquina sutil |
| `R-6` | 6 | |
| `R-8` | 8 | Cards |
| `R-full` | 1000 | Pill / botón CTA |

---

## Efectos

| Efecto | Uso |
|--------|-----|
| `glow` | Resplandor neón activo |
| `glow-soft` | Resplandor suave |
| `mid-shadow` | Sombra media |
| `hard-shadow` | Sombra fuerte |

El glow se aplica con opacity 0.15–0.4 del verde `#00ee00` en bordes de elementos activos.

---

## Layout

| Elemento | Valor |
|----------|-------|
| Frame móvil | 393 × 852 px |
| Grid | `Grid/Mobile-8-Col` — 8 columnas |
| Status bar | 44 px |
| Bottom nav | 80 px |
| Padding horizontal | 24 px (`S-24`) c/lado → content width ~345 px |
| Touch target mínimo | 48 px (`--touch-size`) |

---

## Íconos

**Tamaño:** 24 × 24 px | **Stroke:** 1.5 px round | **Color por defecto:** `#f2f2f7`  
**Contenedor:** Elipse 32–40 px con fondo `#0b0f14` al 80%

| Ícono | |
|-------|-|
| Boxing | |
| Bicicleta (ruta) | |
| AddOtherActivity | |
| HealthConnect | |
| Google, Apple, Mail | Autenticación |
| Stop | |
| arrow_forward | |
| repeat | |
| Note | |
| TrainingLog | |
| trailingLogContained | |
| Add | low / high / fineLine |
| Play | |
| Info | |
| check | |
| x | |
| downArrow | |
| Home | |
| Profile | |
| Upload | |
| training | outline / filled |
| explore | outline / filled |
| community | outline / filled |

---

## Patrones de UI

### Botón CTA
- Forma: pill (`R-full` = 1000 px)
- Fondo: `#00ee00`
- Texto: oscuro encima del verde
- Efecto: `glow` en estado activo

### Cards
- Radius: `R-8` (8 px)
- Fondo: `bg/surface-2` = `#1d1f23`

### Nav bar activo
- Pill verde + label + ícono
- Color activo: `brand/primary` = `#00ee00`

### Glow en bordes activos
- Opacity: 0.15–0.4 del verde neón
- Aplicado sobre `stroke/divider` o `stroke/stronge`

---

## Variables en la library

| Colección | Key |
|-----------|-----|
| `Color/Primitives` | `6c54b51cfdcc3d693da7ff0b9c1c073a1b760f2c` |
| `Color/Semantic` | `23c41dfd6681d3ed114a6cdef107e693046eea44` |
| `Tokens` | `8aecb9d0de299864556d4054a39f547909a30e8d` |
