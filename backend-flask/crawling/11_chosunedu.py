from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def getdata():
    # 웹드라이버 설정 (크롬 드라이버)
    options = Options()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    driver.get('https://edu.chosun.com/svc/edu_list.html?catid=14')
    driver.implicitly_wait(3)

    # 페이지 로드 후 HTML 가져오기
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    news_list = soup.select('#contentList02 article.ui-item')

    result = []
    for news in news_list:
        title_tag = news.select_one('div.ui-subject a')
        title = title_tag.text.strip()

        # 2024.10.30(수)
        date_text = news.select_one('span.date').text.strip()
        date = date_text.split(' ')[0]

        link = "https:" + title_tag.attrs['href'].strip()

        #print(f"제목: {title}")
        #print(f"날짜: {date}")
        #print(f"링크: {link}")
        #print("-" * 100)
        dict_data = {"title": title, "link": link, "date": date}
        result.append(dict_data)

    driver.quit()
    return result


getdata()