# Output Format Rules

Rules về định dạng output, xlsx, Google Sheets, time estimation.
**Đọc khi**: `/cook`, `/fix`

---

## 1. Output Workflow

- **Test cases / Checklist**: **MANDATORY** to create local `.xlsx` file first, then upload to Drive (Lark or Google)
- **Workflow**:
  1. Create `.xlsx` file in `results/<feature_name>/` (or corresponding output folder)
  2. Upload to Drive theo **Upload Priority** (see below)
  3. Return both the local file path and Drive URL to user
- **Reason**: The local `.xlsx` file serves as a hard backup - if Drive upload fails, the local copy is still available
- `.md` files are only used for: test plans, bug analysis reports, descriptive documents
- Template code: see `.claude/templates/testcase-template.md`
- **MANDATORY IMPORT**: All create_*.py scripts MUST `import` from `configs/tc_template.py`:
  ```python
  from configs.tc_template import (
      save_xlsx_local, create_tc_spreadsheet, create_multi_sheet_tc_spreadsheet,
      sanitize_text, sanitize_tc, TOTAL_COLS, FONT_NAME, TIME_EST_FORMULA
  )
  ```
  **BANNED**: Copying/redefining `TIME_EST_FORMULA`, `sanitize_text`, `sanitize_tc`, or any template function inline in create_*.py scripts. This causes Vietnamese diacritics loss (e.g., "phút" => "phut").
- **MANDATORY FINAL FILE**: When there are multi-phase outputs (phase-1.xlsx, phase-2.xlsx...), after merging you **MUST** save a `<prefix>-final.xlsx` file containing all sheets

### Upload Priority (IMPORTANT)

Upload target is determined by `.env` config, checked in order:

```
1. LARK_DRIVE_FOLDER_ID != null => Import to Lark Drive as editable Lark Sheet (via configs/lark-upload.py)
   - Script auto-detects file type: .xlsx/.xls/.csv => Lark Sheet, .doc/.docx/.md/.txt => Lark Doc, others => raw file
   - Import flow: /medias/upload_all => /import_tasks => poll result => editable Sheet/Doc URL
   - Success => return editable Lark Sheet URL, DONE
   - Fail (token expired) => auto re-auth (browser opens) => retry
   - Fail (other error) => fall through to step 2

2. GOOGLE_DRIVE_FOLDER_ID != null => Upload to Google Sheets (via Google API Python)
   - Success => return Google Sheets URL, DONE
   - Fail => report error, confirm local .xlsx is OK

3. Both null => skip upload, return local .xlsx path only
```

**Key rules**:
- Lark upload: `python3 configs/lark-upload.py <file_path> <folder_token>` (auto-detect file type, auto re-auth)
  - xlsx/xls/csv => Lark Sheet (editable spreadsheet)
  - doc/docx/md/txt => Lark Doc (editable document)
  - other files => raw file (download only)
  - Add `--raw` flag to force raw upload (no conversion)
- Google upload: `create_tc_spreadsheet()` / `create_multi_sheet_tc_spreadsheet()` from template
- Nếu Lark upload fail => **tiếp tục thử Google** (không dừng lại)
- Nếu cả 2 fail => vẫn confirm local file OK, báo lỗi cả 2
- Read folder IDs via `configs/env_loader.py`: `get_lark_drive_folder_id()`, `get_drive_folder_id()`

## 2. Time Estimation

- **Required** to add "Time Est (1 round):" in header Row 6 (columns B-C)
- Format: `~Xh (Y TCs x avg Z min/TC)`
- Formula:
  - Simple (UI check, display, toggle): **2 min/TC**
  - Medium (form input, validation, CRUD): **3 min/TC**
  - Complex (API integration, cross-platform, multi-step flow): **4-5 min/TC**
  - Mixed => default **3 min/TC**
  - Add buffer of **~20%** for setup, navigation, logging bugs
- Count exact number of actual TCs (do not count section header rows)

---

## 3. Google Sheets Formatting

- **Data row height**: DO NOT fix to a specific pixel value. Let it auto-resize to fit the data
- **Wrap Text**: Enable for ALL data columns (A-P), not just B-F
- **Status values**: Always center-aligned (center + middle)

## 4. Header Summary Formulas & Multi-Sheet Header

### Header per Sheet (MANDATORY)
- Each sheet in the workbook **MUST** have its own header (Rows 1-6)
- COUNTIF formulas reference data within **that same sheet**, DO NOT reference other sheets
- Each sheet has its own Time Est, Create Date, and link

### COUNTIF Formulas
- Summary cells (E1:E4) use **COUNTIF formulas** for automatic counting, DO NOT use static values
- Formulas (on Google Sheets):
  - E1 (Passed): `=COUNTIF(G10:G;D1)`
  - E2 (Failed): `=COUNTIF(G10:G;D2)`
  - E3 (Not start): `=COUNTIF(G10:G;D3)`
  - E4 (Cancel): `=COUNTIF(G10:G;D4)`
  - E5 (Testcases): `=SUM(E1:E4)`
- **valueInputOption** must be `USER_ENTERED` so Google Sheets evaluates formulas

### Multi-Sheet vs Single-Sheet
- **Prefer merging into 1 sheet** when phases/sections belong to the same feature => TC_ID sequential, split by section header rows
- **Only create separate sheets** when there are clearly independent modules/tasks => each sheet = 1 module, TC_ID reset per sheet, separate header
- Use `create_multi_sheet_tc_spreadsheet()` for both cases

## 5. Google Sheets Config

- **Drive Folder**: Automatically created if not present, or set `GOOGLE_DRIVE_FOLDER_ID` in `.env`
- **OAuth token**: `configs/google-oauth-token.json` (created by `python3 configs/setup-oauth.py`)
- **OAuth client**: Pre-configured in repo (defaults in `configs/env_loader.py`)
- **Workflow**:
  1. Prepare `data_rows` (list of dicts)
  2. Call `create_tc_spreadsheet()` from `.claude/templates/testcase-template.md` (pass `output_dir`)
  3. Automatically creates local `.xlsx` file => uploads to Google Sheets => formats + borders + moves to shared folder
  4. Returns `(spreadsheet_id, url, local_filepath)` to user
  5. If upload fails => the local `.xlsx` file in `results/<feature_name>/` is still available

---

## 6. /fix Workflow - Update Existing TCs on Drive

### User provides:
- **Google Sheets link** (URL of spreadsheet already on Drive) - this is the primary input
- Description of changes: add TCs, edit TCs, delete TCs, update steps/expected...
- Latest specs/Figma link (if requirements changed)

### DO NOT use phase xlsx files or local files
- Phase files (`{prefix}-phase-X.xlsx`) are temporary files during creation
- Local `.xlsx` files are backups only
- When updating => always work with **Google Sheets URL** (the merged final file)

### Workflow for updating TCs on Drive
1. User provides Google Sheets URL + change description
2. Read current sheet via Google Sheets API
3. Analyze and propose changes (present to user for confirmation FIRST)
4. Execute:
   - **Add TCs**: Append new rows, TC_ID continues from last TC in that sheet
   - **Edit TCs**: Update cells directly on Google Sheets
   - **Delete TCs**: Delete rows + re-number TC_IDs to be sequential
5. Update header: Time Est, COUNTIF range (if TC count changed)
6. Return updated URL

### Important notes
- **DO NOT** create new file when you only need to update existing one
- **DO NOT** delete and recreate entire sheet
- Keep existing format, style, data validation intact
- If user already tested and has status (PASSED/FAILED) => keep that status
