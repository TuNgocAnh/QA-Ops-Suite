# QA Ops Suite

[![English](https://img.shields.io/badge/lang-en-blue.svg)](README.md)
[![Vietnamese](https://img.shields.io/badge/lang-vi-red.svg)](README-vi.md)

**QA Ops Suite** is an AI-powered QA/QC toolkit running on **Claude Code CLI** and **VS Code Extension** - a dedicated assistant that handles the heavy lifting so QA/QC teams can focus on what matters most: finding bugs and ensuring quality.

QA Ops Suite helps teams and stakeholders with:

**QA / QC**:
- Generating production-ready test cases (`.xlsx` + Lark Drive / Google Sheets)
- Creating detailed test plans with phase splitting and Story Point estimation
- Analyzing requirement documents (Lark docs, Figma, specs, local files) from a QC perspective
- Reviewing test quality and coverage gaps
- Estimating Story Points adjusted by team role

**Product Ops**:

- Evaluating SLA compliance with percentile analysis and trend tracking
- Generating Product Health Scorecards (quality, customer, testing, velocity metrics)
- Assessing release readiness with quality gates (GO / CONDITIONAL GO / NO-GO)
- Triaging bugs/incidents with RICE scoring and cross-feature impact analysis
- Risk assessment with risk matrix, mitigation plans, and test strategy recommendations

> Works on both **macOS** and **Windows**. Claude Code CLI (terminal) and Claude Code Extension (VS Code) are both supported.

![Example /plan-tc prompt on VS Code Extension](example/example-plan-prompt.png)

---

## Table of Contents

- [Key Features](#key-features)
- [System Requirements](#system-requirements)
- [Installation (Step by Step)](#installation-step-by-step)
  - [Step 1: Clone the project](#step-1-clone-the-project)
  - [Step 2: Install Python](#step-2-install-python)
  - [Step 3: Install Python dependencies](#step-3-install-python-dependencies)
  - [Step 4: Install Node.js](#step-4-install-nodejs-required-for-lark-mcp)
  - [Step 5: Install Claude Code](#step-5-install-claude-code)
  - [Step 6: Run OAuth setup](#step-6-run-oauth-setup-authenticate-your-google-account)
  - [Step 7: (Optional) Configure upload target](#step-7-optional-configure-upload-target)
  - [Step 8: Open Claude Code](#step-8-open-claude-code)
- [How Google Sheets Integration Works](#how-google-sheets-integration-works)
- [MCP Servers Configuration](#mcp-servers-configuration)
  - [Figma MCP](#figma-mcp)
  - [Lark MCP](#lark-mcp)
- [Command Guide](#command-guide)
  - [QA / QC Commands](#qa--qc-commands)
    - [/analyze](#analyze---analyze-requirement-documents)
    - [/plan-tc](#plan-tc---create-test-plan)
    - [/cook](#cook---generate-test-cases--checklists)
    - [/fix](#fix---update-tcs-on-drive--bug-analysis)
    - [/log-bug](#log-bug---log-bugs-to-lark-bitable)
    - [/bug](#bug---log-bugs-compact-style)
    - [/update-board](#update-board---update-board-configuration)
    - [/check-duplicate-bug](#check-duplicate-bug---check-potential-duplicate-bugs)
    - [/explain-bug](#explain-bug---explain-bug-reports)
    - [/search-doc](#search-doc---search-lark-wiki)
    - [/ask](#ask---qctesting-consulting)
    - [/est-sp](#est-sp---estimate-story-points)
  - [Product Ops Commands](#product-ops-commands)
    - [/sla](#sla---sla-evaluation--reporting)
    - [/health](#health---product-health-scorecard)
    - [/release-check](#release-check---release-readiness-assessment)
    - [/triage](#triage---bugincident-triage)
    - [/risk](#risk---risk-assessment)
- [Recommended Workflow](#recommended-workflow)
- [Multi-Agent Architecture](#multi-agent-architecture)
- [Output Format](#output-format)
- [Tips for Effective Prompts](#tips-for-effective-prompts)
- [Directory Structure](#directory-structure)
- [Extensible Architecture](#extensible-architecture)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)

---

## Key Features

### QA / QC

| Command | Role | Description | Output |
|---------|------|-------------|--------|
| `/analyze` | Senior QA Analyst | Analyze requirement documents from QC perspective | `.md` file in `results/` |
| `/plan-tc` | Senior QA Lead | Create detailed test plan with phases and SP estimation | `.md` file in `plans/` |
| `/cook` | Senior QC Engineer | Generate production-ready test cases and checklists | Lark/Google Sheets URL + local `.xlsx` |
| `/fix` | Senior QC Engineer | Update/add/delete TCs on Drive + bug analysis | Updated Sheets + `.md` report |
| `/log-bug` | Senior QC Engineer | Log bugs to Lark Bitable with attachments (images/videos) | Bug record + direct link |
| `/bug` | Senior QC Engineer | Draft a compact bug report (single-block body, auto Severity/Priority, video frame analysis) — **does NOT upload to Lark**, output as chat text for manual paste | Bug draft in chat |
| `/update-board` | Configuration Assistant | Update bug/task/test board config from a Lark Bitable URL | `.env` updated + status output |
| `/check-duplicate-bug` | Senior QC Engineer | Check potential duplicate bugs before creating a new one | Direct response |
| `/explain-bug` | Senior QC Engineer | Explain unclear bug reports in plain language | Direct response |
| `/search-doc` | Senior QA Research Assistant | Search Lark Wiki, synthesize answer from top 1-5 docs with citations | Direct response |
| `/ask` | Senior QA Consultant | Deep Q&A, strategy consulting based on project context | Direct response |
| `/est-sp` | Senior QA Lead | Estimate Story Points from QC perspective | Direct response + update plan |
| `/help` | Lookup Assistant | Print command list, or details of a single command, or current `.env` config | Direct response |

### Product Ops

| Command | Role | Description | Output |
|---------|------|-------------|--------|
| `/sla` | Senior Product Ops Analyst | Evaluate SLA compliance, generate SLA reports | `.md` report + `.xlsx` |
| `/health` | Senior Product Ops Analyst | Product Health Scorecard (quality, customer, testing, velocity) | `.md` scorecard |
| `/release-check` | Senior QA Lead | Release Readiness Assessment (GO / CONDITIONAL GO / NO-GO) | `.md` report |
| `/triage` | Senior QA/PS Lead | Bug/Incident triage with RICE scoring and impact analysis | `.md` report + `.xlsx` |
| `/risk` | Senior QA Lead | Risk Assessment with risk matrix and mitigation plan | `.md` report |

---

## System Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| **Claude Code** | Latest | Main tool (CLI or VS Code Extension) |
| **Python** | 3.9+ | Run scripts to create and upload spreadsheets |
| **Node.js** | 18+ | Run MCP servers (Lark) via npx |
| **npx** | (comes with Node.js) | Launch MCP servers |
| **Git** | Any | Clone repository |

---

## Installation (Step by Step)

### Step 1: Clone the project

```bash
git clone <repo-url> QAOpsSuite
cd QAOpsSuite
```

### Step 2: Install Python

**macOS:**
```bash
# Check if Python is installed
python3 --version

# If not installed, use Homebrew:
brew install python
```

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. **IMPORTANT**: During installation, check **"Add Python to PATH"**
3. Verify in PowerShell or CMD:
   ```powershell
   python --version
   ```

> On Windows, use `python` instead of `python3`. On macOS, use `python3`.

### Step 3: Install Python dependencies

> **Shortcut**: Use the one-command setup script to do steps 3-7 together:
>
> - macOS / Linux: `./scripts/setup.sh`
> - Windows (PowerShell): `.\scripts\setup.ps1`
>
> The script checks Python/Node/ffmpeg, installs pip deps, copies `.env.example` + `.mcp.json.example`, and runs Google OAuth. If you prefer manual setup, continue with the steps below.

**macOS / Linux:**
```bash
pip3 install -r requirements.txt
```

**Windows (PowerShell or CMD):**
```powershell
pip install -r requirements.txt
```

`requirements.txt` includes: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, `openpyxl`, `requests`, `PyYAML`.

### Step 4: Install Node.js (required for Lark MCP)

**macOS:**
```bash
node -v           # Check
brew install node  # If not installed
```

**Windows:**
1. Download Node.js LTS from https://nodejs.org/
2. Run the installer (npx is included automatically)
3. Verify in PowerShell:
   ```powershell
   node -v
   npx -v
   ```

### Step 5: Install Claude Code

**macOS:**
```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

**Windows (PowerShell as Administrator):**
```powershell
npm install -g @anthropic-ai/claude-code
claude --version
```

**VS Code Extension (both platforms):**
1. Open VS Code
2. Go to Extensions (`Cmd+Shift+X` on macOS / `Ctrl+Shift+X` on Windows)
3. Search for **"Claude Code"** by Anthropic
4. Click **Install**

### Step 6: Run OAuth setup (authenticate your Google account)

**macOS:**
```bash
python3 configs/setup-oauth.py
```

**Windows:**
```powershell
python configs/setup-oauth.py
```

The script will:
1. Open your browser -- log in with your Google account
2. Google will ask you to grant permission -- click **Continue**

![Google OAuth consent - click Continue](example/verify-google.png)

3. After granting permission, the terminal shows the setup progress:

![OAuth setup complete in terminal](example/cmd-auth-google.png)

The script automatically:
- Saves your OAuth token at `configs/google-oauth-token.json`
- Creates/updates `.env` file with refresh token
- Creates a new Drive folder **"QA Ops Suite - Test Cases"** on your account (if none exists)

> **Only 1 scope is needed**: `drive.file` -- allows the app to create and manage files it created. No broad access to your entire Drive or all Sheets. See [Security Notes](#security-notes) for details.

### Step 7: (Optional) Configure upload target

Set where test case files are uploaded. **Lark has higher priority** -- if both are set, Lark is used first (falls back to Google on failure).

**Option A - Lark Drive (recommended for Lark users):**
1. Open Lark Drive, navigate to target folder
2. Copy the folder ID from URL: `https://...larksuite.com/drive/folder/<FOLDER_ID>`
3. Edit `.env`:
   ```
   LARK_DRIVE_FOLDER_ID=<paste_folder_id>
   ```
4. First upload will open browser for Lark OAuth -- authorize once, token is cached at `configs/lark-oauth-token.json`
5. Files are **auto-converted** based on type:
   - `.xlsx` / `.xls` / `.csv` => **Lark Sheet** (editable spreadsheet)
   - `.doc` / `.docx` / `.md` / `.txt` => **Lark Doc** (editable document)
   - Other files => Raw file (download only)

**Option B - Google Drive:**
1. Open Google Drive, select the folder for storing test cases
2. Copy the folder ID from URL: `https://drive.google.com/drive/folders/<FOLDER_ID_HERE>`
3. Edit `.env`:
   ```
   GOOGLE_DRIVE_FOLDER_ID=<paste_folder_id>
   ```

**Upload priority**: `LARK_DRIVE_FOLDER_ID` > `GOOGLE_DRIVE_FOLDER_ID` > skip (local `.xlsx` only). If Lark upload fails, automatically falls back to Google.

**Option C - Lark Bitable boards (bug tracking, tasks):**

Configure Lark Bitable boards to enable bug search, bug logging, task reading, and SLA analysis.

1. Open your Bitable board on Lark, copy IDs from URL: `https://<domain>.larksuite.com/base/<BASE_ID>?table=<TABLE_ID>`
2. Edit `.env`:
   ```
   # Bug Board (for /bug, /log-bug, /triage, /fix, duplicate check)
   LARK_BUG_BASE_NAME=<paste_base_name>
   LARK_BUG_BASE_ID=<paste_base_id>
   LARK_BUG_TABLE_ID=<paste_table_id>
   LARK_BUG_VIEW_ID=<paste_view_id>            # used to build record URLs
   LARK_BUG_WIKI_TOKEN=<paste_wiki_token>      # used to build record URLs

   # Task/Sprint Board (for /sla, /release-check, /health)
   LARK_TASK_BASE_ID=<paste_base_id>
   LARK_TASK_TABLE_ID=<paste_table_id>

   # Test Execution Board (optional, for /release-check, /health)
   LARK_TEST_BASE_ID=<paste_base_id>
   LARK_TEST_TABLE_ID=<paste_table_id>
   ```
3. Re-authenticate to get new scopes (one-time after first setup):
   ```bash
   rm configs/lark-oauth-token.json
   python3 configs/lark-upload.py .env <your_lark_folder_id>
   ```
4. Verify: `python3 configs/lark_bitable.py status`

Capabilities enabled:

| Feature | Description | Commands |
|---------|-------------|----------|
| Search bugs | Search by description, check duplicates | `/triage`, `/fix` |
| Log bugs | Create bug with description + attachments | `/fix`, direct prompt |
| Read bug status | Get status of existing bugs | `/triage`, `/fix` |
| Read tasks | List tasks for SLA/release analysis | `/sla`, `/release-check`, `/health` |

**Option D - Set user role for Story Point estimation:**

Edit `.env`:
```
USER_ROLE=senior
```

Valid values: `junior`, `mid`, `senior`, `lead` (default: `senior`). This affects Story Point estimation in `/plan-tc`, `/cook`, and `/est-sp` commands. See [/est-sp](#est-sp---estimate-story-points) for details.

**Option E - Bug logging defaults & search tuning:**

Optional `.env` variables that streamline `/bug`, `/log-bug`, and `/search-doc`:

```
DEFAULT_SPRINT=1-2026/4                  # /log-bug uses if user omits Sprint; auto-updated when user provides a new one
DEFAULT_VERSION=STG 1.0.9 (2)            # same behaviour as DEFAULT_SPRINT
TEST_ACCOUNT=0923267268 - 123456         # auto-prepended to bug body when user does not supply one
CHECK_DUPLICATE_BUG=true                 # /log-bug and /bug call /check-duplicate-bug before creating
LARK_WIKI_PRIORITY_KEYWORDS=Sổ Bán Hàng,SoBanHang,SBH,Shinhan   # boost score for /search-doc results
```

**Multi-board setup**: If your team tracks bugs on multiple Lark boards (one per app/project), keep the full registry in [.claude/boards.md](.claude/boards.md) and only point `.env` at one **active** board at a time. `/log-bug` confirms the active board once per day via `.claude/.board-state.json` (gitignored). Switch active board with `/update-board tracking bug: <URL>`.

### Step 8: Open Claude Code

**Option 1 - Claude Code CLI (Terminal):**
```bash
cd QAOpsSuite
claude
```

**Option 2 - VS Code Extension:**
1. Open VS Code
2. Open the `QAOpsSuite` folder
3. Open Claude Code panel (Claude icon on sidebar, or `Cmd+Shift+P` / `Ctrl+Shift+P` => "Claude Code")
4. Start using commands: `/cook`, `/plan-tc`, `/fix`...

> MCP servers are pre-configured in `.mcp.json` (included in repo) -- **NO NEED** to run `claude mcp add` manually.

---

## How Google Sheets Integration Works

QA Ops Suite uses **Python scripts with Google APIs directly** (not MCP) to create and manage Google Sheets. This approach provides full control over formatting, merging, borders, dropdowns, and all advanced features.

### Architecture

```
Claude Code generates Python script with test case data
    |
    v
Python script (openpyxl + Google API)
    |
    +-- 1. Create local .xlsx file (backup in results/)
    |
    +-- 2. Upload to Drive (priority order):
    |       a. Lark Drive => auto-import as editable Lark Sheet
    |       b. Google Sheets => full formatting via API
    |       c. Local only => if both are unavailable
    |
    +-- 3. Return editable URL (Lark Sheet or Google Sheets)
```

### Why Python API instead of MCP Sheets?

| Capability | Python API (current) | MCP Sheets |
|---|---|---|
| Read/Write data | Yes | Yes |
| Cell formatting (bold, color, borders) | Yes | No |
| Merge cells | Yes | No |
| Data validation (dropdowns) | Yes | No |
| Freeze rows/columns | Yes | No |
| Column width control | Yes | No |
| Local .xlsx backup | Yes | No |

MCP Sheets only supports basic CRUD operations. QA Ops Suite needs full formatting control (which accounts for ~60% of the spreadsheet code), so the Python API is the right choice.

---

## MCP Servers Configuration

### File `.mcp.json` (included in repo)

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
        "-a", "<app_id>",
        "-s", "<app_secret>",
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

To let Claude read designs from Figma:

1. **Login to Figma MCP**: First time, Claude will ask you to login to Figma -- follow the instructions
2. **Enable Dev Mode** on Figma:
   - Open Figma file => Toggle **"Dev Mode"** on the toolbar (or shortcut `Shift + D`)
   - Dev Mode shows more accurate specs (spacing, padding, colors, typography)
3. **Copy the node link**:
   - Select the frame/component => Right-click => **Copy link to selection**
   - Link format: `https://www.figma.com/design/<fileKey>/<fileName>?node-id=<nodeId>`
4. **Use `&m=dev` in the link** so Claude reads in dev mode:
   - Example: `https://www.figma.com/design/abc123/MyApp?node-id=451-8205&m=dev`

### Lark MCP

- Automatically connects to Lark (Larksuite) for reading documents, sheets, and comments
- First time: Claude will ask you to **authenticate your Lark account** via OAuth
- After authentication, you can reference Lark links directly in prompts
- **Supported types**: Wiki, Docx, Doc, Sheets, Bitable, Mindnote, Slides, File attachments, document comments
- **Token mode**: `user_access_token` -- all actions use the authenticated user's identity for full traceability
- **Tools enabled**: Document content, block list, comments, media download, search, Bitable CRUD, Task API
- **Embedded link reading**: Links found inside Lark documents are automatically read by sub-agents in parallel (Lark links, external URLs, and Figma links trigger their respective reader agents)
- **Bitable integration**: Read/create/update records on Lark Bitable boards (bug tracking, task management)
- Example: `https://sobanhang.sg.larksuite.com/wiki/...`

> **Python-first rule (IMPORTANT)**: For any Lark read/write (wiki, docx, search, Bitable CRUD, comments, media), QA Ops Suite prefers [configs/lark_api.py](configs/lark_api.py) over the MCP server. The Python helper auto-refreshes tokens (and falls back to browser OAuth if the refresh token is also expired); the MCP server does not, so it frequently fails with `99991668: user_access_token invalid or expired`. MCP is kept only as a fallback when `lark_api.py` lacks a wrapper.
>
> CLI debug: `python3 configs/lark_api.py token` (refresh shared token), `read-wiki <token>`, `list-fields <base> <table>`, `search-wiki <query>`.

---

## Command Guide

### QA / QC Commands

#### `/analyze` - Analyze requirement documents

**Role**: Senior QA Analyst

**Purpose**: Analyze specs/PRD documents from a QC perspective, creating a detailed analysis as input for `/plan-tc` and `/cook`.

**Workflow**:
1. Receive document link (online URL or local file)
2. Automatically read content via sub-agents in parallel:
   - **Lark documents**: Wiki, Docx, Doc, Sheet, Bitable, Mindnote, Slides, File
   - **Web URLs**: Any accessible web page
   - **Local files**: All text-based formats, PDFs, images (multimodal), spreadsheets, notebooks
3. **Embedded links read in parallel**: Links found inside the source document are automatically dispatched to sub-agents
4. **Comments read automatically** from Lark documents
5. Analyze 6 sections: metadata, summary, QC analysis, document quality assessment, questions for PO/Design, test plan suggestions
6. Export `.md` file to `results/<feature_name>/`

**Example prompts**:
```
/analyze https://<your-domain>.larksuite.com/wiki/<wiki_token>
```

```
/analyze Docs/purchase-order/specs.md
```

```
/analyze Please analyze these 2 documents together:
- Specs: https://sobanhang.sg.larksuite.com/wiki/xxx
- Figma: https://www.figma.com/design/abc/Finan?node-id=451-8205&m=dev
```

---

#### `/plan-tc` - Create test plan

**Role**: Senior QA Lead

**Purpose**: Create a detailed test plan with phase splitting, TC matrix, dependency analysis, and Story Point estimation. The plan is structured so any QC engineer can use it directly as input for `/cook`.

**Output includes**:
- Test scope and objectives
- Phase breakdown with independent TC_ID ranges
- Coverage matrix (positive, negative, boundary, edge)
- Story Point estimation (adjusted by user role)
- Impact analysis from sitemap
- Time estimation

**Example prompts**:
```
/plan-tc Test cases for Purchase Order module
Specs: https://sobanhang.sg.larksuite.com/wiki/xxx
```

```
/plan-tc Sprint 12 - VNPay payment integration
Specs: Docs/payment/specs.md
Figma: https://www.figma.com/design/abc/Finan?node-id=123-456&m=dev
Platform: iOS + Android
```

```
/plan-tc Create test plan from this analysis:
results/purchase-order/po-analysis.md
```

---

#### `/cook` - Generate test cases & checklists

**Role**: Senior QC Engineer

**Purpose**: Generate production-ready test cases from a plan or specs, then upload to Lark Drive or Google Sheets.

**Quality standards**:
- Detailed step-by-step: specific action, test data, UI element location
- Expected results with real testing value (NOT "app does not crash")
- Full coverage: Positive + Negative + Boundary + Edge cases
- Priority levels: Critical > High > Medium > Low
- Multi-agent parallel execution for large features
- TC_ID resets per sheet: TC_001, TC_002... (each sheet starts from TC_001)

**Example prompts**:
```
/cook Write test cases for Purchase Order
Specs: https://sobanhang.sg.larksuite.com/wiki/xxx
Figma: https://www.figma.com/design/abc/Finan?node-id=451-8205&m=dev
```

```
/cook Execute plan in plans/purchase-order/test-plan.md
```

```
/cook Checklist for login feature
Specs: Docs/auth/login-specs.md
Language: English
```

---

#### `/fix` - Update TCs on Drive & bug analysis

**Role**: Senior QC Engineer

**Purpose**: Update, add, or delete existing test cases on Drive, or analyze bugs to create regression TCs.

**3 modes**:

| Mode | Input | Action |
|------|-------|--------|
| Update TCs on Drive | Sheets URL + change description | Edit directly on Sheets via API |
| Fix TCs from plan | Sheets link or plan file | Analyze and fix on Sheets |
| Bug analysis | Bug report description | Analyze root cause + create regression TCs |

**Example prompts**:
```
/fix Add 5 negative test cases to sheet "Create Purchase Order"
Link: https://docs.google.com/spreadsheets/d/xxx
```

```
/fix Update test cases based on new specs:
Sheets: https://docs.google.com/spreadsheets/d/xxx
New specs: https://sobanhang.sg.larksuite.com/wiki/yyy
```

```
/fix User cannot receive OTP on iOS 17
Build: v2.1.0 (build 345)
Steps: Register > Enter phone > Tap "Send OTP" > No SMS received
```

---

#### `/log-bug` - Log bugs to Lark Bitable

**Role**: Senior QC Engineer

**Purpose**: Log bugs directly to your Lark Bitable bug tracking board from a prompt. Supports image and video attachments via file path.

**2 modes**:

| Mode           | Condition                                      | Behavior                                       |
|----------------|------------------------------------------------|------------------------------------------------|
| Full info      | Dev PIC + Sprint + Version + Feature all present | Create immediately, return direct link         |
| Missing fields | Any mandatory field missing                    | Display draft, ask user to fill in, then create |

**Attachment support**: Images (`.png`, `.jpg`, `.gif`, `.webp`) and videos (`.mp4`, `.mov`, `.avi`) -- provide the file path in your prompt.

> **How to copy file path for attachment**:
>
> | OS          | Method                                                       | Shortcut                 |
> |-------------|--------------------------------------------------------------|--------------------------|
> | **macOS**   | Select file in Finder, press                                 | **Cmd + Option + C**     |
> | **macOS**   | Or: **Option + Right-click** file > **Copy ... as Pathname** |                          |
> | **Windows** | **Shift + Right-click** file > **Copy as path**              |                          |
> | **Windows** | Or: Select file in Explorer, press                           | **Ctrl + Shift + C**     |
>
> Then paste the path into your prompt: `/log-bug ... attachment: <paste_path_here>`

**Example prompts**:

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
> If mandatory fields (Dev PIC, Sprint, Version, Feature) are missing, QA Ops Suite will display a draft and ask you to provide them before creating.

---

#### `/bug` - Log bugs (compact style)

**Role**: Senior QC Engineer

**Purpose**: Draft a compact, single-block bug report (inherits the "Report bug" project format) and **print it to the chat for manual paste** into Lark / Slack / comments. **Does NOT call Lark API and does NOT create a record** — use `/log-bug` if you want to push the bug onto the board.

**Differences vs `/log-bug`**:

| Criteria | `/bug` | `/log-bug` |
|----------|--------|------------|
| Upload to Lark | **No** — chat output only | **Yes** — creates a Bitable record |
| When to use | Quick draft to share manually (Slack, comment, paste) | Officially track the bug on the team board |
| Body style | Single block (Steps + Actual + Expected glued together) | Separate template fields per Lark schema |
| Body sections | Account test → Steps → Actual → Expected (no FE/BE, Preconditions, Notes) | Preconditions, Steps, Actual, Notes, Account test |
| Headers | No colons (`Steps to Reproduce`) | With colons (`Steps:`) |
| Duplicate check | No (no record to dedupe against) | Yes |
| Severity & Priority | Auto-estimated and shown in draft header | Optional |
| Video support | Yes — extracts frames to understand flow (does NOT upload the video) | Yes — uploads the video |

**Metadata auto-filled in the draft header**: Name, Platform, Type, Priority, Severity, Version. User fills Dev PIC, Sprint, Tính năng manually when pasting onto the board.

**Example prompts**:

```
/bug Báo cáo Kho tính tổng tồn sai, tính năng: Báo cáo, version stg-1.0.51
```

```
/bug C:/Users/me/Downloads/bug-payment.mp4
```

```
/bug [screenshot attached] lỗi hiển thị số lần chỉnh sửa tên miền, version STG 1.0.9
```

> For videos: put them in `bug-videos/` at project root, then pass the full path. Videos > 120s are rejected.

---

#### `/update-board` - Update board configuration

**Role**: Configuration Assistant

**Purpose**: Update bug/task/test board settings in `.env` from a Lark Bitable URL.

**What it updates**:
- `LARK_DOMAIN`
- `LARK_BUG_*` or `LARK_TASK_*` or `LARK_TEST_*` (based on board type hint)
- Resolves and stores bug base title in `LARK_BUG_BASE_NAME` when applicable

**Example prompts**:

```text
/update-board tracking bug: https://<your-domain>.larksuite.com/wiki/<wiki_token>?table=<table_id>&view=<view_id>
```

```text
/update-board task: https://<your-domain>.larksuite.com/wiki/<wiki_token>?table=<table_id>&view=<view_id>
```

```text
/update-board
```

> If no board type is provided, it defaults to bug board.

---

#### `/check-duplicate-bug` - Check potential duplicate bugs

**Role**: Senior QC Engineer

**Purpose**: Search the bug board for similar active bugs before creating a new one. This command does not create records.

**Typical use cases**:
- Use standalone when you want a quick duplicate scan before logging.
- Used internally by `/log-bug` when `CHECK_DUPLICATE_BUG=true` in `.env`.

**Example prompts**:

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

#### `/explain-bug` - Explain bug reports

**Role**: Senior QC Engineer

**Purpose**: Explain unclear or poorly written bug reports in plain language -- helps you quickly understand what the bug reporter meant.

**3 input methods**:

| Method               | Input                 | Example                                                        |
|----------------------|-----------------------|----------------------------------------------------------------|
| Bug ID (recommended) | Bug ID from the board | `/explain-bug BId-000427` or `/explain-bug 427`               |
| Paste text           | Raw bug description   | `/explain-bug <paste bug text>`                                |
| Lark record link     | Full Lark record URL  | `/explain-bug https://...larksuite.com/wiki/...?record=recXXX` |

**Example prompts**:

```
/explain-bug BId-000427
```

```
/explain-bug user said: "payment screen broke after I click many time fast the button not work then money gone"
```

---

#### `/search-doc` - Search Lark Wiki

**Role**: Senior QA Research Assistant

**Purpose**: Search Lark Wiki across **all spaces you have access to** (both title and content), then synthesize an answer from the top 1-5 most relevant documents with **inline citations**. Useful for finding internal policies, dept guidelines, cross-team specs, etc.

**How it works** (multi-agent dispatcher):

1. Main agent generates 3-5 keyword variants from your query (with/without diacritics, synonyms, abbreviations)
2. **Wave 1 (parallel, max 5 sub-agents)**: Each sub-agent searches 1 keyword variant on both `wiki_v1_node_search` (title) and `docx_builtin_search` (content)
3. Main agent dedupes + ranks results. Documents matching `LARK_WIKI_PRIORITY_KEYWORDS` (default: "Sổ Bán Hàng,SoBanHang,SBH,Shinhan") get a 1.5x score boost
4. **Wave 2 (parallel, max 5 sub-agents)**: Top 1-5 docx documents are read in full (truncated to 10000 chars per doc)
5. Main agent synthesizes a Q&A answer using **only** content from those docs, with `[N]` citations matching the reference table

**Output**:
- Synthesized answer with `[1]`, `[2]`... citations
- Reference table (title, space, type, link)
- Secondary table for non-docx matches (sheets, bitable, slides — open manually)
- Confidence: High / Medium / Low

**Example prompts**:

```
/search-doc quy định L8 là gì
```

```
/search-doc policy hoàn tiền S2C HKD
```

```
/search-doc onboarding flow Shinhan customer
```

```
/search-doc quy trình release Marketing
```

> **Note**: Result is returned in conversation only (not saved to a file). For 0 matches or vague queries, the command suggests alternative keywords instead of auto-retrying.
>
> **Required OAuth scopes**: `wiki:wiki:readonly`, `docs:document.content:read`, `drive:drive.search:readonly`. If 401/403: `rm configs/lark-oauth-token.json` then retry.

---

#### `/ask` - QC/Testing consulting

**Role**: Senior QA Consultant

**Purpose**: Deep Q&A about QC/Testing, strategy consulting based on actual project context. Ask about coverage, test strategy, best practices, or get a quality review.

**Example prompts**:
```
/ask Is the test coverage sufficient for the invoice export feature?
```

```
/ask Review test case quality in results/purchase-order/
```

```
/ask What testing strategy would you recommend for a payment gateway integration?
```

```
/ask Compare the pros and cons of risk-based testing vs exhaustive testing for our Sprint 15 scope
```

---

#### `/est-sp` - Estimate Story Points

**Role**: Senior QA Lead

**Purpose**: Estimate Story Points from the QC perspective (writing TCs + execution + bug logging + retest), adjusted by the user role configured in `.env`.

**Modes**:

| Mode | Input | Action |
|------|-------|--------|
| From plan | Path to plan file | Read plan, estimate SP, update plan |
| From prompt | Feature description + specs/Figma links | Analyze requirements, estimate SP |
| Existing SP | Plan that already has SP | Display existing SP, ask to re-estimate |

**Story Point scale**: Fibonacci (1, 2, 3, 5, 8, 13, 21)

**Role multiplier** (configured via `USER_ROLE` in `.env`):

| Role | Multiplier | Description |
|------|-----------|-------------|
| junior | x1.5 | More time for learning context, detailed TC writing |
| mid | x1.2 | Experienced but may need guidance on complex parts |
| senior | x1.0 | Baseline -- quick understanding, efficient TC writing |
| lead | x1.0 | Same as senior for execution, plus review responsibility |

**Example prompts**:

```
/est-sp plans/purchase-order/test-plan.md
```

```
/est-sp VNPay payment module
Specs: https://sobanhang.sg.larksuite.com/wiki/xxx
Figma: https://www.figma.com/design/abc/Finan?node-id=123-456&m=dev
```

**Example output**:

![Example /est-sp output](example/estimate-story-point.png)

> **Note**: `/plan-tc` and `/cook` also automatically include SP estimation in their output.

---

### Product Ops Commands

#### `/sla` - SLA Evaluation & Reporting

**Role**: Senior Product Ops Analyst

**Purpose**: Evaluate SLA compliance from ticket/bug data, generate SLA reports with percentile analysis, breach tracking, and trend comparison.

**Metrics calculated**:

| Metric | Description |
|--------|-------------|
| SLA Compliance Rate | `(Tickets resolved within SLA / Total) x 100%` -- target >= 95% |
| MTTR (Response) | Mean time to first response, per priority |
| MTTR (Resolution) | Mean time to resolution, per priority |
| SLA Breach Rate | % tickets exceeding SLA, by priority |
| Percentile Analysis | P50, P90, P95 for response and resolution times |
| Assignee Performance | Compliance rate and avg resolution per person |

**Default SLA targets**:

| Priority | Response Time | Resolution Time |
|----------|--------------|-----------------|
| P1 - Critical | 15 min | 4 hours |
| P2 - High | 1 hour | 24 hours |
| P3 - Medium | 4 hours | 72 hours |
| P4 - Low | 24 hours | 1 week |

**Example prompts**:

```
/sla Evaluate SLA for Sprint 15 tickets
Link: https://docs.google.com/spreadsheets/d/xxx
```

```
/sla Analyze SLA from bug tracker export
File: results/sprint-15/bug-list.xlsx
Period: March 2026
```

---

#### `/health` - Product Health Scorecard

**Role**: Senior Product Ops Analyst

**Purpose**: Generate a product health scorecard with quality, customer, testing, and velocity metrics. Each metric is rated Healthy / Warning / Critical with an overall health score.

**Metric groups**:

| Group | Key Metrics |
|-------|-------------|
| **Quality** | Bug Escape Rate (<5%), Regression Rate (<3%), Critical Bugs Open |
| **Customer** | Customer-Reported Bug Ratio (<20%), Repeat Issue Rate (<5%) |
| **Testing** | Test Coverage (>80%), Execution Rate (>95%), Pass Rate (>95%) |
| **Velocity** | Bug Fix Turnaround, Release Frequency, Hotfix Rate (<10%) |

**Overall Health Score**: Healthy (>=80%) / Warning (60-79%) / Critical (<60%)

**Example prompts**:

```
/health Generate scorecard from Sprint 15 data
Bugs: https://docs.google.com/spreadsheets/d/xxx
Test results: https://docs.google.com/spreadsheets/d/yyy
```

```
/health Scan project data and generate health report
```

---

#### `/release-check` - Release Readiness Assessment

**Role**: Senior QA Lead

**Purpose**: Assess release readiness against quality gates, output a GO / CONDITIONAL GO / NO-GO verdict with confidence score.

**Quality Gates**:

| Gate | Criteria | Pass Condition |
|------|----------|----------------|
| G1 - Test Completion | All TCs executed | Execution rate >= 95% |
| G2 - Test Pass Rate | Sufficient pass rate | Pass rate >= 95% |
| G3 - Critical Bugs | No blockers | 0 P1/P2 open |
| G4 - High Bugs | P3 triaged | All P3 have workaround or accepted |
| G5 - Regression | Regression clean | 100% pass |
| G6 - Rollback Plan | Documented | Yes/No |
| G7 - Release Notes | Reviewed | Yes/No |
| G8 - Sign-off | Approved | Yes/No |

**Verdict**: GO (all pass) / CONDITIONAL GO (non-critical failures, confidence >= 70%) / NO-GO (critical gate failure)

**Example prompts**:

```
/release-check v2.1.0 release readiness
Test results: https://docs.google.com/spreadsheets/d/xxx
Known bugs: 2 P3 open (workaround available), 0 P1/P2
```

```
/release-check Scan latest test results in results/payment-module/
Version: v3.0.0
```

---

#### `/triage` - Bug/Incident Triage

**Role**: Senior QA/PS Lead

**Purpose**: Classify bugs by severity, calculate RICE priority scores, analyze cross-feature impact from sitemap, and recommend handling order with SLA deadlines.

**RICE scoring**: `Score = (Reach x Impact x Confidence) / Effort`

**Output includes**:
- Auto-classified severity (P1-P4) with confirmation request
- RICE score and priority ranking
- Bug type classification (Functional, UI/UX, Performance, Data, Security, Integration, Regression)
- Cross-feature impact analysis from sitemap
- Regression scope per bug
- SLA deadlines per severity

**Example prompts**:

```
/triage Triage these bugs from Sprint 15
Link: https://docs.google.com/spreadsheets/d/xxx
```

```
/triage
BUG-101: Payment fails when using VNPay on iOS 17, affects all iOS users
BUG-102: Filter dropdown doesn't reset after clearing search, workaround: refresh page
BUG-103: Typo in invoice export header "Inoice" instead of "Invoice"
```

---

#### `/risk` - Risk Assessment

**Role**: Senior QA Lead

**Purpose**: Assess risks for a feature or release from QA perspective, output a risk matrix with likelihood x impact scoring, mitigation strategies, and test strategy recommendations.

**Risk dimensions**:

| Category | Factors Assessed |
|----------|-----------------|
| **Technical** | Code complexity, integration points, data migration, new tech, platform scope, performance |
| **Process** | Specs completeness, timeline pressure, team familiarity, dependencies, historical bugs |
| **Business** | User impact, revenue impact, compliance, data sensitivity, rollback difficulty |

**Risk levels**: Low (1-4) / Medium (5-9) / High (10-15) / Critical (16-25)

**Example prompts**:

```
/risk Assess risk for VNPay payment integration
Specs: https://sobanhang.sg.larksuite.com/wiki/xxx
Timeline: 2 weeks
```

```
/risk Risk assessment for release v3.0.0
Scope: Payment module rewrite + new invoice template + supplier management changes
```

```
/risk plans/purchase-order/test-plan.md
```

---

## Recommended Workflow

### QA / QC Workflow

```
1. /analyze   =>  Analyze requirement documents
   Input: specs link (Lark/Web/local file)
   Output: results/<feature>/<prefix>-analysis.md

2. /plan-tc   =>  Create detailed test plan (includes SP estimation)
   Input: analysis + specs + Figma + scope
   Output: plans/<feature>/test-plan.md

3. /cook      =>  Generate test cases from plan (includes SP in header)
   Input: plan + specs + Figma
   Output: Lark Sheet / Google Sheets URL + local .xlsx backup

4. Execute    =>  Run tests (manual)
   Update status on Sheets (PASSED / FAILED / NOT START / CANCEL)

5. /fix       =>  Fix TCs / analyze bugs / add regression TCs
   Input: Sheets link + change description or bug report
   Output: Updated Sheets + bug report (.md)

6. /est-sp    =>  Estimate Story Points (or re-estimate after scope changes)
   Input: plan path or feature description
   Output: SP estimation + updated plan

7. /ask       =>  Ask anytime during the process
   Review coverage, predict bugs, strategy consulting, quality review
```

### Product Ops Workflow

```
Before Development:
  /risk           =>  Assess risks for upcoming feature/release
                      Output: Risk matrix + mitigation plan + test strategy

Before Release:
  /release-check  =>  Evaluate release readiness (GO / CONDITIONAL GO / NO-GO)
                      Input: test results + known bugs + release scope
                      Output: Quality gates verdict + confidence score

During Sprint / Ongoing:
  /triage         =>  Prioritize bugs/incidents with RICE scoring
                      Input: bug list (Sheets/file/paste)
                      Output: Ranked list + impact analysis + SLA deadlines

  /sla            =>  Evaluate SLA compliance for the period
                      Input: ticket data (Sheets/file)
                      Output: SLA report + breach analysis + trend

End of Sprint / Monthly:
  /health         =>  Generate Product Health Scorecard
                      Input: bug data + test results + customer feedback
                      Output: Scorecard with quality/customer/testing/velocity metrics
```

---

## Multi-Agent Architecture

QA Ops Suite uses a multi-agent architecture for optimal performance on large features. Maximum **5 concurrent agents** during execution.

### Overall Flow

```
+------------------- DATA COLLECTION (parallel) -------------------+
|                                                                    |
|  Agent Docs Reader ------=> {prefix}-docs-summary.md               |
|                     ------=> {prefix}-links-tracking.md             |
|                                  |                                  |
|                                  v                                  |
|  Agent Link Reader #1-N --=> Read embedded Lark/URL links           |
|  Agent Figma Reader #1-N -=> {prefix}-figma-summary-{batch}.md     |
|                              (5 screens per agent)                  |
|                                                                    |
+---------------------- WAIT FOR ALL TO COMPLETE -------------------+
                              |
                              v
+-------------- CONFLICT DETECTION (main agent) -------------------+
|  Compare docs-summary vs figma-summary                             |
|  Conflicts found? => Handle per command:                           |
|    /analyze: Auto-trigger Agent Team debate                        |
|    /plan-tc, /cook, /fix: Ask user to choose resolution            |
|  No conflicts? => Continue normally                                |
+------------------------------------------------------------------+
                              |
                              v
+-------------- PLANNING (main agent) -----------------------------+
|  Read all summaries => Analyze => Create overview plan             |
|  Split into INDEPENDENT phases                                     |
|  Each phase = separate feature group with TC_ID range              |
+------------------------------------------------------------------+
                              |
                              v
+-------------- EXECUTION (parallel, max 5 agents) ----------------+
|  Agent Phase 1 ----=> {prefix}-phase-1.xlsx                        |
|  Agent Phase 2 ----=> {prefix}-phase-2.xlsx                        |
|  Agent Phase N ----=> {prefix}-phase-N.xlsx                        |
+---------------------- WAIT FOR ALL TO COMPLETE -------------------+
                              |
                              v
+-------------- MERGE & UPLOAD (main agent) ------------------------+
|  Merge all xlsx => 1 workbook => save {prefix}-final.xlsx          |
|  Upload to Lark Drive or Google Sheets => return 1 URL             |
+------------------------------------------------------------------+
```

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Phase Independence** | Each phase is fully independent -- no data overlap with other phases |
| **Max 5 Concurrent** | Maximum 5 agents running simultaneously during execution |
| **Embedded Links Parallel** | Links found in docs are read by sub-agents in parallel |
| **Sync Before Next** | Planning only starts when ALL data collection agents complete |
| **Conflict Resolution** | Specs vs Figma conflicts are detected and resolved before execution |
| **Merge Before Upload** | Individual phases are NOT pushed -- only the merged final file |
| **Final .xlsx Required** | A merged `{prefix}-final.xlsx` is always saved locally as backup |
| **TC_ID Reset** | Each sheet starts from TC_001 (NOT continuous across sheets) |

---

## Output Format

### Test cases on Sheets

Each spreadsheet file includes:

| Area | Content |
|------|---------|
| Header (Rows 1-7) | Link DOC, Link Figma, Created by, Date, Time Est, Status summary (COUNTIF formulas), Story Point |
| Column headers (Rows 8-9) | TC ID, Description, Pre-condition, Steps, Expected Result, Status, BugID, Test Type... |
| Data rows | Test cases grouped by section, with color formatting and section headers |
| Status dropdown | Data validation: `PASSED`, `FAILED`, `NOT START`, `CANCEL` |

Local `.xlsx` file is saved in `results/` as backup, and uploaded to **Lark Drive** (auto-converted to editable Lark Sheet) or **Google Sheets** (based on `.env` config) with a returned URL.

### Test plan

Markdown (`.md`) file saved in `plans/<feature_name>/`, including: scope, phases, TC matrix, SP estimation, impact analysis, and time estimation.

### Analysis report

Markdown (`.md`) file saved in `results/<feature_name>/`, including: metadata, summary, QC analysis, document quality assessment, questions for PO/Design, and test plan suggestions.

### Bug analysis report

Markdown (`.md`) file saved in `results/<feature_name>/`, including: root cause analysis, affected areas, regression test cases, and fix verification plan.

---

## Tips for Effective Prompts

1. **Always include Figma link with `&m=dev`** -- Claude reads specs directly from the design in dev mode
2. **Provide full context** -- Feature description + specs + Figma = highest quality test cases
3. **Specify scope** -- If only testing part of a feature, state so explicitly
4. **Mention special edge cases** -- If you know unusual business rules, include them in the prompt
5. **Specify platform** -- If testing separately for iOS/Android/Web, mention it
6. **Use the recommended workflow** -- `/analyze` => `/plan-tc` => `/cook` produces the best results
7. **Multiple link types supported** -- Lark wiki, Google Docs, web URLs, or local files
8. **Specify language** -- Default is Vietnamese. For English output, add: `language: English`
9. **Update existing TCs** -- Use `/fix` + paste the Sheets URL to edit directly on Drive
10. **Clear context between commands** -- Run `/clear` or `/compact` between heavy commands (e.g., after `/plan-tc` before `/cook`) to free up context window

---

## Directory Structure

```
QAOpsSuite/
+-- CLAUDE.md                    # Configuration & rules for Claude Code
+-- README.md                    # This file (English)
+-- README-vi.md                 # Vietnamese version
+-- .mcp.json                    # MCP servers config (Figma + Lark)
+-- .env.example                 # Template environment file
+-- .env                         # Actual credentials (DO NOT commit)
|
+-- configs/                     # Infrastructure & setup scripts
|   +-- tc_template.py           # Test case template (xlsx creation, formatting, sanitize)
|   +-- env_loader.py            # Environment variable helper (Python runtime)
|   +-- setup-oauth.py           # Google OAuth setup script
|   +-- setup-lark-oauth.py      # Lark OAuth setup script
|   +-- lark_api.py              # Python-first Lark API wrapper (auto token refresh) — PREFERRED
|   +-- lark_auth.py             # Lark OAuth + token refresh helper
|   +-- lark-upload.py           # Lark Drive smart upload (auto-import xlsx=>Sheet, docx=>Doc)
|   +-- lark_bitable.py          # Lark Bitable helper (attachment upload, board config)
|   +-- lark_bug_cache.py        # Fuzzy lookup helper for bug board options (Dev PIC, Sprint, etc.)
|   +-- lark_bug_board_cache.json# Cached bug board options (Dev PIC, Sprint, Platform, Tính năng, Version...)
|   +-- sitemap_helper.py        # Sitemap read/write/enrich/validate helper
|   +-- video_frames.py          # Extract frames from bug videos (for /bug)
|   +-- google-oauth-token.json  # Google token (DO NOT commit)
|   +-- lark-oauth-token.json    # Lark token (DO NOT commit)
|
+-- scripts/                     # Utility scripts
+-- docs/                        # Input specs/requirements documents
+-- example/                     # Screenshots, prompt examples, sample files
+-- results/                     # Output from /analyze, /cook, /fix
+-- plans/                       # Output from /plan-tc
|
+-- .claude/
    +-- rules/                   # Layer 0 - Always loaded rules (split by topic)
    |   +-- core.md              # Language, ID, status, sanitize, time tracking
    |   +-- test-quality.md      # Steps quality, expected results, coverage
    |   +-- output-format.md     # xlsx workflow, Google Sheets, formatting
    |   +-- orchestration.md     # Multi-agent, phases, merge, sync
    |   +-- story-point.md       # Story Point estimation rules, role multiplier
    |   +-- sitemap.md           # Sitemap read/enrich/impact rules
    |   +-- conflict-resolution.md  # Docs vs Figma conflict handling
    |   +-- product-ops.md       # SLA, health metrics, release gates, RICE, risk matrix
    |
    +-- docs/                    # Layer 1 - On-demand reference
    |   +-- output-types.md      # TC vs Checklist vs Regression
    |   +-- lark-integration.md  # Lark MCP guide + link detection + Bitable integration
    |   +-- lark-scopes-reference.md  # Lark scopes reference (tenant + user)
    |   +-- figma-workflow.md    # Figma multi-agent, tracking
    |   +-- setup-config.md      # Setup/.env/.mcp.json troubleshooting flow
    |   +-- severity-priority-framework.md  # Severity & Priority normalization framework
    |   +-- team-kpi.md          # QC team KPI tracking guide
    |
    +-- boards.md                # Registry of bug/task/test boards (multi-board setup)
    +-- .board-state.json        # Daily active-board confirmation state (gitignored)
    |
    +-- commands/                # Slash command definitions
    |   +-- analyze.md, plan-tc.md, cook.md, fix.md, ask.md, est-sp.md  (QA/QC core)
    |   +-- log-bug.md, bug.md, check-duplicate-bug.md, explain-bug.md  (Bug tracking)
    |   +-- search-doc.md, update-board.md, help.md                     (Search/Config)
    |   +-- sla.md, health.md, release-check.md, triage.md, risk.md     (Product Ops)
    |
    +-- agents/                  # Sub-agent definitions
    |   +-- docs-reader.md       # Document reader (Lark/URL/local + comments + links)
    |   +-- figma-reader.md      # Figma design reader (multi-screen batching)
    |   +-- link-reader.md       # Embedded link reader
    |   +-- wiki-searcher.md     # Lark Wiki search (1 keyword, title + content)
    |   +-- wiki-reader.md       # Lark Wiki content reader (1 doc full content)
    |   +-- designer-review.md   # Conflict resolution - Designer perspective
    |   +-- po-review.md         # Conflict resolution - PO perspective
    |   +-- qa-arbitrator.md     # Conflict resolution - QA final decision
    |
    +-- templates/
    |   +-- testcase-template.md # Python template for spreadsheet creation
    |
    +-- sitemap.yaml             # Navigation tree, feature registry, impact map
```

---

## Extensible Architecture

QA Ops Suite is designed as a comprehensive QA + Product Ops platform. The architecture supports two major capability groups:

**QA / QC capabilities**:

- **Test case generation** -- Production-ready TCs with multi-agent parallel execution
- **Requirement analysis** -- Deep analysis of specs from multiple sources (Lark, Figma, local files) with conflict detection
- **Impact analysis** -- Sitemap-driven impact mapping to understand how changes in one feature affect others
- **Conflict resolution** -- Multi-agent debate system (Designer + PO + QA perspectives) for resolving specification conflicts

**Product Ops capabilities**:

- **SLA tracking** -- Evaluate SLA compliance with percentile analysis, breach tracking, and trend comparison
- **Product health** -- Scorecard with quality, customer, testing, and velocity metrics
- **Release management** -- Quality gate-based release readiness assessment (GO / NO-GO)
- **Bug triage** -- RICE-based prioritization with cross-feature impact analysis from sitemap
- **Risk assessment** -- Risk matrix with mitigation strategies and test strategy recommendations

**Extensibility**:

- **Custom agents** -- New sub-agents can be added to `.claude/agents/` for specialized tasks
- **Custom commands** -- New slash commands can be defined in `.claude/commands/` to extend capabilities
- **Configurable rules** -- Layered rule system (`.claude/rules/`) allows fine-tuning behavior per command without modifying core logic

The layered configuration (rules loaded per command, on-demand docs, auto-enriching sitemap) means QA Ops Suite can adapt to new workflows as team needs evolve.

---

## Troubleshooting

### Token expired

**macOS:**
```bash
python3 configs/setup-oauth.py
```

**Windows:**
```powershell
python configs/setup-oauth.py
```

Then restart Claude Code.

### MCP server not working

Check MCP servers:
```bash
claude mcp list
```

If you don't see `figma` or `lark-mcp`, check:
- `.mcp.json` exists in the project root directory
- Node.js and npx are installed: `node -v && npx -v`

### Google Sheets upload fails

QA Ops Suite uses Python + Google APIs directly (not MCP). Check:
- `.env` has been created (contains `GOOGLE_OAUTH_REFRESH_TOKEN` and `GOOGLE_DRIVE_FOLDER_ID`)
- Python dependencies are installed: `pip3 list | grep google` (macOS) or `pip list | findstr google` (Windows)
- Re-run OAuth setup if token expired: `python3 configs/setup-oauth.py`

### Lark Drive upload fails

- Check that `LARK_DRIVE_FOLDER_ID` is set in `.env`
- First upload requires browser-based Lark OAuth -- allow the popup
- If token expired, the script auto-opens browser for re-authentication
- If Lark fails, upload automatically falls back to Google Sheets

### Lark Bitable not working

- Check that `LARK_BUG_BASE_NAME`, `LARK_BUG_BASE_ID`, and `LARK_BUG_TABLE_ID` are set in `.env`
- Verify with: `python3 configs/lark_bitable.py status`
- If token lacks Bitable scopes: `rm configs/lark-oauth-token.json` then re-auth via any upload
- Ensure user has access to the Bitable board on Lark

### Figma MCP not connecting

- Make sure you logged into Figma MCP when prompted
- Check Figma link format: `figma.com/design/<fileKey>/<fileName>?node-id=<nodeId>&m=dev`
- If permission error: check file access on Figma (must have view permission)

### Lark MCP cannot read documents

- First time: authenticate your Lark account when prompted
- Ensure Lark link format is correct: `https://sobanhang.sg.larksuite.com/wiki/...`
- Check document access permissions on Lark

### Claude Code does not recognize slash commands

Make sure you are running Claude Code **inside the QAOpsSuite directory** (where `CLAUDE.md` and `.claude/commands/` are located).

### Windows-specific issues

- If `python3` is not recognized, use `python` instead
- If `pip3` is not recognized, use `pip` instead
- If scripts fail with encoding errors, set: `$env:PYTHONIOENCODING = "utf-8"` in PowerShell
- Use PowerShell (not CMD) for best compatibility

---

## Security Notes

The following files contain sensitive information -- **DO NOT commit to git** (already in `.gitignore`):

```
.env                             # Contains refresh tokens and folder IDs
configs/google-oauth-token.json  # Google OAuth token (created by setup-oauth.py)
configs/lark-oauth-token.json    # Lark OAuth token (created by lark-upload.py on first upload)
```

### OAuth scope: `drive.file` (minimal permission)

The app only requests the `drive.file` scope, which means:
- It can **only** access files it created -- not your existing Drive files
- No broad access to your Google Drive or all Google Sheets
- This single scope covers all needs: create, read, write, format, and organize spreadsheets
- Your existing Drive files remain completely untouched

### Local-first approach

- All test case files are saved locally as `.xlsx` before any upload
- If all cloud uploads fail, the local backup in `results/` is always available
- No data is sent to third-party services beyond Google/Lark APIs for file management

---

*Created by: QA Ops Suite*
