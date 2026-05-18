Log bug lên Lark Bitable từ mô tả trong prompt, kèm ảnh/video nếu có.

## Role

You are a **Senior QC Engineer** logging bugs into the team's Lark Bitable bug tracking board. Output must follow the team's bug template exactly.

## Config Loading

- **Always read**: `.claude/rules/core.md`
- **Read**: `.claude/docs/lark-integration.md` (for Lark Bitable interaction)
- **Read**: `.claude/docs/severity-priority-framework.md` (quy tắc chấm Severity/Priority dùng chung)
- **Read cache**: `configs/lark_bug_board_cache.json` (cached field options - Dev PIC, Sprint, Platform, Version, etc.)

## Lark API - Python-First (CRITICAL)

- **MANDATORY**: Dùng Python qua `configs/lark_api.py` cho MỌI thao tác Bitable (list/get/search/create/update/list_fields). **KHÔNG** dùng `mcp__lark-mcp__*` — MCP gần như luôn fail `99991668 token expired`.
- Upload attachment: `configs/lark_bitable.py` (helper riêng — MCP không support).
- Import cần dùng: `from configs.lark_api import create_record, search_records, list_fields, update_record, get_record`.

## Lark Bug Board Config

- Read board config from `.env` via `configs/env_loader.py`:
  - `get_lark_bug_board()` => `(base_id, table_id)`
- If `.env` has `LARK_BUG_BASE_ID` + `LARK_BUG_TABLE_ID` => use those (`LARK_BUG_BASE_NAME` dùng để hiển thị/xác nhận board)
- If not set => ask user for Lark Bitable URL, extract IDs from URL pattern: `https://<domain>.larksuite.com/base/<BASE_ID>?table=<TABLE_ID>`
- If board was provided via prompt URL (e.g., user pastes a Lark wiki/base link with `?table=`) => extract and use directly

## Read-only Guard (BLOCK trước mọi thao tác create)

**MUST CHECK trước khi tạo record bất kỳ.** Nếu bug board active được đánh dấu read-only => DỪNG, không tạo record.

### Cách check (theo thứ tự)

1. **`.env` flag**: đọc `LARK_BUG_READ_ONLY` (xem trực tiếp file `.env`). Giá trị `true` / `1` / `yes` (case-insensitive) => board read-only.
2. **State file**: đọc `.claude/.board-state.json`, key `read_only`. Giá trị `true` => read-only.
3. **Registry note**: trong `.claude/boards.md`, section của board hiện tại có dòng `Mode | **READ-ONLY**` hoặc cảnh báo "KHÔNG `/log-bug`" => read-only.

Bất kỳ nguồn nào báo read-only => coi là read-only.

### Behavior khi board read-only

- **DỪNG ngay**, KHÔNG tạo record.
- Hiển thị thông báo cho user:

  ```text
  Board active **`<alias>`** (LARK_BUG_BASE_NAME=`<base_name>`) đang ở chế độ **READ-ONLY** (production view).
  Tôi sẽ không log bug lên đây để tránh ghi vào dữ liệu thật.

  Để log bug:
    1. Chuyển sang board STG: `/update-board tracking bug: <URL board STG>`
    2. Hoặc tạm bypass nếu thực sự cần: xóa `LARK_BUG_READ_ONLY=true` trong `.env` rồi gửi lại

  Boards STG có sẵn (registry: .claude/boards.md):
    - <alias 1>
    - <alias 2>
  ```

- KHÔNG tự động đổi board, KHÔNG tự bypass — phải để user ra quyết định.
- Vẫn cho phép `/explain-bug`, `/check-duplicate-bug`, `/sla`, `/health`, `/triage`, `/release-check`, `/risk` chạy bình thường (chỉ đọc dữ liệu).

### Bypass

- Nếu user truyền `LARK_BUG_READ_ONLY=false` trong prompt hoặc explicit nói "tôi biết đây là production, vẫn log" => OK, vẫn yêu cầu confirm 1 lần nữa trước khi create.
- Nếu user paste URL board khác trong prompt => dùng URL đó, bỏ qua read-only check của board active (nhưng vẫn check read-only của board mới — nếu URL paste cũng read-only => block).

## Multi-board confirmation (DAILY CHECK - IMPORTANT)

Project tracks **multiple bug boards** (registry: `.claude/boards.md`). Mỗi đầu ngày, log bug **đầu tiên** PHẢI confirm với user xem có đang trỏ đúng board không, để tránh log nhầm.

### Workflow

1. **Đếm board** trong `.claude/boards.md` (mục "Boards registry"). Nếu chỉ có 1 board => skip toàn bộ confirmation, log thẳng.
2. **Đọc state file** `.claude/.board-state.json` (gitignored, machine-local). Format:
   ```json
   {"last_confirm_date": "2026-04-25", "confirmed_alias": "Shinhan"}
   ```
3. **Lấy ngày hôm nay** (system clock, format `YYYY-MM-DD`) và alias hiện đang active (đọc `LARK_BUG_BASE_NAME` từ `.env`, đối chiếu với registry để tìm alias).
4. **Compare**:
   - Nếu `last_confirm_date` == hôm nay AND `confirmed_alias` == alias hiện tại => skip confirmation, tiếp tục log bình thường.
   - Nếu khác (hoặc file chưa tồn tại) => HIỂN THỊ confirmation:

     ```
     Hôm nay là bug đầu tiên trong ngày. Hiện `.env` đang trỏ board: **Shinhan** (LARK_BUG_BASE_NAME="SBH STG Overview").

     Boards có sẵn:
       1. Shinhan (active)
       2. SoBanHang

     Bạn muốn log bug này lên **Shinhan** đúng không? (yes/no, hoặc gõ tên board khác)
     ```

5. **Xử lý phản hồi**:
   - `yes` / xác nhận đúng board hiện tại => update state file (last_confirm_date = hôm nay, confirmed_alias = alias hiện tại) => tiếp tục log.
   - User chọn board khác => không tự đổi `.env` (việc swap board là manual). Báo: "Để đổi board sang **`<alias>`**, chạy `/update-board tracking bug: <board_URL>`. Sau khi đổi xong, gửi lại lệnh log bug." => DỪNG, không tạo record.
   - User reply mơ hồ => hỏi lại 1 lần.

### State file management

- Đường dẫn: `.claude/.board-state.json` (đã gitignore — machine-local).
- Tạo mới nếu chưa có. Schema:
  ```json
  {"last_confirm_date": "YYYY-MM-DD", "confirmed_alias": "<alias>"}
  ```
- Confirm xong => luôn ghi đè file với date hôm nay.

### Skip confirmation

- Nếu user **explicitly truyền URL board mới trong prompt** (paste wiki/base link) => skip confirmation cho lần đó, dùng board từ URL, KHÔNG update state file.
- Nếu chỉ có 1 board trong registry => không cần confirm.

## Field Cache (IMPORTANT - Use Before API)

- **Cache file**: `configs/lark_bug_board_cache.json` - contains cached options for: Dev PIC, Sprint, Platform, Tính năng, Type, Priority, Status, Version
- **Helper**: `configs/lark_bug_cache.py` - Python helper for searching/updating cache
- **Workflow**:
  1. Use cache FIRST to resolve field values (Dev PIC IDs, Sprint names, Tính năng...)
  2. Only call `list_fields(base, table)` from `configs.lark_api` if cache is missing or user says data has changed (CLI: `python3 configs/lark_api.py list-fields <base> <table>`)
  3. After fetching from API => update cache via helper functions
- **Dev PIC lookup**:

  ```bash
  python3 configs/lark_bug_cache.py find-dev "Example"
  # => ou_<openid>  Example, Developer Name
  ```

  - If user provides Dev PIC name and cache has a match => use the open_id directly in record creation
  - If no match found => ask user to clarify (MANDATORY field)
- **Other field lookup**:

  ```bash
  python3 configs/lark_bug_cache.py find tinh_nang "đơn hàng"
  python3 configs/lark_bug_cache.py find sprint "Sprint 12"
  python3 configs/lark_bug_cache.py find version "3.2.176"
  ```

- **Adding new entries** (when fetched from API):

  ```bash
  python3 configs/lark_bug_cache.py add-dev <open_id> <name> [alias1,alias2]
  python3 configs/lark_bug_cache.py add sprint <option_id> <name>
  ```

## Information Gathering

1. Receive input from user: "$ARGUMENTS"
2. Parse the prompt to extract bug information:

### Mandatory fields (MUST ask user if missing - DO NOT skip):
- **Dev PIC**: Developer(s) responsible. Lookup from cache. If not in prompt => ASK user
- **Sprint**: Current sprint. Lookup from cache. If not in prompt => read `DEFAULT_SPRINT` from `.env`. If `.env` also empty => ASK user
- **Version**: App/build version. Lookup from cache. If not in prompt => read `DEFAULT_VERSION` from `.env`. If `.env` also empty => ASK user
- **Tính năng**: Feature/module. Match from cache. If ambiguous or not in prompt => ASK user

### Update .env defaults (IMPORTANT)

When user **explicitly provides** Sprint or Version in the prompt AND it differs from current `.env` defaults:

- Update `DEFAULT_SPRINT` and/or `DEFAULT_VERSION` in `.env` so future `/log-bug` calls use the latest values
- Read `.env` file, find and replace the old value, write back
- This ensures the defaults stay current as sprints/versions change over time

### Auto-determined fields (agent fills in, no need to ask):
- **Name of bug**: Format `[Tên tính năng / màn hình] Mô tả bug sơ bộ`
  - Auto-generate from context if user describes the bug naturally
- **Platform**: Detect from prompt context. If not clear => default `App`
  - Keywords: "web", "website", "trình duyệt" => `Web`
  - Keywords: "app", "mobile", "điện thoại", "iOS", "Android" => `App`
  - Keywords: "admin", "portal", "admin portal" => `Admin Portal`
  - Keywords: "tablet" => `App`
- **Type**: Determine from bug description:
  - UI issues (hiển thị, layout, text sai, icon, spacing...) => `UI/UX`
  - Logic, flow, validation, data issues => `Function`
  - Slow, timeout, lag => `Performance`
- **Priority / Severity**: See "Priority & Severity Handling" section below
- **Input data / Action**: Steps to reproduce (see template below)
- **Expected result**: What should happen
- **Status**: Always set to `New`
- **Attachment**: See "Attachment Handling" section below

## Priority & Severity Handling (IMPORTANT)

Some boards have both **Priority** and **Severity** fields, some only have **Priority**. Handle dynamically:

### Step 1: Detect if board has Severity field

- Check cache (`configs/lark_bug_board_cache.json`) for `severity` key
- If not in cache => call `bitable_v1_appTableField_list` to check actual board fields
- If board has Severity field => apply rules below
- If board does NOT have Severity => skip, only use Priority (old behavior)

### Step 2: Determine values based on user input

| User provides | Priority value | Severity value |
|---------------|---------------|----------------|
| **Priority only** (e.g., "priority: High") | User's value | **Same as Priority** (auto-sync) |
| **Severity only** (e.g., "severity: Critical") | **Same as Severity** (auto-sync) | User's value |
| **Both explicitly** (e.g., "priority: High, severity: Critical") | User's Priority value | User's Severity value |
| **Neither** | ASK user | ASK user |

### Step 3: Auto-estimate (when user provides neither)

If user doesn't specify either Priority or Severity, estimate from bug description:
- Crash, data loss, security, block flow => `Critical`
- Main feature broken, no workaround => `High`
- Feature impaired, workaround exists => `Medium`
- Minor, cosmetic, nice-to-have => `Low`
- If unclear => default `Medium`
- Use estimated value for BOTH Priority and Severity (if board has Severity)

### Notes:
- Priority and Severity may have different option lists on some boards. When auto-syncing, match the closest available option by name
- If exact match not found in target field's options => ask user to clarify
- Trước khi create record, validate kết quả theo `.claude/docs/severity-priority-framework.md`. Nếu user-provided level mâu thuẫn rõ ràng với evidence, hiển thị cảnh báo và ask user confirm.

## Attachment Handling & Visual Bug Analysis (CRITICAL)

**RULE #1**: When user provides image/video (any source), you **MUST read and analyze the content** to understand the bug: what screen, what steps led to the issue, what is the actual vs expected behavior. The image/video IS the primary source of truth for the bug description.

**RULE #2**: If user also provides a brief text description, **follow and prioritize that description** - use image/video to supplement details (Steps, Actual, Expected) rather than overriding the user's intent.

### Source 1: Image attached via IDE (+ button) or visible in conversation

When an image/screenshot is **visible in the conversation context** (attached via IDE's `+` button):

1. **ANALYZE the image to understand the bug** (MANDATORY):
   - Examine the screenshot carefully: identify the screen/feature shown
   - Detect visual issues: wrong layout, missing elements, incorrect data, error messages, UI glitches
   - Detect functional issues: wrong state, unexpected behavior visible in the UI
   - Use the visual analysis to auto-generate: bug Name, Steps, Actual result, Expected result
   - If user only provides keywords (e.g., "màn hình Thanh toán, priority low") => **the image IS the bug description** - extract all bug details from it
   - If user provides a brief description (e.g., "lỗi hiển thị số lần chỉnh sửa") => **follow user's description**, use image to fill in Steps/Actual/Expected
2. **Upload limitation**: IDE-attached images exist only as base64 in context - cannot be saved to disk for Lark upload. Inform user they can add attachment manually on the board, or re-send with file path.

### Source 2: File path in prompt (image or video)

When user provides a **file path** (e.g., `attachment: /path/to/file.png`):

**Detect file type**:
- Image (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.bmp`) => **read image + upload**
- Video (`.mp4`, `.mov`, `.avi`, `.webm`, `.mkv`) => **extract frames + analyze + upload**

**For images** (file path):
1. Read the image using the Read tool to analyze its content
2. Analyze the image to understand the bug (same as Source 1 step 1)
3. Upload to Lark: `python3 configs/lark_bitable.py upload <file_path> --base <base_id>`
4. Get `file_token` for the attachment field

**For videos** (file path):

**Suggested folder**: `bug-videos/` at project root. If user doesn't provide a path (or path doesn't exist), suggest: "Bạn bỏ video vào `e:/FINAN -AUTO TEST/QA Ops Suite/bug-videos/` rồi gọi lại với path đầy đủ nhé". Video attached via IDE `+` button => reject (no real file path => cannot upload to Lark).

1. **Check duration first** (MANDATORY - max 2 minutes):
   ```bash
   python3 configs/video_frames.py <video_path> --json
   ```
   - If duration > 120s => reject with message: "Video quá dài (Xs). Vui lòng cắt video dưới 2 phút."
   - If ffmpeg not installed => inform user: "Cần cài ffmpeg: `brew install ffmpeg` (macOS) hoặc download từ ffmpeg.org (Windows)"

2. **Extract key frames**:
   ```bash
   python3 configs/video_frames.py <video_path>
   ```
   - Script auto-calculates optimal frame timestamps based on duration
   - Short video (<5s): 2-3 frames
   - Medium (5-30s): frame every 3-5s
   - Long (30-120s): frame every 8-15s
   - Max 10 frames by default

3. **Analyze extracted frames**: Read all extracted frame images using the Read tool to understand the bug flow:
   - Frame sequence shows: initial state => user action => bug manifestation
   - Generate Steps from the frame sequence
   - Identify the bug from visual changes between frames
   - Generate Actual and Expected results

4. **Upload original video** to Lark as attachment (not the frames):
   ```bash
   python3 configs/lark_bitable.py upload <video_path> --base <base_id>
   ```

### Source 3: Both image and video provided

When user provides **both** image and video (or multiple files):
- Process each file with its corresponding handler (image analysis + video frame extraction)
- Combine insights from all sources to generate a comprehensive bug description
- Upload all files as attachments to the bug record

### Upload command:

```bash
python3 configs/lark_bitable.py upload <file_path> --base <base_id>
```

- If upload fails => create bug without attachment, note the failure, user can add manually
- If multiple files => upload each, collect all file_tokens for the Attachment field array

## Test Account Handling

- **Read** test account from `.env` via `configs/env_loader.py`: `get_test_account()`
- If `TEST_ACCOUNT` is set in `.env` AND user does NOT provide a different account in the prompt:
  - **Append** to the `Input data / Action` field, at the end (after Notes):
    ```
    Account test: <value from .env>
    ```
- If user provides a specific account in the prompt (e.g., "account: 09xxx - 123") => use user's account instead of `.env` value
- If `TEST_ACCOUNT` is NOT set => do nothing, skip this section

## Bug Template Format

The `Input data / Action` field follows this structure:

```
Preconditions (nếu có):
- <điều kiện tiên quyết>

Steps:
1. <bước 1>
2. <bước 2>
...

Actual:
- <kết quả thực tế>

Notes (nếu có):
- <ghi chú bổ sung>

Account test: <từ .env hoặc prompt, nếu có>
```

The `Expected result` field:

```
Expected:
- <kết quả mong đợi>
```

## Duplicate Bug Check (delegated to `/check-duplicate-bug`)

**Controlled by `.env` flag**: `CHECK_DUPLICATE_BUG` (default: `true`)
- `true` => gọi command `/check-duplicate-bug` trước khi create bug
- `false` => bỏ qua duplicate check, create bug trực tiếp

Read flag:
`python3 -c "import sys; sys.path.insert(0, '.'); from configs.env_loader import load_env; load_env(); import os; print(os.getenv('CHECK_DUPLICATE_BUG', 'true'))"`

Nếu flag là `false` => bỏ qua toàn bộ bước check duplicate.

Nếu flag là `true` => sau khi parse xong bug draft (Name, Tính năng, Platform, Priority, Sprint, Version), **KHÔNG tự search inline trong `/log-bug` nữa**. Thay vào đó, gọi trực tiếp command riêng:

```text
COMMAND: /check-duplicate-bug
ARGUMENTS:
name: <generated bug name>
feature: <tính năng>
platform: <platform>
priority: <priority>
sprint: <sprint>
version: <version>
keywords: <optional, comma-separated>
```

Xử lý kết quả từ `/check-duplicate-bug`:
- Không có bug trùng liên quan => tiếp tục create bug
- Có bug trùng tiềm năng => hiển thị danh sách và hỏi user:
  - (a) Vẫn tạo bug mới
  - (b) Không tạo vì trùng
- Nếu duplicate check lỗi API/network => log warning, **không block** create bug (tiếp tục tạo)

---

## Processing Flow (IMPORTANT - 2 modes)

### Mode 1: FULL INFO => Create immediately, NO confirm needed

If the prompt contains ALL of the following => ~~create bug directly~~ **run `/check-duplicate-bug` first** (khi flag bật), rồi create nếu không trùng (hoặc user xác nhận vẫn tạo):
- Bug description (enough to generate Name, Steps, Expected result) - from text AND/OR image/video analysis
- Dev PIC (name matchable in cache)
- Sprint (from prompt OR `DEFAULT_SPRINT` in `.env`)
- Version (from prompt OR `DEFAULT_VERSION` in `.env`)
- Tính năng (matchable in cache or clearly determinable)

**Flow**: Parse => analyze image/video (if any) => lookup cache => fallback Sprint/Version from `.env` => **call `/check-duplicate-bug` (if `CHECK_DUPLICATE_BUG=true`)** => upload attachment (if any) => create record => update `.env` defaults if user provided new Sprint/Version => return link. Done.

### Mode 2: MISSING mandatory fields => Ask user FIRST

If any of **Dev PIC, Sprint, Version, Tính năng** is missing from BOTH prompt AND `.env` defaults:
1. Parse what's available, auto-fill what you can (Name, Platform, Type, Priority, Steps, Expected)
2. Analyze image/video to generate Steps, Actual, Expected (MANDATORY if media provided)
3. Display draft with missing fields highlighted
4. ASK user to provide the missing mandatory fields
5. Once user provides => **call `/check-duplicate-bug` (if `CHECK_DUPLICATE_BUG=true`)** => create record => update `.env` defaults => return link

**Draft format for Mode 2**:

```
--- Bug Draft ---
Name: [Tính năng] Mô tả bug
Platform: App
Type: Function
Priority: Medium
Status: New

Input data / Action:
Steps:
1. ...

Actual:
- ...

Expected result:
- ...

Attachment: <file path or "từ IDE attachment">

--- Cần bổ sung ---
- Dev PIC: ???
- Sprint: ???
- Version: ???

Vui lòng cung cấp các thông tin trên để tạo bug.
```

### After record created (both modes):
- Build the **direct link to the bug record** using `get_lark_record_url('bug', record_id)` from `configs/env_loader.py`
  - This constructs: `https://<domain>/wiki/<wiki_token>?table=<table_id>&view=<view_id>&record=<record_id>`
  - `record_id`: from the create record response field `record_id` (e.g., `recXXXXX`)
  - Fallback if wiki_token not set: `https://<domain>/base/<base_id>?table=<table_id>&record=<record_id>`

### Field mapping (SBH UAT board):

| Template Field | Lark Field Name | Field Type |
|---------------|----------------|------------|
| Name of bug | Name of bug | Text |
| Platform | Platform | SingleSelect |
| Tính năng | Tính năng | MultiSelect |
| Type | Type | SingleSelect |
| Priority | Priority | SingleSelect |
| Severity | Severity | SingleSelect (optional - board may not have this field) |
| Status | Status | SingleSelect (always "New") |
| Input data / Action | Input data / Action | Text |
| Expected result | Expected result | Text |
| Attachment | Attachment | Attachment (file_token) |
| Version | Version | SingleSelect |
| Sprint | Sprint | SingleSelect |
| Dev PIC | Dev PIC | User (open_id, multiple) |

## Multi-Bug Mode

If user describes **multiple bugs** in one prompt:
1. Parse and separate each bug
2. Check mandatory fields for ALL bugs
3. If all bugs have full info => create all sequentially, return summary
4. If any bug missing mandatory fields => display all drafts, ask user to fill missing fields, then create
5. Return summary table with all Bug IDs and links

## Important Rules

- **NEVER modify or delete existing records** - this command only CREATES new bugs
- **Full info = no confirm needed** - just create and return link
- **Missing mandatory fields = must ask** - Dev PIC, Sprint, Version, Tính năng are required
- If board fields don't match the template (different field names) => read field list first via Python `list_fields(base, table)` from `configs.lark_api` (CLI: `python3 configs/lark_api.py list-fields <base> <table>`) and adapt
- Vietnamese content MUST have proper diacritics (core rule)
- Steps must be clear and reproducible (same quality standard as test cases)

## Examples

### Example 1: Full info + video => create immediately (Mode 1)

```
User: /log-bug /Users/me/Downloads/bug.mp4, dev pic: Tường
  [.env has DEFAULT_SPRINT=1-2026/4, DEFAULT_VERSION=1.0.50]

=> Agent: analyzes video frames => understands bug flow from visual content
=> Dev PIC from prompt, Sprint + Version from .env defaults, Tính năng from video context
=> All mandatory fields resolved => Mode 1
=> Upload video => create record => return link

Response:
Bug đã tạo thành công!
- Name: [Cửa hàng trực tuyến] Tìm kiếm địa chỉ Website không tìm thấy domain hiện tại
- Link: https://sobanhang.sg.larksuite.com/wiki/<token>?table=<id>&view=<id>&record=recXXXXX
```

### Example 2: Full info + user provides Sprint/Version => create + update .env

```
User: /log-bug Bán hàng bị crash khi quét barcode.
  Dev Pic: Hung, Sprint 2-2026/4, version 1.0.51
  attachment: /tmp/screenshot.png
  [.env has DEFAULT_SPRINT=1-2026/4, DEFAULT_VERSION=1.0.50]

=> Agent: Sprint + Version from prompt differ from .env defaults
=> Upload attachment => create record => return link
=> Update .env: DEFAULT_SPRINT=2-2026/4, DEFAULT_VERSION=1.0.51
```

### Example 3: Missing Dev PIC => ask user (Mode 2)

```
User: /log-bug App bán hàng bị crash khi nhấn nút thanh toán với giỏ hàng trống
  [.env has DEFAULT_SPRINT=1-2026/4, DEFAULT_VERSION=1.0.50]

=> Agent: Sprint + Version from .env, Tính năng = Bán hàng => OK
=> Missing: Dev PIC only
=> Display draft + ask:

--- Bug Draft ---
Name: [Bán hàng] App crash khi thanh toán với giỏ hàng trống
...
--- Cần bổ sung ---
- Dev PIC: ???

=> User replies: Dev Pic: Trung
=> Agent creates record => returns link
```

### Example 4: Bug from screenshot + brief description (follow user's description)

```
User: /log-bug [attached screenshot via + button]
  Lỗi hiển thị số lần chỉnh sửa tên miền
  Dev: Tuong, Sprint 1-2026/4, version STG 1.0.9

=> Agent: analyzes screenshot => sees "Cửa hàng trực tuyến" screen
=> User provided brief description "Lỗi hiển thị số lần chỉnh sửa tên miền"
   => FOLLOW user's description as primary intent
   => Use screenshot to fill in Steps, Actual, Expected around that description
=> All mandatory fields present
=> Create record => update .env (Sprint + Version differ) => return link
```

### Example 5: Bug from video + no text description (video IS the description)

```
User: /log-bug /Users/me/Desktop/bug-recording.mp4
  Dev: Trung

=> Agent: extracts frames => reads all frames to understand bug flow:
   Frame 1: Màn hình tạo đơn hàng, đã nhập sản phẩm
   Frame 2: Nhấn nút "Tạo đơn"
   Frame 3: Loading spinner hiển thị
   Frame 4: Spinner vẫn quay, không kết thúc
=> Video IS the bug description => generate Name, Steps, Actual, Expected entirely from frames
=> Sprint + Version from .env defaults
=> Upload video => create record => return link
```

### Example 6: Multiple bugs

```
User: /log-bug Dev: Trung
1. Web: popup xác nhận xóa sản phẩm bị mất nút "Hủy"
2. App: trang đăng nhập thiếu loading khi nhấn đăng nhập
  [.env has DEFAULT_SPRINT=1-2026/4, DEFAULT_VERSION=1.0.50]

=> Sprint + Version from .env, all mandatory fields present for both
=> Create 2 records => return summary:

| # | Name | Platform | Link |
|---|------|----------|------|
| 1 | [Quản lý sản phẩm] Popup xóa thiếu nút "Hủy" | Web | link1 |
| 2 | [Login] Thiếu loading khi đăng nhập | App | link2 |
```
