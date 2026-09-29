# 📋 KẾ HOẠCH TRIỂN KHAI: HỆ THỐNG TÓM TẮT VIDEO HỌC THUẬT YOUTUBE (ACADEMIC YOUTUBE SUMMARIZER)

> **Mục tiêu**: Xây dựng công cụ tóm tắt video YouTube chuyên sâu (bài giảng, talk kỹ thuật, hội thảo bảo mật/công nghệ) khắc phục triệt để hiện tượng sai lệch thuật ngữ chuyên ngành do Auto-caption của YouTube, bằng cách kết hợp **yt-dlp** và **Gemini Native Audio Understanding (File API)**.

---

## 1. 🔍 Phân Tích Thực Trạng & So Sánh Giải Pháp

### 1.1. Căn nguyên lỗi của các Extension hiện tại
- **Extension thông thường** (như *YouTube Summary with ChatGPT & Claude*): Chỉ cào lớp text phụ đề có sẵn (thường là Auto-generated STT của YouTube).
- **Hạn chế nghiêm trọng đối với nội dung học thuật**:
  - Bị che các từ nhạy cảm / chửi thề hoặc nhận diện sai thành `[ __ ]`.
  - Nuốt âm, mất dấu câu, ngắt câu sai dẫn đến đảo ngược logic câu lệnh/khái niệm.
  - Nhận nhầm các thuật ngữ chuyên ngành (ví dụ: `XSS` thành `excess`, `CSRF` thành `sea surf`, `heap spraying` thành `deep spring`...).
  - **Hệ quả**: "Garbage In, Garbage Out" — Dù dùng model mạnh nhất (GPT-4o, Claude 3.5 Sonnet hay Gemini 3.8), bản tóm tắt vẫn bị sai lệch hoàn toàn về bản chất kỹ thuật.

---

### 1.2. Bảng So Sánh Các Hướng Đi

| Tiêu chí | Cào Auto-Sub + LLM (Extension) | Chạy Local Whisper + LLM | Gemini Native Audio (Đề xuất ⭐) |
| :--- | :--- | :--- | :--- |
| **Độ chính xác thuật ngữ** | ❌ Kém (phụ thuộc sub YouTube) | ✔️ Rất cao (Whisper large-v3) | ⭐ Cực cao (Gemini nghe trực tiếp) |
| **Yêu cầu phần cứng** | Siêu nhẹ | Nặng (GPU VRAM > 6GB, PyTorch) | Siêu nhẹ (Xử lý trên Cloud) |
| **Cài đặt & Phụ thuộc** | Cài extension trình duyệt | Phức tạp (Cần ffmpeg, Torch, C++) | Rất đơn giản (`yt-dlp` + SDK Gemini) |
| **Tốc độ xử lý** | Vài giây | 2 - 10 phút tùy độ dài | 15 - 30 giây cho video 1 tiếng |
| **Chi phí** | Miễn phí | Miễn phí (tốn điện/GPU) | Miễn phí (Free Tier Google AI Studio) |
| **Khả năng hiểu ngữ cảnh** | Chỉ có chữ bị lỗi | Chỉ có chữ (đúng hơn) | Hiểu cả ngữ điệu, nhấn nhá, đa ngôn ngữ |

---

## 2. 🏗️ Kiến Trúc Hệ Thống Đề Xuất (Hybrid Smart Pipeline)

Hệ thống hoạt động theo nguyên lý **"Smart Fallback"**:

```mermaid
graph TD
    A[Nhập YouTube URL] --> B[Kiểm tra Metadata & Subtitles bằng yt-dlp]
    B --> C{Có Manual Subtitles<br/>do tác giả tải lên?}
    
    C -- Có (Chuẩn xác 100%) --> D[Trích xuất Manual Subtitle]
    C -- Không (Chỉ có Auto-Sub) --> E[Tải Audio Stream nén .m4a]
    
    E --> F[Upload Audio lên Gemini File API]
    D --> G[Gửi Transcript kèm Academic Prompt vào Gemini]
    F --> H[Gọi Gemini tóm tắt trực tiếp từ Audio Stream]
    
    G --> I[Format Markdown: Key Takeaways, Deep Dive, Code/Formula, Glossary]
    H --> I
    I --> J[Lưu vào thư mục /outputs/ dưới dạng .md]
```

### Điểm đột phá kỹ thuật:
1. **Không cần cài đặt FFmpeg phức tạp**: YouTube lưu sẵn các luồng audio DASH định dạng `.m4a` (AAC codec). `yt-dlp` có thể trích xuất trực tiếp stream audio này mà không cần re-encode hay gọi FFmpeg. Dung lượng chỉ khoảng **15 - 30 MB cho 1 video 60 phút**.
2. **Gemini File API hỗ trợ Native Audio**: Đẩy thẳng file `.m4a` lên Google AI Studio. Gemini nghe trực tiếp từng giây của audio, bắt trúng các từ ngữ chuyên ngành tiếng Anh/Việt.
3. **Tiết kiệm tài nguyên tối đa**: Nếu video của các trường đại học lớn (MIT, Stanford) hoặc hội nghị lớn (DEF CON, Black Hat) đã có phụ đề thủ công (Manual CC), hệ thống chỉ tải text (vài KB), không cần tải audio.

---

## 3. 📂 Cấu Trúc Dự Án Trong Thư Mục `Summary_Video`

```
Summary_Video/
├── .env.example              # Mẫu cấu hình API Key (GEMINI_API_KEY)
├── .env                      # File chứa API Key cá nhân (được gitignore)
├── .gitignore                # Bỏ qua file audio tạm và .env
├── requirements.txt          # Các thư viện Python nhẹ (yt-dlp, google-genai, python-dotenv)
├── PLAN.md                   # Bản kế hoạch chi tiết (File này)
├── README.MD                 # Hướng dẫn sử dụng & Kiến trúc tổng quan
├── src/
│   ├── __init__.py
│   ├── config.py             # Quản lý cấu hình & Model settings
│   ├── downloader.py         # Module lấy sub thủ công hoặc tải audio stream .m4a
│   ├── gemini_service.py     # Module upload File API và tương tác với Gemini
│   ├── prompt_templates.py   # Bộ prompt chuyên biệt cho Academic/Tech Summary
│   └── utils.py              # Xử lý lưu file markdown, sanitize tên file
├── outputs/                  # Thư mục chứa các file .md tóm tắt kết quả
└── main.py                   # Điểm khởi chạy CLI (python main.py <URL>)
```

---

## 4. 🗓️ Kế Hoạch Triển Khai Chi Tiết (Roadmap)

### Giai Đoạn 1: Chuẩn Bị & Khởi Tạo Môi Trường (ĐÃ HOÀN THÀNH ✅)
- [x] Tạo tài liệu kiến trúc & kế hoạch (`PLAN.md`).
- [x] Tạo file cấu hình `requirements.txt` (`yt-dlp`, `google-genai`, `python-dotenv`).
- [x] Hướng dẫn lấy và thiết lập `GEMINI_API_KEY` từ Google AI Studio (đã cấu hình an toàn trong `.env`).
- [x] Thiết lập file `.gitignore` để không commit cache, audio tạm, hay API key.

### Giai Đoạn 2: Xây Dựng Core Modules (ĐÃ HOÀN THÀNH ✅)
- [x] **`src/downloader.py`**:
  - Dùng `yt-dlp` lấy metadata (Title, Channel, Duration, Description) với cờ `noplaylist: True`.
  - Tự động kiểm tra phụ đề: nếu có phụ đề thủ công chuẩn (en, vi...) -> trích xuất trực tiếp transcript.
  - Tải luồng audio stream định dạng `.m4a` native siêu nhẹ (AAC) mà KHÔNG cần cài đặt FFmpeg.
- [x] **`src/gemini_service.py`**:
  - Kết nối với Google GenAI SDK (`google-genai`).
  - Xử lý upload file âm thanh qua File API với cơ chế polling trạng thái `ACTIVE`.
  - Tự động xóa file trên cloud (`client.files.delete`) ngay sau khi tóm tắt xong để bảo vệ quota.
  - Tích hợp cơ chế tự động thử lại (Retry) với exponential backoff và chuyển đổi Model Fallback khi gặp lỗi 503/429.

### Giai Đoạn 3: Thiết Kế Bộ Prompt Học Thuật (ĐÃ HOÀN THÀNH ✅)
- [x] Xây dựng cấu trúc bản tóm tắt chuẩn hóa trong `src/prompt_templates.py`:
  1. **Executive Summary (TL;DR)**
  2. **Core Concepts & Frameworks**
  3. **Technical Glossary** (Bảng thuật ngữ đối chiếu)
  4. **Detailed Breakdown with Timestamps**
  5. **Code, Formulas & Technical Mechanics**
  6. **Critical Insights & Actionable Takeaways**

### Giai Đoạn 4: CLI Interface & Kiểm Thử Toàn Diện (ĐÃ HOÀN THÀNH ✅)
- [x] Viết `main.py` nhận tham số dòng lệnh:
  - `python main.py <URL>`
  - Tùy chọn `--force-audio`: Bắt buộc nghe audio trực tiếp qua Gemini.
  - Tùy chọn `--lang`: Ngôn ngữ xuất bản tóm tắt (Mặc định: Tiếng Việt).
  - Tùy chọn `--model`: Chỉ định model cụ thể nếu muốn.
- [x] Khắc phục triệt để lỗi mã hóa `UnicodeEncodeError` trên Windows Console.
- [x] Chạy kiểm thử End-to-End thành công cả luồng tải audio, upload File API và xuất bản báo cáo Markdown vào `outputs/`.

### Giai Đoạn 5: Mở Rộng (Tùy Chọn Tương Lai)
- [ ] Giao diện WebUI đơn giản bằng Streamlit / Gradio (chỉ cần dán link và bấm nút).
- [ ] Tích hợp xuất trực tiếp sang Notion hoặc Obsidian Vault.
