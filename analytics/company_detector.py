# Maps keywords to the exact company name stored in document_chunks.company
COMPANY_MAP = {
    "apple":     "Apple Inc.",
    "microsoft": "Microsoft Corporation",
    "tesla":     "Tesla, Inc.",
    "nvidia":    "NVIDIA Corporation",
    "amazon":    "Amazon.com, Inc.",
    "meta":      "Meta Platforms, Inc.",
    "google":    "Alphabet Inc.",
}

def detect_company(question):
    """Return the full DB company name if found in the question, else None."""
    q = question.lower()
    for keyword, full_name in COMPANY_MAP.items():
        if keyword in q:
            return full_name
    return None   # None means: search all companies