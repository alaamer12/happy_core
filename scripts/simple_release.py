"""Simple release management script."""
import argparse
import sys
from datetime import date
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.styles import print_header, Styles


def get_release_notes(version: str) -> str:
    """Get simple release notes from user."""
    print_header("Release Notes", f"Version {version}")
    return input(Styles.PROMPT("Enter release notes: ")).strip()

def create_release_notes(version: str, notes: str, release_path: str = "releases") -> None:
    """Create simple release notes file.
    
    Args:
        version (str): Version number
        notes (str): Release notes content
        release_path (str): Custom path for releases directory
    """
    # Convert to absolute path relative to current directory if path is relative
    if not Path(release_path).is_absolute():
        release_dir = Path.cwd() / release_path
    else:
        release_dir = Path(release_path)
    
    release_dir.mkdir(exist_ok=True, parents=True)
    
    today = date.today().strftime("%Y-%m-%d")
    file_path = release_dir / f"release-v{version}.md"
    
    content = [
        f"# Release v{version}",
        f"\nRelease Date: {today}",
        "\n## Release Notes",
        notes or "No release notes provided."
    ]
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(Styles.SUCCESS(f"Release notes created: {file_path}"))
    except Exception as e:
        raise ValueError(Styles.ERROR(f"Failed to create release notes: {e}"))

def merge_releases(output_file: str = "RELEASES.md", release_path: str = "releases") -> None:
    """Merge all release notes into a single file.
    
    Args:
        output_file (str): Output file name
        release_path (str): Custom path for releases directory
    """
    print_header("Merging Release Notes", f"Output file: {output_file}")
    
    # Convert to absolute path relative to current directory if path is relative
    if not Path(release_path).is_absolute():
        release_dir = Path.cwd() / release_path
    else:
        release_dir = Path(release_path)
    
    if not release_dir.exists():
        raise FileNotFoundError(Styles.ERROR("No releases directory found"))
    
    release_files = sorted(release_dir.glob("release-v*.md"), reverse=True)
    if not release_files:
        raise FileNotFoundError(Styles.ERROR("No release files found"))
    
    merged_content = ["# Release History", ""]
    
    for file_path in release_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            merged_content.append(content)
            merged_content.append("\n---\n")
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(merged_content))
        print(Styles.SUCCESS(f"Release notes merged into: {output_file}"))
    except Exception as e:
        raise ValueError(Styles.ERROR(f"Failed to merge release notes: {e}"))

def cli():
    """Command line interface for simple release management."""
    parser = argparse.ArgumentParser(description="Simple release management tool")
    parser.add_argument("--version", help="Version number")
    parser.add_argument("--merge", action="store_true", help="Merge release notes")
    parser.add_argument("--output", default="RELEASES.md", help="Output file for merge")
    parser.add_argument("--path", default="releases", help="Custom path for releases directory")
    
    args = parser.parse_args()
    
    try:
        if args.merge:
            merge_releases(args.output, args.path)
        elif args.version:
            notes = get_release_notes(args.version)
            create_release_notes(args.version, notes, args.path)
        else:
            parser.print_help()
    except Exception as e:
        print(Styles.ERROR(f"Error: {e}"), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    cli()
