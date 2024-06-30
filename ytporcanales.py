import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Definir la función para obtener los datos de YouTube de un canal
def get_youtube_data(api_key, channel_id, max_results=50):
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Realizar la solicitud para obtener los videos del canal
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=max_results,
        order='date'
    )
    response = request.execute()

    video_data = []
    for item in response['items']:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        publish_date = item['snippet']['publishedAt']
        description = item['snippet']['description'] 
        # Obtener estadísticas del video
        stats_request = youtube.videos().list(
            part='statistics',
            id=video_id
        )
        stats_response = stats_request.execute()
        if stats_response['items']:
            view_count = stats_response['items'][0]['statistics']['viewCount']
            like_count = stats_response['items'][0]['statistics'].get('likeCount', 0)
        else:
            view_count = 0
            like_count = 0

        video_data.append({
            'Video ID': video_id,
            'Title': title,
            'Publish Date': publish_date,
            'Description': description,
            'Views': view_count,
            'Likes': like_count
        })

    return video_data

def main():
    api_key = os.getenv('YOUTUBE_API_KEY')
    channel_id = 'UC_x5XG1OV2P6uZZ5FSM9Ttw' # Aca va la ID
    max_results = 50  

    if api_key:
        # Obtener datos de YouTube
        data = get_youtube_data(api_key, channel_id, max_results)

        # Convertir a DataFrame de pandas
        df = pd.DataFrame(data)

        # Guardar el DataFrame en un archivo CSV
        csv_filename = 'youtube_data.csv'
        df.to_csv(csv_filename, index=False)

        print(f'Datos de YouTube guardados en {csv_filename}')
    else:
        print('No se encontró una clave de API de YouTube válida en el archivo .env')

if __name__ == "__main__":
    main()
