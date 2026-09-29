import sys
import argparse
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Ensure UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.downloader import process_video_source
from src.gemini_service import summarize_audio, summarize_transcript
from src.prompt_templates import format_academic_prompt
from src.utils import format_duration, save_markdown_report


def print_banner():
    banner = r"""
========================================================================
   🎓 ACADEMIC YOUTUBE SUMMARIZER (Powered by Gemini Multimodal)
   Loại bỏ lỗi nhận diện Auto-Caption • Tóm tắt chuyên sâu học thuật
========================================================================
"""
    print(banner)


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="Tóm tắt video học thuật YouTube với Gemini Multimodal (Audio & Transcript)"
    )
    parser.add_argument(
        "url",
        type=str,
        help="URL video YouTube cần tóm tắt (ví dụ: https://www.youtube.com/watch?v=...)",
    )
    parser.add_argument(
        "--force-audio",
        action="store_true",
        help="Bắt buộc tải và nghe trực tiếp luồng Audio qua Gemini, bỏ qua Subtitle",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="Tiếng Việt",
        help="Ngôn ngữ đầu ra của bài tóm tắt (Mặc định: 'Tiếng Việt')",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Tên mô hình Gemini tùy chọn (ví dụ: gemini-3.8-flash, gemini-3.1-flash-lite-preview)",
    )

    args = parser.parse_args()
    url = args.url.strip()

    start_time = time.time()

    try:
        # Bước 1: Trích xuất và phân tích nguồn dữ liệu
        print(f"[*] Đang phân tích video: {url}")
        process_result = process_video_source(url, force_audio=args.force_audio)
        metadata = process_result["metadata"]
        source_type = process_result["source_type"]

        duration_str = format_duration(metadata.get("duration", 0))
        print(f"\n[+] Tiêu đề: {metadata.get('title')}")
        print(f"[+] Kênh: {metadata.get('uploader')}")
        print(f"[+] Thời lượng: {duration_str}")
        print(f"[+] Phương thức xử lý: {source_type.upper()}")

        # Bước 2: Chuẩn bị Prompt học thuật
        prompt = format_academic_prompt(
            video_title=metadata.get("title", ""),
            uploader=metadata.get("uploader", ""),
            duration=duration_str,
            url=metadata.get("webpage_url", url),
            target_language=args.lang,
        )

        # Bước 3: Gửi qua Gemini API
        print("\n[*] Đang gửi dữ liệu tới Gemini để phân tích học thuật...")
        if source_type == "audio":
            audio_path = process_result["audio_path"]
            summary = summarize_audio(
                audio_path=audio_path,
                prompt=prompt,
                preferred_model=args.model,
            )
        else:
            transcript = process_result["content"]
            summary = summarize_transcript(
                transcript=transcript,
                prompt=prompt,
                preferred_model=args.model,
            )

        # Bước 4: Lưu file kết quả
        output_file = save_markdown_report(
            summary_text=summary,
            metadata=metadata,
            source_type=source_type,
        )

        elapsed = time.time() - start_time
        print("\n" + "=" * 72)
        print(f"[SUCCESS] Hoàn thành tóm tắt trong {elapsed:.1f} giây!")
        print(f"[OUTPUT] Báo cáo đã được lưu tại:\n👉 {output_file.resolve()}")
        print("=" * 72)

    except KeyboardInterrupt:
        print("\n[!] Đã hủy quá trình bởi người dùng.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Xảy ra lỗi trong quá trình thực thi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
