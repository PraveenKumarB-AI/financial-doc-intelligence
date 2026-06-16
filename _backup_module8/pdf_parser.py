from bs4 import BeautifulSoup
from pathlib import Path
import fitz


def extract_text(file_path):

    path = Path(file_path)

    # SEC filings
    if path.suffix.lower() in [".txt", ".html", ".htm"]:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            raw_text = f.read()

        soup = BeautifulSoup(
            raw_text,
            "html.parser"
        )

        return soup.get_text(
            separator=" ",
            strip=True
        )

    # PDF files
    doc = fitz.open(file_path)

    pages = []

    for page in doc:

        pages.append(
            page.get_text()
        )

    return "\n".join(
        pages
    )