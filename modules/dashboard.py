from collections import Counter
import pandas as pd
import streamlit as st

def render_dashboard(df, usage, elapsed):
    analysed = df[df["analysis"].apply(lambda x: isinstance(x, dict))]
    total = len(analysed)
    counts = Counter(a["sentiment"] for a in analysed["analysis"])
    replies = sum(a["needs_reply"] for a in analysed["analysis"])
    positive = counts["positive"] / total * 100 if total else 0
    neutral = counts["neutral"] / total * 100 if total else 0
    negative = counts["negative"] / total * 100 if total else 0

    st.subheader("Overview")
    cols = st.columns(5)
    cols[0].metric("Reviews analysed", total)
    cols[1].metric("Positive", f"{positive:.1f}%")
    cols[2].metric("Neutral", f"{neutral:.1f}%")
    cols[3].metric("Negative", f"{negative:.1f}%")
    cols[4].metric("Needs reply", replies)

    st.subheader("What customers are saying")
    praise, complaints = Counter(), Counter()
    for a in analysed["analysis"]:
        target = praise if a["sentiment"] == "positive" else complaints if a["sentiment"] == "negative" else None
        if target is not None:
            target.update(a["topics"])
    left, right = st.columns(2)
    with left:
        st.markdown("**Top 3 praises**")
        for topic, count in praise.most_common(3):
            st.write(f"👍 {topic.replace('_', ' ').title()} — {count}")
        if not praise:
            st.caption("No positive themes yet.")
    with right:
        st.markdown("**Top 3 complaints**")
        for topic, count in complaints.most_common(3):
            st.write(f"⚠️ {topic.replace('_', ' ').title()} — {count}")
        if not complaints:
            st.caption("No negative themes yet.")

    # Bonus: rating/sentiment agreement, excluding unknown ratings and neutral reviews.
    comparable = [a for _, a in analysed.iterrows()
                  if a["rating"] is not None and pd.notna(a["rating"])
                  and a["analysis"]["sentiment"] in ("positive", "negative")]
    if comparable:
        matches = sum((r["rating"] >= 4 and r["analysis"]["sentiment"] == "positive") or
                      (r["rating"] <= 2 and r["analysis"]["sentiment"] == "negative")
                      for r in comparable)
        st.metric("Rating / sentiment agreement", f"{matches / len(comparable) * 100:.1f}%")

    st.caption(f'AI batch calls: {usage.get("ai_calls", 0)} · Cache hits: {usage.get("cache_hits", 0)} · '
               f'Failed: {usage.get("failed", 0)} · Processing time: {elapsed:.1f}s')
