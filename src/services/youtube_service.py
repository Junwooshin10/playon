import os
import requests

API_KEY =  os.environ.get('YOUTUBE_API_KEY')  # 실제로는 os.environ.get('YOUTUBE_API_KEY') 등
url = 'https://www.googleapis.com/youtube/v3/search'

#-----------------------------------
# YouTube API로 데이터 가져오기 
#-----------------------------------
def fetch_youtube_data(category, query="스포츠 부상", max_results=10):
    """
    YouTube Data API를 통해 'query' 검색 결과를 가져옵니다.
    반환: 동영상 정보 리스트 (title, videoId, channelTitle 등)
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
    print('result', data)

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