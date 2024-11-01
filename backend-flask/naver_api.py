# -*- coding: utf-8 -*-

import os
import requests, json, urllib.request
from datetime import date, timedelta
from dotenv import load_dotenv

import pandas as pd



# Naver 통합검색어 트랜드 API 사용

# Naver Key 데이터 불러오기
def load_key():
    try:
        load_dotenv('env/data.env')
    except Exception as e:
        print("Error : Naver-API 키 데이터를 불러오지 못햇습니다.")
        print(e)
        exit()

    client_id = str(os.getenv('client_id'))
    client_secret = str(os.getenv('client_secret'))
    return client_id, client_secret


# API 요청
def access_API(param):
    client_id, client_secret = load_key()
    url = "https://openapi.naver.com/v1/datalab/search"

    body = {
        #"startDate": "2024-10-2",
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
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type", "application/json")

    response = urllib.request.urlopen(request, data=body.encode("utf-8"))
    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read()
        result = response_body.decode('utf-8')
        print(result)
        refresh_item(json.loads(response_body))
    else:
        print("Error : API 요청에 실패하였습니다.")

# https://yenpa.tistory.com/15
# https://wooiljeong.github.io/python/naver_datalab_open_api/


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





access_API("a")


