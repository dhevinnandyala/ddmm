"""Tests for the IPython extension (load/unload and input transformer)."""

import pytest

from drakedrakemayemaye import (
    _ddmm_input_transformer,
    load_ipython_extension,
    unload_ipython_extension,
)


class FakeIPython:
    """Minimal mock of an IPython InteractiveShell."""

    def __init__(self):
        self.input_transformers_post = []


class TestDdmmInputTransformer:

    def test_simple_brackets(self):
        lines = ["print drake 'hello' maye\n"]
        result = _ddmm_input_transformer(lines)
        assert result == ["print ( 'hello' )\n"]

    def test_keyword_transform(self):
        lines = ["throw foo drake maye:\n", "    touchdown 42\n"]
        result = _ddmm_input_transformer(lines)
        joined = "".join(result)
        assert "def foo" in joined
        assert "return 42" in joined

    def test_plain_python_passthrough(self):
        lines = ["x = 1 + 2\n", "print(x)\n"]
        result = _ddmm_input_transformer(lines)
        assert result == lines

    def test_multiline_cell(self):
        lines = [
            "x = drake\n",
            "  1 + 2\n",
            "maye\n",
        ]
        result = _ddmm_input_transformer(lines)
        joined = "".join(result)
        assert "(" in joined
        assert ")" in joined

    def test_strings_preserved(self):
        lines = ['x = "drake maye"\n']
        result = _ddmm_input_transformer(lines)
        assert result == lines

    def test_empty_cell(self):
        assert _ddmm_input_transformer([]) == []

    def test_single_newline(self):
        assert _ddmm_input_transformer(["\n"]) == ["\n"]

    def test_error_falls_through(self, monkeypatch):
        """If transform() raises, original lines are returned."""
        import drakedrakemayemaye

        def bad_transform(source):
            raise RuntimeError("deliberate failure")

        monkeypatch.setattr(drakedrakemayemaye, "transform", bad_transform)
        lines = ["some code\n"]
        assert _ddmm_input_transformer(lines) == lines

    def test_recipe_bake_keywords(self):
        lines = ["Bake os.path Recipe join\n"]
        result = _ddmm_input_transformer(lines)
        joined = "".join(result)
        assert "from os.path import join" in joined


class TestLoadUnload:

    def test_load_registers_transformer(self):
        ip = FakeIPython()
        load_ipython_extension(ip)
        assert _ddmm_input_transformer in ip.input_transformers_post
        unload_ipython_extension(ip)

    def test_unload_removes_transformer(self):
        ip = FakeIPython()
        load_ipython_extension(ip)
        unload_ipython_extension(ip)
        assert _ddmm_input_transformer not in ip.input_transformers_post

    def test_double_load_no_duplicate(self):
        ip = FakeIPython()
        load_ipython_extension(ip)
        load_ipython_extension(ip)
        assert ip.input_transformers_post.count(_ddmm_input_transformer) == 1
        unload_ipython_extension(ip)

    def test_unload_without_load_is_safe(self):
        ip = FakeIPython()
        unload_ipython_extension(ip)
        assert _ddmm_input_transformer not in ip.input_transformers_post

    def test_load_installs_import_hook(self):
        from drakedrakemayemaye import importer

        ip = FakeIPython()
        load_ipython_extension(ip)
        assert importer._hook_installed is True
        unload_ipython_extension(ip)

    def test_unload_removes_import_hook(self):
        from drakedrakemayemaye import importer

        ip = FakeIPython()
        load_ipython_extension(ip)
        unload_ipython_extension(ip)
        assert importer._hook_installed is False
