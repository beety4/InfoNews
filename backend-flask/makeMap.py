import pandas as pd
import os
import json
import folium


# 시군구별 Json 파일 생성
def dataBySigungu():
    df = pd.read_csv('./applicantMap/가공_2025 고교별 지원자 정보.csv', encoding='utf-8-sig')
    result = {}
    grouped = df.groupby(['지역명', '시군구명'])

    for (지역명, 시군구명), group in grouped:
        if 지역명 not in result:
            result[지역명] = {}
        result[지역명][시군구명] = group[['모집시기', '전형', '학과명', '졸업연도',
                                   '고교코드', '고교명', '지역명', '주소지', '연락처',
                                   '위도', '경도', '시군구명', '고교수']].to_dict(orient='records')

    # 결과를 JSON으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))

    # JSON 파일로 저장
    with open('./applicantMap/DataBySigungu.json', 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)


def main():
    df = pd.read_csv('./applicantMap/가공_2025 고교별 지원자 정보.csv', encoding='utf-8-sig')
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

    지역별_고교수 = df[['지역명', '고교수']].drop_duplicates()

    # GeoJSON 데이터에 고교 수 추가
    for feature in geojson_data_sido['features']:
        지역명 = feature['properties']['CTP_KOR_NM']
        고교수_row = 지역별_고교수[지역별_고교수['지역명'] == 지역명]

        if not 고교수_row.empty:
            feature['properties']['NUM_APPLICANT'] = int(고교수_row.iloc[0]['고교수'])
        else:
            feature['properties']['NUM_APPLICANT'] = 0

    geojson_sido = json.dumps(geojson_data_sido)  # 수정된 데이터를 JSON으로 변환

    # 지역별 고교수 통계를 시각화에 활용
    min_schools = 지역별_고교수['고교수'].min()
    max_schools = 지역별_고교수['고교수'].max()

    # 범위 설정 (색상 구간을 직접 설정)
    thresholds = [min_schools, 200, 300, 400, 500, 700, 1000, 5000, 7000, max_schools]

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

                // 시도 경계선 레이어
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
                        layer.bindTooltip('<b style="font-size: 16px;">' + feature.properties.CTP_KOR_NM + '</b>' + '<b style="font-size: 13px;">' + '<br>지원자 수: ' + feature.properties.NUM_APPLICANT + '</b>');
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
                    var sidoName = item.sido.trim();  // 시도 이름
                    var geojsonData = item.data;  // 시도별 geojson 데이터

                    sigunguLayers[sidoName] = L.geoJson(geojsonData, {{
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
                            var key = sidoName + "_" + sigunguName;

                            if (result[key]) {{
                                totalApplicants = result[key];  // 데이터 개수
                            }} else {{
                                // console.log('No data for ' + sigunguName);  // 해당 시군구 데이터가 없을 경우
                            }}

                            layer.bindTooltip('<b style="font-size: 16px;">' + sigunguName + '</b>' + '<b style="font-size: 13px;">' + '<br>지원자 수: ' + totalApplicants + '</b>');

                            // 클릭 이벤트 - 마커
                            layer.on('click', function(e) {{
                                // 선택한 시군구 이름 출력
                                console.log("Clicked sigungu:", sigunguName);

                                addMarker(sidoName, sigunguName);

                                // 줌 레벨 및 뷰 설정 (선택 사항)
                                // var bounds = layer.getBounds();
                                // map.fitBounds(bounds);
                            }});
                        }},
                        show: false  // 해당 레이어는 기본적으로 보이지 않도록 설정
                    }});
                }});

                var markersBySigungu = {{ }};
                
                // 모든 마커 제거 함수
                function clearAllMarkers() {{
                    for (var sido in markersBySigungu) {{
                        for (var sigungu in markersBySigungu[sido]) {{
                            markersBySigungu[sido][sigungu].forEach(function (marker) {{
                                map.removeLayer(marker.marker);
                            }});
                        }}
                    }}            
                    markersBySigungu = {{}};
                }}

                // 시군구 별 데이터 마커
                function addMarker(sidoName, sigunguName) {{
                    clearAllMarkers();

                    var markerData = dataBysigungu[sidoName][sigunguName];

                    if (!markerData || markerData.length === 0) {{
                        console.log('No data for', sigunguName); 
                        return;
                    }}
                    
                    // 마커 추가
                    var groupedData = {{}};           // 위도, 경도를 기준으로 그룹화
                    
                    markerData.forEach(function(point) {{
                        var lat = point.위도; 
                        var lng = point.경도; 
                        // 위도/경도가 없는 경우 로그 출력
                        if (!lat || !lng) {{
                            console.error('Invalid LatLng for', sigunguName, point);
                            return;
                        }}
                        var key = `${{lat}},${{lng}}`; // 위도, 경도를 키로 사용
                        if (!groupedData[key]) {{
                            groupedData[key] = [];
                        }}
                        groupedData[key].push(point);
                    }});

                    // 그룹화된 데이터가 없는 경우
                    if (Object.keys(groupedData).length === 0) {{
                        return;
                    }}
                    
                    // 해당 시군구의 마커 배열 초기화
                    markersBySigungu[sidoName] = markersBySigungu[sidoName] || {{ }};
                    markersBySigungu[sidoName][sigunguName] = [];
                    
                    // 그룹화된 데이터로 마커 추가
                    Object.keys(groupedData).forEach(function(key) {{
                        var firstKey = Object.keys(groupedData)[0]; // 첫 번째 마커만 선택
                        var points = groupedData[key];
                        var latLng = key.split(',');        // 키를 다시 위도, 경도로 분리
                        var lat = parseFloat(latLng[0]);    // 위도
                        var lng = parseFloat(latLng[1]);    // 경도
                        
                        // 전형별로 그룹화
                        var typeGroups = {{}};
                        
                        points.forEach(function(point) {{
                            var type = point.모집시기;
                            
                            // 타입이 제대로 있는지 확인
                            if (!type) {{
                                console.error("모집시기 정보가 없습니다:", point);
                                return;
                            }}

                            if (!typeGroups[type]) {{
                                typeGroups[type] = 0;
                            }}
                            typeGroups[type] += 1;
                        }});

                        var schoolNames = points[0].고교명;
                        var totalCount = 0;

                        // 팝업 내용
                        var popupContent = `<b style="font-size: 16px;">${{schoolNames}}</b><br><br>`;
                        for (var type in typeGroups) {{
                            if (typeGroups.hasOwnProperty(type)) {{
                                popupContent += `<b style="font-size: 13px;">${{type}}: ${{typeGroups[type]}}명</b><br>`;
                                totalCount += typeGroups[type];     // 총 지원자 수 계산
                            }}
                        }}
                        popupContent += `<br><b style="font-size: 13px;">지원자 총 ${{totalCount}}명</b><br>`;
                        
                        // 마커 생성
                        var marker = L.marker([lat, lng]).addTo(map);
                        marker.bindPopup(popupContent);

                        // 마커 배열에 추가
                        markersBySigungu[sidoName][sigunguName].push({{
                            marker : marker,
                            typeGroups: typeGroups,
                            schoolNames : schoolNames,
                            dataCount : points.length,
                        }});
                    }});

                    // 부모에게 데이터 전달
                    parent.postMessage({{
                        action: 'add',
                        data: markersBySigungu[sidoName][sigunguName].map(item => ({{
                            type: item.type,
                            typeGroups: item.typeGroups,
                            schoolNames: item.schoolNames,
                            dataCount: item.dataCount
                        }}))
                    }}, "http://127.0.0.1:8080/");
                }}

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
    m.save('./templates/2025_map.html')
    print("지도가 생성되어 2025_map.html로 저장되었습니다.")


if __name__ == '__main__':
    # sidoMap()
    # dataBySigungu()
    main()
