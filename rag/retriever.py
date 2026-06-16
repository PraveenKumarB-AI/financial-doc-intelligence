from analytics.company_detector import detect_company
from vectorstore.search import search
from rag.text_cleaner import clean_text


def retrieve_context(question):
    """
    Detect which company the question is about, then search only
    that company's chunks. Falls back to all companies if none detected.
    """
    company = detect_company(question)
    print(f"Detected company: {company or 'All (no specific company detected)'}")

    results = search(question, company=company)

    context = []
    for row in results:
        cleaned = clean_text(row[0])
        context.append(cleaned)

    return "\n\n".join(context)