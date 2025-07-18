import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def get_data():
    # 웹사이트 URL 설정
    url = "https://www.veritas-a.com/news/articleList.html?sc_section_code=&view_type=sm"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    # 웹페이지 요청
    response = requests.get(url, headers=headers)

    try:
        # 요청 성공 여부 확인
        if response.status_code == 200:
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')

            # 뉴스 데이터 선택
            news_list = soup.select('#section-list > ul > li')

            result = []
            # 타임존 설정
            kst = pytz.timezone('Asia/Seoul')

            for news in news_list:
                # 제목과 링크
                title_tag = news.select_one('div h2 a')
                if title_tag:
                    title = title_tag.text.strip()
                    link_str = title_tag['href']
                    link = "https://www.veritas-a.com" + link_str

                # 날짜
                write_info = news.select_one('.byline')
                if write_info:
                    date_em = write_info.select('em')[2]
                    raw_date_str = date_em.text.strip()
                    naive_dt = datetime.strptime(raw_date_str, "%Y.%m.%d %H:%M")
                    aware_dt = kst.localize(naive_dt)

                # 출력
                # print(f"제목: {title}")
                # print(f"링크: {link}")
                # print(f"날짜: {aware_dt}")
                # print("-" * 100)
                dict_data = {"title": title, "link": link, "date": aware_dt}
                result.append(dict_data)

            return {"베리타스알파": result}
        else:
            #print(f"Failed to fetch the page, status code: {response.status_code}")
            return {"베리타스알파": ["Error", response.status_code, "News Server Error"]}
    except Exception as e:
        return {"베리타스알파": ["Error", response.status_code, e]}