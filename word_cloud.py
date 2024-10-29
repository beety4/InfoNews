from wordcloud import WordCloud
import matplotlib.pyplot as plt


# 데이터 전처리 함수
def data_for_dict(data):
    pass


# wordcloud 이미지 생성 및 저장
def create_img(dict_data, file_name):
    wordcloud = WordCloud(
        font_path="malgun",
        width=800,
        height=400,
        max_font_size=100,
        colormap="Blues",
        background_color="white",
    ).generate_from_frequencies(dict_data)

    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    #plt.show()

    # 로컬에 파일 저장
    plt.savefig(f"static/wc-img/{file_name}")

