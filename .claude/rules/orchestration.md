# Multi-Agent Orchestration Rules

Rules về phân chia phases, parallel agents, merge & upload.
**Đọc khi**: `/plan-tc`, `/cook`, `/fix`

---

## 1. General Rules

- Maximum **5 concurrent agents** at any time
- Only spawn new agent when **no data conflict** with running agents
- **Mandatory sync**: Dependent tasks MUST WAIT for dependencies to complete
- Agents only work within their assigned scope, DO NOT expand scope
- **Sub-agent code rule**: All create_*.py scripts MUST `import` from `configs/tc_template.py`. NEVER copy/redefine `TIME_EST_FORMULA`, `sanitize_text`, `sanitize_tc`, or other template functions inline. This is the #1 cause of Vietnamese diacritics being lost in output files.
- **Sub-agent prompt MUST include**: When spawning any agent that writes create_*.py scripts, include this instruction:
  > "IMPORT from configs/tc_template.py. DO NOT copy or redefine TIME_EST_FORMULA, sanitize_text, sanitize_tc, save_xlsx_local, or any template constant/function. Rewriting from memory causes diacritics loss."

## 2. Phase Independence (MOST IMPORTANT)

- Each phase MUST be a completely independent section/feature
- When splitting phases: ensure **no data overlap**, each phase can run in parallel
- When merging results: NO data conflicts, NO missing/extra data
- Each phase has its own TC_ID range (e.g., Phase 1: TC_001-TC_025, Phase 2: TC_026-TC_050)
- **When merging into 1 sheet**: TC_ID numbered sequentially throughout (no reset between sections)
- **When separating into sheets**: TC_ID reset per sheet (TC_001 for each new sheet)
- Small features can be grouped into 1 phase, but that phase must still be independent from others

## 3. Overall Flow

```
┌─────────────────── DATA COLLECTION (parallel) ───────────────────┐
│                                                                    │
│  Agent Docs Reader ─────=> {prefix}-docs-summary.md                │
│  Agent Figma #1-N ──────=> {prefix}-figma-summary-{batch}.md       │
│                                                                    │
└───────────────────── WAIT FOR ALL TO COMPLETE ───────────────────┘
                              │
                              ▼
┌──────────── CONFLICT DETECTION (main agent) ─────────────────────┐
│  So sánh docs-summary vs figma-summary                             │
│  Có xung đột? => Kích hoạt Conflict Resolution Team               │
│  Không xung đột? => Tiếp tục flow bình thường                     │
│  (Chi tiết: xem conflict-resolution.md)                            │
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
              Có xung đột          Không xung đột
                    │                    │
             ┌──────┴──────┐             │
             │             │             │
        /analyze      /plan-tc,/cook,/fix│
             │             │             │
             ▼             ▼             │
        AUTO-TRIGGER   DỪNG LẠI         │
        Agent Team     Hỏi user         │
             │         chọn cách xử lý  │
             │             │             │
             │      ┌──────┴──────┐      │
             │   User chọn    User chọn  │
             │   (a)(b)(c)    (d) Team   │
             │   Áp dụng ngay    │       │
             │        │          │       │
             │        │          │       │
             ▼        │          ▼       │
┌──── CONFLICT RESOLUTION TEAM ────┐    │
│  Round 1 (parallel):             │    │
│  ├─ Trinh (Sr. Designer)        │    │
│  └─ Hiếu (Sr. PO)              │    │
│  Round 2 (sequential):          │    │
│  └─ Châu (Sr. QA) => QUYẾT     │    │
│     ĐỊNH CUỐI CÙNG              │    │
│  Hiển thị chi tiết tranh luận   │    │
│  => {prefix}-conflict-           │    │
│     resolution.md                │    │
└──────────────────────────────────┘    │
                    │         │          │
                    └─────────┴──────────┘
                              │
                              ▼
┌─────────────── PLANNING / ANALYSIS (main agent) ─────────────────┐
│  Read all summary files + conflict resolution (if exists)          │
│  Analyze => Create overall plan                                    │
│  Split into INDEPENDENT phases (each phase = separate section)     │
│  Write plan + phase-tracking                                       │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────── EXECUTION (parallel, max 5 agents) ──────────────┐
│  Agent Phase 1-N ───=> {prefix}-phase-{N}.xlsx                     │
│  (Agent that finishes first => writes results immediately)         │
└───────────────────── WAIT FOR ALL TO COMPLETE ───────────────────┘
                              │
                              ▼
┌─────────────────── MERGE & UPLOAD (main agent) ──────────────────┐
│  Merge all xlsx => 1 workbook => Push to Google Sheets => 1 URL   │
└──────────────────────────────────────────────────────────────────┘
```

## 4. Data Collection Phase (Docs + Figma)

- **1 Docs Reader agent** (if document links provided)
- **N Figma Reader agents** (each reads exactly **5 screens**, NOT 7):
  - Formula: `N = ceil(total_screens / 5)`, last agent may read < 5 (remainder)
  - <= 7 screens => 1 agent reads all (only case where 1 agent reads > 5)
  - 8 screens => 2 agents (5 + 3)
  - 13 screens => 3 agents (5 + 5 + 3)
  - 20 screens => 4 agents (5 + 5 + 5 + 5)
  - If N Figma agents > 4 => split into 2 rounds (to keep total agents <= 5)
  - Each agent writes to separate file: `{prefix}-figma-summary-{batch}.md`
- **Sync**: Plan-TC/Cook/Fix ONLY STARTS when **ALL** docs + figma agents complete
- If 1 agent fails => fallback to direct reading, DO NOT start plan without data

## 5. Conflict Detection & Resolution Phase

- Chạy SAU data collection, TRƯỚC planning
- **Chỉ kích hoạt** khi có CẢ docs-summary VÀ figma-summary VÀ phát hiện xung đột
- **Chi tiết đầy đủ**: Đọc `.claude/rules/conflict-resolution.md`
- **Hành vi khác nhau theo command**:
  - `/analyze`: Tự động spawn Agent Team tranh luận, hiển thị chi tiết cho user
  - `/plan-tc`, `/cook`, `/fix`: **DỪNG LẠI** hỏi user chọn cách xử lý (theo Docs / Figma / từng cái / mở Agent Team)
- Agents trong phase này (max 3) **KHÔNG tính vào quota 5 agents** của execution phase
- Kết quả: user decision hoặc `{prefix}-conflict-resolution.md` (nếu Agent Team chạy)
- Nếu không có xung đột => bỏ qua phase này, tiếp tục bình thường

## 6. Plan Phase

- Only starts when ALL documents are available (docs-summary + figma-summary)
- If conflicts detected: apply user's decision OR read `{prefix}-conflict-resolution.md` (if Agent Team was triggered)
- Analyze requirements => split into independent phases => create overview plan
- Each phase in plan must describe: scope, TC_ID range, dependencies (if any), estimated TCs
- If conflicts were resolved: add "Conflict Resolution Summary" section in plan

## 7. Execution Phase (Cook/Fix)

- Read plan => determine number of phases => create N agents (max 5 concurrent)
- Each agent creates a separate xlsx file (e.g., `{prefix}-phase-1.xlsx`, `{prefix}-phase-2.xlsx`)
- Agent that finishes first => writes result to plan tracking immediately, does NOT wait for others
- Results arriving out of order => still record in plan, merge will reorder
- **DO NOT push individual phases to Google Sheets** - only push AFTER merging all phases

## 8. Merge & Upload (REQUIRED)

- Only execute when **ALL phases** are complete (status = DONE)
- Merge all xlsx files into 1 combined file:
  - **Prefer merging into 1 sheet**: When phases belong to the same feature/module => merge all into **1 single sheet**, split into **sections** (use section header rows as separators)
    - TC_ID numbered **sequentially** throughout the sheet (TC_001, TC_002... no reset)
    - Each section has 1 header row marking the section name (bold, merged cells)
  - **Only create a new sheet** when the plan has clearly **independent tasks/modules** (e.g., Login module vs Payment module)
    - When separating sheets: TC_ID RESET per sheet, each sheet has its own header (Rows 1-6) with separate COUNTIF formulas
    - Sheet name = feature/module name (short)
- **REQUIRED FINAL .xlsx FILE**: After merging, MUST save a combined `.xlsx` file at `results/<feature_name>/<prefix>-final.xlsx`. DO NOT skip this step.
- After merge => push to Drive theo **Upload Priority** (xem `output-format.md` section "Upload Priority")
  - `LARK_DRIVE_FOLDER_ID` set => upload Lark Drive (via `configs/lark-upload.py`, auto re-auth)
  - Lark fail hoặc không set => fallback Google Sheets (via `create_multi_sheet_tc_spreadsheet()`)
  - Cả 2 không set => skip upload, trả file local
- Return 1 single URL to user (Lark hoặc Google)

## 9. Agent Spawn Rules

```
Spawn OK when:
  - Total current agents < 5
  - Task has no data conflict with any running agent
  - All task dependencies are satisfied

Spawn NOT OK when:
  - Already at max 5 agents
  - Task needs to read/write same data as another agent
  - Dependencies not yet complete (e.g., plan has no data => don't start)
  - Previous phase has side effects on next phase (next phase must wait)
```

## 10. Synchronization Rules

```
docs-reader DONE ──────+
                       +──=> Conflict Detection (main agent)
figma-reader DONE ─────+
                              │
                    ┌─────────┴──────────┐
                    │                    │
              Có xung đột          Không xung đột
                    │                    │
             ┌──────┴──────┐             │
        /analyze      /plan-tc,/cook,/fix│
             │             │             │
             ▼             ▼             │
        AUTO Agent     DỪNG LẠI         │
        Team           Hỏi user =>      │
        Trinh+Hiếu     user chọn cách   │
        =>Châu         xử lý            │
             │             │             │
             └──────┬──────┘             │
                    └────────┬───────────┘
                              │
                              ▼
                         Plan starts

plan DONE ──=> Cook/Fix starts

phase-1 DONE ──+
phase-2 DONE ──+──=> Merge + Upload
phase-N DONE ──+
```

---

## 11. Estimation & Phase Splitting

### Estimation Thresholds (guideline)

| Task | Safe threshold / phase | When to split into phases |
|------|------------------------|--------------------------|
| `/plan-tc` | 1 plan for <= 5 modules | > 5 modules or > 7 Figma screens |
| `/cook` | <= 40-50 test cases | > 50 TCs or > 5 modules |
| `/fix` | <= 30-40 test cases to update | > 40 TCs to modify or > 3 files |

### Phase Split Notification Format

When splitting into phases is needed, notify the user **BEFORE** starting:

```
Workload Estimate:
- Input: X modules, Y Figma screens, Z requirements
- Expected output: ~N test cases
- Proposal: Split into P phases (parallel, independent)

Phase 1 (Section "Part A, B"): ~25 TCs, TC_001-TC_025
Phase 2 (Section "Part C, D"): ~20 TCs, TC_026-TC_045 (continues TC_ID)
Phase 3 (Section "Part E"):    ~15 TCs, TC_046-TC_060 (continues TC_ID)

=> Merge into 1 sheet, split by section. If modules are independent => separate sheets, TC_ID reset.
All phases are fully independent, will run in parallel and merge at the end.
Continue?
```

## 12. Phase Progress Tracking

Save a `<prefix>-phase-tracking.md` file in the same output folder:

```markdown
# Phase Tracking

## Feature: <feature name>
Task: /cook (or /plan-tc, /fix)
Total phases: P
Created: <date>

| Phase | Sheet Name | Scope | TC_ID Range | Status | Output File |
|-------|-----------|-------|-------------|--------|-------------|
| 1 | Module A, B | ~25 TCs | TC_001-TC_025 | DONE | {prefix}-phase-1.xlsx |
| 2 | Module C, D | ~20 TCs | TC_001-TC_020 | DONE | {prefix}-phase-2.xlsx |
| 3 | Module E | ~15 TCs | TC_001-TC_015 | IN_PROGRESS | - |

## Merge Status: PENDING
## Google Sheets URL: (after merge + upload)
```

## 13. Plan/Phase Completion Markers (MANDATORY)

Each completed plan/phase **MUST be clearly marked at the BEGINNING and END** of the plan file.

**Marker at the beginning of the plan file:**
```markdown
<!-- PLAN STATUS
Total Phases: X
Phase 1: COMPLETED (Sheet "Module A, B") - TC_001-TC_025, file: results/feature/xxx-phase-1.xlsx
Phase 2: COMPLETED (Sheet "Module C, D") - TC_001-TC_020, file: results/feature/xxx-phase-2.xlsx
Phase 3: PENDING (Sheet "Module E") - TC_001-TC_015
MERGE: PENDING
NEXT ACTION: Phase 3 execution => then merge all
-->
```

**Marker at the end of each phase section:**
```markdown
<!-- PHASE 1 COMPLETED - TC_001-TC_025, file: results/feature/xxx-phase-1.xlsx -->
```

**Process when `/cook` or `/fix` reads a plan:**
1. Read the `<!-- PLAN STATUS -->` block at the top => identify ALL PENDING phases
2. Spawn N agents in parallel (max 5) for N PENDING phases
3. Each agent that completes => update markers in the plan file
4. All phases DONE => merge + upload
