"""
QA Ops Suite - Google API wrapper (Python-first, giống lark_api.py)

Hỗ trợ:
- read_doc(doc_id_or_url) -> {"title", "content"}  : đọc Google Docs
- read_sheet(sheet_id_or_url, range) -> list[list] : đọc Google Sheets

Token tự refresh từ google-oauth-token.json. Hết hạn refresh => yêu cầu user
chạy lại `python configs/setup-oauth.py`.

CLI debug:
    python configs/google_api.py read-doc <doc_url_or_id>
    python configs/google_api.py read-sheet <sheet_url_or_id> [range]
"""

import json
import os
import re
import sys
from typing import Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from configs.env_loader import (
    load_env, get_google_oauth_creds_data, get_oauth_token_path,
)

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Installing google-api-python-client...", file=sys.stderr)
    os.system("pip install google-auth google-auth-oauthlib google-api-python-client")
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError


SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
]


def _extract_id(url_or_id: str, kind: str = 'doc') -> str:
    """Extract document/sheet ID from URL or return as-is if already an ID."""
    if not url_or_id:
        raise ValueError("Empty URL/ID")
    patterns = {
        'doc': r'/document/d/([a-zA-Z0-9_-]+)',
        'sheet': r'/spreadsheets/d/([a-zA-Z0-9_-]+)',
    }
    m = re.search(patterns.get(kind, patterns['doc']), url_or_id)
    if m:
        return m.group(1)
    if re.fullmatch(r'[a-zA-Z0-9_-]{20,}', url_or_id):
        return url_or_id
    raise ValueError(f"Cannot extract {kind} ID from: {url_or_id}")


def get_creds() -> Credentials:
    """Load OAuth creds, refresh if expired. Raises if token missing or refresh fails."""
    load_env()
    token_path = get_oauth_token_path()
    if not os.path.exists(token_path):
        raise RuntimeError(
            f"Không tìm thấy {token_path}. Chạy `python configs/setup-oauth.py` để OAuth lần đầu."
        )

    with open(token_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    oauth_data = get_google_oauth_creds_data()
    creds = Credentials(
        token=data.get('access_token'),
        refresh_token=data.get('refresh_token'),
        token_uri=data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=oauth_data['installed']['client_id'],
        client_secret=oauth_data['installed']['client_secret'],
        scopes=data.get('scopes', SCOPES),
    )

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                data['access_token'] = creds.token
                if creds.expiry:
                    data['expiry_date'] = creds.expiry.isoformat()
                with open(token_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                raise RuntimeError(
                    f"Refresh token thất bại ({e}). Xóa {token_path} và chạy lại "
                    f"`python configs/setup-oauth.py`."
                )
        else:
            raise RuntimeError(
                f"Token không hợp lệ. Xóa {token_path} và chạy lại `python configs/setup-oauth.py`."
            )

    return creds


def _has_scope(creds: Credentials, scope: str) -> bool:
    return scope in (creds.scopes or [])


def _require_scope(creds: Credentials, scope: str, feature: str):
    if not _has_scope(creds, scope):
        raise RuntimeError(
            f"Token thiếu scope '{scope}' (cần cho {feature}). "
            f"Xóa configs/google-oauth-token.json và chạy lại `python configs/setup-oauth.py` "
            f"để re-auth với scope mới."
        )


def _flatten_doc_content(body: dict) -> str:
    """Convert Google Docs body.content to plain text, giữ structure cơ bản."""
    lines = []
    for element in body.get('content', []):
        if 'paragraph' in element:
            para = element['paragraph']
            style = para.get('paragraphStyle', {}).get('namedStyleType', '')
            text_parts = []
            for el in para.get('elements', []):
                tr = el.get('textRun')
                if tr:
                    text_parts.append(tr.get('content', ''))
            text = ''.join(text_parts).rstrip('\n')
            if not text:
                lines.append('')
                continue
            if style.startswith('HEADING_'):
                level = style.replace('HEADING_', '')
                try:
                    n = int(level)
                except ValueError:
                    n = 1
                lines.append(f"\n{'#' * min(n, 6)} {text}\n")
            elif style == 'TITLE':
                lines.append(f"\n# {text}\n")
            elif style == 'SUBTITLE':
                lines.append(f"\n## {text}\n")
            else:
                lines.append(text)
        elif 'table' in element:
            for row in element['table'].get('tableRows', []):
                cells = []
                for cell in row.get('tableCells', []):
                    cell_text = _flatten_doc_content(cell).strip().replace('\n', ' ')
                    cells.append(cell_text)
                lines.append('| ' + ' | '.join(cells) + ' |')
            lines.append('')
        elif 'tableOfContents' in element:
            toc = element['tableOfContents']
            lines.append(_flatten_doc_content(toc))
    return '\n'.join(lines)


def read_doc(doc_id_or_url: str) -> dict:
    """Read a Google Doc. Returns {'title': str, 'doc_id': str, 'content': str}."""
    doc_id = _extract_id(doc_id_or_url, kind='doc')
    creds = get_creds()
    _require_scope(creds, 'https://www.googleapis.com/auth/documents.readonly', 'read_doc')

    service = build('docs', 'v1', credentials=creds, cache_discovery=False)
    try:
        doc = service.documents().get(documentId=doc_id).execute()
    except HttpError as e:
        status = getattr(e, 'status_code', None) or getattr(e.resp, 'status', None)
        if status in (401, 403):
            raise RuntimeError(
                f"Không có quyền đọc Doc {doc_id} (HTTP {status}). "
                f"Kiểm tra: (1) Doc đã share cho account login chưa, "
                f"(2) Token có scope documents.readonly chưa."
            )
        if status == 404:
            raise RuntimeError(f"Doc {doc_id} không tồn tại hoặc không truy cập được.")
        raise

    return {
        'doc_id': doc_id,
        'title': doc.get('title', ''),
        'content': _flatten_doc_content(doc.get('body', {})).strip(),
    }


def read_sheet(sheet_id_or_url: str, range_a1: Optional[str] = None) -> dict:
    """Read a Google Sheet. Returns {'sheet_id', 'title', 'range', 'values'}."""
    sheet_id = _extract_id(sheet_id_or_url, kind='sheet')
    creds = get_creds()
    _require_scope(creds, 'https://www.googleapis.com/auth/spreadsheets.readonly', 'read_sheet')

    service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
    meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    title = meta.get('properties', {}).get('title', '')

    if not range_a1:
        first_sheet = meta['sheets'][0]['properties']['title']
        range_a1 = first_sheet

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=range_a1
    ).execute()
    return {
        'sheet_id': sheet_id,
        'title': title,
        'range': result.get('range', range_a1),
        'values': result.get('values', []),
    }


def _cli():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'read-doc':
        if len(sys.argv) < 3:
            print("Usage: read-doc <doc_url_or_id>", file=sys.stderr)
            sys.exit(1)
        result = read_doc(sys.argv[2])
        print(f"=== {result['title']} ===")
        print(f"Doc ID: {result['doc_id']}\n")
        print(result['content'])
    elif cmd == 'read-sheet':
        if len(sys.argv) < 3:
            print("Usage: read-sheet <sheet_url_or_id> [range]", file=sys.stderr)
            sys.exit(1)
        rng = sys.argv[3] if len(sys.argv) > 3 else None
        result = read_sheet(sys.argv[2], rng)
        print(f"=== {result['title']} ({result['range']}) ===")
        for row in result['values']:
            print('\t'.join(str(c) for c in row))
    elif cmd == 'token':
        creds = get_creds()
        print(f"Token valid: {creds.valid}")
        print(f"Scopes: {creds.scopes}")
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    _cli()
