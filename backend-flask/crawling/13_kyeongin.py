import requests
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime

def get_data():
    temp_profile = tempfile.mkdtemp()
    options = Options()
    options.add_argument('headless')
    options.add_argument(f'--user-data-dir={temp_profile}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    result = []
    try:
        driver.get('https://www.kyeongin.com/society')
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#container > div > section > div > ul"))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        li_elements = soup.select("#container > div > section > div > ul > li")

        for li in li_elements:
            try:
                title_tag = li.select_one('h2 > a')
                title = title_tag.text.strip() if title_tag else "No Title"
                raw_link = title_tag.get('href').strip() if title_tag and title_tag.get('href') else "No Link"
                if raw_link != "No Link" and not raw_link.startswith('https:'):
                    link = "https:" + raw_link
                else:
                    link = raw_link

                date_elem = li.select_one('div.byline span.date')
                raw_date = date_elem.text.strip() if date_elem else ""

                if not raw_date:
                    date = datetime.today().strftime("%Y.%m.%d")
                else:
                    date = raw_date.replace('-', '.')

                result.append({
                    "title": title,
                    "link": link,
                    "date": date
                })
                # print(f"제목: {title}")
                # print(f"날짜: {date}")
                # print(f"링크: {link}")
                # print("-" * 100)
            except Exception as e:
                print(f"개별 아이템 처리 중 오류 발생: {e}")
                continue

        return {"경인일보": result}

    except Exception as e:
        print(f"전체 크롤링 중 오류 발생: {e}")
        return {"경인일보": []}
    finally:
        driver.quit()