# Core Rules & Conventions

Rules cơ bản, áp dụng cho MỌI command (`/analyze`, `/cook`, `/fix`, `/plan-tc`, `/ask`, `/est-sp`).

---

## 0. LANGUAGE - RULE #1 (READ THIS BEFORE ANYTHING ELSE)

**THIS IS THE MOST IMPORTANT RULE. APPLIES TO ALL OUTPUT INCLUDING SUB-AGENTS.**

- **REQUIRED**: All Vietnamese content MUST have proper diacritics
  - Correct: "Đăng nhập", "Mật khẩu", "Nhà cung cấp", "Kiểm tra hiển thị thông báo lỗi"
  - **WRONG**: "Dang nhap", "Mat khau", "Nha cung cap", "Kiem tra hien thi thong bao loi"
- **APPLIES TO ALL**: test case descriptions, preconditions, steps, expected results, section titles, summary files, all output text
- **ESPECIALLY FOR SUB-AGENTS**: When spawning a sub-agent (Agent tool), you **MUST** include this line in the prompt:
  > "CRITICAL: All Vietnamese content MUST have proper diacritics. 'Đăng nhập' NOT 'Dang nhap'. 'Mật khẩu' NOT 'Mat khau'. Output without diacritics is WRONG and must be fixed."
- Technical terms stay in English (API, token, session, database...)
- If the user wants English => prompt must specify: `language: English`
- **CHECK BEFORE OUTPUT**: Before writing any content, self-check: "Does this content have proper diacritics?" If not => fix it.
- **APPLIES TO CODE TOO**: Vietnamese strings inside Python code, formulas, constants MUST also have diacritics.
  - Correct in code: `&" phút / "`, `&" giờ "`
  - **WRONG** in code: `&" phut / "`, `&" gio "`
  - This includes: TIME_EST_FORMULA, section titles, any Vietnamese string literal
- **DO NOT rewrite template constants from memory**. Always `import` from `configs/tc_template.py`. Rewriting from memory is the #1 cause of diacritics loss.

---

## 1. Role & Output Quality

- All output must meet **Senior QA/QC** standards - detailed, accurate, actionable
- `/analyze`: Role of **Senior QA Analyst** - analyze requirement documents, produce quality input for `/plan-tc`
- `/plan-tc`: Role of **Senior QA Lead** - plan detailed enough for any QC to use as input for `/cook`
- `/cook`: Role of **Senior QC Engineer** - production-ready TCs, executable immediately without further explanation
- `/fix`: Role of **Senior QC Engineer** - fix existing TCs + bug analysis + regression TCs
- `/ask`: Role of **Senior QA Consultant** - advise based on real data, specific, actionable
- Recommended workflow: `/analyze` => `/plan-tc` => `/cook` => Execute => `/fix` => `/ask` (ask anytime)

---

## 2. Test Case ID

- Concise format: `TC_001`, `TC_002`, `TC_003`... (incrementing)
- DO NOT use long formats like `TC_Module_Feature_001`
- **TC_ID RESET per sheet**: Each new sheet starts over from `TC_001`
  - Example: Sheet 1: TC_001-TC_050, Sheet 2: TC_001-TC_035
  - **DO NOT** number sequentially across sheets (TC_051 on sheet 2 is WRONG)
- Same rule applies for Checklist (`CL_001`) and Regression Test (`RT_001`)

## 3. Documentation Requirements

- When the user requests **writing test cases** for a feature => **MANDATORY** to ask for:
  - Link to requirement documents (specs, PRD, ticket...)
  - Figma design link (if available)
- **Exception**: When the user requests direct testing (not writing TCs), no need to ask

## 4. Status Column

- Each Status cell is a **data validation (combobox/dropdown)**
- Values: `PASSED`, `FAILED`, `NOT START`, `CANCEL`
- Default value on creation: `NOT START`
- Format: **center-aligned** for all Status cells

## 5. Output Directory

- `/analyze`, `/cook` and `/fix`: `results/<feature_name>/`
- `/plan-tc`: `plans/<feature_name>/`
- Directory names: lowercase, hyphens instead of spaces (e.g., `invoice-export`)
- Automatically create directory if it does not exist

## 6. Language & Branding

- **See Section 0 at the top of the file** - this is the most important rule
- Created by: **QA Ops Suite**

## 7. Sanitize Text (MANDATORY)

- Replace AI-generated incorrect characters **BEFORE** writing to file:
  - `—` (em dash) => `-`
  - `–` (en dash) => `-`
  - `->` => `=>`
  - Smart quotes (`'` `'` `"` `"`) => straight quotes (`'` `"`)
- Applies to ALL content: description, precondition, steps, expected result, section title
- Use the `sanitize_text()` and `sanitize_tc()` functions in `.claude/templates/testcase-template.md`

## 8. Story Point Estimation

- **Áp dụng cho**: `/plan-tc`, `/cook`, `/est-sp`
- **Role**: Đọc từ `USER_ROLE` trong `.env` (giá trị: `junior`, `mid`, `senior`, `lead`). Mặc định: `senior`
- **Cách đọc role**: `python3 -c "import sys; sys.path.insert(0, '.'); from configs.env_loader import get_user_role; print(get_user_role())"`
- **Rules chi tiết**: Đọc `.claude/rules/story-point.md`
- **Thang điểm**: Fibonacci (1, 2, 3, 5, 8, 13, 21)
- **Role multiplier**: junior x1.5, mid x1.2, senior x1.0, lead x1.0
- `/plan-tc`: Thêm section "Story Point Estimation" trong plan output
- `/cook`: Thêm dòng "Story Point:" vào header Row 7 của xlsx
- `/est-sp`: Command độc lập để ước lượng SP từ plan hoặc prompt

---

## 9. Token Management after `/plan-tc`

- After completing `/plan-tc`, it is **MANDATORY** to assess token/context usage level in the current session
- **Notify the user** if:
  - The conversation has been long (many exchanges, many files read)
  - The plan is complex with many modules/sections
  - Many specs/Figma documents have been read in the session
- Notification content:
  > "Plan hoàn tất. Nên chạy `/clear` hoặc `/compact` trước khi tiếp tục với `/cook` hoặc `/fix`, để đảm bảo đủ context window cho việc tạo test case chất lượng cao."
- **Reason**: `/cook` and `/fix` require many tokens to generate detailed test cases - if the context window is near its limit, output will be truncated, lack detail, or not complete
- If the session is still light (simple plan, few documents) => may continue but should still report the status

## 10. Task Time Tracking (MANDATORY)

- **Every task** (`/analyze`, `/plan-tc`, `/cook`, `/fix`) must report time upon completion
- Record the start time (when processing begins) and end time (when output is complete)
- If sub-agents are used => report time for **each agent** separately
- End-of-task report format:

```
--- Time Report ---
Task: /plan-tc (or /cook, /analyze, /fix)
Start: HH:MM:SS
End: HH:MM:SS
Total: X minutes Y seconds

Sub-agents:
  Figma Reader: HH:MM:SS => HH:MM:SS (X minutes Y seconds)
  Docs Reader:  HH:MM:SS => HH:MM:SS (X minutes Y seconds)
---
```

- If no sub-agents are used => only report Start / End / Total
- Time is taken from the system clock (`date` command) at the start and end moments
