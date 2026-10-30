---
service: example-service
risk_tier: High              # High | Medium | Low
owner_team: BE
repo_path:                   # optional: local path of the service repo, used to read diffs
stale_after_days:            # leave blank = no stale flag
---

# example-service

> DỮ LIỆU MẪU. Xóa thư mục `services/example-service/` khi thêm service thật.

## Mô tả ngắn
Service quản lý đơn hàng và thanh toán, được web và mobile gọi trực tiếp.

## Nhóm rủi ro
High: thay đổi hàng tuần, xử lý tiền, từng có incident trùng đơn hàng.

## Override tiêu chí (tùy chọn)
- Kiểm tra thêm: mọi API tạo đơn/thanh toán phải có idempotency key.
- Bỏ qua: thư mục `generated/`.

## Lưu ý đặc thù
Cổng thanh toán được cấu hình ngoài repo; không thấy được timeout/retry trong diff.
