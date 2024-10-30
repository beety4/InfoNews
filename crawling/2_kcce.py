import requests
from bs4 import BeautifulSoup


def title_from_link(link):
    # 링크로 이동 후 제목 가져오는 함수
    response = requests.get(link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 제목 선택
        title_tag = soup.select_one(
            '#container > div.content_wrap > div.content > div.con_wrap > table > tbody > tr:nth-child(1) > th').text.strip()
        return title_tag
    return None


# 웹사이트 URL 설정
url = "https://www.kcce.or.kr/web/board/1485.do"
# 웹페이지 요청
response = requests.get(url)

# 요청 성공 여부 확인
if response.status_code == 200:
    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 뉴스 데이터 선택
    news_table = soup.select_one('#form1 > fieldset > div.list_tbl > table > tbody')

    newses = news_table.select('tr')
    for news in newses[1:]:

        info = news.find_all('td')
        title_tag = info[1].select_one('a')

        if title_tag:
            # link (index 추출 후 수정)
            link_no = title_tag['onclick'].split("'")[1]
            link = "https://www.kcce.or.kr/web/board/1485.do?mode=view&schBcode=&schCon=&schStr=&pageIndex=1&pageUnit=20&idx=" + link_no

            # 제목
            title = title_tag.text.strip()
            if "..." in title:
                title = title_from_link(link)

            # 날짜
            date_str = info[4].text.strip()
            date = date_str.replace('-', '.')

        # 출력
        print(f"제목: {title}")
        print(f"링크: {link}")
        print(f"날짜: {date}")
        print("-" * 100)

else:
    print(f"Failed to fetch the page, status code: {response.status_code}")
