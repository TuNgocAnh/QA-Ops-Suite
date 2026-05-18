"""
Convert sitemap.xml (Appium-style) to sitemap.yaml (QA Ops Suite format).
One-time migration script.

Usage: python3 configs/convert_xml_sitemap.py <path_to_sitemap.xml>
"""
import sys
import xml.etree.ElementTree as ET
import yaml
from datetime import date


def parse_xml_sitemap(xml_path):
    """Parse sitemap.xml and return structured data."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    screens = {}
    for screen_el in root.findall('.//screen'):
        sid = screen_el.get('id')
        if not sid:
            continue

        screen = {
            'id': sid,
            'name': screen_el.get('name', ''),
            'group': screen_el.get('group', ''),
            'class': screen_el.get('class', ''),
            'type': screen_el.get('type', ''),  # "external" etc.
            'description': '',
            'nav_from': [],
            'nav_to': [],
            'elements': [],
            'children_refs': [],
            'notes': '',
        }

        # Description
        desc_el = screen_el.find('description')
        if desc_el is not None and desc_el.text:
            screen['description'] = desc_el.text.strip()

        # Navigation
        nav_el = screen_el.find('navigation')
        if nav_el is not None:
            for from_el in nav_el.findall('from'):
                screen['nav_from'].append({
                    'screen': from_el.get('screen', ''),
                    'action': from_el.get('action', ''),
                    'condition': from_el.get('condition', ''),
                })
            for to_el in nav_el.findall('to'):
                screen['nav_to'].append({
                    'screen': to_el.get('screen', ''),
                    'action': to_el.get('action', ''),
                    'condition': to_el.get('condition', ''),
                })

        # Elements
        elements_el = screen_el.find('elements')
        if elements_el is not None:
            for elem in elements_el.findall('element'):
                screen['elements'].append({
                    'name': elem.get('name', ''),
                    'id': elem.get('id', ''),
                    'type': elem.get('type', ''),
                    'accessibility': elem.get('accessibility', ''),
                    'description': elem.get('description', ''),
                    'hint': elem.get('hint', ''),
                    'no_id': elem.get('NO_ID', '') == 'true',
                })

        # Children
        children_el = screen_el.find('children')
        if children_el is not None:
            for child in children_el.findall('screen'):
                ref = child.get('ref') or child.get('id') or ''
                screen['children_refs'].append(ref)

        # Notes
        notes_el = screen_el.find('notes')
        if notes_el is not None and notes_el.text:
            screen['notes'] = notes_el.text.strip()

        screens[sid] = screen

    return root.get('app', 'App'), screens


def _short_name(screen):
    """Get a short display name for a screen."""
    desc = screen.get('description', '')
    # Use text before " - " as short name (e.g., "Trang chủ - Dashboard..." -> "Trang chủ")
    if ' - ' in desc:
        return desc.split(' - ')[0].strip()
    # Use text before " (" (e.g., "Kho ứng dụng (Tab 4...)" -> "Kho ứng dụng")
    if ' (' in desc:
        return desc.split(' (')[0].strip()
    return desc or screen.get('name', screen.get('id', ''))


def determine_nav_steps(screen, screens):
    """Build nav_steps string from navigation data."""
    if not screen['nav_from']:
        return "Mở app"

    # Use primary (first) from source
    primary_from = screen['nav_from'][0]
    from_screen_id = primary_from['screen']
    action = primary_from.get('action', '')

    from_screen = screens.get(from_screen_id, {})
    from_name = _short_name(from_screen) if from_screen else from_screen_id

    # Clean up action: remove "tap " prefix for readability
    if action:
        clean_action = action
        if clean_action.startswith('tap '):
            # Map element names to human-readable labels where possible
            element_name = clean_action[4:]
            # Try to find element's accessibility/description in from_screen
            if from_screen:
                for elem in from_screen.get('elements', []):
                    if elem['name'] == element_name:
                        label = elem.get('accessibility') or elem.get('description') or ''
                        if label:
                            clean_action = f"Nhấn '{label}'"
                            break
                else:
                    clean_action = f"Nhấn {element_name}"
        return f"{from_name} > {clean_action}"
    return f"Từ {from_name}"


def determine_primary_parent(screen):
    """Determine the primary parent screen."""
    if not screen['nav_from']:
        return None
    return screen['nav_from'][0]['screen']


def extract_inputs(screen):
    """Extract input fields from elements."""
    inputs = []
    input_types = {'android.widget.EditText', 'android.widget.CheckBox', 'android.widget.Switch'}

    for elem in screen['elements']:
        elem_type = elem['type']
        if elem_type in input_types:
            field_name = (
                elem.get('description')
                or elem.get('accessibility')
                or elem.get('hint')
                or elem['name']
            )
            yaml_type = 'text'
            if 'CheckBox' in elem_type:
                yaml_type = 'checkbox'
            elif 'Switch' in elem_type:
                yaml_type = 'toggle'

            inputs.append({
                'field': field_name,
                'type': yaml_type,
                'element_id': elem.get('id') or elem['name'],
            })

    # Also check for dropdown-like views (Views with description containing select/choose)
    for elem in screen['elements']:
        desc = (elem.get('description') or '').lower()
        acc = (elem.get('accessibility') or '').lower()
        if any(kw in desc or kw in acc for kw in ['chon', 'chọn', 'dropdown', 'picker']):
            inputs.append({
                'field': elem.get('description') or elem.get('accessibility') or elem['name'],
                'type': 'dropdown',
                'element_id': elem.get('id') or elem['name'],
            })

    return inputs


def extract_impacts(screen, screens):
    """Extract impact relationships from navigation targets."""
    impacts = []
    seen = set()

    for nav_to in screen['nav_to']:
        target = nav_to['screen']
        if target == screen['id'] or target in seen:
            continue
        # Skip "back" navigations
        action = nav_to.get('action', '')
        if 'back' in action.lower() or 'scrim' in action.lower():
            continue

        seen.add(target)
        condition = nav_to.get('condition', '')
        detail = condition if condition else f"Điều hướng đến {target}"

        # Determine impact type
        impact_type = 'navigation'
        if any(kw in detail.lower() for kw in ['data', 'success', 'create', 'update', 'delete', 'xoa', 'tao']):
            impact_type = 'data_change'

        impacts.append({
            'target': target,
            'type': impact_type,
            'detail': detail,
        })

    return impacts


def extract_depends_on(screen, screens):
    """Extract dependencies from navigation sources."""
    deps = []
    seen = set()

    for nav_from in screen['nav_from']:
        source = nav_from['screen']
        if source in seen:
            continue
        seen.add(source)
        condition = nav_from.get('condition', '')
        reason = condition if condition else f"Truy cập từ {source}"
        deps.append({
            'feature': source,
            'reason': reason,
        })

    return deps


def build_children_list(screen, screens):
    """Build children list from nav_to targets and explicit children."""
    children = set(screen['children_refs'])

    for nav_to in screen['nav_to']:
        target = nav_to['screen']
        target_screen = screens.get(target, {})
        # Add as child if target's primary parent is this screen
        if target_screen:
            primary_parent = determine_primary_parent(target_screen)
            if primary_parent == screen['id']:
                children.add(target)

    return sorted(children)


def determine_auth_required(screen):
    """Determine if auth is required based on group and position in nav tree."""
    # Auth group screens and splash don't require auth
    if screen['group'] in ('auth', 'splash'):
        return False
    if screen['type'] == 'external':
        return False
    return True


def convert_to_yaml(app_name, screens):
    """Convert parsed screens to YAML sitemap structure."""
    pages = {}
    features = {}
    flows = {}

    # Group mapping for roles
    group_roles = {
        'auth': ['all'],
        'splash': ['all'],
        'home': ['merchant'],
        'sales': ['merchant'],
        'product': ['merchant'],
        'report': ['merchant'],
        'cashbook': ['merchant'],
        'search': ['merchant'],
        'scan': ['merchant'],
        'inbox': ['merchant'],
        'feature-store': ['merchant'],
        'settings': ['merchant'],
        'customer': ['merchant'],
        'external': ['all'],
    }

    for sid, screen in screens.items():
        # Skip external screens (not real in-app pages)
        is_external = screen['type'] == 'external'

        # === Build page entry ===
        page = {
            'name': screen['description'] or screen['name'],
            'group': screen['group'],
            'nav_steps': determine_nav_steps(screen, screens),
            'auth_required': determine_auth_required(screen),
            'roles': group_roles.get(screen['group'], ['merchant']),
            'parent': determine_primary_parent(screen),
            'children': build_children_list(screen, screens),
        }

        if is_external:
            page['type'] = 'external'

        pages[sid] = page

        # === Build feature entry (skip splash, external, and simple screens) ===
        if is_external or sid == 'splash':
            continue

        inputs = extract_inputs(screen)
        impacts = extract_impacts(screen, screens)
        depends_on = extract_depends_on(screen, screens)

        feature = {
            'page': sid,
            'description': screen['description'] or screen['name'],
        }

        if inputs:
            feature['inputs'] = inputs
        if impacts:
            feature['impacts'] = impacts
        if depends_on:
            feature['depends_on'] = depends_on
        if screen['notes']:
            feature['notes'] = [screen['notes']]

        # tc_history defaults
        feature['tc_history'] = {
            'last_cook': None,
            'tc_count': 0,
            'sheets_url': None,
        }
        feature['known_bugs'] = []

        features[sid] = feature

    # === Build shared flows ===
    # Login flow (common)
    flows['login_flow'] = {
        'name': 'Luồng đăng nhập chuẩn',
        'steps': [
            "Mở app > Nhấn nút 'Bắt đầu' trên SplashScreen",
            "Nhập số điện thoại vào trường phoneInput",
            "Tick checkbox đồng ý điều khoản",
            "Nhấn nút 'Tiếp tục'",
            "Nhập mã OTP hoặc mật khẩu",
        ],
        'postcondition': 'Hiển thị Trang chủ (HomeScreen)',
        'used_by': sorted([
            sid for sid, s in screens.items()
            if s['group'] not in ('auth', 'splash', 'external') and s['type'] != 'external'
        ]),
    }

    # Navigate to sidebar flow
    flows['sidebar_flow'] = {
        'name': 'Mở sidebar trái',
        'steps': [
            "Tại Trang chủ, nhấn vào avatar (home_avatar_button) ở góc trái header",
        ],
        'postcondition': 'Hiển thị LeftSideBar với menu cài đặt',
        'used_by': sorted([
            sid for sid, s in screens.items()
            if any(f['screen'] == 'left-sidebar' for f in s['nav_from'])
        ]),
    }

    # Back to home flow
    flows['back_to_home_flow'] = {
        'name': 'Quay về Trang chủ',
        'steps': [
            "Nhấn nút Back hoặc nút quay lại",
        ],
        'postcondition': 'Hiển thị Trang chủ (HomeScreen)',
        'used_by': sorted([
            sid for sid, s in screens.items()
            if any(t['screen'] == 'home' and 'back' in t.get('action', '').lower() for t in s['nav_to'])
        ]),
    }

    return {
        'version': 1,
        'product': app_name,
        'last_updated': date.today().isoformat(),
        'pages': pages,
        'features': features,
        'flows': flows,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 configs/convert_xml_sitemap.py <path_to_sitemap.xml>")
        sys.exit(1)

    xml_path = sys.argv[1]
    print(f"Reading: {xml_path}")

    app_name, screens = parse_xml_sitemap(xml_path)
    print(f"Parsed: {len(screens)} screens from app '{app_name}'")

    sitemap = convert_to_yaml(app_name, screens)

    output_path = '.claude/sitemap.yaml'
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(
            sitemap, f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )

    print(f"Written: {output_path}")
    print(f"  Pages: {len(sitemap['pages'])}")
    print(f"  Features: {len(sitemap['features'])}")
    print(f"  Flows: {len(sitemap['flows'])}")

    # Validate
    from sitemap_helper import validate_sitemap
    valid, errors = validate_sitemap(sitemap)
    if valid:
        print("Validation: PASSED")
    else:
        print(f"Validation: {len(errors)} errors")
        for err in errors:
            print(f"  - {err}")


if __name__ == '__main__':
    main()
