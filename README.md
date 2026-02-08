# drakedrakemayemaye

A Python-compatible interpreter that replaces brackets and select keywords with Drake Maye-themed syntax. Files use the `.ddmm` extension. Under the hood it is a source-to-source transpiler that converts `.ddmm` to valid Python, then runs it via CPython.

```
Recipe json

throw greet drake name maye:
    touchdown f"Hello, {name}!"

print drake greet drake "World" maye maye
```

## Syntax Mapping

### Brackets

| ddmm | Python | Description |
|---|---|---|
| `drake` | `(` | Open paren |
| `maye` | `)` | Close paren |
| `Drake` | `{` | Open curly brace |
| `Maye` | `}` | Close curly brace |
| `DRAKE` | `[` | Open square bracket |
| `MAYE` | `]` | Close square bracket |

Case is significant. `drake` maps to `(`, `Drake` to `{`, `DRAKE` to `[`.

### Keywords

| ddmm | Python | Reference |
|---|---|---|
| `Recipe` | `import` | Ann's baking hobby |
| `Bake` | `from` | Ann's baking hobby |
| `throw` | `def` | Football |
| `touchdown` | `return` | Football |
| `ann` | `and` | Drake's wife |

All other Python syntax is unchanged.

## Installation

Requires Python 3.10+.

```bash
pip install -e .
```

This installs two CLI commands: `drakedrakemayemaye` and `ddmm` (short alias).

## Usage

### Run a file

```bash
ddmm script.ddmm
ddmm script.ddmm --flag value   # args passed through to sys.argv
```

### Interactive REPL

```bash
ddmm
```

Launches a REPL with readline history and tab completion. Prompts are `ddmm>>> ` and `ddmm... ` for continuation lines.

### Inline execution

```bash
ddmm -c "print drake 42 maye"
```

### Run a module

```bash
ddmm -m json.tool <<< '{"key": "value"}'
```

### Convert between formats

```bash
ddmm --convert file.py          # Python -> ddmm (stdout)
ddmm --to-python file.ddmm      # ddmm -> Python (stdout)
ddmm --show-transform file.ddmm # same as --to-python
```

### Validate bracket matching

```bash
ddmm --check file.ddmm
```

Reports mismatched or unclosed bracket keywords with line numbers.

### Other flags

| Flag | Description |
|---|---|
| `-V`, `--version` | Print version |
| `-h`, `--help` | Print help |
| `-i` | Enter REPL after running a script |
| `-u` | Unbuffered stdout/stderr |
| `-E` | Ignore environment variables |

## Imports

`.ddmm` files can import other `.ddmm` files, stdlib modules, and pip packages using standard import syntax (with `Recipe`/`Bake` keywords):

```
Recipe os
Bake pathlib Recipe Path
Recipe json
```

The import hook searches `sys.path` for `.ddmm` files and `__init__.ddmm` packages. Compiled bytecode is cached in `__ddmmcache__/` directories with mtime-based invalidation.

## How it works

The transpiler is a character-by-character state machine that:

1. Replaces ddmm keywords with their Python equivalents
2. Preserves string contents (regular, raw, byte, triple-quoted)
3. Preserves comments
4. Transforms keywords inside f-string expressions but not f-string literal text
5. Respects word boundaries (`drakesmith`, `throwback`, `announce` are not touched)

The transformation is line-preserving, so tracebacks show correct `.ddmm` filenames and line numbers.

## Compatibility

- Python 3.10+
- All Python features work (decorators, generators, async/await, walrus operator, match/case, type hints, etc.)
- All stdlib modules and pip packages work normally

## License

MIT
