from embeddings.embedding_generator import (
    generate_embedding
)

from vectorstore.database import (
    get_connection
)


def search(query):

    embedding = generate_embedding(query)

    embedding = str(embedding)

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
    """
    SELECT
        chunk_text
    FROM document_chunks
    ORDER BY
        embedding <=> %s::vector
    LIMIT 5
    """,
    (embedding,)
)
    

    results = cursor.fetchall()

    cursor.close()

    conn.close()

    return results


if __name__ == "__main__":

    query = input(
        "Question: "
    )

    results = search(
        query
    )

    for r in results:

        print("\n")
        print(r[0][:500])
