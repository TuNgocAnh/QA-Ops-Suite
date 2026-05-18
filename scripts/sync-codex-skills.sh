#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMANDS_DIR="${PROJECT_ROOT}/.claude/commands"
SKILLS_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
CREATOR_ROOT="${SKILLS_ROOT}/.system/skill-creator"
INIT_SCRIPT="${CREATOR_ROOT}/scripts/init_skill.py"
VALIDATE_SCRIPT="${CREATOR_ROOT}/scripts/quick_validate.py"

if [[ ! -d "${COMMANDS_DIR}" ]]; then
  echo "Missing commands directory: ${COMMANDS_DIR}" >&2
  exit 1
fi

if [[ ! -f "${INIT_SCRIPT}" || ! -f "${VALIDATE_SCRIPT}" ]]; then
  echo "Missing skill creator scripts in: ${CREATOR_ROOT}" >&2
  exit 1
fi

mkdir -p "${SKILLS_ROOT}"

normalize_one_line() {
  tr '\n' ' ' | sed -E 's/[[:space:]]+/ /g; s/^ //; s/ $//'
}

yaml_block_indent() {
  sed 's/^/  /'
}

skill_count=0

for cmd_file in "${COMMANDS_DIR}"/*.md; do
  cmd_name="$(basename "${cmd_file}" .md)"
  skill_name="qa-ops-suite-${cmd_name}"
  skill_dir="${SKILLS_ROOT}/${skill_name}"

  intent="$(head -n 1 "${cmd_file}" | normalize_one_line)"
  role="$(
    awk '
      /^## Role$/ {capture=1; next}
      capture && NF {print; exit}
    ' "${cmd_file}" | normalize_one_line
  )"

  if [[ -z "${intent}" ]]; then
    intent="Execute QA Ops Suite command /${cmd_name}."
  fi

  if [[ -z "${role}" ]]; then
    role="Follow the command specification in .claude/commands/${cmd_name}.md."
  fi

  description="${intent} Use when user requests /${cmd_name} behavior from QA Ops Suite workflows in this repository."

  if [[ ! -d "${skill_dir}" ]]; then
    python3 "${INIT_SCRIPT}" "${skill_name}" --path "${SKILLS_ROOT}" >/dev/null
  fi

  description_block="$(printf '%s' "${description}" | yaml_block_indent)"

  cat > "${skill_dir}/SKILL.md" <<EOF
---
name: ${skill_name}
description: |-
${description_block}
---

# ${skill_name}

Execute QA Ops Suite command semantics for \`/${cmd_name}\` by reusing the existing project command spec and rules.

## Workflow

1. Ensure current workspace is the QA Ops Suite project root (contains \`CLAUDE.md\` and \`.claude/\`).
2. Read \`CLAUDE.md\` for command loading strategy.
3. Read \`.claude/commands/${cmd_name}.md\` as the authoritative command procedure.
4. Read \`.claude/rules/core.md\` and any additional files required by the command matrix.
5. Apply the command flow exactly as documented, including required data gathering, output format, and fallback behavior.
6. Default to Vietnamese with proper diacritics unless user explicitly requests English.

## Input Pattern

- Accept prompts in style \`COMMAND: /${cmd_name}\` with free-form arguments.
- Treat any additional user text as \`ARGUMENTS\` payload for the command flow.

## Notes

- Command intent: ${intent}
- Command role: ${role}
EOF

  python3 "${VALIDATE_SCRIPT}" "${skill_dir}" >/dev/null
  skill_count=$((skill_count + 1))
done

echo "Synced ${skill_count} QA Ops Suite skills to ${SKILLS_ROOT}"
