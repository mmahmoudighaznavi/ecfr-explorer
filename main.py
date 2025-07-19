from fastapi import FastAPI, Query
import pandas as pd
import re

app = FastAPI(title="eCFR API", version="1.0")

# Load the CSV file once at startup
df = pd.read_csv("data/ecfr_chunks_all_titles.csv")

# Print available columns to verify the structure
print("Columns in CSV:", list(df.columns))

# Rename 'part_text' to 'text' for consistency (only if it exists)
if 'part_text' in df.columns:
    df.rename(columns={'part_text': 'text'}, inplace=True)

# Extract 'title' from 'source_file' if 'title' column is missing or has nulls
if "title" not in df.columns or df["title"].isnull().all():
    df["title"] = df["source_file"].str.extract(r"title-(\d+)", expand=False).astype("Int64")

# Ensure 'word_count' column exists
if 'word_count' not in df.columns:
    df['word_count'] = df['text'].str.split().str.len()

@app.get("/")
def read_root():
    return {"message": "eCFR API is running."}

@app.get("/search")
def search_chunks(
    query: str = Query(..., description="Keyword to search for"),
    title: int = Query(None, description="Optional Title number")
):
    # Filter by query
    filtered_df = df[df['text'].str.contains(query, case=False, na=False)]
    
    # Optional filter by title number
    if title is not None:
        filtered_df = filtered_df[filtered_df['title'] == title]

    # Return selected fields
    results = filtered_df[["title", "part_title", "authority", "text"]].to_dict(orient="records")
    return results

@app.get("/stats/wordcount")
def word_count_stats():
    # Group total word count by title
    stats = df.groupby("title")['word_count'].sum().reset_index()
    stats = stats.sort_values(by="word_count", ascending=False)
    return stats.to_dict(orient="records")

@app.get("/stats/by-authority")
def word_count_by_authority():
    if "authority" not in df.columns:
        return {"error": "No 'authority' column in dataset."}

    # Group word counts by authority
    authority_stats = (
        df.groupby("authority")["word_count"]
        .sum()
        .reset_index()
        .sort_values(by="word_count", ascending=False)
        .to_dict(orient="records")
    )
    return authority_stats
