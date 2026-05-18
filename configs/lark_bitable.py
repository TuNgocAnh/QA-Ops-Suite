"""
Lark Bitable helper - Upload attachments for Bitable records.

MCP tools handle all Bitable CRUD (list/get/create/update/delete records).
This script handles what MCP cannot: file upload for attachment fields.

Usage:
  python3 configs/lark_bitable.py upload <file_path>
  python3 configs/lark_bitable.py upload <file_path> --base <base_id>

Programmatic:
  from configs.lark_bitable import upload_bitable_attachment
  file_token = upload_bitable_attachment("screenshot.png")
"""
import json
import os
import sys

try:
    import requests
except ImportError:
    os.system("pip3 install requests")
    import requests

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from configs.env_loader import (
    get_lark_bug_board,
    get_lark_task_board,
    get_lark_test_board,
    get_lark_bug_field,
    get_lark_board_full,
    get_lark_record_url,
    load_env,
)

DOMAIN = "https://open.larksuite.com"
TOKEN_FILE = os.path.join(PROJECT_ROOT, "configs", "lark-oauth-token.json")


# =============================================================
# Token reuse from lark-upload.py OAuth cache
# =============================================================

def _get_cached_token():
    """Load user_access_token from shared OAuth cache."""
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        data = json.load(f)
    from datetime import datetime, timedelta
    expiry = data.get("expiry")
    if expiry and datetime.fromisoformat(expiry) > datetime.now() + timedelta(minutes=2):
        return data["access_token"]
    # Try refresh
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        return None
    try:
        from configs import env_loader  # noqa: avoid circular
        # Read app credentials from .mcp.json
        mcp_path = os.path.join(PROJECT_ROOT, ".mcp.json")
        with open(mcp_path, "r") as f:
            mcp = json.load(f)
        args = mcp["mcpServers"]["lark-mcp"]["args"]
        app_id = args[args.index("-a") + 1]
        app_secret = args[args.index("-s") + 1]
        # Get app_access_token
        resp = requests.post(
            f"{DOMAIN}/open-apis/auth/v3/app_access_token/internal",
            json={"app_id": app_id, "app_secret": app_secret},
        )
        app_token = resp.json().get("app_access_token")
        if not app_token:
            return None
        # Refresh user token
        resp = requests.post(
            f"{DOMAIN}/open-apis/authen/v1/oidc/refresh_access_token",
            headers={"Authorization": f"Bearer {app_token}"},
            json={"grant_type": "refresh_token", "refresh_token": refresh_token},
        )
        rdata = resp.json()
        if rdata.get("code") != 0:
            return None
        token_info = rdata["data"]
        expires_in = token_info.get("expires_in", 7200)
        cache = {
            "access_token": token_info["access_token"],
            "refresh_token": token_info.get("refresh_token", ""),
            "expiry": (datetime.now() + timedelta(seconds=expires_in)).isoformat(),
            "token_type": "Bearer",
        }
        with open(TOKEN_FILE, "w") as f:
            json.dump(cache, f, indent=2)
        return token_info["access_token"]
    except Exception:
        return None


def get_token():
    """Get valid user_access_token. Raises if unavailable."""
    token = _get_cached_token()
    if not token:
        print("[ERROR] Lark token expired. Run: python3 configs/lark-upload.py <any_file> <folder>")
        print("        to re-authenticate via browser, then retry.")
        raise RuntimeError("No valid Lark user_access_token")
    return token


# =============================================================
# Bitable Attachment Upload
# =============================================================

def upload_bitable_attachment(file_path, app_token=None):
    """Upload a file as Bitable attachment.

    Uses /drive/v1/medias/upload_all with parent_type='bitable_image' (images)
    or 'bitable_file' (other files).

    Args:
        file_path: Path to file (image, video, etc.)
        app_token: Bitable app_token. If None, reads LARK_BUG_BASE_ID from .env.

    Returns:
        dict: {"file_token": "xxx"} - use this in attachment field value.
    """
    if not os.path.isabs(file_path):
        file_path = os.path.join(PROJECT_ROOT, file_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not app_token:
        base_id, _ = get_lark_bug_board()
        app_token = base_id
    if not app_token:
        raise ValueError("No app_token provided and LARK_BUG_BASE_ID not set in .env")

    access_token = get_token()
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Determine parent_type by file extension
    _, ext = os.path.splitext(file_name)
    ext = ext.lower()
    image_exts = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg', '.ico'}
    parent_type = "bitable_image" if ext in image_exts else "bitable_file"

    print(f"[Upload] {file_name} ({file_size} bytes) as {parent_type}...")

    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{DOMAIN}/open-apis/drive/v1/medias/upload_all",
            headers={"Authorization": f"Bearer {access_token}"},
            data={
                "file_name": file_name,
                "parent_type": parent_type,
                "parent_node": app_token,
                "size": str(file_size),
            },
            files={"file": (file_name, f)},
        )

    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Bitable attachment upload failed: code={data.get('code')}, msg={data.get('msg')}")

    file_token = data["data"]["file_token"]
    print(f"[OK] Uploaded: file_token={file_token}")
    return {"file_token": file_token}


def upload_multiple_attachments(file_paths, app_token=None):
    """Upload multiple files, return list of {"file_token": "xxx"} dicts."""
    results = []
    for fp in file_paths:
        result = upload_bitable_attachment(fp, app_token)
        results.append(result)
    return results


# =============================================================
# Board config helpers (for agent prompts)
# =============================================================

def get_bug_board_config():
    """Return bug board config dict for use in agent prompts.
    Returns None if not configured."""
    cfg = get_lark_board_full('bug')
    if not cfg['base_id']:
        return None
    return {
        "base_name": cfg.get('base_name'),
        "base_id": cfg['base_id'],
        "table_id": cfg['table_id'],
        "view_id": cfg['view_id'],
        "wiki_token": cfg['wiki_token'],
        "domain": cfg['domain'],
        "fields": {
            "title": get_lark_bug_field("title"),
            "description": get_lark_bug_field("description"),
            "status": get_lark_bug_field("status"),
            "priority": get_lark_bug_field("priority"),
            "assignee": get_lark_bug_field("assignee"),
            "attachment": get_lark_bug_field("attachment"),
            "reporter": get_lark_bug_field("reporter"),
        },
    }


def get_task_board_config():
    """Return task board config dict."""
    cfg = get_lark_board_full('task')
    if not cfg['base_id']:
        return None
    return {
        "base_id": cfg['base_id'],
        "table_id": cfg['table_id'],
        "view_id": cfg['view_id'],
        "wiki_token": cfg['wiki_token'],
        "domain": cfg['domain'],
    }


def get_test_board_config():
    """Return test execution board config dict."""
    cfg = get_lark_board_full('test')
    if not cfg['base_id']:
        return None
    return {
        "base_id": cfg['base_id'],
        "table_id": cfg['table_id'],
        "view_id": cfg['view_id'],
        "wiki_token": cfg['wiki_token'],
        "domain": cfg['domain'],
    }


def print_board_status():
    """Print configured boards status."""
    board_types = [
        ("Bug Board", "bug"),
        ("Task Board", "task"),
        ("Test Board", "test"),
    ]
    print("=== Lark Bitable Boards ===")
    for name, btype in board_types:
        cfg = get_lark_board_full(btype)
        if cfg['base_id']:
            parts = [f"base={cfg['base_id']}", f"table={cfg['table_id'] or '(auto-detect)'}"]
            if cfg.get('base_name'):
                parts.insert(0, f"name={cfg['base_name']}")
            if cfg['view_id']:
                parts.append(f"view={cfg['view_id']}")
            if cfg['wiki_token']:
                parts.append(f"wiki={cfg['wiki_token']}")
            print(f"  [OK] {name}: {', '.join(parts)}")
        else:
            print(f"  [--] {name}: not configured")
    print()


# =============================================================
# CLI
# =============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 configs/lark_bitable.py status              # Show configured boards")
        print("  python3 configs/lark_bitable.py upload <file_path>  # Upload attachment")
        print("  python3 configs/lark_bitable.py upload <file_path> --base <base_id>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status":
        load_env()
        print_board_status()

    elif cmd == "upload":
        if len(sys.argv) < 3:
            print("Error: file_path required")
            sys.exit(1)
        file_path = sys.argv[2]
        app_token = None
        if "--base" in sys.argv:
            idx = sys.argv.index("--base")
            app_token = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        load_env()
        result = upload_bitable_attachment(file_path, app_token)
        print(json.dumps(result))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
