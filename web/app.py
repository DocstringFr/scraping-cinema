from flask import Flask, render_template
import json
import os
from datetime import datetime
import locale

app = Flask(__name__)

# Configuration de la locale en français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

@app.template_filter('strftime')
def strftime_filter(date_str, format_str):
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime(format_str)
    except:
        return date_str

def get_latest_json_file():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not json_files:
        return None
    latest_file = max(json_files, key=lambda x: os.path.getctime(os.path.join(data_dir, x)))
    return os.path.join(data_dir, latest_file)

def format_datetime(date_str):
    try:
        # Conversion de la chaîne ISO en objet datetime
        dt = datetime.fromisoformat(date_str)
        # Formatage en français
        return dt.strftime("%d/%m/%Y à %H:%M:%S")
    except:
        return "Date inconnue"

@app.route('/')
def index():
    json_file = get_latest_json_file()
    if not json_file:
        return "Aucun fichier de données trouvé"

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    movies_data = data.get('movies', [])
    scraping_date = format_datetime(data.get('export_date', ''))
    movies_with_schedules = [movie for movie in movies_data if movie.get('schedules')]
    
    movies_to_display = [{
        'title': movie['metadata']['title'],
        'duration': f"{movie['metadata'].get('duration', 'Non spécifié')} min",
        'genres': [movie['metadata'].get('genre', 'Non spécifié')],  # Le genre est une chaîne unique dans le JSON
        'synopsis': movie['metadata'].get('synopsis', 'Synopsis non disponible'),
        'image_url': f"https:{movie['metadata'].get('portraitimages', {}).get('path', '')}",
        'version': movie['metadata'].get('version', ''),
        'format': movie['metadata'].get('format', ''),
        'schedules': [{
            'date': schedule['date'],
            'cinemas': [{
                'cinema_name': cinema['name'],
                'times': [session.get('time', '') for session in cinema.get('sessions', [])]
            } for cinema in schedule.get('cinemas', [])]
        } for schedule in movie.get('schedules', [])]
    } for movie in movies_with_schedules]
    
    return render_template('index.html', 
                         movies=movies_to_display,
                         scraping_date=scraping_date)

if __name__ == '__main__':
    app.run(debug=True, port=5001) 