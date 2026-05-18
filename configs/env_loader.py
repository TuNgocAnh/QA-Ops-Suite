"""
Load environment variables from .env file.

User phải tự tạo Google OAuth Desktop client và set vào .env:
  GOOGLE_SHEETS_CLIENT_ID, GOOGLE_SHEETS_CLIENT_SECRET, GOOGLE_PROJECT_ID

Hướng dẫn: xem .env.example hoặc README "Google Cloud Setup".

Usage: from configs.env_loader import load_env
"""
import os
from datetime import datetime, timedelta


def _project_root():
    """Return absolute path to project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env():
    """Load .env file from project root into os.environ."""
    env_path = os.path.join(_project_root(), '.env')
    if not os.path.exists(env_path):
        # .env is optional — defaults are built-in
        return
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            # Remove surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            os.environ.setdefault(key, value)


def get_google_oauth_creds_data():
    """Return OAuth credentials dict from .env. Raises if not configured."""
    load_env()
    client_id = os.environ.get('GOOGLE_SHEETS_CLIENT_ID', '').strip()
    client_secret = os.environ.get('GOOGLE_SHEETS_CLIENT_SECRET', '').strip()
    project_id = os.environ.get('GOOGLE_PROJECT_ID', '').strip()
    if not client_id or not client_secret:
        raise RuntimeError(
            "Google OAuth chưa cấu hình. Tạo Desktop OAuth client tại "
            "https://console.cloud.google.com/apis/credentials rồi điền "
            "GOOGLE_SHEETS_CLIENT_ID + GOOGLE_SHEETS_CLIENT_SECRET vào .env. "
            "Xem .env.example hoặc README mục 'Google Cloud Setup' để biết chi tiết."
        )
    return {
        'installed': {
            'client_id': client_id,
            'project_id': project_id,
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            'client_secret': client_secret,
            'redirect_uris': ['http://localhost']
        }
    }


def get_oauth_token_path():
    """Return path to OAuth token JSON file."""
    return os.path.join(_project_root(), 'configs', 'google-oauth-token.json')


def get_oauth_credentials_path():
    """Return path to OAuth client credentials JSON file (for MCP server)."""
    return os.path.join(_project_root(), 'configs', 'oauth-credentials.json')


def get_drive_folder_id():
    """Return Google Drive folder ID from env, or None if not set."""
    load_env()
    folder_id = os.environ.get('GOOGLE_DRIVE_FOLDER_ID', '').strip()
    return folder_id if folder_id and folder_id != 'your_folder_id_here' else None


def get_lark_drive_folder_id():
    """Return Lark Drive folder ID from env, or None if not set."""
    load_env()
    folder_id = os.environ.get('LARK_DRIVE_FOLDER_ID', '').strip()
    return folder_id if folder_id else None


def get_user_role():
    """Return user role from env for Story Point estimation. Default: 'senior'.
    Valid values: junior, mid, senior, lead."""
    load_env()
    role = os.environ.get('USER_ROLE', 'senior').strip().lower()
    valid_roles = ('junior', 'mid', 'senior', 'lead')
    return role if role in valid_roles else 'senior'


# =============================================================
# Lark Bitable - Board IDs
# =============================================================

def get_lark_bug_board():
    """Return (base_id, table_id) for bug tracking board, or (None, None)."""
    load_env()
    base_id = os.environ.get('LARK_BUG_BASE_ID', '').strip()
    table_id = os.environ.get('LARK_BUG_TABLE_ID', '').strip()
    return (base_id or None, table_id or None)


def get_lark_bug_base_name():
    """Return bug board base name from env, or None if not set."""
    load_env()
    base_name = os.environ.get('LARK_BUG_BASE_NAME', '').strip()
    return base_name or None


def get_lark_task_board():
    """Return (base_id, table_id) for task/sprint board, or (None, None)."""
    load_env()
    base_id = os.environ.get('LARK_TASK_BASE_ID', '').strip()
    table_id = os.environ.get('LARK_TASK_TABLE_ID', '').strip()
    return (base_id or None, table_id or None)


def get_lark_test_board():
    """Return (base_id, table_id) for test execution board, or (None, None)."""
    load_env()
    base_id = os.environ.get('LARK_TEST_BASE_ID', '').strip()
    table_id = os.environ.get('LARK_TEST_TABLE_ID', '').strip()
    return (base_id or None, table_id or None)


def get_lark_board_full(board_type='bug'):
    """Return full board config dict for a given board type.
    board_type: 'bug', 'task', or 'test'.
    Returns dict with keys: base_name, base_id, table_id, view_id, wiki_token, domain.
    All values may be None if not configured."""
    load_env()
    prefix = f'LARK_{board_type.upper()}'
    base_name = os.environ.get(f'{prefix}_BASE_NAME', '').strip() or None
    base_id = os.environ.get(f'{prefix}_BASE_ID', '').strip() or None
    table_id = os.environ.get(f'{prefix}_TABLE_ID', '').strip() or None
    view_id = os.environ.get(f'{prefix}_VIEW_ID', '').strip() or None
    wiki_token = os.environ.get(f'{prefix}_WIKI_TOKEN', '').strip() or None
    domain = os.environ.get('LARK_DOMAIN', 'sobanhang.sg.larksuite.com').strip()
    return {
        'base_name': base_name,
        'base_id': base_id,
        'table_id': table_id,
        'view_id': view_id,
        'wiki_token': wiki_token,
        'domain': domain,
    }


def get_lark_record_url(board_type='bug', record_id=None):
    """Build a direct record URL from board config.
    Returns URL string or None if wiki_token not configured."""
    cfg = get_lark_board_full(board_type)
    if not cfg['wiki_token'] or not cfg['table_id']:
        return None
    url = f"https://{cfg['domain']}/wiki/{cfg['wiki_token']}?table={cfg['table_id']}"
    if cfg['view_id']:
        url += f"&view={cfg['view_id']}"
    if record_id:
        url += f"&record={record_id}"
    return url


def get_test_account():
    """Return test account string from env, or None if not set.
    Format: 'phone - password' (e.g., '0923267268 - 123456')."""
    load_env()
    account = os.environ.get('TEST_ACCOUNT', '').strip()
    return account if account else None


def get_default_version():
    """Return DEFAULT_VERSION from env (e.g. 'stg-1.0.51'), or None if not set."""
    load_env()
    v = os.environ.get('DEFAULT_VERSION', '').strip()
    return v if v else None


def get_default_sprint():
    """Return DEFAULT_SPRINT from env (e.g. '1-2026/4'), or None if not set."""
    load_env()
    s = os.environ.get('DEFAULT_SPRINT', '').strip()
    return s if s else None


def update_env_vars(updates, env_path=None):
    """Update multiple KEY=VALUE pairs in .env, preserving comments & ordering.
    - Existing keys => replace value in-place
    - New keys => appended at end
    - Values with whitespace or special chars are quoted with double quotes
    - Commented form `# KEY=...` is replaced with uncommented `KEY=...`
    """
    if env_path is None:
        env_path = os.path.join(_project_root(), '.env')

    def _quote(v):
        v = str(v)
        if v == '' or any(c in v for c in ' \t"\'#'):
            return '"' + v.replace('"', '\\"') + '"'
        return v

    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()

    pending = dict(updates)
    out = []
    for raw in lines:
        stripped = raw.strip()
        handled = False
        if stripped and '=' in stripped:
            # Match both `KEY=...` and `# KEY=...` / `#KEY=...`
            body = stripped.lstrip('#').strip() if stripped.startswith('#') else stripped
            if '=' in body:
                key = body.split('=', 1)[0].strip()
                if key in pending:
                    out.append(f"{key}={_quote(pending.pop(key))}\n")
                    handled = True
        if not handled:
            out.append(raw if raw.endswith('\n') else raw + '\n')

    if pending:
        if out and not out[-1].endswith('\n'):
            out[-1] = out[-1] + '\n'
        if out and out[-1].strip() != '':
            out.append('\n')
        for k, v in pending.items():
            out.append(f"{k}={_quote(v)}\n")

    os.makedirs(os.path.dirname(env_path) or '.', exist_ok=True)
    with open(env_path, 'w') as f:
        f.writelines(out)


def get_lark_app_credentials():
    """Return (app_id, app_secret) from .env, or (None, None) if missing."""
    load_env()
    app_id = os.environ.get('LARK_APP_ID', '').strip()
    app_secret = os.environ.get('LARK_APP_SECRET', '').strip()
    return (app_id or None, app_secret or None)


def get_lark_user_token_state():
    """Return dict with current Lark user token state from .env.
    Keys: access_token, refresh_token, expiry (datetime|None), is_valid (bool).
    is_valid = has access_token AND expiry > now + 5min."""
    load_env()
    access_token = os.environ.get('LARK_USER_ACCESS_TOKEN', '').strip()
    refresh_token = os.environ.get('LARK_USER_REFRESH_TOKEN', '').strip()
    expiry_str = os.environ.get('LARK_USER_TOKEN_EXPIRY', '').strip()
    expiry = None
    if expiry_str:
        try:
            expiry = datetime.fromisoformat(expiry_str)
        except ValueError:
            expiry = None
    is_valid = bool(access_token and expiry and expiry > datetime.now() + timedelta(minutes=5))
    return {
        'access_token': access_token or None,
        'refresh_token': refresh_token or None,
        'expiry': expiry,
        'is_valid': is_valid,
    }


def save_lark_user_token(access_token, refresh_token, expires_in=7200):
    """Persist Lark user token to .env.
    expires_in: seconds from now. Default 7200 (2h) per Lark docs."""
    expiry = (datetime.now() + timedelta(seconds=int(expires_in))).isoformat(timespec='seconds')
    update_env_vars({
        'LARK_USER_ACCESS_TOKEN': access_token,
        'LARK_USER_REFRESH_TOKEN': refresh_token or '',
        'LARK_USER_TOKEN_EXPIRY': expiry,
    })
    # Reflect in current process env so subsequent calls in same run see fresh value
    os.environ['LARK_USER_ACCESS_TOKEN'] = access_token
    if refresh_token:
        os.environ['LARK_USER_REFRESH_TOKEN'] = refresh_token
    os.environ['LARK_USER_TOKEN_EXPIRY'] = expiry
    return expiry


def get_lark_bug_field(field_key, default=None):
    """Return custom field name for bug board, or default.
    field_key: title, description, status, priority, assignee, attachment, reporter, created."""
    _defaults = {
        'title': 'Title',
        'description': 'Description',
        'status': 'Status',
        'priority': 'Priority',
        'assignee': 'Assignee',
        'attachment': 'Attachment',
        'reporter': 'Reporter',
        'created': 'Created',
    }
    load_env()
    env_key = f'LARK_BUG_FIELD_{field_key.upper()}'
    value = os.environ.get(env_key, '').strip()
    return value if value else (default or _defaults.get(field_key, field_key.capitalize()))
