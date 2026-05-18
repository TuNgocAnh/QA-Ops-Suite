#!/usr/bin/env bash
# QA Ops Suite - One-command setup (macOS / Linux)
#
# Chạy: ./scripts/setup.sh
# Script sẽ: check Python/Node/ffmpeg => pip install => copy env/mcp từ example => chạy Google OAuth.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

ok()    { printf "${GREEN}[OK]${NC}   %s\n" "$*"; }
warn()  { printf "${YELLOW}[WARN]${NC} %s\n" "$*"; }
err()   { printf "${RED}[ERR]${NC}  %s\n" "$*" >&2; }
step()  { printf "\n${BOLD}==> %s${NC}\n" "$*"; }

# ------------------------------------------------------------
step "1/5  Kiểm tra Python 3"
if ! command -v python3 >/dev/null 2>&1; then
    err "Không tìm thấy python3. Cài: brew install python (macOS) hoặc apt install python3 (Linux)."
    exit 1
fi
PY_VER=$(python3 -c 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 9 ]; }; then
    err "Python $PY_VER quá cũ. Cần >= 3.9."
    exit 1
fi
ok "Python $PY_VER"

# ------------------------------------------------------------
step "2/5  Kiểm tra Node.js + npm (cần cho Lark MCP)"
if command -v node >/dev/null 2>&1 && command -v npx >/dev/null 2>&1; then
    ok "Node $(node --version) / npx có sẵn"
else
    warn "Không tìm thấy Node.js hoặc npx. Lark MCP sẽ không chạy được."
    warn "Cài: brew install node (macOS) hoặc https://nodejs.org"
fi

if command -v ffmpeg >/dev/null 2>&1; then
    ok "ffmpeg có sẵn (cần cho /log-bug video)"
else
    warn "Không tìm thấy ffmpeg. /log-bug với video sẽ không extract frame được."
    warn "Cài: brew install ffmpeg (macOS) hoặc apt install ffmpeg (Linux)"
fi

# ------------------------------------------------------------
step "3/5  Cài Python dependencies"
if [ ! -f "requirements.txt" ]; then
    err "Không tìm thấy requirements.txt ở $(pwd)"
    exit 1
fi
python3 -m pip install --user -r requirements.txt
ok "Đã cài xong dependencies từ requirements.txt"

# ------------------------------------------------------------
step "4/5  Tạo .env và .mcp.json từ example (nếu chưa có)"

if [ -f ".env" ]; then
    ok ".env đã tồn tại, giữ nguyên"
else
    if [ ! -f ".env.example" ]; then
        err "Không tìm thấy .env.example"
        exit 1
    fi
    cp .env.example .env
    ok "Đã copy .env.example => .env"
fi

if [ -f ".mcp.json" ]; then
    ok ".mcp.json đã tồn tại, giữ nguyên"
else
    if [ ! -f ".mcp.json.example" ]; then
        err "Không tìm thấy .mcp.json.example"
        exit 1
    fi
    cp .mcp.json.example .mcp.json
    ok "Đã copy .mcp.json.example => .mcp.json"
    warn "Nhớ điền LARK_APP_ID và LARK_APP_SECRET vào .env (lấy từ Lark Developer Console)"
fi

if [ -f ".claude/boards.md" ]; then
    ok ".claude/boards.md đã tồn tại, giữ nguyên"
elif [ -f ".claude/boards.example.md" ]; then
    cp .claude/boards.example.md .claude/boards.md
    ok "Đã copy .claude/boards.example.md => .claude/boards.md"
fi

if [ -f "configs/lark_bug_board_cache.json" ]; then
    ok "configs/lark_bug_board_cache.json đã tồn tại, giữ nguyên"
elif [ -f "configs/lark_bug_board_cache.example.json" ]; then
    cp configs/lark_bug_board_cache.example.json configs/lark_bug_board_cache.json
    ok "Đã copy configs/lark_bug_board_cache.example.json => configs/lark_bug_board_cache.json"
fi

# ------------------------------------------------------------
step "5/5  Google OAuth (mở browser, đăng nhập)"
echo "Nếu đã authorize rồi, bước này chỉ verify token. Nếu chưa, browser sẽ mở để đăng nhập."
read -r -p "Nhấn Enter để tiếp tục (hoặc Ctrl+C để bỏ qua)..." _
python3 configs/setup-oauth.py
ok "Google OAuth setup xong"

# ------------------------------------------------------------
cat <<'EOF'

==========================================================
  QA Ops Suite setup hoàn tất!

  Next steps:
    1. Mở .env, điền LARK_APP_ID + LARK_APP_SECRET (nếu dùng Lark).
    2. Mở Claude Code tại thư mục project, gõ /help xem danh sách skill.
    3. Đọc README.md (Command Guide) để xem ví dụ prompt.

  Cấu hình Lark board (tuỳ chọn):
    Trong Claude Code, chạy: /update-board tracking bug: <lark_url>
==========================================================
EOF
