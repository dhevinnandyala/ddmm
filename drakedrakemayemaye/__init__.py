"""drakedrakemayemaye - A Python interpreter with Drake Maye bracket syntax."""

__version__ = "1.0.0"

from drakedrakemayemaye.transpiler import transform, reverse_transform

__all__ = ["transform", "reverse_transform", "__version__"]
