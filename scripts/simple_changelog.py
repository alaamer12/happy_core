"""Simple changelog management script."""
import argparse
import sys
from datetime import date
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.styles import Styles, print_header

def get_changelog_entry() -> str:
    """Get a simple changelog entry from user."""
    return input(Styles.PROMPT("Enter changelog entry: ")).strip()

def create_changelog(version: str, entry: str, changelog_path: str = "changelog") -> None:
    """Create a simple changelog file for the given version.
    
    Args:
        version (str): Version number
        entry (str): Changelog entry content
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
    
    content = [
        "# Changelog",
        "",
        f"## [{version}] - {today}",
        "",
        entry
    ]
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(Styles.SUCCESS(f"Changelog created: {file_path}"))
    except Exception as e:
        raise ValueError(Styles.ERROR(f"Failed to create changelog: {e}"))

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
    
    merged_content = ["# Changelog", ""]
    
    for file_path in changelog_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            section_start = content.find("## [")
            if section_start != -1:
                merged_content.append(content[section_start:])
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n\n".join(merged_content))
        print(Styles.SUCCESS(f"Changelogs merged into: {output_file}"))
    except Exception as e:
        raise ValueError(Styles.ERROR(f"Failed to merge changelogs: {e}"))

def cli():
    """Command line interface for simple changelog management."""
    parser = argparse.ArgumentParser(description="Simple changelog management tool")
    parser.add_argument("--version", help="Version number")
    parser.add_argument("--merge", action="store_true", help="Merge changelog files")
    parser.add_argument("--output", default="CHANGELOG.md", help="Output file for merge")
    parser.add_argument("--path", default="changelog", help="Custom path for changelog directory")
    
    args = parser.parse_args()
    
    try:
        if args.merge:
            merge_changelogs(args.output, args.path)
        elif args.version:
            entry = get_changelog_entry()
            create_changelog(args.version, entry, args.path)
        else:
            parser.print_help()
    except Exception as e:
        print(Styles.ERROR(f"Error: {e}"), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    cli()
