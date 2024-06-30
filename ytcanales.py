import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Función para obtener videos populares
def get_popular_videos(api_key, max_results=50, region_code='ES', published_after=None, published_before=None):
    # Configuración de la API de YouTube
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Parámetros de búsqueda
    search_params = {
        'part': 'snippet',
        'type': 'video',
        'order': 'viewCount',
        'regionCode': region_code,
        'maxResults': max_results,
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

    return video_ids

# Función para obtener detalles de los canales basados en videos populares
def get_channel_details(api_key, video_ids):
    # Configuración de la API de YouTube
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Obtener detalles de los videos encontrados
    videos_request = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    )
    videos_response = videos_request.execute()

    # Crear una lista para almacenar los datos de todos los canales
    all_data = []

    # Iterar sobre los videos obtenidos
    for video in videos_response.get('items', []):
        channel_id = video['snippet']['channelId']
        channel_request = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        channel_response = channel_request.execute()
        channel = channel_response['items'][0]

        channel_data = {
            'ChannelTitle': channel['snippet']['title'],
            'Subscribers': int(channel['statistics'].get('subscriberCount', 0)),
            'TotalViews': int(channel['statistics'].get('viewCount', 0)),
            'TotalVideos': int(channel['statistics'].get('videoCount', 0)),
            'CreationDate': pd.to_datetime(channel['snippet']['publishedAt']).replace(tzinfo=None),
            'VideoTitle': video['snippet']['title'],
            'VideoViews': int(video['statistics'].get('viewCount', 0))
        }
        all_data.append(channel_data)

    # Convertir la lista de datos en un DataFrame de pandas
    df = pd.DataFrame(all_data)

    # Seleccionar las columnas de interés para el análisis
    df = df[['ChannelTitle', 'Subscribers', 'TotalViews', 'TotalVideos', 'CreationDate', 'VideoTitle', 'VideoViews']]

    return df

# Función para guardar los datos en un archivo CSV
def save_to_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f'Datos guardados en {filename}')

# Función principal para ejecutar el script
def main():
    api_key = os.getenv('YOUTUBE_API_KEY')
    max_results = 50  
    region_code = 'ES' 
    published_after = '2023-01-01T00:00:00Z'  
    published_before = '2024-01-01T00:00:00Z' 

    if api_key:
        # Obtener videos populares
        video_ids = get_popular_videos(api_key, max_results, region_code, published_after, published_before)
        
        # Obtener detalles de los canales basados en los videos populares
        df = get_channel_details(api_key, video_ids)

        # Guardar los datos en un archivo CSV
        csv_filename = 'popular_channels.csv'
        save_to_csv(df, csv_filename)
    else:
        print('No se encontró una clave de API de YouTube válida en el archivo .env')

if __name__ == "__main__":
    main()
