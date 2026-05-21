"""Chart.js HTML for Science Lab time-series and forecast panels."""
import json


def hourly_chart_html(hourly: list[dict], title: str = "48-Hour Meteorological Series") -> str:
    times = [h.get("time", "")[-11:] or "" for h in hourly[:48]]
    temps = [h.get("temperature") or 0 for h in hourly[:48]]
    precs = [h.get("precipitation") or 0 for h in hourly[:48]]
    winds = [h.get("wind") or 0 for h in hourly[:48]]
    hums = [h.get("humidity") or 0 for h in hourly[:48]]

    return f"""<!DOCTYPE html><html><head>
<meta charset="utf-8"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>body{{margin:0;background:#060a10;color:#9eb0c8;font-family:Segoe UI,sans-serif}}
.wrap{{padding:16px}} h3{{color:#3b9eff;margin:0 0 12px;font-size:14px}}</style></head>
<body><div class="wrap"><h3>{title}</h3>
<canvas id="c" height="120"></canvas></div>
<script>
const ctx = document.getElementById('c');
new Chart(ctx, {{
  type: 'line',
  data: {{
    labels: {json.dumps(times)},
    datasets: [
      {{ label: 'Temp °C', data: {json.dumps(temps)}, borderColor: '#3b9eff', tension: 0.3, yAxisID: 'y' }},
      {{ label: 'Precip mm', data: {json.dumps(precs)}, borderColor: '#22c58b', backgroundColor: 'rgba(34,197,139,0.2)', fill: true, yAxisID: 'y1' }},
      {{ label: 'Wind km/h', data: {json.dumps(winds)}, borderColor: '#fbbf24', tension: 0.3, yAxisID: 'y' }},
      {{ label: 'RH %', data: {json.dumps(hums)}, borderColor: '#a78bfa', borderDash: [4,4], tension: 0.3, yAxisID: 'y2' }}
    ]
  }},
  options: {{
    responsive: true,
    interaction: {{ mode: 'index', intersect: false }},
    plugins: {{ legend: {{ labels: {{ color: '#9eb0c8' }} }} }},
    scales: {{
      x: {{ ticks: {{ color: '#5c6f88', maxTicksLimit: 12 }}, grid: {{ color: '#243550' }} }},
      y: {{ position: 'left', ticks: {{ color: '#5c6f88' }}, grid: {{ color: '#243550' }} }},
      y1: {{ position: 'right', ticks: {{ color: '#22c58b' }}, grid: {{ display: false }} }},
      y2: {{ display: false, min: 0, max: 100 }}
    }}
  }}
}});
</script></body></html>"""


def forecast_chart_html(daily: list[dict]) -> str:
    labels = [d.get("date", "")[-5:] for d in daily[:7]]
    tmax = [d.get("temp_max") or 0 for d in daily[:7]]
    tmin = [d.get("temp_min") or 0 for d in daily[:7]]
    precip = [d.get("precip_sum") or 0 for d in daily[:7]]

    return f"""<!DOCTYPE html><html><head>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>body{{margin:0;background:#060a10}} .wrap{{padding:16px}}</style></head>
<body><div class="wrap"><canvas id="f" height="100"></canvas></div>
<script>
new Chart(document.getElementById('f'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(labels)},
    datasets: [
      {{ label: 'T max °C', data: {json.dumps(tmax)}, backgroundColor: 'rgba(59,158,255,0.7)' }},
      {{ label: 'T min °C', data: {json.dumps(tmin)}, backgroundColor: 'rgba(59,158,255,0.25)' }},
      {{ label: 'Precip mm', data: {json.dumps(precip)}, type: 'line', borderColor: '#22c58b', yAxisID: 'y1' }}
    ]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ labels: {{ color: '#9eb0c8' }} }} }},
    scales: {{
      x: {{ ticks: {{ color: '#5c6f88' }}, grid: {{ color: '#243550' }} }},
      y: {{ ticks: {{ color: '#5c6f88' }}, grid: {{ color: '#243550' }} }},
      y1: {{ position: 'right', grid: {{ display: false }} }}
    }}
  }}
}});
</script></body></html>"""
