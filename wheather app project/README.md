# Weather Dashboard

A beautiful and responsive weather application that displays real-time weather information with engaging visuals. Built with Flask, the OpenWeatherMap API, and Google Maps API.

![Weather Dashboard Screenshot](https://via.placeholder.com/800x450.png?text=Weather+Dashboard)

## Features

- Real-time weather data from OpenWeatherMap API
- Responsive design that works on desktop and mobile devices
- Beautiful UI with visual indicators for different weather conditions
- Displays temperature, wind speed, humidity, pressure, sunrise and sunset times
- Background changes based on current weather conditions
- 5-day weather forecast with daily statistics
- Google Maps Places API integration for powerful location search
- Accurate address and location finding powered by Google's global database

## Using the Google Maps Search

The Weather Dashboard now uses Google Maps Places API for location search:

1. **Begin typing** any location - a city, address, landmark, or region
2. **Google-powered suggestions** will appear as you type
3. **Select a location** from the dropdown to get precise weather data
4. **Globally accurate** search results with the power of Google Maps

The Google Maps integration provides superior location search with access to millions of places worldwide, precise geocoding, and familiar user experience.

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd weather-dashboard
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   - Get a Google Maps API key (see API Keys section below)
   - Update the `GOOGLE_MAPS_API_KEY` variable in `app.py`

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## API Keys

This project uses two external APIs:

### OpenWeatherMap API
An API key is already included in the code, but if you want to use your own:

1. Register for a free account at [OpenWeatherMap](https://openweathermap.org/)
2. Get your API key from the dashboard
3. Replace the `API_KEY` variable in `app.py` with your own key

### Google Maps API
You'll need to get your own Google Maps API key:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the following APIs:
   - Places API
   - Geocoding API
   - Maps JavaScript API
4. Create API credentials and get your API key
5. Replace the `GOOGLE_MAPS_API_KEY` variable in `app.py` with your key
6. Set up appropriate API key restrictions in the Google Cloud Console

**Note**: Google Maps Platform offers a free tier that should be sufficient for personal use, but you'll need to set up billing information.

## Technologies Used

- **Backend**: Flask (Python)
- **APIs**: OpenWeatherMap, Google Maps Places API
- **Frontend**: HTML, CSS, JavaScript
- **UI Components**: Font Awesome for icons, Google Fonts

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Weather data provided by [OpenWeatherMap](https://openweathermap.org/)
- Location search powered by [Google Maps Platform](https://cloud.google.com/maps-platform)
- Icons from [Font Awesome](https://fontawesome.com/)
- Fonts from [Google Fonts](https://fonts.google.com/)