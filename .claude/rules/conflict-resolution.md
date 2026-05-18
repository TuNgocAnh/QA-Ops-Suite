# Conflict Resolution Rules

Rules for detecting and handling conflicts between documentation sources (Docs vs Figma).
**Read when**: `/cook`, `/plan-tc`, `/fix`, `/analyze` — AFTER data collection completes, WHEN both Docs and Figma are available

---

## 1. Activation Conditions & Command-Specific Behavior

### Conflict detection conditions (shared across all commands):
- Both `{prefix}-docs-summary.md` AND `{prefix}-figma-summary.md` (or figma-summary-{batch}.md) exist
- Main agent detects **>= 1 conflict** between the 2 sources
- Conflicts are **non-visual** (not just color, font, or spacing differences)

### Different behavior per command (IMPORTANT):

| Command | Conflict Detection | Behavior |
|---------|-------------------|----------|
| `/analyze` | Automatic | **AUTO-TRIGGER** Agent Team debate. Display detailed debate content for user to read |
| `/plan-tc`, `/cook`, `/fix` | Automatic | **STOP** — display conflict list, ask user to choose resolution method. **DO NOT auto-spawn Agent Team** |

### For `/plan-tc`, `/cook`, `/fix` — WAIT FOR USER DECISION:

When conflicts are detected, display to user:

```
Warning: Detected {N} conflicts between Docs and Figma:

1. [FIELD_MISMATCH] Number of columns in list table
   - Docs: Table has 5 columns: Code, Name, Created Date, Creator, Status
   - Figma: Table has only 4 columns (missing "Creator")

2. [VALIDATION_MISMATCH] Character limit for Name field
   - Docs: Allows max 50 characters
   - Figma: Field appears short, estimated ~20 characters
...

How would you like to resolve?
  (a) Follow Docs for all — prioritize requirement documents
  (b) Follow Figma for all — prioritize current design
  (c) I'll decide per conflict — list each one for me to choose
  (d) Open Agent Team debate — let Trinh (Design), Hieu (PO), Chau (QA) discuss and recommend
```

- If user chooses (a), (b), (c) => apply immediately, DO NOT spawn agent team
- If user chooses (d) => spawn Agent Team (same flow as `/analyze`)
- **REASON**: When creating documents (TCs, plans...), the actual context may differ. The user knows best which source to follow. Auto-triggered Agent Team debate may produce results that don't fit the current situation.

### For `/analyze` — AUTO-TRIGGER + DISPLAY DETAILS:

Agent Team debate is auto-triggered because `/analyze` is **analysis** — debate and reasoning produce better analysis results.

**MANDATORY VERBOSE OUTPUT**:
- After each agent completes, MUST display a summary of their review content for user to read
- User needs to see: what Trinh thinks, what Hieu thinks, how Chau decides
- Display format: see Section 5.1

**DO NOT activate when**:
- Only 1 source available (Docs only OR Figma only)
- No conflicts detected
- Conflicts are visual-only (color, font, spacing) that docs don't mention

=> When not activated: continue normal flow.

---

## 2. Conflict Types to Detect

| Type | Code | Description | Example |
|------|------|------------|---------|
| Field/column mismatch | `FIELD_MISMATCH` | Different field count or names | Docs: 5 table columns, Figma: 4 columns |
| Flow mismatch | `FLOW_MISMATCH` | Different operation/navigation flows | Docs: 3-step creation, Figma: 2 steps |
| Validation mismatch | `VALIDATION_MISMATCH` | Different validation rules | Docs: max 50 chars, Figma: field ~20 chars |
| State mismatch | `STATE_MISMATCH` | Different states/conditions | Docs: 4 statuses, Figma: 3 statuses |
| Data format mismatch | `DATA_FORMAT` | Different display formats | Docs: DD/MM/YYYY, Figma: MM/DD/YYYY |
| Scope mismatch | `SCOPE_MISMATCH` | Feature exists in 1 source but missing in other | Docs has tab C, Figma only has A + B |
| Behavior mismatch | `BEHAVIOR_MISMATCH` | Different behavioral responses | Docs: popup confirm, Figma: inline confirm |

**NOT a conflict** (skip):
- Different color/hex code (visual only)
- Different font size, font weight (visual only)
- Different spacing/padding (visual only)
- Figma has extra decorative elements not mentioned in docs

---

## 3. Conflict Detection Process

After reading docs-summary + figma-summary, main agent performs:

### Step 1: Structured comparison

Compare corresponding sections:

| Docs Section | Figma Section | What to compare |
|-------------|--------------|----------------|
| Functional Requirements | UI Elements | Field count, field names, input types |
| Business Rules | States & Interactions | Conditions, states, behaviors |
| Validation Rules | UI Elements (constraints) | Max length, format, required/optional |
| Data Flow | Data Display | Display format, ordering, sort/filter |
| Integration Points | Screen navigation | API calls, transitions |

### Step 2: Create Conflict List

Standard format (used by all 3 agents):

```markdown
## Conflicts Detected: {N}

### Conflict #1
- **Type**: FIELD_MISMATCH
- **Title**: Number of columns in list table
- **Docs says**: Table has 5 columns: Code, Name, Created Date, Creator, Status
- **Figma shows**: Table has only 4 columns: Code, Name, Created Date, Status (missing "Creator")
- **Impact**: Affects TC coverage — need to decide whether to test "Creator" column

### Conflict #2
- **Type**: VALIDATION_MISMATCH
- **Title**: Character limit for Name field
- **Docs says**: Allows max 50 characters
- **Figma shows**: Field appears short, estimated ~20 characters
- **Impact**: TC validation will differ depending on which source is correct
```

### Step 3: Handle per command

**If `/analyze`**: Display conflict list + auto-spawn Agent Team (Section 5)

**If `/plan-tc`, `/cook`, `/fix`**: Display conflict list + ask user to choose resolution method (Section 1). WAIT for user confirmation before continuing.

---

## 4. Conflict Resolution Flow

```
docs-summary + figma-summary READY
         |
         v
   Main Agent: Compare 2 sources (Step 1-2)
   Create conflict list
         |
    +----+----+
    |         |
 0 conflicts  >= 1 conflict
    |         |
    v         v
 Continue    Branch by command
 normal           |
         +--------+--------+
         |                 |
    /analyze          /plan-tc, /cook, /fix
         |                 |
         v                 v
   AUTO-TRIGGER       STOP
   Agent Team         Display conflicts
         |            Ask user to choose:
         |            (a) Follow Docs
         |            (b) Follow Figma
         |            (c) Decide per conflict
         |            (d) Open Agent Team
         |                 |
         |          +------+------+
         |          |             |
         |     (a)(b)(c)        (d)
         |     Apply now        |
         |     No agent team    |
         |          |           |
         v          |           v
   +----------------------------------+
   |  ROUND 1 (PARALLEL):            |
   |  +- Trinh (Sr. Designer)        |
   |  |  => {prefix}-designer-       |
   |  |     review.md                |
   |  +- Hieu (Sr. PO)              |
   |     => {prefix}-po-review.md    |
   |                                 |
   |  DISPLAY reviews to user        |
   |  WAIT for both to complete      |
   |                                 |
   |  ROUND 2 (SEQUENTIAL):         |
   |  +- Chau (Sr. QA)              |
   |     Read both reviews           |
   |     => {prefix}-conflict-       |
   |        resolution.md            |
   |                                 |
   |  DISPLAY resolution to user     |
   +----------------------------------+
          |           |
          v           v
   Main agent applies decisions
```

---

## 5. Spawn Team Agents

> **ONLY RUNS WHEN**: `/analyze` (automatic) OR `/plan-tc`, `/cook`, `/fix` when user chooses option (d)

### 5.1 Display Debate Content (MANDATORY)

After each agent completes, **MUST** display a summary of their content for user to read:

```
=== ROUND 1: Debate ===

Designer: Trinh (Senior Designer) — Review complete:
+------------------------------------------+
| Conflict #1: [title]                     |
| Position: [summary 1-2 sentences]        |
| Recommendation: Follow Figma/Docs/...    |
| Confidence: High/Medium/Low              |
|                                          |
| Conflict #2: [title]                     |
| Position: [summary 1-2 sentences]        |
| Recommendation: ...                      |
+------------------------------------------+

PO: Hieu (Senior PO) — Review complete:
+------------------------------------------+
| Conflict #1: [title]                     |
| Position: [summary 1-2 sentences]        |
| Recommendation: Follow Docs/Figma/...    |
| Confidence: High/Medium/Low              |
|                                          |
| Conflict #2: ...                         |
+------------------------------------------+

=== ROUND 2: Verdict ===

QA: Chau (Senior QA) — Final decision:
+------------------------------------------+
| Conflict #1: [title]                     |
| Trinh: [summary] | Hieu: [summary]      |
| Decision: **Follow Figma/Docs/Compromise |
| Reason: [1-2 sentences]                  |
|                                          |
| Conflict #2: ...                         |
|                                          |
| Summary: X follow Figma, Y follow Docs, |
| Z compromise, W need team review         |
+------------------------------------------+
```

**Reason**: User needs to read and understand the debate process to assess decision quality, not just receive the final result.

### 5.2 Round 1 — Parallel (Designer + PO)

Spawn **2 agents SIMULTANEOUSLY** using Agent tool:

**Agent 1 — Trinh (Senior Designer)**:
```
Agent definition: .claude/agents/designer-review.md
Input:
  - conflicts: [conflict list from Step 2]
  - figma_summary: [content of {prefix}-figma-summary.md]
  - docs_summary: [content of {prefix}-docs-summary.md]
  - output_file: {output_folder}/{prefix}-designer-review.md

Prompt MUST include:
"CRITICAL: All Vietnamese text MUST have diacritics. 'Đăng nhập' NOT 'Dang nhap'."
```

**Agent 2 — Hieu (Senior PO)**:
```
Agent definition: .claude/agents/po-review.md
Input:
  - conflicts: [conflict list from Step 2]
  - docs_summary: [content of {prefix}-docs-summary.md]
  - figma_summary: [content of {prefix}-figma-summary.md]
  - output_file: {output_folder}/{prefix}-po-review.md

Prompt MUST include:
"CRITICAL: All Vietnamese text MUST have diacritics. 'Đăng nhập' NOT 'Dang nhap'."
```

**AFTER Round 1 completes**: Display Trinh + Hieu review content to user (format in Section 5.1)

### 5.3 Round 2 — Sequential (QA Arbitrator)

**WAIT for Round 1 to complete + results displayed**, then spawn:

**Agent 3 — Chau (Senior QA)**:
```
Agent definition: .claude/agents/qa-arbitrator.md
Input:
  - designer_review: [content of {prefix}-designer-review.md]
  - po_review: [content of {prefix}-po-review.md]
  - conflicts: [original conflict list]
  - output_file: {output_folder}/{prefix}-conflict-resolution.md

Prompt MUST include:
"CRITICAL: All Vietnamese text MUST have diacritics. 'Đăng nhập' NOT 'Dang nhap'."
```

**AFTER Round 2 completes**: Display Chau's final decision to user (format in Section 5.1)

### 5.4 Agent Quota
- Conflict Resolution Team: **max 3 agents** (Trinh + Hieu + Chau)
- These agents **DO NOT count toward the 5-agent quota** of the execution phase
- Runs AFTER data collection, BEFORE planning/execution

---

## 6. Using Resolution Results

### Read resolution file
Main agent reads `{prefix}-conflict-resolution.md` and applies:

### In Plan (`/plan-tc`):
- Add "Conflict Resolution Summary" section in plan
- List each conflict + decision (user-chosen or Agent Team decided)
- Mark decision source: `[User choice]` or `[Agent Team - Chau's decision]`
- If flagged "Needs team review" => note clearly in plan

### In Test Cases (`/cook`):
- TCs related to resolved conflicts => add in Precondition:
  - `[Resolved: Follow Figma]` or `[Resolved: Follow Docs]` or `[Resolved: Compromise]`
- TCs with "Pending Review" flag => add `[Pending Review - needs PO/Designer confirmation]`
- Write TCs based on **user's chosen decision** or **Chau's decision** (if user chose Agent Team)

### In Fix (`/fix`):
- Same as `/cook` — apply user's chosen decision to TCs being updated

### In Analysis (`/analyze`):
- Add "Docs vs Figma Conflicts" section with decision summary table
- Highlight conflicts needing real team review
- **Mandatory**: include detailed arguments from each agent (not just final results)

---

## 7. Fallback Rules

| Scenario | Resolution |
|----------|-----------|
| Designer agent fails | Main agent uses default rule: Follow Docs |
| PO agent fails | Main agent uses default rule: Follow Docs |
| QA arbitrator fails | Main agent decides based on available designer + PO reviews |
| All 3 fail | Fallback to old rule: Follow Docs (section 6.3 test-quality.md) |
| Too many conflicts (> 10) | Split into 2 batches, each batch spawns separate team |

---

## 8. Output Files Summary

After Conflict Resolution completes, output folder will contain:

```
{output_folder}/
├── {prefix}-docs-summary.md          (from data collection)
├── {prefix}-figma-summary.md          (from data collection)
├── {prefix}-designer-review.md        (NEW - Trinh's review)
├── {prefix}-po-review.md             (NEW - Hieu's review)
└── {prefix}-conflict-resolution.md    (NEW - Chau's final decision)
```

All files are retained for traceability — to know WHY decisions were made.
