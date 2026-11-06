"""The plain functions that a frontend composes around its own rules."""
import unittest

import text2spoken
from text2spoken import (
    expand_dates_and_times,
    expand_hyphen_digits,
    expand_units,
    expand_word,
    normalize,
)


class TestPublicFunctions(unittest.TestCase):

    def test_all_names_resolve(self):
        for name in text2spoken.__all__:
            with self.subTest(name=name):
                self.assertTrue(hasattr(text2spoken, name))

    def test_version_is_the_version_module_value(self):
        from text2spoken.version import __version__
        self.assertEqual(text2spoken.__version__, __version__)

    def test_expand_hyphen_digits_splits_a_word_from_a_digit(self):
        self.assertEqual(expand_hyphen_digits("sub-23"), "sub 23")

    def test_expand_hyphen_digits_keeps_a_range(self):
        self.assertEqual(expand_hyphen_digits("3-2"), "3-2")

    def test_expand_units_reads_the_portuguese_table(self):
        self.assertEqual(expand_units("10kg", "pt"), "dez quilogramas")

    def test_expand_dates_and_times_leaves_plain_words(self):
        self.assertEqual(expand_dates_and_times("I am happy", "en"), "I am happy")

    def test_expand_word_reads_a_contraction(self):
        self.assertEqual(expand_word("can't", "en"), "can not")

    def test_expand_word_reads_a_number_and_keeps_its_punctuation(self):
        self.assertEqual(expand_word("23,", "en"), "twenty three,")

    def test_expand_word_equals_the_word_pass_of_normalize(self):
        for word in ("Dr.", "doesn't", "12", "3/4", "hello"):
            with self.subTest(word=word):
                self.assertEqual(expand_word(word, "en"), normalize(word, "en"))


if __name__ == "__main__":
    unittest.main()
