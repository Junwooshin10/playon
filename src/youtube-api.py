"""
Google Cloud Platform에서 새로운 프로젝트를 생성하고 YouTube Data API v3를 활성화합니다.
API 사용을 위해 API 키를 발급받습니다.


"""
import requests

API_KEY = 'YOUR_API_KEY'
search_query = '스포츠 부상'
url = 'https://www.googleapis.com/youtube/v3/search'

params = {
    'part': 'snippet',
    'q': search_query,
    'type': 'video',
    'maxResults': 50,
    'key': API_KEY
}

response = requests.get(url, params=params)
data = response.json()


# import requests

# API_KEY = 'YOUR_API_KEY'
# search_query = '스포츠 부상'
# url = 'https://www.googleapis.com/youtube/v3/search'

# params = {
#     'part': 'snippet',
#     'q': search_query,
#     'type': 'video',
#     'maxResults': 50,
#     'key': API_KEY
# }

# response = requests.get(url, params=params)
# data = response.json()

# # 수집한 데이터 출력
# for item in data['items']:
#     video_id = item['id']['videoId']
#     title = item['snippet']['title']
#     description = item['snippet']['description']
#     publish_time = item['snippet']['publishedAt']
#     channel_title = item['snippet']['channelTitle']
#     print(f"Video ID: {video_id}")
#     print(f"Title: {title}")
#     print(f"Description: {description}")
#     print(f"Published At: {publish_time}")
#     print(f"Channel Title: {channel_title}")
#     print("-" * 40)