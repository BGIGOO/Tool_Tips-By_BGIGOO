# Report Writing System

Goal: Transform AI into a **methodical research/technical report writing assistant**, rather than a superficial prompt for proofreading sentences.

## System Philosophy

The AI must follow this rigorous pipeline:

`Context → Discovery/Q&A → Evidence → Outline → Draft → Technical Review → Human-Voice Review → Final QA`

Never jump straight from a prompt to a final draft while critical data is missing.

## Multilingual & Token Optimization

- **Core prompts, workflows, and rules are in English** to maximize instruction precision and minimize token consumption for LLMs.
- **User Interaction**: You can converse and give instructions in **Vietnamese** (or any preferred language).
- **Document Output**: The AI produces reports in whatever target language you specify (Vietnamese, English, etc.) as designated in the prompt or document specifications.

## Architecture

- `SYSTEM_PROMPT.md`: Master orchestration prompt.
- `context/`: Author profile, project background, and document specifications.
- `rules/`: Rules for technical style, factuality, citations, tables/figures, and anti-AI-filler patterns.
- `workflow/`: Step-by-step phased workflow.
- `templates/`: Input schemas, experiment logs, and evidence ledgers.
- `prompts/`: Quick-trigger prompts for distinct tasks.
- `examples/`: Tone calibration examples (Good vs. Bad).

## Usage Workflow

1. Fill out `context/author_profile.md`.
2. Fill out `context/project_context.md`.
3. Configure citation style and target language in `context/document_spec.md`.
4. Initiate a report session using `prompts/start_report.md`.
5. The AI runs the **Question Gate** to evaluate context sufficiency before drafting.
6. Record sources, raw metrics, and measurements in `templates/evidence_ledger.csv`.
7. Finalize the section outline before drafting content.
8. Run `prompts/reviewer.md` before final approval.

## Core Principles

"Human-like" does not mean deliberately making typos, awkward phrasing, or grammar mistakes. Natural authenticity stems from:
- Consistent authorial voice.
- Purposeful argumentation.
- Dynamic sentence cadence tailored to technical depth.
- Strict consistency in technical terminology.
- Epistemic calibration: claims precisely match the strength of evidence.
- Explicitly stated boundaries, assumptions, and scope limitations.
- Avoidance of academic fluff and marketing buzzwords.
