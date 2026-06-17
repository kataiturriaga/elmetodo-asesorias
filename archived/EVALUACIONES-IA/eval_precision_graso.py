"""
Evaluación de precisión del modelo de IA para % graso.
Usa las fotos de samples-%-graso/ como ground truth.
"""
import os, re, base64, json, time
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image
import requests

API_KEY = "AIzaSyC1EqKngJ-szh3OFS4EOZIvNpr0H020Rx4"
MODEL   = "gemini-2.5-flash-lite"
SAMPLES = "/Users/kataiturriaga/repos/elmetodo_asesorias/samples-%-graso"

SYSTEM_PROMPT = """You are a body-composition analyst assisting certified fitness coaches. Estimate body-fat percentage from the physique photo provided. Anchor to the Henselmans visual reference scale (5, 10, 15, 20, 25, 30, 35% BF) and interpolate to a specific number — do not round to the nearest anchor.

Based on validated reference photos, your estimates for lean-to-medium subjects (below 25% BF) tend to run 2–3 points high. Adjust your point estimate conservatively when in doubt.

Read these cues: abdominal definition and separation, oblique/serratus visibility, vascularity, deltoid and arm striations, lower-back and lat detail, love-handle and lower-ab fat, and glute/thigh fat. Weigh the abdomen and waist most for men, the hips and thighs for women.

Be calibrated, not flattering: report what the photo shows. The range must honestly reflect uncertainty (typically ±3% for a clear male photo, ±5% or more for female or imperfect photos).

Return ONLY valid JSON with these fields: point_estimate_bf_pct (number), range_low (number), range_high (number), confidence ("low"|"medium"|"high"), confidence_pct (number 0-100), limiting_factors (array of strings), visible_cues (array of strings), gender_observed ("male"|"female"|"unclear"). Never return null for numeric fields."""

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


def resize_encode(path, max_edge=768):
    with Image.open(path) as img:
        img = img.convert("RGB")
        w, h = img.size
        scale = max_edge / max(w, h)
        if scale < 1.0:
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode()


def call_model(photo_path, ground_truth_pct):
    b64 = resize_encode(photo_path)
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{
            "parts": [
                {"text": "One physique photo follows. Estimate body-fat percentage."},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
            ]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
            "temperature": 0.2,
        },
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    t0 = time.monotonic()
    r = requests.post(url, json=payload, timeout=40)
    latency_ms = int((time.monotonic() - t0) * 1000)
    r.raise_for_status()

    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    result = json.loads(text)
    estimated = result.get("point_estimate_bf_pct")

    return {
        "photo":            os.path.basename(photo_path),
        "ground_truth":     ground_truth_pct,
        "estimated":        estimated,
        "range_low":        result.get("range_low"),
        "range_high":       result.get("range_high"),
        "confidence":       result.get("confidence"),
        "confidence_pct":   result.get("confidence_pct"),
        "gender_observed":  result.get("gender_observed"),
        "limiting_factors": result.get("limiting_factors", []),
        "visible_cues":     result.get("visible_cues", []),
        "error":            round(estimated - ground_truth_pct, 1) if estimated is not None else None,
        "latency_ms":       latency_ms,
        "status":           "success",
    }


def run_item(args):
    idx, total, path, pct = args
    name = os.path.basename(path)
    print(f"  [{idx}/{total}] {name} (GT: {pct}%)")
    try:
        return call_model(path, pct)
    except Exception as e:
        print(f"    ERROR: {e}")
        return {"photo": name, "ground_truth": pct, "status": "failed", "error_msg": str(e)}


def load_samples():
    files = sorted(os.listdir(SAMPLES))
    items = []
    for f in files:
        m = re.match(r'^(\d+)', f)
        if m and f.lower().endswith(('.jpg', '.jpeg', '.png')):
            items.append((int(m.group(1)), os.path.join(SAMPLES, f)))
    return items  # [(pct, path), ...]


# ── Metrics ────────────────────────────────────────────────────────────────────

def compute_metrics(results):
    ok = [r for r in results if r.get("status") == "success" and r.get("error") is not None]
    errors = [r["error"] for r in ok]
    n = len(errors)
    if n == 0:
        return {}
    mae   = round(sum(abs(e) for e in errors) / n, 2)
    bias  = round(sum(errors) / n, 2)
    rmse  = round((sum(e**2 for e in errors) / n) ** 0.5, 2)
    w2    = round(sum(1 for e in errors if abs(e) <= 2) / n * 100, 1)
    w5    = round(sum(1 for e in errors if abs(e) <= 5) / n * 100, 1)

    ranges = [("8–15%", 8, 15), ("16–24%", 16, 24), ("25–38%", 25, 38)]
    by_range = []
    for label, lo, hi in ranges:
        sub = [r for r in ok if lo <= r["ground_truth"] <= hi]
        if sub:
            se = [r["error"] for r in sub]
            by_range.append({
                "range": label,
                "n": len(se),
                "mae": round(sum(abs(e) for e in se) / len(se), 2),
                "bias": round(sum(se) / len(se), 2),
            })

    return {"n": n, "mae": mae, "bias": bias, "rmse": rmse,
            "within_2pct": w2, "within_5pct": w5, "by_range": by_range}


# ── HTML report ────────────────────────────────────────────────────────────────

def error_color(e):
    if e is None: return "#6b7280"
    ae = abs(e)
    if ae <= 2: return "#22c55e"
    if ae <= 4: return "#f59e0b"
    return "#ef4444"

def conf_color(c):
    return {"high": "#22c55e", "medium": "#f59e0b", "low": "#ef4444"}.get(c or "", "#6b7280")

def generate_html(results, metrics):
    rows = ""
    for r in results:
        pct   = r.get("ground_truth", "?")
        est   = r.get("estimated")
        err   = r.get("error")
        conf  = r.get("confidence", "")
        cpct  = r.get("confidence_pct")
        lim   = r.get("limiting_factors", [])
        cues  = r.get("visible_cues", [])
        photo = r.get("photo", "")
        photo_path = os.path.join(SAMPLES, photo)
        gender = r.get("gender_observed", "")

        # Embed photo as base64
        try:
            b64_img = resize_encode(photo_path, max_edge=300)
            img_src = f"data:image/jpeg;base64,{b64_img}"
        except Exception:
            img_src = ""

        ec = error_color(err)
        cc = conf_color(conf)
        status = r.get("status", "failed")

        if status != "success":
            rows += f"""
            <div class="row error-row">
              <img class="photo" src="{img_src}" />
              <div class="data">
                <div class="photo-name">{photo}</div>
                <div style="color:#ef4444">Error: {r.get('error_msg','')}</div>
              </div>
            </div>"""
            continue

        cues_html  = "".join(f'<span class="tag cue">{c}</span>' for c in cues[:4])
        lim_html   = "".join(f'<span class="tag lim">{l}</span>' for l in lim[:3])

        rows += f"""
        <div class="row">
          <img class="photo" src="{img_src}" />
          <div class="data">
            <div class="top-line">
              <span class="filename">{photo}</span>
              <span class="gt">GT: <b>{pct}%</b></span>
              <span class="est">IA: <b>{est}%</b></span>
              <span class="error-badge" style="background:{ec}20;color:{ec};border:1px solid {ec}50">
                {"+" if err and err > 0 else ""}{err} pts
              </span>
              <span class="conf-badge" style="background:{cc}">
                {(conf or "").upper()} {f'{cpct:.0f}%' if cpct else ''}
              </span>
              <span class="gender">{gender}</span>
            </div>
            <div class="tags">{cues_html}</div>
            <div class="tags">{lim_html}</div>
          </div>
        </div>"""

    br = metrics.get("by_range", [])
    range_rows = "".join(
        f"<tr><td>{b['range']}</td><td>{b['n']}</td><td>{b['mae']}</td>"
        f"<td style='color:{'#ef4444' if b['bias']>0 else '#22c55e'}'>{'+' if b['bias']>0 else ''}{b['bias']}</td></tr>"
        for b in br
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<title>Evaluación precisión IA % graso</title>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:#0f0f0f; color:#e5e5e5; }}
  .header {{ background:#1a1a1a; border-bottom:1px solid #2d2d2d; padding:24px 32px; }}
  .header h1 {{ font-size:20px; font-weight:700; color:#fff; }}
  .header .sub {{ font-size:13px; color:#888; margin-top:4px; }}
  .kpis {{ display:flex; gap:16px; margin-top:16px; flex-wrap:wrap; }}
  .kpi {{ background:#252525; border-radius:8px; padding:10px 18px; }}
  .kpi b {{ color:#fff; font-size:20px; display:block; }}
  .kpi span {{ font-size:12px; color:#888; }}
  .range-table {{ margin-top:16px; border-collapse:collapse; font-size:13px; }}
  .range-table th {{ color:#888; text-align:left; padding:4px 16px 4px 0; border-bottom:1px solid #333; }}
  .range-table td {{ padding:4px 16px 4px 0; }}
  .legend {{ display:flex; gap:16px; margin-top:12px; align-items:center; font-size:12px; color:#888; }}
  .legend-dot {{ width:10px; height:10px; border-radius:2px; display:inline-block; margin-right:4px; }}

  .container {{ padding:16px 32px; max-width:1100px; margin:0 auto; }}
  .row {{ display:flex; gap:16px; background:#1a1a1a; border:1px solid #2a2a2a; border-radius:10px;
          margin-bottom:10px; padding:12px; align-items:flex-start; }}
  .row.error-row {{ border-color:#ef444430; }}
  .photo {{ width:100px; height:130px; object-fit:cover; border-radius:6px; flex-shrink:0; border:1px solid #333; }}
  .data {{ flex:1; }}
  .top-line {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:8px; }}
  .filename {{ font-size:12px; color:#666; }}
  .gt {{ font-size:14px; color:#aaa; }}
  .est {{ font-size:14px; color:#fff; }}
  .error-badge {{ font-size:12px; font-weight:700; padding:2px 10px; border-radius:20px; }}
  .conf-badge {{ font-size:11px; font-weight:700; padding:2px 8px; border-radius:4px; color:#fff; }}
  .gender {{ font-size:11px; color:#555; margin-left:auto; }}
  .tags {{ display:flex; flex-wrap:wrap; gap:4px; margin-top:4px; }}
  .tag {{ font-size:11px; padding:2px 7px; border-radius:4px; }}
  .tag.cue {{ background:#1e3a5f; color:#93c5fd; }}
  .tag.lim {{ background:#3d1f0a; color:#fb923c; }}
</style>
</head>
<body>
<div class="header">
  <h1>Evaluación de precisión — IA % graso</h1>
  <div class="sub">Modelo: {MODEL} · {metrics.get('n', 0)} fotos evaluadas · {time.strftime('%Y-%m-%d %H:%M')}</div>
  <div class="kpis">
    <div class="kpi"><b>{metrics.get('mae','—')}</b><span>Error medio (MAE)</span></div>
    <div class="kpi"><b style="color:{'#ef4444' if (metrics.get('bias') or 0)>0 else '#22c55e'}">{'+' if (metrics.get('bias') or 0)>0 else ''}{metrics.get('bias','—')}</b><span>Sesgo (+ sobreestima)</span></div>
    <div class="kpi"><b>{metrics.get('rmse','—')}</b><span>RMSE</span></div>
    <div class="kpi"><b>{metrics.get('within_2pct','—')}%</b><span>Fotos con error ≤ 2 pts</span></div>
    <div class="kpi"><b>{metrics.get('within_5pct','—')}%</b><span>Fotos con error ≤ 5 pts</span></div>
  </div>
  <table class="range-table">
    <tr><th>Franja</th><th>Fotos</th><th>MAE</th><th>Sesgo</th></tr>
    {range_rows}
  </table>
  <div class="legend">
    <span>Error:</span>
    <span><span class="legend-dot" style="background:#22c55e"></span>≤ 2 pts</span>
    <span><span class="legend-dot" style="background:#f59e0b"></span>3–4 pts</span>
    <span><span class="legend-dot" style="background:#ef4444"></span>≥ 5 pts</span>
  </div>
</div>
<div class="container">{rows}</div>
</body>
</html>"""


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    print("=== Evaluación precisión IA % graso ===")
    samples = load_samples()
    print(f"Fotos encontradas: {len(samples)} ({min(p for p,_ in samples)}%–{max(p for p,_ in samples)}%)")

    tasks = [(i+1, len(samples), path, pct) for i, (pct, path) in enumerate(samples)]

    results = []
    print(f"\nEjecutando con {MODEL} (concurrencia 6)...")
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = [ex.submit(run_item, t) for t in tasks]
        for f in as_completed(futures):
            results.append(f.result())

    results.sort(key=lambda r: (r.get("ground_truth", 0), r.get("photo", "")))

    metrics = compute_metrics(results)
    print(f"\n── Métricas ──────────────────────────")
    print(f"  Fotos evaluadas: {metrics.get('n')}")
    print(f"  MAE:             {metrics.get('mae')} puntos")
    print(f"  Sesgo:           {metrics.get('bias')} (+ sobreestima)")
    print(f"  RMSE:            {metrics.get('rmse')}")
    print(f"  Error ≤ 2 pts:   {metrics.get('within_2pct')}%")
    print(f"  Error ≤ 5 pts:   {metrics.get('within_5pct')}%")
    for b in metrics.get("by_range", []):
        print(f"  {b['range']}: MAE={b['mae']} sesgo={b['bias']:+} (n={b['n']})")

    output = "/Users/kataiturriaga/repos/elmetodo_asesorias/eval_precision_report.html"
    with open(output, "w") as f:
        f.write(generate_html(results, metrics))
    print(f"\nInforme: {output}")

if __name__ == "__main__":
    main()
