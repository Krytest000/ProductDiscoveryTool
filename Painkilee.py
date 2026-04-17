import tkinter as tk
from tkinter import messagebox
from google_play_scraper import reviews
import json
import os
from datetime import datetime

# ====== CONFIG ======
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ====== FUNCTIONS ======

def fetch_reviews(app_id, count):
    result, _ = reviews(app_id, count=count)
    return result


def preprocess_reviews(reviews_data, only_negative=False):
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
            "user": r.get("userName")
        })

    return cleaned


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ====== MAIN ACTION ======

def run_pipeline():
    app_name = app_name_entry.get().strip()
    app_id = app_id_entry.get().strip()

    try:
        count = int(num_reviews_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid number of reviews")
        return

    only_negative = negative_var.get()

    if not app_name or not app_id:
        messagebox.showerror("Error", "Fill all fields")
        return

    status_label.config(text="Fetching reviews...")
    window.update()

    try:
        raw_reviews = fetch_reviews(app_id, count)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    timestamp = datetime.now().strftime("%Y-%m-%d")

    raw_path = f"{RAW_DIR}/{app_name}_{timestamp}.json"
    save_json(raw_reviews, raw_path)

    status_label.config(text="Preprocessing...")
    window.update()

    processed = preprocess_reviews(raw_reviews, only_negative)

    processed_path = f"{PROCESSED_DIR}/{app_name}_{timestamp}_cleaned.json"
    save_json(processed, processed_path)

    status_label.config(
        text=f"Done!\nRaw: {raw_path}\nProcessed: {processed_path}"
    )


# ====== UI ======

window = tk.Tk()
window.title("Review Scraper + AI Prep")
window.geometry("420x300")

# App name
tk.Label(window, text="App Name").pack()
app_name_entry = tk.Entry(window)
app_name_entry.pack()

# App ID
tk.Label(window, text="Google Play App ID").pack()
app_id_entry = tk.Entry(window)
app_id_entry.pack()

# Count
tk.Label(window, text="Number of Reviews").pack()
num_reviews_entry = tk.Entry(window)
num_reviews_entry.pack()

# Checkbox
negative_var = tk.BooleanVar()
tk.Checkbutton(window, text="Only negative (≤3★)", variable=negative_var).pack()

# Button
tk.Button(window, text="Run", command=run_pipeline).pack(pady=10)

# Status
status_label = tk.Label(window, text="")
status_label.pack()

window.mainloop()
