import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz

def get_article_date(article_url):
    response = requests.get(article_url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    tag = soup.select_one('#main > div.viewTitle > dl > dd')

    if tag:
        full_text = tag.get_text(separator=" ", strip=True)
        match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', full_text)
        if match:
            raw_date = match.group(0)
            naive_dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")

            # 타임존 설정
            kst = pytz.timezone('Asia/Seoul')
            aware_dt = kst.localize(naive_dt)

            return aware_dt

    return None

def get_data():
    # 가져올 웹사이트 주소
    url = "https://dhnews.co.kr/news/cate/"
    # 웹페이지 요청
    response = requests.get(url)

    try:
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
                link = "https://dhnews.co.kr" + title_tag.attrs['href']

                date = get_article_date(link)

                # print(f"제목: {title}")
                # print(f"날짜: {date}")
                # print(f"링크: {link}")
                # print("-" * 100)
                dict_data = {"title": title, "link": link, "date": date}
                result.append(dict_data)

            return {"대학저널": result}

        # 웹사이트 요청 실패 시 출력
        else:
            #print(f"Failed to fetch the page, status code: {response.status_code}")
            return {"대학저널": ["Error", response.status_code, "News Server Error"]}
    except Exception as e:
        return {"대학저널": ["Error", response.status_code, e]}
