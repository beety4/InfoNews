import requests
import re
from bs4 import BeautifulSoup

url = 'https://www.usline.kr/news/articleList.html?view_type=sm'

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    news_list = soup.select('section#section-list div.view-cont')

    for news in news_list:
        title_tag = news.select_one('h4 a')
        title = title_tag.text.strip()

        # <em>사회</em><em>박병수 편집국장</em><em>2024.10.30 04:16</em>
        date = None
        for em in news.find_all('em'):
            match = re.match(r'(\d{4}\.\d{2}\.\d{2}) \d{2}:\d{2}', em.text)
            if match:
                date = match.group(1)
                break

        link = "https://www.usline.kr" + title_tag.get('href')

        print(f"제목: {title}")
        print(f"날짜: {date}")
        print(f"링크: {link}")
        print("-" * 100)

else:
    print(f"Failed to fetch the page, status code: {response.status_code}")