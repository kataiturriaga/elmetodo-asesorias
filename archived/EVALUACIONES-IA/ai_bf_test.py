"""
AI Body Fat Tester - Batch run 100 users, both Gemini models, generate HTML report.
"""
import requests
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

API_BASE = "https://api.apps.elmetodoapp.com"
HEADERS_BASE = {"X-Client-ID": "elmetodo", "Content-Type": "application/json"}

# --- Auth ---
def get_token():
    r = requests.post(f"{API_BASE}/api/coaches/auth/login", headers=HEADERS_BASE,
                      json={"email": "kaitugraphics@outlook.com", "password": "testtest1"})
    return r.json()["access_token"]

# --- Data fetching ---
def get_users(token, limit=150):
    h = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_BASE}/api/admin/ai-tester/users?limit={limit}", headers=h)
    return r.json()["users"]

def get_reviews(token, user_id):
    h = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_BASE}/api/admin/ai-tester/users/{user_id}/reviews", headers=h)
    data = r.json()
    return data.get("reviews", [])

def run_test(token, review_id, config_ids=[1, 2]):
    h = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}
    r = requests.post(f"{API_BASE}/api/admin/ai-tester/run", headers=h,
                      json={"review_id": review_id, "config_ids": config_ids})
    return r.json()

# --- Main batch logic ---
def get_all_users_in_range(token, id_min=300, id_max=9000):
    """Paginate through all users and return those with IDs in [id_min, id_max]."""
    h = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}
    # Get total count first
    r = requests.get(f"{API_BASE}/api/admin/ai-tester/users?limit=1", headers=h)
    total = r.json()["total"]
    print(f"Total eligible users: {total}. Paginating to find IDs {id_min}–{id_max}...")

    all_users = []
    page_size = 200
    offsets = list(range(0, total, page_size))

    def fetch_page(offset):
        r = requests.get(f"{API_BASE}/api/admin/ai-tester/users?limit={page_size}&offset={offset}", headers=h)
        return r.json().get("users", [])

    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(fetch_page, off): off for off in offsets}
        for f in as_completed(futures):
            all_users.extend(f.result())

    in_range = [u for u in all_users if id_min <= u["id"] <= id_max]
    print(f"Found {len(in_range)} eligible users with ID {id_min}–{id_max}")
    return in_range

def collect_sample(token, target=100, id_min=300, id_max=9000):
    import random
    all_in_range = get_all_users_in_range(token, id_min, id_max)
    if len(all_in_range) <= target:
        sample = all_in_range
    else:
        # Stratified: divide ID range into buckets and pick evenly
        all_in_range.sort(key=lambda u: u["id"])
        bucket_size = len(all_in_range) / target
        sample = [all_in_range[int(i * bucket_size)] for i in range(target)]
    print(f"Sample of {len(sample)} users across ID range {id_min}–{id_max}")
    return sample

def fetch_latest_review(args):
    token, user = args
    reviews = get_reviews(token, user["id"])
    eligible_reviews = [r for r in reviews if r["eligible"] and r["photo_count"] >= 3]
    if not eligible_reviews:
        return None
    latest = sorted(eligible_reviews, key=lambda r: r["created_at"], reverse=True)[0]
    return {"user": user, "review": latest}

def run_test_for_item(args):
    token, item, idx, total = args
    review_id = item["review"]["id"]
    user_name = item["user"]["name"]
    print(f"  [{idx}/{total}] Running review {review_id} for {user_name}...")
    try:
        result = run_test(token, review_id)
        return {**item, "runs": result.get("runs", []), "error": None}
    except Exception as e:
        print(f"  ERROR on review {review_id}: {e}")
        return {**item, "runs": [], "error": str(e)}

# --- HTML generation ---
def confidence_color(conf):
    return {"high": "#22c55e", "medium": "#f59e0b", "low": "#ef4444"}.get(conf, "#6b7280")

def model_label(model_id):
    return {"gemini-2.5-flash-lite": "Gemini 2.5 Flash-Lite", "gemini-3.1-flash-lite": "Gemini 3.1 Flash-Lite"}.get(model_id, model_id)

def render_run_card(run, model_color):
    if not run:
        return '<div class="run-card empty">Sin resultado</div>'

    bf = run.get("point_estimate_bf_pct")
    range_low = run.get("range_low")
    range_high = run.get("range_high")
    conf = run.get("confidence", "")
    conf_pct = run.get("confidence_pct")
    limiting = run.get("limiting_factors", [])
    cues = run.get("visible_cues", [])
    gender = run.get("gender_observed", "")
    latency = run.get("latency_ms", 0)
    cost = run.get("cost_usd", 0)
    status = run.get("status", "")

    if status != "success" or bf is None:
        error_msg = run.get("error_message") or "Error desconocido"
        return f'<div class="run-card error"><div class="run-error">Error: {error_msg[:80]}</div></div>'

    cues_html = "".join(f'<span class="tag cue">{c}</span>' for c in cues[:5])
    limiting_html = "".join(f'<span class="tag limit">{l}</span>' for l in limiting[:4])

    conf_color = confidence_color(conf)

    return f"""
    <div class="run-card" style="border-top: 3px solid {model_color}">
        <div class="run-header" style="background:{model_color}15">
            <span class="bf-pct">{bf}%</span>
            <span class="bf-range">{range_low}–{range_high}%</span>
            <span class="conf-badge" style="background:{conf_color}">{conf.upper()} {f'{conf_pct:.0f}%' if conf_pct else ''}</span>
        </div>
        <div class="gender-row">Género detectado: <b>{gender}</b> &nbsp;·&nbsp; {latency:.0f}ms &nbsp;·&nbsp; ${cost:.5f}</div>
        <div class="tags-section">
            <div class="tags-label">Indicadores visibles:</div>
            <div class="tags">{cues_html if cues_html else '<span class="tag empty-tag">—</span>'}</div>
        </div>
        <div class="tags-section">
            <div class="tags-label">Factores limitantes:</div>
            <div class="tags">{limiting_html if limiting_html else '<span class="tag ok-tag">Ninguno</span>'}</div>
        </div>
    </div>"""

def generate_html(results):
    MODEL_COLORS = {
        "gemini-2.5-flash-lite": "#4f46e5",
        "gemini-3.1-flash-lite": "#0891b2",
    }

    rows_html = ""
    for i, item in enumerate(results, 1):
        user = item["user"]
        review = item["review"]
        runs = item.get("runs", [])
        error = item.get("error")

        photos = review.get("photos", [])
        photos_html = ""
        for p in photos[:3]:
            photos_html += f'<img class="photo" src="{p}" loading="lazy" onerror="this.src=\'https://placehold.co/120x180?text=No+photo\'" />'

        # Map runs by model
        runs_by_model = {}
        for run in runs:
            mid = run.get("model_identifier", "")
            # Normalize
            mid_clean = mid.replace("gemini/", "").replace("-2024-07-18", "")
            runs_by_model[mid_clean] = run

        gem25_run = runs_by_model.get("gemini-2.5-flash-lite")
        gem31_run = runs_by_model.get("gemini-3.1-flash-lite")

        card25 = render_run_card(gem25_run, MODEL_COLORS["gemini-2.5-flash-lite"])
        card31 = render_run_card(gem31_run, MODEL_COLORS["gemini-3.1-flash-lite"])

        # Spread
        spread_html = ""
        if gem25_run and gem31_run and gem25_run.get("status") == "success" and gem31_run.get("status") == "success":
            spread = abs((gem25_run.get("point_estimate_bf_pct") or 0) - (gem31_run.get("point_estimate_bf_pct") or 0))
            spread_color = "#22c55e" if spread <= 2 else "#f59e0b" if spread <= 4 else "#ef4444"
            spread_html = f'<span class="spread-badge" style="background:{spread_color}15;color:{spread_color};border:1px solid {spread_color}40">Δ {spread:.1f}%</span>'

        rows_html += f"""
        <div class="user-row">
            <div class="user-header">
                <span class="user-num">#{i}</span>
                <span class="user-name">{user['name']}</span>
                <span class="review-meta">Review #{review['id']} · {review['type']} · {review['weight']} kg · {review['created_at'][:10]}</span>
                {spread_html}
            </div>
            <div class="user-body">
                <div class="photos-col">
                    {photos_html}
                </div>
                <div class="results-col">
                    <div class="model-label" style="color:{MODEL_COLORS['gemini-2.5-flash-lite']}">■ Gemini 2.5 Flash-Lite</div>
                    {card25}
                    <div class="model-label" style="color:{MODEL_COLORS['gemini-3.1-flash-lite']}">■ Gemini 3.1 Flash-Lite</div>
                    {card31}
                </div>
            </div>
        </div>"""

    total_cost = sum(
        (run.get("cost_usd") or 0)
        for item in results
        for run in item.get("runs", [])
        if run.get("status") == "success"
    )
    success_count = sum(1 for item in results if any(r.get("status") == "success" for r in item.get("runs", [])))

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>AI Body Fat Test — 100 usuarios</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f0f0f; color: #e5e5e5; }}
  .header {{ background: #1a1a1a; border-bottom: 1px solid #2d2d2d; padding: 24px 32px; }}
  .header h1 {{ font-size: 22px; font-weight: 700; color: #fff; }}
  .header .meta {{ font-size: 13px; color: #888; margin-top: 6px; }}
  .header .stats {{ display: flex; gap: 24px; margin-top: 12px; }}
  .stat {{ background: #252525; border-radius: 8px; padding: 8px 16px; font-size: 13px; }}
  .stat b {{ color: #fff; font-size: 16px; display: block; }}
  .legend {{ display: flex; gap: 16px; margin-top: 12px; align-items: center; }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 12px; color: #aaa; }}
  .legend-dot {{ width: 10px; height: 10px; border-radius: 2px; }}

  .container {{ padding: 16px 32px; max-width: 1400px; margin: 0 auto; }}
  .user-row {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px; margin-bottom: 16px; overflow: hidden; }}
  .user-header {{ background: #212121; padding: 10px 16px; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; border-bottom: 1px solid #2a2a2a; }}
  .user-num {{ background: #333; color: #aaa; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }}
  .user-name {{ font-weight: 600; font-size: 15px; color: #fff; }}
  .review-meta {{ font-size: 12px; color: #666; }}
  .spread-badge {{ font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; margin-left: auto; }}

  .user-body {{ display: flex; gap: 0; }}
  .photos-col {{ display: flex; flex-direction: column; gap: 4px; padding: 12px; background: #151515; min-width: 130px; border-right: 1px solid #2a2a2a; }}
  .photo {{ width: 110px; height: 140px; object-fit: cover; border-radius: 6px; border: 1px solid #333; }}
  .results-col {{ flex: 1; padding: 12px; display: flex; flex-direction: column; gap: 8px; }}

  .model-label {{ font-size: 11px; font-weight: 700; letter-spacing: 0.05em; margin-top: 4px; }}
  .run-card {{ background: #252525; border-radius: 8px; padding: 12px; border: 1px solid #333; }}
  .run-card.empty {{ color: #555; font-size: 13px; text-align: center; padding: 20px; }}
  .run-card.error {{ border-color: #ef444440; background: #1a0808; }}
  .run-error {{ color: #ef4444; font-size: 12px; }}
  .run-header {{ display: flex; align-items: center; gap: 12px; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px; }}
  .bf-pct {{ font-size: 28px; font-weight: 800; color: #fff; line-height: 1; }}
  .bf-range {{ font-size: 14px; color: #aaa; }}
  .conf-badge {{ font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 20px; color: #fff; margin-left: auto; }}
  .gender-row {{ font-size: 12px; color: #888; margin-bottom: 8px; }}
  .tags-section {{ margin-bottom: 6px; }}
  .tags-label {{ font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }}
  .tags {{ display: flex; flex-wrap: wrap; gap: 4px; }}
  .tag {{ font-size: 11px; padding: 2px 8px; border-radius: 4px; }}
  .tag.cue {{ background: #1e3a5f; color: #93c5fd; border: 1px solid #1e40af40; }}
  .tag.limit {{ background: #3d1f0a; color: #fb923c; border: 1px solid #9a3412;20; }}
  .tag.empty-tag {{ color: #555; }}
  .tag.ok-tag {{ background: #0f2e1a; color: #4ade80; border: 1px solid #16532440; }}
</style>
</head>
<body>
<div class="header">
  <h1>AI Body Fat Test — 100 usuarios</h1>
  <div class="meta">Generado el {time.strftime('%Y-%m-%d %H:%M')} · Producción elmetodo</div>
  <div class="stats">
    <div class="stat"><b>{len(results)}</b> usuarios</div>
    <div class="stat"><b>{success_count}</b> con resultados</div>
    <div class="stat"><b>${total_cost:.4f}</b> coste total</div>
    <div class="stat"><b>Gemini 2.5 + 3.1</b> Flash-Lite</div>
  </div>
  <div class="legend">
    <span style="font-size:11px;color:#666;margin-right:4px">Spread entre modelos:</span>
    <span class="legend-item"><span class="legend-dot" style="background:#22c55e"></span> ≤2%</span>
    <span class="legend-item"><span class="legend-dot" style="background:#f59e0b"></span> 2–4%</span>
    <span class="legend-item"><span class="legend-dot" style="background:#ef4444"></span> >4%</span>
  </div>
</div>
<div class="container">
{rows_html}
</div>
</body>
</html>"""

# --- Main ---
def main():
    print("=== AI Body Fat Batch Tester ===")
    token = get_token()
    print("Authenticated OK")

    users = collect_sample(token, target=100)

    print(f"\nFetching latest eligible review for each user...")
    items = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(fetch_latest_review, (token, u)): u for u in users}
        for f in as_completed(futures):
            result = f.result()
            if result:
                items.append(result)

    print(f"Got {len(items)} users with eligible reviews")

    print(f"\nRunning AI tests (both Gemini models) for {len(items)} reviews...")
    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(run_test_for_item, (token, item, i+1, len(items)))
                   for i, item in enumerate(items)]
        for f in as_completed(futures):
            results.append(f.result())

    # Sort by original order (user id desc as returned)
    results.sort(key=lambda x: x["user"]["id"], reverse=True)

    print(f"\nGenerating HTML report...")
    html = generate_html(results)

    output_path = "/Users/kataiturriaga/repos/elmetodo_asesorias/ai_bf_report.html"
    with open(output_path, "w") as f:
        f.write(html)

    success = sum(1 for item in results for run in item.get("runs", []) if run.get("status") == "success")
    total_cost = sum((run.get("cost_usd") or 0) for item in results for run in item.get("runs", []) if run.get("status") == "success")
    print(f"\n✓ Done! {len(results)} users, {success} successful runs, ${total_cost:.4f} total cost")
    print(f"→ Report: {output_path}")

if __name__ == "__main__":
    main()
