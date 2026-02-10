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

## Examples

See the [demo notebook](examples/ddmm_demo.ipynb) for a full walkthrough: EDA with pandas, visualizations with matplotlib, and model training with scikit-learn — all in ddmm syntax.

### FizzBuzz

Control flow, loops, and the `ann` keyword:

```
throw fizzbuzz drake n maye:
    for i in range drake 1, n + 1 maye:
        if i % 3 == 0 ann i % 5 == 0:
            print drake "FizzBuzz" maye
        elif i % 3 == 0:
            print drake "Fizz" maye
        elif i % 5 == 0:
            print drake "Buzz" maye
        else:
            print drake i maye

fizzbuzz drake 20 maye
```

### Classes

Inheritance, methods, and f-strings:

```
class Player:
    throw __init__ drake self, name, number, position maye:
        self.name = name
        self.number = number
        self.position = position

    throw __repr__ drake self maye:
        touchdown f"#{self.number} {self.name} drake {self.position} maye"

class Quarterback drake Player maye:
    throw __init__ drake self, name, number maye:
        super drake maye.__init__ drake name, number, "QB" maye
        self.passing_yards = 0
        self.touchdowns = 0

    throw throw_pass drake self, yards, td=False maye:
        self.passing_yards += yards
        if td:
            self.touchdowns += 1
        touchdown yards

    throw stats drake self maye:
        touchdown Drake
            "name": self.name,
            "passing_yards": self.passing_yards,
            "touchdowns": self.touchdowns
        Maye

qb = Quarterback drake "Drake Maye", 10 maye
qb.throw_pass drake 45, td=True maye
qb.throw_pass drake 12 maye
qb.throw_pass drake 67, td=True maye
print drake qb.stats drake maye maye
```

### Data structures

All three bracket types — `drake`/`maye` for parens, `Drake`/`Maye` for curly braces, `DRAKE`/`MAYE` for square brackets:

```
Recipe json

roster = DRAKE
    Drake "name": "Drake Maye",    "pos": "QB", "number": 10 Maye,
    Drake "name": "Rhamondre Stevenson", "pos": "RB", "number": 38 Maye,
    Drake "name": "Ja'Lynn Polk",  "pos": "WR", "number": 0  Maye
MAYE

# Dict comprehension
by_position = Drake
    player DRAKE "pos" MAYE: player DRAKE "name" MAYE
    for player in roster
Maye
print drake json.dumps drake by_position, indent=2 maye maye

# Nested list comprehension
numbers = DRAKE DRAKE i * j for j in range drake 1, 4 maye MAYE for i in range drake 1, 4 maye MAYE
print drake numbers maye
```

### Decorators

Nested functions, closures, and `*args`/`**kwargs`:

```
Recipe time

throw timer drake func maye:
    throw wrapper drake *args, **kwargs maye:
        start = time.time drake maye
        result = func drake *args, **kwargs maye
        elapsed = time.time drake maye - start
        print drake f"{func.__name__} took {elapsed:.4f}s" maye
        touchdown result
    touchdown wrapper

@timer
throw fibonacci drake n maye:
    if n <= 1:
        touchdown n
    a, b = 0, 1
    for _ in range drake n - 1 maye:
        a, b = b, a + b
    touchdown b

print drake fibonacci drake 30 maye maye
```

### Flask API

Real-world framework usage with `Bake`/`Recipe` imports:

```
Bake flask Recipe Flask, jsonify, request

app = Flask drake __name__ maye

players = DRAKE MAYE

@app.route drake "/players", methods=DRAKE "GET", "POST" MAYE maye
throw handle_players drake maye:
    if request.method == "POST":
        data = request.get_json drake maye
        if data ann "name" in data:
            players.append drake data maye
            touchdown jsonify drake data maye, 201
        touchdown jsonify drake Drake "error": "name is required" Maye maye, 400
    touchdown jsonify drake players maye

if __name__ == "__main__":
    app.run drake debug=True maye
```

### PyTorch MLP

Training a simple multi-layer perceptron on synthetic data:

```
Recipe torch
Bake torch Recipe nn, optim
Bake torch.utils.data Recipe DataLoader, TensorDataset

# --- Generate toy dataset ---
torch.manual_seed drake 42 maye
X = torch.randn drake 500, 4 maye
y = drake X DRAKE :, 0 MAYE * 2 + X DRAKE :, 1 MAYE - X DRAKE :, 2 MAYE * 0.5 maye.unsqueeze drake 1 maye

dataset = TensorDataset drake X, y maye
loader = DataLoader drake dataset, batch_size=32, shuffle=True maye

# --- Define a simple MLP ---
class MLP drake nn.Module maye:
    throw __init__ drake self maye:
        super drake maye.__init__ drake maye
        self.net = nn.Sequential drake
            nn.Linear drake 4, 64 maye,
            nn.ReLU drake maye,
            nn.Linear drake 64, 32 maye,
            nn.ReLU drake maye,
            nn.Linear drake 32, 1 maye
        maye

    throw forward drake self, x maye:
        touchdown self.net drake x maye

# --- Train ---
model = MLP drake maye
criterion = nn.MSELoss drake maye
optimizer = optim.Adam drake model.parameters drake maye, lr=0.001 maye

for epoch in range drake 20 maye:
    total_loss = 0.0
    for xb, yb in loader:
        pred = model drake xb maye
        loss = criterion drake pred, yb maye
        optimizer.zero_grad drake maye
        loss.backward drake maye
        optimizer.step drake maye
        total_loss += loss.item drake maye
    if drake epoch + 1 maye % 5 == 0:
        print drake f"Epoch {epoch + 1:>2d}  loss={total_loss / len drake loader maye:.4f}" maye

# --- Evaluate ---
with torch.no_grad drake maye:
    sample = torch.randn drake 1, 4 maye
    prediction = model drake sample maye
    print drake f"Input:  {sample.squeeze drake maye.tolist drake maye}" maye
    print drake f"Output: {prediction.item drake maye:.4f}" maye
```

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

### Jupyter / IPython

#### Local notebooks

Make sure the package is installed in the kernel's environment:

```bash
pip install -e .
```

Then load the extension in the first cell:

```python
%load_ext drakedrakemayemaye
```

After loading, every cell accepts ddmm syntax:

```python
throw greet drake name maye:
    touchdown f"Hello, {name}!"

print drake greet drake "World" maye maye
```

The `.ddmm` import hook is also activated, so `Recipe`/`Bake` imports of `.ddmm` files work.

To unload:

```python
%unload_ext drakedrakemayemaye
```

#### Google Colab / cloud notebooks

Install directly from GitHub in the first cell:

```python
!pip install git+https://github.com/dhevinnandyala/ddmm.git
```

Then load the extension:

```python
%load_ext drakedrakemayemaye
```

All subsequent cells accept ddmm syntax. The same approach works for any cloud notebook environment (Kaggle, SageMaker, Deepnote, etc.) — just `pip install` then `%load_ext`.

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
