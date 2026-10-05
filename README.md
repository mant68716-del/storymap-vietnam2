# StoryMap Việt Nam V2 — Python Flask

Web app nhật ký hành trình Việt Nam, tối ưu cho máy tính và điện thoại.

## Chức năng
- Đăng ký / đăng nhập / đăng xuất, mật khẩu hash, CSRF.
- Bản đồ Leaflet với 63 tỉnh/thành theo bộ lịch sử trước 2025.
- Click marker hoặc chọn tỉnh → **+ Lưu Story**.
- Story gồm tiêu đề, nội dung, ngày đi, địa điểm, tọa độ.
- Upload nhiều ảnh và video: PNG/JPG/WebP/GIF + MP4/MOV/WebM/M4V.
- Preview ảnh/video trước khi lưu.
- Story được lưu trong SQLite và tự đánh dấu tỉnh đã đi.
- Kho Story và trang xem lại Story.
- Task hành trình.
- Hồ sơ người dùng và thống kê X/63.
- Responsive mobile.
- Chạy `0.0.0.0:5000` để điện thoại cùng Wi-Fi truy cập.

## Chạy trên Windows + VS Code
```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```
Mở trên máy tính: http://127.0.0.1:5000

### Mở trên điện thoại cùng Wi-Fi
1. Chạy `ipconfig` trên Windows.
2. Lấy `IPv4 Address`, ví dụ `192.168.1.10`.
3. Điện thoại cùng Wi-Fi mở `http://192.168.1.10:5000`.
4. Nếu Windows Firewall hỏi, cho phép Python trên mạng Private.

## Lưu ý production
Đây là bản local/MVP. Khi đưa lên Internet nên dùng HTTPS, SECRET_KEY riêng, reverse proxy, object storage cho ảnh/video, giới hạn dung lượng, antivirus/quét file và database server.
