from __future__ import print_function
from flask import Flask, render_template, jsonify, request
import requests
import certifi
from datetime import datetime
import threading
import time
import os

app = Flask(__name__)

# Broomfield, Colorado coordinates
LATITUDE = 39.9165
LONGITUDE = -104.9103
LOCATION_NAME = "Broomfield, Colorado"

# Global weather data
weather_data = {}
last_update = None

def fetch_weather():
    """Fetch weather data from Open-Meteo API"""
    global weather_data, last_update
    
    try:
        # Get current weather
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
            "hourly": "temperature_2m,precipitation_probability,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": "America/Denver"
        }
        
        response = requests.get(weather_url, params=params, verify=certifi.where())
        response.raise_for_status()
        data = response.json()
        
        # Get weather alerts from NWS
        alerts_url = "https://api.weather.gov/alerts/active"
        alerts_params = {
            "point": "{0},{1}".format(LATITUDE, LONGITUDE)
        }
        
        try:
            alerts_response = requests.get(alerts_url, params=alerts_params, timeout=5, verify=certifi.where())
            alerts_data = alerts_response.json() if alerts_response.ok else {"features": []}
        except:
            alerts_data = {"features": []}
        
        weather_data = {
            "current": data.get("current", {}),
            "hourly": data.get("hourly", {}),
            "daily": data.get("daily", {}),
            "alerts": alerts_data.get("features", []),
            "location": LOCATION_NAME,
            "latitude": LATITUDE,
            "longitude": LONGITUDE
        }
        
        last_update = datetime.now()
        print("Weather data updated at {0}".format(last_update))
        
    except Exception as e:
        print("Error fetching weather: {0}".format(e))
        weather_data = {
            "error": str(e),
            "location": LOCATION_NAME
        }

def background_update():
    """Background thread to update weather every hour"""
    while True:
        time.sleep(3600)  # 1 hour
        fetch_weather()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html', location=LOCATION_NAME)

@app.route('/api/weather')
def get_weather():
    """API endpoint to get weather data"""
    if not weather_data:
        fetch_weather()
    
    return jsonify({
        "data": weather_data,
        "last_update": last_update.isoformat() if last_update else None
    })

@app.route('/api/refresh')
def refresh_weather():
    """API endpoint to manually refresh weather"""
    fetch_weather()
    return jsonify({
        "data": weather_data,
        "last_update": last_update.isoformat() if last_update else None
    })

@app.route('/api/set-location', methods=['POST'])
def set_location():
    """API endpoint to set location by city/state"""
    global LATITUDE, LONGITUDE, LOCATION_NAME
    
    try:
        data = request.get_json()
        location_query = data.get('location', '').strip()
        
        if not location_query:
            return jsonify({"error": "Location cannot be empty"}), 400
        
        print("Searching for location: {0}".format(location_query))
        
        # Try multiple geocoding approaches
        latitude = None
        longitude = None
        location_name = None
        
        # Approach 1: Use Open-Meteo geocoding API with correct parameters
        try:
            geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
            geocode_params = {
                "name": location_query,
                "count": 10,
                "language": "en"
            }
            
            geocode_response = requests.get(geocode_url, params=geocode_params, verify=certifi.where(), timeout=5)
            geocode_response.raise_for_status()
            geocode_data = geocode_response.json()
            
            print("Geocoding response: {0}".format(geocode_data))
            
            if "results" in geocode_data and len(geocode_data["results"]) > 0:
                result = geocode_data["results"][0]
                latitude = result.get("latitude")
                longitude = result.get("longitude")
                
                # Build location name
                location_parts = []
                if "name" in result:
                    location_parts.append(result["name"])
                if "admin1" in result:
                    location_parts.append(result["admin1"])
                elif "country" in result:
                    location_parts.append(result["country"])
                
                location_name = ", ".join(location_parts) if location_parts else "Unknown Location"
        except Exception as e:
            print("Approach 1 failed: {0}".format(str(e)))
        
        # If Approach 1 failed, try manual lookup for US cities
        if latitude is None:
            print("Trying manual lookup for US cities")
            # Comprehensive US city coordinates (major cities from all 50 states)
            us_cities = {
                # Alabama
                "birmingham, alabama": (33.5186, -86.8104),
                "birmingham, al": (33.5186, -86.8104),
                "montgomery, alabama": (32.3792, -86.3077),
                "montgomery, al": (32.3792, -86.3077),
                "mobile, alabama": (30.6954, -88.2398),
                "mobile, al": (30.6954, -88.2398),
                # Alaska
                "anchorage, alaska": (61.2181, -149.9003),
                "anchorage, ak": (61.2181, -149.9003),
                "juneau, alaska": (58.3019, -134.4197),
                "juneau, ak": (58.3019, -134.4197),
                # Arizona
                "phoenix, arizona": (33.4484, -112.0742),
                "phoenix, az": (33.4484, -112.0742),
                "mesa, arizona": (33.4152, -111.8313),
                "mesa, az": (33.4152, -111.8313),
                "tucson, arizona": (32.2226, -110.9747),
                "tucson, az": (32.2226, -110.9747),
                "scottsdale, arizona": (33.4942, -111.9261),
                "scottsdale, az": (33.4942, -111.9261),
                # Arkansas
                "little rock, arkansas": (34.7465, -92.2896),
                "little rock, ar": (34.7465, -92.2896),
                "fort smith, arkansas": (35.3859, -94.4181),
                "fort smith, ar": (35.3859, -94.4181),
                # California
                "los angeles, california": (34.0522, -118.2437),
                "los angeles, ca": (34.0522, -118.2437),
                "san francisco, california": (37.7749, -122.4194),
                "san francisco, ca": (37.7749, -122.4194),
                "san diego, california": (32.7157, -117.1611),
                "san diego, ca": (32.7157, -117.1611),
                "san jose, california": (37.3382, -121.8863),
                "san jose, ca": (37.3382, -121.8863),
                "fresno, california": (36.7469, -119.7726),
                "fresno, ca": (36.7469, -119.7726),
                "oakland, california": (37.8044, -122.2712),
                "oakland, ca": (37.8044, -122.2712),
                "long beach, california": (33.7701, -118.1937),
                "long beach, ca": (33.7701, -118.1937),
                # Colorado
                "denver, colorado": (39.7392, -104.9903),
                "denver, co": (39.7392, -104.9903),
                "colorado springs, colorado": (38.8339, -104.8202),
                "colorado springs, co": (38.8339, -104.8202),
                "aurora, colorado": (39.7294, -104.8202),
                "aurora, co": (39.7294, -104.8202),
                "fort collins, colorado": (40.5853, -105.0844),
                "fort collins, co": (40.5853, -105.0844),
                "broomfield, colorado": (39.9165, -104.9103),
                "broomfield, co": (39.9165, -104.9103),
                "westminster, colorado": (39.8363, -104.9861),
                "westminster, co": (39.8363, -104.9861),
                # Connecticut
                "bridgeport, connecticut": (41.1788, -73.1995),
                "bridgeport, ct": (41.1788, -73.1995),
                "new haven, connecticut": (41.3083, -72.9279),
                "new haven, ct": (41.3083, -72.9279),
                "hartford, connecticut": (41.7658, -72.6734),
                "hartford, ct": (41.7658, -72.6734),
                # Delaware
                "wilmington, delaware": (39.7390, -75.5453),
                "wilmington, de": (39.7390, -75.5453),
                "dover, delaware": (39.1582, -75.5244),
                "dover, de": (39.1582, -75.5244),
                # Florida
                "miami, florida": (25.7617, -80.1918),
                "miami, fl": (25.7617, -80.1918),
                "orlando, florida": (28.5383, -81.3792),
                "orlando, fl": (28.5383, -81.3792),
                "tampa, florida": (27.9506, -82.4593),
                "tampa, fl": (27.9506, -82.4593),
                "jacksonville, florida": (30.3322, -81.6557),
                "jacksonville, fl": (30.3322, -81.6557),
                "fort lauderdale, florida": (26.1224, -80.1373),
                "fort lauderdale, fl": (26.1224, -80.1373),
                # Georgia
                "atlanta, georgia": (33.7490, -84.3880),
                "atlanta, ga": (33.7490, -84.3880),
                "columbus, georgia": (32.4609, -84.9789),
                "columbus, ga": (32.4609, -84.9789),
                "savannah, georgia": (32.0809, -81.0912),
                "savannah, ga": (32.0809, -81.0912),
                # Hawaii
                "honolulu, hawaii": (21.3099, -157.8581),
                "honolulu, hi": (21.3099, -157.8581),
                "pearl city, hawaii": (21.3973, -157.9869),
                "pearl city, hi": (21.3973, -157.9869),
                # Idaho
                "boise, idaho": (43.6150, -116.2023),
                "boise, id": (43.6150, -116.2023),
                "meridian, idaho": (43.6121, -116.3915),
                "meridian, id": (43.6121, -116.3915),
                # Illinois
                "chicago, illinois": (41.8781, -87.6298),
                "chicago, il": (41.8781, -87.6298),
                "aurora, illinois": (41.7606, -88.2434),
                "aurora, il": (41.7606, -88.2434),
                "rockford, illinois": (42.2711, -89.0940),
                "rockford, il": (42.2711, -89.0940),
                # Indiana
                "indianapolis, indiana": (39.7684, -86.1581),
                "indianapolis, in": (39.7684, -86.1581),
                "fort wayne, indiana": (41.0535, -85.1872),
                "fort wayne, in": (41.0535, -85.1872),
                "evansville, indiana": (37.9716, -87.5711),
                "evansville, in": (37.9716, -87.5711),
                # Iowa
                "des moines, iowa": (41.5868, -93.6250),
                "des moines, ia": (41.5868, -93.6250),
                "cedar rapids, iowa": (42.0089, -91.6646),
                "cedar rapids, ia": (42.0089, -91.6646),
                # Kansas
                "kansas city, kansas": (39.0997, -94.6783),
                "kansas city, ks": (39.0997, -94.6783),
                "wichita, kansas": (37.6872, -97.3301),
                "wichita, ks": (37.6872, -97.3301),
                "topeka, kansas": (39.0473, -95.6752),
                "topeka, ks": (39.0473, -95.6752),
                # Kentucky
                "louisville, kentucky": (38.2527, -85.7585),
                "louisville, ky": (38.2527, -85.7585),
                "lexington, kentucky": (38.0297, -84.4745),
                "lexington, ky": (38.0297, -84.4745),
                # Louisiana
                "new orleans, louisiana": (29.9511, -90.2623),
                "new orleans, la": (29.9511, -90.2623),
                "baton rouge, louisiana": (30.4515, -91.1871),
                "baton rouge, la": (30.4515, -91.1871),
                # Maine
                "portland, maine": (43.6591, -70.2568),
                "portland, me": (43.6591, -70.2568),
                "lewiston, maine": (44.1006, -70.1957),
                "lewiston, me": (44.1006, -70.1957),
                # Maryland
                "baltimore, maryland": (39.2904, -76.6122),
                "baltimore, md": (39.2904, -76.6122),
                # Massachusetts
                "boston, massachusetts": (42.3601, -71.0589),
                "boston, ma": (42.3601, -71.0589),
                "worcester, massachusetts": (42.2655, -71.8022),
                "worcester, ma": (42.2655, -71.8022),
                "springfield, massachusetts": (42.1015, -72.5898),
                "springfield, ma": (42.1015, -72.5898),
                # Michigan
                "detroit, michigan": (42.3314, -83.0458),
                "detroit, mi": (42.3314, -83.0458),
                "grand rapids, michigan": (42.9633, -85.6749),
                "grand rapids, mi": (42.9633, -85.6749),
                # Minnesota
                "minneapolis, minnesota": (44.9778, -93.2650),
                "minneapolis, mn": (44.9778, -93.2650),
                "st. paul, minnesota": (44.9537, -93.0900),
                "st. paul, mn": (44.9537, -93.0900),
                "saint paul, minnesota": (44.9537, -93.0900),
                "saint paul, mn": (44.9537, -93.0900),
                # Mississippi
                "jackson, mississippi": (32.2988, -90.1848),
                "jackson, ms": (32.2988, -90.1848),
                "gulfport, mississippi": (30.3674, -89.0928),
                "gulfport, ms": (30.3674, -89.0928),
                # Missouri
                "kansas city, missouri": (39.0997, -94.5786),
                "kansas city, mo": (39.0997, -94.5786),
                "st. louis, missouri": (38.6270, -90.1994),
                "st. louis, mo": (38.6270, -90.1994),
                "saint louis, missouri": (38.6270, -90.1994),
                "saint louis, mo": (38.6270, -90.1994),
                # Montana
                "billings, montana": (45.7833, -103.8676),
                "billings, mt": (45.7833, -103.8676),
                "missoula, montana": (46.8797, -114.0076),
                "missoula, mt": (46.8797, -114.0076),
                # Nebraska
                "omaha, nebraska": (41.2565, -95.9345),
                "omaha, ne": (41.2565, -95.9345),
                "lincoln, nebraska": (40.7978, -96.6603),
                "lincoln, ne": (40.7978, -96.6603),
                # Nevada
                "las vegas, nevada": (36.1699, -115.1398),
                "las vegas, nv": (36.1699, -115.1398),
                "henderson, nevada": (36.0395, -115.0443),
                "henderson, nv": (36.0395, -115.0443),
                "reno, nevada": (39.5296, -119.8138),
                "reno, nv": (39.5296, -119.8138),
                # New Hampshire
                "manchester, new hampshire": (42.9956, -71.4548),
                "manchester, nh": (42.9956, -71.4548),
                "nashua, new hampshire": (42.7655, -71.5017),
                "nashua, nh": (42.7655, -71.5017),
                # New Jersey
                "newark, new jersey": (40.7357, -74.1724),
                "newark, nj": (40.7357, -74.1724),
                "jersey city, new jersey": (40.7178, -74.0431),
                "jersey city, nj": (40.7178, -74.0431),
                # New Mexico
                "albuquerque, new mexico": (35.0844, -106.6504),
                "albuquerque, nm": (35.0844, -106.6504),
                "santa fe, new mexico": (35.6870, -105.9378),
                "santa fe, nm": (35.6870, -105.9378),
                # New York
                "new york, new york": (40.7128, -74.0060),
                "new york, ny": (40.7128, -74.0060),
                "buffalo, new york": (42.8864, -78.8784),
                "buffalo, ny": (42.8864, -78.8784),
                "rochester, new york": (43.1629, -77.6094),
                "rochester, ny": (43.1629, -77.6094),
                "yonkers, new york": (40.9461, -73.8994),
                "yonkers, ny": (40.9461, -73.8994),
                # North Carolina
                "charlotte, north carolina": (35.2271, -80.8431),
                "charlotte, nc": (35.2271, -80.8431),
                "raleigh, north carolina": (35.7796, -78.6382),
                "raleigh, nc": (35.7796, -78.6382),
                "greensboro, north carolina": (36.0726, -79.7920),
                "greensboro, nc": (36.0726, -79.7920),
                # North Dakota
                "bismarck, north dakota": (46.8083, -100.7837),
                "bismarck, nd": (46.8083, -100.7837),
                "grand forks, north dakota": (47.9253, -97.0329),
                "grand forks, nd": (47.9253, -97.0329),
                # Ohio
                "columbus, ohio": (39.9612, -82.9988),
                "columbus, oh": (39.9612, -82.9988),
                "cleveland, ohio": (41.4993, -81.6944),
                "cleveland, oh": (41.4993, -81.6944),
                "cincinnati, ohio": (39.1031, -84.5585),
                "cincinnati, oh": (39.1031, -84.5585),
                # Oklahoma
                "oklahoma city, oklahoma": (35.4676, -97.5164),
                "oklahoma city, ok": (35.4676, -97.5164),
                "tulsa, oklahoma": (36.1539, -95.9928),
                "tulsa, ok": (36.1539, -95.9928),
                # Oregon
                "portland, oregon": (45.5152, -122.6784),
                "portland, or": (45.5152, -122.6784),
                "eugene, oregon": (44.0521, -123.0868),
                "eugene, or": (44.0521, -123.0868),
                "salem, oregon": (44.9429, -123.0351),
                "salem, or": (44.9429, -123.0351),
                # Pennsylvania
                "philadelphia, pennsylvania": (39.9526, -75.1652),
                "philadelphia, pa": (39.9526, -75.1652),
                "pittsburgh, pennsylvania": (40.4406, -79.9959),
                "pittsburgh, pa": (40.4406, -79.9959),
                # Rhode Island
                "providence, rhode island": (41.8240, -71.4128),
                "providence, ri": (41.8240, -71.4128),
                # South Carolina
                "charleston, south carolina": (32.7765, -79.9318),
                "charleston, sc": (32.7765, -79.9318),
                "columbia, south carolina": (34.0007, -81.0348),
                "columbia, sc": (34.0007, -81.0348),
                # South Dakota
                "sioux falls, south dakota": (43.5460, -96.7313),
                "sioux falls, sd": (43.5460, -96.7313),
                "rapid city, south dakota": (44.0805, -103.2310),
                "rapid city, sd": (44.0805, -103.2310),
                # Tennessee
                "memphis, tennessee": (35.1495, -90.0490),
                "memphis, tn": (35.1495, -90.0490),
                "nashville, tennessee": (36.1627, -86.7816),
                "nashville, tn": (36.1627, -86.7816),
                "knoxville, tennessee": (35.9606, -83.9207),
                "knoxville, tn": (35.9606, -83.9207),
                # Texas
                "houston, texas": (29.7604, -95.3698),
                "houston, tx": (29.7604, -95.3698),
                "san antonio, texas": (29.4241, -98.4936),
                "san antonio, tx": (29.4241, -98.4936),
                "dallas, texas": (32.7767, -96.7970),
                "dallas, tx": (32.7767, -96.7970),
                "austin, texas": (30.2672, -97.7431),
                "austin, tx": (30.2672, -97.7431),
                "fort worth, texas": (32.7555, -97.3308),
                "fort worth, tx": (32.7555, -97.3308),
                # Utah
                "salt lake city, utah": (40.7608, -111.8910),
                "salt lake city, ut": (40.7608, -111.8910),
                "provo, utah": (40.2338, -111.6585),
                "provo, ut": (40.2338, -111.6585),
                # Vermont
                "burlington, vermont": (44.4759, -73.2121),
                "burlington, vt": (44.4759, -73.2121),
                # Virginia
                "virginia beach, virginia": (36.7685, -76.0681),
                "virginia beach, va": (36.7685, -76.0681),
                "richmond, virginia": (37.5407, -77.4360),
                "richmond, va": (37.5407, -77.4360),
                # Washington
                "seattle, washington": (47.6062, -122.3321),
                "seattle, wa": (47.6062, -122.3321),
                "tacoma, washington": (47.2529, -122.4443),
                "tacoma, wa": (47.2529, -122.4443),
                "spokane, washington": (47.6587, -117.4260),
                "spokane, wa": (47.6587, -117.4260),
                # West Virginia
                "charleston, west virginia": (38.3498, -81.6326),
                "charleston, wv": (38.3498, -81.6326),
                # Wisconsin
                "milwaukee, wisconsin": (43.0389, -87.9065),
                "milwaukee, wi": (43.0389, -87.9065),
                "madison, wisconsin": (43.0731, -89.4012),
                "madison, wi": (43.0731, -89.4012),
                # Wyoming
                "cheyenne, wyoming": (41.1400, -104.8202),
                "cheyenne, wy": (41.1400, -104.8202),
                "casper, wyoming": (42.8334, -106.3395),
                "casper, wy": (42.8334, -106.3395),
            }
            
            location_key = location_query.lower().strip()
            if location_key in us_cities:
                latitude, longitude = us_cities[location_key]
                location_name = location_query
                print("Found in manual lookup: {0}".format(location_name))
        
        if latitude is None or longitude is None:
            print("City not found, trying state capital fallback")
            
            # State capitals mapping
            state_capitals = {
                # Full state names
                "alabama": ("montgomery", (32.3792, -86.3077)),
                "alaska": ("juneau", (58.3019, -134.4197)),
                "arizona": ("phoenix", (33.4484, -112.0742)),
                "arkansas": ("little rock", (34.7465, -92.2896)),
                "california": ("sacramento", (38.5816, -121.4944)),
                "colorado": ("denver", (39.7392, -104.9903)),
                "connecticut": ("hartford", (41.7658, -72.6734)),
                "delaware": ("dover", (39.1582, -75.5244)),
                "florida": ("tallahassee", (30.4383, -84.2807)),
                "georgia": ("atlanta", (33.7490, -84.3880)),
                "hawaii": ("honolulu", (21.3099, -157.8581)),
                "idaho": ("boise", (43.6150, -116.2023)),
                "illinois": ("springfield", (39.7817, -89.6501)),
                "indiana": ("indianapolis", (39.7684, -86.1581)),
                "iowa": ("des moines", (41.5868, -93.6250)),
                "kansas": ("topeka", (39.0473, -95.6752)),
                "kentucky": ("frankfort", (38.2009, -84.8733)),
                "louisiana": ("baton rouge", (30.4515, -91.1871)),
                "maine": ("augusta", (44.3106, -69.7795)),
                "maryland": ("annapolis", (38.9784, -76.4922)),
                "massachusetts": ("boston", (42.3601, -71.0589)),
                "michigan": ("lansing", (42.7335, -84.5555)),
                "minnesota": ("st. paul", (44.9537, -93.0900)),
                "mississippi": ("jackson", (32.2988, -90.1848)),
                "missouri": ("jefferson city", (38.5816, -92.1735)),
                "montana": ("helena", (46.5891, -112.0000)),
                "nebraska": ("lincoln", (40.7978, -96.6603)),
                "nevada": ("carson city", (39.1638, -119.7674)),
                "new hampshire": ("concord", (43.2081, -71.5376)),
                "new jersey": ("trenton", (40.2206, -74.7597)),
                "new mexico": ("santa fe", (35.6870, -105.9378)),
                "new york": ("albany", (42.6526, -73.7562)),
                "north carolina": ("raleigh", (35.7796, -78.6382)),
                "north dakota": ("bismarck", (46.8083, -100.7837)),
                "ohio": ("columbus", (39.9612, -82.9988)),
                "oklahoma": ("oklahoma city", (35.4676, -97.5164)),
                "oregon": ("salem", (44.9429, -123.0351)),
                "pennsylvania": ("harrisburg", (40.2732, -76.8867)),
                "rhode island": ("providence", (41.8240, -71.4128)),
                "south carolina": ("columbia", (34.0007, -81.0348)),
                "south dakota": ("pierre", (44.3683, -100.3364)),
                "tennessee": ("nashville", (36.1627, -86.7816)),
                "texas": ("austin", (30.2672, -97.7431)),
                "utah": ("salt lake city", (40.7608, -111.8910)),
                "vermont": ("montpelier", (44.2601, -72.5754)),
                "virginia": ("richmond", (37.5407, -77.4360)),
                "washington": ("olympia", (47.0379, -122.9007)),
                "west virginia": ("charleston", (38.3498, -81.6326)),
                "wisconsin": ("madison", (43.0731, -89.4012)),
                "wyoming": ("cheyenne", (41.1400, -104.8202)),
                # State abbreviations
                "al": ("montgomery", (32.3792, -86.3077)),
                "ak": ("juneau", (58.3019, -134.4197)),
                "az": ("phoenix", (33.4484, -112.0742)),
                "ar": ("little rock", (34.7465, -92.2896)),
                "ca": ("sacramento", (38.5816, -121.4944)),
                "co": ("denver", (39.7392, -104.9903)),
                "ct": ("hartford", (41.7658, -72.6734)),
                "de": ("dover", (39.1582, -75.5244)),
                "fl": ("tallahassee", (30.4383, -84.2807)),
                "ga": ("atlanta", (33.7490, -84.3880)),
                "hi": ("honolulu", (21.3099, -157.8581)),
                "id": ("boise", (43.6150, -116.2023)),
                "il": ("springfield", (39.7817, -89.6501)),
                "in": ("indianapolis", (39.7684, -86.1581)),
                "ia": ("des moines", (41.5868, -93.6250)),
                "ks": ("topeka", (39.0473, -95.6752)),
                "ky": ("frankfort", (38.2009, -84.8733)),
                "la": ("baton rouge", (30.4515, -91.1871)),
                "me": ("augusta", (44.3106, -69.7795)),
                "md": ("annapolis", (38.9784, -76.4922)),
                "ma": ("boston", (42.3601, -71.0589)),
                "mi": ("lansing", (42.7335, -84.5555)),
                "mn": ("st. paul", (44.9537, -93.0900)),
                "ms": ("jackson", (32.2988, -90.1848)),
                "mo": ("jefferson city", (38.5816, -92.1735)),
                "mt": ("helena", (46.5891, -112.0000)),
                "ne": ("lincoln", (40.7978, -96.6603)),
                "nv": ("carson city", (39.1638, -119.7674)),
                "nh": ("concord", (43.2081, -71.5376)),
                "nj": ("trenton", (40.2206, -74.7597)),
                "nm": ("santa fe", (35.6870, -105.9378)),
                "ny": ("albany", (42.6526, -73.7562)),
                "nc": ("raleigh", (35.7796, -78.6382)),
                "nd": ("bismarck", (46.8083, -100.7837)),
                "oh": ("columbus", (39.9612, -82.9988)),
                "ok": ("oklahoma city", (35.4676, -97.5164)),
                "or": ("salem", (44.9429, -123.0351)),
                "pa": ("harrisburg", (40.2732, -76.8867)),
                "ri": ("providence", (41.8240, -71.4128)),
                "sc": ("columbia", (34.0007, -81.0348)),
                "sd": ("pierre", (44.3683, -100.3364)),
                "tn": ("nashville", (36.1627, -86.7816)),
                "tx": ("austin", (30.2672, -97.7431)),
                "ut": ("salt lake city", (40.7608, -111.8910)),
                "vt": ("montpelier", (44.2601, -72.5754)),
                "va": ("richmond", (37.5407, -77.4360)),
                "wa": ("olympia", (47.0379, -122.9007)),
                "wv": ("charleston", (38.3498, -81.6326)),
                "wi": ("madison", (43.0731, -89.4012)),
                "wy": ("cheyenne", (41.1400, -104.8202)),
            }
            
            # Try to extract state from input
            parts = location_query.split(',')
            if len(parts) >= 2:
                state_input = parts[-1].strip().lower()
                
                # Look up state capital
                if state_input in state_capitals:
                    capital_city, (latitude, longitude) = state_capitals[state_input]
                    location_name = "{0}, {1}".format(capital_city.title(), state_input.title())
                    warning = "City not found. Showing {0} capital instead.".format(state_input.title())
                    print("Using state capital fallback: {0}".format(location_name))
                    
                    LATITUDE = latitude
                    LONGITUDE = longitude
                    LOCATION_NAME = location_name
                    
                    # Fetch weather for new location
                    fetch_weather()
                    
                    return jsonify({
                        "location_name": LOCATION_NAME,
                        "latitude": LATITUDE,
                        "longitude": LONGITUDE,
                        "warning": warning,
                        "data": weather_data,
                        "last_update": last_update.isoformat() if last_update else None
                    })
            
            print("No results found for: {0}".format(location_query))
            return jsonify({"error": "Location '{0}' not found. Try 'Denver, CO' or 'New York, NY'".format(location_query)}), 404
        
        LATITUDE = latitude
        LONGITUDE = longitude
        LOCATION_NAME = location_name
        
        print("New location set to: {0} ({1}, {2})".format(LOCATION_NAME, LATITUDE, LONGITUDE))
        
        # Fetch weather for new location
        fetch_weather()
        
        return jsonify({
            "location_name": LOCATION_NAME,
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "data": weather_data,
            "last_update": last_update.isoformat() if last_update else None
        })
        
    except Exception as e:
        print("Error in set_location: {0}".format(str(e)))
        return jsonify({"error": "Error processing location: {0}".format(str(e))}), 500

if __name__ == '__main__':
    # Initial fetch
    fetch_weather()
    
    # Start background update thread
    update_thread = threading.Thread(target=background_update)
    update_thread.setDaemon(True)
    update_thread.start()
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run Flask app - use 0.0.0.0 for external access
    app.run(debug=False, host='0.0.0.0', port=port)
