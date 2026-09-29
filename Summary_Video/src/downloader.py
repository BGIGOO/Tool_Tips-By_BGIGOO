import sys
import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import yt_dlp

from src.config import TEMP_AUDIO_DIR

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def sanitize_filename(name: str) -> str:
    """Loại bỏ ký tự không hợp lệ trên Windows filesystem."""
    clean = re.sub(r'[\\/*?:"<>|]', "", name)
    clean = re.sub(r"\s+", "_", clean).strip("_")
    return clean[:80]  # Giới hạn độ dài tên file an toàn


def get_video_metadata(url: str) -> Dict[str, Any]:
    """Lấy thông tin cơ bản của video mà không tải xuống."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "id": info.get("id"),
            "title": info.get("title", "Unknown Title"),
            "uploader": info.get("uploader", "Unknown Channel"),
            "duration": info.get("duration", 0),
            "description": info.get("description", ""),
            "subtitles": info.get("subtitles", {}),
            "automatic_captions": info.get("automatic_captions", {}),
            "webpage_url": info.get("webpage_url", url),
        }


def check_manual_subtitles(metadata: Dict[str, Any], preferred_langs=("vi", "en")) -> Optional[str]:
    """
    Kiểm tra xem video có Manual Subtitles (phụ đề do người tải lên) hay không.
    Trả về mã ngôn ngữ phù hợp nhất nếu có.
    """
    subs = metadata.get("subtitles", {})
    if not subs:
        return None

    # Tìm theo thứ tự ưu tiên: vi -> en -> các thứ tiếng khác
    for lang in preferred_langs:
        for sub_lang in subs.keys():
            if sub_lang.startswith(lang):
                return sub_lang

    # Nếu có sub bất kỳ do người tải lên
    if len(subs) > 0:
        return next(iter(subs.keys()))

    return None


def download_manual_subtitles(url: str, lang: str) -> Optional[str]:
    """Tải và parse phụ đề thủ công thành văn bản thuần."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "writesubtitles": True,
        "subtitleslangs": [lang],
        "subtitlesformat": "json3/vtt/srt",
        "outtmpl": str(TEMP_AUDIO_DIR / "%(id)s.%(ext)s"),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subs = info.get("subtitles", {}).get(lang, [])
            # Tìm link format json3 hoặc vtt
            json3_url = next((s["url"] for s in subs if s.get("ext") == "json3"), None)
            vtt_url = next((s["url"] for s in subs if s.get("ext") == "vtt"), None)
            
            import urllib.request
            target_url = json3_url or vtt_url
            if target_url:
                req = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req) as response:
                    content = response.read().decode("utf-8", errors="ignore")
                    
                    if json3_url:
                        data = json.loads(content)
                        lines = []
                        for event in data.get("events", []):
                            segs = event.get("segs", [])
                            text = "".join([s.get("utf8", "") for s in segs]).strip()
                            if text:
                                lines.append(text)
                        return "\n".join(lines)
                    else:
                        # VTT format: loại bỏ header và timestamp
                        cleaned_lines = []
                        for line in content.splitlines():
                            line = line.strip()
                            if not line or "-->" in line or line.startswith("WEBVTT") or line.isdigit():
                                continue
                            cleaned_lines.append(line)
                        return "\n".join(cleaned_lines)
    except Exception as e:
        print(f"[Warning] Không thể trích xuất phụ đề thủ công: {e}")
    return None


def download_audio_stream(url: str, video_id: str, title: str) -> Path:
    """
    Tải luồng audio nhẹ (.m4a) trực tiếp từ YouTube DASH stream.
    Không yêu cầu cài đặt ffmpeg.
    """
    clean_title = sanitize_filename(title)
    output_filename = f"{clean_title}_{video_id}.m4a"
    output_path = TEMP_AUDIO_DIR / output_filename

    # Nếu file đã tồn tại và kích thước > 0 thì tái sử dụng
    if output_path.exists() and output_path.stat().st_size > 1024:
        print(f"[Info] File audio đã có sẵn trong cache: {output_path.name}")
        return output_path

    print(f"[Download] Đang tải luồng âm thanh nhẹ (.m4a) cho: {title}...")
    
    # Định dạng m4a native không cần ffmpeg merge
    ydl_opts = {
        "format": "140/ba[ext=m4a]/ba",  # itag 140 là standard 128k AAC audio của YouTube
        "outtmpl": str(output_path),
        "quiet": False,
        "no_warnings": True,
        "nocheckcertificate": True,
        "prefer_insecure": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError(f"Không thể tải file âm thanh cho video: {url}")

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[Success] Tải thành công file audio: {output_path.name} ({size_mb:.2f} MB)")
    return output_path


def process_video_source(url: str, force_audio: bool = False) -> Dict[str, Any]:
    """
    Hàm điều phối thông minh:
    1. Lấy metadata.
    2. Nếu không force_audio, kiểm tra có Manual Sub không.
    3. Nếu có Manual Sub -> Tải text phụ đề.
    4. Nếu không -> Tải luồng audio .m4a.
    """
    metadata = get_video_metadata(url)
    video_id = metadata["id"]
    title = metadata["title"]

    if not force_audio:
        manual_lang = check_manual_subtitles(metadata)
        if manual_lang:
            print(f"[Info] Phát hiện phụ đề thủ công chuẩn ({manual_lang}) do tác giả tải lên!")
            transcript = download_manual_subtitles(url, manual_lang)
            if transcript and len(transcript.strip()) > 100:
                return {
                    "source_type": "transcript",
                    "content": transcript,
                    "language": manual_lang,
                    "metadata": metadata,
                }
            print("[Warning] Không tải được phụ đề thủ công đầy đủ, tự động fallback sang Audio Stream.")

    # Fallback to audio stream
    audio_path = download_audio_stream(url, video_id, title)
    return {
        "source_type": "audio",
        "audio_path": audio_path,
        "metadata": metadata,
    }
