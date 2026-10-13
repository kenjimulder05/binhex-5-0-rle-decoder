"""BinHex 5.0 run-length encoding decoder.

Exports a single function, ``decode``, which expands the lead-byte RLE
stream used by BinHex 5.0 files.
"""

from .core import decode

__all__ = ["decode"]
