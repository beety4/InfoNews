from naver_api import NaverAPI
import pandas as pd
from scipy.stats import zscore
import data_process as dp

# 입력받은 키워드를 적절히 나누기 위해 2~5 사이의 원소를 가진 2차원 배열로 변환
def keyword_split(keyword_list, max_size=5, min_size=2):
    if len(keyword_list) <= 5:
        return [keyword_list]

    result = []
    temp = []

    for item in keyword_list:
        temp.append(item)

        if len(temp) == max_size or (
                len(keyword_list) - len(result) * max_size - len(temp) <= min_size and len(temp) >= min_size):
            result.append(temp)
            temp = []

    if len(temp) >= min_size:
        result.append(temp)

    return result




# 데이터 입력받은 뒤, naver_api를 사용하여 요청
def get_each_data(keyword_list, startDate, endDate, timeUnit, nowdate):
    each_keyword_list = keyword_split(keyword_list)

    try:
        api = NaverAPI()
        df_list = []
        for kl in each_keyword_list:
            result = api.access_keyword(kl, startDate, endDate, timeUnit)
            df_list.append(refresh_item(result))
    except:
        return "1"


    # 가져와졌는지 확인
    if len(df_list) == 0:
        return "1"

    # z-score 정규화
    merge_df = pd.concat(df_list, ignore_index=True)
    merge_df['z_score'] = zscore(merge_df['ratio'])
    #print(merge_df)

    # z-score 점수를 0~100 사이로 min-max 스케일링 적용
    z_min = merge_df['z_score'].min()
    z_max = merge_df['z_score'].max()
    merge_df['min_max'] = 100 * (merge_df['z_score'] - z_min) / (z_max - z_min)
    print(merge_df)


    # 완성된 DataFrame을 딕셔너리 형태로 변환 후 wordcloud 생성
    wc_dict = merge_df.groupby('title')['min_max'].sum().to_dict()
    dp.create_wc_img(wc_dict, nowdate)

    # 차트 생성
    dp.create_chart_img(merge_df, nowdate)

    return nowdate



# 데이터 가공 처리
def refresh_item(data):
    data_rows = []
    for result in data["results"]:
        title = result["title"]
        for item in result["data"]:
            data_rows.append({"title": title, "period": item["period"], "ratio": item["ratio"]})

    # DataFrame 생성
    df = pd.DataFrame(data_rows)
    df = df.sort_values('period')
    #print(df)
    return df



#test_keyword = ["서울대", "고려대", "연세대"]
#df1 = get_each_data(test_keyword, "2023-11-03", "2024-11-01", "month", "e")

