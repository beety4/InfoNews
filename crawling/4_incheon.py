import requests
from bs4 import BeautifulSoup

# 웹사이트 URL 설정
url = "https://www.incheon.go.kr/IC010205"
# 웹페이지 요청
response = requests.get(url)

# 요청 성공 여부 확인
if response.status_code == 200:
    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 뉴스 데이터 선택
    news_list = soup.select('#content2024 .board-blog-list ul li')

    for news in news_list:
        # 링크와 제목
        link_tag = news.select_one('a')  # 각 뉴스 항목의 링크
        if link_tag:
            link_str = link_tag['href']
            link = "https://www.incheon.go.kr" + link_str
            title = link_tag.select_one('.subject').text.strip()

        # 날짜 정보 추출
        date_tag = news.select_one('.board-item-area dt')
        date = date_tag.find_next_sibling('dd').text.strip()

        # 날짜 형식 변환 (YYYY-MM-DD → YYYY.MM.DD)
        date = date.replace('-', '.')

        # 출력
        print(f"제목: {title}")
        print(f"링크: {link}")
        print(f"날짜: {date}")
        print("-" * 100)

else:
    print(f"Failed to fetch the page, status code: {response.status_code}")
