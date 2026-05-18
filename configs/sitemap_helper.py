"""
Sitemap Helper - Đọc, ghi, và enrich sitemap.yaml
Auto-enriched qua mỗi lần /cook, /fix, /analyze, /plan

Usage:
    from configs.sitemap_helper import (
        load_sitemap, save_sitemap, get_nav_path, get_impacts,
        get_precondition, get_dependencies, enrich_feature,
        enrich_page, enrich_flow, add_bug, validate_sitemap
    )
"""
import os
import yaml
from datetime import date


def _sitemap_path():
    """Return absolute path to sitemap.yaml."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, '.claude', 'sitemap.yaml')


def load_sitemap():
    """Load sitemap.yaml and return dict. Returns empty structure if file missing."""
    path = _sitemap_path()
    if not os.path.exists(path):
        return _empty_sitemap()
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if not data or not isinstance(data, dict):
        return _empty_sitemap()
    # Ensure required keys exist
    data.setdefault('pages', {})
    data.setdefault('features', {})
    data.setdefault('flows', {})
    # Clean out None values from commented-out examples
    if data['pages'] is None:
        data['pages'] = {}
    if data['features'] is None:
        data['features'] = {}
    if data['flows'] is None:
        data['flows'] = {}
    return data


def save_sitemap(data):
    """Save sitemap dict back to sitemap.yaml with updated timestamp."""
    data['last_updated'] = date.today().isoformat()
    path = _sitemap_path()
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(
            data, f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120
        )


def _empty_sitemap():
    """Return empty sitemap structure."""
    return {
        'version': 1,
        'product': '',
        'last_updated': date.today().isoformat(),
        'pages': {},
        'features': {},
        'flows': {}
    }


# =========================================================================
# NAVIGATION & PRECONDITION
# =========================================================================

def get_nav_path(sitemap, page_id):
    """Build full navigation path by walking up parent chain.

    Returns list of nav_steps from root to target page.
    Example: ["Mở app", "Đăng nhập thành công", "Sidebar > Hóa đơn > Danh sách"]
    """
    pages = sitemap.get('pages', {})
    if page_id not in pages:
        return []

    path = []
    current = page_id
    visited = set()

    while current and current not in visited:
        visited.add(current)
        page = pages.get(current)
        if not page:
            break
        path.append(page.get('nav_steps', page.get('name', current)))
        current = page.get('parent')

    path.reverse()
    return path


def get_precondition(sitemap, feature_id):
    """Generate precondition text for a feature.

    Combines: auth requirement + role + simplified nav path.
    Skips auth-related screens (splash, login, otp, password) since
    "Đã đăng nhập" already implies completing the auth flow.
    Returns string ready to use in TC precondition field.
    """
    features = sitemap.get('features', {})
    pages = sitemap.get('pages', {})

    feature = features.get(feature_id, {})
    page_id = feature.get('page', feature_id)
    page = pages.get(page_id, {})

    parts = []

    # Auth + role
    auth_required = page.get('auth_required', True)
    if auth_required:
        roles = page.get('roles', [])
        if roles and roles != ['all']:
            parts.append(f"Đã đăng nhập với tài khoản {'/'.join(roles)}")
        else:
            parts.append("Đã đăng nhập")

    # Navigation path - simplified
    nav_path = get_nav_path(sitemap, page_id)
    if nav_path:
        # Filter out auth-flow steps when user is already logged in
        auth_groups = {'splash', 'auth'}
        if auth_required:
            filtered = []
            for step in nav_path:
                # Find which page this step belongs to by matching nav_steps
                is_auth_step = False
                for pid, pdata in pages.items():
                    if pdata.get('nav_steps') == step and pdata.get('group') in auth_groups:
                        is_auth_step = True
                        break
                if step in ("Mở app", "Mở ứng dụng"):
                    is_auth_step = True
                if not is_auth_step:
                    filtered.append(step)
            nav_path = filtered

        # Simplify: use only page name (not full description) for intermediate steps
        simplified = []
        for step in nav_path:
            # Clean up verbose descriptions
            for pid, pdata in pages.items():
                if pdata.get('nav_steps') == step:
                    # Use short name from nav_steps directly
                    simplified.append(step)
                    break
            else:
                simplified.append(step)

        if simplified:
            parts.append("truy cập " + " > ".join(simplified))

    return ", ".join(parts) if parts else ""


# =========================================================================
# IMPACT & DEPENDENCY ANALYSIS
# =========================================================================

def get_impacts(sitemap, feature_id):
    """Get list of features impacted by this feature.

    Returns list of dicts: [{ target, type, detail }, ...]
    """
    features = sitemap.get('features', {})
    feature = features.get(feature_id, {})
    return feature.get('impacts', [])


def get_reverse_impacts(sitemap, feature_id):
    """Get list of features that impact this feature (reverse lookup).

    Useful for regression analysis - "what else could break this feature?"
    Returns list of dicts: [{ source, type, detail }, ...]
    """
    result = []
    for fid, fdata in sitemap.get('features', {}).items():
        if fid == feature_id:
            continue
        for impact in fdata.get('impacts', []):
            if impact.get('target') == feature_id:
                result.append({
                    'source': fid,
                    'type': impact.get('type', ''),
                    'detail': impact.get('detail', '')
                })
    return result


def get_dependencies(sitemap, feature_id):
    """Get list of features this feature depends on.

    Returns list of dicts: [{ feature, reason }, ...]
    """
    features = sitemap.get('features', {})
    feature = features.get(feature_id, {})
    return feature.get('depends_on', [])


# =========================================================================
# SHARED FLOWS
# =========================================================================

def get_flows_for_feature(sitemap, feature_id):
    """Get shared flows that include this feature.

    Returns list of flow dicts with their IDs.
    """
    result = []
    for flow_id, flow_data in sitemap.get('flows', {}).items():
        used_by = flow_data.get('used_by', [])
        if feature_id in used_by:
            result.append({'id': flow_id, **flow_data})
    return result


# =========================================================================
# ENRICH FUNCTIONS
# =========================================================================

def enrich_page(sitemap, page_id, page_data):
    """Add or update a page entry. Merges with existing data."""
    pages = sitemap.get('pages', {})
    if page_id in pages:
        existing = pages[page_id]
        # Merge - keep existing values, add new ones
        for key, value in page_data.items():
            if key == 'children':
                # Merge children lists
                existing_children = set(existing.get('children', []))
                new_children = set(value) if isinstance(value, list) else set()
                existing['children'] = sorted(existing_children | new_children)
            elif value is not None:
                existing[key] = value
    else:
        # Set defaults for new page
        page_data.setdefault('children', [])
        page_data.setdefault('auth_required', True)
        page_data.setdefault('roles', [])
        page_data.setdefault('parent', None)
        pages[page_id] = page_data
    sitemap['pages'] = pages
    return sitemap


def enrich_feature(sitemap, feature_id, feature_data):
    """Add or update a feature entry. Merges with existing data."""
    features = sitemap.get('features', {})
    if feature_id in features:
        existing = features[feature_id]
        for key, value in feature_data.items():
            if key == 'impacts':
                # Merge impacts - avoid duplicates by target
                existing_targets = {i['target'] for i in existing.get('impacts', [])}
                for impact in (value or []):
                    if impact.get('target') not in existing_targets:
                        existing.setdefault('impacts', []).append(impact)
            elif key == 'depends_on':
                # Merge dependencies - avoid duplicates by feature
                existing_deps = {d['feature'] for d in existing.get('depends_on', [])}
                for dep in (value or []):
                    if dep.get('feature') not in existing_deps:
                        existing.setdefault('depends_on', []).append(dep)
            elif key == 'inputs':
                # Merge inputs - avoid duplicates by field name
                existing_fields = {i['field'] for i in existing.get('inputs', [])}
                for inp in (value or []):
                    if inp.get('field') not in existing_fields:
                        existing.setdefault('inputs', []).append(inp)
            elif key == 'outputs':
                # Merge outputs - avoid duplicates
                existing_outputs = set(existing.get('outputs', []))
                for out in (value or []):
                    if out not in existing_outputs:
                        existing.setdefault('outputs', []).append(out)
            elif key == 'notes':
                # Append notes, avoid duplicates
                existing_notes = set(existing.get('notes', []))
                for note in (value or []):
                    if note not in existing_notes:
                        existing.setdefault('notes', []).append(note)
            elif key == 'tc_history':
                # Always overwrite tc_history with latest
                existing['tc_history'] = value
            elif value is not None:
                existing[key] = value
    else:
        # Set defaults for new feature
        feature_data.setdefault('impacts', [])
        feature_data.setdefault('depends_on', [])
        feature_data.setdefault('inputs', [])
        feature_data.setdefault('outputs', [])
        feature_data.setdefault('api_endpoints', [])
        feature_data.setdefault('tc_history', {
            'last_cook': None,
            'tc_count': 0,
            'sheets_url': None
        })
        feature_data.setdefault('known_bugs', [])
        feature_data.setdefault('notes', [])
        features[feature_id] = feature_data
    sitemap['features'] = features
    return sitemap


def enrich_flow(sitemap, flow_id, flow_data):
    """Add or update a shared flow. Merges used_by list."""
    flows = sitemap.get('flows', {})
    if flow_id in flows:
        existing = flows[flow_id]
        # Merge used_by
        existing_used_by = set(existing.get('used_by', []))
        new_used_by = set(flow_data.get('used_by', []))
        existing['used_by'] = sorted(existing_used_by | new_used_by)
        # Update steps if provided
        if flow_data.get('steps'):
            existing['steps'] = flow_data['steps']
        if flow_data.get('postcondition'):
            existing['postcondition'] = flow_data['postcondition']
    else:
        flow_data.setdefault('used_by', [])
        flows[flow_id] = flow_data
    sitemap['flows'] = flows
    return sitemap


def add_bug(sitemap, feature_id, bug_info):
    """Add a known bug to a feature. bug_info is a string like 'BUG-123: description'."""
    features = sitemap.get('features', {})
    if feature_id not in features:
        return sitemap
    bugs = features[feature_id].get('known_bugs', [])
    if bug_info not in bugs:
        bugs.append(bug_info)
        features[feature_id]['known_bugs'] = bugs
    sitemap['features'] = features
    return sitemap


def update_tc_history(sitemap, feature_id, tc_count, sheets_url=None):
    """Update tc_history for a feature after /cook completes."""
    features = sitemap.get('features', {})
    if feature_id not in features:
        return sitemap
    features[feature_id]['tc_history'] = {
        'last_cook': date.today().isoformat(),
        'tc_count': tc_count,
        'sheets_url': sheets_url
    }
    sitemap['features'] = features
    return sitemap


# =========================================================================
# VALIDATION
# =========================================================================

def validate_sitemap(sitemap=None):
    """Validate sitemap structure. Returns (is_valid, errors_list)."""
    if sitemap is None:
        sitemap = load_sitemap()

    errors = []
    pages = sitemap.get('pages', {})
    features = sitemap.get('features', {})
    flows = sitemap.get('flows', {})

    # Validate pages
    for pid, pdata in pages.items():
        if not isinstance(pdata, dict):
            errors.append(f"Page '{pid}' is not a dict")
            continue
        if 'name' not in pdata:
            errors.append(f"Page '{pid}' missing 'name'")
        if 'nav_steps' not in pdata:
            errors.append(f"Page '{pid}' missing 'nav_steps'")
        # Check parent exists
        parent = pdata.get('parent')
        if parent and parent not in pages:
            errors.append(f"Page '{pid}' has parent '{parent}' which does not exist in pages")

    # Validate features
    for fid, fdata in features.items():
        if not isinstance(fdata, dict):
            errors.append(f"Feature '{fid}' is not a dict")
            continue
        # Check page reference
        page_ref = fdata.get('page')
        if page_ref and page_ref not in pages:
            errors.append(f"Feature '{fid}' references page '{page_ref}' which does not exist")
        # Check impact targets
        for impact in fdata.get('impacts', []):
            target = impact.get('target')
            if target and target not in features and target not in pages:
                errors.append(f"Feature '{fid}' impact target '{target}' not found in features or pages")

    # Check circular dependencies
    for fid in features:
        if _has_circular_dep(features, fid, set()):
            errors.append(f"Feature '{fid}' has circular dependency")

    return (len(errors) == 0, errors)


def _has_circular_dep(features, feature_id, visited):
    """Check for circular dependencies recursively."""
    if feature_id in visited:
        return True
    visited.add(feature_id)
    feature = features.get(feature_id, {})
    for dep in feature.get('depends_on', []):
        dep_id = dep.get('feature')
        if dep_id and _has_circular_dep(features, dep_id, visited.copy()):
            return True
    return False


# =========================================================================
# QUERY HELPERS
# =========================================================================

def find_feature_by_name(sitemap, name_query):
    """Find feature(s) matching a name query (case-insensitive partial match).

    Returns list of (feature_id, feature_data) tuples.
    """
    results = []
    query_lower = name_query.lower()
    for fid, fdata in sitemap.get('features', {}).items():
        desc = fdata.get('description', '')
        if query_lower in fid.lower() or query_lower in desc.lower():
            results.append((fid, fdata))

    # Also check pages
    for pid, pdata in sitemap.get('pages', {}).items():
        page_name = pdata.get('name', '')
        if query_lower in pid.lower() or query_lower in page_name.lower():
            # Check if any feature references this page
            for fid, fdata in sitemap.get('features', {}).items():
                if fdata.get('page') == pid and (fid, fdata) not in results:
                    results.append((fid, fdata))

    return results


def get_regression_scope(sitemap, feature_id):
    """Get full regression scope for a feature.

    Returns dict with:
    - direct_impacts: features directly impacted
    - reverse_impacts: features that impact this one
    - dependency_chain: features this depends on
    """
    return {
        'direct_impacts': get_impacts(sitemap, feature_id),
        'reverse_impacts': get_reverse_impacts(sitemap, feature_id),
        'dependency_chain': get_dependencies(sitemap, feature_id)
    }


def summary(sitemap=None):
    """Print a quick summary of sitemap contents."""
    if sitemap is None:
        sitemap = load_sitemap()
    pages = sitemap.get('pages', {})
    features = sitemap.get('features', {})
    flows = sitemap.get('flows', {})
    return {
        'product': sitemap.get('product', ''),
        'last_updated': sitemap.get('last_updated', ''),
        'total_pages': len(pages),
        'total_features': len(features),
        'total_flows': len(flows),
        'total_impacts': sum(
            len(f.get('impacts', [])) for f in features.values()
        ),
        'total_bugs': sum(
            len(f.get('known_bugs', [])) for f in features.values()
        )
    }
