import requests
from bs4 import BeautifulSoup

def get_data():
    url = 'https://www.incheonilbo.com/news/articleList.html?sc_sub_section_code=S2N14&view_type=sm'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 원하는 ul > li들 선택
        news_items = soup.select('#section-list ul > li')
        result = []
        print(news_items)
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
            full_date = byline_ems[2].get_text(strip=True)
            # 날짜만 추출
            date = full_date.split()[0]

            result.append({
                "title": title,
                "link": link,
                "date": date
            })
            # print(f"제목: {title}")
            # print(f"날짜: {date}")
            # print(f"링크: {link}")
            # print("-" * 100)
        return {"인천일보": result}

    else:
        print(f"HTTP 요청 실패: {response.status_code}")
        return {"Error": response.status_code}
