from flask import Flask, render_template, request
from datetime import datetime
import naver_search_trend as nst
import naver_search as ns
import news as n
import ast

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/queryItem', methods=['POST'])
def query_item():
    keywordList = ast.literal_eval(request.form["keywordList"])
    startDate = request.form["startDate"]
    endDate = request.form["endDate"]
    timeUnit = request.form["timeUnit"]

    # 네이버 API 요청
    now_date = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    result = nst.get_each_data(keywordList, startDate, endDate, timeUnit, now_date)
    return result


@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/searchItem', methods=['POST'])
def search_item():
    search = request.form["search"]

    # 네이버 API 요청
    result = ns.search_news(search)
    return result



@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/newsItem', methods=['POST'])
def news_item():
    # 크롤링 진행
    result = n.news_data_crawling()
    return result



if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
