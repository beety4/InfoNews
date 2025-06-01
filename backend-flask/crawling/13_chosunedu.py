import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import re


def get_data_before():
    # 웹드라이버 설정 (크롬 드라이버)
    options = Options()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    driver.get('https://edu.chosun.com/svc/edu_list.html?catid=14')
    driver.implicitly_wait(3)

    # 페이지 로드 후 HTML 가져오기
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    news_list = soup.select('#contentList02 article.ui-item')

    result = []
    for news in news_list:
        title_tag = news.select_one('div.ui-subject a')
        title = title_tag.text.strip()

        # 2024.10.30(수)
        date_text = news.select_one('span.date').text.strip()
        date = date_text.split(' ')[0]

        link = "https:" + title_tag.attrs['href'].strip()

        dict_data = {"title": title, "link": link, "date": date}
        result.append(dict_data)

    driver.quit()
    return result



def get_data():
    # AJAX 요청을 보내는 URL 및 헤더 설정
    url = 'https://edu.chosun.com/svc/app/edu_list.php'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # 요청 파라미터 설정
    params = {
        'catid': '14',
        'pn': 1,
        'rows': 10
    }

    try:
        # AJAX 요청 보내기
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        result = []
        # 타임존 설정
        kst = pytz.timezone('Asia/Seoul')
        # 데이터 출력
        for content in data["CONTENT"]:
            link = "https:" + content["ART_HREF"]

            article_resp = requests.get(link, headers=headers)
            if article_resp.status_code == 200:
                article_soup = BeautifulSoup(article_resp.text, 'html.parser')
                date_div = article_soup.select_one(
                    '#detailBlock2 > div > div.innerwrap > div.side-01.article > div.article_etc > div')

                if date_div:
                    raw_text = date_div.text.strip()
                    match = re.search(r'(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2})', raw_text)
                    if match:
                        raw_date = match.group(1)
                        naive_dt = datetime.strptime(raw_date, "%Y.%m.%d %H:%M")
                        aware_dt = kst.localize(naive_dt)

                    else:
                        date = content["DATE"][:10]
                else:
                    date = content["DATE"][:10]
            else:
                date = content["DATE"][:10]

            dict_data = {"title": content["TITLE"], "link": link, "date": aware_dt}
            result.append(dict_data)

        if len(result) == 0:
            return {"조선에듀": ["Error", response.status_code, "News Server Error"]}

        return {"조선에듀": result}
    except Exception as e:
        return {"조선에듀": ["Error", response.status_code, e]}