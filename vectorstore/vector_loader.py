import json

from embeddings.embedding_generator import (
    generate_embedding
)

from vectorstore.database import (
    get_connection
)


def load_chunks():

    with open(
        "data/processed/chunks.json",
        "r"
    ) as f:

        chunks = json.load(f)

    conn = get_connection()

    cursor = conn.cursor()

    for chunk in chunks:

       embedding = str(generate_embedding(chunk))
    

       cursor.execute(
            """
            INSERT INTO document_chunks
            (
                chunk_text,
                metadata,
                embedding
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                chunk,
                json.dumps({}),
                embedding
            )
        )

    conn.commit()

    cursor.close()

    conn.close()

    print(
        f"Loaded {len(chunks)} chunks"
    )


if __name__ == "__main__":

    load_chunks()
