import json

from naver_api import NaverAPI
import pandas as pd
from scipy.stats import zscore
import data_process as dp


# 입력받은 키워드 리스트를, 'compare'가 포함된 5개 이하의 2차원 배열로 변환
def keyword_split(keyword_list):
    result = []

    for i in range(0, len(keyword_list), 4):
        group = ['compare'] + keyword_list[i:i + 4]
        result.append(group)

    #print(result)
    return result


# API 결과 json 을 dataframe으로 생성
def create_df(data):
    rows = []
    for item in data['results']:
        title = item['title']
        for entry in item['data']:
            rows.append({'title': title, 'period': entry['period'], 'ratio': entry['ratio']})

    df = pd.DataFrame(rows)
    df = df.sort_values('period')

    return df


# 데이터 입력받은 뒤, naver_api를 사용하여 요청
def get_each_data(universityGroup, startDate, endDate, timeUnit, nowdate):

    keyword_list = []
    if universityGroup == "uni1":
        keyword_list = ['인하공전', '유한대', '부천대', '재능대', '재능대', '동양미래대', '연성대', '동서울대', '한양여대']
    elif universityGroup == "uni2":
        keyword_list = ['인하공전', '유한대', '부천대', '재능대', '동양미래대', '연성대', '동서울대', '한양여대', '경복대', '명지전문대', '서일대']

    each_keyword_list = keyword_split(keyword_list)


    try:
        api = NaverAPI()
        df_list = []
        for kl in each_keyword_list:
            result = api.access_keyword(kl, startDate, endDate, timeUnit)
            result_df = create_df(result)

            # 첫번째 compare의 ratio값을 가져온뒤 임의값 100으로 비율 게산
            first_compare_ratio = result_df[result_df['title'] == 'compare'].iloc[0]['ratio']
            point_per_ratio = 100 / first_compare_ratio

            # 새로 계산한 ratio 값 추가 후, compare은 삭제
            result_df['point_ratio'] = result_df['ratio'] * point_per_ratio
            result_df = result_df[result_df['title'] != 'compare']
            df_list.append(result_df)
    except:
        return "1"


    # 가져와졌는지 확인
    #print(f"dfList Size : {len(df_list)}")
    if len(df_list) == 0:
        return "1"

    # 가져온 리스트 전부 합치기
    merge_df = pd.concat(df_list, ignore_index=True)

    # 병합한 df들의 point_ratio 값을 Min-Max 정규화로 0~100 설정
    min_point = merge_df['point_ratio'].min()
    max_point = merge_df['point_ratio'].max()
    merge_df['normalize_ratio'] = (merge_df['point_ratio'] - min_point) / (max_point - min_point) * 100
    #print(merge_df)

    # 완성된 DataFrame을 딕셔너리 형태로 변환 후 wordcloud 생성
    wc_dict = merge_df.groupby('title')['normalize_ratio'].sum().to_dict()
    dp.create_wc_img(wc_dict, nowdate)

    # 차트 생성
    dp.create_chart_img(merge_df, nowdate)




    # 테이블에 보여줄 값 처리
    # Drop unnecessary columns and create the pivot table
    pivot_df = merge_df.drop(columns=["ratio", "point_ratio"]) \
        .pivot_table(index="title", columns="period", values="normalize_ratio", fill_value=0)

    # Reset index to ensure a clean table format
    pivot_df = pivot_df.reset_index()

    # Rename columns for better readability (optional)
    pivot_df.columns.name = None

    # 1. 'title'을 '대학명'으로 변경
    pivot_df = pivot_df.rename(columns={'title': '대학명'})

    # 2. 날짜 컬럼의 포맷을 변경 (2023-12-01 -> 23.12.01)
    pivot_df.columns = [col[2:4] + '.' + col[5:7] + '.' + col[8:10] if '-' in col else col for col in pivot_df.columns]

    # 3. 값들을 소수점 한 자리로 반올림
    pivot_df.iloc[:, 1:] = pivot_df.iloc[:, 1:].round(1)
    #print(pivot_df)

    # 엑셀 파일 저장
    excel_name = nowdate.split(".")[0] + ".xlsx"
    pivot_df.to_excel(rf"static/xlsx/{excel_name}", index=True)


    json_data = json.dumps({nowdate: pivot_df.to_dict(orient="records")}, ensure_ascii=False)
    return json_data



#test_keyword = ["서울대","고려대","연세대"]
#df1 = get_each_data(test_keyword, "2023-11-03", "2024-11-01", "month", "e")


