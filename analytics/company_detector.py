COMPANIES = [
    "apple",
    "microsoft",
    "tesla",
    "nvidia",
    "amazon",
    "meta",
    "google"
]


def detect_company(question):

    question = question.lower()

    for company in COMPANIES:

        if company in question:
            return company.title()

    return "Apple"