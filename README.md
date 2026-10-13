# binhex-5-0-rle-decoder

Decodes the run-length encoding layer used inside BinHex 5.0 files.

```python
from binhex_5_0_rle_decoder import decode

decode(b"\x03A")          # -> b"AAA"
decode(b"\x00\x04ABCD")  # -> b"ABCD"
```

BinHex 5.0 wraps a Macintosh file (data fork, resource fork, header) in a
7-bit ASCII text envelope.  Before the 7-bit step, the bytes are run-length
encoded so long runs — common in resource forks — do not bloat the output.
This library handles only that RLE layer.  Framing, the 7-bit text encoding,
and fork reassembly are out of scope; pair it with your own BinHex parser if
you need the full format.

The encoding uses a lead byte per block.  Values 1..214 mean "repeat the next
byte *n* times."  A lead byte of 0 means "copy the next *count* bytes
verbatim" (count is the following byte, 1..255).  We treat lead bytes 215..255
and literal counts of 0 as corruption and raise `RLEError` (a `ValueError`
subclass) with the byte offset of the offending block.

The awkward edge: the payload byte of a run block may legitimately be 0, so a
run block `\x03\x00` correctly decodes to three zero bytes.  A naive decoder
that special-cases a 0 payload will mangle sparse data.
