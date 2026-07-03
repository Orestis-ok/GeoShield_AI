# GeoShield Pro

**Enterprise Disaster Risk Intelligence** — a professional desktop application for geographic flood, wildfire, and landslide risk analysis. Designed for a premium ($20/mo) analyst workflow.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyQt6](https://img.shields.io/badge/UI-PyQt6-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

# NOTICE

This branch is only for **TESTING**!

## Features

- **Premium auth** — branded split-screen login/signup with remember-me
- **Live weather** — Open-Meteo geocoding (lat/lon, humidity, wind, precipitation)
- **Risk engine** — composite scoring + operational recommendations per hazard
- **Interactive maps** — Leaflet pan/zoom (PyQt6-WebEngine) with analysis & disaster markers
- **History & archives** — per-user analysis log + regional disaster database
- **Science Lab** — 48h instruments, model decomposition, 24h/72h/7d projections, Chart.js series, CSV/JSON exports
- **Settings** — units, default location, map style, privacy controls, subscription panel
- **Attribution** — By Orestis Kerkines (splash, auth, footer, reports, methodology)
- **HTML reports** — export branded intelligence reports for stakeholders
- **Background processing** — non-blocking analysis via worker threads

## Screenshots

Run the app locally to explore the loading screen, auth flow, analysis dashboard, history tables, and settings panel.

## Requirements

- Python 3.10+
- Windows, macOS, or Linux
- Internet connection (weather API)

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/geoshield-desktop.git
cd geoshield-desktop

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

> **Interactive maps** require `PyQt6-WebEngine`. Without it, the app falls back to a static map preview.

## Project structure

```
geoshield-desktop/
├── main.py              # Application entry point
├── config.py            # Version and constants
├── theme.py             # Design system / styles
├── auth.py              # Local authentication
├── session.py           # Remember-me persistence
├── database.py          # SQLite disasters + history
├── weather_api.py       # Open-Meteo integration
├── risk_engine.py       # Risk scoring + recommendations
├── workers.py           # Background analysis thread
├── report_export.py     # HTML report generator
└── ui/
    ├── app_window.py    # Screen navigation
    ├── shell_page.py    # Main workspace shell
    └── views/           # Analysis, science lab, history, settings
```

## Building an executable (Windows)

From the project folder:

```powershell
.\build_exe.ps1
```

Or manually:

```bash
pip install -r requirements.txt
pyinstaller --noconfirm geoshield.spec
```

The app will be at `dist/GeoShield.exe`. Double-click to run (no terminal). User data is stored in a `data` folder **next to the executable**.

If you see `file is not a database` when running from source, delete `data/geoshield.db` and restart — the app will recreate it (or upgrade to a version that auto-repairs corrupt files).

## Data & privacy

- User accounts and analysis history are stored **locally** in `data/geoshield.db`
- Exported reports are saved to `data/reports/`
- Weather data is fetched from [Open-Meteo](https://open-meteo.com/) (no API key required)

## Disclaimer

GeoShield provides informational risk estimates for planning purposes. It is **not** a substitute for official government alerts, emergency services, or licensed professional assessment.

## License

MIT — see repository license file.
