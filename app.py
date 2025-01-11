#######################
# app.py
#######################
from flask import render_template, request
from src.services.sheets_service import *
from src.services.youtube_service import *
from src.services.queries_service import *
from src.ops.factory import create_app, mongo
from dotenv import load_dotenv

load_dotenv()

app = create_app()
default_queries = generate_and_search_queries()

#-----------------------------------
# 3) Flask 라우트
#-----------------------------------
@app.route('/')
def main_dashboard():
    """
    메인 대시보드
    """
    mongo.db.command("ping")
    print("MongoDB Atlas 연결 성공")
    # (1) 스포츠 카테고리
    sports_categories = fetch_sports_types_from_sheet()

    # (2) 새로운 데이터 알림 (예시로 YouTube 최신 영상 5개)
    new_injuries = get_latest_query_results(num=8)

    
    # (3) 구글 시트에서 부상종류/데이터를 가져와서 필요 시 가공
    sheet_injury_data = fetch_injury_types_from_sheet()
    df = etl()
    df_exploded_inj = df.explode('all_injuries').dropna(subset=['all_injuries'])
    injury_counts_series = df_exploded_inj['all_injuries'].value_counts()
    injuryChartData = injury_counts_series.reset_index().to_dict(orient='records')

    df_exploded_sports = df.explode('all_sports').dropna(subset=['all_sports'])
    # 스포츠와 부상 데이터 병합
    df_exploded = pd.merge(
        df_exploded_sports[['all_sports', '_id']], 
        df_exploded_inj[['all_injuries', '_id']],
        on='_id'
    )
    # 그룹화하여 빈도 계산
    sport_injury_counts = df_exploded.groupby(['all_sports', 'all_injuries']).size().reset_index(name='count')
    # 빈도수 기준으로 정렬하여 상위 5개 선택
    top_sport_injury_counts = sport_injury_counts.sort_values(by='count', ascending=False).head(8)
    # 원하는 형태로 데이터 변환
    sportInjuryList = top_sport_injury_counts.rename(columns={
        'all_sports': 'sport', 
        'all_injuries': 'injury'
    }).to_dict(orient='records')

    return render_template(
        'index.html',
        injuryChartData=injuryChartData,
        sportInjuryList=sportInjuryList,
        sports_categories=sports_categories,
        new_injuries=new_injuries,
        sheet_injury_data=sheet_injury_data
    )

@app.route('/save', methods=['POST']) 
def save_queries():
    # 각 스포츠별 데이터 처리 및 저장
    for sport, queries in default_queries.items():
        process_random_queries(sport, queries, max_results=5)  # 저장 로직 호출
    return "Data saved successfully"

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

    injuries = get_document_by_sport(sport_name, 5)
    print(injuries)
    return render_template(
        'category.html',
        sport_name=sport_name,
        injuries=injuries
    )


# Flask 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)