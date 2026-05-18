#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

MODE="${1:-sync}"
if [[ "${MODE}" != "sync" && "${MODE}" != "--check" ]]; then
  echo "Usage: $0 [--check]" >&2
  exit 1
fi

if [[ ! -f "CLAUDE.md" || ! -d ".claude" ]]; then
  echo "Missing CLAUDE.md or .claude directory" >&2
  exit 1
fi

mkdir -p .codex

TMP_CHECKSUM="$(mktemp)"
trap 'rm -f "${TMP_CHECKSUM}"' EXIT

{
  shasum -a 256 "CLAUDE.md"
  find ".claude" -type f ! -name ".DS_Store" | sort | while read -r file; do
    shasum -a 256 "${file}"
  done
} > "${TMP_CHECKSUM}"

if [[ "${MODE}" == "--check" ]]; then
  if [[ ! -f ".codex/context-checksum.txt" ]]; then
    echo "Context checksum not found. Run: ./scripts/sync-codex-context.sh" >&2
    exit 2
  fi

  if cmp -s "${TMP_CHECKSUM}" ".codex/context-checksum.txt"; then
    echo "Codex context is up to date."
    exit 0
  fi

  echo "Codex context drift detected."
  diff -u ".codex/context-checksum.txt" "${TMP_CHECKSUM}" || true
  exit 3
fi

cp "${TMP_CHECKSUM}" ".codex/context-checksum.txt"

NOW_UTC="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

{
  echo "# Codex Context Index"
  echo
  echo "- Generated at (UTC): ${NOW_UTC}"
  echo
  echo "## Canonical Inputs"
  echo
  echo "- [CLAUDE.md](../CLAUDE.md)"
  echo "- [.claude/rules](../.claude/rules)"
  echo "- [.claude/commands](../.claude/commands)"
  echo "- [.claude/agents](../.claude/agents)"
  echo "- [.claude/docs](../.claude/docs)"
  echo "- [.claude/templates](../.claude/templates)"
  echo "- [.claude/sitemap.yaml](../.claude/sitemap.yaml)"
  echo
  echo "## Rule Files"
  echo
  find ".claude/rules" -type f ! -name ".DS_Store" | sort | while read -r file; do
    echo "- [${file#./}](../${file#./})"
  done
  echo
  echo "## Command Files"
  echo
  find ".claude/commands" -type f ! -name ".DS_Store" | sort | while read -r file; do
    echo "- [${file#./}](../${file#./})"
  done
  echo
  echo "## Agent Files"
  echo
  find ".claude/agents" -type f ! -name ".DS_Store" | sort | while read -r file; do
    echo "- [${file#./}](../${file#./})"
  done
  echo
  echo "## Documentation Files"
  echo
  find ".claude/docs" -type f ! -name ".DS_Store" | sort | while read -r file; do
    echo "- [${file#./}](../${file#./})"
  done
  echo
  echo "## Template Files"
  echo
  find ".claude/templates" -type f ! -name ".DS_Store" | sort | while read -r file; do
    echo "- [${file#./}](../${file#./})"
  done
} > ".codex/context-index.md"

{
  echo "# Codex Command Map"
  echo
  echo "- Generated at (UTC): ${NOW_UTC}"
  echo
  echo "| Command | Intent | Role | Source |"
  echo "|---|---|---|---|"
  for file in .claude/commands/*.md; do
    command_name="$(basename "${file}" .md)"
    intent="$(head -n 1 "${file}" | sed 's/|/\\|/g')"
    role="$(
      awk '
        /^## Role$/ {capture=1; next}
        capture && NF {print; exit}
      ' "${file}" | sed 's/|/\\|/g'
    )"
    source_path="${file#./}"
    echo "| \`/${command_name}\` | ${intent} | ${role} | [${source_path}](../${source_path}) |"
  done
} > ".codex/command-map.md"

echo "Codex context synced."
echo "- .codex/context-index.md"
echo "- .codex/command-map.md"
echo "- .codex/context-checksum.txt"
