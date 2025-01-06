import pandas as pd
import random
from utils.sheets import *
from utils.youtube import *

def process_random_queries(queries, max_results):
    """ 여러 개의 쿼리 중 무작위로 선택된 일부 쿼리를 처리합니다. """
    # 무작위로 num_samples개의 쿼리 선택
    random_queries = random.sample(queries, min(max_results, len(queries)))
    all_results = []
    for query in random_queries:
        # print(f"Searching for: {query}")
        results = fetch_youtube_data(query)
        all_results.extend(results)  # 결과를 하나의 리스트에 추가
    return all_results

# 데이터 조합 및 YouTube 검색 실행
def generate_and_search_queries():
    # 데이터 가져오기
    injury_df = fetch_sheet_data('부상종류')  # '부상종류' 워크시트
    sports_df = fetch_sheet_data('운동종류')  # '운동종류' 워크시트
    body_parts_df = fetch_sheet_data('부상부위')  # '부상부위' 워크시트

    sports_queries = {}
    # 검색 쿼리 생성
    for _, sport_row in sports_df.iterrows():
        queries = []
        for _, injury_row in injury_df.iterrows():
            for _, body_part_row in body_parts_df.iterrows():
                query = f"{body_part_row['부위']}+{injury_row['부상종류']}+{sport_row['name']}+{injury_row['설명']}"
                queries.append(query)
        sports_queries[sport_row['name']]=queries
        

    return sports_queries