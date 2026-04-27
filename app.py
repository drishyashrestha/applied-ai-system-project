from __future__ import annotations

from datetime import datetime
import json
import logging
from pathlib import Path

import streamlit as st

from logic_utils import benchmark_assistant, diagnose_bug, export_trace


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LOG_PATH = Path(__file__).with_name("diagnosis_log.jsonl")


SAMPLE_REPORTS = {
    "State reset bug": "The secret number changes every time I click submit in Streamlit.",
    "Invalid input bug": "My invalid string input still uses up an attempt and affects the score.",
    "Hint bug": "The hints say go higher when the guess is already too high.",
    "Difficulty bug": "After the difficulty changes, the range says easy but the secret behaves like hard mode.",
}


def log_diagnosis(report_text: str, result: dict[str, object]) -> None:
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "report": report_text,
        "diagnosis": result.get("diagnosis"),
        "root_cause": result.get("root_cause"),
        "confidence": result.get("confidence"),
        "status": result.get("status"),
    }
    try:
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=True) + "\n")
    except OSError as error:
        LOGGER.warning("Could not write diagnosis log: %s", error)


st.set_page_config(page_title="Game Glitch Investigator", page_icon="🕵️", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #171529 0%, #0f0f1f 45%, #090913 100%);
        color: #f5f7fb;
    }
    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 1.2rem;
        background: linear-gradient(135deg, rgba(99,102,241,0.22), rgba(14,165,233,0.14));
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 20px 60px rgba(0,0,0,0.28);
        margin-bottom: 1rem;
    }
    .metric-card {
        border-radius: 1rem;
        padding: 1rem 1rem;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.09);
        min-height: 110px;
    }
    .step-card {
        border-left: 4px solid #67e8f9;
        padding: 0.8rem 1rem;
        background: rgba(255,255,255,0.04);
        border-radius: 0.8rem;
        margin-bottom: 0.55rem;
    }
    .muted {
        color: rgba(255,255,255,0.7);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "benchmark" not in st.session_state:
    st.session_state.benchmark = None
if "report_text" not in st.session_state:
    st.session_state.report_text = SAMPLE_REPORTS["State reset bug"]


st.markdown(
    """
    <div class="hero">
      <h1 style="margin-bottom:0.2rem;">🕵️ Game Glitch Investigator</h1>
            <p class="muted" style="margin:0;">A local applied-AI debugging assistant extended from a Streamlit guessing game. Type a bug report, not a game move: the app retrieves similar cases, reasons about root cause, and reports confidence.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
        "Start here: this project was redesigned from a guessing game into a debugging assistant. "
        "To test it, describe a bug in plain English, or click one of the sample bug reports in the sidebar. "
        "Good prompts mention symptoms like state resets, invalid input, wrong hints, or difficulty/range mismatches."
)

with st.sidebar:
    st.header("Controls")
    st.caption("Pick a sample or submit your own bug report.")
    st.markdown(
        """
        **What to ask**
        - "The secret changes every time I click submit"
        - "Invalid input still uses an attempt"
        - "The hints point the wrong way"
        - "Difficulty changes but the secret does not reset"
        """
    )
    for label, report in SAMPLE_REPORTS.items():
        if st.button(label, use_container_width=True):
            st.session_state.report_text = report
            st.session_state.last_result = diagnose_bug(report)
            log_diagnosis(report, st.session_state.last_result)
            st.rerun()

    st.divider()
    if st.button("Run reliability benchmark", use_container_width=True):
        st.session_state.benchmark = benchmark_assistant()
        st.rerun()

    if st.session_state.benchmark:
        st.subheader("Benchmark summary")
        st.metric("Accuracy", f"{st.session_state.benchmark['accuracy']:.0%}")
        st.metric("Avg confidence", f"{st.session_state.benchmark['average_confidence']:.2f}")
        st.metric("Cases", st.session_state.benchmark["total_cases"])


left, right = st.columns([1.25, 0.95], gap="large")

with left:
    st.subheader("Bug report")
    with st.form("report_form"):
        report_text = st.text_area(
            "Describe the bug or confusing behavior",
            value=st.session_state.report_text,
            height=160,
            placeholder="Example: The secret number changes every time I click submit.",
        )
        submitted = st.form_submit_button("Investigate bug")

    if submitted:
        st.session_state.report_text = report_text
        st.session_state.last_result = diagnose_bug(report_text)
        log_diagnosis(report_text, st.session_state.last_result)

    result = st.session_state.last_result
    if result:
        status = result.get("status")
        confidence = float(result.get("confidence") or 0.0)
        st.markdown("### Diagnosis")
        st.markdown(f"**Status:** {status}")
        st.markdown(f"**Root cause:** {result.get('root_cause') or 'Need more detail'}")
        st.markdown(f"**Recommended fix:** {result.get('recommended_fix')}")

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.markdown(
            f'<div class="metric-card"><div class="muted">Confidence</div><h2>{confidence:.0%}</h2></div>',
            unsafe_allow_html=True,
        )
        metric_col2.markdown(
            f'<div class="metric-card"><div class="muted">Top match</div><h2>{result["retrieved_cases"][0]["title"] if result.get("retrieved_cases") else "None"}</h2></div>',
            unsafe_allow_html=True,
        )
        metric_col3.markdown(
            f'<div class="metric-card"><div class="muted">Matched terms</div><h2>{len(result["retrieved_cases"][0]["matched_terms"]) if result.get("retrieved_cases") else 0}</h2></div>',
            unsafe_allow_html=True,
        )

        st.markdown("### Agent trace")
        for step in result.get("trace", []):
            st.markdown(f'<div class="step-card">{step}</div>', unsafe_allow_html=True)

        st.markdown("### Retrieved cases")
        for case in result.get("retrieved_cases", []):
            with st.expander(f"{case['title']} · score {case['score']:.2f}"):
                st.write("Root cause:", case["root_cause"])
                st.write("Diagnosis:", case["diagnosis"])
                st.write("Fix:", case["fix"])
                st.write("Matched terms:", ", ".join(case["matched_terms"]) or "None")

with right:
    st.subheader("How it works")
    st.write("1. Parse the bug report for key terms and symptoms.")
    st.write("2. Retrieve similar debugging cases from a local knowledge base.")
    st.write("3. Rank the most likely root cause and recommended fix.")
    st.write("4. Score confidence from retrieval strength and match separation.")

    st.subheader("What this used to be")
    st.write(
        "The earlier project was a number-guessing game. Those same ideas now show up as debugging cases: "
        "state reset, hint direction, input validation, scoring, and difficulty reset behavior."
    )

    st.subheader("Guardrails")
    st.write("- The assistant asks for more detail when the report is empty.")
    st.write("- Invalid or vague reports do not produce a fabricated root cause.")
    st.write("- Every result includes the retrieved evidence used to form the answer.")

    st.subheader("Current log")
    if LOG_PATH.exists():
        try:
            lines = LOG_PATH.read_text(encoding="utf-8").splitlines()[-5:]
            for line in reversed(lines):
                st.code(line, language="json")
        except OSError as error:
            st.warning(f"Could not read log file: {error}")
    else:
        st.caption("No log entries yet.")

if st.session_state.benchmark:
    st.divider()
    st.subheader("Benchmark details")
    for case in st.session_state.benchmark["cases"]:
        st.write(
            f"- {case['report']} -> predicted {case['predicted_case_id']} | correct={case['correct']} | confidence={case['confidence']:.2f}"
        )
