"""
QA Ops Suite - Lark OAuth2 Manager (CLI)

Usage:
  python3 configs/setup-lark-oauth.py           # auto: valid => skip, expired => refresh, else => browser
  python3 configs/setup-lark-oauth.py --force   # force browser flow (ignore existing token)
  python3 configs/setup-lark-oauth.py --status  # print current token state, do nothing

Token được lưu vào .env (3 biến):
  LARK_USER_ACCESS_TOKEN    - ~2 giờ lifetime
  LARK_USER_REFRESH_TOKEN   - ~30 ngày lifetime (dùng để auto-refresh)
  LARK_USER_TOKEN_EXPIRY    - ISO timestamp

.mcp.json đọc ${LARK_USER_ACCESS_TOKEN} qua -u flag => MCP dùng trực tiếp,
không còn --oauth flow (không còn link 60 giây).

Khi token hết hạn:
  - Còn refresh_token hợp lệ => chạy lại script không cần browser
  - refresh_token cũng hết => script tự mở browser
Sau khi script xong => Reload VSCode Window để MCP server pickup token mới.
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from configs.env_loader import get_lark_app_credentials, get_lark_user_token_state  # noqa: E402
from configs.lark_auth import ensure_valid_token, FULL_SCOPES  # noqa: E402


def print_status():
    state = get_lark_user_token_state()
    app_id, app_secret = get_lark_app_credentials()
    print("=" * 55)
    print("  Lark OAuth Token Status")
    print("=" * 55)
    print(f"  App ID:          {app_id or '(not set)'}")
    print(f"  App Secret:      {'(set)' if app_secret else '(not set)'}")
    print(f"  Access Token:    {'(set)' if state['access_token'] else '(empty)'}")
    print(f"  Refresh Token:   {'(set)' if state['refresh_token'] else '(empty)'}")
    print(f"  Expiry:          {state['expiry'].isoformat(timespec='seconds') if state['expiry'] else '(unknown)'}")
    print(f"  Is valid:        {state['is_valid']}")
    print(f"  Scopes requested: {len(FULL_SCOPES)}")
    print("=" * 55)


def main():
    args = sys.argv[1:]
    if "--status" in args:
        print_status()
        return
    force = "--force" in args
    print("=" * 55)
    print("  QA Ops Suite - Lark OAuth Manager")
    print("=" * 55)
    try:
        ensure_valid_token(force_browser=force)
    except Exception as e:
        print(f"\n[ERR] {e}")
        sys.exit(1)
    print("\n[DONE] Reload VSCode Window để MCP server pickup token mới.")


if __name__ == "__main__":
    main()
