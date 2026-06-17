"""
Production run v2: 100 stratified users, gender-specific prompts + biometric context.
Calls Gemini directly (no backend proxy). Generates HTML report.
"""
import requests, json, time, base64, os, re
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

API_BASE   = "https://api.apps.elmetodoapp.com"
GEMINI_KEY = "AIzaSyC1EqKngJ-szh3OFS4EOZIvNpr0H020Rx4"
MODEL      = "gemini-2.5-flash-lite"
HEADERS_BASE = {"X-Client-ID": "elmetodo", "Content-Type": "application/json"}

# ── Prompts ────────────────────────────────────────────────────────────────────

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
    "required": ["point_estimate_bf_pct", "range_low", "range_high",
                 "confidence", "confidence_pct", "gender_observed"],
}

# ── Auth & API helpers ─────────────────────────────────────────────────────────

def get_token():
    r = requests.post(f"{API_BASE}/api/coaches/auth/login", headers=HEADERS_BASE,
                      json={"email": "kaitugraphics@outlook.com", "password": "testtest1"})
    return r.json()["access_token"]

def get_users_page(token, limit, offset):
    h = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_BASE}/api/admin/ai-tester/users?limit={limit}&offset={offset}", headers=h)
    return r.json().get("users", [])

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
        "gender": q.get("gender"),        # "male" / "female"
        "height": q.get("height"),        # cm
        "weight": q.get("weight"),        # kg (from questionnaire)
    }

# ── Sampling ───────────────────────────────────────────────────────────────────

def collect_sample(token, target=100, id_min=300, id_max=9000):
    h = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_BASE}/api/admin/ai-tester/users?limit=1", headers=h)
    total = r.json()["total"]
    print(f"Total eligible users: {total}. Paginating for IDs {id_min}–{id_max}...")

    page_size = 200
    offsets = list(range(0, total, page_size))
    all_users = []

    def fetch_page(offset):
        return get_users_page(token, page_size, offset)

    with ThreadPoolExecutor(max_workers=10) as ex:
        for result in as_completed([ex.submit(fetch_page, off) for off in offsets]):
            all_users.extend(result.result())

    in_range = [u for u in all_users if id_min <= u["id"] <= id_max]
    in_range.sort(key=lambda u: u["id"])
    print(f"Found {len(in_range)} eligible users in range")

    if len(in_range) <= target:
        return in_range
    bucket_size = len(in_range) / target
    sample = [in_range[int(i * bucket_size)] for i in range(target)]
    print(f"Stratified sample: {len(sample)} users")
    return sample

# ── Image helpers ──────────────────────────────────────────────────────────────

def download_encode(url, max_edge=768):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    img_bytes = resp.content
    if HAS_PIL:
        from PIL import Image as PILImage
        img = PILImage.open(BytesIO(img_bytes)).convert("RGB")
        w, h = img.size
        scale = max_edge / max(w, h)
        if scale < 1.0:
            img = img.resize((int(w*scale), int(h*scale)), PILImage.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode()
    else:
        return base64.b64encode(img_bytes).decode()

# ── Gemini call ────────────────────────────────────────────────────────────────

def call_gemini(photo_url, gender, height, weight):
    prompt = PROMPT_MALE if gender == "male" else PROMPT_FEMALE
    bmi = round(weight / ((height / 100) ** 2), 1) if height and weight else None
    bmi_str = f", BMI: {bmi}" if bmi else ""
    biometric_context = f"Sex: {gender}, Height: {height}cm, Weight: {weight}kg{bmi_str}"

    b64 = download_encode(photo_url)
    payload = {
        "system_instruction": {"parts": [{"text": prompt}]},
        "contents": [{
            "parts": [
                {"text": f"Client biometrics: {biometric_context}\n\nEstimate body-fat percentage from the physique photo."},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
            ]
        }],
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
    result["prompt_used"] = "male" if gender == "male" else "female"
    result["biometric_context"] = biometric_context
    result["bmi"] = bmi
    return result

# ── Per-user fetch & run ───────────────────────────────────────────────────────

def process_user(args):
    token, user, idx, total = args
    uid = user["id"]
    name = user["name"]
    print(f"  [{idx}/{total}] {name} (id={uid})")
    try:
        reviews = get_reviews(token, uid)
        eligible = [r for r in reviews if r.get("eligible") and r.get("photo_count", 0) >= 1]
        if not eligible:
            return {"user": user, "error": "no eligible reviews", "result": None, "questionnaire": {}, "review": None}
        review = sorted(eligible, key=lambda r: r["created_at"], reverse=True)[0]

        q = get_questionnaire(token, uid)
        gender = q.get("gender") or "male"
        height = q.get("height") or 175
        weight = review.get("weight") or q.get("weight") or 75

        photos = review.get("photos", [])
        if not photos:
            return {"user": user, "error": "no photos", "result": None, "questionnaire": q, "review": review}

        # Use first photo (front)
        result = call_gemini(photos[0], gender, height, weight)
        return {
            "user": user,
            "review": review,
            "questionnaire": q,
            "result": result,
            "all_photos": photos[:3],
            "error": None,
        }
    except Exception as e:
        print(f"    ERROR {uid}: {e}")
        return {"user": user, "error": str(e), "result": None, "questionnaire": {}, "review": None}

# ── HTML generation ────────────────────────────────────────────────────────────

def conf_color(c):
    return {"high": "#22c55e", "medium": "#f59e0b", "low": "#ef4444"}.get(c or "", "#6b7280")

def generate_html(items, run_label="2"):
    ok = [x for x in items if x.get("result")]
    estimates = [x["result"]["point_estimate_bf_pct"] for x in ok if x["result"].get("point_estimate_bf_pct") is not None]
    males   = [x for x in ok if x.get("questionnaire", {}).get("gender") == "male"]
    females = [x for x in ok if x.get("questionnaire", {}).get("gender") == "female"]
    avg_all    = round(sum(estimates) / len(estimates), 1) if estimates else "—"
    avg_male   = round(sum(x["result"]["point_estimate_bf_pct"] for x in males) / len(males), 1) if males else "—"
    avg_female = round(sum(x["result"]["point_estimate_bf_pct"] for x in females) / len(females), 1) if females else "—"

    rows_html = ""
    for i, item in enumerate(items, 1):
        user = item["user"]
        q    = item.get("questionnaire") or {}
        rev  = item.get("review") or {}
        res  = item.get("result")
        err  = item.get("error")
        photos = item.get("all_photos", [])

        photos_html = "".join(
            f'<img class="photo" src="{p}" loading="lazy" onerror="this.src=\'https://placehold.co/110x140?text=no+photo\'" />'
            for p in photos
        )

        gender  = q.get("gender", "?")
        height  = q.get("height", "?")
        weight  = rev.get("weight") or q.get("weight", "?")
        bmi     = res.get("bmi") if res else None
        bmi_str = f" · IMC {bmi}" if bmi else ""
        gender_icon = "♂" if gender == "male" else "♀" if gender == "female" else "?"
        gender_color = "#60a5fa" if gender == "male" else "#f472b6"

        if res:
            bf       = res.get("point_estimate_bf_pct")
            r_low    = res.get("range_low")
            r_high   = res.get("range_high")
            conf     = res.get("confidence", "")
            conf_pct = res.get("confidence_pct")
            cues     = res.get("visible_cues", [])
            limiting = res.get("limiting_factors", [])
            latency  = res.get("latency_ms", 0)
            prompt_used = res.get("prompt_used", gender)
            bio_ctx  = res.get("biometric_context", "")

            cues_html = "".join(f'<span class="tag cue">{c}</span>' for c in cues[:5])
            lim_html  = "".join(f'<span class="tag lim">{l}</span>' for l in limiting[:4])
            cc = conf_color(conf)

            result_html = f"""
            <div class="result-card">
              <div class="result-header">
                <span class="bf-big">{bf}%</span>
                <span class="bf-range">{r_low}–{r_high}%</span>
                <span class="conf-badge" style="background:{cc}">{(conf or '').upper()} {f'{conf_pct:.0f}%' if conf_pct else ''}</span>
                <span class="latency">{latency}ms</span>
              </div>
              <div class="bio-ctx">{bio_ctx} · prompt: {prompt_used}</div>
              <div class="tags">{cues_html or '<span class="tag empty">—</span>'}</div>
              <div class="tags">{lim_html}</div>
            </div>"""
        else:
            result_html = f'<div class="result-card error">Error: {err or "unknown"}</div>'

        rows_html += f"""
        <div class="user-row">
          <div class="user-header">
            <span class="num">#{i}</span>
            <span class="uname">{user['name']}</span>
            <span class="umeta">id={user['id']} · {gender_icon} {gender} · {height}cm · {weight}kg{bmi_str}</span>
            <span class="gender-chip" style="background:{gender_color}20;color:{gender_color};border:1px solid {gender_color}40">{gender_icon} {gender}</span>
          </div>
          <div class="user-body">
            <div class="photos-col">{photos_html}</div>
            <div class="results-col">{result_html}</div>
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>100 usuarios · prompt género + altura/peso · run {run_label}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f0f0f;color:#e5e5e5}}
  .header{{background:#1a1a1a;border-bottom:1px solid #2d2d2d;padding:24px 32px}}
  .header h1{{font-size:20px;font-weight:700;color:#fff}}
  .header .sub{{font-size:13px;color:#888;margin-top:4px}}
  .kpis{{display:flex;gap:16px;margin-top:16px;flex-wrap:wrap}}
  .kpi{{background:#252525;border-radius:8px;padding:10px 18px}}
  .kpi b{{color:#fff;font-size:20px;display:block}}
  .kpi span{{font-size:12px;color:#888}}
  .methodology{{background:#1e2a1e;border:1px solid #2d4a2d;border-radius:8px;padding:14px 18px;margin-top:16px;font-size:12px;color:#aaa;line-height:1.6}}
  .methodology b{{color:#86efac}}
  .container{{padding:16px 32px;max-width:1200px;margin:0 auto}}
  .user-row{{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;margin-bottom:14px;overflow:hidden}}
  .user-header{{background:#212121;padding:10px 16px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;border-bottom:1px solid #2a2a2a}}
  .num{{background:#333;color:#aaa;font-size:11px;padding:2px 8px;border-radius:4px;font-weight:600}}
  .uname{{font-weight:600;font-size:15px;color:#fff}}
  .umeta{{font-size:12px;color:#666}}
  .gender-chip{{font-size:11px;padding:2px 8px;border-radius:4px;font-weight:600;margin-left:auto}}
  .user-body{{display:flex}}
  .photos-col{{display:flex;flex-direction:column;gap:4px;padding:12px;background:#151515;min-width:130px;border-right:1px solid #2a2a2a}}
  .photo{{width:110px;height:140px;object-fit:cover;border-radius:6px;border:1px solid #333}}
  .results-col{{flex:1;padding:12px}}
  .result-card{{background:#252525;border-radius:8px;padding:12px;border:1px solid #333}}
  .result-card.error{{background:#1a0808;border-color:#ef444440;color:#ef4444;font-size:13px}}
  .result-header{{display:flex;align-items:center;gap:12px;margin-bottom:8px}}
  .bf-big{{font-size:32px;font-weight:800;color:#fff;line-height:1}}
  .bf-range{{font-size:14px;color:#aaa}}
  .conf-badge{{font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;color:#fff}}
  .latency{{font-size:11px;color:#555;margin-left:auto}}
  .bio-ctx{{font-size:11px;color:#666;margin-bottom:8px;font-family:monospace}}
  .tags{{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px}}
  .tag{{font-size:11px;padding:2px 8px;border-radius:4px}}
  .tag.cue{{background:#1e3a5f;color:#93c5fd;border:1px solid #1e40af40}}
  .tag.lim{{background:#3d1f0a;color:#fb923c}}
  .tag.empty{{color:#444}}
</style>
</head>
<body>
<div class="header">
  <h1>100 usuarios · prompt género + altura/peso · run {run_label}</h1>
  <div class="sub">Modelo: {MODEL} · Temperature: 0.2 · {time.strftime('%Y-%m-%d %H:%M')} · Gemini directo (sin proxy backend)</div>
  <div class="kpis">
    <div class="kpi"><b>{len(ok)}</b><span>usuarios procesados</span></div>
    <div class="kpi"><b>{len(males)}</b><span>hombres</span></div>
    <div class="kpi"><b>{len(females)}</b><span>mujeres</span></div>
    <div class="kpi"><b>{avg_all}%</b><span>media estimada (todos)</span></div>
    <div class="kpi"><b style="color:#60a5fa">{avg_male}%</b><span>media hombres</span></div>
    <div class="kpi"><b style="color:#f472b6">{avg_female}%</b><span>media mujeres</span></div>
  </div>
  <div class="methodology">
    <b>Metodología:</b> Muestra estratificada de 100 usuarios reales (IDs 300–9000). Género, altura y peso obtenidos del cuestionario vía API. Foto principal de la revisión más reciente enviada a Gemini con contexto biométrico.
    Prompt ♂: escala Henselmans / calibración −1-2 pts. Prompt ♀: escala femenina / calibración −4-5 pts.
    Sin corrección post-procesado aplicada.
  </div>
</div>
<div class="container">
{rows_html}
</div>
</body>
</html>"""

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=== Production run: gender prompts + biometric context ===")
    token = get_token()
    print("Authenticated OK")

    sample = collect_sample(token, target=100)

    print(f"\nProcessing {len(sample)} users (concurrent 10)...")
    items = []
    args = [(token, u, i+1, len(sample)) for i, u in enumerate(sample)]
    with ThreadPoolExecutor(max_workers=10) as ex:
        for result in as_completed([ex.submit(process_user, a) for a in args]):
            items.append(result.result())

    items.sort(key=lambda x: x["user"]["id"])

    ok = [x for x in items if x.get("result")]
    print(f"\nCompleted: {len(ok)}/{len(items)} successful")

    html = generate_html(items, run_label="2")
    out = "/Users/kataiturriaga/repos/elmetodo_asesorias/EVALUACIONES-IA/100_usuarios_promptgenero_alturaxpeso-2.html"
    with open(out, "w") as f:
        f.write(html)
    print(f"→ {out}")

if __name__ == "__main__":
    main()
