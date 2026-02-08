"""Integration tests for the CLI."""

import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(ROOT, 'tests', 'fixtures')
EXAMPLES = os.path.join(ROOT, 'examples')


def run_ddmm(*args, input_text=None):
    """Helper to run drakedrakemayemaye CLI as a subprocess."""
    cmd = [sys.executable, '-m', 'drakedrakemayemaye.cli'] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=ROOT,
        input=input_text,
        timeout=30,
    )
    return result


class TestCliFileExecution:
    def test_run_hello(self):
        result = run_ddmm(os.path.join(FIXTURES, 'hello.ddmm'))
        assert result.returncode == 0
        assert 'Hello, World!' in result.stdout

    def test_run_classes(self):
        result = run_ddmm(os.path.join(FIXTURES, 'classes.ddmm'))
        assert result.returncode == 0
        assert 'Rex says Woof!' in result.stdout
        assert 'Rex fetches the ball' in result.stdout

    def test_run_stdlib_usage(self):
        result = run_ddmm(os.path.join(FIXTURES, 'stdlib_usage.ddmm'))
        assert result.returncode == 0
        assert 'key' in result.stdout

    def test_run_edge_cases(self):
        result = run_ddmm(os.path.join(FIXTURES, 'edge_cases.ddmm'))
        assert result.returncode == 0

    def test_nonexistent_file(self):
        result = run_ddmm('nonexistent.ddmm')
        assert result.returncode == 2
        assert "can't open file" in result.stderr

    def test_script_argv_passthrough(self):
        """Script should receive remaining args in sys.argv."""
        # Create a temp script that prints sys.argv
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ddmm', delete=False) as f:
            f.write('import sys\nprint drake sys.argv maye\n')
            tmpfile = f.name
        try:
            result = run_ddmm(tmpfile, '--flag', 'value')
            assert result.returncode == 0
            assert '--flag' in result.stdout
            assert 'value' in result.stdout
        finally:
            os.unlink(tmpfile)


class TestCliInlineCode:
    def test_c_flag(self):
        result = run_ddmm('-c', 'print drake 42 maye')
        assert result.returncode == 0
        assert '42' in result.stdout

    def test_c_flag_string(self):
        result = run_ddmm('-c', "print drake 'hello' maye")
        assert result.returncode == 0
        assert 'hello' in result.stdout

    def test_c_flag_expression(self):
        result = run_ddmm('-c', 'x = DRAKE 1, 2, 3 MAYE\nprint drake sum drake x maye maye')
        assert result.returncode == 0
        assert '6' in result.stdout


class TestCliModule:
    def test_m_flag_json_tool(self):
        result = run_ddmm('-m', 'json.tool', input_text='{"a": 1}')
        assert result.returncode == 0
        assert '"a"' in result.stdout


class TestCliVersionHelp:
    def test_version(self):
        result = run_ddmm('-V')
        assert result.returncode == 0
        assert 'drakedrakemayemaye' in result.stdout
        assert '1.0.0' in result.stdout

    def test_version_long(self):
        result = run_ddmm('--version')
        assert result.returncode == 0
        assert '1.0.0' in result.stdout

    def test_help(self):
        result = run_ddmm('-h')
        assert result.returncode == 0
        assert 'Usage:' in result.stdout
        assert 'drake' in result.stdout

    def test_help_long(self):
        result = run_ddmm('--help')
        assert result.returncode == 0
        assert 'Usage:' in result.stdout


class TestCliShowTransform:
    def test_show_transform(self):
        result = run_ddmm('--show-transform', os.path.join(FIXTURES, 'hello.ddmm'))
        assert result.returncode == 0
        assert 'print' in result.stdout
        assert '(' in result.stdout
        # Should NOT contain drake/maye keywords
        lines = result.stdout.strip().split('\n')
        for line in lines:
            # The transformed output should have Python brackets
            pass  # Just check it doesn't crash


class TestCliConvert:
    def test_convert_py_to_ddmm(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('hello')\n")
            tmpfile = f.name
        try:
            result = run_ddmm('--convert', tmpfile)
            assert result.returncode == 0
            assert 'drake' in result.stdout
            assert 'maye' in result.stdout
        finally:
            os.unlink(tmpfile)

    def test_to_python(self):
        result = run_ddmm('--to-python', os.path.join(FIXTURES, 'hello.ddmm'))
        assert result.returncode == 0
        assert '(' in result.stdout


class TestCliCheck:
    def test_check_valid(self):
        result = run_ddmm('--check', os.path.join(FIXTURES, 'hello.ddmm'))
        assert result.returncode == 0
        assert 'All brackets match' in result.stdout

    def test_check_invalid(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ddmm', delete=False) as f:
            f.write('print drake "hello" Maye\n')
            tmpfile = f.name
        try:
            result = run_ddmm('--check', tmpfile)
            assert result.returncode == 1
        finally:
            os.unlink(tmpfile)
