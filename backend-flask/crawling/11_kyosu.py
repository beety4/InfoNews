import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def get_data():
    #url = 'https://www.kyosu.net/news/articleList.html?view_type=sm'

    try:
        pagenum = 0
        result = []
        while len(result) < 10:
            pagenum += 1
            url = f'https://www.kyosu.net/news/articleList.html?page={pagenum}&total=111930&sc_section_code=&sc_sub_section_code=&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&sc_word2=&sc_andor=&sc_order_by=E&view_type=sm&sc_multi_code='
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                news_list = soup.select('div.list-block')
                # 타임존 설정
                kst = pytz.timezone('Asia/Seoul')

                for news in news_list:
                    title = news.select_one('div.list-titles a strong').text.strip()

                    # 대학핫뉴스-일반대 | 배지우 | 2024-10-30 15:46
                    date_text = news.select_one('div.list-dated').text

                    # 뉴스 카테고리 검출
                    category = date_text.split("|")[0].strip()
                    if category == "새로나온 책":
                        continue

                    # 2024-10-30 13:00
                    match = re.search(r'(\d{4})-(\d{2})-(\d{2}) \d{2}:\d{2}', date_text)
                    if match is not None:
                        raw_date = match.group(0)
                        naive_dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M")
                        aware_dt = kst.localize(naive_dt)

                    link = "https://www.kyosu.net" + news.select_one('div.list-titles a').attrs['href']

                    # print(f"제목: {title}")
                    # print(f"날짜: {aware_dt}")
                    # print(f"링크: {link}")
                    # print("-" * 100)
                    dict_data = {"title": title, "link": link, "date": aware_dt}
                    result.append(dict_data)
            else:
                #print(f"Failed to fetch the page, status code: {response.status_code}")
                return {"교수신문": ["Error", response.status_code, "News Server Error"]}

        return {"교수신문": result}
    except Exception as e:
        return {"교수신문": ["Error", response.status_code, e]}

