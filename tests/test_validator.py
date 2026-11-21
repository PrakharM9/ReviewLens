import pytest
from modules.validator import validate_analysis

def test_valid_analysis_passes():
    item = {"sentiment": "negative", "topics": ["quality"],
            "summary": "The earbud stopped working after two days.",
            "needs_reply": True}
    assert validate_analysis(item) == item

def test_invalid_sentiment_fails():
    item = {"sentiment": "excellent", "topics": ["quality"],
            "summary": "Good.", "needs_reply": False}
    with pytest.raises(ValueError):
        validate_analysis(item)
