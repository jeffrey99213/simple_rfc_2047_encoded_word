import unittest

from simple_rfc_2047_encoded_word import encode, decode


class TestEncode(unittest.TestCase):
    def test_q_encode_ascii(self):
        self.assertEqual(encode("Hello"), "=?utf-8?Q?Hello?=")

    def test_q_encode_space_becomes_underscore(self):
        self.assertEqual(encode("Hello world"), "=?utf-8?Q?Hello_world?=")

    def test_q_encode_non_ascii(self):
        # Euro sign U+20AC is E2 82 AC in UTF-8.
        self.assertEqual(encode("\u20ac"), "=?utf-8?Q?=E2=82=AC?=")

    def test_q_encode_reserved_characters(self):
        # '=', '?', and '_' must be escaped in Q encoding.
        self.assertEqual(encode("a=b?c_d"), "=?utf-8?Q?a=3Db=3Fc=5Fd?=")

    def test_b_encode_ascii(self):
        self.assertEqual(encode("Hello", encoding="B"), "=?utf-8?B?SGVsbG8=?=")

    def test_b_encode_non_ascii(self):
        self.assertEqual(encode("\u20ac", encoding="B"), "=?utf-8?B?4oKs?=")

    def test_encode_lowercase_encoding_name(self):
        self.assertEqual(encode("Hi", encoding="b"), "=?utf-8?B?SGk=?=")

    def test_encode_unknown_encoding_raises(self):
        with self.assertRaises(ValueError):
            encode("x", encoding="X")

    def test_encode_unknown_charset_raises(self):
        with self.assertRaises(LookupError):
            encode("x", charset="no-such-charset")


class TestDecode(unittest.TestCase):
    def test_q_decode_ascii(self):
        self.assertEqual(decode("=?utf-8?Q?Hello?="), "Hello")

    def test_q_decode_underscore_becomes_space(self):
        self.assertEqual(decode("=?utf-8?Q?Hello_world?="), "Hello world")

    def test_q_decode_hex_escape(self):
        self.assertEqual(decode("=?utf-8?Q?=E2=82=AC?="), "\u20ac")

    def test_q_decode_literal_equals(self):
        # A lone '=' not followed by two hex digits is kept literally.
        self.assertEqual(decode("=?utf-8?Q?a=b?="), "a=b")

    def test_b_decode_ascii(self):
        self.assertEqual(decode("=?utf-8?B?SGVsbG8=?="), "Hello")

    def test_b_decode_non_ascii(self):
        self.assertEqual(decode("=?utf-8?B?4oKs?="), "\u20ac")

    def test_decode_lowercase_encoding_indicator(self):
        self.assertEqual(decode("=?utf-8?q?Hi?="), "Hi")

    def test_decode_unknown_charset_raises(self):
        with self.assertRaises(LookupError):
            decode("=?no-such-charset?Q?Hello?=")

    def test_decode_invalid_encoded_word_raises(self):
        with self.assertRaises(ValueError):
            decode("not an encoded word")

    def test_decode_invalid_base64_raises(self):
        with self.assertRaises(ValueError):
            decode("=?utf-8?B?!!!?=")


class TestRoundTrip(unittest.TestCase):
    def test_round_trip_q(self):
        original = "Caf\u00e9 \u20ac \u4e2d\u6587"
        encoded = encode(original, encoding="Q")
        self.assertEqual(decode(encoded), original)

    def test_round_trip_b(self):
        original = "Caf\u00e9 \u20ac \u4e2d\u6587"
        encoded = encode(original, encoding="B")
        self.assertEqual(decode(encoded), original)

    def test_round_trip_latin1_charset(self):
        original = "Caf\u00e9"
        encoded = encode(original, charset="latin-1", encoding="Q")
        self.assertEqual(decode(encoded), original)


if __name__ == "__main__":
    unittest.main()
