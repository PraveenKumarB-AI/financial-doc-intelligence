import json

from rag.chain import ask_question


def evaluate():

    with open(
        "evaluation/test_questions.json",
        "r"
    ) as f:

        questions = json.load(f)

    correct = 0

    total = len(
        questions
    )

    for item in questions:

        question = item["question"]

        expected = item["expected"]

        answer = ask_question(
            question
        )

        print("\n")
        print("=" * 60)

        print(
            f"Question: {question}"
        )

        print(
            f"Expected: {expected}"
        )

        print(
            f"Generated: {answer}"
        )

        if expected.lower() in answer.lower():

            correct += 1

    accuracy = (
        correct / total
    ) * 100

    print("\n")
    print("=" * 60)

    print(
        f"Accuracy: {accuracy:.2f}%"
    )


if __name__ == "__main__":

    evaluate()