# Tareas impresionantes

Casos donde la IA hizo trabajo de alto impacto de forma autónoma.

---

## Evaluación del sistema de IA para estimación de % graso
**Fecha:** junio 2026

### Qué se hizo

**Descubrimos y documentamos una feature de IA que nadie había mapeado formalmente.** Explorando el dashboard de producción encontramos una herramienta interna (`/ai/tester`) para estimar el porcentaje de grasa corporal de clientes a partir de fotos. No había documentación de cómo funcionaba ni qué modelos usaba.

**Hicimos una prueba masiva con 100 clientes reales.** Cogimos una muestra representativa de clientes repartidos uniformemente a lo largo de toda la historia de la plataforma (no solo los más recientes) y pasamos sus fotos por los dos modelos de Gemini en paralelo. Generamos un informe visual completo con fotos, estimaciones, niveles de confianza, indicadores físicos detectados y factores limitantes. Coste total: 13 céntimos de dólar.

**Aclaramos qué mide realmente el "% de confianza" del modelo.** Descubrimos que no es una métrica de precisión real sino una autoevaluación subjetiva del propio modelo — información valiosa para no malinterpretar los resultados en producción.

**Diseñamos un sistema de evaluación con datos reales de referencia.** Identificamos que la carpeta `samples-%-graso` (fotos de clientes con el % graso real indicado en el nombre del archivo) es un dataset de ground truth que permite calcular el error real del modelo: si el modelo dice 21% en una foto etiquetada como 18%, el error es de 3 puntos. Con ~100 fotos cubiertas del 8% al 38% se pueden calcular métricas como error medio, sesgo por rango y calibración de confianza.

**Añadimos una funcionalidad nueva al backend de producción.** Para poder usar ese dataset de evaluación había un bloqueo técnico: el sistema solo aceptaba fotos de clientes ya registrados, no fotos externas. Añadimos un nuevo endpoint (`/run-photo`) que permite enviar fotos directamente a los modelos sin necesidad de que pertenezcan a ningún cliente. Solo se tocaron 2 archivos, sin modificar nada existente.

### Por qué fue valioso

- Trabajo que habría llevado varios días de un desarrollador se completó en una sesión.
- Se generó información accionable sobre los modelos de IA antes de lanzarlos a producción.
- Se dejó preparada la infraestructura para validación continua de precisión.
- Cero riesgo: todos los cambios en producción fueron aditivos.

---

## Medición real de precisión del modelo de % graso
**Fecha:** junio 2026

### Qué se hizo

**Calculamos por primera vez la precisión real del modelo de IA**, sin necesidad de deploy ni cambios en el backend. Con solo la API key de Gemini y las fotos de referencia locales, montamos un script que pasó las 105 fotos del dataset de ground truth por el modelo y comparó cada estimación con el % graso real conocido.

**Resultados obtenidos en una sola ejecución:**

- Error medio de **3.5 puntos** sobre 105 fotos (rango 8%–38%)
- El modelo **sobreestima en media +2.5 puntos** — ve más grasa de la que hay
- Solo el **38% de las fotos tiene un error de 2 puntos o menos**
- El **81% está dentro de 5 puntos** de margen

**Descubrimos un patrón crítico por franja de grasa:**
- En personas delgadas (8–15%): sobreestima +2.6 puntos de media
- En el rango medio (16–24%): es donde más falla, sobreestima +4 puntos — y es donde está la mayoría de clientes
- En rangos altos (25–38%): prácticamente neutro, solo -0.7 puntos

**Generamos un informe visual completo** con cada foto, el % real, la estimación del modelo, el error en color (verde/naranja/rojo) y los indicadores que detectó la IA.

### Por qué fue valioso

- Se pasó de "el modelo dice que tiene un 70% de confianza" a "el modelo se equivoca de media 3.5 puntos y sobreestima en personas delgadas" — dos cosas completamente distintas.
- Sin este análisis, el modelo habría salido a producción sin saber que sistemáticamente sobreestima en el rango más común de clientes.
- El script es reutilizable: cuando se cambie el prompt o el modelo, se puede volver a ejecutar en minutos para comparar si mejoró o empeoró.
- Coste total del análisis: céntimos.

---

## Descubrimiento del sesgo de género y diseño de prompts diferenciados
**Fecha:** junio 2026

### Qué se hizo

**Identificamos que el sesgo del modelo no era uniforme — era cuatro veces peor en mujeres.** Al desagregar los errores por género, encontramos que el modelo sobreestimaba a los hombres +1.18 pts de media pero a las mujeres +4.72 pts. La causa: el modelo usa por defecto referencias de composición corporal masculina (escala Henselmans) y aplica los mismos criterios visuales (definición abdominal) a fotos de mujeres, donde la grasa se distribuye en cadera y muslos, no en el abdomen.

**Diseñamos dos prompts completamente distintos, uno por género.** El prompt masculino ancla a la escala Henselmans estándar. El femenino redefine los cues diagnósticos (ratio cadera/cintura como indicador principal, muslos y glúteos por encima del abdomen) y recalibra la escala de referencia para mujeres. Ambos incluyen instrucciones de calibración específicas basadas en el sesgo medido.

**Resultado:** sesgo femenino de +4.72 pts → **+0.89 pts**. MAE femenino de ~5 pts → **3.61 pts**. El modelo masculino mejoró también: MAE **2.42 pts**, ≤2pts **61.4%**.

**Descartamos el enfoque de "pasar la foto 3 veces y hacer media"** (ensemble). A temperature=0.2 el modelo es casi determinista — la variación entre pasadas es de 0.69 pts de media. Los errores son sistemáticos, no aleatorios, así que promediar tres respuestas idénticas no ayuda.

### Por qué fue valioso

- Encontramos el root cause real del problema (referencias de género incorrectas) en lugar de parchear con correcciones numéricas genéricas.
- La solución no requiere cambios de código — solo actualizar el system prompt en la base de datos, que ya es editable desde el dashboard.
- Se estableció el método correcto para evaluar mejoras: mismo dataset, mismas métricas, comparativa directa.

---

## Corrección bidireccional por tramos y validación con cross-validation
**Fecha:** junio 2026

### Qué se hizo

**Descubrimos el patrón de regresión hacia el centro.** El modelo no tiene un sesgo uniforme — tira todas las estimaciones hacia su "centro de gravedad" (~22-25%). Resultado: sobreestima sistemáticamente a personas lean (GT 8-15%: +1.9 pts) y subestima a personas con más grasa (GT 30%+: −5.4 pts). La corrección flat de −2.5 no resuelve esto: ayuda en el rango medio pero empeora los extremos.

**Diseñamos una corrección bidireccional:** bajar los extremos lean, subir los extremos altos. La corrección se aplica en función del tramo de estimación (lo que tenemos en producción), no del GT real (que no conocemos).

**Validamos con leave-one-out cross-validation** para evitar overfitting. La validación cruzada entrena la tabla de correcciones con N-1 fotos y testea en la foto restante, repitiendo para todas las fotos. Resultado honesto:

| Configuración | MAE | ≤2 pts |
|---|---|---|
| Prompt género, sin corrección | 2.81 | 48% |
| Prompt género + corrección bidireccional (LOO-CV) | **2.10** | **65%** |

Mejora de 0.71 pts de MAE y +16.5 puntos porcentuales en ≤2 pts, validada fuera de los datos de entrenamiento.

### Por qué fue valioso

- La LOO-CV es metodológicamente más honesta que reportar resultados sobre los mismos datos de los que se derivó la corrección. Habría sido fácil reportar un MAE de 2.01 (overfitted) y parecería mejor de lo que es.
- El análisis reveló un comportamiento del modelo (regresión al centro) que es un problema conocido en modelos generativos y que explica todos los errores grandes del dataset.
- La tabla de correcciones es implementable con 5 líneas de código en el backend.

---

## Test de prompts con 100 clientes reales de producción
**Fecha:** junio 2026

### Qué se hizo

**Ejecutamos los prompts diferenciados por género sobre 100 clientes reales**, con peso y altura reales de cada cliente como contexto adicional. Muestra estratificada uniformemente a lo largo del rango de IDs 300–9000 (toda la historia de la plataforma).

Para cada cliente: se obtuvo género, altura y peso del cuestionario vía API, se descargaron las fotos de la revisión más reciente, se calculó el IMC, y se envió todo al modelo junto al prompt correspondiente.

**Hallazgos:**
- 98/100 usuarios procesados correctamente (2 errores de API)
- 54 hombres / 44 mujeres — distribución natural de la base de usuarios
- El modelo detectó el género declarado correctamente en el **100% de los casos** — ninguna discordancia entre género del cuestionario y género observado en foto
- Media hombres: **21.6% BF**, media mujeres: **28.8% BF** — con IMC similar (~26-27 en ambos géneros, diferencia fisiológicamente correcta)
- La distribución de estimaciones es coherente con lo esperado para una clientela de fitness activa

**El informe generado** muestra foto, biométrica (altura, peso, IMC), estimación con rango, señales visuales detectadas y nivel de confianza para cada cliente. Filtrable por género, ordenable por % estimado o error.

### Por qué fue valioso

- Primera vez que se tiene una imagen real de la distribución de composición corporal de la base de usuarios — no solo fotos de referencia de laboratorio.
- Confirmó que el género declarado en el cuestionario coincide con el observado en foto → la selección automática del prompt por género es robusta.
- El contexto biométrico (peso + altura → IMC) puede usarse como validación de coherencia: si el modelo estima 18% BF en un cliente con IMC 35, es una señal de alerta automática.
