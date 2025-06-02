import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import importlib
import naver_search as ns
import json
from collections import defaultdict
from dateutil.parser import parse
import smtplib
from email.mime.text import MIMEText


# sourceIDX 와 뉴스 정보 매칭
source_map = {
    "네이버통합뉴스(인하공전)": 1,
    "네이버통합뉴스(인하대)": 2,
    "네이버통합뉴스(항공대)": 3,
    "한국전문대학교육협의회": 4,
    "교육부보도자료": 5,
    "인천광역시보도자료": 6,
    "베리타스알파": 7,
    "한국대학신문(UNN)": 8,
    "대학저널": 9,
    "유스라인(Usline)": 10,
    "교수신문": 11,
    "대학지성IN&OUT": 12,
    "조선에듀": 13,
    "연합뉴스": 14,
    "경인일보": 15,
    "인천일보": 16
}




# PostgreSQL 로의 커넥션 반환
def get_connection():
    load_dotenv('env/data.env')
    conn = psycopg2.connect(
        host=str(os.getenv('dbhost')),
        database=str(os.getenv('dbname')),
        user=str(os.getenv('dbuser')),
        password=str(os.getenv('dbpass')),
        port=5432
    )

    return conn


# 크롤링 모듈 로드
def load_modules():
    crawler_funcs = []
    crawler_dir = 'crawling'

    # 크롤링 코드 실행
    for filename in os.listdir(crawler_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # .py 제거
            module = importlib.import_module(f'{crawler_dir}.{module_name}')
            if hasattr(module, 'get_data'):
                crawler_funcs.append(module.get_data)

    # 네이버 결과 추가
    keyword_list = ['인하공전', '인하대', '항공대']
    for keyword in keyword_list:
        crawler_funcs.append(lambda k=keyword: ns.search_item(k))
        
    return crawler_funcs



# 데이터 DB에 저장
def save_data_toDB():
    # DB에 받아온 데이터 삽입 하는 SQL
    insert_query = """
            INSERT INTO newsinfo (sourceIDX, title, date, link) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (link) DO NOTHING;
        """
    # 마지막으로 크로링 시도한 날짜로 업데이트 하는 SQL
    update_attempt_query = """
            UPDATE source
            SET last_attempt = %s
            WHERE sourceIDX = %s;
        """
    # 마지막으로 크롤링 결과가 성공한 날짜로 업데이트 하는 SQL
    update_success_query = """
            UPDATE source
            SET status = 'Success',
                last_success = %s,
                message = NULL
            WHERE sourceIDX = %s;
        """
    # 크롤링 업데이트 실패 시 상태를 변경하는 SQL
    update_fail_query = """
            UPDATE source
            SET status = 'Fail',
                message = %s
            WHERE sourceIDX = %s;
        """

    # 전체 수집 및 삽입
    conn = get_connection()
    cur = conn.cursor()
    crawler_funcs = load_modules()
    now = datetime.now()
    for crawl in crawler_funcs:
        data_dict = crawl()

        for source_name, articles in data_dict.items():
            sourceIDX = source_map.get(source_name)

            # last_attempt 업데이트
            cur.execute(update_attempt_query, (now, sourceIDX))

            # 에러 처리: dict가 {"Error": code} 형식이면 실패 처리
            if isinstance(articles, list) and articles and articles[0] == "Error":
                cur.execute(update_fail_query, (str(articles), sourceIDX))
                continue


            try:
                for article in articles:
                    cur.execute(insert_query, (
                        sourceIDX,
                        article["title"],
                        article["date"],
                        article["link"]
                    ))
                # 크로링 성공 시 status 업데이트
                cur.execute(update_success_query, (now, sourceIDX))

            except Exception as e:
                #print(f"Error inserting: {article.get('title', 'Unknown')}", e)
                cur.execute(update_fail_query, (str(e), sourceIDX))

    conn.commit()
    cur.close()
    conn.close()

    #print("==Data Input Success!! (postgresql)")
    return


# 데이터 DB로 부터 가져오기
def get_data_fromDB():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT *
    FROM (
        SELECT 
            s.name AS source_name,
            n.title,
            n.link,
            TO_CHAR(n.date, 'MM.DD') AS date,
            ROW_NUMBER() OVER (PARTITION BY s.sourceIDX ORDER BY n.date DESC) AS rn
        FROM newsinfo n
        JOIN source s ON n.sourceIDX = s.sourceIDX
    ) sub
    WHERE rn <= 10
    ORDER BY source_name, date DESC;
    """)

    rows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    # defaultdict으로 그룹화
    result = defaultdict(list)
    for source_name, title, link, date, _ in rows:
        result[source_name].append({
            "title": title,
            "link": link,
            "date": date
        })

    # 원하는 JSON 구조로 변환 및 정렬
    order_list = ["네이버통합뉴스(인하공전)", "네이버통합뉴스(인하대)", "네이버통합뉴스(항공대)",
                  "한국전문대학교육협의회", "교육부보도자료", "인천광역시보도자료",
                  "베리타스알파", "한국대학신문(UNN)", "대학저널",
                  "유스라인(Usline)", "교수신문", "대학지성IN&OUT",
                  "조선에듀", "경인일보", "인천일보", "연합뉴스"]

    final_json = [
        {source: result[source]} for source in order_list if source in result
    ]

    #print(json.dumps(final_json, indent=2, ensure_ascii=False))
    #return final_json

    crawling_result = check_crawling() if check_crawling() else ""
    json_data = json.dumps([crawling_result, final_json], ensure_ascii=False)
    return json_data




# 크롤링 실패 여부 확인
def check_crawling():
    conn = get_connection()
    cur = conn.cursor()

    query = """
       SELECT name, status, last_attempt, last_success, message
       FROM source
       WHERE status = 'Fail' OR
         (last_attempt IS NOT NULL
         AND last_success IS NOT NULL
         AND last_attempt != last_success);
       """

    try:
        cur.execute(query)
        failed_data = cur.fetchall()
        result = []

        if failed_data:
            for row in failed_data:
                dict_data = {"name": row[0], "status": row[1], "last_attempt": str(row[2]), "last_success": str(row[3]), "message": row[4]}
                result.append(dict_data)
        else:
            #print("모든 데이터가 성공적으로 크롤링되었습니다.")
            return None
        return result
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        cur.close()
        conn.close()




# 하루 지정 시간 2번 검사 후, 메일 보내기
def send_mail():
    # 크롤링 검증 확인 및 메일 내용 작성
    result = check_crawling()
    if result:
        mailText = f'''
                <html>
                <body>
                <h2>실패한 크롤링 데이터</h2>
                <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
                    <tr>
                        <th>뉴스이름</th>
                        <th>크롤링 상태</th>
                        <th>마지막 시도</th>
                        <th>마지막 성공</th>
                        <th>오류메세지</th>
                    </tr>
                '''
        # result 리스트의 데이터를 HTML 테이블로 변환
        for row in result:
            mailText += f"""
                    <tr>
                       <td>{row["name"]}</td>
                       <td>{row["status"]}</td>
                       <td>{str(row["last_attempt"]).split('.')[0]}</td>
                       <td>{str(row["last_success"]).split('.')[0]}</td>
                       <td>{row["message"]}</td>
                   </tr>
                   """
        mailText += """
                </table>
                </body>
                </html>
                """

        # 메일 정보 가져오기
        load_dotenv()
        mail_sender = os.getenv("mailsender")
        mail_list = os.getenv("maillist").split(",")
        mail_key = os.getenv("mailkey")

        # 메일 설정
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(mail_sender, mail_key)

        msg = MIMEText(mailText, 'html')
        msg['Subject'] = '인하공전 뉴스 크롤링 실패 알림'
        s.sendmail(mail_sender, mail_list, msg.as_string())
        s.quit()
    # else:
    # print("크롤링 잘됨.")








# 입학지도 Map코드
def getSigunguPos(sigunguname):
    return









# Cron으로 저장할때 사용
if __name__ == "__main__":
    # 현재 크롤링 저장
    save_data_toDB()

    # 현재 시간이 해당 시간 범위(8:10~8:30, 19:10~19:30 사이)
    now = datetime.now()
    morning_start = now.replace(hour=8, minute=10, second=0, microsecond=0)
    morning_end = now.replace(hour=8, minute=30, second=0, microsecond=0)
    evening_start = now.replace(hour=19, minute=10, second=0, microsecond=0)
    evening_end = now.replace(hour=19, minute=30, second=0, microsecond=0)

    if morning_start <= now <= morning_end or evening_start <= now <= evening_end:
        send_mail()

    #get_data_fromDB()


