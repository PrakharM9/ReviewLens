import os
from openai import OpenAI

def generate_reply(product, review_text, summary):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is missing.")
    client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        temperature=0.4,
        messages=[
            {"role": "system", "content":
             "Write a short, polite, empathetic customer-service reply in English. "
             "Do not promise refunds, replacements, or actions that are not confirmed."},
            {"role": "user", "content":
             f"Product: {product}\nReview summary: {summary}\nCustomer review: {review_text}"}
        ]
    )
    return response.choices[0].message.content.strip()
