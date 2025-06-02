from naver_api import NaverAPI
import pandas as pd

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


def refresh(lst):
    result = []

    # 매 3개씩 잘라서 ['compar', 'value', ...] 형태로 만듦
    for i in range(0, len(lst), 3):
        group = ['compare', 'value'] + lst[i:i + 3]
        result.append(group)

    return result

def create_df(data):
    rows = []
    for item in data['results']:
        title = item['title']
        for entry in item['data']:
            rows.append({'title': title, 'period': entry['period'], 'ratio': entry['ratio']})
    return pd.DataFrame(rows)


api = NaverAPI()
#kl = ["인하대", "인하공전"]
kl = ["고려대", "연세대", "서울대", "하늘","날다", "뭐든"]
startDate = "2024-11-02"
endDate = "2024-11-02"
timeUnit = "date"

aa = refresh(kl)
print(aa)

result = api.access_keyword(aa[0], startDate, endDate, timeUnit)


print(result)
print("=" * 25)
result2 = api.access_keyword(aa[1], startDate, endDate, timeUnit)
print(result2)

print("=" * 25)
result3 = api.access_keyword(["고려대", "날다"], startDate, endDate, timeUnit)
print(result3)



df1 = create_df(result)
df2 = create_df(result2)
df3 = create_df(result3)

print(df1)
print(df2)
print(df3)


print("=" * 40)
df1_w = 100 / df1.loc[0]['ratio']   # df1에서의 ratio 1점당 가중치 점수
df2_w = 100 / df2.loc[0]['ratio']   # df2에서의 ratio 1점당 가중치 점수
print(f"df1_w : {df1_w} // df2_w : {df2_w}")

df1_score = df1.loc[2]['ratio'] * df1_w     # 가중치를 사용한 새로운 점수 계산
df2_score = df2.loc[3]['ratio'] * df2_w     # 가중치를 사용한 새로운 점수 계산
print(f"df1_score : {df1_score} // df2_score : {df2_score}")

print(f"키워드 간의 비율 결과 : {df1_score / df2_score}")

print(f"실제 요청 결과 : {df3.loc[0]['ratio'] / df3.loc[1]['ratio']}")


print()
print("=" * 70)
print()

url = "https://cloudsearch.apigw.ntruss.com/CloudSearch/real/v1/domain/{name}/document/search/autocomplete"


