"""Basque: euskara batua, the standard of Euskaltzaindia, for every Basque tag through eu-ES.

The rules come from the norms of Euskaltzaindia, the Basque academy (https://www.euskaltzaindia.eus/dok/arauak/):
Araua 7 (cardinals), Araua 196 (abbreviations), Araua 197 (symbols) and Araua 203, "Zenbakizko adierazpenak",
which holds the readings of cardinals, ordinals, fractions, decimals, percentages, times and dates. Section 5.4 of
the design page `text2spoken-design.md` names ovos-number-parser for the Basque cardinal: it reads the 50 cardinals
of the academy tables right. Ordinals, fractions and decimals follow the academy rules in this file, because
ovos-number-parser misreads `milioigarren` and five of the 17 fractions of the tables.

A Basque case ending joins the digits, as in `2024ko`, `25ean` and `15:00etan`, and a hyphen joins it to a symbol,
as in `1 €-etik` (Araua 197, section 6.4). `attach` joins the ending to the last spoken word by the rules of
Araua 203, section 12.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety
from text2spoken.core.numbers import SIGNS, Number
from text2spoken.core.recognizers import (SHARED, _affixes, _cluster_edge, _free_before, _period_after, _prefix,
                                          _sentence_period, _suffix, numbers_in, speak_cardinal, speak_lexicon)
from text2spoken.core.spans import Features, Span, SpanContext, clause_breaks, clause_window, context_words
from text2spoken.core.spellers import OvosNumberSpeller, _integer
from text2spoken.core.times import clock_fields, twelve_hour
from text2spoken.core.tokens import (Token, digit_script, fold_digits, is_bounded, is_letter, is_mark, is_word_char,
                                     next_visible)
from text2spoken.params import FrozenMap, Form, freeze

GAPS = ("", " ", "\u00a0")
"""The gaps between a number and its symbol: none, a space or a no-break space (Araua 197, section 6.3)."""

RANGE_MARKS = ("-", "–")
"""The marks that join two amounts as a range, as in `% 2-% 5` (Araua 203, section 7.1, page 32)."""

SPACE_GROUPS = re.compile("[0-9]{1,3}(?:[ \u00a0\u202f][0-9]{3})+(?:,[0-9]{1,3}(?:[ \u00a0\u202f][0-9]{1,3})*)?"
                          "|[0-9]+,[0-9]{3}(?:[ \u00a0\u202f][0-9]{1,3})+")
"""Digits in groups of three with a space, a no-break space or a narrow no-break space between them, in the
whole part or in the fraction: `36 524`, `123 456 789,987 546`, `0,264 7` (Araua 203, section 3.2.1.1, page 12)."""

REGNAL_LETTERS = frozenset("IVX")
"""The one-letter Roman numerals that follow a name as a regnal or series number, as in `Elisabet I.a` (Araua 203,
section 3.1.2, page 7) and `Atano X.arekin` (Araua 18, page 116). No name in these sources takes L, C, D or M."""

PLURAL_ENDINGS = frozenset({"ak", "ek", "ei", "etan", "etako", "etatik", "etara", "en", "ekin", "entzat", "ez"})
"""The plural case endings after which `hiru` and `lau` keep their old final r: hirurak, lauretan (Araua 203,
section 12.2)."""

ONE_HOUR = {"ak": "a", "etan": "ean", "etatik": "etik", "etara": "era", "etako": "eko"}
"""The singular ending of `ordu bat` for each plural hour ending: `13:00etan` reads "ordu batean" (Araua 203,
section 14.3.2, page 52: ordu bata is singular)."""

ZERO_HOUR = {"ak": "a", "etan": "an", "ean": "an", "n": "an", "etatik": "tik", "etik": "tik", "etara": "ra",
             "era": "ra", "etako": "ko", "eko": "ko"}
"""The singular ending of `zero ordu` for each plural hour ending and each ending after a consonant: `00:00etan`
reads "zero orduan" (Araua 203, section 14.3.2, page 52: zero ordua is singular; Araua 35, page 184: "Zero orduan /
orenean")."""


def attach(spoken: str, prefix: str, suffix: str) -> str:
    """The case ending joined to the last spoken word (Araua 203, section 12, pages 37 to 41).

    A word in `-r` doubles it: hamarretik, hamarreko (page 29) and hogeita hamarrean (pages 59 and 60). A word in
    `-a` merges with an ending in `a` or `e`: hamaikan, hamaiketan, milek. Any other consonant takes an epenthetic
    `e` before an ending in a consonant: bosteko, ehunetik. Alone, `hiru` and `lau` keep a final r before a plural
    ending, while `hogeita hiru` does not."""
    if not suffix:
        return prefix + spoken
    head, space, word = spoken.rpartition(" ")
    previous = head.rpartition(" ")[2]
    if word == "bat" and previous == "ordu":
        suffix = ONE_HOUR.get(suffix, suffix)
    elif word == "ordu" and previous == "zero":
        suffix = ZERO_HOUR.get(suffix, suffix)
    if word in ("hiru", "lau") and not previous.endswith("ta") and suffix in PLURAL_ENDINGS:
        word += "r"
    elif word.endswith("a") and suffix[0] in "ae":
        word = word[:-1]
    elif word.endswith("r"):
        word += "r" if suffix[0] in "aeiou" else "re"
    elif word[-1] not in "aeiou" and suffix[0] not in "aeiou":
        word += "e"
    return prefix + head + space + word + suffix


def genitive(words: str) -> str:
    """A cardinal with the ending `-(r)en` that names a fraction: bosten, hamarren, hogeiren, ehunen (Araua 203,
    section 6, page 28)."""
    return words + ("ren" if words[-1] in "aeiour" else "en")


class BasqueSpeller:
    """ovos-number-parser for cardinals, and the academy rules for ordinals, decimals and fractions."""

    def __init__(self):
        self.ovos = OvosNumberSpeller({})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self.ovos.cardinal(digits, features, request)

    def year(self, digits: str, features: Features, request: Request) -> str:
        return self.cardinal(digits, features, request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        """The cardinal and `-garren`, where `bost` drops its t: bigarren, hamabosgarren, hogeita batgarren. A
        million drops its `bat`: milioigarren. One reads `lehen` (Araua 203, section 5, pages 24 to 26)."""
        number = str(_integer(digits))
        special = request.data["ordinal_words"].get(number)
        if special is not None:
            return special
        words = _scale_noun(self.cardinal(number, features, request))
        if words.endswith("bost"):
            words = words[:-1]
        return words + request.data["ordinal_suffix"]

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """The whole part, `koma`, each leading zero of the fraction as `zero`, and the rest as a cardinal:
        `24,5` is "hogeita lau koma bost", `0,043` is "zero koma zero berrogeita hiru" and `2,60` is "bi koma
        hirurogei" (Araua 203, section 3.2.1.3, page 15)."""
        whole = self.cardinal(integer or "0", features, request)
        rest = fraction.lstrip("0")
        words = [request.data["digit_words"][0]] * (len(fraction) - len(rest))
        if rest:
            words.append(self.cardinal(rest, features, request))
        return f"{whole} {request.data['decimal_word']} {' '.join(words)}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """`1/5` is "bosten bat", `2/3` is "bi heren", and a denominator of more than one word reads `zati`:
        `13/47` is "hamahiru zati berrogeita zazpi" (Araua 203, section 6, pages 27 to 29)."""
        bottom = str(_integer(denominator))
        names = request.data["fraction_names"]
        cardinal = _scale_noun(self.cardinal(bottom, features, request))
        name = names.get(bottom) or genitive(cardinal)
        if _integer(numerator) == 1:
            return f"{name} bat"
        top = self.cardinal(numerator, features, request)
        if bottom in names or " " not in cardinal:
            return f"{top} {name}"
        return f"{top} {request.data['fraction_word']} {cardinal}"


def _scale_noun(words: str) -> str:
    """A cardinal that ends in `milioi bat` or `bilioi bat` without its `bat`, as an ordinal and a fraction name
    take it: milioigarren, milioiren (Araua 203, pages 26 and 29)."""
    return words[:-4] if words.endswith("ioi bat") else words


SPELLER = BasqueSpeller()


def _cardinal(digits: str, request: Request) -> str:
    return SPELLER.cardinal(digits, Features(), request)


def _signed(words: str, sign: str, request: Request) -> str:
    return f"{request.data['sign_words'][sign]} {words}" if sign else words


def _number(amount: FrozenMap, request: Request) -> str:
    if amount["fraction"]:
        return SPELLER.decimal(amount["integer"], amount["fraction"], Features(), request)
    return _cardinal(amount["integer"], request)


def _counted(amount: FrozenMap, noun: str, request: Request) -> str:
    """A number and the noun that it counts. One whole unit reads the noun first: "euro bat", "gradu bat", while
    `1,0` reads "bat koma zero gradu" (Araua 197, section 6.3 and its note 6)."""
    if not amount["fraction"] and amount["integer"].lstrip("0") == "1":
        return f"{noun} bat"
    return f"{_number(amount, request)} {noun}"


def speak_ordinal(span: Span, context: SpanContext) -> str:
    return SPELLER.ordinal(span.fields["digits"], Features(), context.request)


def speak_roman(span: Span, context: SpanContext) -> str:
    return SPELLER.ordinal(str(span.fields["value"]), Features(), context.request)


def speak_decimal(span: Span, context: SpanContext) -> str:
    return _signed(_number(span.fields, context.request), span.fields["sign"], context.request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    fields = span.fields
    words = SPELLER.fraction(fields["numerator"], fields["denominator"], Features(), context.request)
    return _signed(words, fields["sign"], context.request)


def speak_expression(span: Span, context: SpanContext) -> str:
    """`5 x 0 = 0` reads "bost bider zero berdin zero" (Araua 203, page 21)."""
    request = context.request
    operands = span.fields["operands"]

    def operand(written: str) -> str:
        sign = SIGNS.get(written[0], "")
        return _signed(_cardinal(written.lstrip("-−+"), request), sign, request)

    words = [operand(operands[0])]
    for operator, written in zip(span.fields["operators"], operands[1:]):
        words += [request.data["operators"][operator], operand(written)]
    return " ".join(words)


def speak_date(span: Span, context: SpanContext) -> str:
    """The year in `-ko`, the month in the genitive, and the day: `1983-03-07` reads "mila bederatziehun eta
    laurogeita hiruko martxoaren zazpia". With no written ending, the day takes the article `-a` (Araua 203,
    section 15.2, page 66)."""
    request = context.request
    fields = span.fields
    year = attach(_cardinal(str(fields["year"]), request), "", "ko")
    day = _cardinal(str(fields["day"]), request)
    if not fields["suffix"]:
        day = attach(day, "", "a")
    return f"{year} {request.data['months'][fields['month'] - 1]} {day}"


def speak_time(span: Span, context: SpanContext) -> str:
    """The usual reading of Araua 203, section 14.3.2, pages 52 to 57, on the 12-hour clock: the day period, the
    hour with the plural article, and the minutes: `03:05ean` reads "goizeko hirurak eta bostean". At minute
    zero, the hour takes the written ending: `15:00etan` reads "arratsaldeko hiruretan". A day period written
    before the time replaces the one that the hour gives.

    The 24-hour reading is the unusual reading of the same tables, without the word `minutu`, which note 39 lets
    the reader leave out: `15:05ean` reads "hamabostak eta bostean", and `13:00etan` "hamahiruetan" (note 43).
    `00:00etan` reads "zero orduan", the formal reading of Araua 35, page 184.

    A time with `a.m.` or `p.m.` after it takes the day period of its hour (Araua 203, note 34, page 49):
    `12:15 a.m.` reads "gaueko hamabiak eta hamabost". Section 14.2, on the same page, reads `12:15` as "hamabiak
    eta hamabost" or "hamabiak eta laurden", and this file reads the minutes as a number."""
    request = context.request
    data = request.data
    fields = span.fields
    hour, minute = fields["hour"], fields["minute"]
    if fields["period"] is not None:
        hour = hour % 12 + (12 if fields["period"] == "pm" else 0)
    twelve = request.params.clock == "12h"
    face = twelve_hour(hour) if twelve else hour
    stem = data["hour_words"].get(str(face)) or _cardinal(str(face), request)
    if minute == 0:
        words = stem if fields["suffix"] else attach(stem, "", "ak")
    else:
        words = f"{attach(stem, '', 'ak')} eta {_cardinal(str(minute), request)}"
    written_period = context.before and context.before[-1].lower() in data["time_words"]
    if twelve and not written_period:
        words = f"{data['day_period_words'][str(hour)]} {words}"
    return words


def speak_money(span: Span, context: SpanContext) -> str:
    """`5 €` reads "bost euro", `1 €` "euro bat", and euros with two decimals read the cents: `3,25 €` is "hiru
    euro eta hogeita bost zentimo" (Araua 203, page 15; Araua 197, section 6.3)."""
    request = context.request
    fields = span.fields
    amount = fields["amount"]
    currency = request.data["currencies"][fields["currency"]]
    fraction = amount["fraction"]
    minor = currency.get("minor")
    if minor is not None and len(fraction) == 2:
        major = FrozenMap({**amount, "fraction": ""})
        cents = FrozenMap({**amount, "integer": str(int(fraction)), "fraction": ""})
        if int(fraction) == 0:
            words = _counted(major, currency["word"], request)
        elif not amount["integer"].lstrip("0"):
            words = _counted(cents, minor, request)
        else:
            words = f"{_counted(major, currency['word'], request)} eta {_counted(cents, minor, request)}"
    else:
        words = _counted(amount, currency["word"], request)
    return _signed(words, amount["sign"], request)


def speak_measure(span: Span, context: SpanContext) -> str:
    request = context.request
    amount = span.fields["amount"]
    return _signed(_counted(amount, request.data["units"][span.fields["unit"]], request), amount["sign"], request)


def speak_percent(span: Span, context: SpanContext) -> str:
    """The word `ehuneko` comes first, and a minus sign before it: `% 25` is "ehuneko hogeita bost", and `−% 4`
    "minus ehuneko lau" (Araua 203, sections 7.1 and 7.2, pages 30 to 32)."""
    request = context.request
    amount = span.fields["amount"]
    return _signed(f"{request.data['percent']['word']} {_number(amount, request)}", amount["sign"], request)


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    return context.request.data["abbreviations"][span.fields["key"]]


def _symbol_suffix(text: str, end: int, data) -> tuple[int, str] | None:
    """The end and the case ending after a symbol: a hyphen and a declared ending, as in `€-etik` and `kg-ek`
    (Araua 197, section 6.4), or what `_suffix` reads."""
    if text.startswith("-", end):
        stop = end + 1
        while stop < len(text) and (is_letter(text[stop]) or is_mark(text[stop])):
            stop += 1
        ending = text[end + 1:stop]
        if ending in data.get("case_suffixes", ()) and not (stop < len(text) and is_word_char(text[stop])):
            return stop, ending
    return _suffix(text, end, data, ())


def _ordinal_follower(text: str, stop: int, data) -> tuple[int, str] | None:
    """The end and the case ending after the full stop of an ordinal at text[stop - 1]: a declared ending, as in
    `3.ak`, a space and a lowercase word, as in `27. orrialdea`, or the comma of a list, as in `XIX., XX. eta XXI.
    mendeetan`. A capital letter or the end of the text after the stop ends a sentence."""
    end = stop
    while end < len(text) and (is_letter(text[end]) or is_mark(text[end])):
        end += 1
    if end > stop:
        if text[stop:end] in data.get("case_suffixes", ()) and not (end < len(text) and is_word_char(text[end])):
            return end, text[stop:end]
        return None
    if text[stop:stop + 1] == "," or (text[stop:stop + 1] == " " and next_visible(text, stop).islower()):
        return stop, ""
    return None


@dataclass(frozen=True)
class BasqueOrdinal:
    """`27. orrialdea`, `2. eta 3. ataletan`, `3.ak`, `1.etik`: a whole number and a full stop (Araua 203,
    sections 5 and 12.3)."""
    name: str = "basque_ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for number in numbers_in(text, request):
            if (number.sign or number.fraction is not None or not text.startswith(".", number.end)
                    or (len(number.integer) > 1 and number.integer[0] == "0")
                    or not _cluster_edge(text, number.start, number.end)
                    or not _free_before(text, number.start, request.data["symbols"])):
                continue
            follower = _ordinal_follower(text, number.end + 1, request.data)
            if follower is not None:
                yield Span(number.start, follower[0], Form.ORDINAL,
                           FrozenMap({"digits": number.integer, "marker": ".", "prefix": "", "suffix": follower[1],
                                      "script": number.script}), recognizer=self.name)


def _noun_after(text: str, stop: int, nouns: Sequence[str], data) -> bool:
    """Whether a space and one of `nouns` follow text[:stop], bare or with a case ending: `mendean`, `mendeetan`,
    `Legea`."""
    if text[stop:stop + 1] != " ":
        return False
    end = stop + 1
    while end < len(text) and is_letter(text[end]):
        end += 1
    word = text[stop + 1:end]
    endings = ("", *data["case_suffixes"])
    return any(word.startswith(noun) and word[len(noun):] in endings for noun in nouns)


def _name_before(text: str, start: int) -> bool:
    """Whether a capitalised word and one space come right before text[start:], as `Elisabet` in `Elisabet I.a`."""
    end = start - 1
    if end < 1 or text[end] != " " or not is_letter(text[end - 1]):
        return False
    first = end
    while first > 0 and is_letter(text[first - 1]):
        first -= 1
    return text[first].isupper()


@dataclass(frozen=True)
class Roman:
    """`XX. mendea`, `III.a`, `II.ak`: an upper-case Roman numeral and a full stop, read as an ordinal (Araua 203,
    section 3.1.2, page 7: "X. urtean (hamargarren urtean)").

    One capital letter and a full stop is also a label, as `A` to `D` label the rows of a table on page 13 of
    Araua 203, or an initial, as in `M. Zabala` (Araua 18, page 116). So a numeral of one letter reads as an
    ordinal only before a noun of the `roman_nouns` table, the nouns that pages 7 to 10 number with Roman
    numerals, or when it is `I`, `V` or `X` with a case ending after a capitalised name, as in `Elisabet I.a`."""
    name: str = "roman"
    form: Form = Form.ROMAN

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        from text2spoken.core.roman import value as roman_value

        for match in re.finditer("[IVXLCDM]+[.]", text):
            start, stop = match.span()
            numeral = match.group()[:-1]
            number = roman_value(numeral)
            if number is None or (start and is_word_char(text[start - 1])):
                continue
            follower = _ordinal_follower(text, stop, request.data)
            if follower is None:
                continue
            if len(numeral) == 1 and not (_noun_after(text, stop, request.data["roman_nouns"], request.data)
                                          or (follower[1] and numeral in REGNAL_LETTERS
                                              and _name_before(text, start))):
                continue
            yield Span(start, follower[0], Form.ROMAN,
                       FrozenMap({"value": number, "role": "ordinal", "suffix": follower[1]}), recognizer=self.name)


@dataclass(frozen=True)
class SpaceGroups:
    """`36 524`, `Duela 30 000 urte`: digits in groups of three with a space between them, which Araua 203,
    section 3.2.1.1, page 12, recommends. The group mark of this file is `.`, so each group would read as a number
    of its own, and the span stays as written."""
    name: str = "space_groups"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in SPACE_GROUPS.finditer(fold_digits(text)):
            start, end = match.span()
            script = digit_script(text[start:end])
            if script is None or (start and is_word_char(text[start - 1])) or not _cluster_edge(text, start, end):
                continue
            digits = re.sub("[^0-9]", "", match.group())
            yield Span(start, end, Form.CARDINAL,
                       FrozenMap({"digits": digits, "sign": "", "lead": "", "prefix": "", "suffix": "",
                                  "script": script}), recognizer=self.name, keep=True)


@dataclass(frozen=True)
class LetterCode:
    """`COVID-19`, `BI-2617`, `sub-23`: letters, a hyphen and digits, as a code or an alphanumeric sigla (Araua
    196, section 6.1, pages 56 and 57). Araua 203, section 15.3, page 67, reads one capital letter, a hyphen and a
    day as a sigla and a number: `M-8an` is "eme zortzian". No source reads a longer sigla, so these stay as
    written."""
    name: str = "letter_code"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in re.finditer("-[0-9]+", fold_digits(text)):
            hyphen, end = match.span()
            start = hyphen
            while start > 0 and is_letter(text[start - 1]):
                start -= 1
            letters = text[start:hyphen]
            if (not letters or (len(letters) == 1 and letters.isupper()) or (start and is_word_char(text[start - 1]))
                    or not _cluster_edge(text, hyphen + 1, end)):
                continue
            yield Span(hyphen + 1, end, Form.CARDINAL,
                       FrozenMap({"digits": match.group()[1:], "sign": "", "lead": "-", "prefix": "", "suffix": "",
                                  "script": digit_script(text[hyphen + 1:end]) or "Latn"}),
                       recognizer=self.name, keep=True)


@dataclass(frozen=True)
class LawNumber:
    """`3/2015 Legea`, `6/89 Legea`, `222/2001 Dekretua`: the number and the year of a law or a decree before a
    noun of the `code_nouns` table (Araua 203, page 45; EIMA, Ortotipografia, page 14). The pair is no fraction,
    and it stays as written."""
    name: str = "law_number"
    form: Form = Form.FRACTION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in re.finditer("([0-9]+)/([0-9]+)", fold_digits(text)):
            start, end = match.span()
            if ((start and is_word_char(text[start - 1])) or not _cluster_edge(text, start, end)
                    or not _noun_after(text, end, request.data["code_nouns"], request.data)):
                continue
            yield Span(start, end, Form.FRACTION,
                       FrozenMap({"numerator": match.group(1), "denominator": match.group(2), "sign": "",
                                  "prefix": "", "suffix": ""}), recognizer=self.name, keep=True)


@dataclass(frozen=True)
class RomanMonthDate:
    """`1995/III/07`, `1995-III-27`: the year, the month as a Roman numeral and the day, as Araua 37, printed
    pages 193 and 194, writes them. Araua 203, note 47, page 66, calls the form old, and does not call it wrong."""
    name: str = "roman_month_date"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        from text2spoken.core.roman import value as roman_value

        for match in re.finditer("([0-9]{4})(?:/([IVX]+)/|-([IVX]+)-)([0-9]{1,2})", fold_digits(text)):
            start, end = match.span()
            year, month, day = int(match.group(1)), roman_value(match.group(2) or match.group(3)), int(match.group(4))
            if (month is None or not is_valid(year, month, day) or (start and is_word_char(text[start - 1]))
                    or not _cluster_edge(text, start, end)):
                continue
            after = _suffix(text, end, request.data, ())
            if after is not None:
                yield Span(start, after[0], Form.DATE,
                           FrozenMap({"year": year, "month": month, "day": day, "written_order": "YMD",
                                      "month_written": "digits", "prefix": "", "suffix": after[1]}),
                           recognizer=self.name)


@dataclass(frozen=True)
class BasqueTime:
    """`15:00etan`, `00:08an`, `arratsaldeko 7:10`, `7:10 p.m.`: a clock time with a case ending, after a word of
    the `time_words` table, which names a day period, or before `a.m.` or `p.m.` (Araua 203, note 34, page 49). A
    time with none of these, as in a timetable, stays as written. `24:00` closes a day, as in
    `08:00etatik 24:00etara` (Araua 203, section 14.2, page 50)."""
    name: str = "basque_time"
    form: Form = Form.TIME

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        words = context_words(tokens)
        breaks = clause_breaks(text)
        time_words = frozenset(data["time_words"])
        for match in re.finditer("[0-9][0-9]?:[0-9][0-9]", fold_digits(text)):
            start, end = match.span()
            if (start and is_word_char(text[start - 1])) or not _cluster_edge(text, start, end):
                continue
            hour, minute = match.group().split(":")
            fields = (24, 0, None) if match.group() == "24:00" else clock_fields(hour, minute, None)
            if fields is None:
                continue
            written_period = _period_after(text, end, data["day_periods"])
            if written_period is not None:
                period, stop = written_period
                if 1 <= fields[0] <= 12:
                    yield Span(start, stop, Form.TIME,
                               FrozenMap({"hour": fields[0], "minute": fields[1], "second": None, "period": period,
                                          "suffix": ""}),
                               trail="." if _sentence_period(text, stop) else "", recognizer=self.name)
                continue
            after = _suffix(text, end, data, ())
            if after is None:
                continue
            stop, suffix = after
            if suffix and suffix not in data["time_suffixes"]:
                continue
            before = clause_window(text, words, start, end, -1, limit=1, breaks=breaks)
            if not (suffix or (before and before[0].lower() in time_words)):
                continue
            yield Span(start, stop, Form.TIME,
                       FrozenMap({"hour": fields[0], "minute": fields[1], "second": None, "period": None,
                                  "suffix": suffix}), recognizer=self.name)


def _amount_spans(text: str, request: Request, symbols: Sequence[str]) -> Iterator[tuple[Number, str, int, int,
                                                                                             str, str, bool]]:
    """Each number with a symbol after it, as in `5 €` and `25 °C`, or before it, as in `$5`, with the start, the
    end, the prefix and the case ending of the span, and whether the symbol comes first. A dash right after a
    symbol or a letter is no minus sign, so `-10` in `5 €-10 €` and `5 km-10 km` reads as `10`."""
    data = request.data
    ordered = sorted(symbols, key=len, reverse=True)
    for number in numbers_in(text, request):
        if number.sign and number.start and (text[number.start - 1] in symbols or is_letter(text[number.start - 1])):
            number = replace(number, start=number.start + 1, sign="")
        found = None
        for gap in GAPS:
            symbol = next((s for s in ordered if text.startswith(gap + s, number.end)), None)
            if symbol is None:
                continue
            after = _symbol_suffix(text, number.end + len(gap) + len(symbol), data)
            before = _prefix(text, number.start, data, ())
            if after is not None and before is not None and not _per_unit(text, after[0]):
                found = (symbol, before[0], after[0], before[1], after[1], False)
                break
        if found is None and not number.sign:
            for gap in GAPS:
                symbol = next((s for s in ordered if text.endswith(s + gap, 0, number.start)), None)
                if symbol is None:
                    continue
                bounds = _affixes(text, number.start - len(gap) - len(symbol), number.end, data, ())
                if bounds is not None:
                    found = (symbol, *bounds, True)
                    break
        if found is not None:
            yield number, *found


def _kept_ranges(spans: Iterable[Span], text: str) -> Iterator[Span]:
    """The spans, where two that a mark of `RANGE_MARKS` joins stay as written: `10%-20%`, `5 €-10 €`. A Basque
    range reads with the case endings `-tik` and `-ra` (design section 4.2), and this file has no rule for them."""
    spans = sorted(spans, key=lambda span: span.start)
    ranged = {index for pair in range(len(spans) - 1)
              if text[spans[pair].end:spans[pair + 1].start] in RANGE_MARKS for index in (pair, pair + 1)}
    for index, span in enumerate(spans):
        yield replace(span, keep=True) if index in ranged else span


def _per_unit(text: str, end: int) -> bool:
    """Whether a slash and a letter continue a unit, as in `m/s` when the table holds only `m`."""
    return end + 1 < len(text) and text[end] == "/" and is_letter(text[end + 1])


@dataclass(frozen=True)
class BasqueMoney:
    """`5 €`, `3,25 €`, `1 €-etik`, `$5`: a number and a currency symbol of the `currencies` table. A dash right
    after a symbol is no minus sign, and two amounts that a dash joins stay as written, as in `5 €-10 €`.

    The reading puts the currency noun last, so a case ending written on the digits of `€5eko` belongs to the
    number and not to the noun: "bost euroeko" is wrong, and the amount stays as written."""
    name: str = "basque_money"
    form: Form = Form.MONEY

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return _kept_ranges(self._amounts(text, request), text)

    def _amounts(self, text: str, request: Request) -> Iterator[Span]:
        codes = {symbol: code for code, currency in request.data["currencies"].items()
                 for symbol in currency["symbols"]}
        for number, symbol, start, end, prefix, suffix, first in _amount_spans(text, request, tuple(codes)):
            yield Span(start, end, Form.MONEY,
                       FrozenMap({"amount": number.amount(), "currency": codes[symbol], "written_symbol": symbol,
                                  "scale": "", "prefix": prefix, "suffix": suffix}),
                       recognizer=self.name, keep=first and bool(suffix))


@dataclass(frozen=True)
class BasqueMeasure:
    """`5 km`, `25 °C`, `1 kg-ek`: a number and a unit of the `units` table after it. A dash right after a unit
    is no minus sign, and two measures that a dash joins stay as written, as in `5 km-10 km`."""
    name: str = "basque_measure"
    form: Form = Form.MEASURE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return _kept_ranges(self._measures(text, request), text)

    def _measures(self, text: str, request: Request) -> Iterator[Span]:
        units = tuple(request.data["units"])
        for number, unit, start, end, prefix, suffix, _ in _amount_spans(text, request, units):
            if text.startswith(unit, number.end) or text.startswith(unit, number.end + 1):
                yield Span(start, end, Form.MEASURE,
                           FrozenMap({"amount": number.amount(), "relation": "", "unit": unit, "prefix": prefix,
                                      "suffix": suffix}), recognizer=self.name)


@dataclass(frozen=True)
class BasquePercent:
    """`% 25`, `% 7k`, `−% 4`, `20%` and `20 %-ko`: the percent sign before the number, as the academy writes it,
    or after it, as ISO 80000 writes it, with a hyphen before a case ending (Araua 203, section 7.1 and its note
    27; Araua 197, section 6.6, page 13).

    A dash right after a percent sign is no minus sign. Two percentages that a dash joins, as in `10%-20%` and
    `% 2-% 5`, are a range, and the range stays as written."""
    name: str = "basque_percent"
    form: Form = Form.PERCENT

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return _kept_ranges(self._percents(text, request), text)

    def _percents(self, text: str, request: Request) -> Iterator[Span]:
        data = request.data
        for number in numbers_in(text, request):
            if number.sign and text[number.start - 1:number.start] in data["percent"]["signs"]:
                number = replace(number, start=number.start + 1, sign="")
            for sign in data["percent"]["signs"]:
                for gap in GAPS:
                    start = number.start - len(gap) - len(sign)
                    if number.sign or start < 0 or text[start:number.start] != sign + gap:
                        continue
                    written_sign = SIGNS.get(text[start - 1], "") if start else ""
                    if written_sign and _free_before(text, start - 1, ()):
                        start -= 1
                    else:
                        written_sign = ""
                    bounds = _affixes(text, start, number.end, data, ())
                    if bounds is not None:
                        yield self._span(number, written_sign, "before", bounds)
                    break
                for gap in GAPS:
                    if not text.startswith(gap + sign, number.end):
                        continue
                    before = _prefix(text, number.start, data, ())
                    after = _symbol_suffix(text, number.end + len(gap) + len(sign), data)
                    if before is not None and after is not None:
                        yield self._span(number, number.sign, "after", (before[0], after[0], before[1], after[1]))
                    break

    def _span(self, number: Number, sign: str, position: str, bounds: tuple[int, int, str, str]) -> Span:
        amount = FrozenMap({**number.amount(), "sign": sign})
        return Span(bounds[0], bounds[1], Form.PERCENT,
                    FrozenMap({"amount": amount, "sign_position": position, "prefix": bounds[2],
                               "suffix": bounds[3]}), recognizer=self.name)


@dataclass(frozen=True)
class BasqueAbbreviation:
    """The abbreviations of the table, as `etab.` and `K.a.` (Araua 196). The full stop of an abbreviation at the
    end of the text also ends the sentence, so it stays (Araua 196, section 12.1, page 31). An abbreviation of
    `sentence_final` also keeps it before a capital letter. Others come before a name or a numeral, as in
    `Agirre jn. Bilbon` or `K.a. V. mendean`, where a capital letter starts no sentence."""
    name: str = "basque_abbreviation"
    form: Form = Form.ABBREVIATION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        final = frozenset(data["sentence_final"])
        for key in sorted(data["abbreviations"], key=len, reverse=True):
            position = text.find(key)
            while position != -1:
                end = position + len(key)
                if is_bounded(text, position, end):
                    following = next_visible(text, end)
                    sentence_end = following == "" or (key in final and following.isupper())
                    yield Span(position, end, Form.ABBREVIATION, FrozenMap({"key": key}),
                               trail="." if sentence_end else "", recognizer=self.name)
                position = text.find(key, end)


DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "defaults": {"date_order": "DMY", "clock": "12h", "minute_style": "number", "decimal_mark": ",",
                 "scale": "long"},
    "sign_words": {"-": "minus", "+": "plus"},
    "decimal_word": "koma",
    "digit_words": ["zero", "bat", "bi", "hiru", "lau", "bost", "sei", "zazpi", "zortzi", "bederatzi"],
    "leads": {"-": ""},
    "case_suffixes": ["a", "ak", "an", "ean", "n", "en", "ren", "aren", "ari", "ri", "ei", "i", "k", "ek", "ko",
                      "eko", "tik", "etik", "ra", "era", "rako", "erako", "tako", "etako", "etan", "tan", "etatik",
                      "tatik", "etara", "tara", "ekin", "rekin", "arekin", "entzat", "rentzat", "arentzat", "z", "ez",
                      "az", "raino", "eraino", "rantz", "erantz", "koa", "ekoa", "koak", "ekoak", "tikoa", "etikoa"],
    "time_suffixes": ["a", "ak", "an", "ean", "n", "etan", "tik", "etik", "etatik", "ra", "era", "etara", "ko", "eko",
                      "etako"],
    "day_periods": {"am": ["a.m."], "pm": ["p.m."]},
    "time_words": ["goizeko", "goizaldeko", "eguerdiko", "arratsaldeko", "arratseko", "iluntzeko", "gaueko",
                   "gauerdiko"],
    "day_period_words": {"0": "gaueko", "1": "goizeko", "2": "goizeko", "3": "goizeko", "4": "goizeko",
                         "5": "goizeko", "6": "goizeko", "7": "goizeko", "8": "goizeko", "9": "goizeko",
                         "10": "goizeko", "11": "goizeko", "12": "eguerdiko", "13": "eguerdiko",
                         "14": "arratsaldeko", "15": "arratsaldeko", "16": "arratsaldeko", "17": "arratsaldeko",
                         "18": "arratsaldeko", "19": "arratsaldeko", "20": "arratsaldeko", "21": "gaueko",
                         "22": "gaueko", "23": "gaueko", "24": "gaueko"},
    "hour_words": {"0": "zero ordu", "1": "ordu bat", "2": "ordu bi"},
    "months": ["urtarrilaren", "otsailaren", "martxoaren", "apirilaren", "maiatzaren", "ekainaren", "uztailaren",
               "abuztuaren", "irailaren", "urriaren", "azaroaren", "abenduaren"],
    "code_nouns": ["Lege", "lege", "Dekretu", "dekretu"],
    "roman_nouns": ["mende", "milurteko", "urte", "dinastia", "liburuki", "ekitaldi", "kapitulu", "atal", "gradu"],
    "ordinal_words": {"1": "lehen"},
    "ordinal_suffix": "garren",
    "fraction_names": {"2": "erdi", "3": "heren", "4": "laurden"},
    "fraction_word": "zati",
    "percent": {"signs": ["%"], "position": "either", "word": "ehuneko"},
    "currencies": {
        "EUR": {"symbols": ["€"], "word": "euro", "minor": "zentimo"},
        "USD": {"symbols": ["$"], "word": "dolar"},
        "GBP": {"symbols": ["£"], "word": "libera"},
    },
    "units": {"kg": "kilogramo", "km": "kilometro", "km/h": "kilometro zati ordu", "m": "metro", "cm": "zentimetro",
              "mm": "milimetro", "l": "litro", "L": "litro", "min": "minutu", "s": "segundo", "°C": "gradu",
              "MW": "megawatt", "Hz": "hertz", "V": "volt"},
    "operators": {"+": "gehi", "−": "ken", "x": "bider", "×": "bider", "÷": "zati", "=": "berdin"},
    "patterns": {"expression": "[-−+]?[0-9]+(?: ?[+−x×÷=] ?[-−+]*[0-9]+)+"},
    "abbreviations": {"etab.": "eta abar", "adib.": "adibidez", "ik.": "ikus", "K.a.": "Kristo aurreko",
                      "K.o.": "Kristo ondoko", "o.a.a.": "oraingo aroaren aurreko", "o.a.": "oraingo aroko",
                      "id.": "idem", "zk.": "zenbakia", "zenb.": "zenbakia", "or.": "orrialdea", "hurr.": "hurrengoak",
                      "jn.": "jauna", "and.": "andrea", "k.": "kalea", "pl.": "plaza", "etorb.": "etorbidea",
                      "tel.": "telefonoa"},
    "sentence_final": ["etab.", "hurr."],
    "symbols": {"%": "percent", "€": "money", "$": "money", "£": "money", "°": "measure"},
})
"""The day period of each hour follows the table of Araua 203, pages 53 to 55, which gives hours 1 to 5, 11 to 15,
20, 21, 23, 24 and 0, and elides the hours between two hours that take the same word."""

LANGUAGE = LanguageSpec(
    code="eu",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("eu-ES"),),
    data=DATA,
    recognizers=(SHARED["lexicon"], RomanMonthDate(), SpaceGroups(), LetterCode(), LawNumber(),
                 SHARED["date_numeric"], BasqueTime(), BasqueMoney(), BasquePercent(), BasqueMeasure(),
                 SHARED["expression"], SHARED["fraction"], BasqueOrdinal(), Roman(), BasqueAbbreviation(),
                 SHARED["decimal"], SHARED["cardinal"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.DATE: speak_date, Form.TIME: speak_time, Form.MONEY: speak_money,
        Form.PERCENT: speak_percent, Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression,
        Form.FRACTION: speak_fraction, Form.ORDINAL: speak_ordinal, Form.ROMAN: speak_roman,
        Form.ABBREVIATION: speak_abbreviation, Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal,
    },
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER},
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={
        "date_order": frozenset({"DMY", "MDY", "YMD"}),
        "clock": frozenset({"12h", "24h"}),
        "minute_style": frozenset({"number"}),
        "decimal_mark": frozenset({","}),
        "scale": frozenset({"long"}),
    },
    not_applicable=frozenset({"default_gender", "register", "phone_regions"}),
    attach=attach,
)
