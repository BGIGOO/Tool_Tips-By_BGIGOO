# Report Writing System

Mục tiêu: biến AI thành một **trợ lý viết báo cáo/paper có quy trình**, không phải một prompt sửa câu.

## Tư duy hệ thống

AI phải đi theo chuỗi:

`Context → Discovery/Q&A → Evidence → Outline → Draft → Technical Review → Human-voice Review → Final QA`

Không được nhảy thẳng từ "hãy viết" sang bài hoàn chỉnh khi còn thiếu dữ liệu quan trọng.

## Cấu trúc

- `SYSTEM_PROMPT.md`: prompt điều phối chính.
- `context/`: hiểu tác giả, dự án, bối cảnh học thuật.
- `rules/`: luật viết, kiểm chứng, trích dẫn, bảng/hình, chống văn AI.
- `workflow/`: quy trình từng giai đoạn.
- `templates/`: biểu mẫu dữ liệu đầu vào và sổ bằng chứng.
- `prompts/`: prompt gọi nhanh cho từng tác vụ.
- `examples/`: ví dụ để calibrate văn phong.

## Cách dùng

1. Điền `context/author_profile.md`.
2. Điền `context/project_context.md`.
3. Chọn chuẩn trích dẫn trong `context/document_spec.md`.
4. Khi bắt đầu báo cáo, dùng `prompts/start_report.md`.
5. AI phải chạy Question Gate trước khi viết.
6. Ghi nguồn, số liệu và kết quả đo vào `templates/evidence_ledger.csv`.
7. Sau khi có outline mới bắt đầu draft.
8. Chạy `prompts/reviewer.md` trước bản cuối.

## Nguyên tắc quan trọng

"Human-like" không có nghĩa là cố tình viết sai, viết vụng hoặc tạo lỗi chính tả. Văn phong tự nhiên phải đến từ:
- tiếng nói tác giả ổn định;
- lập luận có mục đích;
- câu dài/ngắn thay đổi theo nội dung;
- thuật ngữ được dùng nhất quán;
- mức độ chắc chắn phù hợp với bằng chứng;
- có giới hạn và điều kiện áp dụng;
- không cố "làm màu" bằng từ ngữ học thuật.

