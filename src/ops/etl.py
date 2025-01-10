from bson import ObjectId
from ops.factory import mongo
import pandas as pd
import re
from services.sheets_service import *

def update_query_results(key:dict, update_data):
    """문서 업데이트"""
    result = mongo.db.query_results.update_one(
       key,
        {"$set": update_data},
        upsert=True  # 없으면 삽입
    )
    return result.modified_count

def get_document_by_id(doc_id):
    """문서 조회"""
    return mongo.db.query_results.find_one({"_id": ObjectId(doc_id)})

def get_latest_query_results(num=5):
    """MongoDB에서 createdAt 기준으로 최신 5개 문서를 가져오는 함수"""
    docs = (mongo.db.query_results
            .find()
            .sort("published_at", -1)  # createdAt 기준 내림차순
            .limit(num))              # 5개만 조회
    return list(docs)

def get_documents():
    """문서 조회"""
    return mongo.db.query_results.find()

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
    injurys = fetch_injury_types_from_sheet()
    sports = fetch_sports_types_from_sheet()

    injury_keywords = []
    for i in injurys:
        injury_keywords.append((i['부상종류']))

    sports_keywords = []
    for i in sports:
        sports_keywords.append((i['name']))

    # collection to dataframe
    collection = mongo.db.query_results
    result = collection.find()
    docs = []
    if result:
        for doc in result:
            docs.append(doc)
    else:
        print("No documents found.")

    df = pd.DataFrame(docs)

    df['keyword_list'] = df['keyword'].astype(str).apply(lambda x: x.split('+'))
    df['injuries'] = df['keyword_list'].apply(lambda words: [w for w in words if w in injury_keywords])
    df['sports'] = df['keyword_list'].apply(lambda words: [w for w in words if w in sports_keywords])
    
    def extract_injuries_from_title(title_words):
        return [w for w in title_words if w in injury_keywords]

    def extract_sports_from_title(title_words):
        return [w for w in title_words if w in sports_keywords]

    df['title_keywords'] = df['title'].astype(str).apply(tokenize_title)
    df['title_injuries'] = df['title_keywords'].apply(extract_injuries_from_title)
    df['title_sports'] = df['title_keywords'].apply(extract_sports_from_title)

    df['all_injuries'] = df.apply(
        lambda row: list(set(row['injuries'] + row['title_injuries'])),
        axis=1
    )
    df['all_sports'] = df.apply(
        lambda row: list(set(row['sports'] + row['title_sports'])),
        axis=1
    )
    return df


