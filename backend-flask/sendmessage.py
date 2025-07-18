import requests
import os
import sys
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error



# DB 커넥션 가져오기
def get_db_connection():
    try:
        load_dotenv('./env/db.env')
        db_config = {
            'host': os.getenv('nDBDB_HOST'),
            'user': os.getenv('nDBDB_USER'),
            'password': os.getenv('nDBDB_PASSWORD'),
            'database': os.getenv('nDBDB_DATABASE'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_general_ci',
            'connection_timeout': 10
        }

        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None



# DB로부터 elearning 사용자 정보 전부 가져오기
def get_token_fromdb():
    query = """
            SELECT t.tokenvalue
            FROM token AS t
            JOIN userinfo AS ui ON t.tokenIDX = ui.tokenIDX
            WHERE ui.type = 'news.mojuk.kr';
            """

    conn = None
    cursor = None
    tokens = []
    try:
        conn = get_db_connection()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        tokens = [item[0] for item in results]

        print(f"성공: 총 {len(tokens)}개의 토큰을 조회했습니다.")
    except Error as e:
        print(f"데이터 조회 중 오류 발생: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return tokens



# 원하는 사용자(token)에게 title,message로 알림 보내기
def send_fcm_notification(token, title, message):
    url = "https://mojuk.kr/notifyplus/sendmsg"

    payload = {
        'token': token,
        'title': title,
        'message': message,
        'servicekey': os.getenv('nDBDB_SERVICEKEY')
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        return True
    except requests.exceptions.RequestException as e:
        # 네트워크 오류 또는 HTTP 오류 처리
        #print(f"요청 실패: {e}")
        #if e.response is not None:
        #    print(f"서버 응답: {e.response.text}")
        return False



# 외부 -> send_to_admin 요청 함수
def send_to_admin(message):
    tokens = get_token_fromdb()

    for token in tokens:
        send_fcm_notification(token, "[뉴스 크롤링 실패 알림]", message)

    print(f"{len(tokens)}개 : 전달을 완료하였습니다!")