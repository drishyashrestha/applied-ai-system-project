from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from logic_utils import benchmark_assistant, diagnose_bug, retrieve_cases


def test_retrieval_finds_state_reset_case():
    results = retrieve_cases("The secret number changes every time I click submit in Streamlit.")
    assert results[0]["case_id"] == "streamlit-rerun-state"
    assert results[0]["score"] > 0


def test_diagnosis_returns_fix_and_confidence():
    result = diagnose_bug("My invalid string input still uses up an attempt and affects the score.")
    assert result["status"] == "diagnosed"
    assert result["root_cause"] is not None
    assert result["recommended_fix"]
    assert 0.0 < result["confidence"] <= 0.99


def test_empty_report_requests_more_info():
    result = diagnose_bug("")
    assert result["status"] == "needs_more_info"
    assert result["confidence"] == 0.0


def test_benchmark_reports_summary():
    summary = benchmark_assistant()
    assert summary["total_cases"] >= 4
    assert 0.0 <= summary["accuracy"] <= 1.0
    assert 0.0 <= summary["average_confidence"] <= 0.99
    assert all("predicted_case_id" in case for case in summary["cases"])
