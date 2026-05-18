Hiển thị danh sách các command của QA Ops Suite với mô tả ngắn gọn. Có 3 chế độ: rỗng (in bảng đầy đủ), `<tên command>` (in chi tiết 1 command), `--config` (in cấu hình `.env` hiện tại).

## Role

Bạn là trợ lý tra cứu nhanh. KHÔNG load bất kỳ file nào trong `.claude/rules/`, KHÔNG spawn agent. Chỉ đọc từ thư mục `.claude/commands/` và (khi cần) file `.env`.

## Task

Nhận input `$ARGUMENTS`:

### Case 1: `$ARGUMENTS` rỗng => in bảng đầy đủ

In đúng output bên dưới (copy nguyên). KHÔNG thêm giới thiệu dài dòng, KHÔNG hỏi thêm.

```
# QA Ops Suite - Commands

Gõ `/help <tên command>` để xem chi tiết (Role, when to use, examples).
Gõ `/help --config` để xem cấu hình `.env` hiện tại.

## QA / QC

| Command                | Tác dụng |
|------------------------|----------|
| `/analyze`             | Phân tích requirement docs (PRD, specs, wiki, Figma) => input cho `/plan-tc` |
| `/plan-tc`             | Tạo test plan chi tiết với phase splitting + Story Point estimation |
| `/cook`                | Sinh test case / checklist từ specs, push Google Sheets hoặc Lark |
| `/fix`                 | Update TC trên Drive, phân tích bug, sinh regression TC |
| `/log-bug`             | Log bug lên Lark Bitable, đính kèm ảnh/video (path hoặc nút `+`) |
| `/check-duplicate-bug` | Check trùng bug trên Lark Bitable trước khi log mới |
| `/explain-bug`         | Giải thích bug từ mô tả lủng củng (Bug ID / paste text / Lark link) |
| `/search-doc`          | Search Lark Wiki, tổng hợp câu trả lời từ top 1-5 tài liệu kèm citation |
| `/ask`                 | Q&A về QA/QC/Testing, tư vấn chiến lược test theo context |
| `/est-sp`              | Ước lượng Story Point theo role (junior/mid/senior/lead) |

## Product Ops

| Command          | Tác dụng |
|------------------|----------|
| `/sla`           | Đánh giá SLA compliance từ ticket/bug, báo cáo sprint/tháng/quý |
| `/health`        | Product Health Scorecard (quality, customer, testing, velocity) |
| `/release-check` | Release Readiness: GO / CONDITIONAL GO / NO-GO theo gates |
| `/triage`        | Phân loại severity/priority, đề xuất thứ tự xử lý (RICE scoring) |
| `/risk`          | Risk Assessment cho feature/release, Risk Matrix + mitigation |

## Config

| Command         | Tác dụng |
|-----------------|----------|
| `/update-board` | Parse URL Lark Bitable => update `.env` (bug/task/test board) |
| `/help`         | In bảng này. `/help <cmd>` xem chi tiết, `/help --config` xem cấu hình |

---

Workflow đề xuất: `/analyze` => `/plan-tc` => `/cook` => (test) => `/log-bug` + `/fix`
Tài liệu chi tiết: `CLAUDE.md`, `README.md`, `.codex/command-map.md`
```

### Case 2: `$ARGUMENTS` là tên command (vd `cook`, `/cook`, `log-bug`)

1. Strip dấu `/` ở đầu => còn `cook`, `log-bug`, ...
2. Đọc file `.claude/commands/<name>.md`.
3. Nếu không tồn tại => báo: `Không có command /<name>. Gõ /help để xem danh sách.`
4. Nếu tồn tại => in:
   - Line 1 của file (description)
   - Section `## Role` (nếu có) — copy nguyên
   - Section "When to use" / "Input type" / "Example" (nếu có) — trích tối đa ~30 dòng
   - Dòng cuối: `Full docs: .claude/commands/<name>.md`

### Case 3: `$ARGUMENTS == "--config"` => in cấu hình `.env` hiện tại

Chạy (Bash tool) đúng 1 lệnh để đọc cấu hình an toàn (không lộ token):

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from configs.env_loader import load_env
import os
load_env()

def show(k, masked=False):
    v = os.environ.get(k, '') or '(chưa set)'
    if masked and v != '(chưa set)' and len(v) > 8:
        v = v[:4] + '...' + v[-4:]
    print(f'  {k:30} = {v}')

print('=== QA Ops Suite Config (from .env) ===')
print()
print('User:')
show('USER_ROLE')
print()
print('Defaults cho /log-bug:')
show('DEFAULT_SPRINT')
show('DEFAULT_VERSION')
show('TEST_ACCOUNT')
show('CHECK_DUPLICATE_BUG')
print()
print('Upload target:')
show('LARK_DRIVE_FOLDER_ID')
show('GOOGLE_DRIVE_FOLDER_ID')
print()
print('Lark Bug Board:')
show('LARK_BUG_BASE_NAME')
show('LARK_BUG_BASE_ID')
show('LARK_BUG_TABLE_ID')
show('LARK_DOMAIN')
print()
print('Secrets (masked):')
show('GOOGLE_OAUTH_REFRESH_TOKEN', masked=True)
show('LARK_APP_ID', masked=True)
show('LARK_APP_SECRET', masked=True)
"
```

Sau đó in thêm dòng hint:

```
Để đổi: edit .env trực tiếp, hoặc /update-board <url> cho Lark board.
```

## Rules

- KHÔNG đọc rules/*.md, KHÔNG load sitemap.
- KHÔNG spawn sub-agent.
- Output tiếng Việt có dấu đầy đủ (theo CLAUDE.md language rule).
- Không dài dòng — mục đích của `/help` là nhanh.
