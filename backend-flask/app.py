from flask import Flask, render_template, request
from datetime import datetime
import naver_api as na
import data_process as wc

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/queryItem', methods=['POST'])
def query_item():
    search = request.form["value1"]


    # 네이버 API 요청
    param = {'startDate': '', 'endDate': '', 'timeUnit': '',
             'keywordGroups': '', 'keywordGroups.groupName': '',
             'keywordGroups.keywords': ''}
    #search_result = na.access_API(param)



    # 각종 신문사에서 크롤링 데이터




    # 워드클라우드 이미지 생성
    dict_data = {
        '워드클라우드': 1965,
        '테스트': 1666,
        '인하공전': 955,
        '메세지': 855,
        '워드': 841,
        '클라우드': 612,
        '파이썬': 598,
        '모죽': 576,
        '최고': 542,
        '인공': 487,
        '우와': 412,
        '한번 더': 401,
        '좋아요': 397,
        '쟝고': 391,
        '플라스크': 308,
        '셀레니움': 284,
        '크롤링': 255,
        '뉴스': 231,
        '대학': 175,
        '자바스크립트': 152,
        '스프링': 109,
        '부트': 71
    }

    now_date = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    wc.create_img(dict_data, now_date)



    # 최종 출력
    #return render_template('index.html', img=now_date)
    return now_date


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
