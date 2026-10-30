# Review MR-101 – example-service

> DỮ LIỆU MẪU để minh họa định dạng. Xóa cùng thư mục `services/example-service/`.

| Mục | Giá trị |
|---|---|
| Service | example-service |
| MR | MR-101 |
| Ngày review | 2026-10-28 |
| Nhóm rủi ro | High |
| Reviewer | Owner + Claude |
| Phạm vi | Chỉ các dòng thay đổi trong diff. Code cũ ngoài diff không được review. |

> **Khuyến nghị (chỉ mang tính tham khảo):** Merge sau khi sửa các mục
>
> **Lý do:** Có 1 BLOCKER và 1 MAJOR trong code mới (mục 1.1 và 2.1) cần sửa trước khi merge.

## Tổng hợp

| Mức độ | Cần sửa trong MR | Nợ kỹ thuật ghi nhận |
|---|---|---|
| 🔴 BLOCKER | 1 | 0 |
| 🟠 MAJOR | 1 | 1 |
| 🟡 MINOR | 1 | 0 |
| ❓ QUESTION | 0 | 0 |

## 1. Giao dịch và I/O (anti-pattern)

### 1.1 🔴 BLOCKER · New · Fix now — Gửi email xác nhận bên trong `@Transactional`
- **Vị trí:** `src/main/java/com/example/order/OrderService.java:120`
- **Vấn đề:** Email được gửi trước khi transaction commit.
- **Tác động:** Nếu commit lỗi, khách vẫn nhận email cho đơn không tồn tại. Gọi SMTP chậm cũng giữ connection DB.
- **Đề xuất:** Publish event và gửi email ở `@TransactionalEventListener(phase = AFTER_COMMIT)`.

## 2. Xác thực và phân quyền

### 2.1 🟠 MAJOR · New · Fix now — Endpoint hủy đơn chỉ kiểm tra đăng nhập
- **Vị trí:** `src/main/java/com/example/order/OrderController.java:75`
- **Vấn đề:** `POST /orders/{id}/cancel` không kiểm tra user là chủ đơn hoặc có role ADMIN.
- **Tác động:** User đã đăng nhập có thể hủy đơn của người khác.
- **Đề xuất:** Dùng `orderAccessPolicy.assertOwnerOrAdmin(id)` như các endpoint khác.

## 3. Hiệu năng và đồng thời

### 3.1 🟡 MINOR · New · Fix now — Query theo status chưa rõ có index
- **Vị trí:** `src/main/java/com/example/order/OrderRepository.java:22`
- **Vấn đề:** Query mới lọc theo `status` và `created_at`; migration không nằm trong diff nên chưa xác nhận được index.
- **Tác động:** Nếu thiếu index, query quét toàn bảng khi dữ liệu lớn.
- **Đề xuất:** Xác nhận index `(status, created_at)` trong migration hoặc bổ sung.

## 4. Xử lý lỗi và chất lượng code

(Không có mục.)

## 5. Chất lượng code FE

(Không áp dụng cho MR này.)

## Kiểm tra vấn đề cũ

| Mã vấn đề | Vấn đề | Trạng thái trước | Kết quả trong MR này | Trạng thái mới | Bằng chứng |
|---|---|---|---|---|---|
| P-example-service-001 | N+1 query khi load danh sách đơn hàng | Open | Còn nguyên | Open | MR-101: `OrderService.java` được chạm, vòng lặp ở dòng 88 vẫn còn |
| P-example-service-002 | GET /orders/{id} không kiểm tra chủ sở hữu đơn (IDOR) | Open | Đã sửa | Fixed (verified) | MR-101: `OrderController.java:44` gọi `orderAccessPolicy.assertOwner` |
| P-example-service-004 | Gọi API cổng thanh toán bên trong `@Transactional` | Open | Sửa một phần | Partially fixed | MR-101: thêm timeout 3s (`PaymentClient.java:20`) nhưng lời gọi vẫn trong `@Transactional` (`PaymentService.java:57`) |

## Vấn đề tồn tại trong các file MR này chạm vào

Gợi ý cho dev, không bắt buộc. Có thể sửa cùng lúc nếu thuận tiện.

- `P-example-service-001` — N+1 query khi load danh sách đơn hàng — `OrderService.java:88`
- `P-example-service-004` — Gọi API cổng thanh toán trong `@Transactional` — `PaymentService.java:57`

## Nợ kỹ thuật mới ghi nhận

### D1 🟠 MAJOR · Existing-touched · Debt-Track — Consumer Kafka không có dead-letter topic
- **Vị trí:** `src/main/java/com/example/event/OrderEventConsumer.java:33`
- **Vấn đề:** Message lỗi bị retry vô hạn và chặn partition.
- **Tác động:** Các đơn phía sau không được xử lý cho đến khi can thiệp thủ công.
- **Đề xuất:** Cấu hình `DefaultErrorHandler` với `DeadLetterPublishingRecoverer` và giới hạn số lần retry.

## Câu hỏi mở

- ❓ Index cho query ở mục 3.1 có trong migration nào không? Cần xem file migration của MR này.
