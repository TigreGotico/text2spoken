"""Language tags and the loader (design section 6). The loader needs `langcodes`, which the package requires
through `linguatag[langcodes]`."""
from importlib.metadata import requires

import pytest
from packaging.requirements import Requirement

from text2spoken import (Form, InvalidLanguageTagError, NormalizationParams, UnreadFormError, normalize,
                         supports)
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


# README: "A language with no file reads cardinal numbers from the CLDR spell-out rules, and keeps all other forms
# as written." Each text holds one form other than a cardinal, so it stays whole.
WRITTEN_FORMS = [
    ("it-IT", "Ha pagato £5."), ("it-IT", "Ha pagato 5 €."), ("it-IT", "Ha pagato 5\u00a0€."), ("it-IT", "50%"),
    ("it-IT", "È il 25 % in meno."), ("de-DE", "Es kostet $5."), ("de-DE", "Es kostet 50%."),
    ("de-DE", "Es wiegt 5 kg."), ("de-DE", "Es hat 25°."), ("de-DE", "Wir fahren 50 km/h."), ("de-DE", "am 3. Mai"),
    ("de-DE", "Er wurde 2. Sieger."), ("pt-PT", "Price: $5."), ("pt-PT", "Custa R$5."), ("es-ES", "el 1.º de mayo"),
    ("es-ES", "la 2.ª vez"), ("it-IT", "Costa 5 € al giorno."), ("it-IT", "Il 12/03/2024 alle 7:30."),
    ("tr-TR", "%50 indirim"),
]


@pytest.mark.parametrize(("tag", "text"), WRITTEN_FORMS)
def test_a_language_with_no_file_keeps_the_forms_it_cannot_read_as_written(tag, text, caplog):
    assert normalize(text, tag) == text
    assert normalize(text, tag, NormalizationParams().only(Form.CARDINAL)) == text
    assert "unread written form" in caplog.text
    with pytest.raises(UnreadFormError):
        normalize(text, tag, NormalizationParams(strict=True))


def test_a_language_with_no_file_reads_the_cardinals_next_to_a_kept_form():
    assert normalize("Ha pagato £5 e 5 € per 3 mele.", "it-IT") == "Ha pagato £5 e 5 € per tre mele."
    assert normalize("Am 3. Mai kaufte ich 3.", "de-DE") == "Am 3. Mai kaufte ich drei."
    # CLDR `digits-ordinal` writes 3.º in Portuguese, so a full stop and a space end a sentence.
    assert normalize("Tenho 3. Ele tem 2.", "pt-PT") == "Tenho três. Ele tem dois."


def test_a_language_with_no_file_and_no_rbnf_reads_only_the_lexicon():
    assert supports("tlh").forms == {"lexicon"}
    assert normalize("jIH 3", "tlh") == "jIH 3"
