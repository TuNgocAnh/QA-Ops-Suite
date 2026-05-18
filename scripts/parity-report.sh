#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

mkdir -p .codex/parity/reports

status=0

for case_file in .codex/parity/cases/*.md; do
  case_name="$(basename "${case_file}" .md)"
  claude_out=".codex/parity/results/claude/${case_name}.md"
  codex_out=".codex/parity/results/codex/${case_name}.md"
  report_file=".codex/parity/reports/${case_name}.diff"

  if [[ ! -f "${claude_out}" || ! -f "${codex_out}" ]]; then
    echo "[MISSING] ${case_name}: expected both ${claude_out} and ${codex_out}"
    status=1
    continue
  fi

  if diff -u "${claude_out}" "${codex_out}" > "${report_file}"; then
    echo "[MATCH] ${case_name}"
  else
    echo "[DIFF]  ${case_name} -> ${report_file}"
    status=1
  fi
done

exit ${status}
