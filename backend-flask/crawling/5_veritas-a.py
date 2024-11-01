import requests
from bs4 import BeautifulSoup

# 웹사이트 URL 설정
url = "https://www.veritas-a.com/news/articleList.html?sc_section_code=&view_type=sm"
# 웹페이지 요청
response = requests.get(url)

# 요청 성공 여부 확인
if response.status_code == 200:
    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 뉴스 데이터 선택
    news_list = soup.select('#section-list > ul > li')

    for news in news_list:
        # 제목과 링크
        title_tag = news.select_one('div h2 a')
        if title_tag:
            title = title_tag.text.strip()
            link_str = title_tag['href']
            link = "https://www.veritas-a.com" + link_str

        # 날짜
        write_info = news.select_one('.byline')
        if write_info:
            date_em = write_info.select('em')[2]
            date = date_em.text.strip()

            date = date.split(' ')[0]

        # 출력
        print(f"제목: {title}")
        print(f"링크: {link}")
        print(f"날짜: {date}")
        print("-" * 100)
else:
    print(f"Failed to fetch the page, status code: {response.status_code}")
