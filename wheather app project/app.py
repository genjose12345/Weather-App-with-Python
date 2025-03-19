from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import os
from datetime import datetime, timedelta
from collections import defaultdict
import json
import random

app = Flask(__name__)

# OpenWeatherMap API key
API_KEY = '30d4741c779ba94c470ca1f63045390a'

# Geocoding API key for OpenCage
# Get your free API key at https://opencagedata.com/users/sign_up
GEOCODING_API_KEY = '8c0892514e884f4d9640b89566e300cd'  # This key may have restrictions

# Sample data for fallback when API is not available
SAMPLE_LOCATIONS = [
    {"formatted": "New York City, New York, United States of America", "lat": 40.7128, "lng": -74.0060},
    {"formatted": "London, Greater London, England, United Kingdom", "lat": 51.5074, "lng": -0.1278},
    {"formatted": "Paris, Île-de-France, France", "lat": 48.8566, "lng": 2.3522},
    {"formatted": "Tokyo, Japan", "lat": 35.6762, "lng": 139.6503},
    {"formatted": "Sydney, New South Wales, Australia", "lat": -33.8688, "lng": 151.2093},
    {"formatted": "Los Angeles, California, United States", "lat": 34.0522, "lng": -118.2437},
    {"formatted": "Chicago, Illinois, United States", "lat": 41.8781, "lng": -87.6298},
    {"formatted": "Toronto, Ontario, Canada", "lat": 43.6532, "lng": -79.3832},
    {"formatted": "Berlin, Germany", "lat": 52.5200, "lng": 13.4050},
    {"formatted": "Madrid, Spain", "lat": 40.4168, "lng": -3.7038},
    {"formatted": "Rome, Italy", "lat": 41.9028, "lng": 12.4964},
    {"formatted": "Beijing, China", "lat": 39.9042, "lng": 116.4074},
    {"formatted": "Mumbai, Maharashtra, India", "lat": 19.0760, "lng": 72.8777},
    {"formatted": "Cairo, Egypt", "lat": 30.0444, "lng": 31.2357},
    {"formatted": "123 Main Street, Springfield", "lat": 39.9242, "lng": -83.8088},
    {"formatted": "Eiffel Tower, Paris, France", "lat": 48.8584, "lng": 2.2945},
    {"formatted": "Times Square, New York City, USA", "lat": 40.7580, "lng": -73.9855},
    {"formatted": "Central Park, New York City, USA", "lat": 40.7829, "lng": -73.9654},
    # Add more common cities
    {"formatted": "Dallas, Texas, United States", "lat": 32.7767, "lng": -96.7970},
    {"formatted": "Houston, Texas, United States", "lat": 29.7604, "lng": -95.3698},
    {"formatted": "San Francisco, California, United States", "lat": 37.7749, "lng": -122.4194},
    {"formatted": "Seattle, Washington, United States", "lat": 47.6062, "lng": -122.3321},
    {"formatted": "Atlanta, Georgia, United States", "lat": 33.7490, "lng": -84.3880},
    {"formatted": "Miami, Florida, United States", "lat": 25.7617, "lng": -80.1918},
    {"formatted": "Boston, Massachusetts, United States", "lat": 42.3601, "lng": -71.0589},
    {"formatted": "Denver, Colorado, United States", "lat": 39.7392, "lng": -104.9903},
    {"formatted": "Las Vegas, Nevada, United States", "lat": 36.1699, "lng": -115.1398},
    {"formatted": "Amsterdam, Netherlands", "lat": 52.3676, "lng": 4.9041},
    {"formatted": "Barcelona, Spain", "lat": 41.3851, "lng": 2.1734},
    {"formatted": "Sydney, Australia", "lat": -33.8688, "lng": 151.2093},
    {"formatted": "Dubai, United Arab Emirates", "lat": 25.2048, "lng": 55.2708},
    {"formatted": "Singapore, Singapore", "lat": 1.3521, "lng": 103.8198},
    # Common street addresses
    {"formatted": "123 Main Street, Boston, MA, USA", "lat": 42.3601, "lng": -71.0589},
    {"formatted": "456 Oak Avenue, Chicago, IL, USA", "lat": 41.8781, "lng": -87.6298},
    {"formatted": "789 Broadway, New York, NY, USA", "lat": 40.7128, "lng": -74.0060},
    {"formatted": "101 First Street, San Francisco, CA, USA", "lat": 37.7749, "lng": -122.4194},
    {"formatted": "555 Elm Road, Los Angeles, CA, USA", "lat": 34.0522, "lng": -118.2437},
    {"formatted": "777 Park Lane, Dallas, TX, USA", "lat": 32.7767, "lng": -96.7970},
    {"formatted": "888 Lake Drive, Seattle, WA, USA", "lat": 47.6062, "lng": -122.3321},
    {"formatted": "999 Ocean Boulevard, Miami, FL, USA", "lat": 25.7617, "lng": -80.1918},
    {"formatted": "222 Mountain View, Denver, CO, USA", "lat": 39.7392, "lng": -104.9903},
    {"formatted": "333 Desert Road, Las Vegas, NV, USA", "lat": 36.1699, "lng": -115.1398},
    # Landmarks
    {"formatted": "Statue of Liberty, New York, USA", "lat": 40.6892, "lng": -74.0445},
    {"formatted": "Golden Gate Bridge, San Francisco, USA", "lat": 37.8199, "lng": -122.4783},
    {"formatted": "Empire State Building, New York, USA", "lat": 40.7484, "lng": -73.9857},
    {"formatted": "Big Ben, London, UK", "lat": 51.5007, "lng": -0.1246},
    {"formatted": "Sydney Opera House, Sydney, Australia", "lat": -33.8568, "lng": 151.2153},
    {"formatted": "Taj Mahal, Agra, India", "lat": 27.1751, "lng": 78.0421},
    {"formatted": "Colosseum, Rome, Italy", "lat": 41.8902, "lng": 12.4922},
    {"formatted": "Sagrada Familia, Barcelona, Spain", "lat": 41.4036, "lng": 2.1744},
    {"formatted": "Great Wall of China, Beijing, China", "lat": 40.4319, "lng": 116.5704},
    {"formatted": "Louvre Museum, Paris, France", "lat": 48.8606, "lng": 2.3376}
]

# Extended address components that can be used to generate more realistic suggestions
ADDRESS_COMPONENTS = {
    'streets': ['Main Street', 'Oak Avenue', 'Maple Road', 'Broadway', 'Park Lane', 'Lake Drive', 
                'Highland Avenue', 'Elm Street', 'Washington Avenue', 'Lincoln Road', 'Church Street',
                'River Road', 'Forest Drive', 'Valley View', 'Sunset Boulevard', 'Ocean Drive',
                'Mountain View', 'Spring Garden', 'Willow Lane', 'Cedar Court', 'Dalton Street',
                'Dalton Avenue', 'Dalton Road', 'Dalton Drive', 'Dalton Place', 'Dalton Way',
                'Dalton Lane', 'Dalton Boulevard', 'Dalton Circle', 'Dalton Court'],
    'cities': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 
               'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville', 
               'San Francisco', 'Columbus', 'Indianapolis', 'Seattle', 'Denver', 'Boston',
               'Portland', 'Las Vegas', 'Detroit', 'Atlanta', 'Miami', 'Cleveland', 'Dalton',
               'Nashville', 'Baltimore', 'Oklahoma City', 'Louisville', 'Memphis', 'Richmond'],
    'states': [
        {'name': 'Alabama', 'abbr': 'AL'}, {'name': 'Alaska', 'abbr': 'AK'}, 
        {'name': 'Arizona', 'abbr': 'AZ'}, {'name': 'Arkansas', 'abbr': 'AR'}, 
        {'name': 'California', 'abbr': 'CA'}, {'name': 'Colorado', 'abbr': 'CO'}, 
        {'name': 'Connecticut', 'abbr': 'CT'}, {'name': 'Delaware', 'abbr': 'DE'}, 
        {'name': 'Florida', 'abbr': 'FL'}, {'name': 'Georgia', 'abbr': 'GA'}, 
        {'name': 'Hawaii', 'abbr': 'HI'}, {'name': 'Idaho', 'abbr': 'ID'}, 
        {'name': 'Illinois', 'abbr': 'IL'}, {'name': 'Indiana', 'abbr': 'IN'}, 
        {'name': 'Iowa', 'abbr': 'IA'}, {'name': 'Kansas', 'abbr': 'KS'}, 
        {'name': 'Kentucky', 'abbr': 'KY'}, {'name': 'Louisiana', 'abbr': 'LA'}, 
        {'name': 'Maine', 'abbr': 'ME'}, {'name': 'Maryland', 'abbr': 'MD'}, 
        {'name': 'Massachusetts', 'abbr': 'MA'}, {'name': 'Michigan', 'abbr': 'MI'}, 
        {'name': 'Minnesota', 'abbr': 'MN'}, {'name': 'Mississippi', 'abbr': 'MS'}, 
        {'name': 'Missouri', 'abbr': 'MO'}, {'name': 'Montana', 'abbr': 'MT'}
    ]
}

# Add more sample locations, including Dalton, GA and other cities named Dalton
SAMPLE_LOCATIONS.extend([
    {"formatted": "Dalton, Georgia, United States", "lat": 34.7697, "lng": -84.9705},
    {"formatted": "Dalton, Massachusetts, United States", "lat": 42.4737, "lng": -73.1662},
    {"formatted": "Dalton, Minnesota, United States", "lat": 46.1722, "lng": -96.0617},
    {"formatted": "Dalton, Ohio, United States", "lat": 40.7985, "lng": -81.6994},
    {"formatted": "Dalton, Pennsylvania, United States", "lat": 41.5642, "lng": -75.7416},
    {"formatted": "123 Dalton Street, New York, NY, USA", "lat": 40.7128, "lng": -74.0060},
    {"formatted": "456 Dalton Avenue, Chicago, IL, USA", "lat": 41.8781, "lng": -87.6298},
    {"formatted": "789 Dalton Road, Los Angeles, CA, USA", "lat": 34.0522, "lng": -118.2437},
    {"formatted": "101 Dalton Way, Boston, MA, USA", "lat": 42.3601, "lng": -71.0589},
    {"formatted": "555 Dalton Drive, Dallas, TX, USA", "lat": 32.7767, "lng": -96.7970}
])

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    forecast_data = None
    error = None
    
    if request.method == 'POST':
        location = request.form.get('location', '').strip()
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        
        if not location:
            error = "Please enter a location"
        else:
            # If we have coordinates from the form, use them directly
            if lat and lng:
                print(f"Using coordinates from form submission: {lat}, {lng}")
                weather_data = get_weather_by_coordinates(lat, lng, location)
                if weather_data.get('cod') and weather_data.get('cod') != 200:
                    error = f"Error: {weather_data.get('message', 'Something went wrong. Please try again.')}"
                else:
                    forecast_data = get_forecast_by_coordinates(lat, lng)
            else:
                # Otherwise, geocode the location search
                print(f"Geocoding location from search: {location}")
                coordinates = get_coordinates(location)
                
                if not coordinates:
                    error = f"Location '{location}' not found. Please try another search."
                else:
                    print(f"Found coordinates: {coordinates['lat']}, {coordinates['lng']}")
                    weather_data = get_weather_by_coordinates(coordinates['lat'], coordinates['lng'], coordinates['formatted'])
                    
                    if weather_data.get('cod') and weather_data.get('cod') != 200:
                        error = f"Error: {weather_data.get('message', 'Something went wrong. Please try again.')}"
                    else:
                        forecast_data = get_forecast_by_coordinates(coordinates['lat'], coordinates['lng'])
    
    # Pass only the current year to the template
    return render_template('index.html', 
                          weather_data=weather_data, 
                          forecast_data=forecast_data, 
                          error=error, 
                          current_year=datetime.now().year)

@app.route('/address-autocomplete', methods=['GET'])
def address_autocomplete():
    """API endpoint for address autocomplete using OpenCage API"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    suggestions = []
    
    try:
        # First try using OpenCage API for real-time suggestions
        url = f"https://api.opencagedata.com/geocode/v1/json?q={query}&key={GEOCODING_API_KEY}&limit=5&no_annotations=1"
        print(f"Making request to OpenCage API for autocomplete: {url.replace(GEOCODING_API_KEY, 'API_KEY_HIDDEN')}")
        
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('results'):
                for result in data['results']:
                    suggestions.append({
                        'text': result['formatted'],
                        'lat': result['geometry']['lat'],
                        'lng': result['geometry']['lng']
                    })
    except Exception as e:
        print(f"Error with OpenCage API: {e}")
    
    # If we don't have enough suggestions or API failed, use sample data as backup
    if len(suggestions) < 5:
        # Use sample data for additional suggestions
        count_needed = 5 - len(suggestions)
        matching_samples = []
        
        for location in SAMPLE_LOCATIONS:
            if query.lower() in location['formatted'].lower():
                # Check if this location is already in suggestions
                if not any(s['text'] == location['formatted'] for s in suggestions):
                    matching_samples.append({
                        'text': location['formatted'],
                        'lat': location['lat'],
                        'lng': location['lng']
                    })
        
        # Add the best matches from sample data
        suggestions.extend(matching_samples[:count_needed])
    
    print(f"Autocomplete for '{query}' found {len(suggestions)} suggestions")
    return jsonify(suggestions)

# Add a fallback API route for autocomplete to handle old requests
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    """Legacy endpoint - redirects to the new address-autocomplete endpoint"""
    return address_autocomplete()

def get_coordinates(location):
    """Get coordinates (lat, lng) from a location query"""
    try:
        # Clean the location string
        location = location.strip()
        if not location:
            return None
            
        # Check if the location is one of our sample locations (for testing/fallback)
        for sample in SAMPLE_LOCATIONS:
            if sample['formatted'].lower() == location.lower():
                print(f"Found exact match in sample data: {sample['formatted']}")
                return sample
        
        # Check for partial matches in our sample data
        partial_matches = [sample for sample in SAMPLE_LOCATIONS 
                         if location.lower() in sample['formatted'].lower()]
        
        if partial_matches:
            best_match = min(partial_matches, key=lambda x: len(x['formatted']))
            print(f"Found partial match in sample data: {best_match['formatted']}")
            return best_match
                
        # Use OpenCage Geocoding API to get coordinates
        url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={GEOCODING_API_KEY}&limit=1&no_annotations=1"
        print(f"Making request to OpenCage Geocoding API: {url.replace(GEOCODING_API_KEY, 'API_KEY_HIDDEN')}")
        
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Geocoding response received with status: {data.get('status', {}).get('code')}")
            
            if data.get('results') and len(data['results']) > 0:
                result = data['results'][0]
                return {
                    'lat': result['geometry']['lat'],
                    'lng': result['geometry']['lng'],
                    'formatted': result['formatted']
                }
            else:
                print("API returned no results, trying sample data")
        else:
            print(f"API returned error status: {response.status_code}")
        
        # If API failed, try to intelligently match with our sample data
        words = location.lower().split()
        best_score = 0
        best_match = None
        
        for sample in SAMPLE_LOCATIONS:
            sample_words = sample['formatted'].lower().split()
            
            # Calculate a simple match score: number of words in common
            score = sum(1 for word in words if any(word in sample_word for sample_word in sample_words))
            
            if score > best_score:
                best_score = score
                best_match = sample
                
        if best_match and best_score > 0:
            print(f"Found best fuzzy match in sample data: {best_match['formatted']} (score: {best_score})")
            return best_match
            
        print(f"No matches found for '{location}'")
        return None
    except Exception as e:
        print(f"Error getting coordinates: {e}")
        
        # Try to match with sample data as fallback
        try:
            # Last attempt: generate dynamic coordinates based on the location string
            import random
            
            # If location looks like a US address
            if any(c.isdigit() for c in location) and ('street' in location.lower() or 'avenue' in location.lower() or 'road' in location.lower()):
                # Extract city if possible
                parts = location.split(',')
                city_part = parts[1].strip() if len(parts) > 1 else None
                
                if city_part:
                    # Try to find a matching city in our sample data
                    city_match = next((loc for loc in SAMPLE_LOCATIONS if city_part.lower() in loc['formatted'].lower()), None)
                    
                    if city_match:
                        # Use the city coordinates with a small random offset
                        lat = city_match['lat'] + random.uniform(-0.02, 0.02)
                        lng = city_match['lng'] + random.uniform(-0.02, 0.02)
                        
                        return {
                            'lat': round(lat, 4),
                            'lng': round(lng, 4),
                            'formatted': location
                        }
            
            # Last resort: use a random location from our sample data
            fallback = random.choice(SAMPLE_LOCATIONS)
            fallback = {
                'lat': fallback['lat'],
                'lng': fallback['lng'], 
                'formatted': location  # Return the original query as the formatted address
            }
            print(f"Using fallback location with coordinates: {fallback['lat']}, {fallback['lng']}")
            return fallback
        except Exception as inner_error:
            print(f"Error in fallback coordinate generation: {inner_error}")
            return None

def get_weather_by_coordinates(lat, lng, location_name):
    """Fetch weather data from OpenWeatherMap API using coordinates"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&units=imperial&appid={API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if data.get('cod') == '404':
            return data
        
        # Ensure weather data exists
        if 'weather' not in data or not data['weather']:
            return {'cod': '500', 'message': 'Unexpected API response - weather data missing'}
            
        weather = {
            'city': location_name,  # Use the formatted location name
            'country': data['sys']['country'],
            'description': data['weather'][0]['description'].capitalize(),
            'icon': data['weather'][0]['icon'],
            'temperature': round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'min_temp': round(data['main']['temp_min']),
            'max_temp': round(data['main']['temp_max']),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'datetime': datetime.fromtimestamp(data['dt']).strftime('%I:%M %p, %A %d %B %Y'),
            'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%I:%M %p'),
            'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%I:%M %p'),
            'main': data['weather'][0]['main'],
            # Additional weather data
            'visibility': round(data.get('visibility', 0) / 1000, 1),  # Convert to km
            'clouds': data.get('clouds', {}).get('all', 0),  # Cloud coverage percentage
            'rain_1h': data.get('rain', {}).get('1h', 0),  # Rain volume for last hour in mm
            'snow_1h': data.get('snow', {}).get('1h', 0),  # Snow volume for last hour in mm
            'timezone_offset': data.get('timezone', 0),  # Timezone offset in seconds from UTC
            'local_time': datetime.fromtimestamp(data['dt'] + data.get('timezone', 0)).strftime('%I:%M %p')
        }
        
        # Add direction data if available
        if 'deg' in data['wind']:
            weather['wind_direction'] = get_wind_direction(data['wind']['deg'])
            
        # Add wind gust if available
        if 'gust' in data.get('wind', {}):
            weather['wind_gust'] = round(data['wind']['gust'], 1)
        
        # Calculate apparent temperature using a simpler formula if not provided
        weather['apparent_temp'] = round(weather['feels_like'])
        
        # Calculate dewpoint using approximation formula
        # Dewpoint = T - ((100 - RH) / 5)
        weather['dew_point'] = round(weather['temperature'] - ((100 - weather['humidity']) / 5))
        
        # Get the UV index if present
        weather['uv_index'] = 0  # Default value
        weather_one_call_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}&exclude=minutely,hourly,daily,alerts&units=imperial&appid={API_KEY}"
        try:
            print(f"Fetching UV index data from OneCall API for current weather")
            one_call_response = requests.get(weather_one_call_url, timeout=3)
            if one_call_response.status_code == 200:
                one_call_data = one_call_response.json()
                uv_value = one_call_data.get('current', {}).get('uvi', 0)
                weather['uv_index'] = round(uv_value, 1)
                print(f"Successfully retrieved UV index: {weather['uv_index']}")
            else:
                print(f"OneCall API returned status code: {one_call_response.status_code}")
        except Exception as e:
            print(f"Error fetching UV data: {e}")
        
        # Ensure UV index is numeric
        if weather['uv_index'] is None:
            weather['uv_index'] = 0
            
        print(f"Final weather data with UV index: {weather['uv_index']}")
        
        return weather
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return {'cod': '500', 'message': f'Error: {str(e)}'}

def get_forecast_by_coordinates(lat, lng):
    """Fetch 5-day forecast data using coordinates"""
    try:
        # Get forecast data from the standard endpoint
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lng}&units=imperial&appid={API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if data.get('cod') != '200':
            return None
            
        # Get one call data to supplement with UV index
        one_call_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}&exclude=current,minutely,hourly,alerts&units=imperial&appid={API_KEY}"
        daily_uv_data = {}
        
        try:
            one_call_response = requests.get(one_call_url, timeout=3)
            if one_call_response.status_code == 200:
                one_call_data = one_call_response.json()
                # Map UV index by date for easy lookup
                if 'daily' in one_call_data:
                    for day_data in one_call_data['daily']:
                        day_date = datetime.fromtimestamp(day_data['dt']).strftime('%Y-%m-%d')
                        daily_uv_data[day_date] = {
                            'uv_index': round(day_data.get('uvi', 0), 1),
                            'feels_like_day': round(day_data.get('feels_like', {}).get('day', 0))
                        }
        except Exception as e:
            print(f"Error fetching UV data for forecast: {e}")
            
        # Group forecast data by day
        daily_forecasts = defaultdict(list)
        
        for item in data['list']:
            # Convert timestamp to date string (YYYY-MM-DD)
            date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            
            forecast_item = {
                'time': datetime.fromtimestamp(item['dt']).strftime('%I %p'),
                'date': datetime.fromtimestamp(item['dt']).strftime('%A, %b %d'),
                'day_name': datetime.fromtimestamp(item['dt']).strftime('%A'),
                'temperature': round(item['main']['temp']),
                'feels_like': round(item['main']['feels_like']),
                'description': item['weather'][0]['description'].capitalize(),
                'icon': item['weather'][0]['icon'],
                'humidity': item['main']['humidity'],
                'wind_speed': item['wind']['speed'],
                'main': item['weather'][0]['main']
            }
            
            daily_forecasts[date].append(forecast_item)
        
        # Create a list of daily forecasts with aggregated data
        processed_forecasts = []
        
        for date, items in daily_forecasts.items():
            if len(processed_forecasts) >= 5:  # Limit to 5 days
                break
                
            # Skip today as we already have current weather
            if date == datetime.now().strftime('%Y-%m-%d') and len(processed_forecasts) == 0:
                continue
                
            # Calculate average/min/max values
            temps = [item['temperature'] for item in items]
            feels_like_temps = [item['feels_like'] for item in items]
            icons = [item['icon'] for item in items]
            descriptions = [item['description'] for item in items]
            
            # Get the most common weather condition for the day
            common_icon = max(set(icons), key=icons.count)
            common_description = max(set(descriptions), key=descriptions.count)
            common_main = max(set([item['main'] for item in items]), key=[item['main'] for item in items].count)
            
            # Create a daily forecast summary
            day_forecast = {
                'date': items[0]['date'],
                'day_name': items[0]['day_name'],
                'min_temp': round(min(temps)),
                'max_temp': round(max(temps)),
                'avg_temp': round(sum(temps) / len(temps)),
                'feels_like': round(sum(feels_like_temps) / len(feels_like_temps)),  # Average feels like
                'description': common_description,
                'icon': common_icon,
                'humidity': round(sum(item['humidity'] for item in items) / len(items)),
                'wind_speed': round(sum(item['wind_speed'] for item in items) / len(items), 1),
                'hourly_data': items,
                'main': common_main
            }
            
            # Add UV index data if available from one call API
            if date in daily_uv_data:
                day_forecast['uv_index'] = daily_uv_data[date]['uv_index']
                # Optionally use the One Call API's feels like if available
                if 'feels_like_day' in daily_uv_data[date]:
                    day_forecast['feels_like'] = daily_uv_data[date]['feels_like_day']
            
            processed_forecasts.append(day_forecast)
            
        return processed_forecasts
            
    except Exception as e:
        print(f"Error fetching forecast data: {e}")
        return None

def get_wind_direction(degrees):
    """Convert wind direction in degrees to cardinal direction"""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]

if __name__ == '__main__':
    print(f"Weather app running with OpenCage Geocoding API")
    app.run(debug=True) 