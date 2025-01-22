from bson import ObjectId
from src.ops.factory import mongo
import pandas as pd
import re
from src.services.sheets_service import *
import datetime

def update_query_results(key:dict, update_data):
    """문서 업데이트""" 
    result = mongo.db.query_results.update_one( 
       key,
        {"$set": update_data},
        upsert=True  # 없으면 삽입 update + insert
    )
    return result.modified_count

# 카테고리(sports) 기준으로 문서 조회
def get_document_by_sport(sport, num=8):
    """문서 조회"""
    return mongo.db.query_results.find({"category": sport}).limit(num)

# Id 기준으로 문서 조회
def get_document_by_id(doc_id):
    """문서 조회"""
    return mongo.db.query_results.find_one({"_id": ObjectId(doc_id)})

# 전체 문서
def get_documents():
    """문서 조회"""
    return mongo.db.query_results.find()

def get_latest_query_results(num=5):
    """MongoDB에서 published_at 기준으로 최신 5개 문서를 가져오는 함수"""
    docs = (mongo.db.query_results
            .find()
            .sort("published_at", -1)  # createdAt 기준 내림차순
            .limit(num))              # 5개만 조회
    return list(docs)

def tokenize_title(title: str):
    """
    title 문자열을 간단히 전처리한 뒤,
    띄어쓰기 단위로 쪼개서 리스트로 반환
    """
    # 1) 모두 소문자로
    title = title.lower()
    # 2) 알파벳/한글/숫자/기타문자만 남기고 제거 (예: 정규식)
    title = re.sub(r'[^0-9a-zA-Z가-힣\s+]', '', title)
    # 3) 띄어쓰기로 split
    return title.split()

def etl():
    # 키워드 리스트 생성
    injurys = fetch_csv_data("부상종류")
    sports = fetch_csv_data("운동종류")
    body_parts = fetch_csv_data("부상부위")

    injury_keywords = injurys['부상종류'].tolist()
    sports_keywords = sports['name'].tolist()
    body_parts_keywords = body_parts['부위'].tolist()

    # MongoDB 데이터를 가져와 DataFrame으로 변환
    collection = mongo.db.query_results
    result = collection.find()
    docs = list(result)

    if not docs:
        print("No documents found.")
        return pd.DataFrame()

    df = pd.DataFrame(docs)

    # 키워드 및 제목에서 데이터 추출
    df['keyword_list'] = df['keyword'].astype(str).apply(lambda x: x.split('+'))
    df['injuries'] = df['keyword_list'].apply(lambda words: [w for w in words if w in injury_keywords])
    df['sports'] = df['keyword_list'].apply(lambda words: [w for w in words if w in sports_keywords])
    df['body_parts'] = df['keyword_list'].apply(lambda words: [w for w in words if w in body_parts_keywords])

    def extract_injuries_from_title(title_words):
        return [w for w in title_words if w in injury_keywords]

    def extract_sports_from_title(title_words):
        return [w for w in title_words if w in sports_keywords]

    def extract_body_parts_from_title(title_words):
        return [w for w in title_words if w in body_parts_keywords]

    df['title_keywords'] = df['title'].astype(str).apply(tokenize_title)
    df['title_injuries'] = df['title_keywords'].apply(extract_injuries_from_title)
    df['title_sports'] = df['title_keywords'].apply(extract_sports_from_title)
    df['title_body_parts'] = df['title_keywords'].apply(extract_body_parts_from_title)

    # 병합된 데이터
    df['all_injuries'] = df.apply(
        lambda row: list(set(row['injuries'] + row['title_injuries'])),
        axis=1
    )
    df['all_sports'] = df.apply(
        lambda row: list(set(row['sports'] + row['title_sports'])),
        axis=1
    )
    df['all_body_parts'] = df.apply(
        lambda row: list(set(row['body_parts'] + row['title_body_parts'])),
        axis=1
    )
    return df

# published_at 포맷팅 함수
def format_published_at(data):
    for item in data:
        try:
            # 기존 published_at 값을 파싱
            original_date = datetime.datetime.strptime(item['published_at'], "%Y-%m-%dT%H:%M:%SZ")
            # 새로운 포맷으로 변환 (예: 'YYYY-MM-DD HH:MM:SS')
            item['published_at'] = original_date.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            print(f"Error parsing date for {item['_id']}: {e}")
    return data

import pandas as pd

def prepare_pie_chart_data(df_exploded_inj_body):
    """
    주어진 데이터프레임에서 부상과 빈도수를 계산하고,
    빈도수가 전체의 20% 미만인 것을 기타로 묶어서 반환.
    """
    # 부상 종류별로 빈도 계산
    body_injury_counts = df_exploded_inj_body.groupby(['body_part_injury']).size().reset_index(name='count')
    
    # 전체 빈도 합계
    total_count = body_injury_counts['count'].sum()

    # 전체 대비 비율 계산
    body_injury_counts['percentage'] = body_injury_counts['count'] / total_count * 100

    # 기타로 그룹화 (20% 미만인 항목)
    grouped = body_injury_counts.copy()
    grouped.loc[grouped['percentage'] < 5, 'body_part_injury'] = '기타'
    
    # 기타 포함하여 그룹 재집계
    grouped = grouped.groupby('body_part_injury', as_index=False).agg({
        'count': 'sum',
        'percentage': 'sum'
    }).sort_values(by='count', ascending=False)

    # Chart.js용 데이터 포맷
    pie_chart_data = {
        'labels': grouped['body_part_injury'].tolist(),
        'datasets': [{
            'data': grouped['count'].tolist(),
            'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF']
        }]
    }
    return pie_chart_data