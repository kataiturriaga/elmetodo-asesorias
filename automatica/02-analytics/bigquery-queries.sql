-- ============================================================
-- EL MÉTODO — BigQuery Analytics Queries
-- Proyecto: automatica-v2
-- Dataset: analytics_517999677
-- Tabla consolidada: events_combined_mat_mat
-- ============================================================

-- INSTRUCCIONES:
-- 1. Abre BigQuery en console.cloud.google.com/bigquery
-- 2. Tabla a usar: `automatica-v2.analytics_517999677.events_combined_mat_mat`
-- 3. Cada query puedes guardarla como una "Saved Query" en BigQuery
--    o conectarla directamente a Looker Studio

-- ============================================================
-- HELPERS / VARIABLES
-- ============================================================
-- Usa esto al inicio de cualquier query para fijar el rango de fechas:
-- DECLARE start_date DATE DEFAULT '2026-03-01';
-- DECLARE end_date DATE DEFAULT CURRENT_DATE();

-- ============================================================
-- 1. INSTALLS (descargas)
-- Métrica: Adquisición — Driver
-- ============================================================
SELECT
  DATE(TIMESTAMP_MICROS(event_timestamp)) AS date,
  COUNT(DISTINCT user_pseudo_id)          AS installs
FROM `automatica-v2.analytics_517999677.events_combined_mat`
WHERE
  event_name = 'first_open'
  AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
GROUP BY 1
ORDER BY 1 DESC;


-- ============================================================
-- 2. LIGHT ACTIVATION RATE (D0)
-- Métrica: % de installs con health_permission_granted OR ranking_unlock_success en D0
-- Objetivo: ≥40%
-- ============================================================
-- falta el evento de ranking enroll por meter(carles)

WITH installs AS (
  SELECT
    user_pseudo_id,
    MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS install_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'first_open'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
),
light_activations AS (
  SELECT DISTINCT
    user_pseudo_id,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS activation_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'pedometer_enabled'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
)
SELECT
  i.install_date,
  COUNT(DISTINCT i.user_pseudo_id)  AS installs,
  COUNT(DISTINCT a.user_pseudo_id)  AS light_activations,
  ROUND(
    COUNT(DISTINCT a.user_pseudo_id) / NULLIF(COUNT(DISTINCT i.user_pseudo_id), 0) * 100,
    1
  )                                  AS light_activation_rate_pct
FROM installs i
LEFT JOIN light_activations a
  ON i.user_pseudo_id = a.user_pseudo_id
  AND a.activation_date = i.install_date  -- D0: mismo día de instalación
GROUP BY 1
ORDER BY 1 DESC;


-- ============================================================
-- 3. BASE ENROLL RATE (D0–D3)  ← FOCO PRINCIPAL PRODUCTO
-- Métrica: % de installs con program_enroll en los primeros 3 días
-- Objetivo: ≥20%
-- ============================================================
WITH installs AS (
  SELECT
    user_pseudo_id,
    MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS install_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'first_open'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
),
enrolls AS (
  SELECT
    user_pseudo_id,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS enroll_date,
    -- Extraer parámetros del evento
    MAX(IF(ep.key = 'entry_point',  ep.value.string_value, NULL)) AS entry_point,
    MAX(IF(ep.key = 'program_type', ep.value.string_value, NULL)) AS program_type
  FROM `automatica-v2.analytics_517999677.events_combined_mat`,
  UNNEST(event_params) AS ep
  WHERE event_name = 'program_enroll'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1, 2
  HAVING MAX(IF(ep.key = 'entry_point', ep.value.string_value, NULL)) = 'onboarding'
)
SELECT
  i.install_date,
  COUNT(DISTINCT i.user_pseudo_id) AS installs,
  COUNT(DISTINCT e.user_pseudo_id) AS base_enrolls_d0_d3,
  ROUND(
    COUNT(DISTINCT e.user_pseudo_id) / NULLIF(COUNT(DISTINCT i.user_pseudo_id), 0) * 100,
    1
  )                                 AS base_enroll_rate_pct,
  20.0                              AS objetivo_pct  -- línea de objetivo
FROM installs i
LEFT JOIN enrolls e
  ON i.user_pseudo_id = e.user_pseudo_id
  AND DATE_DIFF(e.enroll_date, i.install_date, DAY) BETWEEN 0 AND 3
GROUP BY 1
ORDER BY 1 DESC;


-- ACTUALMENTE ESTA ESTE:
-- Carles tiene que meter el parametro o 'program_enroll' o signup_success

WITH installs AS (
  SELECT
    user_pseudo_id,
    MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS install_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'first_open'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
),
signups AS (
  SELECT
    user_pseudo_id,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS signup_date,
    MAX(IF(ep.key = 'entry_point', ep.value.string_value, NULL)) AS entry_point
  FROM `automatica-v2.analytics_517999677.events_combined_mat`,
  UNNEST(event_params) AS ep
  WHERE event_name = 'signup_method_selected'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1, 2
)
SELECT
  i.install_date,
  COUNT(DISTINCT i.user_pseudo_id) AS installs,
  COUNT(DISTINCT s.user_pseudo_id) AS signups_d0_d3,
  ROUND(
    COUNT(DISTINCT s.user_pseudo_id) / NULLIF(COUNT(DISTINCT i.user_pseudo_id), 0) * 100,
    1
  ) AS signup_rate_pct,
  20.0 AS objetivo_pct
FROM installs i
LEFT JOIN signups s
  ON i.user_pseudo_id = s.user_pseudo_id
  AND DATE_DIFF(s.signup_date, i.install_date, DAY) BETWEEN 0 AND 3
GROUP BY 1
ORDER BY 1 DESC;

-- creo que si que va el program_enroll. en esta query la uso y ademas le pongo entry_point=onboarding

WITH installs AS (
  SELECT
    user_pseudo_id,
    MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS install_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'first_open'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
),
enroll_events AS (
  SELECT
    user_pseudo_id,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS enroll_date,
    (
      SELECT ep.value.string_value
      FROM UNNEST(event_params) ep
      WHERE ep.key = 'entry_point'
      LIMIT 1
    ) AS entry_point,
    (
      SELECT ep.value.string_value
      FROM UNNEST(event_params) ep
      WHERE ep.key = 'program_type'
      LIMIT 1
    ) AS program_type
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'program_enroll'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
),
enrolls AS (
  SELECT
    user_pseudo_id,
    enroll_date,
    entry_point,
    program_type
  FROM enroll_events
  WHERE entry_point = 'onboarding'
)
SELECT
  i.install_date,
  COUNT(DISTINCT i.user_pseudo_id) AS installs,
  COUNT(DISTINCT e.user_pseudo_id) AS base_enrolls_d0_d3,
  ROUND(
    COUNT(DISTINCT e.user_pseudo_id) / NULLIF(COUNT(DISTINCT i.user_pseudo_id), 0) * 100,
    1
  ) AS base_enroll_rate_pct,
  20.0 AS objetivo_pct
FROM installs i
LEFT JOIN enrolls e
  ON i.user_pseudo_id = e.user_pseudo_id
  AND DATE_DIFF(e.enroll_date, i.install_date, DAY) BETWEEN 0 AND 3
GROUP BY 1
ORDER BY 1 DESC;


-- ============================================================
-- 4. HABIT FORMATION - 6 WORKOUTS / 14 DAYS (Base Starters) 
-- Métrica: % de usuarios con program_enroll que completan ≥6 sesiones en 14 días
-- Objetivo: ≥35%
-- ============================================================
WITH enrolls AS (
  SELECT
    user_pseudo_id,
    MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS enroll_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'program_enroll'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
),
sessions AS (
  SELECT
    user_pseudo_id,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS session_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'training_session_complete'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
),
sessions_in_window AS (
  SELECT
    e.user_pseudo_id,
    e.enroll_date,
    COUNT(s.session_date) AS sessions_in_14d
  FROM enrolls e
  LEFT JOIN sessions s
    ON e.user_pseudo_id = s.user_pseudo_id
    AND DATE_DIFF(s.session_date, e.enroll_date, DAY) BETWEEN 0 AND 13
  GROUP BY 1, 2
)
SELECT
  enroll_date,
  COUNT(DISTINCT user_pseudo_id)                                           AS base_starters,
  COUNT(DISTINCT IF(sessions_in_14d >= 6, user_pseudo_id, NULL))          AS completed_6_workouts,
  ROUND(
    COUNT(DISTINCT IF(sessions_in_14d >= 6, user_pseudo_id, NULL))
    / NULLIF(COUNT(DISTINCT user_pseudo_id), 0) * 100,
    1
  )                                                                         AS habit_rate_pct,
  35.0                                                                      AS objetivo_pct
FROM sessions_in_window
GROUP BY 1
ORDER BY 1 DESC;


-- ============================================================
-- 5. TRIAL START RATE
-- Métrica: % de installs que hacen trial_started (en cualquier momento)
-- Objetivo: ≥20%
-- ============================================================
WITH installs AS (
  SELECT
    user_pseudo_id,
    MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS install_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'first_open'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
),
trials AS (
  SELECT DISTINCT user_pseudo_id
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'trial_started'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
)
SELECT
  i.install_date,
  COUNT(DISTINCT i.user_pseudo_id)  AS installs,
  COUNT(DISTINCT t.user_pseudo_id)  AS trial_starts,
  ROUND(
    COUNT(DISTINCT t.user_pseudo_id) / NULLIF(COUNT(DISTINCT i.user_pseudo_id), 0) * 100,
    1
  )                                  AS trial_start_rate_pct,
  20.0                               AS objetivo_pct
FROM installs i
LEFT JOIN trials t ON i.user_pseudo_id = t.user_pseudo_id
GROUP BY 1
ORDER BY 1 DESC;


-- ============================================================
-- 6. TRIAL → PAID CONVERSION  ← FOCO PRINCIPAL NEGOCIO
-- Métrica: % de trial_started que pasan a purchase_completed
-- Objetivo: ≥50%
-- ============================================================
WITH trials AS (
  SELECT
    user_pseudo_id,
    MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS trial_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'trial_started'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
),
conversions AS (
  SELECT
    user_pseudo_id,
    (
      SELECT ep.value.string_value
      FROM UNNEST(event_params) ep
      WHERE ep.key = 'tier'
      LIMIT 1
    ) AS tier
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'purchase_completed'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
)
SELECT
  t.trial_date,
  COUNT(DISTINCT t.user_pseudo_id)  AS trial_starts,
  COUNT(DISTINCT c.user_pseudo_id)  AS paid_conversions,
  ROUND(
    COUNT(DISTINCT c.user_pseudo_id) / NULLIF(COUNT(DISTINCT t.user_pseudo_id), 0) * 100,
    1
  )                                  AS trial_to_paid_rate_pct,
  -- Breakdown por tier (monthly / quarterly / yearly)
  COUNT(DISTINCT IF(c.tier = 'monthly',   c.user_pseudo_id, NULL)) AS tier_monthly,
  COUNT(DISTINCT IF(c.tier = 'quarterly', c.user_pseudo_id, NULL)) AS tier_quarterly,
  COUNT(DISTINCT IF(c.tier = 'yearly',    c.user_pseudo_id, NULL)) AS tier_yearly,
  50.0                               AS objetivo_pct
FROM trials t
LEFT JOIN conversions c ON t.user_pseudo_id = c.user_pseudo_id
GROUP BY 1
ORDER BY 1 DESC;


-- ============================================================
-- 12. FUNNEL DE MONETIZACIÓN (paywall → compra)
-- Muestra dónde se caen los usuarios en el flujo de pago.
-- ============================================================
WITH funnel AS (
  SELECT
    user_pseudo_id,
    event_name,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS event_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name IN (
    'paywall_viewed',
    'purchase_started',
    'purchase_completed',
    'purchase_cancelled',
    'purchase_failed'
  )
  AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
),
step_counts AS (
  SELECT
    event_name,
    COUNT(DISTINCT user_pseudo_id) AS unique_users
  FROM funnel
  GROUP BY 1
)
SELECT
  event_name,
  unique_users,
  ROUND(
    unique_users / (SELECT unique_users FROM step_counts WHERE event_name = 'paywall_viewed') * 100,
    1
  ) AS pct_of_paywall_views
FROM step_counts
ORDER BY unique_users DESC;


-- ============================================================
-- 13. PAYWALL POR ENTRY POINT
-- ¿Desde dónde llegan los usuarios al paywall?
-- Sirve para priorizar dónde colocar los CTAs de suscripción.
-- entry_points: base_program | catalog | trial_expired | explore | banner | next_level
-- ============================================================
SELECT
  (
    SELECT ep.value.string_value
    FROM UNNEST(event_params) ep
    WHERE ep.key = 'entry_point'
    LIMIT 1
  ) AS entry_point,
  COUNT(DISTINCT user_pseudo_id) AS paywall_views,
  ROUND(
    COUNT(DISTINCT user_pseudo_id) /
    (
      SELECT COUNT(DISTINCT user_pseudo_id)
      FROM `automatica-v2.analytics_517999677.events_combined_mat`
      WHERE event_name = 'paywall_viewed'
        AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
    ) * 100,
    1
  ) AS pct_of_total
FROM `automatica-v2.analytics_517999677.events_combined_mat`
WHERE event_name = 'paywall_viewed'
  AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
GROUP BY 1
ORDER BY paywall_views DESC;


-- ============================================================
-- 14. RESUMEN DIARIO MONETIZACIÓN
-- Tabla base para el dashboard de monetización.
-- Una fila por día con todos los eventos clave.
-- ============================================================
WITH daily AS (
  SELECT
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS date,
    event_name,
    user_pseudo_id
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name IN (
    'paywall_viewed', 'purchase_started', 'purchase_completed',
    'purchase_cancelled', 'purchase_failed',
    'trial_started', 'trial_ended',
    'base_expiry_warning_shown', 'base_expiry_locked_view'
  )
  AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
)
SELECT
  date,
  COUNT(DISTINCT IF(event_name = 'paywall_viewed',          user_pseudo_id, NULL)) AS paywall_views,
  COUNT(DISTINCT IF(event_name = 'purchase_started',        user_pseudo_id, NULL)) AS purchase_starts,
  COUNT(DISTINCT IF(event_name = 'purchase_completed',      user_pseudo_id, NULL)) AS purchases,
  COUNT(DISTINCT IF(event_name = 'purchase_cancelled',      user_pseudo_id, NULL)) AS cancellations,
  COUNT(DISTINCT IF(event_name = 'purchase_failed',         user_pseudo_id, NULL)) AS failures,
  COUNT(DISTINCT IF(event_name = 'trial_started',           user_pseudo_id, NULL)) AS trial_starts,
  COUNT(DISTINCT IF(event_name = 'trial_ended',             user_pseudo_id, NULL)) AS trial_ends,
  COUNT(DISTINCT IF(event_name = 'base_expiry_warning_shown', user_pseudo_id, NULL)) AS expiry_warnings,
  COUNT(DISTINCT IF(event_name = 'base_expiry_locked_view', user_pseudo_id, NULL)) AS locked_views,
  -- Tasas clave
  ROUND(
    COUNT(DISTINCT IF(event_name = 'purchase_started',   user_pseudo_id, NULL)) /
    NULLIF(COUNT(DISTINCT IF(event_name = 'paywall_viewed', user_pseudo_id, NULL)), 0) * 100,
    1
  ) AS ctr_paywall_pct,
  ROUND(
    COUNT(DISTINCT IF(event_name = 'purchase_completed', user_pseudo_id, NULL)) /
    NULLIF(COUNT(DISTINCT IF(event_name = 'paywall_viewed', user_pseudo_id, NULL)), 0) * 100,
    1
  ) AS conversion_paywall_pct
FROM daily
GROUP BY 1
ORDER BY 1 DESC;


-- ============================================================
-- BONUS: FUNNEL COMPLETO DE CONVERSIÓN (onboarding → enroll) (por hacer)
-- Para identificar dónde se caen los usuarios en el funnel de Training Onboarding
-- ============================================================
WITH funnel_events AS (
  SELECT
    user_pseudo_id,
    event_name,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS event_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name IN (
    'first_open',
    'training_onboarding_continue_clicked',
    'program_start_intent_clicked',
    'program_enroll_intent_clicked',
    'signup_method_selected',
    'signup_completed',
    'program_enroll'
  )
  AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
),
step_counts AS (
  SELECT
    event_name,
    COUNT(DISTINCT user_pseudo_id) AS unique_users
  FROM funnel_events
  GROUP BY 1
)
SELECT
  event_name,
  unique_users,
  ROUND(
    unique_users / (SELECT unique_users FROM step_counts WHERE event_name = 'first_open') * 100,
    1
  ) AS pct_of_installs
FROM step_counts
ORDER BY unique_users DESC;


-- ============================================================
-- 7. RETENCIÓN D1 / D7 / D30
-- La métrica más importante después de installs.
-- Te dice si estás llenando un cubo agujereado.
-- ============================================================
WITH installs AS (
  SELECT
    user_pseudo_id,
    MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS install_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'first_open'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
),
activity AS (
  SELECT DISTINCT
    user_pseudo_id,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS activity_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
    AND event_name = 'app_open'  -- solo apertura real del usuario (excluye pedometer_sync y otros background events)
)
SELECT
  i.install_date,
  COUNT(DISTINCT i.user_pseudo_id) AS installs,
  COUNT(DISTINCT IF(DATE_DIFF(a.activity_date, i.install_date, DAY) = 1,  i.user_pseudo_id, NULL)) AS retained_d1,
  COUNT(DISTINCT IF(DATE_DIFF(a.activity_date, i.install_date, DAY) = 7,  i.user_pseudo_id, NULL)) AS retained_d7,
  COUNT(DISTINCT IF(DATE_DIFF(a.activity_date, i.install_date, DAY) = 30, i.user_pseudo_id, NULL)) AS retained_d30,
  ROUND(COUNT(DISTINCT IF(DATE_DIFF(a.activity_date, i.install_date, DAY) = 1,  i.user_pseudo_id, NULL)) / NULLIF(COUNT(DISTINCT i.user_pseudo_id), 0) * 100, 1) AS d1_pct,
  ROUND(COUNT(DISTINCT IF(DATE_DIFF(a.activity_date, i.install_date, DAY) = 7,  i.user_pseudo_id, NULL)) / NULLIF(COUNT(DISTINCT i.user_pseudo_id), 0) * 100, 1) AS d7_pct,
  ROUND(COUNT(DISTINCT IF(DATE_DIFF(a.activity_date, i.install_date, DAY) = 30, i.user_pseudo_id, NULL)) / NULLIF(COUNT(DISTINCT i.user_pseudo_id), 0) * 100, 1) AS d30_pct
FROM installs i
LEFT JOIN activity a ON i.user_pseudo_id = a.user_pseudo_id
GROUP BY 1
ORDER BY 1 DESC;


-- ============================================================
-- 8. TIEMPO HASTA PRIMER ENTRENO (Time to First Workout)
-- Mediana de horas entre first_open → training_session_complete
-- Si la mediana es >48h, hay fricción en el onboarding.
-- ============================================================
WITH installs AS (
  SELECT
    user_pseudo_id,
    MIN(TIMESTAMP_MICROS(event_timestamp)) AS install_ts
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'first_open'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
),
first_session AS (
  -- Sin límite superior de fecha: captura el primer entreno aunque sea días después del install
  SELECT
    user_pseudo_id,
    MIN(TIMESTAMP_MICROS(event_timestamp)) AS first_session_ts
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'training_session_complete'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) >= PARSE_DATE('%Y%m%d', @DS_START_DATE)
  GROUP BY 1
)
SELECT
  COUNT(DISTINCT i.user_pseudo_id)                                                               AS installs,
  COUNT(DISTINCT f.user_pseudo_id)                                                               AS reached_first_workout,
  ROUND(COUNT(DISTINCT f.user_pseudo_id) / NULLIF(COUNT(DISTINCT i.user_pseudo_id), 0) * 100, 1) AS pct_reach_first_workout,
  ROUND(APPROX_QUANTILES(TIMESTAMP_DIFF(f.first_session_ts, i.install_ts, MINUTE), 100)[OFFSET(50)], 0) AS median_minutes_to_first_workout,
  ROUND(APPROX_QUANTILES(TIMESTAMP_DIFF(f.first_session_ts, i.install_ts, MINUTE), 100)[OFFSET(75)], 0) AS p75_minutes_to_first_workout
FROM installs i
LEFT JOIN first_session f ON i.user_pseudo_id = f.user_pseudo_id
WHERE f.user_pseudo_id IS NOT NULL;


-- ============================================================
-- 9. GUEST → ACCOUNT CONVERSION 
-- % de usuarios que empezaron como guest y crearon cuenta real.
-- Crítico porque tienes login de invitado.
-- ============================================================
WITH guests AS (
  SELECT DISTINCT user_pseudo_id
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'guest_login'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
),
converted AS (
  SELECT DISTINCT user_pseudo_id
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'signup_completed'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
),
-- Usuarios guest que luego se registraron (guest_upgrade)
upgraded AS (
  SELECT
    user_pseudo_id,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS upgrade_date,
    MAX(IF(ep.key = 'method', ep.value.string_value, NULL)) AS upgrade_method
  FROM `automatica-v2.analytics_517999677.events_combined_mat`,
  UNNEST(event_params) AS ep
  WHERE event_name = 'guest_upgrade'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1, 2
)
SELECT
  COUNT(DISTINCT g.user_pseudo_id)  AS total_guests,
  COUNT(DISTINCT u.user_pseudo_id)  AS converted_to_account,
  ROUND(COUNT(DISTINCT u.user_pseudo_id) / NULLIF(COUNT(DISTINCT g.user_pseudo_id), 0) * 100, 1) AS guest_conversion_rate_pct,
  -- Breakdown por método
  COUNT(DISTINCT IF(u.upgrade_method = 'google', u.user_pseudo_id, NULL)) AS via_google,
  COUNT(DISTINCT IF(u.upgrade_method = 'apple',  u.user_pseudo_id, NULL)) AS via_apple,
  COUNT(DISTINCT IF(u.upgrade_method = 'email',  u.user_pseudo_id, NULL)) AS via_email
FROM guests g
LEFT JOIN upgraded u ON g.user_pseudo_id = u.user_pseudo_id;


-- ============================================================
-- 10. SESIONES POR SEMANA POR USUARIO ENROLLADO
-- Calidad del engagement, no solo volumen.
-- Un usuario que entrena 3x/semana vale 10x más que uno que entrena 1x/mes.
-- ============================================================
WITH enrolled_users AS (
  SELECT DISTINCT user_pseudo_id
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'program_enroll'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
),
weekly_sessions AS (
  SELECT
    e.user_pseudo_id,
    DATE_TRUNC(DATE(TIMESTAMP_MICROS(s.event_timestamp)), WEEK) AS week,
    COUNT(*) AS sessions_that_week
  FROM enrolled_users e
  JOIN `automatica-v2.analytics_517999677.events_combined_mat` s ON e.user_pseudo_id = s.user_pseudo_id
  WHERE s.event_name = 'training_session_complete'
    AND DATE(TIMESTAMP_MICROS(s.event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1, 2
)
SELECT
  week,
  COUNT(DISTINCT user_pseudo_id)                                                              AS active_users,
  ROUND(AVG(sessions_that_week), 2)                                                           AS avg_sessions_per_user,
  ROUND(APPROX_QUANTILES(sessions_that_week, 100)[OFFSET(50)], 1)                            AS median_sessions,
  COUNT(DISTINCT IF(sessions_that_week >= 3, user_pseudo_id, NULL))                          AS users_3plus_sessions,
  ROUND(COUNT(DISTINCT IF(sessions_that_week >= 3, user_pseudo_id, NULL)) / NULLIF(COUNT(DISTINCT user_pseudo_id), 0) * 100, 1) AS pct_3plus_sessions
FROM weekly_sessions
GROUP BY 1
ORDER BY 1 DESC;


-- ============================================================
-- 11. TOP PROGRAMAS POR ENROLLMENT
-- ¿Qué programa convierte mejor? Decide qué poner primero en el onboarding.
-- ============================================================
SELECT
  MAX(IF(ep.key = 'program_name', ep.value.string_value, NULL)) AS program_name,
  MAX(IF(ep.key = 'program_type', ep.value.string_value, NULL)) AS program_type,
  MAX(IF(ep.key = 'location',     ep.value.string_value, NULL)) AS location,
  MAX(IF(ep.key = 'entry_point',  ep.value.string_value, NULL)) AS entry_point,
  COUNT(DISTINCT user_pseudo_id)                                 AS total_enrolls,
  MAX(IF(ep.key = 'program_id',   ep.value.int_value,    NULL)) AS program_id
FROM `automatica-v2.analytics_517999677.events_combined_mat`,
UNNEST(event_params) AS ep
WHERE event_name = 'program_enroll'
  AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
GROUP BY
  -- Agrupar por program_id implícitamente a través de los parámetros
  (SELECT ep2.value.int_value FROM UNNEST(event_params) ep2 WHERE ep2.key = 'program_id' LIMIT 1),
  (SELECT ep2.value.string_value FROM UNNEST(event_params) ep2 WHERE ep2.key = 'entry_point' LIMIT 1)
ORDER BY total_enrolls DESC
LIMIT 20;


-- ============================================================
-- BONUS: RESUMEN DIARIO DE KPIs (dashboard rápido)
-- Útil para conectar directamente a Looker Studio como tabla base
-- ============================================================
WITH daily_installs AS (
  SELECT DATE(TIMESTAMP_MICROS(event_timestamp)) AS date, COUNT(DISTINCT user_pseudo_id) AS installs
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'first_open' AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
),
daily_enrolls AS (
  -- Solo entry_point=onboarding: mide activación (North Star).
  -- Catalog enrolls = engagement de usuarios ya activos, no cuentan aquí.
  SELECT DATE(TIMESTAMP_MICROS(event_timestamp)) AS date, COUNT(DISTINCT user_pseudo_id) AS enrolls
  FROM `automatica-v2.analytics_517999677.events_combined_mat`,
  UNNEST(event_params) AS ep
  WHERE event_name = 'program_enroll'
    AND ep.key = 'entry_point' AND ep.value.string_value = 'onboarding'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
),
daily_sessions AS (
  SELECT DATE(TIMESTAMP_MICROS(event_timestamp)) AS date, COUNT(DISTINCT user_pseudo_id) AS active_trainers
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'training_session_complete' AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1
)
SELECT
  i.date,
  i.installs,
  COALESCE(e.enrolls, 0)          AS program_enrolls,
  COALESCE(s.active_trainers, 0)  AS active_trainers,
  ROUND(COALESCE(e.enrolls, 0) / NULLIF(i.installs, 0) * 100, 1) AS enroll_rate_pct
FROM daily_installs i
LEFT JOIN daily_enrolls e  ON i.date = e.date
LEFT JOIN daily_sessions s ON i.date = s.date
ORDER BY 1 DESC;


-- ============================================================
-- DIAGNÓSTICO: ¿Se está recibiendo el evento signup_completed?
-- Corre esto en BigQuery para verificar que el evento llega.
-- ============================================================
SELECT
  DATE(TIMESTAMP_MICROS(event_timestamp)) AS date,
  COUNT(*)                                AS total_eventos,
  COUNT(DISTINCT user_pseudo_id)          AS usuarios_unicos
FROM `automatica-v2.analytics_517999677.events_combined_mat`
WHERE event_name = 'signup_completed'
  AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
GROUP BY 1
ORDER BY 1 DESC;


-- ============================================================
-- DIAGNÓSTICO: ¿Se está recibiendo el evento program_enroll?
-- Muestra también el desglose por entry_point.
-- ============================================================
SELECT
  date,
  entry_point,
  COUNT(*)                       AS total_eventos,
  COUNT(DISTINCT user_pseudo_id) AS usuarios_unicos
FROM (
  SELECT
    DATE(TIMESTAMP_MICROS(event_timestamp))                      AS date,
    user_pseudo_id,
    MAX(IF(ep.key = 'entry_point', ep.value.string_value, NULL)) AS entry_point
  FROM `automatica-v2.analytics_517999677.events_combined_mat`,
  UNNEST(event_params) AS ep
  WHERE event_name = 'program_enroll'
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1, 2
)
GROUP BY 1, 2
ORDER BY 1 DESC;



-- Query para listar todos los eventos de la app
-- DESCUBRIMIENTO: todos los eventos únicos en el dataset
SELECT
  event_name,
  COUNT(*)                       AS total_eventos,
  COUNT(DISTINCT user_pseudo_id) AS usuarios_unicos,
  MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS primera_vez,
  MAX(DATE(TIMESTAMP_MICROS(event_timestamp))) AS ultima_vez
FROM `automatica-v2.analytics_517999677.events_combined_mat`
WHERE DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN '2026-03-06' AND '2026-03-10'
GROUP BY 1
ORDER BY total_eventos DESC;


-- ============================================================
-- VIDEO BANNER — Query #15: Funnel principal
-- Métrica: apertura, retención y conversión del video banner
-- Fuente Looker Studio: "Video Banner Funnel"
-- ============================================================
-- Funnel:
--   video_banner_shown → video_opened → video_completed → video_cta_tapped
-- ============================================================
WITH video_events AS (
  SELECT
    user_pseudo_id,
    event_name,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS event_date,
    MAX(IF(ep.key = 'video_id',    ep.value.int_value,    NULL)) AS video_id,
    MAX(IF(ep.key = 'video_title', ep.value.string_value, NULL)) AS video_title,
    MAX(IF(ep.key = 'user_type',   ep.value.string_value, NULL)) AS user_type
  FROM `automatica-v2.analytics_517999677.events_combined_mat`,
  UNNEST(event_params) AS ep
  WHERE event_name IN (
      'video_banner_shown',
      'video_opened',
      'video_completed',
      'video_cta_tapped'
    )
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1, 2, 3
)
SELECT
  event_name,
  COUNT(DISTINCT user_pseudo_id) AS unique_users
FROM video_events
GROUP BY 1
ORDER BY
  CASE event_name
    WHEN 'video_banner_shown' THEN 1
    WHEN 'video_opened'       THEN 2
    WHEN 'video_completed'    THEN 3
    WHEN 'video_cta_tapped'   THEN 4
  END;


-- ============================================================
-- VIDEO BANNER — Query #16: Tasas de conversión por video y user_type
-- Fuente Looker Studio: "Video Banner Performance"
-- ============================================================
WITH base AS (
  SELECT
    user_pseudo_id,
    event_name,
    MAX(IF(ep.key = 'video_id',         ep.value.int_value,    NULL)) AS video_id,
    MAX(IF(ep.key = 'video_title',       ep.value.string_value, NULL)) AS video_title,
    MAX(IF(ep.key = 'user_type',         ep.value.string_value, NULL)) AS user_type,
    MAX(IF(ep.key = 'percent_watched',   ep.value.int_value,    NULL)) AS percent_watched,
    MAX(IF(ep.key = 'seconds_watched',   ep.value.int_value,    NULL)) AS seconds_watched,
    MAX(IF(ep.key = 'cta_type',          ep.value.string_value, NULL)) AS cta_type
  FROM `automatica-v2.analytics_517999677.events_combined_mat`,
  UNNEST(event_params) AS ep
  WHERE event_name IN (
      'video_banner_shown',
      'video_opened',
      'video_completed',
      'video_closed_early',
      'video_cta_shown',
      'video_cta_tapped',
      'video_cta_dismissed'
    )
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
  GROUP BY 1, 2
)
SELECT
  video_title,
  user_type,
  COUNT(DISTINCT IF(event_name = 'video_banner_shown', user_pseudo_id, NULL))  AS banner_shown,
  COUNT(DISTINCT IF(event_name = 'video_opened',       user_pseudo_id, NULL))  AS video_opened,
  COUNT(DISTINCT IF(event_name = 'video_completed',    user_pseudo_id, NULL))  AS video_completed,
  COUNT(DISTINCT IF(event_name = 'video_cta_tapped',   user_pseudo_id, NULL))  AS cta_tapped,
  ROUND(
    COUNT(DISTINCT IF(event_name = 'video_opened', user_pseudo_id, NULL))
    / NULLIF(COUNT(DISTINCT IF(event_name = 'video_banner_shown', user_pseudo_id, NULL)), 0) * 100, 1
  ) AS open_rate_pct,
  ROUND(
    COUNT(DISTINCT IF(event_name = 'video_completed', user_pseudo_id, NULL))
    / NULLIF(COUNT(DISTINCT IF(event_name = 'video_opened', user_pseudo_id, NULL)), 0) * 100, 1
  ) AS completion_rate_pct,
  ROUND(
    COUNT(DISTINCT IF(event_name = 'video_cta_tapped', user_pseudo_id, NULL))
    / NULLIF(COUNT(DISTINCT IF(event_name = 'video_cta_shown', user_pseudo_id, NULL)), 0) * 100, 1
  ) AS cta_conversion_rate_pct,
  ROUND(AVG(IF(event_name IN ('video_completed', 'video_closed_early'), percent_watched, NULL)), 1) AS avg_percent_watched,
  ROUND(AVG(IF(event_name IN ('video_completed', 'video_closed_early'), seconds_watched, NULL)), 0) AS avg_seconds_watched
FROM base
GROUP BY 1, 2
ORDER BY banner_shown DESC;


-- ============================================================
-- VIDEO BANNER — Query #17: CTA breakdown (choose_program vs motivation)
-- Fuente Looker Studio: "Video Banner CTA Split"
-- ============================================================
SELECT
  MAX(IF(ep.key = 'cta_type',  ep.value.string_value, NULL)) AS cta_type,
  MAX(IF(ep.key = 'user_type', ep.value.string_value, NULL)) AS user_type,
  COUNT(DISTINCT IF(event_name = 'video_cta_shown',     user_pseudo_id, NULL)) AS cta_shown,
  COUNT(DISTINCT IF(event_name = 'video_cta_tapped',    user_pseudo_id, NULL)) AS cta_tapped,
  COUNT(DISTINCT IF(event_name = 'video_cta_dismissed', user_pseudo_id, NULL)) AS cta_dismissed,
  ROUND(
    COUNT(DISTINCT IF(event_name = 'video_cta_tapped', user_pseudo_id, NULL))
    / NULLIF(COUNT(DISTINCT IF(event_name = 'video_cta_shown', user_pseudo_id, NULL)), 0) * 100, 1
  ) AS tap_rate_pct
FROM `automatica-v2.analytics_517999677.events_combined_mat`,
UNNEST(event_params) AS ep
WHERE event_name IN ('video_cta_shown', 'video_cta_tapped', 'video_cta_dismissed')
  AND DATE(TIMESTAMP_MICROS(event_timestamp)) BETWEEN PARSE_DATE('%Y%m%d', @DS_START_DATE) AND PARSE_DATE('%Y%m%d', @DS_END_DATE)
GROUP BY
  (SELECT ep2.value.string_value FROM UNNEST(event_params) ep2 WHERE ep2.key = 'cta_type'  LIMIT 1),
  (SELECT ep3.value.string_value FROM UNNEST(event_params) ep3 WHERE ep3.key = 'user_type' LIMIT 1)
ORDER BY cta_shown DESC;


-- ============================================================
-- RETENCIÓN — Query #18: ¿Qué hace el % retenido en D7?
-- Muestra los eventos del día exacto (activity_date = install_date + 7)
-- para usuarios de una cohorte específica.
-- Cambia '2026-04-07' por la fecha de instalación que quieras analizar.
-- ============================================================
WITH cohort AS (
  SELECT
    user_pseudo_id,
    MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS install_date
  FROM `automatica-v2.analytics_517999677.events_combined_mat`
  WHERE event_name = 'first_open'
  GROUP BY 1
),
retained_d7 AS (
  SELECT DISTINCT c.user_pseudo_id
  FROM cohort c
  JOIN `automatica-v2.analytics_517999677.events_combined_mat` e
    ON c.user_pseudo_id = e.user_pseudo_id
  WHERE c.install_date = '2026-04-07'
    AND DATE(TIMESTAMP_MICROS(e.event_timestamp)) = DATE_ADD(c.install_date, INTERVAL 7 DAY)
    AND e.event_name NOT IN ('first_open', 'session_start', 'app_remove')
)
SELECT
  e.event_name,
  COUNT(DISTINCT e.user_pseudo_id)                                        AS usuarios,
  COUNT(*)                                                                 AS total_eventos,
  ROUND(COUNT(DISTINCT e.user_pseudo_id) /
    (SELECT COUNT(*) FROM retained_d7) * 100, 1)                          AS pct_del_segmento
FROM `automatica-v2.analytics_517999677.events_combined_mat` e
JOIN retained_d7 r ON e.user_pseudo_id = r.user_pseudo_id
WHERE DATE(TIMESTAMP_MICROS(e.event_timestamp)) = DATE_ADD(DATE '2026-04-07', INTERVAL 7 DAY)
  AND e.event_name NOT IN ('first_open', 'session_start', 'app_remove')
GROUP BY 1
ORDER BY usuarios DESC;
