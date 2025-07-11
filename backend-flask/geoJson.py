import pandas as pd
import geopandas as gpd
import json
import os

# 실행 필요 없음 - 시도 GeoJson 수정 완료
def sido():
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

    print("GeoJSON 파일 수정 완료")


# 실행 필요 없음 - 시군구 GeoJson 생성 완료
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
    print("GeoJSON 파일 생성 완료")


# 실행 필요 없음 - 시군구별 파일 생성 완료
def filteredBySigungu():
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
            "세종특별자치시"
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

        # 시군구 GeoJSON 저장 폴더가 없다면 생성
        output_dir = './applicantMap/sigungu_geojson'
        os.makedirs(output_dir, exist_ok=True)

        file_path = f'./applicantMap/sigungu_geojson/{sido}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(frame, f, ensure_ascii=False, separators=(',', ':'))

        cnt += 1
        print(f'{sido}의 GeoJSON 파일이 {file_path}로 저장되었습니다. // 총 {cnt}/17개')


def main():
    filteredBySigungu()


if __name__ == '__main__':
    main()