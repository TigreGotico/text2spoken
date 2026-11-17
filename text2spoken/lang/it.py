"""Italian: it-IT, the default variety, it-CH and it-SM.

Cardinals and ordinals come from ovos-number-parser (design section 5.4), the `it` extra. Its forms agree with the
Enciclopedia dell'Italiano Treccani, "numerali", Pronuncia e grafia. A compound in uno keeps its full form, as
"ventuno", "centouno" and "ventunomila", and the same section allows both forms before a noun: "Nei composti (ventuno,
trentuno, ecc.) accompagnati da un nome, questo è invariabile se il numerale segue il nome, ma può essere apocopato se
il numerale precede il nome". 108 reads "centootto": "con cento seguito da una decina o da un'unità, l'elisione è poco
comune con uno, otto e undici [...] (29) centootto [raramente centotto]". 1003 reads "milletré": "I composti di tre
vanno accentati". CLDR RBNF `it` writes "centotto" and "milletre" for these numbers. The Accademia della Crusca,
consulenza 1077, agrees: "108: centootto, meno bene centotto", and "21.000: ventunomila o ventunmila: entrambe le forme
vanno bene".

Of the cardinals, only uno changes with the noun (Treccani, "numerali", Cardinali: "In italiano sono invariabili, a
eccezione di uno, che varia secondo il genere [...] e che al femminile assume la forma una"). Without a noun, 1 reads
"uno" (Vocabolario Treccani, "uno", 1: "il numero uno, a pagina uno"), or "una" when the caller gives `default_gender`
feminine. Before a noun, uno takes the form of the indefinite article ("numerali": "Il numerale cardinale uno subisce
apocope là dove la subirebbe l'articolo indeterminativo"). Before a masculine noun the article is un, unless the noun
takes lo (Vocabolario Treccani, "uno": "l'uso della quale è regolato dalle stesse norme che regolano l'uso dell'art.
determ. masch. sing. il, rispetto alla sua variante lo: un uomo, un osso, un cane, uno scolaro, uno zoccolo"). The
Vocabolario Treccani, "articolo", gives where lo stands, and un and uno "si usano rispettivamente negli stessi casi di
il e di lo": "b) davanti alle consonanti gl(i), gn, sc(i), z [...] c) davanti ai gruppi consonantici s + cons., ps-,
pn-, x". `lo_onsets` lists these onsets, and an s before a consonant takes uno too, so `1 zaino` reads "uno zaino" and
`1 studente` "uno studente". Before a feminine noun the article is una, "che davanti a vocale di regola si elide (una
casa, una spazzola, un'isola, un'amica)", but not before a semiconsonant: "in tutti i casi una per il femm. (una iena,
una uosa)" (the same entry). The Accademia della Crusca, consulenza 82, gives the same rule: "si avrà un'aiola,
un'eresia, un'ora, un'isola, un'udienza". So `1 ora` reads "un'ora".

The gender of a noun comes from the noun list `data/wiktionary/it_noun_genders.json`, which
`scripts/extract_noun_genders.py` makes from the categories "Italian masculine nouns" and "Italian feminine nouns" of
the English Wiktionary. The Italian Wiktionary has no category for the gender of a noun. A word of both categories, as
"cantante", is in the list with no gender. So `1 anno` reads "un anno", `1 gatta` "una gatta" and `1 uomo` "un uomo". A
scale word is a masculine noun (Vocabolario Treccani, "milione": "s. m."; "un m. di sterline"). A unit name of CLDR that
the list leaves out, such as "metro", takes its CLDR gender. The list comes first: CLDR gives "miglio" the feminine of
its plural, and the Vocabolario Treccani, "miglio", gives "s. m. [...] (pl. le mìglia)", so `1 miglio` reads "un
miglio". A month name after a number writes a date, as in `1 maggio`. A noun of the list that is also a function word is
a noun after 1, as in `1 via di fuga`: "una via di fuga" (Vocabolario Treccani, "via": "aprirsi una v. nella foresta").
The words of `partitive_words`, `score_words` and `kept_links` come first, so `1 di loro` reads "uno di loro".

1 before another lowercase word reads by what that word is. Before a word of `partitive_words` it is the pronoun
(Vocabolario Treccani, "uno": "in costruzioni partitive: uno di loro e una di voi"; "si alzò uno dei presenti"), so `1
di loro` reads "uno di loro" and `1 delle città` "una delle città". Before or after a preposition of `score_words` ("a",
"su", "contro") it is a score, a ratio or a pronoun, read as the bare number (Vocabolario Treccani, "vincere": "v. per
quattro a due"; "contro": "scommettere dieci c. uno"): `1 a 0` reads "uno a zero", `2 a 1` "due a uno" and `1 contro 3`
"uno contro tre". A preposition takes no article, so 1 before it is no article. Before another word it takes the
masculine article form, as in `1 altro libro`: "un altro libro". Before "e" or "o" (`kept_links`) it stays as written,
because its noun comes later, as in `tra 1 e 2 ore`. A number right after a label noun is a label, and reads the bare
"uno" (Vocabolario Treccani, "uno": "il numero uno, a pagina uno"; "numero": "il n. 5, il n. 11"). A label noun is a
noun of `label_nouns`, a noun of the list after a determiner of `label_determiners`, elided forms included, as in `il
binario 1` and `l'articolo 1`, or an abbreviation of `label_abbreviations`, as in `art. 1`. The clitic in `C'era 1 sola
persona` is no determiner. A noun of the list with no determiner may be a participle or a verb, as "visto" in `Ho visto
1 film`, so it is no label. A noun of the list with a capital inside a sentence starts a name, as `Formula` in `il
mondiale di Formula 1`, and is a label noun. After a label noun other than an abbreviation or a noun of `label_nouns`,
the number counts the next word when that word is a CLDR unit name or a noun of `label_counted_nouns`: `la gara 1 anno
fa` reads "la gara un anno fa", `Marco 1 settimana fa` "Marco una settimana fa" and `il film 1 volta` "il film una
volta". Before any other word it stays a label, because the word may be a verb that is also a noun: `il binario 1 porta
a Roma` reads "il binario uno porta a Roma". A unit name that is also a function word, as "ora" ("now") and
"secondo" ("according to"), is counted too, as in `il percorso 1 ora circa`: "il percorso un'ora circa". Only a verb
of `adverb_verbs` right after it makes it the adverb, and 1 stays a label: `il binario 1 ora è chiuso` reads "il
binario uno ora è chiuso". The list holds forms of essere (Vocabolario Treccani, "essere": "pres. sóno, sèi, è,
siamo") and "fa parte" ("parte": "Far parte di qualche cosa", "essere uno dei componenti"), so `la linea 1 ora fa
parte della rete` reads "uno ora", and `il cane 1 ora fa` "un'ora fa". "secondo" before an article or a capital is the
preposition ("secondo", prep.: "agire s. la legge"), as in `il livello 1 secondo la scala`, and 1 stays a label.
1 before a word with a capital, as a name or a unit symbol that the file does not list, takes the masculine article
form "un", unless a label noun comes before it: `con 1 Airbus` reads "con un Airbus", and `fino a 1 Gbps` "fino a un
Gbps".

A scale word before a noun takes "di" (Treccani, "numerali", Cardinali: milione, miliardo "devono essere [...] seguiti –
qualora precedano un altro nome – dalla preposizione di"; Vocabolario Treccani, "milione": "un m. di volte", "un m. di
amici"), also when it comes from digits: `1.000.000 €` reads "un milione di euro" and `3.000.000 km` "tre milioni di
chilometri". The word after the scale word takes "di" when it is a noun of the list of either gender or of both, or the
regular plural of one: `2.000.000 abitanti` reads "due milioni di abitanti". A function word takes no "di": `2.000.000
adesso` reads "due milioni adesso". `function_words` holds the words of the Wiktionary categories of prepositions,
conjunctions, adverbs, pronouns, determiners and articles. Before any other word the number stays as written: a word
that is a noun and a function word, as "ieri" and "specie", a verb, as in `I 2.000.000 erano`, and a noun that the list
does not hold, as in `10.000.000 follower`. `scale_words` holds the scale nouns of ovos-number-parser.

A decimal reads the CLDR RBNF `it` rule `x.x: ←← virgola →→` of `spellout-numbering`: the whole part, "virgola", then
each digit of the decimal part, so `3,14` reads "tre virgola uno quattro" and the zero of `2,50` stays. The minus sign
reads "meno" (RBNF `-x: meno →→`; Vocabolario Treccani, "meno": "il termometro segna m. quattro (-4)"), and the plus
sign "più" ("più": "stamattina il termometro segna appena più tre (+ 3)").

An ordinal is written with "il piccolo segno esponenziale ‹º› per il genere maschile o ‹ª› per il genere femminile"
("numerali", Pronuncia e grafia), as the CLDR RBNF `it` rules `digits-ordinal-masculine` and `digits-ordinal-feminine`
write it. The Vocabolario Treccani, "ordinale", gives the rule of the ordinals after decimo: they "si formano dal tema
del corrispondente cardinale ital. con l'aggiunta della terminazione -èsimo: così undicesimo, [...] ventitreesimo, [...]
centunesimo, [...] millesimo, duemillesimo, [...] diecimillesimo". So 108 reads "centoottesimo", from "centootto", and
180 "centottantesimo". The same entry gives the separate form for the ordinals "per i quali l'altro tipo sarebbe sentito
come poco eufonico: centesimo decimo, millesimo primo, millesimo secondo, millesimo decimo, millesimo undecimo o
undicesimo, ecc. (in questi casi la grafia staccata è preferita)". ovos-number-parser, the `it` extra, writes the
ordinals, the separate forms included: "millesimo primo" for 1001, "millesimo undicesimo" for 1011, and every number
above 100 that ends in 10 as the ordinal of the number without the 10 and "decimo": "centesimo decimo" for 110,
"duecentesimo decimo" for 210, "trecentesima decima" in the feminine. From a million up the parser writes one word with
a singular scale word, as "tremilionecinquecentomillesimo" for 3500000, and no source gives that form, so an ordinal
above 999999 stays as written until a sourced form exists.

The degree sign writes an ordinal too (Vocabolario Treccani, "primo": "Numerale ordinale (indicato con 1° se si
utilizzano cifre arabiche"; "centesimo": "in scrittura numerica 100°"). It also writes an angle and a coordinate, as in
`46° nord` and `90° rispetto al suolo`, so `noun_ordinal_marks` makes an ordinal only before one space and a noun of
`ordinal_nouns`, each of which the Vocabolario Treccani writes after an ordinal: "anniversario" ("cinquantenario":
"Cinquantesimo anniversario"), "anno" ("frequentare il terzo a. del liceo"), "capitolo" ("l'ottavo c. dei «Promessi
Sposi»"), "edizione" ("prima, seconda, sesta e."), "giorno" ("decimo": "il d. giorno del mese"), "grado" ("3° g."),
"piano" ("primo p., secondo p. [...], terzo p."), "posto" ("è al terzo p. nella classifica generale"), "secolo" ("il 4°
o IV sec. a. C.", "19° secolo") and "volume" ("secondo, terzo v."). The ordinal agrees with the noun: `3° edizione`
reads "terza edizione". In other places the degree sign and its number stay as written. Before a month name, `1°` writes
the first day of the month, and reads as a date.

A fraction is "formati da un aggettivo numerale cardinale e da un ordinale (un terzo, due quinti, quattro decimi, ecc.)"
("numerali", Frazionari), and 1/2 is "un mezzo" (Vocabolario Treccani, "mezzo", 5: "un mezzo, una metà"). The ordinal is
plural after a numerator other than one (`spellout-ordinal-masculine-plural`), and a denominator above 100 stays as
written. Before a noun, mezzo is an adjective that agrees with it ("numerali", Frazionari: "mi darebbe mezzo chilo di
patate e mezza lattuga?"), so 1/2 before a noun of the noun list reads "mezzo" or "mezza", and before another lowercase
word it stays as written. Every other fraction has "il valore di nomi" ("numerali", Frazionari), so the noun it counts
follows "di", as in `I 3/4 della popolazione`. Before a word that is not "di" or one of its forms, as in `2/3
milioni`, `l'anno scolastico 23/24 in via` or `onde alte 3/4 metri`, the slash writes a range, a pair or a score, and
the fraction stays as written. `half_links` names the words after which 1/2 is still the noun "un mezzo" ("mezzo", 1:
"ancora un mezzo di vino"). A percentage is the number and "per cento" (Vocabolario Treccani, "per cento": "n per cento
(simbolo: n%)").

An expression reads its operators by the Vocabolario Treccani: "più" ("quattro più cinque è uguale a nove (in simboli: 4
+ 5 = 9)"), "meno" ("tredici meno otto è uguale a cinque"), "per" ("a × b [...] si legge: a per b") and "è uguale a" for
`=`. The dimension mark `×` of a measure reads "per" too.

Unit words and the gender of each unit come from CLDR 49 (`cldr-units-full`, the `long` patterns of the variety): `5 km`
reads "cinque chilometri". CLDR gives `duration-hour` the feminine gender, and the article form una elides as before a
noun, so `1 h` reads "un'ora". A unit with no CLDR gender takes the gender of its first word in the noun list. A symbol
that cannot be a plain word, such as `km/h` or `°C`, reads with no list. `unit_symbols` names the symbols made only of
letters that read as units.

Currency names and currency symbols come from CLDR 49 (`cldr-numbers-full`, `currencies.json` of the variety): `15 €`
reads "quindici euro", because CLDR `it` gives the euro one name for every plural category, and the Vocabolario
Treccani, "euro", marks it "s. m. [...] invar.". The word "euro" after an amount reads as the sign does, so `8,50 euro`
reads as `8,50 €`. `currency_symbols` names the ISO 4217 codes that read, because a symbol of letters reads only from
that list. CLDR gives a currency no gender, so 1 takes the gender of the first word of the currency name in the noun
list: "un euro", "una sterlina britannica". `$` and `USD` read as "dollaro", as the German and English files read them:
the word also names the dollar of other countries (Vocabolario Treccani, "dollaro": "Anche unità monetaria di altri
paesi [...]: d. canadese, australiano"). An amount next to `¥` stays as written, with its number, because CLDR `it`
gives the sign to the yen and the yuan; `kept_currency_signs` names it. Two decimals read as the minor unit after "e",
so `10,50 €` reads "dieci euro e cinquanta centesimi", and other decimals read as a decimal number before the currency
name. The minor unit of the euro and of the franc is the centesimo (Vocabolario Treccani, "centesimo", 2b: "Moneta che
vale la centesima parte di un'euro, di una lira o di altra unità monetaria"), of the dollar the cent (the same entry:
"cent negli Stati Uniti d'America"), and of the pound the penny ("penny": "pl. pence [...] usato in ital. al masch.
[...] alla 100a parte della sterlina"). `currencies` gives these names, and the gender of a name that the noun list does
not hold. A scale word takes "di" before the currency name, also after an amount in digits: `€ 2 milioni` and `2.000.000
€` read "due milioni di euro".

A character that no other form claims reads by its CLDR 49 annotation name (`cldr-annotations-full` and
`cldr-annotations-derived-full`) of the variety.

A title reads as its full word before a name, in the short form that the word takes there (Vocabolario Treccani,
"signore", 2: "il signor Rossi [...] al sig. Mario Rossi"; "dottore", 2: "si abbrevia in dott. o dr.", and "il dottor
Graziano"; "professore": "il professor Mario Rossi"). The feminine forms do not shorten: "sig.ra" ("signora": "Alla
sig.ra Luisa Rossi"), "sig.na" ("signorina": "Alla sig.na Claudia Bianchi"), "dott.ssa" ("dott.": "abbreviando
dottoressa in dott.ssa") and "prof.ssa" ("prof.": "per il femm. professoressa si usa o prof. o, volendo evitare
equivoco, prof.ssa"). Those entries also let the short form name a woman: "Le stesse abbreviazioni si possono usare
anche con riferimento a donna" ("dott."), and "per il femm. professoressa si usa o prof." ("prof."). So `prof.`, `dott.`
and `Dr.` read the feminine word, "professoressa" or "dottoressa", when the determiner of their noun phrase is a word of
`feminine_determiners`, as in `la prof. Gallo`, and the masculine word in other places. Between the determiner and the
title may come words of `possessives` and `title_adjectives`, and any other word ends the noun phrase, as in `Questa
mattina Prof. Rossi`. An adjective of `title_adjectives` with a gender gives the title that gender in a letter
heading, where only adjectives come between the start of the line and the title: `Egregia Dott. Neri` reads "Egregia
dottoressa Neri" (Accademia della Crusca, consulenza 33625: "è corretto scrivere sia Egregio signor Bianchi sia
Egregia dottoressa Rossi"; Vocabolario Treccani, "egregio": "Si adopera spec. negli indirizzi e nelle intestazioni delle
lettere"). The list holds the superlatives of the heading too: "Il superl. gentilìssimo è spesso usato negli indirizzi
e nell'intestazione delle lettere" ("gentile"), "illustrissimo" "nelle intestazioni epistolari", and "chiarissimo" "in
partic. ai professori universitarî". Two adjectives of different genders, a determiner and an adjective of another
gender, or an adjective after another word that stops the walk leave the title as written: in `Come nota Prof. Rossi`
and `Lo nota Prof. Rossi` the word "nota" is a verb. `la nostra Dott. Ferri` reads "la nostra dottoressa Ferri", and
`La cara prof. Marini` "La cara professoressa Marini". The Vocabolario Treccani, "sig.", gives only "Abbreviazione
di signore", and "signora" gives "sig.ra" for the feminine. After a feminine determiner `sig.` reads "signora", the
title that agrees with the determiner, as in `La sig. Rossi`. The word is lowercase, as these entries write it, and
takes a capital only where a clause starts. "ecc." reads "eccetera" ("ecc.": "Abbreviazione di eccetera"), "art." before
a number "articolo" ("art.": "Abbreviazione grafica di articolo"), and "pag." before a number "pagina" ("pagina": "vedi
a pagina (abbrev. p. o pag.) 40").

it-IT and it-SM write the decimal comma and the group mark `.`, and it-CH the decimal point and the group mark `'` (CLDR
49 number symbols of `it`, `it_SM` and `it_CH`). In it-CH a decimal point reads as a decimal, as in `2.5 km`, `3.14159`
and `CHF 12.50`, except in the forms that Italian text also writes with the point. A point before three digits may be a
thousands group, as in `1.000` (CLDR `it`), and a lone point before three digits fits both readings (CGPM 2003,
Resolution 10: the decimal marker "shall be either the point on the line or the comma on the line"). An hour up to 24,
the point and two digits up to 59 may be a clock time, as in `alle 8.00` of FLORES-200 devtest, when no amount, measure
or percentage claims it. These forms stay as written, and so does a number with a letter right after its digits, as
`802.11g` of FLORES-200 devtest: the letters make the name of a standard or a model, not a unit. In every variety, a
number with a decimal comma right after a word of `time_words`, as `ore 15,00`, stays as written when it may be a
clock time: a clock time reads only with `:` or `.`, and no source gives the comma as a mark of the clock.

A sign after an opening bracket and before one space and a
decimal or a number with a mark after it, as `(- 2,8%)`, stays as written with the number and its form: the space parts
the sign from the number, so it may be a minus or a dash. A whole number alone after the sign, as `(+ 2)`, reads as a
cardinal, as in a language with no file. An acute or a grave accent next to a letter, as in `l´Italia`, stands for an
apostrophe or a quotation mark and stays as written.

The words of a date, a clock time and a year come from `ovos_date_parser.spoken` (design section 5.4), the `it` extra,
and so do the month names. A numeric date reads in the order day, month, year. In `25 dicembre 2024` the day and the
month read as a date, and the year as a cardinal. The first day of a month is an ordinal: the Accademia della Crusca,
consulenza 1077, "per il giorno iniziale di un mese si usa l'ordinale: il primo ottobre (o il 1° ottobre)", and
consulenza 86, "il 1/2/2003 (cioè il primo febbraio duemilatré)". A day above 12 and a month with a slash and no year,
right after a definite article or a preposition joined with one of `date_words`, read as a date too: `il 13/11` reads
"il tredici novembre". With a day of 12 or below the pair may be a fraction, a time signature, a day range or a rating,
as in `Il 3/4 è una frazione`, `il 4/4`, `del 3/4 luglio` and `il 5/10 in pagella`, so it stays as written. So do `24/7`
(`kept_day_months`) and a pair before a form of di and a word, as in `il 31/12 del quinto anno`. A year reads as one
cardinal word, as "duemilaventidue" (the Accademia della Crusca, consulenza 20176, which reports the media form "venti
ventidue anziché [...] duemilaventidue"). A clock time with `:` or `.` reads after a word of `time_words`, as in `alle
14:30`: "alle quattordici e trenta". A whole hour 0 or 12 reads "mezzanotte" or "mezzogiorno" (Vocabolario Treccani,
"mezzanotte": "in partic. a mezzanotte", "verso m."), and before it "alle", "dalle" and "delle" become "a", "da" and
"di": `alle 12:00` reads "a mezzogiorno". The hour 1 is "l'una": the Accademia della Crusca, consulenza 236, "mostrano
pressoché generalizzato l'uso di l' / all'una", so `alle 1:30` reads "all'una e trenta". `time_articles` gives these
forms. After "le", which cannot stand before mezzogiorno, 0 and 12 read the 24-hour form: `Sono le 12:00` reads "Sono le
dodici".
"""
from __future__ import annotations

import json
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace
from functools import lru_cache
from importlib.resources import files
from itertools import takewhile

from text2spoken.core.currencies import currency_name, currency_table
from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety, drop_affixes, plural_category
from text2spoken.core.numbers import Number, written_amount
from text2spoken.core.recognizers import SHARED, TimeClock, numbers_in, signed, speak_decimal, speak_expression
from text2spoken.core.recognizers import Abbreviation as CoreAbbreviation
from text2spoken.core.recognizers import speak_cardinal as core_speak_cardinal
from text2spoken.core.recognizers import speak_fraction as core_speak_fraction
from text2spoken.core.recognizers import speak_lexicon, speak_percent
from text2spoken.core.spans import Features, Span, SpanContext
from text2spoken.core.spellers import DIGIT_BOUND, OvosNumberSpeller, RbnfSpeller, bounded_integer, spell_digits
from text2spoken.core.symbols import speak_emoji, speak_symbol
from text2spoken.core.times import day_hour
from text2spoken.core.tokens import Token, is_bounded, is_letter, is_word_char
from text2spoken.core.units import cldr_data, unit_reading
from text2spoken.errors import DeclinedReading
from text2spoken.params import OPTIONS, FrozenMap, Form, GrammaticalGender, freeze

M, F = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "sign_words": {"-": "meno", "+": "più"},
    "digit_words": ["zero", "uno", "due", "tre", "quattro", "cinque", "sei", "sette", "otto", "nove"],
    "decimal_word": "virgola",
    "leads": {"pag. ": "pagina"},
    "percent": {"signs": ["%"], "position": "after", "word": "per cento"},
    "currency_symbols": ["EUR", "USD", "GBP", "CHF"],
    "currencies": {"EUR": {"symbols": ["euro"], "minor": {"one": "centesimo", "other": "centesimi"}},
                   "CHF": {"minor": {"one": "centesimo", "other": "centesimi"}},
                   "USD": {"symbols": ["$"], "one": "dollaro", "other": "dollari",
                           "minor": {"one": "cent", "other": "cent"}},
                   "GBP": {"minor": {"one": "penny", "other": "pence", "gender": "masculine"}}},
    "kept_currency_signs": ["¥"],
    "scales": {"milione": "milione", "milioni": "milioni", "miliardo": "miliardo", "miliardi": "miliardi"},
    "unit_symbols": ["kg", "g", "km", "m", "cm", "mm", "l", "h", "min"],
    "dimension_marks": ["x", "×"],
    "dimension_word": "per",
    "operators": {"+": "più", "−": "meno", "×": "per", "=": "è uguale a"},
    "ordinal_marks": {"º": "masculine", "ª": "feminine"},
    "noun_ordinal_marks": ["°"],
    "ordinal_nouns": ["anniversario", "anno", "capitolo", "edizione", "giorno", "grado", "piano", "posto", "secolo",
                      "volume"],
    "lo_onsets": ["gli", "gn", "ps", "pn", "x", "z"],
    "half_links": ["di"],
    "label_abbreviations": ["art.", "cap.", "n.", "pag."],
    "label_nouns": ["numero", "pagina"],
    "label_determiners": ["il", "lo", "la", "l'", "i", "gli", "le", "un", "uno", "una", "un'", "del", "dello", "della",
                          "dell'", "dei", "degli", "delle", "al", "allo", "alla", "all'", "ai", "agli", "alle", "dal",
                          "dallo", "dalla", "dall'", "dai", "dagli", "dalle", "nel", "nello", "nella", "nell'", "nei",
                          "negli", "nelle", "sul", "sullo", "sulla", "sull'", "sui", "sugli", "sulle", "questo",
                          "questa", "quest'", "quel", "quello", "quella", "quell'"],
    "score_words": ["a", "su", "contro"],
    "label_counted_nouns": ["volta", "punto", "uomo", "cosa", "tipo", "mezzo"],
    "adverb_verbs": ["è", "sono", "era", "erano", "sarà", "saranno", "fa parte", "fanno parte"],
    "preposition_units": ["secondo"],
    "kept_links": ["e", "o"],
    "partitive_words": {"di": "masculine", "del": "masculine", "dello": "masculine", "dei": "masculine",
                        "degli": "masculine", "della": "feminine", "delle": "feminine", "tra": "masculine",
                        "fra": "masculine"},
    "clock_marks": [{"mark": ":", "seconds": False, "needs": "evidence"},
                    {"mark": ".", "seconds": False, "needs": "evidence"}],
    "time_words": ["alle", "dalle", "delle", "sulle", "le", "ore", "verso", "entro"],
    "time_articles": {"alle": {"0": "a", "1": "all'", "12": "a"}, "dalle": {"0": "da", "1": "dall'", "12": "da"},
                      "delle": {"0": "di", "1": "dell'", "12": "di"}, "sulle": {"1": "sull'"}, "le": {"1": "l'"},
                      "ore": {}},
    "date_words": ["il", "l'", "dal", "dall'", "al", "all'", "del", "dell'", "nel", "nell'", "sul", "sull'"],
    "kept_day_months": ["24/7"],
    "of_words": ["di", "del", "dello", "della", "dei", "degli", "delle"],
    "titles": {"Sig.": "signor", "sig.": "signor", "Sig.ra": "signora", "sig.ra": "signora", "Sig.na": "signorina",
               "sig.na": "signorina", "Dott.": "dottor", "dott.": "dottor", "Dr.": "dottor", "dr.": "dottor",
               "Dott.ssa": "dottoressa", "dott.ssa": "dottoressa", "Prof.": "professor", "prof.": "professor",
               "Prof.ssa": "professoressa", "prof.ssa": "professoressa"},
    "feminine_titles": {"Sig.": "signora", "sig.": "signora", "Dott.": "dottoressa", "dott.": "dottoressa",
                        "Dr.": "dottoressa", "dr.": "dottoressa", "Prof.": "professoressa", "prof.": "professoressa"},
    "feminine_determiners": ["la", "una", "alla", "della", "dalla", "nella", "sulla", "colla", "quella", "questa"],
    "masculine_determiners": ["il", "lo", "un", "uno", "del", "dello", "al", "allo", "dal", "dallo", "nel", "nello",
                              "sul", "sullo", "col", "quel", "quello", "questo"],
    "possessives": ["mia", "tua", "sua", "nostra", "vostra", "loro"],
    "title_adjectives": {"cara": "feminine", "caro": "masculine", "carissima": "feminine", "carissimo": "masculine",
                         "stessa": "feminine", "stesso": "masculine", "vecchia": "feminine", "vecchio": "masculine",
                         "nuova": "feminine", "nuovo": "masculine", "brava": "feminine", "bravo": "masculine",
                         "stimata": "feminine", "stimato": "masculine", "famosa": "feminine", "famoso": "masculine",
                         "nota": "feminine", "noto": "masculine", "egregia": "feminine", "egregio": "masculine",
                         "gentilissima": "feminine", "gentilissimo": "masculine", "illustrissima": "feminine",
                         "illustrissimo": "masculine", "chiarissima": "feminine", "chiarissimo": "masculine",
                         "giovane": "both", "gentile": "both", "grande": "both", "celebre": "both", "illustre": "both"},
    "abbreviations": {"ecc.": "eccetera"},
    "sentence_final": ["ecc."],
    "number_abbreviations": {"art.": "articolo"},
    "symbols": {"%": "percent", "€": "money", "£": "money", "$": "money", "¥": "money", "°": "measure", "×": "measure"},
    "patterns": {"expression": "[-−+]?[0-9]+(?: ?[+−×=] ?[-−+]*[0-9]+)+"},
})

DEFAULTS = {"date_order": "DMY", "clock": "24h"}

VARIETIES = (
    Variety("it-IT", freeze({"defaults": DEFAULTS})),
    Variety("it-CH", freeze({"defaults": DEFAULTS, "number_marks": {"Latn": [{"decimal": ".", "group": "'"}]},
                             "keep_decimals": True})),
    Variety("it-SM", freeze({"defaults": DEFAULTS})),
)

LARGEST_PLURAL_ORDINAL = 100
"""The last plural ordinal that a fraction reads, by RBNF `it`. The core fraction recognizer reads no larger
denominator."""
LARGEST_ORDINAL = 999_999
"""The last ordinal that reads. From a million up ovos-number-parser writes "tremilionecinquecentomillesimo" for
3500000, a form that no source gives."""
VOWELS = "aeiouàèéìíòóù"


class ItalianSpeller:
    """ovos-number-parser for integers and ordinals up to `LARGEST_ORDINAL`; decimals by the RBNF `x.x` rule;
    fractions with the plural ordinals of RBNF."""

    def __init__(self):
        self.parser = OvosNumberSpeller({M: "masculine", F: "feminine"})
        self.plural = RbnfSpeller(cardinal={Features(): "spellout-numbering"},
                                  ordinal={Features(): "spellout-ordinal-masculine-plural"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self.parser.cardinal(digits, Features(gender=features.gender), request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        value = bounded_integer(digits)
        if value is None or value > LARGEST_ORDINAL:
            raise DeclinedReading(f"no ordinal above {LARGEST_ORDINAL}")
        return self.parser.ordinal(digits, Features(gender=features.gender), request)

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        whole = self.cardinal(integer or "0", Features(), request)
        return f"{whole} {request.data['decimal_word']} {spell_digits(fraction, request)}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        if bounded_integer(numerator) == 1:
            bottom = "mezzo" if bounded_integer(denominator) == 2 else self.ordinal(denominator, Features(), request)
            return f"un {bottom}"
        value = bounded_integer(denominator)
        if value is None or value > LARGEST_PLURAL_ORDINAL:
            raise DeclinedReading(f"no plural ordinal above {LARGEST_PLURAL_ORDINAL}")
        bottom = self.plural.ordinal(denominator, Features(), request)
        return f"{self.cardinal(numerator, Features(), request)} {bottom}"


SPELLER = ItalianSpeller()


def _default_gender(request: Request) -> GrammaticalGender | None:
    return request.params.default_gender.get(LANGUAGE.code)


@lru_cache(maxsize=1)
def _noun_list() -> dict:
    path = files("text2spoken") / "data" / "wiktionary" / "it_noun_genders.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def noun_genders() -> dict[str, str]:
    """The gender of each noun of `data/wiktionary/it_noun_genders.json`, by its lowercase singular."""
    table = _noun_list()
    return {**dict.fromkeys(table["masculine"], M.value), **dict.fromkeys(table["feminine"], F.value)}


@lru_cache(maxsize=1)
def function_words() -> frozenset[str]:
    """The prepositions, conjunctions, adverbs, pronouns, determiners and articles of the Wiktionary categories, as
    "ieri", "circa" and "ciascuno"."""
    return frozenset(_noun_list()["function_words"])


@lru_cache(maxsize=1)
def both_gender_nouns() -> frozenset[str]:
    """The nouns of the noun list that are masculine and feminine, as "cantante" and "abitante"."""
    return frozenset(_noun_list()["both"])


@lru_cache(maxsize=1)
def scale_words() -> frozenset[str]:
    """The scale nouns that ovos-number-parser writes at the end of a number: "milione", "miliardi", "bilione". They
    stop where the parser writes a power of ten, as "uno per dieci elevato alla quarantadue"."""
    from ovos_number_parser import pronounce_number

    words = set()
    for power in range(6, DIGIT_BOUND, 3):
        try:
            readings = [pronounce_number(lead * 10 ** power, "it").split() for lead in (1, 2)]
        except (OverflowError, NotImplementedError):
            break
        if any(len(reading) != 2 for reading in readings):
            break
        words.update(reading[1] for reading in readings)
    return frozenset(words)


@lru_cache(maxsize=None)
def month_names(tag: str) -> tuple[str, ...]:
    """The month names of ovos-date-parser, January first."""
    from ovos_date_parser.spoken import spoken_date

    return tuple(spoken_date(tag, month=month) for month in range(1, 13))


def elides(word: str) -> bool:
    """Whether una elides before the word: before a vowel, but not before the semiconsonant of i or u and a
    vowel, as in "una iena"."""
    return word[:1] in VOWELS and not (word[:1] in "iu" and word[1:2] in VOWELS)


def one_before(noun: str, gender: str | None, request: Request) -> str:
    """1 before a noun, as the indefinite article: "una" before a feminine noun, "un'" before a feminine noun that
    starts with a vowel, "uno" before a masculine noun that takes lo, and "un" before another masculine noun."""
    if gender == F.value:
        return "un'" if elides(noun) else "una"
    if gender != M.value:
        raise DeclinedReading(f"no gender for {noun!r}")
    takes_lo = noun.startswith(tuple(request.data["lo_onsets"])) or (
        noun[:1] == "s" and noun[1:2] != "" and noun[1] not in VOWELS)
    return "uno" if takes_lo else "un"


def before_noun(words: str, noun: str) -> str:
    """The number words and the noun after them: with no space after an elided "un'", and with "di" after a scale
    word, as in "un milione di euro"."""
    if words.endswith("'"):
        return words + noun
    if words.split()[-1] in scale_words():
        return f"{words} di {noun}"
    return f"{words} {noun}"


def plain_amount(amount: FrozenMap, request: Request) -> str:
    """An amount with its sign, through the decimal speller for decimals and the cardinal speller for integers."""
    if amount["fraction"]:
        words = SPELLER.decimal(amount["integer"], amount["fraction"], Features(), request)
    else:
        words = SPELLER.cardinal(amount["integer"] or "0", Features(), request)
    return signed(words, amount["sign"], request)


def amount_before(amount: FrozenMap, noun: str, gender: str | None, request: Request) -> str:
    """An amount before its noun: the article form for 1, else the plain amount."""
    if amount["fraction"] or bounded_integer(amount["integer"] or "0") != 1:
        return plain_amount(amount, request)
    return signed(one_before(noun, gender, request), amount["sign"], request)


@lru_cache(maxsize=None)
def unit_nouns(tag: str) -> dict[str, str]:
    """The gender of each one-word CLDR unit name of a variety that CLDR gives a gender: "ora", "metro"."""
    return {name: unit["gender"] for unit in cldr_data(tag)["units"].values() if unit.get("gender")
            for pattern in unit["names"].values() if pattern.startswith("{0} ") and " " not in (name := pattern[4:])}


def counted_noun(word: str, request: Request) -> str | None:
    """The gender of a word after a number that the number counts: a scale word is masculine, a noun has its gender
    in the noun list, also a noun that is a function word too, as "via", and a CLDR unit name that the list leaves out
    has its CLDR gender, as "metro". The list comes first, because CLDR gives "miglio" the gender of its plural
    "miglia". A month name, as in `1 maggio`, writes a date and gives None."""
    if word in request.data["scales"]:
        return M.value
    if word in month_names(request.variety.tag):
        return None
    return noun_genders().get(word) or unit_nouns(request.variety.tag).get(word)


def counts_after_label(word: str, rest: str, request: Request) -> bool:
    """Whether 1 after a label noun counts the word, with `rest` the text after the word: a noun of
    `label_counted_nouns`, as "volta", or a CLDR unit name, as "anno". Any other word may be a verb that is also a
    noun, as "porta" in `il binario 1 porta a Roma`. A unit name that is also a function word, as "ora" ("now") and
    "secondo" ("according to"), counts too, as in `il percorso 1 ora circa`, except where the next words show the
    function word. A verb of `adverb_verbs` after "ora" makes it the adverb, as in `il binario 1 ora è chiuso` and `la
    linea 1 ora fa parte della rete`. A word of `preposition_units` before a determiner of `label_determiners` or a
    capital is the preposition, as in `il livello 1 secondo la scala`."""
    data = request.data
    if word in data["label_counted_nouns"]:
        return True
    if word not in unit_nouns(request.variety.tag):
        return False
    if word not in function_words():
        return True
    following = re.findall(r"[^\W\d_]+['’]?", rest[1:]) if rest[:1] == " " else []
    if any(following[:len(verb.split())] == verb.split() for verb in data["adverb_verbs"]):
        return False
    return not (word in data["preposition_units"] and following
                and (following[0].lower() in data["label_determiners"] or following[0][0].isupper()))


def scale_link(word: str) -> str | None:
    """What a scale word takes before the word. A function word takes nothing, as "adesso" in `2.000.000 adesso`. A
    noun of the list of either gender or of both, or its regular plural, -i for -o, -e or -a and -e for -a
    (Vocabolario Treccani, "plurale"), takes "di", as "abitanti". A word that is a noun and a function word, as "ieri"
    and "specie", a verb, as "erano", and a noun that the list does not hold, as the loanword "follower", give None."""
    nouns = noun_genders()
    if word in function_words():
        return None if word in nouns or word in both_gender_nouns() else ""
    stems = {"i": [word[:-1] + end for end in "oea"], "e": [word[:-1] + "a"]}.get(word[-1:], [])
    if any(form in nouns or form in both_gender_nouns() for form in (word, *stems)):
        return "di"
    return None


def word_before(text: str, start: int) -> str:
    """The word that one space separates from text[start:], with the full stop of an abbreviation, or ""."""
    if not text[:start].endswith(" "):
        return ""
    begin = start - 1
    while begin and (text[begin - 1].isalpha() or text[begin - 1] == "."):
        begin -= 1
    return text[begin:start - 1]


def is_label(text: str, start: int, request: Request) -> bool:
    """Whether a noun right before the number at text[start:] makes it a label: a noun of the noun list that a
    determiner of `label_determiners` comes before, as in `il binario 1` and `l'articolo 1`. A noun with no
    determiner may be a verb or a participle, as "visto" in `Ho visto 1 film`, so it makes no label. A noun of the
    list with a capital inside a sentence starts a name, as in `il mondiale di Formula 1`, and makes a label. The
    words of `label_abbreviations` and `label_nouns` make a label in every place, and `BeforeWord` reads them."""
    data = request.data
    word = word_before(text, start)
    lower = word.lower()
    if lower.endswith("."):
        return False
    begin = start - 1 - len(word)
    if word[:1].isupper() and text[:begin].endswith(" ") and is_word_char(text[begin - 2:begin - 1]):
        return lower in noun_genders()
    if text[begin - 1:begin] in ("'", "’"):
        elided = "".join(takewhile(str.isalpha, reversed(text[:begin - 1])))[::-1]
        determined = f"{elided.lower()}'" in data["label_determiners"]
    else:
        determined = word_before(text, begin).lower() in data["label_determiners"]
    return bool(word) and lower in noun_genders() and determined


def after_score(text: str, start: int, request: Request) -> bool:
    """Whether a number and a word of `score_words` come before the number at text[start:], as in `2 a 1` and
    `10 contro 1`."""
    word = word_before(text, start)
    rest = text[:start - 1 - len(word)]
    return word in request.data["score_words"] and rest.endswith(" ") and rest[-2:-1].isdigit()


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A number that `BeforeWord` finds reads by the role that its recognizer name ends in. 1 in other places
    reads by `default_gender`, and other numbers read through the core verbalizer."""
    fields, request = span.fields, context.request
    role = span.recognizer.removeprefix(f"{BeforeWord.name}:") if span.recognizer.startswith(BeforeWord.name) else None
    if fields["lead"] or (role is None and (bounded_integer(fields["digits"]) != 1 or len(fields["digits"]) > 1)):
        return core_speak_cardinal(span, context)
    if role is None:
        words = SPELLER.cardinal("1", Features(gender=_default_gender(request)), request)
        return signed(words, fields["sign"], request)
    word = "".join(takewhile(str.isalpha, context.after[0])) if context.after else ""
    if role == "noun":
        words = one_before(word, counted_noun(word, request), request)
    elif role == "scale":
        return f"{SPELLER.cardinal(fields['digits'], Features(), request)} di"
    elif role == "pronoun":
        words = SPELLER.cardinal("1", Features(gender=GrammaticalGender(request.data["partitive_words"][word])),
                                 request)
    elif role == "article":
        words = one_before(word, M.value, request)
    elif role == "capital":
        words = "un"
    else:
        words = SPELLER.cardinal("1", Features(), request)
    return signed(words, fields["sign"], request)


def speak_fraction(span: Span, context: SpanContext) -> str:
    """1/2 before a noun is the adjective mezzo, which agrees with the noun: "mezzo chilo di patate e mezza
    lattuga". Before "di" it is the noun "un mezzo". Before another lowercase word 1/2 stays as written. Another
    fraction is a noun, so before a word it reads only when the word is "di" or one of its forms. After a word of
    `label_nouns` or `label_abbreviations`, as in `numero 11/22`, the pair is a code and stays as written."""
    fields, after = span.fields, context.after
    half = bounded_integer(fields["numerator"]) == 1 and bounded_integer(fields["denominator"]) == 2
    labels = {word.rstrip(".") for word in (*context.request.data["label_abbreviations"],
                                            *context.request.data["label_nouns"])}
    if context.before and context.before[-1].lower().rstrip(".") in labels:
        raise DeclinedReading(f"a fraction after the label {context.before[-1]!r} is a code")
    if not half and after and after[0][:1].isalpha():
        link = re.split(r"(?<=['’])", after[0])[0]
        if link not in context.request.data["of_words"] and link.rstrip("'’") not in ("d", "dell"):
            raise DeclinedReading(f"a fraction before {after[0]!r}, which is not a form of di")
    word = after[0] if after and after[0].isalpha() and after[0].islower() else ""
    if not half or not word or word in context.request.data["half_links"] or fields["sign"]:
        return core_speak_fraction(span, context)
    gender = counted_noun(word, context.request)
    if gender is None:
        raise DeclinedReading("1/2 before a word that is not in the noun list")
    return "mezza" if gender == F.value else "mezzo"


def speak_ordinal(span: Span, context: SpanContext) -> str:
    """The marker gives the gender of the ordinal. After a mark of `noun_ordinal_marks` the ordinal agrees with the
    noun that follows: "3° piano" reads "terzo piano"."""
    request = context.request
    marker, word = span.fields["marker"], context.after[0] if context.after else ""
    gender = request.data["ordinal_marks"].get(marker) or counted_noun(word, request) or M.value
    return SPELLER.ordinal(span.fields["digits"], Features(gender=GrammaticalGender(gender)), request)


def fill(pattern: str, words: str) -> str:
    """A CLDR unit pattern with its number words, with no space after an elided "un'"."""
    return pattern.replace("{0} ", words) if words.endswith("'") else pattern.replace("{0}", words)


def speak_measure(span: Span, context: SpanContext) -> str:
    """The last amount agrees with the unit, by the CLDR gender of the unit or else by the noun list: "un
    chilometro", "un'ora". A scale word takes "di": "un milione di chilometri"."""
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    pattern, gender = unit_reading(request, span.fields["unit"], plural_category(request, written_amount(amounts[-1])))
    noun = pattern.replace("{0}", "").split()[0]
    gender = gender.value if isinstance(gender, GrammaticalGender) else gender or noun_genders().get(noun)
    read = [plain_amount(a, request) for a in amounts[:-1]] + [amount_before(amounts[-1], noun, gender, request)]
    words = f" {request.data['dimension_word']} ".join(read)
    if pattern.startswith("{0} ") and words.split()[-1] in scale_words():
        words += " di"
    return fill(pattern, words)


def speak_money(span: Span, context: SpanContext) -> str:
    """The amount and the currency name in the plural category of the amount: "quindici euro", "un euro". 1 takes
    the gender of the first word of the name in the noun list: "una sterlina britannica". A scale word comes between
    them, with "di": "due milioni di euro". Two decimals are the minor unit, when the currency names one: "dieci
    euro e cinquanta centesimi". Other decimals read as a decimal number: "uno virgola cinque euro"."""
    request = context.request
    fields = span.fields
    currency = currency_table(request)[fields["currency"]]
    amount = FrozenMap({**fields["amount"], "sign": ""})
    integer, fraction = amount["integer"] or "0", amount["fraction"]
    if fields["scale"]:
        scale = request.data["scales"][fields["scale"]]
        words = f"{amount_before(amount, scale, M.value, request)} {scale} di {currency_name(currency, 'other')}"
    elif fraction and not (len(fraction) == 2 and "minor" in currency):
        category = plural_category(request, written_amount(amount))
        words = f"{plain_amount(amount, request)} {currency_name(currency, category)}"
    elif fraction and int(fraction):
        cents = str(int(fraction))
        minor = _counted(cents, currency["minor"][plural_category(request, cents)], request,
                         currency["minor"].get("gender"))
        words = minor if bounded_integer(integer) == 0 else f"{_currency_amount(integer, currency, request)} e {minor}"
    else:
        words = _currency_amount(integer, currency, request)
    return signed(words, fields["amount"]["sign"], request)


def _counted(digits: str, name: str, request: Request, gender: str | None = None) -> str:
    """A whole number before a noun phrase of the given gender, or else of the gender of its first word in the noun
    list."""
    amount = FrozenMap({"integer": digits, "fraction": "", "sign": ""})
    noun = name.split()[0]
    return before_noun(amount_before(amount, noun, gender or noun_genders().get(noun), request), name)


def _currency_amount(integer: str, currency: FrozenMap, request: Request) -> str:
    return _counted(integer, currency_name(currency, plural_category(request, integer)), request)


def title_gender(text: str, position: int, data: FrozenMap) -> str:
    """The gender of the noun phrase that ends at the title at text[position:]: "feminine", "masculine", "" when the
    words before the title give no gender, or "kept" when they disagree or may not belong to the title. The walk back
    from the title, inside its line, steps over the words of `possessives` and `title_adjectives`. A determiner of
    `feminine_determiners` or `masculine_determiners` gives the gender, and an adjective of another gender makes it
    "kept", as `Lo nota Prof. Rossi`, where "nota" is a verb. Where the walk reaches the start of the line, the words
    are a letter heading, and the adjectives give the gender (Accademia della Crusca, consulenza 33625: "Egregia
    dottoressa Rossi"), or "kept" when they disagree. Where another word stops the walk, as "mattina" in `Questa mattina
    Prof. Rossi`, an adjective of one gender makes it "kept", because the word may be a verb, as "nota" in `Come nota
    Prof. Rossi`."""
    line = text[text.rfind("\n", 0, position) + 1:position]
    adjectives: set[str] = set()
    determiner = None
    stopped = False
    for word in reversed(re.findall(r"[^\W\d_]+['’]?|[^\w\s]", line)):
        lower = word.lower().replace("’", "'")
        if lower in data["title_adjectives"]:
            adjectives.add(data["title_adjectives"][lower])
        elif lower not in data["possessives"]:
            if lower in data["feminine_determiners"]:
                determiner = F.value
            elif lower in data["masculine_determiners"]:
                determiner = M.value
            elif lower not in data["label_determiners"]:
                stopped = True
            break
    gendered = adjectives - {"both"}
    if determiner:
        return determiner if gendered <= {determiner} else "kept"
    if stopped:
        return "kept" if gendered else ""
    return "kept" if len(gendered) > 1 else next(iter(gendered), "")


@dataclass(frozen=True)
class Abbreviation(CoreAbbreviation):
    """The abbreviations of the core. The recognizer name of a title of `feminine_titles` ends in the gender of
    `title_gender`, and a title whose gender is "kept" stays as written."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        for span in super().find(text, tokens, request):
            if span.fields["key"] in data["feminine_titles"]:
                gender = title_gender(text, span.start, data)
                span = replace(span, recognizer=f"{self.name}:{gender}", keep=gender == "kept")
            yield span


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    """The full word of the abbreviation, with a capital where a clause starts. A title of `feminine_titles` whose
    recognizer name ends in the feminine gender reads its feminine word: "la prof. Gallo" reads "la professoressa
    Gallo"."""
    data = context.request.data
    key = span.fields["key"]
    if span.recognizer == f"{Abbreviation.name}:{F.value}":
        return data["feminine_titles"][key]
    word = next(data[table][key] for table in ("titles", "abbreviations", "number_abbreviations")
                if data[table].get(key) is not None)
    return word[0].upper() + word[1:] if not context.before else word


def speak_date(span: Span, context: SpanContext) -> str:
    """The date words of ovos-date-parser: "primo maggio duemilaventiquattro"."""
    from ovos_date_parser.spoken import spoken_date

    fields = span.fields
    try:
        return spoken_date(context.request.variety.tag, day=fields["day"], month=fields["month"], year=fields["year"])
    except ValueError as error:
        raise DeclinedReading(f"ovos-date-parser reads no date {fields['day']}/{fields['month']}: {error}") from error


def speak_time(span: Span, context: SpanContext) -> str:
    """The time words of ovos-date-parser: "tredici e quarantacinque". A whole hour 0 or 12 reads "mezzanotte" or
    "mezzogiorno", unless the word before it is a word of `time_articles` with no form for that hour, as "le". The
    word of `time_articles` that `Clock` puts in the `prefix` field takes the form of its entry: "alle 12:00" reads "a
    mezzogiorno" and "alle 1:30" "all'una e trenta"."""
    from ovos_date_parser.spoken import spoken_time

    fields, request = span.fields, context.request
    hour, minute = day_hour(fields["hour"], fields["period"]), fields["minute"]
    word = fields["prefix"].strip()
    before = word or (context.before[-1] if context.before else "")
    forms = request.data["time_articles"].get(before.lower())
    named = minute == 0 and not fields["second"] and hour in (0, 12) and (forms is None or str(hour) in forms)
    try:
        if named:
            reading = spoken_time(request.variety.tag, hour, clock="12h", period=True)
        else:
            reading = spoken_time(request.variety.tag, hour, minute)
    except ValueError as error:
        raise DeclinedReading(f"ovos-date-parser reads no time {hour}:{minute:02}: {error}") from error
    if not word:
        return reading
    article = request.data["time_articles"][word.lower()][str(hour)]
    article = article[0].upper() + article[1:] if word[0].isupper() else article
    return article + reading if article.endswith("'") else f"{article} {reading}"


@dataclass(frozen=True)
class BeforeWord:
    """A whole number and one space before a lowercase word that ends the word. For 1, the recognizer name of each span
    ends in a role:
    `label` after a label abbreviation or a noun of `label_nouns` (`art. 1`, `numero 1`), after another label noun
    before a word that it does not count (`binario 1`, `Formula 1 è`), after a number and a word of `score_words`
    (`2 a 1`), and before a word of `score_words` (`1 a 0`, `1 su 3`, `1 contro tutti`), a preposition that no
    article comes before: "uno";
    `noun` before a noun that it counts: the article of the noun, "un anno", "uno zaino", "una gatta", "un'ora";
    `pronoun` before a word of `partitive_words`: "uno di loro", "una delle città";
    `article` before another word: the masculine article form, "un altro", "uno strano";
    `capital` before a word with a capital that is no label, as a name or a unit symbol that the file does not list:
    "un", as in `con 1 Airbus` and `fino a 1 Gbps`.
    Before a word of `kept_links`, as in `tra 1 e 2 ore`, 1 stays as written: its noun comes later. A number of
    another value whose words end in a scale word takes the role `scale` before a noun of the list or its plural:
    "due milioni di persone", "due milioni di abitanti". Before a word that neither list holds, as `2.000.000
    follower`, it stays as written."""
    name: str = "before_word"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        for number in numbers_in(text, request):
            if (number.sign or number.fraction is not None or not text.startswith(" ", number.end)
                    or (number.start and is_word_char(text[number.start - 1]))):
                continue
            word = "".join(takewhile(str.isalpha, text[number.end + 1:]))
            if not word:
                continue
            rest = text[number.end + 1 + len(word):]
            if rest[:1] and is_word_char(rest[0]):
                continue
            end, keep = number.end, False
            if number.integer != "1" or number.end - number.start != 1:
                if (not word.islower() or word in data["scales"] or word in data["label_determiners"]
                        or word in data["partitive_words"] or rest[:1] in ("'", "’") or (link := scale_link(word)) == ""
                        or SPELLER.cardinal(number.integer, Features(), request).split()[-1] not in scale_words()):
                    continue
                role, keep = "scale", link is None
            elif (word in data["score_words"] or after_score(text, number.start, request)
                  or word_before(text, number.start).lower() in {*data["label_abbreviations"], *data["label_nouns"]}
                  or (is_label(text, number.start, request) and not counts_after_label(word, rest, request))):
                role = "label"
            elif not word.islower():
                role = "capital"
            elif word in data["kept_links"]:
                role, keep = "label", True
            elif word in data["partitive_words"]:
                role = "pronoun"
            elif (gender := counted_noun(word, request)) is not None:
                role = "noun"
                end += gender == F.value and elides(word)
            else:
                role = "article"
            yield Span(number.start, end, Form.CARDINAL,
                       FrozenMap({"digits": number.integer, "sign": "", "lead": "", "prefix": "", "suffix": "",
                                  "script": number.script}), recognizer=f"{self.name}:{role}", keep=keep)


def may_be_clock(number: Number) -> bool:
    """Whether a number with two decimals may be a clock time: an hour up to 24 and two digits up to 59."""
    return (number.fraction is not None and len(number.fraction) == 2 and int(number.fraction) <= 59
            and len(number.integer) <= 2 and int(number.integer or "0") <= 24)


@dataclass(frozen=True)
class KeptDecimal:
    """In a variety with `keep_decimals`, a number with a decimal point that may be another form stays as written, also
    in an amount, a measure or a percentage: three digits after the point, as in `1.000`, may be a thousands group,
    and a letter right after the digits, as in `802.11g`, makes a name. With `clock`, a number that no amount,
    measure or percentage claims stays as written when it may be a clock time, as `8.00` and `12.30`: an hour up to
    24 and two digits up to 59."""
    name: str = "kept_decimal"
    form: Form = Form.DECIMAL
    clock: bool = False

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        if request.data.get("keep_decimals"):
            for number in numbers_in(text, request):
                if number.fraction is None:
                    continue
                if may_be_clock(number) if self.clock else (
                        len(number.fraction) == 3 or (number.end < len(text) and is_letter(text[number.end]))):
                    yield Span(number.start, number.end, Form.DECIMAL, number.amount(), recognizer=self.name,
                               keep=True)


@dataclass(frozen=True)
class KeptCommaTime:
    """A number with a decimal comma right after a word of `time_words`, as `ore 15,00` and `dalle ore 8,30`, stays
    as written when it may be a clock time. A clock time reads only with a mark of `clock_marks`, and no source gives
    the comma as a mark of the clock."""
    name: str = "kept_comma_time"
    form: Form = Form.DECIMAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for number in numbers_in(text, request):
            if (may_be_clock(number) and text[number.end - 3] == ","
                    and word_before(text, number.start).lower() in request.data["time_words"]):
                yield Span(number.start, number.end, Form.DECIMAL, number.amount(), recognizer=self.name, keep=True)


@dataclass(frozen=True)
class KeptApostrophe:
    """An acute accent (U+00B4) or a grave accent (U+0060) next to a letter stays as written: Italian writes an accent
    on its vowel, never as a mark of its own, so the mark stands for the apostrophe of an elision or a truncation, as
    in `l´Italia` or `Fra´ Giuseppe`, or for a quotation mark, as in `´Umbertì´`."""
    name: str = "kept_apostrophe"
    form: Form = Form.SYMBOL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in re.finditer(r"(?<=[^\W\d_])[´`]|[´`](?=[^\W\d_])", text):
            yield Span(match.start(), match.end(), Form.SYMBOL, FrozenMap({"symbol": match[0]}),
                       recognizer=self.name, keep=True)


@dataclass(frozen=True)
class KeptSign:
    """A sign of `sign_words` right after an opening bracket, then one space and a decimal or a number with a mark
    after it, as in `(- 2,8%)`, stays as written with the number and the form that the number starts: the space parts
    the sign from the number, so the sign may be a minus or a dash. A whole number alone, as in `(+ 2)`, reads."""
    name: str = "kept_sign"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        signs = "".join(request.data["sign_words"]) + "−"
        for match in re.finditer(rf"\(([{re.escape(signs)}]) ([0-9]+(?:[.,][0-9]+)*)", text):
            end = match.end()
            while end < len(text) and not text[end].isspace() and text[end] not in ")]":
                end += 1
            end = match.start(1) + len(text[match.start(1):end].rstrip(".,;:!?"))
            if end == match.end() and match[2].isdigit():
                continue
            yield Span(match.start(1), end, Form.CARDINAL,
                       FrozenMap({"digits": match[2], "sign": "", "lead": "", "prefix": "", "suffix": "",
                                  "script": "Latn"}), recognizer=self.name, keep=True)


@dataclass(frozen=True)
class KeptMoney:
    """An amount next to a sign of `kept_currency_signs`, as `2.500 ¥`, stays as written, with its number: CLDR
    `it` gives the sign to more than one currency."""
    name: str = "kept_money"
    form: Form = Form.MONEY

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        signs = FrozenMap({"kept": FrozenMap({"symbols": request.data["kept_currency_signs"]})})
        data = FrozenMap({**{k: v for k, v in request.language.data.items() if k != "currency_symbols"},
                          "currencies": signs})
        kept = Request(request.tag, request.variety, replace(request.language, data=data), request.params)
        return (replace(span, keep=True) for span in SHARED["money"].find(text, tokens, kept))


@dataclass(frozen=True)
class DateNamed:
    """`25 dicembre`, `1 maggio`, `1° maggio`: a day, one space and a month name of ovos-date-parser. Only 1 takes
    the degree sign. A year after the month reads as a cardinal, which is the form of `spoken_year`. Day 1 after an
    elided article, as in `dall'1 maggio`, stays as written: the elided article stands only before a vowel, and the
    day reads "primo"."""
    name: str = "date_named"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        months = month_names(request.variety.tag)
        for number in numbers_in(text, request):
            if (number.sign or number.fraction is not None or number.end - number.start > 2
                    or (number.start and is_word_char(text[number.start - 1]))):
                continue
            end = number.end + (number.integer == "1" and text[number.end:number.end + 1] == "°")
            word = "".join(takewhile(str.isalpha, text[end + 1:])) if text.startswith(" ", end) else ""
            if word not in months:
                continue
            stop = end + 1 + len(word)
            day, month = int(number.integer), months.index(word) + 1
            if is_bounded(text, number.start, stop) and is_valid(None, month, day):
                elided = day == 1 and text[number.start - 1:number.start] in ("'", "’")
                yield Span(number.start, stop, Form.DATE,
                           FrozenMap({"year": None, "month": month, "day": day, "written_order": "DMY",
                                      "month_written": "name", "prefix": "", "suffix": ""}), recognizer=self.name,
                           keep=elided)


@dataclass(frozen=True)
class DateDayMonth:
    """`il 13/11`, `dal 22/02`, `al 25/12`: a day above 12, a slash and a month 1 to 12 right after a word of
    `date_words`, a definite article or a preposition joined with one, read as a date with no year. A day of 12 or
    below may be a fraction, a time signature, a day range or a rating (`Il 3/4 è una frazione`, `il 4/4`, `del 3/4
    luglio`, `il 5/10 in pagella`), so in that place a pair with such a day stays as written, and so does a pair of
    `kept_day_months`, as `24/7`. Before a form of di of `of_words` and a word, as in `il 31/12 del quinto anno`, the
    pair stays as written too."""
    name: str = "date_day_month"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in re.finditer(r"(?<![0-9/])([0-9]{1,2})/([0-9]{1,2})(?![0-9/])", text):
            start, end = match.span()
            if text[start - 1:start] in ("'", "’"):
                letters = "".join(takewhile(str.isalpha, reversed(text[:start - 1])))[::-1]
                begin = start - 1 - len(letters)
                word = "" if begin and is_word_char(text[begin - 1]) else letters + "'"
            else:
                word = word_before(text, start)
            day, month = int(match[1]), int(match[2])
            after = text[end:].split(" ", 2)
            kept = (day <= 12 or match[0] in request.data["kept_day_months"]
                    or (text.startswith(" ", end) and len(after) == 3 and after[1] in request.data["of_words"]
                        and after[2][:1].isalpha()))
            if (word.lower() in request.data["date_words"] and is_bounded(text, start, end)
                    and is_valid(None, month, day)):
                yield Span(start, end, Form.DATE,
                           FrozenMap({"year": None, "month": month, "day": day, "written_order": "DMY",
                                      "month_written": "digits", "prefix": "", "suffix": ""}), recognizer=self.name,
                           keep=kept)


@dataclass(frozen=True)
class Clock(TimeClock):
    """The clock times of the core, with `:` or `.` between the hour and the minutes and a word of `time_words`
    before them. A word of `time_articles` with a form for the hour, right before a whole hour 0 or 12 or before the
    hour 1, joins the span with its space in the field `prefix`: `alle 12:00`, `alle 1:30`."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in super().find(text, tokens, request):
            fields = span.fields
            hour = day_hour(fields["hour"], fields["period"])
            word = word_before(text, span.start)
            forms = request.data["time_articles"].get(word.lower(), {})
            if str(hour) in forms and (hour == 1 or (fields["minute"] == 0 and not fields["second"])):
                yield replace(span, start=span.start - len(word) - 1,
                              fields=FrozenMap({**fields, "prefix": text[span.start - len(word) - 1:span.start]}))
            else:
                yield span


@dataclass(frozen=True)
class Ordinal:
    """`1º`, `2ª`: a whole number and a marker of the `ordinal_marks` table, with no full stop between them. A mark
    of `noun_ordinal_marks` makes an ordinal only before one space and a noun of `ordinal_nouns`, as in `3° piano`
    and `21° secolo`: in other places it is the degree sign of an angle or a coordinate, as in `46° nord`."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        for number in numbers_in(text, request):
            if number.sign or number.fraction is not None or (number.start and is_word_char(text[number.start - 1])):
                continue
            marker = text[number.end:number.end + 1]
            if marker in data["noun_ordinal_marks"]:
                word = "".join(takewhile(str.isalpha, text[number.end + 2:]))
                noun = text.startswith(" ", number.end + 1) and word in data["ordinal_nouns"]
                marker = marker if noun else ""
            if marker in (*data["ordinal_marks"], *data["noun_ordinal_marks"]) \
                    and is_bounded(text, number.start, number.end + 1):
                yield Span(number.start, number.end + 1, Form.ORDINAL,
                           FrozenMap({"digits": number.integer, "marker": marker, "prefix": "", "suffix": "",
                                      "script": number.script}), recognizer=self.name)


LANGUAGE = LanguageSpec(
    code="it",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], KeptSign(), DateNamed(), DateDayMonth(), SHARED["date_numeric"], Clock(),
                 KeptDecimal(), SHARED["money"], KeptMoney(), SHARED["percent"], SHARED["measure"],
                 SHARED["expression"], SHARED["fraction"], Ordinal(), Abbreviation(),
                 KeptDecimal(name="kept_clock", clock=True), KeptCommaTime(), SHARED["decimal"], BeforeWord(),
                 SHARED["cardinal"], SHARED["emoji"], KeptApostrophe(), SHARED["symbol"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.DATE: speak_date, Form.TIME: speak_time, Form.MONEY: speak_money,
        Form.PERCENT: speak_percent, Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression,
        Form.FRACTION: speak_fraction, Form.ORDINAL: speak_ordinal, Form.ABBREVIATION: speak_abbreviation,
        Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal, Form.SYMBOL: speak_symbol, Form.EMOJI: speak_emoji,
    },
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER},
    attach=drop_affixes,  # the one prefix, a word of `time_articles` before a time, is a word of the time reading
    genders=frozenset({M, F}),
    default_gender=M,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={"date_order": frozenset({"DMY", "MDY", "YMD"}), "clock": frozenset({"24h"}),
             "default_gender": frozenset({"masculine", "feminine"})},
    not_applicable=frozenset(OPTIONS) - {"date_order", "clock", "default_gender"},
)
