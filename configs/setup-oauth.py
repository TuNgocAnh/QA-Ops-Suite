"""
QA Ops Suite - OAuth2 Setup
Run: python3 configs/setup-oauth.py

Chỉ cần chạy 1 lần. Script sẽ:
1. Mở browser để đăng nhập Google
2. Lưu token tại configs/google-oauth-token.json
3. Tự động cập nhật .env
4. Tạo Drive folder nếu chưa có
"""
import json
import os
import re
import sys
import argparse

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
from configs.env_loader import load_env, get_google_oauth_creds_data, get_oauth_token_path, get_drive_folder_id

load_env()

TOKEN_FILE = get_oauth_token_path()

# Auto-install dependencies if needed
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError:
    print("Installing required packages...")
    os.system("pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/drive.file'
]


def run_oauth_flow():
    """Run OAuth2 flow and return credentials."""
    oauth_data = get_google_oauth_creds_data()
    flow = InstalledAppFlow.from_client_config(oauth_data, SCOPES)
    try:
        creds = flow.run_local_server(port=0, open_browser=True)
    except Exception as e:
        print(f"Local server failed: {e}")
        print("\nFalling back to manual auth flow...")
        creds = flow.run_console()
    return creds


def save_token(creds):
    """Save OAuth token to JSON file. Returns refresh_token."""
    oauth_data = get_google_oauth_creds_data()
    token_data = {
        'access_token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': oauth_data['installed']['client_id'],
        'client_secret': oauth_data['installed']['client_secret'],
        'scopes': list(creds.scopes),
        'expiry_date': creds.expiry.isoformat() if creds.expiry else None
    }
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)
    print(f"[OK] Token saved: {TOKEN_FILE}")
    return creds.refresh_token


def update_env_file(refresh_token, folder_id=None):
    """Update .env file with refresh token and optional folder ID."""
    env_path = os.path.join(PROJECT_ROOT, '.env')

    # Read existing .env or create from example
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
    else:
        example_path = os.path.join(PROJECT_ROOT, '.env.example')
        if os.path.exists(example_path):
            with open(example_path, 'r') as f:
                content = f.read()
        else:
            content = '# QA Ops Suite Environment\n'

    # Update refresh token
    if 'GOOGLE_OAUTH_REFRESH_TOKEN=' in content:
        content = re.sub(
            r'GOOGLE_OAUTH_REFRESH_TOKEN=.*',
            f'GOOGLE_OAUTH_REFRESH_TOKEN={refresh_token}',
            content
        )
    else:
        content += f'\nGOOGLE_OAUTH_REFRESH_TOKEN={refresh_token}\n'

    # Update folder ID if provided
    if folder_id:
        if re.search(r'^#?\s*GOOGLE_DRIVE_FOLDER_ID=', content, re.MULTILINE):
            content = re.sub(
                r'#?\s*GOOGLE_DRIVE_FOLDER_ID=.*',
                f'GOOGLE_DRIVE_FOLDER_ID={folder_id}',
                content
            )
        else:
            content += f'\nGOOGLE_DRIVE_FOLDER_ID={folder_id}\n'

    with open(env_path, 'w') as f:
        f.write(content)
    print(f"[OK] .env updated: {env_path}")


def auto_create_drive_folder(creds):
    """Create a Drive folder for test case output."""
    oauth_data = get_google_oauth_creds_data()
    api_creds = Credentials(
        token=creds.token,
        refresh_token=creds.refresh_token,
        token_uri=creds.token_uri,
        client_id=oauth_data['installed']['client_id'],
        client_secret=oauth_data['installed']['client_secret'],
        scopes=SCOPES
    )
    drive_svc = build('drive', 'v3', credentials=api_creds)

    folder_metadata = {
        'name': 'QA Ops Suite - Test Cases',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive_svc.files().create(body=folder_metadata, fields='id,webViewLink').execute()
    folder_id = folder.get('id')
    print(f"[OK] Drive folder created: {folder.get('webViewLink')}")
    return folder_id


def main():
    parser = argparse.ArgumentParser(description='Setup OAuth2 for QA Ops Suite')
    parser.add_argument('--no-folder', action='store_true',
                       help='Skip auto-creating Drive folder')
    args = parser.parse_args()

    print("=" * 50)
    print("  QA Ops Suite - OAuth2 Setup")
    print("=" * 50)

    # Step 1: OAuth login
    print("\n[1/3] Google OAuth login...")
    print("Browser will open. Log in with your Google account.\n")
    creds = run_oauth_flow()
    refresh_token = save_token(creds)

    # Step 2: Drive folder
    folder_id = None
    existing_folder = get_drive_folder_id()

    if not existing_folder and not args.no_folder:
        print("\n[2/3] Creating Drive folder...")
        folder_id = auto_create_drive_folder(creds)
    elif existing_folder:
        print(f"\n[2/3] Using existing Drive folder: {existing_folder}")
    else:
        print("\n[2/3] Skipped Drive folder creation (--no-folder)")

    # Step 3: Update .env
    print("\n[3/3] Updating .env...")
    update_env_file(refresh_token, folder_id)

    print("\n" + "=" * 50)
    print("  SETUP COMPLETE!")
    print("=" * 50)
    print("\nBạn có thể dùng Claude Code với /cook, /plan-tc, /fix, /analyze, /ask, /est-sp.")
    print("Restart Claude Code nếu đang chạy.")


if __name__ == '__main__':
    main()
