from flask import Flask, render_template, request, jsonify
from datetime import datetime
import naver_search_trend as nst
import naver_search as ns
import news as n
import db_control as dc
import ast
from dotenv import load_dotenv
import os
import json

app = Flask(__name__)


# Debug 모드 False 일시 로깅 시스템 작동
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    log_path = '/var/log/news.log'
    #log_path = 'C:\\filetest\\news.log'

    try:
        if not os.path.exists(log_path):
            with open(log_path, 'a'):
                os.utime(log_path, None)

        log_handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
        log_handler.setLevel(logging.INFO)
        app.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(asctime)s] Access From %(message)s  ',
            datefmt='%y.%m.%d %H:%M'
        )
        log_handler.setFormatter(formatter)
        app.logger.addHandler(log_handler)
    except Exception as e:
        print(f"사용중인 로그 파일: {log_path}...")
        print("현재 구동중인 OS 에 맞게 app.py를 수정하여 실행시켜주세요!")



# 요청에 대한 로그 저장
@app.after_request
def log_response(response):
    ip = ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    path = request.path
    method = request.method
    status_code = response.status_code
    app.logger.info(f'{ip} -> {method} {path} ({status_code})')
    return response



# 메인 화면
@app.route('/')
def index():
    result = dc.get_data_fromDB()
    return render_template('index.html', data=result)


# Naver 검색 빈도 추이 API Ajax
@app.route('/queryItem', methods=['POST'])
def query_item():
    #keywordList = ast.literal_eval(request.form["keywordList"])
    universityGroup = request.form["universityGroup"]
    startDate = request.form["startDate"]
    endDate = request.form["endDate"]
    timeUnit = request.form["timeUnit"]

    # 네이버 API 요청
    now_date = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    result = nst.get_each_data(universityGroup, startDate, endDate, timeUnit, now_date)
    return result


# 입학지도 iframe 내부 html
@app.route('/map')
def map_item():
    return render_template('2025_map.html')


# 입학지도 쿠키 지정 및 로그인 검증 route
@app.route('/validatePwd', methods=['POST'])
def validate_pwd():
    data = request.get_json()
    password = data.get("password")

    load_dotenv('env/data.env')
    map_key = str(os.getenv('map_key'))

    if password == map_key:
        response = jsonify({"success": True})
        # 쿠키에 'authenticated=true' 저장
        # 365일 -> 24시간 * 60분 * 60초 
        response.set_cookie("authenticated", "true", max_age=60 * 60 * 24* 365)  # 1년
        return response
    else:
        return jsonify({"success": False})















# trend페이지, search페이지 (XXX 폐기 XXX)
@app.route('/trend')
def home():
    return render_template('trend.html')
@app.route('/news')
def news():
    return render_template('news.html')
@app.route('/search')
def search():
    return render_template('search.html')
@app.route('/searchItem', methods=['POST'])
def search_item():
    search = request.form["search"]

    # 네이버 API 요청
    result = ns.search_item(search)
    return result
# 새로고침 시 뉴스 정보 재로딩 ( DB추가로 폐기 )
@app.route('/newsItem', methods=['POST'])
def news_item():
    #indexnum = request.form["indexnum"]
    # 크롤링 진행
    #result = n.news_data_crawling()
    result = n.module_exec()
    #print(result)
    return result
# 처음 화면 접속 시 DB로부터 받아온 뉴스 데이터 보여줌.(index에서 동시처리로 변경)
@app.route('/newsItemfromFile', methods=['POST'])
def news_item_from_db():
    #result = n.read_file_data()
    #return jsonify(result)
    result = dc.get_data_fromDB()
    return jsonify(result)



# 시작점. 배포 시 debug 옵션 False로 끌것!!
if __name__ == '__main__':
    #app.run('0.0.0.0', port=8081, debug=True)
    app.run('0.0.0.0', port=8081, debug=False)
