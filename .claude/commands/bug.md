Tạo bug report mới. Bạn là QA/Tester chuyên nghiệp với khả năng phân tích bug sâu.

Nhận argument từ user: $ARGUMENTS

## BƯỚC 0 — Kiểm tra ngữ cảnh dự án
Nếu user đã gọi /docs trước đó, nội dung docs đã có sẵn trong conversation → SỬ DỤNG ngữ cảnh đó để:
- Viết Steps to Reproduce chính xác theo flow thật
- Điền Expected Result đúng theo spec
- Dùng đúng thuật ngữ, tên menu, tên tính năng của dự án

Nếu CHƯA có docs trong context, vẫn viết bug report bình thường dựa trên mô tả + ảnh của user.

## BƯỚC 1 — Parse input
1. Nếu $ARGUMENTS trống, hỏi user mô tả bug
2. Nếu user gửi kèm ảnh chụp màn hình, phân tích kỹ ảnh để lấy thêm context (tên menu, data hiển thị, lỗi nhìn thấy...)
3. Nếu user gửi kèm **video** (đường dẫn file .mp4, .mov, .webm, .avi, .mkv):
   a. **Resolve path**: nếu user chỉ đưa **filename** (không có `/` hoặc `\`) → mặc định lookup tại `e:/FINAN -AUTO TEST/QA Ops Suite/bug-videos/<filename>`. KHÔNG dùng `find` để search — tất cả video bug đều ở folder này. Chỉ khi user đưa absolute path khác thì mới dùng path đó.
   b. **Chạy ffmpeg trích xuất frames**. Lệnh ffmpeg:
      ```bash
      FFMPEG="C:/Users/lenovo/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe"
      mkdir -p "e:/FINAN -AUTO TEST/QA Ops Suite/results/bugs/video_frames/<bug_id>"
      "$FFMPEG" -i "<đường_dẫn_video>" -vf "fps=1,select='gt(scene,0.3)'" -vsync vfr -q:v 2 "e:/FINAN -AUTO TEST/QA Ops Suite/results/bugs/video_frames/<bug_id>/frame_%03d.jpg" 2>/dev/null
      ```
      - `fps=1`: lấy tối đa 1 frame/giây
      - `select='gt(scene,0.3)'`: chỉ lấy frame khi có thay đổi đáng kể (scene change > 30%)
      - Nếu video ngắn (<5s) hoặc scene filter cho ít frame, fallback: `ffmpeg -i "<video>" -vf "fps=1" -q:v 2 "...frame_%03d.jpg"`
      - Giới hạn: đọc tối đa 10 frame quan trọng nhất
   c. **Đọc tất cả frame PARALLEL**: gọi nhiều Read tool calls trong CÙNG 1 message (KHÔNG đọc tuần tự, sẽ chậm gấp 3-4 lần).
   d. Phân tích các frame để hiểu flow lỗi: trước khi lỗi → lúc lỗi → sau lỗi
4. Kết hợp: mô tả user + ảnh/video frames + docs dự án → hiểu đầy đủ ngữ cảnh

## BƯỚC 2 — Timestamp cho folder frames (nếu có video)
Chỉ cần khi có video → dùng timestamp `bug-YYYYMMDD-HHMMSS` làm tên folder chứa frames (tránh trùng).
- Lấy bằng: `python -c "from datetime import datetime; print(datetime.now().strftime('bug-%Y%m%d-%H%M%S'))"`
- **KHÔNG** in timestamp/ID ra chat. **KHÔNG** đặt ID trong nội dung bug report.

## BƯỚC 3 — Viết bug report (CHỈ output ra chat, KHÔNG lưu file)
TỰ VIẾT bug report đầy đủ ngay trong chat để user copy/paste. **KHÔNG** dùng Write tool tạo file `.md`. Format:

```
# Bug Report

> **Created:** [ngày giờ hiện tại]
> **Platform:** [web/app]
> **Environment:** [Dev/Staging/Production]

---

## Title
[Tiêu đề ngắn gọn, rõ ràng, bao gồm tên tính năng]

## Description
[1-2 câu mô tả ngắn gọn bug là gì, ở đâu]

**Account:** `0333333335 / 123456`

## Steps to Reproduce
1\. [Hành động ngắn gọn, dùng → để chỉ navigation. VD: Vào Báo cáo → Kho.]
2\. [Hành động tiếp theo]
3\. [Quan sát kết quả]

## Actual Result
- [Điều gì xảy ra — viết ngắn, mỗi ý 1 dòng]
- [Nếu liên quan tính toán thì có số liệu]

## Expected Result
- [Điều gì đáng lẽ phải xảy ra — viết ngắn, rõ ràng]
- [Không lặp lại spec dài dòng, chỉ nêu hành vi đúng]

## Priority
**[Critical/High/Medium/Low]** — [1 câu lý do ngắn, góc nhìn business: cần fix sớm hay muộn]

## Severity
**[Critical/High/Medium/Low]** — [1-2 câu lý do, góc nhìn kỹ thuật: mức impact tới hệ thống/feature, có workaround không]

## Type
**[Function / UI-UX / Performance / Data / Security / Integration / Regression]** — [1 câu lý do ngắn, chọn 1 loại phù hợp nhất]

## Bug thuộc FE hay BE
**[Frontend/Backend/Cả hai]**
- [1-2 câu giải thích ngắn]

## Attachments
- [Liệt kê ảnh hoặc video đính kèm, nếu có]
- [Nếu video: ghi đường dẫn gốc + thư mục frames đã trích xuất]
```

## BƯỚC 4 — KHÔNG lưu file
- **KHÔNG** tạo file `.md`, **KHÔNG** dùng Write tool. Bug report chỉ xuất hiện trong chat.
- **KHÔNG** tạo/cập nhật bugs.json, **KHÔNG** đếm số.
- Folder duy nhất được ghi: `results/bugs/video_frames/<timestamp>/` (chỉ khi có video, để ffmpeg đổ frames vào).
- Sau khi output bug report ra chat, KHÔNG cần báo "đã lưu file..." vì không lưu gì cả.

QUAN TRỌNG — PHONG CÁCH VIẾT:
- **BẮT BUỘC** dòng `**Account:** \`0333333335 / 123456\`` ngay TRÊN section `## Steps to Reproduce` (1 hàng duy nhất, không dùng heading `##`). Fallback từ env `TEST_ACCOUNT` chỉ khi hardcode mất. KHÔNG được bỏ qua.
- NGẮN GỌN, TRỰC TIẾP. Không viết dài dòng, không lặp lại spec.
- Steps to Reproduce: dùng → cho navigation (VD: Báo cáo → Kho). Mỗi bước 1 hành động rõ ràng. Không cần "Đăng nhập" nếu không liên quan. LUÔN dùng `1\.` `2\.` `3\.` (escaped backslash) thay vì `1.` `2.` `3.` để user copy sang tool khác giữ được số thứ tự.
- Actual Result: **TỐI ĐA 2-3 bullet**, mỗi bullet 1 dòng NGẮN (<= 20 từ). Chỉ nêu hiện tượng cốt lõi, KHÔNG kể chi tiết toast/banner/copy text dài. Có số liệu nếu bug liên quan tính toán.
- Expected Result: **TỐI ĐA 1-2 bullet**, mỗi bullet 1 dòng NGẮN. Chỉ nêu hành vi đúng cốt lõi, KHÔNG mô tả ngược lại Actual, KHÔNG quote spec.
- Priority: 1 câu lý do ngắn, không để mặc định Medium. Góc nhìn **business** (ưu tiên fix).
- Severity: **BẮT BUỘC** có section riêng, KHÔNG được gộp chung với Priority. Góc nhìn **kỹ thuật** (mức impact + có workaround không). Thang: Critical/High/Medium/Low. Chi tiết framework: `.claude/docs/severity-priority-framework.md`.
- Type: **BẮT BUỘC** có section riêng. Phân loại bug theo bản chất: **Function** (logic/flow/business rule sai), **UI-UX** (hiển thị, layout, tương tác, navigation timing), **Performance**, **Data**, **Security**, **Integration**, **Regression**. Chọn 1 type phù hợp nhất, có lý do ngắn.
- FE/BE: 1-2 câu phân tích logic, không dựa trên keyword.
- KHÔNG viết "Đề xuất nguyên nhân" và "Đề xuất hướng fix" — phần này thuộc /analysis.
- Nếu bug đã tồn tại (cùng mô tả + ảnh), KHÔNG tạo trùng — hỏi user trước.

Ví dụ cách user gọi:
- /bug lỗi không click được nút login
- /bug --desc "API trả 500 khi submit form" --feature "Payment"
- /bug [gửi kèm ảnh chụp màn hình]
- /bug lỗi thanh toán C:/Users/video/bug-record.mp4
- /bug [kéo thả file video vào chat]
