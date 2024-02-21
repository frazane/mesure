"""Utility functions."""
import typing as tp
import re



###############################################################################
# Terminal output
###############################################################################

def colored(st, color: str | None = None, background=False):
    colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    if color is not None:
        colorfmt = (
            10 * background
            + 60 * (color.upper() == color)
            + 30
            + colors.index(color.lower())
        )
        return f"\u001b[{colorfmt}m{st}\u001b[0m"
    else:
        return st

def colored256(text, fg_color=None, bg_color=None):
    fg_color = f"38;5;{fg_color}" if fg_color is not None else ""
    bg_color = f"48;5;{bg_color}" if bg_color is not None else ""
    return f"\033[{bg_color};{fg_color}m{text}\033[0;0m"


def styled(text: str, style: str) -> str:

    styles = {
        "bold": ("\033[1m", "\033[0m"),
        "italic": ("\033[3m", "\033[0m"),
        "underline": ("\033[4m", "\033[0m"),
    }
    
    start_code, end_code = styles[style]
    return f"{start_code}{text}{end_code}"

def scale_memory_units(memory_bytes, unit: tp.Literal["auto", "MB", "KB", "GB"] = "auto"):
    units = {"B": 1, "KB": 1e-3, "MB": 1e-6, "GB": 1e-9}

    if unit == "auto":
        for unit, multiplier in units.items():
            scaled_memory = memory_bytes * multiplier
            if abs(scaled_memory) <= 1000.0:
                break
        return scaled_memory, unit
    elif unit in ("MB", "KB", "GB"):
        scaled_memory = memory_bytes * units[unit]
    else:
        raise ValueError(f"Invalid unit: {unit}")
    return scaled_memory, unit

def scale_time_units(time_seconds, unit: tp.Literal["auto", "s", "ms", "μs", "ns"] = "auto"):
    units = {"s": 1, "ms": 1e-3, "μs": 1e-6, "ns": 1e-9}

    if unit == "auto":
        for unit, multiplier in units.items():
            scaled_time = time_seconds / multiplier
            if scaled_time >= 0.1:
                break
    elif unit in ("s", "ms", "μs", "ns"):
        scaled_time = time_seconds / units[unit]
    else:
        raise ValueError(f"Invalid unit: {unit}")
    
    return scaled_time, unit


def time_unit_str(time, unit):
    if time >= 10:
        time_str = f"{time:.1f}"
    else:
        time_str = f"{time:.2f}"
    return f"{time_str} {unit}"


###############################################################################
# Syntax highlighting
###############################################################################



def syntax_highlight(code):
    # Color codes
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    BRIGHT_GREEN = "\033[38;5;72m"
    BRIGHT_YELLOW = "\033[38;5;186m"
    ORANGE = "\033[38;5;216m"
    RESET = "\033[0m"

    keywords = [ # def is excluded on purpose, as it is handled separately
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue','del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
        'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield'
    ]

    # Regex to match strings, reserved keywords, 'def' followed by function names, and comments
    pattern = (
        r'(\".*?[^\\]\"|\'.*?[^\\]\')'  # Strings
        r'|(\b' + r'\b|\b'.join(keywords) + r'\b)'  # Keywords
        r'|(def\s+)(\w+)'  # 'def' keyword and function names
        r'|(#.*)'  # Comments
        r'|(\b\d+\b)'  # Numbers
    )
    
    def replacer(match):
        if match.group(1):  # Strings
            return f"{GREEN}{match.group(1)}{RESET}"
        elif match.group(2):  # Keywords
            return f"{BLUE}{match.group(2)}{RESET}"
        elif match.group(3) and match.group(4):  # 'def' keyword and function names
            # Apply blue to 'def' and yellow to the function name
            return f"{BLUE}{match.group(3)}{RESET}{BRIGHT_YELLOW}{match.group(4)}{RESET}"
        elif match.group(5):  # Comments
            return f"{ORANGE}{match.group(5)}{RESET}"
        elif match.group(6):  # Numbers
            return f"{BRIGHT_GREEN}{match.group(6)}{RESET}"
        else:
            return match.group(0)  # Default, should not be reached
    
    # Replace using the replacer function, with multiline support for comments
    highlighted_code = re.sub(pattern, replacer, code, flags=re.MULTILINE)
    
    return highlighted_code
