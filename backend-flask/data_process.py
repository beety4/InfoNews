from wordcloud import WordCloud
import matplotlib
import matplotlib.pyplot as plt


# wordcloud 이미지 생성 및 저장
def create_wc_img(dict_data, file_name):
    wordcloud = WordCloud(
        #font_path="./malgun.ttf",
        font_path="malgun",
        width=800,
        height=400,
        max_font_size=100,
        background_color="white",
    ).generate_from_frequencies(dict_data)

    matplotlib.use('Agg')
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    #plt.show()

    # 로컬에 파일 저장
    plt.savefig(f"static/wc-img/{file_name}")


# 차트 이미지 생성 및 저장
def create_chart_img(df, file_name):
    matplotlib.use('Agg')

    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False

    # 차트 생성
    plt.figure(figsize=(10, 7))

    # title 별로 선 그래프를 그림
    for title, group in df.groupby('title'):
        plt.plot(group['period'], group['normalize_ratio'], marker='o', label=title)

    plt.title("키워드 별 검색 빈도 수 추이")
    plt.xlabel("날짜")
    plt.ylabel("검색 빈도 수")
    plt.xticks(rotation=45)
    plt.legend(title="키워드 항목")
    plt.grid(True)

    # 이미지 저장
    plt.savefig(f"static/chart-img/{file_name}")  # 이미지 경로 설정
    #plt.show()

