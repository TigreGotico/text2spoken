"""English: en-GB, the default variety, and en-US.

Number words come from CLDR RBNF. American English writes no "and" in the whole part of a number, and
British English writes "one hundred and one" (Wikipedia, "English numerals"), so each variety names its rule
set. The design page `text2spoken-design.md`, section 5.4, gives the measured reason for each speller.

A mixed number reads its whole part, "and", and its fraction: Wikipedia, "Fraction", Mixed numbers: "The mixed number
2+3/4 is spoken two and three quarters or two and three fourths", "with the integer and fraction portions connected by
the word and". A numerator 1 over 2 or 4 reads "a": Wikipedia, "English numerals", Fractions and decimals: "Fractions
together with an integer are read as follows": "one and a half", "six and a quarter", "seven and five eighths". Every
other fraction reads as a fraction alone reads, as "two and one-third".

Unit words come from CLDR 49 (`cldr-units-full`, the `long` patterns of en-GB and en). A symbol that cannot be a
plain word, such as `km/h`, `°C` or `µm`, reads with no list. `unit_symbols` names the symbols made only of
letters that read as units: the SI symbols `kg`, `g`, `mg`, `km`, `m`, `cm`, `mm` and `ml`, and `mph`, `MHz`,
`GHz` and `MB`. Other CLDR symbols are also words or letters of running text, so `1 in 3`, `Plan 2 A` and
`29 GB golds` read no unit. `GB` names Great Britain as often as gigabytes (design section 16), and `ft.` names
"featuring" in a music credit, as in `Maroon 5 ft. Cardi B`.

Currency names and currency symbols come from CLDR 49 (`cldr-numbers-full`, `currencies.json` of en-GB, en-001
and en), and a symbol with a currency sign reads with no list: `R$ 500` reads "five hundred Brazilian reals" and
`₹50` "fifty Indian rupees". `currency_symbols` names the ISO 4217 codes that read, as in `CHF 20` and `20 EUR`.
The `currencies` table replaces a CLDR name that carries the country. CLDR names USD "US dollar", GBP "British
pound" and JPY "Japanese yen", and the CLDR 49 en annotations name the signs `$` "dollar", `£` "pound" and `¥`
"yen", so these currencies read "dollar", "pound" and "yen". The table also assigns a shared sign. CLDR 49 en gives
USD the symbol `$` and JPY the symbol `¥`, but en-001, the parent of en-GB, writes `US$` and `JP¥`, and en-GB
shares the narrow `$` and `¥` between currencies. The en symbol and the en annotation name keep `$` for the dollar
and `¥` for the yen in en-GB. en-US reads `US$`, the symbol of USD in CLDR en-001 and root, as the dollar too.

`Prof.` reads "Professor" also where no name follows it, as in `The Prof. arrived.`: Wiktionary, "Prof.", gives an
English noun, with the plural `Profs.`, that abbreviates Professor (after the Collins English Dictionary). A decimal
comma before or after `€`, as in `23,88 €`, reads in both varieties, because CLDR 49 writes the euro with that comma in
de, es, fr and it, and an en group has three digits.

A character that no other form claims reads by its CLDR 49 annotation name (`cldr-annotations-full` and
`cldr-annotations-derived-full`): `©` reads "copyright", `→` "right-pointing arrow" and `¶` "paragraph mark".

An e-mail or web address reads the name of each symbol. Wiktionary gives each name: "@" is "at" ("@", sense 2:
the separator in an e-mail address, "at" the domain name), "." is "dot" ("dot", usage note: "In email addresses
and URLs, it is conventionally read aloud as 'dot'"), "-" is "dash" ("dash", sense 1.1: "A hyphen or minus
sign"), and "_", "/", ":", "~", "#", "?", "=", "&" and "+" are "underscore", "slash", "colon", "tilde", "hash",
"question mark", "equals", "ampersand" and "plus" (the entries of the same names, and "hash", sense 3: "The #
symbol"). The Wiktionary example "en.wiktionary.org", read aloud "E-N-dot-wiktionary-dot-org", spells the
two-letter label and reads the longer labels as words. A letter reads by the name that Wikipedia, "English
alphabet", Letter names, gives from the Oxford English Dictionary, with "zed" in British and "zee" in American
English. C reads "see", another spelling of its name, because misaki, an English phonemizer, has no "cee" in its
American lexicon (Wiktionary, "see", Etymology 3, Noun: "Alternative form of cee; the name of the Latin script
letter C/c."). A keeps "a". English phonemizers read "a" inside a phrase as the article, but espeak-ng and misaki read
it as the letter name before a full stop, as in "u ess a.". The other spelling "ay" reads as /aɪ/, the name of
I, in espeak-ng.

A run of capital letters reads by the `LETTERS` form (design section 4.6) when the caller turns the form on. A run
that splits into English syllables stays as written, and any other run reads letter by letter. The syllable sets are
the spellings of the clusters in Wikipedia, "English phonology", Phonotactics, a secondary source: it gives English
"clusters of up to three consonants in the syllable onset and up to four consonants in the syllable coda" (citing
Hansen 2004, p. 91), and its onset and coda tables carry a "Citation needed" mark. An onset is one of "All
single-consonant phonemes except /ŋ/", or a cluster of the onset table, spelled as in its example words: play, blood,
clean, glove, prize, bring, tree, dream, crowd, green, twin, dwarf, quick, floor, sleep, friend, three, shrimp, what,
swoon, thwart, speak, stop, skill, smile, snow, sphere, split, sclera, spring, street, scream and square. The /sk/ of
"sclera" and "scream" is spelled sc, so sc is an onset too. The letter x spells /ks/, which is no onset ("xylophone"
begins with /z/), so x is no onset. A coda is one of "The single consonant phonemes except /h/, /w/, /j/", or a
cluster of the coda table, spelled as in help, bulb, belt, hold, milk, belch, harp, orb, fort, beard, mark, morgue,
arch, golf, solve, wealth, else, Welsh, dwarf, carve, north, Mars, marsh, film, kiln, arm, born, snarl, jump, tent,
end, lunch, pink, sing, triumph, month, bronze, left, crisp, lost, ask, opt, act, fifth, depth, lapse, klutz, width,
box, next and horst. The section above the coda table says: "Most (in theory, all) of the following except those that
end with the sibilants /s/, /z/, /ʃ/, /ʒ/, /tʃ/ or /dʒ/ can be extended with /s/ or /z/ representing the morpheme
-s/-z." So each coda that does not end in s, z, x, sh or ch also takes an s, as in the ds of AIDS, the rts of SPORTS
and the nts of EVENTS. The tables give r and its clusters "in rhotic varieties" only, but en-GB writes the r that it
does not say, so r stays a coda letter. ch, sh, th and ng spell one consonant each (Wikipedia, "English orthography":
"chin", "shin", "thing", "strength"). The vowels are a, e, i, o and u, and the spellings with w and y in the table
"Combinations of vowel letters" of Wikipedia, "English orthography", which "includes ⟨h, w, y⟩ when they represent
vowel sounds": y as in myth and sky, aw as in flaw, ew as in dew, and ow as in owl. The rule reads CIA, IRS, USA, IBS
and IDS as words, and Wiktionary spells them letter by letter: CIA /ˌsiːˌaɪˈeɪ/, IRS /ˈaɪ.ɑɹ.ɛs/, USA /juː ɛs ˈeɪ/,
IBS /aɪ.biːˈɛs/ and IDS /aɪ diː ɛs/. So `letter_runs` holds them.

A Roman numeral reads only where a rule below gives its reading, and every other numeral stays as written: a
capitalised word alone does not tell a title of a work, a product or a council from a name, so `Apollo XIII`,
`Vatican II`, `Rocky II` and `Start IV fluids` keep the numeral. On every path but a noun of `roman_nouns`, the
value is at most 30.

A regnal number reads "the" and the ordinal: `Henry VIII` reads "Henry the Eighth". Wikipedia, "Roman numerals", Modern
use: "Names of monarchs and popes, e.g. Elizabeth II of the United Kingdom, Pope Leo XIV. These are referred to as
regnal numbers and are usually read as ordinals; e.g. II is pronounced "the second"." The BBC News style guide,
"royalty", writes the numeral: "We use Roman numerals with names (eg: Henry VIII, Charles III)". A regnal number follows
a regnal title and a name, as in `King Charles III`, or a name of `regnal_names`. Only spaces part the title, the name
and the numeral, or one mark of `apposition_marks` parts the title from a name of `regnal_names`, as an apposition does
in `the Holy Roman Emperor, Henry V`, `our king [Charles I]` and `Kaiser (Emperor) Wilhelm I`. The marks are the comma,
the parentheses, the square brackets, the straight and curly quotes, and the guillemets `«` and `»`, which Wikipedia,
"Guillemet", calls "Double chevrons used as quotation marks". A single quote, `'` or `’`, parts them only when it opens
a quote, with a space before it and the name after it, as in `the emperor 'Pedro I'`. Wikipedia, "Quotation mark": "The
closing or right single quotation mark is identical in form to the apostrophe", and Wikipedia, "English possessive",
says that a singular noun ending in -s is "also spelled by adding only an apostrophe". So in `the princess' Charles I
danced with` the apostrophe parts nothing, and the pronoun stays. The pronoun stays in `the title of king, Which I
conceive` and `a queen / Best I've` too, and a colon, a slash, a dash, two marks or a mark before a name outside
`regnal_names` leave the numeral as written. `Coretta Scott King, Malcolm X` reads "Malcolm the Tenth", because the
surname King is also a title and Malcolm is the name of four kings of Scotland. The regnal titles are those that
Wikipedia, "Regnal number", names: "kings, queens regnant, popes, and rarely princes and princesses", with Saint,
Emperor, Empress, Tsar and Tsarina. `regnal_names` holds the names that carry a regnal number in the Wikipedia lists of
English monarchs, Scottish monarchs, French monarchs, Frankish kings, Spanish monarchs, popes, Holy Roman emperors,
Russian emperors and Byzantine emperors, in their English form, such as Adrian, the name of six popes (Wikipedia, "List
of popes": "Adrian I" to "Adrian VI"), so `Adrian IV` reads "Adrian the Fourth". It also holds the Spanish forms of the
Spanish list, such as Isabel ("Isabel II, la de los Tristes Destinos"), the German forms of the German and Austrian
emperors (Wilhelm, Franz and Karl), Konrad, the German form of four German kings (German Wikipedia, "Liste der
römisch-deutschen Herrscher": "Konrad I" to "Konrad IV"), and Valentinian, the name of two Roman emperors of the West
(Wikipedia, "Valentinian II" and "Valentinian III"). It holds the names as they stand in the Wikipedia lists of Polish
(Jan, Władysław, Stanisław), Hungarian (Béla, also written Bela, and Ladislaus), Bosnian (Tvrtko), Portuguese (João,
Maria, Pedro), Swedish (Gustav, Carl), Danish (Christian), Armenian (Tiridates, Tigranes), Mercian (Ceolwulf), Spartan
(Cleomenes), Sri Lankan (Parakramabahu) and Jordanian (Abdullah) monarchs, of the pharaohs (Amenhotep) and of the rulers
of Bavaria (Welf), and in the Wikipedia articles on the monarchs of Jerusalem (Baldwin) and Cambodia (Jayavarman), the
Kabakas of Buganda (Mutesa), the Grand Princes of Kiev (Vladimir), the tlatoque (Moctezuma), the Duchy of Masovia
(Siemowit), Lazica (Tzath), Huahine (Tehaapapa), the Chalukya and Pallava dynasties (Kirtivarman, Vikramaditya,
Narasimhavarman), the Achaemenid Empire (Darius, Artaxerxes) and the Indo-Greek Kingdom (Menander).

A generational suffix from II to IV reads the ordinal too: `Hank Williams III` reads "Hank Williams the Third".
Wikipedia, "Name suffix": "he can use the II suffix, which is pronounced "the second"". The suffix follows exactly two
words, a given name of `text2spoken/data/en/given_names.json` and a surname of `text2spoken/data/en/surnames.json`, and
no capitalised word comes before them in the clause, so `Mary Jane Smith III` and `Grace Hopper Building II` stay as
written. The given-name file holds 6,515 names: the union of the 1,000 names of each sex with the most births in each
year from 1900 to 2020, in the baby-name data of the US Social Security Administration. The surname file holds the 1,000
most frequent surnames of the 2010 US census, in capitals. Both are public-domain records, and
`scripts/extract_names.py` writes the two files. Many given names are also words, such as Star, Golden and Major, so a
title of a work can start with one. The surname check keeps the numeral of such a title: `Star Trek II`, `Golden Axe
III` and `Peter Pan II` stay as written. A title of a work, a company, a product or a place can also be built from a
given name and a surname of the two lists, and such a name reads as a person: `Harry Potter IV`, `Morgan Stanley
III` and `Forest Hill III` read "the Fourth" and "the Third". The text alone does not tell this class from a person.

After a noun of `roman_nouns`, which names a series, a numeral reads as a cardinal: `World War II` reads "World War
Two", `Super Bowl LVII` "Super Bowl Fifty-Seven" and `chapter IV` "chapter four". The BBC News style guide, "World
War": "write out World War One and World War Two". Wikipedia, "Roman numerals", Modern use, lists "Book volume and
chapter numbers, as well as the several acts within a play", "The Super Bowl, the annual championship game of the
National Football League (e.g. Super Bowl XLII; Super Bowl 50 was a one-time exception", and says that "grade IX" is
"sometimes seen for grade 9". Wikipedia, "Star Wars (film)", gives the subtitle "Episode IV – A New Hope" and the
draft title "Adventures of the Starkiller, Episode One: The Star Wars", and the citations of Wikipedia, "Roman
numerals", number the parts of a book of Caesar as "Book II, Section 4". So `roman_nouns` holds chapter, volume,
book, act, grade, episode and section, the names "World War" and "Super Bowl", and, by a ruling of the maintainer,
part, phase, class, level, stage, type and war. The cardinal takes a capital on each word after a capitalised noun,
as the BBC writes "World War Two".

A numeral of one letter reads only after a regnal title and a name, as in `King Henry V`, and after a noun of two
words, as in `World War I`. So `the book I read` keeps its pronoun, and `Malcolm X` stays as written: Malcolm is
also the name of four kings of Scotland. The word before the numeral reads it only when spaces alone part them. A
word of `function_words` in any case, such as the `The` that starts a sentence, reads no numeral.

`roman_words` holds the numerals that are also an initialism or a word, from the same measurement as `pt.py` (FLORES+
devtest and "meio milhão de frases", judged in
`knowledge/wiki/audits/text2spoken-langs/letters-limits/evidence/roman-runs.tsv`) and from Wiktionary, which gives each
one an English sense: CC ("init of carbon copy"), CD ("initialism of compact disc"), CDI ("capacitor discharge
ignition"), CDL ("commercial driver's licence"), CI ("cochlear implant"), CL ("light cruiser"), CM ("chief minister"),
CML ("capital market line"), CV ("curriculum vitae"), DC ("District of Columbia"), DIV ("div": "A section"), DL
("download"), MC ("master of ceremonies"), MCI ("mild cognitive impairment"), MD ("Maryland"), MDC ("Metropolitan
Detention Center"), MI ("Michigan"), MIX ("mix": "To stir together"), ML (Wikipedia, "Mercedes-Benz M-Class": "ML"
badging, "e.g. ML 320"), MM ("Master of Music"), MV ("motor vehicle"), MX ("mail exchanger") and XL ("extra large").
After a noun of `roman_nouns`, a numeral of `roman_words` reads only after a noun of `roman_letter_nouns`, and only when
no word in lowercase follows it, because the word that follows a size or an initialism names the thing it qualifies:
`Chapter XL.` and `Super Bowl XL Champions` read the numeral, and `chapter XL now`, `Grade XL size`, `type MX record`
and `class MV Tacoma` stay as written. `roman_letter_nouns` holds the nouns of `roman_nouns` whose members take numbers
and never letters, as in `pt.py`: chapter, volume, book, act and episode, the parts of a work that Wikipedia, "Roman
numerals", and Wikipedia, "Star Wars (film)", number, and war, "World War" and "Super Bowl". The other nouns label their
members with letters too, so after them a numeral of `roman_words` is a label as often as a number, and it stays as
written, as in `He drove a Class CL.` and `See Section DIV.`. A count over the 1.8 million lines of wikitext-103 found a
capital letter alone (B, E, F, G or H) as a label after class (76 times), type (39), part (12), phase (9), grade (6),
section (5) and stage (3), as in `Class B`, `Type B service areas` and `Section B`, and the ruling for `nível` in
`pt.py` gives levels. It found volume once (`Volume F` of the International Tables for Crystallography), and chapter,
book, act and episode never (the count is in
`knowledge/wiki/audits/text2spoken-langs/letters-limits/followup-r3/letter-labels.txt`). Any other numeral after a noun
of `roman_nouns` reads with no cap, as `Super Bowl LVII`.

In a clause in capitals, a two-letter run of `letter_words` reads as a word, so `DO NOT ENTER` keeps `DO`, and `IF
IT IS` keeps each word. A clause in capitals is the text between two marks of a clause, a full stop, a comma, a
semicolon, a colon, a bracket, a quote or the edge of the text, where every word with a letter is in capitals, and
that holds two words or more. A word is a run that reads as a word, so a code that reads letter by letter, such as
`AGR` in `AO 1334 AGR`, does not count. English has no word lexicon in the stack of this library, so `letter_words`
is its only word check. Wiktionary gives each word a part of speech of its English section: "do", "is", "be", "go"
and "am" are verbs, "no" and "my" determiners, "to", "in", "on", "at", "of", "up" and "by" prepositions, "it", "we",
"me" and "he" pronouns, "so", "or", "as" and "if" conjunctions, and "an" an article. "us" is a pronoun too, and it
stays out of the set, because `US` names the United States in a text in capitals as often as the pronoun. The
capitals alone "I", a pronoun, and "A", an article, are words of `letter_words` too, so `I DO` and `I AM ON IT` keep
each word. Outside a text in capitals, a run of two letters reads letter by letter, so `TV` and `PC` are spelled. A
Roman numeral right after a word of `letter_words` does not read, because a numeral follows a name or a noun, so `IF
XIV` keeps `XIV` as a run.

The digits of a run read as a cardinal when the letters read as a word, as in `COVID19` ("COVID nineteen"), or when
they are one to three digits with no leading zero, as in `B52` ("bee fifty-two") and `M25` ("em twenty-five"). No
usage source gives the reading of a road name such as `M25`, so this reading is a ruling of the maintainer.

Digits joined to a CLDR unit symbol of two capital letters or more read as a measure, as in `10GB` ("ten
gigabytes"), because a run of capitals that touches digits is no word of running text. `unjoined_symbols` holds
`CD`, the CLDR en symbol of the carat, because a `2CD` set holds two compact discs (Wiktionary, "CD": "initialism of
compact disc"). It holds `ML`, the CLDR symbol of the megalitre, because CLDR also names `mL` the millilitre, so
`ML` in capitals may be either unit, and `2ML` stays as written.
"""
from __future__ import annotations

import json
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import cache
from importlib.resources import files

from text2spoken.core.color import speak_color
from text2spoken.core.currencies import currency_name, currency_table
from text2spoken.core.dates import is_valid
from text2spoken.core.electronic import speak_electronic
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.letters import speak_letters
from text2spoken.core.numbers import Number, written_amount
from text2spoken.core.recognizers import (PHONE_PLANS, SHARED, DateNumeric, Telephone, _edge, amount_words, join_ranges,
                                          numbers_in, signed, speak_abbreviation, speak_cardinal, speak_decimal,
                                          speak_expression, speak_fraction as core_speak_fraction, speak_idiom,
                                          speak_lexicon, speak_ordinal,
                                          speak_percent, speak_range, speak_telephone)
from bisect import bisect_right

from text2spoken.core.spans import Features, Span, SpanContext, clause_breaks, clause_window, context_words
from text2spoken.core.spellers import RbnfSpeller, bounded_integer, spell_digits
from text2spoken.core.symbols import speak_emoji, speak_symbol
from text2spoken.core.times import twelve_hour
from text2spoken.core.tokens import Token, fold_digits, is_bounded, is_letter, is_word_char, one_digit_set
from text2spoken.core.units import unit_reading, unit_table
from text2spoken.params import FrozenMap, Form, freeze

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
_MONTH = "(" + "|".join(MONTHS) + ")"
_ORDINAL_MARK = "(?:st|nd|rd|th)"

COLORS = {
    "000000": "black", "0000cd": "medium blue", "0000ff": "blue", "006400": "dark green", "008000": "green",
    "008080": "teal", "008b8b": "dark cyan", "00bfff": "deep sky blue", "00ced1": "dark turquoise",
    "00fa9a": "medium spring green", "00ff00": "lime", "00ff7f": "spring green", "00ffff": "cyan",
    "191970": "midnight blue", "1e90ff": "dodger blue", "20b2aa": "light sea green", "228b22": "forest green",
    "2e8b57": "sea green", "2f4f4f": "dark slate gray", "32cd32": "lime green", "3cb371": "medium sea green",
    "40e0d0": "turquoise", "4169e1": "royal blue", "4682b4": "steel blue", "483d8b": "dark slate blue",
    "48d1cc": "medium turquoise", "4b0082": "indigo", "556b2f": "dark olive green", "5f9ea0": "cadet blue",
    "6495ed": "cornflower blue", "66cdaa": "medium aquamarine", "696969": "dim gray", "6a5acd": "slate blue",
    "6b8e23": "olive drab", "708090": "slate gray", "778899": "light slate gray", "7b68ee": "medium slate blue",
    "7cfc00": "lawn green", "7fff00": "chartreuse", "7fffd4": "aquamarine", "800000": "maroon", "800080": "purple",
    "808000": "olive", "808080": "gray", "87ceeb": "sky blue", "87cefa": "light sky blue", "8a2be2": "blue-violet",
    "8b0000": "dark red", "8b008b": "dark magenta", "8b4513": "saddle brown", "8fbc8b": "dark sea green",
    "90ee90": "light green", "9370db": "medium purple", "9400d3": "dark violet", "9932cc": "dark orchid",
    "9acd32": "yellow-green", "a0522d": "sienna", "a52a2a": "brown", "add8e6": "light blue",
    "b0c4de": "light steel blue", "b0e0e6": "powder blue", "b22222": "firebrick", "b8860b": "dark goldenrod",
    "ba55d3": "medium orchid", "bc8f8f": "rosy brown", "bdb76b": "dark khaki", "c0c0c0": "silver",
    "cd5c5c": "indian red", "d2691e": "chocolate", "d2b48c": "tan", "d3d3d3": "light gray", "d8bfd8": "thistle",
    "da70d6": "orchid", "daa520": "goldenrod", "dc143c": "crimson", "dcdcdc": "gainsboro", "dda0dd": "plum",
    "deb887": "burlywood", "e0ffff": "light cyan", "e6e6fa": "lavender", "e9967a": "dark salmon", "ee82ee": "violet",
    "f08080": "light coral", "f0e68c": "khaki", "f0f8ff": "alice blue", "f0ffff": "azure", "f4a460": "sandy brown",
    "f5deb3": "wheat", "f5f5dc": "beige", "f5fffa": "mint cream", "f8f8ff": "ghost white", "fa8072": "salmon",
    "faebd7": "antique white", "faf0e6": "linen", "fafad2": "light goldenrod yellow", "fdf5e6": "old lace",
    "ff0000": "red", "ff00ff": "magenta", "ff1493": "deep pink", "ff6347": "tomato", "ff69b4": "hot pink",
    "ff7f50": "coral", "ff8c00": "dark orange", "ffa07a": "light salmon", "ffa500": "orange", "ffb6c1": "light pink",
    "ffc0cb": "pink", "ffd700": "gold", "ffdab9": "peach puff", "ffdead": "navajo white", "ffe4b5": "moccasin",
    "ffe4c4": "bisque", "ffe4e1": "misty rose", "ffebcd": "blanched almond", "ffefd5": "papaya whip",
    "fff0f5": "lavender blush", "fff5ee": "seashell", "fff8dc": "cornsilk", "fffacd": "lemon chiffon",
    "fffaf0": "floral white", "fffafa": "snow", "ffff00": "yellow", "ffffe0": "light yellow", "fffff0": "ivory",
    "ffffff": "white",
}
"""Seeded by `scripts/seed_colors.py en` from the ovos-color-parser palette `en-US/dot-net-colors.json`."""


@cache
def _names(file: str) -> frozenset[str]:
    """The `names` field of a person-name list of `text2spoken/data/en/`, read on first use, because importing a
    language file reads no file (contract clause 12)."""
    return frozenset(json.loads((files("text2spoken") / "data" / "en" / file).read_text(encoding="utf-8"))["names"])


_CODAS = [*"bcdfgklmnprstvxz", "ch", "sh", "th", "ng", "lp", "lb", "lt", "ld", "lk", "lch", "rp", "rb",
          "rt", "rd", "rk", "rg", "rch", "lf", "lv", "lth", "ls", "lsh", "rf", "rv", "rth", "rs", "rsh",
          "lm", "ln", "rm", "rn", "rl", "mp", "nt", "nd", "nch", "nk", "mph", "nth", "nz", "ft", "sp",
          "st", "sk", "pt", "ct", "fth", "pth", "ps", "tz", "dth", "xt", "rst"]

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ".", "group": ","}, {"decimal": ",", "group": "."}]},
    "defaults": {"date_order": "DMY", "clock": "12h", "minute_style": "number", "decimal_mark": ".",
                 "scale": "short"},
    "sign_words": {"-": "minus", "+": "plus"},
    "decimal_word": "point",
    "digit_words": ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"],
    "leads": {"#": "number", "-": ""},
    "fraction_names": {"2": ["half", "halves"], "4": ["quarter", "quarters"]},
    "mixed_word": "and",
    "idioms": {"24/7": "twenty-four seven", "50/50": "fifty-fifty"},
    "range_word": "to",
    "range_marks": ["-", "–"],
    "clock_marks": [{"mark": ":", "seconds": True, "needs": "evidence"},
                    {"mark": ".", "seconds": False, "needs": "day_period"}],
    "dimension_marks": ["x", "×"],
    "dimension_word": "by",
    "operators": {"+": "plus", "−": "minus", "×": "times", "÷": "divided by", "=": "equals"},
    "time_words": ["at", "from", "until", "till", "since", "before", "after", "around"],
    "year_words": ["in", "since", "until", "till", "during", "circa", "year"],
    "year_links": ["and", "or", "to"],
    "function_words": ["a", "an", "the", "and", "or", "but", "so", "then", "to", "in", "on", "at", "by",
                       "for", "from", "with", "as", "after", "before", "until", "since", "when", "while", "where",
                       "he", "she", "it", "we", "they", "you", "his", "her", "its", "our", "their", "this",
                       "that", "there", "was", "were", "is", "are", "had", "has", "have", "many", "some", "all",
                       "now", "immediately", "today", "tonight"],
    "day_periods": {"am": ["am", "a.m.", "AM", "A.M."], "pm": ["pm", "p.m.", "PM", "P.M."]},
    "spoken_periods": {"am": "AM", "pm": "PM"},
    "minute_phrases": {"0": "{hour} o'clock", "15": "quarter past {hour}", "30": "half past {hour}",
                       "45": "quarter to {next_hour}"},
    "months": MONTHS,
    "numeric_date_reading": {"full": "the {day} of {month} {year}", "no_year": "the {day} of {month}"},
    "currencies": {
        "USD": {"one": "dollar", "other": "dollars", "minor": {"one": "cent", "other": "cents"}},
        "GBP": {"one": "pound", "other": "pounds", "minor": {"one": "penny", "other": "pence"}},
        "EUR": {"minor": {"one": "cent", "other": "cents"}},
        "JPY": {"one": "yen", "other": "yen", "minor": {"one": "sen", "other": "sen"}},
    },
    "currency_symbols": ["USD", "EUR", "GBP", "JPY", "CHF"],
    "scales": {"thousand": "thousand", "million": "million", "billion": "billion", "trillion": "trillion",
               "k": "thousand", "m": "million", "bn": "billion"},
    "percent": {"signs": ["%"], "position": "after", "word": "per cent"},
    "unjoined_symbols": ["CD", "ML"],
    "unit_symbols": ["kg", "g", "mg", "km", "m", "cm", "mm", "mph", "ml", "MHz", "GHz", "MB"],
    "phone_words": ["phone", "telephone", "tel", "call", "dial", "ring", "text", "mobile", "cell", "fax"],
    "short_codes": ["000", "101", "111", "112", "211", "311", "411", "511", "611", "711", "811", "911", "988", "999"],
    "list_links": ["and", "or"],
    "phone_shapes": ["[(][2-9][0-9]{2}[)] [2-9][0-9]{2}[- ][0-9]{4}", "[2-9][0-9]{2}-[2-9][0-9]{2}-[0-9]{4}"],
    "phone_unit_shapes": ["(?:[(]0[0-9]*[)]|0[0-9]*)(?: [0-9]+)+"],
    "phone_kept_shapes": ["[1-9][0-9]{0,2}(?: [0-9]{3})+"],
    "no_phone_shapes": ["(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})"],
    "color_words": ["color", "colour", "colors", "colours"],
    "colors": COLORS,
    "titles": {"Dr.": "Doctor", "Mr.": "Mister", "Mrs.": "Missus", "Prof.": "Professor",
               "Dr": "Doctor", "Mr": "Mister", "Mrs": "Missus"},
    "abbreviations": {"etc.": "et cetera", "e.g.": "for example", "i.e.": "that is", "vs.": "versus",
                      "Prof.": "Professor"},
    "sentence_final": ["etc.", "Prof."],
    "number_abbreviations": {"No.": "number"},
    "symbols": {"%": "percent", "$": "money", "£": "money", "€": "money", "¥": "money", "°": "measure",
                "×": "measure"},
    "ordinal_marks": ["st", "nd", "rd", "th"],
    "electronic_symbols": {"@": "at", ".": "dot", "-": "dash", "_": "underscore", "/": "slash", ":": "colon",
                           "~": "tilde", "#": "hash", "?": "question mark", "=": "equals", "&": "ampersand",
                           "+": "plus"},
    "letter_names": dict(zip("abcdefghijklmnopqrstuvwxyz", (
        "a", "bee", "see", "dee", "e", "ef", "gee", "aitch", "i", "jay", "kay", "el", "em", "en", "o", "pee", "cue",
        "ar", "ess", "tee", "u", "vee", "double-u", "ex", "wye", "zed"))),
    "electronic_vowels": ["a", "e", "i", "o", "u"],
    "electronic_schemes": {"http": "read", "https": "read", "ftp": "read"},
    "electronic_tlds": ["com", "org", "net", "edu", "gov", "uk"],
    "letter_vowels": ["a", "e", "i", "o", "u", "y", "aw", "ew", "ow"],
    "letter_onsets": [*"bcdfghjklmnprstvwyz", "ch", "sh", "th", "ph", "wh", "qu", "pl", "bl", "cl", "gl", "pr", "br",
                      "tr", "dr", "cr", "gr", "tw", "dw", "fl", "sl", "fr", "thr", "shr", "sw", "thw", "sp", "st",
                      "sk", "sm", "sn", "sph", "spl", "sc", "scl", "spr", "str", "scr", "squ"],
    "letter_codas": [*_CODAS, *(coda + "s" for coda in _CODAS if not coda.endswith(("s", "z", "x", "sh", "ch")))],
    "regnal_titles": ["King", "Queen", "Pope", "Prince", "Princess", "Saint", "Emperor", "Empress", "Tsar", "Tsarina",
                      "king", "queen", "pope", "prince", "princess", "saint", "emperor", "empress", "tsar", "tsarina"],
    "apposition_marks": [",", "(", "[", '"', "“", "‘", "'", "«", ")", "]", "”", "’", "»"],
    "regnal_names": ["Abdullah", "Adrian", "Agapetus", "Albert", "Alexander", "Alexios", "Alfonso", "Amadeo",
                    "Amenhotep", "Anastasius", "Andronikos", "Artaxerxes", "Baldwin", "Basil", "Bela", "Béla",
                    "Benedict", "Boniface", "Callixtus", "Carl", "Carloman", "Carlos", "Catherine", "Celestine",
                    "Ceolwulf", "Charibert", "Charles", "Childebert", "Childeric", "Chilperic", "Chlothar", "Christian",
                    "Clement", "Cleomenes", "Clovis", "Conrad", "Constans", "Constantine", "Constantius", "Dagobert",
                    "Damasus", "Darius", "David", "Donald", "Duncan", "Edmund", "Edward", "Elizabeth", "Eugene",
                    "Felipe", "Felix", "Ferdinand", "Fernando", "Francis", "Franz", "Frederick", "Gelasius", "George",
                    "Gregory", "Gustav", "Hadrian", "Harold", "Henry", "Honorius", "Innocent", "Isaac", "Isabel",
                    "Isabella", "Ivan", "James", "Jan", "Jayavarman", "João", "John", "Joseph", "Julius", "Justin",
                    "Justinian", "Karl", "Kenneth", "Kirtivarman", "Konrad", "Ladislaus", "Leo", "Leopold", "Lothair",
                    "Louis", "Lucius", "Luis", "Malcolm", "Manuel", "Marcellus", "Maria", "Marinus", "Martin", "Mary",
                    "Matthias", "Maximilian", "Menander", "Michael", "Moctezuma", "Mutesa", "Napoleon",
                    "Narasimhavarman", "Nicholas", "Nikephoros", "Otto", "Parakramabahu", "Paschal", "Paul", "Pedro",
                    "Pelagius", "Peter", "Philip", "Pius", "Richard", "Robert", "Romanos", "Rudolf", "Sergius",
                    "Siemowit", "Sigebert", "Sigismund", "Sixtus", "Stanisław", "Stephen", "Sylvester", "Tehaapapa",
                    "Theodore", "Theodosius", "Theudebert", "Theuderic", "Tiberius", "Tigranes", "Tiridates", "Tvrtko",
                    "Tzath", "Urban", "Valentinian", "Victor", "Vikramaditya", "Vladimir", "Władysław", "Welf",
                    "Wilhelm", "William"],
    "roman_words": ["CC", "CD", "CDI", "CDL", "CI", "CL", "CM", "CML", "CV", "DC", "DIV", "DL", "MC", "MCI", "MD",
                    "MDC", "MI", "MIX", "ML", "MM", "MV", "MX", "XL"],
    "roman_nouns": ["chapter", "volume", "book", "act", "grade", "episode", "section", "part", "phase", "class",
                    "level", "stage", "type", "war", "world war", "super bowl"],
    "roman_letter_nouns": ["chapter", "volume", "book", "act", "episode", "war", "world war", "super bowl"],
    "letter_words": ["I", "A", "DO", "NO", "TO", "IN", "ON", "AT", "OF", "IT", "IS", "BE", "WE", "ME", "MY", "SO", "UP",
                     "OR", "AN", "AS", "BY", "GO", "HE", "IF", "AM"],
    "letter_runs": {"CIA": "letters", "IRS": "letters", "USA": "letters", "IBS": "letters", "IDS": "letters"},
    "patterns": {
        "expression": "[-−+]?[0-9]+(?: ?[+−×÷=] ?[-−+]*[0-9]+)+",
        "date_month_day": _MONTH + " ([0-9][0-9]?)" + _ORDINAL_MARK + "?(?:,? ([0-9][0-9][0-9][0-9]))?",
        "date_day_month": "([0-9][0-9]?)" + _ORDINAL_MARK + "? (?:of )?" + _MONTH + "(?:,? ([0-9][0-9][0-9][0-9]))?",
        "date_month_year": _MONTH + " ([0-9][0-9][0-9][0-9])",
    },
})

VARIETIES = (
    Variety("en-GB", freeze({"colors": {code: name.replace("gray", "grey") for code, name in COLORS.items()
                                        if "gray" in name},
                             "currencies": {"USD": {"symbols": ["$"]}, "JPY": {"symbols": ["¥"]}}})),
    Variety("en-US", freeze({
        "defaults": {"date_order": "MDY"},
        "currencies": {"USD": {"symbols": ["US$"]}},
        "letter_names": {"z": "zee"},
        "numeric_date_reading": {"full": "{month} {day} {year}", "no_year": "{month} {day}"},
        "percent": {"word": "percent"},
        "titles": {"Dr": None, "Mr": None, "Mrs": None},
    })),
)


def ordinal_suffix(number: int) -> str:
    """The written suffix of an English ordinal: "th" when the tens digit is 1, else by the last digit."""
    if number // 10 % 10 == 1:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")


class EnglishSpeller:
    """RBNF integers with the rule sets of each variety, decimals read digit by digit after "point"."""

    def __init__(self):
        self.rbnf = {
            "en-GB": RbnfSpeller(cardinal={Features(): "spellout-cardinal-verbose"},
                                 ordinal={Features(): "spellout-ordinal-verbose"}),
            "en-US": RbnfSpeller(cardinal={Features(): "spellout-cardinal"}, ordinal={Features(): "spellout-ordinal"}),
        }

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self.rbnf[request.variety.tag].cardinal(digits, features, request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self.rbnf[request.variety.tag].ordinal(digits, features, request)

    def year(self, digits: str, features: Features, request: Request) -> str:
        """`spellout-numbering-year`, except that a year it reads with "thousand" reads as the cardinal of the
        variety: "two thousand (and) one" for 2001 (Wikipedia, "English numerals", Dates)."""
        words = self.rbnf[request.variety.tag].year(digits, features, request)
        return self.cardinal(digits, features, request) if "thousand" in words else words

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        whole = self.cardinal(integer or "0", features, request)
        return f"{whole} {request.data['decimal_word']} {spell_digits(fraction, request)}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """One-half, two-thirds, three-quarters, one one-hundredth (Wikipedia, "English numerals")."""
        top = self.cardinal(numerator, features, request)
        plural = bounded_integer(numerator) != 1
        value = bounded_integer(denominator)
        names = None if value is None else request.data["fraction_names"].get(str(value))
        if names is not None:
            bottom = names[plural]
        else:
            bottom = self.ordinal(denominator, features, request).replace(" ", "-") + ("s" if plural else "")
        simple = " " not in top and "-" not in top and "-" not in bottom
        return f"{top}-{bottom}" if simple else f"{top} {bottom}"


SPELLER = EnglishSpeller()


def _cardinal(digits: str, request: Request) -> str:
    return SPELLER.cardinal(digits, Features(), request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    """A fraction; a mixed number reads its whole part, "and", and the fraction, with "a" for the numerator 1 of a
    half and a quarter: "one and a half", "six and a quarter", "seven and five eighths" (Wikipedia, "English
    numerals", Fractions and decimals: "Fractions together with an integer are read as follows")."""
    fields, request = span.fields, context.request
    if not fields["whole"]:
        return core_speak_fraction(span, context)
    numerator, denominator = fields["numerator"], fields["denominator"]
    names = request.data["fraction_names"].get(denominator)
    part = (f"a {names[0]}" if numerator == "1" and names is not None
            else SPELLER.fraction(numerator, denominator, Features(), request))
    return f"{SPELLER.cardinal(fields['whole'], Features(), request)} {request.data['mixed_word']} {part}"


def speak_date(span: Span, context: SpanContext) -> str:
    """A day-first reading says "the", the ordinal day, "of" and the month (Wikipedia, "Date and time notation in
    the United Kingdom": "When saying the date, it is usually pronounced using "the", then the ordinal number of the
    day first, then the preposition "of", then the month"). When the text writes "the" right before the date, with
    whitespace alone between them, the reading says no second one: `the 3rd of May` reads "the third of May". The
    date recognizers mark such a date in `Request.memo` (`mark_article`)."""
    request = context.request
    fields = span.fields
    month = request.data["months"][fields["month"] - 1]
    year = SPELLER.year(str(fields["year"]), Features(), request) if fields["year"] is not None else None
    if fields["day"] is None:
        return f"{month} {year}"
    day = SPELLER.ordinal(str(fields["day"]), Features(), request)
    if fields["month_written"] == "name":
        template = "{month} {day} {year}" if fields["written_order"] == "MDY" else "the {day} of {month} {year}"
    else:
        template = request.data["numeric_date_reading"]["full"]
    if span.start in request.memo.get(_ARTICLE, ()):
        template = template.removeprefix("the ")
    if year is None:
        template = template.replace(" {year}", "")
    return template.format(month=month, day=day, year=year)


def speak_time(span: Span, context: SpanContext) -> str:
    """The 12-hour reading says the day period that the text writes, or that hours 0 and 13 to 23 imply
    (Wikipedia, "12-hour clock"). Minutes 1 to 9 read "oh one" to "oh nine"."""
    request = context.request
    params = request.params
    fields = span.fields
    hour, minute, second = fields["hour"], fields["minute"], fields["second"]
    period = fields["period"]
    if period is None and params.clock == "12h" and (hour == 0 or hour >= 13):
        period = "pm" if hour >= 13 else "am"
    twelve = fields["period"] is not None or params.clock == "12h"
    face = twelve_hour(hour) if twelve else hour
    next_face = twelve_hour(hour + 1) if twelve else (hour + 1) % 24
    phrase = request.data["minute_phrases"].get(str(minute))
    if params.minute_style == "phrase" and phrase is not None and second is None:
        words = phrase.format(hour=_cardinal(str(face), request), next_hour=_cardinal(str(next_face), request))
    elif minute == 0 and second is None:
        if not twelve:
            words = f"{_cardinal(str(face), request)} hundred"
        elif period is not None:
            words = _cardinal(str(face), request)
        else:
            words = request.data["minute_phrases"]["0"].format(hour=_cardinal(str(face), request))
    else:
        minutes = f"oh {_cardinal(str(minute), request)}" if minute < 10 else _cardinal(str(minute), request)
        words = f"{_cardinal(str(face), request)} {minutes}"
    if second is not None:
        unit = "second" if plural_category(request, str(second)) == "one" else "seconds"
        words += f" and {_cardinal(str(second), request)} {unit}"
    if period is not None:
        words += " " + request.data["spoken_periods"][period]
    return words


def speak_money(span: Span, context: SpanContext) -> str:
    """A scale word comes between the amount and the plural currency name: "two million dollars". Two decimals
    read as the minor unit when the currency names one: "five dollars and fifty cents"."""
    request = context.request
    fields = span.fields
    amount = FrozenMap({**fields["amount"], "sign": ""})
    currency = currency_table(request)[fields["currency"]]
    integer, fraction = amount["integer"] or "0", amount["fraction"]
    if fields["scale"]:
        amount = FrozenMap({**amount, "fraction": (fraction or "").rstrip("0")})
        words = f"{amount_words(amount, request)} {request.data['scales'][fields['scale']]} {currency['other']}"
    elif len(fraction) == 2 and "minor" in currency:
        major = f"{_cardinal(integer, request)} {currency_name(currency, plural_category(request, integer))}"
        minor_digits = str(int(fraction))
        minor = f"{_cardinal(minor_digits, request)} {currency['minor'][plural_category(request, minor_digits)]}"
        if int(fraction) == 0:
            words = major
        else:
            words = minor if bounded_integer(integer) == 0 else f"{major} and {minor}"
    else:
        category = plural_category(request, written_amount(amount))
        words = f"{amount_words(amount, request)} {currency_name(currency, category)}"
    return signed(words, fields["amount"]["sign"], request)


def speak_measure(span: Span, context: SpanContext) -> str:
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    pattern, _ = unit_reading(request, span.fields["unit"], plural_category(request, written_amount(amounts[-1])))
    link = request.data["range_word" if span.fields["relation"] == "range" else "dimension_word"]
    return pattern.replace("{0}", f" {link} ".join(amount_words(a, request) for a in amounts))


def speak_roman(span: Span, context: SpanContext) -> str:
    """A numeral after a name reads "the" and the ordinal, with a capital: `Henry VIII` reads "Henry the Eighth".
    After a noun of `roman_nouns` it reads the cardinal, with a capital on each word after a capitalised noun and
    with none after a noun in lowercase: `World War II` reads "World War Two" and `chapter IV` "chapter four"."""
    request = context.request
    digits = str(span.fields["value"])
    if span.fields["role"] == "ordinal":
        return "the " + _title_case(SPELLER.ordinal(digits, Features(), request))
    words = SPELLER.cardinal(digits, Features(), request)
    before = context.before[-1] if context.before else ""
    return _title_case(words) if before[:1].isupper() else words


def _title_case(words: str) -> str:
    """Each word and each part of a hyphenated word with a capital, except "and": "One Hundred and Fifty-Seven"."""
    return " ".join(word if word == "and" else "-".join(part[:1].upper() + part[1:] for part in word.split("-"))
                    for word in words.split(" "))


def speak_year(span: Span, context: SpanContext) -> str:
    """The short end of a year range, `45` in `1939-45`, holds the whole year and reads without the century when
    the year reading starts with it: "nineteen thirty-nine to forty-five", "twenty ten to twelve"."""
    request = context.request
    digits = span.fields["digits"]
    words = SPELLER.year(digits, Features(), request)
    century = _cardinal(digits[:2], request) + " "
    if span.end - span.start == 2 and words.startswith(century):
        return words[len(century):]
    return words


class EnglishTelephone(Telephone):
    """The shared telephone recognizer with the English conventions of design section 4.3.

    A phone word also names a run up to three words back, where a function word does not count, when the run has
    the shape of a phone number, as in `Call us on 0800 123 456.` The same window names a short code of
    `short_codes` that ends its clause or that a function word follows, as in `Call the police on 999 now.`, and
    not the count in `The phone rang 101 times.` The `LANGUAGE` spec sets these fields of the shared recognizer,
    and turns `keeps_hour_after_stop` off.

    The `phone_unit_shapes` of `en` make space-separated groups of which the first starts with `0`, perhaps in
    brackets, read digit by digit as one unit, as in `020 7946 0018` and `(0161) 496 0000`. Its
    `phone_kept_shapes` keep thousands that spaces group, as in `10 000` and `1 000 000 2nd-generation`, as
    written, and its `no_phone_shapes` take the phone shape from two years that a dash joins.

    A last group of one or two digits is the hour or a count, not a phone group, when the shared recognizer drops
    it as an hour, and also when a word character, a digit or a cluster mark continues the run on either side, or
    a space and a lowercase word that is no function word follow it, so `Call 0800 123 456 8 am to 8 pm.` and
    `Ring 0800 123 456 24 hours a day.` read the number and the hour."""

    def continued(self, text: str, start: int, end: int) -> bool:
        return not _edge(text, start, end)

    def hour_after(self, text: str, end: int, request: Request) -> bool:
        if not text.startswith(" ", end):
            return False
        stop = end + 1
        while stop < len(text) and is_letter(text[stop]):
            stop += 1
        word = text[end + 1:stop]
        return (word.islower() and word not in request.data.get("function_words", ())) \
            or super().hour_after(text, end, request)


@dataclass(frozen=True)
class Ordinal:
    """`1st`, `22nd`, `113th`, `1,000th`: a whole number with the suffix that it takes."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        marks = request.data["ordinal_marks"]
        for number in numbers_in(text, request):
            marker = text[number.end:number.end + 2]
            if (number.sign or number.fraction is not None or marker not in marks
                    or ordinal_suffix(int(number.integer[-2:])) != marker
                    or not is_bounded(text, number.start, number.end + 2)):
                continue
            yield Span(number.start, number.end + 2, Form.ORDINAL,
                       FrozenMap({"digits": number.integer, "marker": marker, "prefix": "", "suffix": "",
                                  "script": number.script}), recognizer=self.name)


@dataclass(frozen=True)
class Year:
    """A year from 1000 to 2099 (section 4.2): after a year word, as in `In 1984`; two years that a range mark
    joins, the lower one first, as in `1939-1945`, or a year and a higher two-digit end after a year word, as in
    `during 1939-45`; and a number that a link joins to a year, as in `In 1066 and 1215`. A comma alone links
    only inside a list that a link word ends, as in `In 1066, 1215 and 1415`.

    A count read as a year is wrong, so the follower of a linked list decides for all its years, and a range is
    one link of a list. A lowercase word that is not in `function_words` blocks them, as in `in 1234 steps`, and
    so do a symbol of `unit_symbols` in any case, another unit symbol in its own case, an operator and a dimension
    mark, as in `in 2048 MB`, `in 2020 mA` and `in 1920 × 1080`. An acronym that only matches a unit symbol in
    another case, such as `EV` or `MA`, is a capitalised name, so `In 2023 EV sales rose.` keeps its year."""
    name: str = "year"
    form: Form = Form.YEAR

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._years(text, tokens, request), text, request)

    def _years(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        year_words = frozenset(data["year_words"])
        function_words = frozenset(data["function_words"])
        marks = frozenset(data["range_marks"])
        units = unit_table(request)
        listed = frozenset(symbol.lower() for symbol in data["unit_symbols"])
        signs = frozenset(data["operators"]) | frozenset(data["dimension_marks"]) | {"*", "/"}
        word_link = re.compile(",? (?:" + "|".join(map(re.escape, data["year_links"])) + ") ")
        words = context_words(tokens)
        breaks = clause_breaks(text)
        numbers = [n for n in numbers_in(text, request) if not n.sign and n.fraction is None
                   and n.end - n.start in (2, 4) and is_bounded(text, n.start, n.end)]

        def year(number: Number) -> bool:
            return number.end - number.start == 4 and 1000 <= int(number.integer) <= 2099

        def after_year_word(number: Number) -> bool:
            before = clause_window(text, words, number.start, number.end, -1, limit=1, breaks=breaks)
            return bool(before) and before[0].lower() in year_words

        def free(end: int) -> bool:
            start = end
            while start < len(text) and text[start].isspace():
                start += 1
            if start in (end, len(text)):
                return True
            stop = start
            while stop < len(text) and not text[stop].isspace():
                stop += 1
            follower = text[start:stop].rstrip(".,;:!?)")
            if (text[start] in signs and not is_letter(text[start])) or follower in units or follower.lower() in listed:
                return False
            stop = start
            while stop < len(text) and is_letter(text[stop]):
                stop += 1
            word = text[start:stop]
            return not word.islower() or word in function_words

        claimed = {}
        partners = {}
        for first, second in zip(numbers, numbers[1:]):
            if not (year(first) and text[first.end:second.start] in marks):
                continue
            if year(second) and int(first.integer) < int(second.integer):
                claimed |= {first: first.integer, second: second.integer}
                partners |= {first: second, second: first}
            elif (second.end - second.start == 2 and int(first.integer) % 100 < int(second.integer)
                  and after_year_word(first)):
                claimed |= {first: first.integer, second: first.integer[:2] + second.integer}
                partners |= {first: second, second: first}
        chains: list[list[Number]] = []
        for number in numbers:
            if not (year(number) or number in claimed):
                continue
            gap = text[chains[-1][-1].end:number.start] if chains else ""
            if chains and (gap == ", " or word_link.fullmatch(gap) or partners.get(number) is chains[-1][-1]):
                chains[-1].append(number)
            elif number in claimed or after_year_word(number):
                chains.append([number])
        for chain in chains:
            while len(chain) > 1 and text[chain[-2].end:chain[-1].start] == ", ":
                chain.pop()
            if free(chain[-1].end):
                claimed |= {number: number.integer for number in chain if number not in claimed}
            else:
                for number in chain:
                    claimed.pop(number, None)
        for number, digits in claimed.items():
            yield Span(number.start, number.end, Form.YEAR, FrozenMap({"digits": digits, "suffix": ""}),
                       recognizer=self.name)


@dataclass(frozen=True)
class Roman:
    """A Roman numeral after a noun of `roman_nouns`, a regnal title and a name, a name of `regnal_names`, or a given
    name and a surname.

    After a noun of `roman_nouns`, which names a series, as in `chapter IV`, `World War II` and `Super Bowl LVII`, the
    numeral reads as a cardinal, but a numeral of `roman_words` reads there only after a noun of `roman_letter_nouns`
    and when no word in lowercase follows it, so `Chapter XL.` reads and `type MX record` and `Class CL.` stay as
    written. After a regnal title and a capitalised name that only spaces, or a mark of `apposition_marks` before a name
    of `regnal_names`, part, as in `King Charles III`, where a single quote counts only when it opens a quote, after a
    name of `regnal_names`, as in `Henry VIII`, and, for II to IV, after exactly two words, a given name and a surname
    of the name files, as in `Hank Williams III`, it reads "the" and the ordinal, and the value is at most 30. Every
    other numeral stays as written, as in `Apollo XIII` and `Rocky II`. The word before the numeral reads it only when
    spaces alone part them. A numeral of one letter reads only after a regnal title and a name, and after a noun of
    `roman_nouns` that holds two words, as `World War I` does. So the pronoun in `the book I read` stays a pronoun, and
    `Malcolm X` stays as written. A word of `function_words` in any case, as the `The` that starts a sentence, reads no
    numeral."""
    name: str = "roman"
    form: Form = Form.ROMAN

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        from text2spoken.core.roman import value as roman_value, word_follows

        data = request.data
        titles = frozenset(data["regnal_titles"])
        regnal_names = frozenset(data["regnal_names"])
        apposition_marks = frozenset(data["apposition_marks"])
        given_names = _names("given_names.json")
        surnames = _names("surnames.json")
        nouns = frozenset(data["roman_nouns"])
        number_nouns = frozenset(data["roman_letter_nouns"])
        function_words = frozenset(data["function_words"])
        numeral_words = frozenset(data["roman_words"])
        letter_words = frozenset(data["letter_words"])
        words = context_words(tokens)
        breaks = clause_breaks(text)
        for match in re.finditer("[IVXLCDM]+", text):
            start, end = match.span()
            numeral = match.group()
            value = roman_value(numeral)
            if value is None or not is_bounded(text, start, end) or not text.endswith(" ", 0, start):
                continue
            index = bisect_right(words, start, key=lambda word: word.end)
            before = clause_window(text, words, start, end, -1, limit=3, breaks=breaks)
            if not before or index < 1 or not text[words[index - 1].end:start].isspace() \
                    or before[-1].lower() in function_words or before[-1].lower() in titles:
                continue
            last = before[-1]
            gap = text[words[index - 2].end:words[index - 1].start] if len(before) >= 2 else ""
            mark = gap.strip()
            # A single quote is also the apostrophe of a possessive, as in `the princess' Charles I danced with`, so
            # it parts the title from the name only when it opens a quote and touches the name.
            apposition = mark in apposition_marks and last in regnal_names \
                and (mark not in ("'", "’") or gap.endswith(mark))
            regnal = len(before) >= 2 and before[-2] in titles and last[0].isupper() and (gap.isspace() or apposition)
            pair = " ".join(before[-2:]).lower()
            two_words = len(before) >= 2 and pair in nouns
            noun = pair if two_words else last.lower()
            if regnal:
                role = "ordinal" if value <= 30 else None
            elif len(numeral) == 1 and not (two_words and numeral in "IVX") or last.upper() in letter_words:
                role = None
            elif noun in nouns:
                role = None if numeral in numeral_words and (noun not in number_nouns or word_follows(text, end)) \
                    else "cardinal"
            elif not last[0].isupper() or value > 30:
                role = None
            elif last in regnal_names:
                role = "ordinal"
            elif 2 <= value <= 4 and len(before) >= 2 and before[-2] in given_names and last.upper() in surnames \
                    and (len(before) == 2 or not before[0][0].isupper() or before[0].lower() in function_words):
                role = "ordinal"
            else:
                role = None
            if role is not None:
                yield Span(start, end, Form.ROMAN, FrozenMap({"value": value, "role": role, "suffix": ""}),
                           recognizer=self.name)


_ARTICLE = "en_date_article"
"""The key of `Request.memo` that holds the starts of the date spans that the word "the" stands right before."""


def mark_article(span: Span, text: str, request: Request) -> Span:
    """The date span, marked in `Request.memo` under `_ARTICLE` when the word "the" stands before it with whitespace
    alone between the two. Punctuation between them, as in `the. 3rd of May` or `"the" 3rd of May`, means that the
    word is no article of the date. The span keeps its bounds, so a lexicon entry for "the" and a hint at the offset
    of the date find the date as they do with no article."""
    gap = span.start
    while gap and text[gap - 1].isspace():
        gap -= 1
    article = gap - 3
    if gap < span.start and article >= 0 and text[article:gap].lower() == "the" \
            and not (article and is_word_char(text[article - 1])):
        request.memo.setdefault(_ARTICLE, set()).add(span.start)
    return span


@dataclass(frozen=True)
class EnglishDateNumeric(DateNumeric):
    """The shared numeric date, with the article before it marked (`mark_article`)."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return (mark_article(span, text, request) for span in super().find(text, tokens, request))


@dataclass(frozen=True)
class DateNamed:
    """`March 12, 2024`, `12th of March 2024`, `March 2024`: a date with a month name."""
    name: str = "date_named"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        patterns = request.data["patterns"]
        symbols = request.data["symbols"]
        folded = fold_digits(text)
        for key, order in (("date_month_day", "MDY"), ("date_day_month", "DMY"), ("date_month_year", "MY")):
            for match in re.finditer(patterns[key], folded):
                start, end = match.span()
                if (not is_bounded(text, start, end) or (start and text[start - 1] in symbols)
                        or not one_digit_set(text[start:end])):
                    continue
                if order == "MY":
                    month_name, day, year = match.group(1), None, match.group(2)
                elif order == "MDY":
                    month_name, day, year = match.group(1), match.group(2), match.group(3)
                else:
                    day, month_name, year = match.group(1), match.group(2), match.group(3)
                written_day = match.group()[match.start(1 if order == "DMY" else 2) - start:]
                if day is not None and written_day[len(day):len(day) + 2] in ("st", "nd", "rd", "th") \
                        and written_day[len(day):len(day) + 2] != ordinal_suffix(int(day)):
                    continue
                month = request.data["months"].index(month_name) + 1
                year_value = int(year) if year is not None else None
                if day is not None and not is_valid(year_value, month, int(day)):
                    continue
                yield mark_article(Span(start, end, Form.DATE,
                                        FrozenMap({"year": year_value, "month": month,
                                                   "day": int(day) if day else None,
                                                   "written_order": "DMY" if order == "DMY" else "MDY",
                                                   "month_written": "name", "era": "", "prefix": "", "suffix": ""}),
                                        recognizer=self.name), text, request)


LANGUAGE = LanguageSpec(
    code="en",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["electronic"], SHARED["color"], SHARED["idiom"], DateNamed(),
                 EnglishDateNumeric(), SHARED["time_clock"],
                 EnglishTelephone(reach=3, content_words=True, names_shaped=True, names_short_codes=True,
                                  keeps_hour_after_stop=False),
                 SHARED["money"], SHARED["kept_money"], SHARED["percent"], SHARED["measure"], Year(),
                 SHARED["expression"], SHARED["fraction"], SHARED["range"], Ordinal(), Roman(), SHARED["abbreviation"],
                 SHARED["letters"], SHARED["decimal"], SHARED["cardinal"], SHARED["emoji"], SHARED["symbol"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.COLOR: speak_color, Form.IDIOM: speak_idiom, Form.DATE: speak_date,
        Form.TIME: speak_time, Form.TELEPHONE: speak_telephone, Form.MONEY: speak_money,
        Form.PERCENT: speak_percent, Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression,
        Form.FRACTION: speak_fraction, Form.RANGE: speak_range, Form.ORDINAL: speak_ordinal, Form.ROMAN: speak_roman,
        Form.ABBREVIATION: speak_abbreviation, Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal,
        Form.YEAR: speak_year, Form.ELECTRONIC: speak_electronic, Form.LETTERS: speak_letters,
        Form.SYMBOL: speak_symbol, Form.EMOJI: speak_emoji,
    },
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER,
              Form.YEAR: SPELLER},
    genders=frozenset(),
    default_gender=None,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={
        "date_order": frozenset({"DMY", "MDY", "YMD"}),
        "clock": frozenset({"12h", "24h"}),
        "minute_style": frozenset({"number", "phrase"}),
        "decimal_mark": frozenset({".", ","}),
        "scale": frozenset({"short"}),
        "phone_regions": frozenset(PHONE_PLANS),
    },
    not_applicable=frozenset({"default_gender", "register"}),
)
