import os
import importlib.util
import json
import threading
import queue
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


# 모듈 Import 및 실행 함수
def module_exec():
    #module_list = get_py_modules()
    module_list = ['crawling/10_unipress.py',
                        'crawling/12_yna.py', 'crawling/2_kcce.py',
                        'crawling/3_moe.py', 'crawling/4_incheon.py',
                        'crawling/5_veritas-a.py', 'crawling/6_unn.py',
                        'crawling/7_dhnews.py', 'crawling/8_usline.py',
                        'crawling/9_kyosu.py']

    th_list = []
    results_queue = queue.Queue()

    for module in module_list:
        spec = importlib.util.spec_from_file_location(module, module)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 3. 모듈 내 함수 호출
        # module.py 안에 있는 함수 이름을 호출
        #result = module.get_data()
        th = threading.Thread(target=lambda q, mod: q.put(mod.get_data()), args=(results_queue, module))
        th_list.append(th)

    # 3. 모든 쓰레드 시작
    for th in th_list:
        th.start()
        th.join()

    # 4. 모든 쓰레드 완료 대기
    for th in th_list:
        pass

    # 5. 결과 수집
    result = []
    while not results_queue.empty():
        result.append(results_queue.get())

    json_data = json.dumps(result, ensure_ascii=False, indent=4)
    return json_data
    #return result


#print(module_exec())