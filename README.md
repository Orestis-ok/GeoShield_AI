# GeoShield_AI_V2

**Disaster Risk Intelligence Platform** — a professional desktop application for geographic flood, wildfire, and landslide risk analysis.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyQt6](https://img.shields.io/badge/UI-PyQt6-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## Features

- **Secure workspace** — local accounts with sign up / sign in and optional “remember me”
- **Live weather** — Open-Meteo geocoding and forecast (temperature, humidity, wind, precipitation)
- **Risk engine** — composite scoring for flood, wildfire, and landslide hazards
- **Historical archive** — curated disaster records by region
- **Analysis history** — per-user saved runs with timestamps
- **HTML reports** — export branded intelligence reports for stakeholders
- **Map preview** — static OpenStreetMap view for analyzed coordinates
- **Background processing** — non-blocking API calls via worker threads

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
    └── views/           # Analysis, history, settings
```

## Building an executable (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name GeoShield main.py
```

The binary will be in `dist/GeoShield.exe`.

## Data & privacy

- User accounts and analysis history are stored **locally** in `data/geoshield.db`
- Exported reports are saved to `data/reports/`
- Weather data is fetched from [Open-Meteo](https://open-meteo.com/) (no API key required)

## Disclaimer

GeoShield provides informational risk estimates for planning purposes. It is **not** a substitute for official government alerts, emergency services, or licensed professional assessment.

## License

MIT — see repository license file.
