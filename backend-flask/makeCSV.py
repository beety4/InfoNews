import pandas as pd
import os
import requests
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor
import json


def main():
    file_path = './applicantMap/2025 고교별 지원자 정보.csv'

    df = pd.read_csv(file_path)

    # .env 파일 로드
    load_dotenv(dotenv_path='./env/data.env')

    # API 키 읽기
    kakao_api_key = os.getenv("KAKAO_API_KEY")

    # API 키 확인
    print("API Key:", kakao_api_key)  # 확인용 출력

    # 캐시 파일 로드
    try:
        with open('./applicantMap/cache.json', 'r', encoding='utf-8') as f:
            cached = json.load(f)
    except FileNotFoundError:
        cached = {}

    def kakao_geocode(address, rest_api_key=kakao_api_key):
        # 프로세싱 확인
        print(f"요청 중: {address}")

        # 캐시 확인
        if address in cached:
            return cached[address]

        url = "https://dapi.kakao.com/v2/local/search/address.json"
        headers = {"Authorization": f"KakaoAK {rest_api_key}"}
        params = {"query": address}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                documents = response.json().get('documents')
                if documents:
                    # 위도, 경도 반환 및 캐시 저장
                    lat, lon = documents[0]['y'], documents[0]['x']
                    cached[address] = (lat, lon)
                    return lat, lon
            # 실패 시 None 반환
            return None, None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e} for address: {address}")
            return None, None

    # 병렬 처리를 위한 함수
    def process_addresses(addresses, rest_api_key=kakao_api_key):
        with ThreadPoolExecutor(max_workers=5) as executor:
            return list(executor.map(lambda addr: kakao_geocode(addr, rest_api_key), addresses))

    # 요청 간 딜레이 추가 (API 제한 고려)
    batch_size = 30
    results = []

    for i in range(0, len(df), batch_size):
        batch = df['주소지'][i:i + batch_size]
        batch_results = process_addresses(batch)
        results.extend(batch_results)
        time.sleep(1)  # 요청 간 1초 딜레이

    # 위도, 경도 컬럼 추가
    df['위도'], df['경도'] = zip(*results)

    # 결과 저장 또는 출력
    df.to_csv('./applicantMap/가공_2025 고교별 지원자 정보.csv', index=False, encoding='utf-8-sig')

    # 캐시 저장
    with open('./applicantMap/cache.json', 'w', encoding='utf-8') as f:
        json.dump(cached, f, ensure_ascii=False, indent=2)


def encoding():
    # 기존 utf-8로 저장된 CSV 불러오기
    df = pd.read_csv('./applicantMap/가공_2025 고교별 지원자 정보.csv', encoding='utf-8')

    # utf-8-sig로 다시 저장 (엑셀 한글 깨짐 방지)
    df.to_csv('./applicantMap/가공_2025 고교별 지원자 정보.csv', index=False, encoding='utf-8-sig')


def sigunguColumn():
    df = pd.read_csv('./applicantMap/가공_2025 고교별 지원자 정보.csv', encoding='utf-8-sig')

    # 주소지에서 시군구명 추출하여 '시군구명' 컬럼 생성
    def extract_sigunggu(address):
        if isinstance(address, str):
            parts = address.split()

            # 세종시 예외처리
            if parts[0] == '세종특별자치시':
                return '세종특별자치시'

            if len(parts) >= 3:  # 최소 3개 이상의 요소가 있는 경우
                return parts[1]
            else:
                return None  # 시군구명이 없는 경우 None 반환
        return None

    # 주소지 컬럼을 기준으로 시군구명 추출
    df['시군구명'] = df['주소지'].apply(extract_sigunggu)

    # CSV 파일 저장
    df.to_csv('./applicantMap/가공_2025 고교별 지원자 정보.csv', index=False, encoding='utf-8-sig')
    print("저장")


def schoolNum():
    # CSV 불러오기
    df = pd.read_csv('./applicantMap/가공_2025 고교별 지원자 정보.csv', encoding='utf-8-sig')

    # 지역명 기준 고교 수 계산 후 각 행에 채우기
    df['고교수'] = df.groupby('지역명')['지역명'].transform('count')

    # 결과 저장
    df.to_csv('./applicantMap/가공_2025 고교별 지원자 정보.csv', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    # main()
    # encoding()
    # sigunguColumn()
    schoolNum()
