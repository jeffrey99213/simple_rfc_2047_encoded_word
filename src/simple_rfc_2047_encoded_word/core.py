"""Core implementation of RFC 2047 encoded-word encoding and decoding.

The module exposes two functions:

- ``encode(text, charset='utf-8', encoding='Q')``
- ``decode(encoded_word)``

The implementation deliberately supports only the two standard encodings
(``Q`` and ``B``) and a single encoded-word at a time.  Multi-word
concatenation and header folding are outside the scope; callers that need
them can split on whitespace and join after decoding.
"""

import base64
import binascii
import quopri
import re

__all__ = ["encode", "decode"]

# A strict but practical pattern for an encoded-word as defined in RFC 2047.
# The charset is restricted to characters that can appear in a MIME token.
_ENCODED_WORD_RE = re.compile(
    r"=\?"
    r"(?P<charset>[^?]+)"
    r"\?"
    r"(?P<encoding>[QqBb])"
    r"\?"
    r"(?P<text>[^?]*)"
    r"\?="
)


def _q_encode(data: bytes) -> str:
    """Encode bytes using the Q encoding from RFC 2047.

    The Q encoding is a restricted form of quoted-printable: spaces are
    represented as underscores, and printable ASCII characters other than
    ``=``, ``?``, and ``_`` are left as-is.  All other bytes are written as
    ``=XX`` with uppercase hex digits.
    """
    out = []
    for byte in data:
        if byte == 0x20:
            out.append("_")
        elif 0x21 <= byte <= 0x7E and byte not in (0x3D, 0x3F, 0x5F):
            out.append(chr(byte))
        else:
            out.append(f"={byte:02X}")
    return "".join(out)


def _q_decode(text: str) -> bytes:
    """Decode a Q-encoded string back to bytes.

    Underscores become spaces, and ``=XX`` sequences are converted to bytes.
    A literal ``=`` that is not followed by two hex digits is treated as a
    literal equals sign, matching the permissive behaviour of many mailers.
    """
    out = bytearray()
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "_":
            out.append(0x20)
            i += 1
        elif ch == "=":
            if i + 2 < n:
                hex_part = text[i + 1 : i + 3]
                try:
                    out.append(int(hex_part, 16))
                    i += 3
                    continue
                except ValueError:
                    pass
            # Not a valid escape; keep the equals sign literally.
            out.append(ord("="))
            i += 1
        else:
            out.append(ord(ch))
            i += 1
    return bytes(out)


def encode(text: str, charset: str = "utf-8", encoding: str = "Q") -> str:
    """Encode a string as an RFC 2047 encoded-word.

    Parameters
    ----------
    text : str
        The text to encode.  It is converted to bytes using *charset*.
    charset : str, optional
        The character set to use.  Defaults to ``"utf-8"``.
    encoding : str, optional
        Either ``"Q"`` (quoted-printable-like) or ``"B"`` (base64).
        Case-insensitive.  Defaults to ``"Q"``.

    Returns
    -------
    str
        An encoded-word of the form ``=?charset?encoding?encoded-text?=``.

    Raises
    ------
    ValueError
        If *encoding* is not ``"Q"`` or ``"B"``.
    LookupError
        If *charset* is not a known codec.
    """
    encoding_upper = encoding.upper()
    if encoding_upper not in ("Q", "B"):
        raise ValueError(f"unsupported encoding: {encoding!r}")

    data = text.encode(charset)

    if encoding_upper == "B":
        encoded_text = base64.b64encode(data).decode("ascii")
    else:
        encoded_text = _q_encode(data)

    return f"=?{charset}?{encoding_upper}?{encoded_text}?="


def decode(encoded_word: str) -> str:
    """Decode a single RFC 2047 encoded-word.

    Parameters
    ----------
    encoded_word : str
        A string that is exactly one encoded-word, e.g.
        ``"=?utf-8?Q?Hello_=E2=82=AC?="``.

    Returns
    -------
    str
        The decoded text.

    Raises
    ------
    ValueError
        If *encoded_word* is not a valid encoded-word.
    LookupError
        If the charset named in the encoded-word is unknown.
    """
    match = _ENCODED_WORD_RE.fullmatch(encoded_word)
    if match is None:
        raise ValueError(f"not a valid encoded-word: {encoded_word!r}")

    charset = match.group("charset")
    encoding = match.group("encoding").upper()
    text = match.group("text")

    if encoding == "B":
        # Base64 decoding is strict; padding is required.
        try:
            data = base64.b64decode(text, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError(f"invalid base64 in encoded-word: {text!r}") from exc
    else:
        data = _q_decode(text)

    return data.decode(charset)
