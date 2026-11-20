# simple_rfc_2047_encoded_word

Encode and decode RFC 2047 encoded-words, handling Q and B encodings across multiple charsets.

```python
from simple_rfc_2047_encoded_word import encode, decode

encoded = encode("Caf\u00e9 \u20ac", encoding="Q")
print(encoded)          # =?utf-8?Q?Caf=C3=A9_=E2=82=AC?=
print(decode(encoded))  # Caf\u00e9 \u20ac
```

## Why this library exists

Email headers are plain ASCII, but the text inside them often is not. RFC 2047
solves this by packing non-ASCII text into a short token like
`=?utf-8?Q?Caf=C3=A9?=` that any mail client can pass around. The encoding looks
simple until you hit the details: Q encoding treats space as underscore, escapes
`=`, `?`, and `_`, and tolerates stray equals signs; B encoding is just base64
but the charset still has to be honoured on the way out.

This library does one thing: it turns a single string into a single encoded-word
and back. It does **not** try to parse whole headers, fold lines, or join
adjacent encoded-words. That decision keeps the API small and the failure modes
obvious. If you need to handle a full header, split it on whitespace, decode each
token, and concatenate the results yourself.

## API

### `encode(text, charset='utf-8', encoding='Q')`

Returns an encoded-word string. `encoding` may be `'Q'` or `'B'`
(case-insensitive). Raises `ValueError` for an unsupported encoding and
`LookupError` for an unknown charset.

### `decode(encoded_word)`

Returns the decoded string. Raises `ValueError` if the input is not a valid
encoded-word (including malformed base64), and `LookupError` for an unknown
charset.

## Awkward edge

A lone `=` in a Q-encoded word that is not followed by two hex digits is kept as
a literal equals sign. This matches what many mailers do and avoids rejecting
otherwise valid-looking tokens, but it means `=?utf-8?Q?a=b?=` decodes to
`a=b`, not an error.
