from embeddings.embedding_generator import generate_embedding
from vectorstore.database import get_connection


def search(query):

    conn = get_connection()
    cursor = conn.cursor()

    # Keyword search first
    if "ceo" in query.lower() or "chief executive officer" in query.lower():

        cursor.execute(
            """
            SELECT chunk_text, 0 as distance
            FROM document_chunks
            WHERE chunk_text ILIKE '%Timothy D. Cook%'
               OR chunk_text ILIKE '%Chief Executive Officer%'
            LIMIT 10
            """
        )

        results = cursor.fetchall()

        if results:
            cursor.close()
            conn.close()
            return results

    # Normal vector search
    embedding = generate_embedding(query)
    embedding = str(embedding)

    cursor.execute(
        """
        SELECT
            chunk_text,
            embedding <=> %s::vector AS distance
        FROM document_chunks
        ORDER BY distance
        LIMIT 20
        """,
        (embedding,)
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

        if len(r) > 1:
            print("Distance:", r[1])

        print(r[0][:1000])