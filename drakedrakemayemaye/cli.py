"""CLI entry point for drakedrakemayemaye.

Mirrors python's CLI interface. Manual arg parsing to support passthrough
of remaining args to scripts (like python does).
"""

from __future__ import annotations

import os
import runpy
import sys

from drakedrakemayemaye.compat import check_python_version
from drakedrakemayemaye.importer import install_hook
from drakedrakemayemaye.transpiler import (
    check_bracket_matching,
    transform,
    reverse_transform,
)

HELP_TEXT = """\
Usage: drakedrakemayemaye [option] ... [-c cmd | -m mod | file | -] [arg] ...

Options:
  -c cmd    : program passed in as string (terminates option list)
  -m mod    : run library module as a script (terminates option list)
  -i        : inspect interactively after running script
  -u        : force unbuffered stdout and stderr
  -E        : ignore environment variables
  -V, --version : print version and exit
  -h, --help    : print this help message and exit

Drake Maye options:
  --show-transform <file.ddmm> : print the transformed Python source
  --convert <file.py>          : convert a .py file to .ddmm (prints to stdout)
  --to-python <file.ddmm>     : convert a .ddmm file to .py (prints to stdout)
  --check <file.ddmm>         : validate bracket matching

Bracket mapping:
  drake / maye  →  ( )   parentheses
  Drake / Maye  →  { }   curly braces
  DRAKE / MAYE  →  [ ]   square brackets
"""


def main(argv=None):
    """Main CLI entry point."""
    check_python_version()

    if argv is None:
        argv = sys.argv[1:]

    inspect_mode = False
    unbuffered = False
    i = 0

    while i < len(argv):
        arg = argv[i]

        if arg in ('-h', '--help'):
            print(HELP_TEXT)
            return 0

        if arg in ('-V', '--version'):
            from drakedrakemayemaye import __version__
            print(f'drakedrakemayemaye {__version__}')
            return 0

        if arg == '-i':
            inspect_mode = True
            i += 1
            continue

        if arg == '-u':
            unbuffered = True
            # Make stdout/stderr unbuffered
            sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
            sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)
            i += 1
            continue

        if arg == '-E':
            # Ignore environment variables — mostly a no-op for us
            i += 1
            continue

        if arg == '-c':
            if i + 1 >= len(argv):
                print('Argument expected for the -c option', file=sys.stderr)
                return 2
            code_str = argv[i + 1]
            remaining = argv[i + 2:]
            return _run_code(code_str, remaining)

        if arg == '-m':
            if i + 1 >= len(argv):
                print('No module name specified', file=sys.stderr)
                return 2
            module_name = argv[i + 1]
            remaining = argv[i + 2:]
            return _run_module(module_name, remaining)

        if arg == '--show-transform':
            if i + 1 >= len(argv):
                print('Expected file argument for --show-transform', file=sys.stderr)
                return 2
            return _show_transform(argv[i + 1])

        if arg == '--convert':
            if i + 1 >= len(argv):
                print('Expected file argument for --convert', file=sys.stderr)
                return 2
            return _convert_py_to_ddmm(argv[i + 1])

        if arg == '--to-python':
            if i + 1 >= len(argv):
                print('Expected file argument for --to-python', file=sys.stderr)
                return 2
            return _convert_ddmm_to_py(argv[i + 1])

        if arg == '--check':
            if i + 1 >= len(argv):
                print('Expected file argument for --check', file=sys.stderr)
                return 2
            return _check_file(argv[i + 1])

        if arg == '-':
            # Read from stdin
            return _run_stdin()

        if arg.startswith('-'):
            print(f'Unknown option: {arg}', file=sys.stderr)
            return 2

        # It's a file path — everything after is script args
        filepath = arg
        remaining = argv[i + 1:]
        result = _run_file(filepath, remaining, inspect_mode=inspect_mode)
        return result

        i += 1

    # No arguments — start REPL
    install_hook()
    from drakedrakemayemaye.repl import start_repl
    start_repl()
    return 0


def _run_code(code_str: str, remaining_args: list[str]) -> int:
    """Run inline code passed via -c."""
    install_hook()
    sys.argv = ['-c'] + remaining_args
    python_code = transform(code_str)
    try:
        exec(compile(python_code, '<string>', 'exec'), {'__name__': '__main__'})
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception:
        import traceback
        traceback.print_exc()
        return 1
    return 0


def _run_module(module_name: str, remaining_args: list[str]) -> int:
    """Run a module via -m."""
    install_hook()
    sys.argv = [module_name] + remaining_args
    try:
        runpy.run_module(module_name, run_name='__main__', alter_sys=True)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception:
        import traceback
        traceback.print_exc()
        return 1
    return 0


def _run_file(filepath: str, remaining_args: list[str], inspect_mode: bool = False) -> int:
    """Run a .ddmm file."""
    install_hook()

    if not os.path.isfile(filepath):
        print(f"drakedrakemayemaye: can't open file '{filepath}': No such file or directory",
              file=sys.stderr)
        return 2

    sys.argv = [filepath] + remaining_args

    # Add the script's directory to sys.path
    script_dir = os.path.dirname(os.path.abspath(filepath))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ddmm_source = f.read()
        python_source = transform(ddmm_source)
        code = compile(python_source, filepath, 'exec')
        globs = {'__name__': '__main__', '__file__': filepath}
        exec(code, globs)
    except SystemExit as e:
        if inspect_mode:
            from drakedrakemayemaye.repl import start_repl
            start_repl(local_vars=globs)
        return e.code if isinstance(e.code, int) else 1
    except Exception:
        import traceback
        traceback.print_exc()
        if inspect_mode:
            from drakedrakemayemaye.repl import start_repl
            start_repl()
        return 1

    if inspect_mode:
        from drakedrakemayemaye.repl import start_repl
        start_repl(local_vars=globs)

    return 0


def _run_stdin() -> int:
    """Run code from stdin."""
    install_hook()
    sys.argv = ['-']
    source = sys.stdin.read()
    python_code = transform(source)
    try:
        exec(compile(python_code, '<stdin>', 'exec'), {'__name__': '__main__'})
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception:
        import traceback
        traceback.print_exc()
        return 1
    return 0


def _show_transform(filepath: str) -> int:
    """Print the transformed Python source of a .ddmm file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except OSError as e:
        print(f'Error reading {filepath}: {e}', file=sys.stderr)
        return 1
    print(transform(source))
    return 0


def _convert_py_to_ddmm(filepath: str) -> int:
    """Convert a .py file to Drake Maye syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except OSError as e:
        print(f'Error reading {filepath}: {e}', file=sys.stderr)
        return 1
    print(reverse_transform(source))
    return 0


def _convert_ddmm_to_py(filepath: str) -> int:
    """Convert a .ddmm file to Python syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except OSError as e:
        print(f'Error reading {filepath}: {e}', file=sys.stderr)
        return 1
    print(transform(source))
    return 0


def _check_file(filepath: str) -> int:
    """Validate bracket matching in a .ddmm file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except OSError as e:
        print(f'Error reading {filepath}: {e}', file=sys.stderr)
        return 1

    errors = check_bracket_matching(source, filename=filepath)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    else:
        print(f'{filepath}: All brackets match!')
        return 0


if __name__ == '__main__':
    sys.exit(main())
