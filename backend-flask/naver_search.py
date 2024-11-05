from datetime import datetime
from naver_api import NaverAPI


def search_item(search):
    api = NaverAPI()
    result = api.search_news(search)

    # 데이터 전처리
    if result:
        result_lst = []
        for item in result['items']:
            title = item['title']
            link = item['link']
            date_str = item['pubDate']
            if "&quot;" in title or "&amp;" in title:
                title = title.replace("&quot;", '"').replace("&amp;", '&')
            date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            date = date_obj.strftime('%Y.%m.%#d')

            # 출력
            temp_dict = {"title": title, "link": link, "date": date}
            result_lst.append(temp_dict)

            #print(f"제목: {title}")
            #print(f"링크: {link}")
            #print(f"날짜: {date}")
            #print("-" * 100)

        return result_lst

