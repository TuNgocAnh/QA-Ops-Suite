Đọc và ghi nhớ tài liệu dự án để các lệnh /bug, /analysis, /summary hiểu ngữ cảnh tốt hơn.

Nhận argument từ user: $ARGUMENTS

Quy tắc:
1. Parse đường dẫn file hoặc thư mục từ $ARGUMENTS
2. Nếu $ARGUMENTS trống, đọc tất cả file trong "e:/FINAN -AUTO TEST/Report bug/bug_reporter/docs/project/"
3. Nếu $ARGUMENTS là đường dẫn cụ thể (file hoặc folder), đọc file/folder đó

Hành động:
1. Dùng Glob tìm tất cả file trong đường dẫn (*.md, *.txt, *.pdf, *.docx, *.json...)
2. Dùng Read đọc NỘI DUNG từng file
3. Sau khi đọc xong, TÓM TẮT lại cho user:

```
## Docs đã đọc

| # | File | Nội dung chính |
|---|------|---------------|
| 1 | [tên file] | [1 dòng tóm tắt] |
| 2 | ... | ... |

## Tóm tắt ngữ cảnh dự án
- **Tên dự án:** [...]
- **Các tính năng chính:** [...]
- **Menu / Flow chính:** [...]
- **Thuật ngữ quan trọng:** [...]
```

4. Giữ toàn bộ nội dung docs trong context conversation hiện tại
5. Thông báo: "Đã đọc xong. Từ giờ /bug, /analysis, /summary sẽ dùng ngữ cảnh này."

QUAN TRỌNG:
- Đọc KỸ, không lướt qua. Ghi nhớ: tên tính năng, flow, expected behavior, menu structure, API endpoints
- Nội dung docs sẽ TỒN TẠI TRONG CONVERSATION này, nên các lệnh /bug gọi sau sẽ tự động có context
- Nếu user gửi path tới 1 file cụ thể (VD: /docs brd.md), chỉ đọc file đó
- Nếu user gửi path tới folder, đọc tất cả file trong folder

Ví dụ cách user gọi:
- /docs                                    → đọc tất cả trong docs/project/
- /docs e:/path/to/brd.md                  → đọc 1 file cụ thể
- /docs e:/path/to/specs/                  → đọc cả folder
- /docs brd.md prd.md                      → đọc nhiều file
