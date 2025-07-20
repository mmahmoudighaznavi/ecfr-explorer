from fastapi import FastAPI, Query
from typing import List
from fastapi.responses import JSONResponse
import pandas as pd
import re
import hashlib
from textstat import flesch_kincaid_grade

app = FastAPI(title="eCFR API", version="2.0")

# --- Load and Clean eCFR Data ---
df = pd.read_csv("data/ecfr_chunks_all_titles.csv")

if 'part_text' in df.columns:
    df.rename(columns={'part_text': 'text'}, inplace=True)

if "title" not in df.columns or df["title"].isnull().all():
    df["title"] = df["source_file"].str.extract(r"title-(\d+)", expand=False).astype("Int64")

if 'word_count' not in df.columns:
    df['word_count'] = df['text'].astype(str).str.split().str.len()

# --- Routes ---

@app.get("/")
def read_root():
    return {"message": "eCFR API is running."}

@app.get("/search")
def search_chunks(query: str, title: int = Query(None, description="Optional title number")):
    filtered_df = df[df['text'].str.contains(query, case=False, na=False)]
    if title is not None:
        filtered_df = filtered_df[filtered_df['title'] == title]
    return filtered_df[["title", "part_title", "authority", "text"]].to_dict(orient="records")

@app.get("/stats/wordcount")
def word_count_stats():
    stats = df.groupby("title")['word_count'].sum().reset_index()
    return stats.sort_values(by="word_count", ascending=False).to_dict(orient="records")

@app.get("/stats/by-authority")
def word_count_by_authority():
    if "authority" not in df.columns:
        return {"error": "No 'authority' column in dataset."}
    return df.groupby("authority")["word_count"].sum().reset_index()\
             .sort_values(by="word_count", ascending=False).to_dict(orient="records")

@app.get("/titles", response_model=List[int])
def list_titles():
    return sorted(df["title"].dropna().unique().tolist())

@app.get("/checksum/{authority}")
def checksum_by_authority(authority: str):
    subset = df[df['authority'] == authority]
    full_text = " ".join(subset['text'].dropna().astype(str).tolist())
    checksum = hashlib.sha256(full_text.encode('utf-8')).hexdigest()
    return {"authority": authority, "checksum": checksum}

@app.get("/history/{title}")
def simulate_history(title: int):
    simulated = [
        {"date": "2021-01-01", "word_count": 10000 + title * 50},
        {"date": "2022-01-01", "word_count": 10200 + title * 50},
        {"date": "2023-01-01", "word_count": 10450 + title * 50},
        {"date": "2024-01-01", "word_count": 10600 + title * 50}
    ]
    return {"title": title, "history": simulated}

# --- ✅ FIXED Readability by Authority ---
@app.get("/stats/custom-readability")
def readability_by_authority():
    try:
        # Ensure necessary columns
        if 'text' not in df.columns or 'authority' not in df.columns:
            return JSONResponse(status_code=500, content={"error": "Missing required columns."})

        # Drop NaN and ensure text is string
        valid_df = df.dropna(subset=["text", "authority"]).copy()
        valid_df["text"] = valid_df["text"].astype(str)

        if valid_df.empty:
            return JSONResponse(status_code=200, content=[])

        # Compute readability safely
        def safe_grade(text):
            try:
                return flesch_kincaid_grade(text)
            except Exception:
                return None

        valid_df["readability"] = valid_df["text"].apply(safe_grade)
        valid_df = valid_df.dropna(subset=["readability"])

        if valid_df.empty:
            return JSONResponse(status_code=200, content=[])

        result = valid_df.groupby("authority")["readability"].mean().reset_index()
        return result.sort_values(by="readability").to_dict(orient="records")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
