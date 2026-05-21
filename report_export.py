"""Export analysis reports to HTML."""
import os
from datetime import datetime

from config import APP_VERSION, REPORTS_DIR, AUTHOR_CREDIT, AUTHOR_NAME, MODEL_VERSION
import theme


def export_html_report(result: dict, user_name: str) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    city = result["city"]
    weather = result["weather"]
    risks = result["risks"]
    recs = result.get("recommendations", {})
    science = result.get("science", {})
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{city.replace(' ', '_')}_{ts}.html"
    path = os.path.join(REPORTS_DIR, filename)

    def risk_row(name, key):
        r = risks[key]
        color = theme.risk_color(r["level"])
        return f"""
        <tr>
          <td>{name}</td>
          <td>{r['score']:.0f}/100</td>
          <td style="color:{color};font-weight:700">{r['level'].upper()}</td>
        </tr>"""

    rec_html = "".join(
        f"<li><strong>{k.title()}:</strong> {v}</li>" for k, v in recs.items()
    )

    pred_html = ""
    for p in science.get("predictions", []):
        pred_html += (
            f"<li><strong>{p['horizon']}:</strong> Ψ={p['projected_overall']:.0f} "
            f"({p['projected_level'].upper()}), confidence {p.get('confidence_pct', 0):.0f}%</li>"
        )

    diag = science.get("diagnostics", {})
    unc = diag.get("uncertainty_band", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>GeoShield Report — {city}</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; background:#060a10; color:#f4f7fb; padding:40px; }}
    .card {{ background:#131f33; border:1px solid #243550; border-radius:14px; padding:24px; margin-bottom:20px; }}
    h1 {{ color:#3b9eff; margin:0 0 8px; }}
    table {{ width:100%; border-collapse:collapse; }}
    td, th {{ padding:10px; border-bottom:1px solid #243550; text-align:left; }}
    .muted {{ color:#9eb0c8; font-size:14px; }}
    .credit {{ color:#3b9eff; font-weight:700; margin-top:24px; }}
  </style>
</head>
<body>
  <h1>GeoShield Pro — Scientific Risk Report</h1>
  <p class="muted">Generated {datetime.now().strftime("%B %d, %Y at %H:%M")} · Analyst: {user_name} · Model {MODEL_VERSION}</p>
  <p class="credit">{AUTHOR_CREDIT}</p>
  <div class="card">
    <h2>Location: {city}</h2>
    <p>{weather.get('display_name', city)}</p>
    <p>Coordinates: {weather.get('lat', '—')}, {weather.get('lon', '—')}</p>
    <p>Elevation: {weather.get('elevation_m', 'N/A')} m · TZ: {weather.get('timezone', '')}</p>
  </div>
  <div class="card">
    <h3>Meteorological instruments</h3>
    <p>T: {weather['temperature']:.2f}°C · RH: {weather['humidity']:.1f}% · Dew: {weather.get('dewpoint_c', 0):.2f}°C<br/>
       Wind: {weather['wind_speed']:.1f} km/h (gust {weather.get('wind_gust', 0):.1f})<br/>
       Precip 24h: {weather.get('precipitation', 0):.2f} mm · Pressure: {weather.get('surface_pressure_hpa', 0):.1f} hPa<br/>
       VPD: {weather.get('vapor_pressure_deficit_kpa', 0):.3f} kPa · FWI proxy: {weather.get('fire_weather_index_proxy', 0):.1f}<br/>
       Condition: {weather.get('condition', 'N/A')}</p>
  </div>
  <div class="card">
    <h3>Risk assessment</h3>
    <table>
      <tr><th>Type</th><th>Score</th><th>Level</th></tr>
      {risk_row("Flood", "flood")}
      {risk_row("Wildfire", "fire")}
      {risk_row("Landslide", "landslide")}
    </table>
    <p><strong>Composite Ψ:</strong> {risks['overall']:.0f}/100 — {risks.get('overall_level', 'low').upper()}</p>
    <p>Uncertainty: {unc.get('overall_low', 0):.0f} – {unc.get('overall_high', 0):.0f}</p>
  </div>
  <div class="card">
    <h3>Projections</h3>
    <ul>{pred_html or '<li>See Science Lab export for full projection tables.</li>'}</ul>
  </div>
  <div class="card">
    <h3>Recommendations</h3>
    <ul>{rec_html}</ul>
  </div>
  <p class="muted">GeoShield v{APP_VERSION} — Decision-support only. Not certified for life-safety.</p>
  <p class="credit">{AUTHOR_NAME} · {AUTHOR_CREDIT}</p>
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
