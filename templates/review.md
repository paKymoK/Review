# Review MR-<id> – <service>

| Mục | Giá trị |
|---|---|
| Service | <service> |
| MR | MR-<id> (<link nếu có>) |
| Ngày review | YYYY-MM-DD |
| Nhóm rủi ro | High / Medium / Low |
| Reviewer | <tên> + Claude |
| Phạm vi | Chỉ các dòng thay đổi trong diff. Code cũ ngoài diff không được review. |

> **Khuyến nghị (chỉ mang tính tham khảo):** Có thể merge / Merge sau khi sửa các mục / Cần trao đổi thêm
>
> **Lý do:** <1-3 câu dựa trên các mục BLOCKER/MAJOR của code mới>

## Tổng hợp

| Mức độ | Cần sửa trong MR | Nợ kỹ thuật ghi nhận |
|---|---|---|
| 🔴 BLOCKER | 0 | 0 |
| 🟠 MAJOR | 0 | 0 |
| 🟡 MINOR | 0 | 0 |
| ❓ QUESTION | 0 | 0 |

## 1. Giao dịch và I/O (anti-pattern)

### 1.1 🔴 BLOCKER · New · Fix now — <tiêu đề ngắn>
- **Vị trí:** `path/to/File.java:42`
- **Vấn đề:** <mô tả>
- **Tác động:** <hậu quả>
- **Đề xuất:** <cách sửa cụ thể>

## 2. Xác thực và phân quyền

## 3. Hiệu năng và đồng thời

## 4. Xử lý lỗi và chất lượng code

## 5. Chất lượng code FE

## Kiểm tra nợ cũ

| Mã nợ | Vấn đề | Trạng thái trước | Kết quả trong MR này | Trạng thái mới | Bằng chứng |
|---|---|---|---|---|---|
| TD-<service>-001 | <tiêu đề> | Open | Đã sửa / Sửa một phần / Còn nguyên / Không chạm | Fixed (verified) | MR-<id>, `File.java:10` |

## Nợ trong các file MR này chạm vào

Gợi ý cho dev, không bắt buộc. Có thể sửa cùng lúc nếu thuận tiện.

- `TD-<service>-002` — <tiêu đề> — `File.java:88`

## Nợ kỹ thuật mới ghi nhận

### D1 🟠 MAJOR · Existing-touched · Debt-Track — <tiêu đề ngắn>
- **Vị trí:** `path/to/File.java:120`
- **Vấn đề:** <mô tả>
- **Tác động:** <hậu quả>
- **Đề xuất:** <cách sửa>

## Câu hỏi mở

- ❓ <câu hỏi cần dev/owner trả lời, nêu rõ cần thấy code nào để kết luận>
