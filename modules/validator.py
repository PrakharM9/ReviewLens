ALLOWED_SENTIMENTS = {"positive", "neutral", "negative"}
ALLOWED_TOPICS = {"quality", "delivery", "price", "packaging", "support", "size_fit", "other"}
REQUIRED_KEYS = {"sentiment", "topics", "summary", "needs_reply"}

def validate_analysis(data):
    if not isinstance(data, dict) or set(data.keys()) != REQUIRED_KEYS:
        raise ValueError("Response must contain exactly sentiment, topics, summary, needs_reply.")
    if data["sentiment"] not in ALLOWED_SENTIMENTS:
        raise ValueError("Invalid sentiment.")
    if not isinstance(data["topics"], list) or not data["topics"]:
        raise ValueError("Topics must be a non-empty list.")
    if any(topic not in ALLOWED_TOPICS for topic in data["topics"]):
        raise ValueError("Invalid topic.")
    if not isinstance(data["summary"], str) or not data["summary"].strip():
        raise ValueError("Summary must be a non-empty English sentence.")
    if not isinstance(data["needs_reply"], bool):
        raise ValueError("needs_reply must be boolean.")
    return data
