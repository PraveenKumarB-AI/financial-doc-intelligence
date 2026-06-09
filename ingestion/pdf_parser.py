from pathlib import Path
import fitz


def extract_text(file_path):
    """
    Extract text from a PDF file.

    Args:
        file_path (str): Path to PDF file

    Returns:
        str: Extracted text
    """

    file_path = Path(file_path)

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return ""

    text = ""

    try:
        with fitz.open(file_path) as document:
            for page in document:
                text += page.get_text()

        return text

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""