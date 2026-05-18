# Test Case Template - Google Sheets Code Reference

## HOW TO USE (MANDATORY - Read First)

**Python module**: `configs/tc_template.py` - IMPORT this module, DO NOT copy code inline.

```python
# CORRECT - Import from module
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from configs.tc_template import (
    save_xlsx_local, create_tc_spreadsheet, create_multi_sheet_tc_spreadsheet,
    sanitize_text, sanitize_tc, TOTAL_COLS, FONT_NAME, TIME_EST_FORMULA
)

# WRONG - DO NOT copy/redefine these in your script:
# TIME_EST_FORMULA = '...'  # NEVER redefine
# TOTAL_COLS = 15            # NEVER redefine
# def sanitize_text(text):   # NEVER redefine
```

**BANNED**: Copying functions or constants from this file into create_*.py scripts.
**REASON**: Inline copying causes Vietnamese diacritics to be lost (e.g., "phút" becomes "phut").

---

## Column Structure (Row 7-8, 15 columns A-O)

| Col | Row 7 Header | Row 8 Sub-header | Width(px) |
|-----|-------------|-------------------|-----------|
| A | Testcase ID | (merged with row 7) | 80 |
| B | Testcase Description | (merged) | 250 |
| C | Pre - Condition | (merged) | 200 |
| D | Test Procedures (merged D-E) | Steps to Perform | 250 |
| E | (merged) | Steps Expected Result | 250 |
| F | Status (merged F-G) | Build STG | 100 |
| G | (merged) | Build PRD | 100 |
| H | Bug ID | (merged) | 100 |
| I | Time Est | (merged) | 80 |
| J | isAuto | (merged) | 80 |
| K | Build #1() (merged K-M) | Device #1() | 100 |
| L | (merged) | Device #2() | 100 |
| M | (merged) | Device #3() | 100 |
| N | Status #1 | (merged) | 100 |
| O | Notes | (merged) | 120 |

## Header Rows 1-7

| Row | Col A | Col B | Col C | Col D | Col E (formula) |
|-----|-------|-------|-------|-------|-----------------|
| 1 | Link DOC: | (link/empty) | | Passed (green bg) | =COUNTIF(F11:F1000,D1) |
| 2 | Link Figma: | (link/empty) | | Failed (red bg) | =COUNTIF(F11:F1000,D2) |
| 3 | Create by | QA Ops Suite | | Not start (blue bg) | =COUNTIF(F11:F1000,D3) |
| 4 | Create Date | {YYYY-MM-DD} | | Cancel (gray bg) | =COUNTIF(F11:F1000,D4) |
| 5 | | | | Testcases | =SUM(E1:E4) |
| 6 | Time Est (1 round): | (auto-formula: converts phút to giờ+phút) | | | |
| 7 | Story Point: | {SP} points ({role}) | | | |

**Note**: E1:E4 use COUNTIF to auto-count from Status column (F). E5 = total. valueInputOption must be USER_ENTERED. B6 is a formula that auto-calculates from Time Est column (I). B7 shows the Story Point estimation with the user's role (read from `.env` USER_ROLE, default: senior). SP is estimated using Fibonacci scale (1,2,3,5,8,13,21) and adjusted by role multiplier (see `.claude/rules/story-point.md`).

## Multi-Result TC (Merge B+C cells)

When 1 TC description has multiple expected results, each result occupies its own row with separate steps + expected. The Testcase Description (col B) and Pre-Condition (col C) cells are merged across those rows.

**Data structure**: Use `merge_with_prev: True` on continuation rows:
```
Row 1: id=TC_004, desc="Kiểm tra Đăng xuất", precond="...", steps="...nhấn Hủy", expected="...", time_est=2
Row 2: id=TC_005, steps="...nhấn Đồng ý", expected="...", time_est=3, merge_with_prev=True
=> B and C cells of row 1 and row 2 will be merged
```

## Styles Reference

```
Header row 7-8: bg=#CCFFFF (light cyan), bold, center, middle
Section row: bg=#ECE2FE (light purple), bold, center, merged A-O
Font: Arial (all cells, both xlsx and Google Sheets)
Data col A: bold, center, middle, wrap
Data col B: bold, wrap, top
Data col C-O: wrap, top (ALL columns auto-wrap)
Status col F-G: center, middle (values always centered)
Row height: auto-fit (DO NOT fix to specific pixel values)
Status colors: Passed=#D9F5D6, Failed=#FBBFBC, Not start=#E1EAFF, Cancel=#DEE0E3
Border: thin, color=#D0D0D0, ALL cells from row 7 to last data row
Freeze: row 8 (frozen top 8 rows)
isAuto col J: Leave blank, DO NOT auto-fill
Time Est col I: Number (minutes per case), used to calculate total in B6
```

## IMPORTANT RULES - Read BEFORE using the code

### Language (RULE #1)
- **REQUIRED**: All Vietnamese content in test cases MUST have **proper diacritics**
- Correct: "Đăng nhập thành công", "Nhập mật khẩu", "Hiển thị thông báo lỗi"
- WRONG: "Dang nhap thanh cong", "Nhap mat khau", "Hien thi thong bao loi"
- Applies to: desc, precond, steps, expected, section title - ALL fields

### Final .xlsx File (REQUIRED for multi-phase)
- When using multi-phase (phase-1.xlsx, phase-2.xlsx...), after merging you **MUST** save `<prefix>-final.xlsx`
- The final file contains ALL merged sheets - this is the complete local backup
- `create_multi_sheet_tc_spreadsheet()` automatically creates local files, but ensure the filename is final

### TC_ID Reset Per Sheet
- Each new sheet **STARTS over from TC_001** (or CL_001, RT_001 depending on type)
- Example: Total 85 TCs, Sheet 1 has 50 TCs (TC_001-TC_050), Sheet 2 has 35 TCs (TC_001-TC_035)
- **DO NOT** number sequentially across sheets (TC_051 on sheet 2 is WRONG)

### Header Per Sheet (REQUIRED)
- Each sheet in the workbook **MUST** have its own header (Rows 1-6) with COUNTIF formulas
- Formulas reference data within **that same sheet**, DO NOT reference other sheets
- Example: "Login" sheet has COUNTIF counting status within "Login" sheet, "Forgot Password" sheet has its own COUNTIF

### Sanitize Text (REQUIRED)
- Replace AI-generated incorrect characters: `—` => `-`, `→` => `=>`
- Applies to ALL TC content: desc, precond, steps, expected

### Language (REQUIRED)
- Default: **Vietnamese WITH diacritics** (Đăng nhập, Mật khẩu, Nhà cung cấp...)
- **DO NOT** write Vietnamese without diacritics (Dang nhap, Mat khau... is WRONG)
- If user wants English => prompt must specify: `language: English`

---

## Python Code - Create Google Sheets Test Case

```python
import json, os, sys
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# Load env vars
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from configs.env_loader import load_env, get_drive_folder_id, get_oauth_token_path
load_env()

# Total columns in the template (A-O = 15)
TOTAL_COLS = 15
# Default font for all cells (xlsx + Google Sheets)
FONT_NAME = 'Arial'
# Time Est formula for B6
# Auto-converts minutes to "X giờ Y phút" format
TIME_EST_FORMULA = '=IF(SUM(I10:I999)<60,SUM(I10:I999)&" phút / "&E5&" cases",IF(MOD(SUM(I10:I999),60)=0,INT(SUM(I10:I999)/60)&" giờ / "&E5&" cases",INT(SUM(I10:I999)/60)&" giờ "&MOD(SUM(I10:I999),60)&" phút / "&E5&" cases"))'


def sanitize_text(text):
    """Replace AI-generated special characters with standard ones."""
    if not isinstance(text, str):
        return text
    text = text.replace('\u2014', '-')   # em dash
    text = text.replace('\u2013', '-')   # en dash
    text = text.replace('\u2192', '=>')  # arrow
    text = text.replace('\u2018', "'")   # left single quote
    text = text.replace('\u2019', "'")   # right single quote
    text = text.replace('\u201c', '"')   # left double quote
    text = text.replace('\u201d', '"')   # right double quote
    return text


def sanitize_tc(tc):
    """Sanitize all text fields in a test case dict."""
    result = {
        'id': tc.get('id', ''),
        'desc': sanitize_text(tc.get('desc', '')),
        'precond': sanitize_text(tc.get('precond', '')),
        'steps': sanitize_text(tc.get('steps', '')),
        'expected': sanitize_text(tc.get('expected', '')),
        'time_est': tc.get('time_est', ''),
    }
    if tc.get('merge_with_prev'):
        result['merge_with_prev'] = True
    return result

def get_google_creds():
    """Load and refresh Google OAuth credentials from token file."""
    token_file = get_oauth_token_path()
    if not os.path.exists(token_file):
        raise FileNotFoundError(
            f"OAuth token not found at {token_file}\n"
            "Run: python3 configs/setup-oauth.py"
        )
    with open(token_file, 'r') as f:
        token_data = json.load(f)
    creds = Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token') or os.environ.get('GOOGLE_OAUTH_REFRESH_TOKEN', ''),
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )
    if creds.expired or not creds.valid:
        creds.refresh(Request())
        token_data['access_token'] = creds.token
        if creds.expiry:
            token_data['expiry_date'] = creds.expiry.isoformat()
        with open(token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
    return creds


def _write_tc_data_rows_xlsx(ws, tc_list, start_row, dv, bold_font, base_font, center_align, bold_top_align, top_align, thin_border):
    """
    Write TC data rows to an openpyxl worksheet, handling merge_with_prev for multi-result TCs.
    Returns: (next_row, merge_ranges) where merge_ranges is list of (start_row, end_row) for B+C merging.
    """
    current_row = start_row
    merge_ranges = []  # [(start_row, end_row)] for B+C merging
    merge_start = None

    for tc in tc_list:
        tc = sanitize_tc(tc)
        is_merge = tc.get('merge_with_prev', False)

        if is_merge:
            # Continuation row - shares desc+precond with previous
            if merge_start is None:
                merge_start = current_row - 1  # previous row starts the merge group
        else:
            # Close previous merge group if any
            if merge_start is not None:
                merge_ranges.append((merge_start, current_row - 1))
                merge_start = None

        # Write row data
        ws.cell(row=current_row, column=1, value=tc['id']).font = bold_font
        ws.cell(row=current_row, column=1).alignment = center_align
        if not is_merge:
            ws.cell(row=current_row, column=2, value=tc['desc']).font = bold_font
            ws.cell(row=current_row, column=2).alignment = bold_top_align
            ws.cell(row=current_row, column=3, value=tc.get('precond', '')).alignment = top_align
        ws.cell(row=current_row, column=4, value=tc.get('steps', '')).alignment = top_align
        ws.cell(row=current_row, column=5, value=tc.get('expected', '')).alignment = top_align
        # Status in column F (col 6)
        status_cell = ws.cell(row=current_row, column=6, value='NOT START')
        status_cell.alignment = center_align
        dv.add(status_cell)
        # Time Est in column I (col 9)
        time_est = tc.get('time_est', '')
        if time_est != '':
            ws.cell(row=current_row, column=9, value=time_est)
        # Borders + font for all 15 columns
        for c in range(1, TOTAL_COLS + 1):
            cell = ws.cell(row=current_row, column=c)
            cell.border = thin_border
            if not cell.font.bold:
                cell.font = base_font
        current_row += 1

    # Close any open merge group at the end
    if merge_start is not None:
        merge_ranges.append((merge_start, current_row - 1))

    # Apply B+C merges for multi-result TCs
    for m_start, m_end in merge_ranges:
        ws.merge_cells(f'B{m_start}:B{m_end}')
        ws.merge_cells(f'C{m_start}:C{m_end}')

    return current_row, merge_ranges


def save_xlsx_local(filepath, sheet_name, header_values, data_rows, sections, total_tc, time_est_str=None):
    """
    Save test cases as .xlsx file locally (backup before uploading to Google Sheets).

    Args:
        filepath: Full path to save .xlsx file (e.g. 'results/login/TC_Login.xlsx')
        sheet_name: Sheet tab name
        header_values: dict with keys: link_doc, link_figma, created_date
        data_rows: list of dicts with keys: id, desc, precond, steps, expected, time_est, merge_with_prev
        sections: list of tuples [(section_title, [data_rows_for_section]), ...]
                  OR single string section_title (backward compat)
        total_tc: Number of test cases
        time_est_str: Optional override for Time Est formula in B6. If None, uses auto-formula.

    Returns: filepath
    """
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    # --- Styles ---
    base_font = Font(name=FONT_NAME)
    bold_font = Font(name=FONT_NAME, bold=True)
    header_fill = PatternFill(start_color='CCFFFF', end_color='CCFFFF', fill_type='solid')
    section_fill = PatternFill(start_color='ECE2FE', end_color='ECE2FE', fill_type='solid')
    center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    top_align = Alignment(vertical='top', wrap_text=True)
    bold_top_align = Alignment(vertical='top', wrap_text=True)
    thin_border = Border(
        left=Side(style='thin', color='D0D0D0'), right=Side(style='thin', color='D0D0D0'),
        top=Side(style='thin', color='D0D0D0'), bottom=Side(style='thin', color='D0D0D0')
    )
    status_colors = {
        'Passed': 'D9F5D6', 'Failed': 'FBBFBC', 'Not start': 'E1EAFF', 'Cancel': 'DEE0E3'
    }

    # --- Header rows 1-6 ---
    created_date = header_values.get('created_date', datetime.now().strftime('%Y-%m-%d'))
    b6_value = time_est_str if time_est_str else TIME_EST_FORMULA
    header_data = [
        ['Link DOC:', header_values.get('link_doc', ''), '', 'Passed', f'=COUNTIF(F10:F{total_tc + 20},D1)'],
        ['Link Figma:', header_values.get('link_figma', ''), '', 'Failed', f'=COUNTIF(F10:F{total_tc + 20},D2)'],
        ['Create by', 'QA Ops Suite', '', 'Not start', f'=COUNTIF(F10:F{total_tc + 20},D3)'],
        ['Create Date', created_date, '', 'Cancel', f'=COUNTIF(F10:F{total_tc + 20},D4)'],
        ['', '', '', 'Testcases', '=SUM(E1:E4)'],
        ['Time Est (1 round):', b6_value],
    ]
    for r_idx, row_data in enumerate(header_data, 1):
        for c_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            if c_idx == 1:
                cell.font = bold_font
            else:
                cell.font = base_font
        # Status summary colors
        if r_idx <= 4:
            d_cell = ws.cell(row=r_idx, column=4)
            color_key = d_cell.value
            if color_key in status_colors:
                d_cell.fill = PatternFill(start_color=status_colors[color_key], end_color=status_colors[color_key], fill_type='solid')

    # Time Est bold
    ws.cell(row=6, column=1).font = bold_font
    ws.cell(row=6, column=2).font = bold_font

    # --- Column headers row 7-8 ---
    row7 = ['Testcase ID', 'Testcase Description', 'Pre - Condition', 'Test Procedures', '', 'Status', '', 'Bug ID', 'Time Est', 'isAuto', 'Build #1()', '', '', 'Status #1', 'Notes']
    row8 = ['', '', '', 'Steps to Perform', 'Steps Expected Result', 'Build STG', 'Build PRD', '', '', '', 'Device #1()', 'Device #2()', 'Device #3()', '', '']

    for c_idx, val in enumerate(row7, 1):
        cell = ws.cell(row=7, column=c_idx, value=val)
        cell.font = bold_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
    for c_idx, val in enumerate(row8, 1):
        cell = ws.cell(row=8, column=c_idx, value=val)
        cell.font = bold_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border

    # Merges for header rows
    ws.merge_cells('D7:E7')  # Test Procedures
    ws.merge_cells('F7:G7')  # Status
    ws.merge_cells('K7:M7')  # Build #1
    for col_letter in ['A', 'B', 'C', 'H', 'I', 'J', 'N', 'O']:
        ws.merge_cells(f'{col_letter}7:{col_letter}8')

    # --- Data rows ---
    current_row = 9

    # Status dropdown validation
    dv = DataValidation(type='list', formula1='"PASSED,FAILED,NOT START,CANCEL"', allow_blank=True)
    dv.showDropDown = False
    ws.add_data_validation(dv)

    if isinstance(sections, str):
        # Single section
        ws.merge_cells(f'A{current_row}:O{current_row}')
        cell = ws.cell(row=current_row, column=1, value=sanitize_text(sections))
        cell.font = bold_font
        cell.fill = section_fill
        cell.alignment = center_align
        current_row += 1
        current_row, _ = _write_tc_data_rows_xlsx(
            ws, data_rows, current_row, dv,
            bold_font, base_font, center_align, bold_top_align, top_align, thin_border
        )
    else:
        # Multi-section
        for section_title, section_data in sections:
            ws.merge_cells(f'A{current_row}:O{current_row}')
            cell = ws.cell(row=current_row, column=1, value=sanitize_text(section_title))
            cell.font = bold_font
            cell.fill = section_fill
            cell.alignment = center_align
            current_row += 1
            current_row, _ = _write_tc_data_rows_xlsx(
                ws, section_data, current_row, dv,
                bold_font, base_font, center_align, bold_top_align, top_align, thin_border
            )

    # --- Column widths ---
    col_widths = {'A': 12, 'B': 35, 'C': 28, 'D': 35, 'E': 35,
                  'F': 14, 'G': 14, 'H': 14, 'I': 11, 'J': 11,
                  'K': 14, 'L': 14, 'M': 14, 'N': 14, 'O': 16}
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width

    # Freeze top 8 rows
    ws.freeze_panes = 'A9'

    # Save
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    wb.save(filepath)
    return filepath


def create_tc_spreadsheet(title, sheet_name, header_values, data_rows, sections, total_tc, time_est_str=None, output_dir=None):
    """
    Create a formatted test case spreadsheet: save .xlsx locally first, then upload to Google Drive.

    Args:
        title: Spreadsheet title (e.g. 'TC_ForgetPassword')
        sheet_name: Sheet tab name (e.g. 'TC_ForgetPassword')
        header_values: dict with keys: link_doc, link_figma, created_date
        data_rows: list of dicts with keys: id, desc, precond, steps, expected, time_est, merge_with_prev
        sections: list of tuples [(section_title, [data_rows_for_section]), ...]
                  OR single string section_title (backward compat - uses data_rows param)
        total_tc: Number of test cases
        time_est_str: Optional override for Time Est in B6. If None, uses auto-formula.
        output_dir: Directory to save local .xlsx file (e.g. 'results/login/')
                    If None, defaults to 'results/'

    Returns: (spreadsheet_id, url, local_filepath)
    """
    # Step 1: Save .xlsx locally first (backup)
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
    local_filepath = os.path.join(output_dir, f'{title}.xlsx')
    save_xlsx_local(local_filepath, sheet_name, header_values, data_rows, sections, total_tc, time_est_str)
    print(f"[OK] Local backup saved: {local_filepath}")

    # Step 2: Upload to Google Sheets
    try:
        creds = get_google_creds()
        sheets_svc = build('sheets', 'v4', credentials=creds)
        drive_svc = build('drive', 'v3', credentials=creds)

        FOLDER_ID = get_drive_folder_id()

        # Auto-create Drive folder if not configured
        if not FOLDER_ID:
            print("[INFO] GOOGLE_DRIVE_FOLDER_ID not set. Creating new Drive folder...")
            folder_metadata = {
                'name': 'QA Ops Suite - Test Cases',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = drive_svc.files().create(body=folder_metadata, fields='id').execute()
            FOLDER_ID = folder.get('id')
            print(f"[OK] Created Drive folder: https://drive.google.com/drive/folders/{FOLDER_ID}")
            print(f"[TIP] Add to .env to reuse: GOOGLE_DRIVE_FOLDER_ID={FOLDER_ID}")

        # 1. Create spreadsheet (with default font Arial)
        sp = sheets_svc.spreadsheets().create(body={'properties': {'title': title, 'defaultFormat': {'textFormat': {'fontFamily': FONT_NAME}}}}).execute()
        sp_id = sp['spreadsheetId']

        # 2. Move to shared folder
        f = drive_svc.files().get(fileId=sp_id, fields='parents').execute()
        drive_svc.files().update(fileId=sp_id, addParents=FOLDER_ID,
            removeParents=','.join(f.get('parents', [])), fields='id').execute()

        # 3. Rename sheet
        sheets_svc.spreadsheets().batchUpdate(spreadsheetId=sp_id, body={'requests': [
            {'updateSheetProperties': {'properties': {'sheetId': 0, 'title': sheet_name}, 'fields': 'title'}}
        ]}).execute()

        # 4. Build values
        b6_value = time_est_str if time_est_str else TIME_EST_FORMULA
        values = [
            ['Link DOC:', header_values.get('link_doc', ''), '', 'Passed', '=COUNTIF(F10:F;D1)'] + ['']*(TOTAL_COLS - 5),
            ['Link Figma:', header_values.get('link_figma', ''), '', 'Failed', '=COUNTIF(F10:F;D2)'] + ['']*(TOTAL_COLS - 5),
            ['Create by', 'QA Ops Suite', '', 'Not start', '=COUNTIF(F10:F;D3)'] + ['']*(TOTAL_COLS - 5),
            ['Create Date', header_values.get('created_date', datetime.now().strftime('%Y-%m-%d')), '', 'Cancel', '=COUNTIF(F10:F;D4)'] + ['']*(TOTAL_COLS - 5),
            ['', '', '', 'Testcases', '=SUM(E1:E4)'] + ['']*(TOTAL_COLS - 5),
            ['Time Est (1 round):', b6_value] + ['']*(TOTAL_COLS - 2),
            # Row 7: Column headers
            ['Testcase ID', 'Testcase Description', 'Pre - Condition', 'Test Procedures', '', 'Status', '', 'Bug ID', 'Time Est', 'isAuto', 'Build #1()', '', '', 'Status #1', 'Notes'],
            # Row 8: Sub-headers
            ['', '', '', 'Steps to Perform', 'Steps Expected Result', 'Build STG', 'Build PRD', '', '', '', 'Device #1()', 'Device #2()', 'Device #3()', '', ''],
        ]

        # Handle sections and track merge ranges for multi-result TCs
        section_rows = []
        merge_b_c_ranges = []  # [(start_0indexed, end_0indexed)] for B+C merging

        def _append_tc_rows(tc_list):
            """Append TC rows to values, tracking merge_with_prev groups."""
            merge_start = None
            for tc in tc_list:
                tc = sanitize_tc(tc)
                is_merge = tc.get('merge_with_prev', False)
                if is_merge:
                    if merge_start is None:
                        merge_start = len(values) - 1  # previous row (0-indexed)
                else:
                    if merge_start is not None:
                        merge_b_c_ranges.append((merge_start, len(values) - 1))
                        merge_start = None

                row = [''] * TOTAL_COLS
                row[0] = tc['id']
                if not is_merge:
                    row[1] = tc['desc']
                    row[2] = tc.get('precond', '')
                row[3] = tc.get('steps', '')
                row[4] = tc.get('expected', '')
                row[5] = 'NOT START'  # Status col F
                row[8] = tc.get('time_est', '')  # Time Est col I
                values.append(row)

            if merge_start is not None:
                merge_b_c_ranges.append((merge_start, len(values) - 1))

        if isinstance(sections, str):
            values.append([sanitize_text(sections)] + ['']*(TOTAL_COLS - 1))
            section_rows.append(len(values) - 1)
            _append_tc_rows(data_rows)
        else:
            for section_title, section_data in sections:
                values.append([sanitize_text(section_title)] + ['']*(TOTAL_COLS - 1))
                section_rows.append(len(values) - 1)
                _append_tc_rows(section_data)

        last_row = len(values)
        sheets_svc.spreadsheets().values().update(
            spreadsheetId=sp_id, range=f'{sheet_name}!A1:O{last_row}',
            valueInputOption='USER_ENTERED', body={'values': values}
        ).execute()

        # 5. Formatting requests
        requests = []

        # Header rows 7-8: cyan bg + bold + center
        requests.append({'repeatCell': {
            'range': {'sheetId': 0, 'startRowIndex': 6, 'endRowIndex': 8, 'startColumnIndex': 0, 'endColumnIndex': TOTAL_COLS},
            'cell': {'userEnteredFormat': {
                'backgroundColor': {'red': 0.8, 'green': 1.0, 'blue': 1.0},
                'textFormat': {'bold': True, 'fontFamily': FONT_NAME}, 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE'
            }},
            'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
        }})

        # Section rows: purple bg + merge
        for sr in section_rows:
            requests.append({'repeatCell': {
                'range': {'sheetId': 0, 'startRowIndex': sr, 'endRowIndex': sr + 1, 'startColumnIndex': 0, 'endColumnIndex': TOTAL_COLS},
                'cell': {'userEnteredFormat': {
                    'backgroundColor': {'red': 0.925, 'green': 0.886, 'blue': 0.996},
                    'textFormat': {'bold': True, 'fontFamily': FONT_NAME}, 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE'
                }},
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
            }})
            requests.append({'mergeCells': {
                'range': {'sheetId': 0, 'startRowIndex': sr, 'endRowIndex': sr + 1, 'startColumnIndex': 0, 'endColumnIndex': TOTAL_COLS},
                'mergeType': 'MERGE_ALL'
            }})

        # Multi-result TC merges (B+C cells)
        for m_start, m_end in merge_b_c_ranges:
            # Merge B cells
            requests.append({'mergeCells': {
                'range': {'sheetId': 0, 'startRowIndex': m_start, 'endRowIndex': m_end + 1, 'startColumnIndex': 1, 'endColumnIndex': 2},
                'mergeType': 'MERGE_ALL'
            }})
            # Merge C cells
            requests.append({'mergeCells': {
                'range': {'sheetId': 0, 'startRowIndex': m_start, 'endRowIndex': m_end + 1, 'startColumnIndex': 2, 'endColumnIndex': 3},
                'mergeType': 'MERGE_ALL'
            }})

        # Data columns formatting
        # Col A: bold + center for all data area
        requests.append({'repeatCell': {
            'range': {'sheetId': 0, 'startRowIndex': 8, 'endRowIndex': last_row, 'startColumnIndex': 0, 'endColumnIndex': 1},
            'cell': {'userEnteredFormat': {
                'textFormat': {'bold': True, 'fontFamily': FONT_NAME}, 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE'
            }},
            'fields': 'userEnteredFormat(textFormat,horizontalAlignment,verticalAlignment)'
        }})

        # Col B: bold + wrap
        requests.append({'repeatCell': {
            'range': {'sheetId': 0, 'startRowIndex': 8, 'endRowIndex': last_row, 'startColumnIndex': 1, 'endColumnIndex': 2},
            'cell': {'userEnteredFormat': {
                'textFormat': {'bold': True, 'fontFamily': FONT_NAME}, 'wrapStrategy': 'WRAP', 'verticalAlignment': 'TOP'
            }},
            'fields': 'userEnteredFormat(textFormat,wrapStrategy,verticalAlignment)'
        }})

        # Col C-O: wrap (all remaining data columns)
        requests.append({'repeatCell': {
            'range': {'sheetId': 0, 'startRowIndex': 8, 'endRowIndex': last_row, 'startColumnIndex': 2, 'endColumnIndex': TOTAL_COLS},
            'cell': {'userEnteredFormat': {'wrapStrategy': 'WRAP', 'verticalAlignment': 'TOP'}},
            'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment)'
        }})

        # Status col F-G: center + middle
        requests.append({'repeatCell': {
            'range': {'sheetId': 0, 'startRowIndex': 8, 'endRowIndex': last_row, 'startColumnIndex': 5, 'endColumnIndex': 7},
            'cell': {'userEnteredFormat': {'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE', 'wrapStrategy': 'WRAP'}},
            'fields': 'userEnteredFormat(horizontalAlignment,verticalAlignment,wrapStrategy)'
        }})

        # Header area col A bold
        requests.append({'repeatCell': {
            'range': {'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 6, 'startColumnIndex': 0, 'endColumnIndex': 1},
            'cell': {'userEnteredFormat': {'textFormat': {'bold': True, 'fontFamily': FONT_NAME}}},
            'fields': 'userEnteredFormat(textFormat)'
        }})

        # Time Est row bold
        requests.append({'repeatCell': {
            'range': {'sheetId': 0, 'startRowIndex': 5, 'endRowIndex': 6, 'startColumnIndex': 0, 'endColumnIndex': 2},
            'cell': {'userEnteredFormat': {'textFormat': {'bold': True, 'fontFamily': FONT_NAME}}},
            'fields': 'userEnteredFormat(textFormat)'
        }})

        # Status summary colors (rows 1-4, col D)
        for row_idx, color in [(0, {'red':0.851,'green':0.961,'blue':0.839}),
                               (1, {'red':0.984,'green':0.749,'blue':0.737}),
                               (2, {'red':0.882,'green':0.918,'blue':1.0}),
                               (3, {'red':0.871,'green':0.878,'blue':0.890})]:
            requests.append({'repeatCell': {
                'range': {'sheetId': 0, 'startRowIndex': row_idx, 'endRowIndex': row_idx+1, 'startColumnIndex': 3, 'endColumnIndex': 4},
                'cell': {'userEnteredFormat': {'backgroundColor': color, 'horizontalAlignment': 'RIGHT'}},
                'fields': 'userEnteredFormat(backgroundColor,horizontalAlignment)'
            }})

        # Column widths
        for col_idx, px in [(0,80),(1,250),(2,200),(3,250),(4,250),(5,100),(6,100),(7,100),(8,80)]:
            requests.append({'updateDimensionProperties': {
                'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': col_idx, 'endIndex': col_idx+1},
                'properties': {'pixelSize': px}, 'fields': 'pixelSize'
            }})

        # Freeze top 8 rows
        requests.append({'updateSheetProperties': {
            'properties': {'sheetId': 0, 'gridProperties': {'frozenRowCount': 8}},
            'fields': 'gridProperties.frozenRowCount'
        }})

        # BORDERS: All cells from row 7 to last data row
        requests.append({'updateBorders': {
            'range': {'sheetId': 0, 'startRowIndex': 6, 'endRowIndex': last_row, 'startColumnIndex': 0, 'endColumnIndex': TOTAL_COLS},
            'top': {'style': 'SOLID', 'color': {'red':0.7,'green':0.7,'blue':0.7}},
            'bottom': {'style': 'SOLID', 'color': {'red':0.7,'green':0.7,'blue':0.7}},
            'left': {'style': 'SOLID', 'color': {'red':0.7,'green':0.7,'blue':0.7}},
            'right': {'style': 'SOLID', 'color': {'red':0.7,'green':0.7,'blue':0.7}},
            'innerHorizontal': {'style': 'SOLID', 'color': {'red':0.7,'green':0.7,'blue':0.7}},
            'innerVertical': {'style': 'SOLID', 'color': {'red':0.7,'green':0.7,'blue':0.7}},
        }})

        # Header merges
        # D7:E7 Test Procedures
        requests.append({'mergeCells': {'range': {'sheetId': 0, 'startRowIndex': 6, 'endRowIndex': 7, 'startColumnIndex': 3, 'endColumnIndex': 5}, 'mergeType': 'MERGE_ALL'}})
        # F7:G7 Status
        requests.append({'mergeCells': {'range': {'sheetId': 0, 'startRowIndex': 6, 'endRowIndex': 7, 'startColumnIndex': 5, 'endColumnIndex': 7}, 'mergeType': 'MERGE_ALL'}})
        # K7:M7 Build #1
        requests.append({'mergeCells': {'range': {'sheetId': 0, 'startRowIndex': 6, 'endRowIndex': 7, 'startColumnIndex': 10, 'endColumnIndex': 13}, 'mergeType': 'MERGE_ALL'}})
        # Vertical merges for single-column headers (row 7-8)
        for col in [0, 1, 2, 7, 8, 9, 13, 14]:
            requests.append({'mergeCells': {'range': {'sheetId': 0, 'startRowIndex': 6, 'endRowIndex': 8, 'startColumnIndex': col, 'endColumnIndex': col+1}, 'mergeType': 'MERGE_ALL'}})

        # 6. DATA VALIDATION: Status columns (F) - dropdown combobox
        data_start = 8  # 0-indexed, row 9
        status_validation = {
            'setDataValidation': {
                'range': {'sheetId': 0, 'startRowIndex': data_start, 'endRowIndex': last_row, 'startColumnIndex': 5, 'endColumnIndex': 6},
                'rule': {
                    'condition': {
                        'type': 'ONE_OF_LIST',
                        'values': [
                            {'userEnteredValue': 'PASSED'},
                            {'userEnteredValue': 'FAILED'},
                            {'userEnteredValue': 'NOT START'},
                            {'userEnteredValue': 'CANCEL'}
                        ]
                    },
                    'showCustomUi': True,
                    'strict': True
                }
            }
        }
        requests.append(status_validation)

        # Also apply to Build PRD (col G)
        requests.append({
            'setDataValidation': {
                'range': {'sheetId': 0, 'startRowIndex': data_start, 'endRowIndex': last_row, 'startColumnIndex': 6, 'endColumnIndex': 7},
                'rule': {
                    'condition': {
                        'type': 'ONE_OF_LIST',
                        'values': [
                            {'userEnteredValue': 'PASSED'},
                            {'userEnteredValue': 'FAILED'},
                            {'userEnteredValue': 'NOT START'},
                            {'userEnteredValue': 'CANCEL'}
                        ]
                    },
                    'showCustomUi': True,
                    'strict': True
                }
            }
        })

        sheets_svc.spreadsheets().batchUpdate(spreadsheetId=sp_id, body={'requests': requests}).execute()

        url = f"https://docs.google.com/spreadsheets/d/{sp_id}"
        print(f"[OK] Google Sheets created: {url}")
        return sp_id, url, local_filepath
    except Exception as e:
        print(f"[WARN] Google Sheets upload failed: {e}")
        print(f"[OK] Local .xlsx file is still available at: {local_filepath}")
        return None, None, local_filepath


def _write_sheet_to_ws(ws, sheet_name, header_values, sections, data_rows, total_tc, time_est_str=None):
    """
    Write header + column headers + data rows into an openpyxl worksheet.
    Used by both single-sheet and multi-sheet functions.
    TC_ID starts from 1 within each sheet (TC_001, TC_002...).
    """
    base_font = Font(name=FONT_NAME)
    bold_font = Font(name=FONT_NAME, bold=True)
    header_fill = PatternFill(start_color='CCFFFF', end_color='CCFFFF', fill_type='solid')
    section_fill = PatternFill(start_color='ECE2FE', end_color='ECE2FE', fill_type='solid')
    center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    top_align = Alignment(vertical='top', wrap_text=True)
    bold_top_align = Alignment(vertical='top', wrap_text=True)
    thin_border = Border(
        left=Side(style='thin', color='D0D0D0'), right=Side(style='thin', color='D0D0D0'),
        top=Side(style='thin', color='D0D0D0'), bottom=Side(style='thin', color='D0D0D0')
    )
    status_colors = {
        'Passed': 'D9F5D6', 'Failed': 'FBBFBC', 'Not start': 'E1EAFF', 'Cancel': 'DEE0E3'
    }

    # --- Header rows 1-6 ---
    created_date = header_values.get('created_date', datetime.now().strftime('%Y-%m-%d'))
    b6_value = time_est_str if time_est_str else TIME_EST_FORMULA
    header_data = [
        ['Link DOC:', header_values.get('link_doc', ''), '', 'Passed', f'=COUNTIF(F10:F{total_tc + 20},D1)'],
        ['Link Figma:', header_values.get('link_figma', ''), '', 'Failed', f'=COUNTIF(F10:F{total_tc + 20},D2)'],
        ['Create by', 'QA Ops Suite', '', 'Not start', f'=COUNTIF(F10:F{total_tc + 20},D3)'],
        ['Create Date', created_date, '', 'Cancel', f'=COUNTIF(F10:F{total_tc + 20},D4)'],
        ['', '', '', 'Testcases', '=SUM(E1:E4)'],
        ['Time Est (1 round):', b6_value],
    ]
    for r_idx, row_data in enumerate(header_data, 1):
        for c_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            if c_idx == 1:
                cell.font = bold_font
            else:
                cell.font = base_font
        if r_idx <= 4:
            d_cell = ws.cell(row=r_idx, column=4)
            color_key = d_cell.value
            if color_key in status_colors:
                d_cell.fill = PatternFill(start_color=status_colors[color_key], end_color=status_colors[color_key], fill_type='solid')
    ws.cell(row=6, column=1).font = bold_font
    ws.cell(row=6, column=2).font = bold_font

    # --- Column headers row 7-8 ---
    row7 = ['Testcase ID', 'Testcase Description', 'Pre - Condition', 'Test Procedures', '', 'Status', '', 'Bug ID', 'Time Est', 'isAuto', 'Build #1()', '', '', 'Status #1', 'Notes']
    row8 = ['', '', '', 'Steps to Perform', 'Steps Expected Result', 'Build STG', 'Build PRD', '', '', '', 'Device #1()', 'Device #2()', 'Device #3()', '', '']
    for c_idx, val in enumerate(row7, 1):
        cell = ws.cell(row=7, column=c_idx, value=val)
        cell.font = bold_font; cell.fill = header_fill; cell.alignment = center_align; cell.border = thin_border
    for c_idx, val in enumerate(row8, 1):
        cell = ws.cell(row=8, column=c_idx, value=val)
        cell.font = bold_font; cell.fill = header_fill; cell.alignment = center_align; cell.border = thin_border
    # Merges
    ws.merge_cells('D7:E7'); ws.merge_cells('F7:G7'); ws.merge_cells('K7:M7')
    for col_letter in ['A', 'B', 'C', 'H', 'I', 'J', 'N', 'O']:
        ws.merge_cells(f'{col_letter}7:{col_letter}8')

    # --- Data rows ---
    current_row = 9
    dv = DataValidation(type='list', formula1='"PASSED,FAILED,NOT START,CANCEL"', allow_blank=True)
    dv.showDropDown = False
    ws.add_data_validation(dv)

    if isinstance(sections, str):
        ws.merge_cells(f'A{current_row}:O{current_row}')
        cell = ws.cell(row=current_row, column=1, value=sanitize_text(sections))
        cell.font = bold_font; cell.fill = section_fill; cell.alignment = center_align
        current_row += 1
        current_row, _ = _write_tc_data_rows_xlsx(
            ws, data_rows, current_row, dv,
            bold_font, base_font, center_align, bold_top_align, top_align, thin_border
        )
    else:
        for section_title, section_data in sections:
            ws.merge_cells(f'A{current_row}:O{current_row}')
            cell = ws.cell(row=current_row, column=1, value=sanitize_text(section_title))
            cell.font = bold_font; cell.fill = section_fill; cell.alignment = center_align
            current_row += 1
            current_row, _ = _write_tc_data_rows_xlsx(
                ws, section_data, current_row, dv,
                bold_font, base_font, center_align, bold_top_align, top_align, thin_border
            )

    # Column widths
    col_widths = {'A': 12, 'B': 35, 'C': 28, 'D': 35, 'E': 35,
                  'F': 14, 'G': 14, 'H': 14, 'I': 11, 'J': 11,
                  'K': 14, 'L': 14, 'M': 14, 'N': 14, 'O': 16}
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width
    ws.freeze_panes = 'A9'
    return current_row  # last row used


def create_multi_sheet_tc_spreadsheet(title, sheets_data, output_dir=None):
    """
    Create a formatted test case spreadsheet with MULTIPLE SHEETS.
    Each sheet has its own header (rows 1-6), column headers (7-8), and data.
    TC_ID resets per sheet (starts from TC_001 in each sheet).

    Args:
        title: Spreadsheet title (e.g. 'TC_PhieuNhapHang')
        sheets_data: list of dicts, each with:
            - sheet_name: Sheet tab name (e.g. 'Nhap hang')
            - header_values: dict with keys: link_doc, link_figma, created_date
            - data_rows: list of dicts (used when sections is a string)
            - sections: list of tuples [(section_title, [data_rows]), ...] OR single string
            - total_tc: Number of TCs in this sheet
            - time_est_str: Optional override for Time Est in B6
        output_dir: Directory to save local .xlsx file

    Returns: (spreadsheet_id, url, local_filepath)
    """
    # Step 1: Save .xlsx locally (backup)
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
    local_filepath = os.path.join(output_dir, f'{title}.xlsx')
    os.makedirs(os.path.dirname(local_filepath), exist_ok=True)

    wb = Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    for sd in sheets_data:
        ws = wb.create_sheet(title=sd['sheet_name'])
        _write_sheet_to_ws(
            ws, sd['sheet_name'], sd.get('header_values', {}),
            sd['sections'], sd.get('data_rows', []),
            sd['total_tc'], sd.get('time_est_str')
        )

    wb.save(local_filepath)
    print(f"[OK] Local backup saved: {local_filepath}")

    # Step 2: Upload to Google Sheets
    try:
        creds = get_google_creds()
        sheets_svc = build('sheets', 'v4', credentials=creds)
        drive_svc = build('drive', 'v3', credentials=creds)
        FOLDER_ID = get_drive_folder_id()

        if not FOLDER_ID:
            print("[INFO] GOOGLE_DRIVE_FOLDER_ID not set. Creating new Drive folder...")
            folder_metadata = {'name': 'QA Ops Suite - Test Cases', 'mimeType': 'application/vnd.google-apps.folder'}
            folder = drive_svc.files().create(body=folder_metadata, fields='id').execute()
            FOLDER_ID = folder.get('id')
            print(f"[OK] Created Drive folder: https://drive.google.com/drive/folders/{FOLDER_ID}")

        # Create spreadsheet with multiple sheets (with default font Arial)
        sheet_props = [{'properties': {'title': sd['sheet_name']}} for sd in sheets_data]
        sp = sheets_svc.spreadsheets().create(body={
            'properties': {'title': title, 'defaultFormat': {'textFormat': {'fontFamily': FONT_NAME}}},
            'sheets': sheet_props
        }).execute()
        sp_id = sp['spreadsheetId']

        # Move to folder
        f = drive_svc.files().get(fileId=sp_id, fields='parents').execute()
        drive_svc.files().update(fileId=sp_id, addParents=FOLDER_ID,
            removeParents=','.join(f.get('parents', [])), fields='id').execute()

        # Get sheet IDs
        sheet_id_map = {}
        for sheet in sp['sheets']:
            sheet_id_map[sheet['properties']['title']] = sheet['properties']['sheetId']

        all_requests = []

        for sd in sheets_data:
            sname = sd['sheet_name']
            sid = sheet_id_map[sname]
            hv = sd.get('header_values', {})
            total_tc = sd['total_tc']
            time_est_str = sd.get('time_est_str')
            sections = sd['sections']
            data_rows = sd.get('data_rows', [])

            # Build values for this sheet
            created_date = hv.get('created_date', datetime.now().strftime('%Y-%m-%d'))
            b6_value = time_est_str if time_est_str else TIME_EST_FORMULA
            values = [
                ['Link DOC:', hv.get('link_doc', ''), '', 'Passed', '=COUNTIF(F10:F;D1)'] + ['']*(TOTAL_COLS - 5),
                ['Link Figma:', hv.get('link_figma', ''), '', 'Failed', '=COUNTIF(F10:F;D2)'] + ['']*(TOTAL_COLS - 5),
                ['Create by', 'QA Ops Suite', '', 'Not start', '=COUNTIF(F10:F;D3)'] + ['']*(TOTAL_COLS - 5),
                ['Create Date', created_date, '', 'Cancel', '=COUNTIF(F10:F;D4)'] + ['']*(TOTAL_COLS - 5),
                ['', '', '', 'Testcases', '=SUM(E1:E4)'] + ['']*(TOTAL_COLS - 5),
                ['Time Est (1 round):', b6_value] + ['']*(TOTAL_COLS - 2),
                ['Testcase ID', 'Testcase Description', 'Pre - Condition', 'Test Procedures', '', 'Status', '', 'Bug ID', 'Time Est', 'isAuto', 'Build #1()', '', '', 'Status #1', 'Notes'],
                ['', '', '', 'Steps to Perform', 'Steps Expected Result', 'Build STG', 'Build PRD', '', '', '', 'Device #1()', 'Device #2()', 'Device #3()', '', ''],
            ]

            section_rows = []
            merge_b_c_ranges = []

            def _append_tc_rows(tc_list):
                merge_start = None
                for tc in tc_list:
                    tc = sanitize_tc(tc)
                    is_merge = tc.get('merge_with_prev', False)
                    if is_merge:
                        if merge_start is None:
                            merge_start = len(values) - 1
                    else:
                        if merge_start is not None:
                            merge_b_c_ranges.append((merge_start, len(values) - 1))
                            merge_start = None
                    row = [''] * TOTAL_COLS
                    row[0] = tc['id']
                    if not is_merge:
                        row[1] = tc['desc']
                        row[2] = tc.get('precond', '')
                    row[3] = tc.get('steps', '')
                    row[4] = tc.get('expected', '')
                    row[5] = 'NOT START'
                    row[8] = tc.get('time_est', '')
                    values.append(row)
                if merge_start is not None:
                    merge_b_c_ranges.append((merge_start, len(values) - 1))

            if isinstance(sections, str):
                values.append([sanitize_text(sections)] + ['']*(TOTAL_COLS - 1))
                section_rows.append(len(values) - 1)
                _append_tc_rows(data_rows)
            else:
                for section_title, section_data in sections:
                    values.append([sanitize_text(section_title)] + ['']*(TOTAL_COLS - 1))
                    section_rows.append(len(values) - 1)
                    _append_tc_rows(section_data)

            last_row = len(values)

            # Write values
            sheets_svc.spreadsheets().values().update(
                spreadsheetId=sp_id, range=f"'{sname}'!A1:O{last_row}",
                valueInputOption='USER_ENTERED', body={'values': values}
            ).execute()

            # Formatting requests for this sheet
            requests = []
            # Header rows 7-8
            requests.append({'repeatCell': {
                'range': {'sheetId': sid, 'startRowIndex': 6, 'endRowIndex': 8, 'startColumnIndex': 0, 'endColumnIndex': TOTAL_COLS},
                'cell': {'userEnteredFormat': {'backgroundColor': {'red': 0.8, 'green': 1.0, 'blue': 1.0}, 'textFormat': {'bold': True, 'fontFamily': FONT_NAME}, 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE'}},
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
            }})
            # Section rows
            for sr in section_rows:
                requests.append({'repeatCell': {
                    'range': {'sheetId': sid, 'startRowIndex': sr, 'endRowIndex': sr+1, 'startColumnIndex': 0, 'endColumnIndex': TOTAL_COLS},
                    'cell': {'userEnteredFormat': {'backgroundColor': {'red': 0.925, 'green': 0.886, 'blue': 0.996}, 'textFormat': {'bold': True, 'fontFamily': FONT_NAME}, 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE'}},
                    'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
                }})
                requests.append({'mergeCells': {'range': {'sheetId': sid, 'startRowIndex': sr, 'endRowIndex': sr+1, 'startColumnIndex': 0, 'endColumnIndex': TOTAL_COLS}, 'mergeType': 'MERGE_ALL'}})
            # Multi-result TC merges (B+C cells)
            for m_start, m_end in merge_b_c_ranges:
                requests.append({'mergeCells': {'range': {'sheetId': sid, 'startRowIndex': m_start, 'endRowIndex': m_end + 1, 'startColumnIndex': 1, 'endColumnIndex': 2}, 'mergeType': 'MERGE_ALL'}})
                requests.append({'mergeCells': {'range': {'sheetId': sid, 'startRowIndex': m_start, 'endRowIndex': m_end + 1, 'startColumnIndex': 2, 'endColumnIndex': 3}, 'mergeType': 'MERGE_ALL'}})
            # Col A bold+center, Col B bold+wrap, Col C-O wrap, Status center
            requests.append({'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 8, 'endRowIndex': last_row, 'startColumnIndex': 0, 'endColumnIndex': 1}, 'cell': {'userEnteredFormat': {'textFormat': {'bold': True, 'fontFamily': FONT_NAME}, 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE'}}, 'fields': 'userEnteredFormat(textFormat,horizontalAlignment,verticalAlignment)'}})
            requests.append({'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 8, 'endRowIndex': last_row, 'startColumnIndex': 1, 'endColumnIndex': 2}, 'cell': {'userEnteredFormat': {'textFormat': {'bold': True, 'fontFamily': FONT_NAME}, 'wrapStrategy': 'WRAP', 'verticalAlignment': 'TOP'}}, 'fields': 'userEnteredFormat(textFormat,wrapStrategy,verticalAlignment)'}})
            requests.append({'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 8, 'endRowIndex': last_row, 'startColumnIndex': 2, 'endColumnIndex': TOTAL_COLS}, 'cell': {'userEnteredFormat': {'wrapStrategy': 'WRAP', 'verticalAlignment': 'TOP'}}, 'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment)'}})
            requests.append({'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 8, 'endRowIndex': last_row, 'startColumnIndex': 5, 'endColumnIndex': 7}, 'cell': {'userEnteredFormat': {'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE', 'wrapStrategy': 'WRAP'}}, 'fields': 'userEnteredFormat(horizontalAlignment,verticalAlignment,wrapStrategy)'}})
            # Header area bold
            requests.append({'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 6, 'startColumnIndex': 0, 'endColumnIndex': 1}, 'cell': {'userEnteredFormat': {'textFormat': {'bold': True, 'fontFamily': FONT_NAME}}}, 'fields': 'userEnteredFormat(textFormat)'}})
            requests.append({'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 5, 'endRowIndex': 6, 'startColumnIndex': 0, 'endColumnIndex': 2}, 'cell': {'userEnteredFormat': {'textFormat': {'bold': True, 'fontFamily': FONT_NAME}}}, 'fields': 'userEnteredFormat(textFormat)'}})
            # Status summary colors
            for row_idx, color in [(0, {'red':0.851,'green':0.961,'blue':0.839}), (1, {'red':0.984,'green':0.749,'blue':0.737}), (2, {'red':0.882,'green':0.918,'blue':1.0}), (3, {'red':0.871,'green':0.878,'blue':0.890})]:
                requests.append({'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': row_idx, 'endRowIndex': row_idx+1, 'startColumnIndex': 3, 'endColumnIndex': 4}, 'cell': {'userEnteredFormat': {'backgroundColor': color, 'horizontalAlignment': 'RIGHT'}}, 'fields': 'userEnteredFormat(backgroundColor,horizontalAlignment)'}})
            # Column widths
            for col_idx, px in [(0,80),(1,250),(2,200),(3,250),(4,250),(5,100),(6,100),(7,100),(8,80)]:
                requests.append({'updateDimensionProperties': {'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': col_idx, 'endIndex': col_idx+1}, 'properties': {'pixelSize': px}, 'fields': 'pixelSize'}})
            # Freeze + borders
            requests.append({'updateSheetProperties': {'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 8}}, 'fields': 'gridProperties.frozenRowCount'}})
            requests.append({'updateBorders': {'range': {'sheetId': sid, 'startRowIndex': 6, 'endRowIndex': last_row, 'startColumnIndex': 0, 'endColumnIndex': TOTAL_COLS}, 'top': {'style':'SOLID','color':{'red':0.7,'green':0.7,'blue':0.7}}, 'bottom': {'style':'SOLID','color':{'red':0.7,'green':0.7,'blue':0.7}}, 'left': {'style':'SOLID','color':{'red':0.7,'green':0.7,'blue':0.7}}, 'right': {'style':'SOLID','color':{'red':0.7,'green':0.7,'blue':0.7}}, 'innerHorizontal': {'style':'SOLID','color':{'red':0.7,'green':0.7,'blue':0.7}}, 'innerVertical': {'style':'SOLID','color':{'red':0.7,'green':0.7,'blue':0.7}}}})
            # Header merges
            requests.append({'mergeCells': {'range': {'sheetId': sid, 'startRowIndex': 6, 'endRowIndex': 7, 'startColumnIndex': 3, 'endColumnIndex': 5}, 'mergeType': 'MERGE_ALL'}})
            requests.append({'mergeCells': {'range': {'sheetId': sid, 'startRowIndex': 6, 'endRowIndex': 7, 'startColumnIndex': 5, 'endColumnIndex': 7}, 'mergeType': 'MERGE_ALL'}})
            requests.append({'mergeCells': {'range': {'sheetId': sid, 'startRowIndex': 6, 'endRowIndex': 7, 'startColumnIndex': 10, 'endColumnIndex': 13}, 'mergeType': 'MERGE_ALL'}})
            for col in [0, 1, 2, 7, 8, 9, 13, 14]:
                requests.append({'mergeCells': {'range': {'sheetId': sid, 'startRowIndex': 6, 'endRowIndex': 8, 'startColumnIndex': col, 'endColumnIndex': col+1}, 'mergeType': 'MERGE_ALL'}})
            # Data validation
            data_start = 8
            requests.append({'setDataValidation': {'range': {'sheetId': sid, 'startRowIndex': data_start, 'endRowIndex': last_row, 'startColumnIndex': 5, 'endColumnIndex': 6}, 'rule': {'condition': {'type': 'ONE_OF_LIST', 'values': [{'userEnteredValue': 'PASSED'}, {'userEnteredValue': 'FAILED'}, {'userEnteredValue': 'NOT START'}, {'userEnteredValue': 'CANCEL'}]}, 'showCustomUi': True, 'strict': True}}})
            requests.append({'setDataValidation': {'range': {'sheetId': sid, 'startRowIndex': data_start, 'endRowIndex': last_row, 'startColumnIndex': 6, 'endColumnIndex': 7}, 'rule': {'condition': {'type': 'ONE_OF_LIST', 'values': [{'userEnteredValue': 'PASSED'}, {'userEnteredValue': 'FAILED'}, {'userEnteredValue': 'NOT START'}, {'userEnteredValue': 'CANCEL'}]}, 'showCustomUi': True, 'strict': True}}})

            all_requests.extend(requests)

        # Apply all formatting
        if all_requests:
            sheets_svc.spreadsheets().batchUpdate(spreadsheetId=sp_id, body={'requests': all_requests}).execute()

        url = f"https://docs.google.com/spreadsheets/d/{sp_id}"
        print(f"[OK] Google Sheets created ({len(sheets_data)} sheets): {url}")
        return sp_id, url, local_filepath
    except Exception as e:
        print(f"[WARN] Google Sheets upload failed: {e}")
        print(f"[OK] Local .xlsx file is still available at: {local_filepath}")
        return None, None, local_filepath
```

## Usage Example - Single Sheet (1 sheet, 1 tính năng)

```python
data_rows = [
    {
        'id': 'TC_001',
        'desc': 'Đăng nhập thành công với email và password hợp lệ',
        'precond': '- Đã có tài khoản đăng ký\n- Tài khoản chưa bị khóa',
        'steps': '1. Mở app > Vào màn hình Đăng nhập\n2. Nhập email "test@gmail.com" vào ô Email\n3. Nhập password "Abc@1234" vào ô Mật khẩu\n4. Nhấn nút "Đăng nhập"',
        'expected': '- Hiển thị thông báo "Đăng nhập thành công"\n- Chuyển sang màn hình Trang chủ\n- Avatar user hiển thị ở header',
        'time_est': 3,
    },
    # Multi-result TC example: 1 description, 2 expected results
    {
        'id': 'TC_002',
        'desc': 'Kiểm tra tính năng Đăng xuất',
        'precond': '- Đã đăng nhập thành công\n- Đang ở màn hình Trang chủ',
        'steps': '1. Nhấn vào avatar người dùng tại header\n2. Chọn menu "Đăng xuất"\n3. Tại popup xác nhận, nhấn nút "Hủy"',
        'expected': '- Popup đóng lại\n- Session hiện tại giữ nguyên, user vẫn sử dụng app bình thường',
        'time_est': 2,
    },
    {
        'id': 'TC_003',
        'steps': '1. Nhấn vào avatar người dùng tại header\n2. Chọn menu "Đăng xuất"\n3. Tại popup xác nhận, nhấn nút "Đồng ý"',
        'expected': '- Hiển thị thông báo "Đăng xuất thành công"\n- Chuyển về màn hình Đăng nhập\n- Session/token bị xóa',
        'time_est': 3,
        'merge_with_prev': True,  # B+C cells merged with TC_002 above
    },
]

# Single section
sp_id, url, local_file = create_tc_spreadsheet(
    title='TC_Login',
    sheet_name='TC_Login',
    header_values={'link_doc': '', 'link_figma': '', 'created_date': '2026-03-09'},
    data_rows=data_rows,
    sections='ĐĂNG NHẬP',  # single string = 1 section
    total_tc=len(data_rows),
    output_dir='results/login/'
)

# Multi-section (1 sheet, nhiều section)
sp_id, url, local_file = create_tc_spreadsheet(
    title='TC_Login',
    sheet_name='TC_Login',
    header_values={'created_date': '2026-03-09'},
    data_rows=[],  # ignored when sections is list
    sections=[
        ('ĐĂNG NHẬP - HAPPY PATH', [data_rows[0]]),
        ('ĐĂNG NHẬP - NEGATIVE', []),
    ],
    total_tc=1,
    output_dir='results/login/'
)
```

## Usage Example - Multi Sheet (nhiều sheet, mỗi sheet = 1 tính năng)

**TC_ID reset về 1 ở mỗi sheet**. Sheet "Đăng nhập" có TC_001-TC_050, Sheet "Quên MK" có TC_001-TC_035.

```python
# Mỗi sheet có header riêng (rows 1-6) + COUNTIF formulas riêng
sp_id, url, local_file = create_multi_sheet_tc_spreadsheet(
    title='TC_PhieuNhapHang',
    sheets_data=[
        {
            'sheet_name': 'Tạo phiếu nhập',
            'header_values': {'link_doc': 'https://...', 'link_figma': 'https://...', 'created_date': '2026-03-09'},
            'sections': [
                ('TẠO PHIẾU NHẬP - HAPPY PATH', [
                    {'id': 'TC_001', 'desc': 'Tạo phiếu nhập thành công', 'precond': '...', 'steps': '...', 'expected': '...', 'time_est': 3},
                    {'id': 'TC_002', 'desc': 'Tạo phiếu nhập với nhiều sản phẩm', 'precond': '...', 'steps': '...', 'expected': '...', 'time_est': 5},
                ]),
                ('TẠO PHIẾU NHẬP - NEGATIVE', [
                    {'id': 'TC_003', 'desc': 'Tạo phiếu khi chưa chọn NCC', 'precond': '...', 'steps': '...', 'expected': '...', 'time_est': 2},
                ]),
            ],
            'data_rows': [],
            'total_tc': 3,
        },
        {
            'sheet_name': 'Sửa phiếu nhập',
            'header_values': {'link_doc': 'https://...', 'created_date': '2026-03-09'},
            'sections': [
                ('SỬA PHIẾU NHẬP - HAPPY PATH', [
                    {'id': 'TC_001', 'desc': 'Sửa số lượng SP trong phiếu', 'precond': '...', 'steps': '...', 'expected': '...', 'time_est': 3},  # Reset TC_001!
                    {'id': 'TC_002', 'desc': 'Sửa NCC trong phiếu', 'precond': '...', 'steps': '...', 'expected': '...', 'time_est': 4},
                ]),
            ],
            'data_rows': [],
            'total_tc': 2,
        },
    ],
    output_dir='results/phieu-nhap-hang/'
)
print(f"Local: {local_file}")
print(f"Google Sheets: {url}")
```

## Notes

### Time Est (IMPORTANT)
- Column I = Time Est per test case (số, tính theo phút)
- B6 tự động convert phút sang giờ+phút: `139 phút` => `2 giờ 19 phút / 54 cases`, `45 phút` => `45 phút / 54 cases`
- `time_est_str` parameter là optional - nếu không truyền, dùng formula tự động
- Mỗi TC dict nên có `time_est` (number) để ước lượng thời gian test mỗi case

### Multi-Result TC (merge_with_prev)
Khi 1 TC description có nhiều expected results, tách thành nhiều row:
```python
# Row đầu: có desc + precond + steps + expected
{'id': 'TC_004', 'desc': 'Kiểm tra Đăng xuất', 'precond': '...', 'steps': '1. Nhấn Hủy', 'expected': '...', 'time_est': 2}
# Row tiếp theo: merge_with_prev=True, chỉ có steps + expected (B+C merge với row trên)
{'id': 'TC_005', 'steps': '1. Nhấn Đồng ý', 'expected': '...', 'time_est': 3, 'merge_with_prev': True}
```
- B (Testcase Description) và C (Pre-Condition) cells được merge across grouped rows
- Mỗi row vẫn có TC_ID, steps, expected, time_est, và status riêng

### Multiple Sections (1 sheet)
Khi dùng multi-section mode trong `create_tc_spreadsheet`, truyền `sections` là list of tuples:
```python
sections = [
    ('SECTION 1 TITLE', [tc1, tc2, tc3]),
    ('SECTION 2 TITLE', [tc4, tc5]),
]
```
Param `data_rows` sẽ bị ignore trong mode này.

### Multiple Sheets (nhiều sheet)
Dùng `create_multi_sheet_tc_spreadsheet` khi có nhiều tính năng/module:
- Mỗi sheet = 1 tính năng/module
- **TC_ID reset về TC_001 ở mỗi sheet**
- Mỗi sheet có **header riêng** (rows 1-6) với COUNTIF formulas
- Mỗi sheet có freeze row 8, borders, data validation riêng

### Sanitize Text
Hàm `sanitize_text()` và `sanitize_tc()` tự động thay thế ký tự đặc biệt:
- `—` (em dash) => `-`
- `–` (en dash) => `-`
- `→` => `=>`
- Smart quotes => straight quotes
