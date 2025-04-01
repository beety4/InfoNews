import requests
from bs4 import BeautifulSoup


def get_data():
    # 웹사이트 URL 설정
    url = "https://www.incheon.go.kr/IC010205"
    # 웹페이지 요청
    response = requests.get(url)

    # 요청 성공 여부 확인
    if response.status_code == 200:
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        # 뉴스 데이터 선택
        news_list = soup.select('.board-article-group')  # 'board-article-group' 클래스의 요소 선택

        result = []
        for news in news_list:
            # 링크 추출
            link_tag = news.find_parent('a')
            if link_tag:
                link = "https://www.incheon.go.kr" + link_tag['href']

            # 제목 추출
            title_tag = news.select_one('.subject')
            if title_tag:
                title = title_tag.text.strip()

            # 날짜 정보 추출
            date_tag = news.select_one('.board-item-area dt:-soup-contains("제공일자")')
            if date_tag:
                date = date_tag.find_next_sibling('dd').text.strip()
                date = date.replace('-', '.')

            # 출력
            #print(f"제목: {title}")
            #print(f"링크: {link}")
            #print(f"날짜: {date}")
            #print("-" * 100)

            dict_data = {"title": title, "link": link, "date": date}
            result.append(dict_data)
            
        return {"인천광역시보도자료": result}
    else:
        print(f"Failed to fetch the page, status code: {response.status_code}")
        return {"Error": response.status_code}
