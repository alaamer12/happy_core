"""Shared styling for CLI scripts."""
from colorama import Fore, Style, init

# Initialize colorama
init()

class Icons:
    """Unicode icons for CLI output."""
    CHECK = "✓"
    CROSS = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    ARROW = "→"
    GEAR = "⚙"
    PENCIL = "✎"
    BULLET = "•"
    FOLDER = "📁"
    FILE = "📄"
    PACKAGE = "📦"
    CLOCK = "🕒"
    SEARCH = "🔍"
    TOOLS = "🛠"
    SPARKLES = "✨"
    ROCKET = "🚀"

class Styles:
    """Text styles for CLI output."""
    # Headers
    HEADER = lambda text: f"\n{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}"
    SUBHEADER = lambda text: f"{Fore.BLUE}{text}{Style.RESET_ALL}"
    
    # Status
    SUCCESS = lambda text: f"{Fore.GREEN}{Icons.CHECK} {text}{Style.RESET_ALL}"
    ERROR = lambda text: f"{Fore.RED}{Icons.CROSS} {text}{Style.RESET_ALL}"
    WARNING = lambda text: f"{Fore.YELLOW}{Icons.WARNING} {text}{Style.RESET_ALL}"
    INFO = lambda text: f"{Fore.CYAN}{Icons.INFO} {text}{Style.RESET_ALL}"
    
    # Input prompts
    PROMPT = lambda text: f"{Fore.CYAN}{Icons.ARROW} {text}{Style.RESET_ALL}"
    OPTION = lambda text: f"{Fore.YELLOW}{Icons.BULLET} {text}{Style.RESET_ALL}"
    
    # File operations
    FILE_OP = lambda text: f"{Fore.BLUE}{Icons.FILE} {text}{Style.RESET_ALL}"
    FOLDER_OP = lambda text: f"{Fore.BLUE}{Icons.FOLDER} {text}{Style.RESET_ALL}"
    
    # Version info
    VERSION_OLD = lambda text: f"{Fore.YELLOW}Old version: {text}{Style.RESET_ALL}"
    VERSION_NEW = lambda text: f"{Fore.GREEN}New version: {text}{Style.RESET_ALL}"
    
    # Changelog
    CHANGELOG_SECTION = lambda text: f"{Fore.MAGENTA}{Icons.PENCIL} {text}{Style.RESET_ALL}"
    CHANGELOG_ENTRY = lambda text: f"{Fore.WHITE}{Icons.BULLET} {text}{Style.RESET_ALL}"

def print_header(text: str, subtext: str = None) -> None:
    """Print a formatted header with optional subtext."""
    print(Styles.HEADER(text))
    if subtext:
        print(Styles.SUBHEADER(subtext))
    print()

def print_step(step: int, total: int, text: str) -> None:
    """Print a step in a multi-step process."""
    print(f"{Fore.CYAN}[{step}/{total}] {Icons.ARROW} {text}{Style.RESET_ALL}")

def print_options(options: list, prompt: str = "Choose an option:") -> None:
    """Print a list of options."""
    print(Styles.PROMPT(prompt))
    for i, option in enumerate(options, 1):
        print(Styles.OPTION(f"{i}. {option}"))
