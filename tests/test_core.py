"""Tests for the BinHex 5.0 RLE decoder."""

import unittest

from binhex_5_0_rle_decoder import decode
from binhex_5_0_rle_decoder.core import RLEError


class TestDecode(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(decode(b""), b"")

    def test_run_block(self):
        # lead=3, payload byte 0x41
        self.assertEqual(decode(b"\x03A"), b"AAA")

    def test_run_max_lead_214(self):
        self.assertEqual(decode(b"\xd6A"), b"A" * 214)

    def test_literal_block(self):
        # lead=0, count=4, payload bytes
        self.assertEqual(decode(b"\x00\x04ABCD"), b"ABCD")

    def test_literal_count_255(self):
        self.assertEqual(decode(b"\x00\xff" + b"x" * 255), b"x" * 255)

    def test_multiple_blocks(self):
        self.assertEqual(
            decode(b"\x03A\x00\x02BC\x02Z"),
            b"AAABCZZ",
        )

    def test_lead_zero_payload_byte(self):
        # The payload byte of a run block may itself be zero; we must repeat it.
        self.assertEqual(decode(b"\x03\x00"), b"\x00\x00\x00")

    def test_lead_byte_215_rejected(self):
        with self.assertRaises(RLEError) as ctx:
            decode(b"\xd7A")
        self.assertEqual(ctx.exception.offset, 0)

    def test_lead_byte_255_rejected(self):
        with self.assertRaises(RLEError):
            decode(b"\xffA")

    def test_zero_literal_count_rejected(self):
        with self.assertRaises(RLEError) as ctx:
            decode(b"\x00\x00")
        self.assertEqual(ctx.exception.offset, 1)

    def test_run_missing_payload(self):
        with self.assertRaises(RLEError) as ctx:
            decode(b"\x03")
        self.assertEqual(ctx.exception.offset, 0)

    def test_literal_missing_count(self):
        with self.assertRaises(RLEError) as ctx:
            decode(b"\x00")
        self.assertEqual(ctx.exception.offset, 0)

    def test_literal_payload_truncated(self):
        with self.assertRaises(RLEError) as ctx:
            decode(b"\x00\x05ABC")
        self.assertEqual(ctx.exception.offset, 1)

    def test_returns_bytes_type(self):
        self.assertIsInstance(decode(b""), bytes)


if __name__ == "__main__":
    unittest.main()
