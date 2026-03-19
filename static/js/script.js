// Temperature unit toggle
let tempUnit = localStorage.getItem('tempUnit') || 'F';

function celsiusToFahrenheit(celsius) {
    return (celsius * 9/5) + 32;
}

function fahrenheitToCelsius(fahrenheit) {
    return (fahrenheit - 32) * 5/9;
}

function convertTemp(temp, toUnit) {
    if (toUnit === 'C' && tempUnit === 'F') {
        return fahrenheitToCelsius(temp);
    } else if (toUnit === 'F' && tempUnit === 'C') {
        return celsiusToFahrenheit(temp);
    }
    return temp;
}

function formatTemp(temp) {
    const displayTemp = tempUnit === 'F' ? temp : fahrenheitToCelsius(temp);
    return Math.round(displayTemp) + '°' + tempUnit;
}

// Weather condition codes to human-readable descriptions
const WEATHER_CONDITIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
};

// Weather icons mapping
const WEATHER_EMOJIS = {
    0: "☀️",
    1: "🌤️",
    2: "⛅",
    3: "☁️",
    45: "🌫️",
    48: "🌫️",
    51: "🌧️",
    53: "🌧️",
    55: "🌧️",
    61: "🌧️",
    63: "🌧️",
    65: "⛈️",
    71: "🌨️",
    73: "🌨️",
    75: "🌨️",
    77: "🌨️",
    80: "🌦️",
    81: "🌦️",
    82: "⛈️",
    85: "🌨️",
    86: "🌨️",
    95: "⛈️",
    96: "⛈️",
    99: "⛈️"
};

// Get emoji for weather code
function getWeatherEmoji(code) {
    return WEATHER_EMOJIS[code] || "🌤️";
}

// Get description for weather code
function getWeatherDescription(code) {
    return WEATHER_CONDITIONS[code] || "Unknown";
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { weekday: 'short', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Format time
function formatTime(timeString) {
    const date = new Date(timeString);
    const hours = date.getHours();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    return `${displayHours}${ampm}`;
}

// Get cardinal direction from angle
function getCardinalDirection(angle) {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                       'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round(angle / 22.5) % 16;
    return directions[index];
}

// Update current weather display
function updateCurrentWeather(current) {
    document.getElementById('currentTemp').textContent = formatTemp(current.temperature_2m);
    document.getElementById('feelsLike').textContent = formatTemp(current.apparent_temperature);
    document.getElementById('condition').textContent = 
        `${getWeatherEmoji(current.weather_code)} ${getWeatherDescription(current.weather_code)}`;
    document.getElementById('humidity').textContent = `${current.relative_humidity_2m}%`;
    document.getElementById('windSpeed').textContent = `${Math.round(current.wind_speed_10m)} mph`;
    
    const cardinal = getCardinalDirection(current.wind_direction_10m);
    document.getElementById('windDir').textContent = `${cardinal} (${Math.round(current.wind_direction_10m)}°)`;
    
    document.getElementById('precipitation').textContent = `${current.precipitation || 0}%`;
}

// Update hourly forecast
function updateHourlyForecast(hourly) {
    const forecastContainer = document.getElementById('hourlyForecast');
    forecastContainer.innerHTML = '';

    const now = new Date();
    const currentHour = now.getHours();
    
    // Show next 12 hours
    for (let i = 0; i < 12; i++) {
        const hourIndex = i + currentHour;
        if (hourIndex < hourly.time.length) {
            const time = hourly.time[hourIndex];
            const temp = hourly.temperature_2m[hourIndex];
            const precipProb = hourly.precipitation_probability[hourIndex];
            const weatherCode = hourly.weather_code[hourIndex];

            const hourDiv = document.createElement('div');
            hourDiv.className = 'hourly-item';
            hourDiv.innerHTML = `
                <div class="time">${formatTime(time)}</div>
                <div class="temp">${formatTemp(temp)}</div>
                <div class="condition">${getWeatherEmoji(weatherCode)}</div>
                <div class="condition" style="font-size: 0.75em; opacity: 0.7;">
                    💧 ${precipProb}%
                </div>
            `;
            forecastContainer.appendChild(hourDiv);
        }
    }
}

// Update daily forecast
function updateDailyForecast(daily) {
    const forecastContainer = document.getElementById('dailyForecast');
    forecastContainer.innerHTML = '';

    // Show next 7 days
    for (let i = 0; i < Math.min(7, daily.time.length); i++) {
        const date = daily.time[i];
        const high = daily.temperature_2m_max[i];
        const low = daily.temperature_2m_min[i];
        const weatherCode = daily.weather_code[i];
        const precipitation = daily.precipitation_sum[i];

        const dayDiv = document.createElement('div');
        dayDiv.className = 'daily-item';
        dayDiv.innerHTML = `
            <div class="day">${formatDate(date)}</div>
            <div class="high-low">
                <span class="high">${formatTemp(high)}</span>
                <span class="low" style="margin-left: 5px;">/${formatTemp(low)}</span>
            </div>
            <div class="condition" style="font-size: 1.5em; margin: 8px 0;">
                ${getWeatherEmoji(weatherCode)}
            </div>
            <div class="condition">${getWeatherDescription(weatherCode)}</div>
            <div class="condition" style="font-size: 0.8em; margin-top: 8px;">
                💧 ${precipitation.toFixed(1)}"
            </div>
        `;
        forecastContainer.appendChild(dayDiv);
    }
}

// Format last update time
function formatLastUpdate(isoString) {
    if (!isoString) return "Unknown";
    
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) {
        return "Just now";
    } else if (diffMins < 60) {
        return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    } else {
        const hours = Math.floor(diffMins / 60);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }
}

// Display alerts
function displayAlerts(alerts) {
    const alertsSection = document.getElementById('alertsSection');
    const alertsList = document.getElementById('alertsList');
    
    if (!alerts || alerts.length === 0) {
        alertsSection.style.display = 'none';
        return;
    }
    
    alertsSection.style.display = 'block';
    alertsList.innerHTML = '';
    
    alerts.forEach(alert => {
        const properties = alert.properties || {};
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert-item';
        alertDiv.innerHTML = `
            <h3>${properties.event || 'Weather Alert'}</h3>
            <p>${properties.description || properties.headline || 'No description available'}</p>
            <div class="alert-severity">${properties.severity || 'Unknown'}</div>
        `;
        alertsList.appendChild(alertDiv);
    });
}

// Fetch and update weather
async function fetchAndUpdateWeather() {
    try {
        const response = await fetch('/api/weather');
        const result = await response.json();
        
        if (result.data.error) {
            console.error('Error from server:', result.data.error);
            return;
        }
        
        const weatherData = result.data;
        
        // Update current weather
        if (weatherData.current) {
            updateCurrentWeather(weatherData.current);
        }
        
        // Update hourly forecast
        if (weatherData.hourly && weatherData.hourly.time) {
            updateHourlyForecast(weatherData.hourly);
        }
        
        // Update daily forecast
        if (weatherData.daily && weatherData.daily.time) {
            updateDailyForecast(weatherData.daily);
        }
        
        // Display alerts
        if (weatherData.alerts) {
            displayAlerts(weatherData.alerts);
        }
        
        // Update last update time
        if (result.last_update) {
            document.getElementById('lastUpdate').textContent = formatLastUpdate(result.last_update);
        }
        
    } catch (error) {
        console.error('Error fetching weather:', error);
        alert('Error fetching weather data. Please try again.');
    }
}

// Location modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('locationModal');
    const closeBtn = document.querySelector('.close');
    const changeLocationBtn = document.getElementById('changeLocationBtn');
    const submitLocationBtn = document.getElementById('submitLocationBtn');
    const locationInput = document.getElementById('locationInput');
    const locationError = document.getElementById('locationError');

    // Make sure elements exist
    if (!modal || !changeLocationBtn || !submitLocationBtn) {
        console.error('Modal elements not found');
        return;
    }

    // Open modal
    changeLocationBtn.addEventListener('click', function() {
        modal.style.display = 'flex';
        locationInput.value = '';
        locationError.style.display = 'none';
        locationInput.focus();
    });

    // Close modal
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });

    // Submit location
    submitLocationBtn.addEventListener('click', async function() {
        const location = locationInput.value.trim();
        if (!location) {
            locationError.textContent = 'Please enter a location';
            locationError.style.display = 'block';
            return;
        }
        
        submitLocationBtn.disabled = true;
        submitLocationBtn.textContent = 'Searching...';
        locationError.style.display = 'none';
        
        try {
            const response = await fetch('/api/set-location', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ location: location })
            });
            
            const result = await response.json();
            
            if (result.error) {
                locationError.textContent = result.error;
                locationError.style.display = 'block';
                locationError.style.color = '#d32f2f';  // Red for error
            } else {
                // Update location display
                document.querySelector('.location').textContent = result.location_name;
                
                // Show warning message if present
                if (result.warning) {
                    locationError.textContent = '⚠️ ' + result.warning;
                    locationError.style.display = 'block';
                    locationError.style.color = '#ff9800';  // Orange for warning
                    locationError.style.fontSize = '1.1em';
                    locationError.style.padding = '15px';
                    locationError.style.backgroundColor = '#fff3e0';
                    locationError.style.borderRadius = '4px';
                    locationError.style.marginTop = '15px';
                    
                    // Wait 2 seconds before closing modal and refreshing
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                    locationError.style.display = 'none';
                    locationError.style.fontSize = '0.9em';
                    locationError.style.padding = '0';
                    locationError.style.backgroundColor = 'transparent';
                }
                
                // Close modal and refresh weather
                modal.style.display = 'none';
                await fetchAndUpdateWeather();
            }
        } catch (error) {
            console.error('Error setting location:', error);
            locationError.textContent = 'Error changing location. Please try again.';
            locationError.style.display = 'block';
        } finally {
            submitLocationBtn.disabled = false;
            submitLocationBtn.textContent = 'Search';
        }
    });

    // Allow Enter key to submit
    locationInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            submitLocationBtn.click();
        }
    });
});

// Temperature toggle button
document.addEventListener('DOMContentLoaded', function() {
    const tempToggleBtn = document.getElementById('tempToggleBtn');
    
    function updateToggleButton() {
        tempToggleBtn.textContent = tempUnit === 'F' ? '°F | °C' : '°C | °F';
    }
    
    tempToggleBtn.addEventListener('click', function() {
        tempUnit = tempUnit === 'F' ? 'C' : 'F';
        localStorage.setItem('tempUnit', tempUnit);
        updateToggleButton();
        // Refresh weather display with new unit
        fetchAndUpdateWeather();
    });
    
    updateToggleButton();
});

// Manual refresh button
document.getElementById('refreshBtn').addEventListener('click', async function() {
    this.disabled = true;
    this.textContent = '🔄 Refreshing...';
    
    try {
        const response = await fetch('/api/refresh');
        const result = await response.json();
        
        const weatherData = result.data;
        
        // Update current weather
        if (weatherData.current) {
            updateCurrentWeather(weatherData.current);
        }
        
        // Update hourly forecast
        if (weatherData.hourly && weatherData.hourly.time) {
            updateHourlyForecast(weatherData.hourly);
        }
        
        // Update daily forecast
        if (weatherData.daily && weatherData.daily.time) {
            updateDailyForecast(weatherData.daily);
        }
        
        // Display alerts
        if (weatherData.alerts) {
            displayAlerts(weatherData.alerts);
        }
        
        // Update last update time
        if (result.last_update) {
            document.getElementById('lastUpdate').textContent = formatLastUpdate(result.last_update);
        }
        
    } catch (error) {
        console.error('Error refreshing weather:', error);
        alert('Error refreshing weather data. Please try again.');
    } finally {
        this.disabled = false;
        this.textContent = '🔄 Refresh Now';
    }
});

// Initial load
document.addEventListener('DOMContentLoaded', function() {
    fetchAndUpdateWeather();
    
    // Update last update time every minute
    setInterval(function() {
        const lastUpdateSpan = document.getElementById('lastUpdate');
        const text = lastUpdateSpan.textContent;
        // Re-fetch to get accurate time
        fetchAndUpdateWeather();
    }, 60000); // Every minute
});
