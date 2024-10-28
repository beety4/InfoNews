from flask import Flask, render_template, request
import naver_api as na

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/queryItem', methods=['POST'])
def query_item():
    given_item = request.args.get('value1')
    print(given_item)


    # 네이버 API 요청
    param = {'startDate': '', 'endDate': '', 'timeUnit': '',
             'keywordGroups': '', 'keywordGroups.groupName': '',
             'keywordGroups.keywords': ''}
    search_result = na.access_API(param)



    # 각종 신문사에서 크롤링 데이터




    # 워드클라우드 이미지 생성





    # 최종 출력

    return render_template('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
