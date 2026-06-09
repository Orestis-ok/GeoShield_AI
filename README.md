# GeoShield AI

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyQt6](https://img.shields.io/badge/UI-PyQt6-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

GeoShield AI / GeoShield Pro is a Python desktop application for live disaster-risk intelligence. It combines Open-Meteo weather and geocoding data with a local tri-hazard model to estimate flood, wildfire, landslide, and composite regional risk.

The current version is a PyQt6 desktop app with authentication, saved analysis history, an interactive map, science-oriented diagnostics, and export tools for reports and research data.

## Features

- Live location lookup through Open-Meteo geocoding
- Real-time weather ingestion with current, hourly, and 7-day forecast fields
- Tri-hazard risk model for:
  - Flood risk
  - Wildfire risk
  - Landslide risk
  - Composite risk index
- Operational recommendations based on current hazard levels
- Local user signup/login with SQLite-backed accounts
- Per-user analysis history
- Seeded regional disaster archive for comparison
- Interactive map view using PyQt6 WebEngine
- Science Lab with:
  - Meteorological instrument panel
  - Model factor decomposition
  - 24-hour, 72-hour, and 7-day projections
  - Diagnostics and uncertainty bands
  - Variable correlations
  - Methodology text
- HTML report export for stakeholder-ready summaries
- JSON and CSV exports for scientific/research workflows
- Preferences for default location, map style, remembered sessions, and report behavior
- Windows executable build support through PyInstaller

## Tech Stack

- Python 3.10+
- PyQt6
- PyQt6-WebEngine
- SQLite
- requests
- Open-Meteo Forecast API
- Open-Meteo Geocoding API
- PyInstaller

## Requirements

- Python 3.10 or newer
- Internet connection for live weather and geocoding data
- A desktop OS capable of running PyQt6

Install dependencies from:

```bash
pip install -r requirements.txt
Current dependencies:

PyQt6>=6.6.1
PyQt6-WebEngine>=6.6.0
requests>=2.31.0
pyinstaller>=6.10.0
Installation
Clone the repository:

git clone https://github.com/Orestis-ok/GeoShield_AI.git
cd GeoShield_AI
Create and activate a virtual environment:

python -m venv venv
On Windows:

venv\Scripts\activate
On macOS/Linux:

source venv/bin/activate
Install dependencies:

pip install -r requirements.txt
Run the app:

python main.py
How It Works
The user enters a city, region, or location.
GeoShield geocodes the location through Open-Meteo.
The app fetches current weather, hourly instrument data, and 7-day forecast data.
The risk engine calculates flood, wildfire, landslide, and composite scores.
The science engine builds model diagnostics, forecast projections, correlations, and uncertainty ranges.
Results are shown in the desktop interface and can be saved/exported.
Risk Model
GeoShield uses an empirical composite model named:

GS-RM-2.1 — Tri-Hazard Composite Engine
Hazard weights:

Flood:     0.35
Wildfire:  0.35
Landslide: 0.30
Composite formula:

Ψ = 0.35 * S_flood + 0.35 * S_fire + 0.30 * S_landslide
Risk levels:

Low:      < 40
Moderate: 40-59
High:     60-74
Critical: >= 75
The model is intended for decision support and planning, not certified emergency forecasting.

Project structure
GeoShield_AI/
├── main.py                  # Application entry point
├── config.py                # App metadata, paths, constants, model version
├── theme.py                 # Global styling and design helpers
├── auth.py                  # Local authentication
├── session.py               # Remember-me session persistence
├── database.py              # SQLite users, disasters, and analysis history
├── weather_api.py           # Open-Meteo geocoding and weather integration
├── risk_engine.py           # Hazard scoring and recommendations
├── science_engine.py        # Model diagnostics, projections, methodology
├── workers.py               # Background analysis worker thread
├── report_export.py         # HTML report export
├── data_export.py           # JSON/CSV science exports
├── build_exe.ps1            # Windows executable build script
├── geoshield.spec           # PyInstaller configuration
├── requirements.txt
├── assets/
│   └── icon.ico
├── data/
│   ├── geoshield.db
│   ├── session.json
│   ├── prefrences.json
│   ├── reports/
│   └── science_reports/
└── ui/
    ├── app_window.py
    ├── auth_layout.py
    ├── dashboard_page.py
    ├── loading_screen.py
    ├── login_page.py
    ├── signup_page.py
    ├── shell_page.py
    ├── map_widget.py
    ├── science_charts.py
    ├── widgets.py
    └── views/
        ├── analysis_view.py
        ├── science_view.py
        ├── history_view.py
        └── settings_view.py
Data Storage
GeoShield stores user data locally.

data/geoshield.db        Local SQLite database
data/session.json        Remembered session state
data/prefrences.json     User preferences
data/reports/            Exported HTML reports
data/science_exports/    Generated JSON/CSV science exports
The database is created automatically if missing or repaired if the existing file is invalid.

Exports
GeoShield can export:

HTML intelligence reports
Full scientific JSON packages
Hourly weather CSV files
7-day forecast CSV files
HTML reports are saved to:

data/reports/
Science exports are saved to:

data/science_exports/
Building a Windows Executable
Run:

.\build_exe.ps1
The script installs dependencies and builds the app using PyInstaller.

Output:

dist/GeoShield.exe
When running as an executable, GeoShield creates and uses a data folder next to the executable for accounts, sessions, preferences, history, and exports.

Notes
The app requires internet access to fetch live Open-Meteo weather data.
If weather data cannot be retrieved, check the location name and network connection.
PyQt6-WebEngine is required for the interactive map.
The repository currently uses the app name GeoShield Pro internally.
Disclaimer
GeoShield AI is a decision-support and educational risk-intelligence tool. It is not a replacement for official emergency alerts, civil protection authorities, certified hydrometeorological forecasts, or professional engineering/geotechnical assessment.

For life-safety decisions, always follow official local and national emergency guidance.

