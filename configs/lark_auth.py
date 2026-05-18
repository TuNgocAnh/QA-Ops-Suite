"""
Core Lark OAuth logic — shared bởi setup-lark-oauth.py (CLI) và lark-upload.py (script).

Main entry: `ensure_valid_token(force_browser=False)` =>
  1. Check .env: token còn hạn => return ngay
  2. Còn refresh_token => dùng refresh API (không cần browser)
  3. Hết đường => mở browser OAuth flow (port 3000)
  Trả về access_token string, luôn lưu .env sau khi refresh/auth xong.
"""
import http.server
import os
import sys
import threading
import urllib.parse
import webbrowser

try:
    import requests
except ImportError:
    os.system("pip3 install requests")
    import requests

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from configs.env_loader import (  # noqa: E402
    load_env,
    get_lark_app_credentials,
    get_lark_user_token_state,
    save_lark_user_token,
)

DOMAIN = "https://open.larksuite.com"
CALLBACK_PATH = "/callback"
DEFAULT_PORT = 3000

# Full scope list — sync với .claude/docs/lark-scopes-reference.md
FULL_SCOPES = [
    # Tenant-level
    "board:whiteboard:node:read",
    "docs:permission.member:readonly", "docs:permission.setting:readonly",
    "drive:file.meta.sec_label.read_only", "drive:file:view_record:readonly",
    "slides:presentation:read",
    "wiki:setting:read", "wiki:space:read",
    # Base / Bitable
    "base:app:read", "base:app:update",
    "base:collaborator:read",
    "base:dashboard:read", "base:dashboard:update",
    "base:field:create", "base:field:read", "base:field:update",
    "base:field_group:create",
    "base:form:create", "base:form:read", "base:form:update",
    "base:history:read",
    "base:record:create", "base:record:read",
    "base:record:retrieve", "base:record:update",
    "base:role:create", "base:role:read",
    "base:table:create", "base:table:read", "base:table:update",
    "base:view:read", "base:view:write_only",
    "base:workflow:create", "base:workflow:read",
    "base:workflow:update", "base:workflow:write",
    "base:workspace:list",
    "bitable:app", "bitable:app:readonly",
    # Task API v2
    "task:attachment:read", "task:attachment:write",
    "task:comment:read", "task:comment:write",
    "task:custom_field:read", "task:custom_field:write",
    "task:section:read", "task:section:write",
    "task:task:read", "task:task:write", "task:task:writeonly",
    "task:tasklist:read", "task:tasklist:write",
    # Drive
    "drive:drive", "drive:drive:readonly",
    "drive:drive.metadata:readonly", "drive:drive.search:readonly",
    "drive:file", "drive:file:readonly",
    "drive:file:upload", "drive:file:download",
    "drive:export:readonly",
    "drive:drive:version", "drive:drive:version:readonly",
    # Docs
    "docs:doc", "docs:doc:readonly",
    "docs:document.comment:create", "docs:document.comment:read",
    "docs:document.comment:update",
    "docs:document.content:read",
    "docs:document.media:download", "docs:document.media:upload",
    "docs:document:export", "docs:document:import",
    # Docx
    "docx:document", "docx:document:readonly",
    "docx:document:create", "docx:document:write_only",
    # Sheets
    "sheets:spreadsheet", "sheets:spreadsheet:create",
    "sheets:spreadsheet:read", "sheets:spreadsheet:write_only",
    # Wiki
    "wiki:wiki", "wiki:wiki:readonly",
    "wiki:node:read", "wiki:node:create", "wiki:node:update",
    # Space
    "space:document:retrieve", "space:folder:create",
]
SCOPE_STR = " ".join(FULL_SCOPES)


def _require_credentials():
    app_id, app_secret = get_lark_app_credentials()
    if not app_id or not app_secret:
        raise RuntimeError(
            "LARK_APP_ID / LARK_APP_SECRET chưa set trong .env. "
            "Lấy từ Lark Developer Console => điền vào .env."
        )
    return app_id, app_secret


def get_app_access_token(app_id, app_secret):
    resp = requests.post(
        f"{DOMAIN}/open-apis/auth/v3/app_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=15,
    )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Failed to get app_access_token: {data}")
    return data["app_access_token"]


def refresh_user_token(app_access_token, refresh_token):
    """Return dict token_info or None if refresh failed."""
    resp = requests.post(
        f"{DOMAIN}/open-apis/authen/v1/oidc/refresh_access_token",
        headers={"Authorization": f"Bearer {app_access_token}"},
        json={"grant_type": "refresh_token", "refresh_token": refresh_token},
        timeout=15,
    )
    data = resp.json()
    if data.get("code") != 0:
        print(f"[WARN] Refresh token failed: code={data.get('code')}, msg={data.get('msg')}")
        return None
    return data["data"]


def browser_oauth_flow(app_id, app_access_token, port=DEFAULT_PORT):
    """Mở browser authorize + nhận code + đổi access_token.
    Redirect URI phải khớp với cái đã đăng ký trong Lark Developer Console
    (mặc định localhost:3000/callback). Nếu port bận => user phải kill process
    đang giữ nó."""
    redirect_uri = f"http://localhost:{port}{CALLBACK_PATH}"
    auth_code = {"value": None, "error": None}
    server_ready = threading.Event()

    class OAuthHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            code = params.get("code", [None])[0]
            error = params.get("error", [None])[0]
            if code:
                auth_code["value"] = code
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    (
                        "<html><body style='font-family:sans-serif;padding:40px'>"
                        "<h2>Lark authorization thành công!</h2>"
                        "<p>Bạn có thể đóng tab này.</p></body></html>"
                    ).encode("utf-8")
                )
            else:
                auth_code["error"] = error or "missing_code"
                self.send_response(400)
                self.end_headers()
                self.wfile.write((auth_code["error"] or "error").encode())

        def log_message(self, fmt, *args):
            pass

    try:
        server = http.server.HTTPServer(("localhost", port), OAuthHandler)
    except OSError as e:
        raise RuntimeError(
            f"Port {port} đang bị chiếm. Kill process đó rồi thử lại.\n"
            f"  macOS/Linux:  lsof -ti :{port} | xargs kill -9\n"
            f"Detail: {e}"
        )

    auth_url = (
        f"{DOMAIN}/open-apis/authen/v1/authorize"
        f"?app_id={app_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&scope={urllib.parse.quote(SCOPE_STR)}"
        f"&state=qaopssuite"
    )

    def serve():
        server_ready.set()
        server.handle_request()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    server_ready.wait()

    print("\n[AUTH] Opening browser for Lark authorization...")
    print(f"       Redirect URI: {redirect_uri}")
    print(f"       Scopes: {len(FULL_SCOPES)} full permissions")
    print(f"\n       If browser does not open, paste this URL:\n       {auth_url}\n")
    webbrowser.open(auth_url)

    thread.join(timeout=300)
    server.server_close()

    if not auth_code["value"]:
        raise RuntimeError(
            "OAuth timeout — không nhận được authorization code sau 5 phút. "
            f"Error: {auth_code['error']}"
        )

    resp = requests.post(
        f"{DOMAIN}/open-apis/authen/v1/oidc/access_token",
        headers={"Authorization": f"Bearer {app_access_token}"},
        json={"grant_type": "authorization_code", "code": auth_code["value"]},
        timeout=15,
    )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Failed to exchange code: {data}")
    return data["data"]


def ensure_valid_token(force_browser=False, verbose=True):
    """Core entry: đảm bảo .env có LARK_USER_ACCESS_TOKEN còn hạn.
    Returns access_token string."""
    load_env()
    state = get_lark_user_token_state()

    if not force_browser and state["is_valid"]:
        if verbose:
            print(f"[OK] Token vẫn còn hạn đến {state['expiry'].isoformat(timespec='seconds')}.")
        return state["access_token"]

    app_id, app_secret = _require_credentials()
    app_token = get_app_access_token(app_id, app_secret)

    if not force_browser and state["refresh_token"]:
        if verbose:
            print("[INFO] Access token hết hạn, thử refresh bằng refresh_token...")
        token_info = refresh_user_token(app_token, state["refresh_token"])
        if token_info:
            expires_in = token_info.get("expires_in", 7200)
            expiry = save_lark_user_token(
                access_token=token_info["access_token"],
                refresh_token=token_info.get("refresh_token") or state["refresh_token"],
                expires_in=expires_in,
            )
            if verbose:
                print(f"[OK] Refresh thành công, token mới hết hạn: {expiry}")
            return token_info["access_token"]
        if verbose:
            print("[WARN] Refresh fail => fallback sang browser flow.")

    if verbose:
        print("[INFO] Bắt đầu browser OAuth flow...")
    token_info = browser_oauth_flow(app_id, app_token)
    expires_in = token_info.get("expires_in", 7200)
    expiry = save_lark_user_token(
        access_token=token_info["access_token"],
        refresh_token=token_info.get("refresh_token", ""),
        expires_in=expires_in,
    )
    if verbose:
        print(f"[OK] Auth thành công, token hết hạn: {expiry}")
        print(f"     Scopes granted: {len(FULL_SCOPES)}")
    return token_info["access_token"]
