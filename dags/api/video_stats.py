import requests
import json
from datetime import datetime

from airflow.decorators import task
from airflow.models import Variable

API_KEY = Variable.get("API_KEY")
CHANNEL_HANDLE = Variable.get("CHANNEL_HANDLE")
max_results = 50


@task
def get_playlist_id(channel_handle, api_key):
    try: 
        response = requests.get(
            f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_handle}&key={api_key}"
        )
        response.raise_for_status()
        data = response.json()

        channel_items = data["items"][0]
        channel_playlistsId = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]
        return channel_playlistsId

    except requests.exceptions.RequestException as e:
        raise Exception(f"An error occurred while making the API request: {e}")


@task
def get_videos_id(playlist_id):
    video_ids = []
    pageToken = None

    base_url = (
        f"https://youtube.googleapis.com/youtube/v3/playlistItems"
        f"?part=contentDetails"
        f"&maxResults={max_results}"
        f"&playlistId={playlist_id}"
        f"&key={API_KEY}"
    )

    try:
        while True:
            url = base_url

            if pageToken:
                url += f"&pageToken={pageToken}"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)

            pageToken = data.get("nextPageToken")

            if not pageToken:
                break

        return video_ids

    except requests.exceptions.RequestException as e:
        raise e


@task
def extract_videos_data(video_ids):
    extracted_data = []

    def batch_list(video_id_lst, batch_size):
        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id : video_id + batch_size]

    try:
        for batch in batch_list(video_ids, max_results):
            video_ids_str = ",".join(batch)

            url = (
                f"https://youtube.googleapis.com/youtube/v3/videos"
                f"?part=contentDetails,snippet,statistics"
                f"&id={video_ids_str}"
                f"&key={API_KEY}"
            )

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                video_id = item["id"]
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]

                video_data = {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "publishedAt": snippet["publishedAt"],
                    "duration": contentDetails["duration"],
                    "viewCount": statistics.get("viewCount"),
                    "likeCount": statistics.get("likeCount"),
                    "commentCount": statistics.get("commentCount"),
                }

                extracted_data.append(video_data)

        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e


@task
def save_data_to_json(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/opt/airflow/data/video_stats_{timestamp}.json"

    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Saved file: {filename}")