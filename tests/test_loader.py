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
    # Wiktionary, eenanzwanzeg (fetched): Luxembourgish "twenty-one".
    assert normalize("Ech hunn 21 Äppel.", "lb") == "Ech hunn eenanzwanzeg Äppel."
    assert supports("lb").code == "lb" and set(supports("lb").forms) == {"lexicon", "cardinal"}


# README: "A language with no file reads cardinal numbers from the CLDR spell-out rules, and keeps all other forms
# as written." Each text holds one form other than a cardinal, so it stays whole.
WRITTEN_FORMS = [
    ("it-IT", "Ha pagato £5."), ("it-IT", "Ha pagato 5 €."), ("it-IT", "Ha pagato 5\u00a0€."), ("it-IT", "50%"),
    ("it-IT", "È il 25 % in meno."), ("lb-LU", "Et kascht $5."), ("lb-LU", "Et kascht 50%."),
    ("lb-LU", "Et weit 5 kg."), ("lb-LU", "Et huet 25°."), ("lb-LU", "Mir fueren 50 km/h."), ("lb-LU", "den 3. Mee"),
    ("lb-LU", "Hie gouf 2. Sieger."), ("mt-MT", "Il-prezz: $5."), ("mt-MT", "Jiswa R$5."), ("gl-ES", "o 1.º de maio"),
    ("gl-ES", "a 2.ª vez"), ("it-IT", "Costa 5 € al giorno."), ("it-IT", "Il 12/03/2024 alle 7:30."),
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
    # Wiktionary, tre: Italian "three".
    assert normalize("Ha pagato £5 e 5 € per 3 mele.", "it-IT") == "Ha pagato £5 e 5 € per tre mele."
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
# percent sign is no sign at all, by the rule of `find_numbers` that en.py reads too. A minus at the start of a
# line can mark a list item, and a minus after a number or a dash can mark a range or a code: the number before
# it stays as written too, so that a second pass reads the same. A number grouped with a space, as in `-1 000`,
# stays as written whole, with each kind of space that groups digits. A minus next to a currency symbol leaves the money
# form, which a language with no file keeps as written. RBNF has no word for minus zero, and zu.xml has no -x
# rule. Each number that reads takes its word from ovos-number-parser: 5 п'ять, as the English Wiktionary writes.
NO_FILE_KEPT_MINUS = [
    ("uk-UA", "з 5-10 градусів", "з 5-10 градусів"),
    ("uk-UA", "код A-5", "код A-п'ять"),
    ("uk-UA", "знижка -5%", "знижка -5%"),
    ("uk-UA", "температура -0 градусів", "температура -0 градусів"),
    ("uk-UA", "від 5 -10 градусів", "від 5 -10 градусів"),
    ("uk-UA", "розділи 5--10", "розділи п'ять--10"),
    ("uk-UA", "тел. 333 -1234567", "тел. 333 -1234567"),
    ("uk-UA", "-3 яблука", "-3 яблука"),
    ("uk-UA", "Список:\n  -3 яблука", "Список:\n  -3 яблука"),
    ("uk-UA", "температура -1 000 градусів", "температура -1 000 градусів"),
    ("uk-UA", "борг -10\u00a0000 гривень", "борг -10\u00a0000 гривень"),
    ("bg-BG", "Температура -1 000 градуса", "Температура -1 000 градуса"),
    ("bg-BG", "Разлика -12\u202f000 кг", "Разлика -12\u202f000 кг"),
    ("zu", "Izinga -5 namuhla.", "Izinga -5 namuhla."),
]

# A line break or a tab groups no digits: the minus at the end of a line reads, and so does the number of the next
# line. A minus at the start of a line stays as written. Words of the English Wiktionary, Module:number list/data/bg
# (5 пет, 3 три, 10 десет, 12 дванадесет), /uk (5 п'ять, 3 три, 10 десять) and /pl (5 pięć, 3 trzy).
NO_FILE_LINE_BREAKS = [
    ("uk-UA", "Оцінка: -5\n10 студентів прийшли", "Оцінка: мінус п'ять\nдесять студентів прийшли"),
    ("uk-UA", "сьогодні -5\n3 яблука", "сьогодні мінус п'ять\nтри яблука"),
    ("uk-UA", "сьогодні -5\t10", "сьогодні мінус п'ять\tдесять"),
    ("pl-PL", "dziś -5\n3 jabłka", "dziś minus pięć\ntrzy jabłka"),
    ("bg-BG", "Оценка: -5\n10 души", "Оценка: минус пет\nдесет души"),
    ("bg-BG", "днес -5\n\n3 ябълки", "днес минус пет\n\nтри ябълки"),
    ("bg-BG", "-5\n\n12 души", "-5\n\nдванадесет души"),
]

NO_FILE_KEPT_MONEY = [(tag, text, text) for tag, texts in (
    ("uk-UA", ("Баланс: -50 €", "Баланс: € -50", "Баланс: -1 000 €")),
    ("bg-BG", ("Баланс: -50 €", "Баланс: € -50", "Баланс: -1 000 €")),
    ("he-IL", ("יתרה: -50 ₪", "יתרה: ₪ -50")),
    ("ja-JP", ("残高: -50 €", "残高: € -50")),
    ("ca-ES", ("Saldo: -50 €", "Saldo: € -50")),
    ("pl-PL", ("Saldo: -50 €", "Saldo: € -50")),
) for text in texts]


@pytest.mark.parametrize(("tag", "text", "expected"),
                         NO_FILE_MINUS + NO_FILE_KEPT_MINUS + NO_FILE_LINE_BREAKS + NO_FILE_KEPT_MONEY)
def test_a_language_with_no_file_reads_the_minus_of_rbnf(tag, text, expected):
    assert normalize(text, tag) == expected
    assert normalize(expected, tag) == expected


# A language with no file whose number words ovos-number-parser writes with a module of its own reads them through
# the parser, and RBNF reads every other language (design section 6.1). Expected words: English Wiktionary,
# Module:number list/data/nb (3 tre), /az (7 yeddi, 60 altmış, 100 yüz) and /gl (0 cero); Galician "tres" from the
# Wiktionary entry tres; Catalan "dos-cents" from the Wiktionary entry dos-cents, where RBNF writes "dos-cent".
NO_FILE_PARSER = [
    ("nb-NO", "Jeg har 3 katter", "Jeg har tre katter"),
    ("gl-ES", "O Dr. Pérez ten 3 pacientes.", "O Dr. Pérez ten tres pacientes."),
    ("gl-ES", "Hai 0 erros", "Hai cero erros"),
    ("az-AZ", "bu gün 7 gün 60 il 100", "bu gün yeddi gün altmış il yüz"),
    ("ca-ES", "avui 201 fa", "avui dos-cents un fa"),
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
    """Danish is in RBNF_HELD: the parser drops the "og" of "tusind og en", which the title of the Danish Wikipedia
    page "Tusind og en Nat" writes. RBNF da, spellout-cardinal: 1001 "tusind og et"."""
    assert normalize("år 1001", "da-DK") == "år tusind og et"


def test_a_language_with_no_file_and_no_rbnf_reads_only_the_lexicon():
    assert supports("tlh").forms == {"lexicon"}
    assert normalize("jIH 3", "tlh") == "jIH 3"
