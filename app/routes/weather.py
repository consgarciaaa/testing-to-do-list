import requests
from flask import Blueprint, jsonify, request
from flask_login import login_required

bp = Blueprint('weather', __name__, url_prefix='/api/weather')

@bp.route('/current', methods=['GET'])
@login_required
def get_weather():
    # Obtener la ciudad o usar una predeterminada
    city = request.args.get('city', 'Guadalajara')

    # Coordenadas para Guadalajara (puedes agregar más ciudades si lo necesitas)
    city_coordinates = {
        'Guadalajara': {'latitude': 20.6597, 'longitude': -103.3496},
        'London': {'latitude': 51.5074, 'longitude': -0.1278},
        'New York': {'latitude': 40.7128, 'longitude': -74.0060}
    }

    # Verificar si la ciudad está en la lista
    if city not in city_coordinates:
        return jsonify({"error": "Ciudad no encontrada. Prueba Guadalajara, London o New York."}), 400

    # Obtener las coordenadas
    latitude = city_coordinates[city]['latitude']
    longitude = city_coordinates[city]['longitude']

    # Hacer la solicitud a la API
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return jsonify({
            "city": city,
            "temperature": data['current_weather']['temperature'],
            "windspeed": data['current_weather']['windspeed'],
            "weathercode": data['current_weather']['weathercode']
        })
    else:
        return jsonify({"error": "No se pudo obtener el clima. Verifica la ciudad o la API."}), 400
