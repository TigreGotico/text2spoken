"""French cross-checks against independent sources: num2words, ovos-number-parser and CLDR through Babel.

Each test skips when its source is not installed. Where a source has a known defect, the test names it and
corrects it with the grammar rule (Académie française, "Les nombres") before it compares."""

import datetime as dt
import logging
import re

import pytest

from text2spoken import normalize
from text2spoken.lang.fr import MONTHS, UNITS, DATA

NUMBERS = (
    list(range(0, 3001))
    + [10**k for k in range(4, 13)]
    + [2 * 10**k for k in range(4, 13)]
    + [80 * 10**k for k in range(3, 11)]
    + [200 * 10**k for k in range(3, 11)]
    + [81000, 280000, 380000000]
)
UNIT_WORDS = "un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize"


def fix_num2words(words: str) -> str:
    """The defects of num2words fr_BE and fr_CH: a hyphen, not "et", after quatre-vingt, no "s" on cent before another
    numeral, no "s" on quatre-vingt at the end or before a million, and "un millions"."""
    words = re.sub(r"\bquatre-vingt et ", "quatre-vingt-", words)
    words = re.sub(
        r"\bcents (?=(%s|vingt|trente|quarante|cinquante|soixante|septante|huitante|nonante|quatre-vingt))"
        % UNIT_WORDS,
        "cent ",
        words,
    )
    words = re.sub(r"\bcents mille", "cent mille", words)
    words = re.sub(r"\bun (millions|milliards|billions)", lambda m: "un " + m.group(1)[:-1], words)
    words = re.sub(r"\bquatre-vingt$", "quatre-vingts", words)
    words = re.sub(r"\bquatre-vingt (?=(million|milliard|billion))", "quatre-vingts ", words)
    return re.sub(
        r"\b(deux|trois|quatre|cinq|six|sept|huit|neuf) cent (?=(million|milliard|billion))", r"\1 cents ", words
    )


@pytest.mark.parametrize("tag,lang", [("fr-FR", "fr"), ("fr-BE", "fr_BE"), ("fr-CH", "fr_CH")])
def test_cardinals_agree_with_num2words(tag, lang):
    num2words = pytest.importorskip("num2words").num2words
    for number in NUMBERS:
        assert normalize(str(number), tag) == fix_num2words(num2words(number, lang=lang)), number


@pytest.mark.parametrize("tag,lang", [("fr-FR", "fr"), ("fr-BE", "fr_BE"), ("fr-CH", "fr_CH")])
def test_ordinals_agree_with_num2words(tag, lang):
    num2words = pytest.importorskip("num2words").num2words
    for number in range(2, 2001):
        words = num2words(number, lang=lang, to="ordinal")
        words = re.sub(r"(quatre-vingt|cent)s(?=ième)", r"\1", words)
        words = re.sub(r"\bquatre-vingt et ", "quatre-vingt-", words)
        words = re.sub(r"\bcents? et ", "cent ", words)
        words = re.sub(
            r"\bcents (?=([a-zé-]+ième|%s|vingt|trente|quarante|cinquante|soixante|septante|huitante|nonante|"
            r"quatre-vingt))" % UNIT_WORDS,
            "cent ",
            words,
        )
        words = re.sub(r"\bmille et ", "mille ", words)
        assert normalize(f"{number}e", tag) == words, number


def test_cardinals_agree_with_ovos_number_parser():
    pronounce_number = pytest.importorskip("ovos_number_parser").pronounce_number
    for number in NUMBERS:
        assert normalize(str(number), "fr-FR") == pronounce_number(number, "fr-FR").replace("-et-", " et "), number


def test_month_names_agree_with_cldr():
    names = pytest.importorskip("babel.dates").get_month_names
    assert [names("wide", locale="fr")[i] for i in range(1, 13)] == MONTHS


# Not compared: kWh (CLDR writes "kilowatt-heure", the BIPM "kilowattheure"), mm² and t (not in Babel).
CLDR_UNITS = {
    "kg": "mass-kilogram",
    "g": "mass-gram",
    "mg": "mass-milligram",
    "km": "length-kilometer",
    "m": "length-meter",
    "cm": "length-centimeter",
    "mm": "length-millimeter",
    "dm": "length-decimeter",
    "km/h": "speed-kilometer-per-hour",
    "m/s": "speed-meter-per-second",
    "l": "volume-liter",
    "ml": "volume-milliliter",
    "cl": "volume-centiliter",
    "dl": "volume-deciliter",
    "m²": "area-square-meter",
    "km²": "area-square-kilometer",
    "m³": "volume-cubic-meter",
    "ha": "area-hectare",
    "h": "duration-hour",
    "min": "duration-minute",
    "s": "duration-second",
    "ms": "duration-millisecond",
    "°C": "temperature-celsius",
    "°F": "temperature-fahrenheit",
    "°": "angle-degree",
    "Hz": "frequency-hertz",
    "kHz": "frequency-kilohertz",
    "MHz": "frequency-megahertz",
    "GHz": "frequency-gigahertz",
    "kW": "power-kilowatt",
    "MW": "power-megawatt",
    "W": "power-watt",
    "hPa": "pressure-hectopascal",
    "kPa": "pressure-kilopascal",
    "kcal": "energy-kilocalorie",
    "ko": "digital-kilobyte",
    "Mo": "digital-megabyte",
    "Go": "digital-gigabyte",
    "To": "digital-terabyte",
    "µm": "length-micrometer",
    "nm": "length-nanometer",
    "µg": "mass-microgram",
    "cm²": "area-square-centimeter",
    "cm³": "volume-cubic-centimeter",
}


@pytest.mark.parametrize("symbol,unit", sorted(CLDR_UNITS.items()))
def test_unit_names_agree_with_cldr(symbol, unit):
    format_unit = pytest.importorskip("babel.units").format_unit
    ours = UNITS[symbol]
    for count, form in ((1, "one"), (2, "other"), (1.5, "one")):
        cldr = re.sub(r"^[\d,\s  ]+", "", format_unit(count, unit, locale="fr", length="long"))
        assert cldr == ours[form], (symbol, count)


@pytest.mark.parametrize(
    "code,one,other",
    [
        ("EUR", "euro", "euros"),
        ("CHF", "franc suisse", "francs suisses"),
        ("CAD", "dollar canadien", "dollars canadiens"),
    ],
)
def test_currency_names_agree_with_cldr(code, one, other):
    name = pytest.importorskip("babel.numbers").get_currency_name
    assert (name(code, count=1, locale="fr"), name(code, count=2, locale="fr")) == (one, other)
    currency = DATA["currencies"][code]
    assert (currency["one"], currency["other"]) == (one, other)


@pytest.mark.parametrize(
    "locale,tag",
    [
        ("fr_FR", "fr-FR"),
        ("fr_CA", "fr-CA"),
        ("fr_BE", "fr-BE"),
        ("fr_CH", "fr-CH"),
        ("fr_LU", "fr-LU"),
        ("fr_SN", "fr-SN"),
        ("fr_TN", "fr-TN"),
        ("fr_HT", "fr-HT"),
    ],
)
def test_the_formats_that_cldr_writes_for_each_region_read(locale, tag):
    babel = pytest.importorskip("babel")
    numbers, dates = pytest.importorskip("babel.numbers"), pytest.importorskip("babel.dates")
    assert normalize(numbers.format_decimal(1234567.5, locale=locale), tag) == (
        "un million deux cent trente-quatre mille cinq cent soixante-sept virgule cinq"
        if tag != "fr-CH"
        else "un million deux cent trente-quatre mille cinq cent soixante-sept virgule cinq"
    )
    assert normalize(f"Il y a {numbers.format_percent(0.5, locale=locale)}.", tag) == "Il y a cinquante pour cent."
    assert normalize(f"Cela coûte {numbers.format_currency(3.5, 'EUR', locale=locale)}.", tag) == (
        "Cela coûte trois euros cinquante."
    )
    short = dates.format_date(dt.date(2026, 11, 10), "short", locale=locale)
    if re.fullmatch(r"\d\d[/.-]\d\d[/.-]\d\d\d\d|\d{4}-\d\d-\d\d", short):
        assert normalize(short, tag) == "dix novembre deux mille vingt-six", short
    assert babel.__version__


def test_cldr_writes_quebec_times_as_14_h_30_and_others_as_14_colon_30():
    time = pytest.importorskip("babel.dates").format_time
    assert time(dt.time(14, 30), "short", locale="fr_CA") == "14 h 30"
    assert normalize("à " + time(dt.time(14, 30), "short", locale="fr_CA"), "fr-CA") == "à quatorze heures trente"
    assert normalize("à " + time(dt.time(14, 30), "short", locale="fr_FR"), "fr-FR") == "à quatorze heures trente"
    assert normalize("à " + time(dt.time(14, 30), "short", locale="fr_TN").replace(" ", " "), "fr-TN") == (
        "à deux heures trente de l'après-midi"
    )


@pytest.mark.parametrize("two_digit_year", ["10/11/26", "10.11.26"])
def test_a_date_with_a_two_digit_year_stays_as_written(two_digit_year, caplog):
    """CLDR writes fr_BE and fr_CH short dates with two digits for the year; the year is ambiguous, so it stays."""
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        assert normalize(f"Le {two_digit_year} ici.", "fr-BE") == f"Le {two_digit_year} ici."
