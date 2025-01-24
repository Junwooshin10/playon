from bson import ObjectId
from src.ops.factory import mongo
import pandas as pd
import re
from src.services.sheets_service import *
import datetime

def update_query_results(key: dict, update_data):
    """Update document""" 
    result = mongo.db.query_results.update_one(
        key,
        {"$set": update_data},
        upsert=True  # Insert if not exists (update + insert)
    )
    return result.modified_count

# Retrieve documents by category (sports)
def get_document_by_sport(sport, num=8):
    """Retrieve documents by category"""
    return mongo.db.query_results.find({"category": sport}).limit(num)

# Retrieve document by ID
def get_document_by_id(doc_id):
    """Retrieve document by ID"""
    return mongo.db.query_results.find_one({"_id": ObjectId(doc_id)})

# Retrieve all documents
def get_documents():
    """Retrieve all documents"""
    return mongo.db.query_results.find()

def get_latest_query_results(num=5):
    """Fetch the latest 5 documents from MongoDB based on published_at"""
    docs = (mongo.db.query_results
            .find()
            .sort("published_at", -1)  # Sort by published_at descending
            .limit(num))               # Limit to 5 documents
    return list(docs)

def tokenize_title(title: str):
    """
    Preprocess the title string,
    split by spaces and return as a list
    """
    # 1) Convert to lowercase
    title = title.lower()
    # 2) Keep only alphabets/numbers/Korean characters/spaces using regex
    title = re.sub(r'[^0-9a-zA-Z가-힣\s+]', '', title)
    # 3) Split by spaces
    return title.split()

def etl():
    # Create keyword lists
    injurys = fetch_csv_data("Injury Type")
    sports = fetch_csv_data("Sports Type")
    body_parts = fetch_csv_data("Body Part")

    injury_keywords = injurys['Injury Type'].tolist()
    sports_keywords = sports['name'].tolist()
    body_parts_keywords = body_parts['Body Part'].tolist()

    # Retrieve MongoDB data and convert to DataFrame
    collection = mongo.db.query_results
    result = collection.find()
    docs = list(result)

    if not docs:
        print("No documents found.")
        return pd.DataFrame()

    df = pd.DataFrame(docs)

    # Extract data from keywords and titles
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

    # Merge extracted data
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

# Format published_at date function
def format_published_at(data):
    for item in data:
        try:
            # Parse the original published_at value
            original_date = datetime.datetime.strptime(item['published_at'], "%Y-%m-%dT%H:%M:%SZ")
            # Convert to new format (e.g., 'YYYY-MM-DD HH:MM:SS')
            item['published_at'] = original_date.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            print(f"Error parsing date for {item['_id']}: {e}")
    return data

def prepare_pie_chart_data(df_exploded_inj_body):
    """
    Calculate injury types and their frequency from the given DataFrame,
    and group those with less than 20% frequency as 'Others'.
    """
    # Count frequency by injury type
    body_injury_counts = df_exploded_inj_body.groupby(['body_part_injury']).size().reset_index(name='count')
    
    # Calculate total count
    total_count = body_injury_counts['count'].sum()

    # Calculate percentage
    body_injury_counts['percentage'] = body_injury_counts['count'] / total_count * 100

    # Group as 'Others' if frequency is less than 5%
    grouped = body_injury_counts.copy()
    grouped.loc[grouped['percentage'] < 5, 'body_part_injury'] = 'Others'
    
    # Aggregate including 'Others'
    grouped = grouped.groupby('body_part_injury', as_index=False).agg({
        'count': 'sum',
        'percentage': 'sum'
    }).sort_values(by='count', ascending=False)

    # Format data for Chart.js
    pie_chart_data = {
        'labels': grouped['body_part_injury'].tolist(),
        'datasets': [{
            'data': grouped['count'].tolist(),
            'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF']
        }]
    }
    return pie_chart_data