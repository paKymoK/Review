---
service: <service-name>
risk_tier: Medium            # High | Medium | Low
owner_team: BE               # BE | FE | BE+FE
repo_path:                   # optional: local path of the service repo, used to read diffs
stale_after_days:            # leave blank = no stale flag
---

# <service-name>

## Mô tả ngắn
<service làm gì, ai dùng, mức độ quan trọng với business>

## Nhóm rủi ro
<vì sao chọn High/Medium/Low: tần suất thay đổi, lịch sử incident, mức độ lộ ra ngoài, dữ liệu nhạy cảm>

## Override tiêu chí (tùy chọn)
- Kiểm tra thêm: <ví dụ: service này gọi cổng thanh toán, kiểm tra idempotency key>
- Bỏ qua: <ví dụ: thư mục generated/, module legacy-x chưa được đụng tới>

## Lưu ý đặc thù
<quirk của service: config ngoài repo, service phụ thuộc, quy ước riêng>
