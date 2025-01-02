import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# Add the project root directory to Python path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.styles import Styles as styles
from scripts.styles import print_header

# Check common project files
common_files = [
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "true/__init__.py",
]

def read_file_content(file_path: Path) -> str:
    with open(file_path, 'r') as f:
        return f.read()

def write_file_content(file_path: Path, content: str) -> None:
    with open(file_path, 'w') as f:
        f.write(content)

def get_version_increment(current_version: str, increment_type: str) -> str:
    """Calculate new version based on increment type."""
    major, minor, patch = map(int, current_version.split('.'))

    if increment_type.lower() == 'major':
        return f"{major + 1}.0.0"
    elif increment_type.lower() == 'minor':
        return f"{major}.{minor + 1}.0"
    elif increment_type.lower() == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError("Invalid version increment type")

def get_version_decrement(current_version: str) -> str:
    """Calculate previous version by decrementing patch number."""
    major, minor, patch = map(int, current_version.split('.'))
    if patch > 0:
        return f"{major}.{minor}.{patch - 1}"
    elif minor > 0:
        return f"{major}.{minor - 1}.0"
    elif major > 0:
        return f"{major - 1}.0.0"
    else:
        raise ValueError(styles.ERROR("Cannot decrement version 0.0.0"))

def update_version_in_content(content: str, old_version: str, new_version: str) -> str:
    """Update version while preserving the original format."""
    # First find how version is formatted in the file
    patterns = [
        r'version\s*=\s*"[^"]*"',  # version = "0.1.3"
        r'version\s*=\s*\'[^\']*\'',  # version = '0.1.3'
        r'version\s*=\s*[0-9.]+',  # version = 0.1.3
        r'__version__\s*=\s*"[^"]*"',  # __version__ = "0.1.3"
        r'__version__\s*=\s*\'[^\']*\'',  # __version__ = '0.1.3'
        r'VERSION\s*=\s*"[^"]*"',  # VERSION = "0.1.3"
        r'VERSION\s*=\s*\'[^\']*\'',  # VERSION = '0.1.3'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            # Get the matched version string
            old_str = match.group(0)
            # Create new string with updated version
            new_str = old_str.replace(old_version, new_version)
            # Replace in content
            content = content.replace(old_str, new_str)
            break
    
    return content

def update_version_in_file(file_path: Path, old_version: str, new_version: str) -> None:
    try:
        content = read_file_content(file_path)
        updated_content = update_version_in_content(content, old_version, new_version)
        write_file_content(file_path, updated_content)
        print(styles.SUCCESS(f"Successfully updated: {file_path}"))
    except Exception as e:
        print(styles.ERROR(f"Error updating {file_path}: {e}"))

def get_current_version(file_path: Path) -> str:
    """Extract version from various file formats."""
    try:
        content = read_file_content(file_path)
        
        # Try different version patterns
        patterns = [
            r'version\s*=\s*["\']?(\d+\.\d+\.\d+)["\']?',  # Matches: version = "X.Y.Z" or version = X.Y.Z
            r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # Matches: __version__ = "X.Y.Z"
            r'VERSION\s*=\s*["\'](\d+\.\d+\.\d+)["\']',  # Matches: VERSION = "X.Y.Z"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        raise ValueError(styles.ERROR(f"No version pattern found in {file_path}"))
    except Exception as e:
        raise ValueError(styles.ERROR(f"Failed to extract version: {e}"))

def validate_files(files: List[Path], quiet: bool) -> None:
    if not quiet:
        print(styles.INFO("Checking files..."))
    for file_path in files:
        if not file_path.exists():
            raise FileNotFoundError(styles.ERROR(f"File not found: {file_path}"))
        if not quiet:
            print(styles.FILE_OP(f"Found: {file_path}"))

def get_increment_type() -> str:
    print_header("Version Update Options")
    print(styles.OPTION("major - For significant changes"))
    print(styles.OPTION("minor - For new features"))
    print(styles.OPTION("patch - For bug fixes"))
    
    while True:
        increment_type = input(styles.PROMPT("Choose version type (major/minor/patch): ")).lower()
        if increment_type in ['major', 'minor', 'patch']:
            return increment_type
        print(styles.ERROR("Invalid input. Please choose 'major', 'minor', or 'patch'"))

def check_version_consistency(files: List[Path], quiet: bool = False) -> str:
    """Check if all files have the same version number."""
    versions = {}
    for file_path in files:
        try:
            version = get_current_version(file_path)
            versions[str(file_path)] = version
        except Exception as e:
            raise ValueError(styles.ERROR(f"Failed to get version from {file_path}: {e}"))
    
    if not versions:
        raise ValueError(styles.ERROR("No version information found in any files"))
    
    unique_versions = set(versions.values())
    if len(unique_versions) > 1:
        error_msg = "Version mismatch detected:\n"
        for file_path, version in versions.items():
            error_msg += styles.FILE_OP(f"  {file_path}: {version}\n")
        raise ValueError(styles.ERROR(error_msg))
    
    if not quiet:
        print(styles.SUCCESS(f"All files have consistent version: {list(unique_versions)[0]}"))
    
    return list(unique_versions)[0]

def rollback_files(files: List[Path], quiet: bool = False) -> None:
    """Roll back version by decrementing the version number."""
    if not quiet:
        print(styles.INFO("Rolling back version..."))
    
    try:
        current_version = check_version_consistency(files, quiet)
        previous_version = get_version_decrement(current_version)
        
        if not quiet:
            print(styles.INFO(f"Rolling back from {styles.VERSION_OLD(current_version)} to {styles.VERSION_NEW(previous_version)}"))
        
        for file_path in files:
            update_version_in_file(file_path, current_version, previous_version)
            
        if not quiet:
            print(styles.SUCCESS("Version rollback complete"))
            
    except Exception as e:
        raise ValueError(styles.ERROR(f"Failed to rollback version: {e}"))

def get_changelog_input(section: str, quiet: bool = False) -> str:
    """Get changelog input for a specific section."""
    if quiet:
        return ""
    changes = input(styles.PROMPT(f"Enter {section} (separate with commas or press Enter to skip): ")).strip()
    return changes

def create_changelog(version: str, changes: Dict[str, str], quiet: bool = False, changelog_path: str = "changelog", root_dir: Optional[Path] = None) -> None:
    """Create a changelog file for the given version."""
    if not quiet:
        print_header("Creating Changelog", f"Version {version}")
    
    # Convert to absolute path relative to root_dir if path is relative
    if root_dir and not Path(changelog_path).is_absolute():
        abs_changelog_path = str(root_dir / changelog_path)
    else:
        abs_changelog_path = str(Path(changelog_path))
    
    from scripts.changelog import create_changelog as create_changelog_file
    create_changelog_file(version, changes, abs_changelog_path)

def update_version(root_dir: Path, increment_type: Optional[str] = None, quiet: bool = False, 
                   rollback: bool = False, include_changelogs: bool = False,
                   changelog_path: str = "changelog", release_path: str = "releases") -> str:
    """Update version in all relevant files."""
    if not quiet:
        print_header("Version Update Tool", f"Working directory: {root_dir}")

    validate_root_directory(root_dir)
    files_to_update = find_version_files(root_dir)
    validate_files(files_to_update, quiet)

    if rollback:
        return perform_rollback(files_to_update, quiet)

    current_version = check_version_consistency(files_to_update, quiet)
    new_version = determine_new_version(current_version, increment_type, quiet)

    try:
        update_files_with_new_version(files_to_update, current_version, new_version, quiet)
        handle_changelog_creation(include_changelogs, new_version, quiet, changelog_path, release_path, root_dir)
        display_update_summary(current_version, new_version, quiet)
    except Exception as e:
        handle_update_error(e, files_to_update, quiet)

    return new_version

def validate_root_directory(root_dir: Path) -> None:
    if not root_dir.exists():
        raise FileNotFoundError(styles.ERROR(f"Directory not found: {root_dir}"))

def find_version_files(root_dir: Path) -> List[Path]:
    files_to_update = [root_dir / file for file in common_files if (root_dir / file).exists()]
    package_init = find_package_init(root_dir)
    if package_init:
        files_to_update.append(package_init)
    if not files_to_update:
        raise FileNotFoundError(styles.ERROR(f"No version files found in: {root_dir}"))
    return files_to_update

def find_package_init(root_dir: Path) -> Optional[Path]:
    package_name = get_package_name(root_dir)
    if package_name:
        package_dir = package_name.replace('-', '_')
        init_file = root_dir / package_dir / "__init__.py"
        if init_file.exists():
            return init_file
    return None

def get_package_name(root_dir: Path) -> Optional[str]:
    for config_file in ["pyproject.toml", "setup.cfg"]:
        config_path = root_dir / config_file
        if config_path.exists():
            with open(config_path) as f:
                content = f.read()
                if 'name = "' in content or 'name = ' in content:
                    return content.split('name = ')[1].split('"')[0].strip()
    return None

def perform_rollback(files_to_update: List[Path], quiet: bool) -> str:
    rollback_files(files_to_update, quiet)
    return ""

def determine_new_version(current_version: str, increment_type: Optional[str], quiet: bool) -> str:
    if increment_type is None:
        increment_type = get_increment_type()
    if not quiet:
        print(styles.INFO(f"Current Version: {current_version}"))
    return get_version_increment(current_version, increment_type)

def update_files_with_new_version(files_to_update: List[Path], current_version: str, new_version: str, quiet: bool) -> None:
    if not quiet:
        print(styles.INFO("Updating version in files..."))
    for file_path in files_to_update:
        update_version_in_file(file_path, current_version, new_version)

def handle_changelog_creation(include_changelogs: bool, new_version: str, quiet: bool, 
                              changelog_path: str, release_path: str, root_dir: Path) -> None:
    if include_changelogs:
        changes = get_changelog_entries(quiet)
        abs_changelog_path = get_absolute_path(changelog_path, root_dir)
        abs_release_path = get_absolute_path(release_path, root_dir)
        create_changelog(new_version, changes, quiet, abs_changelog_path, root_dir)
        create_release_notes(new_version, changes, abs_release_path)

def get_absolute_path(path: str, root_dir: Path) -> str:
    return str(root_dir / path) if not Path(path).is_absolute() else path

def create_release_notes(new_version: str, changes: Dict[str, str], release_path: str) -> None:
    from scripts.simple_release import create_release_notes
    notes = " ".join(changes.get(section.lower(), "") for section in ["Added", "Changed", "Fixed"])
    create_release_notes(new_version, notes, release_path)

def display_update_summary(current_version: str, new_version: str, quiet: bool) -> None:
    if not quiet:
        print_header("Version Update Complete")
        print(styles.VERSION_OLD(current_version))
        print(styles.VERSION_NEW(new_version))

def handle_update_error(e: Exception, files_to_update: List[Path], quiet: bool) -> None:
    print(styles.ERROR(f"Error during update: {e}"))
    print(styles.WARNING("Rolling back changes..."))
    rollback_files(files_to_update, quiet)
    raise

def get_changelog_entries(quiet: bool = False) -> Dict[str, str]:
    """Gather changelog entries from user input."""
    if not quiet:
        print_header("Changelog Entry", "Enter changes for each section (press Enter to skip)")
    
    changes = {}
    sections = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
    
    # Get unreleased changes
    if not quiet:
        print(styles.CHANGELOG_SECTION("[Unreleased] Section:"))
    for section in sections:
        changes[f"unreleased_{section.lower()}"] = get_changelog_input(f"unreleased {section.lower()}", quiet)
    
    # Get version-specific changes
    if not quiet:
        print(styles.CHANGELOG_SECTION("[Version] Section:"))
    for section in sections:
        changes[section.lower()] = get_changelog_input(section.lower(), quiet)
    
    return changes

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Update version numbers in project files")
    parser.add_argument("-t", "--type", choices=["major", "minor", "patch"], help="Type of version increment")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output messages")
    parser.add_argument("-r", "--rollback", action="store_true", help="Rollback to previous version")
    
    add_changelog_arguments(parser)
    add_release_arguments(parser)
    
    parser.add_argument("--changelog-path", default="changelog", help="Custom path for changelog directory")
    parser.add_argument("--release-path", default="releases", help="Custom path for releases directory")
    
    add_usage_examples(parser)
    
    return parser.parse_args()

def add_changelog_arguments(parser):
    """Add changelog-related arguments to the parser."""
    changelog_group = parser.add_mutually_exclusive_group()
    changelog_group.add_argument("-sc", "--simple-changelog", action="store_true", help="Create a simple changelog entry")
    changelog_group.add_argument("-cc", "--comprehensive-changelog", action="store_true", help="Create a comprehensive changelog")

def add_release_arguments(parser):
    """Add release-related arguments to the parser."""
    release_group = parser.add_mutually_exclusive_group()
    release_group.add_argument("-sr", "--simple-release", action="store_true", help="Create simple release notes")
    release_group.add_argument("-cr", "--comprehensive-release", action="store_true", help="Create comprehensive release notes")

def add_usage_examples(parser):
    """Add usage examples to the parser."""
    parser.epilog = """
Examples:
  # Update patch version with simple changelog and release
  update_version.py -t patch -sc -sr
  
  # Update minor version with comprehensive changelog and release
  update_version.py -t minor -cc -cr
  
  # Update major version quietly with simple changelog
  update_version.py -t major -q -sc
  
  # Rollback to previous version
  update_version.py -r
    """
    parser.formatter_class = argparse.RawDescriptionHelpFormatter

def handle_version_update(args):
    """Handle version update based on arguments."""
    root_dir = Path.cwd()
    if args.rollback:
        return update_version(root_dir, rollback=True, quiet=args.quiet)
    return update_version(
        root_dir,
        increment_type=args.type,
        quiet=args.quiet,
        include_changelogs=args.comprehensive_changelog,
        changelog_path=args.changelog_path,
        release_path=args.release_path
    )

def handle_changelog_creation_utility(args, new_version, path):
    """Handle changelog creation based on arguments."""
    if args.simple_changelog:
        from scripts.simple_changelog import create_changelog, get_changelog_entry
        entry = get_changelog_entry()
        create_changelog(new_version, entry, path)
    elif args.comprehensive_changelog:
        from scripts.changelog import create_changelog, get_changelog_entries
        changes = get_changelog_entries()
        create_changelog(new_version, changes, path)

def handle_release_notes_creation(args, new_version, path):
    """Handle release notes creation based on arguments."""
    if args.simple_release:
        from scripts.simple_release import create_release_notes, get_release_notes
        notes = get_release_notes(new_version)
        create_release_notes(new_version, notes, path)
    elif args.comprehensive_release:
        from scripts.release import create_release_notes, get_release_notes
        notes = get_release_notes(new_version)
        create_release_notes(new_version, notes, path)

def cli():
    """Command line interface for the version updater."""
    args = parse_arguments()
    
    try:
        new_version = handle_version_update(args)
        changelog_path = args.changelog_path
        release_path = args.release_path
        print_header(changelog_path)
        print_header(release_path)
        handle_changelog_creation_utility(args, new_version, changelog_path)
        handle_release_notes_creation(args, new_version, release_path)
    except Exception as e:
        print(styles.ERROR(f"Error: {e}"), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    cli()