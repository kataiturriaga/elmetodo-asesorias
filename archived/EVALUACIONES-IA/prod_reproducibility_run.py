"""
Reproducibility test: same 100 user IDs as run 2, run again, compare deltas.
Goal: show the model is NOT perfectly deterministic (temp=0.2).
"""
import requests, json, time, base64, re
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

API_BASE   = "https://api.apps.elmetodoapp.com"
GEMINI_KEY = "AIzaSyC1EqKngJ-szh3OFS4EOZIvNpr0H020Rx4"
MODEL      = "gemini-2.5-flash-lite"
HEADERS_BASE = {"X-Client-ID": "elmetodo", "Content-Type": "application/json"}

# Exact same 100 IDs from run 2
FIXED_IDS = [313,435,535,592,647,703,756,812,867,922,974,1031,1083,1138,1196,
             1250,1308,1362,1415,1476,1526,1582,1645,1703,1757,1812,1866,1923,
             1986,2043,2106,2157,2216,2270,2329,2387,2443,2524,2582,2665,2720,
             2776,2832,2899,2959,3021,3084,3137,3195,3259,3313,3374,3438,3492,
             3546,3606,3658,3713,3770,3830,3894,3954,4047,4102,4160,4217,4277,
             4331,4395,4452,4510,4572,4629,4694,4751,4827,4890,4953,5015,5077,
             5190,5259,5328,5440,5504,5569,5647,5710,5785,5878,5978,7450,7958,
             8299,8487,8568,8644,8724,8828,8915]

PROMPT_MALE = """You are a body-composition analyst for certified fitness coaches. Estimate body-fat percentage for a MALE subject from this physique photo.

Anchor to the Henselmans male visual reference scale: 5% (contest lean), 10% (visible abs), 15% (soft abs outline), 20% (no ab definition), 25% (love handles), 30% (rounded belly), 35% (prominent belly).

Primary cues: 1. Abdominal definition 2. Oblique/serratus 3. Vascularity 4. Deltoid striations 5. Lower-back/lat 6. Love-handle fat 7. Glute/leg fat

Calibration: estimates run ~1-2 points high. Shade conservative.
Uncertainty: ±3% range for clear photos.

Return ONLY valid JSON: point_estimate_bf_pct, range_low, range_high, confidence, confidence_pct, limiting_factors, visible_cues, gender_observed."""

PROMPT_FEMALE = """You are a body-composition analyst for certified fitness coaches. Estimate body-fat percentage for a FEMALE subject.

Female scale: 14-17% (athletic, visible abs), 18-22% (fit, defined waist), 23-27% (healthy, soft midsection, moderate hip/thigh fat), 28-32% (rounder lower body, waist less defined), 33-38% (pronounced curves, significant hip/thigh mass).

Primary cues: 1. Hip-to-waist ratio (MOST diagnostic) 2. Thigh/inner-thigh fat 3. Lower-ab roundness 4. Upper-arm/tricep fullness 5. Glute shape 6. Face/neck leanness
7. Visible abs in women ONLY at ≤18% — do NOT use ab absence as high BF indicator

Critical: female fat distributes to hips/thighs, not abs. Weigh lower body heavily.
Calibration: estimates run 4-5 points high. Apply firm downward adjustment.
Uncertainty: ±4% minimum range for women.

Return ONLY valid JSON: point_estimate_bf_pct, range_low, range_high, confidence, confidence_pct, limiting_factors, visible_cues, gender_observed."""

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "point_estimate_bf_pct": {"type": "NUMBER"},
        "range_low":             {"type": "NUMBER"},
        "range_high":            {"type": "NUMBER"},
        "confidence":            {"type": "STRING"},
        "confidence_pct":        {"type": "NUMBER"},
        "limiting_factors":      {"type": "ARRAY", "items": {"type": "STRING"}},
        "visible_cues":          {"type": "ARRAY", "items": {"type": "STRING"}},
        "gender_observed":       {"type": "STRING"},
    },
    "required": ["point_estimate_bf_pct","range_low","range_high",
                 "confidence","confidence_pct","gender_observed"],
}

# ── API helpers ────────────────────────────────────────────────────────────────

def get_token():
    r = requests.post(f"{API_BASE}/api/coaches/auth/login", headers=HEADERS_BASE,
                      json={"email": "kaitugraphics@outlook.com", "password": "testtest1"})
    return r.json()["access_token"]

def get_reviews(token, user_id):
    h = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_BASE}/api/admin/ai-tester/users/{user_id}/reviews", headers=h)
    return r.json().get("reviews", [])

def get_questionnaire(token, user_id):
    h = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_BASE}/api/coaches/me/users/{user_id}", headers=h)
    data = r.json()
    q = data.get("questionnaire") or {}
    return {
        "gender": q.get("gender") or "male",
        "height": q.get("height") or 175,
        "name":   data.get("name", "?"),
    }

def download_encode(url, max_edge=768):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    if HAS_PIL:
        img = PILImage.open(BytesIO(resp.content)).convert("RGB")
        w, h = img.size
        scale = max_edge / max(w, h)
        if scale < 1.0:
            img = img.resize((int(w*scale), int(h*scale)), PILImage.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode()
    return base64.b64encode(resp.content).decode()

def call_gemini(photo_url, gender, height, weight):
    prompt = PROMPT_MALE if gender == "male" else PROMPT_FEMALE
    bmi = round(weight / ((height / 100) ** 2), 1) if height and weight else None
    bmi_str = f", BMI: {bmi}" if bmi else ""
    bio = f"Sex: {gender}, Height: {height}cm, Weight: {weight}kg{bmi_str}"
    b64 = download_encode(photo_url)
    payload = {
        "system_instruction": {"parts": [{"text": prompt}]},
        "contents": [{"parts": [
            {"text": f"Client biometrics: {bio}\n\nEstimate body-fat percentage from the physique photo."},
            {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
        ]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
            "temperature": 0.2,
        },
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_KEY}"
    t0 = time.monotonic()
    r = requests.post(url, json=payload, timeout=45)
    latency_ms = int((time.monotonic() - t0) * 1000)
    r.raise_for_status()
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    result = json.loads(text)
    result["latency_ms"] = latency_ms
    return result

def process_user(args):
    token, uid, idx, total = args
    print(f"  [{idx}/{total}] id={uid}")
    try:
        q = get_questionnaire(token, uid)
        reviews = get_reviews(token, uid)
        eligible = [r for r in reviews if r.get("eligible") and r.get("photo_count", 0) >= 1]
        if not eligible:
            return {"uid": uid, "name": q["name"], "gender": q["gender"],
                    "height": q["height"], "error": "no reviews", "run2": None, "run3": None}
        review = sorted(eligible, key=lambda r: r["created_at"], reverse=True)[0]
        weight = review.get("weight") or 75
        photos = review.get("photos", [])
        if not photos:
            return {"uid": uid, "name": q["name"], "gender": q["gender"],
                    "height": q["height"], "error": "no photos", "run2": None, "run3": None}

        # Two consecutive runs, same photo, same prompt
        r2 = call_gemini(photos[0], q["gender"], q["height"], weight)
        r3 = call_gemini(photos[0], q["gender"], q["height"], weight)
        return {
            "uid": uid, "name": q["name"], "gender": q["gender"],
            "height": q["height"], "weight": weight,
            "photo": photos[0], "error": None,
            "run2": r2, "run3": r3,
        }
    except Exception as e:
        print(f"    ERROR {uid}: {e}")
        return {"uid": uid, "name": "?", "gender": "?", "error": str(e), "run2": None, "run3": None}

# ── HTML ───────────────────────────────────────────────────────────────────────

def generate_comparison_html(items):
    ok = [x for x in items if x.get("run2") and x.get("run3")]
    deltas = []
    for x in ok:
        b2 = x["run2"].get("point_estimate_bf_pct")
        b3 = x["run3"].get("point_estimate_bf_pct")
        if b2 is not None and b3 is not None:
            deltas.append(abs(b2 - b3))

    n = len(deltas)
    avg_delta  = round(sum(deltas) / n, 2) if n else 0
    max_delta  = round(max(deltas), 1) if n else 0
    exact_same = sum(1 for d in deltas if d == 0)
    within_1   = sum(1 for d in deltas if d <= 1)
    over_2     = sum(1 for d in deltas if d > 2)

    rows = ""
    for x in items:
        b2 = x.get("run2", {}) or {}
        b3 = x.get("run3", {}) or {}
        est2 = b2.get("point_estimate_bf_pct")
        est3 = b3.get("point_estimate_bf_pct")
        err  = x.get("error")

        gender = x.get("gender", "?")
        gender_icon = "♂" if gender == "male" else "♀"
        gender_color = "#60a5fa" if gender == "male" else "#f472b6"

        if est2 is None or est3 is None:
            rows += f"""
            <div class="row row-error">
              <div class="cell-name"><span class="uid">id={x['uid']}</span> {x.get('name','?')}</div>
              <div class="cell-r2">—</div>
              <div class="cell-r3">—</div>
              <div class="cell-delta">Error: {err or '?'}</div>
            </div>"""
            continue

        delta = round(est3 - est2, 1)
        abs_delta = abs(delta)
        if abs_delta == 0:
            delta_color = "#6b7280"
            delta_label = "igual"
        elif abs_delta <= 1:
            delta_color = "#22c55e"
            delta_label = f"{delta:+} pt"
        elif abs_delta <= 2:
            delta_color = "#f59e0b"
            delta_label = f"{delta:+} pts"
        else:
            delta_color = "#ef4444"
            delta_label = f"{delta:+} pts"

        rows += f"""
        <div class="row">
          <div class="cell-photo">
            <img class="thumb" src="{x.get('photo','')}" loading="lazy"
                 onerror="this.style.display='none'" />
          </div>
          <div class="cell-name">
            <span class="uid">id={x['uid']}</span>
            <span class="uname">{x.get('name','?')}</span>
            <span class="gender-chip" style="color:{gender_color}">{gender_icon}</span>
          </div>
          <div class="cell-r2">
            <span class="est">{est2}%</span>
            <span class="conf">{b2.get('confidence','')[:1].upper()}</span>
          </div>
          <div class="cell-r3">
            <span class="est">{est3}%</span>
            <span class="conf">{b3.get('confidence','')[:1].upper()}</span>
          </div>
          <div class="cell-delta">
            <span class="delta-badge" style="background:{delta_color}20;color:{delta_color};border:1px solid {delta_color}50">
              {delta_label if abs_delta > 0 else "= igual"}
            </span>
          </div>
        </div>"""

    # Distribution of deltas for bar chart
    buckets = {"0 pts (igual)": 0, "0.5–1 pt": 0, "1.5–2 pts": 0, ">2 pts": 0}
    for d in deltas:
        if d == 0: buckets["0 pts (igual)"] += 1
        elif d <= 1: buckets["0.5–1 pt"] += 1
        elif d <= 2: buckets["1.5–2 pts"] += 1
        else: buckets[">2 pts"] += 1

    bar_colors = {"0 pts (igual)": "#6b7280", "0.5–1 pt": "#22c55e", "1.5–2 pts": "#f59e0b", ">2 pts": "#ef4444"}
    bars_html = ""
    for label, count in buckets.items():
        pct = round(count / n * 100) if n else 0
        bars_html += f"""
        <div class="bar-row">
          <div class="bar-label">{label}</div>
          <div class="bar-track">
            <div class="bar-fill" style="width:{pct}%;background:{bar_colors[label]}"></div>
          </div>
          <div class="bar-count">{count} ({pct}%)</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>No determinismo IA — misma foto, dos pasadas</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f8f9fa;color:#1a1a1a}}
  .header{{background:#fff;border-bottom:2px solid #e5e7eb;padding:28px 40px}}
  .header h1{{font-size:22px;font-weight:700;color:#111}}
  .header .sub{{font-size:13px;color:#888;margin-top:4px}}
  .insight-box{{background:#fffbeb;border:1px solid #fcd34d;border-radius:10px;padding:16px 20px;margin-top:18px;font-size:13px;color:#78350f;line-height:1.6}}
  .insight-box b{{color:#92400e}}
  .kpis{{display:flex;gap:12px;margin-top:18px;flex-wrap:wrap}}
  .kpi{{background:#f3f4f6;border-radius:8px;padding:10px 18px;border:1px solid #e5e7eb}}
  .kpi b{{font-size:22px;display:block;color:#111}}
  .kpi span{{font-size:11px;color:#888}}
  .kpi.highlight b{{color:#ef4444}}
  .dist-section{{margin-top:20px}}
  .dist-section h3{{font-size:13px;font-weight:600;color:#444;margin-bottom:10px;text-transform:uppercase;letter-spacing:.05em}}
  .bar-row{{display:flex;align-items:center;gap:10px;margin-bottom:8px}}
  .bar-label{{width:120px;font-size:12px;color:#555;text-align:right}}
  .bar-track{{flex:1;height:18px;background:#e5e7eb;border-radius:4px;overflow:hidden}}
  .bar-fill{{height:100%;border-radius:4px;transition:width .3s}}
  .bar-count{{width:90px;font-size:12px;color:#555}}

  .table-wrap{{padding:24px 40px;max-width:1000px;margin:0 auto}}
  .table-header{{display:grid;grid-template-columns:60px 1fr 120px 120px 130px;gap:0;background:#f3f4f6;border:1px solid #e5e7eb;border-radius:8px 8px 0 0;padding:8px 12px;font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.05em}}
  .row{{display:grid;grid-template-columns:60px 1fr 120px 120px 130px;gap:0;background:#fff;border:1px solid #e5e7eb;border-top:none;padding:10px 12px;align-items:center}}
  .row:hover{{background:#f9fafb}}
  .row-error{{background:#fff5f5;border-color:#fecaca}}
  .row:last-child{{border-radius:0 0 8px 8px}}
  .thumb{{width:48px;height:60px;object-fit:cover;border-radius:4px;border:1px solid #e5e7eb}}
  .uid{{font-size:10px;color:#aaa;display:block}}
  .uname{{font-size:13px;font-weight:500;color:#111}}
  .gender-chip{{font-size:14px;margin-left:6px}}
  .est{{font-size:18px;font-weight:700;color:#111}}
  .conf{{font-size:11px;color:#aaa;margin-left:4px}}
  .delta-badge{{font-size:12px;font-weight:700;padding:3px 10px;border-radius:20px}}
</style>
</head>
<body>
<div class="header">
  <h1>No determinismo de la IA — misma foto, dos pasadas</h1>
  <div class="sub">Modelo: {MODEL} · Temperature: 0.2 · {time.strftime('%Y-%m-%d %H:%M')} · {n} usuarios · misma foto enviada dos veces consecutivas</div>

  <div class="insight-box">
    <b>¿Qué demuestra esto?</b> La IA no es una calculadora determinista. Con la <b>misma foto, mismo prompt y mismos datos biométricos</b>,
    el modelo puede dar resultados ligeramente distintos en cada llamada. A temperatura 0.2 la variación es pequeña pero existe —
    lo que significa que el resultado de una sola pasada tiene una incertidumbre intrínseca además de la incertidumbre del propio análisis visual.
    <br><br>
    Implicación práctica: <b>el % graso estimado por la IA debe interpretarse como un rango</b>, no como un número exacto.
    El coach puede usar esto como punto de partida y ajustar según su criterio.
  </div>

  <div class="kpis">
    <div class="kpi"><b>{n}</b><span>usuarios comparados</span></div>
    <div class="kpi"><b>{avg_delta} pts</b><span>variación media entre pasadas</span></div>
    <div class="kpi"><b>{max_delta} pts</b><span>variación máxima</span></div>
    <div class="kpi"><b>{exact_same}</b><span>resultados idénticos ({round(exact_same/n*100) if n else 0}%)</span></div>
    <div class="kpi"><b>{within_1}</b><span>variación ≤ 1 pt ({round(within_1/n*100) if n else 0}%)</span></div>
    <div class="kpi {'highlight' if over_2 > 5 else ''}"><b>{over_2}</b><span>variación > 2 pts ({round(over_2/n*100) if n else 0}%)</span></div>
  </div>

  <div class="dist-section" style="max-width:500px;margin-top:20px">
    <h3>Distribución de variaciones</h3>
    {bars_html}
  </div>
</div>

<div class="table-wrap">
  <div class="table-header">
    <div>Foto</div>
    <div>Usuario</div>
    <div>Pasada 1</div>
    <div>Pasada 2</div>
    <div>Δ diferencia</div>
  </div>
  {rows}
</div>
</body>
</html>"""

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=== Reproducibility test: same IDs, two consecutive runs ===")
    token = get_token()
    print(f"Authenticated OK. Running {len(FIXED_IDS)} users (2 Gemini calls each)...")

    args = [(token, uid, i+1, len(FIXED_IDS)) for i, uid in enumerate(FIXED_IDS)]
    items = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for result in as_completed([ex.submit(process_user, a) for a in args]):
            items.append(result.result())

    items.sort(key=lambda x: FIXED_IDS.index(x["uid"]) if x["uid"] in FIXED_IDS else 999)

    ok = [x for x in items if x.get("run2") and x.get("run3")]
    print(f"\nCompleted: {len(ok)}/{len(items)} with both runs")

    html = generate_comparison_html(items)
    out = "/Users/kataiturriaga/repos/elmetodo_asesorias/EVALUACIONES-IA/no_determinismo_ia.html"
    with open(out, "w") as f:
        f.write(html)
    print(f"→ {out}")

if __name__ == "__main__":
    main()
