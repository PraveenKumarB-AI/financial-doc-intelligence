import json
from pathlib import Path

from ingestion.chunker import chunk_text
from ingestion.metadata_builder import (
    extract_metadata
)

from ingestion.pdf_parser import (
    extract_text
)

PROCESSED_DIR = Path(
    "data/processed"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# Use one SEC filing

file_path = input("Enter filing path: ").strip()


print("\nExtracting text...")

text = extract_text(file_path)

print(
    f"Characters extracted: {len(text)}"
)

metadata = extract_metadata(
    text
)

chunks = chunk_text(text)

print(
    f"Total chunks: {len(chunks)}"
)

# Save text

with open(
    PROCESSED_DIR /
    "extracted_text.txt",
    "w"
) as f:

    f.write(text)

# Save metadata

with open(
    PROCESSED_DIR /
    "metadata.json",
    "w"
) as f:

    json.dump(
        metadata,
        f,
        indent=4
    )

# Save chunks

with open(
    PROCESSED_DIR /
    "chunks.json",
    "w"
) as f:

    json.dump(
        chunks,
        f,
        indent=4
    )

print("\nProcessing Complete")