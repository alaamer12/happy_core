"""Comprehensive release management script."""
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

def get_release_notes(version: str) -> Dict[str, str]:
    """Gather comprehensive release notes."""
    print_header("Release Notes", f"Version {version}")
    
    sections = {
        "summary": "Release Summary",
        "features": "New Features",
        "improvements": "Improvements",
        "breaking": "Breaking Changes",
        "deprecations": "Deprecations",
        "fixes": "Bug Fixes",
        "security": "Security Updates",
        "dependencies": "Dependency Updates",
        "docs": "Documentation Updates",
        "contributors": "Contributors"
    }
    
    notes = {}
    for key, title in sections.items():
        print(Styles.SUBHEADER(f"\n{title}:"))
        notes[key] = input(Styles.PROMPT("Enter details (or press Enter to skip): ")).strip()
    
    return notes

def create_release_notes(version: str, notes: Dict[str, str], release_path: str = "releases") -> None:
    """Create release notes file.
    
    Args:
        version (str): Version number
        notes (Dict[str, str]): Release notes by section
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
        "\n## Release Summary",
        notes.get("summary", "No summary provided."),
        "\n## New Features",
        notes.get("features", "No new features in this release."),
        "\n## Improvements",
        notes.get("improvements", "No improvements in this release."),
        "\n## Breaking Changes",
        notes.get("breaking", "No breaking changes in this release."),
        "\n## Deprecations",
        notes.get("deprecations", "No deprecations in this release."),
        "\n## Bug Fixes",
        notes.get("fixes", "No bug fixes in this release."),
        "\n## Security Updates",
        notes.get("security", "No security updates in this release."),
        "\n## Dependency Updates",
        notes.get("dependencies", "No dependency updates in this release."),
        "\n## Documentation Updates",
        notes.get("docs", "No documentation updates in this release."),
    ]
    
    if notes.get("contributors"):
        content.extend([
            "\n## Contributors",
            "Thanks to the following contributors for this release:",
            notes["contributors"]
        ])
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(Styles.SUCCESS(f"\nRelease notes created: {file_path}"))
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
        print_step(len(merged_content), len(release_files) + 2, f"Processing {file_path.name}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            merged_content.append(content)
            merged_content.append("\n---\n")
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(merged_content))
        print(Styles.SUCCESS(f"\nRelease notes merged into: {output_file}"))
    except Exception as e:
        raise ValueError(Styles.ERROR(f"Failed to merge release notes: {e}"))

def cli():
    """Command line interface for release management."""
    parser = argparse.ArgumentParser(description="Comprehensive release management tool")
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
