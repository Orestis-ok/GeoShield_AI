"""Export analysis reports to HTML."""
import os
from datetime import datetime

from config import APP_VERSION, REPORTS_DIR
import theme


def export_html_report(result: dict, user_name: str) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    city = result["city"]
    weather = result["weather"]
    risks = result["risks"]
    recs = result.get("recommendations", {})
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
        f"<li><strong>{k.title()}:</strong> {v}</li>"
        for k, v in recs.items()
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>GeoShield Report — {city}</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; background:#0f1419; color:#f1f5f9; padding:40px; }}
    .card {{ background:#1e2a3a; border:1px solid #2d3f54; border-radius:12px; padding:24px; margin-bottom:20px; }}
    h1 {{ color:#0ea5e9; margin:0 0 8px; }}
    table {{ width:100%; border-collapse:collapse; }}
    td, th {{ padding:10px; border-bottom:1px solid #2d3f54; text-align:left; }}
    .muted {{ color:#94a3b8; font-size:14px; }}
  </style>
</head>
<body>
  <h1>GeoShield Risk Report</h1>
  <p class="muted">Generated {datetime.now().strftime("%B %d, %Y at %H:%M")} · Analyst: {user_name}</p>
  <div class="card">
    <h2>Location: {city}</h2>
    <p>{weather.get('display_name', city)}</p>
    <p>Coordinates: {weather.get('lat', '—')}, {weather.get('lon', '—')}</p>
  </div>
  <div class="card">
    <h3>Weather Conditions</h3>
    <p>Temperature: {weather['temperature']:.1f}°C · Humidity: {weather['humidity']}%<br/>
       Wind: {weather['wind_speed']:.1f} km/h · Precipitation (24h avg): {weather.get('precipitation', 0):.1f} mm<br/>
       Condition: {weather.get('condition', 'N/A')}</p>
  </div>
  <div class="card">
    <h3>Risk Assessment</h3>
    <table>
      <tr><th>Type</th><th>Score</th><th>Level</th></tr>
      {risk_row("Flood", "flood")}
      {risk_row("Wildfire", "fire")}
      {risk_row("Landslide", "landslide")}
    </table>
    <p><strong>Overall composite:</strong> {risks['overall']:.0f}/100 — {risks.get('overall_level', 'low').upper()}</p>
  </div>
  <div class="card">
    <h3>Recommendations</h3>
    <ul>{rec_html}</ul>
  </div>
  <p class="muted">GeoShield v{APP_VERSION} — For informational purposes. Not a substitute for official emergency services.</p>
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
