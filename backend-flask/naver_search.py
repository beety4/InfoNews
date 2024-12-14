from datetime import datetime
from naver_api import NaverAPI
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time
from datetime import datetime

# need pip
# pip install scikit-learn numpy

def search_item(search, target_count=20):
    api = NaverAPI()
    result_lst = []
    start = 1

    while len(result_lst) < target_count:
        result = api.search_news(search, start=start)

        # 검색 실패 시 종료
        if not result:
            #print("API에서 결과를 받지 못했습니다.")
            break

        # 데이터 전처리
        for item in result['items']:
            title = item['title']
            link = item['link']
            date_str = item['pubDate']

            # HTML 인코딩 및 태그 제거
            title = title.replace("&quot;", '"').replace("&amp;", '&').replace("<b>", "").replace("</b>", "")

            # 제목에 검색어가 포함된 뉴스만 추가
            if search in title:
                date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                date = date_obj.strftime('%Y.%m.%#d')

                temp_dict = {"title": title, "link": link, "date": date}
                result_lst.append(temp_dict)

                # print(f"제목: {title}")
                # print(f"링크: {link}")
                # print(f"날짜: {date}")
                # print("-" * 100)

                # 목표 개수에 도달하면 종료
                if len(result_lst) >= target_count:
                    break

        # `start` 위치를 다음 100개로 이동
        start += 100

        # 네이버 API의 결과가 더 이상 없을 경우 종료
        if len(result['items']) < 100:
            break

    return result_lst


def sort_by_date(data):
    # 날짜 형식 정의
    date_format = "%Y.%m.%d"

    # 데이터를 'date' 기준으로 정렬
    sorted_data = sorted(data, key=lambda x: datetime.strptime(x['date'], date_format), reverse=True)

    return sorted_data


def search_item_with_ai(keyword1, keyword2, threshold=0.8):
    result1 = search_item(keyword1)
    result2 = search_item(keyword2)
    result = result1 + result2
    result = sort_by_date(result)

    #print(result1)
    #print(result2)

    # 제목만 분리
    titles = [entry['title'] for entry in result]


    # TfidfVectorizer를 사용하여 제목들의 TF-IDF 벡터화
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(titles)

    # 제목들 간의 Cosine Similarity 계산
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # 중복을 제거할 제목들
    to_drop = set()

    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            # 두 제목의 유사도가 threshold 이상이면 하나를 제거
            if cosine_sim[i][j] > threshold:
                to_drop.add(j)

    # 유사도가 높은 제목들을 제외한 리스트 반환
    filtered_titles = [title for i, title in enumerate(result) if i not in to_drop]
    #print(result)
    #print(filtered_titles)

    return filtered_titles

