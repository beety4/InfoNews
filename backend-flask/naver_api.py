# -*- coding: utf-8 -*-

import os
import requests, json, urllib.request
from dotenv import load_dotenv


# 키워드 5개를 검색할 수 있는 naver api 객체
class NaverAPI:
    def __init__(self):
        self.client_id, self.client_secret = self.load_key(self)

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
    def access_keyword(self, keyword_list, startDate, endDate, timeUnit):
        url = "https://openapi.naver.com/v1/datalab/search"

        keywordGroups = []
        for keyword in keyword_list:
            group = {"groupName": keyword, "keywords": [keyword]}
            keywordGroups.append(group)

        body = {
            "startDate": startDate,
            "endDate": endDate,
            "timeUnit": timeUnit,
            "keywordGroups": keywordGroups
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
            return json.loads(response_body)
            #result = response_body.decode('utf-8')
            #print(result)
            #self.refresh_item(json.loads(response_body))
        else:
            print(f"HTTP 요청 실패 : {rescode}")
            return None


    # 네이버 뉴스 키워드 검색 API 요청
    def search_news(self, keyword, display=100, start=1, sort="date"):
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
            #print(f"HTTP 요청 실패 : {response.status_code}")
            return None


# 참고 블로그
# https://yenpa.tistory.com/15
# https://wooiljeong.github.io/python/naver_datalab_open_api/
