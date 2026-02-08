"""Interactive REPL for drakedrakemayemaye."""

from __future__ import annotations

import code
import codeop
import os
import sys
import traceback

from drakedrakemayemaye.transpiler import transform

BANNER = r"""
     _     _
  __| | __| |_ __ ___  _ __ ___
 / _` |/ _` | '_ ` _ \| '_ ` _ \
| (_| | (_| | | | | | | | | | | |
 \__,_|\__,_|_| |_| |_|_| |_| |_|

  drakedrakemayemaye v{version} — Python {pyver}
  Where every bracket tells a story.

  Bracket Reference:
    drake / maye   →  ( )   parentheses
    Drake / Maye   →  {{ }}   curly braces
    DRAKE / MAYE   →  [ ]   square brackets

  Keyword Reference:
    Recipe         →  import
    Bake           →  from
    throw          →  def
    touchdown      →  return
    ann            →  and

  Type 'exit drake maye' or Ctrl-D to quit.
"""

PS1 = 'ddmm>>> '
PS2 = 'ddmm... '


class DdmmConsole(code.InteractiveConsole):
    """Interactive console that transforms Drake Maye syntax before execution."""

    def __init__(self, locals=None):
        super().__init__(locals=locals)
        self._compiler = codeop.CommandCompiler()
        self._buffer: list[str] = []

    def runsource(self, source, filename='<ddmm-repl>', symbol='single'):
        """Transform the source, then compile and run."""
        try:
            python_source = transform(source)
        except Exception as e:
            self.showsyntaxerror(filename)
            return False

        try:
            code_obj = self._compiler(python_source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            self.showsyntaxerror(filename)
            return False

        if code_obj is None:
            # Incomplete input — need more lines
            return True

        self.runcode(code_obj)
        return False

    def interact(self, banner=None, exitmsg=None):
        """Run the REPL loop with custom prompts."""
        from drakedrakemayemaye import __version__

        if banner is None:
            banner = BANNER.format(
                version=__version__,
                pyver=f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
            )

        # Set up readline if available
        _setup_readline()

        cprt = f'Type "help", "copyright", "credits" or "license" for more information.'
        sys.stdout.write(banner + '\n' + cprt + '\n')

        more = False
        while True:
            try:
                if more:
                    prompt = PS2
                else:
                    prompt = PS1
                try:
                    line = input(prompt)
                except EOFError:
                    sys.stdout.write('\n')
                    break

                if more:
                    self._buffer.append(line)
                else:
                    self._buffer = [line]

                source = '\n'.join(self._buffer) + '\n'
                more = self.runsource(source)

            except KeyboardInterrupt:
                sys.stdout.write('\nKeyboardInterrupt\n')
                self._buffer = []
                more = False

        if exitmsg is None:
            exitmsg = 'Goodbye!'
        sys.stdout.write(exitmsg + '\n')


def _setup_readline():
    """Set up readline for history and tab completion if available."""
    try:
        import readline
    except ImportError:
        return

    histfile = os.path.expanduser('~/.ddmm_history')
    try:
        readline.read_history_file(histfile)
    except (FileNotFoundError, OSError):
        pass

    import atexit
    atexit.register(_save_history, histfile)

    # Basic tab completion
    try:
        import rlcompleter
        readline.set_completer(rlcompleter.Completer(namespace=None).complete)
        if sys.platform == 'darwin':
            readline.parse_and_bind('bind ^I rl_complete')
        else:
            readline.parse_and_bind('tab: complete')
    except Exception:
        pass


def _save_history(histfile):
    """Save readline history."""
    try:
        import readline
        readline.set_history_length(10000)
        readline.write_history_file(histfile)
    except (ImportError, OSError):
        pass


def start_repl(local_vars=None):
    """Start the interactive REPL."""
    console = DdmmConsole(locals=local_vars)
    console.interact()
