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

        
def extract_video_data(video_ids):
    extracted_data = []

    def batch_list(video_id_lst, batch_size):
        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id : video_id + batch_size]

    try:
        for batch in batch_list(video_ids, max_results):
            video_ids_str = ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails,snippet,statistics&id={video_ids_str}&key={API_KEY}"

            response = requests.get(url)

            response.raise_for_status()

            data = response.json()

            for item in data.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                video_data = {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "publishedAt": snippet["publishedAt"],
                    "duration": contentDetails["duration"],
                    "viewCount": statistics.get("viewCount", None),
                    "likeCount": statistics.get("likeCount", None),
                    "commentCount": statistics.get("commentCount", None),
                }

                extracted_data.append(video_data)

        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e


def save_data_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)    

if __name__ == "__main__":    
    playlist_id = get_playlist_id(CHANNEL_HANDLE, API_KEY)
    video_ids = get_videos_id(playlist_id)
    video_data = extract_video_data(video_ids)
    save_data_to_json(video_data, "video_data.json")




base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxesults={max_results}&playlistId={playlist_id}&key={API_KEY}"