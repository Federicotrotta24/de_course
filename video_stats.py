import requests
import json
import os
from dotenv import load_dotenv  

load_dotenv(dotenv_path="./.env")



API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
max_results = 50


url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"


def get_playlist_id(channel_handle, api_key):
    try: 
        response = requests.get(f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_handle}&key={api_key}")
        data = response.json()
        json.dumps(data, indent=4)
        channel_items = data["items"][0] 
        channel_playlistsId = channel_items["contentDetails"]["relatedPlaylists"]['uploads']
        return channel_playlistsId
    except requests.exceptions.RequestException  as e:
        raise Exception(f"An error occurred while making the API request: {e}")



def get_videos_id (playlist_id):
    video_ids = []

    pageToken = None

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlist_id}&key={API_KEY}"

    try:

        while True:

            url = base_url

            if pageToken:
                url += f"&pageToken={pageToken}"

            response = requests.get(url)

            response.raise_for_status()

            data = response.json()

            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        return video_ids
    except requests.exceptions.RequestException  as e:
        raise e



if __name__ == "__main__":    
    playlist_id = get_playlist_id(CHANNEL_HANDLE, API_KEY)
    print(get_videos_id(playlist_id))





base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlist_id}&key={API_KEY}"