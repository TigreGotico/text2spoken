"""Greek: el-GR.

Cardinals come from the CLDR RBNF rule sets of `el` (design section 5.4): `spellout-cardinal-masculine`,
`spellout-cardinal-feminine` and `spellout-cardinal-neuter`. A number takes the gender of the noun that it counts. The
words that change are 1 (ένας, μία, ένα), 3 (τρεις, τρία), 4 (τέσσερις, τέσσερα), 13 and 14, the hundreds from 200
(διακόσιοι, διακόσιες, διακόσια) and 1000 (χίλιοι, χίλιες, χίλια). From 2000 up the thousands are the feminine noun
χιλιάδες, and the number before it takes the feminine in every gender, as the rule `2000:
←%spellout-cardinal-feminine← χιλιάδες` says: `3000` reads "τρεις χιλιάδες". Wikipedia, "Modern Greek grammar",
Numerals: "The numerals one, three and four are declined irregularly. Other numerals such as διακόσιοι [...] and
χίλιοι [...] are declined regularly like adjectives."

A number with no noun reads the neuter. The `el` rule set `spellout-numbering` is `0: =%spellout-cardinal-neuter=;`,
and UTS #35, Part 3, "Rule-Based Number Formatting", defines that rule set as "the default used when there is no
context for the number. Usually this is used for counting without reference to a noun". The English Wiktionary,
"δεκατρείς", Usage notes: "When counting, use the "numeral noun", neuter δεκατρία", and "δεκατέσσερις" says the same of
δεκατέσσερα. A number before a word that the lists below do not hold reads the same neuter, and `default_gender`
changes it.

The gender of a noun comes from `data/wiktionary/el_nouns.json`, which `scripts/extract_el_nouns.py` makes from the
categories "Greek masculine nouns", "Greek feminine nouns" and "Greek neuter nouns" of the English Wiktionary, with the
inflected forms of each noun, singular and plural, by case. So `3 βιβλία` reads "τρία βιβλία", `3 γυναίκες` "τρεις
γυναίκες" and `200 σκύλοι` "διακόσιοι σκύλοι". The noun may come after adjectives: Wikipedia, "Modern Greek grammar":
"Within the noun phrase, adjectives commonly precede the noun", with "the usual order ένα νέο βιβλίο". The same page
says "Adjectives agree with nouns in gender, case and number", so an adjective form of the category "Greek adjectives"
gives the gender too, when no noun of the list follows it: `3 μεγάλα κουτάκια` reads "τρία". Between two numbers a
word of `number_links` stands, and both numbers count the noun after the second: `3 ή 4 γυναίκες` reads "τρεις ή
τέσσερις γυναίκες".

The article before a number agrees with the same noun (Wikipedia, "Modern Greek grammar", Articles: "The article
agrees with the noun it modifies"), and `articles` gives its genders from the table of definite articles on that page.
The forms with σε are contractions, as the English Wiktionary, "στις", says: "contraction of σε τις". The article
decides when no noun follows, as in `στις 5` and `το 1956`. When the article and the noun disagree, the article
decides, because the noun lists also hold forms of other words. A phrase that leaves more than one gender open reads
the default gender when that gender is one of them, and else the masculine: `οι 200` reads "διακόσιοι", and so does
`200 γιατροί`, a noun of both genders that the English Wiktionary heads `{{el-noun|m|g2=f}}`, masculine first.

The case of the noun form changes the number, by the rules of CLDR 49 (`release-49/common/rbnf/el.xml`):
`spellout-cardinal-masculine-accusative` gives "έναν", the hundreds in "-κόσιους" and "χίλιους",
and the genitive rule sets give "ενός", "μιας", "τριών", "τεσσάρων", the hundreds in "-κοσίων", "χιλίων",
"χιλιάδων" and "εκατομμυρίων". The feminine and the neuter accusative are the nominative ("0:
=%spellout-cardinal-feminine=;"). `case_words` holds these words. A noun form that is only accusative or only
genitive gives its case, as `σκύλους` and `βιβλίων`. A form that is also nominative reads the nominative. An article
gives no case alone, because a year after a genitive article keeps its nominative, as in `του 1998`.

A number above 1 counts a plural noun, and only a genitive plural gives it the genitive. Every genitive plural ends
in -ων, and no genitive singular does, in the noun tables Ο1 to Ο53 of the Λεξικό της κοινής νεοελληνικής
(Triantafyllidis Foundation, on the Portal for the Greek Language, "Ουσιαστικά"), as Ο25 "ώρα ώρας [...] ώρες ωρών"
and Ο38 "βουνό βουνού [...] βουνά βουνών". So a genitive form with no -ων after such a number names no counted noun,
and the number reads with no noun: `η τάξη 3 Γυμνασίου` reads "τρία". The same dictionary, "τρεις", gives the plural
genitive: "Ένα παιδί τριών χρόνων".

Two numbers that και joins count the same noun, as with ή: the numbers are adjectives, "τρεις -εις -ία [...] αριθμτ.
επίθ. απόλ." (Λεξικό της κοινής νεοελληνικής, "τρεις"). The walk to the noun skips the adverb ακόμη or ακόμα, which may
stand before the noun: "Θα χρειαστώ λίγα ~ τετράδια" ("ακόμη", 2, ποσοτικό). It reads the pronoun άλλος as an
adjective: "άλλος -η -ο [...] αντων. αόρ. (βλ. Ε3) [...] με λειτουργία επιθέτου ή ουσιαστικού" ("άλλος"), and
`pronoun_adjectives` holds its forms by the table Ε3 of the dictionary, whose masculine row is "άσπρος άσπρου άσπρο
άσπρε άσπροι άσπρων άσπρους άσπροι". A noun form that is also an adjective, as νέα, the news, and νέα, new, is an
adjective when the word after it agrees with it: `1 νέα μεγάλη τσάντα` reads "μία".

A number is an hour of the clock, and counts the feminine ώρα, before the words of `hour_phrases`, where # stands
for a number: "Να έρθει στις ~ (η ώρα). Είναι ~ (η ώρα.)" ("τρεις"), "Η ώρα είναι μία / δύο / τρεις και μισή"
("μισός") and "Η ώρα είναι δώδεκα και τρία λεπτά" ("λεπτό" 2). So `Είναι 3 και 5 λεπτά` reads "τρεις". A number
after a weekday name, with no noun after it, is the day of the month, as in the CLDR 49 date formats of `el` `full`
"EEEE d MMMM y" and `MEd` "E d/M". It counts the feminine ημέρα, as before a month name: "Στις ~ του μηνός, την τρίτη
ημέρα του μήνα" ("τρεις"). `weekdays` holds the CLDR 49 format wide day names.

Text in capitals writes no accent: Wikipedia, "Greek diacritics", Position in letters: "In uppercase (all-caps),
accents and breathings are eliminated". So each form of more than one vowel group of the noun and adjective lists is
also found with no accent, as `ΓΥΝΑΙΚΕΣ` and `μερες` find γυναίκες and μέρες. A word of one vowel group, as `οι`,
finds only its own form, so that an article stays an article.

A day before a month name counts the feminine ημέρα, the day of the month, and day 1 is its ordinal: Βικιλεξικό,
"Πρωτομαγιά": "η πρώτη ημέρα του Μαΐου". `month_names` holds the genitive month names of CLDR 49, `el`, format
wide and abbreviated. So `4 Ιουνίου` reads "τέσσερις Ιουνίου" and `1 Μαΐου` "πρώτη Μαΐου".

The RBNF data of unicode-rbnf writes "χίλιάδες" with two accents, "εννενήντα" with two ν and 13 as "δεκατρεις" with
no accent. The core table `data/rbnf_corrections.json` gives the right words and their sources, and `RbnfSpeller`
reads it (design section 5.4).

A minus reads "μείον", the word of the RBNF rule `-x: μείον >>;`. As in the other files, the hyphen of `5-10` and
`A-5` is no minus. Money, measures and an ordinal with a full stop stay as written, as for a language with no file
(design section 6.1), and so does an amount with a minus, as `-50 €` and `€ -50`.

A percentage reads its number and "τοις εκατό", the unit pattern of `concentr-percent` in the CLDR units of `el`, which
gives the unit the neuter gender: `20%` reads "είκοσι τοις εκατό" and `-5%` "μείον πέντε τοις εκατό". A decimal
before it reads by the rule `x.x: << κόμμα >>` of `spellout-cardinal-neuter` (CLDR 49, common/rbnf/el.xml): the
integer, κόμμα and each written digit, as RBNF reads 2.25 "δύο κόμμα δύο πέντε". So `2,5%` reads "δύο κόμμα πέντε
τοις εκατό". A per mille sign and two percentages that a dash joins stay as written.

A fraction reads when its denominator has a one-word name in the English Wiktionary appendix "Greek numerals",
Fraction column: 2 to 12, 20, 60, 70, 80 and 100. The Λεξικό της κοινής νεοελληνικής gives the names of 60, 70 and
80 as nouns: "το εξηκοστό, το ένα από τα εξήντα ίσα μέρη ενός συνόλου" ("εξηκοστός"), "το εβδομηκοστό, το ένα από
τα εβδομήντα ίσα μέρη ενός συνόλου: Μου ανήκουν τα τριάντα εβδομηκοστά του οικοπέδου" ("εβδομηκοστός") and "το
ογδοηκοστό, το ένα από τα ογδόντα ίσα μέρη ενός συνόλου" ("ογδοηκοστός"). The half is the adjective μισός, which
agrees with its noun (English Wiktionary, "μισός": "μισή ώρα", half an hour; "μισό": "μισό κιλό κρασί"). Any other
name is a neuter noun, as "τρίτο", plural "τρίτα", and "τέταρτο", plural "τέταρτα" (English Wiktionary), so its
numerator reads in the neuter: `1/3` reads "ένα τρίτο" and `3/4` "τρία τέταρτα". The plural of each name is the
neuter plural of its ordinal adjective in -ος. Any other fraction stays as written.

A fraction with a denominator up to 12 may be a day and a month: the CLDR 49 date formats of `el` write `d/M/yy`
(short) and `d/M` (`Md`). With no mark of a fraction, such a form stays as written (design section 10), as do a
score and a count of tries. The marks are a neuter article before it, as the fraction is a neuter noun ("Το μισό
αριθμητικά γράφεται ως 1/2 ή 0,5", Λεξικό της κοινής νεοελληνικής, "μισός"); a genitive article or noun after it,
the whole that it divides ("Ένα τέταρτο της ώρας", "ώρα" 1); and, for 1/2, a noun after it ("Μισό μέτρο / κιλό.
Μισή ώρα.", "μισός"). So `Έφαγε τα 3/4 της πίτας` reads and `στις 3/8` stays as written. The same marks decide for
60, 70 and 80, which follow the number of a law or a decree as a two-digit year, as in `Νόμος 14/60`, and a ratio, as
in `40/60`. A denominator with a leading zero, as in `03/09`, has no name, so such a form stays as written too.

A whole number up to 20 and a half are one word. The Λεξικό της κοινής νεοελληνικής, "-μισι": "-μισι [misi], όταν
το α' συνθετικό λήγει σε φωνήεν & -ήμισι [ímisi], όταν το α' συνθετικό λήγει σε σύμφωνο : β' συνθετικό σε σύνθεση με
τα απόλυτα αριθμητικά συνήθ. ως το είκοσι· προσδίδει στο οποιουδήποτε γένους ουσιαστικό που προσδιορίζει την έννοια
του αριθμητικού αυξημένη κατά μισή μονάδα: οκτώ ~ : Εργασία οκτώ ~ ωρών· δεκατρεισήμισι: Απόσταση δεκατρεισήμισι
χιλιομέτρων· τρεισήμισι και τριά ~ , τεσσερισήμισι και τεσσερά ~". Before -μισι, the CLDR cardinal takes the
accent on its last syllable, as in τεσσεράμισι (Λεξικό, "τεσσερά ~"; Βικιλεξικό, "τεσσεράμισι"), δωδεκάμισι and
οκτώμισι (Βικιλεξικό, "-μισι") and εξίμισι (Βικιλεξικό, "εξίμισι", after Μπαμπινιώτης: "γράφεται εξίμισι (εξί -
μισι), όπως τα ενάμισι, δυόμισι, πεντέμισι").
The Λεξικό allows that accent on επτά and εννέα: "επτά- [...] όταν κατά τη σύνθεση ο τόνος ανεβαίνει στο α'
συνθετικό" ("επτα-"), and the same for "εννεά-". The English Wiktionary gives τρεισήμισι ("g=m|g2=f|neuter|τριάμισι")
and τεσσερισήμισι ("g=m|g2=f|neuter|τεσσεράμισι"), so the neuter of 3, 4, 13 and 14 takes -μισι after τρία and
τέσσερα. The genitive of these numbers is one form for each gender, as τριών, and the Λεξικό writes δεκατρεισήμισι
with the neuter χιλιομέτρων, so the genitive takes -ήμισι. One and a half declines: "ενάμισης μιάμιση ενάμισι [...]
αριθμτ. επίθ. : ένας και μισός: ~ χρόνος. Μιάμιση ώρα. Ενάμισι μέτρο. Σε διάστημα ενάμιση χρόνου / μιάμισης ώρας /
ενάμισι έτους" ("ενάμισης"). `halves` holds these words by gender and case. The masculine accusative of ενάμισης and
a whole number above 20, where the Λεξικό names no word, stay as written.

A numeric date reads day, month and year, as the CLDR long date format of `el`, `d MMMM y`, writes it, with the month
name of `months`, CLDR 49 format wide, in the genitive. The day is the feminine ημέρα, as above, and the year reads
in the neuter, as a number with no noun. The date adds no weekday. The core resolves the order: a field above 12 is
the day, and when both fields are 12 or below the day comes first, as in the CLDR short date format `d/M/yy`. The
decimal mark is the comma and the group mark the full stop (CLDR 49 number symbols of `el`), so `1.234` reads as one
number. A decimal stays as written.

The file claims no ordinal in plain text. A say-as ordinal (text2spoken design, section 17.5) reads through the
ordinal rule sets of `el`, `spellout-ordinal-masculine`, `-feminine` and `-neuter`, in the default gender, the neuter:
`3` reads "τρίτο".
"""
from __future__ import annotations

import json
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace
from functools import lru_cache
from importlib.resources import files

from text2spoken.core.language import LanguageSpec, Request, Variety
from text2spoken.core.recognizers import (GAPS, SHARED, OrdinalStop, _free_before, numbers_in, signed,
                                          speak_lexicon, written_shapes)
from text2spoken.core.spans import (FIELDS, Features, Recognizer, Span, SpanContext, clause_breaks, clause_window,
                                    context_words)
from text2spoken.core.spellers import RbnfSpeller
from text2spoken.core.tokens import Token
from text2spoken.errors import DeclinedReading
from text2spoken.params import OPTIONS, FrozenMap, Form, GrammaticalGender, freeze

M, F, N = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE, GrammaticalGender.NEUTER
NOMINATIVE, ACCUSATIVE, GENITIVE = "nominative", "accusative", "genitive"
MASCULINE, FEMININE, NEUTER = M.value, F.value, N.value

_HUNDREDS = ("διακόσι", "τριακόσι", "τετρακόσι", "πεντακόσι", "εξακόσι", "επτακόσι", "οκτακόσι", "εννιακόσι")

DATA = freeze({
    **written_shapes(),
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}]},
    "sign_words": {"-": "μείον"},
    "decimal_word": "κόμμα",
    "percent": {**written_shapes()["percent"], "word": "τοις εκατό"},
    "months": ["Ιανουαρίου", "Φεβρουαρίου", "Μαρτίου", "Απριλίου", "Μαΐου", "Ιουνίου", "Ιουλίου", "Αυγούστου",
               "Σεπτεμβρίου", "Οκτωβρίου", "Νοεμβρίου", "Δεκεμβρίου"],
    "half": {
        MASCULINE: {NOMINATIVE: "μισός", ACCUSATIVE: "μισό", GENITIVE: "μισού"},
        FEMININE: {NOMINATIVE: "μισή", ACCUSATIVE: "μισή", GENITIVE: "μισής"},
        NEUTER: {NOMINATIVE: "μισό", ACCUSATIVE: "μισό", GENITIVE: "μισού"},
    },
    "fraction_names": {"3": ["τρίτο", "τρίτα"], "4": ["τέταρτο", "τέταρτα"], "5": ["πέμπτο", "πέμπτα"],
                       "6": ["έκτο", "έκτα"], "7": ["έβδομο", "έβδομα"], "8": ["όγδοο", "όγδοα"],
                       "9": ["ένατο", "ένατα"], "10": ["δέκατο", "δέκατα"], "11": ["ενδέκατο", "ενδέκατα"],
                       "12": ["δωδέκατο", "δωδέκατα"], "20": ["εικοστό", "εικοστά"], "60": ["εξηκοστό", "εξηκοστά"],
                       "70": ["εβδομηκοστό", "εβδομηκοστά"], "80": ["ογδοηκοστό", "ογδοηκοστά"],
                       "100": ["εκατοστό", "εκατοστά"]},
    "halves": {
        "1": {MASCULINE: {NOMINATIVE: "ενάμισης", GENITIVE: "ενάμιση"},
              FEMININE: {NOMINATIVE: "μιάμιση", ACCUSATIVE: "μιάμιση", GENITIVE: "μιάμισης"},
              NEUTER: dict.fromkeys((NOMINATIVE, ACCUSATIVE, GENITIVE), "ενάμισι")},
        **{whole: {MASCULINE: dict.fromkeys((NOMINATIVE, ACCUSATIVE, GENITIVE), other),
                   FEMININE: dict.fromkeys((NOMINATIVE, ACCUSATIVE, GENITIVE), other),
                   NEUTER: {NOMINATIVE: neuter, ACCUSATIVE: neuter, GENITIVE: other}}
           for whole, other, neuter in (
               ("2", "δυόμισι", "δυόμισι"), ("3", "τρεισήμισι", "τριάμισι"), ("4", "τεσσερισήμισι", "τεσσεράμισι"),
               ("5", "πεντέμισι", "πεντέμισι"), ("6", "εξίμισι", "εξίμισι"), ("7", "επτάμισι", "επτάμισι"),
               ("8", "οκτώμισι", "οκτώμισι"), ("9", "εννεάμισι", "εννεάμισι"), ("10", "δεκάμισι", "δεκάμισι"),
               ("11", "εντεκάμισι", "εντεκάμισι"), ("12", "δωδεκάμισι", "δωδεκάμισι"),
               ("13", "δεκατρεισήμισι", "δεκατριάμισι"), ("14", "δεκατεσσερισήμισι", "δεκατεσσεράμισι"),
               ("15", "δεκαπεντέμισι", "δεκαπεντέμισι"), ("16", "δεκαεξίμισι", "δεκαεξίμισι"),
               ("17", "δεκαεπτάμισι", "δεκαεπτάμισι"), ("18", "δεκαοκτώμισι", "δεκαοκτώμισι"),
               ("19", "δεκαεννεάμισι", "δεκαεννεάμισι"), ("20", "εικοσίμισι", "εικοσίμισι"))},
    },
    "leads": {},
    "case_words": {
        ACCUSATIVE: {"ένας": "έναν", "χίλιοι": "χίλιους", **{f"{h}οι": f"{h}ους" for h in _HUNDREDS}},
        GENITIVE: {"ένας": "ενός", "ένα": "ενός", "μία": "μιας", "τρεις": "τριών", "τρία": "τριών",
                   "τέσσερις": "τεσσάρων", "τέσσερα": "τεσσάρων", "δεκατρείς": "δεκατριών", "δεκατρία": "δεκατριών",
                   "δεκατέσσερις": "δεκατεσσάρων", "δεκατέσσερα": "δεκατεσσάρων", "χίλιοι": "χιλίων",
                   "χίλιες": "χιλίων", "χίλια": "χιλίων", "χιλιάδες": "χιλιάδων", "εκατομμύριο": "εκατομμυρίου",
                   "εκατομμύρια": "εκατομμυρίων", "δισεκατομμύριο": "δισεκατομμυρίου",
                   "δισεκατομμύρια": "δισεκατομμυρίων", "τρισεκατομμύριο": "τρισεκατομμυρίου",
                   "τρισεκατομμύρια": "τρισεκατομμυρίων",
                   **{f"{h}{end}": h.replace("όσι", "οσί") + "ων" for h in _HUNDREDS for end in ("οι", "ες", "α")}},
    },
    "articles": {
        "ο": [[MASCULINE, NOMINATIVE]], "η": [[FEMININE, NOMINATIVE]],
        "το": [[NEUTER, NOMINATIVE], [NEUTER, ACCUSATIVE]], "τον": [[MASCULINE, ACCUSATIVE]],
        "τη": [[FEMININE, ACCUSATIVE]], "την": [[FEMININE, ACCUSATIVE]],
        "του": [[MASCULINE, GENITIVE], [NEUTER, GENITIVE]], "της": [[FEMININE, GENITIVE]],
        "οι": [[MASCULINE, NOMINATIVE], [FEMININE, NOMINATIVE]], "τα": [[NEUTER, NOMINATIVE], [NEUTER, ACCUSATIVE]],
        "τους": [[MASCULINE, ACCUSATIVE]], "τις": [[FEMININE, ACCUSATIVE]],
        "των": [[MASCULINE, GENITIVE], [FEMININE, GENITIVE], [NEUTER, GENITIVE]],
        "στο": [[NEUTER, ACCUSATIVE]], "στον": [[MASCULINE, ACCUSATIVE]], "στη": [[FEMININE, ACCUSATIVE]],
        "στην": [[FEMININE, ACCUSATIVE]], "στου": [[MASCULINE, GENITIVE], [NEUTER, GENITIVE]],
        "στης": [[FEMININE, GENITIVE]], "στα": [[NEUTER, ACCUSATIVE]], "στους": [[MASCULINE, ACCUSATIVE]],
        "στις": [[FEMININE, ACCUSATIVE]], "στων": [[MASCULINE, GENITIVE], [FEMININE, GENITIVE], [NEUTER, GENITIVE]],
    },
    "number_links": ["ή", "έως", "ως", "μέχρι", "με", "και"],
    "walk_adverbs": ["ακόμη", "ακόμα"],
    "pronoun_adjectives": {
        "άλλος": [[MASCULINE, NOMINATIVE]], "άλλου": [[MASCULINE, GENITIVE], [NEUTER, GENITIVE]],
        "άλλο": [[MASCULINE, ACCUSATIVE], [NEUTER, NOMINATIVE], [NEUTER, ACCUSATIVE]],
        "άλλοι": [[MASCULINE, NOMINATIVE]], "άλλους": [[MASCULINE, ACCUSATIVE]],
        "άλλων": [[MASCULINE, GENITIVE], [FEMININE, GENITIVE], [NEUTER, GENITIVE]],
        "άλλη": [[FEMININE, NOMINATIVE], [FEMININE, ACCUSATIVE]], "άλλης": [[FEMININE, GENITIVE]],
        "άλλες": [[FEMININE, NOMINATIVE], [FEMININE, ACCUSATIVE]], "άλλα": [[NEUTER, NOMINATIVE], [NEUTER, ACCUSATIVE]],
    },
    "hour_phrases": [["η", "ώρα"], ["και", "μισή"], ["και", "#", "λεπτά"], ["και", "#", "λεπτό"]],
    "weekdays": ["κυριακή", "δευτέρα", "τρίτη", "τετάρτη", "πέμπτη", "παρασκευή", "σάββατο"],
    "month_names": ["ιανουαρίου", "φεβρουαρίου", "μαρτίου", "απριλίου", "μαΐου", "ιουνίου", "ιουλίου", "αυγούστου",
                    "σεπτεμβρίου", "οκτωβρίου", "νοεμβρίου", "δεκεμβρίου", "ιαν", "φεβ", "μαρ", "απρ", "μαΐ", "ιουν",
                    "ιουλ", "αυγ", "σεπ", "οκτ", "νοε", "δεκ"],
})

GENDER_ORDER = (M, F, N)
CASE_ORDER = (NOMINATIVE, ACCUSATIVE, GENITIVE)
ADJECTIVE_WALK = 2
"""The adjectives that may stand between a number and its noun."""
NUMBER = re.compile(r"[0-9]{1,3}(?:[.][0-9]{3})+|[0-9]+")
"""A number among the words after a number: digits, or groups of three digits after the full stop of `number_marks`."""
NO_TONOS = str.maketrans("άέήίόύώΐΰ", "αεηιουωϊϋ")
VOWELS = re.compile("[αεηιουωϊϋ]+")


class GreekSpeller:
    """The RBNF `el` cardinal of a gender, with the case words of `case_words`. The accusative words are masculine
    words only; the genitive words serve each gender."""

    def __init__(self):
        self.rbnf = RbnfSpeller(
            cardinal={Features(): "spellout-numbering", Features(gender=M): "spellout-cardinal-masculine",
                      Features(gender=F): "spellout-cardinal-feminine", Features(gender=N): "spellout-cardinal-neuter"},
            ordinal={Features(): "spellout-ordinal-neuter", Features(gender=M): "spellout-ordinal-masculine",
                     Features(gender=F): "spellout-ordinal-feminine", Features(gender=N): "spellout-ordinal-neuter"})

    @staticmethod
    def _respell(words: str, features: Features, request: Request) -> str:
        if features.case == GENITIVE or (features.case == ACCUSATIVE and features.gender == M):
            table = request.data["case_words"][features.case]
            return " ".join(table.get(word, word) for word in words.split())
        return words

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        return self._respell(self.rbnf.cardinal(digits, Features(gender=features.gender), request), features, request)

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        return self._respell(self.rbnf.ordinal(digits, Features(gender=features.gender), request), Features(),
                             request)

    def year(self, digits: str, features: Features, request: Request) -> str:
        raise NotImplementedError("the Greek file reads no year")

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """The RBNF rule `x.x: << κόμμα >>`: the integer, `decimal_word` and each written digit."""
        digits = " ".join(self.cardinal(digit, features, request) for digit in fraction)
        return f"{self.cardinal(integer, features, request)} {request.data['decimal_word']} {digits}"

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """A half in the gender and case of `features`, as μισή; any other fraction as the neuter numerator and the
        name of `fraction_names`, as "ένα τρίτο" and "δύο τρίτα"."""
        numerator, denominator = str(int(numerator)), str(int(denominator))
        if denominator == "2":
            gender = (features.gender or N).value
            return request.data["half"][gender][features.case or NOMINATIVE]
        singular, plural = request.data["fraction_names"][denominator]
        count = self.cardinal(numerator, Features(gender=N, case=NOMINATIVE), request)
        return f"{count} {singular if numerator == '1' else plural}"


SPELLER = GreekSpeller()

Reading = frozenset[tuple[str, str]]
"""The (gender, case) pairs that a word may have."""


@lru_cache(maxsize=1)
def _word_list() -> dict:
    path = files("text2spoken") / "data" / "wiktionary" / "el_nouns.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _readings(table: dict) -> dict[str, Reading]:
    """Each form with its readings, and each form of more than one vowel group also with no accent, as text in
    capitals writes it; a form with no accent of its own keeps its readings."""
    found: dict[str, set[tuple[str, str]]] = {}
    for gender, by_case in table.items():
        for case, forms in by_case.items():
            for form in forms:
                found.setdefault(form, set()).add((gender, case))
    bare: dict[str, set[tuple[str, str]]] = {}
    for form, pairs in found.items():
        key = form.translate(NO_TONOS)
        if key not in found and len(VOWELS.findall(key)) > 1:
            bare.setdefault(key, set()).update(pairs)
    return {form: frozenset(pairs) for form, pairs in (bare | found).items()}


@lru_cache(maxsize=1)
def noun_readings() -> dict[str, Reading]:
    """The gender and the case of each noun form of `data/wiktionary/el_nouns.json`."""
    return _readings(_word_list()["nouns"])


@lru_cache(maxsize=1)
def adjective_readings() -> dict[str, Reading]:
    """The gender and the case of each adjective form of `data/wiktionary/el_nouns.json`."""
    return _readings(_word_list()["adjectives"])


def phrase_after(after: Sequence[str], data: FrozenMap, singular: bool) -> tuple[Reading | None, bool]:
    """The genders and cases that the words after a number give, and whether a month name follows it. The walk skips
    a word of `number_links` with the number after it, a word of `walk_adverbs`, and up to `ADJECTIVE_WALK`
    adjectives; a noun form ends it, unless it is also an adjective that agrees with the noun or adjective after it.
    Unless the number is `singular`, a genitive reading counts only in a form in -ων."""
    nouns, adjectives = noun_readings(), adjective_readings()
    words = [word.lower() for word in after]
    found: Reading | None = None
    walked = 0
    index = 0
    while index < len(words):
        word = words[index]
        if word in data["month_names"]:
            return frozenset({(FEMININE, NOMINATIVE)}), True
        if any(len(phrase) <= len(words) - index
               and all(w == p or (p == "#" and NUMBER.fullmatch(w)) for w, p in zip(words[index:], phrase))
               for phrase in data["hour_phrases"]):
            return frozenset({(FEMININE, NOMINATIVE)}), False
        if word in data["number_links"] and index + 1 < len(words) and NUMBER.fullmatch(words[index + 1]):
            index += 2
            continue
        if word in data["walk_adverbs"]:
            index += 1
            continue
        genitive = singular or word.translate(NO_TONOS).endswith("ων")
        noun = frozenset(p for p in nouns.get(word, ()) if genitive or p[1] != GENITIVE)
        adjective = frozenset(p for p in adjectives.get(word) or data["pronoun_adjectives"].get(word, ())
                              if genitive or p[1] != GENITIVE)
        following = words[index + 1] if index + 1 < len(words) else ""
        agrees = adjective & (nouns.get(following, frozenset()) | adjectives.get(following, frozenset()))
        if word in nouns and not (agrees and walked < ADJECTIVE_WALK):
            return noun or None, False
        if adjective and walked < ADJECTIVE_WALK:
            found = adjective if found is None else (found & adjective) or found
            walked += 1
            index += 1
            continue
        break
    return found, False


def choose(readings: Reading, default: GrammaticalGender) -> Features:
    """One gender and case of the open ones: the default gender when it is one of them, else the first of
    `GENDER_ORDER`, and the first case of `CASE_ORDER` that the gender has."""
    genders = {gender for gender, _ in readings}
    gender = default.value if default.value in genders else next(g.value for g in GENDER_ORDER if g.value in genders)
    case = next(c for c in CASE_ORDER if (gender, c) in readings)
    return Features(gender=GrammaticalGender(gender), case=case)


def number_features(context: SpanContext, singular: bool) -> tuple[Features, bool]:
    """The gender and case of a number, from the noun phrase around it, and whether it is a day of the month: a
    month name follows it, or a weekday name stands before it and no noun follows."""
    if context.hint is not None:
        return context.hint, False
    request = context.request
    default = request.params.default_gender.get(request.language.code) or request.language.default_gender
    data = request.data
    after, month = phrase_after(context.after, data, singular)
    before = context.before[-1].lower() if context.before else ""
    if after is None and before in data["weekdays"]:
        after, month = frozenset({(FEMININE, NOMINATIVE)}), True
    article = data["articles"].get(before)
    if article is not None:
        pairs = frozenset(map(tuple, article))
        genders = {gender for gender, _ in pairs}
        agreeing = frozenset(pair for pair in after or () if pair[0] in genders)
        after = ((after or frozenset()) & pairs) or agreeing or frozenset((gender, NOMINATIVE) for gender in genders)
    if after is None:
        return Features(gender=default, case=NOMINATIVE), month
    return choose(after, default), month


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal in the gender and case of its noun phrase; day 1 before a month name reads its ordinal."""
    request = context.request
    digits = span.fields["digits"]
    features, month = number_features(context, digits == "1")
    if month and digits == "1":
        words = SPELLER.ordinal(digits, features, request)
    else:
        words = SPELLER.cardinal(digits, features, request)
    return signed(words, span.fields["sign"], request)


KEPT_FIELDS = FrozenMap(dict.fromkeys(FIELDS[Form.CARDINAL], ""))


def kept(span: Span, name: str) -> Span:
    """`span` as a span that keeps its text and guards it from the cardinal reading (design section 6.1)."""
    return replace(span, form=Form.CARDINAL, fields=KEPT_FIELDS, recognizer=name, keep=True)


def speak_date(span: Span, context: SpanContext) -> str:
    """Day, month name and year: the day in the feminine of ημέρα, day 1 as its ordinal, the month in the genitive
    of `months`, and the year in the neuter."""
    request = context.request
    fields = span.fields
    day = str(fields["day"])
    if day == "1":
        day_words = SPELLER.ordinal(day, Features(gender=F), request)
    else:
        day_words = SPELLER.cardinal(day, Features(gender=F, case=NOMINATIVE), request)
    year = SPELLER.cardinal(str(fields["year"]), Features(gender=N, case=NOMINATIVE), request)
    return f"{day_words} {request.data['months'][fields['month'] - 1]} {year}"


def speak_percent(span: Span, context: SpanContext) -> str:
    """The amount in the neuter, the gender of τοις εκατό, then the word of the `percent` table."""
    request = context.request
    amount = span.fields["amount"]
    neuter = Features(gender=N, case=NOMINATIVE)
    words = (SPELLER.decimal(amount["integer"], amount["fraction"], neuter, request) if amount["fraction"]
             else SPELLER.cardinal(amount["integer"], neuter, request))
    return f"{signed(words, amount['sign'], request)} {request.data['percent']['word']}"


def speak_fraction(span: Span, context: SpanContext) -> str:
    """A fraction in the gender and case of the noun phrase around it, which only a half shows, and a whole number
    and a half as the one word of `halves`."""
    fields = span.fields
    features, _ = number_features(context, int(fields["whole"] or fields["numerator"]) == 1)
    if fields["whole"]:
        words = context.request.data["halves"][fields["whole"]][(features.gender or N).value]
        if (features.case or NOMINATIVE) not in words:
            raise DeclinedReading(f"no word for {fields['whole']} 1/2 in the {features.case}")
        return words[features.case or NOMINATIVE]
    return signed(SPELLER.fraction(fields["numerator"], fields["denominator"], features, context.request),
                  fields["sign"], context.request)


DASHES = ("-", "–", "−")


@dataclass(frozen=True)
class ReadPercent:
    """A number before a percent sign, with no sign or a minus. A per mille sign, a sign before the number and two
    percentages that a dash joins, as `10%-20%`, stay as written: the file has no range word. So
    does a percentage that a word character or a symbol touches from the left, as the fraction recognizer of the core
    decides, because its words would join that character."""
    name: str = "read_percent"
    form: Form = Form.PERCENT

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for span in SHARED["percent"].find(text, tokens, request):
            amount = span.fields["amount"]
            read = (isinstance(amount, FrozenMap) and amount["integer"]
                    and (not amount["sign"] or amount["sign"] in request.data["sign_words"])
                    and span.fields["sign_position"] == "after" and "%" in text[span.start:span.end]
                    and _free_before(text, span.start, request.data["symbols"])
                    and text[span.end:span.end + 1] not in DASHES
                    and not (span.start > 1 and text[span.start - 1] in DASHES and text[span.start - 2] in "%٪‰"))
            yield span if read else replace(span, keep=True)


@dataclass(frozen=True)
class ListedFraction:
    """A proper fraction whose denominator has a name: 2 and the keys of `fraction_names`, and a whole number of
    `halves` and 1/2. A fraction whose denominator is not 20 or 100 may be a date or a number with a year, so it
    reads only after a neuter article, before a genitive article or noun, or, for 1/2, before a noun. Any other
    fraction and mixed number stays as written."""
    name: str = "listed_fraction"
    form: Form = Form.FRACTION

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        spans = list(SHARED["fraction"].find(text, tokens, request))
        if not spans:
            return
        data, nouns = request.data, noun_readings()
        words, breaks = context_words(tokens), clause_breaks(text)
        for span in spans:
            fields = span.fields
            numerator, denominator = fields["numerator"], fields["denominator"]
            if fields["whole"]:
                read = fields["whole"] in data["halves"] and numerator == "1" and denominator == "2"
            else:
                before = clause_window(text, words, span.start, span.end, -1, limit=1, breaks=breaks)
                after = [word.lower() for word in clause_window(text, words, span.start, span.end, 1, limit=1,
                                                                breaks=breaks)]
                article = data["articles"].get(before[0].lower(), ()) if before else ()
                readings = (data["articles"].get(after[0]) or nouns.get(after[0], ())) if after else ()
                genitive = {case for _, case in readings} == {GENITIVE}
                read = ((denominator == "2" or denominator in data["fraction_names"])
                        and (denominator in ("20", "100") or any(gender == NEUTER for gender, _ in article) or genitive
                             or (denominator == "2" and after and after[0] in nouns))
                        and (not fields["sign"] or fields["sign"] in data["sign_words"]))
            yield span if read and not span.keep else replace(span, keep=True)


@dataclass(frozen=True)
class Kept:
    """The spans of a shape recognizer, kept as written, as for a language with no file. A span takes the form and
    the fields of the cardinal that it guards, so that it guards the digits also when only `CARDINAL` is on."""
    shape: Recognizer
    form: Form = Form.CARDINAL

    @property
    def name(self) -> str:
        return self.shape.name

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        return (kept(span, self.name) for span in self.shape.find(text, tokens, request))


@dataclass(frozen=True)
class SignedMoney:
    """A number with a sign next to a currency sign, as `-50 €` and `€ -50`, stays as written, as money does."""
    name: str = "signed_money"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        symbols = request.data["currencies"]["Sc"]["symbols"]
        for number in numbers_in(text, request):
            if not number.sign:
                continue
            for gap in GAPS:
                after = number.end + len(gap)
                before = number.start - len(gap) - 1
                if text.startswith(gap, number.end) and text[after:after + 1] in symbols:
                    yield kept(Span(number.start, after + 1, Form.CARDINAL, KEPT_FIELDS), self.name)
                    break
                if before >= 0 and text[before] in symbols and text[before + 1:number.start] == gap:
                    yield kept(Span(before, number.end, Form.CARDINAL, KEPT_FIELDS), self.name)
                    break


SHAPES = (SHARED["money"], SHARED["percent"], SHARED["measure"], SHARED["date_numeric"],
          OrdinalStop(bare_stop=False))

LANGUAGE = LanguageSpec(
    code="el",
    serves=(),
    cldr_aliases=(),
    varieties=(Variety("el-GR"),),
    data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["date_numeric"], ReadPercent(), ListedFraction(), *map(Kept, SHAPES),
                 SignedMoney(), SHARED["cardinal"]),
    verbalizers={Form.LEXICON: speak_lexicon, Form.CARDINAL: speak_cardinal, Form.DATE: speak_date,
                 Form.PERCENT: speak_percent, Form.FRACTION: speak_fraction},
    spellers={Form.CARDINAL: SPELLER, Form.FRACTION: SPELLER, Form.ORDINAL: SPELLER},
    genders=frozenset({M, F, N}),
    default_gender=N,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={"default_gender": frozenset({"masculine", "feminine", "neuter"})},
    not_applicable=frozenset(OPTIONS) - {"default_gender"},
)
