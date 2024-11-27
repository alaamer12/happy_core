#!/usr/bin/env python3
import re
from pathlib import Path

def fix_rst_titles(file_path):
    """Fix RST title underlines that are too short or long."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match RST titles and their underlines
    # This matches:
    # 1. Title text
    # 2. Underline character repeated one or more times
    # The underline must be on the next line after the title
    pattern = r'([^\n]+)\n([=\-~"`\':.^_*+#!])\2+'

    def fix_underline(match):
        title = match.group(1)
        underline_char = match.group(2)
        # Create new underline with exact length of title
        new_underline = underline_char * len(title) + 1
        return f'{title}\n{new_underline}'

    # Replace all title patterns with fixed underlines
    new_content = re.sub(pattern, fix_underline, content)

    # Only write if changes were made
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def process_directory(directory):
    """Process all .rst files in the given directory and its subdirectories."""
    fixed_files = []
    for path in Path(directory).rglob('*.rst'):
        if fix_rst_titles(path):
            fixed_files.append(path)
    return fixed_files

def main():
    # Get the docs/source directory
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent / 'docs' / 'source'
    
    if not docs_dir.exists():
        print(f"Documentation directory not found: {docs_dir}")
        return

    print(f"Processing RST files in: {docs_dir}")
    fixed_files = process_directory(docs_dir)

    if fixed_files:
        print("\nFixed title underlines in the following files:")
        for file in fixed_files:
            print(f"- {file}")
    else:
        print("\nNo files needed fixing!")

if __name__ == '__main__':
    main()
