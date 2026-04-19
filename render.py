import re, keyword

# ANSI Color / Style helpers
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

# Foreground colors
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Bright foreground
B_RED = "\033[91m"
B_GREEN = "\033[92m"
B_YELLOW = "\033[93m"
B_BLUE = "\033[94m"
B_MAGENTA = "\033[95m"
B_CYAN = "\033[96m"
B_WHITE = "\033[97m"

# Background colors
BG_BLACK = "\033[40m"
BG_BLUE = "\033[44m"
BG_CYAN = "\033[46m"
BG_DARK = "\033[48;5;235m"
BG_CODE = "\033[48;5;236m"

DIFFICULTY_COLOR = {"Easy": B_GREEN, "Medium": B_YELLOW, "Hard": B_RED}

# Python highlights
_BUILTINS = {
    "print",
    "len",
    "range",
    "enumerate",
    "zip",
    "map",
    "filter",
    "sorted",
    "list",
    "dict",
    "set",
    "tuple",
    "int",
    "str",
    "float",
    "bool",
    "type",
    "None",
    "True",
    "False",
    "self",
    "cls",
    "append",
    "extend",
    "pop",
    "get",
    "items",
    "values",
    "keys",
    "heappush",
    "heappop",
}
_KW = set(keyword.kwlist)
_TOK = re.compile(
    "|".join(
        f"(?P<{n}>{p})"
        for n, p in [
            ("COMMENT", r"#[^\n]*"),
            ("STRING3D", r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''),
            ("STRING", r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\''),
            ("NUMBER", r"\b\d+(?:\.\d+)?\b"),
            (
                "KEYWORD",
                r"\b(?:" + "|".join(sorted(_KW, key=len, reverse=True)) + r")\b",
            ),
            (
                "BUILTIN",
                r"\b(?:" + "|".join(sorted(_BUILTINS, key=len, reverse=True)) + r")\b",
            ),
            ("FUNC_DEF", r"(?<=def )\w+"),
            ("CLASS_DEF", r"(?<=class )\w+"),
            ("OTHER", r".|\n"),
        ]
    ),
    re.DOTALL,
)


def print_markdown(text: str) -> None:
    """Renders and prints text as markdown."""
    for line in text.split("\n"):
        stripped = line.strip()

        # Bold **text**
        line = re.sub(r"\*\*(.+?)\*\*", f"{BOLD}\\1{RESET}", line)
        # Inline code `text`
        line = re.sub(
            r"`([^`]+)`", f"{BG_CODE} {CYAN}\\1{RESET}{BG_CODE} {RESET}", line
        )

        if (
            stripped.startswith("Input:")
            or stripped.startswith("Output:")
            or stripped.startswith("Explanation:")
        ):
            key, _, rest = stripped.partition(":")
            print(f"  {BOLD}{B_CYAN}{key}:{RESET}{rest}")
        elif stripped.startswith("- "):
            print(f"  {CYAN}•{RESET} {line.lstrip('- ')}")
        elif stripped.startswith("**") and stripped.endswith("**"):
            print(f"  {BOLD}{B_WHITE}{stripped.strip('*')}{RESET}")
        else:
            print(f"  {line}")


def python_highlight(code: str) -> str:
    """Adds highlight codes to a single line of python code."""
    out = []
    for m in _TOK.finditer(code):
        k, v = m.lastgroup, m.group()
        if k == "COMMENT":
            out.append(f"{DIM}{GREEN}{v}{RESET}")
        elif k in ("STRING3D", "STRING"):
            out.append(f"{YELLOW}{v}{RESET}")
        elif k == "NUMBER":
            out.append(f"{B_MAGENTA}{v}{RESET}")
        elif k == "KEYWORD":
            out.append(f"{BOLD}{B_BLUE}{v}{RESET}")
        elif k == "BUILTIN":
            out.append(f"{CYAN}{v}{RESET}")
        elif k == "FUNC_DEF":
            out.append(f"{BOLD}{B_GREEN}{v}{RESET}")
        elif k == "CLASS_DEF":
            out.append(f"{BOLD}{B_YELLOW}{v}{RESET}")
        else:
            out.append(v)
    return "".join(out)


# Print highlighted python code
def print_code(code: str) -> None:
    """Renders and prints text as Python code"""
    lines = code.rstrip().split("\n")
    w = len(str(len(lines)))
    for i, line in enumerate(lines, 1):
        print(f"{DIM}{i:>{w}}{RESET} {python_highlight(line)}")


def print_problem(problem):
    color = DIFFICULTY_COLOR.get(problem["difficulty"], WHITE)
    tags = ", ".join(f"{t}" for t in problem.get("tags", []))

    print(
        f"\n{BOLD}{problem['id']}. {problem['title']}{RESET}  [{color}{problem['difficulty']}{RESET}]"
    )
    print(f"{DIM}{tags}{RESET}\n")
    print(f"  {BOLD}{B_MAGENTA}DESCRIPTION{RESET}\n")
    print_markdown(problem["description"])


def prompt_solution():
    input(f"\n{DIM}[enter to reveal]{RESET}")


def print_solution(problem):

    verified_string = f"[{B_YELLOW}UNVERIFIED{RESET}]"
    if problem['verified']:
        verified_string = f"[{B_GREEN}VERIFIED{RESET}]"

    if problem.get('easy_solution'):
        print()
        print(f"  {BOLD}{B_MAGENTA}SUBOPTIMAL APPROACH{RESET}\n")
        print_markdown(problem["easy_approach"])

        print(f"  {BOLD}{B_MAGENTA}SUBOPTIMAL COMPLEXITY{RESET}\n")
        print(f"  Time: {problem['easy_time']}")
        print(f"  Space: {problem['easy_space']}")

        print()
        print(f"  {BOLD}{B_MAGENTA}SUBOPTIMAL_SOLUTION{RESET}\n")
        print_code(problem["easy_solution"])
        print()


    print()
    print(f"  {BOLD}{B_MAGENTA}APPROACH{RESET}\n")
    print_markdown(problem["approach"])

    print(f"  {BOLD}{B_MAGENTA}COMPLEXITY{RESET}\n")
    print(f"  Time: {problem['time']}")
    print(f"  Space: {problem['space']}")

    print()
    print(f"  {BOLD}{B_MAGENTA}SOLUTION{RESET} {verified_string}\n")
    print_code(problem["solution"])
    print()


def list_problems(problems):
    print(f"  {BOLD}{B_MAGENTA}PROBLEMS{RESET}\n")

    width = len(str(max(p["id"] for p in problems)))

    for p in problems:
        color = DIFFICULTY_COLOR.get(p["difficulty"], WHITE)
        print(f"  {BOLD}{CYAN}{p['id']:{width}}{RESET}. {color}{p['title']}{RESET}")
