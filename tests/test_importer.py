"""Tests for the .ddmm import hook."""

import os
import sys
import tempfile
import shutil

import pytest

from drakedrakemayemaye.importer import install_hook, uninstall_hook


@pytest.fixture(autouse=True)
def clean_hook():
    """Install hook before each test, uninstall after."""
    install_hook()
    yield
    uninstall_hook()
    # Clean up any test modules from sys.modules
    to_remove = [k for k in sys.modules if k.startswith('_test_ddmm_')]
    for k in to_remove:
        del sys.modules[k]


@pytest.fixture
def tmp_module_dir(tmp_path):
    """Create a temp dir and add it to sys.path for imports."""
    sys.path.insert(0, str(tmp_path))
    yield tmp_path
    sys.path.remove(str(tmp_path))


class TestBasicImport:
    def test_import_simple_module(self, tmp_module_dir):
        # Create a .ddmm module
        mod_file = tmp_module_dir / '_test_ddmm_simple.ddmm'
        mod_file.write_text('x = 42\ndef get_x drake maye:\n    return x\n')

        import _test_ddmm_simple
        assert _test_ddmm_simple.x == 42
        assert _test_ddmm_simple.get_x() == 42

    def test_from_import(self, tmp_module_dir):
        mod_file = tmp_module_dir / '_test_ddmm_frommod.ddmm'
        mod_file.write_text('value = "hello"\n')

        from _test_ddmm_frommod import value
        assert value == "hello"


class TestCrossImport:
    def test_ddmm_imports_ddmm(self, tmp_module_dir):
        # utils module
        utils = tmp_module_dir / '_test_ddmm_utils2.ddmm'
        utils.write_text('def double drake n maye:\n    return n * 2\n')

        # main module that imports utils
        main = tmp_module_dir / '_test_ddmm_main2.ddmm'
        main.write_text('from _test_ddmm_utils2 import double\nresult = double drake 21 maye\n')

        import _test_ddmm_main2
        assert _test_ddmm_main2.result == 42


class TestStdlibImport:
    def test_stdlib_from_ddmm(self, tmp_module_dir):
        mod = tmp_module_dir / '_test_ddmm_stdlib.ddmm'
        mod.write_text('import math\npi = math.pi\nsqrt4 = math.sqrt drake 4 maye\n')

        import _test_ddmm_stdlib
        assert abs(_test_ddmm_stdlib.pi - 3.14159) < 0.001
        assert _test_ddmm_stdlib.sqrt4 == 2.0


class TestPackageImport:
    def test_init_ddmm_package(self, tmp_module_dir):
        pkg_dir = tmp_module_dir / '_test_ddmm_pkg'
        pkg_dir.mkdir()
        init = pkg_dir / '__init__.ddmm'
        init.write_text('pkg_name = "test_package"\n')

        import _test_ddmm_pkg
        assert _test_ddmm_pkg.pkg_name == "test_package"

    def test_package_submodule(self, tmp_module_dir):
        pkg_dir = tmp_module_dir / '_test_ddmm_pkg2'
        pkg_dir.mkdir()
        (pkg_dir / '__init__.ddmm').write_text('')
        (pkg_dir / 'sub.ddmm').write_text('val = 99\n')

        from _test_ddmm_pkg2 import sub
        assert sub.val == 99


class TestCaching:
    def test_cache_created(self, tmp_module_dir):
        mod = tmp_module_dir / '_test_ddmm_cached.ddmm'
        mod.write_text('cached_val = True\n')

        import _test_ddmm_cached
        assert _test_ddmm_cached.cached_val is True

        # Check cache dir exists
        cache_dir = tmp_module_dir / '__ddmmcache__'
        assert cache_dir.exists()


class TestSelfImportBlock:
    def test_no_recurse_on_self(self):
        """Importing drakedrakemayemaye should NOT go through DdmmFinder."""
        # This should work without recursion
        import drakedrakemayemaye
        assert hasattr(drakedrakemayemaye, '__version__')
