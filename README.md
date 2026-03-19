# Weather Dashboard - Broomfield, Colorado

A real-time weather application for Broomfield, Colorado with hourly auto-refresh, manual refresh capability, and weather alerts.

## Features

- ☀️ **Current Weather**: Temperature, feels like, humidity, wind speed, and precipitation
- 📊 **Hourly Forecast**: Next 12 hours of weather with precipitation probability
- 📅 **7-Day Forecast**: Extended forecast with high/low temperatures and conditions
- ⚠️ **Weather Alerts**: Real-time weather alerts from the National Weather Service
- 🔄 **Auto-Refresh**: Weather data updates automatically every hour
- 🖱️ **Manual Refresh**: Refresh weather data on demand with a button click

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: 
  - Open-Meteo (weather data) - Free, no API key required
  - National Weather Service API (alerts) - Free, no API key required

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "Weather app"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to: `http://127.0.0.1:5000`

3. **View the weather dashboard**
   - Current weather conditions are displayed prominently
   - Hourly forecast shows the next 12 hours
   - 7-day forecast for extended planning
   - Any active weather alerts appear at the top

## How It Works

- **Auto-Refresh**: The application automatically fetches updated weather data every 60 minutes (3600 seconds)
- **Manual Refresh**: Click the "🔄 Refresh Now" button to get the latest weather data immediately
- **Weather Alerts**: Alerts are fetched from the National Weather Service for the Broomfield area
- **Temperature Unit**: All temperatures are displayed in Fahrenheit
- **Wind Speed**: Wind speeds are shown in miles per hour (mph)

## Project Structure

```
Weather app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # HTML template for the dashboard
├── static/
│   ├── css/
│   │   └── styles.css    # CSS styling
│   └── js/
│       └── script.js     # JavaScript for interactivity
└── README.md             # This file
```

## API Endpoints

- **GET `/`** - Serve the main dashboard page
- **GET `/api/weather`** - Return current weather data (JSON)
- **GET `/api/refresh`** - Manually refresh weather data (JSON)

## Dependencies

- **Flask**: Web framework
- **requests**: HTTP library for API calls
- **Werkzeug**: Utility library (included with Flask)

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, you can modify the port in `app.py`:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Change 5000 to another port
```

### API Request Errors
The application gracefully handles API failures. If the Open-Meteo API or NWS API is unavailable, it will cache the last known data or display an error message.

### Weather Data Not Updating
- Check your internet connection
- Verify that the Open-Meteo and NWS APIs are accessible
- Check the Flask console for any error messages

## Location

Currently configured for:
- **Location**: Broomfield, Colorado
- **Latitude**: 39.9165
- **Longitude**: -104.9103
- **Timezone**: America/Denver

To change the location, modify the coordinates in `app.py`:
```python
LATITUDE = 39.9165
LONGITUDE = -104.9103
```

## License

This project is open source and available for personal use.

## Author

Created as a weather dashboard tool for real-time weather monitoring in Broomfield, Colorado.
