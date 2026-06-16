from embeddings.embedding_generator import generate_embedding
from vectorstore.database import get_connection


def search(query, company=None):
    """
    Vector-search document_chunks for the most relevant chunks.
    If company is provided (e.g. 'Microsoft Corporation'), search
    only that company's chunks. Otherwise search all.
    """
    conn = get_connection()
    cursor = conn.cursor()
    embedding = str(generate_embedding(query))

    if company:
        cursor.execute(
            """
            SELECT chunk_text,
                   embedding <=> %s::vector AS distance
            FROM document_chunks
            WHERE company = %s
            ORDER BY distance
            LIMIT 5
            """,
            (embedding, company),
        )
    else:
        cursor.execute(
            """
            SELECT chunk_text,
                   embedding <=> %s::vector AS distance
            FROM document_chunks
            ORDER BY distance
            LIMIT 5
            """,
            (embedding,),
        )

    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


if __name__ == "__main__":
    query = input("Question: ")
    results = search(query)
    for r in results:
        print("\n" + "=" * 80)
        print("Distance:", r[1])
        print(r[0][:1000])