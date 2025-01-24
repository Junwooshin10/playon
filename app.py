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
# 3) Flask Routes
#-----------------------------------
@app.route('/')
def main_dashboard():
    """
    Main Dashboard
    """
    mongo.db.command("ping")
    print("MongoDB Atlas connection successful")
    
    # (1) Sports categories
    # Generate keyword list
    sports = fetch_csv_data("Sports Type")
    sports_categories = sports.to_dict(orient="records")

    # (2) New data notifications (Example: Latest 8 YouTube videos)
    new_injuries_data = get_latest_query_results(num=8)
    new_injuries = format_published_at(new_injuries_data)

    # (3) Retrieve injury data from Google Sheets and process if needed
    injuries = fetch_csv_data("Injury Type")
    sheet_injury_data = injuries['Injury Type'].tolist()

    df = etl()

    df_exploded_inj = df.explode('all_injuries').dropna(subset=['all_injuries'])
    df_exploded_sports = df.explode('all_sports').dropna(subset=['all_sports'])
    df_exploded_body_parts = df.explode('all_body_parts').dropna(subset=['all_body_parts'])
    
    # Common injury list
    df_exploded_inj_body = pd.merge(
            df_exploded_body_parts[['all_body_parts', '_id']],
            df_exploded_inj[['all_injuries', '_id']],
            on='_id'
        )
    body_injury_counts = df_exploded_inj_body.groupby(['all_body_parts', 'all_injuries']).size().reset_index(name='count')
    top_body_injury_counts = body_injury_counts.sort_values(by='count', ascending=False).head(8)
    injuryChartData = top_body_injury_counts.to_dict(orient='records')
    df_exploded_inj_body['body_part_injury'] = df_exploded_inj_body['all_body_parts'] + ' ' + df_exploded_inj_body['all_injuries']
    pie_chart_data = prepare_pie_chart_data(df_exploded_inj_body)

    # Injury list by sport 
    # Merge data
    df_exploded = pd.merge(
        pd.merge(
            df_exploded_sports[['all_sports', '_id']],
            df_exploded_inj[['all_injuries', '_id']],
            on='_id'
        ),
        df_exploded_body_parts[['all_body_parts', '_id']],
        on='_id'
    )

    # Group and calculate frequencies
    sport_injury_body_counts = df_exploded.groupby(['all_sports', 'all_injuries', 'all_body_parts']).size().reset_index(name='count')

    # Sort by frequency and select top 8
    top_sport_injury_body_counts = sport_injury_body_counts.sort_values(by='count', ascending=False).head(8)
    
    # Convert data to desired format
    sportInjuryList = top_sport_injury_body_counts.rename(columns={
        'all_sports': 'sport', 
        'all_injuries': 'injury', 
        'all_body_parts': 'body_part'
    }).to_dict(orient='records')

    return render_template(
        'index.html',
        injuryChartData=injuryChartData,
        sportInjuryList=sportInjuryList,
        sports_categories=sports_categories,
        new_injuries=new_injuries,
        sheet_injury_data=sheet_injury_data,
        pie_chart_data=pie_chart_data
    )

@app.route('/save', methods=['POST']) 
def save_queries():
    # Process and store data for each sport
    for sport, queries in default_queries.items():
        process_random_queries(sport, queries, max_results=5)  # Call save logic
    return "Data saved successfully"

@app.route('/search', methods=['GET'])
def search_injuries():
    """
    Search processing:
    - Receive query via ?q=ankle
    - Filter results by injury name, sport type, or body part
    - Render the results page
    """
    query = request.args.get('q', '').strip()

    if not query:
        return render_template('search_result.html', query="", results=[])

    # Example: Simple search from injury type sheet
    # Actual implementation may use DB LIKE/REGEX search
    records = fetch_csv_data('Injury Type')
    filtered = [
        r for r in records 
        if (query.lower() in r.get('Injury Type', '').lower()
            or query.lower() in r.get('Sport', '').lower())
    ]

    return render_template('search_result.html', query=query, results=filtered)

@app.route('/category/<sport_name>')
def show_sport_category(sport_name):
    # 1) Generate query list for the sport
    # 2) Search YouTube with the query list
    # 3) Display search results
    
    injuries_data = list(get_document_by_sport(sport_name, 5))
    injuries = format_published_at(injuries_data)
    
    return render_template(
        'category.html',
        sport_name=sport_name,
        injuries=injuries
    )

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)