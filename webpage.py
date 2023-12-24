from flask import Flask, render_template
from datetime import datetime
import time
import threading

import requests
import json

app = Flask(__name__)

def update_time():
    while True:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        time.sleep(1)
        socketio.emit('update_time', {'time': current_time}, namespace='/test')
        
def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 48.74,
        "longitude": 9.10,
        "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "snowfall", "weather_code", "apparent_temperature", "is_day"],
        "daily": ["sunrise", "sunset", "daylight_duration", "uv_index_max"],
        "timezone": "auto",
        "forecast_days": 1,
    }
    resp = requests.get(url, params=params)
    print(resp.url)

    weather_code = resp.json()['current']['weather_code']
    is_day = resp.json()['current']['is_day']
    weather_code_descriptor = ''
    # Fetch the weather url from descriptions.json using weather_code
    with open('/root/descriptions.json') as f:
        descriptions = json.load(f)
        weather_code_descriptor = descriptions[str(weather_code)][str(is_day)]
    
    print(weather_code_descriptor['image'])
    
    return {
        "temperature": resp.json()['current']['temperature_2m'],
        "humidity": resp.json()['current']['relative_humidity_2m'],
        "precipitation": resp.json()['current']['precipitation'],
        "rain": resp.json()['current']['rain'],
        "snowfall": resp.json()['current']['snowfall'],
        "weather_code_description": weather_code_descriptor['description'],
        "weather_code_image": weather_code_descriptor['image'],
        "apparent_temperature": resp.json()['current']['apparent_temperature'],
        "is_day": "Day" if resp.json()['current']['is_day'] else "Night",
        "sunrise": resp.json()['daily']['sunrise'][0],
        "sunset": resp.json()['daily']['sunset'][0],
        "uv_index_max": resp.json()['daily']['uv_index_max'][0],
    }

    

@app.route('/')
def home():
    weather = get_weather()
    return render_template(
        'index.html', 
        address='42B-304 Pfaffenhof, 70569 Stuttgart',
        temperature=weather['temperature'],
        humidity=weather['humidity'],
        precipitation=weather['precipitation'],
        rain=weather['rain'],
        snowfall=weather['snowfall'],
        weather_description=weather['weather_code_description'],
        weather_image=weather['weather_code_image'],
        apparent_temperature=weather['apparent_temperature'],
        sunrise=weather['sunrise'],
        sunset=weather['sunset'],
        uv_index_max=weather['uv_index_max'],
    )

if __name__ == '__main__':
    from flask_socketio import SocketIO

    socketio = SocketIO(app)

    threading.Thread(target=update_time, daemon=True).start()

    @socketio.on('connect', namespace='/test')
    def test_connect():
        print('Client connected')

    @socketio.on('disconnect', namespace='/test')
    def test_disconnect():
        print('Client disconnected')

    socketio.run(app, debug=True, host='0.0.0.0', allow_unsafe_werkzeug=True)
