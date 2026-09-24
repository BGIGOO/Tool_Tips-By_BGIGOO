# 📱 Điều Khiển Từ Xa Android Qua Scrcpy Trên Nền Tảng Tailscale Mesh VPN

[![Tailscale](https://img.shields.io/badge/Network-Tailscale%20Mesh%20VPN-blue?logo=tailscale&logoColor=white)](https://tailscale.com/)
[![Scrcpy](https://img.shields.io/badge/Engine-Scrcpy%20v2.0%2B-orange?logo=android&logoColor=white)](https://github.com/Genymobile/scrcpy)
[![Security](https://img.shields.io/badge/Security-WireGuard%20Protocol-darkgreen?logo=wireguard&logoColor=white)](https://www.wireguard.com/)
[![OS](https://img.shields.io/badge/OS-Android%20%7C%20ColorOS%20%7C%20OneUI%20%7C%20MIUI-green?logo=android)](https://www.android.com/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/Genymobile/scrcpy)

> **Mục tiêu kỹ thuật:** Thiết lập kênh điều khiển từ xa thiết bị Android thông qua mạng Internet bằng cách kết hợp **Scrcpy** (truyền luồng video qua giao thức ADB với độ trễ danh định 35–70 ms) và **Tailscale** (mạng riêng ảo Mesh VPN xây dựng trên giao thức WireGuard).
> 
> **Đặc tính kỹ thuật:** Không yêu cầu mở cổng (Port Forwarding) trên router biên, hoạt động trong môi trường CGNAT thông qua cơ chế NAT traversal (hoặc DERP relay), mã hóa lưu lượng bằng WireGuard.

---

## 📖 Mục Lục

- [1. Mô Hình Kiến Trúc & Cơ Chế Hoạt Động](#1-mô-hình-kiến-trúc--cơ-chế-hoạt-động)
  - [1.1 Sơ đồ kết nối mạng](#11-sơ-đồ-kết-nối-mạng)
  - [1.2 Cơ chế kỹ thuật cốt lõi](#12-cơ-chế-kỹ-thuật-cốt-lõi)
  - [1.3 Bảng so sánh các phương thức kết nối](#13-bảng-so-sánh-các-phương-thức-kết-nối)
- [2. Yêu Cầu Môi Trường & Công Cụ](#2-yêu-cầu-môi-trường--công-cụ)
- [3. Quy Trình Cấu Hình Từng Bước](#3-quy-trình-cấu-hình-từng-bước)
  - [Bước 1: Cấu hình hệ điều hành Android (ColorOS / Android thuần)](#bước-1-cấu-hình-hệ-điều-hành-android-coloros--android-thuần)
  - [Bước 2: Cài đặt và cấu hình duy trì node trên Tailscale](#bước-2-cài-đặt-và-cấu-hình-duy-trì-node-trên-tailscale)
  - [Bước 3: Khởi tạo kết nối ADB TCP/IP qua cổng 5555](#bước-3-khởi-tạo-kết-nối-adb-tcpip-qua-cổng-5555)
  - [Bước 4: Thiết lập kết nối và khởi chạy phiên Scrcpy](#bước-4-thiết-lập-kết-nối-và-khởi-chạy-phiên-scrcpy)
- [4. Tham Số Tối Ưu Hóa & Phím Tắt](#4-tham-số-tối-ưu-hóa--phím-tắt)
- [5. Kịch Bản Tự Động Hóa Cho Windows (`connect.bat`)](#5-kịch-bản-tự-động-hóa-cho-windows-connectbat)
- [6. Phân Tích & Xử Lý Sự Cố Thường Gặp](#6-phân-tích--xử-lý-sự-cố-thường-gặp)
- [7. Phân Tích Kỹ Thuật Chuyên Sâu Về Mạng Tailscale](#7-phân-tích-kỹ-thuật-chuyên-sâu-về-mạng-tailscale)

---

## 1. Mô Hình Kiến Trúc & Cơ Chế Hoạt Động

### 1.1 Sơ Đồ Kết Nối Mạng

```mermaid
graph LR
    subgraph Client ["💻 Máy Tính Điều Khiển (Client)"]
        direction TB
        PC_App["Scrcpy / ADB Client"]
        PC_TS["Tailscale Daemon (WireGuard)"]
        PC_IP["IP: 100.80.20.10 (Mạng ngoài/Internet)"]
    end

    subgraph Coord ["🌐 Tailscale Control Plane"]
        TS_Server["Coordination Server (Discovery & Key Exchange)"]
    end

    subgraph Host ["📱 Thiết Bị Android (Host / Mạng Nội Bộ)"]
        direction TB
        Phone_TS["Tailscale App (Always-on VPN)"]
        Phone_ADB["ADB Daemon (TCP Port 5555)"]
        Phone_IP["IP: 100.80.20.20 (Sau NAT/Router)"]
    end

    PC_App -->|Socket nội bộ| PC_TS
    PC_TS -.->|1. Trao đổi Public Key & STUN Endpoint| TS_Server
    Phone_TS -.->|1. Trao đổi Public Key & STUN Endpoint| TS_Server

    PC_TS ===|2. Kênh truyền WireGuard P2P (UDP Hole Punching)| Phone_TS
    Phone_TS -->|Loopback nội bộ| Phone_ADB
```

### 1.2 Cơ Chế Kỹ Thuật Cốt Lõi

1. **Phân tách Mặt phẳng Điều khiển (Control Plane) và Mặt phẳng Dữ liệu (Data Plane)**:
   - **Control Plane**: Máy chủ điều phối trung tâm (Coordination Server) của Tailscale quản lý việc xác thực danh tính, trao đổi khóa công khai (Public Key) và ánh xạ endpoint giữa các thiết bị. Máy chủ này không chuyển tiếp hay đọc nội dung lưu lượng người dùng (payload).
   - **Data Plane**: Lưu lượng dữ liệu thực tế (luồng video, âm thanh, tín hiệu điều khiển ADB) được mã hóa bằng giao thức WireGuard và truyền trực tiếp giữa client và host theo mô hình ngang hàng (Peer-to-Peer - P2P).
2. **Cơ chế Vượt Tường Lửa (NAT Traversal)**:
   - Hai node sử dụng giao thức dạng STUN gửi gói tin UDP ra máy chủ điều phối để xác định địa chỉ IP công khai và cổng NAT được ánh xạ.
   - Các node thực hiện kỹ thuật đục lỗ UDP (UDP Hole Punching) đồng thời để tạo kết nối P2P trực tiếp qua router và hạ tầng CGNAT.
   - **Cơ chế dự phòng (Fallback)**: Trong trường hợp môi trường mạng áp dụng NAT đối xứng (Symmetric NAT) ngăn chặn việc đục lỗ P2P, Tailscale tự động chuyển tiếp gói tin qua máy chủ chuyển tiếp mã hóa **DERP Relay** (ví dụ cụm máy chủ tại khu vực địa lý gần nhất) nhằm duy trì kết nối.
3. **Cơ chế Truyền Luồng Của Scrcpy**:
   - Client nạp một file thực thi Java (`scrcpy-server.jar`) lên thiết bị Android qua socket ADB.
   - Máy chủ này đọc dữ liệu hiển thị từ hệ thống đồ họa của Android (`SurfaceFlinger`), mã hóa phần cứng bằng bộ nén H.264/H.265 thông qua `MediaCodec` và truyền gói dữ liệu thô qua kết nối TCP cổng 5555. Độ trễ xử lý danh định của Scrcpy nằm trong khoảng 35–70 ms.

### 1.3 Bảng So Sánh Các Phương Thức Kết Nối

| Tiêu Chí | Cáp USB Trực Tiếp | Wi-Fi Cục Bộ (LAN) | Mạng Diện Rộng Qua Tailscale (WAN) |
| :--- | :--- | :--- | :--- |
| **Phạm vi mạng** | Giới hạn theo chiều dài cáp vật lý (thường $\le$ 2 m) | Cùng phân đoạn mạng cục bộ (Subnet / WLAN) | Qua Internet; khả năng kết nối phụ thuộc vào khả năng thiết lập đường hầm giữa các endpoint |
| **Độ trễ** | Khoảng 15–30 ms qua bus USB | Khoảng 30–50 ms trong điều kiện sóng Wi-Fi ổn định và không nghẽn kênh | Khoảng 40–80 ms trong trường hợp thiết lập được kết nối P2P trực tiếp; giá trị thực tế phụ thuộc vị trí mạng và đường truyền |
| **Yêu cầu mở port router** | Không yêu cầu | Không yêu cầu | Không yêu cầu trên router biên đối với hầu hết mô hình NAT; tự động định tuyến qua DERP relay khi gặp Symmetric NAT |
| **Cơ chế bảo vệ** | Giới hạn vật lý trên thiết bị và cổng kết nối | Phụ thuộc vào giao thức bảo mật mạng Wi-Fi (WPA2/WPA3) và chính sách phân tách mạng (AP Isolation) | Mã hóa lưu lượng bằng WireGuard; mức độ bảo vệ phụ thuộc cấu hình endpoint, khóa và chính sách truy cập |
| **Quản trị kết nối** | Yêu cầu kết nối vật lý cố định | Cần duy trì IP tĩnh hoặc cập nhật IP khi DHCP thay đổi địa chỉ | Thiết bị được quản lý thông qua hệ thống nhận diện và cấu hình mạng của Tailscale |

---

## 2. Yêu Cầu Môi Trường & Công Cụ

- **Máy trạm điều khiển (Client)**:
  - Hệ điều hành: Windows 10/11, macOS, hoặc Linux.
  - Công cụ điều khiển: [Scrcpy v2.0+](https://github.com/Genymobile/scrcpy/releases/latest) (khuyến nghị phiên bản 3.1 trở lên để đảm bảo tính ổn định). Thư mục chứa Scrcpy đã bao gồm sẵn các tệp nhị phân `adb.exe`, `scrcpy.exe` và `scrcpy-server`.
  - Ứng dụng mạng: [Tailscale Client](https://tailscale.com/download) tương ứng với hệ điều hành.
- **Thiết bị Android mục tiêu (Host)**:
  - Hệ điều hành: Android 11 trở lên (trong tài liệu này sử dụng thiết bị kiểm thử **OPPO A77s - ColorOS 12/13/14**; các thiết bị chạy Android thuần hoặc OneUI/HyperOS áp dụng các nguyên lý cấu hình tương đương).
  - Ứng dụng mạng: **Tailscale** cài đặt từ Google Play Store hoặc F-Droid.
  - Phụ kiện kết nối: Cáp USB hỗ trợ truyền dữ liệu (Data Cable), chỉ yêu cầu kết nối trong giai đoạn khởi tạo chế độ ADB TCP/IP.

---

## 3. Quy Trình Cấu Hình Từng Bước

### Bước 1: Cấu hình hệ điều hành Android (ColorOS / Android thuần)

Trên các hệ điều hành tùy biến như ColorOS, tiến trình nền của ứng dụng VPN hoặc ADB daemon có thể bị hệ thống quản lý năng lượng (Doze Mode / Background Process Limiter) chấm dứt nhằm tiết kiệm pin. Do đó, cần cấu hình các tham số duy trì hoạt động liên tục:

#### 1. Kích hoạt Developer Options và Gỡ lỗi USB
1. Truy cập **Cài đặt (Settings)** $\rightarrow$ **Giới thiệu về thiết bị (About device)** $\rightarrow$ **Phiên bản (Version)**.
2. Chạm liên tục **7 lần** vào mục **Số bản dựng (Build number)** cho đến khi xuất hiện thông báo xác nhận quyền nhà phát triển.
3. Quay lại **Cài đặt** $\rightarrow$ **Cài đặt hệ thống (System settings)** $\rightarrow$ **Tùy chọn cho nhà phát triển (Developer options)**.
4. Bật tùy chọn **Gỡ lỗi USB (USB Debugging)** và xác nhận hộp thoại cảnh báo.

#### 2. Cấp quyền nhập lệnh điều khiển từ xa (Bắt buộc trên ColorOS / OxygenOS)
> [!IMPORTANT]
> Nếu tùy chọn **Tắt giám sát quyền** không được kích hoạt, hệ điều hành sẽ chỉ cho phép truyền luồng hình ảnh chiều đi; toàn bộ thao tác mô phỏng cảm ứng từ chuột hoặc nhập phím từ xa sẽ bị hệ thống ColorOS từ chối.
- Trong giao diện **Tùy chọn cho nhà phát triển**, cuộn xuống và kích hoạt tùy chọn **Tắt giám sát quyền (Disable permission monitoring)**.
- Kích hoạt tùy chọn **Không khóa màn hình khi sạc (Stay awake)** để ngăn hệ thống chuyển sang trạng thái ngủ sâu khi duy trì nguồn sạc cố định.

#### 3. Cấu hình miễn trừ tối ưu hóa pin cho tiến trình Tailscale
- **Quản lý sử dụng pin**: Truy cập **Cài đặt** $\rightarrow$ **Pin (Battery)** $\rightarrow$ **Cài đặt khác** $\rightarrow$ **Tối ưu hóa mức sử dụng pin (Optimize battery use)** $\rightarrow$ Chọn **Tailscale** $\rightarrow$ Thiết lập sang **Không tối ưu hóa (Don't optimize)**.
- **Quyền thực thi nền**: Truy cập **Cài đặt** $\rightarrow$ **Ứng dụng** $\rightarrow$ **Quản lý ứng dụng** $\rightarrow$ **Tailscale** $\rightarrow$ **Mức sử dụng pin** $\rightarrow$ Kích hoạt:
  - `Cho phép hoạt động ở chế độ nền (Allow background activity)`.
  - `Cho phép tự khởi chạy (Allow auto-launch)`.
- **Khóa tiến trình trong bộ nhớ**: Mở giao diện quản lý đa nhiệm (Recents), chọn menu mở rộng của ứng dụng Tailscale và chọn **Khóa (Lock)** để giữ tiến trình trong RAM.

---

### Bước 2: Cài đặt và cấu hình duy trì node trên Tailscale

1. **Xác thực danh tính**:
   - Đăng nhập cùng một định danh xác thực (Google, Microsoft, hoặc GitHub) trên cả client và host để hai thiết bị tự động thuộc về cùng một mạng nội bộ (**Tailnet**).
2. **Kích hoạt chế độ Always-on VPN trên Android**:
   - Truy cập **Cài đặt Android** $\rightarrow$ **Mạng và Internet** $\rightarrow$ **VPN**.
   - Chọn biểu tượng cài đặt cạnh mục **Tailscale** $\rightarrow$ Kích hoạt tùy chọn **VPN luôn bật (Always-on VPN)**.
3. **Vô hiệu hóa thời hạn khóa (Disable Key Expiry)**:
   > [!WARNING]
   > Theo chính sách bảo mật mặc định của Tailscale, khóa xác thực của node có thời hạn 180 ngày. Khi hết hạn, node sẽ bị ngắt kết nối cho đến khi thực hiện xác thực lại. Đối với thiết bị đóng vai trò máy chủ nhận kết nối không người trực, cần tắt thời hạn khóa:
   - Đăng nhập vào trang quản trị: [Tailscale Admin Console - Machines](https://login.tailscale.com/admin/machines).
   - Định vị node Android tương ứng $\rightarrow$ Chọn menu tùy chọn `...` $\rightarrow$ Chọn **Disable key expiry**. Thiết bị sẽ hiển thị trạng thái `Expiry disabled`.
4. **Xác định địa chỉ IP nội bộ**:
   - Mở ứng dụng Tailscale trên điện thoại, kích hoạt trạng thái **Active**.
   - Ghi nhận địa chỉ IPv4 được cấp trong dải `100.64.0.0/10` (ví dụ: `100.82.51.71`).

---

### Bước 3: Khởi tạo kết nối ADB TCP/IP qua cổng 5555

> [!NOTE]
> Thao tác cắm cáp USB chỉ cần thực hiện một lần trong giai đoạn thiết lập ban đầu để gửi lệnh chuyển đổi chế độ hoạt động của ADB daemon trên điện thoại sang TCP/IP.

1. Kết nối điện thoại với máy tính bằng cáp USB.
2. Trên màn hình điện thoại, xác nhận hộp thoại **"Cho phép gỡ lỗi USB từ máy tính này"** $\rightarrow$ Chọn **Luôn cho phép** $\rightarrow$ Xác nhận.
3. Mở PowerShell tại thư mục làm việc của Scrcpy và xác nhận kết nối:
   ```powershell
   cd D:\app_dow\scrcpy-win64
   .\adb devices
   ```
   *Kết quả hợp lệ hiển thị mã định danh thiết bị kèm trạng thái `device`.*
4. Chuyển ADB daemon sang chế độ lắng nghe cổng mạng TCP:
   ```powershell
   .\adb tcpip 5555
   ```
   *Hệ thống phản hồi: `restarting in TCP mode port: 5555`.*
5. **Rút cáp USB**. ADB daemon trên Android hiện tiếp tục lắng nghe trên cổng TCP 5555 thông qua tất cả các giao diện mạng khả dụng.

---

### Bước 4: Thiết lập kết nối và khởi chạy phiên Scrcpy

1. **Kiểm tra thông tuyến và phương thức truyền qua Tailscale**:
   ```powershell
   tailscale ping 100.82.51.71
   ```
   - Nếu phản hồi có dạng: `pong from oppo-a77s (100.82.51.71) via [Public_IP]:port in ... ms` $\rightarrow$ Kết nối được thiết lập trực tiếp dạng P2P.
   - Nếu phản hồi có dạng: `pong from oppo-a77s (100.82.51.71) via DERP(sin) in ... ms` $\rightarrow$ Gói tin đang được chuyển tiếp qua relay DERP (Singapore) do giới hạn của cơ chế NAT ở một hoặc hai đầu mạng.

2. **Khởi tạo phiên ADB qua địa chỉ Tailscale**:
   ```powershell
   cd D:\app_dow\scrcpy-win64
   .\adb connect 100.82.51.71:5555
   ```
   *Hệ thống phản hồi: `connected to 100.82.51.71:5555`.*

3. **Khởi chạy Scrcpy với các tham số tối ưu**:
   ```powershell
   .\scrcpy -s 100.82.51.71:5555 --stay-awake --turn-screen-off
   ```
   - Cửa sổ hiển thị giao diện Android xuất hiện trên màn hình máy trạm.
   - Kiểm tra khả năng nhập liệu bằng chuột và bàn phím để xác nhận tính hai chiều của phiên điều khiển.

---

## 4. Tham Số Tối Ưu Hóa & Phím Tắt

### 4.1 Danh Mục Tham Số Cấu Hình Dòng Lệnh

| Tham Số | Cơ Chế Kỹ Thuật | Phạm Vi Áp Dụng |
| :--- | :--- | :--- |
| `--turn-screen-off` | Tắt màn hình vật lý trên Android bằng cách gửi lệnh tắt hiển thị phần cứng trong khi phiên render ảo vẫn duy trì | Giảm mức tiêu thụ điện năng và hạn chế phát nhiệt trên thiết bị |
| `--stay-awake` | Ngăn chặn hệ điều hành Android chuyển sang trạng thái ngủ sâu (Sleep Mode) khi đang kết nối nguồn điện | Duy trì tính sẵn sàng của tiến trình dịch vụ trên host |
| `--no-audio` | Bỏ qua việc khởi tạo bộ thu và phát âm thanh phía client | Giảm tải băng thông; xử lý lỗi khi client không có thiết bị xuất âm thanh khả dụng |
| `-b 4M` | Giới hạn bitrate mã hóa của luồng video xuống 4 Mbps (mặc định 8 Mbps) | Áp dụng khi kết nối qua mạng di động hoặc đường truyền có băng thông hạn chế |
| `-m 1024` | Giới hạn chiều dài của cạnh lớn nhất trên khung hình về mức 1024 pixel | Giảm độ phân giải video để hạ độ trễ xử lý mã hóa và giải mã phần cứng |
| `--video-codec=h265` | Chuyển đổi bộ mã hóa sang chuẩn H.265 / HEVC thay cho chuẩn mặc định H.264 | Nâng cao hiệu quả nén dữ liệu ở mức bitrate thấp (yêu cầu phần cứng hai đầu hỗ trợ) |
| `-s <endpoint>` | Chỉ định địa chỉ IP:Port hoặc Serial của thiết bị mục tiêu | Tránh xung đột thiết bị khi môi trường ADB có nhiều phiên kết nối khả dụng |

### 4.2 Cấu Hình Tham Số Cho Đường Truyền Băng Thông Thấp / Độ Trễ Cao

Khi thực hiện kết nối từ xa qua mạng di động 4G/5G hoặc mạng Wi-Fi công cộng có độ ổn định kém, cấu hình sau kết hợp các cơ chế giảm tải băng thông và giảm trễ:

```powershell
.\scrcpy -s 100.82.51.71:5555 --stay-awake --turn-screen-off --no-audio -b 4M -m 1280
```

### 4.3 Định Danh Thiết Bị Thông Qua MagicDNS

Tailscale tích hợp hệ thống phân giải tên miền nội bộ MagicDNS. Khi tính năng này hoạt động, có thể sử dụng trực tiếp hostname thay cho địa chỉ IPv4 dạng số:

```powershell
.\adb connect oppo-a77s:5555
.\scrcpy -s oppo-a77s:5555 --stay-awake --turn-screen-off
```

### 4.4 Bảng Phím Tắt Thao Tác Trong Scrcpy

| Tổ Hợp Phím | Hành Động Điều Khiển Tương Ứng |
| :--- | :--- |
| `Ctrl + O` | Tắt màn hình vật lý của thiết bị (phiên stream vẫn duy trì) |
| `Ctrl + Shift + O` | Bật lại màn hình vật lý của thiết bị |
| `Ctrl + P` | Gửi tín hiệu nút Nguồn vật lý (Power) |
| `Ctrl + H` | Gửi tín hiệu nút Trang chính (Home) |
| `Ctrl + B` hoặc `Chuột Phải` | Gửi tín hiệu Quay lại (Back) |
| `Ctrl + S` | Mở màn hình quản lý đa nhiệm ứng dụng (App Switcher) |
| `Ctrl + V` | Đồng bộ dữ liệu bảng tạm (Clipboard) từ máy tính sang thiết bị |

---

## 5. Kịch Bản Tự Động Hóa Cho Windows (`connect.bat`)

Nhằm rút ngắn quy trình thiết lập thủ công, repository cung cấp kịch bản [connect.bat](file:///d:/Hoc_Tap/file_vs_code/Tool_Tips/remote%20android%20by%20scrcpy%20using%20tailscale/connect.bat) để tự động hóa các bước kiểm tra và khởi chạy.

### Cơ Chế Hoạt Động Của Kịch Bản:
1. Tiếp nhận địa chỉ IP hoặc hostname thiết bị (sử dụng giá trị mặc định được cấu hình trong biến `DEFAULT_DEVICE` nếu người dùng không nhập).
2. Chuẩn hóa chuỗi kết nối bằng cách tự động bổ sung cổng `:5555` nếu chuỗi đầu vào thiếu cổng.
3. Gửi lệnh `adb connect` đến endpoint mục tiêu và liệt kê danh sách thiết bị hiện hành qua `adb devices`.
4. Khởi chạy `scrcpy.exe` với tập hợp các cờ tham số tối ưu hóa: `--stay-awake`, `--turn-screen-off`, `--no-audio`, và `-b 4M`.

---

## 6. Phân Tích & Xử Lý Sự Cố Thường Gặp

### ❌ Sự Cố 1: Xung Đột Định Danh Thiết Bị (`ERROR: Multiple (2) ADB devices`)

```text
ERROR: Multiple (2) ADB devices:
ERROR:     -->   (usb)  d9b6e79c                        device  CPH2473
ERROR:     --> (tcpip)  192.168.100.98:5555             device  CPH2473
ERROR: Select a device via -s (--serial), -d (--select-usb) or -e (--select-tcpip)
ERROR: Server connection failed
```

- **Nguyên nhân kỹ thuật**: Tiến trình `scrcpy` phát hiện nhiều hơn một thiết bị ADB hợp lệ mà không có tham số định danh cụ thể, dẫn đến trạng thái không xác định được thiết bị mục tiêu (`ambiguous target`). Trường hợp này xảy ra khi thiết bị vừa duy trì kết nối cáp USB vừa có kết nối TCP/IP đang hoạt động.
- **Phương án xử lý**:
  - **Phương án 1 (Khuyến nghị cho kịch bản không dây)**: Ngắt kết nối cáp vật lý USB. Tiến trình Scrcpy sẽ tự động liên kết với phiên TCP/IP duy nhất còn lại.
  - **Phương án 2 (Khi duy trì cắm sạc qua máy tính)**:
    - Bắt buộc Scrcpy chọn kết nối không dây qua cờ `-e` hoặc tham số chỉ định đích `-s`:
      ```powershell
      .\scrcpy -s 100.82.51.71:5555 --stay-awake --turn-screen-off
      ```
    - Bắt buộc Scrcpy chọn kết nối qua cáp USB thông qua cờ `-d`:
      ```powershell
      .\scrcpy -d --stay-awake --turn-screen-off
      ```

---

### ❌ Sự Cố 2: Lỗi Khởi Tạo Bộ Phân Tách Âm Thanh Phía Client (`Demuxer error`)

```text
ERROR: Could not open audio device: No default audio device available
ERROR: Demuxer error
```

- **Nguyên nhân kỹ thuật**: Kể từ phiên bản 2.0, Scrcpy mặc định khởi tạo đồng thời luồng truyền tải âm thanh. Lỗi xuất phát từ phía hệ điều hành client (Windows) khi không có thiết bị đầu ra âm thanh khả dụng (Audio Output Sink) ở trạng thái hoạt động (chưa kết nối tai nghe/loa, driver âm thanh bị tắt, hoặc đang sử dụng màn hình không có loa tích hợp). Việc không thể mở audio sink khiến module phân tách luồng (`Demuxer`) gặp ngoại lệ và chấm dứt tiến trình.
- **Phương án xử lý**:
  - **Phương án 1 (Khuyến nghị khi chỉ cần thao tác hình ảnh)**: Vô hiệu hóa việc truyền luồng âm thanh thông qua cờ `--no-audio`:
    ```powershell
    .\scrcpy -s 100.82.51.71:5555 --stay-awake --turn-screen-off --no-audio
    ```
  - **Phương án 2 (Khi cần nhận luồng âm thanh từ Android)**:
    - Kích hoạt hoặc kết nối một thiết bị xuất âm thanh trên hệ điều hành Windows.
    - Nhấn tổ hợp phím `Windows + R`, nhập `mmsys.cpl` $\rightarrow$ Enter.
    - Tại tab **Playback**, nhấp chuột phải vào thiết bị âm thanh mục tiêu $\rightarrow$ Chọn **Enable** và thiết lập **Set as Default Device**.

---

### ❌ Sự Cố 3: Cửa Sổ Stream Hoạt Động Nhưng Không Nhận Thao Tác Chuột/Bàn Phím

- **Nguyên nhân kỹ thuật**: Cơ chế kiểm soát bảo mật của ColorOS / OxygenOS / HyperOS mặc định chặn việc gửi sự kiện cảm ứng (Touch Events) và sự kiện phím (Key Events) từ bên thứ ba thông qua cổng gỡ lỗi ADB nhằm phòng chống tấn công điều khiển trái phép.
- **Phương án xử lý**:
  - Trên thiết bị Android, truy cập **Cài đặt** $\rightarrow$ **Cài đặt hệ thống** $\rightarrow$ **Tùy chọn cho nhà phát triển**.
  - Kích hoạt tùy chọn **Tắt giám sát quyền (Disable permission monitoring)**.
  - (Đối với thiết bị chạy Xiaomi HyperOS/MIUI: Kích hoạt đồng thời tùy chọn *Gỡ lỗi USB (Cài đặt bảo mật) / USB Debugging (Security Settings)*).

---

### ❌ Sự Cố 4: Gián Đoạn Kết Nối Sau Khoảng Thời Gian Màn Hình Tắt

- **Nguyên nhân kỹ thuật**: Cơ chế Doze Mode của Android hạn chế tài nguyên mạng và CPU của các ứng dụng chạy nền khi thiết bị không chuyển động và màn hình tắt trong một khoảng thời gian nhất định.
- **Phương án xử lý**:
  1. Xác nhận tùy chọn **VPN luôn bật (Always-on VPN)** trong cài đặt mạng của hệ điều hành đã được kích hoạt cho Tailscale.
  2. Xác nhận quyền **Không tối ưu hóa pin (Don't optimize)** và quyền **Tự khởi chạy (Auto-launch)** đã được cấp cho ứng dụng Tailscale.
  3. Kích hoạt tùy chọn **Không khóa màn hình khi sạc (Stay awake)** trong Tùy chọn cho nhà phát triển và duy trì cấp nguồn liên tục cho thiết bị.

---

## 7. Phân Tích Kỹ Thuật Chuyên Sâu Về Mạng Tailscale

### ❓ 1. Khả năng thiết lập phiên kết nối khi sử dụng hai tài khoản Tailscale khác nhau
- **Khả năng thực hiện**: Hoàn toàn có thể thực hiện thông qua tính năng **Node Sharing**.
- **Cơ chế kỹ thuật**: Mỗi tài khoản người dùng tương ứng với một Tailnet độc lập. Mặc định, các node thuộc các Tailnet khác nhau không có bảng định tuyến chung.
  - Khi sử dụng **cùng một tài khoản**: Hai thiết bị tự động được gán vào cùng một Tailnet, chia sẻ chung bảng định tuyến nội bộ mà không yêu cầu cấu hình ủy quyền bổ sung.
  - Khi sử dụng **hai tài khoản khác nhau**: Cần thực hiện thao tác chia sẻ thiết bị (Node Sharing) từ tài khoản quản lý host sang tài khoản client thông qua Web Console.

---

### ❓ 2. Tính chất của địa chỉ IPv4 `100.x.y.z` và cơ chế phân giải tên miền
- **Tính chất địa chỉ IP**: Địa chỉ IPv4 thuộc dải `100.64.0.0/10` do Tailscale cấp là **địa chỉ cố định (Static IP)** cho từng node dựa trên khóa định danh của thiết bị, trừ trường hợp node bị xóa thủ công khỏi Tailnet. Địa chỉ này không thay đổi khi thiết bị chuyển đổi môi trường mạng vật lý (Wi-Fi, mạng có dây, hoặc mạng di động).
- **Cơ chế phân giải**: Hệ thống tích hợp MagicDNS tự động gán bản ghi DNS cục bộ cho từng node (ví dụ: `oppo-a77s`), cho phép thực hiện kết nối thông qua hostname thay vì phải tra cứu địa chỉ IP số.

---

### ❓ 3. Khả năng truy cập từ Internet công cộng đối với dải địa chỉ `100.64.0.0/10`
- **Cơ chế định tuyến**: Dải địa chỉ `100.64.0.0/10` được chuẩn hóa tại **RFC 6598** (Shared Address Space dành cho Carrier-Grade NAT).
  - Dải địa chỉ này **không được định tuyến trên bảng định tuyến Internet công cộng (BGP)**. Toàn bộ các router biên và gateway trên mạng công cộng sẽ loại bỏ (drop) các gói tin có địa chỉ đích thuộc dải này.
  - Lưu lượng gửi đến địa chỉ `100.x.y.z` chỉ có thể được đóng gói và giải mã giữa các endpoint đã tham gia cùng một Tailnet và sở hữu cặp khóa mã hóa WireGuard hợp lệ.

---

### ❓ 4. Phân biệt kiến trúc Tailscale Mesh VPN với Proxy, Exit Node và Full-Tunnel VPN
- **Proxy (Lớp 7 - Application Layer)**: Chỉ xử lý lưu lượng của các ứng dụng cụ thể được cấu hình hỗ trợ proxy (như trình duyệt web); không có khả năng định tuyến các gói tin tầng mạng của tiến trình hệ điều hành hoặc socket ADB.
- **Tailscale Mesh VPN thông thường (Mặc định - Split-Tunnel)**: Hoạt động ở tầng mạng (Lớp 3 - Network Layer). Chỉ các gói tin có địa chỉ đích thuộc dải mạng nội bộ Tailnet mới được định tuyến qua đường hầm mã hóa WireGuard; toàn bộ lưu lượng Internet công cộng khác tiếp tục đi qua gateway mạng vật lý bình thường.
- **Tailscale Exit Node (Full-Tunnel)**: Cấu hình định tuyến toàn bộ lưu lượng mạng (`0.0.0.0/0`) của client qua một node cụ thể trong Tailnet làm cổng ra Internet. Địa chỉ IP công khai của client khi đó sẽ mang thông số của đường truyền mạng tại node Exit Node.
- **Dịch vụ DNS (ví dụ: Cloudflare 1.1.1.1)**: Chỉ thực hiện chức năng phân giải tên miền thành địa chỉ IP; không cung cấp đường hầm mạng riêng hoặc cơ chế mã hóa kênh truyền giữa các thiết bị nội bộ.

---

### ❓ 5. Các tính năng mạng mở rộng trên nền tảng Tailscale
- **Subnet Router**: Cho phép một node đóng vai trò gateway cầu nối định tuyến đến toàn bộ phân đoạn mạng LAN cục bộ (ví dụ: dải `192.168.1.0/24`), giúp các client từ xa truy cập các thiết bị không cài đặt được Tailscale trong mạng LAN.
- **Tailscale SSH**: Quản lý phiên SSH dựa trên danh tính Tailnet, thay thế việc cấu hình và xoay vòng khóa SSH thủ công (`authorized_keys`).
- **Taildrop**: Giao thức truyền tệp trực tiếp giữa các node theo mô hình P2P thông qua đường hầm mã hóa nội bộ mà không qua máy chủ lưu trữ trung gian.
- **Access Control Lists (ACLs)**: Thiết lập chính sách kiểm soát truy cập theo mô hình Zero Trust dựa trên tệp cấu hình JSON/HuJSON, cho phép giới hạn quyền kết nối tới các cổng hoặc dịch vụ cụ thể.

---

## 📄 Bản Quyền & Tài Liệu Tham Khảo

- Dự án được phát hành dưới giấy phép [MIT License](LICENSE).
- Tài liệu kỹ thuật tham khảo:
  - [Tài liệu kỹ thuật Genymobile Scrcpy](https://github.com/Genymobile/scrcpy)
  - [Tài liệu kiến trúc mạng Tailscale](https://tailscale.com/kb/)
  - [Chuẩn IANA RFC 6598 - IANA-Reserved IPv4 Prefix for Shared Address Space](https://datatracker.ietf.org/doc/html/rfc6598)
