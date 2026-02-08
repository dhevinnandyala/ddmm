"""Tests for the core transpiler."""

import pytest
from drakedrakemayemaye.transpiler import (
    transform, reverse_transform, check_bracket_matching, DdmmSyntaxError,
)


class TestTransformBasicBrackets:
    def test_parentheses(self):
        assert transform("print drake 'hi' maye") == "print ( 'hi' )"

    def test_curly_braces(self):
        assert transform("d = Drake 'a': 1 Maye") == "d = { 'a': 1 }"

    def test_square_brackets(self):
        assert transform("x = DRAKE 1, 2, 3 MAYE") == "x = [ 1, 2, 3 ]"


class TestTransformMixedNesting:
    def test_mixed_nesting(self):
        assert transform(
            "x DRAKE Drake 'k': v Maye for k, v in items drake maye MAYE"
        ) == "x [ { 'k': v } for k, v in items ( ) ]"


class TestTransformStringsPreserved:
    def test_double_quoted_string(self):
        assert transform('x = "drake maye"') == 'x = "drake maye"'

    def test_single_quoted_string(self):
        assert transform("x = 'Drake Maye'") == "x = 'Drake Maye'"

    def test_triple_quoted_string(self):
        assert transform('x = """drake DRAKE Drake"""') == 'x = """drake DRAKE Drake"""'


class TestTransformComments:
    def test_comments_preserved(self):
        assert transform("# drake maye Drake Maye") == "# drake maye Drake Maye"

    def test_inline_comment(self):
        result = transform("x = 1  # drake maye")
        assert result == "x = 1  # drake maye"


class TestTransformFStrings:
    def test_fstring_expressions_transformed(self):
        assert transform('f"{x.upper drake maye}"') == 'f"{x.upper ( )}"'

    def test_fstring_square_brackets(self):
        assert transform('f"{d DRAKE key MAYE}"') == 'f"{d [ key ]}"'

    def test_fstring_literal_not_transformed(self):
        assert transform('f"drake maye"') == 'f"drake maye"'


class TestTransformWordBoundaries:
    def test_drakesmith(self):
        assert transform("drakesmith = 1") == "drakesmith = 1"

    def test_x_drake(self):
        assert transform("x_drake = 1") == "x_drake = 1"

    def test_mayefield(self):
        assert transform("mayefield = 1") == "mayefield = 1"

    def test_DRAKES(self):
        assert transform("DRAKES = 1") == "DRAKES = 1"


class TestTransformRawStrings:
    def test_raw_string(self):
        assert transform('r"drake maye"') == 'r"drake maye"'

    def test_raw_fstring_literal(self):
        assert transform('rf"drake maye"') == 'rf"drake maye"'


class TestTransformRealWorld:
    def test_dict_comprehension(self):
        input_code = "result = Drake k: v for k, v in items drake maye if v > 0 Maye"
        expected = "result = { k: v for k, v in items ( ) if v > 0 }"
        assert transform(input_code) == expected

    def test_nested_data_structure(self):
        input_code = "data = Drake 'users': DRAKE Drake 'name': 'Alice' Maye, Drake 'name': 'Bob' Maye MAYE Maye"
        expected = "data = { 'users': [ { 'name': 'Alice' }, { 'name': 'Bob' } ] }"
        assert transform(input_code) == expected

    def test_class_definition(self):
        input_code = "class Foo drake Bar, metaclass=ABCMeta maye:"
        expected = "class Foo ( Bar, metaclass=ABCMeta ):"
        assert transform(input_code) == expected


class TestReverseTransform:
    def test_parentheses(self):
        assert reverse_transform("print('hi')") == "print drake 'hi' maye"

    def test_curly_braces(self):
        assert reverse_transform("d = {'a': 1}") == "d = Drake 'a': 1 Maye"

    def test_square_brackets(self):
        assert reverse_transform("x = [1, 2]") == "x = DRAKE 1, 2 MAYE"


class TestTransformEdgeCases:
    def test_empty_input(self):
        assert transform("") == ""

    def test_no_keywords(self):
        assert transform("x = 1 + 2") == "x = 1 + 2"

    def test_consecutive_keywords(self):
        assert transform("drake drake maye maye") == "( ( ) )"

    def test_keyword_at_start(self):
        assert transform("drake maye") == "( )"

    def test_keyword_at_end(self):
        assert transform("f drake x maye") == "f ( x )"

    def test_multiline(self):
        src = "x = drake\n  1 + 2\nmaye"
        expected = "x = (\n  1 + 2\n)"
        assert transform(src) == expected

    def test_escaped_quotes_in_string(self):
        assert transform(r'x = "dra\"ke"') == r'x = "dra\"ke"'

    def test_byte_string(self):
        assert transform('b"drake maye"') == 'b"drake maye"'

    def test_backslash_continuation(self):
        src = "x = drake \\\n  1 + 2 \\\nmaye"
        expected = "x = ( \\\n  1 + 2 \\\n)"
        assert transform(src) == expected

    def test_numbers_adjacent(self):
        # Keywords next to numbers should still transform (numbers aren't identifier starts for boundary)
        assert transform("x = drake 42 maye") == "x = ( 42 )"

    def test_string_with_prefix_uppercase(self):
        assert transform('F"drake maye"') == 'F"drake maye"'

    def test_triple_single_quoted(self):
        assert transform("x = '''drake maye'''") == "x = '''drake maye'''"


class TestCheckBracketMatching:
    def test_valid_brackets(self):
        errors = check_bracket_matching("drake maye")
        assert len(errors) == 0

    def test_mismatched(self):
        errors = check_bracket_matching("drake Maye")
        assert len(errors) == 1
        assert "paren" in str(errors[0])
        assert "curly brace" in str(errors[0])

    def test_unclosed(self):
        errors = check_bracket_matching("drake")
        assert len(errors) == 1
        assert "Unclosed" in str(errors[0])

    def test_extra_closer(self):
        errors = check_bracket_matching("maye")
        assert len(errors) == 1
        assert "Unexpected" in str(errors[0])
