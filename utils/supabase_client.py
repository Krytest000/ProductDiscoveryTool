import os
from supabase import create_client, Client

_client = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]
        _client = create_client(url, key)
    return _client


def save_reviews(reviews: list[dict], app_name: str, app_id: str, fetched_at: str) -> None:
    client = get_client()
    rows = [
        {
            "app_name": app_name,
            "app_id": app_id,
            "fetched_at": fetched_at,
            "text": r["text"],
            "rating": r["rating"],
            "likes": r["likes"],
            "review_date": r["date"],
            "user_name": r["user"],
        }
        for r in reviews
    ]
    client.table("reviews").insert(rows).execute()
