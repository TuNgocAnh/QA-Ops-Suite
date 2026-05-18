"""
Lark API helper - Python-first entry point for Lark operations.

Use this module INSTEAD of `mcp__lark-mcp__*` tools. MCP tools often fail with
expired token errors (99991668) because MCP doesn't auto-refresh. This module
uses `ensure_valid_token()` which auto-refreshes via refresh_token, or re-opens
browser OAuth if needed.

Covered operations:
  - Wiki / Docx read         : read_wiki, read_docx, read_docx_blocks
  - Wiki search              : search_wiki, search_docs
  - Bitable records          : list_records, search_records, get_record,
                               create_record, update_record, delete_record
  - Bitable schema           : list_fields, list_tables, get_app
  - Drive file comments      : list_comments, get_comment
  - Drive media              : get_media_download_url
  - Raw call                 : call(method, path, ...)   # for anything else

Quick start:
  from configs.lark_api import read_wiki, search_records
  doc = read_wiki("UQXcw2oQ6iPDnOkRZxclaze5gYf")
  print(doc["title"], doc["content"][:200])

CLI:
  python3 configs/lark_api.py read-wiki <wiki_token>
  python3 configs/lark_api.py search-records <base_id> <table_id> --filter '...'
  python3 configs/lark_api.py list-fields <base_id> <table_id>
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
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from configs.lark_auth import ensure_valid_token, DOMAIN  # noqa: E402


# =============================================================
# Core: token + low-level call
# =============================================================

def get_token(force_browser: bool = False, verbose: bool = False) -> str:
    """Return a valid user_access_token. Auto-refresh or re-OAuth if needed."""
    return ensure_valid_token(force_browser=force_browser, verbose=verbose)


def call(
    method: str,
    path: str,
    *,
    params: dict | None = None,
    json_body: dict | None = None,
    token: str | None = None,
    raise_on_error: bool = True,
) -> dict:
    """Low-level Lark API call.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE).
        path: API path starting with `/open-apis/...`.
        params: Query string params.
        json_body: JSON body for POST/PUT/PATCH.
        token: Override token (default: auto-fetch via get_token()).
        raise_on_error: If True, raise on non-zero `code`. Default True.

    Returns:
        Parsed JSON response (dict).
    """
    tok = token or get_token()
    url = f"{DOMAIN}{path}"
    headers = {"Authorization": f"Bearer {tok}"}
    if json_body is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"

    resp = requests.request(
        method=method.upper(),
        url=url,
        headers=headers,
        params=params,
        json=json_body,
        timeout=30,
    )
    try:
        data = resp.json()
    except Exception:
        data = {"code": -1, "msg": f"Non-JSON response: {resp.text[:200]}"}

    if raise_on_error and data.get("code", 0) != 0:
        raise RuntimeError(
            f"Lark API error {data.get('code')}: {data.get('msg')} "
            f"[{method} {path}]"
        )
    return data


# =============================================================
# Wiki / Docx read
# =============================================================

def resolve_wiki_node(wiki_token: str) -> dict:
    """Resolve a wiki node token to {obj_token, obj_type, title, ...}."""
    data = call(
        "GET",
        "/open-apis/wiki/v2/spaces/get_node",
        params={"token": wiki_token, "obj_type": "wiki"},
    )
    return data["data"]["node"]


def read_docx(document_id: str) -> str:
    """Return plain-text content of a Lark Docx."""
    data = call(
        "GET",
        f"/open-apis/docx/v1/documents/{document_id}/raw_content",
    )
    return data["data"]["content"]


def read_docx_blocks(document_id: str, page_size: int = 500) -> list:
    """Return list of blocks (for docs with images, tables, etc.)."""
    blocks = []
    page_token = None
    while True:
        params = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token
        data = call(
            "GET",
            f"/open-apis/docx/v1/documents/{document_id}/blocks",
            params=params,
        )
        items = data["data"].get("items", [])
        blocks.extend(items)
        if not data["data"].get("has_more"):
            break
        page_token = data["data"].get("page_token")
        if not page_token:
            break
    return blocks


def read_wiki(wiki_token: str) -> dict:
    """Read a wiki link end-to-end. Returns:
      {title, obj_type, obj_token, content (if docx), node (raw node info)}
    """
    node = resolve_wiki_node(wiki_token)
    result = {
        "title": node.get("title"),
        "obj_type": node.get("obj_type"),
        "obj_token": node.get("obj_token"),
        "node": node,
        "content": None,
    }
    if node.get("obj_type") == "docx":
        result["content"] = read_docx(node["obj_token"])
    return result


# =============================================================
# Wiki / Doc search
# =============================================================

def search_wiki(query: str, space_id: str | None = None, page_size: int = 10) -> list:
    """Search wiki nodes. Returns list of nodes."""
    body = {"query": query, "page_size": page_size}
    if space_id:
        body["space_id"] = space_id
    data = call(
        "POST",
        "/open-apis/wiki/v1/nodes/search",
        json_body=body,
    )
    return data["data"].get("items", [])


def search_docs(query: str, count: int = 10, offset: int = 0) -> list:
    """Search cloud documents (docx, doc, sheet, bitable, ...)."""
    data = call(
        "POST",
        "/open-apis/suite/docs-api/search/object",
        json_body={"search_key": query, "count": count, "offset": offset},
    )
    return data["data"].get("docs_entities", [])


# =============================================================
# Bitable: records
# =============================================================

def list_records(
    app_token: str,
    table_id: str,
    *,
    filter_expr: str | None = None,
    sort: list | None = None,
    field_names: list | None = None,
    page_size: int = 20,
    page_token: str | None = None,
) -> dict:
    """List Bitable records. Returns {items, has_more, page_token, total}."""
    params = {"page_size": page_size}
    if page_token:
        params["page_token"] = page_token
    if filter_expr:
        params["filter"] = filter_expr
    if sort:
        params["sort"] = json.dumps(sort)
    if field_names:
        params["field_names"] = json.dumps(field_names)
    data = call(
        "GET",
        f"/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records",
        params=params,
    )
    return data["data"]


def search_records(
    app_token: str,
    table_id: str,
    *,
    filter_conditions: list | None = None,
    conjunction: str = "and",
    sort: list | None = None,
    field_names: list | None = None,
    view_id: str | None = None,
    page_size: int = 20,
    page_token: str | None = None,
) -> dict:
    """Search Bitable records (POST /search — more powerful than list).

    Example filter_conditions:
        [{"field_name": "Title", "operator": "contains", "value": ["login"]}]
    """
    body: dict = {"automatic_fields": False}
    if filter_conditions:
        body["filter"] = {
            "conjunction": conjunction,
            "conditions": filter_conditions,
        }
    if sort:
        body["sort"] = sort
    if field_names:
        body["field_names"] = field_names
    if view_id:
        body["view_id"] = view_id

    params = {"page_size": page_size}
    if page_token:
        params["page_token"] = page_token

    data = call(
        "POST",
        f"/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search",
        params=params,
        json_body=body,
    )
    return data["data"]


def get_record(app_token: str, table_id: str, record_id: str) -> dict:
    """Get a single Bitable record."""
    data = call(
        "GET",
        f"/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
    )
    return data["data"].get("record", {})


def create_record(app_token: str, table_id: str, fields: dict) -> dict:
    """Create a Bitable record. Returns the created record."""
    data = call(
        "POST",
        f"/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records",
        json_body={"fields": fields},
    )
    return data["data"].get("record", {})


def update_record(
    app_token: str, table_id: str, record_id: str, fields: dict
) -> dict:
    """Update a Bitable record."""
    data = call(
        "PUT",
        f"/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
        json_body={"fields": fields},
    )
    return data["data"].get("record", {})


def delete_record(app_token: str, table_id: str, record_id: str) -> bool:
    """Delete a Bitable record. Returns True on success."""
    data = call(
        "DELETE",
        f"/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
    )
    return bool(data["data"].get("deleted"))


# =============================================================
# Bitable: schema
# =============================================================

def list_fields(app_token: str, table_id: str, page_size: int = 100) -> list:
    """List all fields of a Bitable table. Returns list of field dicts."""
    fields = []
    page_token = None
    while True:
        params = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token
        data = call(
            "GET",
            f"/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
            params=params,
        )
        fields.extend(data["data"].get("items", []))
        if not data["data"].get("has_more"):
            break
        page_token = data["data"].get("page_token")
        if not page_token:
            break
    return fields


def list_tables(app_token: str, page_size: int = 100) -> list:
    """List all tables in a Bitable app."""
    tables = []
    page_token = None
    while True:
        params = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token
        data = call(
            "GET",
            f"/open-apis/bitable/v1/apps/{app_token}/tables",
            params=params,
        )
        tables.extend(data["data"].get("items", []))
        if not data["data"].get("has_more"):
            break
        page_token = data["data"].get("page_token")
        if not page_token:
            break
    return tables


def get_app(app_token: str) -> dict:
    """Get Bitable app metadata (name, etc.)."""
    data = call("GET", f"/open-apis/bitable/v1/apps/{app_token}")
    return data["data"].get("app", {})


# =============================================================
# Drive: comments + media
# =============================================================

def list_comments(
    file_token: str,
    file_type: str = "docx",
    page_size: int = 20,
    page_token: str | None = None,
) -> dict:
    """List comments on a file (docx, doc, sheet, bitable, ...)."""
    params = {"file_type": file_type, "page_size": page_size}
    if page_token:
        params["page_token"] = page_token
    data = call(
        "GET",
        f"/open-apis/drive/v1/files/{file_token}/comments",
        params=params,
    )
    return data["data"]


def get_comment(file_token: str, comment_id: str, file_type: str = "docx") -> dict:
    """Get a single comment with full reply thread."""
    data = call(
        "GET",
        f"/open-apis/drive/v1/files/{file_token}/comments/{comment_id}",
        params={"file_type": file_type},
    )
    return data["data"].get("comment", {})


def get_media_download_url(file_tokens: list) -> list:
    """Get temporary download URLs for media (images, files).

    Returns: [{file_token, tmp_download_url}, ...]
    """
    data = call(
        "GET",
        "/open-apis/drive/v1/medias/batch_get_tmp_download_url",
        params={"file_tokens": ",".join(file_tokens)},
    )
    return data["data"].get("tmp_download_urls", [])


# =============================================================
# CLI
# =============================================================

def _cli():
    import argparse
    parser = argparse.ArgumentParser(description="Lark API Python helper CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("read-wiki", help="Read a wiki link")
    p.add_argument("wiki_token")

    p = sub.add_parser("read-docx", help="Read docx raw content")
    p.add_argument("document_id")

    p = sub.add_parser("search-wiki", help="Search wiki nodes")
    p.add_argument("query")
    p.add_argument("--space", default=None)

    p = sub.add_parser("list-fields", help="List Bitable fields")
    p.add_argument("base_id")
    p.add_argument("table_id")

    p = sub.add_parser("list-records", help="List Bitable records")
    p.add_argument("base_id")
    p.add_argument("table_id")
    p.add_argument("--filter", dest="filter_expr", default=None)
    p.add_argument("--page-size", type=int, default=20)

    p = sub.add_parser("get-record", help="Get a Bitable record")
    p.add_argument("base_id")
    p.add_argument("table_id")
    p.add_argument("record_id")

    p = sub.add_parser("list-comments", help="List file comments")
    p.add_argument("file_token")
    p.add_argument("--type", dest="file_type", default="docx")

    p = sub.add_parser("token", help="Print current access token (debug)")

    args = parser.parse_args()

    if args.cmd == "read-wiki":
        result = read_wiki(args.wiki_token)
        print(f"Title: {result['title']}")
        print(f"Type:  {result['obj_type']}  |  Token: {result['obj_token']}")
        if result["content"]:
            print(f"\n=== Content ({len(result['content'])} chars) ===")
            print(result["content"])
    elif args.cmd == "read-docx":
        print(read_docx(args.document_id))
    elif args.cmd == "search-wiki":
        for item in search_wiki(args.query, space_id=args.space):
            print(f"- {item.get('title')}  [{item.get('node_token')}]")
    elif args.cmd == "list-fields":
        for f in list_fields(args.base_id, args.table_id):
            print(f"- {f.get('field_name')}  type={f.get('type')}  id={f.get('field_id')}")
    elif args.cmd == "list-records":
        data = list_records(
            args.base_id, args.table_id,
            filter_expr=args.filter_expr, page_size=args.page_size,
        )
        print(f"Total: {data.get('total')}  has_more: {data.get('has_more')}")
        for r in data.get("items", []):
            print(json.dumps(r, ensure_ascii=False))
    elif args.cmd == "get-record":
        print(json.dumps(
            get_record(args.base_id, args.table_id, args.record_id),
            ensure_ascii=False, indent=2,
        ))
    elif args.cmd == "list-comments":
        data = list_comments(args.file_token, file_type=args.file_type)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.cmd == "token":
        print(get_token(verbose=True))


if __name__ == "__main__":
    _cli()
