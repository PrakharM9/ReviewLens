# ReviewLens – AI Review Insights

ReviewLens is a Streamlit application that cleans customer-review CSV files, analyses review sentiment and topics with an LLM, caches results, and highlights reviews that need a response.

## Features
- CSV upload and validation; empty reviews are skipped and invalid/missing ratings become unknown.
- Duplicate review text is detected; duplicates reuse one analysis.
- LLM analysis returns sentiment, topics, an English summary, and `needs_reply`.
- Schema validation, one review-level validation retry, and exponential backoff for transient API errors.
- Batch processing (default 5 reviews per request).
- SHA-256 text cache stored locally in `data/cache.json`.
- Dashboard, product/sentiment/topic filters, and on-demand suggested replies.
- Bonus rating/sentiment agreement and basic AI/cache usage metrics.

## Setup
1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your own Groq API key:
   ```env
   GROQ_API_KEY=your_key_here
   ```
5. Run:
   ```bash
   streamlit run app.py
   ```
6. Upload `data/reviews.csv` in the browser.

Never commit `.env` or a real API key. The browser sends the CSV to the Streamlit server; only the server calls the LLM provider.

## Architecture
`app.py` handles the Streamlit interface. `csv_cleaner.py` validates and normalizes the uploaded table. `ai_analyzer.py` sends batches to the LLM and validates its responses. `cache_manager.py` stores successful analyses by SHA-256 hash of normalized review text. `dashboard.py` calculates and displays aggregate insights. `reply_generator.py` creates a suggested response only after the user clicks the button.

## Prompt and prompt-injection handling
The system prompt explicitly says review text is untrusted data, not instructions. It tells the model to ignore commands embedded in reviews, classify the customer's actual experience, and not let a star rating override the text. The review text is passed as JSON data in a user message, separate from the system instructions. Thus R012 should be classified as negative because the left earbud stopped working after two days, despite its embedded instruction.

## Tests
Run:
```bash
pytest -q
```
Tests cover CSV cleaning and duplicate detection, schema validation, and the one-retry failure path.

## Known limitations
- Cache is local to the machine running Streamlit; production deployment should use a persistent database.
- The demo uses one provider/model. Provider quotas and model availability may change.
- Topic counts are a simple aggregation of model-assigned topics, not a deeper clustering of free-text themes.
- A production system should add authentication, upload-size limits, structured logging, and stronger monitoring.
- The application has not been deployed publicly.

## AI coding tools
Document the tools you actually used and what you used them for before submission. Do not claim tools you did not use.

## Git history
Commit work in meaningful stages. Before submission, run:
```bash
git log --date=iso > gitlog.txt
git add gitlog.txt
git commit -m "Add git commit history"
git push
```
