# Bug Boards Registry (EXAMPLE)

> File này là **template public**. Khi `scripts/setup.*` chạy lần đầu sẽ copy `boards.example.md` => `boards.md` (file thật, gitignored).
>
> Sau đó dùng `/update-board tracking bug: <lark_url>` để tự resolve IDs từ Lark API, hoặc điền thủ công theo format bên dưới.

Team QA thường theo dõi nhiều dự án trên các board Lark Bitable khác nhau. Mỗi lần log bug **chỉ ghi vào 1 board duy nhất** (active) — board còn lại chỉ giữ thông tin để tham chiếu / swap khi cần.

## 1. Active board (đang được `.env` trỏ tới)

Đọc trực tiếp từ `.env` các biến `LARK_BUG_BASE_NAME` / `LARK_BUG_BASE_ID` / `LARK_BUG_TABLE_ID` / `LARK_BUG_VIEW_ID` / `LARK_BUG_WIKI_TOKEN`.

## 2. Boards registry

### 2.1 ProjectA — Tên app / dự án

| Field | Value |
|-------|-------|
| Alias | `ProjectA` |
| Lark base name | `<base_name>` |
| Base ID | `bas<...>` |
| Table ID | `tbl<...>` |
| View ID | `vew<...>` |
| Wiki token | `<wiki_token>` |
| URL | https://<your-domain>.larksuite.com/wiki/<wiki_token>?table=<table_id>&view=<view_id> |

### 2.2 ProjectB — (template, copy block bên trên cho mỗi project)

> Thêm các board khác theo cùng format. Mỗi board 1 section.

## 3. Confirm board mỗi đầu ngày (rule cho `/log-bug`)

Vì có >= 2 board trong registry, mỗi ngày trước khi tạo bug ĐẦU TIÊN, `/log-bug` **phải confirm với user** đang muốn log lên board nào, để tránh log nhầm.

- State file: `.claude/.board-state.json` (gitignored, machine-local).
- Check & update logic: xem `.claude/commands/log-bug.md` mục "Multi-board confirmation".

## 4. Adding a new board

1. Lấy URL board từ Lark (dạng wiki hoặc base).
2. Chạy `/update-board tracking bug: <URL>` — sẽ resolve và ghi `.env` (đồng thời update `LARK_BUG_BASE_NAME`).
3. Bổ sung 1 section vào file này (registry) với alias dễ nhớ.
4. Refresh field cache: `python3 configs/lark_api.py list-fields <base> <table>` rồi cập nhật `configs/lark_bug_board_cache.json` nếu cần.
