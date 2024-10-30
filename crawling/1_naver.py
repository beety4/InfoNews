import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

search = "마그네틱"

# 웹사이트 URL 설정
url = "https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query=" + search + "&sort=date"
# 웹페이지 요청
response = requests.get(url)

# 요청 성공 여부 확인
if response.status_code == 200:
    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 뉴스 데이터 div 선택
    news_list = soup.select('#main_pack > section > div.api_subject_bx > div.group_news > ul > li')

    # 현재 시간
    now = datetime.now()

    for news in news_list:
        # 제목과 링크
        title_tag = news.select_one('div.news_wrap.api_ani_send > div > div.news_contents > a.news_tit')
        title = title_tag['title']
        link = title_tag['href']

        # 날짜 전처리
        date_text = news.select_one(
            'div.news_wrap.api_ani_send > div > div.news_info > div.info_group > span').text.strip()

        if "시간 전" in date_text:
            hours_ago = int(re.search(r'\d+', date_text).group())
            news_time = now - timedelta(hours=hours_ago)
            formatted_date = news_time.strftime("%Y.%m.%d")
        elif "분 전" in date_text:
            minutes_ago = int(re.search(r'\d+', date_text).group())
            news_time = now - timedelta(minutes=minutes_ago)
            formatted_date = news_time.strftime("%Y.%m.%d")
        elif "일 전" in date_text:
            days_ago = int(re.search(r'\d+', date_text).group())
            news_time = now - timedelta(days=days_ago)
            formatted_date = news_time.strftime("%Y.%m.%d")
        elif "주 전" in date_text:
            weeks_ago = int(re.search(r'\d+', date_text).group())  # 숫자 부분 추출
            news_time = now - timedelta(weeks=weeks_ago)
            formatted_date = news_time.strftime("%Y.%m.%d")
        else:
            # "YYYY.MM.DD" 형식
            formatted_date = date_text

        # 출력
        print(f"제목: {title}")
        print(f"링크: {link}")
        print(f"날짜: {formatted_date}")
        print("-" * 100)
else:
    print(f"Failed to fetch the page, status code: {response.status_code}")
