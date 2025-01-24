import os
import requests

API_KEY = os.environ.get('YOUTUBE_API_KEY')  # Typically set as an environment variable
url = 'https://www.googleapis.com/youtube/v3/search'

#-----------------------------------
# Fetch data using YouTube API
#-----------------------------------
def fetch_youtube_data(category, query="sports injury", max_results=10):
    """
    Fetches search results for the given 'query' using the YouTube Data API.
    Returns: A list of video information (title, videoId, channelTitle, etc.)
    """
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'order': 'rating',
        'key': API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    # print('result', data)

    video_list = []
    items = data.get("items", [])
    for item in items:
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]
        video_info = {
            "category": category,
            "keyword": query,
            "title": snippet["title"],
            "video_id": video_id,
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "thumbnail_url": snippet['thumbnails']['medium']['url'],
            "channel_title": snippet["channelTitle"],
            "published_at": snippet["publishedAt"]
        }
        video_list.append(video_info)
    return video_list