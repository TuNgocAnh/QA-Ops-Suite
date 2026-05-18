"""
Lark Drive - Smart upload with auto-conversion.
Usage: python3 configs/lark-upload.py <file_path> <folder_token> [--raw]

Behavior by file type:
  .xlsx/.xls/.csv  => Import as Lark Sheet (editable spreadsheet)
  .doc/.docx       => Import as Lark Doc (editable document)
  .md/.txt         => Import as Lark Doc (editable document)
  other files      => Upload as raw file (download only)
  --raw flag       => Force upload as raw file (no conversion)

Token management: dùng chung `.env` via configs/lark_auth.py
  LARK_USER_ACCESS_TOKEN còn hạn => dùng luôn
  Hết hạn nhưng có refresh_token => auto-refresh (không cần browser)
  Hết cả 2 => mở browser OAuth flow 1 lần
"""
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip3 install requests")
    import requests

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
from configs.lark_auth import ensure_valid_token  # noqa: E402

DOMAIN = "https://open.larksuite.com"

# ============================================================
# File type => Lark import type mapping
# ============================================================
# Maps file extension to (lark_type, obj_type_for_media_upload)
# lark_type: used in import_tasks API "type" field
# obj_type: used in medias/upload_all "extra.obj_type" field
IMPORT_TYPE_MAP = {
    # Spreadsheet => Lark Sheet
    '.xlsx': ('sheet', 'sheet'),
    '.xls':  ('sheet', 'sheet'),
    '.csv':  ('sheet', 'sheet'),
    # Document => Lark Doc
    '.docx': ('docx', 'docx'),
    '.doc':  ('docx', 'docx'),
    '.md':   ('docx', 'docx'),
    '.txt':  ('docx', 'docx'),
}

LARK_TYPE_LABELS = {
    'sheet': 'Lark Sheet',
    'docx': 'Lark Doc',
}


def get_import_info(file_path):
    """Determine import type from file extension.
    Returns (lark_type, obj_type, label) or (None, None, None) if not importable."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext in IMPORT_TYPE_MAP:
        lark_type, obj_type = IMPORT_TYPE_MAP[ext]
        label = LARK_TYPE_LABELS.get(lark_type, lark_type)
        return lark_type, obj_type, label
    return None, None, None


# ============================================================
# Upload Methods
# ============================================================

def upload_raw_file(access_token, file_path, folder_token):
    """Upload file to Lark Drive as raw file (download-only, not editable).
    API: POST /open-apis/drive/v1/files/upload_all
    Scopes: drive:file, drive:file:upload
    """
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    print(f"Uploading {file_name} ({file_size} bytes) as raw file...")

    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{DOMAIN}/open-apis/drive/v1/files/upload_all",
            headers={"Authorization": f"Bearer {access_token}"},
            data={
                "file_name": file_name,
                "parent_type": "explorer",
                "parent_node": folder_token,
                "size": str(file_size),
            },
            files={"file": (file_name, f)},
        )

    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Upload failed: {data}")

    file_token = data["data"]["file_token"]
    file_url = f"https://sobanhang.sg.larksuite.com/file/{file_token}"
    print(f"[OK] Upload successful!")
    print(f"  File token: {file_token}")
    print(f"  URL: {file_url}")
    return file_token, file_url


def upload_for_import(access_token, file_path, folder_token, obj_type):
    """Upload file via /medias/upload_all for import (step 1 of import flow).
    API: POST /open-apis/drive/v1/medias/upload_all
    Scopes: docs:document.media:upload, drive:drive, sheets:spreadsheet
    Returns file_token (valid for ~5 minutes only).
    """
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    _, ext = os.path.splitext(file_name)
    file_ext = ext.lstrip('.').lower() or 'xlsx'

    print(f"[Step 1/3] Uploading {file_name} ({file_size} bytes) for import...")

    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{DOMAIN}/open-apis/drive/v1/medias/upload_all",
            headers={"Authorization": f"Bearer {access_token}"},
            data={
                "file_name": file_name,
                "parent_type": "ccm_import_open",
                "parent_node": folder_token,
                "size": str(file_size),
                "extra": json.dumps({"obj_type": obj_type, "file_extension": file_ext}),
            },
            files={"file": (file_name, f)},
        )

    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Media upload failed: {data}")

    file_token = data["data"]["file_token"]
    print(f"[OK] Media uploaded, file_token: {file_token}")
    return file_token


def create_import_task(access_token, file_token, file_name, folder_token, lark_type):
    """Create import task to convert uploaded file to Lark native format (step 2).
    API: POST /open-apis/drive/v1/import_tasks
    Scopes: drive:drive, sheets:spreadsheet (for sheet), docs:doc (for docx)
    Returns ticket for polling.
    """
    _, ext = os.path.splitext(file_name)
    file_ext = ext.lstrip('.').lower() or 'xlsx'
    display_name = os.path.splitext(file_name)[0]
    label = LARK_TYPE_LABELS.get(lark_type, lark_type)

    print(f"[Step 2/3] Creating import task: {display_name} => {label}...")

    resp = requests.post(
        f"{DOMAIN}/open-apis/drive/v1/import_tasks",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json={
            "file_extension": file_ext,
            "file_token": file_token,
            "type": lark_type,
            "file_name": display_name,
            "point": {
                "mount_type": 1,
                "mount_key": folder_token,
            },
        },
    )

    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Import task creation failed: {data}")

    ticket = data["data"]["ticket"]
    print(f"[OK] Import task created, ticket: {ticket}")
    return ticket


def poll_import_result(access_token, ticket, lark_type, max_wait=60):
    """Poll import task until complete (step 3).
    API: GET /open-apis/drive/v1/import_tasks/{ticket}
    Returns (token, url).
    """
    label = LARK_TYPE_LABELS.get(lark_type, lark_type)
    print(f"[Step 3/3] Waiting for {label} import to complete...")

    STATUS_NAMES = {
        0: "Success", 1: "Initializing", 2: "Processing",
        100: "Document encrypted", 104: "Tenant capacity insufficient",
        108: "Processing timeout", 110: "No permission",
        112: "Format error", 120: "File type error", 121: "File token expired",
    }

    # URL path by type
    URL_PATHS = {'sheet': 'sheets', 'docx': 'docx'}

    waited = 0
    while waited < max_wait:
        resp = requests.get(
            f"{DOMAIN}/open-apis/drive/v1/import_tasks/{ticket}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"Poll failed: {data}")

        result = data["data"]["result"]
        status = result.get("job_status", -1)
        status_name = STATUS_NAMES.get(status, f"Unknown({status})")

        if status == 0:
            doc_token = result.get("token", "")
            doc_url = result.get("url", "")
            if not doc_url and doc_token:
                url_path = URL_PATHS.get(lark_type, 'file')
                doc_url = f"https://sobanhang.sg.larksuite.com/{url_path}/{doc_token}"
            print(f"[OK] Import complete!")
            print(f"  Token: {doc_token}")
            print(f"  URL: {doc_url}")
            return doc_token, doc_url
        elif status in (1, 2):
            time.sleep(1)
            waited += 1
            continue
        else:
            raise Exception(f"Import failed: {status_name} (status={status})")

    raise Exception(f"Import timed out after {max_wait}s")


def import_file(access_token, file_path, folder_token):
    """Full import flow: upload => import task => poll result.
    Auto-detects target type from file extension.
    Returns (token, url).
    """
    file_name = os.path.basename(file_path)
    lark_type, obj_type, label = get_import_info(file_path)

    if not lark_type:
        raise Exception(f"File type not importable: {file_name}")

    print(f"Importing {file_name} as {label}...")

    # Step 1: Upload for import (file_token valid ~5 min)
    file_token = upload_for_import(access_token, file_path, folder_token, obj_type)

    # Step 2: Create import task
    ticket = create_import_task(access_token, file_token, file_name, folder_token, lark_type)

    # Step 3: Poll for result
    doc_token, doc_url = poll_import_result(access_token, ticket, lark_type)

    return doc_token, doc_url


# ============================================================
# Main
# ============================================================

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 configs/lark-upload.py <file_path> <folder_token> [--raw]")
        print("       --raw: Force upload as raw file (no conversion)")
        print()
        print("Auto-detection:")
        print("  .xlsx/.xls/.csv  => Lark Sheet (editable)")
        print("  .doc/.docx/.md/.txt => Lark Doc (editable)")
        print("  other files      => Raw file (download only)")
        print()
        print("Example: python3 configs/lark-upload.py results/skt/skt-final.xlsx QPlNfzLdWlhJuGdp01YlcWsvglg")
        sys.exit(1)

    file_path = sys.argv[1]
    folder_token = sys.argv[2]
    raw_mode = "--raw" in sys.argv

    if not os.path.isabs(file_path):
        file_path = os.path.join(PROJECT_ROOT, file_path)

    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    # Determine upload strategy
    lark_type, _, label = get_import_info(file_path)
    can_import = lark_type is not None and not raw_mode

    print("=" * 50)
    if can_import:
        print(f"  Lark Drive - Import as {label}")
    else:
        print("  Lark Drive - Raw File Upload")
    print("=" * 50)

    # ensure_valid_token: valid => reuse; expired but refreshable => refresh;
    # otherwise => browser. Writes token back to .env automatically.
    access_token = ensure_valid_token()

    def do_upload(tok):
        if can_import:
            return import_file(tok, file_path, folder_token)
        else:
            return upload_raw_file(tok, file_path, folder_token)

    try:
        _, result_url = do_upload(access_token)
    except Exception as e:
        error_msg = str(e)
        if "99991668" in error_msg or "99991679" in error_msg or "permission" in error_msg.lower():
            print("[WARN] Token expired or no permission, forcing re-auth...")
            access_token = ensure_valid_token(force_browser=True)
            _, result_url = do_upload(access_token)
        else:
            raise

    print("\n" + "=" * 50)
    if can_import:
        print(f"  IMPORT COMPLETE! (Editable {label})")
    else:
        print("  UPLOAD COMPLETE! (Raw file)")
    print(f"  URL: {result_url}")
    print("=" * 50)


if __name__ == "__main__":
    main()
