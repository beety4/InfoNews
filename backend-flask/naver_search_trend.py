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

    print(result)
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
def get_each_data(keyword_list, startDate, endDate, timeUnit, nowdate):
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
    if len(df_list) == 0:
        return "1"

    # 가져온 리스트 전부 합치기
    merge_df = pd.concat(df_list, ignore_index=True)

    # 병합한 df들의 point_ratio 값을 Min-Max 정규화로 0~100 설정
    min_point = merge_df['point_ratio'].min()
    max_point = merge_df['point_ratio'].max()
    merge_df['normalize_ratio'] = (merge_df['point_ratio'] - min_point) / (max_point - min_point) * 100
    print(merge_df)

    # 완성된 DataFrame을 딕셔너리 형태로 변환 후 wordcloud 생성
    wc_dict = merge_df.groupby('title')['normalize_ratio'].sum().to_dict()
    dp.create_wc_img(wc_dict, nowdate)

    # 차트 생성
    dp.create_chart_img(merge_df, nowdate)

    return nowdate



#test_keyword = ["서울대","고려대","연세대"]
#df1 = get_each_data(test_keyword, "2023-11-03", "2024-11-01", "month", "e")


