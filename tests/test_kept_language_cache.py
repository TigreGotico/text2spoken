"""A recognizer that reads with a narrower language builds that language once, so the caches keyed on a language
keep one entry for it and do not fill with one entry for each call."""
import pytest

from text2spoken import normalize
from text2spoken.core.language import number_grouping


@pytest.mark.parametrize("text, tag", [("Costa 5 € e ¥-5.", "pt-PT"), ("Fa 35 mm i 5 €.", "ca-ES"),
                                       ("off 🇵🇹 x", "en-GB")])
def test_a_second_call_on_the_same_text_adds_no_cache_entry(text, tag):
    normalize(text, tag)
    misses = number_grouping.cache_info().misses
    normalize(text, tag)
    assert number_grouping.cache_info().misses == misses
