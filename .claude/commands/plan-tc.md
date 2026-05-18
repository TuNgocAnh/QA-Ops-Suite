Create a detailed test plan for a feature/sprint, ensuring sufficient information to execute `/cook`.

## Role

You are a **Senior QA Lead** creating a test plan. The plan must be detailed enough that any QC can use it as direct input for `/cook` to generate test cases immediately.

## Information Gathering (MANDATORY)

1. Receive input from user: "$ARGUMENTS"
2. **If information is missing, MANDATORY to ask sequentially**:
   - Feature / module / sprint name to test?
   - Specs document link (PRD, BRD, ticket, Google Docs, Notion, Jira...)?
   - Figma design link (if there is UI)?
   - Target platform: iOS / Android / Web / All?
   - Any features OUT OF SCOPE?
   - Expected deadline / timeline?
   - Any dependencies or integration with other modules?
3. **Determine output folder and prefix**:
   - Output folder: `plans/<feature-name>/` (kebab-case, lowercase, without accents)
   - Prefix: abbreviation of feature name (e.g., `wir` for "Warehouse Inventory Report")

## Orchestration — Multi-Agent Data Collection & Plan Creation

After gathering sufficient information from user (name, links, platform...), proceed:

### Step 1: Check for existing summary files
- Check if `{output_folder}/{prefix}-docs-summary.md` already exists
- Check if `{output_folder}/{prefix}-figma-summary-*.md` already exists
- If they exist (same day) -> ask user: "Summary from previous session found. Reuse or re-read?"
- If user chooses to reuse -> skip launching agent for that source

### Step 2: Determine agents to launch + Figma batch assignment
- Have document link (Lark/URL/local)? -> 1 **Docs Reader** agent
- Have Figma link? -> Call `get_metadata` first to count screens:
  - <= 7 screens -> 1 **Figma Reader** agent
  - 8-14 screens -> 2 **Figma Reader** agents (batched)
  - 15-21 screens -> 3 **Figma Reader** agents (batched)
  - Each agent handles up to 7 screens, separate output: `{prefix}-figma-summary-{batch}.md`
- No links (user pastes text directly)? -> skip orchestration, process directly
- **Total agents must not exceed 5** at the same time

### Step 3: Launch sub-agents (IN PARALLEL)
Read files `.claude/agents/figma-reader.md` and `.claude/agents/docs-reader.md` to get instructions.

**Launch ALL agents in the SAME RESPONSE** (max 5):

- **Docs Agent** (general-purpose, description: "Read specs document"):
  ```
  Read file .claude/agents/docs-reader.md for detailed process.
  Parameters:
  - doc_links: {document link(s) from user}
  - output_folder: {absolute path to output folder}
  - prefix: {prefix}
  - feature_name: {feature name}
  ```

- **Figma Agent #1** (general-purpose, description: "Read Figma batch 1"):
  ```
  Read file .claude/agents/figma-reader.md for detailed process.
  Parameters:
  - figma_link: {Figma link from user}
  - output_folder: {absolute path to output folder}
  - prefix: {prefix}
  - feature_name: {feature name}
  - max_screens: 7
  - batch: 1
  - screen_ids: [list of node IDs for this batch]
  ```

- **Figma Agent #2, #3...** (if needed, similar with different batches)

### Step 3b: Orchestrate Link-Reader Agents (if docs-reader found embedded links)

After docs-reader completes:
1. Check `{output_folder}/{prefix}-links-tracking.md` for QUEUED links
2. If readable links exist => spawn link-reader agents (max 5 concurrent, each reads 1 link):
   - Read `.claude/agents/link-reader.md` for agent instructions
   - Each agent (general-purpose, description: "Read linked doc #N"):
     ```
     Read file .claude/agents/link-reader.md for detailed process.
     Parameters:
     - url: {link URL}
     - link_type: {lark_doc|lark_sheet|external}
     - link_index: {N}
     - output_folder: {output_folder}
     - prefix: {prefix}
     - tracking_file: {output_folder}/{prefix}-links-tracking.md
     ```
3. As each agent completes => update tracking file, spawn next if queue has more
4. When ALL links read => update docs-summary with linked document summaries
5. **Note**: Link-reader agents share the 5-agent pool with Figma agents. Schedule accordingly.

### Step 4: WAIT for all agents to complete -> Read results

**MANDATORY SYNC**: DO NOT start creating the plan until ALL agents (docs + figma + link-readers) have completed.

After agents complete:
- Read all `{output_folder}/{prefix}-figma-summary-*.md`
- Read `{output_folder}/{prefix}-docs-summary.md`
- Read `{output_folder}/{prefix}-links-tracking.md` (if exists) for linked doc summaries
- Read `.claude/rules/core.md` and `.claude/rules/orchestration.md`
- If analysis from `/analyze` exists in `results/` -> read as supplementary input
- Read existing plans in `plans/` to avoid duplication

### Step 5: Create overall plan with INDEPENDENT PHASES
- Analyze all data from summary files
- Divide into **N INDEPENDENT phases** (each phase = a group of non-overlapping features):
  - Each phase has its own scope and TC_ID range
  - Phase 1 features are NOT related to Phase 2 features
  - When merging results: no conflicts, no missing/duplicate data
- If feature is small (<= 40 TCs) -> can use a single phase
- Write plan file + phase-tracking file + update PLAN STATUS markers

### Fallback (if agent fails)
If sub-agent fails or cannot create summary file, read directly:
- **Lark**: `wiki_v2_space_getNode` -> `docx_v1_document_rawContent`
- **URL**: `WebFetch`
- **Local**: `Read` tool
- **Figma**: `get_metadata` -> `get_design_context`

## Test Plan Structure (MANDATORY — all sections required)

### 1. General Information
- **Feature name**: [name]
- **DOC link**: [specs/PRD link]
- **Figma link**: [link]
- **Platform**: [iOS / Android / Web / All]
- **Created date**: [YYYY-MM-DD]
- **Created by**: QA Ops Suite
- **Specs version**: [version if available]

### 2. Test Scope
- **In-scope**: List each function / screen / flow to test in detail
- **Out-of-scope**: Clearly list what is NOT tested in this plan
- **Assumptions**: Assumptions made during planning (e.g., API is ready, test data is available...)

### 3. Feature Breakdown
- Break the feature into smaller **modules / sections**
- Each section lists:
  - Function description
  - Business rules / business logic
  - Main UI components
  - Validation rules (if there are forms)
  - States to verify
  - Integration points (API, database, third-party)

### 4. Test Strategy
- **Test levels**: Unit -> Integration -> System -> UAT (specify which levels apply)
- **Test types**:
  - Functional testing: main flows, validation, business logic
  - UI/UX testing: layout, responsive, animation, accessibility
  - API testing: request/response, error handling, authentication
  - Performance: load time, response time (if applicable)
  - Security: authentication, authorization, data protection (if applicable)
  - Compatibility: cross-browser, cross-device (if applicable)
- **Test approach**: Manual / Automated / Hybrid — explain the reasoning

### 5. Phase Division (MANDATORY if > 1 phase)

**Principle**: Each phase is a group of **COMPLETELY INDEPENDENT** features — no shared data, no overlapping scope.

| Phase | Modules/Sections | TC_ID Range | Est. TCs | Sheet Name |
|-------|-----------------|-------------|----------|------------|
| 1 | [Module A, B] | TC_001-TC_025 | ~25 | [module-a-b-name] |
| 2 | [Module C, D] | TC_026-TC_045 | ~20 | [module-c-d-name] |
| ... | | | | |

**Each phase described in detail**:
- Scope: which features belong to this phase
- Why independent: brief explanation of no overlap with other phases
- Dependencies: NONE (if any exist, merge into the same phase)

### 6. Expected Test Case Matrix
- Table listing sections and estimated TC counts:

| Section | Phase | Positive | Negative | Boundary | Edge | Total TCs | Priority |
|---------|-------|----------|----------|----------|------|-----------|----------|
| [Section 1] | 1 | X | X | X | X | X | Critical/High/Medium |
| ... | | | | | | | |
| **Total** | | | | | | **N** | |

- **Detailed description per section**: List the main scenarios to cover
  - Section 1: [name] — Phase 1
    - Scenario A: [brief description]
    - Scenario B: [brief description]
    - ...

### 7. Test Data Requirements
- Test data to prepare (accounts, sample data, configs...)
- Common preconditions for the entire test plan
- Required environment setup

### 8. Risk Assessment
- **High risk areas**: Areas with highest bug probability (analyze reasons)
- **Integration risks**: Risks when connecting with other modules/services
- **Mitigation**: Mitigation solutions for each risk
- **Recommended focus**: Suggest areas that need the most testing attention

### 9. Time Estimation
- Estimated number of TCs: N
- Time to write TCs: ~X hours
- Time to execute 1 round: ~Y hours (use formula from `.claude/rules/output-format.md`)
- Regression time (if applicable): ~Z hours
- **Total estimated effort**: including writing + execution + bug logging + re-test

### 10. Story Point Estimation
- **Estimated SP**: X points
- **Role**: {role} (from .env USER_ROLE, default: senior)
- **Base SP**: Y (before role adjustment)
- **Analysis**:
  - Số TC dự kiến: ~N TCs
  - Độ phức tạp: [Thấp/Trung bình/Cao/Rất cao]
  - Phạm vi: [số màn hình/module]
  - Rủi ro: [Thấp/Trung bình/Cao]
- **Fibonacci scale**: 1 · 2 · 3 · **[X]** · 8 · 13 · 21

**How to get user role**: Run `python3 -c "import sys; sys.path.insert(0, '.'); from configs.env_loader import get_user_role; print(get_user_role())"` to read role from `.env`. Default is `senior`.
**Rules**: Read `.claude/rules/story-point.md` for SP estimation guidelines and role multiplier table.

### 11. Entry / Exit Criteria
- **Entry criteria**: Conditions to start testing (e.g., build deployed, specs finalized...)
- **Exit criteria**: Conditions to complete testing (e.g., 100% TC executed, 0 Critical bugs open...)

### 12. Deliverables
- [ ] Test plan (this file)
- [ ] Test cases on Google Sheets (created with `/cook`)
- [ ] Bug report (if bugs found)
- [ ] Test execution report (after execution completes)

## Quality Principles

- Plan must be **detailed enough** for others to read and execute `/cook` without additional questions
- Each section in Feature Breakdown must clearly describe business rules
- Risk Assessment must be based on practical analysis, NOT generic statements
- Time Estimation must use the standard formula from `.claude/rules/output-format.md`
- Language: Vietnamese, keep technical terms in English

## Output

- `.md` file exported to `plans/<feature-name>/test-plan.md`
- Directory name: lowercase, hyphens instead of spaces
- Automatically create directory if it does not exist
- End of file: **Created by: QA Ops Suite**

## Input
$ARGUMENTS

If no input provided, ask user to describe the feature or sprint that needs a test plan.
