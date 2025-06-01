import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def get_data():
    url = 'https://www.incheonilbo.com/news/articleList.html?view_type=sm'
    response = requests.get(url)

    try:
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            news_items = soup.select('#section-list ul > li')
            result = []
            # 타임존 설정
            kst = pytz.timezone('Asia/Seoul')

            for item in news_items:
                # 제목 및 링크
                title_tag = item.select_one('h2.titles > a')
                if not title_tag:
                    continue
                base_url = "https://www.incheonilbo.com"
                title = title_tag.get_text(strip=True)
                link = base_url + title_tag.get('href', '')

                # 날짜
                byline_ems = item.select('span.byline > em')
                raw_date = byline_ems[2].get_text(strip=True)
                naive_dt = datetime.strptime(raw_date, "%Y.%m.%d %H:%M")
                aware_dt = kst.localize(naive_dt)

                result.append({
                    "title": title,
                    "link": link,
                    "date": aware_dt
                })
                # print(f"제목: {title}")
                # print(f"날짜: {aware_dt}")
                # print(f"링크: {link}")
                # print("-" * 100)
            return {"인천일보": result}

        else:
            #print(f"HTTP 요청 실패: {response.status_code}")
            return {"인천일보": ["Error", response.status_code, "News Server Error"]}
    except Exception as e:
        return {"인천일보": ["Error", response.status_code, e]}