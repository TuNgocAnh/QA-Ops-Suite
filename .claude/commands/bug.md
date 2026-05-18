Soạn **bug draft ngắn gọn, chất lượng** theo style của Report bug project. **KHÔNG upload lên Lark** — chỉ output text vào chat để user copy/paste tay vào Lark / Slack / comment / wiki.

## Role

Bạn là **QA/Tester Senior** chuyên phân tích bug sâu. Output phải **ngắn gọn, trực tiếp, không dài dòng** — mỗi ý một dòng, không lặp spec.

## Khác biệt với `/log-bug`

| Tiêu chí | `/bug` (command này) | `/log-bug` |
|----------|---------------------|------------|
| Upload Lark | **KHÔNG** — chỉ output text vào chat | **CÓ** — tạo record trên Lark Bitable |
| Mục đích | Draft bug nhanh để paste/share tay | Push bug thật sự lên board team |
| Style viết | Markdown ngắn gọn, mỗi section 1-2 câu prose | Tách riêng field theo template Lark chuẩn |
| Cấu trúc body | Title → Description → Account → Steps → Actual → Expected → Priority → Severity → FE/BE | Preconditions, Steps, Actual, Notes, Account test |
| Steps numbering | `1\.` `2\.` `3\.` **escaped** (giữ số khi paste sang tool khác) | Tự do |
| Duplicate check | Không (chat-only, không có persistent storage) | Có |
| Cache board options | Không cần (không gọi API tạo record) | Có |
| Root cause / Fix suggestion | **CẤM** (thuộc `/explain-bug`) | Không đề cập |

`/bug` phù hợp khi bạn muốn bug draft tối giản để gửi nhanh ai đó (Slack, comment, PR review, paste tay vào board), không cần tạo record chính thức ngay.

## Config Loading

- **Always read**: `.claude/rules/core.md` (diacritics rule)
- **On-demand**: `.claude/sitemap.yaml` (Steps theo nav_steps thật nếu cần)
- **On-demand**: `.claude/docs/severity-priority-framework.md` (nếu cần chấm Severity/Priority chính xác)

## BƯỚC 0 — Kiểm tra ngữ cảnh dự án

Nếu user đã gọi `/docs` trước đó trong session, nội dung docs đã có sẵn trong conversation => **SỬ DỤNG ngữ cảnh đó** để:
- Viết Steps to Reproduce chính xác theo flow thật
- Điền Expected Result đúng theo spec
- Dùng đúng thuật ngữ, tên menu, tên tính năng của dự án

Nếu CHƯA có docs trong context => vẫn viết bug draft bình thường dựa trên mô tả + ảnh/video của user.

## BƯỚC 1 — Parse input + phân tích media

1. Nhận `$ARGUMENTS` từ user
2. Nếu trống và không có ảnh/video => hỏi user mô tả bug
3. Nếu có ảnh đính kèm (nút `+` IDE) hoặc file path (ảnh/video) => **PHẢI phân tích** để hiểu bug

### Account: ƯU TIÊN HARDCODE — chỉ fallback env khi cần

Thứ tự ưu tiên (dừng ở value đầu tiên có):

1. **User cung cấp account trong prompt** => dùng prompt
2. **Hardcode default**: `0333333335 / 123456` => dùng luôn, KHÔNG spawn bash đọc env
3. **Fallback**: nếu vì lý do nào đó hardcode bị xoá khỏi bug.md => mới spawn `python -c "from configs.env_loader import get_test_account; print(get_test_account() or '')"` đọc env

Trong flow bình thường, hardcode ở rule này LUÔN có => env không bao giờ được đọc => 0 bash call, nhanh nhất.

### Version: chỉ ghi nếu user cung cấp

- User có version trong prompt (vd `version stg-1.0.51`) => ghi inline trong Description
- Không có => bỏ qua, không hỏi, không đọc env, không in `???`

**RULE #1**: Media (ảnh/video) là nguồn chính hiểu bug. PHẢI đọc và phân tích trước khi viết draft.

**RULE #2**: Nếu user có mô tả text => **bám sát mô tả user**, dùng media để bổ sung chi tiết.

### Ảnh (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.bmp`)

- **File path trong prompt** => dùng Read tool đọc
- **Đính kèm IDE (base64)** => phân tích trực tiếp để viết draft

### Video (`.mp4`, `.mov`, `.avi`, `.webm`, `.mkv`)

**Folder quy ước cho video**: `bug-videos/` ở root project.

#### Detect video filename trong `$ARGUMENTS` (BẮT BUỘC — tiết kiệm 2-3 tool call search)

Khi parse arg, nếu thấy 1 **token** (chuỗi không có space) thỏa **bất kỳ** điều kiện:
- Kết thúc bằng `.mp4` / `.mov` / `.avi` / `.webm` / `.mkv`
- HOẶC bắt đầu bằng pattern timestamp recording `YYYYMMDDHHMMSS_rec` (kiểu OBS / screen recorder)

=> Coi là filename video, **KHÔNG dùng Glob search**, thay vào đó:

1. Token có `/` hoặc `\` (path đầy đủ) => dùng nguyên trạng, kiểm tra tồn tại
2. Token KHÔNG có `/` `\`:
   - Có extension => thử `bug-videos/<token>` trực tiếp
   - Không có extension => thử lần lượt `bug-videos/<token>.mp4`, `.mov`, `.webm`, `.avi`, `.mkv` (stop ở cái đầu tiên tồn tại)
3. Tìm thấy => dùng path đó
4. KHÔNG tìm thấy ở cả 5 extension => hỏi user: "Không tìm thấy `bug-videos/<token>(.mp4|.mov|...)`. Bạn check lại path hoặc bỏ video vào folder `bug-videos/`."

**CẤM** Glob toàn project (`**/*<token>*`) để tìm video — chậm + dễ match nhầm file.

#### Đính kèm IDE (nút `+`)

Nếu user dùng nút `+` IDE cho video => không có path thật => **reject**, yêu cầu user copy file vào `bug-videos/` rồi gọi lại với filename.

1. Check duration (max 120s):
   ```bash
   # Windows
   python configs/video_frames.py <video_path> --json
   # macOS / Linux
   python3 configs/video_frames.py <video_path> --json
   ```
   - > 120s => reject, yêu cầu cắt dưới 2 phút
   - Không có ffmpeg => hướng dẫn cài
   - **Windows**: LUÔN dùng `python` (không phải `python3` — Windows redirect `python3` sang Microsoft Store)

2. Extract frames + đọc hiểu flow (trước-lúc-sau bug):
   ```bash
   # Windows
   python configs/video_frames.py <video_path>
   # macOS / Linux
   python3 configs/video_frames.py <video_path>
   ```
   - Mặc định resize frame về width **1280px** (giữ tỉ lệ) — đọc nhanh hơn, text UI vẫn rõ
   - Cần res gốc: `--width 0` | mobile bug nhỏ: `--width 720` | nhiều/ít frame: `--max-frames N`
   - **PHẢI** Read TẤT CẢ frames trong **1 message duy nhất** (gọi nhiều Read tool song song) để tối ưu tốc độ — KHÔNG đọc tuần tự

> **Lưu ý**: KHÔNG upload video gốc đi đâu cả. User tự attach video vào nơi họ paste draft.

## BƯỚC 2 — Auto-fill body fields

`/bug` **KHÔNG có metadata header block** (đã bỏ ID/Created/Platform/Environment/Version riêng — output gọn, paste nhanh). Mọi info quan trọng dồn vào body:

- **Title**: `[Tên tính năng / màn hình] Mô tả bug ngắn` (~10 từ). Tên màn = nguồn duy nhất xác định Platform/Feature
- **Description**: 1-2 câu mô tả bug là gì, ở đâu. **Nếu user cung cấp version** => ghi inline trong Description (vd: "Trên Admin Portal stg-1.0.51, ...")
- **Type**: KHÔNG output field riêng. Detect ngầm để chọn Priority/Severity hợp lý
- **Priority**: Critical | High | Medium | Low — tự estimate **kèm 1 câu lý do ngắn**
- **Severity**: High | Medium | Low — tự estimate

> **KHÔNG** hỏi user bổ sung Dev PIC / Sprint / Tính năng — `/bug` chỉ là draft, user sẽ điền các field này tay khi paste lên board.
> **KHÔNG** spawn Python đọc env (`TEST_ACCOUNT`, `DEFAULT_VERSION`, ...) — chậm, không cần.

## Priority & Severity

### Priority (nghiệp vụ — mức ưu tiên fix)

- **Critical**: Block user, mất tiền, báo cáo quan trọng
- **High**: Ảnh hưởng nhiều user hoặc flow chính
- **Medium**: Ảnh hưởng ít, không gấp
- **Low**: Nice-to-have, UI nhỏ, cosmetic

Mỗi giá trị phải kèm **1 câu lý do ngắn** — KHÔNG để mặc định Medium mà không giải thích.

### Severity (kỹ thuật — mức nghiêm trọng)

Style chỉ có 3 mức: **High / Medium / Low** (không có Critical).

- **High**: Crash, data loss, security, tính năng chính không dùng được
- **Medium**: Tính năng phụ hỏng, có workaround, bug logic/UI ảnh hưởng UX
- **Low**: UI nhỏ, cosmetic, text sai, icon lệch

Priority & Severity thường giống nhau nhưng có thể khác (vd: bug UI Low severity trên landing page => Priority High vì ảnh hưởng brand).

## Test Account

**ÁP DỤNG CHO TOÀN BỘ BUG** — không có exception (kể cả admin portal, web nội bộ, app khách hàng đều dùng cùng 1 rule).

Thứ tự ưu tiên:

1. **User cung cấp account khác trong prompt** => dùng prompt (override)
2. **Hardcode default**: `0333333335 / 123456` => dùng luôn, KHÔNG spawn bash đọc env
3. **Fallback** (chỉ khi hardcode bị xoá khỏi bug.md): mới đọc `TEST_ACCOUNT` từ `.env` qua `get_test_account()` trong `configs/env_loader.py`

Format: Account đặt **ngay trước** Steps to Reproduce, dạng `## Account: <phone> / <pass>`.

**CẤM** viết kiểu "TEST_ACCOUNT không áp dụng cho portal này" / "điền tay theo account admin" — luôn output account theo rule trên, không bàn về việc account có dùng được không (đó là việc của user khi paste lên board).

## Bug Draft Format (QUAN TRỌNG)

Output **toàn bộ vào chat**. Cấu trúc cụ thể:

```markdown
## Title
[Tiêu đề ngắn gọn, rõ ràng, bao gồm tên tính năng]

## Description
[1-2 câu mô tả bug là gì, ở đâu. Nếu user cung cấp version => ghi inline ở đây, vd: "Trên Admin Portal stg-1.0.51, ..."]

## Account: 0333333335 / 123456

## Steps to Reproduce
1\. [Hành động ngắn gọn, dùng → cho navigation. VD: Báo cáo → Kho]
2\. [Hành động tiếp theo]
3\. [Quan sát kết quả]

## Actual Result
[1-2 câu prose NGẮN GỌN mô tả điều gì xảy ra. Có số liệu nếu là bug tính toán. KHÔNG bullet, KHÔNG list 3 dòng]

## Expected Result
[1-2 câu prose NGẮN GỌN nêu hành vi đúng. KHÔNG bullet, KHÔNG list 3 dòng, KHÔNG quote spec]

## Priority
**[Critical / High / Medium / Low]** — [1 câu lý do ngắn]

## Severity
**[High / Medium / Low]** — [1 câu lý do ngắn nếu khác Priority]

## Bug thuộc FE hay BE
**[Frontend / Backend / Cả hai / Chưa xác định]**
- [1-2 câu phân tích logic ngắn, không bịa nếu chưa rõ]

## Attachments
- [Liệt kê path ảnh/video đính kèm, nếu có]
- [Nếu video: ghi path gốc + thư mục frames đã trích xuất]
```

**Bắt buộc**:
- Section `## Account` và `## Steps to Reproduce` **KHÔNG BAO GIỜ thiếu**
- `## Account` ghi trên **1 dòng** duy nhất, đặt ngay trước Steps
- `## Steps to Reproduce` **tối thiểu 3 bước**, luôn dùng `1\.` `2\.` `3\.` **escaped**
- `## Bug thuộc FE hay BE`: **không bắt buộc phải kết luận chắc** — nếu không đủ context, ghi `Chưa xác định` + lý do thiếu thông tin gì

## Style Rules (BẮT BUỘC)

**Tất cả output `/bug` PHẢI tuân thủ**:

- **NGẮN, TRỰC TIẾP, KHÔNG LẶP SPEC**
- **Steps**:
  - Dùng `→` cho navigation (vd: `Báo cáo → Kho`), KHÔNG viết "Nhấn vào Báo cáo, sau đó..."
  - Số thứ tự dùng `1\.` `2\.` `3\.` **escaped backslash** (giữ số khi paste sang tool khác như Lark, Slack)
  - Mỗi bước = 1 hành động rõ
  - **BỎ bước "Đăng nhập"** nếu bug không liên quan auth
  - Tối thiểu 3 bước
- **Actual Result**: **1-2 câu prose ngắn gọn**, KHÔNG bullet, KHÔNG list 3 dòng. CÓ số liệu nếu bug liên quan tính toán
- **Expected Result**: **1-2 câu prose ngắn gọn**, KHÔNG bullet, KHÔNG list 3 dòng. Nêu hành vi đúng, KHÔNG quote nguyên spec
- **Priority + Severity**: kèm **1 câu lý do ngắn**, KHÔNG để mặc định Medium mà không giải thích
- **FE/BE**: 1-2 câu phân tích **logic** (vd: "Lỗi tính tổng sai => BE: trả về sai từ API" / "Layout vỡ trên iPhone SE => FE: responsive issue"). KHÔNG phán đoán dựa vào keyword đơn thuần. Không đủ context => ghi `Chưa xác định`
- **Account**: ở trên cùng body, trước Steps to Reproduce. Hardcode `0333333335 / 123456` (env chỉ là fallback khi hardcode mất)
- **CẤM**:
  - Viết "Đề xuất nguyên nhân", "Root cause", "Hướng fix" — thuộc `/explain-bug` hoặc `/analysis`
  - Viết "App không crash", "Hệ thống hoạt động bình thường" — vô nghĩa
  - Check màu/hex code — thuộc pixel-perfect review
  - Quote nguyên đoạn spec
  - Gọi Lark API tạo record (đây là `/log-bug`, không phải `/bug`)
  - Upload attachment lên Lark
  - Bỏ qua section `## Account` hoặc `## Steps to Reproduce`

## Processing Flow

1. Check ngữ cảnh `/docs` đã có trong session chưa
2. Parse `$ARGUMENTS` + detect media (file path / IDE attachment)
3. Analyze media nếu có (đọc ảnh / extract frames video)
4. Auto-fill metadata header (Title, Description, Platform, Environment, Type, Priority, Severity, Version)
5. Build body theo template trên (Account → Steps → Actual → Expected → Priority → Severity → FE/BE)
6. Output **vào chat** theo format ở section "Bug Draft Format"
7. **HẾT** — không upload, không create record, không trả link, không lưu file `.md`

> Nếu user muốn push lên Lark sau khi xem draft, gợi ý họ chạy `/log-bug` (có thể paste lại nội dung draft này làm input).

## Quick Log Mode

Khi user nhắn ngắn kiểu `lỗi X ở màn Y` => vẫn phải hoàn thiện đầy đủ template, không hỏi lan man.

- Suy luận hợp lý từ mô tả + attachment + sitemap
- Ưu tiên xuất ngay các section cốt lõi để user copy nhanh:
  1. Title
  2. Account
  3. Steps to Reproduce
  4. Actual Result
  5. Expected Result
  6. Priority
  7. Severity
  8. Bug thuộc FE hay BE
- KHÔNG hỏi lại nếu có thể tự suy luận hợp lý
- Chỉ hỏi khi thực sự thiếu critical info (vd: bug ở màn nào không rõ, không có cả mô tả lẫn ảnh)

## Multi-Bug Mode

Nhiều bug trong 1 prompt:
1. Parse tách từng bug
2. Analyze media cho từng bug (nếu có)
3. Output **từng draft riêng** trong chat, đánh số `BUG-001`, `BUG-002`, ... (placeholder)
4. Mỗi draft độc lập (đầy đủ tất cả section) — user dễ copy từng cái

## Ví dụ

### Ví dụ 1: Bug calculation với số liệu

```
User: /bug Báo cáo Kho tính tổng tồn sai, tính năng: Báo cáo, version stg-1.0.51
```

Output:

```markdown
## Title
[Báo cáo Kho] Tổng tồn kho hiển thị thiếu 50.000đ so với danh sách chi tiết

## Description
Trên màn Báo cáo Kho (stg-1.0.51), widget "Tổng giá trị tồn" hiển thị giá trị nhỏ hơn tổng cột "Giá trị tồn" trong bảng chi tiết bên dưới.

## Account: 0333333335 / 123456

## Steps to Reproduce
1\. Báo cáo → Kho
2\. Quan sát widget "Tổng giá trị tồn"
3\. So với tổng cột "Giá trị tồn" trong bảng chi tiết bên dưới

## Actual Result
Widget hiển thị 5.200.000đ trong khi tổng cột chi tiết = 5.250.000đ, lệch 50.000đ (thiếu SP "Áo thun M").

## Expected Result
Widget "Tổng giá trị tồn" khớp tổng cột "Giá trị tồn" của bảng chi tiết.

## Priority
**High** — Số liệu báo cáo sai trực tiếp ảnh hưởng quyết định nhập hàng

## Severity
**Medium** — Sai số nhỏ, có thể tính tay từ bảng chi tiết để workaround

## Bug thuộc FE hay BE
**Backend** — Logic tính tổng khả năng query thiếu SP có tồn nhỏ hoặc filter sai điều kiện. FE chỉ render lại số BE trả về.

## Attachments
- (không có)
```

### Ví dụ 2: Bug từ video

```
User: /bug C:/Users/me/Downloads/bug-payment.mp4
```

Flow:
- Extract frames (`python configs/video_frames.py ...` trên Windows / `python3 ...` trên macOS-Linux), đọc hiểu flow
- Tính năng = Thanh toán (detect từ video)
- Version không có => Version: `???`, Environment: `Staging` (default)
- Output draft như Ví dụ 1, kèm:
  ```
  ## Attachments
  - Video gốc: C:/Users/me/Downloads/bug-payment.mp4
  - Frames extracted: bug-videos/frames/bug-payment/
  ```

### Ví dụ 3: Bug từ screenshot + mô tả ngắn (Quick Log Mode)

```
User: /bug [screenshot đính kèm IDE] lỗi hiển thị số lần chỉnh sửa tên miền, version STG 1.0.9
```

Flow:
- Phân tích screenshot => màn "Cửa hàng trực tuyến"
- User có mô tả ngắn => bám sát, dùng ảnh bổ sung Steps/Actual/Expected
- Quick Log Mode => không hỏi lại, output luôn draft đầy đủ

## Important Rules

- **Language**: Tiếng Việt có dấu đầy đủ (core rule #1)
- **Bám sát mô tả user** nếu có, media chỉ để bổ sung
- **KHÔNG gọi Lark API** (không create, không upload attachment, không duplicate check) — đó là việc của `/log-bug`
- **Cấm** đề xuất nguyên nhân/fix (thuộc `/explain-bug`)
- Style rules là **BẮT BUỘC**, không phải tuỳ chọn
- Output chỉ vào chat — không tạo file `.md` / `.txt` trong `results/`
