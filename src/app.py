#######################
# app.py
#######################
from flask import Flask, render_template, request
from pandas import DataFrame
import plotly.express as px
from dotenv import load_dotenv
load_dotenv()

from utils.sheets import *
from utils.youtube import *
from utils.helps import *


app = Flask(__name__)
default_queries = generate_and_search_queries()
print(default_queries)
# generate_and_search_queries()
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
    # (1) 스포츠 카테고리
    sports_categories = fetch_sports_types_from_sheet()
    
    # (2) 인기 부상 사례
    popular_injuries = [
        {"title": "전방 십자인대 파열(ACL)", "desc": "무릎에 흔히 발생하는 심각한 부상"},
        {"title": "발목 염좌", "desc": "점프 착지 시 자주 발생"},
        {"title": "어깨 회전근개 파열", "desc": "과도한 스윙 동작에서 자주 발생"}
    ]

    # (3) 오늘의 팁 (1개만 노출 예시)
    tip_of_the_day = "운동 전후에 충분한 워밍업과 쿨다운을 하세요."

    # (4) 새로운 데이터 알림 (예시로 YouTube 최신 영상 5개)
    # 실제론 부상 사례 DB로부터 '최신 등록 순' 불러올 수도 있음
    new_injuries = process_random_queries(queries=default_queries, max_results=5)
    # (5) 구글 시트에서 불상종류/데이터를 가져와서 필요 시 가공
    sheet_injury_data = fetch_injury_types_from_sheet()

    return render_template(
        'index.html',
        sports_categories=sports_categories,
        popular_injuries=popular_injuries,
        tip_of_the_day=tip_of_the_day,
        new_injuries=new_injuries,
        sheet_injury_data=sheet_injury_data
    )


@app.route('/search', methods=['GET'])
def search_injuries():
    """
    검색 처리:
    - ?q=발목 형태로 검색어 받음
    - 부상 이름, 스포츠 종류, 신체 부위 등에 대해 필터링
    - 결과 페이지 렌더링
    """
    query = request.args.get('q', '').strip()
    print("query", query)

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
    records = fetch_injury_types_from_sheet()
    injuries = [r for r in records if r.get('스포츠') == sport_name]

    return render_template(
        'category.html',
        sport_name=sport_name,
        injuries=injuries
    )


# Flask 실행
if __name__ == '__main__':
    app.run(debug=True, port=5000)