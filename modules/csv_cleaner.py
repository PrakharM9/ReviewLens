import pandas as pd

REQUIRED_COLUMNS = {"review_id", "product", "rating", "date", "review_text"}

def clean_reviews(df: pd.DataFrame):
    """Validate columns, remove empty text and flag repeated review text."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

    uploaded = len(df)
    df["review_text"] = df["review_text"].astype(str).str.strip()
    df["rating"] = df["rating"].astype(str).str.strip()
    df["rating"] = df["rating"].apply(
        lambda value: int(value) if value.isdigit() and 1 <= int(value) <= 5 else None
    )
    empty_mask = df["review_text"].eq("") | df["review_text"].str.lower().eq("nan")
    empty_count = int(empty_mask.sum())
    df = df.loc[~empty_mask].copy().reset_index(drop=True)

    # Hashing is performed on normalized text; duplicates remain visible but are analysed once.
    df["_normalized_text"] = df["review_text"].str.lower().str.replace(r"\s+", " ", regex=True)
    df["is_duplicate"] = df["_normalized_text"].duplicated(keep="first")
    first_ids = {}
    duplicate_of = []
    for _, row in df.iterrows():
        key = row["_normalized_text"]
        duplicate_of.append(first_ids.get(key, ""))
        first_ids.setdefault(key, row["review_id"])
    df["duplicate_of"] = duplicate_of

    stats = {
        "uploaded": uploaded,
        "valid": len(df),
        "empty": empty_count,
        "duplicates": int(df["is_duplicate"].sum()),
    }
    return df, stats
