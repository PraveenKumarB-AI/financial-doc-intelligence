from rag.chain import (
    ask_question
)

print(
    "Financial RAG Assistant"
)

print(
    "Type 'exit' to quit"
)

while True:

    question = input(
        "\nQuestion: "
    )

    if question.lower() == "exit":

        break

    answer = ask_question(
        question
    )

    print("\nAnswer:\n")

    print(answer)