# QA Ops Suite

[![Tiếng Việt](https://img.shields.io/badge/lang-vi-red.svg)](README-vi.md)
[![English](https://img.shields.io/badge/lang-en-blue.svg)](README.md)

**QA Ops Suite** là bộ công cụ hỗ trợ QA/QC chạy trên **Claude Code CLI** và **VS Code Extension** - tự động hoá các tác vụ QC thường ngày: tạo test case, lập test plan, phân tích yêu cầu (specs/Figma), đánh giá chất lượng test, ước lượng Story Point, và hỗ trợ quy trình Product Ops.

Test case được tạo dưới dạng file `.xlsx` local (bản sao lưu) và upload lên **Lark Drive** (tự động chuyển thành Lark Sheet chỉnh sửa được) hoặc **Google Sheets** (cấu hình ưu tiên qua `.env`).

> Hoạt động trên cả **macOS** và **Windows**. Hỗ trợ Claude Code CLI (terminal) và Claude Code Extension (VS Code).

![Ví dụ prompt /plan-tc trên VS Code Extension](example/example-plan-prompt.png)

---

## Mục Lục

- [Tính Năng Chính](#tính-năng-chính)
- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt (Từng Bước)](#cài-đặt-từng-bước)
  - [Bước 1: Clone dự án](#bước-1-clone-dự-án)
  - [Bước 2: Cài đặt Python](#bước-2-cài-đặt-python)
  - [Bước 3: Cài đặt thư viện Python](#bước-3-cài-đặt-thư-viện-python)
  - [Bước 4: Cài đặt Node.js](#bước-4-cài-đặt-nodejs-cần-cho-lark-mcp)
  - [Bước 5: Cài đặt Claude Code](#bước-5-cài-đặt-claude-code)
  - [Bước 6: Chạy OAuth](#bước-6-chạy-oauth-xác-thực-tài-khoản-google)
  - [Bước 7: Cấu hình upload](#bước-7-tuỳ-chọn-cấu-hình-upload)
  - [Bước 8: Mở Claude Code](#bước-8-mở-claude-code)
- [Kiến Trúc Google Sheets](#kiến-trúc-google-sheets)
- [Cấu Hình MCP Servers](#cấu-hình-mcp-servers)
  - [Figma MCP](#figma-mcp)
  - [Lark MCP](#lark-mcp)
- [Chi Tiết Các Lệnh](#chi-tiết-các-lệnh)
  - [QA / QC](#qa--qc)
    - [/analyze](#analyze---phân-tích-tài-liệu-yêu-cầu)
    - [/plan-tc](#plan-tc---tạo-kế-hoạch-test)
    - [/cook](#cook---tạo-test-case--checklist)
    - [/fix](#fix---cập-nhật-tc-trên-drive--phân-tích-bug)
    - [/log-bug](#log-bug---log-bug-lên-lark-bitable)
    - [/bug](#bug---log-bug-style-gọn)
    - [/update-board](#update-board---cập-nhật-cấu-hình-board)
    - [/check-duplicate-bug](#check-duplicate-bug---kiểm-tra-bug-trùng)
    - [/explain-bug](#explain-bug---giải-thích-bug)
    - [/search-doc](#search-doc---search-lark-wiki)
    - [/ask](#ask---tư-vấn-qctesting)
    - [/est-sp](#est-sp---ước-lượng-story-point)
  - [Product Ops](#product-ops)
    - [/sla](#sla---đánh-giá-sla)
    - [/health](#health---product-health-scorecard)
    - [/release-check](#release-check---đánh-giá-release-readiness)
    - [/triage](#triage---phân-loại-bugincident)
    - [/risk](#risk---đánh-giá-rủi-ro)
- [Quy Trình Làm Việc](#quy-trình-làm-việc)
- [Kiến Trúc Multi-Agent](#kiến-trúc-multi-agent)
- [Quy Tắc Quan Trọng](#quy-tắc-quan-trọng)
- [Mẹo Viết Prompt Hiệu Quả](#mẹo-viết-prompt-hiệu-quả)
- [Định Dạng Output](#định-dạng-output)
- [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
- [Kiến Trúc Mở Rộng](#kiến-trúc-mở-rộng)
- [Xử Lý Sự Cố](#xử-lý-sự-cố)
- [Ghi Chú Bảo Mật](#ghi-chú-bảo-mật)

---

## Tính Năng Chính

### QA / QC

| Lệnh | Vai trò | Output |
|------|---------|--------|
| `/analyze` | Senior QA Analyst - Phân tích tài liệu yêu cầu từ góc nhìn QC | File `.md` trong `results/` |
| `/plan-tc` | Senior QA Lead - Tạo kế hoạch test chi tiết với phases, ma trận TC, ước lượng SP | File `.md` trong `plans/` |
| `/cook` | Senior QC Engineer - Tạo test case production-ready từ plan hoặc specs | Google Sheets URL + `.xlsx` local |
| `/fix` | Senior QC Engineer - Cập nhật/thêm/xoá TC trên Drive, phân tích bug, tạo regression TC | Sheets cập nhật + `.md` report |
| `/log-bug` | Senior QC Engineer - Log bug lên Lark Bitable kèm ảnh/video đính kèm | Bug record + link trực tiếp |
| `/bug` | Senior QC Engineer - Soạn bug draft style **gọn 1 cục** (body dồn, tự động Severity/Priority, phân tích frame video) — **KHÔNG upload Lark**, xuất text vào chat để user paste tay | Bug draft trong chat |
| `/update-board` | Configuration Assistant - Cập nhật cấu hình board bug/task/test từ URL Lark Bitable | Cập nhật `.env` + trạng thái board |
| `/check-duplicate-bug` | Senior QC Engineer - Kiểm tra bug trùng tiềm năng trước khi tạo bug mới | Trả lời trực tiếp |
| `/explain-bug` | Senior QC Engineer - Giải thích bug từ mô tả lủng củng, dễ hiểu nhanh | Trả lời trực tiếp |
| `/search-doc` | Senior QA Research Assistant - Search Lark Wiki, tổng hợp câu trả lời từ top 1-5 tài liệu kèm citation | Trả lời trực tiếp |
| `/ask` | Senior QA Consultant - Hỏi đáp chuyên sâu về QC/Testing, tư vấn chiến lược | Trả lời trực tiếp |
| `/est-sp` | Senior QA Lead - Ước lượng Story Point từ góc nhìn QC với hệ số role | Trả lời trực tiếp + cập nhật plan |
| `/help` | Lookup Assistant - In danh sách command, chi tiết 1 command, hoặc cấu hình `.env` hiện tại | Trả lời trực tiếp |

### Product Ops

| Lệnh | Vai trò | Output |
|------|---------|--------|
| `/sla` | Senior Product Ops Analyst - Đánh giá SLA compliance, phân tích vi phạm, xu hướng | File `.md` + `.xlsx` |
| `/health` | Senior Product Ops Analyst - Product Health Scorecard (chất lượng, khách hàng, testing, velocity) | File `.md` scorecard |
| `/release-check` | Senior QA Lead - Đánh giá mức độ sẵn sàng release (GO / CONDITIONAL GO / NO-GO) | File `.md` report |
| `/triage` | Senior QA/PS Lead - Phân loại bug/incident với RICE scoring và phân tích impact | File `.md` + `.xlsx` |
| `/risk` | Senior QA Lead - Đánh giá rủi ro với risk matrix và kế hoạch giảm thiểu | File `.md` report |

---

## Yêu Cầu Hệ Thống

| Phần mềm | Phiên bản | Mục đích |
|----------|-----------|----------|
| **Claude Code** | Mới nhất | Công cụ chính (CLI hoặc VS Code Extension) |
| **Python** | 3.9+ | Chạy script tạo và upload Google Sheets |
| **Node.js** | 18+ | Chạy MCP servers (Lark) qua npx |
| **npx** | (đi kèm Node.js) | Khởi động MCP servers |
| **Git** | Bất kỳ | Clone repository |

---

## Cài Đặt (Từng Bước)

### Bước 1: Clone dự án

```bash
git clone <repo-url> QAOpsSuite
cd QAOpsSuite
```

### Bước 2: Cài đặt Python

**macOS:**
```bash
# Kiểm tra Python đã cài chưa
python3 --version

# Nếu chưa có, dùng Homebrew:
brew install python
```

**Windows:**
1. Tải Python từ https://www.python.org/downloads/
2. **QUAN TRỌNG**: Khi cài đặt, tích chọn **"Add Python to PATH"**
3. Kiểm tra trong PowerShell hoặc CMD:
   ```powershell
   python --version
   ```

> Trên Windows, dùng `python` thay vì `python3`. Trên macOS, dùng `python3`.

### Bước 3: Cài đặt thư viện Python

> **Cách nhanh**: Dùng script setup 1-lệnh để làm gộp bước 3-7:
>
> - macOS / Linux: `./scripts/setup.sh`
> - Windows (PowerShell): `.\scripts\setup.ps1`
>
> Script check Python/Node/ffmpeg, cài pip deps, copy `.env.example` + `.mcp.json.example`, rồi chạy Google OAuth. Nếu thích setup tay thì xem các bước bên dưới.

**macOS / Linux:**
```bash
pip3 install -r requirements.txt
```

**Windows (PowerShell hoặc CMD):**
```powershell
pip install -r requirements.txt
```

`requirements.txt` gồm: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, `openpyxl`, `requests`, `PyYAML`.

### Bước 4: Cài đặt Node.js (cần cho Lark MCP)

**macOS:**
```bash
node -v           # Kiểm tra
brew install node  # Nếu chưa có
```

**Windows:**
1. Tải Node.js LTS từ https://nodejs.org/
2. Chạy file cài đặt (npx được bao gồm tự động)
3. Kiểm tra trong PowerShell:
   ```powershell
   node -v
   npx -v
   ```

### Bước 5: Cài đặt Claude Code

**macOS:**
```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

**Windows (PowerShell với quyền Administrator):**
```powershell
npm install -g @anthropic-ai/claude-code
claude --version
```

**VS Code Extension (cả 2 nền tảng):**
1. Mở VS Code
2. Vào Extensions (`Cmd+Shift+X` trên macOS / `Ctrl+Shift+X` trên Windows)
3. Tìm kiếm **"Claude Code"** của Anthropic
4. Nhấn **Install**

### Bước 6: Chạy OAuth (xác thực tài khoản Google)

**macOS:**
```bash
python3 configs/setup-oauth.py
```

**Windows:**
```powershell
python configs/setup-oauth.py
```

Script sẽ thực hiện:
1. Mở trình duyệt => đăng nhập tài khoản Google
2. Google yêu cầu cấp quyền cho ứng dụng **AutoCase** - nhấn **Continue**

![Google OAuth - nhấn Continue để cấp quyền](example/verify-google.png)

3. Sau khi cấp quyền, terminal hiển thị tiến trình:

![Hoàn tất OAuth trong terminal](example/cmd-auth-google.png)

Script tự động:
- Lưu OAuth token tại `configs/google-oauth-token.json`
- Tạo/cập nhật file `.env` với refresh token
- Tạo thư mục Drive **"QA Ops Suite - Test Cases"** trên tài khoản của bạn (nếu chưa có)

> **Chỉ cần 1 scope**: `drive.file` - cho phép ứng dụng tạo và quản lý file do chính nó tạo ra. Không truy cập toàn bộ Drive của bạn.

### Bước 7: (Tuỳ chọn) Cấu hình upload

Thiết lập nơi upload file test case. **Lark có ưu tiên cao hơn** - nếu cả 2 được cấu hình, Lark sẽ được dùng trước (tự động chuyển sang Google nếu Lark thất bại).

**Phương án A - Lark Drive (khuyên dùng cho người dùng Lark):**
1. Mở Lark Drive, vào thư mục đích
2. Sao chép folder ID từ URL: `https://...larksuite.com/drive/folder/<FOLDER_ID>`
3. Sửa file `.env`:
   ```
   LARK_DRIVE_FOLDER_ID=<paste_folder_id>
   ```
4. Lần upload đầu tiên sẽ mở trình duyệt để xác thực Lark OAuth - chỉ cần xác thực 1 lần
5. File được **tự động chuyển đổi** theo loại:
   - `.xlsx` / `.xls` / `.csv` => **Lark Sheet** (bảng tính chỉnh sửa được)
   - `.doc` / `.docx` / `.md` / `.txt` => **Lark Doc** (tài liệu chỉnh sửa được)
   - File khác => File gốc (chỉ tải về)

**Phương án B - Google Drive:**
1. Mở Google Drive, chọn thư mục lưu test case
2. Sao chép folder ID từ URL: `https://drive.google.com/drive/folders/<FOLDER_ID>`
3. Sửa file `.env`:
   ```
   GOOGLE_DRIVE_FOLDER_ID=<paste_folder_id>
   ```

**Thứ tự ưu tiên upload**: `LARK_DRIVE_FOLDER_ID` > `GOOGLE_DRIVE_FOLDER_ID` > bỏ qua (chỉ lưu local). Nếu Lark thất bại => tự động chuyển sang Google.

**Phương án C - Cấu hình Lark Bitable boards (quản lý bug, task):**

Cấu hình Lark Bitable boards để tìm kiếm bug, log bug, đọc tasks, và phân tích SLA.

1. Mở Bitable board trên Lark, sao chép IDs từ URL: `https://<domain>.larksuite.com/base/<BASE_ID>?table=<TABLE_ID>`
2. Sửa file `.env`:
   ```
   # Bug Board (cho /bug, /log-bug, /triage, /fix, kiểm tra trùng)
   LARK_BUG_BASE_NAME=<paste_base_name>
   LARK_BUG_BASE_ID=<paste_base_id>
   LARK_BUG_TABLE_ID=<paste_table_id>
   LARK_BUG_VIEW_ID=<paste_view_id>            # dùng để build URL record
   LARK_BUG_WIKI_TOKEN=<paste_wiki_token>      # dùng để build URL record

   # Task/Sprint Board (cho /sla, /release-check, /health)
   LARK_TASK_BASE_ID=<paste_base_id>
   LARK_TASK_TABLE_ID=<paste_table_id>

   # Test Execution Board (tùy chọn, cho /release-check, /health)
   LARK_TEST_BASE_ID=<paste_base_id>
   LARK_TEST_TABLE_ID=<paste_table_id>
   ```
3. Xác thực lại để lấy scopes mới (chỉ cần 1 lần sau khi cấu hình):
   ```bash
   rm configs/lark-oauth-token.json
   python3 configs/lark-upload.py .env <your_lark_folder_id>
   ```
4. Kiểm tra: `python3 configs/lark_bitable.py status`

Chức năng kích hoạt:

| Chức năng | Mô tả | Commands |
|-----------|--------|----------|
| Tìm bug | Tìm theo mô tả, kiểm tra trùng lặp | `/triage`, `/fix` |
| Log bug | Tạo bug mới với mô tả + ảnh/video đính kèm | `/fix`, prompt trực tiếp |
| Xem trạng thái bug | Kiểm tra trạng thái bug hiện có | `/triage`, `/fix` |
| Đọc tasks | Danh sách tasks cho phân tích SLA/release | `/sla`, `/release-check`, `/health` |

**Phương án D - Cấu hình vai trò người dùng (cho ước lượng Story Point):**

Sửa file `.env`:
```
USER_ROLE=senior
```

Giá trị hợp lệ: `junior`, `mid`, `senior`, `lead` (mặc định: `senior`). Ảnh hưởng đến ước lượng Story Point trong `/plan-tc`, `/cook`, và `/est-sp`. Xem [/est-sp](#est-sp---ước-lượng-story-point) để biết chi tiết.

**Phương án E - Default cho log bug & tuning search:**

Các biến `.env` tùy chọn giúp `/bug`, `/log-bug`, `/search-doc` chạy mượt hơn:

```
DEFAULT_SPRINT=1-2026/4                  # /log-bug dùng nếu user không cung cấp Sprint; tự update khi user gửi mới
DEFAULT_VERSION=STG 1.0.9 (2)            # hành vi tương tự DEFAULT_SPRINT
TEST_ACCOUNT=0923267268 - 123456         # tự gắn vào body bug nếu user không cung cấp account
CHECK_DUPLICATE_BUG=true                 # /log-bug và /bug gọi /check-duplicate-bug trước khi tạo
LARK_WIKI_PRIORITY_KEYWORDS=Sổ Bán Hàng,SoBanHang,SBH,Shinhan   # boost score cho kết quả /search-doc
```

**Multi-board setup**: Nếu team track bug ở nhiều Lark board (mỗi app/dự án 1 board), lưu registry đầy đủ ở [.claude/boards.md](.claude/boards.md) và chỉ trỏ `.env` vào **1 board active** tại 1 thời điểm. `/log-bug` confirm board active mỗi ngày qua `.claude/.board-state.json` (gitignored). Đổi board active bằng `/update-board tracking bug: <URL>`.

### Bước 8: Mở Claude Code

**Cách 1 - Claude Code CLI (Terminal):**
```bash
cd QAOpsSuite
claude
```

**Cách 2 - VS Code Extension:**
1. Mở VS Code
2. Mở thư mục `QAOpsSuite`
3. Mở panel Claude Code (icon Claude trên sidebar, hoặc `Cmd+Shift+P` / `Ctrl+Shift+P` => "Claude Code")
4. Bắt đầu sử dụng các lệnh: `/cook`, `/plan-tc`, `/fix`...

> MCP servers đã được cấu hình sẵn trong `.mcp.json` (bao gồm trong repo) - **KHÔNG CẦN** chạy `claude mcp add` thủ công.

---

## Kiến Trúc Google Sheets

Công cụ sử dụng **Python scripts với Google APIs trực tiếp** (không phải MCP) để tạo và quản lý Google Sheets. Phương pháp này cho phép kiểm soát toàn diện việc định dạng, gộp ô, viền, dropdown, và các tính năng nâng cao.

### Sơ đồ kiến trúc

```
Claude Code tạo Python script chứa dữ liệu test case
    |
    v
Python script (openpyxl + Google API)
    |
    +-- 1. Tạo file .xlsx local (bản sao lưu trong results/)
    |
    +-- 2. Upload lên Google Sheets qua API
    |       - Tạo spreadsheet
    |       - Ghi dữ liệu (values().update)
    |       - Áp dụng định dạng (batchUpdate): gộp ô, viền,
    |         màu sắc, dropdown, đóng băng hàng, độ rộng cột...
    |       - Di chuyển vào thư mục Drive
    |
    +-- 3. Trả về Google Sheets URL
```

### Tại sao không dùng MCP Google Sheets?

| Khả năng | Python API (hiện tại) | MCP Sheets |
|----------|----------------------|------------|
| Đọc/Ghi dữ liệu | Có | Có |
| Định dạng ô (in đậm, màu, viền) | Có | Không |
| Gộp ô | Có | Không |
| Xác thực dữ liệu (dropdown) | Có | Không |
| Đóng băng hàng/cột | Có | Không |
| Điều chỉnh độ rộng cột | Có | Không |
| Bản sao lưu .xlsx local | Có | Không |

MCP Sheets chỉ hỗ trợ thao tác CRUD cơ bản. Công cụ cần kiểm soát định dạng đầy đủ (chiếm ~60% mã nguồn spreadsheet), nên Python API là lựa chọn phù hợp.

### Phạm vi OAuth

Chỉ cần **1 scope**: `drive.file`

Scope này cho phép ứng dụng:
- Tạo file Google Sheets mới
- Đọc/ghi dữ liệu trong file do ứng dụng tạo
- Áp dụng định dạng (gộp ô, viền, màu sắc, dropdown, đóng băng)
- Di chuyển file vào thư mục Drive
- Chia sẻ file (khi cần)

Ứng dụng **không thể** truy cập file mà nó không tạo - các file hiện có trên Drive của bạn vẫn an toàn.

---

## Cấu Hình MCP Servers

### File `.mcp.json` (đã bao gồm trong repo)

```json
{
  "mcpServers": {
    "figma": {
      "type": "http",
      "url": "https://mcp.figma.com/mcp"
    },
    "lark-mcp": {
      "command": "npx",
      "args": [
        "-y", "@larksuiteoapi/lark-mcp", "mcp",
        "-a", "<APP_ID>",
        "-s", "<APP_SECRET>",
        "--domain", "https://open.larksuite.com",
        "--oauth",
        "--token-mode", "auto",
        "-t", "preset.doc.default,docx.v1.documentBlock.list,..."
      ]
    }
  }
}
```

### Figma MCP

Để cho phép Claude đọc thiết kế từ Figma:

1. **Đăng nhập Figma MCP**: Lần đầu tiên, Claude sẽ yêu cầu bạn đăng nhập Figma - làm theo hướng dẫn
2. **Bật Dev Mode** trên Figma:
   - Mở file Figma => Bật **"Dev Mode"** trên thanh công cụ (hoặc phím tắt `Shift + D`)
   - Dev Mode hiển thị thông số chính xác hơn (spacing, padding, màu sắc, typography)
3. **Sao chép link node**:
   - Chọn frame/component => Nhấn chuột phải => **Copy link to selection**
   - Định dạng link: `https://www.figma.com/design/<fileKey>/<fileName>?node-id=<nodeId>`
4. **Dùng `&m=dev` trong link** để Claude đọc ở chế độ dev:
   - Ví dụ: `https://www.figma.com/design/abc123/MyApp?node-id=451-8205&m=dev`

### Lark MCP

- Tự động kết nối với Lark (Larksuite) để đọc tài liệu, sheets, và bình luận
- Lần đầu: Claude sẽ yêu cầu **xác thực tài khoản Lark** qua OAuth
- Sau khi xác thực, bạn có thể dán link Lark trực tiếp trong prompt
- **Loại tài liệu hỗ trợ**: Wiki, Docx, Doc, Sheets, Bitable, Mindnote, Slides, file đính kèm, bình luận tài liệu
- **Chế độ token**: `user_access_token` - tất cả actions dùng identity của user đã đăng nhập, đảm bảo traceability
- **Đọc link nhúng**: Link tìm thấy bên trong tài liệu Lark được tự động đọc bởi các sub-agent song song (link Lark, URL bên ngoài, và cả link Figma đều được xử lý tương ứng)
- **Tích hợp Bitable**: Đọc/tạo/cập nhật records trên Lark Bitable boards (quản lý bug, task)
- Ví dụ: `https://sobanhang.sg.larksuite.com/wiki/...`

> **Quy tắc Python-first (QUAN TRỌNG)**: Mọi thao tác đọc/ghi Lark (wiki, docx, search, Bitable CRUD, comments, media), QA Ops Suite ưu tiên [configs/lark_api.py](configs/lark_api.py) hơn là MCP server. Helper Python tự refresh token (và mở browser OAuth nếu refresh token cũng hết); MCP server không có cơ chế này nên hay fail với `99991668: user_access_token invalid or expired`. MCP chỉ là fallback khi `lark_api.py` chưa có wrapper.
>
> CLI debug: `python3 configs/lark_api.py token` (refresh shared token), `read-wiki <token>`, `list-fields <base> <table>`, `search-wiki <query>`.

---

## Chi Tiết Các Lệnh

### QA / QC

#### `/analyze` - Phân tích tài liệu yêu cầu

**Mục đích**: Phân tích tài liệu specs/PRD từ góc nhìn QC, tạo phân tích chi tiết làm đầu vào cho `/plan-tc` và `/cook`.

**Vai trò**: Senior QA Analyst

**Quy trình**:
1. Nhận link tài liệu (URL online hoặc file local)
2. Tự động đọc nội dung qua sub-agent song song:
   - **Tài liệu Lark**: Wiki, Docx, Doc, Sheet, Bitable, Mindnote, Slides, File (mọi loại đều hỗ trợ)
   - **URL web**: Bất kỳ trang web nào truy cập được
   - **File local**: Mọi định dạng văn bản, PDF, hình ảnh (multimodal), spreadsheet, notebook
3. **Đọc link nhúng song song**: Link tìm thấy trong tài liệu nguồn tự động được gửi đến sub-agent (link Lark, link Figma với theo dõi nhiều màn hình, URL bên ngoài)
4. **Tự động đọc bình luận** từ tài liệu Lark
5. Phân tích 6 phần: metadata, tóm tắt, phân tích QC, đánh giá chất lượng tài liệu, câu hỏi cho PO/Design, gợi ý kế hoạch test
6. Xuất file `.md` vào `results/<tên_tính_năng>/`

**Ví dụ prompt**:
```
/analyze https://<your-domain>.larksuite.com/wiki/<wiki_token>
```

```
/analyze Docs/purchase-order/specs.md
```

---

#### `/plan-tc` - Tạo kế hoạch test

**Mục đích**: Tạo kế hoạch test chi tiết mà bất kỳ QC nào cũng có thể sử dụng làm đầu vào cho `/cook`.

**Vai trò**: Senior QA Lead

**Bao gồm**:
- Phạm vi test và phân chia phases độc lập
- Ma trận TC (số lượng TC dự kiến, phạm vi TC_ID cho từng phase)
- Ước lượng thời gian và Story Point (có tính hệ số role)
- Phân tích ảnh hưởng (impact analysis) từ sitemap
- Tóm tắt xung đột (nếu có cả Docs và Figma)

**Ví dụ prompt**:
```
/plan-tc Test case cho module Đơn hàng, specs: https://sobanhang.sg.larksuite.com/wiki/xxx
```

```
/plan-tc Sprint 12 - Module thanh toán VNPay
Specs: Docs/payment/specs.md
Figma: https://www.figma.com/design/abc/Finan?node-id=123-456&m=dev
Platform: iOS + Android
```

---

#### `/cook` - Tạo test case / checklist

**Mục đích**: Viết test case production-ready từ specs/plan, đẩy lên Google Sheets hoặc Lark Drive.

**Vai trò**: Senior QC Engineer

**Tiêu chuẩn chất lượng**:
- Bước thực hiện chi tiết: hành động cụ thể, dữ liệu test, vị trí trên UI
- Kết quả mong đợi có giá trị test thực tế (KHÔNG phải "ứng dụng không bị crash")
- Bao phủ đầy đủ: Positive + Negative + Boundary + Edge case
- Ưu tiên: Critical > High > Medium > Low
- TC ID đặt lại theo sheet: TC_001, TC_002... (mỗi sheet bắt đầu từ TC_001)

**Ví dụ prompt**:
```
/cook Viết test case cho Đơn hàng mua
Specs: https://sobanhang.sg.larksuite.com/wiki/xxx
Figma: https://www.figma.com/design/abc/Finan?node-id=451-8205&m=dev
```

```
/cook Thực thi plan trong plans/purchase-order/test-plan.md
```

---

#### `/fix` - Cập nhật TC trên Drive và phân tích bug

**Mục đích**: Cập nhật/thêm/xoá test case hiện có trên Google Sheets, hoặc phân tích bug để tạo regression TC.

**Vai trò**: Senior QC Engineer

**3 chế độ**:

| Chế độ | Đầu vào | Hành động |
|--------|---------|-----------|
| Cập nhật TC trên Drive | URL Google Sheets + mô tả thay đổi | Chỉnh sửa trực tiếp trên Sheets qua API |
| Sửa TC từ plan | Link Google Sheets hoặc file plan | Phân tích và sửa trên Sheets |
| Phân tích bug | Mô tả báo cáo bug | Phân tích + tạo regression TC |

**Ví dụ prompt**:
```
/fix Thêm 5 test case negative vào sheet "Tạo Đơn hàng"
Link: https://docs.google.com/spreadsheets/d/xxx
```

```
/fix Người dùng không nhận được OTP trên iOS 17
Build: v2.1.0 (build 345)
Bước: Đăng ký > Nhập SĐT > Nhấn "Gửi OTP" > Không nhận được SMS
```

---

#### `/log-bug` - Log bug lên Lark Bitable

**Vai trò**: Senior QC Engineer

**Mục đích**: Log bug trực tiếp lên Lark Bitable từ prompt. Hỗ trợ đính kèm ảnh và video qua đường dẫn file.

**2 chế độ**:

| Chế độ      | Điều kiện                                              | Hành vi                                                |
|-------------|--------------------------------------------------------|--------------------------------------------------------|
| Đủ thông tin | Dev PIC + Sprint + Version + Tính năng đều có trong prompt | Tạo luôn, trả link trực tiếp đến record               |
| Thiếu thông tin | Thiếu bất kỳ trường bắt buộc nào                    | Hiển thị draft, hỏi user bổ sung, rồi mới tạo         |

**Đính kèm**: Hỗ trợ ảnh (`.png`, `.jpg`, `.gif`, `.webp`) và video (`.mp4`, `.mov`, `.avi`) - cung cấp đường dẫn file trong prompt.

> **Cách copy đường dẫn file để đính kèm**:
>
> | Hệ điều hành | Cách làm                                                          | Phím tắt                 |
> |--------------|-------------------------------------------------------------------|--------------------------|
> | **macOS**    | Chọn file trong Finder, nhấn                                     | **Cmd + Option + C**     |
> | **macOS**    | Hoặc: **Option + Chuột phải** vào file > **Copy ... as Pathname** |                          |
> | **Windows**  | **Shift + Chuột phải** vào file > **Copy as path**               |                          |
> | **Windows**  | Hoặc: Chọn file trong Explorer, nhấn                             | **Ctrl + Shift + C**     |
>
> Sau đó dán path vào prompt: `/log-bug ... attachment: <dán_path_vào_đây>`

**Ví dụ prompt**:

```
/log-bug version stg-3.2.198, Sprint 12, Bán hàng bị crash khi quét barcode.
Dev Pic: Hung, Phan Phi
attachment: /Users/me/Desktop/crash-screenshot.png
```

```
/log-bug Màn hình thanh toán hiển thị sai tổng tiền
Dev: Trung, Sprint 12, version stg-3.2.198
attachment: C:\Users\me\Videos\bug-recording.mp4
```

```
/log-bug App bị crash khi nhấn nút thanh toán với giỏ hàng trống
```
> Nếu thiếu trường bắt buộc (Dev PIC, Sprint, Version, Tính năng), QA Ops Suite sẽ hiển thị draft và hỏi bạn bổ sung trước khi tạo.

---

#### `/bug` - Log bug style gọn

**Vai trò**: Senior QC Engineer

**Mục đích**: Soạn bug draft gọn 1 cục (kế thừa format Report bug project) và **in ra chat để user copy/paste tay** vào Lark / Slack / comment. **KHÔNG gọi Lark API, KHÔNG tạo record** — dùng `/log-bug` nếu muốn push bug lên board.

**Khác biệt so với `/log-bug`**:

| Tiêu chí | `/bug` | `/log-bug` |
|----------|--------|-------------|
| Upload Lark | **Không** — chỉ output text trong chat | **Có** — tạo record trên Lark Bitable |
| Khi nào dùng | Draft nhanh để gửi tay (Slack, comment, paste) | Track bug chính thức lên board team |
| Style body | Dồn 1 cục (Steps + Actual + Expected vào 1 khối) | Tách riêng field theo template Lark chuẩn |
| Cấu trúc | Account test → Steps → Actual → Expected (không có FE/BE, Preconditions, Notes) | Preconditions, Steps, Actual, Notes, Account test |
| Headers | Không dấu `:` (`Steps to Reproduce`) | Có dấu `:` (`Steps:`) |
| Duplicate check | Không (không có record để dedup) | Có |
| Severity & Priority | Tự estimate + hiển thị ở dòng metadata header của draft | Tùy chọn |
| Hỗ trợ video | Có - extract frames để hiểu flow (KHÔNG upload video) | Có - upload video |

**Metadata tự fill trong header draft**: Name, Platform, Type, Priority, Severity, Version. User tự điền Dev PIC, Sprint, Tính năng khi paste lên board.

**Ví dụ prompt**:

```
/bug Báo cáo Kho tính tổng tồn sai, tính năng: Báo cáo, version stg-1.0.51
```

```
/bug C:/Users/me/Downloads/bug-payment.mp4
```

```
/bug [đính kèm screenshot] lỗi hiển thị số lần chỉnh sửa tên miền, version STG 1.0.9
```

> Video: bỏ vào `bug-videos/` ở root project rồi truyền full path. Video > 120s sẽ bị reject.

---

#### `/update-board` - Cập nhật cấu hình board

**Vai trò**: Configuration Assistant

**Mục đích**: Cập nhật cấu hình board bug/task/test trong `.env` từ URL Lark Bitable.

**Các biến được cập nhật**:
- `LARK_DOMAIN`
- `LARK_BUG_*` hoặc `LARK_TASK_*` hoặc `LARK_TEST_*` (tùy hint board type)
- Resolve và lưu tên bug base vào `LARK_BUG_BASE_NAME` khi phù hợp

**Ví dụ prompt**:

```text
/update-board tracking bug: https://<your-domain>.larksuite.com/wiki/<wiki_token>?table=<table_id>&view=<view_id>
```

```text
/update-board task: https://<your-domain>.larksuite.com/wiki/<wiki_token>?table=<table_id>&view=<view_id>
```

```text
/update-board
```

> Nếu không truyền loại board, command sẽ mặc định cập nhật bug board.

---

#### `/check-duplicate-bug` - Kiểm tra bug trùng

**Vai trò**: Senior QC Engineer

**Mục đích**: Kiểm tra bug trùng tiềm năng trên bug board trước khi tạo bug mới. Command này không tạo record.

**Khi nào dùng**:
- Dùng độc lập khi muốn rà duplicate nhanh.
- Được `/log-bug` gọi nội bộ khi `CHECK_DUPLICATE_BUG=true` trong `.env`.

**Ví dụ prompt**:

```
/check-duplicate-bug [Bán hàng] Không áp dụng chiết khấu khi thanh toán
```

```
/check-duplicate-bug
name: [Kho ứng dụng] Không thể thêm module ra màn hình chính
feature: Kho ứng dụng
platform: App
keywords: thêm module, màn hình chính
```

---

#### `/explain-bug` - Giải thích bug

**Vai trò**: Senior QC Engineer

**Mục đích**: Giải thích nội dung bug từ mô tả lủng củng, giúp hiểu nhanh bug reporter muốn nói gì.

**3 cách dùng**:

| Cách dùng            | Đầu vào              | Ví dụ                                                          |
|----------------------|-----------------------|-----------------------------------------------------------------|
| Bug ID (khuyên dùng) | Bug ID trên board     | `/explain-bug BId-000427` hoặc `/explain-bug 427`              |
| Paste text           | Mô tả bug thô        | `/explain-bug <paste mô tả bug>`                               |
| Lark record link     | URL đầy đủ Lark record | `/explain-bug https://...larksuite.com/wiki/...?record=recXXX` |

**Ví dụ prompt**:

```
/explain-bug BId-000427
```

```
/explain-bug user nói: "màn thanh toán bấm nhanh nhanh nút rồi tiền mất mà đơn ko tạo"
```

---

#### `/search-doc` - Search Lark Wiki

**Vai trò**: Senior QA Research Assistant

**Mục đích**: Search Lark Wiki trên **tất cả space bạn có quyền truy cập** (cả title và nội dung), rồi tổng hợp câu trả lời từ top 1-5 tài liệu liên quan nhất kèm **citation rõ ràng**. Hữu ích khi tìm quy định nội bộ, tài liệu các phòng ban, specs cross-team...

**Cách hoạt động** (multi-agent dispatcher):

1. Main agent sinh 3-5 keyword variants từ query (có/không dấu, synonym, viết tắt)
2. **Wave 1 (parallel, max 5 sub-agent)**: Mỗi sub-agent search 1 keyword trên cả `wiki_v1_node_search` (title) và `docx_builtin_search` (content)
3. Main agent dedupe + rank kết quả. Tài liệu match `LARK_WIKI_PRIORITY_KEYWORDS` (mặc định "Sổ Bán Hàng,SoBanHang,SBH,Shinhan") được boost score 1.5x
4. **Wave 2 (parallel, max 5 sub-agent)**: Đọc full content top 1-5 docx (truncate 10000 chars/doc)
5. Main agent tổng hợp Q&A, **chỉ dùng** thông tin từ tài liệu, kèm citation `[N]` khớp với bảng tham khảo

**Output**:
- Câu trả lời tổng hợp với citation `[1]`, `[2]`...
- Bảng tài liệu tham khảo (title, space, type, link)
- Bảng tài liệu phụ (sheet/bitable/slide — cần mở thủ công)
- Độ tin cậy: High / Medium / Low

**Ví dụ prompt**:

```
/search-doc quy định L8 là gì
```

```
/search-doc policy hoàn tiền S2C HKD
```

```
/search-doc flow onboarding khách Shinhan
```

```
/search-doc quy trình release của Marketing
```

> **Lưu ý**: Kết quả chỉ trả trong conversation (không lưu file). Khi 0 match hoặc query vague, command sẽ gợi ý từ khoá thay thế thay vì retry tự động.
>
> **OAuth scopes cần**: `wiki:wiki:readonly`, `docs:document.content:read`, `drive:drive.search:readonly`. Nếu 401/403: `rm configs/lark-oauth-token.json` rồi retry.

---

#### `/ask` - Tư vấn QC/Testing

**Mục đích**: Hỏi đáp chuyên sâu, tư vấn chiến lược dựa trên context thực tế của dự án.

**Vai trò**: Senior QA Consultant

**Ví dụ prompt**:
```
/ask Độ bao phủ test đã đủ cho tính năng xuất hoá đơn chưa?
```

```
/ask Review chất lượng test case trong results/purchase-order/
```

```
/ask Chiến lược test nào phù hợp cho sprint này với 3 tính năng mới và 2 bug critical?
```

---

#### `/est-sp` - Ước lượng Story Point

**Mục đích**: Ước lượng Story Point từ góc nhìn QC, điều chỉnh theo hệ số vai trò cấu hình trong `.env`.

**Vai trò**: Senior QA Lead

**Các chế độ**:

| Chế độ | Đầu vào | Hành động |
|--------|---------|-----------|
| Từ plan | Đường dẫn file plan | Đọc plan, ước lượng SP, cập nhật plan |
| Từ prompt | Mô tả tính năng + link specs/Figma | Phân tích yêu cầu, ước lượng SP |
| SP đã có | Plan đã có SP | Hiển thị SP hiện tại, hỏi có muốn tính lại không |

**Thang đo Story Point**: Fibonacci (1, 2, 3, 5, 8, 13, 21)

**Hệ số vai trò** (cấu hình qua `USER_ROLE` trong `.env`):

| Vai trò | Hệ số | Mô tả |
|---------|-------|-------|
| junior | x1.5 | Cần thêm thời gian học context, viết TC chi tiết hơn |
| mid | x1.2 | Có kinh nghiệm nhưng có thể cần hướng dẫn ở phần phức tạp |
| senior | x1.0 | Giá trị cơ sở - hiểu nhanh, viết TC hiệu quả |
| lead | x1.0 | Tương đương senior về thực thi, thêm trách nhiệm review |

**Ví dụ prompt**:
```
/est-sp plans/purchase-order/test-plan.md
```

```
/est-sp Module thanh toán VNPay
Specs: https://sobanhang.sg.larksuite.com/wiki/xxx
Figma: https://www.figma.com/design/abc/Finan?node-id=123-456&m=dev
```

**Ví dụ output**:

![Ví dụ output /est-sp](example/estimate-story-point.png)

> **Ghi chú**: `/plan-tc` và `/cook` cũng tự động bao gồm ước lượng SP trong output.

---

### Product Ops

#### `/sla` - Đánh giá SLA

**Vai trò**: Senior Product Ops Analyst

**Mục đích**: Đánh giá SLA compliance từ dữ liệu ticket/bug, tạo báo cáo SLA với phân tích percentile, theo dõi vi phạm, và so sánh xu hướng.

**Metrics**:

| Metric | Mô tả |
|--------|--------|
| SLA Compliance Rate | `(Tickets xử lý trong SLA / Tổng) x 100%` -- target >= 95% |
| MTTR (Response) | Thời gian phản hồi trung bình, theo priority |
| MTTR (Resolution) | Thời gian giải quyết trung bình, theo priority |
| SLA Breach Rate | % tickets vi phạm SLA, theo priority |
| Percentile Analysis | P50, P90, P95 cho response và resolution |

**Ví dụ**:

```
/sla Đánh giá SLA Sprint 15
Link: https://docs.google.com/spreadsheets/d/xxx
```

---

#### `/health` - Product Health Scorecard

**Vai trò**: Senior Product Ops Analyst

**Mục đích**: Tạo bảng sức khỏe sản phẩm với các nhóm metrics: chất lượng, khách hàng, testing, velocity. Mỗi metric được đánh giá Healthy / Warning / Critical.

**Nhóm metrics**:

| Nhóm | Metrics chính |
|------|---------------|
| **Chất lượng** | Bug Escape Rate (<5%), Regression Rate (<3%), Critical Bugs Open |
| **Khách hàng** | Customer-Reported Bug Ratio (<20%), Repeat Issue Rate (<5%) |
| **Testing** | Test Coverage (>80%), Execution Rate (>95%), Pass Rate (>95%) |
| **Velocity** | Bug Fix Turnaround, Release Frequency, Hotfix Rate (<10%) |

**Ví dụ**:

```
/health Tạo scorecard từ dữ liệu Sprint 15
Bugs: https://docs.google.com/spreadsheets/d/xxx
Test results: https://docs.google.com/spreadsheets/d/yyy
```

---

#### `/release-check` - Đánh giá Release Readiness

**Vai trò**: Senior QA Lead

**Mục đích**: Đánh giá mức độ sẵn sàng release dựa trên quality gates, output GO / CONDITIONAL GO / NO-GO với confidence score.

**Quality Gates**:

| Gate | Tiêu chí | Điều kiện PASS |
|------|---------|----------------|
| G1 | Test Completion | Execution rate >= 95% |
| G2 | Test Pass Rate | Pass rate >= 95% |
| G3 | Critical Bugs | 0 P1/P2 open |
| G4 | High Bugs | Tất cả P3 đã triage |
| G5 | Regression | 100% pass |
| G6 | Rollback Plan | Có tài liệu |
| G7 | Release Notes | Đã review |
| G8 | Sign-off | Đã approve |

**Ví dụ**:

```
/release-check v2.1.0
Test results: https://docs.google.com/spreadsheets/d/xxx
Known bugs: 2 P3 open (có workaround), 0 P1/P2
```

---

#### `/triage` - Phân loại Bug/Incident

**Vai trò**: Senior QA/PS Lead

**Mục đích**: Phân loại bugs theo severity, tính RICE priority score, phân tích cross-feature impact từ sitemap, đề xuất thứ tự xử lý với SLA deadline.

**RICE scoring**: `Score = (Reach x Impact x Confidence) / Effort`

**Output bao gồm**:

- Tự động phân loại severity (P1-P4)
- RICE score và xếp hạng ưu tiên
- Phân tích impact cross-feature từ sitemap
- Regression scope cho từng bug
- SLA deadline theo severity

**Ví dụ**:

```
/triage Phân loại bugs Sprint 15
Link: https://docs.google.com/spreadsheets/d/xxx
```

---

#### `/risk` - Đánh giá Rủi ro

**Vai trò**: Senior QA Lead

**Mục đích**: Đánh giá rủi ro cho feature/release từ góc nhìn QA, output risk matrix (Likelihood x Impact), chiến lược giảm thiểu, và đề xuất test strategy.

**Các chiều đánh giá**:

| Nhóm | Yếu tố đánh giá |
|------|-----------------|
| **Technical** | Độ phức tạp code, integration, data migration, công nghệ mới |
| **Process** | Specs hoàn chỉnh, timeline, team quen thuộc, dependencies |
| **Business** | User impact, revenue, compliance, data sensitivity, rollback |

**Risk levels**: Low (1-4) / Medium (5-9) / High (10-15) / Critical (16-25)

**Ví dụ**:

```
/risk Đánh giá rủi ro tích hợp VNPay
Specs: https://sobanhang.sg.larksuite.com/wiki/xxx
Timeline: 2 tuần
```

---

## Quy Trình Làm Việc

```
1. /analyze   =>  Phân tích tài liệu yêu cầu
   Đầu vào: link specs (Lark/Web/file local)
   Đầu ra: results/<tính_năng>/<prefix>-analysis.md

2. /plan-tc   =>  Tạo kế hoạch test chi tiết (bao gồm ước lượng SP)
   Đầu vào: kết quả phân tích + specs + Figma + phạm vi
   Đầu ra: plans/<tính_năng>/test-plan.md

3. /cook      =>  Viết test case từ plan (bao gồm SP trong header)
   Đầu vào: plan + specs + Figma
   Đầu ra: URL Google Sheets/Lark Drive + file .xlsx local

4. Thực thi   =>  Chạy test (thủ công)
   Cập nhật trạng thái trên Google Sheets/Lark Sheet

5. /fix       =>  Sửa TC / phân tích bug / bổ sung
   Đầu vào: link Sheets + mô tả thay đổi/báo cáo bug
   Đầu ra: Sheets đã cập nhật + báo cáo bug (.md)

6. /est-sp    =>  Ước lượng Story Point (hoặc tính lại)
   Đầu vào: đường dẫn plan hoặc mô tả tính năng
   Đầu ra: Ước lượng SP + cập nhật plan

7. /ask       =>  Hỏi bất cứ lúc nào
   Review độ bao phủ, dự đoán bug, tư vấn chiến lược
```

### Quy trình Product Ops

```
Trước Development:
  /risk           =>  Đánh giá rủi ro cho feature/release sắp tới
                      Đầu ra: Risk matrix + kế hoạch giảm thiểu + test strategy

Trước Release:
  /release-check  =>  Đánh giá release readiness (GO / CONDITIONAL GO / NO-GO)
                      Đầu vào: test results + known bugs + release scope
                      Đầu ra: Quality gates verdict + confidence score

Trong Sprint / Liên tục:
  /triage         =>  Phân loại bugs/incidents với RICE scoring
                      Đầu vào: danh sách bug (Sheets/file/paste)
                      Đầu ra: Danh sách ưu tiên + impact analysis + SLA deadline

  /sla            =>  Đánh giá SLA compliance cho kỳ báo cáo
                      Đầu vào: dữ liệu ticket (Sheets/file)
                      Đầu ra: SLA report + phân tích vi phạm + xu hướng

Cuối Sprint / Hàng tháng:
  /health         =>  Tạo Product Health Scorecard
                      Đầu vào: dữ liệu bug + test results + customer feedback
                      Đầu ra: Scorecard với metrics chất lượng/khách hàng/testing/velocity
```

---

## Kiến Trúc Multi-Agent

Công cụ sử dụng kiến trúc multi-agent để tối ưu hiệu suất. Tối đa **5 agent đồng thời**.

### Tổng quan luồng xử lý

```
+---------------- THU THẬP DỮ LIỆU (song song) ------------------+
|                                                                  |
|  Agent Docs Reader ------=> {prefix}-docs-summary.md             |
|                       ---=> {prefix}-links-tracking.md           |
|                                |                                 |
|                                v                                 |
|  Agent Link Reader #1-N --=> Đọc link Lark/URL (tối đa 5)       |
|  Agent Figma Reader #1-N -=> {prefix}-figma-summary-{N}.md      |
|                              (5 màn hình/agent)                  |
|                                                                  |
+------------- CHỜ TẤT CẢ HOÀN THÀNH --------------------------------+
                              |
                              v
+------------- PHÁT HIỆN XUNG ĐỘT (agent chính) -----------------+
|  So sánh docs-summary vs figma-summary                           |
|  Có xung đột? => Xử lý theo từng lệnh:                         |
|    /analyze: Tự động mở Agent Team tranh luận                    |
|    /plan-tc, /cook, /fix: Dừng lại hỏi người dùng chọn cách    |
|  Không xung đột? => Tiếp tục bình thường                        |
+------------------------------------------------------------------+
                              |
                              v
+------------- LẬP KẾ HOẠCH (agent chính) -------------------------+
|  Đọc tất cả summary => Phân tích => Tạo kế hoạch tổng thể       |
|  Chia thành các phase ĐỘC LẬP (mỗi phase = nhóm tính năng)     |
+------------------------------------------------------------------+
                              |
                              v
+------------- THỰC THI (song song, tối đa 5 agent) ---------------+
|  Agent Phase 1 ------=> {prefix}-phase-1.xlsx                     |
|  Agent Phase 2 ------=> {prefix}-phase-2.xlsx                     |
|  Agent Phase N ------=> {prefix}-phase-N.xlsx                     |
+------------- CHỜ TẤT CẢ HOÀN THÀNH --------------------------------+
                              |
                              v
+------------- GỘP & UPLOAD (agent chính) --------------------------+
|  Gộp tất cả xlsx => 1 workbook => lưu {prefix}-final.xlsx        |
|  Upload lên Lark Drive hoặc Google Sheets => trả 1 URL           |
+------------------------------------------------------------------+
```

### Đội xử lý xung đột (khi có cả Docs và Figma)

Khi phát hiện xung đột giữa tài liệu specs và thiết kế Figma, hệ thống sẽ triển khai đội gồm 3 vai trò:

| Vòng | Vai trò | Nhiệm vụ |
|------|---------|----------|
| Vòng 1 (song song) | **Trinh** - Senior Designer | Đánh giá từ góc nhìn thiết kế |
| Vòng 1 (song song) | **Hiếu** - Senior PO | Đánh giá từ góc nhìn nghiệp vụ |
| Vòng 2 (tuần tự) | **Châu** - Senior QA | Đọc cả 2 đánh giá => Quyết định cuối cùng |

Hành vi khác nhau theo lệnh:
- **`/analyze`**: Tự động kích hoạt đội tranh luận, hiển thị chi tiết cho người dùng đọc
- **`/plan-tc`, `/cook`, `/fix`**: Dừng lại hỏi người dùng chọn cách xử lý (theo Docs / theo Figma / chọn từng cái / mở đội tranh luận)

### Các nguyên tắc chính

| Nguyên tắc | Mô tả |
|------------|-------|
| **Phase độc lập** | Mỗi phase độc lập - không trùng lặp dữ liệu với phase khác |
| **Tối đa 5 đồng thời** | Tối đa 5 agent chạy cùng lúc |
| **Đọc link nhúng song song** | Link trong tài liệu được đọc bởi sub-agent song song |
| **Đồng bộ trước khi tiếp** | Kế hoạch chỉ bắt đầu khi TẤT CẢ agent thu thập dữ liệu hoàn thành |
| **Gộp trước khi upload** | KHÔNG đẩy từng phase riêng lẻ - chỉ upload SAU KHI gộp tất cả |
| **Bắt buộc file .xlsx cuối** | Luôn lưu file .xlsx gộp cuối cùng tại local (bản sao lưu) |
| **Sheet theo tính năng** | Mỗi tính năng/module = 1 sheet riêng trong workbook |
| **TC_ID đặt lại** | Mỗi sheet bắt đầu từ TC_001 (KHÔNG đánh số liên tục qua các sheet) |

---

## Quy Tắc Quan Trọng

| Quy tắc | Mô tả |
|---------|-------|
| **Tiếng Việt có dấu** | Output mặc định bằng tiếng Việt có dấu đầy đủ. Muốn tiếng Anh: ghi rõ `language: English` |
| **TC_ID đặt lại theo sheet** | Mỗi sheet mới bắt đầu từ TC_001 |
| **Làm sạch ký tự** | Tự động thay thế `--` => `-`, dấu ngoặc đơn/kép thông minh => dấu thẳng |
| **Header riêng mỗi sheet** | Mỗi sheet có header riêng (dòng 1-6) với công thức COUNTIF |
| **Cập nhật TC trên Drive** | Dùng `/fix` + URL Google Sheets (KHÔNG dùng file xlsx cục bộ) |
| **Bao phủ test 4 phần** | UI Display, UI Object, Data Display, Interaction & Validation |
| **Ước lượng Story Point** | Tự động tính SP trong `/plan-tc` và `/cook`, điều chỉnh theo role |

---

## Mẹo Viết Prompt Hiệu Quả

1. **Luôn đính kèm link Figma với `&m=dev`** - Claude đọc thông số trực tiếp từ thiết kế
2. **Cung cấp context đầy đủ** - Mô tả tính năng + specs + Figma = test case chất lượng cao nhất
3. **Chỉ định phạm vi** - Nếu chỉ test một phần của tính năng, nói rõ ràng
4. **Đề cập các edge case đặc biệt** - Nếu bạn biết các quy tắc nghiệp vụ đặc thù, hãy bao gồm chúng
5. **Chỉ định nền tảng** - Nếu test riêng cho iOS/Android/Web, ghi rõ trong prompt
6. **Dùng `/analyze` => `/plan-tc` => `/cook`** - Phân tích kỹ trước khi lập kế hoạch sẽ cho TC tốt hơn
7. **Nhiều loại link được hỗ trợ** - Lark wiki, Google Docs, URL web, hoặc file local
8. **Chỉ định ngôn ngữ** - Mặc định là tiếng Việt. Muốn tiếng Anh: `language: English`
9. **Cập nhật TC đã có** - Dùng `/fix` + dán link Google Sheets
10. **Xoá context khi cần** - Sau `/plan-tc`, chạy `/clear` hoặc `/compact` trước khi tiếp tục `/cook` để đảm bảo đủ context window

---

## Định Dạng Output

### Test case trên Google Sheets / Lark Sheet

Mỗi file Google Sheets / Lark Sheet bao gồm:

| Khu vực | Nội dung |
|---------|----------|
| Header (Dòng 1-6) | Link DOC, Link Figma, Người tạo, Ngày tạo, Thời gian ước lượng, Tóm tắt trạng thái (COUNTIF) |
| Story Point (Dòng 7) | Ước lượng SP (giá trị + role) |
| Tiêu đề cột (Dòng 8-9) | TC ID, Mô tả, Điều kiện tiên quyết, Các bước, Kết quả mong đợi, Trạng thái, BugID, Loại test... |
| Dòng dữ liệu | Test case nhóm theo section, có định dạng màu sắc |
| Dropdown trạng thái | Combobox: `PASSED`, `FAILED`, `NOT START`, `CANCEL` |

File `.xlsx` local được lưu trong `results/` (bản sao lưu), và upload lên **Lark Drive** (tự động chuyển thành Lark Sheet) hoặc **Google Drive** (tuỳ cấu hình `.env`) kèm URL trả về.

### Test plan / Báo cáo bug

File Markdown (`.md`) được lưu trong `plans/` hoặc `results/` tương ứng.

---

## Cấu Trúc Thư Mục

```
QAOpsSuite/
+-- CLAUDE.md                    # Cấu hình và quy tắc cho Claude Code
+-- README.md                    # Tài liệu hướng dẫn (tiếng Anh)
+-- README-vi.md                 # Tài liệu hướng dẫn (tiếng Việt)
+-- .mcp.json                    # Cấu hình MCP servers (Figma + Lark)
+-- .env.example                 # Mẫu file cấu hình
+-- .env                         # Cấu hình thực tế (KHÔNG commit vào git)
|
+-- configs/                     # Script hạ tầng và cài đặt
|   +-- tc_template.py           # Module tạo template test case (.xlsx + Google Sheets)
|   +-- env_loader.py            # Trợ giúp biến môi trường (Python runtime)
|   +-- setup-oauth.py           # Script cài đặt Google OAuth
|   +-- setup-lark-oauth.py      # Script cài đặt Lark OAuth
|   +-- lark_api.py              # Lark API wrapper Python-first (tự refresh token) - ƯU TIÊN
|   +-- lark_auth.py             # Helper OAuth + refresh token Lark
|   +-- lark-upload.py           # Upload thông minh lên Lark Drive (tự động chuyển đổi)
|   +-- lark_bitable.py          # Trợ giúp Lark Bitable (upload attachment, cấu hình board)
|   +-- lark_bug_cache.py        # Fuzzy lookup cho options bug board (Dev PIC, Sprint, ...)
|   +-- lark_bug_board_cache.json# Cache options bug board (Dev PIC, Sprint, Platform, Tính năng, Version...)
|   +-- sitemap_helper.py        # Trợ giúp đọc/ghi/làm giàu sitemap
|   +-- video_frames.py          # Extract frames từ video bug (cho /bug)
|   +-- google-oauth-token.json  # Token Google (KHÔNG commit)
|   +-- lark-oauth-token.json    # Token Lark (KHÔNG commit)
|
+-- scripts/                     # Script tiện ích
+-- docs/                        # Tài liệu specs/yêu cầu đầu vào
+-- example/                     # Ảnh chụp màn hình, ví dụ prompt, file mẫu
+-- results/                     # Output từ /cook, /fix, /analyze
+-- plans/                       # Output từ /plan-tc
|
+-- .claude/
    +-- rules/                   # Lớp 0 - Quy tắc luôn tải (chia theo chủ đề)
    |   +-- core.md              # Ngôn ngữ, ID, trạng thái, làm sạch, theo dõi thời gian
    |   +-- test-quality.md      # Chất lượng bước test, kết quả mong đợi, độ bao phủ
    |   +-- output-format.md     # Quy trình xlsx, Google Sheets, định dạng
    |   +-- orchestration.md     # Multi-agent, phases, gộp, đồng bộ
    |   +-- story-point.md       # Quy tắc ước lượng Story Point, hệ số role
    |   +-- sitemap.md           # Quy tắc đọc/làm giàu/ảnh hưởng sitemap
    |   +-- conflict-resolution.md  # Quy tắc xử lý xung đột Docs vs Figma
    |   +-- product-ops.md       # SLA, health metrics, release gates, RICE, risk matrix
    |
    +-- docs/                    # Lớp 1 - Tài liệu tham khảo theo yêu cầu
    |   +-- output-types.md      # TC vs Checklist vs Regression
    |   +-- lark-integration.md  # Hướng dẫn Lark MCP + nhận diện link + tích hợp Bitable
    |   +-- lark-scopes-reference.md  # Tham khảo Lark scopes (tenant + user)
    |   +-- figma-workflow.md    # Figma multi-agent, theo dõi
    |   +-- setup-config.md      # Troubleshoot setup / .env / .mcp.json
    |   +-- severity-priority-framework.md  # Framework chuẩn hóa Severity & Priority
    |   +-- team-kpi.md          # Hướng dẫn track KPI team QC
    |
    +-- boards.md                # Registry các board bug/task/test (multi-board setup)
    +-- .board-state.json        # State confirm board active hằng ngày (gitignored)
    |
    +-- commands/                # Định nghĩa các lệnh slash
    |   +-- analyze.md, plan-tc.md, cook.md, fix.md, ask.md, est-sp.md    (QA/QC core)
    |   +-- log-bug.md, bug.md, check-duplicate-bug.md, explain-bug.md    (Bug tracking)
    |   +-- search-doc.md, update-board.md, help.md                       (Search/Config)
    |   +-- sla.md, health.md, release-check.md, triage.md, risk.md       (Product Ops)
    |
    +-- agents/                  # Hướng dẫn cho sub-agent
    |   +-- docs-reader.md       # Đọc tài liệu (Lark/URL/local + bình luận + link)
    |   +-- figma-reader.md      # Đọc thiết kế Figma
    |   +-- link-reader.md       # Đọc link nhúng
    |   +-- wiki-searcher.md     # Search Lark Wiki (1 keyword, title + nội dung)
    |   +-- wiki-reader.md       # Đọc full content 1 doc trên Lark Wiki
    |   +-- designer-review.md   # Review góc nhìn thiết kế (Trinh)
    |   +-- po-review.md         # Review góc nhìn PO (Hiếu)
    |   +-- qa-arbitrator.md     # Quyết định cuối cùng (Châu)
    |
    +-- templates/               # Template và mã nguồn
        +-- testcase-template.md # Mã Python tạo Google Sheets
```

---

## Kiến Trúc Mở Rộng

QA Ops Suite được thiết kế không chỉ là công cụ tạo test case - mà là **nền tảng hỗ trợ toàn diện cho quy trình QA và Product Ops**.

### Tầm nhìn

```
                        QA Ops Suite
                           |
          +----------------+----------------+
          |                |                |
    Quản Lý           Product Ops       Phân Tích
    Test Case         Hỗ Trợ           & Báo Cáo
          |                |                |
    +-----+-----+   +-----+-----+   +-----+-----+
    | Tạo TC    |   | Phân tích  |   | Độ bao    |
    | Cập nhật  |   | yêu cầu   |   | phủ test  |
    | Regression|   | Xung đột   |   | Dự đoán   |
    | Review    |   | Docs/Figma |   | bug       |
    +-----------+   | Ước lượng  |   | Chất lượng|
                    | SP         |   | báo cáo   |
                    +-----------+   +-----------+
```

### Hướng phát triển

| Lĩnh vực | Khả năng hiện tại | Tiềm năng mở rộng |
|----------|-------------------|-------------------|
| **Phân tích yêu cầu** | `/analyze` đọc và phân tích specs/Figma | Tự động phát hiện khoảng trống, đề xuất câu hỏi cho PO |
| **Xử lý xung đột** | Đội 3 vai trò (Designer, PO, QA) tranh luận và quyết định | Mở rộng cho các loại xung đột khác ngoài Docs vs Figma |
| **Story Point** | Ước lượng SP từ góc nhìn QC với hệ số role | Tích hợp với công cụ quản lý dự án (Jira, Lark Bitable) |
| **Sitemap** | Tự động làm giàu sitemap sau mỗi lệnh | Bản đồ ảnh hưởng toàn dự án, gợi ý phạm vi regression |
| **Product Ops** | Hỗ trợ phân tích và lập kế hoạch | Tự động tạo báo cáo sprint, theo dõi chất lượng qua thời gian |
| **Tích hợp** | Lark Drive + Google Drive + Figma | Mở rộng thêm Jira, Slack, Bitable, CI/CD pipeline |

QA Ops Suite là một **trợ lý thông minh phát triển cùng dự án** - càng sử dụng, càng hiểu context và càng cho output chất lượng hơn thông qua việc tự động làm giàu sitemap và tích luỹ lịch sử.

---

## Xử Lý Sự Cố

### Token hết hạn

**macOS:**
```bash
python3 configs/setup-oauth.py
```

**Windows:**
```powershell
python configs/setup-oauth.py
```

Sau đó khởi động lại Claude Code.

### MCP server không hoạt động

Kiểm tra MCP servers:
```bash
claude mcp list
```

Nếu không thấy `figma` hoặc `lark-mcp`, kiểm tra:
- File `.mcp.json` tồn tại trong thư mục gốc của dự án
- Node.js và npx đã được cài: `node -v && npx -v`

### Upload Google Sheets thất bại

Công cụ sử dụng Python + Google APIs trực tiếp (không phải MCP). Kiểm tra:
- File `.env` đã được tạo (chứa `GOOGLE_OAUTH_REFRESH_TOKEN` và `GOOGLE_DRIVE_FOLDER_ID`)
- Thư viện Python đã cài: `pip3 list | grep google` (macOS) hoặc `pip list | findstr google` (Windows)
- Chạy lại OAuth nếu token hết hạn: `python3 configs/setup-oauth.py`

### Upload Lark Drive thất bại

- Kiểm tra `LARK_DRIVE_FOLDER_ID` trong file `.env`
- Lần đầu upload sẽ mở trình duyệt để xác thực - làm theo hướng dẫn
- Nếu token hết hạn, hệ thống tự động mở trình duyệt để xác thực lại
- Nếu vẫn thất bại => tự động chuyển sang Google Drive (fallback)

### Lark Bitable không hoạt động

- Kiểm tra `LARK_BUG_BASE_NAME`, `LARK_BUG_BASE_ID` và `LARK_BUG_TABLE_ID` trong file `.env`
- Xác nhận: `python3 configs/lark_bitable.py status`
- Nếu token thiếu scopes Bitable: `rm configs/lark-oauth-token.json` rồi xác thực lại qua upload bất kỳ
- Đảm bảo user có quyền truy cập board Bitable trên Lark

### Figma MCP không kết nối

- Đảm bảo bạn đã đăng nhập Figma MCP khi được yêu cầu
- Kiểm tra định dạng link Figma: `figma.com/design/<fileKey>/<fileName>?node-id=<nodeId>&m=dev`
- Nếu lỗi quyền truy cập: kiểm tra quyền xem file trên Figma

### Lark MCP không đọc được tài liệu

- Lần đầu: xác thực tài khoản Lark khi được yêu cầu
- Đảm bảo định dạng link Lark: `https://sobanhang.sg.larksuite.com/wiki/...`
- Kiểm tra quyền truy cập tài liệu trên Lark

### Claude Code không nhận diện lệnh slash

Đảm bảo bạn đang chạy Claude Code **bên trong thư mục QAOpsSuite** (nơi có `CLAUDE.md` và `.claude/commands/`).

### Vấn đề riêng trên Windows

- Nếu `python3` không được nhận, dùng `python` thay thế
- Nếu `pip3` không được nhận, dùng `pip` thay thế
- Nếu script lỗi encoding, đặt: `$env:PYTHONIOENCODING = "utf-8"` trong PowerShell
- Dùng PowerShell (không phải CMD) để tương thích tốt nhất

---

## Ghi Chú Bảo Mật

Các file sau chứa thông tin nhạy cảm - **KHÔNG commit vào git** (đã có trong `.gitignore`):

```
.env                             # Chứa refresh token và folder ID
configs/google-oauth-token.json  # Token Google OAuth (tạo bởi setup-oauth.py)
configs/lark-oauth-token.json    # Token Lark OAuth (tạo bởi lark-upload.py lần upload đầu)
```

### Phạm vi OAuth: `drive.file` (quyền tối thiểu)

Ứng dụng chỉ yêu cầu scope `drive.file`, có nghĩa là:
- **Chỉ có thể** truy cập file do chính nó tạo ra - không truy cập file hiện có của bạn
- Không có quyền truy cập rộng vào toàn bộ Google Drive hay tất cả Google Sheets
- Một scope duy nhất đã đủ cho mọi thao tác: tạo, đọc, ghi, định dạng, và sắp xếp spreadsheet

---

*Created by: QA Ops Suite*
