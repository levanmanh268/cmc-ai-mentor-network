# EduTrainer AI Lab | Education Knowledge and Evaluation

**Independent portfolio project with fictional lessons, synthetic practice questions and provisional rubric feedback. Not an official FUNiX platform, project, dataset or deployment.**

## Alignment with CMC TS AI Engineer Intern

| JD capability | Implementation |
| --- | --- |
| LLM/prompt engineering | Optional dependency-injected text-model call; strict JSON/citation contract; mock-only tests |
| RAG and retrieval | Role-scoped and track-scoped BM25 across Python / ML example lessons with source IDs |
| AI Agents | 4 allowlisted tools: course_search, quiz, rubric_feedback and learning_path |
| Evaluation and data | Public 12-case synthetic benchmark, Hit@3, MRR@3, no-hit negatives, permission-leak checks |
| Document intelligence | Structured lesson metadata with modules, revision, source; teacher-authored quiz and rubric |
| Integration | FastAPI read-only fictional-student service and integration tests |

## Local quickstart (Python 3.11+)

From repository root:

    python -m unittest discover -s edu_trainer_ai/tests -v
    python -m edu_trainer_ai.evaluate
    python -m pip install -r edu_trainer_ai/requirements-api.txt
    uvicorn edu_trainer_ai.api:app --host 127.0.0.1 --port 8012

Interactive API docs: http://127.0.0.1:8012/docs

## Data / safety

    Fictional lessons -> track/role scope -> BM25 -> source-linked excerpts
    Prewritten quiz bank -> withhold answer keys -> practice-only grade
    Teaching rubric -> lexical evidence heuristic -> mandatory trainer review (not an official mark)
    Simulated progress -> deterministic next-module suggestion (not adaptive student profiling)
    Optional mocked LLM -> JSON schema + citation ID membership -> UNVERIFIED feedback draft
    Synthetic QA -> hit@3 / MRR@3 / negative no-hit / scope checks -> CI

Source is data/lessons.json; all names and lesson content are invented for this project. Students cannot query trainer-only reference material via the demo API; it always uses a constant fictional student identity.

## Limitations and integrity

Lexical evaluation is not semantic correctness, and citation membership is not claim-level entailment. Rubric feedback can fail on paraphrases; not suitable for grading actual learners. The prototype does not integrate with an LMS, lacks production SSO, and does not store or profile real students. No real LLM, OCR or private data was used in the offline benchmark. The benchmark is public and too small to claim generalization.

**Important employment distinction:** this is a separate personal portfolio demonstration inspired by educational AI training, not an actual FUNiX company assignment or product. Code created with AI assistance should be personally reviewed and explained by the applicant.
