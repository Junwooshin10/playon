#######################
# app.py
#######################
from flask import Flask, render_template, request, jsonify
from pandas import DataFrame
import plotly.express as px
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()
from utils.sheets import *
from utils.youtube import *
from utils.helps import *


app = Flask(__name__)
default_queries = generate_and_search_queries()
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

#-----------------------------------
# 3) Flask 라우트
#-----------------------------------
@app.route('/')
def main_dashboard():
    """
    메인 대시보드:
    - 카테고리(스포츠) 목록
    - 검색창
    - 요약 카드(새로운 데이터, 오늘의 팁, 인기 부상 사례)
    - YouTube API 결과(필요 시)
    - Google Sheets 결과(필요 시)
    """
    mongo.db.command("ping")
    print("MongoDB Atlas 연결 성공")
    # (1) 스포츠 카테고리
    sports_categories = fetch_sports_types_from_sheet()

    # (2) 새로운 데이터 알림 (예시로 YouTube 최신 영상 5개)
    # 실제론 부상 사례 DB로부터 '최신 등록 순' 불러올 수도 있음
    # queries = list(default_queries.values())
    new_injuries = []
    for sport, queries in default_queries.items():
        result = process_random_queries(queries=queries, max_results=5)
        new_injuries.extend(result)
    # # (3) 구글 시트에서 불상종류/데이터를 가져와서 필요 시 가공
    sheet_injury_data = fetch_injury_types_from_sheet()

    return render_template(
        'index.html',
        sports_categories=sports_categories,
        new_injuries=new_injuries,
        sheet_injury_data=sheet_injury_data
    )

@app.route('/save', methods=['POST'])
def save_results():
    """YouTube 검색 결과를 MongoDB에 여러 개 저장 및 업데이트"""
    data = request.json  # 요청에서 JSON 데이터를 가져옴
    if not data or not isinstance(data, list):
        return jsonify({"error": "Invalid data format. Provide a list of items"}), 400

    try:
        for video in data:
            # `video_id`를 기준으로 업데이트 또는 삽입
            mongo.db.youtube_results.update_many(
                {'video_id': video['video_id']},  # 업데이트 조건
                {'$set': video},  # 업데이트할 데이터
                upsert=True  # 없으면 새로 삽입
            )
        return jsonify({"message": f"{len(data)} items processed successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_injuries():
    """
    검색 처리:
    - ?q=발목 형태로 검색어 받음
    - 부상 이름, 스포츠 종류, 신체 부위 등에 대해 필터링
    - 결과 페이지 렌더링
    """
    query = request.args.get('q', '').strip()

    if not query:
        return render_template('search_result.html', query="", results=[])
    # 예: 부상종류 시트에서 가져와서 간단 검색
    # 실제로는 DB에서 LIKE/REGEX 로 검색 가능
    records = fetch_injury_types_from_sheet()
    filtered = [
        r for r in records 
        if (query.lower() in r.get('부상명', '').lower()
            or query.lower() in r.get('스포츠', '').lower())
    ]

    return render_template('search_result.html', query=query, results=filtered)


@app.route('/category/<sport_name>')
def show_sport_category(sport_name):
    # 1) 스포츠에 해당하는 쿼리 리스트를 생성
    # 2) 쿼리 리스트를 가지고 youtube에 검색
    # 3) 검색 결과를 보여주기
    # records = fetch_injury_types_from_sheet()
    # print(records)
    # injuries = [r for r in records if r.get('스포츠') == sport_name]

    injuries = process_random_queries(default_queries[sport_name], 5)

    return render_template(
        'category.html',
        sport_name=sport_name,
        injuries=injuries
    )


# Flask 실행
if __name__ == '__main__':
    app.run(debug=True, port=5000)