"""Language tags and the loader (design section 6). The loader needs `langcodes`, which the package requires
through `linguatag[langcodes]`."""
from decimal import Decimal
from importlib.metadata import requires

import pytest
from packaging.requirements import Requirement

from text2spoken import (Form, InvalidLanguageTagError, NormalizationParams, UnreadFormError, normalize,
                         supports)
from text2spoken.core.language import cldr_locale, language_file, plural_locales, rbnf_locales, select

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
    # Wiktionary, eenanzwanzeg (fetched): Luxembourgish "twenty-one".
    assert normalize("Ech hunn 21 Äppel.", "lb") == "Ech hunn eenanzwanzeg Äppel."
    assert supports("lb").code == "lb" and set(supports("lb").forms) == {"lexicon", "cardinal", "decimal"}


# README: "A language with no file reads cardinal numbers from the CLDR spell-out rules, and keeps all other forms
# as written." Each text holds one form other than a cardinal, so it stays whole.
WRITTEN_FORMS = [
    ("lb-LU", "Et kascht £5."), ("lb-LU", "Et kascht 5 €."), ("lb-LU", "Et kascht 5\u00a0€."),
    ("lb-LU", "Den 12/03/2024 um 7:30."), ("lb-LU", "Et kascht $5."), ("lb-LU", "Et kascht 50%."),
    ("lb-LU", "Et weit 5 kg."), ("lb-LU", "Et huet 25°."), ("lb-LU", "Mir fueren 50 km/h."), ("lb-LU", "den 3. Mee"),
    ("lb-LU", "Hie gouf 2. Sieger."), ("mt-MT", "Il-prezz: $5."), ("mt-MT", "Jiswa R$5."), ("gl-ES", "o 1.º de maio"),
    ("gl-ES", "a 2.ª vez"), ("tr-TR", "%50 indirim"),
]


@pytest.mark.parametrize(("tag", "text"), WRITTEN_FORMS)
def test_a_language_with_no_file_keeps_the_forms_it_cannot_read_as_written(tag, text, caplog):
    assert normalize(text, tag) == text
    assert normalize(text, tag, NormalizationParams().only(Form.CARDINAL)) == text
    assert "unread written form" in caplog.text
    with pytest.raises(UnreadFormError):
        normalize(text, tag, NormalizationParams(strict=True))


def test_a_language_with_no_file_reads_the_cardinals_next_to_a_kept_form():
    # Wiktionary, dräi (fetched): Luxembourgish "three".
    assert normalize("Den 3. Mee kaaft ech 3.", "lb-LU") == "Den 3. Mee kaaft ech dräi."
    # CLDR `digits-ordinal` writes 3.º in Portuguese, so a full stop and a space end a sentence.
    assert normalize("Tenho 3. Ele tem 2.", "pt-PT") == "Tenho três. Ele tem dois."


# A language with no file reads a minus through the owner of its number words (design section 6.1). Expected
# words: ovos-number-parser writes uk and bg, with the words of the English Wiktionary, Module:number list/data/uk
# (5 п'ять, 21 двадцять один) and /bg (3 три, 5 пет, 10 десет, 12 дванадесет); "мінус" and "минус" are the minus
# words of the uk.xml and bg.xml rules of CLDR too.
NO_FILE_MINUS = [
    ("uk-UA", "сьогодні -5 дуже", "сьогодні мінус п'ять дуже"),
    ("uk", "Було \u221221.", "Було мінус двадцять один."),
    ("bg", "Днес -5 градуса", "Днес минус пет градуса"),
    ("bg-BG", "Температура (\u22123)", "Температура (минус три)"),
]

# A minus stays as written where it may be no minus. A hyphen after a letter, between two numbers or before a
# percent sign is no sign at all, by the rule of `find_numbers` that en.py reads too. A minus after a number or a
# dash can mark a range or a code: the number before it stays as written too, so that a second pass reads the
# same. A number grouped with a space that is no group mark of the locale, as in `-1 000`, stays as written whole.
# A minus next to a currency symbol leaves the money form, which a language with no file keeps as written. RBNF has
# no word for minus zero, and zu.xml has no -x rule. Each number that reads takes its word from ovos-number-parser:
# 5 п'ять, as the English Wiktionary writes.
NO_FILE_KEPT_MINUS = [
    ("uk-UA", "з 5-10 градусів", "з 5-10 градусів"),
    ("uk-UA", "код A-5", "код A-п'ять"),
    ("uk-UA", "знижка -5%", "знижка -5%"),
    ("uk-UA", "температура -0 градусів", "температура -0 градусів"),
    ("uk-UA", "від 5 -10 градусів", "від 5 -10 градусів"),
    ("uk-UA", "розділи 5--10", "розділи п'ять--10"),
    ("uk-UA", "тел. 333 -1234567", "тел. 333 -1234567"),
    ("uk-UA", "температура -1 000 градусів", "температура -1 000 градусів"),
    ("bg-BG", "Температура -1 000 градуса", "Температура -1 000 градуса"),
    ("bg-BG", "Разлика -12\u202f000 кг", "Разлика -12\u202f000 кг"),
    ("zu", "Izinga -5 namuhla.", "Izinga -5 namuhla."),
]

# A line break or a tab groups no digits: the minus at the end of a line reads, and so does the number of the next
# line. A minus at the start of a line reads, as in a language file. The no-break space is the group mark of uk in
# CLDR 49 (numbers.json, symbols-numberSystem-latn), so `-10\u00a0000` is one number. Words of the English
# Wiktionary, Module:number list/data/bg (5 пет, 3 три, 10 десет, 12 дванадесет), /uk (5 п'ять, 3 три, 10 десять,
# 10000 десять тисяч) and /pl (5 pięć, 3 trzy).
NO_FILE_LINE_BREAKS = [
    ("uk-UA", "Оцінка: -5\n10 студентів прийшли", "Оцінка: мінус п'ять\nдесять студентів прийшли"),
    ("uk-UA", "сьогодні -5\n3 яблука", "сьогодні мінус п'ять\nтри яблука"),
    ("uk-UA", "сьогодні -5\t10", "сьогодні мінус п'ять\tдесять"),
    ("pl-PL", "dziś -5\n3 jabłka", "dziś minus pięć\ntrzy jabłka"),
    ("bg-BG", "Оценка: -5\n10 души", "Оценка: минус пет\nдесет души"),
    ("bg-BG", "днес -5\n\n3 ябълки", "днес минус пет\n\nтри ябълки"),
    ("bg-BG", "-5\n\n12 души", "минус пет\n\nдванадесет души"),
    ("uk-UA", "-3 яблука", "мінус три яблука"),
    ("uk-UA", "Список:\n  -3 яблука", "Список:\n  мінус три яблука"),
    ("uk-UA", "борг -10\u00a0000 гривень", "борг мінус десять тисяч гривень"),
]

NO_FILE_KEPT_MONEY = [(tag, text, text) for tag, texts in (
    ("uk-UA", ("Баланс: -50 €", "Баланс: € -50", "Баланс: -1 000 €")),
    ("bg-BG", ("Баланс: -50 €", "Баланс: € -50", "Баланс: -1 000 €")),
    ("he-IL", ("יתרה: -50 ₪", "יתרה: ₪ -50")),
    ("ja-JP", ("残高: -50 €", "残高: € -50")),
    ("pl-PL", ("Saldo: -50 €", "Saldo: € -50")),
) for text in texts]


@pytest.mark.parametrize(("tag", "text", "expected"),
                         NO_FILE_MINUS + NO_FILE_KEPT_MINUS + NO_FILE_LINE_BREAKS + NO_FILE_KEPT_MONEY)
def test_a_language_with_no_file_reads_the_minus_of_rbnf(tag, text, expected):
    assert normalize(text, tag) == expected
    assert normalize(expected, tag) == expected


def _rbnf_words(locale: str, rule_set: str, number: str) -> str:
    """unicode_rbnf called directly, with the rule set that holds the rule, as words separated by single spaces."""
    from unicode_rbnf import RbnfEngine

    text = RbnfEngine.for_language(locale).format_number(Decimal(number), ruleset_names=[rule_set]).text
    return " ".join(text.replace(",", " ").split())


# Languages with no file that read through RBNF: (tag, RBNF locale, the rule set of the -x and x.x rules, the decimal
# mark of the locale). The rule set is `spellout-cardinal`, or the rule set that its 0 rule names, as in km and da.
# The decimal mark is `decimal` of symbols-numberSystem-latn in CLDR 49 numbers.json. da has a parser module, and
# RBNF_HELD keeps it on RBNF, decimals too.
NO_FILE_RBNF_DECIMALS = [
    ("hi-IN", "hi", "spellout-cardinal", "."),
    ("th-TH", "th", "spellout-cardinal", "."),
    ("sw-TZ", "sw", "spellout-cardinal", "."),
    ("vi-VN", "vi", "spellout-cardinal", ","),
    ("ja-JP", "ja", "spellout-cardinal", "."),
    ("km-KH", "km", "spellout-numbering", "."),
    ("hy-AM", "hy", "spellout-cardinal", ","),
    ("ka-GE", "ka", "spellout-cardinal", ","),
    ("ta-IN", "ta", "spellout-cardinal", "."),
    ("my-MM", "my", "spellout-cardinal", "."),
    ("mt-MT", "mt", "spellout-cardinal-masculine", "."),
    ("lt-LT", "lt", "spellout-cardinal-masculine", ","),
    ("am-ET", "am", "spellout-cardinal", "."),
    ("af-ZA", "af", "spellout-cardinal", ","),
    ("da-DK", "da", "spellout-cardinal-neuter", ","),
]


@pytest.mark.parametrize(("tag", "locale", "rule_set", "mark"), NO_FILE_RBNF_DECIMALS)
def test_a_language_with_no_file_reads_a_minus_and_a_decimal_through_rbnf(tag, locale, rule_set, mark):
    """A minus at the start of the text and a decimal in the mark of the locale read through the `-x` and `x.x`
    rules of RBNF (design section 6.1)."""
    for written, number in (("-5", "-5"), (f"3{mark}5", "3.5"), (f"-3{mark}5", "-3.5"),
                            (f"x -12{mark}05 y", "-12.05")):
        expected = _rbnf_words(locale, rule_set, number)
        if written.startswith("x "):
            expected = f"x {expected} y"
        assert normalize(written, tag) == expected
        assert normalize(expected, tag) == expected


# Hand readings of the CLDR XML rules of unicode-rbnf 2.5.0. hi.xml spellout-cardinal: `-x: ऋण →→;`,
# `x.x: ←← दशमलव →→;`, 3 तीन, 5 पाँच. sw.xml: `-x: kasoro →→;`, `x.x: ←← nukta →→;`, 3 tatu, 5 tano. th.xml:
# `-x: ลบ→→;` and `x.x: ←←จุด→→→;` with a zero-width space around each word, 3 สาม, 5 ห้า.
NO_FILE_RBNF_BY_HAND = [
    ("hi", "-5", "ऋण पाँच"),
    ("hi", "3.5", "तीन दशमलव पाँच"),
    ("hi", "-3.5", "ऋण तीन दशमलव पाँच"),
    ("hi", "३.५", "तीन दशमलव पाँच"),
    ("sw", "-5", "kasoro tano"),
    ("sw", "3.5", "tatu nukta tano"),
    ("sw", "-3.5", "kasoro tatu nukta tano"),
    ("th", "-5", "ลบ\u200bห้า"),
    ("th", "3.5", "สาม\u200bจุด\u200bห้า"),
]


@pytest.mark.parametrize(("tag", "text", "expected"), NO_FILE_RBNF_BY_HAND)
def test_a_language_with_no_file_reads_the_rbnf_rules_as_the_xml_writes_them(tag, text, expected):
    assert normalize(text, tag) == expected


# Languages with no file that ovos-number-parser writes, with the decimal mark of CLDR 49: (tag, mark).
NO_FILE_PARSER_DECIMALS = [("nb-NO", ","), ("fa-IR", "."), ("tr-TR", ","), ("pl-PL", ","), ("he-IL", "."),
                           ("sv-SE", ","), ("fy-NL", ",")]


@pytest.mark.parametrize(("tag", "mark"), NO_FILE_PARSER_DECIMALS)
def test_a_language_with_no_file_reads_a_minus_and_a_decimal_through_the_parser(tag, mark):
    """The parser owns the number words of these languages (design section 6.1), so the expected words are its own
    reading of the number, called directly."""
    from ovos_number_parser import pronounce_number

    assert normalize("-5", tag) == " ".join(pronounce_number(-5, tag).split())
    assert normalize(f"3{mark}5", tag) == " ".join(pronounce_number(3.5, tag, places=1).split())
    assert normalize(f"-3{mark}5", tag) == " ".join(pronounce_number(-3.5, tag, places=1).split())


def test_a_held_language_reads_decimals_through_rbnf():
    from text2spoken.core.language import select
    from text2spoken.core.spellers import RBNF_HELD, RbnfSpeller

    assert RBNF_HELD == {"da", "sk"}
    for code in RBNF_HELD:
        spellers = select(code)[1].spellers
        assert isinstance(spellers[Form.CARDINAL], RbnfSpeller) and isinstance(spellers[Form.DECIMAL], RbnfSpeller)


# A say-as `cardinal` reads a decimal in the CLDR mark of the locale, as a text with no say-as does. The mark of sw
# is the full stop, so `3,5` stays as written in sw-TZ.
SAY_AS_DECIMALS = [("da-DK", "3,5"), ("sv-SE", "3,5"), ("nb-NO", "3,5"), ("af-ZA", "3,5"),
                   ("sw-TZ", "3.5"), ("fy-NL", "3,5")]


@pytest.mark.parametrize(("tag", "text"), SAY_AS_DECIMALS)
def test_a_say_as_cardinal_reads_a_decimal_of_a_language_with_no_file(tag, text):
    from text2spoken.core.say_as import SayAs

    expected = normalize(text, tag)
    assert expected != text
    assert normalize(text, tag, say_as=SayAs(interpret_as="cardinal")) == expected


# The marks of each locale come from CLDR 49 numbers.json. hi writes 3,500 (group `,`), nb 3,5 (decimal `,`, group
# no-break space), tr 1.234,5 (decimal `,`, group `.`), and sw-CD 3,5 where sw writes 3.5. A number with one full
# stop or comma and three digits after it, which the CLDR root locale (1,234.5) reads in the other role, stays as
# written: `1.234` in tr and `3,500` in nb. A full stop where the locale has no such mark splits the number, so
# `3.5` stays as written in nb.
NO_FILE_MARKS = [
    ("hi-IN", "3,500", _rbnf_words("hi", "spellout-cardinal", "3500")),
    ("hi-IN", "1,234.5", _rbnf_words("hi", "spellout-cardinal", "1234.5")),
    ("sw-TZ", "3,500", _rbnf_words("sw", "spellout-cardinal", "3500")),
    ("sw-CD", "3,5", _rbnf_words("sw", "spellout-cardinal", "3.5")),
    ("sw-CD", "3,500", "3,500"),
    ("vi-VN", "1.234.567", _rbnf_words("vi", "spellout-cardinal", "1234567")),
    ("vi-VN", "1.234", "1.234"),
    ("nb-NO", "3,500", "3,500"),
    ("nb-NO", "3.5", "3.5"),
    ("tr-TR", "1.234", "1.234"),
    ("hi-IN", "3.0", "3.0"),
    ("nb-NO", "3,0", "3,0"),
    ("hi-IN", "03.5", "03.5"),
    ("hi-IN", "+3.5", "+3.5"),
    ("hi-IN", "3.5.1", "3.5.1"),
    ("hi-IN", "5 -3.5", "5 -3.5"),
]


@pytest.mark.parametrize(("tag", "text", "expected"), NO_FILE_MARKS)
def test_a_language_with_no_file_reads_the_marks_of_its_locale(tag, text, expected):
    assert normalize(text, tag) == expected
    assert normalize(expected, tag) == expected


NO_MINUS_RULE = ("ko", "zu")
"""The RBNF locales whose cardinal rule set has no `-x` rule, in itself or in the rule set that its 0 rule names."""
NO_DECIMAL_RULE = ("zu",)
"""The RBNF locales whose cardinal rule set has no `x.x` rule, in itself or in the rule set that its 0 rule names."""
NO_CLDR_MARKS = ("an", "mwl")
"""The languages with no file that ovos-number-parser writes and CLDR 49 numbers.json has no locale for."""
NO_PARSER_MINUS = ("kab",)
"""The languages with no file whose ovos-number-parser module writes no minus word for -1."""
NO_PARSER_DECIMAL = ("kab",)
"""The languages with no file whose ovos-number-parser module raises for 1.5."""


def test_the_languages_without_the_rules_are_listed():
    from ovos_number_parser import pronounce_number
    from unicode_rbnf import RbnfEngine
    from unicode_rbnf.engine import RbnfSpecialRule, ReplaceRulePart

    from text2spoken.core.language import cldr_number_marks
    from text2spoken.core.parsers import number_writer_languages
    from text2spoken.core.spellers import RBNF_HELD

    def holds(names, name, rule):
        while name is not None:
            if rule in names[name].special_rules:
                return True
            zero = names[name].numeric_rules.get(0)
            name = zero.parts[0].ruleset_name if zero and isinstance(zero.parts[0], ReplaceRulePart) else None
        return False

    def raises(number, code):
        try:
            pronounce_number(number, code, places=1)
        except (ValueError, NotImplementedError):
            return True
        return False

    missing = {RbnfSpecialRule.NEGATIVE_NUMBER: set(), RbnfSpecialRule.IMPROPER_FRACTION: set()}
    for locale in rbnf_locales():
        names = RbnfEngine.for_language(locale).rulesets
        cardinal = next(n for n in ("spellout-cardinal", "spellout-cardinal-masculine", "spellout-numbering")
                        if n in names)
        for rule, locales in missing.items():
            if not holds(names, cardinal, rule):
                locales.add(locale)
    parser = sorted(code for code in number_writer_languages() if code not in RBNF_HELD and not language_file(code))
    assert sorted(missing[RbnfSpecialRule.NEGATIVE_NUMBER]) == list(NO_MINUS_RULE)
    assert sorted(missing[RbnfSpecialRule.IMPROPER_FRACTION]) == list(NO_DECIMAL_RULE)
    assert [code for code in parser if code not in cldr_number_marks()] == list(NO_CLDR_MARKS)
    assert [code for code in parser if raises(-1, code)] == list(NO_PARSER_MINUS)
    assert [code for code in parser if raises(1.5, code)] == list(NO_PARSER_DECIMAL)


@pytest.mark.parametrize("code", NO_MINUS_RULE + NO_PARSER_MINUS)
def test_a_language_with_no_minus_word_keeps_the_minus(code):
    for text in ("-5", "x -5 y", "-3.5", "-3,5"):
        assert normalize(text, code) == text


@pytest.mark.parametrize("code", NO_DECIMAL_RULE + NO_CLDR_MARKS + NO_PARSER_DECIMAL)
def test_a_language_with_no_decimal_rule_or_marks_keeps_the_decimal(code):
    for text in ("3.5", "3,5", "-3.5", "-3,5"):
        assert normalize(text, code) == text


# A language with no file whose number words ovos-number-parser writes with a module of its own reads them through
# the parser, and RBNF reads every other language (design section 6.1). Expected words: English Wiktionary,
# Module:number list/data/nb (3 tre), /az (7 yeddi, 60 altmış, 100 yüz) and /gl (0 cero); Galician "tres" from the
# Wiktionary entry tres.
# Slovene reads through the parser, though the parser writes 2000 as "dve tisoč" where /sl writes "dva tisoč": RBNF
# writes each number from 21 to 99 unit last, "štirideset dva", where /sl writes 7 sedem and 42 dvainštirideset.
NO_FILE_PARSER = [
    ("nb-NO", "Jeg har 3 katter", "Jeg har tre katter"),
    ("gl-ES", "O Dr. Pérez ten 3 pacientes.", "O Dr. Pérez ten tres pacientes."),
    ("gl-ES", "Hai 0 erros", "Hai cero erros"),
    ("az-AZ", "bu gün 7 gün 60 il 100", "bu gün yeddi gün altmış il yüz"),
    ("sl-SI", "danes 7 je 42 zelo", "danes sedem je dvainštirideset zelo"),
]

# Lao reads through RBNF, and the core table rbnf_corrections.json gives the Lao words where the CLDR rules of lo
# write Thai ones. Expected words: English Wiktionary, Module:number list/data/lo: 7 ເຈັດ, 4 ສີ່, 10 ສິບ, 2 ສອງ, 1
# ໜຶ່ງ, 3 ສາມ, 5 ຫ້າ, 100 ຮ້ອຍ, 1000 ພັນ; SEAlang Lao dictionary, ລົບ: "preposition minus". RBNF writes a zero-width space
# between the parts of a number.
NO_FILE_LAO = [
    ("lo", "ມື້ນີ້ 7 ອາກາດ 42 ດີຫຼາຍ 1234",
     "ມື້ນີ້ ເຈັດ ອາກາດ ສີ່\u200bສິບ\u200bສອງ ດີຫຼາຍ ໜຶ່ງ\u200bພັນ\u200bສອງ\u200bຮ້ອຍ\u200bສາມ\u200bສິບ\u200bສີ່"),
    ("lo-LA", "ມື້ນີ້ 7 ອາກາດ 42 ດີຫຼາຍ 1234",
     "ມື້ນີ້ ເຈັດ ອາກາດ ສີ່\u200bສິບ\u200bສອງ ດີຫຼາຍ ໜຶ່ງ\u200bພັນ\u200bສອງ\u200bຮ້ອຍ\u200bສາມ\u200bສິບ\u200bສີ່"),
    ("lo-LA", "ມື້ນີ້ -5 ອາກາດ", "ມື້ນີ້ ລົບ\u200bຫ້າ ອາກາດ"),
]


@pytest.mark.parametrize(("tag", "text", "expected"), NO_FILE_PARSER + NO_FILE_LAO)
def test_a_language_with_no_file_reads_each_number_word_from_its_one_owner(tag, text, expected):
    assert normalize(text, tag) == expected
    assert normalize(expected, tag) == expected


@pytest.mark.parametrize("tag", ["lo", "lo-LA"])
def test_a_lao_number_holds_no_thai_letter(tag):
    """The Thai block is U+0E00 to U+0E7F, and Lao is U+0E80 to U+0EFF (The Unicode Standard, Thai and Lao blocks)."""
    spoken = normalize("0 7 42 100 1234 21000 150000 1000000 -5", tag)
    assert not [char for char in spoken if "\u0e00" <= char <= "\u0e7f"], spoken


def test_a_language_that_rbnf_holds_reads_through_rbnf():
    """RBNF_HELD holds da and sk. Danish shows it: the parser drops the "og" of "tusind og en", which the title of
    the Danish Wikipedia page "Tusind og en Nat" writes. RBNF da, spellout-cardinal: 1001 "tusind og et"."""
    assert normalize("år 1001", "da-DK") == "år tusind og et"


def test_a_language_with_no_file_and_no_rbnf_reads_only_the_lexicon():
    assert supports("tlh").forms == {"lexicon"}
    assert normalize("jIH 3", "tlh") == "jIH 3"
