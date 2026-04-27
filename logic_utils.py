from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import logging
import math
import re
from collections import Counter


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class BugCase:
    case_id: str
    title: str
    symptoms: tuple[str, ...]
    root_cause: str
    diagnosis: str
    fix: str
    keywords: tuple[str, ...]


BUG_CASES: tuple[BugCase, ...] = (
    BugCase(
        case_id="streamlit-rerun-state",
        title="Streamlit rerun resets state",
        symptoms=(
            "secret changes every click",
            "button reruns reset the answer",
            "state disappears after submitting",
        ),
        root_cause="Session state is not storing the generated secret across reruns.",
        diagnosis="Store the secret, attempts, and difficulty in session_state so the app keeps one stable game state across reruns.",
        fix="Initialize state only when the keys are missing and reset them only when the difficulty changes.",
        keywords=("streamlit", "session_state", "rerun", "state", "secret", "difficulty"),
    ),
    BugCase(
        case_id="hint-direction",
        title="Hints point the wrong direction",
        symptoms=(
            "higher and lower are reversed",
            "feedback says go up when the guess is too high",
            "hints lie to the player",
        ),
        root_cause="The hint text and comparison logic are inconsistent.",
        diagnosis="Use the comparison result directly so the message for too-high guesses says lower and too-low guesses says higher.",
        fix="Keep the hint labels tied to the comparison outcome from check_guess.",
        keywords=("hint", "higher", "lower", "comparison", "feedback", "guess"),
    ),
    BugCase(
        case_id="input-validation",
        title="Invalid input still changes game state",
        symptoms=(
            "strings consume attempts",
            "invalid input counts as a guess",
            "non numeric input causes bad scoring",
        ),
        root_cause="Input parsing and attempt handling are not separated from validation.",
        diagnosis="Validate the guess before consuming an attempt or updating score.",
        fix="Return early on invalid input and only update attempts for valid guesses.",
        keywords=("input", "validation", "invalid", "attempt", "score", "number"),
    ),
    BugCase(
        case_id="attempt-limit",
        title="Game over is not enforced",
        symptoms=(
            "new game button does not recover",
            "won state never clears",
            "out of attempts still lets you play",
        ),
        root_cause="The app does not consistently reset or stop after terminal states.",
        diagnosis="Stop the workflow once the game is won or lost, and reset all state when starting a new game.",
        fix="Use explicit won and lost states and guard the submission path when the session is finished.",
        keywords=("game over", "won", "lost", "reset", "new game", "attempts"),
    ),
    BugCase(
        case_id="scoring",
        title="Score changes unpredictably",
        symptoms=(
            "score goes up on incorrect guesses",
            "scoring feels random",
            "attempt number changes the score inconsistently",
        ),
        root_cause="The scoring rules are not isolated and are being applied with the wrong conditions.",
        diagnosis="Make score changes deterministic: reward wins based on attempt count and apply a fixed penalty only for incorrect valid guesses.",
        fix="Separate win rewards from miss penalties and keep invalid input from changing score.",
        keywords=("score", "attempt", "points", "penalty", "win", "incorrect"),
    ),
    BugCase(
        case_id="range-mismatch",
        title="Difficulty range does not match the secret",
        symptoms=(
            "range changes but secret stays outside the bounds",
            "difficulty switch feels inconsistent",
            "easy mode uses a hard mode secret",
        ),
        root_cause="Difficulty changes are not rebuilding all dependent state.",
        diagnosis="Whenever difficulty changes, regenerate the secret and reset the score, attempts, and history together.",
        fix="Treat difficulty as a full session reset boundary.",
        keywords=("difficulty", "range", "bounds", "secret", "easy", "hard"),
    ),
)


BENCHMARK_CASES: tuple[dict[str, Any], ...] = (
    {
        "report": "The secret number changes every time I click submit in Streamlit.",
        "expected_case_id": "streamlit-rerun-state",
        "expected_root_cause": "Session state is not storing the generated secret across reruns.",
    },
    {
        "report": "My invalid string input still uses up an attempt and affects the score.",
        "expected_case_id": "input-validation",
        "expected_root_cause": "Input parsing and attempt handling are not separated from validation.",
    },
    {
        "report": "The hints say go higher when the guess is already too high.",
        "expected_case_id": "hint-direction",
        "expected_root_cause": "The hint text and comparison logic are inconsistent.",
    },
    {
        "report": "After the difficulty changes, the range says easy but the secret behaves like hard mode.",
        "expected_case_id": "range-mismatch",
        "expected_root_cause": "Difficulty changes are not rebuilding all dependent state.",
    },
)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def analyze_report(report_text: str) -> dict[str, Any]:
    text = (report_text or "").strip()
    tokens = _tokenize(text)
    return {
        "text": text,
        "tokens": tokens,
        "token_counts": Counter(tokens),
        "word_count": len(tokens),
        "has_input": bool(text),
    }


def _case_overlap(tokens: list[str], case: BugCase) -> tuple[float, list[str]]:
    if not tokens:
        return 0.0, []

    token_set = set(tokens)
    keywords = set(case.keywords)
    symptom_tokens = set()
    for symptom in case.symptoms:
        symptom_tokens.update(_tokenize(symptom))

    matched = sorted(token_set & (keywords | symptom_tokens))
    coverage = len(matched) / max(len(keywords | symptom_tokens), 1)
    return coverage, matched


def retrieve_cases(report_text: str, top_k: int = 3) -> list[dict[str, Any]]:
    analysis = analyze_report(report_text)
    tokens = analysis["tokens"]
    ranked: list[dict[str, Any]] = []

    for case in BUG_CASES:
        coverage, matched = _case_overlap(tokens, case)
        symptom_hit = 0.0
        if tokens:
            symptom_hit = max(
                (len(set(tokens) & set(_tokenize(symptom))) / max(len(set(_tokenize(symptom))), 1))
                for symptom in case.symptoms
            )

        lexical_bonus = min(1.0, 0.65 * coverage + 0.35 * symptom_hit)
        ranked.append(
            {
                "case_id": case.case_id,
                "title": case.title,
                "root_cause": case.root_cause,
                "diagnosis": case.diagnosis,
                "fix": case.fix,
                "score": round(lexical_bonus, 3),
                "matched_terms": matched,
                "symptoms": list(case.symptoms),
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["case_id"]))
    return ranked[:top_k]


def _confidence_from_matches(report_text: str, retrieved_cases: list[dict[str, Any]]) -> float:
    analysis = analyze_report(report_text)
    word_count = analysis["word_count"]
    if word_count == 0:
        return 0.0

    best_score = retrieved_cases[0]["score"] if retrieved_cases else 0.0
    second_score = retrieved_cases[1]["score"] if len(retrieved_cases) > 1 else 0.0
    coverage = min(1.0, word_count / 12.0)
    separation = max(0.0, best_score - second_score)
    raw = 0.55 * best_score + 0.25 * coverage + 0.20 * separation
    return round(max(0.05, min(0.99, raw)), 2)


def diagnose_bug(report_text: str) -> dict[str, Any]:
    analysis = analyze_report(report_text)
    retrieved = retrieve_cases(report_text, top_k=3)

    if not analysis["has_input"]:
        return {
            "status": "needs_more_info",
            "diagnosis": "Please describe the glitch, error message, or incorrect behavior.",
            "root_cause": None,
            "confidence": 0.0,
            "retrieved_cases": retrieved,
            "analysis": analysis,
            "trace": [
                "Analyze report: no input provided.",
                "Retrieve cases: skipped because there is no report to compare.",
                "Explain result: ask for more detail.",
            ],
        }

    best_case = retrieved[0] if retrieved else None
    confidence = _confidence_from_matches(report_text, retrieved)

    trace = [
        f"Analyze report: {analysis['word_count']} tokens detected.",
        f"Retrieve cases: top match is {best_case['title']} with score {best_case['score']:.2f}." if best_case else "Retrieve cases: no matching cases found.",
        "Hypothesize root cause: map the strongest match to the most likely failure mode.",
        "Explain result: provide a fix that matches the identified cause.",
    ]

    return {
        "status": "diagnosed",
        "diagnosis": best_case["diagnosis"] if best_case else "No matching debugging case was found.",
        "root_cause": best_case["root_cause"] if best_case else None,
        "confidence": confidence,
        "retrieved_cases": retrieved,
        "analysis": analysis,
        "trace": trace,
        "recommended_fix": best_case["fix"] if best_case else "Collect more details or reproduce the bug.",
    }


def benchmark_assistant() -> dict[str, Any]:
    results = []
    for item in BENCHMARK_CASES:
        diagnosis = diagnose_bug(item["report"])
        top_case = diagnosis["retrieved_cases"][0] if diagnosis["retrieved_cases"] else {}
        result = {
            "report": item["report"],
            "expected_case_id": item["expected_case_id"],
            "predicted_case_id": top_case.get("case_id"),
            "expected_root_cause": item["expected_root_cause"],
            "predicted_root_cause": diagnosis["root_cause"],
            "confidence": diagnosis["confidence"],
            "correct": top_case.get("case_id") == item["expected_case_id"],
        }
        results.append(result)

    accuracy = sum(1 for item in results if item["correct"]) / max(len(results), 1)
    avg_confidence = sum(item["confidence"] for item in results) / max(len(results), 1)
    return {
        "cases": results,
        "accuracy": round(accuracy, 2),
        "average_confidence": round(avg_confidence, 2),
        "total_cases": len(results),
    }


def export_trace(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=True)