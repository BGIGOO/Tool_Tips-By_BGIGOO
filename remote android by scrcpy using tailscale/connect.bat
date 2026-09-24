@echo off
chcp 65001 >nul
title Scrcpy Remote via Tailscale

:: ====================================================================
:: CẤU HÌNH THIẾT BỊ MẶC ĐỊNH
:: Thay đổi địa chỉ IP Tailscale hoặc MagicDNS hostname của bạn tại đây:
set "DEFAULT_DEVICE=100.82.51.71:5555"
:: ====================================================================

echo ======================================================================
echo           📱 REMOTE ANDROID VIA SCRCPY OVER TAILSCALE
echo ======================================================================
echo.
echo Thiết bị mặc định: %DEFAULT_DEVICE%
set /p TARGET="Nhập IP/Hostname thiết bị (Nhấn Enter để dùng mặc định): "

if "%TARGET%"=="" set "TARGET=%DEFAULT_DEVICE%"

:: Nếu người dùng không nhập kèm port 5555, tự động nối thêm :5555
echo %TARGET% | findstr /C:":5555" >nul
if errorlevel 1 (
    set "TARGET=%TARGET%:5555"
)

echo.
echo [1/3] Đang kiểm tra kết nối ADB đến: %TARGET%...
adb connect %TARGET%

echo.
echo [2/3] Danh sách thiết bị hiện tại:
adb devices

echo.
echo [3/3] Đang khởi chạy Scrcpy với các cờ tối ưu hóa:
echo       --stay-awake       : Giữ máy không ngủ
echo       --turn-screen-off  : Tắt màn hình vật lý (tiết kiệm pin & bảo mật)
echo       --no-audio         : Tắt âm thanh (tránh lỗi Demuxer & giảm lag)
echo       -b 4M              : Giới hạn bitrate 4Mbps mượt mà
echo.
scrcpy -s %TARGET% --stay-awake --turn-screen-off --no-audio -b 4M

echo.
echo Phiên làm việc đã kết thúc.
pause
