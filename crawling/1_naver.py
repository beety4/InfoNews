from datetime import datetime
import requests

client_id = ""
client_secret = ""

# 검색
def search_news(search, display=15, start=1, sort="date"):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": search,
        "display": display,
        "start": start,
        "sort": sort
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch the page, status code: {response.status_code}")
        return None


if __name__ == "__main__":
    search = "입시"
    result = search_news(search)

    if result:
        for item in result['items']:
            title = item['title']
            link = item['link']
            date_str = item['pubDate']
            if "&quot;" in title or "&amp;" in title:
                title = title.replace("&quot;", '"').replace("&amp;", '&')
            date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            date = date_obj.strftime('%Y.%m.%#d')

            # 출력
            print(f"제목: {title}")
            print(f"링크: {link}")
            print(f"날짜: {date}")
            print("-" * 100)