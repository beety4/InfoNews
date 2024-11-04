import os
import importlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


def load_and_execute(module_path):
    module = importlib.import_module(module_path)
    if hasattr(module, "get_data"):
        return module.get_data()
    return None


# 쓰레드 풀을 사용해 각 모듈의 get_data()를 동시에 실행
def news_data_crawling():
    all_data = []
    directory = "crawling"
    with ThreadPoolExecutor() as executor:
        futures = []
        for filename in os.listdir(directory):
            if filename.endswith(".py"):
                module_name = filename[:-3]
                module_path = f"{directory}.{module_name}"
                futures.append(executor.submit(load_and_execute, module_path))

        # 완료된 작업의 결과를 수집
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                all_data.append(result)

        print(all_data)
        return all_data


a = news_data_crawling()
json.loads(str(a))
print(a)
