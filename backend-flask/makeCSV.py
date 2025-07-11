import pandas as pd
import os
import requests
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor
import json
import math


def searchSameLatLon():
    # CSV 파일 읽기
    df = pd.read_csv('./applicantMap/최종_전국고등학교위치데이터.csv', encoding='utf-8-sig')

    # 중복 좌표(위도+경도) 찾기
    duplicates = df[df.duplicated(subset=["위도", "경도"], keep=False)]

    # 위도+경도별로 고교명 그룹화
    grouped = duplicates.groupby(["위도", "경도"])

    # 고교명이 서로 다른 그룹만 필터링
    result = []
    for (lat, lon), group in grouped:
        school_names = group["학교명"].unique()
        if len(school_names) > 1:
            result.append(list(school_names))

    # 결과 출력
    for group in result:
        print(group)


def makeDifferentLatLon():
    # 데이터 불러오기
    df = pd.read_csv("./applicantMap/전국고등학교위치데이터.csv", encoding='utf-8-sig')

    # 중복 좌표 탐색
    coord_counts = df.groupby(["위도", "경도"]).size().reset_index(name='count')
    duplicates = coord_counts[coord_counts['count'] > 1]

    # 오프셋 반지름 (1 ≒ 약 1.1m → 0.00001)
    radius = 0.0005

    for _, row in duplicates.iterrows():
        lat, lon = row["위도"], row["경도"]
        mask = (df["위도"] == lat) & (df["경도"] == lon)
        indices = df[mask].index.tolist()
        n = len(indices)

        for i, idx in enumerate(indices):
            if i == 0:
                continue  # 첫 번째는 그대로 두기
            angle = 2 * math.pi * i / n
            offset_lat = math.sin(angle) * radius
            offset_lon = math.cos(angle) * radius
            df.at[idx, "위도"] += offset_lat
            df.at[idx, "경도"] += offset_lon

    # 저장
    df.to_csv("./applicantMap/최종_전국고등학교위치데이터.csv", index=False, encoding='utf-8-sig')


# 최종 고등학교 위치데이터에 지역 컬럼 생성
def addRegion():
    # 데이터 불러오기
    df = pd.read_csv("./applicantMap/최종_전국고등학교위치데이터.csv", encoding='utf-8-sig')

    for _, row in df.iterrows():
        df['지역명'] = df['소재지지번주소'].str.split(' ').str[0]

    df.to_csv("./applicantMap/최종_전국고등학교위치데이터.csv", index=False, encoding='utf-8-sig')


def getAddressLatLon():
    # 1. 파일 불러오기
    origin_df = pd.read_csv('./applicantMap/가공_2025 고교별 지원자 정보.csv')
    allSchool_df = pd.read_csv('./applicantMap/진짜_최종_전국고등학교위치데이터.csv')

    # 2. 컬럼명 정리
    allSchool_df = allSchool_df.rename(columns={
        '학교명': '고교명',
        '소재지도로명주소': '주소지'
    })

    # 3. 문자열 공백 정리 (병합 오류 방지)
    origin_df['고교명'] = origin_df['고교명'].str.strip()
    allSchool_df['고교명'] = allSchool_df['고교명'].str.strip()
    origin_df['지역명'] = origin_df['지역명'].str.strip()
    allSchool_df['지역명'] = allSchool_df['지역명'].str.strip()

    # 4. 병합 ('고교명'과 '지역명'을 기준으로 병합)
    merged_df = pd.merge(origin_df, allSchool_df[['고교명', '지역명', '주소지', '위도', '경도']],
                         on=['고교명', '지역명'], # 복합키로 병합
                         how='left', suffixes=('', '_school'))

    # 5. school 정보로 덮어쓰기 (일치할 때만 덮어씀)
    merged_df['주소지'] = merged_df['주소지_school'].combine_first(merged_df['주소지'])
    merged_df['위도'] = merged_df['위도_school'].combine_first(merged_df['위도'])
    merged_df['경도'] = merged_df['경도_school'].combine_first(merged_df['경도'])

    # 6. 임시 병합 컬럼 제거
    merged_df.drop(columns=['주소지_school', '위도_school', '경도_school'], inplace=True)

    # 7. 최종 결과 저장
    merged_df.to_csv('./applicantMap/진짜_최종_2025지원자정보.csv', index=False, encoding='utf-8-sig')

    # 8. 병합 실패한 고교명 출력
    failed = merged_df[merged_df['주소지'].isnull()]
    if not failed.empty:
        print("병합 실패한 고교명 목록:")
        print(failed['고교명'].unique())
    else:
        print("모든 고교명 병합 성공!")


# 학교데이터 위도/경도 저장하기
def getLatLon():
    file_path = './applicantMap/전국고등학교데이터.csv'

    df = pd.read_csv(file_path, encoding='cp949')

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

    failed_addresses = []

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
        batch = df['소재지지번주소'][i:i + batch_size]
        batch_results = process_addresses(batch)

        # 실패한 주소 추적
        for address, result in zip(batch, batch_results):
            if result == (None, None):
                failed_addresses.append(address)

        results.extend(batch_results)
        time.sleep(1)  # 요청 간 1초 딜레이

    # 위도, 경도 컬럼 추가
    df['위도'], df['경도'] = zip(*results)

    # 결과 저장 또는 출력
    df.to_csv('./applicantMap/전국고등학교위치데이터.csv', index=False, encoding='utf-8-sig')

    # 캐시 저장
    with open('./applicantMap/cache.json', 'w', encoding='utf-8') as f:
        json.dump(cached, f, ensure_ascii=False, indent=2)

    # 실패한 주소 출력
    if failed_addresses:
        print("다음 주소에서 실패한 결과가 있습니다:")
        for address in failed_addresses:
            print(address)
    else:
        print("모든 주소 처리 완료.")


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
    df = pd.read_csv('./applicantMap/최종_2025지원자정보.csv', encoding='utf-8-sig')

    # 지역명 기준 고교 수 계산 후 각 행에 채우기
    df['고교수'] = df.groupby('지역명')['지역명'].transform('count')

    # 결과 저장
    df.to_csv('./applicantMap/최종_2025지원자정보.csv', index=False, encoding='utf-8-sig')



################################################################################################################
# 지역명으로 그룹화해서 Json 파일 생성
def groupedBySido():
    df = pd.read_csv("./applicantMap/진짜_최종_2025지원자정보.csv")
    grouped = df.groupby("지역명")

    output_dir = './applicantMap/REGION'
    os.makedirs(output_dir, exist_ok=True)

    for region, group in grouped:
        filename = "./applicantMap/REGION/" + region + ".json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(group.to_dict(orient="records"), f, ensure_ascii=False, indent=4)

    print("시도별 JSON 파일 생성 완료")


if __name__ == '__main__':
    # makeDifferentLatLon()
    # searchSameLatLon()
    # getAddressLatLon()
    # getLatLon()
    # encoding()
    # sigunguColumn()
    # schoolNum()
    # addRegion()
    groupedBySido()
