# Demo HTML — Lab 9

Mở `index.html` trực tiếp bằng trình duyệt. Bản HTML tự chứa CSS, JavaScript và số liệu snapshot, không cần Internet hoặc cài thư viện để xem.

- Mục lục M0–M7: mỗi chặng có **yêu cầu → đầu ra cần có → những gì đã làm**, ví dụ, bằng chứng và thuật ngữ riêng.
- Nhấn từ gạch chấm hoặc nút **Thuật ngữ** để đọc định nghĩa và tìm kiếm không dấu.
- M3: đổi tiền trong reply để xem tại sao lời xác nhận khác ledger bị bắt.
- M4: chuyển giữa report fixed/regression để xem chênh lệch và CI thực.
- M6: đổi số lần PASS và số lần chọn để phân biệt pass@k với pass^k.
- M7: chọn từng trap để xem cách chỉnh report và lý do gate chặn.
- **Xem toàn bộ** hiển thị đủ tám chặng. **In / PDF** gọi chức năng in của trình duyệt; bản in hiển thị cả tám chặng và giải thích thuật ngữ.

Các tương tác minh họa không chạy Python, agent hay model. Số liệu thực lấy từ report/CSV trong repo tại lúc build; trạng thái test 128 PASS là mốc đã xác minh ngày 17/11/2026. Không coi kết quả local là điểm chấm ẩn hoặc GitHub Actions xanh.

Liên kết bằng chứng mở file trong repo nên cần giữ nguyên vị trí thư mục `demo/`. Chỉ sao chép `index.html` vẫn xem được nội dung và mô phỏng, nhưng link file ngoài HTML sẽ không còn dùng được.

Sinh lại HTML sau khi report thay đổi, chạy từ repo root:

```powershell
.\.venv\Scripts\python.exe demo/build_demo.py
```

`build_demo.py` đọc report/CSV, kiểm định nghĩa thuật ngữ và file bằng chứng, tính lại CI M4 rồi điền vào `template.html`. Nó không sửa report hoặc logic agent. Các mô tả/nội dung đã làm cần được cập nhật trong builder nếu triển khai thay đổi.
