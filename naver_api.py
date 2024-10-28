# -*- coding: utf-8 -*-

import os
import sys
import urllib.request
from dotenv import load_dotenv


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
    url = "https://openapi.naver.com/v1/datalab/search";
    body = "{\"startDate\":\"2017-10-01\",\"endDate\":\"2024-04-30\",\"timeUnit\":\"month\",\"keywordGroups\":[{\"groupName\":\"한글\",\"keywords\":[\"한글\",\"korean\"]},{\"groupName\":\"영어\",\"keywords\":[\"영어\",\"english\"]}],\"device\":\"pc\",\"ages\":[\"1\",\"2\"],\"gender\":\"f\"}";

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type", "application/json")
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))
    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()
        print(response_body.decode('utf-8'))

    else:
        print("Error Code:" + rescode)


# 데이터 가공 처리
def refresh_item(data):
    pass



