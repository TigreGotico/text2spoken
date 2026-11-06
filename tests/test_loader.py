"""Language tags and the loader (design section 6), with and without the optional langcodes package."""
import json
import subprocess
import sys

import langcodes  # noqa: F401  the test extra installs it, so the in-process run is the install with langcodes
import pytest

from text2spoken import InvalidLanguageTagError, normalize, supports
from text2spoken.core.language import cldr_locale, plural_locales, rbnf_locales, select

# (input tag, standardized tag with region, file code, variety): design section 6 and loader_probe.out.txt.
LOADER_ROWS = [
    ("en", "en-GB", "en", "en-GB"),
    ("en_us", "en-US", "en", "en-US"),
    ("EN-us", "en-US", "en", "en-US"),
    ("en-AU", "en-AU", "en", "en-GB"),
    ("en-IN", "en-IN", "en", "en-GB"),
    ("lb", "lb-LU", "lb", "lb-LU"),
    ("gsw", "gsw-CH", "gsw", "gsw-CH"),
    ("yue", "yue-CN", "yue", "yue-CN"),
    ("wuu", "wuu-CN", "wuu", "wuu-CN"),
    ("sco", "sco-GB", "sco", "sco-GB"),
    ("en-x-scouse", "en-GB-x-scouse", "en", "en-GB"),
]

_PROBE = """
import json, sys
if sys.argv[1] == "without":
    sys.modules["langcodes"] = None
    try:
        import langcodes
        raise SystemExit("langcodes is still importable")
    except ImportError:
        pass
from text2spoken.core.language import select
rows = json.loads(sys.argv[2])
print(json.dumps([[tag, *(lambda t, l, v: [t, l.code, v.tag])(*select(tag))] for tag in rows]))
"""


def _run(install: str) -> list[list[str]]:
    tags = json.dumps([row[0] for row in LOADER_ROWS])
    out = subprocess.run([sys.executable, "-c", _PROBE, install, tags], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


@pytest.mark.parametrize("install", ["with", "without"])
def test_loader_rows_in_both_installs(install):
    assert _run(install) == [list(row) for row in LOADER_ROWS]


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
