import cohere

# Ganti ini dengan API key milikmu dari https://dashboard.cohere.com/
api_key = "ZxELwDf2Y8W0jxQTVhg7UFTJ3dMl5tuaJ9FfS2Un"
co = cohere.Client(api_key)

response = co.generate(
    model="command",  # atau "command", "command-light"
    prompt="Jelaskan apa itu RAG (Retrieval-Augmented Generation) dalam AI.",
    max_tokens=100
)

print(response)
