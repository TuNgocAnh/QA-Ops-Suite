# Codex Adapter for QA Ops Suite

This repository was originally structured for Claude Code. This file adapts the same operating model for Codex without duplicating business rules.

## Source of Truth

Always treat these as canonical:

1. `CLAUDE.md`
2. `.claude/rules/*.md`
3. `.claude/commands/*.md`
4. `.claude/agents/*.md`
5. `.claude/docs/*.md`
6. `.claude/templates/*.md`
7. `.claude/sitemap.yaml`
8. `configs/*` and `.env` (runtime behavior)

Do not fork rule logic into separate Codex-only copies unless there is a tool incompatibility.

## Command Compatibility Map

Codex does not rely on Claude slash-command runtime. Use the same command intent by explicitly stating the target command in prompt text:

- `COMMAND: /analyze`
- `COMMAND: /plan-tc`
- `COMMAND: /cook`
- `COMMAND: /fix`
- `COMMAND: /ask`
- `COMMAND: /est-sp`
- `COMMAND: /log-bug`
- `COMMAND: /check-duplicate-bug`
- `COMMAND: /explain-bug`
- `COMMAND: /update-board`
- `COMMAND: /sla`
- `COMMAND: /health`
- `COMMAND: /release-check`
- `COMMAND: /triage`
- `COMMAND: /risk`

Input template:

```text
COMMAND: /cook
ARGUMENTS: <same payload you would pass to Claude command>
```

## Rule Loading Matrix

Codex should apply the same loading strategy already defined in `CLAUDE.md`:

- Always load: `.claude/rules/core.md`
- `/cook`: `test-quality.md`, `output-format.md`, `orchestration.md`, `story-point.md`, `sitemap.md`
- `/fix`: `test-quality.md`, `output-format.md`, `orchestration.md`, `sitemap.md`
- `/plan-tc`: `orchestration.md`, `story-point.md`, `sitemap.md`
- `/analyze`: `test-quality.md`, `sitemap.md`
- `/check-duplicate-bug`: `core.md` (và `lark-integration.md` khi cần thao tác Lark API)
- Product Ops commands: `product-ops.md` (+ `sitemap.md` on demand or required by command)
- `conflict-resolution.md`: only when both Docs + Figma are present and conflicts are detected
- On-demand docs:
  - Lark links -> `.claude/docs/lark-integration.md`
  - Figma links -> `.claude/docs/figma-workflow.md`
  - Output type decisions -> `.claude/docs/output-types.md`

## Behavioral Parity Requirements

Codex runs must keep the same outcomes as Claude runs:

1. Vietnamese diacritics are mandatory for Vietnamese output.
2. Output folders:
   - `results/<feature-name>/` for `/analyze`, `/cook`, `/fix`, Product Ops outputs
   - `plans/<feature-name>/` for `/plan-tc`
3. Test case IDs and formatting rules must follow `.claude/rules/*`.
4. Story Point logic must use role from `.env` via existing `configs/env_loader.py`.
5. Lark/Google upload behavior must follow existing helpers in `configs/`.

## Codex Context Sync

Run:

```bash
./scripts/sync-codex-context.sh
```

This generates:

- `.codex/context-index.md`
- `.codex/command-map.md`
- `.codex/context-checksum.txt`

Check for drift without overwriting:

```bash
./scripts/sync-codex-context.sh --check
```

## Parity Test Workflow

1. Sync context:
   - `./scripts/sync-codex-context.sh`
2. Use fixtures in `.codex/parity/cases/`.
3. Save outputs to:
   - `.codex/parity/results/claude/<case>.md`
   - `.codex/parity/results/codex/<case>.md`
4. Compare:
   - `./scripts/parity-report.sh`
5. Review `.codex/parity/reports/*.diff` and resolve material differences.

## Security Notes

- Never commit `.env` or OAuth token files.
- Move hardcoded secrets out of `.mcp.json` into environment-backed values before sharing repo externally.
