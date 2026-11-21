import pandas as pd
from modules.csv_cleaner import clean_reviews

def test_empty_rating_and_duplicate_handling():
    df = pd.DataFrame([
        ["1", "P", "5", "2026-01-01", "Nice product"],
        ["2", "P", "", "2026-01-02", "Nice product"],
        ["3", "P", "five", "2026-01-03", "   "],
    ], columns=["review_id", "product", "rating", "date", "review_text"])
    cleaned, stats = clean_reviews(df)
    assert len(cleaned) == 2
    assert pd.isna(cleaned.iloc[1]["rating"])
    assert cleaned.iloc[1]["is_duplicate"]
    assert stats["empty"] == 1
