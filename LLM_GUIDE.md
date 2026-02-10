# ddmm Language Guide for LLM Agents

This guide is for AI assistants and LLM agents that need to read, write, or debug ddmm code. ddmm is a source-to-source transformation layer on top of Python — all Python semantics apply, only the syntax for brackets and a few keywords differs.

## Quick Reference

### Bracket replacements

| ddmm    | Python | Use for                              |
|---------|--------|--------------------------------------|
| `drake` | `(`    | Function calls, tuples, grouping     |
| `maye`  | `)`    | Close parenthesis                    |
| `Drake` | `{`    | Dicts, sets, f-string expressions    |
| `Maye`  | `}`    | Close curly brace                    |
| `DRAKE` | `[`    | Lists, indexing, slicing             |
| `MAYE`  | `]`    | Close square bracket                 |

**Case is significant.** `drake` ≠ `Drake` ≠ `DRAKE`.

### Keyword replacements

| ddmm        | Python   |
|-------------|----------|
| `Recipe`    | `import` |
| `Bake`      | `from`   |
| `throw`     | `def`    |
| `touchdown` | `return` |
| `ann`       | `and`    |

All other Python keywords (`if`, `else`, `for`, `while`, `class`, `in`, `not`, `or`, `is`, `with`, `as`, `try`, `except`, `raise`, `yield`, `async`, `await`, `lambda`, `pass`, `break`, `continue`, `True`, `False`, `None`, etc.) are **unchanged**.

## Rules

1. **Word boundaries only.** Replacements happen only when the keyword stands alone. `drakesmith`, `throwback`, `announce`, `Recipes`, `touchdown_pass` are NOT transformed — they remain as-is because the keyword is part of a larger identifier.

2. **Strings are preserved.** Content inside string literals (`"drake"`, `'maye'`, `"""Drake"""`, `r"DRAKE"`, `b"maye"`) is never transformed.

3. **Comments are preserved.** Anything after `#` on a line is never transformed.

4. **f-string expressions ARE transformed.** Inside `{}` within an f-string, ddmm keywords are replaced. The literal text portions of f-strings are not. Example: `f"hello {name.upper drake maye}"` → `f"hello {name.upper()}"`.

5. **Line-preserving.** The transformation never adds or removes lines. Line numbers in tracebacks map 1:1 to the `.ddmm` source.

## How to Write ddmm Code

Take any valid Python and apply these mental substitutions:

### Function calls and definitions

```python
# Python
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
```

```
# ddmm
throw greet drake name maye:
    touchdown f"Hello, {name}!"

print drake greet drake "World" maye maye
```

Note the nested `drake`/`maye` pairs: `print drake ... maye` wraps the outer call, `greet drake "World" maye` wraps the inner call.

### Imports

```python
# Python
import json
from os.path import join
from flask import Flask, jsonify
```

```
# ddmm
Recipe json
Bake os.path Recipe join
Bake flask Recipe Flask, jsonify
```

### Lists (square brackets)

```python
# Python
numbers = [1, 2, 3]
first = numbers[0]
sliced = numbers[1:3]
matrix = [[i * j for j in range(3)] for i in range(3)]
```

```
# ddmm
numbers = DRAKE 1, 2, 3 MAYE
first = numbers DRAKE 0 MAYE
sliced = numbers DRAKE 1:3 MAYE
matrix = DRAKE DRAKE i * j for j in range drake 3 maye MAYE for i in range drake 3 maye MAYE
```

### Dicts (curly braces)

```python
# Python
data = {"name": "Drake Maye", "number": 10}
comp = {k: v for k, v in items()}
```

```
# ddmm
data = Drake "name": "Drake Maye", "number": 10 Maye
comp = Drake k: v for k, v in items drake maye Maye
```

### Classes

```python
# Python
class Quarterback(Player):
    def __init__(self, name):
        super().__init__(name, "QB")

    def stats(self):
        return {"name": self.name}
```

```
# ddmm
class Quarterback drake Player maye:
    throw __init__ drake self, name maye:
        super drake maye.__init__ drake name, "QB" maye

    throw stats drake self maye:
        touchdown Drake "name": self.name Maye
```

### Boolean logic with `ann`

```python
# Python
if x > 0 and y > 0:
    print("both positive")
```

```
# ddmm
if x > 0 ann y > 0:
    print drake "both positive" maye
```

`or`, `not`, and `is` remain unchanged.

### Mixed bracket nesting

When brackets of different types nest, match each type independently:

```
# ddmm — a list of dicts accessed by index
players = DRAKE Drake "name": "Maye" Maye, Drake "name": "Polk" Maye MAYE
first_name = players DRAKE 0 MAYE DRAKE "name" MAYE
```

Translates to:
```python
players = [{"name": "Maye"}, {"name": "Polk"}]
first_name = players[0]["name"]
```

### Decorators, lambdas, and advanced patterns

```
# Decorator with arguments
@app.route drake "/api", methods=DRAKE "GET" MAYE maye
throw handler drake maye:
    touchdown jsonify drake Drake "status": "ok" Maye maye

# Lambda
square = lambda x: x ** 2
doubles = list drake map drake lambda x: x * 2, DRAKE 1, 2, 3 MAYE maye maye

# Context manager
with open drake "file.txt" maye as f:
    content = f.read drake maye

# Exception handling (try/except/raise are unchanged)
try:
    result = risky_call drake maye
except ValueError as e:
    print drake f"Error: {e}" maye
```

## Common Patterns to Watch For

### Consecutive `maye` tokens

Nested function calls produce chains of closing `maye`:

```
print drake len drake items maye maye
```

This is `print(len(items))`. Count the nesting depth — each `drake` needs a matching `maye`.

### `drake maye` with nothing between them

Empty parentheses are `drake maye`:

```
x = MyClass drake maye          # MyClass()
items = list drake maye          # list()
super drake maye.__init__ drake maye  # super().__init__()
```

### Method chaining

```
text.strip drake maye.lower drake maye.split drake "," maye
```

This is `text.strip().lower().split(",")`.

### Tuple vs. grouping

Same as Python — a single item in `drake`/`maye` is grouping, add a trailing comma for a single-element tuple:

```
group = drake x + y maye         # (x + y) — grouping
single = drake x, maye           # (x,) — single-element tuple
multi = drake x, y, z maye       # (x, y, z) — tuple
```

## Running ddmm Code

```bash
ddmm script.ddmm                    # Run a file
ddmm -c "print drake 42 maye"       # Inline execution
ddmm                                 # Interactive REPL
ddmm --to-python file.ddmm          # Show transformed Python
ddmm --convert file.py              # Convert Python to ddmm
ddmm --check file.ddmm              # Validate bracket matching
```

### In Jupyter notebooks

```python
%load_ext drakedrakemayemaye
# All subsequent cells accept ddmm syntax
```

## Converting Between Python and ddmm

When asked to convert Python to ddmm:
1. Replace `(` with ` drake ` and `)` with ` maye `
2. Replace `{` with ` Drake ` and `}` with ` Maye `
3. Replace `[` with ` DRAKE ` and `]` with ` MAYE `
4. Replace `import` with `Recipe` and `from` with `Bake`
5. Replace `def` with `throw` and `return` with `touchdown`
6. Replace standalone `and` with `ann`
7. Do NOT replace any of the above inside strings or comments
8. Clean up extra whitespace around brackets if desired

When asked to convert ddmm to Python, reverse the above.

## Debugging Tips

- If you see a `SyntaxError`, check for mismatched bracket types (e.g., opening with `drake` but closing with `Maye`).
- Use `ddmm --check file.ddmm` to find mismatched brackets.
- Use `ddmm --to-python file.ddmm` to see the generated Python — this is useful for verifying correctness.
- Tracebacks show `.ddmm` filenames and correct line numbers.
