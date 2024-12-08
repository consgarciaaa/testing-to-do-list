import requests
from flask import Blueprint, jsonify, request, current_app

# Registrar Blueprint
bp = Blueprint("movies", __name__, url_prefix="/api/movies")

# Endpoint de Búsqueda de Películas
@bp.route('/search', methods=['GET'])
def search_movie():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Validar la existencia del token de API
    api_token = current_app.config.get('TMDB_ACCESS_TOKEN')
    if not api_token:
        return jsonify({"error": "API token is not configured"}), 500

    url = "https://api.themoviedb.org/3/search/movie"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json;charset=utf-8"
    }

    params = {
        "query": query
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                return jsonify(results), 200
            else:
                return jsonify({"error": "No movies found"}), 404
        else:
            return jsonify({"error": f"API request failed: {response.status_code}"}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Could not fetch data"}), 500
