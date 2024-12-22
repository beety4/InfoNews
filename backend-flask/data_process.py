import numpy as np
from matplotlib import cm
from wordcloud import WordCloud
import matplotlib
import matplotlib.pyplot as plt


# wordcloud 이미지 생성 및 저장
def create_wc_img(dict_data, file_name):
    wordcloud = WordCloud(
        font_path="./malgun.ttf",
        #font_path="malgun",
        width=1400,
        height=1400,
        max_font_size=400,
        background_color="white",
        margin=2,
        prefer_horizontal=0.6,
        collocations=False,
        colormap='plasma'
    ).generate_from_frequencies(dict_data)

    matplotlib.use('Agg')
    plt.figure(figsize=(14,14))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    #plt.show()

    # 로컬에 파일 저장
    plt.savefig(rf"static/wc-img/{file_name}", dpi=200, bbox_inches='tight', pad_inches=0)


# 차트 이미지 생성 및 저장
def create_chart_imgs(df, file_name):
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
    plt.savefig(rf"static//chart-img//{file_name}")  # 이미지 경로 설정
    #plt.show()



def create_chart_img(df, file_name):
    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False

    # 고유한 title에 따라 색상 및 스타일 설정
    unique_titles = df['title'].unique()
    colors = cm.tab10(np.linspace(0, 1, len(unique_titles)))
    line_styles = ['-', '--', '-.', ':']

    # 차트 생성
    fig, ax = plt.subplots(figsize=(15, 9))
    for idx, (title, group) in enumerate(df.groupby('title')):
        color = colors[idx % len(colors)]
        linestyle = line_styles[idx % len(line_styles)]

        # "인하공전" 강조 설정
        if title == "인하공전":
            color = 'blue'  # 강조 색상
            linestyle = '-'  # 강조 선 스타일
            linewidth = 2.5  # 선 굵기
            marker = 'o'  # 강조 마커
            alpha = 1.0  # 강조 투명도
        else:
            linewidth = 1.0  # 기본 선 굵기
            marker = 'x'  # 기본 마커
            alpha = 1.0  # 기본 투명도

        plt.plot(
            group['period'],
            group['normalize_ratio'],
            label=title,
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            marker=marker,
            alpha=alpha
        )

    # 그래프 제목, 축 레이블, 범례 등 설정
    ax.set_title("키워드 별 검색 빈도 수 추이", fontsize=18)
    ax.set_xlabel("날짜", fontsize=14)
    ax.set_ylabel("검색 빈도 수", fontsize=14)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=12)
    ax.legend(title="키워드 항목", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)    # 차트 영역 테두리 설정 (검정색)

    for spine in ax.spines.values():
        spine.set_edgecolor('black')  # 테두리 색을 검정색으로 설정
        spine.set_linewidth(1)  # 테두리 두께를 1로 설정    # 전체 figure 테두리 설정

    fig.patch.set_edgecolor('black')  # 전체 figure의 테두리 색상
    fig.patch.set_linewidth(2)  # 전체 figure의 테두리 두께
    fig.patch.set_facecolor('white')  # figure 배경 색상을 흰색으로 설정    # 차트 이미지 저장
    plt.tight_layout()  # 레이아웃을 조정하여 요소들이 잘리지 않도록 함


    # 차트 이미지 저장
    plt.savefig(rf"static/chart-img/{file_name}", dpi=200)  # 이미지 경로 설정