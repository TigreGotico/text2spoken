"""The CLDR currency and symbol data, `MONEY` with CLDR currencies and the `SYMBOL` form (design section 4.7).

Each expected value is read off the clause and the raw CLDR 49 JSON, not off a run of the code."""
import hashlib
import importlib.util
import json
import re
from importlib.resources import files
from pathlib import Path

import pytest

from text2spoken import Form, NormalizationParams, normalize

TAGS = ("en-GB", "en-US", "pt-PT", "pt-BR")
ROOT = Path(__file__).resolve().parent.parent


def data(tag: str, part: str) -> dict:
    return json.loads((files("text2spoken") / "data" / "cldr" / f"{tag}.{part}.json").read_text(encoding="utf-8"))


def extractor():
    spec = importlib.util.spec_from_file_location("extract_cldr", ROOT / "scripts" / "extract_cldr.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Files:
    """A release held in memory, by path."""

    def __init__(self, blobs: dict[str, object]):
        self.blobs = {path: json.dumps(value).encode() if not isinstance(value, bytes) else value
                      for path, value in blobs.items()}
        self.hashes: dict[str, str] = {}
        self.root, self.base = None, ""

    def read(self, path: str) -> bytes | None:
        blob = self.blobs.get(path)
        if blob is not None:
            self.hashes[path] = hashlib.sha256(blob).hexdigest()
        return blob


@pytest.mark.parametrize("tag", TAGS)
def test_each_currency_file_records_the_pinned_release_and_its_inputs(tag):
    source = data(tag, "currencies")["source"]
    assert source["release"] == "49.0.0" and source["commit"] == "a4b67247b446fd51b475991017a2481911210c60"
    expected = {"LICENSE", "cldr-json/cldr-core/supplemental/parentLocales.json",
                *(f"cldr-json/cldr-numbers-full/main/{locale}/currencies.json" for locale in source["locales"])}
    assert set(source["files"]) == expected
    assert all(re.fullmatch("[0-9a-f]{64}", digest) for digest in source["files"].values())


@pytest.mark.parametrize("tag", TAGS)
def test_each_symbol_file_records_the_release_the_unicode_version_and_its_inputs(tag):
    source = data(tag, "symbols")["source"]
    assert source["release"] == "49.0.0" and source["unicode"] == "16.0.0"
    shared = {"LICENSE", "cldr-json/cldr-core/supplemental/parentLocales.json", "ucd/UnicodeData.txt",
              "ucd/emoji/emoji-data.txt"}
    annotations = {f"cldr-json/cldr-annotations-full/annotations/{locale}/annotations.json"
                   for locale in source["locales"]}
    derived = {f"cldr-json/cldr-annotations-derived-full/annotationsDerived/{locale}/annotations.json"
               for locale in source["locales"]}
    assert shared | annotations <= set(source["files"]) <= shared | annotations | derived


def test_a_symbol_that_two_currencies_share_reads_as_the_currency_whose_symbol_it_is():
    """CLDR 49 en gives USD the symbol `$`, and AUD, CAD and others the narrow symbol `$`. en-001, the parent of
    en-GB, gives USD the symbol `US$`, so in en-GB no currency holds `$` as its symbol."""
    assert "$" in data("en-US", "currencies")["currencies"]["USD"]["symbols"]
    assert {"AUD", "CAD", "USD"} <= set(data("en-GB", "currencies")["collisions"]["$"])
    owned = {s for c in data("en-GB", "currencies")["currencies"].values() for s in c["symbols"]}
    assert "$" not in owned and "US$" in data("en-GB", "currencies")["currencies"]["USD"]["symbols"]


def test_the_extractor_assigns_a_shared_symbol_by_the_symbol_field():
    """A narrow symbol that two currencies hold goes to the one whose `symbol` it is, and to none when no currency
    or two currencies hold it so."""
    module = extractor()
    currencies = {
        "AAA": {"displayName-count-one": "a", "displayName-count-other": "as", "symbol": "$", "symbol-alt-narrow": "$"},
        "BBB": {"displayName": "B", "symbol": "B$", "symbol-alt-narrow": "$"},
        "CCC": {"displayName": "C", "symbol-alt-narrow": "¢"},
        "DDD": {"displayName": "D", "symbol-alt-narrow": "¢"},
    }
    release = Files({"cldr-json/cldr-numbers-full/main/qq/currencies.json":
                     {"main": {"qq": {"numbers": {"currencies": currencies}}}}})
    found, collisions = module.extract_currencies("qq", {}, release, {})
    assert found["currencies"]["AAA"] == {"names": {"one": "a", "other": "as"}, "symbols": ["$"]}
    assert found["currencies"]["BBB"] == {"names": {"other": "B"}, "symbols": ["B$"]}
    assert collisions == {"¢": ["CCC", "DDD"]}


def test_the_extractor_keeps_symbols_of_text_presentation_and_child_names():
    """`©` (So) and `§` (Po, a listed mark) read; `😀` has emoji presentation, `½` is No and `&` is ASCII. The child
    locale names `©` and inherits `§` from its parent."""
    module = extractor()
    ucd = Files({"UnicodeData.txt": "\n".join(f"{ord(c):04X};X;{gc};" for c, gc in
                                              (("&", "Po"), ("§", "Po"), ("©", "So"), ("½", "No"),
                                               ("😀", "So"))).encode(),
                 "emoji/emoji-data.txt": b"1F600 ; Emoji_Presentation # grinning face\n"})
    categories, presentation = module.unicode_properties(ucd)
    names = {c: {"tts": [f"parent {c}"]} for c in "&§©½😀"}
    release = Files({
        "cldr-json/cldr-annotations-full/annotations/qq/annotations.json":
            {"annotations": {"annotations": names}},
        "cldr-json/cldr-annotations-full/annotations/qq-XX/annotations.json":
            {"annotations": {"annotations": {"©": {"tts": ["child ©"]}}}},
    })
    found = module.extract_symbols("qq-XX", {}, release, {}, categories, presentation)
    assert found["symbols"] == {"§": "parent §", "©": "child ©"}
    assert found["source"]["locales"] == ["qq-XX", "qq"]


@pytest.mark.parametrize(("tag", "char", "name"), [
    ("en-GB", "©", "copyright"), ("en-US", "→", "right-pointing arrow"), ("pt-PT", "©", "direitos de autor"),
    ("pt-BR", "©", "símbolo de copyright"), ("pt-PT", "‰", "por mil"), ("pt-PT", "§", "secção"),
    ("en-GB", "☺", "smiling face"),
])
def test_the_symbol_names_are_the_cldr_tts_names_of_the_parent_chain(tag, char, name):
    """CLDR 49 annotations: pt-PT names `©` and `§` itself, and gives no `tts` for `‰`, so it takes the pt name."""
    assert data(tag, "symbols")["symbols"][char] == name


@pytest.mark.parametrize("char", ["😀", "½", "²", "&", "µ", "–"])
def test_the_symbol_file_holds_no_emoji_of_emoji_presentation_no_number_and_no_ascii(char):
    assert char not in data("en-GB", "symbols")["symbols"]


@pytest.mark.parametrize(("tag", "text", "spoken"), [
    ("en-GB", "He ran a 10K race.", "He ran a 10K race."), ("en-GB", "Add 10 L of fuel.", "Add ten L of fuel."),
    ("en-US", "TOP 10 songs.", "TOP ten songs."), ("pt-PT", "Corri 10 K hoje.", "Corri dez K hoje."),
])
def test_a_currency_symbol_of_letters_reads_only_when_listed(tag, text, spoken):
    """CLDR 49 en gives `K` to MMK, `L` to HNL and the code `TOP` to the Tongan paʻanga. They hold no currency sign
    and `currency_symbols` does not list them, so the letters stay, and `10K` stays whole as on dev."""
    assert normalize(text, tag) == spoken


def test_two_decimals_read_as_a_decimal_when_the_currency_names_no_minor_unit():
    """CLDR names no minor unit, and en.py names none for INR."""
    assert normalize("The fee is ₹10.50.", "en-GB") == "The fee is ten point five zero Indian rupees."


@pytest.mark.parametrize(("tag", "text"), [
    ("en-GB", "It is 20° today."), ("en-GB", "Use a ÷ b here."), ("en-GB", "Pay in ₹ only."),
    ("pt-PT", "Pague em € agora."), ("en-GB", "The sign ‰ means per thousand."), ("en-US", "Add 3/4 ‰ now."),
    ("pt-PT", "Junte 3/4 ‰ já."),
])
def test_a_character_that_a_table_gives_to_another_form_stays_as_written(tag, text):
    """`°` is in the `symbols` table, `÷` is an operator of en.py, `₹` and `€` are currency signs that MONEY reads,
    and `‰` is the symbol of the CLDR 49 en and pt unit concentr-permille. CLDR names each of them, yet SYMBOL leaves
    them to their form, so `3/4 ‰` stays as written as `3/4 kg` does."""
    assert normalize(text, tag) == text


@pytest.mark.parametrize(("tag", "text", "number"), [
    ("pt-PT", "Ligue → 1.234,56", "1.234,56"), ("en-GB", "Call → 1,234.56", "1,234.56"),
])
def test_a_symbol_that_reads_stands_between_a_phone_word_and_the_digits_as_a_word(tag, text, number):
    """A phone word names the digits right after it only with no word between them. The name of `→` is words, so
    the number reads on the first pass, as it does on the second."""
    once = normalize(text, tag)
    assert once == f"{text.split()[0]} {data(tag, 'symbols')['symbols']['→']} {normalize(number, tag)}"
    assert normalize(once, tag) == once


@pytest.mark.parametrize("text", ["©️ 2024", "☝🏽 up", "🏳‍🌈 flag", "Pay 🅰 now."])
def test_an_emoji_sequence_and_a_name_with_no_words_stay_as_written(text):
    """U+FE0F, a skin tone modifier or a zero width joiner makes the character part of an emoji sequence. CLDR 49
    en names `🅰` "A button (blood type)", which holds brackets."""
    assert normalize(text, "en-GB") == text.replace("2024", "two thousand and twenty-four")


@pytest.mark.parametrize(("text", "spoken"), [
    ("©2024", "copyright two thousand and twenty-four"), ("©®", "copyright registered"),
    ("a→b", "a right-pointing arrow b"), ("(©)", "(copyright)"),
])
def test_a_symbol_name_takes_a_space_where_it_touches_a_word_or_a_symbol(text, spoken):
    assert normalize(text, "en-GB") == spoken


def test_without_the_symbol_form_the_symbol_stays_also_in_an_address():
    params = NormalizationParams().without(Form.SYMBOL)
    assert normalize("© 2024 at a©b.com", "en-GB", params) == "© two thousand and twenty-four at a © bee dot com"
