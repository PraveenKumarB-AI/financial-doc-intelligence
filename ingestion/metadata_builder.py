import re


def extract_metadata(text):

    metadata = {}

    # Company Name
    company_match = re.search(
        r"Apple Inc\.|Microsoft Corporation|Tesla, Inc\.",
        text,
        re.IGNORECASE
    )

    metadata["company"] = (
        company_match.group(0)
        if company_match
        else "Unknown"
    )

    # Fiscal Year

    fiscal_match = re.search(
        r"fiscal year ended\s+([A-Za-z]+\s+\d+,\s+\d+)",
        text,
        re.IGNORECASE
    )

    metadata["fiscal_year"] = (
        fiscal_match.group(1)
        if fiscal_match
        else "Unknown"
    )

    metadata["document_length"] = len(text)

    return metadata