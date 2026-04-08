#!/usr/bin/env python3
"""
Syntax Checker for CLI Weather Dashboard
Checks all Python files for syntax errors.
"""

import os
import sys
import ast
import glob

def check_syntax(file_path):
    """Check syntax of a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source, filename=file_path)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error reading file: {e}"

def main():
    """Check all .py files in project."""
    py_files = []
    for root, _, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(".py") and ".venv" not in root and "venv" not in root:
                py_files.append(os.path.join(root, filename))
    errors = []

    for file_path in sorted(py_files):
        if os.path.isfile(file_path):
            valid, error = check_syntax(file_path)
            if not valid:
                errors.append(f"{file_path}: {error}")
                print(f"ERROR: {file_path}: {error}")
            else:
                print(f"OK: {file_path}")

    if errors:
        print(f"\nFound {len(errors)} syntax error(s).")
        sys.exit(1)
    else:
        print("\nAll Python files have valid syntax!")
        sys.exit(0)

if __name__ == "__main__":
    main()