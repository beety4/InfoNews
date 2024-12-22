import pandas as pd
import os
import requests
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor
import geopandas as gpd
import json
import folium
from folium.plugins import MarkerCluster
from folium import FeatureGroup


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


def test():
    df = pd.read_csv('./applicantMap/가공_고교별_지원자_정보.csv')

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

    # SIDO 경계 추가
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

    # SIGUNGU 경계 추가
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

    # 데이터프레임의 모든 데이터를 마커로 추가
    for _, row in df.iterrows():
        folium.Marker(
            location=[row["위도"], row["경도"]],
            tooltip=f"{row['지역명']} - 고교수: {row['고교수']}",
            popup=folium.Popup(
                f"<b>지역명:</b> {row['지역명']}<br><b>고교수:</b> {row['고교수']}",
                max_width=300
            ),
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(m)

    # 지도에 Layer Control 추가
    folium.LayerControl().add_to(m)

    # 지도 저장
    m.save("./applicantMap/map.html")
    print("지도가 생성되어 'map.html'로 저장되었습니다.")


def makeMap():
    # 시도 데이터 로드
    df = pd.read_csv('./applicantMap/가공_고교별_지원자_정보.csv')

    geojson_path_sido = "./applicantMap/SIDO.json"
    geojson_path_sigungu = "./applicantMap/SIGUNGU.json"

    with open(geojson_path_sido, 'r', encoding='utf-8') as f:
        geojson_data_sido = json.load(f)

    with open(geojson_path_sigungu, 'r', encoding='utf-8') as f:
        geojson_data_sigungu = json.load(f)

    # 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles="OpenStreetMap",
                   attr="Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.")

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
        feature['properties']['고교수'] = int(고교수[0]) if len(고교수) > 0 else 0

    # 고교 수의 최소/최대 값 구하기 (범위 설정)
    min_schools = 지역별_고교수['고교수'].min()
    max_schools = 지역별_고교수['고교수'].max()

    # 범위 설정 (색상 구간을 직접 설정)
    thresholds = [0, 150, 250, 400, 600, 1000, 2000, 3500, 5000]
    # thresholds = [0,  65, 127, 133, 142, 178, 183, 186, 200, 216, 243, 309, 325, 493, 1810, 3335, 5000]

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

    # GeoJSON 데이터를 JSON으로 변환하여 JavaScript로 전달
    geojson_sido = json.dumps(geojson_data_sido)
    geojson_sigungu = json.dumps(geojson_data_sigungu)

    my_js = f"""
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
            var geojson_sido = {geojson_sido};
            var geojson_sigungu = {geojson_sigungu};
        
            var mapId = document.querySelector('.folium-map').id;
            var map = window[mapId];
            
            var sidoLayer = L.geoJson(geojson_sido, {{
                style: function(feature) {{
                    return {{
                        color: 'black',      // 시도 경계선 색상
                        weight: 2,           // 경계선 두께 (좀 더 두껍게 설정)
                        opacity: 0.7,        // 경계선 투명도 (약간 투명하게 설정)
                        fillOpacity: 0       // 내부 영역 투명도 (내부는 투명하게 설정)
                    }};
                }},
                onEachFeature: function(feature, layer) {{
                    layer.bindTooltip('<b>' + feature.properties.CTP_KOR_NM + '</b><br>고교수: ' + feature.properties.고교수);
                    layer.on('click', function(e) {{
                        changezoomFocus(feature, e);
                    }});
                }}
            }}).addTo(map);
        
            var sigunguLayer = L.geoJson(geojson_sigungu, {{
                style: function(feature) {{
                    return {{
                        color: 'black',      // 시군구 경계선 색상
                        weight: 2,           // 경계선 두께 (좀 더 얇게 설정)
                        opacity: 0.6,        // 경계선 투명도 (약간 투명하게 설정)
                        dashArray: '5, 8',   // 점선 스타일 (5px 점선, 5px 간격)
                        fillOpacity: 0       // 내부 영역 투명도 (내부는 투명하게 설정)
                    }};
                }},
                onEachFeature: function(feature, layer) {{
                    layer.bindTooltip('<b>' + feature.properties.SIG_KOR_NM + '</b>');
                }},
                show: false
            }});
            
            // 줌 이벤트: 줌 레벨에 따라 레이어 전환
            map.on('zoomend', function() {{
            var zoomLevel = map.getZoom();
            if (zoomLevel >= 9) {{  // 줌 레벨이 9 이상일 때 시군구 레이어 추가
                if (!map.hasLayer(sigunguLayer)) {{
                    sigunguLayer.addTo(map);
                }}
                if (!map.hasLayer(sidoLayer)) {{
                    sidoLayer.remove();
                }}
            }} else {{  // 줌 레벨이 10 미만일 때 시군구 레이어 제거하고 시도 레이어 보이게 함
                if (!map.hasLayer(sidoLayer)) {{
                    sidoLayer.addTo(map);
                }}
                if (map.hasLayer(sigunguLayer)) {{
                    sigunguLayer.remove();
                }}
            }}
            }});
            
            
            // 클릭 시 줌 이벤트 함수
            function changezoomFocus(feature, e) {{
                var sido = feature.properties;
                var bounds = e.target.getBounds();
                var center = bounds.getCenter();
                
                console.log(sido.CTP_KOR_NM);
                console.log(center);
                
                // 시도별 zoom 레벨 지정
                zoomLevel = 10;
                switch (sido.CTP_KOR_NM) {{
                    case "서울특별시": zoomLevel = 12; break;
                    case "강원특별자치도": zoomLevel = 9; break;
                    case "세종특별자치시": zoomLevel = 11; break;
                    case "대전광역시": zoomLevel = 12; break;
                    case "경상북도": zoomLevel = 9; center = [36.5759, 128.5052]; break;
                    case "전라남도": zoomLevel = 9; center = [34.8679, 126.9910];break;
                    case "전북특별자치도": zoomLevel = 10; center = [35.7175, 127.1530];;break;
                    case "광주광역시": zoomLevel = 11; break;
                    case "울산광역시": zoomLevel = 11; break;
                    case "부산광역시": zoomLevel = 11; break;
                    case "인천광역시": zoomLevel = 10; center = [37.4563, 126.7052]; break;
                    case "경기도": zoomLevel = 9; break;
                    default: zoomLevel = 10; break;
                }}
                
                map.setView(center, zoomLevel);
            }}
            
            }});
        </script>
        """

    m.get_root().html.add_child(folium.Element(my_js))

    # 저장
    m.save('./applicantMap/map.html')
    print("지도가 생성되어 map.html로 저장되었습니다.")


def markerCircle():
    # 시도 데이터 로드
    df = pd.read_csv('./applicantMap/가공_고교별_지원자_정보.csv')

    geojson_path_sido = "./applicantMap/SIDO.json"
    geojson_path_sigungu = "./applicantMap/SIGUNGU.json"

    with open(geojson_path_sido, 'r', encoding='utf-8') as f:
        geojson_data_sido = json.load(f)

    with open(geojson_path_sigungu, 'r', encoding='utf-8') as f:
        geojson_data_sigungu = json.load(f)

    # 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)

    # 대한민국의 범위로 fit_bounds 설정
    south_lat = 33.0  # 최남단 위도
    north_lat = 38.6  # 최북단 위도
    west_lon = 124.0  # 최서단 경도
    east_lon = 132.0  # 최동단 경도

    m.fit_bounds([[south_lat, west_lon], [north_lat, east_lon]])
    m.options['maxBounds'] = [[south_lat, west_lon], [north_lat, east_lon]]
    m.options['minZoom'] = 7  # 최소 줌 레벨

    # MarkerCluster 객체 생성
    marker_cluster = MarkerCluster().add_to(m)

    # 마커와 CircleMarker 추가
    for _, row in df.iterrows():
        folium.Marker(
            location=[row["위도"], row["경도"]],
            popup=f"{row['고교명']} ({row['지역명']})\n학과: {row['학과명']}",
        ).add_to(marker_cluster)

        # 마커 주변에 원을 그리기
        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=10,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.4,
        ).add_to(marker_cluster)

    # GeoJSON 데이터를 JSON으로 변환하여 JavaScript로 전달
    geojson_sido = json.dumps(geojson_data_sido)
    geojson_sigungu = json.dumps(geojson_data_sigungu)

    my_js = f"""
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                var geojson_sido = {geojson_sido};
                var geojson_sigungu = {geojson_sigungu};

                var mapId = document.querySelector('.folium-map').id;
                var map = window[mapId];

                var sidoLayer = L.geoJson(geojson_sido, {{
                    style: function(feature) {{
                        return {{
                            color: 'black',      // 시도 경계선 색상
                            weight: 2,           // 경계선 두께 (좀 더 두껍게 설정)
                            opacity: 0.7,        // 경계선 투명도 (약간 투명하게 설정)
                            fillOpacity: 0       // 내부 영역 투명도 (내부는 투명하게 설정)
                        }};
                    }},
                    onEachFeature: function(feature, layer) {{
                        layer.bindTooltip('<b>' + feature.properties.CTP_KOR_NM + '</b><br>고교수: ' + feature.properties.고교수);
                        layer.on('click', function(e) {{
                            changezoomFocus(feature, e);
                        }});
                    }}
                }}).addTo(map);

                var sigunguLayer = L.geoJson(geojson_sigungu, {{
                    style: function(feature) {{
                        return {{
                            color: 'black',      // 시군구 경계선 색상
                            weight: 2,           // 경계선 두께 (좀 더 얇게 설정)
                            opacity: 0.6,        // 경계선 투명도 (약간 투명하게 설정)
                            dashArray: '5, 8',   // 점선 스타일 (5px 점선, 5px 간격)
                            fillOpacity: 0       // 내부 영역 투명도 (내부는 투명하게 설정)
                        }};
                    }},
                    onEachFeature: function(feature, layer) {{
                        layer.bindTooltip('<b>' + feature.properties.SIG_KOR_NM + '</b>');
                    }},
                    show: false
                }});

                // 줌 이벤트: 줌 레벨에 따라 레이어 전환
                map.on('zoomend', function() {{
                var zoomLevel = map.getZoom();
                if (zoomLevel >= 9) {{  // 줌 레벨이 9 이상일 때 시군구 레이어 추가
                    if (!map.hasLayer(sigunguLayer)) {{
                        sigunguLayer.addTo(map);
                    }}
                    if (!map.hasLayer(sidoLayer)) {{
                        sidoLayer.remove();
                    }}
                }} else {{  // 줌 레벨이 10 미만일 때 시군구 레이어 제거하고 시도 레이어 보이게 함
                    if (!map.hasLayer(sidoLayer)) {{
                        sidoLayer.addTo(map);
                    }}
                    if (map.hasLayer(sigunguLayer)) {{
                        sigunguLayer.remove();
                    }}
                }}
                }});

                // 클릭 시 줌 이벤트 함수
                function changezoomFocus(feature, e) {{
                    var sido = feature.properties;
                    var bounds = e.target.getBounds();
                    var center = bounds.getCenter();

                    console.log(sido.CTP_KOR_NM);
                    console.log(center);

                    // 시도별 zoom 레벨 지정
                    zoomLevel = 10;
                    switch (sido.CTP_KOR_NM) {{
                        case "서울특별시": zoomLevel = 12; break;
                        case "강원특별자치도": zoomLevel = 9; break;
                        case "세종특별자치시": zoomLevel = 11; break;
                        case "대전광역시": zoomLevel = 12; break;
                        case "경상북도": zoomLevel = 9; center = [36.5759, 128.5052]; break;
                        case "전라남도": zoomLevel = 9; center = [34.8679, 126.9910];break;
                        case "전북특별자치도": zoomLevel = 10; center = [35.7175, 127.1530];;break;
                        case "광주광역시": zoomLevel = 11; break;
                        case "울산광역시": zoomLevel = 11; break;
                        case "부산광역시": zoomLevel = 11; break;
                        case "인천광역시": zoomLevel = 10; center = [37.4563, 126.7052]; break;
                        case "경기도": zoomLevel = 9; break;
                        default: zoomLevel = 10; break;
                    }}

                    map.setView(center, zoomLevel);
                }}

                }});
            </script>
            """

    m.get_root().html.add_child(folium.Element(my_js))

    # 저장
    m.save('./applicantMap/map.html')
    print("지도가 생성되어 map.html로 저장되었습니다.")



def sigungu_json_split():
    geojson_path_sigungu = "./applicantMap/SIGUNGU.json"
    with open(geojson_path_sigungu, 'r', encoding='utf-8') as f:
        geojson_data_sigungu = json.load(f)

    # 시도별 시군구 리스트
    sido_list = {
        "서울특별시": [
            "종로구", "중구", "용산구", "성동구", "광진구", "동대문구", "중랑구", "강북구", "도봉구", "노원구", "은평구", "서대문구", "마포구", "양천구", "강서구",
            "구로구", "금천구", "영등포구", "동작구", "관악구", "서초구", "강남구", "송파구", "강동구"
        ],
        "부산광역시": [
            "중구", "서구", "동구", "영도구", "부산진구", "동래구", "남구", "북구", "해운대구", "사하구", "금정구", "강서구", "연제구", "수영구", "사상구", "기장군"
        ],
        "대구광역시": [
            "중구", "서구", "동구", "남구", "북구", "수성구", "달서구", "달성군"
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
            "수원시", "성남시", "의정부시", "안양시", "부천시", "광명시", "평택시", "동두천시", "안산시", "고양시", "과천시", "구리시", "남양주시", "오산시", "화성시",
            "광주시", "이천시", "시흥시", "군포시", "의왕시", "하남시", "용인시", "파주시", "김포시", "양주시", "동두천시", "연천군", "가평군", "여주군", "포천시",
            "양평군"
        ],
        "강원특별자치도": [
            "춘천시", "원주시", "강릉시", "동해시", "태백시", "속초시", "삼척시", "홍천군", "횡성군", "영월군", "평창군", "정선군", "철원군", "화천군", "양구군",
            "인제군", "고성군", "양양군"
        ],
        "충청북도": [
            "청주시", "충주시", "제천시", "보은군", "옥천군", "영동군", "진천군", "괴산군", "음성군", "김제시", "증평군", "청원군"
        ],
        "충청남도": [
            "천안시", "공주시", "보령시", "아산시", "서산시", "논산시", "계룡시", "당진시", "금산군", "부여군", "서천군", "청양군", "홍성군", "예산군", "태안군"
        ],
        "전라북도": [
            "전주시", "익산시", "군산시", "정읍시", "남원시", "김제시", "완주군", "진안군", "임실군", "순창군", "고창군", "부안군"
        ],
        "전라남도": [
            "목포시", "여수시", "순천시", "나주시", "광양시", "담양군", "곡성군", "구례군", "고흥군", "보성군", "화순군", "장흥군", "강진군", "해남군", "영암군",
            "무안군", "함평군", "영광군", "장성군", "완도군", "진도군", "신안군"
        ],
        "경상북도": [
            "포항시", "경주시", "김천시", "안동시", "구미시", "영주시", "영천시", "상주시", "문경시", "경산시", "군위군", "의성군", "청송군", "영양군", "영덕군",
            "청도군", "고령군", "성주군", "칠곡군", "문경시", "예천군", "봉화군", "울진군", "울릉군"
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




def main():
    # 시도 데이터 로드
    df = pd.read_csv('./applicantMap/가공_고교별_지원자_정보.csv')

    geojson_path_sido = "./applicantMap/SIDO.json"
    geojson_path_sigungu = "./applicantMap/SIGUNGU.json"

    with open(geojson_path_sido, 'r', encoding='utf-8') as f:
        geojson_data_sido = json.load(f)

    with open(geojson_path_sigungu, 'r', encoding='utf-8') as f:
        geojson_data_sigungu = json.load(f)

    # GeoJSON 데이터를 JSON으로 변환하여 JavaScript로 전달
    geojson_sido = json.dumps(geojson_data_sido)
    geojson_sigungu = json.dumps(geojson_data_sigungu)


    # 17개 지역 경로 설정
    regions = [
        "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시",
        "세종특별자치시", "경기도", "강원특별자치도", "충청북도", "충청남도", "전북특별자치도", "전라남도",
        "경상북도", "경상남도", "제주특별자치도"
    ]
    file_paths = {
        region: f"./applicantMap/sigungu/{region}.json" for region in regions
    }
    # 파일 로드
    region_data = {}
    for region, path in file_paths.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                region_data[region] = json.load(f)
                print(f"{region} 데이터 로드 완료")
        except FileNotFoundError:
            print(f"파일이 존재하지 않습니다: {path}")
        except json.JSONDecodeError:
            print(f"JSON 형식 오류가 있습니다: {path}")
    print("모든 파일 로드 완료")



    # 시도별 시군구 json 불러오기
    each_sigungu = []
    for region in regions:
        file_path = os.path.join("./applicantMap/sigungu_geojson", f"{region}.json")

        # 해당 파일이 존재하는 경우에만 처리
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                geojson_data = json.load(file)

                # "sido"와 "data" 키를 포함하는 딕셔너리 추가
                each_sigungu.append({
                    "sido": region,
                    "data": geojson_data
                })

    # 최종 결과 출력 (혹은 반환)
    each_sigungu = json.dumps(each_sigungu)
    print("각 시도 별 geojson 데이터 로드 완료")





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
        feature['properties']['고교수'] = int(고교수[0]) if len(고교수) > 0 else 0

    # 고교 수의 최소/최대 값 구하기 (범위 설정)
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





    """
    # 클러스터 생성
    marker_cluster = MarkerCluster().add_to(m)
    # 마커 추가: 시도별 클러스터에 해당하는 고교 데이터 개수를 마커로 표시
    for _, row in 지역별_고교수.iterrows():
        # 해당 지역에 맞는 마커 클러스터 생성
        folium.Marker(
            location=[df[df['지역명'] == row['지역명']].iloc[0]['위도'],
                      df[df['지역명'] == row['지역명']].iloc[0]['경도']],
            popup=f"{row['지역명']} 고교수: {row['고교수']}개",
            icon=folium.Icon(color='blue')
        ).add_to(marker_cluster)
    """


    # 시도별 시군구 고교 json 불러오기
    marker_sigungu = {}
    for region in regions:
        file_path = os.path.join("./applicantMap/sigungu", f"{region}.json")

        # 해당 파일이 존재하는 경우에만 처리
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                geojson_data = json.load(file)
                marker_sigungu[region] = geojson_data


    # 최종 결과 출력 (혹은 반환)
    marker_sigungu = json.dumps(marker_sigungu)
    print("각 시도 별 marker 데이터 로드 완료")










    my_js = f"""
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
            var geojson_sido = {geojson_sido};
            var geojson_sigungu = {geojson_sigungu};
            var each_sigungu = {each_sigungu};
            var marker_sigungu = {marker_sigungu};

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
                    layer.bindTooltip('<b>' + feature.properties.CTP_KOR_NM + '</b><br>고교수: ' + feature.properties.고교수);
                    layer.on('click', function(e) {{
                        changezoomFocus(feature, e);
                        //showMarkers(feature);  // 클릭 시 해당 마커만 표시
                    }});
                }}
            }}).addTo(map);


            var sigunguLayer = L.geoJson(geojson_sigungu, {{
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
                    layer.bindTooltip('<b>' + feature.properties.SIG_KOR_NM + '</b>');
                }},
                show: false
            }});


            // 각각의 시군구 레이어를 시도별 분리한 데이터 레이어로 불러오기
            var sigunguLayers = {{ }};
            each_sigungu.forEach(function(item) {{
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
                        layer.bindTooltip('<b>' + feature.properties.SIG_KOR_NM + '</b>');
                    }},
                    show: false  // 해당 레이어는 기본적으로 보이지 않도록 설정
                }});
            }});
            
            
            
            
            
            
            // MarkerCluster 객체 생성
            var markerCluster = L.markerClusterGroup();
            
            function marker_zzan(clickSidoName) {{
                map.removeLayer(markerCluster);
            
                // 새로운 마커 클러스터 생성
                markerCluster = L.markerClusterGroup();
            
                // 해당 시도의 데이터를 기반으로 마커 추가
                marker_sigungu.forEach(function(school) {{
                    var lat = school.위도;
                    var lon = school.경도;
                    var schoolName = school.고교명;
                    var applicantCount = school.고교수;
        
                        // 마커 생성
                    var marker = L.marker([lat, lon])
                        .bindPopup("<b>" + schoolName + "</b><br>지원자 수: " + applicantCount);
        
                    markerCluster.addLayer(marker);
                }});
        
                // 마커 클러스터를 지도에 추가
                map.addLayer(markerCluster);
            }}
            
            
            
            
            
            
            


            // 줌 이벤트: 줌 레벨에 따라 레이어 전환
            map.on('zoomend', function() {{
                var zoomLevel = map.getZoom();
                if (zoomLevel >= 9) {{
                    if (!map.hasLayer(sigunguLayer)) {{
                        //sigunguLayer.addTo(map);
                    }}
                    if (!map.hasLayer(sidoLayer)) {{
                        sidoLayer.remove();
                    }}
                }} else {{
                    if (!map.hasLayer(sidoLayer)) {{
                        sidoLayer.addTo(map);
                    }}
                    if (map.hasLayer(sigunguLayer)) {{
                        //sigunguLayer.remove();
                    }}
                }}
            }});


            // 클릭 시 줌 이벤트 함수
            function changezoomFocus(feature, e) {{
                var sido = feature.properties;
                var bounds = e.target.getBounds();
                var center = bounds.getCenter();

                var clickSidoName = sido.CTP_KOR_NM;
                var zoomLevel = 10;
                switch (clickSidoName) {{
                    case "서울특별시": zoomLevel = 12; break;
                    case "부산광역시": break;
                    case "대구광역시": break;
                    case "인천광역시": break;
                    case "광주광역시": break;
                    case "대전광역시": break;
                    case "울산광역시": break;
                    case "세종특별자치시": break;
                    case "경기도": zoomLevel = 9; break;
                    case "강원특별자치도": break;
                    case "충청북도": break;
                    case "충청남도": break;
                    case "전북특별자치도": break;
                    case "전라남도": break;
                    case "경상북도": break;
                    case "경상남도": break;
                    case "제주특별자치도": break;
                    default: console.log("Unknown Sido name: " + clickSidoName); break;
                }}
                
                marker_zzan(clickSidoName);
                map.setView(center, zoomLevel);
            }}

            // 클릭된 지역에 해당하는 마커만 표시
            function showMarkers(feature) {{
                // 여기서 해당 지역에 해당하는 마커만 표시
                alert("클릭한 지역에 해당하는 마커를 표시할 수 있습니다!");
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

    # sidoMap()
    # sigunguMap()
    # test()
    # makeMap()
    # markerCircle()
    # sigungu_json_split()
    main()
