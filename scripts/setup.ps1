# QA Ops Suite - One-command setup (Windows PowerShell)
#
# Chạy: .\scripts\setup.ps1
# Script sẽ: check Python/Node/ffmpeg => pip install => copy env/mcp từ example => chạy Google OAuth.

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

function Step($msg)  { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Ok($msg)    { Write-Host "[OK]   $msg" -ForegroundColor Green }
function Warn($msg)  { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Err($msg)   { Write-Host "[ERR]  $msg" -ForegroundColor Red }

# ------------------------------------------------------------
Step "1/5  Kiểm tra Python 3"
$pythonCmd = $null
foreach ($cmd in @("python3", "python", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) { $pythonCmd = $cmd; break }
}
if (-not $pythonCmd) {
    Err "Không tìm thấy Python 3. Cài từ https://www.python.org/downloads/"
    exit 1
}
$pyVer = & $pythonCmd -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))"
$pyParts = $pyVer.Split('.')
if ([int]$pyParts[0] -lt 3 -or ([int]$pyParts[0] -eq 3 -and [int]$pyParts[1] -lt 9)) {
    Err "Python $pyVer quá cũ. Cần >= 3.9."
    exit 1
}
Ok "Python $pyVer ($pythonCmd)"

# ------------------------------------------------------------
Step "2/5  Kiểm tra Node.js + npx + ffmpeg"
if ((Get-Command node -ErrorAction SilentlyContinue) -and (Get-Command npx -ErrorAction SilentlyContinue)) {
    $nodeVer = & node --version
    Ok "Node $nodeVer / npx có sẵn"
} else {
    Warn "Không tìm thấy Node.js hoặc npx. Lark MCP sẽ không chạy được."
    Warn "Cài từ https://nodejs.org"
}

if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Ok "ffmpeg có sẵn (cần cho /log-bug video)"
} else {
    Warn "Không tìm thấy ffmpeg. /log-bug với video sẽ không extract frame được."
    Warn "Cài: choco install ffmpeg  hoặc tải từ https://ffmpeg.org/download.html"
}

# ------------------------------------------------------------
Step "3/5  Cài Python dependencies"
if (-not (Test-Path "requirements.txt")) {
    Err "Không tìm thấy requirements.txt"
    exit 1
}
& $pythonCmd -m pip install --user -r requirements.txt
Ok "Đã cài xong dependencies"

# ------------------------------------------------------------
Step "4/5  Tạo .env và .mcp.json từ example (nếu chưa có)"

if (Test-Path ".env") {
    Ok ".env đã tồn tại, giữ nguyên"
} else {
    if (-not (Test-Path ".env.example")) { Err ".env.example không tồn tại"; exit 1 }
    Copy-Item ".env.example" ".env"
    Ok "Đã copy .env.example => .env"
}

if (Test-Path ".mcp.json") {
    Ok ".mcp.json đã tồn tại, giữ nguyên"
} else {
    if (-not (Test-Path ".mcp.json.example")) { Err ".mcp.json.example không tồn tại"; exit 1 }
    Copy-Item ".mcp.json.example" ".mcp.json"
    Ok "Đã copy .mcp.json.example => .mcp.json"
    Warn "Nhớ điền LARK_APP_ID và LARK_APP_SECRET vào .env"
}

if (Test-Path ".claude/boards.md") {
    Ok ".claude/boards.md đã tồn tại, giữ nguyên"
} else {
    if (Test-Path ".claude/boards.example.md") {
        Copy-Item ".claude/boards.example.md" ".claude/boards.md"
        Ok "Đã copy .claude/boards.example.md => .claude/boards.md"
    }
}

if (Test-Path "configs/lark_bug_board_cache.json") {
    Ok "configs/lark_bug_board_cache.json đã tồn tại, giữ nguyên"
} else {
    if (Test-Path "configs/lark_bug_board_cache.example.json") {
        Copy-Item "configs/lark_bug_board_cache.example.json" "configs/lark_bug_board_cache.json"
        Ok "Đã copy configs/lark_bug_board_cache.example.json => configs/lark_bug_board_cache.json"
    }
}

# ------------------------------------------------------------
Step "5/5  Google OAuth (mở browser, đăng nhập)"
Write-Host "Nhấn Enter để tiếp tục (Ctrl+C để bỏ qua)..."
Read-Host | Out-Null
& $pythonCmd "configs/setup-oauth.py"
Ok "Google OAuth setup xong"

# ------------------------------------------------------------
Write-Host @"

==========================================================
  QA Ops Suite setup hoàn tất!

  Next steps:
    1. Mở .env, điền LARK_APP_ID + LARK_APP_SECRET (nếu dùng Lark).
    2. Mở Claude Code tại thư mục project, gõ /help xem danh sách skill.
    3. Đọc README.md (Command Guide) để xem ví dụ prompt.

  Cấu hình Lark board (tuỳ chọn):
    Trong Claude Code, chạy: /update-board tracking bug: <lark_url>
==========================================================
"@
