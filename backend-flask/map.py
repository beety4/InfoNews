import pandas as pd
import numpy as np
import os
import requests
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor
import geopandas as gpd
import json
import folium
from IPython.display import display


def makeCSV():
    file_path = './applicantMap/고교별 지원자 정보.csv'

    df = pd.read_csv(file_path)

    # .env 파일 로드
    load_dotenv(dotenv_path='./env/data.env')

    # API 키 읽기
    kakao_api_key = os.getenv("KAKAO_API_KEY")

    # API 키 확인
    # print("API Key:", kakao_api_key)  # 확인용 출력

    # 캐시 딕셔너리 초기화
    cache = {}

    def kakao_geocode(address, rest_api_key=kakao_api_key):
        # 캐시 확인
        if address in cache:
            return cache[address]

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
                    cache[address] = (lat, lon)
                    return lat, lon
            # 실패 시 None 반환
            return None, None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e} for address: {address}")
            return None, None

    # 병렬 처리를 위한 함수
    def process_addresses(addresses, rest_api_key=kakao_api_key):
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda addr: kakao_geocode(addr, rest_api_key), addresses))
        return results

    # 요청 간 딜레이 추가 (API 제한 고려)
    batch_size = 30
    results = []
    for i in range(0, len(df), batch_size):
        batch = df['주소지'][i:i + batch_size]
        batch_results = process_addresses(batch)
        results.extend(batch_results)
        time.sleep(1)  # 요청 간 1초 딜레이

    # 결과를 DataFrame에 추가
    df['위도'], df['경도'] = zip(*results)

    # 결과 출력
    # print(df.head())

    # 캐시 저장
    with open('./applicantMap/cache.json', 'w') as f:
        import json

        json.dump(cache, f)

    # 지역명이 0인 줄의 개수 확인
    zero_count = df[df['지역명'] == 0].shape[0]
    # 지역명이 null인 줄의 개수 확인
    null_count = df['지역명'].isnull().sum()

    # 결과 출력
    print(f"지역명이 0인 줄의 개수[]: {zero_count} -> {df[df['지역명'] == '0']['고교명'].drop_duplicates()}")
    # 지역명 컬럼에서 NaN 값 확인
    print(f"지역명이 NaN인 줄의 개수: {null_count} -> {df[df['지역명'].isna()]['고교명'].drop_duplicates()}")
    print()

    # 지역명이 NaN/0인 값을 '기타'로 대체
    df['지역명'] = df['지역명'].fillna('기타')
    df['지역명'] = df['지역명'].replace('0', '기타')

    # 지역별 학교 수 구하기
    지역별_학교_수 = df.groupby('지역명').size()

    # 결과 출력
    print(지역별_학교_수)
    print()

    df['고교수'] = df.groupby('지역명')['지역명'].transform('count')
    # print(df.head(10))

    # 위도와 경도가 None인 행을 제외하여 원본 데이터프레임 수정
    df = df.dropna(subset=['위도', '경도'])

    # CSV 파일 저장 (한글 깨짐 방지)
    df.to_csv('./applicantMap/가공_고교별_지원자_정보.csv', encoding='utf-8-sig', index=False)


def sido():
    # API 요청 지연으로 첫 실행 후 가공 csv로 저장해 로드해서 사용
    df = pd.read_csv('./applicantMap/가공_고교별_지원자_정보.csv')

    # Shapefile 읽기
    shapefile_path = "./applicantMap/ctprvn.shp"
    gdf = gpd.read_file(shapefile_path, encoding='cp949')

    # 좌표계 설정 (EPSG:5179)
    gdf = gdf.set_crs('EPSG:5179', allow_override=True)

    # 좌표계 변환 (EPSG:4326)
    gdf = gdf.to_crs('EPSG:4326')

    # GeoJSON 저장 경로
    geojson_path = "./applicantMap/SIDO.json"

    # GeoJSON 저장
    gdf.to_file(geojson_path, driver="GeoJSON", encoding="utf-8")
    print("GeoJSON 파일이 생성되었습니다.")

    geojson_path = "./applicantMap/SIDO.json"

    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    for feature in geojson_data['features']:
        if feature['properties']['CTP_ENG_NM'] == 'Seoul':
            feature['properties']['CTP_KOR_NM'] = '서울특별시'
        if feature['properties']['CTP_ENG_NM'] == 'Busan':
            feature['properties']['CTP_KOR_NM'] = '부산광역시'
        if feature['properties']['CTP_ENG_NM'] == 'Daegu':
            feature['properties']['CTP_KOR_NM'] = '대구광역시'
        if feature['properties']['CTP_ENG_NM'] == 'Incheon':
            feature['properties']['CTP_KOR_NM'] = '인천광역시'
        if feature['properties']['CTP_ENG_NM'] == 'Gwangju':
            feature['properties']['CTP_KOR_NM'] = '광주광역시'
        if feature['properties']['CTP_ENG_NM'] == 'Daejeon':
            feature['properties']['CTP_KOR_NM'] = '대전광역시'
        if feature['properties']['CTP_ENG_NM'] == 'Ulsan':
            feature['properties']['CTP_KOR_NM'] = '울산광역시'
        if feature['properties']['CTP_ENG_NM'] == 'Sejong-si':
            feature['properties']['CTP_KOR_NM'] = '세종특별자치시'
        if feature['properties']['CTP_ENG_NM'] == 'Gyeonggi-do':
            feature['properties']['CTP_KOR_NM'] = '경기도'
        if feature['properties']['CTP_ENG_NM'] == 'Gangwon-do':
            feature['properties']['CTP_KOR_NM'] = '강원특별자치도'
        if feature['properties']['CTP_ENG_NM'] == 'Chungcheongbuk-do':
            feature['properties']['CTP_KOR_NM'] = '충청북도'
        if feature['properties']['CTP_ENG_NM'] == 'Chungcheongnam-do':
            feature['properties']['CTP_KOR_NM'] = '충청남도'
        if feature['properties']['CTP_ENG_NM'] == 'Jeollabuk-do':
            feature['properties']['CTP_KOR_NM'] = '전북특별자치도'
        if feature['properties']['CTP_ENG_NM'] == 'Jellanam-do':
            feature['properties']['CTP_KOR_NM'] = '전라남도'
        if feature['properties']['CTP_ENG_NM'] == 'Gyeongsangbuk-do':
            feature['properties']['CTP_KOR_NM'] = '경상북도'
        if feature['properties']['CTP_ENG_NM'] == 'Gyeongsangnam-do':
            feature['properties']['CTP_KOR_NM'] = '경상남도'
        if feature['properties']['CTP_ENG_NM'] == 'Jeju-do':
            feature['properties']['CTP_KOR_NM'] = '제주특별자치도'
        print(feature['properties']['CTP_KOR_NM'])

    # 수정된 내용을 저장
    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=4)

    print("GeoJSON 파일이 수정되어 저장되었습니다.")


def sidoMap():
    df = pd.read_csv('./applicantMap/가공_고교별_지원자_정보.csv')

    geojson_path = "./applicantMap/SIDO.json"

    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # 지도 생성 (대한민국 중심으로 설정)
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)

    # 대한민국의 범위로 fit_bounds 설정 (Optional)
    south_lat = 33.0  # 최남단 위도
    north_lat = 38.6  # 최북단 위도
    west_lon = 124.0  # 최서단 경도
    east_lon = 132.0  # 최동단 경도

    m.fit_bounds([[south_lat, west_lon], [north_lat, east_lon]])
    m.options['maxBounds'] = [[south_lat, west_lon], [north_lat, east_lon]]
    m.options['minZoom'] = 7  # 최소 줌 레벨
    m.options['maxZoom'] = 10  # 최대 줌 레벨

    # 지역별 고교 수 집계
    지역별_고교수 = df.groupby('지역명').size().reset_index(name='고교수')

    print(df.groupby('지역명').size().reset_index(name='고교수'))

    # 지역별 고교 수를 GeoJSON 데이터에 추가
    # GeoJSON의 각 지역 정보에 '고교수'를 추가
    for feature in geojson_data['features']:
        지역명 = feature['properties']['CTP_KOR_NM']  # GeoJSON에서 지역명에 해당하는 필드
        고교수 = 지역별_고교수[지역별_고교수['지역명'] == 지역명]['고교수'].values
        if len(고교수) > 0:
            feature['properties']['고교수'] = int(고교수[0])  # 해당 지역에 고교 수 추가

    # 고교 수의 최소/최대 값 구하기 (범위 설정)
    min_schools = 지역별_고교수['고교수'].min()
    max_schools = 지역별_고교수['고교수'].max()

    print(min_schools, max_schools)

    # 범위 설정 (색상 구간을 직접 설정)
    thresholds = [0, 150, 250, 400, 600, 1000, 2000, 3500, 4000]
    # thresholds = [54, 65, 127, 133, 142, 178, 183, 186, 200, 216, 243, 309, 325, 493, 1810, 3335, 3797]

    # choropleth 지도 추가 (지역별 고교 수에 따라 색상 지정)
    folium.Choropleth(
        geo_data=geojson_data,
        name="choropleth",
        data=지역별_고교수,
        columns=['지역명', '고교수'],  # 지역명과 고교 수를 매핑
        key_on="feature.properties.CTP_KOR_NM",  # GeoJSON의 지역명 필드와 매칭
        fill_color="YlGnBu",  # 색상 팔레트 설정 (Yellow-Green-Blue)
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="고교수",
        threshold_scale=thresholds  # 색상 구간 설정
    ).add_to(m)

    folium.GeoJson(
        geojson_data,
        name="boundary",
        style_function=lambda x: {"color": "black", "weight": 0.5, "fillOpacity": 0},
        tooltip=folium.GeoJsonTooltip(
            fields=["CTP_KOR_NM", "고교수"],  # 표시할 필드
            aliases=["지역명", "고교수"],  # 필드명에 대한 별칭
            localize=True,
            style="font-size: 16px; font-weight: bold;",
        ),
        # on_click 이벤트 추가
        highlight_function=lambda x: {"weight": 3, "color": "blue"},
        on_click=onClick()
    ).add_to(m)

    # 지도 저장
    m.save('./applicantMap/map.html')
    print("지도가 생성되어 map.html로 저장되었습니다.")


def sigungu():
    # Shapefile 읽기
    shapefile_path = "./applicantMap/sig.shp"
    gdf = gpd.read_file(shapefile_path, encoding='cp949')

    # 좌표계 설정 (EPSG:5179)
    gdf = gdf.set_crs('EPSG:5179', allow_override=True)

    # 좌표계 변환 (EPSG:4326)
    gdf = gdf.to_crs('EPSG:4326')

    # GeoJSON 저장 경로
    geojson_path = "./applicantMap/SIGUNGU.json"

    # GeoJSON 저장
    gdf.to_file(geojson_path, driver="GeoJSON", encoding="utf-8")
    print("GeoJSON 파일이 생성되었습니다.")


def sigunguMap():
    geojson_path = "./applicantMap/SIGUNGU.json"

    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # 지도 생성 (대한민국 중심으로 설정)
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)

    folium.GeoJson(
        geojson_data,
        name="boundary",
        style_function=lambda x: {"color": "black", "weight": 0.5, "fillOpacity": 0},
        tooltip=folium.GeoJsonTooltip(
            fields=["SIG_KOR_NM"],  # 표시할 필드
            aliases=["지역명"],  # 필드명에 대한 별칭
            localize=True,
            style="font-size: 16px; font-weight: bold;",
        ),
    ).add_to(m)

    # 지도 저장
    m.save('./applicantMap/map.html')
    print("지도가 생성되어 map.html로 저장되었습니다.")


def onClick():
    pass


def main():
    # SIDO.json 경계 파일 경로
    sido_geojson_path = "./applicantMap/SIDO.json"
    with open(sido_geojson_path, 'r', encoding='utf-8') as f:
        sido_geojson_data = json.load(f)

    # SIGUNGU.json 경계 파일 경로
    sigungu_geojson_path = "./applicantMap/SIGUNGU.json"
    with open(sigungu_geojson_path, 'r', encoding='utf-8') as f:
        sigungu_geojson_data = json.load(f)

    # 지도 생성 (대한민국 중심)
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)

    # SIDO 경계 추가 (빨간색 경계)
    folium.GeoJson(
        sido_geojson_data,
        name="SIDO Boundary",
        style_function=lambda x: {
            "color": "blue", "weight": 3, "fillOpacity": 0
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["CTP_KOR_NM"],  # SIDO에서 지역명을 표시
            aliases=["시도명"],
            style="font-size: 14px;",
        ),
    ).add_to(m)

    # SIGUNGU 경계 추가 (파란색 경계)
    folium.GeoJson(
        sigungu_geojson_data,
        name="SIGUNGU Boundary",
        style_function=lambda x: {
            "color": "black", "weight": 1, "fillOpacity": 0
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["SIG_KOR_NM"],  # SIGUNGU에서 지역명을 표시
            aliases=["시군구명"],
            style="font-size: 12px;",
        ),
    ).add_to(m)

    # 지도에 Layer Control 추가
    folium.LayerControl().add_to(m)

    # 지도 저장
    m.save("./applicantMap/map.html")
    print("지도가 생성되어 'map.html'로 저장되었습니다.")


if __name__ == '__main__':
    # makeCSV()
    # sido()
    # sidoMap()
    # sigungu()
    # sigunguMap()
    main()
