"""Changelog management script."""
import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Dict

# Add the project root directory to Python path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.styles import Styles, print_header, print_step

def get_changelog_input(section: str) -> str:
    """Get changelog input for a specific section."""
    changes = input(Styles.PROMPT(f"Enter {section} (separate with commas or press Enter to skip): ")).strip()
    return changes

def create_changelog(version: str, changes: Dict[str, str], changelog_path: str = "changelog") -> None:
    """Create a changelog file for the given version.
    
    Args:
        version (str): Version number
        changes (Dict[str, str]): Dictionary of changes by section
        changelog_path (str): Custom path for changelog directory
    """
    # Convert to absolute path relative to current directory if path is relative
    if not Path(changelog_path).is_absolute():
        changelog_dir = Path.cwd() / changelog_path
    else:
        changelog_dir = Path(changelog_path)
    
    changelog_dir.mkdir(exist_ok=True, parents=True)
    
    today = date.today().strftime("%Y-%m-%d")
    file_path = changelog_dir / f"changelog-v{version}.md"
    
    # Build changelog content
    content = [
        "# Changelog",
        "",
        "All notable changes to this project will be documented in this file.",
        "",
        "## [Unreleased]",
    ]
    
    # Add sections
    sections = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
    
    # Add unreleased sections
    for section in sections:
        content.extend([f"### {section}", changes.get(f"unreleased_{section.lower()}", ""), ""])
    
    # Add version sections
    content.extend([f"## [{version}] - {today}"])
    
    for section in sections:
        content.extend([f"### {section}", changes.get(section.lower(), ""), ""])
    
    # Write to file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(Styles.SUCCESS(f"Changelog created: {file_path}"))
    except Exception as e:
        raise ValueError(Styles.ERROR(f"Failed to create changelog: {e}"))

def get_changelog_entries() -> Dict[str, str]:
    """Gather changelog entries from user input."""
    print_header("Changelog Entry", "Enter changes for each section (press Enter to skip)")
    
    changes = {}
    sections = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
    
    # Get unreleased changes
    print(Styles.CHANGELOG_SECTION("[Unreleased] Section:"))
    for section in sections:
        changes[f"unreleased_{section.lower()}"] = get_changelog_input(f"unreleased {section.lower()}")
    
    # Get version-specific changes
    print(Styles.CHANGELOG_SECTION("[Version] Section:"))
    for section in sections:
        changes[section.lower()] = get_changelog_input(section.lower())
    
    return changes

def merge_changelogs(output_file: str = "CHANGELOG.md", changelog_path: str = "changelog") -> None:
    """Merge all changelog files into a single file.
    
    Args:
        output_file (str): Output file name
        changelog_path (str): Custom path for changelog directory
    """
    print_header("Merging Changelogs", f"Output file: {output_file}")
    
    # Convert to absolute path relative to current directory if path is relative
    if not Path(changelog_path).is_absolute():
        changelog_dir = Path.cwd() / changelog_path
    else:
        changelog_dir = Path(changelog_path)
    
    if not changelog_dir.exists():
        raise FileNotFoundError(Styles.ERROR("No changelog directory found"))
    
    changelog_files = sorted(changelog_dir.glob("changelog-v*.md"), reverse=True)
    if not changelog_files:
        raise FileNotFoundError(Styles.ERROR("No changelog files found"))
    
    # Read and merge content
    merged_content = []
    for i, file_path in enumerate(changelog_files, 1):
        print_step(i, len(changelog_files), f"Processing {file_path.name}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if i == 1:  # First file includes header
                merged_content.append(content)
            else:  # Skip header for subsequent files
                section_start = content.find("## [")
                if section_start != -1:
                    merged_content.append(content[section_start:])
    
    # Write merged content
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n\n".join(merged_content))
        print(Styles.SUCCESS(f"Changelogs merged into: {output_file}"))
    except Exception as e:
        raise ValueError(Styles.ERROR(f"Failed to merge changelogs: {e}"))

def cli():
    """Command line interface for changelog management."""
    parser = argparse.ArgumentParser(description="Changelog management tool")
    parser.add_argument("--version", help="Version number")
    parser.add_argument("--merge", action="store_true", help="Merge changelog files")
    parser.add_argument("--output", default="CHANGELOG.md", help="Output file for merge")
    parser.add_argument("--path", default="changelog", help="Custom path for changelog directory")
    
    args = parser.parse_args()
    
    try:
        if args.merge:
            merge_changelogs(args.output, args.path)
        elif args.version:
            changes = {}
            sections = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
            for section in sections:
                changes[section.lower()] = get_changelog_input(section)
                changes[f"unreleased_{section.lower()}"] = get_changelog_input(f"Unreleased {section}")
            create_changelog(args.version, changes, args.path)
        else:
            parser.print_help()
    except Exception as e:
        print(Styles.ERROR(f"Error: {e}"), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    cli()
