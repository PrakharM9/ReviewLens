import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from modules.csv_cleaner import clean_reviews
from modules.ai_analyzer import analyze_reviews
from modules.cache_manager import load_cache, save_cache
from modules.dashboard import render_dashboard
from modules.reply_generator import generate_reply

load_dotenv()
st.set_page_config(page_title="ReviewLens | AI Review Insights", page_icon="🔎", layout="wide")

st.title("🔎 ReviewLens")
st.caption("Turn customer reviews into practical product insights.")

with st.sidebar:
    st.header("Analysis settings")
    batch_size = st.select_slider("Reviews per AI batch", options=[1, 2, 3, 5], value=5)
    st.caption("The API key is read by the server from your environment.")

uploaded = st.file_uploader("Upload a reviews CSV file", type=["csv"])
if uploaded:
    try:
        raw_df = pd.read_csv(uploaded, dtype=str, keep_default_na=False)
        cleaned_df, cleaning_stats = clean_reviews(raw_df)
    except Exception as exc:
        st.error(f"Could not read this CSV: {exc}")
        st.stop()

    st.subheader("Data quality")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows uploaded", cleaning_stats["uploaded"])
    c2.metric("Valid reviews", cleaning_stats["valid"])
    c3.metric("Empty reviews skipped", cleaning_stats["empty"])
    c4.metric("Duplicate texts", cleaning_stats["duplicates"])

    if cleaned_df.empty:
        st.warning("No non-empty reviews were found.")
        st.stop()

    if st.button("✨ Analyse reviews", type="primary"):
        cache = load_cache()
        progress = st.progress(0, text="Preparing reviews...")
        status = st.empty()
        start = time.time()
        results, usage = analyze_reviews(cleaned_df, cache, batch_size=batch_size,
                                         progress=progress, status=status)
        save_cache(cache)
        results["analysis_status"] = results["analysis"].apply(
            lambda x: "analysis_failed" if not isinstance(x, dict) else "analysed"
        )
        st.session_state["review_results"] = results
        st.session_state["usage"] = usage
        st.session_state["elapsed"] = time.time() - start
        st.rerun()

if "review_results" in st.session_state:
    results = st.session_state["review_results"].copy()
    usage = st.session_state.get("usage", {})
    st.divider()
    render_dashboard(results, usage, st.session_state.get("elapsed", 0))

    st.subheader("Review details")
    products = ["All"] + sorted(results["product"].dropna().unique().tolist())
    sentiments = ["All", "positive", "neutral", "negative", "analysis_failed"]
    topics = ["All"] + sorted({topic for a in results["analysis"] if isinstance(a, dict)
                               for topic in a.get("topics", [])})
    f1, f2, f3 = st.columns(3)
    product_filter = f1.selectbox("Product", products)
    sentiment_filter = f2.selectbox("Sentiment", sentiments)
    topic_filter = f3.selectbox("Topic", topics)

    filtered = results.copy()
    if product_filter != "All":
        filtered = filtered[filtered["product"] == product_filter]
    if sentiment_filter != "All":
        if sentiment_filter == "analysis_failed":
            filtered = filtered[filtered["analysis"].apply(lambda x: not isinstance(x, dict))]
        else:
            filtered = filtered[filtered["analysis"].apply(
                lambda x: isinstance(x, dict) and x["sentiment"] == sentiment_filter)]
    if topic_filter != "All":
        filtered = filtered[filtered["analysis"].apply(
            lambda x: isinstance(x, dict) and topic_filter in x["topics"])]

    display_rows = []
    for _, row in filtered.iterrows():
        a = row["analysis"] if isinstance(row["analysis"], dict) else {}
        display_rows.append({
            "Review ID": row["review_id"], "Product": row["product"],
            "Rating": row["rating"] or "Unknown",
            "Sentiment": a.get("sentiment", "analysis_failed"),
            "Topics": ", ".join(a.get("topics", [])),
            "Summary": a.get("summary", "Analysis unavailable"),
            "Needs reply": a.get("needs_reply", False),
            "Duplicate": bool(row.get("is_duplicate", False))
        })
    st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)

    st.subheader("Suggested replies")
    reply_rows = filtered[filtered["analysis"].apply(
        lambda x: isinstance(x, dict) and x.get("needs_reply") is True)]
    if reply_rows.empty:
        st.info("No filtered reviews currently require a reply.")
    else:
        for _, row in reply_rows.iterrows():
            a = row["analysis"]
            with st.expander(f'{row["review_id"]} · {row["product"]}'):
                st.write(row["review_text"])
                if st.button("Generate suggested reply", key=f'reply_{row["review_id"]}'):
                    with st.spinner("Drafting a reply..."):
                        try:
                            st.session_state[f'reply_text_{row["review_id"]}'] = generate_reply(
                                row["product"], row["review_text"], a["summary"])
                        except Exception as exc:
                            st.error(str(exc))
                reply = st.session_state.get(f'reply_text_{row["review_id"]}')
                if reply:
                    st.text_area("Suggested reply (edit before sending)", reply,
                                 key=f'edit_reply_{row["review_id"]}', height=120)
else:
    st.info("Upload the provided reviews.csv file, then select **Analyse reviews**.")
