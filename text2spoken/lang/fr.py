"""French: fr-FR, the default variety, fr-CA and fr-CH. Every other `fr-*` tag reads as fr-FR.

Number words come from the numtag writer, by the tag, so `fr-BE` and `fr-CH` say "septante" and "nonante",
`fr-CH` says "huitante", and every other region says "soixante-dix", "quatre-vingts" and "quatre-vingt-dix", in the
traditional spelling "vingt et un" and "soixante et onze".

Agreement. A number that ends in 1 says "un" or "une" with its noun: "vingt et un kilos", "vingt et une heures".
The gender of a number comes, in this order, from the hint of the caller, from the words after the number, from
`default_gender`, and from the file, which is masculine. A unit and a currency carry their own gender.

The gender of a noun comes from the noun list `data/wiktionary/fr_noun_genders.json`, which
`scripts/extract_noun_genders.py fr` makes from the categories "French masculine nouns", "French feminine nouns" and
"French nouns with multiple genders" of the English Wiktionary (CC BY-SA 4.0), corrected by
`scripts/fr_noun_gender_corrections.json` where the French Wiktionary gives the opposite single gender, as for
"bobsleigh". The list holds the singular, so a
plural reads through the singulars that `_singulars` gives it: `21 tonnes` reads "vingt et une tonnes". A noun of both
categories or of several genders, as "élève", "enfant" and "livre", takes no gender from the list, so `1 livre` reads
"un livre", and the table `feminine_nouns` names the few of them that count things only as feminine nouns, as "page".
An adjective of `preposed_adjectives` between the number and its noun agrees with the noun, so a form that marks a
gender gives it: `1 belle maison` reads "une belle maison"; "jeune" marks none and passes to the noun. A function
word gives no gender (`_noun_after`), and a number that names a numeral or a numéro takes none (`_named`).

The rules cite these sources, by rule family:

- The gender of "un": Office québécois de la langue française, Vitrine linguistique, "Déterminant numéral se
  terminant par un": "Lorsqu'il fait partie d'un déterminant numéral composé, un est variable seulement en genre",
  "Trente et une espèces de parulines", "Vingt et un mille personnes [...] Vingt et un détermine le nom mille, et non
  le nom personnes".
- Cardinals, the agreement of "cent", "vingt" and "mille", and years: Académie française, Questions de langue,
  "Nombres (écriture, lecture, accord)" (academie-francaise.fr/questions-de-langue). It gives the hyphen and "et"
  rule, "quatre-vingts hommes" but "quatre-vingt-deux hommes", "deux cents euros" but "deux cent vingt euros",
  "deux cents millions d'années", "Mille (ou mil) est toujours invariable", and the singular of a numeral that
  stands for an ordinal: "Ils restent également invariables lorsqu'ils sont employés comme adjectifs numéraux
  ordinaux : page deux cent ; page quatre-vingt ; l'an mille neuf cent." The file reads that singular in an
  ordinal ("deux cent millionième"), in a year, and in a number that labels a page or a year, as the passage
  writes them: "page" and "l'an", which the table `ordinal_nouns` holds, with only spaces before the number.
  Both ends of a range read so: "page 80-90" is "page quatre-vingt à quatre-vingt-dix". The table holds the other
  labels of a numeral with "une valeur ordinale" of the Office québécois de la langue française, Vitrine
  linguistique, "Pluriel de vingt, de cent et de mille": "Le paragraphe quatre-vingt (le 80e paragraphe)",
  "L'article quatre-vingt (le 80e article)", "Le quatre-vingt de la rue des Érables (le numéro 80)", so "numéro",
  and with it `n°`, reads so; and the decade of Larousse, "quatre-vingts, quatre-vingt", Difficultés: "S'écrit sans
  s à vingt quand il est employé comme adjectif numéral ordinal [...] les années quatre-vingt", which "des années"
  and "aux années" contract.
- A mixed number of a half: Dictionnaire de l'Académie française, 9th edition, "demi", II.1: "La moitié d'une
  unité", "Douze et demi ou 12,5". So `12 1/2` reads "douze et demi". Before a noun, "demi" follows the noun and
  agrees with it, I.1: "Coordonné par et à un nom précédé d'un numéral, s'accorde en genre", "Il va bientôt être
  trois heures et demie". So with no noun the whole part and the half take the gender of `default_gender`, and
  `2 1/2 heures` stays as written. No source gives the reading of a mixed number of another fraction, so it stays
  as written.
- A noun after a round million or milliard: the same entry, "vingt et cent varient devant millier, million,
  milliard, qui sont des noms et non des adjectifs numéraux : [...] deux cents millions d'années ; trois cents
  milliers d'habitants." Larousse, "million", Difficultés: "Le nom complément de million ou de milliard se
  construit toujours avec de". So a number whose words end in a noun of `scale_nouns`, or a number that the text
  writes before one, takes "de" before the noun that it counts: "un million d'habitants". The rule reads a range
  whose high end is a round million so too. A word that is not that noun takes none: a function word of
  `no_de_words`, an adjective of `no_de_adjectives`, a participle of `no_de_participles`, a verb with an inverted
  subject ("disent-ils"), an imperative with an object pronoun ("croyez-moi"), a word of one letter, a mark or the
  end of the text.
- The noun that a million counts is plural, and a plural noun ends in "s", "x" or "z": Office québécois de la
  langue française, Banque de dépannage linguistique, "Pluriel des mots d'origine étrangère : rectifications":
  such words "suivent la règle générale du singulier et du pluriel des mots français. Ils prennent donc un s au
  pluriel, sauf s'ils se terminent par un s, un x ou un z". So a word with another ending takes no "de", such as
  the verb in "2 000 000 manifestent", unless `invariable_plurals` holds it. A word with a hyphen counts as one,
  and it is plural when any of its parts is: "années-lumière", "timbres-poste".
- "De" before a vowel or a mute h elides to "d'". The words of `aspirated_h` and the words derived from them begin
  with an aspirated h, which takes no elision: Office québécois de la langue française, Banque de dépannage
  linguistique, "La prononciation du h aspiré": "Voici une liste des principaux mots qui commencent par un h
  aspiré, dont plusieurs comportent des dérivés", and "dans le cas du h aspiré, on ne peut faire l'élision". The
  page "Élision interdite" of the same bank gives the other cases: "C'est le cas de la plupart des noms propres
  qui commencent par un h", so a capitalised h takes no elision. That is a tendency: the page "Noms propres :
  quand faire l'élision" says "il n'existe pas de règle systématique et que l'usage varie considérablement", and
  the page "HAÏTI, HAÏTIEN et HAÏTIENNE : élision et liaison" finds "une forte tendance à le considérer comme un h
  muet", with "originaire d'Haïti" and "de nombreux Haïtiens", so the words of `eliding_h` elide. A word all in
  capitals, such as "HABITANTS", is no proper noun and follows the rules of its lowercase form. A y before a
  consonant is a vowel, and a y before a vowel is the yod: Académie française, Dictionnaire, 9th edition, "Y":
  "La liaison et l'élision se font avec les mots qui commencent par un y se prononçant i, comme dans l'ypérite.
  Elles ne se font pas si y sert à noter le yod, comme le yack, la yole, sauf avec yeux et yeuse". So "de" elides
  before a y and a consonant ("d'Yvelinois"), and before a y and a vowel only in a word of `eliding_y`. The OQLF
  page "Élision interdite" names the same yod words: "Devant les mots étrangers commençant par y, il ne faut pas
  faire d'élision", "yacht, yankee, yaourt". "Il ne faut pas faire d'élision devant les mots oui et ouistiti",
  which `no_elision` holds.
- Ordinals: Académie française, Questions de langue, "Deuxième, second": "seul deuxième entre dans la formation
  des ordinaux complexes (vingt-deuxième, etc.)". Dictionnaire de l'Académie française, 9th edition, "unième":
  "Ne s'emploie qu'avec les nombres vingt, trente, quarante, cinquante, soixante, quatre-vingts, cent et mille,
  souvent précédé de et", with the example "la mille et unième nuit". So 101e is "cent et unième" and 1001e is "mille et unième".
  The marks are "lettres minuscules surélevées", and "Lorsqu'il n'est pas possible de surélever les lettres, il est
  admis de les écrire sur la ligne" (Office québécois de la langue française, Vitrine linguistique, "Abréviation de
  l'adjectif ordinal"). Plain text writes the raised letters with the Unicode modifier letters ᵉ (U+1D49), ʳ
  (U+02B3), ˢ (U+02E2), ᵈ (U+1D48) and ⁿ (U+207F), so `2ᵉ`, `1ᵉʳ`, `1ʳᵉ`, `2ᵈᵉ` and `XIXᵉ` read as `2e`, `1er`,
  `1re`, `2de` and `XIXe` do, and so does `1ᵉʳ` in a date.
- Times: the same "Nombres" entry ("deux heures et demie", "midi et quart"), and the SI Brochure, Table 8, for the
  symbol `h` of the hour.
- Number marks and gaps: BIPM, The International System of Units (SI Brochure), 9th edition. Section 5.4.4 says
  that the decimal marker is the point or the comma on the line, and that the digits "may be divided into groups
  of three by a space". Section 5.4.3 puts a space between a number and its unit symbol, and section 5.4.7 a space
  between a number and `%`.
- A half before a noun: Wiktionnaire, "demi", Notes: "reste invariable quand il le précède", "Une demi-heure.".
- Elision: Wiktionnaire, "l’", Forme d'article défini: "Élision des articles définis le et la devant une voyelle
  ou un h muet", so `3 l'an` holds an article and no litre.
- Telephone numbers: ITU-T E.164 country codes (1 for Canada, 32 for Belgium, 33 for France, 41 for Switzerland)
  and the ARCEP numbering plan of France for the ten digits read in pairs.
- Abbreviations, amounts (`k`, `M`, `Md`) and Roman numerals after a sovereign or before `e`: Lexique des règles
  typographiques en usage à l'Imprimerie nationale.
- `cf.`, `env.`, `av. J.-C.`, `apr. J.-C.`, `boul.` and `Me`: Office québécois de la langue française, Vitrine
  linguistique, "Liste d'abréviations courantes": "confer (« reportez-vous à ») | cf.", "environ | env.", "avant
  Jésus-Christ | av. J.-C.", "après Jésus-Christ | apr. J.-C.", "boulevard | boul.", and "Me" for "maître (avocat ou
  avocate, notaire)". The Wiktionnaire gives `ap. J.-C.` ("Par abréviation de après Jésus-Christ") and `bd`
  ("Abréviation de boulevard", "8, bd Bonne-Nouvelle"). `Me` and `bd` are also the pronoun "me" and the noun "bd",
  so they read only as titles do, before a capitalised name: "Me Dupond", "bd Haussmann". The full stop of a
  `J.-C.` abbreviation also ends a sentence, as the one of `etc.` does.
- Unit, month and currency names: CLDR `common/main` `fr`, `fr_CA` and `fr_CH`. The volt and its multiples: SI
  Brochure, Table 4 ("volt", "V") and Table 7 (the prefixes "kilo", "k", and "milli", "m").
- A written "million" or "milliard" before a currency symbol, as in `1 million €`, reads as the scale `M` does, with
  "de" before the currency, by the Larousse rule above: "un million d'euros".
- A rate after a currency symbol, as in `5 €/mois`: see `speak_french_abbreviation`.

The rows of `tests/data/fr.tsv` give the source of each expected reading. The rows of the telephone, abbreviation,
date, money and Imprimerie nationale families say that their source was not fetched.
"""
from __future__ import annotations

import json
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace
from decimal import Decimal
from functools import lru_cache
from importlib.resources import files

from text2spoken.core.currencies import currency_symbols
from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety, plural_category
from text2spoken.core.color import speak_color
from text2spoken.core.numbers import GROUP_SPACES, Number, written_amount
from text2spoken.core import roman
from text2spoken.core.recognizers import (
    PHONE_PLANS,
    SHARED,
    Cardinal,
    Decimal as DecimalRecognizer,
    Money,
    Percent,
    Range,
    Telephone,
    TimeClock,
    _affixes,
    _scale,
    amount_words,
    join_ranges,
    number_gaps,
    numbers_in,
    signed,
    speak_abbreviation,
    speak_decimal,
    speak_expression,
    speak_idiom,
    speak_lexicon,
    speak_mixed_half,
)
from text2spoken.core.spans import Features, Span, SpanContext, clause_breaks, clause_window, context_words
from text2spoken.core.spellers import NumtagSpeller, spell_digits
from text2spoken.core.times import twelve_hour
from text2spoken.core.tokens import (
    Token,
    fold_digits,
    is_bounded,
    is_digit,
    is_letter,
    is_word_char,
    next_visible,
    one_digit_set,
)
from text2spoken.params import Form, FrozenMap, GrammaticalGender, freeze

FEMININE, MASCULINE = GrammaticalGender.FEMININE, GrammaticalGender.MASCULINE
GROUP = GROUP_SPACES + "'\u2019"
"""The group marks of a number: the spaces of `GROUP_SPACES`, and the apostrophe that Switzerland writes, as in
`1'000`."""
_SPACE = "[" + GROUP_SPACES + "]"

_ROMAN_RUN = re.compile("[IVX]+")

MONTHS = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]
_MONTH = "(" + "|".join(f"[{m[0].upper()}{m[0]}]{m[1:]}" for m in MONTHS) + ")"
_YEAR = "([0-9][0-9][0-9][0-9])"
_DAY = "([0-9][0-9]?)(er|\u1d49\u02b3)?"

FEMININE_NOUNS = ("page", "pages", "part", "parts", "orange", "oranges", "souris")
"""The nouns of both gender categories of `fr_noun_genders.json` that count things only as feminine nouns. The English
Wiktionary gives the feminine "page" of a book and the masculine "page", a page boy; the feminine "part", a share or a
slice, and the masculine "part", a newborn; the feminine "orange", the fruit, and the masculine "orange", the colour;
and the feminine "souris", a mouse, and the masculine "souris", "archaic, literary" for a smile."""

DETERMINERS = {
    **dict.fromkeys(("le", "un", "ce", "cet", "mon", "ton", "son", "du", "au"), "masculine"),
    **dict.fromkeys(("la", "une", "cette", "ma", "ta", "sa"), "feminine"),
    **dict.fromkeys(("l'", "notre", "votre", "leur"), "singular"),
    **dict.fromkeys(("les", "des", "ces", "mes", "tes", "ses", "nos", "vos", "leurs", "aux"), "plural"),
}
"""The articles, demonstratives and possessives, by the gender or the number that they mark: the forms of the French
Wiktionary, "le", "la", "les", "ce", "cette", "ces", "mon", "ma", "mes", and the contractions "du", "au" and "aux"
of "de" and "à" with "le" and "les"."""

PREPOSED_ADJECTIVES = {
    **dict.fromkeys(("vieux", "vieil", "beau", "bel", "beaux", "joli", "jolis", "bon", "bons", "petit", "petits",
                     "grand", "grands", "gros", "meilleur", "meilleurs", "nouveau", "nouvel", "nouveaux", "seul",
                     "seuls"), "masculine"),
    **dict.fromkeys(("vieille", "vieilles", "belle", "belles", "jolie", "jolies", "bonne", "bonnes", "petite",
                     "petites", "grande", "grandes", "grosse", "grosses", "meilleure", "meilleures", "nouvelle",
                     "nouvelles", "seule", "seules"), "feminine"),
    **dict.fromkeys(("jeune", "jeunes"), "both"),
}
"""The adjectives that come before the noun, in each form: Bureau de la traduction, Clés de la rédaction, "adjectif
(place de l'adjectif avec un nom)": "L'adjectif est généralement placé avant le nom dans les cas suivants : il est
court ou très courant (jeune, vieux, beau, joli, bon, petit, grand, gros, meilleur, nouveau, etc.) : une belle fille
une nouvelle maison un vieux vêtement", and "un seul homme". An adjective agrees with its noun, so a form that marks a
gender gives the gender of the number before it, as in "une belle maison", and "jeune", which marks none, passes to
the next word."""


NO_DE_WORDS = (
    "adementiers", "adens", "adoncques", "aels", "ailleurs", "alakons", "alias", "alles", "alors", "als", "après",
    "après-après-demain", "après-demain", "aprés", "assez", "assés", "au-dedans", "au-dehors", "au-dessous",
    "au-dessus", "aucunefois", "aucunes", "aucunesfois", "aucuns", "auprès", "autrefois", "aux", "auxdites", "auxdits",
    "auxquelles", "auxquels", "avecques", "bis", "celles", "celles-ci", "celles-là", "celleux", "certaines", "certains",
    "certes", "ces", "cesdites", "cesdits", "ceulles", "ceuss", "ceusses", "ceux", "ceux-ci", "ceux-là", "ceuxelles",
    "chacunes", "chacuns", "chacunx", "chaques", "cheux", "chez", "ci-après", "ci-delez", "ci-dessous", "ci-dessus",
    "ci-plus-bas", "ci-plus-haut", "clas", "class", "combiennièmes", "combientièmes", "céans", "dans", "decies",
    "dedans", "dehors", "depuis", "des", "desdites", "desdits", "desquelles", "desquels", "dessous", "dessus", "devers",
    "directos", "discrétos", "dix-huitièmement", "dix-neuvièmement", "dix-septièmement", "ds", "duodecies",
    "duotricies", "dès", "dès-méshui", "désormais", "elles", "elles-mêmes", "elleux", "embas", "emprès", "endéans",
    "entre-temps", "entretemps", "envers", "es-qualité", "esdites", "esdits", "eusses", "eux", "eux-autres",
    "eux-mêmes", "ex-aequo", "ex-æquo", "exprès", "extramuros", "fors", "gratis", "gratos", "guères", "hormis", "hors",
    "hors-service", "icelles", "iceux", "ici-bas", "ici-dedans", "iels", "ilelles", "illes", "ils", "ils-elles",
    "intra-muros", "intramuros", "jadis", "jamais", "je-ne-sais-quoi", "jusques", "labès", "lars", "les", "lesdites",
    "lesdits", "lesquelles", "lesquels", "leurs", "leursdites", "leursdits", "leurszigues", "leurzigues", "lez",
    "lombienquess", "long-temps", "long-tems", "longtemps", "longtems", "lors", "là-bas", "là-dedans", "là-delez",
    "là-dessous", "là-dessus", "lès", "léans", "maintefois", "maintes", "maints", "mais", "malgrés", "max", "mes",
    "mesdites", "mesdits", "mesmes", "mi-jambes", "mi-mars", "miennes", "miens", "mieux", "minoribus", "moins",
    "mordicus", "mouais", "moultes", "moults", "naguères", "nix", "nonies", "nos", "noszigues", "nous", "nous-même",
    "nous-mêmes", "novovicies", "nozigues", "nu-bras", "néanmoins", "nôtres", "octies", "octotricies", "octovicies",
    "ols", "oncques", "onques", "orains", "ordoncques", "ores", "par-dehors", "par-dessous", "par-dessus", "par-devers",
    "parfois", "parmis", "pedibus", "peinardos", "pis", "plus", "plusieurs", "près", "puis", "pus", "qqns", "quantes",
    "quaterdecies", "quatertricies", "quelquefois", "quelques", "quelques-ans", "quelques-unes", "quelques-uns",
    "quindecies", "quinquies", "quintricies", "quinvicies", "quèques", "raiz", "rapidos", "ras-le-cresson", "rasibus",
    "razibus", "rez", "rémotis", "sans", "sans-façon", "septies", "septtricies", "septvicies", "ses", "sexies",
    "sextricies", "sexvicies", "siennes", "siens", "soubs", "sous", "souventefois", "ss", "sus", "tandis", "terdecies",
    "tertricies", "tes", "tiennes", "tiens", "tjrs", "tjs", "toujours", "tous", "toustes", "toutefois", "toutes",
    "toutxs", "touz", "toûjours", "tranquillos", "tricies", "très", "ts", "ttes", "uls", "undecies", "untricies", "unx",
    "vers", "versus", "vicies", "volontiers", "vos", "voszigues", "vous", "vous-même", "vous-mêmes", "vozigues", "vs",
    "vôtres", "yels", "z-en", "à-la-fois", "æls", "çauz", "ès",
)
"""The French function words that end in "s", "x" or "z", which take no "de" after a round million: the determiners,
pronouns, prepositions, conjunctions and adverbs of the French Wiktionnaire part-of-speech categories, such as
"Prépositions en français", "Adverbes en français", "Pronoms personnels en français" and "Déterminants possessifs en
français", with their hyphenated members that have such a part, such as "là-bas", "au-dessus", "eux-mêmes" and
"après-demain". The words that also read as a noun or a preposed adjective after a number are not in the table, so
"un million de fois", "un million de pas", "un million d'autres choses" and "un million de vis-à-vis" keep their
"de"."""

NO_DE_ADJECTIVES = (
    "derniers", "dernières", "premiers", "premières", "précédents", "précédentes", "inclus", "incluses", "passés",
    "passées", "déversés", "déversées", "supplémentaires", "nets", "nettes", "bruts", "brutes", "annuels",
    "annuelles", "restants", "restantes", "cumulés", "cumulées",
)
"""The adjectives and participles that follow a bare amount with no noun between them, as in "deux millions
supplémentaires". The table holds each one that a measurement found right after a number, in figures or written
as a scale noun, in Tatoeba French (730,700 sentences) and the FLORES+ French dev and devtest splits, with its
other genders, and the adjectives "supplémentaires", "nets", "bruts", "annuels", "restants" and "cumulés". The
class is open, so an adjective that the table lacks takes a wrong "de"."""

NO_DE_PARTICIPLES = (
    "versés", "versées", "investis", "investies", "répartis", "réparties", "placés", "placées", "prévus", "prévues",
    "promis", "promises", "économisés", "économisées", "dépensés", "dépensées", "perçus", "perçues", "gagnés",
    "gagnées", "perdus", "perdues", "levés", "levées", "alloués", "allouées", "engagés", "engagées", "débloqués",
    "débloquées", "empruntés", "empruntées", "remboursés", "remboursées", "collectés", "collectées",
)
"""The participles that follow a sum of money with no noun between them, as in "deux millions versés en deux fois",
in their plural forms. A singular form ends in no "s" and takes no "de" by the plural check. No form occurs as a
counted noun after an amount in Tatoeba French or the FLORES+ French dev and devtest splits. The class is open, so
a participle that the table lacks takes a wrong "de"."""

INVERTED_PRONOUNS = ("je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles")
"""The subject pronouns, which follow the verb when the subject is inverted: "vois-tu", "disent-ils", "a-t-on". A
hyphenated word with one of them after its first part is that verb and takes no "de", unless `invariable_plurals`
holds it."""

IMPERATIVE_PRONOUNS = ("moi", "toi", "le", "la", "les", "lui", "leur", "y", "en")
"""The object pronouns that close a verb in the imperative: "croyez-moi", "allez-y", "avouons-le". Office québécois de
la langue française, Banque de dépannage linguistique, "Trait d'union pour unir différents éléments du discours": "Le
trait d'union unit également le pronom personnel complément, qu'il soit complément direct ou indirect", as in
"Repose-toi" and "Dites-le-moi"; and "Ajout d'un S entre le verbe et les pronoms EN et Y": "Vas-y sans tarder",
"Manges-en autant que tu en veux". A hyphenated word whose last part is one of them is that verb and takes no "de",
unless `invariable_plurals` holds it. Only the last part counts, so "cessez-le-feu" stays a noun. A noun that ends in
one of them, such as "chez-moi", "revenez-y" or "chromosomes-Y", takes no "de" either."""

ELIDED_PRONOUNS = ("m", "t")
"""The elided pronouns "m'" and "t'" that close a verb in the imperative: "donnez-m'en", "souviens-t'en". Office
québécois de la langue française, "Verbes à l'impératif : ordre des pronoms et trait d'union": "Devant les pronoms en
et y, on fait l'élision des pronoms me et te (qui se substituent à moi et toi)", as in "Donnez-m'en un kilo" and
"Occupe-t'en". The word ends at the apostrophe, so a last part of the word that is one of them marks that verb only
when a mark of `elision_marks` follows it. A letter label keeps its "de": "lymphocytes-T"."""

INVARIABLE_PLURALS = ("abat-jour", "graffiti", "people", "rendez-vous", "garde-à-vous")
"""Nouns whose plural is the singular, and which take "de" after a round million. The plural check stops "abat-jour",
"graffiti" and "people", which have no part that ends in "s", "x" or "z". The pronoun check stops "rendez-vous" and
"garde-à-vous", which have the form of a verb with an inverted subject. The French Wiktionnaire gives "abat-jour" as
invariable in the traditional spelling, "graffiti" as a plural of "graffito", "people" as its own plural,
"rendez-vous" as invariable, and "garde-à-vous" as "masculin, singulier et pluriel identiques"."""

ASPIRATED_H = (
    "hache", "hagard", "haie", "haillon", "haine", "haïr", "hall", "halo", "halte", "hamac", "hambourg", "hamburger",
    "hameau", "hampe", "hamster", "hanche", "handicap", "hangar", "hanter", "happer", "harceler", "hardi", "harem",
    "hareng", "harfang", "hargne", "haricot", "harnais", "harpe", "hasard", "hâte", "hausse", "haut", "havre", "hennir",
    "hérisser", "hernie", "héron", "héros", "hêtre", "heurter", "hibou", "hic", "hideur", "hiérarchie", "hippie",
    "hisser", "hocher", "hockey", "hollande", "homard", "hongr", "honte", "hoquet", "horde", "hors", "hotte", "houblon",
    "houle", "housse", "huard", "hublot", "huche", "huer", "huit", "humer", "hurler", "huron", "husky", "hutte",
)
"""The principal words with an aspirated h, as the Office québécois de la langue française lists them, with the starts
"hongr" and "hambourg" from its page "Noms propres : quand faire l'élision": "(par exemple, hongrois : de Hongrie)",
"les habitants de Hambourg". The French Wiktionnaire marks "Hambourg" and the noun "hambourgeois" as "h aspiré". A
word that starts with one of them, less a final "e", "er" or "ir" when four letters remain, has an aspirated h, as
the derived words of the list do: "handicapés", "hauteurs", "hockeyeurs", "harceleurs", "hérissons"."""

MUTE_H = (
    "hallucin", "halogèn", "haltè", "haltér", "hallali", "hallo", "hippiq", "hippism", "huitre", "hurluberlu",
)
"""The starts of words with a mute h that the start of an `aspirated_h` word would match, as the French Wiktionnaire
gives them with no aspirated-h mark: "hallucination", "halogène", "haltère", "hippique", "hippisme" (\\i.pism\\,
"h muet"), "huitre"."""


def _unit(one: str, gender: str = "masculine", other: str | None = None, many: str | None = None) -> dict:
    """A unit: its name for one, for other numbers and after "million", and its gender. The name after a million
    takes "de", or "d'" before a vowel or a mute h: "un million d'euros", "deux millions de kilomètres"."""
    other = other or one + "s"
    de = "d'" if other[0] in "aeiouyéèêàâîôûh" and not other.startswith(("hertz", "huit")) else "de "
    return {"one": one, "other": other, "many": many or de + other, "gender": gender}


UNITS = {
    "kg": _unit("kilogramme"),
    "g": _unit("gramme"),
    "mg": _unit("milligramme"),
    "km": _unit("kilomètre"),
    "m": _unit("mètre"),
    "cm": _unit("centimètre"),
    "mm": _unit("millimètre"),
    "km/h": _unit("kilomètre par heure", other="kilomètres par heure", many="de kilomètres par heure"),
    "m/s": _unit("mètre par seconde", other="mètres par seconde", many="de mètres par seconde"),
    "tr/min": _unit("tour par minute", other="tours par minute", many="de tours par minute"),
    "l": _unit("litre"),
    "L": _unit("litre"),
    "ml": _unit("millilitre"),
    "mL": _unit("millilitre"),
    "cl": _unit("centilitre"),
    "cL": _unit("centilitre"),
    "dl": _unit("décilitre"),
    "dL": _unit("décilitre"),
    "m²": _unit("mètre carré", other="mètres carrés", many="de mètres carrés"),
    "km²": _unit("kilomètre carré", other="kilomètres carrés", many="de kilomètres carrés"),
    "m³": _unit("mètre cube", other="mètres cubes", many="de mètres cubes"),
    "ha": _unit("hectare"),
    "h": _unit("heure", "feminine"),
    "min": _unit("minute", "feminine"),
    "s": _unit("seconde", "feminine"),
    "°C": _unit("degré Celsius", other="degrés Celsius", many="de degrés Celsius"),
    "°F": _unit("degré Fahrenheit", other="degrés Fahrenheit", many="de degrés Fahrenheit"),
    "°": _unit("degré"),
    "Hz": _unit("hertz", other="hertz"),
    "kHz": _unit("kilohertz", other="kilohertz"),
    "MHz": _unit("mégahertz", other="mégahertz"),
    "GHz": _unit("gigahertz", other="gigahertz"),
    "kW": _unit("kilowatt"),
    "MW": _unit("mégawatt"),
    "Wh": _unit("wattheure"),
    "kWh": _unit("kilowattheure"),
    "hPa": _unit("hectopascal"),
    "kPa": _unit("kilopascal"),
    "kcal": _unit("kilocalorie", "feminine"),
    "ko": _unit("kilooctet"),
    "Ko": _unit("kilooctet"),
    "Mo": _unit("mégaoctet"),
    "Go": _unit("gigaoctet"),
    "To": _unit("téraoctet"),
    "Kio": _unit("kibioctet"),
    "Mio": _unit("mébioctet"),
    "Gio": _unit("gibioctet"),
    "Tio": _unit("tébioctet"),
    "kbit/s": _unit("kilobit par seconde", other="kilobits par seconde", many="de kilobits par seconde"),
    "Mbit/s": _unit("mégabit par seconde", other="mégabits par seconde", many="de mégabits par seconde"),
    "Gbit/s": _unit("gigabit par seconde", other="gigabits par seconde", many="de gigabits par seconde"),
    "t": _unit("tonne", "feminine"),
    "µm": _unit("micromètre"),
    "nm": _unit("nanomètre"),
    "µg": _unit("microgramme"),
    "cm²": _unit("centimètre carré", other="centimètres carrés", many="de centimètres carrés"),
    "mm²": _unit("millimètre carré", other="millimètres carrés", many="de millimètres carrés"),
    "cm³": _unit("centimètre cube", other="centimètres cubes", many="de centimètres cubes"),
    "dm": _unit("décimètre"),
    "ms": _unit("milliseconde", "feminine"),
    "W": _unit("watt"),
    "V": _unit("volt"),
    "kV": _unit("kilovolt"),
    "mV": _unit("millivolt"),
}


def _currency(
    symbols: list[str],
    one: str,
    gender: str,
    minor: str,
    minor_gender: str = "masculine",
    other: str | None = None,
    minor_other: str | None = None,
) -> dict:
    major = _unit(one, gender, other)
    cents = _unit(minor, minor_gender, minor_other)
    return {"symbols": symbols, **major, "minor": cents}


EURO = _currency(["€", "EUR"], "euro", "masculine", "centime")
DOLLAR = _currency(["$", "US$", "$US", "$ US", "$\u00a0US", "USD"], "dollar", "masculine", "cent")
POUND = _currency(["£", "GBP"], "livre", "feminine", "penny", "masculine", minor_other="pence")
FRANC = _currency(["CHF"], "franc suisse", "masculine", "centime", other="francs suisses")
CANADIAN = _currency(
    ["CA$", "C$", "$CA", "$ CA", "$\u00a0CA", "CAD"], "dollar canadien", "masculine", "cent", other="dollars canadiens"
)
CANADIAN["many"] = "de dollars canadiens"
FRANC["many"] = "de francs suisses"
POUND["minor"]["many"] = "de pence"

COLORS = {
    "000000": "noir",
    "000080": "bleu marine",
    "0000ff": "bleu",
    "008000": "vert",
    "008080": "sarcelle",
    "00ff00": "citron vert",
    "00ffff": "cyan",
    "800000": "bordeaux",
    "800080": "violet",
    "808000": "olive",
    "808080": "gris",
    "c0c0c0": "argent",
    "ff0000": "rouge",
    "ff00ff": "magenta",
    "ffa500": "orange",
    "ffc0cb": "rose",
    "ffff00": "jaune",
    "ffffff": "blanc",
}
"""The sixteen HTML 4 colour names and orange and pink, from the ovos-color-parser palette `fr-FR/dot-net-colors.json`
. The rest of that palette is machine-translated and is left out. Any other colour reads as
its digits."""

DATA = freeze(
    {
        "fraction_denominators": ("1000",),
        "number_marks": {"Latn": [{"decimal": ".,", "group": GROUP}, {"decimal": ",.", "group": GROUP}]},
        "number_gaps": ["", " ", "\u00a0", "\u202f"],
        "elision_marks": ["'", "\u2019"],
        "defaults": {
            "date_order": "DMY",
            "clock": "24h",
            "minute_style": "number",
            "decimal_mark": ",",
            "scale": "long",
            "register": "formal",
        },
        "sign_words": {"-": "moins", "+": "plus"},
        "decimal_word": "virgule",
        "digit_words": ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"],
        "leads": {"#": "numéro", "-": ""},
        "idioms": {
            "24h/24": "vingt-quatre heures sur vingt-quatre",
            "24 h/24": "vingt-quatre heures sur vingt-quatre",
            "7j/7": "sept jours sur sept",
            "7 j/7": "sept jours sur sept",
            "50/50": "cinquante-cinquante",
        },
        "range_word": "à",
        "range_marks": ["-", "–"],
        "ordinal_nouns": ["page", "l'an", "les années", "des années", "aux années", "numéro", "paragraphe", "article"],
        "scale_nouns": [
            "million", "millions", "milliard", "milliards", "billion", "billions", "billiard", "billiards",
            "trillion", "trillions",
        ],
        "no_de_words": NO_DE_WORDS,
        "no_de_adjectives": NO_DE_ADJECTIVES,
        "no_de_participles": NO_DE_PARTICIPLES,
        "inverted_pronouns": INVERTED_PRONOUNS,
        "imperative_pronouns": IMPERATIVE_PRONOUNS,
        "elided_pronouns": ELIDED_PRONOUNS,
        "invariable_plurals": INVARIABLE_PLURALS,
        "aspirated_h": ASPIRATED_H,
        "mute_h": MUTE_H,
        "eliding_h": ["haïti"],
        "eliding_y": ["yeux", "yeuse"],
        "no_elision": ["oui", "ouistiti"],
        "clock_marks": [{"mark": ":", "seconds": True, "needs": "evidence"}],
        "dimension_marks": ["x", "×"],
        "dimension_word": "par",
        "time_words": ["à", "vers", "dès", "avant", "après", "jusqu'à", "depuis"],
        "day_periods": {"am": ["am", "a.m.", "AM", "A.M."], "pm": ["pm", "p.m.", "PM", "P.M."]},
        "day_part_words": {"morning": "du matin", "afternoon": "de l'après-midi", "evening": "du soir"},
        "minute_phrases": {"15": "et quart", "30": "et demie", "45": "moins le quart"},
        "months": MONTHS,
        "scales": {
            "k": "mille",
            "K": "mille",
            "M": "million",
            "Md": "milliard",
            "Mds": "milliard",
            "Mrd": "milliard",
            "Mio": "million",
            "Mia": "milliard",
            "million": "million",
            "millions": "million",
            "milliard": "milliard",
            "milliards": "milliard",
        },
        "currencies": {"EUR": EURO, "USD": DOLLAR, "GBP": POUND, "CHF": FRANC, "CAD": CANADIAN},
        "percent": {"signs": ["%", "‰", "%o"], "position": "after", "word": "pour cent", "permille_word": "pour mille"},
        "units": UNITS,
        "symbols": {"%": "percent", "‰": "percent", "$": "money", "£": "money", "€": "money"},
        "operators": {"+": "plus", "−": "moins", "×": "fois", "÷": "divisé par", "=": "égale"},
        "color_words": ["couleur", "couleurs", "teinte", "teintes", "coloris", "rgb", "hexadécimal"],
        "colors": COLORS,
        "year_words": [
            "en",
            "depuis",
            "jusqu'en",
            "dès",
            "vers",
            "année",
            "années",
            "avant",
            "après",
            "millésime",
            "circa",
        ],
        "year_links": ["et", "ou", "à"],
        "function_words": [
            "le",
            "la",
            "les",
            "l'",
            "un",
            "une",
            "des",
            "de",
            "du",
            "et",
            "ou",
            "mais",
            "donc",
            "or",
            "ni",
            "car",
            "à",
            "au",
            "aux",
            "en",
            "dans",
            "sur",
            "sous",
            "pour",
            "par",
            "avec",
            "sans",
            "chez",
            "entre",
            "vers",
            "il",
            "elle",
            "on",
            "nous",
            "vous",
            "ils",
            "elles",
            "je",
            "tu",
            "ce",
            "cet",
            "cette",
            "ces",
            "est",
            "était",
            "a",
            "ont",
            "avait",
            "fut",
            "sont",
            "que",
            "qui",
            "où",
            "quand",
            "puis",
            "alors",
            "ne",
            "pas",
            "se",
            "sa",
            "son",
            "ses",
            "leur",
            "leurs",
            "mon",
            "ma",
            "mes",
            "dont",
            "si",
            "lors",
            "pendant",
            "depuis",
            "avant",
            "après",
            "jusqu'à",
            "déjà",
            "encore",
            "aujourd'hui",
            "maintenant",
            "tout",
            "tous",
            "toute",
            "toutes",
        ],
        "phone_words": [
            "tel",
            "tél",
            "téléphone",
            "telephone",
            "appelez",
            "appeler",
            "appel",
            "composez",
            "composer",
            "joindre",
            "portable",
            "mobile",
            "fax",
            "sms",
            "whatsapp",
        ],
        "short_codes": ["15", "17", "18", "112", "114", "115", "119", "191", "196", "3615", "3919", "3939"],
        "list_links": ["et", "ou"],
        "phone_shapes": [],
        "phone_unit_shapes": [],
        "phone_kept_shapes": [],
        "no_phone_shapes": [],
        "phone_reading": "pairs",
        "roman_headings": [
            "chapitre",
            "acte",
            "tome",
            "livre",
            "partie",
            "article",
            "titre",
            "volume",
            "section",
            "scène",
            "séance",
            "classe",
            "niveau",
            "phase",
            "annexe",
            "planche",
            "cahier",
        ],
        "roman_names": [
            "Alexandre",
            "Alexis",
            "Alphonse",
            "Amédée",
            "Anne",
            "Baudouin",
            "Benoît",
            "Boniface",
            "Boris",
            "Casimir",
            "Catherine",
            "Charles",
            "Childéric",
            "Christian",
            "Clément",
            "Clovis",
            "Constantin",
            "Dagobert",
            "Édouard",
            "Élisabeth",
            "Étienne",
            "Ferdinand",
            "François",
            "Frédéric",
            "Georges",
            "Grégoire",
            "Guillaume",
            "Gustave",
            "Henri",
            "Hugues",
            "Innocent",
            "Isabelle",
            "Jacques",
            "Jean",
            "Jean-Paul",
            "Joseph",
            "Jules",
            "Léon",
            "Léopold",
            "Lothaire",
            "Louis",
            "Louis-Philippe",
            "Marguerite",
            "Marie",
            "Mathias",
            "Maximilien",
            "Michel",
            "Napoléon",
            "Nicolas",
            "Olaf",
            "Otton",
            "Paul",
            "Pépin",
            "Philippe",
            "Pie",
            "Pierre",
            "Ramsès",
            "Richard",
            "Robert",
            "Rodolphe",
            "Sigismond",
            "Sixte",
            "Théodore",
            "Urbain",
            "Victor",
            "Victoria",
            "Vladimir",
        ],
        "titles": {
            "M.": "Monsieur",
            "MM.": "Messieurs",
            "Mme": "Madame",
            "Mmes": "Mesdames",
            "Mlle": "Mademoiselle",
            "Mlles": "Mesdemoiselles",
            "Dr": "Docteur",
            "Dr.": "Docteur",
            "Pr": "Professeur",
            "Pr.": "Professeur",
            "Mgr": "Monseigneur",
            "St": "Saint",
            "St.": "Saint",
            "Ste": "Sainte",
            "Ste.": "Sainte",
            "Me": "Maître",
            "M\u1d49": "Maître",
            "bd": "boulevard",
            "boul.": "boulevard",
        },
        "name_particles": ["le", "la", "de", "du", "des", "d'", "l'"],
        "abbreviations": {
            "etc.": "et cetera", "c.-à-d.": "c'est-à-dire", "p. ex.": "par exemple", "&": "et", "cf.": "confer",
            "env.": "environ", "av. J.-C.": "avant Jésus-Christ", "apr. J.-C.": "après Jésus-Christ",
            "ap. J.-C.": "après Jésus-Christ",
        },
        "rate_words": {
            "mois": "mois", "an": "an", "année": "année", "jour": "jour", "j": "jour", "semaine": "semaine",
            "heure": "heure", "h": "heure", "nuit": "nuit", "personne": "personne",
        },
        "sentence_final": ["etc.", "env.", "av. J.-C.", "apr. J.-C.", "ap. J.-C."],
        "pronoun_titles": ["Me"],
        "street_titles": ["bd"],
        "title_exceptions": ["Me Too"],
        "number_abbreviations": {
            "n°": "numéro",
            "N°": "numéro",
            "nº": "numéro",
            "Nº": "numéro",
            "§": "paragraphe",
            "§§": "paragraphes",
            "p.": "page",
            "pp.": "pages",
            "art.": "article",
            "Art.": "Article",
            "chap.": "chapitre",
            "vol.": "volume",
        },
        "ordinal_marks": {
            "masculine": ["er", "\u1d49\u02b3"],
            "feminine": ["re", "ère", "ere", "\u02b3\u1d49"],
            "masculine_plural": ["ers", "\u1d49\u02b3\u02e2"],
            "feminine_plural": ["res", "ères", "eres", "\u02b3\u1d49\u02e2"],
            "other": ["e", "ème", "eme", "\u1d49", "\u1d49\u1d50\u1d49"],
            "other_plural": ["es", "èmes", "emes", "\u1d49\u02e2", "\u1d49\u1d50\u1d49\u02e2"],
            "second": ["nd", "d", "\u207f\u1d48", "\u1d48"],
            "second_feminine": ["nde", "de", "\u207f\u1d48\u1d49", "\u1d48\u1d49"],
            "second_plural": ["nds", "ds", "\u207f\u1d48\u02e2", "\u1d48\u02e2"],
            "second_feminine_plural": ["ndes", "des", "\u207f\u1d48\u1d49\u02e2", "\u1d48\u1d49\u02e2"],
        },
        "feminine_nouns": FEMININE_NOUNS,
        "preposed_adjectives": PREPOSED_ADJECTIVES,
        "adjective_links": ["et", "ou"],
        "adjective_adverbs": ["très", "si", "plus", "bien", "assez", "trop"],
        "no_noun_words": ["contre", "ensemble", "voici", "voilà"],
        "determiners": DETERMINERS,
        "era_abbreviations": ["av. J.-C.", "apr. J.-C.", "ap. J.-C."],
        "label_links": [", ", " et ", " ou ", " à ", "-", "–"],
        "mixed_word": "et",
        "mixed_half": {"feminine": "demie", "other": "demi"},
        "patterns": {
            "date_day_month": _DAY + _SPACE + _MONTH + "(?:" + _SPACE + _YEAR + ")?",
            "date_month_year": _MONTH + _SPACE + _YEAR,
            "clock_hour": "([0-9][0-9]?)" + _SPACE + "?[hH](?:" + _SPACE + "?([0-9][0-9]))?",
            "expression": "[-−]?[0-9]+(?: ?[+−×÷=] ?[-−]?[0-9]+)+",
        },
    }
)

VARIETIES = (
    Variety("fr-FR"),
    Variety(
        "fr-CA",
        freeze(
            {
                "phone_reading": "digits",
                "phone_shapes": [
                    "[(][2-9][0-9]{2}[)] [2-9][0-9]{2}[- ][0-9]{4}",
                    "[2-9][0-9]{2}-[2-9][0-9]{2}-[0-9]{4}",
                    "[2-9][0-9]{2} [2-9][0-9]{2}-[0-9]{4}",
                ],
                "currencies": {
                    "USD": {
                        "symbols": ["US$", "$US", "$ US", "$\u00a0US", "USD"],
                        "one": "dollar américain",
                        "other": "dollars américains",
                        "many": "de dollars américains",
                    },
                    "CAD": {
                        **{k: v for k, v in DOLLAR.items() if k != "symbols"},
                        "symbols": ["$", "CA$", "C$", "$CA", "$ CA", "$\u00a0CA", "CAD"],
                        "colloquial": {
                            "one": "piastre",
                            "other": "piastres",
                            "many": "de piastres",
                            "gender": "feminine",
                            "minor": {"one": "cenne", "other": "cennes", "many": "de cennes", "gender": "feminine"},
                        },
                    },
                },
            }
        ),
    ),
    Variety("fr-CH", freeze({"currencies": {"CHF": {"symbols": ["CHF", "Fr.", "fr."]}}})),
)


PLANS = FrozenMap(
    {
        **PHONE_PLANS,
        "BE": FrozenMap({"country_code": "32", "trunk": "0", "lengths": (8, 9)}),
        "CA": FrozenMap({"country_code": "1", "trunk": "1", "lengths": (10,)}),
        "CH": FrozenMap({"country_code": "41", "trunk": "0", "lengths": (9,)}),
    }
)
"""The numbering plans of the core and those of Belgium, Canada and Switzerland, where French is an official
language: the country calling code of ITU-T E.164, the trunk prefix and the lengths of the national significant
number."""


def _clock_edge(text: str, start: int, end: int) -> bool:
    """Whether no digit, and no mark of a number before a digit, continues text[start:end]. A dash does not
    continue it, so `9h-17h` is a range of two times. A slash after it does not either: the claim waits on the
    digit that the slash joins, so `4h/2` stays as written and `9h/17h` reads both times."""
    before = start == 0 or not (
        is_digit(text[start - 1]) or (text[start - 1] in "/:.," and start > 1 and is_digit(text[start - 2]))
    )
    after = end == len(text) or not (
        is_digit(text[end]) or (text[end] in ":.," and end + 1 < len(text) and is_digit(text[end + 1]))
    )
    return before and after


def _invariable(words: str) -> str:
    """The words of a numeral that stands for an ordinal: "cent" and "vingt" take no "s" (Académie française,
    "Nombres": "page deux cent ; page quatre-vingt ; l'an mille neuf cent"). "Millions" and "milliards" are nouns
    and keep theirs."""
    return " ".join(word[:-1] if word in ("cents", "quatre-vingts") else word for word in words.split(" "))


class FrenchSpeller:
    """numtag cardinals and ordinals, and decimals that read the digits after the comma as one number when there are
    one or two of them."""

    def __init__(self):
        self.numtag = NumtagSpeller({MASCULINE: "masculine", FEMININE: "feminine"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self.numtag.cardinal(digits, features, request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self.numtag.ordinal(digits, Features(gender=features.gender or MASCULINE), request)

    def year(self, digits: str, features: Features, request: Request) -> str:
        """A year reads as a cardinal in which "cent" and "vingt" stay singular at its end, as numerals that
        stand for an ordinal do: "mille neuf cent", "mille neuf cent quatre-vingt", "deux mille quatre-vingt"
        (Académie française, "Nombres")."""
        return _invariable(self.cardinal(digits, Features(), request))

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """ "trois virgule cinq", "trois virgule quatorze", "trois virgule zéro cinq". A fraction of three digits or
        more reads digit by digit, as in "trois virgule un quatre un"."""
        whole = self.cardinal(integer or "0", Features(), request)
        if len(fraction) <= 2:
            rest = fraction.lstrip("0")
            zeros = ["zéro"] * (len(fraction) - len(rest))
            tail = " ".join([*zeros, *([self.cardinal(rest, Features(), request)] if rest else [])])
        else:
            tail = spell_digits(fraction, request)
        return f"{whole} {request.data['decimal_word']} {tail}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """ "un demi", "deux tiers", "trois quarts", "cinq huitièmes", "un centième". The other fraction names are
        masculine nouns, but "demi" before a noun agrees through its article only: "une demi-heure" (Wiktionnaire,
        "demi"), so a half takes the gender of `features`."""
        bottom = denominator.lstrip("0")
        top = self.cardinal(numerator, features if bottom == "2" else Features(), request)
        plural = numerator.lstrip("0") != "1"
        names = {"2": ("demi", "demis"), "3": ("tiers", "tiers"), "4": ("quart", "quarts")}.get(bottom)
        if names is not None:
            return f"{top} {names[plural]}"
        return f"{top} {self.ordinal(denominator, Features(), request)}{'s' if plural else ''}"


SPELLER = FrenchSpeller()


@lru_cache(maxsize=8)
def _feminine(nouns: tuple[str, ...]) -> frozenset[str]:
    return frozenset(nouns)


@lru_cache(maxsize=1)
def noun_genders() -> dict[str, str]:
    """The gender of each noun of `data/wiktionary/fr_noun_genders.json`, by its singular as the list writes it:
    "masculine", "feminine", or "both" for a word of both categories or of several genders, as "élève"."""
    path = files("text2spoken") / "data" / "wiktionary" / "fr_noun_genders.json"
    table = json.loads(path.read_text(encoding="utf-8"))
    return {**dict.fromkeys(table["masculine"], "masculine"), **dict.fromkeys(table["feminine"], "feminine"),
            **dict.fromkeys(table["both"], "both")}


def _part_singulars(word: str) -> Iterator[str]:
    """`_singulars` of a word, and for a word with a hyphen, the word whose parts each lose a final "s" or "x", as
    "grands-mères" gives "grand-mère" and "eaux-de-vie" "eau-de-vie". Office québécois de la langue française,
    Vitrine linguistique, "Pluriel des noms composés": "Les deux éléments prennent la marque du pluriel lorsqu'il
    s'agit de deux noms dont le second qualifie le premier, d'un nom et d'un adjectif ou d'un adjectif et d'un nom",
    as "des coffres-forts", "des basses-cours", "des ronds-points"."""
    yield from _singulars(word)
    if "-" in word:
        yield "-".join(part[:-1] if len(part) > 2 and part.endswith(("s", "x")) else part for part in word.split("-"))


def _singulars(word: str) -> Iterator[str]:
    """The word, then the singulars that its plural can have: less a final "s" or "x", and "-al" or "-ail" for "-aux".
    A noun takes "s" in the plural, as the OQLF page on the plural of foreign words gives the general rule (see
    `_counted`), and the Office québécois de la langue française, Vitrine linguistique, gives the rest: "La plupart des
    noms qui se terminent en -au et en -eu ainsi que tous les noms qui se terminent en -eau prennent un x au pluriel"
    ("Pluriel des noms en -au, -eau et -eu"), "La plupart des noms qui se terminent en -al forment leur pluriel en
    -aux" ("Pluriel des noms en -al"), and "bail, corail, émail, fermail, gemmail, soupirail, travail, vantail, ventail
    et vitrail" form it "en -aux plutôt qu'en -ails" ("Pluriel des noms en -ail")."""
    yield word
    if word.endswith("aux"):
        yield word[:-3] + "al"
        yield word[:-3] + "ail"
    if word.endswith(("s", "x")):
        yield word[:-1]


def _noun_gender(word: str, data: FrozenMap) -> str | None:
    """The gender of a noun of `feminine_nouns` or of the noun list, in lowercase, and only then as the text writes
    it, because the list also holds proper nouns, such as "Année" and "Ami", and in the singular or the plural."""
    if word.lower() in _feminine(data["feminine_nouns"]):
        return "feminine"
    genders = noun_genders()
    for form in dict.fromkeys((word.lower(), word)):
        for singular in _part_singulars(form):
            if singular in genders:
                return genders[singular]
    return None


@lru_cache(maxsize=8)
def _stops(function_words: tuple[str, ...], no_de_words: tuple[str, ...], no_noun_words: tuple[str, ...]):
    return frozenset((*function_words, *no_de_words, *no_noun_words))


def _noun_after(words: Sequence[str], data: FrozenMap) -> GrammaticalGender | None:
    """The gender that the words after a number give it. "Des", or "de" and a plural determiner, starts a partitive,
    "un des", "une de ses", in which "une, forme féminine du pronom numéral un" agrees with the noun after it:
    "une des sculptrices", and "le féminin une ne peut être associé à un nom masculin" (Office québécois de la
    langue française, Banque de dépannage linguistique, "Accord du verbe avec un des… qui, un de ceux qui…").

    An adjective of `preposed_adjectives` that marks a gender gives it, and one that marks none, or a link of
    `adjective_links` between two of them, passes to the next word, as in "une grande et belle maison" and "une
    jeune fille". An adverb of `adjective_adverbs` before such an adjective passes too: "une très belle maison". Then
    a noun of the list gives its gender, and a noun of both genders gives none. A function word of `function_words`,
    `no_de_words` or `no_noun_words` is no noun, although the list holds "de", "une" and "plus" as nouns, so it gives
    none either: "un de plus", "un des meilleurs films". The French Wiktionary gives the words of `no_noun_words`
    as no noun: "contre" a preposition, "ensemble" an adverb, "voici" and "voilà" a verb and a preposition; and the
    words of `adjective_adverbs` as adverbs ("Adverbes en français")."""
    adjectives = data["preposed_adjectives"]
    stops = _stops(tuple(data["function_words"]), tuple(data["no_de_words"]), tuple(data["no_noun_words"]))
    lowers = [word.lower() for word in words]
    start = 0
    if lowers[:1] == ["des"]:
        start = 1
    elif lowers[:1] == ["de"] and len(lowers) > 1 and data["determiners"].get(lowers[1]) == "plural":
        start = 2
    for index in range(start, len(words)):
        lower = lowers[index]
        if lower in adjectives:
            if adjectives[lower] != "both":
                return GrammaticalGender(adjectives[lower])
            continue
        if index > start and lower in data["adjective_links"] and lowers[index - 1] in adjectives:
            continue
        if lower in data["adjective_adverbs"] and index + 1 < len(words) and lowers[index + 1] in adjectives:
            continue
        if lower in stops:
            return None
        gender = _noun_gender(words[index], data)
        return GrammaticalGender(gender) if gender in ("masculine", "feminine") else None
    return None


def _gender(context: SpanContext, noun: bool = True) -> GrammaticalGender:
    """The agreement order: the hint, the noun after the number, `default_gender`, then the file."""
    if context.hint is not None and context.hint.gender is not None:
        return context.hint.gender
    if noun and (found := _noun_after(context.after, context.request.data)) is not None:
        return found
    return context.request.params.default_gender.get(LANGUAGE.code) or MASCULINE


def _cardinal(digits: str, request: Request, gender: GrammaticalGender | None = None) -> str:
    return SPELLER.cardinal(digits, Features(gender=gender), request)


def _amount(amount: FrozenMap, request: Request, gender: GrammaticalGender | None = None) -> str:
    return amount_words(amount, request, Features(gender=gender))


def _name(record: FrozenMap, request: Request, written: str) -> str:
    """The unit or currency name for a written number: one for 0 and 1, "de ..." for a million."""
    return record.get(plural_category(request, written), record["other"])


_LABELLED = "fr_labelled"
"""The key of `Request.memo` that holds the starts of the cardinal and range spans that a label of `ordinal_nouns`
governs, as `FrenchCardinal` and `FrenchRange` find them."""


def _labelled(text: str, start: int, data: FrozenMap, nouns: Sequence[str]) -> bool:
    """Whether one of `nouns`, or its abbreviation in `number_abbreviations`, ends right before text[start:] with
    only spaces between, as in "page 80", "p. 80" and "l'an 800". A comma, a full stop or a word between them ends
    the label, so "Depuis un an, 21 personnes" holds none."""
    end = start
    while end and text[end - 1] in GROUP_SPACES:
        end -= 1
    for label in (*nouns, *(key for key, noun in data["number_abbreviations"].items() if noun in nouns)):
        begin = end - len(label)
        if begin >= 0 and text[begin:end].lower().replace("\u2019", "'") == label.lower() and not (
            begin and is_word_char(text[begin - 1])
        ):
            return True
    return False


def _word_before(text: str, start: int) -> tuple[str, int]:
    """The word that ends before text[start:] with only spaces between, with an elided article whole, as "l'", and
    its start; or "" when no such word is there."""
    end = start
    while end and text[end - 1] in GROUP_SPACES:
        end -= 1
    if end == start:
        return "", start
    begin = end
    while begin and (is_letter(text[begin - 1]) or text[begin - 1] in "'\u2019"):
        begin -= 1
    return text[begin:end].replace("\u2019", "'"), begin


def _named(text: str, span: Span, data: FrozenMap) -> bool:
    """Whether the number names a numeral or a numéro: "Les numéraux employés comme noms sont précédés d'un
    déterminant. Ils expriment alors soit le chiffre, soit le numéro auquel ils correspondent", and "Employés comme
    noms, ces mots sont toujours invariables" (Office québécois de la langue française, Vitrine linguistique, "Les
    numéraux employés comme noms"). So a number right after a singular determiner of `determiners`, as in "le 21",
    names a number, as "le quatre-vingt de la rue des Érables (le numéro 80)" does ("Pluriel de vingt, de cent et de
    mille"). So does a number after a determiner and a word, as in "le joueur 1" and "la chambre 80", unless a
    plural word or an adjective of `preposed_adjectives` follows it, which belongs to the noun that the number
    counts: "le film 21 fois", "ce film 1 seule fois". A plural determiner counts: "les 21 pommes"."""
    determiners = data["determiners"]
    word, begin = _word_before(text, span.start)
    lower = word.lower()
    if determiners.get(lower, "plural") != "plural":
        return True
    if not word or lower in determiners or lower in data["function_words"] or not word.isalpha():
        return False
    if determiners.get(_word_before(text, begin)[0].lower()) is None:
        return False
    word = _word_after(text, span.end).lower()
    if word in data["preposed_adjectives"]:
        return False
    return not word or not word.endswith(("s", "x", "z")) or word in data["function_words"]


def _word_after(text: str, end: int) -> str:
    """The word, with its hyphens, that follows text[:end] after spaces, or ""."""
    after = text[end:].lstrip(GROUP_SPACES)
    stop = 0
    while stop < len(after) and (is_letter(after[stop]) or after[stop] == "-"):
        stop += 1
    return after[:stop]


def _counts(text: str, end: int, data: FrozenMap) -> bool:
    """Whether the number that ends at `end` counts the word after it: a noun of the noun list that is no function
    word, or an adjective of `preposed_adjectives`, as in "page 80 et 21 pages"."""
    word = _word_after(text, end)
    lower = word.lower()
    if not word or lower in _stops(tuple(data["function_words"]), tuple(data["no_de_words"]),
                                   tuple(data["no_noun_words"])):
        return False
    return lower in data["preposed_adjectives"] or _noun_gender(word, data) is not None


def _era(text: str, end: int, data: FrozenMap) -> bool:
    """Whether an era abbreviation of `era_abbreviations` follows the number, which is then a year: the Wiktionnaire
    gives "av. J.-C." and "apr. J.-C." as "Utilisé pour nommer les années, les siècles et les millénaires", and a
    year reads as `FrenchSpeller.year` does: "en quatre cent quatre-vingt avant Jésus-Christ"."""
    rest = text[end:].lstrip(GROUP_SPACES)
    return rest != text[end:] and rest.startswith(tuple(data["era_abbreviations"]))


_COUNTED = "fr_counted"
"""The key of `Request.memo` that maps the start of a cardinal or decimal span that a noun follows to the text
between the number and the noun, as `_counted` finds it, and to whether "de" elides before the noun."""

_ELIDING = frozenset("aeiouàâäéèêëîïôöùûüœæ")


def _aspirated_start(word: str) -> str:
    """The start that a word of `aspirated_h` gives its family: the word less a final "e", "er" or "ir" when four
    letters remain, so "hausse" gives "hauss" and "harceler" gives "harcel", and "huer" stays whole."""
    for ending in ("er", "ir", "e"):
        if word.endswith(ending) and len(word) - len(ending) >= 4:
            return word[: -len(ending)]
    return word


def _elides(word: str, data: FrozenMap) -> bool:
    """Whether "de" elides before `word`. A word that starts as a word of `eliding_h` does elides. Any other h elides
    unless the word is capitalised and not all in capitals, or starts as a word of `aspirated_h` does, and not as a
    word of `mute_h`. A y elides before a consonant, and before a vowel only in a word of `eliding_y`. The words of
    `no_elision` and their plurals take none. Any other vowel elides."""
    lower = word.lower()
    if lower.startswith(tuple(data["eliding_h"])):
        return True
    if lower[0] == "h":
        if word[0] == "H" and not word.isupper():
            return False
        aspirated = lower.startswith(tuple(_aspirated_start(h) for h in data["aspirated_h"]))
        return not aspirated or lower.startswith(tuple(data["mute_h"]))
    if lower[0] == "y":
        return lower[1] not in _ELIDING or lower.startswith(tuple(data["eliding_y"]))
    if any(lower in (w, w + "s") for w in data["no_elision"]):
        return False
    return lower[0] in _ELIDING


def _counted(text: str, end: int, data: FrozenMap) -> tuple[str, bool] | None:
    """The text between a number that ends at `end` and the noun it counts, with a written noun of `scale_nouns` in
    it if the text gives one, and whether "de" elides before the noun. None when spaces and a word do not follow, or
    when the word has one letter, is in `no_de_words`, `no_de_adjectives` or `no_de_participles`, is a verb with an
    inverted subject or an imperative with an object pronoun, or does not end as a plural noun does and is not in
    `invariable_plurals`. A word with a hyphen counts as one word, which is plural when any part is: "sans-abri",
    "années-lumière"."""
    position = end
    while position < len(text) and text[position] in GROUP_SPACES:
        position += 1
    if position == end:
        return None
    for noun in data["scale_nouns"]:
        stop = position + len(noun)
        if text.startswith(noun, position) and stop < len(text) and text[stop] in GROUP_SPACES:
            position = stop
            while position < len(text) and text[position] in GROUP_SPACES:
                position += 1
            break
    stop = position
    while stop < len(text) and (
        is_letter(text[stop]) or text[stop] == "-" and stop + 1 < len(text) and is_letter(text[stop + 1])
    ):
        stop += 1
    word = text[position:stop].lower()
    parts = word.split("-")
    elided = stop < len(text) and text[stop] in data["elision_marks"]
    verb = len(parts) > 1 and (
        any(part in data["inverted_pronouns"] for part in parts[1:])
        or parts[-1] in data["imperative_pronouns"]
        or elided and parts[-1] in data["elided_pronouns"]
    )
    if (
        len(word) < 2
        or word in data["no_de_words"]
        or word in data["no_de_adjectives"]
        or word in data["no_de_participles"]
        or verb and word not in data["invariable_plurals"]
        or not (any(part.endswith(("s", "x", "z")) for part in parts) or word in data["invariable_plurals"])
    ):
        return None
    return text[end:position], _elides(text[position:stop], data)


def _with_de(words: str, span: Span, request: Request) -> str:
    """The words of a number with "de" or "d'" before the noun that `_counted` found after it."""
    found = request.memo.get(_COUNTED, {}).get(span.start)
    if found is None:
        return words
    between, elided = found
    return words + between.rstrip(GROUP_SPACES) + (" d'" if elided else " de ")


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal with the gender of the agreement order. Digits with a leading zero, which only a lead admits,
    read one by one. A number that labels a page or a year stands for an ordinal, so it is masculine and "cent"
    and "vingt" take no "s": "page quatre-vingt"."""
    fields, request = span.fields, context.request
    digits = fields["digits"]
    if len(digits) > 1 and digits[0] == "0":
        words = spell_digits(digits, request)
    elif span.start in request.memo.get(_LABELLED, ()):
        words = _invariable(_cardinal(digits, request))
    else:
        words = _with_de(_cardinal(digits, request, _gender(context)), span, request)
    words = signed(words, fields["sign"], request)
    if fields["lead"]:
        lead = request.data["leads"][fields["lead"]]
        words = f"{lead} {words}" if lead else f" {words}"
    return words


def speak_fraction(span: Span, context: SpanContext) -> str:
    """A fraction; a half before a feminine noun says "une demi", as in "une demi heure". A mixed number reads
    through `speak_mixed_half`."""
    if span.fields["whole"]:
        return speak_mixed_half(span, context)
    fields, features = span.fields, Features(gender=_gender(context))
    words = SPELLER.fraction(fields["numerator"], fields["denominator"], features, context.request)
    return signed(words, fields["sign"], context.request)


def speak_range(span: Span, context: SpanContext) -> str:
    """A range. After a label of `ordinal_nouns` both ends read as `speak_cardinal` reads a labelled number. A
    range whose high end is a round million takes "de" before its noun, as a cardinal does."""
    request = context.request
    if span.start in request.memo.get(_LABELLED, ()):
        low, high = (_invariable(_cardinal(span.fields[end], request)) for end in ("low", "high"))
        return f"{low} {request.data['range_word']} {high}"
    gender = _gender(context)
    low, high = (_cardinal(span.fields[end], request, gender) for end in ("low", "high"))
    return _with_de(f"{low} {request.data['range_word']} {high}", span, request)


def _ordinal_words(digits: str, marker: str, request: Request) -> str:
    """ "1er" is "premier", "1re" and "1ère" "première", "2e" "deuxième", "2es" "deuxièmes", "2nd" "second"."""
    marks = request.data["ordinal_marks"]
    kind = next(key for key, spellings in marks.items() if marker in spellings)
    plural = kind.endswith("plural")
    if kind.startswith("second"):
        return "second" + ("e" if "feminine" in kind else "") + ("s" if plural else "")
    words = SPELLER.ordinal(digits, Features(gender=FEMININE if kind.startswith("feminine") else MASCULINE), request)
    return words + ("s" if plural else "")


def speak_ordinal(span: Span, context: SpanContext) -> str:
    return _ordinal_words(span.fields["digits"], span.fields["marker"], context.request)


def speak_date(span: Span, context: SpanContext) -> str:
    """ "10 novembre 2026" and "10/11/2026" read "dix novembre deux mille vingt-six", and the first of a month
    reads "premier"."""
    request, fields = context.request, span.fields
    month = request.data["months"][fields["month"] - 1]
    words = []
    if fields["day"] is not None:
        words.append("premier" if fields["day"] == 1 else _cardinal(str(fields["day"]), request))
    words.append(month)
    if fields["year"] is not None:
        words.append(SPELLER.year(str(fields["year"]), Features(), request))
    return " ".join(words)


def _hour_words(hour: int, request: Request) -> str:
    return f"{_cardinal(str(hour), request, FEMININE)} {'heure' if hour < 2 else 'heures'}"


def _day_part(hour: int, request: Request) -> str:
    parts = request.data["day_part_words"]
    return parts["morning"] if hour < 12 else parts["afternoon"] if hour < 18 else parts["evening"]


def speak_time(span: Span, context: SpanContext) -> str:
    """ "14 h 30" is "quatorze heures trente", and "7 h 05" "sept heures cinq". Hour 12 reads "midi" and hour 0 or 24
    reads "minuit" when a time word or "est" comes before it, as in `à 12 h`, on the 12-hour clock, after a written
    `am` or `pm` (which Tunisia and Algeria write, CLDR `fr_TN`) and in the phrase style, so `12 h` stays "douze
    heures" after "pendant". The phrase style, which `register="colloquial"` also selects, says "et quart", "et
    demie" and "moins le quart". The 12-hour clock adds "du matin", "de l'après-midi" or "du soir" (Académie
    française, "L'heure")."""
    request, params, fields = context.request, context.request.params, span.fields
    hour, minute, second = fields["hour"], fields["minute"], fields["second"]
    if fields["period"] is not None:
        hour = hour % 12 + (12 if fields["period"] == "pm" else 0)
    twelve = params.clock == "12h" or fields["period"] is not None
    phrase = params.minute_style == "phrase" or params.register == "colloquial"
    quarter = phrase and second is None and minute in (15, 30, 45)
    # "est" names the hour, as in "il est midi", but it also comes before a ratio, so it is no time word for the
    # colon form (design section 4.2).
    cue = bool(context.before) and context.before[-1].lower() in (*request.data["time_words"], "est")
    named_ok = cue or twelve or quarter

    def noon_or_midnight(h: int) -> str | None:
        if named_ok and h == 12:
            return "midi"
        return "minuit" if named_ok and h in (0, 24) else None

    def face(h: int) -> str:
        return noon_or_midnight(h) or _hour_words(twelve_hour(h % 24) if twelve else h, request)

    if quarter:
        later = hour + 1 if minute == 45 else hour
        named = noon_or_midnight(later) is not None
        words = face(later) + " " + (" ".join(request.data["minute_phrases"][str(minute)].split()))
        if minute == 30 and named:
            words = face(later) + " et demi"
    else:
        words = face(hour)
        named = noon_or_midnight(hour) is not None
        if second is not None:
            unit = "minute" if minute < 2 else "minutes"
            words += f" {_cardinal(str(minute), request, FEMININE)} {unit}"
        elif minute:
            words += " " + _cardinal(str(minute), request, FEMININE)
    if second is not None:
        words += f" et {_cardinal(str(second), request, FEMININE)} {'seconde' if second < 2 else 'secondes'}"
    if twelve and not named:
        words += " " + _day_part(hour, request)
    return words


def _scaled_money(fields: FrozenMap, amount: FrozenMap, currency: FrozenMap, request: Request) -> str:
    """ "2 M€" is "deux millions d'euros", "1,5 Md$" "un virgule cinq milliard de dollars", "5 k€" "cinq mille euros"
    and "1,5 k€" "mille cinq cents euros". "Mille" takes no "de" and no "un", and a million and a milliard take
    the currency of "many": "un million d'euros"."""
    noun = request.data["scales"][fields["scale"]]
    fraction = amount["fraction"].rstrip("0")
    gender = GrammaticalGender(currency["gender"])
    if noun == "mille":
        total = Decimal(f"{amount['integer'] or '0'}.{fraction or '0'}") * 1000
        if total == total.to_integral_value():
            digits = str(int(total))
            return f"{_cardinal(digits, request, gender)} {_name(currency, request, digits)}"
        return f"{_amount(FrozenMap({**amount, 'fraction': fraction}), request)} mille {currency['other']}"
    amount = FrozenMap({**amount, "fraction": fraction})
    plural = "" if plural_category(request, written_amount(amount)) == "one" else "s"
    return f"{_amount(amount, request)} {noun}{plural} {currency['many']}"


def speak_money(span: Span, context: SpanContext) -> str:
    """ "3,50 €" is "trois euros cinquante", "0,50 €" "cinquante centimes", "0,01 €" "un centime", "12,5 €"
    "douze euros cinquante" and "1 000 000 €" "un million d'euros". A currency with a `colloquial` entry says
    "piastres" in the colloquial register."""
    request, fields = context.request, span.fields
    amount = FrozenMap({**fields["amount"], "sign": ""})
    currency = request.data["currencies"][fields["currency"]]
    if request.params.register == "colloquial" and "colloquial" in currency:
        currency = currency["colloquial"]
    integer, fraction = amount["integer"] or "0", amount["fraction"]
    if len(fraction) == 1:
        fraction += "0"

    def gender(record: FrozenMap) -> GrammaticalGender:
        return GrammaticalGender(record["gender"])

    if fields["scale"]:
        words = _scaled_money(fields, amount, currency, request)
    elif len(fraction) == 2:
        minor_digits = str(int(fraction))
        major = f"{_cardinal(integer, request, gender(currency))} {_name(currency, request, integer)}"
        minor_record = currency["minor"]
        minor = _cardinal(minor_digits, request, gender(minor_record))
        if int(fraction) == 0:
            words = major
        elif int(integer) == 0:
            words = f"{minor} {_name(minor_record, request, minor_digits)}"
        else:
            words = f"{major} {minor}"
    else:
        words = f"{_amount(amount, request, gender(currency))} {_name(currency, request, written_amount(amount))}"
    return signed(words, fields["amount"]["sign"], request)


def speak_measure(span: Span, context: SpanContext) -> str:
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    unit = request.data["units"][span.fields["unit"]]
    link = request.data["range_word" if span.fields["relation"] == "range" else "dimension_word"]
    joined = f" {link} ".join(_amount(a, request, GrammaticalGender(unit["gender"])) for a in amounts)
    return f"{joined} {_name(unit, request, written_amount(amounts[-1]))}"


def speak_percent(span: Span, context: SpanContext) -> str:
    """ "50 %" is "cinquante pour cent", and "5 ‰" or "5 %o" is "cinq pour mille" (`sign_position` is `permille`)."""
    request = context.request
    word = request.data["percent"]["permille_word" if span.fields["sign_position"] == "permille" else "word"]
    return f"{_amount(span.fields['amount'], request)} {word}"


def _pair(pair: str, request: Request) -> str:
    """ "12" is "douze", "06" is "zéro six" and "00" is "zéro zéro"."""
    return f"zéro {spell_digits(pair[1], request)}" if pair[0] == "0" else _cardinal(pair, request)


def _phone_group(group: str, request: Request) -> str:
    """A group of two digits, or four, or any even number, reads in pairs; a group of one or three digits reads digit by
    digit; a longer group of an odd length reads its first digit and then pairs. The `phone_reading` of a variety
    set to `digits` reads every digit."""
    if request.data["phone_reading"] == "digits" or len(group) in (1, 3):
        return spell_digits(group, request)
    head = group[:1] if len(group) % 2 else ""
    pairs = [_pair(group[i:i + 2], request) for i in range(len(head), len(group), 2)]
    return " ".join([*([spell_digits(head, request)] if head else []), *pairs])


def speak_telephone(span: Span, context: SpanContext) -> str:
    """
    "06 12 34 56 78" is "zéro six douze trente-quatre cinquante-six soixante-dix-huit", and "+33 6 12 34 56 78" is "plus
    trente-trois six douze trente-quatre cinquante-six soixante-dix-huit". A short code of three digits reads as one
    number, "112" as "cent douze", as it does after an article ("le 112"), unless the variety reads every digit."""
    request, fields = context.request, span.fields
    groups = fields["groups"]
    if (not fields["country_code"] and len(groups) == 1 and len(groups[0]) == 3
            and groups[0] in request.data["short_codes"] and request.data["phone_reading"] != "digits"):
        return _cardinal(groups[0], request)
    words = [_phone_group(group, request) for group in groups]
    if fields["country_code"]:
        words.insert(0, f"{request.data['sign_words']['+']} {_phone_group(fields['country_code'], request)}")
    return " ".join(words)


def speak_year(span: Span, context: SpanContext) -> str:
    """The short end of a year range, `45` in `1939-45`, reads without the part that the first year says: "mille neuf
    cent
    trente-neuf à quarante-cinq", "deux mille dix à douze"."""
    request = context.request
    digits = span.fields["digits"]
    words = SPELLER.year(digits, Features(), request)
    if span.end - span.start == 2:
        head = SPELLER.year(digits[:2] + "00", Features(), request) + " "
        if words.startswith(head):
            return words[len(head):]
    return words


def _round_million(digits: str) -> bool:
    """Whether the words of `digits` end in a noun of `scale_nouns`: a million or more, with six zeros at the end."""
    return len(digits) > 6 and not digits[-6:].strip("0")


def _count(span: Span, text: str, request: Request, round_million: bool) -> Span:
    """The span, through the text before the noun that `_counted` finds after it, when the number is a round
    million, whose words end in a noun of `scale_nouns`, or when the text writes such a noun after it. The span
    then holds the spaces before the noun, so that "de" elides onto it. The text between goes into `Request.memo`
    under `_COUNTED`."""
    if span.fields["suffix"]:
        return span
    found = _counted(text, span.end, request.data)
    if found is None or not (round_million or found[0].strip(GROUP_SPACES)):
        return span
    request.memo.setdefault(_COUNTED, {})[span.start] = found
    return replace(span, end=span.end + len(found[0]))


@dataclass(frozen=True)
class FrenchCardinal(Cardinal):
    """The shared cardinal recognizer. The start of a span that a label of `ordinal_nouns` governs, with no lead or
    prefix between them, goes into `Request.memo` under `_LABELLED`, and so does a number that `_named` finds, a year
    before an era abbreviation (`_era`), and a number that a link of `label_links` joins to such a number, as in "les
    années 70 et 80" and "les numéros 80 à 90", unless it counts the word after it (`_counts`), as in "page 80 et
    21 pages". A round million or milliard that a noun
    follows reaches to the noun, as `_count` gives it, unless a noun of `number_abbreviations` labels it, as in
    "n° 1 000 000", which names a number and counts nothing."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        labelled_end = None
        for span in sorted(super().find(text, tokens, request), key=lambda found: found.start):
            if span.fields["lead"] or span.fields["prefix"]:
                yield span
                continue
            if (_labelled(text, span.start, data, data["ordinal_nouns"]) or _named(text, span, data)
                    or _era(text, span.end, data)
                    or labelled_end is not None and text[labelled_end:span.start] in data["label_links"]
                    and not _counts(text, span.end, data)):
                request.memo.setdefault(_LABELLED, set()).add(span.start)
                labelled_end = span.end
                yield span
                continue
            if _labelled(text, span.start, request.data, tuple(request.data["number_abbreviations"].values())):
                yield span
                continue
            yield _count(span, text, request, _round_million(span.fields["digits"]))


@dataclass(frozen=True)
class FrenchDecimal(DecimalRecognizer):
    """The shared decimal recognizer. A decimal before a written noun of `scale_nouns` and a noun reaches to the
    noun, as `_count` gives it: "1,5 million habitants"."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in super().find(text, tokens, request):
            yield _count(span, text, request, False)


def speak_french_decimal(span: Span, context: SpanContext) -> str:
    return _with_de(speak_decimal(span, context), span, context.request)


@dataclass(frozen=True)
class FrenchRange(Range):
    """The shared range recognizer. A labelled range goes into `Request.memo` as in `FrenchCardinal`. A range whose
    high end is a round million reaches to the noun after it, as `_count` gives it."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in super().find(text, tokens, request):
            if span.fields["prefix"]:
                yield span
            elif _labelled(text, span.start, request.data, request.data["ordinal_nouns"]):
                request.memo.setdefault(_LABELLED, set()).add(span.start)
                yield span
            else:
                yield _count(span, text, request, _round_million(span.fields["high"]))


@dataclass(frozen=True)
class FrenchMoney(Money):
    """The shared money recognizer, with a scale word between the number and a symbol after it, as in `2 M€`, `5 k€`
    and `3 Mio CHF`, and with a sign before a number whose symbol follows it: `-5 €` is "moins cinq euros"."""

    scale_before_symbol: bool = True

    def _amounts(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        yield from super()._amounts(text, tokens, request)
        symbols = currency_symbols(request)
        scales = sorted(request.data["scales"], key=len, reverse=True)
        gaps = number_gaps(request.data)
        for number in numbers_in(text, request):
            if number.sign:
                found = self._after(text, number, symbols, scales, gaps, request)
                if found is not None:
                    yield found

    def _after(self, text: str, number: Number, symbols: Sequence[tuple[str, str]], scales: Sequence[str],
               gaps: Sequence[str], request: Request) -> Span | None:
        for scale, after in dict.fromkeys((_scale(text, number.end, scales, gaps), ("", number.end))):
            for gap in gaps:
                for symbol, code in symbols:
                    end = after + len(gap) + len(symbol)
                    if text.startswith(gap + symbol, after) \
                            and (bounds := _affixes(text, number.start, end, request.data, ())) is not None:
                        start, stop, prefix, suffix = bounds
                        return Span(start, stop, Form.MONEY,
                                    FrozenMap({"amount": number.amount(), "currency": code, "written_symbol": symbol,
                                               "scale": scale, "prefix": prefix, "suffix": suffix}),
                                    recognizer=self.name)
        return None


@dataclass(frozen=True)
class FrenchPercent(Percent):
    """The shared percent recognizer. A per mille sign, `‰` or its ASCII form `%o`, gives the span the
    `sign_position` of `permille`, which `speak_percent` reads as "pour mille"."""

    def _percents(self, text: str, request: Request) -> Iterator[Span]:
        for span in super()._percents(text, request):
            written = text[span.start:span.end]
            if "‰" in written or "%o" in written:
                span = replace(span, fields=FrozenMap({**span.fields, "sign_position": "permille"}))
            yield span


@dataclass(frozen=True)
class Year:
    """A year from 1000 to 2099 (design section 4.2): after a year word, as in `en 1984`; two years that a range
    mark joins, the lower one first, as in `1939-1945`, or a year and a higher two-digit end after a year word, as
    in `en 1939-45`; and a number that a link joins to a year, as in `en 1066 et 1215`. A comma alone links only
    inside a list that a link word ends, as in `en 1066, 1215 et 1415`.

    A count read as a year is wrong, so the follower of a linked list decides for all its years, and a range is
    one link of a list. A lowercase word that is not in `function_words` blocks them, as in `en 1234 étapes`, and
    so do a unit of the units table in any case, an operator and a dimension mark, as in `en 2048 Mo` and
    `en 1920 × 1080`. The rule is the year rule of `en.py`, read with the French tables."""
    name: str = "year"
    form: Form = Form.YEAR

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return join_ranges(self._years(text, tokens, request), text, request)

    def _years(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        year_words = frozenset(data["year_words"])
        function_words = frozenset(data["function_words"])
        marks = frozenset(data["range_marks"])
        units = frozenset(unit.lower() for unit in data["units"])
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
            if (text[start] in signs and not is_letter(text[start])) or follower.lower() in units:
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
    """A Roman numeral, `I`, `V` and `X` only, that is a sign of an ordinal or of a number in a name.

    An ordinal marker follows it with no space: `XXe` and `XIXème` (siècle), `Ier`, `Ire`, `IIe`. The marker is the
    evidence, so `Ve` reads "cinquième" and `Ier` "premier". A bare numeral reads as a number after a name of
    `roman_names`, the first names of sovereigns and popes, as in `Louis XIV` ("Louis quatorze") and `Charles V`, and
    after a heading word of `roman_headings`, as in `Acte II` ("Acte deux"). Any other numeral stays as written,
    such as `Malcolm X`, `Voir XIV` and `Le XI`, and so does a letter code such as `CD` or `MIX`."""

    name: str = "roman"
    form: Form = Form.ROMAN

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        marks = sorted(((m, kind) for kind, spellings in data["ordinal_marks"].items()
                        if not kind.startswith("second") for m in spellings), key=lambda p: len(p[0]), reverse=True)
        headings = frozenset(w.lower() for w in data["roman_headings"])
        names = frozenset(data["roman_names"])
        for run in _ROMAN_RUN.finditer(text):
            start, end = run.span()
            if start and is_word_char(text[start - 1]):
                continue
            value = roman.value(run.group())
            if value is None or value > 39:
                continue
            marker = next((m for m, kind in marks
                           if text.startswith(m, end)
                           and (end + len(m) == len(text) or not is_word_char(text[end + len(m)]))
                           and (value == 1) == kind.startswith(("masculine", "feminine"))), None)
            if marker is not None:
                yield Span(start, end + len(marker), Form.ROMAN,
                           FrozenMap({"value": value, "role": f"ordinal {marker}", "suffix": ""}),
                           recognizer=self.name)
            elif (end == len(text) or not is_word_char(text[end])) \
                    and self._named(text, start, run.group(), value, headings, names):
                yield Span(start, end, Form.ROMAN, FrozenMap({"value": value, "role": "cardinal", "suffix": ""}),
                           recognizer=self.name)

    @staticmethod
    def _named(text: str, start: int, numeral: str, value: int, headings: frozenset[str],
               names: frozenset[str]) -> bool:
        """Whether a heading word, or a capitalised name, stands before the numeral with one space between."""
        gap = start
        while gap > 0 and text[gap - 1] in GROUP_SPACES:
            gap -= 1
        if gap == start or gap == 0:
            return False
        first = gap
        while first > 0 and (is_letter(text[first - 1]) or text[first - 1] in "-'\u2019"):
            first -= 1
        word = text[first:gap]
        if not word:
            return False
        if word.lower() in headings:
            return True
        return word in names and (len(numeral) >= 2 or numeral in ("V", "X"))


def speak_french_abbreviation(span: Span, context: SpanContext) -> str:
    """An abbreviation of the tables, or a rate: `€/mois` is "euros par mois". The slash marks a division, which reads
    "par" (Office québécois de la langue française, Banque de dépannage linguistique, "Signe décimal et division dans
    les unités de mesure": "Les divisions sont indiquées symboliquement par la barre oblique et littéralement par la
    préposition par (ou à)")."""
    key, data = span.fields["key"], context.request.data
    if key.startswith("/"):
        word = key[1:]
        return f" par {data['rate_words'][word] if word in data['rate_words'] else data['units'][word]['one']}"
    return speak_abbreviation(span, context)


def speak_roman(span: Span, context: SpanContext) -> str:
    """`XXe` is "vingtième", `Ier` "premier", `Louis XIV` "quatorze" and `Acte II` "deux".

    The `role` of a span is "cardinal", or "ordinal" and the marker that the text writes."""
    request, fields = context.request, span.fields
    if fields["role"].startswith("ordinal "):
        return _ordinal_words(str(fields["value"]), fields["role"].removeprefix("ordinal "), request)
    return _cardinal(str(fields["value"]), request)


@dataclass(frozen=True)
class FrenchTime(TimeClock):
    """`14h30`, `14 h 30`, `14 h 30`, `21 h`, `7h` and `14:30`.

    The `clock_marks` table gives the colon form, which needs a time word before it, as in `à 14:30`, as in the
    shared recognizer. The letter `h` is evidence enough: `21 h` is "vingt et une heures" as a time and as a
    duration. A time that cannot be one, such as `25 h 99`, `12 h 60` or `24 h 30`, stays as written with a
    warning. An hour above 24 with no minutes, as in `100 h`, is a duration for the measure reader, and so is an
    hour and minutes that `min` or `s` follows, as in `1 h 30 min`. Minutes that a digit continues are no minutes,
    so `4h 305` reads the hour alone and then the number."""

    def _times(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        yield from super()._times(text, tokens, request)
        pattern = re.compile(request.data["patterns"]["clock_hour"])
        folded = fold_digits(text)
        for match in pattern.finditer(folded):
            start = match.start()
            ends = [match.end()]
            if match.group(2) is not None:
                ends.append(start + match.group().lower().index("h") + 1)
            end = next((end for end in ends if _clock_edge(text, start, end)
                        and not (end < len(text) and text[end].isalnum())), None)
            if end is None or (start and text[start - 1].isalnum()) or not one_digit_set(text[start:end]):
                continue
            hour = int(match.group(1))
            minute = None if end < match.end() or match.group(2) is None else int(match.group(2))
            rest = text[end:].lstrip(GROUP_SPACES)
            if next((w for w in ("min", "s") if rest.startswith(w) and is_bounded(rest, 0, len(w))), None):
                continue
            valid = hour <= 24 and (minute is None or (minute <= 59 and (hour < 24 or minute == 0)))
            if not valid and minute is None:
                continue
            yield Span(start, end, Form.TIME,
                       FrozenMap({"hour": hour, "minute": minute or 0, "second": None, "period": None, "prefix": "",
                                  "suffix": ""}), recognizer=self.name, keep=not valid)


@dataclass(frozen=True)
class Ordinal:
    """`1er`, `1re`, `1ère`, `2e`, `3ème`, `21e`, `4es`, `2nd`, `2nde`: a whole number that a marker follows with no
    space. `er`, `re` and `ère` mark 1 only, `nd` and `nde` mark 2 only, and `e` and `ème` mark any other number."""

    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        marks = request.data["ordinal_marks"]
        spellings = sorted(((m, kind) for kind, ms in marks.items() for m in ms), key=lambda p: len(p[0]), reverse=True)
        for number in numbers_in(text, request):
            if number.sign or number.fraction is not None:
                continue
            value = number.integer.lstrip("0")
            for marker, kind in spellings:
                end = number.end + len(marker)
                if not text.startswith(marker, number.end) or not is_bounded(text, number.start, end):
                    continue
                first = kind.startswith(("masculine", "feminine"))
                second = kind.startswith("second")
                plain = not (first or second)
                if (first and value != "1") or (second and value != "2") or (plain and value in ("", "1")):
                    continue
                yield Span(number.start, end, Form.ORDINAL,
                           FrozenMap({"digits": number.integer, "marker": marker, "prefix": "", "suffix": "",
                                      "script": number.script}), recognizer=self.name)
                break


@dataclass(frozen=True)
class Abbreviation:
    """A title before a capitalised name, a saint before a capitalised name or after a hyphen, `n°` before a number,
    and the abbreviations of the table. A title that an initial follows, as in `M. J. Dupont`, stays as written.
    A slash between a currency symbol and a word of `rate_words`, as in `5 €/mois`, reads "par" and the word."""

    name: str = "abbreviation"
    form: Form = Form.ABBREVIATION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        yield from self._rates(text, request)
        final = frozenset(data["sentence_final"])
        particles = tuple(data["name_particles"])
        for table in ("titles", "number_abbreviations", "abbreviations"):
            for key in sorted((k for k, v in data[table].items() if v is not None), key=len, reverse=True):
                position = text.find(key)
                while position != -1:
                    end = position + len(key)
                    following = next_visible(text, end)
                    trail = ""
                    if position and is_word_char(text[position - 1]):
                        ok = False
                    elif table == "titles":
                        ok = self._name_follows(text, end, particles) and self._title_fits(text, position, key, data)
                    elif table == "number_abbreviations":
                        ok = following.isdigit()
                        trail = " " if text[end:end + 1].isdigit() else ""
                    else:
                        ok = is_bounded(text, position, end)
                        if key in final and (following in ("", ".") or following.isupper()):
                            trail = "."
                    if ok:
                        yield Span(position, end, Form.ABBREVIATION, FrozenMap({"key": key}), trail=trail,
                                   recognizer=self.name)
                    position = text.find(key, end)

    @staticmethod
    def _title_fits(text: str, position: int, key: str, data: FrozenMap) -> bool:
        """Whether a title that is also another word reads as the title. `Me` is also the pronoun "me" (Wiktionnaire,
        "me": "Pronom de la première personne du singulier en tant que complément d'objet direct", "Ça me paraît
        logique", "Ne me le dis pas"), so it stays as written after a subject pronoun or "ne", as in
        "Tu Me Manques", after a capitalised word inside a sentence, which writes a title in capitals, before a word
        of `function_words`, `no_de_words` or `no_noun_words`, as in "Me Voici", and in a name of `title_exceptions`,
        which the Wiktionnaire gives: "Me Too", "Variante orthographique de MeToo". `bd` is also the feminine noun
        "bd", a bande dessinée (Wiktionnaire, "BD", f: "Bande dessinée", "Les aventures de Tintin sont une BD"), and
        "bd", boulevard, is masculine (Wiktionnaire,
        "bd": "Boulevard", m), so it stays as written after a feminine or plural determiner: "la bd Astérix"."""
        before, begin = _word_before(text, position)
        lower = before.lower()
        if key in data["street_titles"]:
            return data["determiners"].get(lower) not in ("feminine", "plural")
        if key not in data["pronoun_titles"]:
            return True
        if lower in data["inverted_pronouns"] or lower == "ne":
            return False
        if before[:1].isupper():
            head, _ = _word_before(text, begin)
            stop = begin
            while stop and text[stop - 1] in GROUP_SPACES:
                stop -= 1
            if head or (stop and text[stop - 1] not in ".!?:«\"(\u2026"):
                return False
        if any(text.startswith(name, position) and is_bounded(text, position, position + len(name))
               for name in data["title_exceptions"]):
            return False
        following = text[position + len(key):].lstrip(GROUP_SPACES)
        stop = 0
        while stop < len(following) and is_letter(following[stop]):
            stop += 1
        word = following[:stop].lower()
        return word not in _stops(tuple(data["function_words"]), tuple(data["no_de_words"]),
                                  tuple(data["no_noun_words"]))

    def _rates(self, text: str, request: Request) -> Iterator[Span]:
        """The slash and the word after an amount and a currency symbol, "5 €/mois", "20 $/h", with a space on both
        sides of the slash or on neither, and after such a rate, "5 €/an/personne". The word is a word of
        `rate_words` or a unit symbol of `units`, as in "3 €/kg", and ends at a word boundary."""
        data = request.data
        symbols = tuple(symbol for symbol, _ in currency_symbols(request))
        words = sorted((*data["rate_words"], *data["units"]), key=len, reverse=True)
        rate_end = None
        position = text.find("/")
        while position != -1:
            spaced = position and text[position - 1] == " " and text[position + 1:position + 2] == " "
            begin = position - 1 if spaced else position
            after = position + (2 if spaced else 1)
            amount = text[:begin].endswith(symbols) and next(
                (symbol for symbol in symbols if text[:begin].endswith(symbol)), "")
            anchored = rate_end == begin
            if amount:
                head = text[:begin - len(amount)].rstrip(GROUP_SPACES)
                anchored = anchored or bool(head) and is_digit(head[-1])
            if anchored:
                for word in words:
                    end = after + len(word)
                    if text.startswith(word, after) and is_bounded(text, after, end):
                        yield Span(begin, end, Form.ABBREVIATION, FrozenMap({"key": "/" + word}),
                                   recognizer=self.name)
                        rate_end = end
                        break
            position = text.find("/", position + 1)

    @staticmethod
    def _name_follows(text: str, end: int, particles: tuple[str, ...]) -> bool:
        """Whether a capitalised word, or a particle and more text, or a hyphen and a capital, follows text[:end]."""
        if end < len(text) and is_letter(text[end]):
            return False
        if text.startswith("-", end) and text[end + 1:end + 2].isupper():
            return True
        index = end
        while index < len(text) and text[index] in GROUP_SPACES:
            index += 1
        if index >= len(text):
            return False
        stop = index
        while stop < len(text) and (is_letter(text[stop]) or text[stop] == "'"):
            stop += 1
        word = text[index:stop]
        elided = word[:word.find("'") + 1] if "'" in word else word
        if word.lower() in particles or elided.lower() in particles:
            return stop < len(text)
        return text[index].isupper() and not (len(word) == 1 and text.startswith(".", stop))


@dataclass(frozen=True)
class DateNamed:
    """`10 novembre 2026`, `1er novembre`, `10 novembre`, `novembre 2026`: a date with a month name."""

    name: str = "date_named"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        patterns, symbols = request.data["patterns"], request.data["symbols"]
        folded = fold_digits(text)
        for key in ("date_day_month", "date_month_year"):
            for match in re.finditer(patterns[key], folded):
                start, end = match.span()
                if (not is_bounded(text, start, end) or (start and text[start - 1] in symbols)
                        or not one_digit_set(text[start:end])):
                    continue
                if key == "date_day_month":
                    day, ordinal, month_name, year = match.groups()
                    if ordinal and day != "1":
                        continue
                else:
                    day, month_name, year = None, match.group(1), match.group(2)
                month = [m.lower() for m in request.data["months"]].index(month_name.lower()) + 1
                year_value = int(year) if year is not None else None
                if day is not None and not is_valid(year_value, month, int(day)):
                    continue
                yield Span(start, end, Form.DATE,
                           FrozenMap({"year": year_value, "month": month, "day": int(day) if day else None,
                                      "written_order": "DMY", "month_written": "name", "era": "", "prefix": "",
                                      "suffix": ""}), recognizer=self.name)


LANGUAGE = LanguageSpec(
    code="fr",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(
        SHARED["lexicon"],
        Telephone(declines=True, spaces=GROUP_SPACES, plans=PLANS),
        SHARED["color"],
        SHARED["idiom"],
        DateNamed(),
        SHARED["date_numeric"],
        FrenchTime(),
        Telephone(spaces=GROUP_SPACES, plans=PLANS),
        FrenchMoney(),
        SHARED["kept_money"],
        FrenchPercent(),
        SHARED["measure"],
        Year(),
        SHARED["expression"],
        SHARED["fraction"],
        FrenchRange(),
        Roman(),
        Ordinal(),
        Abbreviation(),
        FrenchDecimal(),
        FrenchCardinal(),
    ),
    verbalizers={
        Form.LEXICON: speak_lexicon,
        Form.COLOR: speak_color,
        Form.IDIOM: speak_idiom,
        Form.DATE: speak_date,
        Form.TIME: speak_time,
        Form.TELEPHONE: speak_telephone,
        Form.MONEY: speak_money,
        Form.PERCENT: speak_percent,
        Form.MEASURE: speak_measure,
        Form.YEAR: speak_year,
        Form.EXPRESSION: speak_expression,
        Form.FRACTION: speak_fraction,
        Form.RANGE: speak_range,
        Form.ROMAN: speak_roman,
        Form.ORDINAL: speak_ordinal,
        Form.ABBREVIATION: speak_french_abbreviation,
        Form.DECIMAL: speak_french_decimal,
        Form.CARDINAL: speak_cardinal,
    },
    writers=("numtag",),
    spellers={
        Form.CARDINAL: SPELLER,
        Form.ORDINAL: SPELLER,
        Form.DECIMAL: SPELLER,
        Form.FRACTION: SPELLER,
        Form.YEAR: SPELLER,
    },
    genders=frozenset({MASCULINE, FEMININE}),
    default_gender=MASCULINE,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={
        "date_order": frozenset({"DMY", "MDY"}),
        "clock": frozenset({"24h", "12h"}),
        "minute_style": frozenset({"number", "phrase"}),
        "decimal_mark": frozenset({",", "."}),
        "scale": frozenset({"long"}),
        "register": frozenset({"formal", "colloquial"}),
        "default_gender": frozenset({"masculine", "feminine"}),
        "phone_regions": frozenset(PLANS),
    },
    not_applicable=frozenset(),
)
