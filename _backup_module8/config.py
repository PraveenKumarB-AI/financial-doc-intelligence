from pathlib import Path

BASE_DIR = Path(__file__).parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"

PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
