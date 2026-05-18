# Codex vs Claude Parity

This folder contains fixed prompts and result placeholders used to compare Claude Code and Codex behavior.

## Cases

- `plan-tc.md`
- `cook.md`
- `log-bug.md`

## Run

1. Run context sync first:
   - `./scripts/sync-codex-context.sh`
2. For each case in `.codex/parity/cases/*.md`, run once in Claude and once in Codex.
3. Save outputs:
   - Claude: `.codex/parity/results/claude/<case>.md`
   - Codex: `.codex/parity/results/codex/<case>.md`
4. Generate diff report:
   - `./scripts/parity-report.sh`
5. Evaluate results with:
   - `.codex/parity/acceptance-checklist.md`

## Evaluation focus

- Vietnamese diacritics quality
- Rule adherence from `.claude/rules/*`
- Output folder/path behavior
- Story Point and role logic from `.env`
- Lark/Google workflow alignment when applicable
