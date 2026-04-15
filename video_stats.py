import requests
import json
import os
from dotenv import load_dotenv  

load_dotenv(dotenv_path="./.env")



API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
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



    



if __name__ == "__main__":    
    playlist_id = get_playlist_id(CHANNEL_HANDLE, API_KEY)
    print(playlist_id)


