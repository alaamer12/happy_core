import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from colorama import init, Fore, Style

# Initialize colorama
init()


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


def update_version_in_file(file_path: Path, old_version: str, new_version: str) -> None:
    """Update version number in a single file."""
    try:
        with open(file_path, 'r+') as f:
            content = f.read()
            content = content.replace(old_version, new_version)
            f.seek(0)
            f.write(content)
            f.truncate()
        print(f"{Fore.GREEN}✓ Successfully updated{Style.RESET_ALL}: {file_path}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error updating {file_path}: {e}{Style.RESET_ALL}")


def get_current_version(file_path: Path) -> str:
    """Extract current version from pyproject.toml."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            return content.split('version = "')[1].split('"')[0]
    except Exception as e:
        raise ValueError(f"Failed to extract version: {e}")


def update_version(root_dir: Path, increment_type: Optional[str] = None, quiet: bool = False) -> None:
    """Main function to update version numbers."""
    if not quiet:
        print(f"\n{Fore.CYAN}📦 Version Update Tool{Style.RESET_ALL}\n")

    # Validate directory exists
    if not root_dir.exists():
        raise FileNotFoundError(f"{Fore.RED}❌ Directory not found: {root_dir}{Style.RESET_ALL}")

    # Files to update
    files_to_update = [
        root_dir / "pyproject.toml",
        root_dir / "true" / "__init__.py",
        root_dir / "setup.cfg",
        root_dir / "setup.py"
    ]

    # Validate all files exist
    if not quiet:
        print(f"{Fore.YELLOW}🔍 Checking files...{Style.RESET_ALL}")
    for file_path in files_to_update:
        if not file_path.exists():
            raise FileNotFoundError(f"{Fore.RED}❌ File not found: {file_path}{Style.RESET_ALL}")
        if not quiet:
            print(f"{Fore.GREEN}✓ Found{Style.RESET_ALL}: {file_path}")

    # Get version increment type if not provided
    if increment_type is None:
        if not quiet:
            print(f"\n{Fore.CYAN}🔄 Version Update Options:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}major{Style.RESET_ALL} - For significant changes")
            print(f"{Fore.YELLOW}minor{Style.RESET_ALL} - For new features")
            print(f"{Fore.YELLOW}patch{Style.RESET_ALL} - For bug fixes")

        while True:
            increment_type = input(f"\n{Fore.CYAN}⚡ Choose version type (major/minor/patch): {Style.RESET_ALL}").lower()
            if increment_type in ['major', 'minor', 'patch']:
                break
            print(f"{Fore.RED}❌ Invalid input. Please choose 'major', 'minor', or 'patch'{Style.RESET_ALL}")

    current_version = get_current_version(files_to_update[0])
    if not quiet:
        print(f"\n{Fore.CYAN}🔄 Current Version: {Style.RESET_ALL}{current_version}")

    new_version = get_version_increment(current_version, increment_type)

    # Change to root directory
    os.chdir(root_dir)

    # Update version in all files
    if not quiet:
        print(f"\n{Fore.YELLOW}🔄 Updating version in files...{Style.RESET_ALL}")
    for file_path in files_to_update:
        update_version_in_file(file_path, current_version, new_version)

    if not quiet:
        print(f"\n{Fore.GREEN}✨ Version successfully updated:{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}Old version:{Style.RESET_ALL} {current_version}")
        print(f"  {Fore.GREEN}New version:{Style.RESET_ALL} {new_version}")


def cli():
    """Command line interface for the version updater."""
    parser = argparse.ArgumentParser(
        description="Update version numbers across project files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  update_version.py --type patch
  update_version.py --type minor --path /path/to/project
  update_version.py --type major --quiet
        """
    )

    parser.add_argument(
        '--type', '-t',
        choices=['major', 'minor', 'patch'],
        help='Type of version increment'
    )

    parser.add_argument(
        '--path', '-p',
        type=Path,
        default=Path.cwd(),
        help='Path to project root directory'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress all non-error output'
    )

    args = parser.parse_args()

    try:
        update_version(
            root_dir=args.path,
            increment_type=args.type,
            quiet=args.quiet
        )
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli()
