import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz


def get_data():
    url = 'https://www.yna.co.kr/news?site=navi_latest_depth01'
    response = requests.get(url)

    try:
        # 연도 정보 부재로 현재 연도로 대체(수정 필요)
        current_year = datetime.now().year

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # ul.list의 li 요소를 선택
            news_list = soup.select('ul.list01 li')

            result = []
            # 타임존 설정
            kst = pytz.timezone('Asia/Seoul')

            for news in news_list:
                title_tag = news.select_one('strong.tit-wrap')

                # 제목이 존재하는지 확인
                if title_tag:
                    title = title_tag.text.strip()
                else:  # HTML상 비어있는 li 요소 존재
                    continue

                date_text = news.select_one('span.txt-time')
                if date_text:
                    # 10-30 18:00
                    date_text = date_text.text.strip()
                    full_date_str = f"{datetime.now().year}-{date_text}"
                    naive_dt = datetime.strptime(full_date_str, "%Y-%m-%d %H:%M")
                    aware_dt = kst.localize(naive_dt)

                link = news.select_one('div.news-con a').attrs['href']

                # print(f"제목: {title}")
                # print(f"날짜: {aware_dt}")
                # print(f"링크: {link}")
                # print("-" * 100)
                dict_data = {"title": title, "link": link, "date": aware_dt}
                result.append(dict_data)

            return {"연합뉴스": result}
        else:
            #print(f"HTTP 요청 실패: {response.status_code}")
            return {"연합뉴스": ["Error", response.status_code, "News Server Error"]}
    except Exception as e:
        return {"연합뉴스": ["Error", response.status_code, e]}