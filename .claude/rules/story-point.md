# Story Point Estimation Rules

Rules for estimating Story Points from the QC perspective.
**Read when**: `/plan-tc`, `/cook`, `/est-sp`

---

## 1. Story Point Scale (Fibonacci)

Use Fibonacci scale: **1, 2, 3, 5, 8, 13, 21**

| SP | Description | Examples |
|----|------------|---------|
| **1** | Very simple, minor change, nearly zero risk | Change label, fix typo, verify 1 field display |
| **2** | Simple, low risk, 1-2 screens | Toggle on/off, verify simple list display |
| **3** | Light-medium, clear logic | Simple form (3-5 fields), basic CRUD for 1 entity |
| **5** | Medium, has validation + business logic | Complex form, filter/sort/pagination, 2-3 step flow |
| **8** | Complex, many scenarios, API integration | Full CRUD module, multi-step flow, payment integration |
| **13** | Very complex, cross-module, many edge cases | Third-party integration, complex workflow, multi-platform |
| **21** | Epic-level, should be split | Entire large module, should split into multiple stories |

---

## 2. SP Assessment Factors (from QC perspective)

When estimating SP, analyze the following factors:

### 2.1 Number of Test Cases
| TC Count | Base SP (before role adjustment) |
|----------|--------------------------------|
| 1-10 | 1-2 |
| 11-25 | 3-5 |
| 26-50 | 5-8 |
| 51-80 | 8-13 |
| 80+ | 13-21 (should split) |

### 2.2 Technical Complexity
- **Low**: UI display, static content, simple navigation
- **Medium**: Form validation, CRUD, filter/sort, state management
- **High**: API integration, real-time data, cross-platform, multi-step workflow
- **Very High**: Third-party integration, payment, security, concurrent operations

### 2.3 Impact Scope
- 1 screen => low
- 2-3 related screens => medium
- Cross-module, affects multiple flows => high

### 2.4 Risk & Uncertainty
- Clear logic, complete specs => low
- Incomplete specs, ambiguity present => medium
- Third-party dependency, no API docs => high

---

## 3. Role Multiplier (IMPORTANT)

SP is adjusted based on the executor's role (read from `USER_ROLE` in `.env`, default `senior`):

| Role | Multiplier | Explanation |
|------|-----------|------------|
| **junior** | x1.5 (round up to nearest Fibonacci) | Needs extra time for context learning, writing more detailed TCs, more reviews |
| **mid** | x1.2 (round up to nearest Fibonacci) | Experienced but may need guidance on complex parts |
| **senior** | x1.0 (baseline) | Baseline — quick understanding, efficient TC writing |
| **lead** | x1.0 (baseline) | Equivalent to senior for execution, plus review responsibility |

### Calculation method:
1. Determine base SP based on factor analysis in Section 2
2. Multiply by role multiplier
3. Round up to nearest Fibonacci number

**Example**: Medium feature, base SP = 5
- Junior: 5 x 1.5 = 7.5 => round up to **8**
- Mid: 5 x 1.2 = 6 => round up to **8**
- Senior: 5 x 1.0 = 5 => stays **5**
- Lead: 5 x 1.0 = 5 => stays **5**

---

## 4. SP Output Format

### In Test Plan (`/plan-tc`):
Add **Story Point Estimation** section after "Time Estimation":

```markdown
### 10. Story Point Estimation
- **Estimated SP**: X points
- **Role**: {role} (from .env)
- **Base SP**: Y (before adjustment)
- **Analysis**:
  - Expected TCs: ~N TCs
  - Complexity: [Low/Medium/High/Very High]
  - Scope: [number of screens/modules]
  - Risk: [Low/Medium/High]
- **Fibonacci scale**: 1 · 2 · 3 · **[X]** · 8 · 13 · 21 (highlight selected SP)
```

### In Test Case output (`/cook`):
Add **Story Point** row to header Row 7 (after Row 6 Time Est):
- Cell A7: `Story Point:`
- Cell B7: `{SP} points ({role})`
- Column header rows shift down to Row 8-9 (instead of Row 7-8)

**NOTE**: Currently Row 7-8 are column headers. When adding SP row, column headers shift to Row 8-9, data starts from Row 10 (instead of Row 9). Update COUNTIF formulas and freeze pane accordingly.

### In `/est-sp` output:
Return result directly (text response), **MANDATORY table format** (MUST always use this exact layout):

```
--- Story Point Estimation ---

| Item | Value |
|------|-------|
| Feature | {feature name} |
| Role | {role} (from .env) |
| Estimated SP | {X} points |
| Base SP | {Y} |
| Expected TCs | ~{N} TCs |
| Complexity | {description} |
| Scope | {description} |
| Risk | {description} |
| Fibonacci | 1 · 2 · 3 · **[X]** · 8 · 13 · 21 |
```

**Rules**:

- ALWAYS use markdown table format — NO other format (bullet list, plain text) allowed
- Bold the selected SP in Fibonacci row with `**[X]**`
- If role multiplier != 1.0, add a row after Base SP: `| Role multiplier | x{multiplier} ({role}) => {Y} x {multiplier} = {result} => round to Fibonacci = {X} |`
- Keep descriptions concise but informative (1 line per cell)

---

## 5. Special Rules

- **Always read role from `.env`** via `get_user_role()` (configs/env_loader.py). Never hard-code role.
- **SP is an estimate**, not an exact number. Always explain reasoning.
- **If feature is too large** (SP > 13): recommend splitting into smaller stories.
- **SP applies to QC effort** (write TCs + execute + log bugs + retest), NOT dev effort.
- **When `/est-sp` reads a plan with existing SP**: display existing SP, ask user if they want to recalculate.
