"""drakedrakemayemaye - A Python interpreter with Drake Maye bracket syntax."""

__version__ = "1.0.0"

from drakedrakemayemaye.transpiler import transform, reverse_transform

__all__ = [
    "transform",
    "reverse_transform",
    "__version__",
    "load_ipython_extension",
    "unload_ipython_extension",
]


def _ddmm_input_transformer(lines: list[str]) -> list[str]:
    """IPython input transformer that converts ddmm syntax to Python."""
    source = "".join(lines)
    try:
        transformed = transform(source)
    except Exception:
        return lines
    result = transformed.splitlines(True)
    if not result and lines:
        return lines
    return result


def load_ipython_extension(ipython):
    """Called by ``%load_ext drakedrakemayemaye``.

    Registers an input transformer so every cell accepts ddmm syntax.
    Also installs the .ddmm import hook.
    """
    from drakedrakemayemaye.importer import install_hook

    if _ddmm_input_transformer not in ipython.input_transformers_post:
        ipython.input_transformers_post.append(_ddmm_input_transformer)

    install_hook()


def unload_ipython_extension(ipython):
    """Called by ``%unload_ext drakedrakemayemaye``.

    Removes the input transformer and uninstalls the import hook.
    """
    from drakedrakemayemaye.importer import uninstall_hook

    try:
        ipython.input_transformers_post.remove(_ddmm_input_transformer)
    except ValueError:
        pass

    uninstall_hook()
