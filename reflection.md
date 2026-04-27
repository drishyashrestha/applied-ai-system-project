# Reflection

## 1) AI Collaboration
I used AI as a coding and planning assistant while building this project extension. AI support helped with:
- restructuring the original mini-project into a modular applied-AI pipeline,
- drafting and refining retrieval and diagnosis logic,
- generating and improving test coverage,
- improving documentation and walkthrough readiness.

I still made the final decisions on project scope, architecture, and quality standards. I validated changes by running the app, checking outputs, and running automated tests before accepting results.

## 2) What Changed from the Original Mini-Project
The original project was a Streamlit number-guessing game. For the final project, I redesigned it into a local AI debugging assistant that reasons over bug reports related to game behavior.

The extension keeps conceptual continuity with the original game domain (state handling, hint direction, input validation, scoring, and difficulty boundaries), but changes the interaction from gameplay to diagnosis.

## 3) Applied AI Features Implemented
The final system includes:
- retrieval over a local bug-case knowledge base,
- an agent-like reasoning flow (analyze -> retrieve -> hypothesize -> explain),
- confidence scoring for diagnosis quality,
- visible trace and retrieved evidence for explainability,
- guardrails for empty or low-information inputs.

## 4) Reliability and Testing Results
I used two levels of reliability checks:
- automated tests with pytest,
- in-app benchmark evaluation.

Latest observed results:
- `python -m pytest -q` -> `4 passed in 0.02s`
- benchmark summary -> accuracy: 0.75, average_confidence: 0.57, total_cases: 4

The benchmark also exposed one meaningful error: an invalid-input report was predicted as `scoring` instead of `input-validation`. This is useful because it identifies a concrete retrieval ambiguity to improve.

## 5) Biases and Limitations
Main limitations and possible biases:
- case-library bias: the assistant only performs well on represented bug patterns,
- lexical bias: strong dependence on keyword overlap,
- calibration risk: confidence is heuristic and may not reflect true correctness,
- domain limitation: designed for game-style bug reports, not general debugging.

## 6) Mitigations and Future Improvements
To improve quality:
- expand benchmark size and diversity,
- add synonyms and stronger matching rules for ambiguous cases,
- introduce abstain logic for low-confidence outputs,
- track per-case metrics to evaluate where retrieval fails most often.

## 7) What I Learned
This project showed me that an applied AI system is not just a single model call. A useful system needs clear data flow, modular logic, guardrails, measurable evaluation, and transparent outputs. It also showed that human review is essential, especially when confidence scores can be wrong.
