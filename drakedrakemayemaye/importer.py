"""Import hook for .ddmm files.

Allows .ddmm files to be imported using standard Python import syntax.
Implements a MetaPathFinder + Loader that reads .ddmm files, transforms
them to Python, compiles, and executes.
"""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import marshal
import os
import struct
import sys
import time
from pathlib import Path
from types import ModuleType

from drakedrakemayemaye.transpiler import transform

_MAGIC = b'ddmm'
_CACHE_DIR = '__ddmmcache__'
_SELF_PACKAGE = 'drakedrakemayemaye'


def _cache_path(source_path: str) -> str:
    """Compute cache path for a .ddmm source file."""
    src = Path(source_path)
    cache_dir = src.parent / _CACHE_DIR
    return str(cache_dir / (src.stem + '.ddmm.pyc'))


def _read_cache(cache_file: str, source_mtime: float) -> bytes | None:
    """Read cached bytecode if valid. Returns code bytes or None."""
    try:
        with open(cache_file, 'rb') as f:
            magic = f.read(4)
            if magic != _MAGIC:
                return None
            stored_mtime = struct.unpack('<d', f.read(8))[0]
            if stored_mtime != source_mtime:
                return None
            return f.read()
    except (OSError, struct.error):
        return None


def _write_cache(cache_file: str, source_mtime: float, code: bytes) -> None:
    """Write compiled bytecode to cache."""
    try:
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'wb') as f:
            f.write(_MAGIC)
            f.write(struct.pack('<d', source_mtime))
            f.write(code)
    except OSError:
        pass


class DdmmFinder(importlib.abc.MetaPathFinder):
    """Finder that locates .ddmm files and __init__.ddmm packages on sys.path."""

    def find_spec(self, fullname, path, target=None):
        # Block self-imports to prevent recursion
        if fullname == _SELF_PACKAGE or fullname.startswith(_SELF_PACKAGE + '.'):
            return None

        parts = fullname.split('.')
        tail = parts[-1]

        search_paths = path if path else sys.path

        for entry in search_paths:
            entry = str(entry)

            # Check for package: <entry>/<tail>/__init__.ddmm
            pkg_init = os.path.join(entry, tail, '__init__.ddmm')
            if os.path.isfile(pkg_init):
                spec = importlib.machinery.ModuleSpec(
                    fullname,
                    DdmmLoader(),
                    origin=pkg_init,
                    is_package=True,
                )
                spec.submodule_search_locations = [os.path.join(entry, tail)]
                return spec

            # Check for module: <entry>/<tail>.ddmm
            mod_file = os.path.join(entry, tail + '.ddmm')
            if os.path.isfile(mod_file):
                return importlib.machinery.ModuleSpec(
                    fullname,
                    DdmmLoader(),
                    origin=mod_file,
                )

        return None


class DdmmLoader(importlib.abc.Loader):
    """Loader that reads .ddmm files, transforms to Python, and executes."""

    def create_module(self, spec):
        return None  # Use default module creation

    def exec_module(self, module):
        source_path = module.__spec__.origin
        source_mtime = os.path.getmtime(source_path)

        # Try cache first
        cache_file = _cache_path(source_path)
        cached = _read_cache(cache_file, source_mtime)

        if cached is not None:
            code = marshal.loads(cached)
        else:
            with open(source_path, 'r', encoding='utf-8') as f:
                ddmm_source = f.read()
            python_source = transform(ddmm_source)
            code = compile(python_source, source_path, 'exec')
            _write_cache(cache_file, source_mtime, marshal.dumps(code))

        # Set up package attributes if needed
        if module.__spec__.submodule_search_locations is not None:
            module.__path__ = list(module.__spec__.submodule_search_locations)

        exec(code, module.__dict__)

    def get_source(self, fullname):
        spec = importlib.util.find_spec(fullname)
        if spec and spec.origin:
            with open(spec.origin, 'r', encoding='utf-8') as f:
                return f.read()
        return None


_hook_installed = False
_finder_instance = None


def install_hook() -> None:
    """Install the .ddmm import hook into sys.meta_path."""
    global _hook_installed, _finder_instance
    if _hook_installed:
        return
    _finder_instance = DdmmFinder()
    sys.meta_path.insert(0, _finder_instance)
    _hook_installed = True


def uninstall_hook() -> None:
    """Remove the .ddmm import hook from sys.meta_path."""
    global _hook_installed, _finder_instance
    if not _hook_installed:
        return
    try:
        sys.meta_path.remove(_finder_instance)
    except ValueError:
        pass
    _finder_instance = None
    _hook_installed = False
