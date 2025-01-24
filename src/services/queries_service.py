import pandas as pd
import random
from src.services.sheets_service import *
from src.services.youtube_service import *
from src.ops.factory import mongo
from src.ops.etl import *

# Process randomly selected queries and store in MongoDB
def process_random_queries(category, queries, max_results):
    """ Select and process a random subset of queries and store the results in MongoDB """
    random_queries = random.sample(queries, min(max_results, len(queries)))
    all_results = []

    for query in random_queries:
        results = fetch_youtube_data(category, query, 10)  # Call YouTube API
        all_results.extend(results)  # Append results to the list
        
        # Store or update in MongoDB
        for video in results:
            update_query_results({'video_id': video['video_id']}, video)
    return all_results

# Generate query combinations and execute YouTube searches
def generate_and_search_queries():
    # Fetch data
    injury_df = fetch_csv_data('Injury Type')  # 'Injury Type' worksheet
    sports_df = fetch_csv_data('Sports Type')  # 'Sports Type' worksheet
    body_parts_df = fetch_csv_data('Body Part')  # 'Body Parts' worksheet

    sports_queries = {}
    # Create search queries
    for _, sport_row in sports_df.iterrows():
        queries = []
        for _, injury_row in injury_df.iterrows():
            for _, body_part_row in body_parts_df.iterrows():
                query = f"{body_part_row['Body Part']}+{injury_row['Injury Type']}+{sport_row['name']}+{injury_row['Description']}"
                queries.append(query)
        sports_queries[sport_row['name']] = queries
    return sports_queries

# Fetch the latest query results from MongoDB
def fetch_latest_query_results(num=5):
    try:
        return get_latest_query_results(num)
    except Exception as e:
        print("Fetching latest query results ", e.message)

# Get statistics about stored queries
def stats_query_results():
    docs = []
    result = get_documents()
    if result:
        for doc in result:
            docs.append(doc)
    else:
        print("No documents found.")
    return docs