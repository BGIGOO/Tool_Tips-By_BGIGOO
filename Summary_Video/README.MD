# 🎓 Academic YouTube Summarizer (Tóm Tắt Video Học Thuật Chuyên Sâu)

> Công cụ tóm tắt video học thuật, bài giảng kỹ thuật, công nghệ và bảo mật từ YouTube bằng cách kết hợp **yt-dlp** và **Gemini Native Audio Understanding (File API)**, loại bỏ hoàn toàn lỗi nhận diện sai thuật ngữ của phụ đề tự động (Auto-generated captions).

---

## 🎯 Vấn Đề Giải Quyết
Các extension trình duyệt thông thường chỉ cào lớp phụ đề tự động (Auto-generated CC) của YouTube. Khi video chứa nhiều thuật ngữ chuyên ngành (Bảo mật, Khoa học máy tính, Toán học, Y khoa...), phụ đề tự động thường:
- Bị kiểm duyệt/thay thế từ ngữ nhạy cảm thành `[ __ ]`.
- Nghe nhầm thuật ngữ (ví dụ: *CSRF* thành *sea surf*, *buffer overflow* thành *buffy over flow*).
- Không có dấu chấm phẩy, ngắt câu sai làm biến đổi ý nghĩa bài học.

**Academic YouTube Summarizer** giải quyết bằng cách:
1. **Kiểm tra phụ đề thủ công (Manual CC)**: Nếu tác giả có tải phụ đề chuẩn lên thì dùng trực tiếp (nhanh, 0 tốn dung lượng).
2. **Native Audio Processing (Fallback thông minh)**: Nếu chỉ có phụ đề tự động, công cụ trích xuất stream audio `.m4a` siêu nhẹ và gửi trực tiếp vào **Gemini File API**. Mô hình Gemini sẽ "nghe" trực tiếp giọng diễn giả và bóc tách nội dung với độ chính xác cao nhất.

---

## 📑 Tài Liệu Kế Hoạch & Kiến Trúc
Xem chi tiết kế hoạch thiết kế và lộ trình triển khai tại:
👉 **[Kế hoạch triển khai chi tiết (PLAN.md)](./PLAN.md)**

---

## 🚀 Dự Kiến Cách Sử Dụng

```bash
# 1. Cài đặt thư viện
pip install -r requirements.txt

# 2. Cấu hình Gemini API Key
cp .env.example .env
# Điền GEMINI_API_KEY vào .env

# 3. Chạy tóm tắt video
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Bản tóm tắt chuẩn học thuật sẽ được lưu tự động tại thư mục `outputs/`.
