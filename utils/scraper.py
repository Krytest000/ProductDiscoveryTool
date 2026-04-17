import json
import os
from datetime import datetime
from google_play_scraper import reviews as gp_reviews

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def fetch_reviews(app_id: str, count: int) -> list:
    result, _ = gp_reviews(app_id, count=count)
    return result


def preprocess_reviews(reviews_data: list, only_negative: bool = False) -> list:
    cleaned = []
    for r in reviews_data:
        text = r.get("content", "")
        if len(text) < 50:
            continue
        if only_negative and r.get("score", 5) > 3:
            continue
        cleaned.append({
            "text": text,
            "rating": r.get("score"),
            "likes": r.get("thumbsUpCount"),
            "date": str(r.get("at")),
            "user": r.get("userName"),
        })
    return cleaned


def save_json(data: list, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_scrape(app_name: str, app_id: str, count: int, only_negative: bool) -> tuple[list, str, str]:
    """Fetch, preprocess, and persist reviews. Returns (processed, raw_path, processed_path)."""
    raw = fetch_reviews(app_id, count)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    raw_path = f"{RAW_DIR}/{app_name}_{timestamp}.json"
    save_json(raw, raw_path)

    processed = preprocess_reviews(raw, only_negative)
    processed_path = f"{PROCESSED_DIR}/{app_name}_{timestamp}_cleaned.json"
    save_json(processed, processed_path)

    return processed, raw_path, processed_path
