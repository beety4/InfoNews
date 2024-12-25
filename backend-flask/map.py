import pandas as pd
import os
import requests
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor
import geopandas as gpd
import json
import folium
from collections import defaultdict


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

    # 고교수 -> 학생수
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

    # 대한민국의 범위로 fit_bounds 설정
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
            aliases=["시도명", "고교수"],  # 필드명에 대한 별칭
            localize=True,
            style="font-size: 16px; font-weight: bold;",
        ),
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


def newColumn():
    # CSV 파일 읽기
    df = pd.read_csv('./applicantMap/가공_고교별_지원자_정보.csv')

    # 주소지에서 시군구명 추출하여 '시군구명' 컬럼에 추가 (예외처리 추가)
    def extract_sigunggu(address):
        parts = address.split()
        if len(parts) >= 3:  # 최소 3개 이상의 요소가 있는 경우
            return parts[1]
        else:
            return None  # 시군구명이 없는 경우 None 반환

    # 주소지 컬럼을 기준으로 시군구명 추출
    df['시군구명'] = df['주소지'].apply(extract_sigunggu)

    # CSV 파일 저장 (한글 깨짐 방지)
    df.to_csv('./applicantMap/가공_고교별_지원자_정보.csv', encoding='utf-8-sig', index=False)
    print("저장되었습니다.")


def filteredBySido():
    df = pd.read_csv("./applicantMap/가공_고교별_지원자_정보.csv")
    grouped = df.groupby("지역명")

    for region, group in grouped:
        filename = "./applicantMap/" + region + ".json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(group.to_dict(orient="records"), f, ensure_ascii=False, indent=4)

    print("지역별 JSON파일이 생성되었습니다.")


def sigungu_json_split():
    geojson_path_sigungu = "./applicantMap/SIGUNGU.json"
    with open(geojson_path_sigungu, 'r', encoding='utf-8') as f:
        geojson_data_sigungu = json.load(f)

    # 시도별 시군구 리스트
    sido_list = {
        "서울특별시": [
            "종로구", "중구", "용산구", "성동구", "광진구", "동대문구", "중랑구", "성북구", "강북구", "도봉구", "노원구", "은평구", "서대문구",
            "마포구", "양천구", "강서구", "구로구", "금천구", "영등포구", "동작구", "관악구", "서초구", "강남구", "송파구", "강동구"
        ],
        "부산광역시": [
            "중구", "서구", "동구", "영도구", "부산진구", "동래구", "남구", "북구", "해운대구", "사하구", "금정구", "강서구", "연제구", "수영구", "사상구", "기장군"
        ],
        "대구광역시": [
            "중구", "서구", "동구", "남구", "북구", "수성구", "달서구", "달성군", "군위군"
        ],
        "인천광역시": [
            "중구", "동구", "미추홀구", "연수구", "남동구", "부평구", "계양구", "서구", "강화군", "옹진군"
        ],
        "광주광역시": [
            "동구", "서구", "남구", "북구", "광산구"
        ],
        "대전광역시": [
            "동구", "중구", "서구", "유성구", "대덕구"
        ],
        "울산광역시": [
            "중구", "남구", "동구", "북구", "울주군"
        ],
        "세종특별자치시": [
            "세종시"
        ],
        "경기도": [
            "수원시", "용인시", "고양시", "화성시", "성남시", "부천시", "남양주시", "안산시", "평택시", "안양시", "시흥시", "파주시", "김포시", "의정부시",
            "광주시", "하남시", "광명시", "군포시", "양주시", "오산시", "이천시", "안성시", "구리시", "의왕시", "포천시", "양평군", "여주시", "동두천시", "과천시",
            "가평군", "연천군"
        ],
        "강원특별자치도": [
            "춘천시", "원주시", "강릉시", "동해시", "태백시", "속초시", "삼척시", "홍천군", "횡성군", "영월군", "평창군", "정선군", "철원군", "화천군", "양구군",
            "인제군", "고성군", "양양군"
        ],
        "충청북도": [
            "청주시", "충주시", "제천시", "보은군", "옥천군", "영동군", "진천군", "괴산군", "음성군", "단양군", "증평군"
        ],
        "충청남도": [
            "천안시", "공주시", "보령시", "아산시", "서산시", "논산시", "계룡시", "당진시", "금산군", "부여군", "서천군", "청양군", "홍성군", "예산군", "태안군"
        ],
        "전북특별자치도": [
            "전주시", "군산시", "익산시", "정읍시", "남원시", "김제시", "완주군", "진안군", "무주군", "장수군", "임실군", "순창군", "고창군", "부안군"
        ],
        "전라남도": [
            "목포시", "여수시", "순천시", "나주시", "광양시", "담양군", "곡성군", "구례군", "고흥군", "보성군", "화순군", "장흥군", "강진군", "해남군",
            "영암군", "무안군", "함평군", "영광군", "장성군", "완도군", "진도군", "신안군"
        ],
        "경상북도": [
            "포항시", "경주시", "김천시", "안동시", "구미시", "영주시", "영천시", "상주시", "문경시", "경산시", "의성군", "청송군",
            "영양군", "영덕군", "청도군", "고령군", "성주군", "칠곡군", "예천군", "봉화군", "울진군", "울릉군"
        ],
        "경상남도": [
            "창원시", "진주시", "통영시", "사천시", "김해시", "밀양시", "거제시", "양산시", "의령군", "함안군", "창녕군", "고성군", "남해군", "하동군", "산청군",
            "함양군", "거창군", "합천군"
        ],
        "제주특별자치도": [
            "제주시", "서귀포시"
        ]
    }

    cnt = 0
    # 전체 GeoJSON에서 각 시도별로 필터링하고 저장
    for sido, sigungu_list in sido_list.items():
        frame = {
            "type": "FeatureCollection",
            "name": "SIGUNGU",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            },
            "features": []
        }

        # 각 시군구 데이터를 필터링
        for feature in geojson_data_sigungu['features']:
            sig_kor_nm = feature['properties']['SIG_KOR_NM']

            # 해당 시군구가 시도 리스트에 속하는지 확인
            if sig_kor_nm in sigungu_list:
                frame['features'].append(feature)

        # 시도별로 GeoJSON 파일을 저장
        file_path = f'./applicantMap/sigungu_geojson/{sido}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(frame, f, ensure_ascii=False, separators=(',', ':'))

        cnt += 1
        print(f'{sido}의 GeoJSON 파일이 {file_path}로 저장되었습니다. // 총 {cnt}/17개')


def data_by_sigungu():
    df = pd.read_csv('./applicantMap/가공_고교별_지원자_정보.csv')
    grouped = df.groupby(['지역명', '시군구명'])

    result = {}

    # 세종특별시를 처리하기 위해 별도로 그룹화하기 전에 세종을 분리
    sejong_data = df[df['지역명'] == '세종특별자치시']

    # 세종특별시 데이터는 시군구명 없이 바로 추가
    result['세종특별자치시'] = sejong_data[['모집시기명', '전형명', '학과명', '졸업년도',
                                     '고교코드', '고교명', '주소지', '연락처',
                                     '위도', '경도', '고교수']].to_dict(orient='records')

    # 나머지 지역들은 지역명과 시군구명 기준으로 그룹화
    grouped = df[df['지역명'] != '세종특별자치시'].groupby(['지역명', '시군구명'])

    for (지역명, 시군구명), group in grouped:
        if 지역명 not in result:
            result[지역명] = {}
        result[지역명][시군구명] = group[['모집시기명', '전형명', '학과명', '졸업년도',
                                   '고교코드', '고교명', '주소지', '연락처',
                                   '위도', '경도', '고교수']].to_dict(orient='records')

    # 결과를 JSON으로 출력
    # print(json.dumps(result, ensure_ascii=False, indent=4))

    # JSON 파일로 저장
    with open('./applicantMap/DataBySigungu.json', 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)


def main():
    # 시도 데이터 로드
    df = pd.read_csv('./applicantMap/가공_고교별_지원자_정보.csv')

    geojson_path_sido = "./applicantMap/SIDO.json"

    with open(geojson_path_sido, 'r', encoding='utf-8') as f:
        geojson_data_sido = json.load(f)

    # GeoJSON 데이터를 JSON으로 변환하여 JavaScript로 전달
    geojson_sido = json.dumps(geojson_data_sido)
    print("각 시도 별 geojson 데이터 로드 완료")

    # 17개 지역 경로 설정
    regions = [
        "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시",
        "세종특별자치시", "경기도", "강원특별자치도", "충청북도", "충청남도", "전북특별자치도", "전라남도",
        "경상북도", "경상남도", "제주특별자치도"
    ]

    # 시도별 시군구 json 불러오기
    geojson_sigungu = []
    for region in regions:
        file_path = os.path.join("./applicantMap/sigungu_geojson", f"{region}.json")

        # 해당 파일이 존재하는 경우에만 처리
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                geojson_data = json.load(file)

                # "sido"와 "data" 키를 포함하는 딕셔너리 추가
                geojson_sigungu.append({
                    "sido": region,
                    "data": geojson_data
                })

    # 최종 결과 출력 (혹은 반환)
    geojson_sigungu = json.dumps(geojson_sigungu)
    print("각 시군구 별 geojson 데이터 로드 완료")

    # DataBySigungu
    geojson_path = "./applicantMap/DataBySigungu.json"

    with open(geojson_path, 'r', encoding='utf-8') as f:
        data_by_sigungu = json.load(f)

    # JavaScript로 전달
    data_by_sigungu = json.dumps(data_by_sigungu)
    print("각 시군구 별 csv 데이터 로드 완료")

    # 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles="CartoDB positron")

    # 대한민국의 범위로 fit_bounds 설정
    south_lat = 33.0  # 최남단 위도
    north_lat = 38.6  # 최북단 위도
    west_lon = 124.0  # 최서단 경도
    east_lon = 132.0  # 최동단 경도

    m.fit_bounds([[south_lat, west_lon], [north_lat, east_lon]])
    m.options['maxBounds'] = [[south_lat, west_lon], [north_lat, east_lon]]
    m.options['minZoom'] = 7  # 최소 줌 레벨
    m.options['maxZoom'] = 15  # 최대 줌 레벨

    # 지역별 고교 수 집계
    지역별_고교수 = df.groupby('지역명').size().reset_index(name='고교수')

    # GeoJSON 데이터에 고교 수 추가
    for feature in geojson_data_sido['features']:
        지역명 = feature['properties']['CTP_KOR_NM']
        고교수 = 지역별_고교수[지역별_고교수['지역명'] == 지역명]['고교수'].values
        feature['properties']['NUM_APPLICANT'] = int(고교수[0]) if len(고교수) > 0 else 0

    # for feature in geojson_data_sido['features']:
    #     print(feature['properties'])  # NUM_APPLICANT 속성이 추가되었는지 확인

    geojson_sido = json.dumps(geojson_data_sido)  # 수정된 데이터를 JSON으로 변환

    # 고교 수의 최소/최대 값 구하기 (범위 확인)
    min_schools = 지역별_고교수['고교수'].min()
    max_schools = 지역별_고교수['고교수'].max()

    # 범위 설정 (색상 구간을 직접 설정)
    thresholds = [0, 150, 250, 400, 600, 1000, 2000, 3500, 5000]

    # Choropleth 추가
    folium.Choropleth(
        geo_data=geojson_data_sido,
        name="choropleth",
        data=지역별_고교수,
        columns=['지역명', '고교수'],
        key_on="feature.properties.CTP_KOR_NM",
        fill_color="YlGnBu",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="고교수",
        threshold_scale=thresholds  # 색상 구간 설정
    ).add_to(m)

    my_js = f"""
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                var geojson_sido = {geojson_sido};          // 시도별 GeoJson
                var geojson_sigungu = {geojson_sigungu};    // 시군구별 GeoJson
                var dataBysigungu = {data_by_sigungu};      // 시군구별 데이터

                var mapId = document.querySelector('.folium-map').id;
                var map = window[mapId];

                // 각 레이어 추가 부분
                var sidoLayer = L.geoJson(geojson_sido, {{
                    style: function(feature) {{
                        return {{
                            color: 'black',      // 시도 경계선 색상
                            weight: 2,           // 경계선 두께
                            opacity: 0.7,        // 경계선 투명도
                            fillOpacity: 0       // 내부 영역 투명도
                        }};
                    }},
                    onEachFeature: function(feature, layer) {{
                        layer.bindTooltip('<b>' + feature.properties.CTP_KOR_NM + '</b><br>지원자 수: ' + feature.properties.NUM_APPLICANT);
                        layer.on('click', function(e) {{
                            changezoomFocus(feature, e);
                        }});
                    }}
                }}).addTo(map);

                // 각 구별 데이터 개수 계산
                var result = {{}};
                for (var sido in dataBysigungu) {{
                    if (dataBysigungu.hasOwnProperty(sido)) {{
                        var sigunguData = dataBysigungu[sido]; 
                        for (var sigungu in sigunguData) {{
                            if (sigunguData.hasOwnProperty(sigungu)) {{
                                // 중복된 이름을 위해 고유 이름 설정
                                var key = sido + "_" + sigungu;
                                result[key] = sigunguData[sigungu].length;  
                            }}
                        }}
                    }}
                }}

                // 각각의 시군구 레이어를 시도별 분리한 데이터 레이어로 불러오기
                var sigunguLayers = {{ }};
                geojson_sigungu.forEach(function(item) {{
                    var sido = item.sido.trim();  // 시도 이름
                    var geojsonData = item.data;  // 시도별 geojson 데이터

                    sigunguLayers[sido] = L.geoJson(geojsonData, {{
                        style: function(feature) {{
                            return {{
                                color: 'black',
                                weight: 2,
                                opacity: 0.6,
                                dashArray: '5, 8',
                                fillOpacity: 0
                            }};
                        }},
                        onEachFeature: function(feature, layer) {{
                            var sigunguName = feature.properties.SIG_KOR_NM;  // 시군구명
                            var totalApplicants = 0;
                            
                            // 해당 시군구의 데이터 개수 가져오기
                            var key = sido + "_" + sigunguName;
                            
                            if (result[key]) {{
                                totalApplicants = result[key];  // 데이터 개수
                            }} else {{
                                console.log('No data for ' + sigunguName);  // 해당 시군구 데이터가 없을 경우
                            }}
                        
                            layer.bindTooltip('<b>' + sigunguName + '</b><br>지원자 수: ' + totalApplicants);
                        }},
                        show: false  // 해당 레이어는 기본적으로 보이지 않도록 설정
                    }});
                }});




                // 현재 활성화된 시군구 레이어
                var currentSigunguLayer = null;

                // 클릭 시 줌 이벤트 함수
                function changezoomFocus(feature, e) {{
                    var sidoName = feature.properties.CTP_KOR_NM;
                    var bounds = e.target.getBounds();
                    var center = bounds.getCenter();
                    
                    // 시도별 zoom 레벨 및 센터 지정
                    var zoomLevel = 10;
                    switch (sidoName) {{
                        case "서울특별시": zoomLevel = 12; break;
                        case "강원특별자치도": zoomLevel = 9; break;
                        case "세종특별자치시": zoomLevel = 11; break;
                        case "대전광역시": zoomLevel = 12; break;
                        case "경상북도": zoomLevel = 9; center = [36.5759, 128.5052]; break;
                        case "전라남도": zoomLevel = 9; center = [34.8679, 126.9910];break;
                        case "전북특별자치도": zoomLevel = 10; center = [35.7175, 127.1530]; break;
                        case "광주광역시": zoomLevel = 11; break;
                        case "울산광역시": zoomLevel = 11; break;
                        case "부산광역시": zoomLevel = 11; break;
                        case "인천광역시": zoomLevel = 10; center = [37.4563, 126.7052]; break;
                        case "경기도": zoomLevel = 9; break;
                        default: zoomLevel = 10; break;
                    }}
                    map.setView(center, zoomLevel);
                    
                    // 기존 시군구 레이어 제거
                    if (currentSigunguLayer && map.hasLayer(currentSigunguLayer)) {{
                        map.removeLayer(currentSigunguLayer);
                    }}
                
                    // 클릭된 시도의 시군구 레이어 추가
                    if (sigunguLayers[sidoName]) {{
                        currentSigunguLayer = sigunguLayers[sidoName];
                        currentSigunguLayer.addTo(map);
                    }}
                
                    // 시도 레이어 숨기기
                    if (map.hasLayer(sidoLayer)) {{
                        map.addLayer(sidoLayer);
                    }}
                }}

            }})
            </script>
        """

    m.get_root().html.add_child(folium.Element(my_js))

    # 저장
    m.save('./applicantMap/map.html')
    print("지도가 생성되어 map.html로 저장되었습니다.")


if __name__ == '__main__':
    # makeCSV()
    # sido()
    # sigungu()
    # newColumn()
    # filteredBySido()
    # sigungu_json_split()

    # sidoMap()
    # sigunguMap()
    data_by_sigungu()
    main()
