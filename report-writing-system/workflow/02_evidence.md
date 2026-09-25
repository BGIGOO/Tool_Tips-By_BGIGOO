# WORKFLOW 02 — EVIDENCE LEDGER

Generate an evidence ledger before drafting sections containing dense technical claims or benchmarks.

For each claim:
- **Claim ID**: Unique identifier (e.g., C001);
- **Claim Statement**: Technical proposition;
- **Type**: `OBSERVED` / `MEASURED` / `SOURCED` / `DERIVED` / `ASSUMED`;
- **Evidence**: Specific log line, data record, or measurement value;
- **Source**: Reference paper, standard, or system file path;
- **Condition**: Test environment, configuration, and parameter constraints;
- **Confidence**: Level of certainty;
- **Notes**: Relevant edge cases.

If supporting evidence does not exist:
Mark `STATUS = UNKNOWN`. Never invent or fabricate evidence.
