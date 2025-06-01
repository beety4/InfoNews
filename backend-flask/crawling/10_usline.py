import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def get_data():
    url = 'https://www.usline.kr/news/articleList.html?view_type=sm'
    response = requests.get(url)

    try:
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            news_list = soup.select('section#section-list div.view-cont')

            result = []
            # 타임존 설정
            kst = pytz.timezone('Asia/Seoul')
            for news in news_list:
                title_tag = news.select_one('h4 a')
                title = title_tag.text.strip()

                # <em>사회</em><em>박병수 편집국장</em><em>2024.10.30 04:16</em>
                date = None
                for em in news.find_all('em'):
                    match = re.match(r'(\d{4}\.\d{2}\.\d{2}) \d{2}:\d{2}', em.text)
                    if match:
                        raw_date = match.group(0)
                        naive_dt = datetime.strptime(raw_date, "%Y.%m.%d %H:%M")
                        aware_dt = kst.localize(naive_dt)
                        # date = aware_dt.strftime("%Y-%m-%d %H:%M:%S%z")
                        # date = date[:-2] + ':' + date[-2:]
                        break

                link = "https://www.usline.kr" + title_tag.get('href')

                # print(f"제목: {title}")
                # print(f"날짜: {aware_dt}")
                # print(f"링크: {link}")
                # print("-" * 100)
                dict_data = {"title": title, "link": link, "date": aware_dt}
                result.append(dict_data)

            return {"유스라인(Usline)": result}
        else:
            #print(f"Failed to fetch the page, status code: {response.status_code}")
            return {"유스라인(Usline)": ["Error", response.status_code, "News Server Error"]}
    except Exception as e:
        return {"유스라인(Usline)": ["Error", response.status_code, e]}

