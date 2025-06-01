import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz

def get_article_date(article_url, headers):
    try:
        res = requests.get(article_url, headers=headers)
        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, 'html.parser')
        date_tag = soup.select_one('#container > div > article > header > div.article-date > div > span.date-publish')
        if date_tag:
            text = date_tag.text.strip()
            match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', text)
            if match:
                raw_date = match.group(1)
                naive_dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M")
                kst = pytz.timezone("Asia/Seoul")
                aware_dt = kst.localize(naive_dt)

                return aware_dt
        print(f"날짜 태그를 찾지 못했습니다 for {article_url}")
    except Exception as e:
        print(f"[{article_url}] 날짜 추출 오류: {e}")
    return None

def get_data():
    # URL 및 헤더 설정
    base_html_url = 'https://www.kyeongin.com/society'
    html_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        'DNT': '1',  # Do Not Track
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    result = []
    try:
        response = requests.get(base_html_url, headers=html_headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        li_elements = soup.select("#container > div > section > div > ul > li")

        for i, li in enumerate(li_elements):
            title_tag = li.select_one('h2 > a')
            title = title_tag.text.strip() if title_tag else "제목 없음"

            raw_link = title_tag.get('href').strip() if title_tag and title_tag.get('href') else "링크 없음"
            full_link = "https:" + raw_link

            date = get_article_date(full_link, html_headers)

            result.append({
                "title": title,
                "link": full_link,
                "date": date
            })

            # print(f"제목: {title}")
            # print(f"날짜: {date}")
            # print(f"링크: {full_link}")
            # print("-" * 100)

        if len(result) == 0:
            return {"조선에듀": ["Error", response.status_code, "News Server Error"]}

        return {"경인일보": result}

    except Exception as e:
        return {"경인일보": ["Error", response.status_code, e]}