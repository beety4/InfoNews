import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def get_data():
    url = 'https://www.usline.kr/news/articleList.html?view_type=sm'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    try:
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            news_list = soup.select('#section-list > ul > li')

            result = []
            # 타임존 설정
            kst = pytz.timezone('Asia/Seoul')
            for news in news_list:
                title_tag = news.select_one('h2.altlist-subject > a')
                title = title_tag.text.strip()

                link = title_tag.get('href')

                date_info_divs = news.select('div.altlist-info > div.altlist-info-item')
                raw_date = date_info_divs[2].text.strip()
                full_date_str = f"{datetime.now(kst).year}-{raw_date}"  # 년도 추가
                naive_dt = datetime.strptime(full_date_str, "%Y-%m-%d %H:%M")
                aware_dt = kst.localize(naive_dt)

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