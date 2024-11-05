from datetime import datetime
from naver_api import NaverAPI


def search_item(search, target_count=15):
    api = NaverAPI()
    result_lst = []
    start = 1

    while len(result_lst) < target_count:
        result = api.search_news(search, start=start)

        # 검색 실패 시 종료
        if not result:
            print("API에서 결과를 받지 못했습니다.")
            break

        # 데이터 전처리
        for item in result['items']:
            title = item['title']
            link = item['link']
            date_str = item['pubDate']

            # HTML 인코딩 및 태그 제거
            title = title.replace("&quot;", '"').replace("&amp;", '&').replace("<b>", "").replace("</b>", "")

            # 제목에 검색어가 포함된 뉴스만 추가
            if search in title:
                date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                date = date_obj.strftime('%Y.%m.%#d')

                temp_dict = {"title": title, "link": link, "date": date}
                result_lst.append(temp_dict)

                # print(f"제목: {title}")
                # print(f"링크: {link}")
                # print(f"날짜: {date}")
                # print("-" * 100)

                # 목표 개수에 도달하면 종료
                if len(result_lst) >= target_count:
                    break

        # `start` 위치를 다음 100개로 이동
        start += 100

        # 네이버 API의 결과가 더 이상 없을 경우 종료
        if len(result['items']) < 100:
            break

    return result_lst