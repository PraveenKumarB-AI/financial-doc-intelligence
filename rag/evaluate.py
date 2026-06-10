from rag.chain import ask_question

questions = [

    "Who is the CEO?",

    "What are Apple's risk factors?",

    "What was total revenue?",

    "What products does Apple sell?"
]

for q in questions:

    print("\n")

    print("=" * 60)

    print("QUESTION:")

    print(q)

    answer = ask_question(q)

    print("\nANSWER:")

    print(answer)