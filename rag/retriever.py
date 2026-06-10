from vectorstore.search import search


def retrieve_context(
    question,
    k=5
):

    results = search(question)

    context = []

    for row in results:

        context.append(
            row[0]
        )

    return "\n\n".join(context)