"""Language tags and the loader (design section 6). The loader needs `langcodes`, which the package requires
through `linguatag[langcodes]`."""
from importlib.metadata import requires

import pytest
from packaging.requirements import Requirement

from text2spoken import InvalidLanguageTagError, normalize, supports
from text2spoken.core.language import cldr_locale, plural_locales, rbnf_locales, select

# (input tag, standardized tag with region, file code, variety): design section 6 and loader_probe.out.txt.
LOADER_ROWS = [
    ("en", "en-GB", "en", "en-GB"),
    ("en_us", "en-US", "en", "en-US"),
    ("EN-us", "en-US", "en", "en-US"),
    ("en-AU", "en-AU", "en", "en-GB"),
    ("en-IN", "en-IN", "en", "en-GB"),
    ("en-PR", "en-PR", "en", "en-US"),
    ("en-VI", "en-VI", "en", "en-US"),
    ("en-Latn-US", "en-US", "en", "en-US"),
    ("lb", "lb-LU", "lb", "lb-LU"),
    ("gsw", "gsw-CH", "gsw", "gsw-CH"),
    ("yue", "yue-CN", "yue", "yue-CN"),
    ("wuu", "wuu-CN", "wuu", "wuu-CN"),
    ("sco", "sco-GB", "sco", "sco-GB"),
    ("en-x-scouse", "en-GB-x-scouse", "en", "en-GB"),
]


@pytest.mark.parametrize("row", LOADER_ROWS, ids=[row[0] for row in LOADER_ROWS])
def test_loader_rows(row):
    tag, language, variety = select(row[0])
    assert (row[0], tag, language.code, variety.tag) == row


def test_the_package_requires_langcodes_through_linguatag():
    declared = [Requirement(r) for r in requires("text2spoken") if "extra ==" not in r]
    assert any(r.name == "linguatag" and "langcodes" in r.extras for r in declared)


@pytest.mark.parametrize("tag", ["not a tag", "", "x-private", "en--US", "12", "e", "en-US-", "pt PT"])
def test_a_tag_that_is_not_bcp47_raises(tag):
    with pytest.raises(InvalidLanguageTagError):
        normalize("1", tag)


@pytest.mark.parametrize("value", [None, 5, b"en"])
def test_lang_and_text_must_be_str(value):
    with pytest.raises(TypeError, match="lang"):
        normalize("1", value)
    with pytest.raises(TypeError, match="text"):
        normalize(value, "en")


def test_a_served_code_loads_the_file_that_serves_it(gendered):
    tag, language, _ = select("qab")
    assert language is gendered.LANGUAGE and tag.startswith("qab")


def test_cldr_locale_tries_the_tag_then_the_code_then_the_aliases(gendered):
    assert cldr_locale("pt-PT", rbnf_locales(), gendered.LANGUAGE) == "pt_PT"
    assert cldr_locale("pt-BR", plural_locales(), gendered.LANGUAGE) == "pt"
    assert cldr_locale("qaa", plural_locales(), gendered.LANGUAGE) == "pt"
    assert cldr_locale("qaa", {"qaa"}, gendered.LANGUAGE) == "qaa"
    assert cldr_locale("zh-Hant-TW", {"zh_Hant_TW", "zh_Hant", "zh"}, gendered.LANGUAGE) == "zh_Hant_TW"
    assert cldr_locale("zh-Hant-TW", {"zh_Hant", "zh"}, gendered.LANGUAGE) == "zh_Hant"
    assert cldr_locale("xx", {"yy"}, gendered.LANGUAGE) is None


def test_a_language_with_no_file_reads_cardinals_through_rbnf():
    # German writes a number below one million as one word (Duden, from memory, not fetched).
    assert normalize("Ich habe 21 Äpfel.", "de") == "Ich habe einundzwanzig Äpfel."
    assert supports("de").code == "de" and set(supports("de").forms) == {"lexicon", "cardinal"}


def test_a_language_with_no_file_and_no_rbnf_reads_only_the_lexicon():
    assert supports("tlh").forms == {"lexicon"}
    assert normalize("jIH 3", "tlh") == "jIH 3"
