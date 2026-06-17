"""
logs/logger.py — MODULE 17: Structured JSON logger
Every API request writes one JSON line to logs/api.log.
Import get_logger() anywhere in the project.
"""

import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("logs/api.log")
LOG_FILE.parent.mkdir(exist_ok=True)


def _get_file_logger():
    logger = logging.getLogger("findoc")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger


_logger = _get_file_logger()


def log_request(
    endpoint: str,
    question: str = None,
    company: str = None,
    answer: str = None,
    latency_s: float = None,
    status: str = "ok",
    error: str = None,
):
    """Write one structured JSON log line."""
    entry = {
        "ts":        datetime.now(timezone.utc).isoformat(),
        "endpoint":  endpoint,
        "status":    status,
        "latency_s": round(latency_s, 3) if latency_s is not None else None,
    }
    if question:  entry["question"] = question[:200]
    if company:   entry["company"]  = company
    if answer:    entry["answer"]   = answer[:300]
    if error:     entry["error"]    = str(error)[:300]
    _logger.info(json.dumps(entry))


def read_logs(n: int = 50):
    """Return the last n log lines as a list of dicts."""
    if not LOG_FILE.exists():
        return []
    lines = LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
    out = []
    for line in reversed(lines[-n:]):
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out
