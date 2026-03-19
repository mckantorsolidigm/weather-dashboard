<!-- Workspace-specific custom instructions for Copilot -->

## Weather Dashboard Project

This is a real-time weather application for Broomfield, Colorado. 

### Project Overview
- **Framework**: Flask (Python)
- **Purpose**: Display current weather, hourly/daily forecasts, and weather alerts
- **Key Features**: Auto-refresh every hour, manual refresh button, weather alerts from NWS

### Running the Project
```bash
python app.py
```
Then navigate to `http://127.0.0.1:5000`

### Project Structure
- `app.py` - Main Flask application with weather data fetching
- `templates/index.html` - Frontend HTML
- `static/css/styles.css` - Styling
- `static/js/script.js` - Frontend JavaScript for interactivity
- `requirements.txt` - Python dependencies

### Key Technologies
- **Weather Data**: Open-Meteo API (free, no key required)
- **Alerts**: National Weather Service API (free, no key required)
- **Backend**: Flask with threading for background auto-refresh
- **Frontend**: HTML/CSS/JavaScript with responsive design

### Development Notes
- Auto-refresh runs in a background thread every 3600 seconds (1 hour)
- Manual refresh available via `/api/refresh` endpoint
- Location: Broomfield, CO (39.9165, -104.9103)
- Timezone: America/Denver
