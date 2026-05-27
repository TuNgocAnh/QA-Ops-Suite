Hiển thị danh sách bug hiện có dưới dạng bảng gọn.

Nhận argument từ user: $ARGUMENTS

Quy tắc:
1. Đọc file "e:/FINAN -AUTO TEST/Report bug/bug_reporter/output/bugs.json"
2. Nếu file rỗng hoặc không có bugs, thông báo: "Chưa có bug nào. Dùng /bug để tạo mới."
3. Parse $ARGUMENTS để filter (tuỳ chọn):
   - Không có argument → hiển thị tất cả
   - --priority Critical → chỉ hiển thị bug Critical
   - --side FE hoặc --side BE → filter theo FE/BE
   - --feature "Báo cáo Kho" → filter theo tính năng
4. TỰ VIẾT bảng ngay trong chat, KHÔNG gọi Python CLI

FORMAT:

```
# Danh sách Bug — [X] bugs

| ID | Title | Priority | FE/BE | Feature | Ngày tạo |
|----|-------|----------|-------|---------|----------|
| BUG-001 | [title ngắn] | Critical | FE | Login | 2026-03-11 |
| BUG-002 | ... | ... | ... | ... | ... |

> Tổng: X bugs | Critical: X | High: X | Medium: X | Low: X
```

Nếu có filter:
```
# Danh sách Bug — Filter: [điều kiện] — [X] bugs

[bảng như trên, chỉ hiển thị bugs match filter]
```

QUAN TRỌNG:
- Title hiển thị ngắn gọn (cắt nếu quá dài)
- Sắp xếp theo Priority: Critical > High > Medium > Low
- Nếu có bug duplicate, ghi chú (dup) bên cạnh

Ví dụ cách user gọi:
- /list                          → tất cả bugs
- /list --priority High          → chỉ bug High
- /list --side FE                → chỉ bug FE
- /list --feature "Báo cáo Kho"  → chỉ bug của tính năng này