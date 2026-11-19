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

A Roman numeral and a full stop read as an ordinal only on evidence that no verbalizer of this file writes, so a
second pass reads nothing that the first pass left as written (design section 11). The evidence is a noun of the
`roman_nouns` table, a case ending on the numeral, the comma of a list, or a conjunction and a numeral that reads.
The last one follows Araua 203, section 5, page 27: "Ordinal bat baino gehiago elkarren ondoan gertatzen direnean,
aukerakoa da bakoitzean -garren atzizkia jartzea edo azkenean bakarrik jartzea", with the example "XIX., XX. eta
XXI. mendeetan". A noun followed by `bat`, bare or with a case ending, is no evidence, because the measure
verbalizer reads one unit noun first: `1 °C` is "gradu bat" (Araua 203, page 21).

The `operators` table holds the words of the same page: `5 x 0 = 0` is "bost bider zero berdin zero". Digits in
groups of three with a space, a no-break space or a narrow no-break space between them, which Araua 203, section
3.2.1.1, page 12, recommends, as in `36 524`, read as one number: the group marks of this file are `.` and these
spaces, so `1 000 000 lagun` reads "milioi bat lagun", as `1.000.000 lagun` does. Two forms stay as written through
`KEPT_SPACE_GROUPS`. A run of three groups of three digits, as `943 123 456`, is also the shape of a telephone
number: Araua 203, footnote 12, page 14, "zenbakiak binaka edo hirunaka ere zatitu daitezke: Telefonoa: +34 944 15
81 55 / +34 944 158 155", and this file has no telephone reading. The run stays as written also after one two-digit group,
which may be a country code with no plus sign, and with the first group in brackets. Digit groups after a country
code, `+34` or `0034`, stay as written, in threes or in pairs. A fraction in groups after the decimal comma, as
`4 712,395 8`, which section 3.2.1.1 marks as unusual (ezohikoa), would read its first group alone, and so would a
fraction in groups after a decimal point, as `3.141 592 6` (page 14), where the point would read as a group mark.

A hyphen between two numbers, or between two percentages, amounts or measures of one kind, marks a range, as in
`% 2-% 5 bitartean` (Araua 203, section 7.1, page 32) and `1999-2011 bitartean` (section 19, page 70). Basque has no
range word, and case endings mark the range. Section 14.3.1, page 52, reads the timetable `09:00-13:00` as
"bederatzietatik ordu batera", because "Irakurtzean, berriz, dagokien artikulua eta kasu-marka jartzen zaizkie". So
`join_range` gives the first end the ablative `-tik` and the second end the allative `-ra`, as in "orduak zerotik
hogeita laura doaz" (page 50). The norm puts the same endings before `bitartean`: "Hogei zenbakitik ehun zenbakira
bitartean" (page 21).

A range reads before a word of the `range_followers` table. A range of percentages, amounts or measures also reads
where its clause or its line ends. Two bare numbers there may be a score, as in "Urdinak 0-2 aitzinatu dira"
(page 45), so they stay as written. Before any other word the pair stays as written. Before a noun, the ending
belongs on the noun, as in "Donibane Garazitik 20 km-ra" (page 44). Before a verb, `% 2-% 5 igoko da` may give the
size of the rise or its start and its end. Before `artean`, as in `1898-1900 artean` (page 70), the norm gives no
reading. A case ending on one end, as in `1914-1918ko` (page 69), keeps the pair as written too.

An en dash stays as written: Araua 197, note 13, page 30, gives it to the minus sign, "minus eta ken adierazteko,
tarte bikoitzeko marratxoa erabiltzen da". A number with no group mark before a number in groups, as in
`15-20 000`, may stand for thousands, so the pair stays as written when the first number is less than the first
group of the second.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety
from text2spoken.core.numbers import SIGNS, Number
from text2spoken.core.recognizers import (SHARED, Range, SpaceGroups, _affixes, _cluster_edge, _free_before,
                                          _per_unit, _period_after, _prefix, _sentence_period, _suffix, numbers_in,
                                          signed, speak_cardinal, speak_decimal, speak_expression, speak_fraction,
                                          speak_lexicon, speak_ordinal)
from text2spoken.core.spans import Features, Span, SpanContext, clause_breaks, clause_window, context_words
from text2spoken.core.spellers import OvosNumberSpeller, _integer
from text2spoken.core.times import clock_fields, day_hour, twelve_hour
from text2spoken.core.tokens import (Token, digit_script, fold_digits, is_bounded, is_letter, is_mark, is_word_char,
                                     next_visible)
from text2spoken.params import FrozenMap, Form, freeze

GAPS = ("", " ", "\u00a0")
"""The gaps between a number and its symbol: none, a space or a no-break space (Araua 197, section 6.3)."""

DASHES = ("-", "–")
"""The marks that may join two amounts as a range: a hyphen, as in `% 2-% 5` (Araua 203, section 7.1, page 32), and
an en dash. Two amounts that one of them joins never read as two amounts."""

ROMAN_NUMERAL = re.compile("[IVXLCDM]+[.]")
"""An upper-case Roman numeral and the full stop of an ordinal."""

COORDINATION = re.compile(" (?:eta|edo) ")
"""The conjunctions that join two ordinals (Araua 203, section 5, page 27)."""

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


def join_range(span: Span, following: Span, range_word: str) -> tuple[Span, Span]:
    """The two ends of a range with their case endings: the first takes `-tik` and the second `-ra`, and the hyphen
    between them reads as a space (module docstring)."""
    return (replace(span, end=following.start, trail=" ", fields=FrozenMap({**span.fields, "suffix": "tik"})),
            replace(following, fields=FrozenMap({**following.fields, "suffix": "ra"})))


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


def speak_roman(span: Span, context: SpanContext) -> str:
    return SPELLER.ordinal(str(span.fields["value"]), Features(), context.request)


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
    hour = day_hour(hour, fields["period"])
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
    return signed(words, amount["sign"], request)


def speak_measure(span: Span, context: SpanContext) -> str:
    request = context.request
    amount = span.fields["amount"]
    return signed(_counted(amount, request.data["units"][span.fields["unit"]], request), amount["sign"], request)


def speak_percent(span: Span, context: SpanContext) -> str:
    """The word `ehuneko` comes first, and a minus sign before it: `% 25` is "ehuneko hogeita bost", and `−% 4`
    "minus ehuneko lau" (Araua 203, sections 7.1 and 7.2, pages 30 to 32)."""
    request = context.request
    amount = span.fields["amount"]
    return signed(f"{request.data['percent']['word']} {_number(amount, request)}", amount["sign"], request)


def speak_range(span: Span, context: SpanContext) -> str:
    """The two ends as cardinals with the endings of `join_range`: `10-20 bitartean` is "hamarretik hogeira
    bitartean"."""
    low, high = (_cardinal(span.fields[end], context.request) for end in ("low", "high"))
    return f"{attach(low, '', 'tik')} {attach(high, '', 'ra')}"


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    return context.request.data["abbreviations"][span.fields["key"]]


def _symbol_suffix(text: str, end: int, symbol: str, data) -> tuple[int, str] | None:
    """The end and the case ending after `symbol`: a hyphen and a declared ending, as in `€-etik` and `kg-ek`
    (Araua 197, section 6.4), or what `_suffix` reads, as in `5€ko` (design section 4.4). Letters that touch a symbol
    of one letter are no ending, because the symbol and the letters may be one word: `0033 sei` holds no unit `s`."""
    if text.startswith("-", end):
        stop = end + 1
        while stop < len(text) and (is_letter(text[stop]) or is_mark(text[stop])):
            stop += 1
        ending = text[end + 1:stop]
        if ending in data.get("case_suffixes", ()) and not (stop < len(text) and is_word_char(text[stop])):
            return stop, ending
    after = _suffix(text, end, data, ())
    if after is not None and after[1] and len(symbol) == 1 and is_letter(symbol):
        return None
    return after


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



_GAP = "[ \u00a0\u202f]"
KEPT_SPACE_GROUPS = SpaceGroups(pattern=re.compile(
    f"(?<![0-9]{_GAP})(?<![0-9+])"
    f"(?:(?:\\+|00)[0-9]{{1,3}}(?:{_GAP}[0-9]{{2,3}})+(?![0-9])"
    f"|(?:[0-9]{{2}}{_GAP})?(?:[0-9]{{3}}|\\([0-9]{{3}}\\))(?:{_GAP}[0-9]{{3}}){{2}}(?!{_GAP}?[0-9]|,[0-9])"
    f"|(?:[0-9]{{1,3}}(?:{_GAP}[0-9]{{3}})+|[0-9]+),[0-9]{{3}}(?:{_GAP}[0-9]{{3}})*{_GAP}[0-9]{{1,3}}(?![0-9])"
    f"|[0-9]+\\.[0-9]{{3}}(?:{_GAP}[0-9]{{3}})*{_GAP}[0-9]{{1,2}}(?![0-9]))"))
"""The space-grouped runs that stay as written: digit groups after a country code, three groups of three digits, the
shape of a Spanish telephone number, with a two-digit group or brackets before it, a fraction in groups after the
decimal comma, with a whole part in groups or not, and a fraction in groups after a decimal point whose last group is
short (module docstring)."""

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


def _one_after_noun(text: str, stop: int, data) -> bool:
    """Whether the word after the noun that starts at text[stop + 1] is `bat`, bare or with a case ending of the
    `case_suffixes` table: `batean`, `batan`, `batekin`. The measure verbalizer writes this order for one unit."""
    end = stop + 1
    while end < len(text) and is_letter(text[end]):
        end += 1
    if text[end:end + 1] != " ":
        return False
    last = end + 1
    while last < len(text) and is_letter(text[last]):
        last += 1
    word = text[end + 1:last]
    return word.startswith("bat") and word[3:] in ("", *data["case_suffixes"])


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
    numerals, or when it is `I`, `V` or `X` with a case ending after a capitalised name, as in `Elisabet I.a`.

    A numeral of two letters or more reads before a noun of the `roman_nouns` table, with a case ending, before
    the comma of a list, or before `eta` or `edo` and a numeral that reads, as in `XIX., XX. eta XXI. mendeetan`
    (page 27). A space and another lowercase word are not enough, because a verbalizer writes lowercase words: in
    `II. 1995ean` the year reads, and `II.` stays as written."""
    name: str = "roman"
    form: Form = Form.ROMAN

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        matches = list(ROMAN_NUMERAL.finditer(text))
        readings: dict[int, tuple[int, int, str]] = {}
        for match in reversed(matches):
            read = _roman_reading(text, match, request.data, readings)
            if read is not None:
                readings[match.start()] = read
        for match in matches:
            if match.start() in readings:
                end, value, suffix = readings[match.start()]
                yield Span(match.start(), end, Form.ROMAN,
                           FrozenMap({"value": value, "role": "ordinal", "suffix": suffix}), recognizer=self.name)


def _roman_reading(text: str, match: re.Match, data, readings: Mapping[int, tuple[int, int, str]]
                   ) -> tuple[int, int, str] | None:
    """The end, the value and the case ending of the Roman ordinal that `match` finds, or None when the text gives
    no evidence for it that a verbalizer cannot write. `readings` holds the readings of the numerals after it, by
    start offset, so that a coordinated numeral looks up the next one and the pass stays linear."""
    from text2spoken.core.roman import value as roman_value

    start, stop = match.span()
    if start and is_word_char(text[start - 1]):
        return None
    numeral = match.group()[:-1]
    number = roman_value(numeral)
    follower = _ordinal_follower(text, stop, data)
    if number is None or follower is None:
        return None
    noun = _noun_after(text, stop, data["roman_nouns"], data) and not _one_after_noun(text, stop, data)
    if len(numeral) == 1:
        evidence = noun or (follower[1] and numeral in REGNAL_LETTERS and _name_before(text, start))
    else:
        link = COORDINATION.match(text, stop)
        evidence = (noun or follower[1] or text.startswith(",", stop)
                    or (link is not None and link.end() in readings))
    return (follower[0], number, follower[1]) if evidence else None


@dataclass(frozen=True)
class LetterCode:
    """`COVID-19`, `BI-2617`, `sub-23`: letters, a hyphen and digits, as a code or an alphanumeric sigla (Araua
    196, section 6.1, pages 56 and 57). Araua 203, section 15.3, page 67, reads one capital letter, a hyphen and a
    day as a sigla and a number: `M-8an` is "eme zortzian". No source reads a longer sigla, so these stay as
    written. A unit of the `units` table after a number is a measure and no code, as `km` in `5 km-10 km`."""
    name: str = "letter_code"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        folded = fold_digits(text)
        for match in re.finditer("-[0-9]+", folded):
            hyphen, end = match.span()
            start = hyphen
            while start > 0 and is_letter(text[start - 1]):
                start -= 1
            letters = text[start:hyphen]
            if (not letters or (len(letters) == 1 and letters.isupper()) or (start and is_word_char(text[start - 1]))
                    or (letters in request.data["units"] and re.search("[0-9][ \u00a0]?\\Z", folded[:start]))
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
                       FrozenMap({"whole": "", "numerator": match.group(1), "denominator": match.group(2), "sign": "",
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
                                      "month_written": "digits", "era": "", "prefix": "", "suffix": after[1]}),
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
                                          "prefix": "", "suffix": ""}),
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
                                  "prefix": "", "suffix": suffix}), recognizer=self.name)


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
            after = _symbol_suffix(text, number.end + len(gap) + len(symbol), symbol, data)
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


CLAUSE_ENDS = frozenset(".,;:!?)\n")
"""The marks after which a range of percentages, amounts or measures ends its clause or its line."""


def _range_follows(text: str, end: int, data, alone: bool) -> bool:
    """Whether a range that ends at text[end] reads: a word of the `range_followers` table comes next, or, when the
    range may stand `alone`, the text ends or a mark of `CLAUSE_ENDS` comes next (module docstring)."""
    rest = text[end:].lstrip("  ")
    word = re.match(r"\w+", rest)
    if word is not None:
        return word.group() in data["range_followers"]
    return alone and (not rest or rest[0] in CLAUSE_ENDS)


def _ranges(spans: Iterable[Span], text: str, request: Request) -> Iterator[Span]:
    """The spans, where two that a mark of `DASHES` joins are a range: `10%-20%`, `5 €-10 €`. The pair reads
    through `join_range` when a mark of `range_marks` joins it, no end has a case ending, and `_range_follows`
    lets it stand alone. Otherwise both ends stay as written, as do three ends or more that dashes chain."""
    chains: list[list[Span]] = []
    for span in sorted(spans, key=lambda span: span.start):
        if chains and text[chains[-1][-1].end:span.start] in DASHES:
            chains[-1].append(span)
        else:
            chains.append([span])
    data = request.data
    for chain in chains:
        if len(chain) == 1:
            yield chain[0]
        elif (len(chain) == 2 and text[chain[0].end:chain[1].start] in data["range_marks"]
              and not any(span.keep or span.fields["prefix"] or span.fields["suffix"] for span in chain)
              and _range_follows(text, chain[1].end, data, alone=True)):
            yield from request.language.join_range(*chain, "")
        else:
            yield from (replace(span, keep=True) for span in chain)


def _scale_elided(low: str, high: str, data) -> bool:
    """Whether the first end of `15-20 000` may stand for thousands: it has no group mark, the second end has one,
    and the first end is less than the first group of the second (module docstring)."""
    marks = data["number_marks"]["Latn"][0]["group"]
    groups = re.split(f"[{re.escape(marks)}]", high)
    return low.isdigit() and len(groups) > 1 and int(low) < int(groups[0])


@dataclass(frozen=True)
class BasqueRange(Range):
    """`10-20 bitartean`, `1 999-2 000 bitartean`: two numbers that a hyphen joins, the lower one first, before a
    word of the `range_followers` table (module docstring). Two numbers where the reading is not clear make no
    span, so the waiting rule keeps them as written, as `Osasunak 2-0` and `15-20 000 lagun`."""
    name: str = "basque_range"

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        for span in super().find(text, tokens, request):
            low, _, high = text[span.start:span.end].partition("-")
            if not (span.keep or span.fields["prefix"] or span.fields["suffix"] or _scale_elided(low, high, data)
                    or not _range_follows(text, span.end, data, alone=False)):
                yield span


@dataclass(frozen=True)
class BasqueMoney:
    """`5 €`, `3,25 €`, `1 €-etik`, `$5`: a number and a currency symbol of the `currencies` table. A dash right
    after a symbol is no minus sign, and two amounts that a dash joins are a range, as in `5 €-10 €` (`_ranges`).

    The reading puts the currency noun last, so a case ending written on the digits of `€5eko` belongs to the
    number and not to the noun: "bost euroeko" is wrong, and the amount stays as written."""
    name: str = "basque_money"
    form: Form = Form.MONEY

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return _ranges(self._amounts(text, request), text, request)

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
    is no minus sign, and two measures that a dash joins are a range, as in `5 km-10 km` (`_ranges`)."""
    name: str = "basque_measure"
    form: Form = Form.MEASURE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return _ranges(self._measures(text, request), text, request)

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
    `% 2-% 5`, are a range (`_ranges`)."""
    name: str = "basque_percent"
    form: Form = Form.PERCENT

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return _ranges(self._percents(text, request), text, request)

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
                    after = _symbol_suffix(text, number.end + len(gap) + len(sign), sign, data)
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
    "number_marks": {"Latn": [{"decimal": ",", "group": ". \u00a0\u202f"}]},
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
    "range_marks": ["-"],
    "range_followers": ["bitartean"],
})
"""The day period of each hour follows the table of Araua 203, pages 53 to 55, which gives hours 1 to 5, 11 to 15,
20, 21, 23, 24 and 0, and elides the hours between two hours that take the same word."""

LANGUAGE = LanguageSpec(
    code="eu",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("eu-ES"),),
    data=DATA,
    recognizers=(SHARED["lexicon"], RomanMonthDate(), KEPT_SPACE_GROUPS, LetterCode(), LawNumber(),
                 SHARED["date_numeric"], BasqueTime(), BasqueMoney(), SHARED["kept_money"], BasquePercent(),
                 BasqueMeasure(), BasqueRange(), SHARED["expression"], SHARED["fraction"], BasqueOrdinal(), Roman(),
                 BasqueAbbreviation(), SHARED["decimal"], SHARED["cardinal"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.DATE: speak_date, Form.TIME: speak_time, Form.MONEY: speak_money,
        Form.PERCENT: speak_percent, Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression,
        Form.FRACTION: speak_fraction, Form.RANGE: speak_range, Form.ORDINAL: speak_ordinal, Form.ROMAN: speak_roman,
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
    join_range=join_range,
)
