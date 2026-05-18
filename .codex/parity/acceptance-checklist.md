# Parity Acceptance Checklist

Use this checklist after running Claude and Codex with the same case prompts.

## Required checks

- Vietnamese output has proper diacritics.
- Command intent matches fixture (`/plan-tc`, `/cook`, `/log-bug`).
- Rule loading behavior follows `CLAUDE.md` mapping.
- Output folder conventions are preserved (`results/*`, `plans/*`).
- Story Point output reflects `USER_ROLE` in `.env`.
- Lark/Google workflow is consistent with `configs/*` helpers.

## Decision

- `PASS`: no material behavior differences that affect execution quality.
- `CONDITIONAL PASS`: only wording differences; process and artifacts equivalent.
- `FAIL`: any logic, formatting, or workflow drift that changes QA execution outcomes.
