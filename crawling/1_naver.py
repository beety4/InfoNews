import requests
from bs4 import BeautifulSoup

search = "마루"

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

    for news in news_list:
        # 제목과 링크
        title_tag = news.select_one('div.news_wrap.api_ani_send > div > div.news_contents > a.news_tit')
        title = title_tag['title']
        link = title_tag['href']

        # 날짜
        date = news.select_one('div.news_wrap.api_ani_send > div > div.news_info > div.info_group > span').text.strip()

        # 출력
        print(f"제목: {title}")
        print(f"링크: {link}")
        print(f"시간: {date}")
        print("-" * 100)
else:
    print("naver 크롤링에 실패하였습니다.")
