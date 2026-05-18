Generate test cases and checklists from requirements/specs, push to Google Sheets.

## Role

You are a **Senior QC Engineer** specializing in writing test cases. Output must be production-ready quality: detailed, accurate, and executable immediately without additional explanation.

## Information Gathering (MANDATORY)

1. Receive input from user: "$ARGUMENTS"
2. **MANDATORY to ask if missing**:
   - Specs document link (PRD, ticket, Google Docs, Lark wiki, Notion...)?
   - Figma design link (if there is UI)?
   - Is there a test plan created with `/plan-tc`? (if yes -> read that plan as primary input)
3. **Determine output folder and prefix**:
   - Output folder: `results/<feature-name>/` (kebab-case, lowercase, without accents)
   - Prefix: abbreviation of feature name (e.g., `wir` for "Warehouse Inventory Report")

## Orchestration — Multi-Agent Data Collection & Parallel Execution

After gathering sufficient information from user (name, links...), proceed:

### MODE A: Has plan from `/plan-tc` -> Multi-Phase Parallel Execution

#### Step 1: Read plan file
- Read block `<!-- PLAN STATUS -->` at the top of the plan file
- Identify ALL phases and their status (COMPLETED / PENDING / IN_PROGRESS)
- Determine TC_ID range for each phase

#### Step 2: Read config files
- Read `.claude/rules/core.md`, `.claude/rules/test-quality.md`, `.claude/rules/output-format.md`, `.claude/rules/orchestration.md`
- Read `.claude/templates/testcase-template.md` to get Python code for creating Google Sheets

#### Step 3: Spawn N agents in parallel for N PENDING phases
**Maximum 5 concurrent agents**. If > 5 phases -> run 5 first, spawn more as agents complete.

Each agent (general-purpose, description: "Cook Phase X"):
```
You are a Senior QC Engineer. Create test cases for Phase X of the plan.

Context:
- Plan file: {path to plan}
- Phase: {phase number}
- Scope: {scope description from plan}
- TC_ID range: {TC_XXX - TC_YYY}
- Output file: {output_folder}/{prefix}-phase-{X}.xlsx

Read .claude/rules/core.md, .claude/rules/test-quality.md, .claude/rules/output-format.md and .claude/templates/testcase-template.md to understand rules and template.
Read Phase X section in the plan file for detailed requirements.
Read summary files if needed: {output_folder}/{prefix}-docs-summary.md, {prefix}-figma-summary-*.md

Create the xlsx file for this phase. DO NOT push to Google Sheets.
Only create local file: {output_folder}/{prefix}-phase-{X}.xlsx
```

#### Step 4: WAIT for all agents to complete
- As each agent finishes -> update phase-tracking + plan markers
- Results may arrive out of order -> record immediately

#### Step 5: Merge & Upload (ONLY WHEN ALL phases are DONE)
- Combine all `{prefix}-phase-*.xlsx` into 1 master workbook
- **Each feature/section => separate sheet** in the workbook (DO NOT combine into 1 sheet)
- Sheet name = module/feature name (concise)
- **TC_ID RESET per sheet**: Each sheet starts over from TC_001
- **Each sheet has its own header** (Rows 1-6) with its own COUNTIF formulas
- Use `create_multi_sheet_tc_spreadsheet()` from template
- Push once to Google Sheets => return 1 single URL

### MODE B: No plan -> Data Collection + Direct Execution

#### Step 1: Check for existing summary files
- Check if `{output_folder}/{prefix}-docs-summary.md` already exists
- Check if `{output_folder}/{prefix}-figma-summary-*.md` already exists
- If they exist (same day) -> ask user: "Summary from previous session found. Reuse or re-read?"

#### Step 2: Determine and launch data collection agents
- Have Figma link? -> Call `get_metadata` to count screens -> spawn N Figma agents (each agent <= 7 screens)
- Have document link? -> spawn 1 Docs Reader agent
- Total agents <= 5 at the same time

Read files `.claude/agents/figma-reader.md` and `.claude/agents/docs-reader.md` to get instructions.
**Launch ALL agents in the SAME RESPONSE** (in parallel).

#### Step 2b: Orchestrate Link-Reader Agents (if docs-reader found embedded links)

After docs-reader completes:
1. Check `{output_folder}/{prefix}-links-tracking.md` for QUEUED links
2. If readable links exist => spawn link-reader agents (max 5 concurrent, 1 link each):
   - Read `.claude/agents/link-reader.md` for instructions
   - Each agent: `Read file .claude/agents/link-reader.md` with url, link_type, link_index, output_folder, prefix
3. As each completes => update tracking, spawn next if queue has more
4. Link-reader agents share the 5-agent pool with Figma agents

#### Step 3: WAIT for all agents to complete -> Read results + config
**MANDATORY SYNC**: DO NOT start creating TCs until ALL agents (docs + figma + link-readers) have completed.

- Read all summary files
- Read `{output_folder}/{prefix}-links-tracking.md` (if exists) for linked doc summaries
- Read `.claude/rules/core.md`, `.claude/rules/test-quality.md`, `.claude/rules/output-format.md` + `.claude/templates/testcase-template.md`

#### Step 4: Estimate & divide phases (if needed)
- Estimate expected number of TCs
- If > 50 TCs or > 5 modules -> divide into INDEPENDENT phases
- Spawn N agents in parallel for N phases (max 5)
- Each agent creates a separate xlsx file

#### Step 5: Merge & Upload (same as MODE A Step 5)

### Fallback (if agent fails)
Read directly: Lark API / WebFetch / Read tool / Figma MCP tools

## Test Case Creation Process

### Step 1: Analyze requirements
- Carefully read specs / plan / Figma design documents
- Identify all testable scenarios
- List business rules, validation rules, UI behavior
- Identify integration points (API, database, third-party)

### Step 2: Design test cases
- **Group by section/scenario** — each section is a clear logical group
- **Ensure comprehensive coverage**:
  - **Positive cases (Happy path)**: Main flow, valid input, expected results
  - **Negative cases**: Invalid input, error handling, empty state, permission denied
  - **Boundary cases**: Min/max values, character limits, maximum/minimum quantities
  - **Edge cases**: Empty/null, special characters, concurrent actions, network loss, multi-device
  - **UI/UX cases**: Layout, responsive, loading/empty/error states, animation, scroll behavior
- **Assign priority to each TC**:
  - **Critical**: Core business flow, if it fails the feature is unusable
  - **High**: Important functionality, affects main user experience
  - **Medium**: Validation, edge cases with reasonable probability
  - **Low**: UI polish, minor edge cases that rarely occur

### Step 3: Write detailed test cases

**TC ID**: TC_001, TC_002... (sequential, **reset per sheet** - new sheet starts over from TC_001)

**Description**: Concise, clear description of the test case objective

**Pre-condition**: List ALL prerequisites:
- Account state (logged in, role, permissions...)
- Required existing data (order created, config set up...)
- Required environment / settings

**Steps to Perform** (MOST IMPORTANT):
- Write step by step, SPECIFIC action + data + UI location
- Each step is a single, clear action
- Include test data values in steps (e.g., enter "test@gmail.com")
- Specify UI element location (e.g., "Save" button in top right corner)
- DETAILED ENOUGH that anyone reading can execute immediately
- GOOD example:
  ```
  1. Open app > Log in with account admin@test.com / Pass@1234
  2. Go to menu "Warehouse Management" > Select "Stock In"
  3. Click "+ Create stock in receipt" button in top right corner
  4. In "Supplier" field, enter "SUP001" > Select the first result
  5. In "Quantity" field, enter value "100"
  6. Click "Save" button at the bottom of the form
  ```
- BAD example (DO NOT DO THIS):
  ```
  1. Log in
  2. Go to stock in
  3. Create receipt and enter information
  4. Save
  ```

**Steps Expected Result**:
- DO NOT write obvious/redundant expected results:
  - "App does not crash" - WRONG
  - "No lag or jitter" - WRONG
  - "No errors" - WRONG
  - "System works normally" - WRONG
  - "App opens successfully" - WRONG
- ONLY write expected results with actual testing value:
  - Describe specifically how the UI changes
  - What notification / message is displayed
  - Where data is updated and what value
  - Navigation: which screen it transitions to
  - How element state changes (enabled/disabled, visible/hidden)

**Status**: Default `NOT START` - dropdown combobox: PASSED, FAILED, NOT START, CANCEL

**Other columns**:
- **Test Type**: Leave blank (user fills in)
- **isAuto**: Leave blank (user fills in)
- **BugID**: Leave blank

### Language & Character Rules (MANDATORY)

**Default language**: Vietnamese WITH diacritics
- Correct: "Đăng nhập tài khoản có quyền truy cập module Báo Cáo"
- WRONG: "Dang nhap tai khoan co quyen truy cap module Bao Cao"
- If user wants English => prompt must have: `language: English`

**Sanitize special characters**: Use `sanitize_text()` and `sanitize_tc()` from template
- `—` (em dash) => `-`
- `->` => `=>`
- Smart quotes => straight quotes

### Step 4: Calculate Time Estimation
- Count exact number of actual TCs (do not count section header rows)
- Apply formula from `.claude/rules/output-format.md`:
  - Simple (UI check, display, toggle): 2 min/TC
  - Medium (form input, validation, CRUD): 3 min/TC
  - Complex (API integration, cross-platform, multi-step flow): 4-5 min/TC
  - Mixed -> default 3 min/TC
  - Buffer +20%

### Step 4b: Story Point Estimation (MANDATORY)
- Read `.claude/rules/story-point.md` for SP estimation rules
- Get user role: `python3 -c "import sys; sys.path.insert(0, '.'); from configs.env_loader import get_user_role; print(get_user_role())"`
- Estimate SP based on: TC count, complexity, scope, risk
- Apply role multiplier (junior x1.5, mid x1.2, senior/lead x1.0)
- Round to nearest Fibonacci: 1, 2, 3, 5, 8, 13, 21
- Add SP info to header Row 7 of xlsx output:
  - Cell A7: `Story Point:`
  - Cell B7: `{SP} points ({role})`
- Display SP estimation summary to user after creating TCs

### Step 5: Create Google Sheets
- Use Python code from `.claude/templates/testcase-template.md`
- Create script file at `results/<feature-name>/create_tc.py`
- Run the script to create Google Sheets
- Return URL to user

## Quality Checklist (self-check before output)

- [ ] Does each TC have complete pre-conditions?
- [ ] Are steps detailed enough with specific test data?
- [ ] Are there NO obvious expected results?
- [ ] Is content written in Vietnamese WITH diacritics? (unless user requests English)
- [ ] Sanitized special characters (—, ->, smart quotes)?
- [ ] Covered Positive + Negative + Boundary + Edge cases?
- [ ] Priority assigned appropriately?
- [ ] Sections grouped logically and clearly?
- [ ] Time Estimation calculated with correct formula?
- [ ] TC_ID reset per sheet (TC_001 at the start of each sheet)?
- [ ] Each sheet has its own header (rows 1-6) with COUNTIF formulas?

## Output

- **Multi-phase**: Each agent creates separate xlsx -> merge all -> push once to Google Sheets
- **Single-phase**: Create local xlsx file -> push to Google Sheets
- Each different feature/section -> **separate sheet** in the workbook (do not combine into 1 sheet)
- Python script saved at `results/<feature-name>/create_tc.py`
- **DO NOT push individual phases separately** — only push AFTER all merging is complete
- Return 1 single Google Sheets URL to user
- Output directory name: lowercase, hyphens instead of spaces

## Input
$ARGUMENTS

If no input provided, ask user to describe the feature or paste the requirement/spec to create test cases.
