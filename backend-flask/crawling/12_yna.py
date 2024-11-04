import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_data():
    url = 'https://www.yna.co.kr/news?site=navi_latest_depth01'
    response = requests.get(url)

    # 연도 정보 부재로 현재 연도로 대체(수정 필요)
    current_year = datetime.now().year

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # ul.list의 li 요소를 선택
        news_list = soup.select('ul.list li')

        result = []
        for news in news_list:
            title_tag = news.select_one('strong.tit-news')

            # 제목이 존재하는지 확인
            if title_tag:
                title = title_tag.text.strip()
            else:  # HTML상 비어있는 li 요소 존재
                continue

            date_text = news.select_one('span.txt-time')
            if date_text:
                # 10-30 18:00
                date_text = date_text.text.strip()
                # 10-30
                date_unformatted = date_text.split(' ')[0]
                # 2024.10.30
                date = f"{current_year}.{date_unformatted.replace('-', '.')}"

            link = soup.select_one('div.news-con a').attrs['href']

            #print(f"제목: {title}")
            #print(f"날짜: {date}")
            #print(f"링크: {link}")
            #print("-" * 100)
            dict_data = {"title": title, "link": link, "date": date}
            result.append(dict_data)

        return result
    else:
        print(f"HTTP 요청 실패: {response.status_code}")

