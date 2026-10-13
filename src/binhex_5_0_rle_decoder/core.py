"""Core decode logic for BinHex 5.0 RLE.

BinHex 5.0 frames a binary file as 7-bit ASCII text, and inside that framing
uses a simple run-length encoding to reduce the size of long runs of identical
bytes (notably runs of zero produced by resource forks).  An encoded stream is
a sequence of blocks.  Each block begins with a one-byte lead byte *n*:

* *n* in 1..214 introduces a run block: the next byte is repeated *n* times.
* *n* == 0 introduces a literal block: the byte after the lead is a count *c*
  in 1..255, and the following *c* bytes are copied verbatim.

A strict decoder must reject lead bytes 215..255 and literal counts of zero,
because those byte patterns never appear in a validly encoded stream and their
presence indicates corruption.  We raise ``ValueError`` with the byte offset so
a caller can report where the stream went wrong.

This module operates on ``bytes`` in and out.  The wider BinHex 5.0 format
(RLE-then-7-bit-encoding, headers, forks) is intentionally out of scope: this
library is the single, small step of undoing the RLE layer.
"""


_LEAD_MAX = 214  # Lead bytes 215..255 are not used by the format.


class RLEError(ValueError):
    """Raised when an encoded stream is structurally invalid.

    Carries the byte offset into the *encoded* input where the problem was
    detected, so callers can locate the corruption.
    """

    def __init__(self, message: str, offset: int) -> None:
        super().__init__(message)
        self.offset = offset


def decode(data: bytes) -> bytes:
    """Decode a BinHex 5.0 run-length-encoded byte stream.

    * 1..214: repeat the next byte that many times.
    * 0: copy the next *count* bytes verbatim (count is 1..255).

    Raises ``RLEError`` (a ``ValueError`` subclass) on a malformed block.
    """
    out = bytearray()
    pos = 0
    n = len(data)

    while pos < n:
        lead = data[pos]
        pos += 1

        if 1 <= lead <= _LEAD_MAX:
            if pos >= n:
                raise RLEError(
                    "run block missing payload byte",
                    pos - 1,
                )
            out.extend(bytes([data[pos]]) * lead)
            pos += 1

        elif lead == 0:
            if pos >= n:
                raise RLEError(
                    "literal block missing count byte",
                    pos - 1,
                )
            count = data[pos]
            pos += 1
            if count == 0:
                raise RLEError("zero literal count", pos - 1)
            if pos + count > n:
                raise RLEError(
                    "literal block payload extends past end of input",
                    pos - 1,
                )
            out.extend(data[pos : pos + count])
            pos += count

        else:
            raise RLEError(
                "invalid lead byte %d (valid: 0..214)" % lead,
                pos - 1,
            )

    return bytes(out)
