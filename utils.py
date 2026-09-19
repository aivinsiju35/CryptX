"""
utils.py — Shared utility helpers for the Cipher Tool
Handles terminal colors, banners, and common input/output helpers.
"""

import os
import sys

# ── Try to use colorama for cross-platform color support ──────────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = BLUE = WHITE = ""
    class Style:
        BRIGHT = RESET_ALL = DIM = ""


# ── Color helper wrappers ─────────────────────────────────────────────────────

def red(text):     return f"{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}"
def green(text):   return f"{Fore.GREEN}{Style.BRIGHT}{text}{Style.RESET_ALL}"
def yellow(text):  return f"{Fore.YELLOW}{Style.BRIGHT}{text}{Style.RESET_ALL}"
def cyan(text):    return f"{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}"
def magenta(text): return f"{Fore.MAGENTA}{Style.BRIGHT}{text}{Style.RESET_ALL}"
def blue(text):    return f"{Fore.BLUE}{Style.BRIGHT}{text}{Style.RESET_ALL}"
def dim(text):     return f"{Style.DIM}{text}{Style.RESET_ALL}"
def bold(text):    return f"{Style.BRIGHT}{text}{Style.RESET_ALL}"


# ── Terminal UI helpers ───────────────────────────────────────────────────────

def clear():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def divider(char="─", width=60, color_fn=cyan):
    """Print a horizontal divider line."""
    print(color_fn(char * width))


def banner():
    """Print the application banner."""
    clear()
    divider("═", 60, cyan)
    print(cyan("  🔐  CryptX — Cipher & Password Tool"))
    print(dim("       Caesar · Vigenère · Frequency Analysis"))
    divider("═", 60, cyan)
    print()


def section_header(title: str):
    """Print a section header."""
    print()
    divider("─", 60, yellow)
    print(yellow(f"  ▶  {title}"))
    divider("─", 60, yellow)


def success(msg: str):
    print(f"\n  {green('✔')}  {msg}")


def error(msg: str):
    print(f"\n  {red('✖')}  {red(msg)}")


def info(msg: str):
    print(f"\n  {cyan('ℹ')}  {msg}")


def result_box(label: str, value: str):
    """Print a highlighted result box."""
    divider("·", 60, dim)
    print(f"  {cyan(label)}")
    print(f"  {green(value)}")
    divider("·", 60, dim)


def prompt(msg: str) -> str:
    """Prompt the user and return stripped input."""
    return input(f"\n  {yellow('?')}  {msg}: ").strip()


def prompt_int(msg: str, min_val: int = 0, max_val: int = 100) -> int:
    """Prompt for an integer within range."""
    while True:
        raw = prompt(msg)
        if raw.lstrip("-").isdigit():
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            else:
                error(f"Enter a number between {min_val} and {max_val}.")
        else:
            error("Please enter a valid integer.")


def pause():
    """Pause and wait for the user to press Enter."""
    input(f"\n  {dim('Press Enter to continue...')}")
