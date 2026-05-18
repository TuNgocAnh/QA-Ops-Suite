Cập nhật board config (bug/task/test) từ URL Lark Bitable.

## Role

You are a **configuration assistant** that updates the Lark Bitable board settings in `.env`.

## Input

$ARGUMENTS

If no input provided, display current board status and usage guide.

## Config Loading

- **Always read**: `.claude/rules/core.md`

## Processing

### Step 1: Parse input

Input format: `<board_type_hint> <lark_url>`

Detect board type from hint keywords:
- **bug** keywords: `bug`, `defect`, `lỗi`, `tracking bug`
- **task** keywords: `task`, `sprint`, `công việc`
- **test** keywords: `test`, `execution`, `kiểm thử`
- If no keyword => default to **bug**

Parse Lark URL to extract:
- `wiki_token`: from `/wiki/<token>` path
- `table_id`: from `?table=<id>` query param
- `view_id`: from `&view=<id>` query param (optional)
- `domain`: from URL hostname (e.g., `sobanhang.sg.larksuite.com`)
- `base_name`: from resolved Bitable title (Step 2)

Supported URL formats:
- `https://<domain>/wiki/<wiki_token>?table=<table_id>&view=<view_id>` (wiki-based bitable)
- `https://<domain>/base/<base_id>?table=<table_id>&view=<view_id>` (direct base URL)

### Step 2: Resolve board info (base_id + base_name)

**Dùng Python** `configs/lark_api.py` — KHÔNG dùng `mcp__lark-mcp__*`:

- If URL has `/wiki/` path:

  ```python
  from configs.lark_api import resolve_wiki_node
  node = resolve_wiki_node(wiki_token)
  base_id = node["obj_token"]       # app_token
  assert node["obj_type"] == "bitable"
  base_name = node["title"]          # for LARK_BUG_BASE_NAME
  ```

- If URL has `/base/` path: the `<base_id>` from URL is already the app_token; wiki_token = null.

  ```python
  from configs.lark_api import get_app
  app = get_app(base_id)
  base_name = app.get("name") or app.get("title")
  ```

### Step 3: Update `.env` file

Read current `.env`, update the relevant variables:

For **bug** board:
```
LARK_BUG_BASE_NAME=<base_name>
LARK_BUG_BASE_ID=<base_id>
LARK_BUG_TABLE_ID=<table_id>
LARK_BUG_VIEW_ID=<view_id>
LARK_BUG_WIKI_TOKEN=<wiki_token>
```

For **task** board:
```
LARK_TASK_BASE_ID=<base_id>
LARK_TASK_TABLE_ID=<table_id>
LARK_TASK_VIEW_ID=<view_id>
LARK_TASK_WIKI_TOKEN=<wiki_token>
```

For **test** board:
```
LARK_TEST_BASE_ID=<base_id>
LARK_TEST_TABLE_ID=<table_id>
LARK_TEST_VIEW_ID=<view_id>
LARK_TEST_WIKI_TOKEN=<wiki_token>
```

Also update `LARK_DOMAIN` if the URL domain differs from current config.

**Rules**:
- Only update the specific board type's variables, DO NOT touch other boards
- Preserve all other `.env` content (comments, other variables)
- If a variable already exists => update its value
- If a variable doesn't exist => add it in the correct section

### Step 4: Refresh board cache (optional)

After updating .env, optionally refresh the board field cache:
- Run Python `list_fields(base_id, table_id)` from `configs.lark_api` (CLI: `python3 configs/lark_api.py list-fields <base> <table>`) to verify access and get field names
- If the board is a bug board => update `configs/lark_bug_board_cache.json` if field options changed significantly

### Step 5: Display result

Print confirmation with full board info:

```
Board updated successfully!

Board type: Bug Board (or Task/Test)
Title: <bitable title from wiki node>
URL: <original URL>

Config:
  LARK_BUG_BASE_NAME = <base_name>
  LARK_BUG_BASE_ID  = <base_id>
  LARK_BUG_TABLE_ID = <table_id>
  LARK_BUG_VIEW_ID  = <view_id>
  LARK_BUG_WIKI_TOKEN = <wiki_token>
  LARK_DOMAIN       = <domain>

Record URL template:
  https://<domain>/wiki/<wiki_token>?table=<table_id>&view=<view_id>&record=<record_id>

Fields detected: <N> fields
  - <field_name> (<field_type>)
  - ...
```

## No-Input Mode (show status)

When called without arguments, display:

```
--- Board Config Status ---

Bug Board:
  Base Name:  <value or "(not set)">
  Base ID:    <value or "(not set)">
  Table ID:   <value or "(not set)">
  View ID:    <value or "(not set)">
  Wiki Token: <value or "(not set)">
  URL: <constructed URL or "(incomplete config)">

Task Board:
  Base ID:    <value or "(not set)">
  ...

Test Board:
  Base ID:    <value or "(not set)">
  ...

--- Usage ---
  /update-board tracking bug: <lark_url>
  /update-board task: <lark_url>
  /update-board test: <lark_url>
```

### Step 6: Ask about Test Account (if not set)

After board update completes, check `.env` for `TEST_ACCOUNT`:
- If `TEST_ACCOUNT` is **not set or empty** => ask user:
  ```
  Bạn có muốn lưu account test không? (dùng cho /log-bug, tự động gắn vào mô tả bug)
  Ví dụ: 0923267268 - 123456
  ```
- If user provides => add `TEST_ACCOUNT=<value>` to `.env`
- If user declines => skip, do not ask again in this session

## Rules

- Vietnamese content MUST have proper diacritics
- CRITICAL: All Vietnamese text MUST have diacritics. Write 'Đăng nhập' NOT 'Dang nhap'. Write 'Mật khẩu' NOT 'Mat khau'. Output without diacritics is WRONG and must be fixed.
- Always verify the board is accessible (wiki_v2_space_getNode or field_list succeeds) before saving
- If access fails => show error, DO NOT update .env
- After update, remind user that commands using this board will now point to the new board

## Examples

### Example 1: Update bug board

```
User: /update-board tracking bug: https://<your-domain>.larksuite.com/wiki/<wiki_token>?table=<table_id>&view=<view_id>

=> Parse: wiki_token=<wiki_token>, table_id=<table_id>, view_id=<view_id>
=> Resolve wiki: obj_token=<base_id>, title="<base_name>"
=> Set bug base name: LARK_BUG_BASE_NAME="<base_name>"
=> Update .env
=> Display result
```

### Example 2: Update task board

```
User: /update-board task: https://<your-domain>.larksuite.com/wiki/<wiki_token>?table=<table_id>&view=<view_id>

=> Parse: wiki_token=<wiki_token>, table_id=<table_id>, view_id=<view_id>
=> Resolve wiki => get base_id
=> Update LARK_TASK_* in .env
=> Display result
```

### Example 3: No arguments

```
User: /update-board

=> Display current board config status + usage guide
```
