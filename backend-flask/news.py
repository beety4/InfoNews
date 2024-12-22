import os
import importlib.util
import json
import threading
import queue
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import naver_search as ns


def load_and_run_get_data(py_file):
    spec = importlib.util.spec_from_file_location("module.name", py_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_data()  # get_data() 함수 실행 후 반환


# 쓰레드 풀을 사용해 각 모듈의 get_data()를 동시에 실행
def news_data_crawling():
    folder_path = 'crawling'  # crawling 폴더 경로
    data_list = []  # 최종 결과 리스트

    # 폴더 내 모든 파이썬 파일을 검색
    py_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.py')]

    # ThreadPoolExecutor로 각 파이썬 파일을 동시에 실행
    with ThreadPoolExecutor() as executor:
        # 각 파일에 대한 get_data() 함수를 실행하는 작업을 제출
        future_to_file = {executor.submit(load_and_run_get_data, py_file): py_file for py_file in py_files}

        # 결과 수집
        for future in as_completed(future_to_file):
            try:
                print(f"test : {future.result()[0]}")
                data_list.append(future.result())  # get_data() 반환 결과를 리스트에 추가
            except Exception as e:
                print(f"Error processing file {future_to_file[future]}: {e}")

    # JSON으로 변환 후 출력
    json_data = json.dumps(data_list, ensure_ascii=False, indent=4)
    return json_data
    #return data_list


def get_py_modules():
    directory = "crawling"
    py_files = [directory + "/" + str(f) for f in os.listdir(directory) if f.endswith('.py')]
    return py_files




## == 위 코드는 폐기 ==

# 모듈을 동적으로 로드하고 실행하는 함수
def load_and_run_module(module):
    try:
        # 모듈을 동적으로 불러옴
        spec = importlib.util.spec_from_file_location(module, module)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # 데이터 수집 후 반환
        value = mod.get_data()
        #print(f"Module {module} returned: {value}")  # 결과 로그 확인
        return value
    except Exception as e:
        print(f"Error in {module}: {e}")
        return f"Error in {module}: {e}"


# 모듈 Import 및 실행 함수
def module_exec():
    #module_list = get_py_modules()
    module_list = ['crawling/10_unipress.py', 'crawling/11_chosunedu.py',
                        'crawling/12_yna.py', 'crawling/2_kcce.py',
                        'crawling/3_moe.py', 'crawling/4_incheon.py',
                        'crawling/5_veritas-a.py', 'crawling/6_unn.py',
                        'crawling/7_dhnews.py', 'crawling/8_usline.py',
                        'crawling/9_kyosu.py']

    # 결과를 담을 리스트
    result = []

    # ProcessPoolExecutor로 멀티프로세싱
    with ProcessPoolExecutor() as executor:
        # `executor.map`으로 병렬 실행 결과를 직접 받아오기
        results = executor.map(load_and_run_module, module_list)

    # 결과를 리스트에 저장
    result.extend(results)


    # 네이버 검색 결과를 최상단에 삽입
    naver_search = ns.search_item_with_ai("인하공전", "인하공업전문대학")
    result.append(naver_search)


    order_list = ["네이버통합뉴스", "한국전문대학교육협의회", "교육부보도자료",
                  "인천광역시보도자료", "베리타스알파", "한국대학신문(UNN)",
                  "대학저널", "유스라인(Usline)", "교수신문",
                  "대학지성IN&OUT", "조선에듀", "연합뉴스"]

    sorted_list = sorted(
        (item for item in result if next(iter(item)) in order_list),  # order_list에 없는 값 필터링
        key=lambda x: order_list.index(next(iter(x)))
    )



    #print(sorted_list)
    # 결과를 JSON으로 반환
    json_data = json.dumps(sorted_list, ensure_ascii=False)
    return json_data


#print(module_exec())