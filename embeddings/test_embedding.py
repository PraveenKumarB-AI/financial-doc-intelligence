from embeddings.embedding_generator import generate_embedding

embedding = generate_embedding(
    "Apple reported strong revenue growth."
)

print("Dimension:", len(embedding))
print("First 5 values:", embedding[:5])
