"""Tetun Dili: tdt-TL.

The file reads a numeric date in Portuguese numerals, and leaves every other number as written.

The source is Catharina Williams-van Klinken and John Hajek, "Mixing numeral systems in Timor-Leste", NUSA 64
(2018): 65-94, DOI 10.5281/zenodo.1450774. Tetun Dili has three sets of numerals. Abstract: "Speakers of Tetun Dili,
in Timor-Leste, commonly use three sets of numerals, namely native Tetun as well as numerals from the languages of the
two former colonial powers, Portuguese and Indonesian."

A numeric date reads in Portuguese. Section 7.7.1: "Dates can be in any language." Section 10.1 (iv) gives the
choice for a written text that a voice reads aloud: "In formal contexts, Indonesian numerals are normally avoided,
just as other Indonesian loans are avoided in formal contexts and in writing (Williams-van Klinken & Hajek 2018). In
television reporting, Tetun numerals are favoured over Portuguese, even for large numbers, for which most people
normally avoid Tetun. On the other hand, the voiceover for written announcements on television make overwhelming use
of Portuguese for items such as telephone numbers, dates and prices." Section 7.7.1 counts the years of the oral
corpus: "Of the 290 examples of the years ‘two thousand ...’, 22% use Tetun rihun rua (mostly formal), 66% use
Portuguese dois míl (mostly formal), and 12% use Indonesian dua ribu (all informal)." Example (24) is a Portuguese
date in Tetun Dili: "Hau moris iha Zumalai iha dia déz de Abril, míl novi-sentus setenta i trés." ("I was born in
Zumalai on tenth April 1973.") Section 6.1: "borrowed numerals are used with much of the phrase-level grammar of
their own language".

The Portuguese words come from `spoken_date` of ovos-date-parser for `pt-PT`, the call that the Portuguese file
makes, so this file holds no Portuguese table. CLDR 48 `parentLocales.json` gives Portuguese in Timor-Leste the
European norm: "pt-TL": "pt-PT". The day comes before the month: CLDR 48 `pt-TL/ca-gregorian.json` writes the
`medium` date "dd/MM/y" and the `long` date "d 'de' MMMM 'de' y", and the examples of the paper put the day first,
as "loron lima fulan rua (lit. day 5.T month 2.T) refers to the fifth day of February" (section 6.2). The paper
spells a Portuguese numeral in Tetun spelling (footnote 2: "Spelling of Portuguese numerals follows Tetun
conventions."). The file writes the Portuguese spelling, which the espeak `pt` voice of the speech stack reads.

These forms stay as written, because the written text does not choose one reading:

- A clock time. Section 7.7.2: "Time can be in any language, with Indonesian being the most common."
- A cardinal in digits. Section 7.1: "If numerals are spelled out in written texts, they are almost always in
  Tetun. If they are written as digits with a following percentage sign or abbreviation, e.g., 70% or 75mm, then
  they can be read in any of the three languages [...]. However if numbers quantify a preceding head noun, they
  must be read in Tetun, [...] e.g. kaixa 7 must be read as kaixa hitu (lit. box 7.T) ‘seven boxes’.
  Alternatively, if the number quantifies a following head noun, it must be read in the language of that noun."
  A number after a noun can also label it with a borrowed numeral. Section 6.2: "This is the use of a borrowed
  cardinal numeral following a head noun of the same language, to function as an ordinal, e.g., Portuguese tópiku
  ún ‘topic one’". So `kaixa 7` reads "kaixa hitu" when it counts, and in Portuguese when it labels.
- A price and a telephone number. Section 10.1 (iv) gives Portuguese for a voiceover, and sections 7.4.3 and 7.4.4
  give Indonesian for everyday speech. A Portuguese reading needs the currency and telephone tables of the
  Portuguese file, which a language file does not import.
"""
from __future__ import annotations

from text2spoken.core import parsers
from text2spoken.core.language import LanguageSpec, Variety
from text2spoken.core.recognizers import LEXICON, SHARED, speak_lexicon, written_shapes
from text2spoken.core.spans import Span, SpanContext
from text2spoken.errors import DeclinedReading
from text2spoken.params import OPTIONS, Form, freeze

PORTUGUESE = "pt-PT"
"""The variety of the Portuguese date words: CLDR 48 `parentLocales.json`, "pt-TL": "pt-PT"."""

DATA = freeze({
    "defaults": {"date_order": "DMY"},
    "symbols": written_shapes()["symbols"],
})


def speak_date(span: Span, context: SpanContext) -> str:
    """The Portuguese date words: `12/11/2025` reads "doze de novembro de dois mil e vinte e cinco"."""
    fields = span.fields
    try:
        return parsers.spoken_date(PORTUGUESE, day=fields["day"], month=fields["month"], year=fields["year"])
    except ValueError as error:
        raise DeclinedReading(f"ovos-date-parser reads no date {fields['day']}/{fields['month']}: {error}") from error


LANGUAGE = LanguageSpec(
    code="tdt",
    serves=(),
    cldr_aliases=("pt_PT",),
    varieties=(Variety("tdt-TL"),),
    data=DATA,
    recognizers=(LEXICON, SHARED["date_numeric"]),
    verbalizers={Form.LEXICON: speak_lexicon, Form.DATE: speak_date},
    spellers={},
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=False,
    options={"date_order": frozenset({"DMY", "MDY", "YMD"})},
    not_applicable=frozenset(OPTIONS) - {"date_order"},
)
