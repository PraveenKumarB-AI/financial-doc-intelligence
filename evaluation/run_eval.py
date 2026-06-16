"""
evaluation/run_eval.py — MODULE 16: RAG Evaluation Harness
Runs every gold question through the live pipeline, judges answers with
local Llama 3, and produces a metrics table + JSON results file.
Run:  python -m evaluation.run_eval
"""

import json
import time
from datetime import datetime
from pathlib import Path

from rag.retriever import retrieve_context
from rag.chain import ask_question
from llm.llm_client import generate_response

GOLD_FILE = Path("evaluation/test_questions.json")
RESULTS_DIR = Path("evaluation/results")
RESULTS_DIR.mkdir(exist_ok=True)


def judge_answer(question, expected, actual):
    """Ask local Llama 3 to judge whether the actual answer contains the
    expected information. Returns True/False."""
    prompt = f"""
You are an evaluation judge. Decide if the ACTUAL answer correctly addresses
the EXPECTED answer for the given question.

Question: {question}
Expected (key information that must be present): {expected}
Actual answer: {actual}

Rules:
- The actual answer passes if it contains the key information from expected.
- Partial matches are OK (e.g. expected "Satya Nadella", actual mentions
  "Satya Nadella is the CEO" → PASS).
- If the actual says "I could not find" or similar → FAIL.
- Numbers: pass if within 5% of expected value.

Reply with exactly one word: PASS or FAIL
"""
    result = generate_response(prompt).strip().upper()
    return result.startswith("PASS")


def run():
    gold = json.loads(GOLD_FILE.read_text())
    print(f"\nRunning evaluation on {len(gold)} questions...\n")

    results = []
    passed = 0
    by_category = {}
    by_company = {}

    for i, item in enumerate(gold, 1):
        q_id       = item["id"]
        company    = item["company"]
        question   = item["question"]
        expected   = item["expected"]
        category   = item.get("category", "general")

        print(f"[{i:02d}/{len(gold)}] {q_id} — {question[:60]}")

        start = time.time()
        try:
            context = retrieve_context(question)
            actual  = ask_question(question)
        except Exception as e:
            actual = f"ERROR: {e}"
            context = ""
        latency = round(time.time() - start, 1)

        hit = bool(context.strip())
        correct = judge_answer(question, expected, actual) if hit else False
        if correct:
            passed += 1

        status = "✅ PASS" if correct else "❌ FAIL"
        print(f"   {status}  ({latency}s)  actual: {actual[:80]}")

        result = {
            "id": q_id,
            "company": company,
            "category": category,
            "question": question,
            "expected": expected,
            "actual": actual,
            "retrieval_hit": hit,
            "correct": correct,
            "latency_s": latency,
        }
        results.append(result)

        by_category.setdefault(category, {"pass": 0, "total": 0})
        by_category[category]["total"] += 1
        if correct:
            by_category[category]["pass"] += 1

        by_company.setdefault(company, {"pass": 0, "total": 0})
        by_company[company]["total"] += 1
        if correct:
            by_company[company]["pass"] += 1

    total = len(gold)
    pct   = round(passed / total * 100)
    avg_latency = round(sum(r["latency_s"] for r in results) / total, 1)

    print(f"\n{'='*60}")
    print(f"  RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"  Overall accuracy : {passed}/{total} ({pct}%)")
    print(f"  Avg latency      : {avg_latency}s per question")
    print(f"\n  By company:")
    for co, s in sorted(by_company.items()):
        p = round(s['pass'] / s['total'] * 100)
        print(f"    {co:<30} {s['pass']}/{s['total']} ({p}%)")
    print(f"\n  By category:")
    for cat, s in sorted(by_category.items()):
        p = round(s['pass'] / s['total'] * 100)
        print(f"    {cat:<15} {s['pass']}/{s['total']} ({p}%)")
    print(f"{'='*60}\n")

    # Save results
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    out_file = RESULTS_DIR / f"eval_{timestamp}.json"
    out_file.write_text(json.dumps({
        "timestamp": timestamp,
        "total": total,
        "passed": passed,
        "accuracy_pct": pct,
        "avg_latency_s": avg_latency,
        "by_company": by_company,
        "by_category": by_category,
        "results": results,
    }, indent=2))
    print(f"Results saved to {out_file}")


if __name__ == "__main__":
    run()
