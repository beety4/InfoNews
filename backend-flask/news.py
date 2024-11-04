import os
import importlib.util
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


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
                data_list.append(future.result())  # get_data() 반환 결과를 리스트에 추가
            except Exception as e:
                print(f"Error processing file {future_to_file[future]}: {e}")

    # JSON으로 변환 후 출력
    json_data = json.dumps(data_list, ensure_ascii=False, indent=4)
    return json_data
    #return data_list


