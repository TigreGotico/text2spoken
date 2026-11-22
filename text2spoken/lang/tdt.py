"""Tetun Dili: tdt-TL.

The file reads a numeric date, a clock time, a price, a telephone number, a percentage and a measure in Portuguese.
It leaves a bare cardinal as written.

The source is Catharina Williams-van Klinken and John Hajek, "Mixing numeral systems in Timor-Leste", NUSA 64
(2018): 65-94, DOI 10.5281/zenodo.1450774. Tetun Dili has three sets of numerals. Abstract, p. 65: "Speakers of
Tetun Dili, in Timor-Leste, commonly use three sets of numerals, namely native Tetun as well as numerals from the
languages of the two former colonial powers, Portuguese and Indonesian."

Section 10.1 (iv), p. 89, gives the choice for a written text that a voice reads aloud: "In formal contexts,
Indonesian numerals are normally avoided, just as other Indonesian loans are avoided in formal contexts and in
writing (Williams-van Klinken & Hajek 2018). In television reporting, Tetun numerals are favoured over Portuguese,
even for large numbers, for which most people normally avoid Tetun. On the other hand, the voiceover for written
announcements on television make overwhelming use of Portuguese for items such as telephone numbers, dates and
prices." So a date, a price and a telephone number read in Portuguese.

Section 7.1, p. 78, names the forms that take a borrowed numeral: "Indonesian and Portuguese are used for prices,
time and date, phone numbers, measurements, sequence, mathematics and sports scores [...]." The formal register of
section 10.1 (iv) avoids Indonesian, which leaves Portuguese. So a clock time, a percentage and a measure also read
in Portuguese. This is the reading of the project, and not a quote: the source names no voiceover use for them.

A numeric date: section 7.7.1, p. 85: "Dates can be in any language." It counts the years of the oral corpus, p. 86:
"Of the 290 examples of the years ‘two thousand ...’, 22% use Tetun rihun rua (mostly formal), 66% use Portuguese
dois míl (mostly formal), and 12% use Indonesian dua ribu (all informal)." Example (24), pp. 85-86, is a Portuguese
date in Tetun Dili: "Hau moris iha Zumalai iha dia déz de Abril, míl novi-sentus setenta i trés." ("I was born in
Zumalai on tenth April 1973.") Section 6.1: "borrowed numerals are used with much of the phrase-level grammar of
their own language".

A clock time: section 7.7.2, p. 86: "Time can be in any language, with Indonesian being the most common." A time
with a colon needs a time word right before it (design section 4.2), because `16:9` and `3:16` are no times. The
Tetun time word is `tuku`. Section 6.1, p. 76: "To state the time using a Tetun numeral, the noun tuku (from the verb
tuku meaning ‘punch’) must be used, e.g., tuku haat ‘four o’clock’." Example (25), p. 86, asks the time with it:
"Agora tuku hira?" ("What time is it?"). A time with `h`, as `9h30`, needs no time word.

A percentage and a measure: section 7.1, pp. 78-79: "If they are written as digits with a following percentage sign
or abbreviation, e.g., 70% or 75mm, then they can be read in any of the three languages, since the abbreviations for
most units of measurement are the same in all three." Section 7.6.4, example (22), p. 85, reads a percentage in
Portuguese: "sae ba noventa porsentu". The same section counts the formal oral texts, where Tetun is as common as
Portuguese: "There are 21 Portuguese numerals plus porsentu, as in (22), all of which are formal except one sein
porsentu (lit. 100%) ‘totally’. There are 23 porsentu followed by a Tetun numeral (all formal [...])". Section 7.7.4,
p. 87, says of weights and measures in oral texts: "50% are in Tetun, and the rest spread between Portuguese and
Indonesian". The file reads both in Portuguese, as a written form with a symbol, like a price.

A price: CLDR 49 `currencyData.json` gives Timor-Leste the US dollar, `"TL": [{"USD": {"_from": "1999-10-20"}}, ...]`,
and CLDR 49 `pt-TL/currencies.json` writes it `"symbol": "US$"`, `"symbol-alt-narrow": "$"`. The Banco Central de
Timor-Leste names the minor unit, "Coins in Circulation" (bancocentral.tl/currency/co_in_c/): "The official
currency of Timor-Leste is the United States dollar, which is legal tender for all payments made in cash. Since 10
November 2003 the Banco Central de Timor-Leste issued coins known as "centavos" minted especially to be used in the
country." So `US$ 1,50` reads "um dólar e cinquenta centavos", where `pt-PT` says "cêntimos".

A scale word after an amount: section 5.2, p. 73: "(ii) milhaun is from Portuguese milhão ‘million’. [...] In a
numeral expressed solely with Portuguese elements, the plural milhoens is used for more than one unit of millions,
e.g. déz milhoens ‘ten million’." Example (11), p. 78, reads an amount with it: "korenta milhoens de dolar-es" ("forty
million dollars"). The Tetun Wikipedia article "Timor-Leste" writes the plural `milloens`, as in "$ 48 milloens". So
`US$ 10 milhoens` reads "dez milhões de dólares". The Tetun and Indonesian scale words of Table 3, p. 71 (`atus`,
`ratus` ‘hundred’, `rihun`, `ribu` ‘thousand’) and of section 5.2 (`tokon`, `juta` ‘million’) take a Tetun or
Indonesian numeral, so an amount before one of them stays as written: `$5 rihun`.

The Portuguese words come from the `pt-PT` recognizers and verbalizers of the Portuguese file, which the file takes
from the loader when it reads a text, and from `spoken_date` of ovos-date-parser for `pt-PT`. So this file holds no
Portuguese table. CLDR 48 `parentLocales.json` gives Portuguese in Timor-Leste the European norm: "pt-TL": "pt-PT".
The day comes before the month: CLDR 48 `pt-TL/ca-gregorian.json` writes the `medium` date "dd/MM/y" and the `long`
date "d 'de' MMMM 'de' y", and the examples of the paper put the day first, as "loron lima fulan rua (lit. day 5.T
month 2.T) refers to the fifth day of February" (section 6.2). The paper spells a Portuguese numeral in Tetun
spelling (footnote 2: "Spelling of Portuguese numerals follows Tetun conventions."). The file writes the Portuguese
spelling, which the espeak `pt` voice of the speech stack reads.

A cardinal in digits stays as written, because the written text does not choose one reading. Section 10.1 (iv),
p. 89: "In television reporting, Tetun numerals are favoured over Portuguese". Section 7.1, pp. 78-79: "If numerals
are spelled out in written texts, they are almost always in Tetun. [...] However if numbers quantify a preceding
head noun, they must be read in Tetun, [...] e.g. kaixa 7 must be read as kaixa hitu (lit. box 7.T) ‘seven boxes’.
Alternatively, if the number quantifies a following head noun, it must be read in the language of that noun." A
number after a noun can also label it with a borrowed numeral. Section 6.2: "This is the use of a borrowed cardinal
numeral following a head noun of the same language, to function as an ordinal, e.g., Portuguese tópiku ún ‘topic
one’". Its example (9) contrasts "rejiaun ida" ‘a region’ with "rejiaun ún" ‘region one’. So a number after a noun
reads in Tetun when it counts, and in a borrowed numeral when it labels.

The file does not read a date with a written month, such as `10 Abril 1973`, yet. Section 10.1 (iv) gives it one
reading, in Portuguese, and the reading needs a table of the Tetun month names, which no source of this file gives.
"""
from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core import parsers
from text2spoken.core.language import LanguageSpec, Request, Variety, drop_affixes, merged_data, resolve
from text2spoken.core.recognizers import LEXICON, SHARED, speak_lexicon, written_shapes
from text2spoken.core.spans import Span, SpanContext
from text2spoken.core.tokens import Token, is_word_char
from text2spoken.errors import DeclinedReading
from text2spoken.params import OPTIONS, Form, NormalizationParams, freeze

PORTUGUESE = "pt-PT"
"""The variety of the Portuguese words: CLDR 48 `parentLocales.json`, "pt-TL": "pt-PT"."""

DATA = freeze({
    "defaults": {"date_order": "DMY"},
    "symbols": written_shapes()["symbols"],
})

TIMOR = freeze({
    "time_words": ["tuku"],
    "currencies": {"USD": {"minor": {"one": "centavo", "other": "centavos"}}},
    "scales": {"milhaun": "milhão de", "milhoens": "milhões de", "milloens": "milhões de"},
})
"""The Timor-Leste data over the `pt-PT` data: the Tetun time word, the centavo of the Banco Central and the Tetun
spellings of `milhão`."""

TETUN_SCALE = re.compile("[ \u00a0]*(?:[Aa]tus|[Rr]atus|[Rr]ihun|[Rr]ibu|[Tt]okon|[Jj]uta)")
"""A Tetun or Indonesian scale word right after a number: a Portuguese reading of the number stops before it."""


def portuguese(request: Request) -> Request:
    """The `pt-PT` request of the call, with `TIMOR` over its data, built once for each call."""
    if PORTUGUESE not in request.memo:
        pt = resolve(PORTUGUESE, NormalizationParams(forms=request.params.forms))
        request.memo[PORTUGUESE] = replace(pt, variety=Variety(pt.tag, merged_data(pt.variety.data, TIMOR)))
    return request.memo[PORTUGUESE]


@dataclass(frozen=True)
class Portuguese:
    """The `pt-PT` recognizers of one form, which read the text with the Portuguese request of the call."""
    form: Form

    @property
    def name(self) -> str:
        return f"portuguese_{self.form.value}"

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        pt = portuguese(request)
        for recognizer in pt.language.recognizers:
            if recognizer.form is self.form:
                for span in recognizer.find(text, tokens, pt):
                    scale = TETUN_SCALE.match(text, span.end)
                    if scale and (scale.end() == len(text) or not is_word_char(text[scale.end()])):
                        span = replace(span, keep=True)
                    yield span


def speak_portuguese(span: Span, context: SpanContext) -> str:
    """The `pt-PT` reading of a span that a `pt-PT` recognizer claims."""
    pt = portuguese(context.request)
    return pt.language.verbalizers[span.form](span, replace(context, request=pt))


def speak_date(span: Span, context: SpanContext) -> str:
    """The Portuguese date words: `12/11/2025` reads "doze de novembro de dois mil e vinte e cinco"."""
    fields = span.fields
    try:
        return parsers.spoken_date(PORTUGUESE, day=fields["day"], month=fields["month"], year=fields["year"])
    except ValueError as error:
        raise DeclinedReading(f"ovos-date-parser reads no date {fields['day']}/{fields['month']}: {error}") from error


READ_IN_PORTUGUESE = (Form.TIME, Form.MONEY, Form.TELEPHONE, Form.PERCENT, Form.MEASURE)

LANGUAGE = LanguageSpec(
    code="tdt",
    serves=(),
    cldr_aliases=("pt_PT",),
    varieties=(Variety("tdt-TL"),),
    data=DATA,
    recognizers=(LEXICON, SHARED["date_numeric"], *(Portuguese(form) for form in READ_IN_PORTUGUESE)),
    verbalizers={Form.LEXICON: speak_lexicon, Form.DATE: speak_date,
                 **dict.fromkeys(READ_IN_PORTUGUESE, speak_portuguese)},
    spellers={},
    attach=drop_affixes,  # the Portuguese verbalizers say the one suffix, the `h` of `14:30h`
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={"date_order": frozenset({"DMY", "MDY", "YMD"})},
    not_applicable=frozenset(OPTIONS) - {"date_order"},
)
