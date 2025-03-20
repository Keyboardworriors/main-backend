from django.conf import settings
from googleapiclient.discovery import build

from ytmusicapi import YTMusic



YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
youtube = build("youtube", "v3", developerKey="YOUTUBE_API_KEY")
ytmusic = YTMusic()


# Genai 통해 받은 음악 리스트를 유튜브에 검색해 정보 반환
def get_youtube(title,artist):
    query = f'{title} {artist} official' # 검색어 설정
    search_results = ytmusic.search(query=query,filter="songs", limit=1)

    if not search_results:
        return None

    music = search_results[0]
    return {
        "videoId": music["videoId"],
        "title": music["title"],
        "artist": music["artists"][0]["name"] if "artists" in music else "Unknown",
        "thumbnail": music["thumbnails"][-1]["url"],  # 가장 고화질 썸네일
        "embedUrl": f"https://www.youtube.com/embed/{music['videoId']}",
    }



