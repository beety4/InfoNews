import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def get_data():
    url = 'http://www.unipress.co.kr/news/articleList.html?sc_section_code=S1N1&view_type=sm'
    response = requests.get(url)

    try:
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            news_list = soup.select('div.list-block')

            result = []
            # 타임존 설정
            kst = pytz.timezone('Asia/Seoul')
            for news in news_list:
                title = news.select_one('div.list-titles a strong').text.strip()

                # 대학핫뉴스-일반대 | 배지우 | 2024-10-30 15:46
                date_text = news.select_one('div.list-dated').text
                # 2024-10-30 13:00
                match = re.search(r'(\d{4})-(\d{2})-(\d{2}) \d{2}:\d{2}', date_text)
                if match is not None:
                    raw_date = match.group(0)
                    naive_dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M")
                    aware_dt = kst.localize(naive_dt)

                link = "http://www.unipress.co.kr" + news.select_one('div.list-titles a').attrs['href']

                # print(f"제목: {title}")
                # print(f"날짜: {aware_dt}")
                # print(f"링크: {link}")
                # print("-" * 100)
                dict_data = {"title": title, "link": link, "date": aware_dt}
                result.append(dict_data)

            return {"대학지성IN&OUT": result}
        else:
            # print(f"Failed to fetch the page, status code: {response.status_code}")
            return {"대학지성IN&OUT": ["Error", response.status_code, "News Server Error"]}
    except Exception as e:
        return {"대학지성IN&OUT": ["Error", response.status_code, e]}