Phân tích sâu một bug đã tồn tại trong hệ thống. Bạn là QA/Tester chuyên nghiệp.

Nhận argument từ user: $ARGUMENTS

Quy tắc:
1. Parse Bug ID từ $ARGUMENTS (VD: BUG-001, hoặc --bug BUG-001)
2. Nếu $ARGUMENTS trống, đọc file "e:/FINAN -AUTO TEST/Report bug/bug_reporter/output/bugs.json" và liệt kê danh sách bug hiện có, hỏi user chọn Bug ID
3. Đọc file "e:/FINAN -AUTO TEST/Report bug/bug_reporter/output/bugs.json" để lấy thông tin bug
4. Nếu Bug ID không tồn tại, thông báo lỗi
5. TỰ VIẾT phân tích đầy đủ ngay trong chat, KHÔNG gọi Python CLI

FORMAT ANALYSIS (hiển thị đầy đủ trong chat):

```
# BUG-XXX — Analysis

> **Bug:** [title]
> **Priority:** [priority]

---

## 1. Nguyên nhân gốc rễ có thể
| # | Nguyên nhân | Khả năng |
|---|---|---|
| 1 | [mô tả chi tiết] | Cao/Trung bình/Thấp |
| 2 | ... | ... |

## 2. Module / Ai bị ảnh hưởng
| Module | Ảnh hưởng |
|---|---|
| [module name] | [mô tả ảnh hưởng] |

## 3. Mức độ lan rộng
[Đánh giá dựa trên priority + context bug]

## 4. Checklist cần test lại sau khi fix
- [ ] [item cụ thể]
- [ ] ...

## 5. Tính năng liên quan
| Tính năng | Liên quan thế nào |
|---|---|
| [feature] | [mô tả] |

## 6. Đề xuất nguyên nhân
1. [Nguyên nhân có thể 1 — phân tích kỹ thuật sâu]
2. [Nguyên nhân có thể 2]

## 7. Đề xuất hướng fix
- [Hướng fix cụ thể cho BE/FE/DB]
```

QUAN TRỌNG:
- Nguyên nhân phải LOGIC, dựa trên phân tích kỹ thuật (không đoán bừa)
- Checklist phải CỤ THỂ cho bug đó, không generic
- Tính năng liên quan phải DỰA TRÊN CONTEXT, không liệt kê random
- Nếu bug có ảnh chụp hoặc mô tả chi tiết, phân tích dựa trên đó

Ví dụ cách user gọi:
- /analysis BUG-001
- /analysis --bug BUG-003
