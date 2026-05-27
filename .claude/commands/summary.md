Tóm tắt bug cho Manager/PM đọc nhanh. Bạn viết KHÔNG dùng từ kỹ thuật.

Nhận argument từ user: $ARGUMENTS

Quy tắc:
1. Parse Bug ID từ $ARGUMENTS (VD: BUG-001, --bug BUG-002, hoặc "all" để tóm tắt tất cả)
2. Nếu $ARGUMENTS trống, đọc file "e:/FINAN -AUTO TEST/Report bug/bug_reporter/output/bugs.json" và liệt kê danh sách bug, hỏi user chọn
3. Đọc file "e:/FINAN -AUTO TEST/Report bug/bug_reporter/output/bugs.json" để lấy thông tin bug
4. TỰ VIẾT tóm tắt ngay trong chat, KHÔNG gọi Python CLI

FORMAT cho 1 bug:
```
# BUG-XXX — Summary (cho Manager/PM)

> **Priority:** [priority]

[3-5 dòng tóm tắt, KHÔNG dùng từ kỹ thuật:]
- Dòng 1: Tính năng nào bị lỗi, biểu hiện thế nào
- Dòng 2: Mức độ ảnh hưởng đến người dùng cuối
- Dòng 3: Người dùng mong muốn gì
- Dòng 4: Khuyến nghị xử lý (ngay / sprint sau)
```

FORMAT cho "all":
```
# Tóm tắt Bug cho PM — Tất cả bugs

> Ngày: [hôm nay] | Tổng: X bugs | Critical: X | High: X | Medium: X | Low: X

### BUG-XXX — [title ngắn] | **[Priority]**
[2-3 dòng tóm tắt không kỹ thuật]

---
[repeat cho mỗi bug]

## Tổng hợp ưu tiên xử lý
| Thứ tự | Bug | Lý do |
|--------|-----|-------|
| 1 | BUG-XXX | [lý do ưu tiên] |
```

QUAN TRỌNG:
- KHÔNG dùng từ kỹ thuật (API, server, frontend, backend, query, endpoint...)
- Viết ngắn gọn, dễ hiểu cho người KHÔNG biết code
- Nêu rõ IMPACT với người dùng cuối / kinh doanh
- Nếu có bug trùng nhau (duplicate), ghi chú gộp lại

Ví dụ cách user gọi:
- /summary BUG-001
- /summary all
