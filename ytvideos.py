import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Función para obtener los videos más populares dentro de un rango de fechas
# Formato para published: "2024-01-01T00:00:00Z" y ir cambiandolo
def get_popular_videos(api_key, max_results=50, published_after=None, published_before=None):
    # Configuración de la API de YouTube
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Parámetros de búsqueda
    search_params = {
        'part': 'snippet',
        'type': 'video',
        'order': 'viewCount',
        'maxResults': max_results,
        'regionCode': 'US' 
    }

    if published_after:
        search_params['publishedAfter'] = published_after

    if published_before:
        search_params['publishedBefore'] = published_before

    # Realizar la búsqueda de videos populares
    search_request = youtube.search().list(**search_params)
    search_response = search_request.execute()

    # Extraer los IDs de los videos encontrados en la búsqueda
    video_ids = [item['id']['videoId'] for item in search_response['items']]

    # Obtener detalles de los videos encontrados
    videos_request = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    )
    videos_response = videos_request.execute()

    # Crear una lista para almacenar los datos de todos los videos
    all_data = []

    # Iterar sobre los videos obtenidos
    for video in videos_response.get('items', []):
        video_data = {
            'VideoTitle': video['snippet']['title'],
            'ChannelTitle': video['snippet']['channelTitle'],
            'PublishDate': pd.to_datetime(video['snippet']['publishedAt']).replace(tzinfo=None),
            'Views': int(video['statistics'].get('viewCount', 0)),
            'Likes': int(video['statistics'].get('likeCount', 0)),
            'Comments': int(video['statistics'].get('commentCount', 0))
        }
        all_data.append(video_data)

    # Convertir la lista de datos en un DataFrame de pandas
    df = pd.DataFrame(all_data)

    # Seleccionar las columnas de interés para el análisis
    df = df[['VideoTitle', 'ChannelTitle', 'PublishDate', 'Views', 'Likes', 'Comments']]

    return df

# Función para guardar los datos en un archivo CSV
def save_to_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f'Datos guardados en {filename}')

# Función principal para ejecutar el script
def main():
    api_key = os.getenv('YOUTUBE_API_KEY')
    max_results = 50 

    # Fechas de búsqueda
    published_after = (datetime.now() - timedelta(days=30)).isoformat("T") + "Z"  # Últimos 30 días
    published_before = datetime.now().isoformat("T") + "Z"  # Hasta hoy

    if api_key:
        # Obtener datos de videos populares
        df = get_popular_videos(api_key, max_results, published_after, published_before)

        # Guardar los datos en un archivo CSV
        csv_filename = 'popular_videos_region_fecha.csv'
        save_to_csv(df, csv_filename)
    else:
        print('No se encontró una clave de API de YouTube válida en el archivo .env')

if __name__ == "__main__":
    main()
