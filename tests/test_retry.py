from unittest.mock import patch
import pandas as pd
from modules.ai_analyzer import _analyse_single_retry

def test_invalid_response_retries_once_then_fails():
    row = type("Row", (), {"review_id": "R1", "product": "P",
                           "rating": 1, "review_text": "Broken"})()
    with patch("modules.ai_analyzer._request_batch", return_value=[{"bad": "json"}]) as mocked:
        assert _analyse_single_retry(row) is None
        assert mocked.call_count == 2
