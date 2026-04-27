# Model Card: Game Glitch Investigator

## Model Overview
- System name: Game Glitch Investigator
- Type: Local retrieval-based debugging assistant (deterministic heuristic ranker)
- Implementation: Python + Streamlit
- Primary modules:
  - `app.py` for UI, interactions, and logging
  - `logic_utils.py` for retrieval, diagnosis, confidence scoring, and benchmark evaluation

## Purpose and Scope
This system helps users diagnose likely bug categories in a number-guessing game context by reading short natural-language bug reports. It returns:
- likely root cause,
- recommended fix,
- confidence score,
- reasoning trace,
- retrieved evidence cases.

## Intended Users
- Students learning debugging workflows
- Instructors evaluating applied AI integration
- Developers who want a local, explainable bug triage demo

## Out of Scope
- It is not a general software debugging model.
- It does not execute code traces, static analysis, or runtime profiling.
- It should not be treated as a final production diagnosis engine.

## Data and Knowledge Source
The system uses an embedded local case library defined in `logic_utils.py` (`BUG_CASES`).
No external API, internet retrieval, or private user telemetry is used.

## How the System Works
1. User provides a bug report.
2. The assistant tokenizes and analyzes text.
3. It retrieves top matching cases from the local library.
4. It chooses the best match and generates diagnosis plus fix.
5. It computes confidence from match quality, report length, and score separation.
6. It returns trace and retrieved evidence to support explainability.

## Human-in-the-Loop and Oversight
- Human users review suggested root cause and fix before taking action.
- Users can compare retrieved cases and matched terms to judge answer quality.
- Human evaluation remains necessary for ambiguous, mixed, or underspecified reports.

## Guardrails and Safety
- Empty input returns `needs_more_info` instead of a fabricated diagnosis.
- Evidence-first output is shown through retrieved cases and trace steps.
- Recent outputs are logged to `diagnosis_log.jsonl` for review and debugging.

## Evaluation and Testing Results
### Pytest (automated checks)
- Command: `python -m pytest -q`
- Latest run: `4 passed in 0.02s`
- Covered behaviors:
  - retrieval ranking behavior,
  - diagnosis structure and confidence,
  - empty-input guardrail,
  - benchmark summary contract.

### Built-in benchmark (curated cases)
- Command used:
  - `python -c "from logic_utils import benchmark_assistant; import json; print(json.dumps(benchmark_assistant(), ensure_ascii=True))"`
- Latest observed metrics:
  - total_cases: 4
  - accuracy: 0.75
  - average_confidence: 0.57
- Noted failure mode:
  - the invalid-input report was misclassified as `scoring` instead of `input-validation` in the latest run.

## Biases, Risks, and Limitations
- Coverage bias: the model can only diagnose patterns represented in the local case library.
- Lexical bias: predictions depend heavily on wording overlap, not deep semantic understanding.
- Confidence calibration risk: high confidence can still be wrong if wording resembles an incorrect case.
- Domain bias: tuned to game-style bug reports and may degrade on unrelated software issues.

## Mitigations and Improvement Plan
- Add more benchmark cases, especially confusing overlaps (input vs scoring).
- Expand synonym handling and weighting for robust semantic matching.
- Add per-class precision/recall analysis to track failure patterns.
- Improve confidence calibration with thresholding and abstain behavior for uncertain matches.

## AI Collaboration Disclosure
AI assistance was used to:
- brainstorm architecture and module boundaries,
- draft/refactor code and documentation,
- suggest tests and guardrail patterns,
- iterate on user-facing explanations.

Human work included:
- selecting project direction,
- validating behavior and outputs,
- deciding final design scope,
- reviewing and approving implementation decisions.

## Ethical and Academic Use Statement
This project is a learning artifact for applied AI system design, evaluation, and communication. Outputs should be reviewed by a human before use in any real debugging workflow.
