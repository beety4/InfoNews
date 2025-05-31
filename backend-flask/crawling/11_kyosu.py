import requests
import re
from bs4 import BeautifulSoup

def get_data():
    #url = 'https://www.kyosu.net/news/articleList.html?view_type=sm'

    pagenum = 0
    result = []
    while len(result) < 10:
        pagenum += 1
        url = f'https://www.kyosu.net/news/articleList.html?page={pagenum}&total=111930&sc_section_code=&sc_sub_section_code=&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&sc_word2=&sc_andor=&sc_order_by=E&view_type=sm&sc_multi_code='
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            news_list = soup.select('div.list-block')

            for news in news_list:
                title = news.select_one('div.list-titles a strong').text.strip()

                # 대학핫뉴스-일반대 | 배지우 | 2024-10-30 15:46
                date_text = news.select_one('div.list-dated').text

                # 뉴스 카테고리 검출
                category = date_text.split("|")[0].strip()
                if category == "새로나온 책":
                    continue

                # 2024-10-30
                match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
                if match is not None:
                    # 2024.10.30
                    date = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"

                link = "https://www.kyosu.net" + news.select_one('div.list-titles a').attrs['href']

                #print(f"제목: {title}")
                #print(f"날짜: {date}")
                #print(f"링크: {link}")
                #print("-" * 100)
                dict_data = {"title": title, "link": link, "date": date}
                result.append(dict_data)
        else:
            print(f"Failed to fetch the page, status code: {response.status_code}")
            return {"Error": response.status_code}

    return {"교수신문": result}

