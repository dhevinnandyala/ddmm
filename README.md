# drakedrakemayemaye

> *"You know what? Forget brackets. We're using Drake Maye now."*

A fully functional Python-compatible interpreter where every bracket is replaced with **Drake Maye syntax**. It's Python. It's ridiculous. It works.

```
print drake "Hello, World!" maye
```

Yes, that prints `Hello, World!`. Yes, it's real. Yes, you can pip install it.

## Bracket Mapping

| Drake Maye | Python | Description |
|---|---|---|
| `drake` | `(` | Open paren |
| `maye` | `)` | Close paren |
| `Drake` | `{` | Open curly brace |
| `Maye` | `}` | Close curly brace |
| `DRAKE` | `[` | Open square bracket |
| `MAYE` | `]` | Close square bracket |

**Case matters.** `drake` is a paren, `Drake` is a curly brace, `DRAKE` is a square bracket.

## Installation

```bash
pip install -e .
```

This gives you two commands:
- `drakedrakemayemaye` - the full, glorious name
- `ddmm` - for when you want to actually type things quickly

## Usage

### Run a file
```bash
drakedrakemayemaye hello.ddmm
ddmm hello.ddmm
```

### Interactive REPL
```bash
ddmm
```

### Inline execution
```bash
ddmm -c "print drake 42 maye"
```

### Run a module
```bash
ddmm -m json.tool <<< '{"key": "value"}'
```

### Convert Python to Drake Maye
```bash
ddmm --convert existing_code.py
```

### Convert Drake Maye to Python
```bash
ddmm --to-python script.ddmm
```

### Validate bracket matching
```bash
ddmm --check script.ddmm
```

### Show transformed Python
```bash
ddmm --show-transform script.ddmm
```

## Examples

### Hello World
```
print drake "Hello, World!" maye
```

### Fibonacci
```
def fib drake n maye:
    if n <= 1:
        return n
    return fib drake n - 1 maye + fib drake n - 2 maye

for i in range drake 10 maye:
    print drake fib drake i maye maye
```

### Data Structures
```
data = Drake
    "team": "Patriots",
    "qb": Drake "name": "Drake Maye", "number": 10 Maye,
    "record": DRAKE 4, 13 MAYE
Maye
```

### Classes
```
class Dog drake Animal maye:
    def __init__ drake self, name maye:
        super drake maye.__init__ drake name, "Woof" maye

    def speak drake self maye:
        return f"{self.name} says {self.sound}!"
```

### F-Strings
```
name = "World"
print drake f"Hello, {name.upper drake maye}!" maye
```

## How It Works

Under the hood, `drakedrakemayemaye` is a **source-to-source transpiler**. It:

1. Reads your `.ddmm` file
2. Transforms Drake Maye syntax to standard Python brackets
3. Hands the result to CPython for execution

The transformation is **token-aware** — it won't touch keywords inside strings or comments. It correctly handles f-strings, raw strings, escape sequences, and all of Python's string prefix combinations.

An import hook lets `.ddmm` files import other `.ddmm` files using standard `import` syntax. Compiled bytecode is cached in `__ddmmcache__/` directories for performance.

## Architecture

```
drakedrakemayemaye/
  transpiler.py  — Character-by-character state machine transformer
  importer.py    — Import hook for .ddmm files (MetaPathFinder + Loader)
  cli.py         — CLI entry point mirroring python's interface
  repl.py        — Interactive REPL with readline support
  compat.py      — Python version helpers
```

## Compatibility

- Python 3.10+
- All Python features work: decorators, generators, async/await, walrus operator, match/case, type hints, everything
- All stdlib modules and pip packages work normally
- Tracebacks show correct `.ddmm` filenames and line numbers

## FAQ

**Q: Why?**
A: Drake Maye.

**Q: No seriously, why?**
A: Because brackets are boring and Drake Maye is not.

**Q: Is this production-ready?**
A: It's as production-ready as your commitment to replacing brackets with quarterback names.

**Q: Does string content get transformed?**
A: No! `"drake maye"` stays as `"drake maye"`. The transpiler is token-aware and respects string boundaries, comments, and f-string expressions.

## License

MIT
