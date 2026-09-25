# START REPORT

Load:
1. `SYSTEM_PROMPT.md`
2. `context/author_profile.md`
3. `context/project_context.md`
4. `context/document_spec.md`
5. relevant files under `rules/`
6. relevant files under `workflow/`

Task:
Tôi muốn viết: [SECTION / DOCUMENT]

Chế độ:
DISCOVERY → OUTLINE → DRAFT → REVIEW → FINAL_QA

Quy tắc:
- Trước tiên kiểm tra Context Sufficiency.
- Nếu thiếu BLOCKING information, chỉ hỏi các câu hỏi cần thiết.
- Không viết trước rồi mới hỏi.
- Không lặp lại câu hỏi đã có đáp án trong context.
- Khi đủ dữ liệu, tạo Context Lock và outline.
