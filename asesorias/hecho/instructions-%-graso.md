# Instrucciones: procesado de fotos % graso

## Tarea

Tomar las fotos de `fotos-%-graso/`, partirlas en dos (izquierda y derecha), y guardar cada mitad como archivo independiente en `samples-%-graso/`.

## Nomenclatura

El nombre del archivo original indica los valores de % graso: `{seq}. De {X} a {Y}.JPG`

- Foto **izquierda** → `{X}.JPG` (valor inicial / antes)
- Foto **derecha** → `{Y}.JPG` (valor final / después)

El nombre final es **solo el número de % graso**. Si ese número ya existe como archivo, se añade letra: `{X}_a.JPG`, `{X}_b.JPG`, etc.

## Casos especiales

| Caso | Ejemplo | Tratamiento |
|------|---------|-------------|
| 3 paneles | `11. 20__16__11_.JPG` | Dividir en tercios → `20.JPG`, `16.JPG`, `11.JPG` |
| Foto individual (antes/después por separado) | `9. 33_Sofia antes.jpeg` | Copiar sin partir → `33_antes.JPG` |
| Foto individual después | `9. 18_ Sofia después.jpeg` | Copiar sin partir → `18_despues.JPG` |

## Script de referencia

```python
from PIL import Image
import os, re

src = 'fotos-%-graso'
dst = 'samples-%-graso'

# Para cada archivo:
# 1. Extraer seq (primer número del nombre)
# 2. Extraer body_nums (todos los números después del seq)
# 3. Si len(body_nums) == 3 → dividir en 3 tercios
# 4. Si contiene "sofia/antes/después" → foto individual, no partir
# 5. Si len(body_nums) == 2 → partir por la mitad (mid = w // 2)
# 6. Guardar como {num}.JPG; si ya existe, usar {num}_a.JPG, {num}_b.JPG, etc.
```

## Resultado

- Origen: `fotos-%-graso/` (53 archivos, originales intactos)
- Destino: `samples-%-graso/` (108 archivos generados)
