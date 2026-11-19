"""Say-as `date` in a language with no `DATE` reading of its file (design section 17.5), over the language tags of
`test_say_as_languages`.

Dutch reads through `ovos_date_parser.spoken_date`, which the test calls directly. Every other language reads its
CLDR 49 `long` date pattern, or the pattern of `data/date_readings.json` where that file cites a source. The test
writes each pattern by hand as a template, with the November and February names of the CLDR file
`ca-gregorian.json`, and reads the numbers through ovos-number-parser or unicode_rbnf. Czech and Ukrainian decline
the ordinal of the day or the year, so their rows are the readings of the cited sources (`CITED`). No expected value
comes from text2spoken."""
import json
import re
import warnings
from importlib.resources import files

import pytest
from ovos_date_parser.spoken import spoken_date
from ovos_number_parser import pronounce_number, pronounce_ordinal
from unicode_rbnf import RbnfEngine

from text2spoken import NormalizationParams, ParameterNotHonouredWarning, SayAs, UnsupportedParameterError, normalize
from text2spoken.core.dates import date_readings, long_date

from tests.test_say_as_languages import TAGS


def rbnf(tag: str, number: int, rule_set: str) -> str:
    language = tag.split("-")[0]
    return RbnfEngine.for_language(language).format_number(number, ruleset_names=[rule_set]).text_by_ruleset[rule_set]


def words(text: str) -> str:
    """The words of a number, with no comma: the writers and RBNF write a comma between the parts of some numbers,
    which text2spoken does not read."""
    return " ".join(text.replace(",", " ").split())


def writer(tag: str):
    return lambda number: words(pronounce_number(number, tag))


def rule_set(tag: str, name: str):
    return lambda number: words(rbnf(tag, number, name))


DATES = {
    "ca-ES": ("{d} {MMMM} del {y}", "de novembre", "de febrer", writer("ca-ES")),
    "gl-ES": ("{d} de {MMMM} de {y}", "novembro", "febreiro", writer("gl-ES")),
    "pl-PL": ("{d.} {MMMM} {y}", "listopada", "lutego", writer("pl-PL")),
    "tr-TR": ("{d} {MMMM} {y}", "Kasım", "Şubat", writer("tr-TR")),
    "sv-SE": ("{d} {MMMM} {y}", "november", "februari", writer("sv-SE")),
    "da-DK": ("{d.} {MMMM} {y}", "november", "februar", rule_set("da-DK", "spellout-numbering")),
    "fi-FI": ("{d.} {MMMM} {y}", "marraskuuta", "helmikuuta", writer("fi-FI")),
    "hu-HU": ("{y} {MMMM} {d}", "november", "február", writer("hu-HU")),
    "ro-RO": ("{d} {MMMM} {y}", "noiembrie", "februarie", writer("ro-RO")),
    "zh-CN": ("{y}年{M}月{d}日", "十一月", "二月", rule_set("zh-CN", "spellout-cardinal")),
    "ja-JP": ("{y}年{M}月{d}日", "11月", "2月", rule_set("ja-JP", "spellout-cardinal")),
    "ko-KR": ("{y}년 {MMMM} {d}일", "11월", "2월", rule_set("ko-KR", "spellout-numbering")),
    "hi-IN": ("{d} {MMMM} {y}", "नवंबर", "फ़रवरी", rule_set("hi-IN", "spellout-cardinal")),
    "fa-IR": ("{d} {MMMM} {y}", "نوامبر", "فوریه", writer("fa-IR")),
    "he-IL": ("{d} ב{MMMM} {y}", "נובמבר", "פברואר", writer("he-IL")),
    "sw-KE": ("{d} {MMMM} {y}", "Novemba", "Februari", rule_set("sw-KE", "spellout-cardinal")),
    "oc-FR": ("{d} {MMMM} de {y}", "de novembre", "de febrièr", writer("oc-FR")),
    "vi-VN": ("{d} {MMMM}, {y}", "tháng 11", "tháng 2", rule_set("vi-VN", "spellout-cardinal")),
    "id-ID": ("{d} {MMMM} {y}", "November", "Februari", writer("id-ID")),
    "cy-GB": ("{d} {MMMM} {y}", "Tachwedd", "Chwefror", rule_set("cy-GB", "spellout-cardinal-masculine")),
    "ta-IN": ("{d} {MMMM}, {y}", "நவம்பர்", "பிப்ரவரி", rule_set("ta-IN", "spellout-cardinal")),
}
"""Each tag that reads the CLDR `long` date pattern: the pattern as a template, where `{d.}` is the ordinal day of
`d.`, the November and the February names, and the cardinal of the language, by which the file of the language reads
its numbers. Polish reads the day as the nominative ordinal (Adam Wolański, Poradnia Językowa PWN, "Odczytywanie
daty zapisanej cyfrowo": "Który dziś jest? podajemy liczebnik oznaczający dzień w formie mianownikowej"). Hungarian
reads `y. MMMM d.` with a cardinal year and day (e-nyelv.hu, "március 15.": "Akár tőszámnévként (március tizenöt)
[...] olvassuk ki"). Occitan reads `d MMMM 'de' y`, the draft pattern of CLDR main `oc.xml` and the order of glibc
`oc_FR` `date_fmt`."""

ORDINAL_DAYS = {
    "da-DK": lambda number: rbnf("da-DK", number, "spellout-ordinal-common"),
    "fi-FI": lambda number: pronounce_ordinal(number, "fi-FI"),
    "pl-PL": lambda number: pronounce_ordinal(number, "pl-PL"),
}
"""The ordinal of a day that the pattern writes `d.`, through the ordinal speller of the language."""

CITED = (
    ("cs-CZ", "2010-09-28", "dvacátého osmého září dva tisíce deset"),
    *(("cs-CZ", f"2026-{month:02}-{day:02}", f"{words} dva tisíce dvacet šest") for day, month, words in (
        (1, 1, "prvního ledna"), (14, 2, "čtrnáctého února"), (5, 3, "pátého března"),
        (23, 4, "dvacátého třetího dubna"), (8, 5, "osmého května"), (30, 6, "třicátého června"),
        (6, 7, "šestého července"), (31, 8, "třicátého prvního srpna"), (28, 9, "dvacátého osmého září"),
        (2, 10, "druhého října"), (17, 11, "sedmnáctého listopadu"), (24, 12, "dvacátého čtvrtého prosince"))),
    ("uk-UA", "1967-03-07", "сьоме березня тисяча дев'ятсот шістдесят сьомого року"),
    ("uk-UA", "1967-04-15", "п'ятнадцяте квітня тисяча дев'ятсот шістдесят сьомого року"),
    ("uk-UA", "1967-09-26", "двадцять шосте вересня тисяча дев'ятсот шістдесят сьомого року"),
    ("uk-UA", "1967-12-31", "тридцять перше грудня тисяча дев'ятсот шістдесят сьомого року"),
    ("uk-UA", "1991-08-24", "двадцять четверте серпня тисяча дев'ятсот дев'яносто першого року"),
)
"""Dates that decline the ordinal, with the reading of the source. Czech: Czech Online, "Čeština jako cizí jazyk pro
specifické účely", table "The date": "The ordinal numeral indicating the day and the name of the month are used in
the genitive singular masculine/neutral form", with the twelve days and months of the rows, and "28. 9. 2010 =
dvacátého osmého září dva tisíce deset"; the year of the other rows is the cardinal of the writer, as the source
reads it. Ukrainian: Ivanna Voitsekhovych, Ukrainian Lessons, "How to Write Dates in Ukrainian": the neuter ordinal
day "сьоме березня", "п’ятнадцяте квітня", "двадцять шосте вересня", "тридцять перше грудня", "Двадцять четверте
серпня 1991 року", and the year "тисяча дев’ятсот шістдесят сьомого року". The genitive "першого" of the last row is
the table of МійКлас, "Відмінювання та правопис порядкових числівників": "перший — першого". The writer spells the
apostrophe as U+0027."""

NO_DATE = frozenset({"is-IS", "yo-NG", "ha-NG", "tw", "bn-IN"})
"""Tags with no reading of a say-as date. `is` writes `d.`, an ordinal day, and has no ordinal. The other tags read
no numbers."""

FILES = frozenset({"en-US", "pt-PT", "de-DE", "fr-FR", "es-ES", "it-IT", "ru-RU", "eu-ES", "el-GR", "ar", "apc"})
"""Tags whose language file reads a date of its own; `apc` reads through the `ar` file."""

assert set(TAGS) == set(DATES) | {tag for tag, _, _ in CITED} | NO_DATE | FILES | {"nl-NL"}


def expected(tag: str, day: int, month: int, year: int) -> str:
    template, november, february, cardinal = DATES[tag]
    name = {11: november, 2: february}[month]
    month_name = "".join(cardinal(int(part)) if part.isdigit() else part
                         for part in re.split("([0-9]+)", name))
    ordinal = ORDINAL_DAYS.get(tag)
    return (template.replace("{d.}", ordinal(day) if ordinal else "").replace("{d}", cardinal(day))
            .replace("{MMMM}", month_name).replace("{M}", cardinal(month)).replace("{y}", cardinal(year)))


def say(text: str, tag: str, params: NormalizationParams | None = None, **fields) -> str:
    return normalize(text, tag, params, say_as=SayAs(interpret_as="date", **fields))


@pytest.mark.parametrize("tag", sorted(DATES))
@pytest.mark.parametrize("text,fields,day,month,year", [("2026-11-09", {}, 9, 11, 2026),
                                                         ("01/02/2000", {"format": "dmy"}, 1, 2, 2000),
                                                         ("02/01/2000", {"format": "mdy"}, 1, 2, 2000)])
def test_a_date_reads_the_cldr_long_pattern(tag, text, fields, day, month, year):
    """W3C Note, section 3.1: the date reads in the order of the format. The `long` pattern names the month, as a
    speaker does, and writes no day of the week, which the text does not hold."""
    spoken = say(text, tag, **fields)
    assert spoken == " ".join(expected(tag, day, month, year).split())
    assert normalize(spoken, tag) == spoken


@pytest.mark.parametrize("tag,text,spoken", CITED)
def test_a_date_reads_the_case_of_the_cited_source(tag, text, spoken):
    assert say(text, tag) == spoken
    assert normalize(spoken, tag) == spoken


@pytest.mark.parametrize("text,spoken", [("2023-06-30", "trzydziesty czerwca"), ("2026-11-09", "dziewiąty listopada")])
def test_a_polish_date_reads_the_day_in_the_nominative(text, spoken):
    """Adam Wolański, Poradnia Językowa PWN, "Odczytywanie daty zapisanej cyfrowo": "– Który dziś jest? – 30.06.2023 r.
    (= trzydziesty czerwca [...])". The second row is the issue's date, in the same form."""
    assert say(text, "pl-PL").startswith(spoken + " ")


@pytest.mark.parametrize("text,spoken", [("2026-03-15", "kétezer-huszonhat március tizenöt"),
                                         ("1999-08-01", "ezerkilencszázkilencvenkilenc augusztus egy")])
def test_a_hungarian_date_reads_the_year_and_the_day_as_cardinals(text, spoken):
    """e-nyelv.hu, "március 15.": "március tizenöt". English Wikipedia, "Date and time notation in Hungary", of
    "1999. augusztus 1.": "unless a suffix is added, they are said as cardinal numbers"."""
    assert say(text, "hu-HU") == spoken


def test_each_cited_reading_names_the_pattern_of_its_dates_file():
    """An entry of `date_readings.json` applies only while CLDR writes the pattern that it names, so a CLDR update
    that changes the pattern shows here."""
    for locale, reading in date_readings().items():
        stored = json.loads((files("text2spoken") / "data" / "cldr" / f"{locale}.dates.json").read_text("utf-8"))
        assert reading["written"] == stored["long"], locale
        assert long_date(locale) is not None, locale


@pytest.mark.parametrize("text,fields,day,month,year", [("2026-11-09", {}, 9, 11, 2026),
                                                         ("09-11-2026", {"format": "dmy"}, 9, 11, 2026),
                                                         ("01/02/2000", {"format": "dmy"}, 1, 2, 2000)])
def test_a_dutch_date_reads_through_the_date_parser(text, fields, day, month, year):
    assert say(text, "nl-NL", **fields) == spoken_date("nl-NL", day=day, month=month, year=year)


def test_a_dutch_date_with_no_markup_stays_as_written():
    assert normalize("Op 09-11-2026 begint het.", "nl-NL") == "Op 09-11-2026 begint het."


@pytest.mark.parametrize("tag", sorted(NO_DATE))
def test_a_language_with_no_date_reading_gives_the_plain_reading(tag):
    with pytest.warns(ParameterNotHonouredWarning, match="date"):
        assert say("2026-11-09", tag) == normalize("2026-11-09", tag)
    with pytest.raises(UnsupportedParameterError):
        say("2026-11-09", tag, NormalizationParams(strict=True))


def test_the_languages_with_no_date_reading_are_exactly_the_listed_ones():
    declining = set()
    for tag in TAGS:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            say("2026-11-09", tag)
        if any("reads no say-as" in str(w.message) for w in caught):
            declining.add(tag)
    assert declining == NO_DATE


@pytest.fixture
def readings(monkeypatch):
    """A copy of `date_readings.json` that a test may change, as a data edit would."""
    import text2spoken.core.dates as dates
    copy = json.loads(json.dumps(date_readings()))
    monkeypatch.setattr(dates, "date_readings", lambda: copy)
    long_date.cache_clear()
    yield copy
    long_date.cache_clear()


def test_an_ordinal_with_no_date_form_stays_as_written(readings, caplog):
    """Design section 10: a reading that cannot be made declines, leaves the written form and logs one WARNING."""
    readings["cs"]["day"]["endings"] = [["ý", "ého"]]
    with caplog.at_level("WARNING"):
        assert say("2026-11-03", "cs-CZ") == "2026-11-03"
    assert [r.levelname for r in caplog.records if "třetí" in r.getMessage()] == ["WARNING"]


def test_a_cardinal_entry_reads_the_day_as_a_cardinal(readings):
    readings["pl"]["day"] = {"reading": "cardinal"}
    assert say("2026-11-09", "pl-PL").startswith(f"{writer('pl-PL')(9)} listopada ")
