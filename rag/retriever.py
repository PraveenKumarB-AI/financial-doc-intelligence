from analytics.company_detector import (
    detect_company
)

from vectorstore.search import (
    search
)

from rag.text_cleaner import (
    clean_text
)


def retrieve_context(question):

    company = detect_company(
        question
    )

    print(
        f"Detected Company: {company}"
    )

    results = search(
        question
    )

    context = []

    for row in results:

        cleaned_chunk = clean_text(
            row[0]
        )

        context.append(
            cleaned_chunk
        )

    return "\n\n".join(
        context
    )