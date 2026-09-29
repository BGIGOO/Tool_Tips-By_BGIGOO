import sys
import time
import logging
from pathlib import Path
from typing import List, Union, Optional, Any
from google import genai
from google.genai import errors, models

# Tắt cảnh báo AFC nội bộ không cần thiết của google-genai
models.logger.setLevel(logging.ERROR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.config import (
    GEMINI_API_KEY,
    MODEL_PRIORITY,
    MAX_RETRIES,
    INITIAL_RETRY_DELAY,
)


def get_genai_client() -> genai.Client:
    """Khởi tạo và trả về Google GenAI Client."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "Chưa cấu hình GEMINI_API_KEY! Vui lòng điền API Key vào file .env"
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def call_gemini_with_fallback(
    client: genai.Client,
    contents: Union[str, List[Any]],
    system_instruction: Optional[str] = None,
    preferred_model: Optional[str] = None,
) -> str:
    """
    Gọi Gemini API với cơ chế tự động thử lại (Retry) và chuyển đổi Model (Fallback)
    khi gặp lỗi 503 (High Demand) hoặc 429 (Rate Limit / Quota).
    """
    models_to_try = []
    if preferred_model:
        models_to_try.append(preferred_model)
    for m in MODEL_PRIORITY:
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = None

    for model_name in models_to_try:
        delay = INITIAL_RETRY_DELAY
        print(f"[AI] Đang kết nối tới mô hình: {model_name}...")

        # Với lỗi 429 (Rate limit), không retry quá nhiều lần trên cùng 1 model để tránh kẹt
        max_attempts = MAX_RETRIES

        for attempt in range(1, max_attempts + 1):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                )
                if response and response.text:
                    print(f"[AI] Hoàn thành phân tích thành công bằng model: {model_name}!")
                    return response.text
                else:
                    raise RuntimeError("Gemini trả về kết quả rỗng.")

            except errors.APIError as e:
                last_error = e
                status_code = getattr(e, "code", None) or getattr(e, "status_code", None)
                err_str = str(e)

                # Trường hợp 1: 429 Quota / Rate Limit (Hết hạn ngạch token trong phút)
                if status_code == 429 or "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    print(
                        f"[Warning] Model {model_name} chạm ngưỡng giới hạn hạn ngạch (429 Rate Limit/Quota). "
                        f"Chuyển ngay sang model tiếp theo có quota khả dụng..."
                    )
                    break  # Chuyển ngay sang model dự phòng tiếp theo để không làm người dùng phải chờ

                # Trường hợp 2: 503 Server High Demand (Máy chủ Google quá tải tạm thời)
                elif status_code == 503 or "503" in err_str or "UNAVAILABLE" in err_str:
                    if attempt < max_attempts:
                        print(
                            f"[Warning] Model {model_name} đang chịu tải cao (503 High Demand). "
                            f"Thử lại lần {attempt}/{max_attempts} sau {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay *= 1.8
                        continue
                    else:
                        print(f"[Warning] Model {model_name} tạm thời không khả dụng sau {max_attempts} lần thử.")
                        break

                # Trường hợp 3: 404 Model Not Found
                elif status_code == 404 or "404" in err_str:
                    print(f"[Warning] Model {model_name} không khả dụng (404). Chuyển sang model dự phòng...")
                    break

                else:
                    print(f"[Error] Lỗi API từ model {model_name}: {e}")
                    break

            except Exception as e:
                last_error = e
                print(f"[Error] Lỗi không xác định khi gọi {model_name}: {e}")
                break

    raise RuntimeError(
        f"Tất cả các model Gemini đều không phản hồi thành công. Lỗi cuối: {last_error}"
    )


def summarize_audio(
    audio_path: Path,
    prompt: str,
    preferred_model: Optional[str] = None,
) -> str:
    """
    Tải file âm thanh lên Gemini File API, phân tích và trả về bản tóm tắt học thuật.
    Tự động xóa file trên cloud sau khi xử lý xong.
    """
    client = get_genai_client()
    uploaded_file = None

    try:
        print(f"[Upload] Đang tải luồng âm thanh lên Gemini File API: {audio_path.name}...")
        uploaded_file = client.files.upload(file=str(audio_path))
        print(f"[Upload] File đã tải lên thành công. Trạng thái: {uploaded_file.state}")

        # Đợi file sẵn sàng nếu đang ở trạng thái PROCESSING
        max_wait = 30
        waited = 0
        while uploaded_file.state == "PROCESSING" and waited < max_wait:
            time.sleep(2)
            waited += 2
            uploaded_file = client.files.get(name=uploaded_file.name)

        print("[AI] Bắt đầu quá trình phân tích tín hiệu âm thanh và tổng hợp học thuật...")
        contents = [uploaded_file, prompt]
        summary_result = call_gemini_with_fallback(
            client=client,
            contents=contents,
            preferred_model=preferred_model,
        )
        return summary_result

    finally:
        if uploaded_file and hasattr(uploaded_file, "name"):
            try:
                print(f"[Cleanup] Đang dọn dẹp file tạm trên Cloud ({uploaded_file.name})...")
                client.files.delete(name=uploaded_file.name)
                print("[Cleanup] Đã dọn dẹp Cloud storage an toàn.")
            except Exception as e:
                print(f"[Warning] Không thể xóa file tạm trên Cloud: {e}")


def summarize_transcript(
    transcript: str,
    prompt: str,
    preferred_model: Optional[str] = None,
) -> str:
    """
    Tóm tắt trực tiếp từ bản chép lời (transcript thủ công).
    """
    client = get_genai_client()
    full_prompt = f"{prompt}\n\n---\n### DƯỚI ĐÂY LÀ TOÀN BỘ NỘI DUNG BÀI GIẢNG (TRANSCRIPT):\n{transcript}"
    print("[AI] Bắt đầu tổng hợp từ bản transcript chuẩn...")
    return call_gemini_with_fallback(
        client=client,
        contents=full_prompt,
        preferred_model=preferred_model,
    )
