# Claude Code Prompt: Build the `drakedrakemayemaye` Interpreter

## Overview

Build a fully functional Python-compatible interpreter called **`drakedrakemayemaye`** (stylized as `Drakedrakemayemaye`) that uses Drake Maye bracket syntax instead of standard brackets. Files use the `.ddmm` extension. It should be installable via pip, callable from the command line identically to how `python` is used, and support 100% of Python's functionality (imports, stdlib, pip packages, etc.) — because under the hood it IS Python, just with a pre-processing transformation layer.

---

## Bracket Mapping

The ONLY syntactic difference from Python is the bracket system:

| Drake Maye | Python | Description       |
|------------|--------|-------------------|
| `drake`    | `(`    | Open paren        |
| `maye`     | `)`    | Close paren       |
| `Drake`    | `{`    | Open curly brace  |
| `Maye`     | `}`    | Close curly brace |
| `DRAKE`    | `[`    | Open square bracket |
| `MAYE`     | `]`    | Close square bracket |

**Case sensitivity is critical.** `drake`, `Drake`, and `DRAKE` are three distinct tokens mapping to three distinct brackets.

---

## Architecture

### Recommended Approach: Source-to-Source Transpiler + CPython

Do NOT try to fork CPython or modify a grammar. Instead:

1. **Transpiler module** (`drakedrakemayemaye/transpiler.py`): A token-aware source transformer that converts `.ddmm` source → valid Python source, then hands it to the standard Python interpreter.

2. **Import hook** (`drakedrakemayemaye/importer.py`): A custom `importlib` finder/loader that lets `.ddmm` files import OTHER `.ddmm` files using standard `import` syntax. This is critical for multi-file projects.

3. **CLI entry point** (`drakedrakemayemaye/cli.py`): A command-line interface that mirrors `python`'s CLI interface as closely as possible.

4. **Package setup** (`pyproject.toml` or `setup.py`): Makes `drakedrakemayemaye` pip-installable and registers the CLI command.

---

## Transpiler Requirements (`transpiler.py`)

### Core transformation function: `transform(source: str) -> str`

This is the heart of the project. It must be **token-aware**, NOT a naive regex/string replace. Specifically:

#### Must transform:
- `drake` → `(`, `maye` → `)` (lowercase → parentheses)
- `Drake` → `{`, `Maye` → `}` (Title case → curly braces)
- `DRAKE` → `[`, `MAYE` → `]` (UPPER CASE → square brackets)

#### Must NOT transform:
- Content inside **regular string literals**: `"drake"`, `'Drake'`, `"""DRAKE"""`
- Content inside **comments**: `# drake maye`
- Content inside **byte strings**: `b"drake"`
- **Partial word matches**: `drakesmith`, `drakes`, `undrakeable`, `mayefield` must NOT be touched. Only standalone tokens bounded by non-identifier characters should match.

#### Must correctly handle:
- **f-string expressions**: Inside `{}` expressions within f-strings, drake/maye tokens SHOULD be transformed. The literal text portions of f-strings should NOT be transformed. Example:
  ```
  f"Hello {name.upper drake maye}" → f"Hello {name.upper()}"
  ```
- **Nested f-strings** (Python 3.12+): `f"{ f'{x}' }"` — handle recursion
- **Raw strings**: `r"drake"` — do NOT transform
- **Escape sequences**: `"dra\"ke"` — handle escaped quotes correctly
- **Triple-quoted strings**: `"""..."""` and `'''...'''` — handle multi-line
- **String prefixes**: `f`, `r`, `b`, `rb`, `br`, `fr`, `rf`, `F`, `R`, `B`, etc.
- **Multi-line expressions**: drake/maye across lines with `\` continuation or inside brackets
- **Mixed bracket nesting**: `drake DRAKE Drake Maye MAYE maye` → `([{}])`

#### Recommended approach:
Walk character by character through the source. Maintain state for:
- Whether you're inside a string (and what kind)
- Whether you're inside a comment
- Whether you're inside an f-string expression `{}`
- Brace depth for f-string expression tracking

Check word boundaries using the character before and after any potential match — if either is alphanumeric or `_`, it's part of an identifier and must not be replaced.

### Reverse transformation: `reverse_transform(source: str) -> str`

Also implement the reverse (Python → Drake Maye) for tooling support. Same rules apply in reverse. This enables converting existing `.py` files to `.ddmm`.

---

## Import Hook (`importer.py`)

Implement a custom import system so `.ddmm` files can import each other:

```python
# main.ddmm
from utils import helper  # should find utils.ddmm

# utils.ddmm
def helper drake maye:
    return "it works"
```

### Implementation:
- Subclass `importlib.abc.MetaPathFinder` and `importlib.abc.Loader`
- The finder should look for `.ddmm` files on `sys.path`
- The loader should read the `.ddmm` file, run it through `transform()`, compile the result, and exec it into the module namespace
- Register the hook in `sys.meta_path` early (in CLI startup and in any programmatic usage)
- `.ddmm` files should also be able to import standard `.py` modules and pip packages normally — this should work automatically since we only intercept when a `.ddmm` file exists
- Support `__init__.ddmm` for packages

### Caching:
- Cache compiled bytecode in `__ddmmcache__/` directories (similar to `__pycache__/`)
- Use source file mtime for cache invalidation
- Store as `.ddmm.pyc` or similar

---

## CLI Entry Point (`cli.py`)

After pip install, the command `drakedrakemayemaye` should work like `python`:

```bash
# Run a file
drakedrakemayemaye main.ddmm

# Interactive REPL
drakedrakemayemaye

# Inline execution
drakedrakemayemaye -c "print drake 'hello' maye"

# Module execution
drakedrakemayemaye -m module_name

# Pass arguments to script
drakedrakemayemaye main.ddmm --flag value

# Show version
drakedrakemayemaye --version

# Show transformed source (bonus debug flag)
drakedrakemayemaye --show-transform main.ddmm

# Convert .py to .ddmm
drakedrakemayemaye --convert file.py

# Convert .ddmm to .py
drakedrakemayemaye --to-python file.ddmm
```

### Supported `python`-equivalent flags (implement at minimum):
- `-c <code>` — run inline code
- `-m <module>` — run a module
- `-i` — inspect interactively after running a script
- `-V` / `--version` — print version
- `-h` / `--help` — print help
- `-u` — unbuffered stdout/stderr
- `-E` — ignore environment variables
- Remaining argv after the script path should be passed through to `sys.argv`

### REPL:
- Full interactive REPL with readline support (history, tab completion)
- Custom prompt: `ddmm>>> ` and `ddmm... ` for continuation lines
- Startup banner with ASCII art and bracket mapping reference
- Support multi-line input (detect incomplete expressions)
- Transform each input line/block before executing

---

## Package Structure

```
drakedrakemayemaye/
├── pyproject.toml
├── README.md
├── LICENSE
├── drakedrakemayemaye/
│   ├── __init__.py          # Package init, version
│   ├── transpiler.py        # Core transform / reverse_transform
│   ├── importer.py          # Import hook for .ddmm files
│   ├── cli.py               # CLI entry point
│   ├── repl.py              # Interactive REPL
│   └── compat.py            # Python version compat helpers
├── tests/
│   ├── test_transpiler.py   # Unit tests for transformation
│   ├── test_importer.py     # Tests for import system
│   ├── test_cli.py          # CLI integration tests
│   ├── test_edge_cases.py   # String/fstring/comment edge cases
│   └── fixtures/            # Sample .ddmm files for testing
│       ├── hello.ddmm
│       ├── imports/
│       │   ├── main.ddmm
│       │   └── utils.ddmm
│       ├── classes.ddmm
│       ├── edge_cases.ddmm
│       └── stdlib_usage.ddmm
└── examples/
    ├── hello_world.ddmm
    ├── fibonacci.ddmm
    ├── web_request.ddmm     # Demonstrates pip package imports
    ├── data_processing.ddmm # Demonstrates dict/list heavy code
    └── flask_app.ddmm       # Demonstrates framework usage
```

---

## pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "drakedrakemayemaye"
version = "1.0.0"
description = "A Python interpreter where brackets are replaced with drake/maye syntax 🏈"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
keywords = ["python", "interpreter", "drake", "maye", "transpiler", "meme"]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Topic :: Software Development :: Interpreters",
]

[project.scripts]
drakedrakemayemaye = "drakedrakemayemaye.cli:main"
```

---

## Test Cases (Important!)

### Transpiler tests — these MUST all pass:

```python
# Basic brackets
assert transform("print drake 'hi' maye") == "print ( 'hi' )"
assert transform("d = Drake 'a': 1 Maye") == "d = { 'a': 1 }"
assert transform("x = DRAKE 1, 2, 3 MAYE") == "x = [ 1, 2, 3 ]"

# Mixed nesting
assert transform("x DRAKE Drake 'k': v Maye for k, v in items drake maye MAYE") == \
    "x [ { 'k': v } for k, v in items ( ) ]"

# Strings NOT transformed
assert transform('x = "drake maye"') == 'x = "drake maye"'
assert transform("x = 'Drake Maye'") == "x = 'Drake Maye'"
assert transform('x = """drake DRAKE Drake"""') == 'x = """drake DRAKE Drake"""'

# Comments NOT transformed
assert transform("# drake maye Drake Maye") == "# drake maye Drake Maye"

# f-string expressions ARE transformed
assert transform('f"{x.upper drake maye}"') == 'f"{x.upper ( )}"'
assert transform('f"{d DRAKE key MAYE}"') == 'f"{d [ key ]}"'

# f-string literal text NOT transformed
assert transform('f"drake maye"') == 'f"drake maye"'

# Word boundaries respected
assert transform("drakesmith = 1") == "drakesmith = 1"
assert transform("x_drake = 1") == "x_drake = 1"
assert transform("mayefield = 1") == "mayefield = 1"
assert transform("DRAKES = 1") == "DRAKES = 1"

# Raw strings NOT transformed
assert transform('r"drake maye"') == 'r"drake maye"'

# Real-world: dict comprehension
input_code = "result = Drake k: v for k, v in items drake maye if v > 0 Maye"
expected   = "result = { k: v for k, v in items ( ) if v > 0 }"
assert transform(input_code) == expected

# Real-world: nested data structure
input_code = "data = Drake 'users': DRAKE Drake 'name': 'Alice' Maye, Drake 'name': 'Bob' Maye MAYE Maye"
expected   = "data = { 'users': [ { 'name': 'Alice' }, { 'name': 'Bob' } ] }"
assert transform(input_code) == expected

# Real-world: class definition
input_code = "class Foo drake Bar, metaclass=ABCMeta maye:"
expected   = "class Foo ( Bar, metaclass=ABCMeta ):"
assert transform(input_code) == expected

# Reverse transform
assert reverse_transform("print('hi')") == "print drake 'hi' maye"
assert reverse_transform("d = {'a': 1}") == "d = Drake 'a': 1 Maye"
assert reverse_transform("x = [1, 2]") == "x = DRAKE 1, 2 MAYE"
```

### Integration tests:

```python
# A .ddmm file can import another .ddmm file
# A .ddmm file can import stdlib modules (os, sys, json, etc.)
# A .ddmm file can import pip packages (requests, numpy, etc.)
# CLI: `drakedrakemayemaye -c "print drake 42 maye"` outputs 42
# CLI: `drakedrakemayemaye script.ddmm` runs the script
# CLI: `drakedrakemayemaye -m json.tool` works
# REPL: multi-line input works (def, class, if blocks)
# Error messages: tracebacks reference .ddmm filenames and correct line numbers
```

---

## Error Handling & Developer Experience

### Tracebacks
This is critical for usability. When an error occurs in a `.ddmm` file, the traceback should:
- Show the `.ddmm` filename (not a temp file or `<string>`)
- Show the correct line number from the ORIGINAL `.ddmm` source
- Ideally show the original Drake Maye source line, not the transformed Python

The transformation is line-preserving (it doesn't add or remove lines), so line numbers should map 1:1 naturally. Use the `filename` parameter in `compile()` to set the correct filename.

### Syntax errors
If someone writes mismatched brackets like `drake ... Maye` (paren open, curly close), the resulting Python `( ... }` will produce a `SyntaxError` from Python. Consider wrapping these to give a more helpful Drake Maye-aware error message like:
```
DrakeMayeSyntaxError: Mismatched brackets — opened with 'drake' (paren) but closed with 'Maye' (curly brace) on line 5
```

### Bracket matching helper
Consider a `--check` flag that validates bracket matching in `.ddmm` files before running them.

---

## Example `.ddmm` Files to Include

### `examples/hello_world.ddmm`
```
print drake "Hello, World!" maye
```

### `examples/fibonacci.ddmm`
```
def fib drake n maye:
    if n <= 1:
        return n
    return fib drake n - 1 maye + fib drake n - 2 maye

for i in range drake 10 maye:
    print drake fib drake i maye maye
```

### `examples/data_processing.ddmm`
```
import json

data = Drake
    "team": "Patriots",
    "qb": Drake
        "name": "Drake Maye",
        "number": 10,
        "stats": Drake
            "passing_yards": 2276,
            "touchdowns": 15
        Maye
    Maye,
    "record": DRAKE 4, 13 MAYE
Maye

print drake json.dumps drake data, indent=2 maye maye

# List comprehension with nested dict access
names = DRAKE
    player DRAKE "name" MAYE
    for player in DRAKE
        Drake "name": "Drake Maye" Maye,
        "name": "Rhamondre Stevenson" Maye
    MAYE
MAYE
print drake names maye
```

### `examples/web_request.ddmm`
```
import requests

response = requests.get drake "https://api.github.com" maye
data = response.json drake maye

print drake f"GitHub API status: {response.status_code}" maye
print drake f"Current user URL: {data DRAKE 'current_user_url' MAYE}" maye
```

---

## Implementation Order

1. **`transpiler.py`** — Get the core transform working and passing all tests. This is the foundation.
2. **`cli.py`** — Basic file execution and `-c` flag.
3. **`repl.py`** — Interactive REPL.
4. **`importer.py`** — Import hook for `.ddmm` ↔ `.ddmm` imports.
5. **`pyproject.toml`** + packaging — Make it pip-installable with the CLI command.
6. **Tests** — Comprehensive test suite.
7. **Examples + README** — Documentation and example files.
8. **Polish** — Error messages, `--convert`, `--to-python`, caching.

---

## Final Notes

- The interpreter should work with Python 3.10+ (to support modern match/case, etc.)
- All standard Python functionality must work — decorators, generators, async/await, walrus operator, type hints, everything. The transformation is purely syntactic bracket replacement, so this should be automatic.
- Keep the transformation **line-preserving** — never insert or remove newlines. This keeps line numbers in tracebacks correct.
- The `drakedrakemayemaye` command name is intentionally long and ridiculous. That's the point. But also register a short alias `ddmm` for convenience.
- Have fun with it. The README should include the Drake meme reference and be entertaining. This is a meme language that actually works.
