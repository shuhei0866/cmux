"""Exercise a separately built Nucleo FFI library without launching cmux."""
import ctypes as c
import sys
import unittest


class Span(c.Structure):
    _fields_ = [("title_offset", c.c_size_t), ("title_len", c.c_size_t),
                ("search_offset", c.c_size_t), ("search_len", c.c_size_t),
                ("rank", c.c_int32)]


class Match(c.Structure):
    _fields_ = [("index", c.c_size_t), ("score", c.c_double), ("rank", c.c_int32)]


class SearchCompatibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = c.CDLL(cls.library_path)
        cls.lib.cmux_nucleo_index_create.argtypes = [c.c_void_p, c.c_size_t, c.POINTER(Span), c.c_size_t]
        cls.lib.cmux_nucleo_index_create.restype = c.c_void_p
        cls.lib.cmux_nucleo_index_destroy.argtypes = [c.c_void_p]
        cls.lib.cmux_nucleo_index_destroy.restype = None
        cls.lib.cmux_nucleo_index_search.argtypes = [c.c_void_p, c.c_void_p, c.c_size_t,
                                                   c.c_size_t, c.POINTER(Match), c.c_size_t,
                                                   c.POINTER(c.c_size_t)]
        cls.lib.cmux_nucleo_index_search.restype = c.c_int32

    def setUp(self):
        titles = ["Open Settings", "Split Right", "設定を開く"]
        blob = b""
        spans = []
        for rank, title in enumerate(titles):
            value = title.encode("utf8")
            spans.append(Span(len(blob), len(value), len(blob), len(value), rank))
            blob += value
        self.buffer = c.create_string_buffer(blob)
        self.spans = (Span * len(spans))(*spans)
        self.index = self.lib.cmux_nucleo_index_create(self.buffer, len(blob), self.spans, len(spans))
        self.assertTrue(self.index)
        self.addCleanup(self.lib.cmux_nucleo_index_destroy, self.index)

    def search(self, query, limit=3):
        raw = query.encode("utf8") if isinstance(query, str) else query
        buffer = c.create_string_buffer(raw)
        matches = (Match * 3)()
        count = c.c_size_t()
        status = self.lib.cmux_nucleo_index_search(self.index, buffer, len(raw), limit,
                                                  matches, len(matches), c.byref(count))
        return status, [(m.index, m.score, m.rank) for m in matches[:count.value]]

    def test_ascii_query(self):
        status, matches = self.search("settings")
        self.assertEqual(status, 0)
        self.assertEqual(matches[0][0], 0)

    def test_japanese_query(self):
        status, matches = self.search("設定")
        self.assertEqual(status, 0)
        self.assertEqual(matches[0][0], 2)

    def test_result_limit(self):
        status, matches = self.search("", limit=2)
        self.assertEqual(status, 0)
        self.assertEqual(len(matches), 2)
        self.assertEqual(self.search("", limit=0), (0, []))

    def test_repeat_query(self):
        expected = self.search("split")
        self.assertEqual(expected[0], 0)
        self.assertEqual(expected[1][0][0], 1)
        for _ in range(10):
            self.assertEqual(self.search("split"), expected)

    def test_invalid_utf8(self):
        self.assertEqual(self.search(b"\xff"), (-2, []))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: ffi_smoke.py /absolute/path/to/test/library")
    SearchCompatibility.library_path = sys.argv.pop()
    unittest.main()
