# -*- coding: utf-8 -*-

import os
import requests, json, urllib.request
from datetime import date, timedelta
from dotenv import load_dotenv
import pandas as pd


# 키워드 5개를 검색할 수 있는 naver api 객체
class NaverAPI:
    def __init__(self):
        self.client_id, self.client_secret = self.load_key()

    @staticmethod
    def load_key(self):
        try:
            load_dotenv('env/data.env')
        except Exception as e:
            print("Error : Naver-API 키 데이터를 불러오지 못햇습니다.")
            print(e)
            return None

        client_id = str(os.getenv('client_id'))
        client_secret = str(os.getenv('client_secret'))
        return client_id, client_secret


    # 네이버 통합 검색어 트랜드 API 요청
    def access_keywork(self, keword_list, startDate, endDate, timeUnit):
        url = "https://openapi.naver.com/v1/datalab/search"
        body = {
            # "startDate": "2024-10-2",
            "startDate": str(date.today() - timedelta(days=2)),
            "endDate": str(date.today()),
            "timeUnit": "date",
            "keywordGroups": [
                {"groupName": "인하공업전문대학", "keywords": ["인하공업전문대학"]},
                {"groupName": "서울대학교", "keywords": ["서울대학교"]},
                {"groupName": "서울대학교", "keywords": ["서울대학교"]},
                {"groupName": "서울대학교", "keywords": ["서울대학교"]},
                {"groupName": "서울대학교", "keywords": ["서울대학교"]}
            ]
        }
        body = json.dumps(body)

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)
        request.add_header("Content-Type", "application/json")

        response = urllib.request.urlopen(request, data=body.encode("utf-8"))
        rescode = response.getcode()

        if rescode == 200:
            response_body = response.read()
            result = response_body.decode('utf-8')
            print(result)
            self.refresh_item(json.loads(response_body))
        else:
            print(f"HTTP 요청 실패 : {rescode}")


    # 네이버 뉴스 키워드 검색 API 요청
    def search_news(self, keyword, display=15, start=1, sort="date"):
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        params = {
            "query": keyword,
            "display": display,
            "start": start,
            "sort": sort
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"HTTP 요청 실패 : {response.status_code}")
            return None


    # 데이터 가공 처리
    def refresh_item(data):
        rows = []
        title = data["results"][0]["title"]
        for entry in data["results"][0]["data"]:
            period = entry["period"]
            ratio = entry["ratio"]
            for university in data["results"][0]["keywords"]:
                rows.append({"title": university, "period": period, "ratio": ratio})

        # DataFrame 생성 및 인덱스 설정
        df = pd.DataFrame(rows, columns=["title", "period", "ratio"])
        df.set_index("title", inplace=True)

        print(df)




# 참고 블로그
# https://yenpa.tistory.com/15
# https://wooiljeong.github.io/python/naver_datalab_open_api/

