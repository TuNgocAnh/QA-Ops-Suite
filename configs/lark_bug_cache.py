"""
Lark Bug Board Cache Helper

Load cached field options (Dev PIC, Sprint, Platform, etc.) for /log-bug.
Supports fuzzy matching for Dev PIC by name/alias.

Usage:
    from configs.lark_bug_cache import (
        load_cache, find_dev_pic, find_option,
        get_sprints, get_platforms, get_types, get_priorities, get_statuses, get_tinh_nang
    )

    # Find Dev PIC by name (fuzzy)
    users = find_dev_pic("Phuong")
    # => [{"id": "ou_19db...", "name": "Phuong, Tran Minh"}]

    # Find option by exact or partial name
    sprint = find_option("sprint", "Sprint 12")
    # => {"id": "optdR7wOvO", "name": "Sprint 12 - 15.04.2026"}
"""

import json
import os
import subprocess
import sys
from datetime import datetime

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lark_bug_board_cache.json")


def load_cache() -> dict:
    """Load cache from JSON file."""
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cache(data: dict):
    """Save cache to JSON file."""
    data["_meta"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Cache saved: {CACHE_FILE}")


def find_dev_pic(query: str) -> list[dict]:
    """
    Find Dev PIC by name or alias (case-insensitive, partial match).
    Returns list of matching users: [{"id": "ou_xxx", "name": "..."}]
    """
    cache = load_cache()
    query_lower = query.lower().strip()
    results = []

    for user in cache.get("dev_pic", []):
        name_lower = user["name"].lower()
        # Check exact name match
        if query_lower in name_lower:
            results.append({"id": user["id"], "name": user["name"]})
            continue
        # Check aliases
        for alias in user.get("aliases", []):
            if query_lower in alias.lower():
                results.append({"id": user["id"], "name": user["name"]})
                break

    return results


def find_option(field: str, query: str) -> dict | None:
    """
    Find an option by field name and query (case-insensitive, partial match).
    field: "sprint", "platform", "type", "priority", "status", "tinh_nang"
    Returns first match: {"id": "opt...", "name": "..."} or None
    """
    cache = load_cache()
    query_lower = query.lower().strip()

    for option in cache.get(field, []):
        if query_lower in option["name"].lower():
            return option

    return None


def find_all_options(field: str, query: str) -> list[dict]:
    """
    Find all matching options by field name and query.
    Returns list of matches: [{"id": "opt...", "name": "..."}]
    """
    cache = load_cache()
    query_lower = query.lower().strip()
    results = []

    for option in cache.get(field, []):
        if query_lower in option["name"].lower():
            results.append(option)

    return results


def get_sprints() -> list[dict]:
    return load_cache().get("sprint", [])


def get_platforms() -> list[dict]:
    return load_cache().get("platform", [])


def get_types() -> list[dict]:
    return load_cache().get("type", [])


def get_priorities() -> list[dict]:
    return load_cache().get("priority", [])


def get_statuses() -> list[dict]:
    return load_cache().get("status", [])


def get_tinh_nang() -> list[dict]:
    return load_cache().get("tinh_nang", [])


def get_dev_pic_list() -> list[dict]:
    return load_cache().get("dev_pic", [])


def add_dev_pic(open_id: str, name: str, aliases: list[str] | None = None):
    """Add a new Dev PIC to cache (if not already exists)."""
    cache = load_cache()
    for user in cache.get("dev_pic", []):
        if user["id"] == open_id:
            print(f"[SKIP] Dev PIC already exists: {name} ({open_id})")
            return

    if aliases is None:
        # Auto-generate aliases from name
        parts = name.replace(",", "").lower().split()
        aliases = [parts[-1]] if parts else []  # last name part as alias

    cache["dev_pic"].append({"id": open_id, "name": name, "aliases": aliases})
    save_cache(cache)
    print(f"[OK] Added Dev PIC: {name} ({open_id})")


def add_option(field: str, option_id: str, name: str):
    """Add a new option to a field cache (if not already exists)."""
    cache = load_cache()
    for opt in cache.get(field, []):
        if opt["id"] == option_id or opt["name"] == name:
            print(f"[SKIP] Option already exists in {field}: {name}")
            return

    if field not in cache:
        cache[field] = []

    cache[field].append({"id": option_id, "name": name})
    save_cache(cache)
    print(f"[OK] Added to {field}: {name}")


# --- CLI ---
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 configs/lark_bug_cache.py find-dev <name>")
        print("  python3 configs/lark_bug_cache.py find <field> <query>")
        print("  python3 configs/lark_bug_cache.py list <field>")
        print("  python3 configs/lark_bug_cache.py add-dev <open_id> <name>")
        print("  python3 configs/lark_bug_cache.py add <field> <option_id> <name>")
        print("")
        print("Fields: sprint, platform, type, priority, status, tinh_nang, dev_pic")
        return

    cmd = sys.argv[1]

    if cmd == "find-dev":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        results = find_dev_pic(query)
        if results:
            for r in results:
                print(f"  {r['id']}  {r['name']}")
        else:
            print(f"  No Dev PIC found for: {query}")

    elif cmd == "find":
        field = sys.argv[2] if len(sys.argv) > 2 else ""
        query = sys.argv[3] if len(sys.argv) > 3 else ""
        results = find_all_options(field, query)
        if results:
            for r in results:
                print(f"  {r['id']}  {r['name']}")
        else:
            print(f"  No options found in {field} for: {query}")

    elif cmd == "list":
        field = sys.argv[2] if len(sys.argv) > 2 else ""
        cache = load_cache()
        options = cache.get(field, [])
        if field == "dev_pic":
            for opt in options:
                aliases = ", ".join(opt.get("aliases", []))
                print(f"  {opt['id']}  {opt['name']}  [{aliases}]")
        else:
            for opt in options:
                print(f"  {opt.get('id', '-')}  {opt['name']}")
        print(f"\nTotal: {len(options)}")

    elif cmd == "add-dev":
        if len(sys.argv) < 4:
            print("Usage: add-dev <open_id> <name> [alias1,alias2,...]")
            return
        open_id = sys.argv[2]
        name = sys.argv[3]
        aliases = sys.argv[4].split(",") if len(sys.argv) > 4 else None
        add_dev_pic(open_id, name, aliases)

    elif cmd == "add":
        if len(sys.argv) < 5:
            print("Usage: add <field> <option_id> <name>")
            return
        field = sys.argv[2]
        option_id = sys.argv[3]
        name = sys.argv[4]
        add_option(field, option_id, name)

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
