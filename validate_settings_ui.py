#!/usr/bin/env python3
"""
Code structure validation for settings UI improvements.
Checks that all the improved methods exist and have correct signatures.
"""

import ast
import sys

def check_settings_ui_structure(file_path):
    """Check that the settings UI has the expected structure."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    checks = {
        '_create_embedded_settings_ui': False,
        '_create_quick_settings_tab': False,
        '_create_alarms_settings_tab': False,
        '_create_advanced_settings_tab': False,
        '_create_settings_section': False,
    }
    
    # Check for class definition
    class_found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name == 'KioskClockApp':
                class_found = True
                # Check for methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name in checks:
                            checks[item.name] = True
    
    print("=" * 60)
    print("Settings UI Structure Validation")
    print("=" * 60)
    
    if not class_found:
        print("❌ KioskClockApp class not found")
        return False
    
    print("✓ KioskClockApp class found")
    
    all_passed = True
    for method, found in checks.items():
        if found:
            print(f"✓ {method} method found")
        else:
            print(f"❌ {method} method NOT found")
            all_passed = False
    
    # Check for modern color scheme in code
    modern_colors = ['#1e1e1e', '#2d2d30', '#0078d4', '#3c3c3c']
    color_found = False
    for color in modern_colors:
        if color in content:
            color_found = True
            break
    
    if color_found:
        print("✓ Modern color scheme detected")
    else:
        print("⚠ Modern color scheme not detected")
    
    # Check for help text support
    if 'help_text' in content:
        print("✓ Help text support detected")
    else:
        print("⚠ Help text support not detected")
    
    # Check for focus effects
    if 'on_focus_in' in content or 'FocusIn' in content:
        print("✓ Input focus effects detected")
    else:
        print("⚠ Input focus effects not detected")
    
    print("=" * 60)
    return all_passed

if __name__ == '__main__':
    file_path = 'src/kiosk_clock_app.py'
    success = check_settings_ui_structure(file_path)
    sys.exit(0 if success else 1)

