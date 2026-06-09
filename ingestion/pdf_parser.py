import fitz
from pathlib import Path


def extract_text(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

    if path.suffix == ".txt":

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            return f.read()

    doc = fitz.open(file_path)

    pages = []

    for page in doc:

        pages.append(
            page.get_text()
        )

    return "\n".join(pages)