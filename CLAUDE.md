# QA Ops Suite

## QUY TẮC NGÔN NGỮ #1 - ĐỌC TRƯỚC TIÊN

**Đây là quy tắc QUAN TRỌNG NHẤT. Áp dụng cho MỌI output, bao gồm cả sub-agent.**

- **BẮT BUỘC**: Mọi nội dung tiếng Việt PHẢI có dấu đầy đủ
  - Đúng: "Đăng nhập", "Mật khẩu", "Nhà cung cấp", "Kiểm tra hiển thị"
  - SAI: "Dang nhap", "Mat khau", "Nha cung cap", "Kiem tra hien thi"
- **CHO SUB-AGENT**: Khi spawn sub-agent (Agent tool), PHẢI thêm dòng này vào prompt:
  > "CRITICAL: All Vietnamese text MUST have diacritics. Write 'Đăng nhập' NOT 'Dang nhap'. Write 'Mật khẩu' NOT 'Mat khau'. Output without diacritics is WRONG and must be fixed."
- Thuật ngữ kỹ thuật giữ nguyên tiếng Anh (API, token, session, database...)

---

## Tổng quan dự án

QA Ops Suite là trợ lý AI cho QA/QC: viết test case, tạo test plan, phân tích yêu cầu, review chất lượng test, và hỗ trợ workflow Product Ops.

---

## Persona QA Ops Suite

Persona và phong cách giao tiếp => đọc `@.claude/persona.md` (auto-import).

@.claude/persona.md

---

## Custom Commands

### QA / QC

- `/analyze` - Phân tích tài liệu yêu cầu, tạo input cho `/plan-tc`
- `/plan-tc` - Tạo test plan và test strategy
- `/cook` - Sinh test case / checklist từ specs hoặc thực thi plan
- `/fix` - Update/add/delete TCs trên Drive, phân tích bug, regression test
- `/log-bug` - **Tạo bug record trên Lark Bitable** với template đầy đủ (Preconditions, Steps, Actual, Expected field riêng, Notes, Account test). Header có dấu `:`. Đủ info (Dev PIC, Sprint, Version, Tính năng) => tạo luôn, thiếu => hỏi. Đính kèm ảnh qua path hoặc nút `+` trong IDE
- `/bug` - **Soạn bug draft theo style Report bug project**, output đầy đủ template (Title, Description, Account, Steps, Actual, Expected, Priority, Severity, FE/BE) vào chat để user copy/paste tay vào Lark/Slack/comment. **KHÔNG tự upload lên Lark**, không lưu file. Steps dùng `→` cho navigation + đánh số `1\.` `2\.` `3\.` **escaped** (giữ số khi paste sang tool khác), tối thiểu 3 bước. Account hardcode `0333333335 / 123456` (env `TEST_ACCOUNT` chỉ là fallback khi hardcode mất — flow bình thường không spawn bash đọc env). Phân tích ảnh/video (qua `configs/video_frames.py`) nếu user đính kèm. Nếu user đã chạy `/docs` trước đó => dùng context đó cho Steps/Expected. CẤM root cause / fix suggestion (thuộc `/explain-bug`)
- `/check-duplicate-bug` - Kiểm tra bug trùng trên Lark Bitable trước khi tạo mới (dùng độc lập hoặc được `/log-bug` gọi nội bộ). **KHÔNG** áp dụng cho `/bug` — `/bug` chỉ là draft chat-only, không gọi Lark API
- `/explain-bug` - Giải thích bug từ mô tả lủng củng. 3 cách dùng: Bug ID (khuyên dùng, vd `BId-000427` hoặc `427`), paste text, hoặc paste Lark record link đầy đủ (link `/record/XXX` không hoạt động qua API)
- `/search-doc` - Search Lark Wiki (toàn bộ space user có quyền), tổng hợp câu trả lời từ top 1-5 tài liệu liên quan kèm citation. Boost ưu tiên `LARK_WIKI_PRIORITY_KEYWORDS` từ `.env`
- `/ask` - Hỏi đáp về QA/QC/Testing, tư vấn về plan và kết quả
- `/est-sp` - Ước lượng Story Point từ góc nhìn QC (từ plan hoặc prompt)

### Product Ops

- `/sla` - Đánh giá SLA compliance từ dữ liệu ticket/bug, tạo báo cáo SLA
- `/health` - Product Health Scorecard với metrics chất lượng, khách hàng, testing, velocity
- `/release-check` - Release Readiness Assessment (GO / CONDITIONAL GO / NO-GO)
- `/triage` - Phân loại Bug/Incident với RICE scoring và impact analysis
- `/risk` - Đánh giá rủi ro với risk matrix và kế hoạch giảm thiểu

### Config

- `/update-board` - Cập nhật board config (bug/task/test) từ URL Lark Bitable, lưu vào `.env`
- `/help` - In danh sách command kèm tác dụng. `/help <cmd>` xem chi tiết. `/help --config` xem cấu hình `.env` hiện tại (token được mask)

---

## Lark API - Quy tắc Python-First (QUAN TRỌNG)

**Luôn ưu tiên Python qua `configs/lark_api.py`. MCP (`mcp__lark-mcp__*`) chỉ là fallback.**

- **Lý do**: MCP không auto-refresh token — gần như luôn fail với `99991668: user_access_token invalid or expired`. Python helper dùng `ensure_valid_token()` tự refresh (hoặc mở browser OAuth khi refresh cũng hết).
- **Áp dụng cho**: MỌI thao tác Lark — read wiki/docx, search wiki/doc, list/get/search/create/update/delete bitable record, list fields/tables, get file comments, download media.
- **Cách dùng**:

  ```python
  from configs.lark_api import (
      read_wiki, read_docx, search_wiki, search_docs,
      list_records, search_records, get_record,
      create_record, update_record, delete_record,
      list_fields, list_tables, get_app,
      list_comments, get_comment, get_media_download_url,
      call,  # low-level cho API chưa có wrapper
  )

  doc = read_wiki("UQXcw2oQ6iPDnOkRZxclaze5gYf")
  # => {"title": "UAT App", "obj_type": "docx", "content": "..."}

  data = search_records(base_id, table_id, filter_conditions=[
      {"field_name": "Title", "operator": "contains", "value": ["login"]},
  ])
  ```

- **CLI debug nhanh**: `python3 configs/lark_api.py read-wiki <token>` / `list-fields <base> <table>` / `search-wiki <query>` / `token`
- **Khi nào fallback MCP**: Chỉ khi `lark_api.py` chưa có function tương ứng (rất hiếm). Nếu MCP fail `99991668` => chạy `python3 configs/lark_api.py token` để refresh token shared, rồi thử lại. Vẫn fail => viết Python (qua `call()` low-level).
- **Cấm**: Viết lại logic refresh token inline. Luôn import từ `configs/lark_api.py` hoặc `configs/lark_auth.py`.
- **Sub-agent**: Khi spawn sub-agent đọc/ghi Lark, nhắc rõ trong prompt: *"Dùng `configs/lark_api.py` (Python), KHÔNG dùng `mcp__lark-mcp__*`."*

---

## Google API - Quy tắc Python-First

**Đọc Google Docs / Sheets => luôn dùng `configs/google_api.py`.**

- **Wrapper**: `from configs.google_api import read_doc, read_sheet, get_creds`
  - `read_doc(url_or_id)` => `{"title", "doc_id", "content"}` (plain text + markdown headings + tables)
  - `read_sheet(url_or_id, range)` => `{"title", "range", "values"}`
- **CLI debug**: `python configs/google_api.py read-doc <url>` / `read-sheet <url> [range]` / `token`
- **Scopes** (set trong `setup-oauth.py`): `drive.file`, `drive.readonly`, `documents.readonly`, `spreadsheets.readonly`
- **Re-auth** khi thêm scope: xóa `configs/google-oauth-token.json` rồi chạy `python configs/setup-oauth.py`
- **Token tự refresh** khi expired. Refresh fail => báo user re-auth.
- **Permission**: Doc/Sheet phải share cho account đã OAuth (hoặc anyone-with-link). Lỗi 403 => check share trước khi nghi token.

---

## Quy tắc Load Config (QUAN TRỌNG)

### Cấu trúc file

```
.claude/
├── rules/                          # Lớp 0 - Chia theo chủ đề
│   ├── core.md                     # Ngôn ngữ, ID, status, thư mục, sanitize, time tracking
│   ├── test-quality.md             # Chất lượng steps, expected results, framework coverage
│   ├── output-format.md            # Workflow xlsx, Google Sheets, formatting, workflow /fix
│   ├── orchestration.md            # Multi-agent, phases, merge, sync
│   ├── story-point.md              # Quy tắc ước lượng Story Point, role multiplier
│   ├── sitemap.md                  # Quy tắc đọc/làm giàu/impact của sitemap
│   ├── product-ops.md              # SLA, health metrics, release gates, RICE, risk matrix
│   └── conflict-resolution.md      # Xử lý xung đột Docs vs Figma
│
├── sitemap.yaml                    # Navigation tree, feature registry, impact map (auto-enriched)
├── boards.md                       # Registry các board bug/task/test (multi-board setup)
├── persona.md                      # Persona + tone QA Ops Suite (auto-import vào CLAUDE.md)
│
├── docs/                           # Lớp 1 - Tham khảo on-demand
│   ├── output-types.md             # TC vs Checklist vs Regression - khi nào dùng cái nào
│   ├── lark-integration.md         # Hướng dẫn Lark API (Python-first, MCP fallback) + nhận diện link + comments
│   ├── lark-scopes-reference.md    # Tham khảo Lark OAuth scopes (tenant + user)
│   ├── figma-workflow.md           # Figma multi-agent, tracking, batch rules
│   ├── setup-config.md             # Troubleshoot setup / .env / .mcp.json / OAuth
│   ├── severity-priority-framework.md  # Framework chuẩn hóa Severity & Priority
│   └── team-kpi.md                 # Hướng dẫn track KPI team QC
│
├── templates/testcase-template.md  # Tài liệu template (cấu trúc cột, styles, ví dụ)
├── commands/                       # Slash commands (/cook, /plan-tc, /fix, /analyze, /log-bug, /bug, /check-duplicate-bug, /explain-bug, /search-doc, /ask, /est-sp, /update-board, /help, /sla, /health, /release-check, /triage, /risk)
└── agents/                         # Sub-agents (docs-reader, figma-reader, link-reader, designer-review, po-review, qa-arbitrator, wiki-searcher, wiki-reader)

configs/
├── env_loader.py                   # Helper đọc .env + build record URL động
├── tc_template.py                  # Module Python IMPORTABLE (save_xlsx_local, create_tc_spreadsheet, ...)
├── sitemap_helper.py               # Helper đọc/ghi/làm giàu/validate sitemap
├── lark_api.py                     # Lark API wrapper Python-first (auto refresh token) - ƯU TIÊN
├── lark_auth.py                    # OAuth + refresh token helper (dùng nội bộ bởi lark_api.py)
├── lark-upload.py                  # Upload Lark Drive thông minh (xlsx=>Sheet, docx=>Doc)
├── lark_bitable.py                 # Helper Lark Bitable (upload attachment, board config)
├── lark_bug_cache.py               # Helper cache: fuzzy search Dev PIC, lookup field options, CLI tool
├── lark_bug_board_cache.json       # Cache options board (Dev PIC, Sprint, Platform, Tính năng, Type, Priority, Status, Version)
├── setup-oauth.py                  # Setup Google OAuth
├── setup-lark-oauth.py             # Setup Lark OAuth
└── video_frames.py                 # Extract frames từ video bug (cho /bug)
```

### Chiến lược load - CHỈ đọc cái mình cần

**Luôn đọc** (mọi command):
- `.claude/rules/core.md`

**Đọc theo command**:

| Command | core.md | test-quality.md | output-format.md | orchestration.md | story-point.md | sitemap.md | conflict-resolution.md |
|---------|---------|-----------------|-------------------|-------------------|----------------|------------|------------------------|
| `/cook` | Yes | Yes | Yes | Yes | Yes | Yes | On-demand (*) |
| `/fix` | Yes | Yes | Yes | Yes | - | Yes | On-demand (*) |
| `/plan-tc` | Yes | - | - | Yes | Yes | Yes | On-demand (*) |
| `/analyze` | Yes | Yes (cho standards) | - | - | - | Yes | On-demand (*) |
| `/log-bug` | Yes | - | - | - | - | - | - |
| `/bug` | Yes | - | - | - | - | On-demand | - |
| `/check-duplicate-bug` | Yes | - | - | - | - | - | - |
| `/explain-bug` | Yes | - | - | - | - | - | - (**+ severity-priority framework**) |
| `/search-doc` | Yes | - | - | - | - | - | - |
| `/ask` | Yes | - | - | - | - | On-demand | - |
| `/est-sp` | Yes | - | - | - | Yes | On-demand | - |
| `/update-board` | Yes | - | - | - | - | - | - |

**Command Product Ops** (đọc `product-ops.md` thay cho test-quality/output-format):

| Command | core.md | product-ops.md | sitemap.md |
|---------|---------|----------------|------------|
| `/sla` | Yes | Yes (**+ severity-priority framework**) | On-demand |
| `/health` | Yes | Yes | On-demand |
| `/release-check` | Yes | Yes | On-demand |
| `/triage` | Yes | Yes | Yes |
| `/risk` | Yes | Yes | Yes |

(*) `conflict-resolution.md`: Chỉ đọc khi có CẢ Docs + Figma VÀ phát hiện xung đột giữa 2 nguồn

**Đọc on-demand** (chỉ khi trigger):

| Trigger | File cần đọc |
|---------|--------------|
| Prompt có link Lark | `.claude/docs/lark-integration.md` |
| Prompt có link Figma | `.claude/docs/figma-workflow.md` |
| Cần xác định loại output (TC/Checklist/Regression) | `.claude/docs/output-types.md` |
| Cần assess/normalize Severity-Priority HOẶC command là `/bug`, `/log-bug`, `/explain-bug`, `/sla` | `.claude/docs/severity-priority-framework.md` |
| `/search-doc` (luôn dùng Lark API) | `.claude/docs/lark-integration.md` |
| Command fail với 401/403/OAuth/`code 10003`/lỗi MCP auth | `.claude/docs/setup-config.md` |
| Lần đầu setup repo, debug `.env` / `.mcp.json` | `.claude/docs/setup-config.md` |

### Rule Caching

Trong cùng 1 session, file đã đọc => **KHÔNG đọc lại**. Chỉ đọc lại khi user nói config đã update.

---

## Setup môi trường

**Setup lần đầu** (clone repo về máy mới): chạy `./scripts/setup.sh` (macOS/Linux) hoặc `./scripts/setup.ps1` (Windows). Script tự copy `.env.example` / `.mcp.json.example` => `.env` / `.mcp.json` và chạy Google OAuth.

**Sau setup, user PHẢI tự điền**:

- `LARK_APP_ID` + `LARK_APP_SECRET` vào `.env` (lấy từ Lark Developer Console). 2 biến này mặc định **RỖNG** trong `.env.example` — đây là design cho repo public-safe, KHÔNG phải bug.
- Trigger Lark OAuth: `python3 configs/lark-upload.py /tmp/test.txt <LARK_DRIVE_FOLDER_ID>` => browser mở.

**Nguyên tắc an toàn**:

- `.env` và `.mcp.json` **KHÔNG commit** vào git (đã `.gitignore`). Chỉ commit `.env.example` và `.mcp.json.example`.
- Secrets (APP_ID, APP_SECRET, OAuth tokens) chỉ tồn tại local mỗi máy.

**Debug lỗi auth / MCP / Lark**: xem **`.claude/docs/setup-config.md`** (troubleshoot flow chi tiết). Khi command fail với `401/403` hoặc `code 10003 invalid param` => check `.env` có điền LARK_APP_ID/SECRET chưa TRƯỚC KHI nghi token expired.

**Hạ tầng file**:

- **`.env`**: Folder IDs + OAuth tokens (local only, không commit)
- **`configs/`**: Scripts & helpers (env_loader.py, setup-oauth.py, lark-upload.py, lark_bitable.py, tc_template.py, sitemap_helper.py)
- **`scripts/`**: Setup automation (setup.sh, setup.ps1)

### Đích upload (set trong `.env`)

| Biến | Mục đích | Ưu tiên |
|------|----------|---------|
| `LARK_DRIVE_FOLDER_ID` | Folder ID trên Lark Drive | **1st** (ưu tiên cao nhất) |
| `GOOGLE_DRIVE_FOLDER_ID` | Folder ID trên Google Drive | **2nd** (fallback nếu Lark fail hoặc không set) |
| `USER_ROLE` | Vai trò người dùng (junior/mid/senior/lead) | Dùng cho SP estimation, mặc định: `senior` |
| `DEFAULT_SPRINT` | Sprint mặc định (vd `1-2026/4`) | `/log-bug` dùng nếu user không cung cấp, tự cập nhật khi user gửi mới |
| `DEFAULT_VERSION` | Version mặc định (vd `STG 1.0.9 (2)`) | `/log-bug` dùng nếu user không cung cấp, tự cập nhật khi user gửi mới |
| `TEST_ACCOUNT` | Account test (vd `0923267268 - 123456`) | `/log-bug` tự gắn vào mô tả bug nếu user không cung cấp |
| `CHECK_DUPLICATE_BUG` | Bật/tắt check bug trùng trước khi tạo bug (`true`/`false`) | `/log-bug`, `/check-duplicate-bug` |
| `LARK_WIKI_PRIORITY_KEYWORDS` | Comma-separated keywords để boost ranking khi search wiki (mặc định: `Sổ Bán Hàng,SoBanHang,SBH,Shinhan`) | `/search-doc` |

- Cả 2 đều null => skip upload, chỉ trả file `.xlsx` local
- Lark fail => tự động fallback sang Google
- Chi tiết: xem `.claude/rules/output-format.md` section "Upload Priority"

### Lark Bitable Boards (set trong `.env`, hoặc dùng `/update-board`)

| Biến | Mục đích | Commands |
|------|----------|----------|
| `LARK_BUG_BASE_NAME` | Tên bug base (bitable title) để hiển thị/đối chiếu config | `/update-board`, `/log-bug` |
| `LARK_BUG_BASE_ID` + `LARK_BUG_TABLE_ID` | Bug tracking board | `/log-bug`, `/triage`, `/fix`, `/health` |
| `LARK_BUG_VIEW_ID` + `LARK_BUG_WIKI_TOKEN` | View + wiki token cho URL | `/log-bug`, `/explain-bug` |
| `LARK_TASK_BASE_ID` + `LARK_TASK_TABLE_ID` | Task/Sprint board | `/sla`, `/release-check`, `/health` |
| `LARK_TEST_BASE_ID` + `LARK_TEST_TABLE_ID` | Test execution board (tùy chọn) | `/release-check`, `/health` |
| `LARK_DOMAIN` | Domain Lark Suite | Tất cả commands |

- Cách nhanh nhất: `/update-board tracking bug: <lark_url>` => tự parse + resolve + lưu vào `.env` (bao gồm `LARK_BUG_BASE_NAME`, `LARK_BUG_BASE_ID`, `LARK_BUG_TABLE_ID`, `LARK_BUG_VIEW_ID`, `LARK_BUG_WIKI_TOKEN`)
- Hoặc điền thủ công: lấy IDs từ URL `https://<domain>/wiki/<WIKI_TOKEN>?table=<TABLE_ID>&view=<VIEW_ID>`
- Tùy chọn override field names: `LARK_BUG_FIELD_TITLE`, `LARK_BUG_FIELD_STATUS`, ...
- Chi tiết: xem `.claude/docs/lark-integration.md` section "Lark Bitable Integration"
- Re-auth sau khi thêm scopes: `rm configs/lark-oauth-token.json` rồi chạy upload bất kỳ
- **Record URL**: Dùng `get_lark_record_url('bug', record_id)` từ `configs/env_loader.py` để xây URL động

### Multi-Board Setup (QUAN TRỌNG)

Project theo dõi nhiều bug board (mỗi app/dự án 1 board). Registry các board: **`.claude/boards.md`** (alias dễ nhớ + IDs đầy đủ).

- `.env` chỉ trỏ tới **1 board active** tại 1 thời điểm.
- `/log-bug` mỗi đầu ngày sẽ confirm với user xem có đang trỏ đúng board không (chi tiết: xem `.claude/commands/log-bug.md` mục "Multi-board confirmation"). Tracking date qua `.claude/.board-state.json` (gitignored, machine-local).
- Đổi board active: chạy `/update-board tracking bug: <URL>` (hoặc edit `.env` thủ công).

### URL Board thực tế

> **Source of truth là `.env`** (local, gitignored). Danh sách board của team xem trong `.claude/boards.md` (local, gitignored). File public chỉ có template `.claude/boards.example.md`.

- **Link trực tiếp đến bug record**: Dùng `get_lark_record_url('bug', '<record_id>')` hoặc thủ công: `https://<domain>/wiki/<wiki_token>?table=<table_id>&view=<view_id>&record=<record_id>`
- **Lưu ý API**: Khi gọi Lark Bitable search/get API, chỉ truyền `app_token` (base_id) + `table_id`. **KHÔNG truyền `view_id`** vào API search/get - sẽ gây lỗi `WrongViewId`. View_id chỉ dùng để build record URL hiển thị cho user.
- **Specs/PRD documents**: Lark Wiki format — token nằm trong URL `https://<domain>.larksuite.com/wiki/<wiki_token>`
- **Domain**: Cấu hình qua `LARK_DOMAIN` trong `.env`

### Bug Board Cache (`configs/lark_bug_board_cache.json`)

- Chứa cached options cho: **Dev PIC** (25 members), **Sprint** (18), **Platform** (9), **Tính năng** (170+), **Type** (5), **Priority** (4), **Status** (14), **Version** (301)
- `/log-bug` dùng cache để tra cứu nhanh Dev PIC ID, tính năng, version... thay vì gọi API mỗi lần
- CLI: `python3 configs/lark_bug_cache.py find-dev "Phuong"` => trả về open_id
- Khi board có thêm options mới => fetch API rồi update cache: `python3 configs/lark_bug_cache.py add <field> <id> <name>`

### `/log-bug` - Quy tắc tạo bug

- **Đủ thông tin** (Dev PIC + Sprint + Version + Tính năng) => **tạo luôn**, không cần confirm
- **Check duplicate**: Nếu `CHECK_DUPLICATE_BUG=true` => `/log-bug` gọi `/check-duplicate-bug` trước khi create
- **Sprint/Version fallback**: Không có trong prompt => đọc `DEFAULT_SPRINT` / `DEFAULT_VERSION` từ `.env`. Cả 2 đều thiếu => hỏi user
- **Sprint/Version update**: User cung cấp Sprint/Version mới => cập nhật lại `DEFAULT_SPRINT` / `DEFAULT_VERSION` trong `.env` cho lần sau
- **Thiếu** Dev PIC hoặc Tính năng (không có default) => hiển thị draft, **hỏi user bổ sung** rồi mới tạo
- **Ảnh/Video**: PHẢI đọc nội dung để hiểu Steps, vấn đề, mong muốn. Nếu user có mô tả sơ => bám sát mô tả đó, dùng ảnh/video bổ sung chi tiết
- Các trường khác (Name, Platform, Type, Priority, Steps, Expected) => agent tự điền từ context + phân tích ảnh/video
- **Attachment**: gửi path file trong prompt HOẶC dùng nút `+` (attach) trong IDE extension => đều được xử lý tự động

## Thư mục output

- `/analyze`, `/cook`, `/fix`: `results/<feature_name>/`
- `/plan-tc`: `plans/<feature_name>/`
- `/sla`, `/health`, `/release-check`, `/triage`, `/risk`: `results/<context_name>/`
- Tên: viết thường, dùng dấu gạch ngang (vd `invoice-export`), tự tạo nếu chưa có

## Chất lượng output

- Tất cả tài liệu generated: **Created by: QA Ops Suite**
- Test case phải rõ ràng, có thể reproduce được, và độc lập
- Bao phủ positive, negative, boundary, và edge cases
- File local: Hệ thống đọc được `.md`, `.txt`, `.pdf`, `.docx`, `.xlsx`, `.csv`, `.json`, `.xml`, `.yaml`, `.html`, code files, images, `.ipynb`, ...
