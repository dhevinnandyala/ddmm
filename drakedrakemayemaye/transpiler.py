"""
Core source-to-source transpiler for drakedrakemayemaye.

Converts .ddmm source (Drake Maye bracket syntax) to valid Python and back.
Uses a character-by-character state machine with a stack of parsing contexts.
"""

from __future__ import annotations

# Keyword-to-bracket mapping
KEYWORD_TO_BRACKET = {
    'drake': '(',
    'maye': ')',
    'Drake': '{',
    'Maye': '}',
    'DRAKE': '[',
    'MAYE': ']',
}

BRACKET_TO_KEYWORD = {v: k for k, v in KEYWORD_TO_BRACKET.items()}

# String prefixes (case-insensitive combos)
_STRING_PREFIX_CHARS = set('fFrRbBuU')


def _is_identifier_char(ch: str) -> bool:
    """Check if a character can be part of a Python identifier."""
    return ch.isalnum() or ch == '_'


def _match_keyword(source: str, pos: int) -> str | None:
    """Try to match a drake/maye keyword at position pos with word boundary checks."""
    for kw in ('drake', 'Drake', 'DRAKE', 'maye', 'Maye', 'MAYE'):
        end = pos + len(kw)
        if end > len(source):
            continue
        if source[pos:end] == kw:
            # Check word boundaries
            if pos > 0 and _is_identifier_char(source[pos - 1]):
                continue
            if end < len(source) and _is_identifier_char(source[end]):
                continue
            return kw
    return None


def _detect_string_prefix(source: str, pos: int) -> tuple[str, bool, bool, bool]:
    """Detect string prefix at pos. Returns (prefix, is_fstring, is_raw, is_bytes)."""
    prefix = ''
    i = pos
    while i < len(source) and source[i] in _STRING_PREFIX_CHARS:
        prefix += source[i]
        i += 1
    lower = prefix.lower()
    is_fstring = 'f' in lower
    is_raw = 'r' in lower
    is_bytes = 'b' in lower
    return prefix, is_fstring, is_raw, is_bytes


def transform(source: str) -> str:
    """Transform Drake Maye source (.ddmm) to valid Python source.

    This is a character-by-character state machine that:
    - Replaces standalone drake/maye keywords with brackets
    - Preserves string contents (except f-string expressions)
    - Preserves comments
    - Respects word boundaries
    """
    result = []
    i = 0
    n = len(source)

    # Stack of parsing contexts
    # Each frame: {'kind': str, 'quote_char': str, 'triple': bool,
    #              'is_raw': bool, 'is_fstring': bool, 'brace_depth': int}
    stack = [{'kind': 'code'}]

    while i < n:
        frame = stack[-1]
        kind = frame['kind']

        if kind == 'comment':
            # In a comment: copy until newline
            ch = source[i]
            result.append(ch)
            i += 1
            if ch == '\n':
                stack.pop()
            continue

        if kind in ('string', 'fstring_literal'):
            quote_char = frame['quote_char']
            triple = frame['triple']
            is_raw = frame['is_raw']
            is_fstring = frame['is_fstring']

            ch = source[i]

            # Check for end of string
            if triple:
                tq = quote_char * 3
                if source[i:i + 3] == tq:
                    result.append(tq)
                    i += 3
                    stack.pop()
                    continue
            else:
                if ch == quote_char and (i == 0 or source[i - 1] != '\\' or is_raw):
                    # For non-raw strings, check if backslash is escaped
                    if not is_raw and i > 0:
                        # Count consecutive backslashes before this quote
                        num_bs = 0
                        j = i - 1
                        while j >= 0 and source[j] == '\\':
                            num_bs += 1
                            j -= 1
                        if num_bs % 2 == 1:
                            # Odd backslashes = escaped quote, not end
                            result.append(ch)
                            i += 1
                            continue
                    result.append(ch)
                    i += 1
                    stack.pop()
                    continue

            # Check for f-string expression start
            if is_fstring and ch == '{':
                if i + 1 < n and source[i + 1] == '{':
                    # Escaped brace {{ in f-string
                    result.append('{{')
                    i += 2
                    continue
                # Enter f-string expression
                result.append('{')
                i += 1
                stack.append({'kind': 'fstring_expr', 'brace_depth': 1,
                              'fstring_quote': quote_char, 'fstring_triple': triple})
                continue

            if is_fstring and ch == '}':
                if i + 1 < n and source[i + 1] == '}':
                    # Escaped brace }} in f-string
                    result.append('}}')
                    i += 2
                    continue

            # Handle escape sequences in non-raw strings
            if not is_raw and ch == '\\' and i + 1 < n:
                result.append(ch)
                result.append(source[i + 1])
                i += 2
                continue

            # Regular character in string literal
            result.append(ch)
            i += 1
            continue

        if kind in ('code', 'fstring_expr'):
            ch = source[i]

            # Check for comment (only in code mode, not fstring_expr)
            if kind == 'code' and ch == '#':
                result.append(ch)
                i += 1
                stack.append({'kind': 'comment'})
                continue

            # Check for string start
            if ch in ('"', "'") or (ch in _STRING_PREFIX_CHARS and i + 1 < n):
                prefix, is_fstring, is_raw, is_bytes = _detect_string_prefix(source, i)
                prefix_end = i + len(prefix)
                if prefix_end < n and source[prefix_end] in ('"', "'"):
                    qchar = source[prefix_end]
                    # Check for triple quote
                    if prefix_end + 2 < n and source[prefix_end:prefix_end + 3] == qchar * 3:
                        result.append(prefix + qchar * 3)
                        i = prefix_end + 3
                        frame_kind = 'fstring_literal' if is_fstring else 'string'
                        stack.append({'kind': frame_kind, 'quote_char': qchar,
                                      'triple': True, 'is_raw': is_raw, 'is_fstring': is_fstring})
                        continue
                    else:
                        result.append(prefix + qchar)
                        i = prefix_end + 1
                        frame_kind = 'fstring_literal' if is_fstring else 'string'
                        stack.append({'kind': frame_kind, 'quote_char': qchar,
                                      'triple': False, 'is_raw': is_raw, 'is_fstring': is_fstring})
                        continue
                elif len(prefix) == 0 and ch in ('"', "'"):
                    # No prefix, just a bare quote
                    qchar = ch
                    if i + 2 < n and source[i:i + 3] == qchar * 3:
                        result.append(qchar * 3)
                        i += 3
                        stack.append({'kind': 'string', 'quote_char': qchar,
                                      'triple': True, 'is_raw': False, 'is_fstring': False})
                        continue
                    else:
                        result.append(qchar)
                        i += 1
                        stack.append({'kind': 'string', 'quote_char': qchar,
                                      'triple': False, 'is_raw': False, 'is_fstring': False})
                        continue

            # In fstring_expr, track braces for nesting
            if kind == 'fstring_expr':
                if ch == '{':
                    frame['brace_depth'] += 1
                    result.append(ch)
                    i += 1
                    continue
                if ch == '}':
                    frame['brace_depth'] -= 1
                    if frame['brace_depth'] == 0:
                        # End of f-string expression, back to f-string literal
                        result.append('}')
                        i += 1
                        stack.pop()
                        continue
                    result.append(ch)
                    i += 1
                    continue

            # Try to match drake/maye keywords
            kw = _match_keyword(source, i)
            if kw is not None:
                bracket = KEYWORD_TO_BRACKET[kw]
                # Add space before bracket if previous char is identifier char
                if result and _is_identifier_char(result[-1]):
                    result.append(' ')
                result.append(bracket)
                i += len(kw)
                # Add space after bracket if next char is identifier char or quote
                if i < n and (_is_identifier_char(source[i]) or source[i] in ('"', "'")):
                    result.append(' ')
                continue

            # Regular character
            result.append(ch)
            i += 1
            continue

    return ''.join(result)


def _match_bracket(source: str, pos: int) -> str | None:
    """Try to match a bracket character at position pos."""
    ch = source[pos]
    if ch in BRACKET_TO_KEYWORD:
        return ch
    return None


def reverse_transform(source: str) -> str:
    """Transform valid Python source to Drake Maye source (.ddmm).

    Same state machine as transform() but brackets -> keywords.
    Injects spaces around keywords when adjacent to identifier chars or quotes.
    """
    result = []
    i = 0
    n = len(source)

    stack = [{'kind': 'code'}]

    while i < n:
        frame = stack[-1]
        kind = frame['kind']

        if kind == 'comment':
            ch = source[i]
            result.append(ch)
            i += 1
            if ch == '\n':
                stack.pop()
            continue

        if kind in ('string', 'fstring_literal'):
            quote_char = frame['quote_char']
            triple = frame['triple']
            is_raw = frame['is_raw']
            is_fstring = frame['is_fstring']

            ch = source[i]

            # Check for end of string
            if triple:
                tq = quote_char * 3
                if source[i:i + 3] == tq:
                    result.append(tq)
                    i += 3
                    stack.pop()
                    continue
            else:
                if ch == quote_char:
                    if not is_raw:
                        num_bs = 0
                        j = i - 1
                        while j >= 0 and source[j] == '\\':
                            num_bs += 1
                            j -= 1
                        if num_bs % 2 == 1:
                            result.append(ch)
                            i += 1
                            continue
                    result.append(ch)
                    i += 1
                    stack.pop()
                    continue

            # f-string expression start
            if is_fstring and ch == '{':
                if i + 1 < n and source[i + 1] == '{':
                    result.append('{{')
                    i += 2
                    continue
                result.append('{')
                i += 1
                stack.append({'kind': 'fstring_expr', 'brace_depth': 1,
                              'fstring_quote': quote_char, 'fstring_triple': triple})
                continue

            if is_fstring and ch == '}':
                if i + 1 < n and source[i + 1] == '}':
                    result.append('}}')
                    i += 2
                    continue

            # Escape sequences
            if not is_raw and ch == '\\' and i + 1 < n:
                result.append(ch)
                result.append(source[i + 1])
                i += 2
                continue

            result.append(ch)
            i += 1
            continue

        if kind in ('code', 'fstring_expr'):
            ch = source[i]

            # Comments
            if kind == 'code' and ch == '#':
                result.append(ch)
                i += 1
                stack.append({'kind': 'comment'})
                continue

            # String start detection
            if ch in ('"', "'") or (ch in _STRING_PREFIX_CHARS and i + 1 < n):
                prefix, is_fstring, is_raw, is_bytes = _detect_string_prefix(source, i)
                prefix_end = i + len(prefix)
                if prefix_end < n and source[prefix_end] in ('"', "'"):
                    qchar = source[prefix_end]
                    if prefix_end + 2 < n and source[prefix_end:prefix_end + 3] == qchar * 3:
                        result.append(prefix + qchar * 3)
                        i = prefix_end + 3
                        frame_kind = 'fstring_literal' if is_fstring else 'string'
                        stack.append({'kind': frame_kind, 'quote_char': qchar,
                                      'triple': True, 'is_raw': is_raw, 'is_fstring': is_fstring})
                        continue
                    else:
                        result.append(prefix + qchar)
                        i = prefix_end + 1
                        frame_kind = 'fstring_literal' if is_fstring else 'string'
                        stack.append({'kind': frame_kind, 'quote_char': qchar,
                                      'triple': False, 'is_raw': is_raw, 'is_fstring': is_fstring})
                        continue
                elif len(prefix) == 0 and ch in ('"', "'"):
                    qchar = ch
                    if i + 2 < n and source[i:i + 3] == qchar * 3:
                        result.append(qchar * 3)
                        i += 3
                        stack.append({'kind': 'string', 'quote_char': qchar,
                                      'triple': True, 'is_raw': False, 'is_fstring': False})
                        continue
                    else:
                        result.append(qchar)
                        i += 1
                        stack.append({'kind': 'string', 'quote_char': qchar,
                                      'triple': False, 'is_raw': False, 'is_fstring': False})
                        continue

            # In fstring_expr, track braces
            if kind == 'fstring_expr':
                if ch in ('{', '(', '['):
                    # For actual braces in fstring expressions that are NOT bracket replacements
                    if ch == '{':
                        frame['brace_depth'] += 1
                elif ch == '}':
                    frame['brace_depth'] -= 1
                    if frame['brace_depth'] == 0:
                        result.append('}')
                        i += 1
                        stack.pop()
                        continue

            # Try to match brackets -> keywords
            if ch in BRACKET_TO_KEYWORD:
                keyword = BRACKET_TO_KEYWORD[ch]
                # Handle fstring_expr brace tracking for { and }
                if kind == 'fstring_expr' and ch in ('{', '}'):
                    # { already incremented brace_depth above, } already handled above
                    # For { in fstring_expr (like dict literal inside f-string), use Drake/Maye
                    pass

                # Need space before keyword if previous char is identifier char or closing quote
                if result and (result[-1] == '_' or (result[-1] and _is_identifier_char(result[-1]))):
                    result.append(' ')
                elif result and result[-1] in ('"', "'"):
                    result.append(' ')
                result.append(keyword)
                i += 1
                # Need space after keyword if next char is identifier char, quote, or another bracket keyword
                if i < n and (_is_identifier_char(source[i]) or source[i] in ('"', "'", '(', ')', '{', '}', '[', ']')):
                    result.append(' ')
                continue

            result.append(ch)
            i += 1
            continue

    return ''.join(result)


class DdmmSyntaxError(SyntaxError):
    """Syntax error with Drake Maye-aware error messages."""

    def __init__(self, msg: str, filename: str | None = None,
                 lineno: int | None = None, offset: int | None = None,
                 text: str | None = None):
        super().__init__(msg, (filename, lineno, offset, text))
        self.msg = msg
        self.filename = filename
        self.lineno = lineno
        self.offset = offset
        self.text = text

    def __str__(self) -> str:
        parts = [self.msg]
        if self.filename and self.lineno:
            parts.append(f'  File "{self.filename}", line {self.lineno}')
        if self.text:
            parts.append(f'    {self.text}')
        return '\n'.join(parts)


_BRACKET_NAMES = {
    'drake': 'paren', 'maye': 'paren',
    'Drake': 'curly brace', 'Maye': 'curly brace',
    'DRAKE': 'square bracket', 'MAYE': 'square bracket',
}

_OPENERS = {'drake', 'Drake', 'DRAKE'}
_CLOSERS = {'maye': 'drake', 'Maye': 'Drake', 'MAYE': 'DRAKE'}


def check_bracket_matching(source: str, filename: str = '<string>') -> list[DdmmSyntaxError]:
    """Validate bracket matching in .ddmm source.

    Returns a list of DdmmSyntaxError for each mismatch found.
    """
    errors = []
    stack_brackets: list[tuple[str, int]] = []  # (keyword, line_number)
    i = 0
    n = len(source)
    line = 1
    in_string = False
    in_comment = False
    quote_char = ''
    triple = False
    is_raw = False

    # Simplified state machine just for bracket matching
    parse_stack = [{'kind': 'code'}]

    while i < n:
        frame = parse_stack[-1]
        fkind = frame['kind']

        if source[i] == '\n':
            line += 1
            if fkind == 'comment':
                parse_stack.pop()
            result_char = source[i]
            i += 1
            continue

        if fkind == 'comment':
            i += 1
            continue

        if fkind in ('string', 'fstring_literal'):
            qc = frame['quote_char']
            tr = frame['triple']
            raw = frame['is_raw']
            fs = frame['is_fstring']

            if tr:
                tq = qc * 3
                if source[i:i + 3] == tq:
                    i += 3
                    parse_stack.pop()
                    continue
            else:
                if source[i] == qc:
                    if not raw:
                        num_bs = 0
                        j = i - 1
                        while j >= 0 and source[j] == '\\':
                            num_bs += 1
                            j -= 1
                        if num_bs % 2 == 1:
                            i += 1
                            continue
                    i += 1
                    parse_stack.pop()
                    continue

            if fs and source[i] == '{':
                if i + 1 < n and source[i + 1] == '{':
                    i += 2
                    continue
                i += 1
                parse_stack.append({'kind': 'fstring_expr', 'brace_depth': 1})
                continue

            if not raw and source[i] == '\\' and i + 1 < n:
                i += 2
                continue

            i += 1
            continue

        if fkind in ('code', 'fstring_expr'):
            ch = source[i]

            if fkind == 'code' and ch == '#':
                i += 1
                parse_stack.append({'kind': 'comment'})
                continue

            # String detection
            if ch in ('"', "'") or (ch in _STRING_PREFIX_CHARS and i + 1 < n):
                prefix, fs, raw, _ = _detect_string_prefix(source, i)
                pe = i + len(prefix)
                if pe < n and source[pe] in ('"', "'"):
                    qc = source[pe]
                    if pe + 2 < n and source[pe:pe + 3] == qc * 3:
                        i = pe + 3
                        fk = 'fstring_literal' if fs else 'string'
                        parse_stack.append({'kind': fk, 'quote_char': qc,
                                            'triple': True, 'is_raw': raw, 'is_fstring': fs})
                        continue
                    else:
                        i = pe + 1
                        fk = 'fstring_literal' if fs else 'string'
                        parse_stack.append({'kind': fk, 'quote_char': qc,
                                            'triple': False, 'is_raw': raw, 'is_fstring': fs})
                        continue
                elif len(prefix) == 0 and ch in ('"', "'"):
                    qc = ch
                    if i + 2 < n and source[i:i + 3] == qc * 3:
                        i += 3
                        parse_stack.append({'kind': 'string', 'quote_char': qc,
                                            'triple': True, 'is_raw': False, 'is_fstring': False})
                        continue
                    else:
                        i += 1
                        parse_stack.append({'kind': 'string', 'quote_char': qc,
                                            'triple': False, 'is_raw': False, 'is_fstring': False})
                        continue

            if fkind == 'fstring_expr':
                if ch == '{':
                    frame['brace_depth'] += 1
                    i += 1
                    continue
                if ch == '}':
                    frame['brace_depth'] -= 1
                    if frame['brace_depth'] == 0:
                        i += 1
                        parse_stack.pop()
                        continue
                    i += 1
                    continue

            # Check for keywords
            kw = _match_keyword(source, i)
            if kw is not None:
                if kw in _OPENERS:
                    stack_brackets.append((kw, line))
                elif kw in _CLOSERS:
                    expected_opener = _CLOSERS[kw]
                    if not stack_brackets:
                        errors.append(DdmmSyntaxError(
                            f"Unexpected closing '{kw}' ({_BRACKET_NAMES[kw]}) with no matching opener",
                            filename=filename, lineno=line))
                    else:
                        opener, open_line = stack_brackets.pop()
                        if opener != expected_opener:
                            errors.append(DdmmSyntaxError(
                                f"Mismatched brackets \u2014 opened with '{opener}' "
                                f"({_BRACKET_NAMES[opener]}) on line {open_line} "
                                f"but closed with '{kw}' ({_BRACKET_NAMES[kw]})",
                                filename=filename, lineno=line))
                i += len(kw)
                continue

            i += 1
            continue

    # Check for unclosed brackets
    for opener, open_line in stack_brackets:
        errors.append(DdmmSyntaxError(
            f"Unclosed '{opener}' ({_BRACKET_NAMES[opener]})",
            filename=filename, lineno=open_line))

    return errors
