import requests
from bs4 import BeautifulSoup

def get_data():
    # 가져올 웹사이트 주소
    url = "https://dhnews.co.kr/news/cate/"

    # 웹페이지 요청
    response = requests.get(url)

    # 요청 성공 여부 확인
    if response.status_code == 200:
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        # 뉴스 데이터 div 선택
        news_list = soup.select('div#listWrap div.listPhoto')

        result = []
        for news in news_list:
            title_tag = news.select_one('dl dt a')
            title = title_tag.text.strip()
            date = news.select_one('dd.winfo span.date').text.strip()
            link = "https://dhnews.co.kr" + title_tag.attrs['href']

            #print(f"제목: {title}")
            #print(f"날짜: {date}")
            #print(f"링크: {link}")
            #print("-" * 100)
            dict_data = {"title": title, "link": link, "date": date}
            result.append(dict_data)

        return result

    # 웹사이트 요청 실패 시 출력
    else:
        print(f"Failed to fetch the page, status code: {response.status_code}")


