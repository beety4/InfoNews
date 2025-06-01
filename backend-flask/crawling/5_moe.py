import requests
from bs4 import BeautifulSoup
import re


def get_data():
    # 웹사이트 URL 설정
    url = "https://www.moe.go.kr/boardCnts/listRenew.do?boardID=294&m=020402&s=moe"
    # 웹페이지 요청
    response = requests.get(url)

    try:
        # 요청 성공 여부 확인
        if response.status_code == 200:
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            # 뉴스 데이터 선택
            news_table = soup.select_one('#txt > section > div:nth-child(2) > div > table > tbody')

            newses = news_table.select('tr')
            result = []
            for news in newses:
                info = news.find_all('td')
                title_tag = info[1].select_one('a')

                if title_tag:
                    # 제목
                    title = title_tag.text.strip()

                    onclick_value = title_tag['onclick']
                    # 자바스크립트 인자값 추출
                    match = re.search(r"goView\('(\d+)', '(\d+)', '(\d+)', null, '(\w)', '(\d+)', '(\w)', ''\);",
                                      onclick_value)
                    if match:
                        var1, var2, var3, var4, var5, var6 = match.groups()

                    # 링크
                    link = f"https://www.moe.go.kr/boardCnts/viewRenew.do?boardID={var1}&boardSeq={var2}&lev={var3}&searchType=null&statusYN={var4}&page={var5}&s=moe&m=020402&opType={var6}"

                    date_str = info[3].text.strip()
                    date = date_str.replace("-", ".")

                # 출력
                # print(f"제목: {title}")
                # print(f"링크: {link}")
                # print(f"날짜: {date}")
                # print("-" * 100)

                dict_data = {"title": title, "link": link, "date": date}
                result.append(dict_data)

            return {"교육부보도자료": result}
        else:
            #print(f"Failed to fetch the page, status code: {response.status_code}")
            return {"교육부보도자료": ["Error", response.status_code, "News Server Error"]}
    except Exception as e:
        return {"교육부보도자료": ["Error", response.status_code, e]}


