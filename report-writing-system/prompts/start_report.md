# START REPORT PROMPT

Initialize session with the following reference modules:
1. `SYSTEM_PROMPT.md`
2. `context/author_profile.md`
3. `context/project_context.md`
4. `context/document_spec.md`
5. Applicable guidelines under `rules/`
6. Applicable steps under `workflow/`

Task:
I want to write: [SECTION / DOCUMENT TITLE]
Target Document Language: [Vietnamese / English / other; default from document_spec]

Execution Pipeline:
`DISCOVERY → OUTLINE → DRAFT → REVIEW → FINAL_QA`

Operational Rules:
- First, perform the **Question Gate** to evaluate Context Sufficiency.
- If `BLOCKING` information is missing, output `CONTEXT STATUS: INSUFFICIENT` and ask only essential questions (max 7).
- Converse with the user in their language (e.g., Vietnamese) while reasoning according to the system rules.
- Never start drafting prematurely before resolving blockers.
- Do not ask for information already documented in the context files.
- Once context is sufficient, output `CONTEXT STATUS: SUFFICIENT`, establish the **Context Lock**, and generate the analytical outline.
