"""Edge case tests for complex Python constructs."""

import subprocess
import sys
import os

import pytest

from drakedrakemayemaye.transpiler import transform, reverse_transform

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_ddmm_code(code):
    """Helper to run ddmm code via -c flag."""
    cmd = [sys.executable, '-m', 'drakedrakemayemaye.cli', '-c', code]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=15)
    return result


class TestClassSyntax:
    def test_class_with_metaclass(self):
        code = transform("class Foo drake Bar, metaclass=type maye:\n    pass")
        assert "class Foo ( Bar, metaclass=type ):" in code

    def test_class_methods(self):
        src = "class C:\n    def m drake self maye:\n        return self.x"
        expected_lines = transform(src).split('\n')
        assert 'def m ( self ):' in expected_lines[1].strip()


class TestDecoratorSyntax:
    def test_decorator_with_args(self):
        src = "@decorator drake arg1, arg2 maye\ndef func drake maye:\n    pass"
        result = transform(src)
        assert "@decorator ( arg1, arg2 )" in result

    def test_property_decorator(self):
        src = "@property\ndef name drake self maye:\n    return self._name"
        result = transform(src)
        assert "@property" in result
        assert "def name ( self ):" in result


class TestAsyncAwait:
    def test_async_def(self):
        src = "async def fetch drake url maye:\n    return await get drake url maye"
        result = transform(src)
        assert "async def fetch ( url ):" in result
        assert "return await get ( url )" in result

    def test_async_for(self):
        src = "async for item in aiter drake maye:\n    pass"
        result = transform(src)
        assert "async for item in aiter ( ):" in result


class TestWalrusOperator:
    def test_walrus_in_if(self):
        src = "if drake n := 10 maye > 5:\n    print drake n maye"
        result = transform(src)
        assert "if ( n := 10 ) > 5:" in result


class TestComprehensions:
    def test_list_comprehension(self):
        src = "DRAKE x for x in range drake 10 maye MAYE"
        result = transform(src)
        assert "[ x for x in range ( 10 ) ]" in result

    def test_dict_comprehension(self):
        src = "Drake k: v for k, v in items drake maye Maye"
        result = transform(src)
        assert "{ k: v for k, v in items ( ) }" in result

    def test_nested_comprehension(self):
        src = "DRAKE DRAKE i * j for j in range drake 3 maye MAYE for i in range drake 3 maye MAYE"
        result = transform(src)
        assert "[ [ i * j for j in range ( 3 ) ] for i in range ( 3 ) ]" in result


class TestMatchCase:
    def test_match_statement(self):
        src = """match command:
    case "quit":
        exit drake maye
    case "hello":
        print drake "hi" maye"""
        result = transform(src)
        assert 'exit ( )' in result
        assert 'print ( "hi" )' in result


class TestTypeHints:
    def test_function_annotations(self):
        src = "def add drake a: int, b: int maye -> int:\n    return a + b"
        result = transform(src)
        assert "def add ( a: int, b: int ) -> int:" in result

    def test_generic_types(self):
        src = "x: list DRAKE int MAYE = DRAKE 1, 2, 3 MAYE"
        result = transform(src)
        assert "x: list [ int ] = [ 1, 2, 3 ]" in result


class TestStringEdgeCases:
    def test_fstring_nested_quotes(self):
        src = """f"{'hello'}" """
        # Should pass through as-is (no keywords)
        result = transform(src)
        assert result.strip() == src.strip()

    def test_multiline_string(self):
        src = '"""\ndrake maye\nDrake Maye\n"""'
        result = transform(src)
        assert result == src  # No transformation inside strings

    def test_fstring_with_dict_access(self):
        src = 'f"{d DRAKE key MAYE}"'
        result = transform(src)
        assert 'f"{d [ key ]}"' == result

    def test_escaped_braces_in_fstring(self):
        src = 'f"{{not an expression}}"'
        result = transform(src)
        assert result == src


class TestRoundTrip:
    """Test that transform -> reverse_transform is close to identity."""

    def test_simple_roundtrip(self):
        original = "print drake 'hello' maye"
        python = transform(original)
        back = reverse_transform(python)
        assert back == original

    def test_complex_roundtrip(self):
        original = "x = DRAKE Drake 'a': 1 Maye, Drake 'b': 2 Maye MAYE"
        python = transform(original)
        back = reverse_transform(python)
        assert back == original


class TestExecution:
    """Test that transformed code actually runs correctly."""

    def test_hello_world_runs(self):
        result = run_ddmm_code('print drake "Hello" maye')
        assert result.returncode == 0
        assert 'Hello' in result.stdout

    def test_list_operations(self):
        code = 'x = DRAKE 1, 2, 3 MAYE\nx.append drake 4 maye\nprint drake x maye'
        result = run_ddmm_code(code)
        assert result.returncode == 0
        assert '[1, 2, 3, 4]' in result.stdout

    def test_dict_operations(self):
        code = 'd = Drake "a": 1 Maye\nd DRAKE "b" MAYE = 2\nprint drake d maye'
        result = run_ddmm_code(code)
        assert result.returncode == 0
        assert "'a': 1" in result.stdout
        assert "'b': 2" in result.stdout

    def test_class_instantiation(self):
        code = """class Point:
    def __init__ drake self, x, y maye:
        self.x = x
        self.y = y
p = Point drake 1, 2 maye
print drake p.x, p.y maye"""
        result = run_ddmm_code(code)
        assert result.returncode == 0
        assert '1 2' in result.stdout
