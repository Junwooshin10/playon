from bson import ObjectId
from ops.factory import mongo


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