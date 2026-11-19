"""RFC 2047 encoded-word codec.

This package provides functions to encode and decode RFC 2047 encoded-words,
which are used in email headers to represent non-ASCII text.
"""

from .core import encode, decode

__all__ = ["encode", "decode"]
