"""Portuguese: pt-PT, the default variety, and pt-BR. Every other `pt-*` tag reads the variety that
`linguatag.closest_lang` gives it, so `pt-AO` and `pt-MZ` read pt-PT.

Number words come from ovos-number-parser (design section 5.4), read with the variety tag. pt-PT follows the
official norm: the long scale (Priberam, "bilião": "Um milhão de milhões"), "dezanove" (Priberam, "dezanove":
"Grafia no Brasil: dezenove"), and lowercase month names (AO1990, Base XIX, 1.º b). pt-BR reads 14 as "quatorze"
and pt-PT as "catorze". Dicio, "Catorze ou quatorze": "As duas palavras existem na língua portuguesa e estão
corretas", and "Já no português falado em Portugal, a palavra quatorze está em desuso, sendo mais correto o uso
da palavra catorze."

A fraction reads `um meio`, `três quartos`, `três onze avos` (Priberam, "avo": "doze vinte e cinco avos = 12/25").

A number agrees with the noun that it counts. The hint of a frontend decides first, then the noun after the
number, then a determiner before it, then `default_gender`. `um`, `dois` and the hundreds from `duzentos` have a
feminine form; a scale word from `milhão` up is a masculine noun, so the words before it stay masculine (Priberam,
"duas": "uma mesa e duas cadeiras"; "uma": "Flexão feminina de um"; "milhão": "nome masculino").

The gender of a common noun comes from the noun lexicon of `tugalex`, behind the `pt` extra (design section 16).
Without the extra, the `noun_gender` table and the endings of `gender_suffixes` give it.

Unit words and the gender of each unit come from CLDR 49 (`cldr-units-full`, the `long` patterns of pt-PT and pt):
`5 µm` reads `cinco micrómetros` in pt-PT and `cinco micrômetros` in pt-BR, and `2 h` reads `duas horas`, because
CLDR gives `duration-hour` the feminine gender. A symbol that cannot be a plain word, such as `km/h`, `°C` or `µm`,
reads with no list. `unit_symbols` names the symbols made only of letters that read as units: the SI symbols `kg`,
`g`, `km`, `m`, `cm`, `mm`, `l` and `ml`, and `h`, `min` and `s` (Ciberdúvidas 14648: "o símbolo da unidade hora
é h e a abreviatura de minuto é min").

Currency names and currency symbols come from CLDR 49 (`cldr-numbers-full`, `currencies.json` of pt-PT and pt), and
a symbol with a currency sign reads with no list: `20 CHF` reads "vinte francos suíços" and `₹50` "cinquenta rupias
indianas". `currency_symbols` names the ISO 4217 codes that read. The `currencies` table replaces a CLDR name that
carries the country with the dictionary word. Priberam, "dólar": "Unidade monetária (símbolo: $) principal de vários
países, nomeadamente [...] dos Estados Unidos (código: USD)", "Plural: dólares"; "real": "Unidade monetária do
Brasil (código: BRL), divisível em centavos", "Plural: reais"; "libra esterlina": "Unidade monetária (símbolo: £) do
Reino Unido (código: GBP). = LIBRA"; "iene": "Unidade monetária do Japão (código: JPY)". The table also replaces a
CLDR adjective that does not agree with its noun: CLDR 49 writes "hryvnia ucraniano", and Priberam, "hryvnia": "nome
feminino [...] Unidade monetária da Ucrânia (código: UAH, símbolo: ₴)", so the name is "hryvnia ucraniana". CLDR pt
writes each currency name with a capital ("Euro", "Rupias indianas"), and a currency name is a common noun with a
small letter (Acordo Ortográfico de 1990, Base XIX, 1.º a: "A letra minúscula inicial é usada: a) Ordinariamente,
em todos os vocábulos da língua nos usos correntes"), so a currency name reads with a small first letter: "euros",
"rupias indianas". CLDR gives a currency no gender, so the noun rules give the gender of the first word of the name, as
they give the gender of a unit with no CLDR gender: `2 £` reads "duas libras" and `2 €` "dois euros".
`currency_noun_gender` names the currency nouns that end in "a" and are masculine: Priberam, "taka": "nome masculino
[...] Unidade monetária do Bangladeche (código: BDT)"; "córdoba": "nome masculino [...] Unidade monetária da
Nicarágua (código: NIO)". The table matches a word only as written. A word with a capital is a proper noun (AO1990,
Base XIX, 2.º: "A letra maiúscula inicial é usada: a) Nos antropónimos/antropônimos, reais ou fictícios [...] b) Nos
topónimos/topônimos, reais ou fictícios"), and Priberam gives the currency its name from one: "córdoba": "Origem:
[Fernández de] Córdoba, antropónimo". So `2 córdobas` reads "dois córdobas", and the city in `Visitei as 2
Córdobas.` takes its gender as another noun does: "duas". A currency amount looks up the name with its small first
letter, so pt-BR `2 C$` reads "dois córdobas nicaraguenses", though CLDR 49 pt writes "Córdoba nicaraguense". The
CLDR 49 pt annotations name `$` "dólar" and `¥` "iene", so `$` reads as the dollar and `¥` as the yen, where CLDR pt
shares the narrow `$` and `¥` between currencies. A `$` after the number is the escudo (see `Money`); CLDR 49 pt-PT
gives the escudo `$` as its decimal mark. The minor units: Priberam, "cêntimo": "Moeda divisionária que corresponde à
centésima parte do euro"; "dólar": "dividida em 100 cêntimos". The design keeps the cêntimo of the euro in pt-BR
(design section 7.1), because no source names the centavo of the euro.

A character that no other form claims reads by its CLDR 49 annotation name (`cldr-annotations-full` and
`cldr-annotations-derived-full`). A name of pt-PT wins over the pt name, so `©` reads "direitos de autor" in pt-PT
and "símbolo de copyright" in pt-BR, and `¶` reads "marca de parágrafo" in pt-PT and "pé de mosca" in pt-BR. pt-PT
takes a name that its locale does not give from pt, so `†` reads "obelisco" in both. `symbol_names` replaces the
CLDR name "secção" and "seção" of `§` with the name of the sign: Priberam, "parágrafo", sense 3: "Sinal desta divisão
(§)." So `Veja o § 5` reads "Veja o parágrafo cinco".

A run of capital letters reads by the `LETTERS` form (design section 4.6) when the caller turns the form on.
Correia and San Payo de Lemos, Inovação Lexical em Português (2005, p. 46), quoted in Ciberdúvidas answer 26164,
give the rule: "aquilo que distingue uma sigla de um acrónimo é apenas a sua concordância/não-concordância com a
estrutura silábica da língua em causa". The Gramática do Português (Fundação Calouste Gulbenkian, p. 222), quoted in
Ciberdúvidas answer 39064, gives the two readings: a sigla such as IRS has "a sua pronúncia ... feita letra a
letra", and acronyms such as IVA and ETAR "têm estrutura silábica, isto é, são pronunciados como uma palavra da
língua". A run that splits into syllables stays as written. Any other run reads each letter by its name in
`lang/_pt_electronic.py`.

The vowels are a, e, i, o and u, with the acute and the circumflex of AO1990, Bases VIII to XI, the grave of Base
XII, and the tilde of "ã" ("representa-se a nasalidade pelo til, se essa vogal é de timbre a", Base VI, 1) and of
"õ" ("ditongos representados por vogal com til e semivogal", Base VII, 3). A diphthong of Base VII is two vowel
letters, which already form two syllables of the rule, so the set holds single vowels only. An onset is a consonant
letter of Base I other than k, w and y, which "usam-se nos seguintes casos especiais" (Base I, 2), or ç and the
digraphs ch, lh and nh (Base I, Obs. 1), which open a syllable in "ca-cho, lha-no, ma-lha, ma-nha" (Base XX). An
onset of two consonants is a group of Base XX, 1, where "a primeira consoante é uma labial, uma velar, uma dental ou
uma labiodental e a segunda um l ou um r" (p, b; c, g; t, d; f, v). A coda is one consonant: "Syllables ending in a
consonant generally end in one of the single consonants /S/, /l/, /R/, /N/" (Cristófaro Silva 2024, p. 98, quoted
in Wikipedia, "Portuguese phonology", a secondary source). The letters are s, z and x for /S/ ("nas-cer",
"atroz-mente", "bissex-to", Base XX, 2), l, r, and m and n "com valor de nasalidade" (Base XX, 2). So IRS, with the
coda rs, reads letter by letter.

A consonant of `letter_free_consonants` can also stand before a vowel that the reader adds. Mendes, Oliveira and
Teixeira, "PLE: uma sigla para ler ou soletrar?", Cadernos de PLE, Universidade de Aveiro, DOI
10.34624/cadernosple.v0i0.36961, p. 6: "na língua os núcleos vazios são autorizados, podendo apresentar sílabas cuja
vogal não é realizada foneticamente". The set holds each consonant letter of Base I but h, which has no sound. Such a
consonant closes a syllable that another syllable follows, as Base XX, 2 divides "ab-dicar", "af-ta" and "rit-mo",
so OVNI reads ov-ni. One such consonant can also follow the last syllable. Viana et al. 1994 ("Sobre a pronúncia de
nomes próprios, siglas e acrónimos em Português Europeu"), quoted by Mendes, Oliveira and Teixeira on p. 14, read a
run in this way "quando CC são silabificáveis e a sigla apenas contém um núcleo vazio (ex. SERB, CELT), em posição
final absoluta". So PIB, CIAV, PALOP and TAP read as words. Ciberdúvidas answer 35524 names PALOP and TAP among the
runs that read: "Acaso tinha alguma lógica escrever-se com pontos acrónimos e siglas com sentido silábico, como APU,
FAOJ, FENPROF, FIFA, ONU, PALOP, TAP, UEFA, UNESCO ou VARIG?" The final consonant reads only in a run that holds a
consonant before a vowel (p. 13: "Para serem lidos, os acrónimos necessitam de compreender, pelo menos, um grupo
CV"), so IRS still reads letter by letter. It also reads only in a run with no h outside ch, lh and nh (p. 13: "a
presença da consoante «H», em qualquer posição"), so HIV reads letter by letter. A run that is a well-formed Roman
numeral, which `ROMAN` declines in its context, takes no free consonant (design section 4.6). So `XIV` reads letter
by letter where `ROMAN` does not read it, and `CIC`, which is no Roman numeral, reads as a word.

The words of a date, a clock time and a year come from `ovos_date_parser.spoken` (design section 5.4), read with the
variety tag: `1/5/2024` reads "primeiro de maio de dois mil e vinte e quatro", `14:30` "catorze e trinta" and
`17h30` "dezassete horas e trinta minutos". text2spoken recognises the written form and gives the parser its fields.
A field that the parser refuses (`UnsupportedForm` or `ValueError`) keeps the written text. The maintainer ruled
that spoken text says "meia-noite" for 00:00 and "meio-dia" for 12:00, and that the preposition before the time
agrees with the noun. So a whole hour written as a clock with no `h`, at 0 or 12, reads the 12-hour form of the
parser, and the article in the word before it agrees: "às 0:00" reads "à meia-noite", "das 12:00" "do meio-dia" and
"até às 12:00" "até ao meio-dia". The article "as" agrees in the same way after a preposition of
`time_article_prepositions`: "entre as 0:00" reads "entre a meia-noite" and "até as 12:00" "até o meio-dia".
Priberam labels each of entre, desde, após, até, para, sobre, contra and sem "preposição". Any other "as" before the
time stands for "às", the contraction of the preposition a and the article as (Ciberdúvidas 27390: "A(preposição) +
A(S) (artigo definido feminino singular ou plural): ÀS"). So that "as" stays as written, and the time reads the
hours that it agrees with: "Almoçamos as 12:00." reads "Almoçamos as doze horas.". A singular "à" or "da" before
12:00 takes the masculine too: "à 12:00" reads "ao meio-dia". `time_contractions` gives the words: Priberam,
"meia-noite": "nome feminino"; "meio-dia": "nome masculino"; "as": "feminino plural de o"; "ao": "Contracção da
preposição a e do artigo ou pronome o"; "do": "Contracção da preposição de e artigo ou pronome o"; "pelo":
"Aglutinação da preposição antiga per e do artigo ou pronome lo". The word keeps the case of its first letter only,
so "DAS 12:00" reads "Do meio-dia": an all-caps "DO" would be a two-letter word that the input did not write, which
the LETTERS form spells. A time that writes `h`, such as `0h` or `12h`, reads the hour unit as written, as the
ruling keeps it: "zero horas" in pt-PT and "zero hora" in pt-BR (Dicio, "Zero grau ou zero graus": "No Brasil, o
zero é encarado como singular: zero grau; zero real; zero hora. Em Portugal, o zero é encarado como plural: zero
graus; zero reais; zero horas.").

`letter_runs` holds three runs that the rule reads wrong. EUA reads letter by letter against the syllable rule:
Ciberdúvidas answer 9355 lists EUA among the "Siglas (siglóides)", with "letras em que é típico (mas não
obrigatório) serem soletradas independentemente". APPO and OCDE read letter by letter against the free consonant
inside the run: Mendes, Oliveira and Teixeira, p. 10: "A estrutura VCCV admite também algumas excepções à leitura:
OSCE, OCDE e APPO."

The titles: Priberam, "Sr.": "Abreviatura de senhor"; "Sr.ª": "Abreviatura de senhora"; "Dra.": "Abreviatura de
doutora"; "D.": "Abreviatura de dom e de dona". Dicio, "Abreviaturas: lista de abreviações": "senhora - Sr.ª, Sr.a ou
Sra.", "doutora - Dra. ou Dr.ª", "dona - D., d., D.ª ou Da.". The Manual de Comunicação of the Senado Federal writes
the titles before a name in lowercase: "prefira abreviá-las: sr. e sra. (use com inicial minúscula)". Dicio,
"Abreviação de senhora e senhor": "O ponto abreviativo deverá ser grafado no fim da abreviatura (como em Sr. e Sra.)
ou antes das letras em expoente (como em Sr.ª)", so `Drª.` and `Dª` are no titles.

pt-PT writes the space as the group mark of an amount: CLDR 49 pt-PT gives the group mark U+00A0 and the currency
format `#,##0.00 ¤`, so `250 000 €` reads "duzentos e cinquenta mil euros". pt-BR takes the full stop (CLDR 49 pt).
"""
from __future__ import annotations

import re
from bisect import bisect_right
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, replace

from text2spoken.core.color import speak_color
from text2spoken.core.currencies import currency_name, currency_table
from text2spoken.core.dates import is_valid
from text2spoken.core.language import LanguageSpec, Request, Variety, drop_affixes, plural_category
from text2spoken.core.letters import speak_letters
from text2spoken.core.numbers import SIGNS, Number, written_amount
from text2spoken.core.recognizers import Abbreviation as CoreAbbreviation
from text2spoken.core.recognizers import Money as CoreMoney
from text2spoken.core.recognizers import (PHONE_PLANS, SHARED, Telephone, TimeClock, amount_words, signed,
                                          speak_decimal, speak_expression, speak_fraction, speak_lexicon,
                                          speak_percent, speak_telephone)
from text2spoken.core.spans import Features, Span, SpanContext, Word, clause_breaks, clause_window, context_words
from text2spoken.core.spellers import OvosNumberSpeller, bounded_integer, spell_digits
from text2spoken.core.symbols import speak_emoji, speak_symbol
from text2spoken.core.times import clock_fields, day_hour
from text2spoken.core.tokens import Token, digit_script, fold_digits, is_bounded, is_word_char, one_digit_set
from text2spoken.core.units import unit_reading
from text2spoken.errors import DeclinedReading
from text2spoken.lang import _pt_electronic
from text2spoken.params import FrozenMap, Form, GrammaticalGender, freeze

MASCULINE, FEMININE = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE
MONTHS = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
          "novembro", "dezembro"]
_MONTH = "(" + "|".join(f"[{m[0]}{m[0].upper()}]{m[1:]}" for m in MONTHS) + ")"

DATA = freeze({
    "number_marks": {"Latn": [{"decimal": ",", "group": "."}, {"decimal": ".", "group": ","}]},
    "sign_words": {"-": "menos", "+": "mais"},
    "digit_words": ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"],
    "leads": {"#": "número", "-": ""},
    "range_word": "a",
    "range_marks": ["-", "–"],
    "clock_marks": [{"mark": ":", "seconds": False, "needs": "evidence"},
                    {"mark": "h", "seconds": False, "needs": "none", "closes_hour": True}],
    "time_words": ["às", "as", "à", "pelas", "das", "até", "desde"],
    "time_suffixes": ["h"],
    "time_units": {"h": {"one": "hora", "other": "horas"}},
    "time_contractions": {"às": {"0": "à", "12": "ao"}, "à": {"0": "à", "12": "ao"}, "as": {"0": "a", "12": "o"},
                          "das": {"0": "da", "12": "do"}, "da": {"0": "da", "12": "do"},
                          "pelas": {"0": "pela", "12": "pelo"}},
    "time_article_prepositions": {"as": ["entre", "desde", "após", "até", "para", "sobre", "contra", "sem"]},
    "range_articles": {"da": {"one": "à", "other": "às"}, "das": {"one": "à", "other": "às"}},
    "day_periods": {"am": ["a.m."], "pm": ["p.m."]},
    "dimension_marks": ["x", "×"],
    "dimension_word": "por",
    "operators": {"+": "mais", "−": "menos", "×": "vezes", "=": "igual a"},
    "months": MONTHS,
    "currencies": {
        "EUR": {"minor": {"one": "cêntimo", "other": "cêntimos"}},
        "BRL": {"one": "real", "other": "reais", "minor": {"one": "centavo", "other": "centavos"}},
        "USD": {"symbols": ["$"], "one": "dólar", "other": "dólares", "minor": {"one": "cêntimo", "other": "cêntimos"}},
        "GBP": {"one": "libra", "other": "libras"},
        "JPY": {"symbols": ["¥"], "one": "iene", "other": "ienes"},
        "UAH": {"one": "hryvnia ucraniana", "other": "hryvnias ucranianas"},
    },
    "currency_symbols": ["EUR", "USD", "BRL", "GBP", "JPY", "CHF"],
    "symbol_names": {"§": "parágrafo"},
    "scales": {"mil": "mil", "milhão": "milhão de", "milhões": "milhões de", "bilhão": "bilhão de",
               "bilhões": "bilhões de", "bilião": "bilião de", "biliões": "biliões de"},
    "symbols_before_only": ["$"],
    "percent": {"signs": ["%"], "position": "after", "word": "por cento"},
    "fraction_names": {"2": "meio", "3": "terço", "4": "quarto", "5": "quinto", "6": "sexto", "7": "sétimo",
                       "8": "oitavo", "9": "nono", "10": "décimo", "100": "centésimo"},
    "fraction_word": "avos",
    "unit_symbols": ["kg", "g", "km", "m", "cm", "mm", "l", "ml", "h", "min", "s"],
    "phone_words": ["telefone", "tel", "telemóvel", "telemóveis", "ligue", "ligar", "liga", "telefona", "fax",
                    "contacto", "contato", "celular"],
    "short_codes": ["112", "190", "192", "193", "199"],
    "list_links": ["e", "ou"],
    "phone_shapes": ["[(][1-9][0-9][)] 9?[0-9]{4}-[0-9]{4}"],
    "phone_unit_shapes": ["[29][0-9]{2} [0-9]{3} [0-9]{3}"],
    "phone_kept_shapes": ["[1-9][0-9]{0,2}(?: [0-9]{3})+"],
    "no_phone_shapes": ["(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})"],
    "function_words": ["o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na", "nos",
                       "nas", "para", "pelo", "pela", "por", "e", "ou", "com", "ao", "que", "agora", "já", "hoje"],
    "color_words": ["cor", "cores"],
    "colors": {"000000": "preto", "0000ff": "azul", "008000": "verde", "ff0000": "vermelho", "ffff00": "amarelo",
               "ffffff": "branco"},
    "titles": {"Sr.": "Senhor", "Sra.": "Senhora", "Sr.ª": "Senhora", "Dr.": "Doutor", "Dra.": "Doutora",
               "Dr.ª": "Doutora", "D.ª": "Dona", "Prof.": "Professor", "Eng.": "Engenheiro"},
    "abbreviations_any_case": ["sr.", "sra.", "dr.", "dra.", "prof.", "eng."],
    "honorific_before_name": {"D.": {"masculine": "Dom", "feminine": "Dona"}},
    "abbreviations": {"Av.": "Avenida", "av.": "avenida", "etc.": "et cetera"},
    "sentence_final": ["etc."],
    "number_abbreviations": {"n.º": "número", "N.º": "Número"},
    "ordinal_marks": {"º": "masculine", "ª": "feminine"},
    "regnal_titles": ["D", "D.ª", "Dom", "Dona", "rei", "rainha", "papa", "imperador", "imperatriz", "príncipe",
                      "princesa", "infante", "infanta"],
    "century_words": ["século", "séculos"],
    "determiners": {"as": "feminine", "das": "feminine", "nas": "feminine", "pelas": "feminine", "às": "feminine",
                    "à": "feminine", "os": "masculine", "dos": "masculine", "nos": "masculine", "pelos": "masculine"},
    "noun_gender": {
        "dia": "masculine", "dias": "masculine", "mapa": "masculine", "mapas": "masculine",
        "problema": "masculine", "problemas": "masculine", "sistema": "masculine", "sistemas": "masculine",
        "programa": "masculine", "programas": "masculine", "tema": "masculine", "temas": "masculine",
        "grama": "masculine", "gramas": "masculine", "quilograma": "masculine", "quilogramas": "masculine",
        "lei": "feminine", "leis": "feminine", "vez": "feminine", "vezes": "feminine", "noite": "feminine",
        "noites": "feminine", "tarde": "feminine", "tardes": "feminine", "parte": "feminine", "partes": "feminine",
        "mulher": "feminine", "mulheres": "feminine", "flor": "feminine", "flores": "feminine",
        "Isabel": "feminine", "Leonor": "feminine", "Beatriz": "feminine", "Inês": "feminine",
    },
    "currency_noun_gender": {"taka": "masculine", "takas": "masculine", "córdoba": "masculine",
                             "córdobas": "masculine"},
    "gender_suffixes": [["dade", "feminine"], ["dades", "feminine"], ["agem", "feminine"], ["agens", "feminine"],
                        ["ção", "feminine"], ["ções", "feminine"], ["a", "feminine"], ["as", "feminine"]],
    "symbols": {"%": "percent", "€": "money", "$": "money", "°": "measure", "×": "measure"},
    "letter_names": _pt_electronic.ELECTRONIC["letter_names"],
    "letter_vowels": [*"aeiouáéíóúâêôàãõ"],
    "letter_onsets": [*"bcçdfghjlmnpqrstvxz", "ch", "lh", "nh",
                      *(first + second for first in "pbcgtdfv" for second in "lr")],
    "letter_codas": [*"lrszxmn"],
    "letter_free_consonants": [*"bcçdfgjklmnpqrstvwxz"],
    "letter_runs": {"EUA": "letters", "APPO": "letters", "OCDE": "letters"},
    "patterns": {
        "date_named": "([0-9][0-9]?) de " + _MONTH + "(?: de ([0-9][0-9][0-9][0-9]))?",
        "expression": "[-−+]?[0-9]+(?: ?[+−×=] ?[-−+]*[0-9]+)+",
    },
})

DEFAULTS = {"date_order": "DMY", "clock": "24h", "minute_style": "number", "decimal_mark": ","}

VARIETIES = (
    Variety("pt-PT", freeze({"defaults": {**DEFAULTS, "scale": "long"},
                             "space_group_money": True,
                             "colors": {"808080": "cinzento"},
                             "letter_names": _pt_electronic.VARIETIES["pt-PT"]["letter_names"]})),
    Variety("pt-BR", freeze({
        "defaults": {**DEFAULTS, "scale": "short"},
        "letter_names": _pt_electronic.VARIETIES["pt-BR"]["letter_names"],
        "colors": {"808080": "cinza"},
        "currencies": {"USD": {"minor": {"one": "centavo", "other": "centavos"}}},
    })),
)

_SCALE_WORD = re.compile("[a-z]+(?:ão|ões)")


def at_variety(request: Request) -> Request:
    """The request with the tag of its variety, so that `pt-US`, which reads pt-BR, gets the Brazilian words and
    plural rules, and `pt-AO` gets those of pt-PT."""
    return request if request.tag == request.variety.tag else replace(request, tag=request.variety.tag)


class PortugueseSpeller:
    """ovos-number-parser, read with the variety tag and the gender of the noun."""

    def __init__(self):
        self.ovos = OvosNumberSpeller({MASCULINE: "masculine", FEMININE: "feminine"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        gender = FEMININE if features.gender is FEMININE else MASCULINE
        return self.ovos.cardinal(digits, Features(gender=gender), at_variety(request))

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        """From 2000 up, the first element is a cardinal: `2022.º` reads `dois milésimo vigésimo segundo`
        (Teyssier, Manual de Língua Portuguesa, p. 183, as the owner of ovos-number-parser reports it)."""
        gender = FEMININE if features.gender is FEMININE else MASCULINE
        return self.ovos.ordinal(digits, Features(gender=gender), at_variety(request))

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        return self.ovos.decimal(integer, fraction, Features(), at_variety(request))

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """`um meio`, `três quartos`, `um centésimo`, and the cardinal and `avos` for any other denominator:
        `dois onze avos` (Ciberdúvidas 11493, after Cunha and Cintra). A field with a leading zero, as in `01/02`,
        may be a day and a month, so the fraction stays as written."""
        if numerator.startswith("0") or denominator.startswith("0"):
            raise DeclinedReading("a fraction with a leading zero may be a day and a month")
        top = self.cardinal(numerator, Features(), request)
        name = request.data["fraction_names"].get(denominator)
        if name is None:
            return f"{top} {self.cardinal(denominator, Features(), request)} {request.data['fraction_word']}"
        return f"{top} {name if numerator == '1' else name + 's'}"


SPELLER = PortugueseSpeller()


def _cardinal(digits: str, request: Request, gender: GrammaticalGender | None = None) -> str:
    return SPELLER.cardinal(digits, Features(gender=gender), request)


def _plural(request: Request, written: str) -> str:
    return plural_category(at_variety(request), written)


def _counted(forms: FrozenMap, request: Request, written: str) -> str:
    """The word of `forms` for the plural category of the written number: `hora` or `horas`."""
    return forms.get(_plural(request, written), forms["other"])


_LEXICON_GENDERS = {"m": "masculine", "f": "feminine"}
_PARTITIVES = ("das", "dos")


def _lexicon_gender(word: str) -> str | None:
    """The gender code that `tugalex` gives a word read as a common noun: "m", "f", "mf" for a noun of two genders,
    or None when tugalex does not know the word or is not installed."""
    try:
        from tugalex import TugaLexicon
    except ImportError:
        return None
    return TugaLexicon.get_noun_gender(word)


def _listed_gender(word: str, data: FrozenMap) -> str | None:
    """The gender that the tables name: `currency_noun_gender` for the word as written, then `noun_gender` for the
    word or its lower case. A currency noun matches only in lower case, because the word with a capital is a proper
    noun, as the city Córdoba is."""
    return data["currency_noun_gender"].get(word) or data["noun_gender"].get(word) \
        or data["noun_gender"].get(word.lower())


def _gender_of(word: str, request: Request) -> GrammaticalGender | None:
    """The gender of a noun or a given name: the tables of `_listed_gender`, then the endings of `gender_suffixes`."""
    data = request.data
    if word in data["function_words"]:
        return None
    entry = _listed_gender(word, data)
    if entry is not None:
        return GrammaticalGender(entry)
    for suffix, gender in data["gender_suffixes"]:
        if word.lower().endswith(suffix):
            return GrammaticalGender(gender)
    return None


def agreement(context: SpanContext) -> GrammaticalGender:
    """The gender of a number (design section 5.6): the hint, the noun after the number, a determiner before it,
    then the `default_gender` of the params, then the language default.

    A written `mil` after the number is not the noun: `mil` has two genders (Priberam, "mil": "quantificador
    numeral cardinal de dois géneros"), so `2 mil pessoas` takes the gender of `pessoas`, as `2000 pessoas` does. A
    partitive `das` or `dos` right after the number gives the gender, as in `1 das casas`.

    The tables of `_listed_gender` name a noun first. When tugalex knows the word after the number, a determiner comes
    before the answer of tugalex, because tugalex reads any word as a noun ("The caller decides whether the word is
    a noun"), and that word can be an adjective with no noun, as in `as 2 melhores`. A noun of two genders, such as
    `artista` (Priberam: "nome de dois géneros"), takes its gender from the determiner or the default. Without
    tugalex, the endings of `gender_suffixes` come before the determiner."""
    if context.hint is not None and context.hint.gender is not None:
        return context.hint.gender
    request = context.request
    data = request.data
    after = list(context.after)
    if after and after[0].lower() == "mil":
        after = after[1:]
    noun = after[0] if after else ""
    if noun.lower() in _PARTITIVES:
        return GrammaticalGender(data["determiners"][noun.lower()])
    determiner = data["determiners"].get(context.before[-1].lower()) if context.before else None
    listed = _listed_gender(noun, data)
    code = _lexicon_gender(noun) if noun and listed is None and noun not in data["function_words"] else None
    if code is None:
        found = _gender_of(noun, request) if noun else None
        gender = found or (GrammaticalGender(determiner) if determiner else None)
    else:
        name = determiner or _LEXICON_GENDERS.get(code)
        gender = GrammaticalGender(name) if name else None
    return gender or request.params.default_gender.get(LANGUAGE.code) or LANGUAGE.default_gender


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal that agrees with its noun, with the sign and lead words of the data. A lead word of "" stands for
    a space. Digits with a leading zero, which only a lead admits, read one by one. A reading that ends in a scale
    word from `milhão` up takes `de` before the noun, because the scale word is a noun (Priberam, "milhão": "nome
    masculino"): `um milhão de pessoas`."""
    fields, request = span.fields, context.request
    digits = fields["digits"]
    if len(digits) > 1 and digits[0] == "0":
        words = spell_digits(digits, request)
    else:
        words = _cardinal(digits, request, agreement(context))
        if _SCALE_WORD.fullmatch(words.split()[-1]) and context.after \
                and context.after[0].lower() not in request.data["function_words"]:
            words += " de"
    words = signed(words, fields["sign"], request)
    if fields["lead"]:
        lead = request.data["leads"][fields["lead"]]
        words = f"{lead} {words}" if lead else f" {words}"
    return words


def speak_ordinal(span: Span, context: SpanContext) -> str:
    """`1.º` and `1.ª`: the indicator gives the gender."""
    marker = span.fields["marker"][-1]
    gender = GrammaticalGender(context.request.data["ordinal_marks"][marker])
    return SPELLER.ordinal(span.fields["digits"], Features(gender=gender), context.request)


def _range_word(before: Sequence[str], high: str, request: Request) -> str:
    """`às` or `à` after `das` or `da` names the end of a span of time with its article, as in `das cinco às seis
    horas`. With no article before the range, `a` stays (Ciberdúvidas 22241: "de cinco a seis horas")."""
    articles = request.data["range_articles"].get(before[-1].lower()) if before else None
    return _counted(articles, request, high) if articles is not None else request.data["range_word"]


def speak_range(span: Span, context: SpanContext) -> str:
    request = context.request
    gender = agreement(context)
    low, high = (_cardinal(span.fields[end], request, gender) for end in ("low", "high"))
    hours = request.data["time_units"]["h"].values()
    of_hours = bool(context.after) and context.after[0] in hours
    word = _range_word(context.before, span.fields["high"], request) if of_hours else request.data["range_word"]
    return f"{low} {word} {high}"


def speak_date(span: Span, context: SpanContext) -> str:
    from ovos_date_parser.spoken import spoken_date

    fields = span.fields
    try:
        return spoken_date(context.request.variety.tag, day=fields["day"], month=fields["month"], year=fields["year"])
    except ValueError as error:
        raise DeclinedReading(f"ovos-date-parser reads no date {fields['day']}/{fields['month']}: {error}") from error


def _day_point(fields: FrozenMap) -> int | None:
    """0 or 12 for a whole hour that reads "meia-noite" or "meio-dia": a clock with no `h` and no seconds. A `prefix`
    of None marks a time whose word of `time_contractions` stays as written, so its hour reads the 24-hour form that
    the plural article agrees with. A written `a.m.` or `p.m.` gives the hour of the 24-hour clock (Priberam, "a.m.":
    "antes do meio-dia"; "p.m.": "depois do meio-dia")."""
    hour = day_hour(fields["hour"], fields["period"])
    whole = fields["minute"] == 0 and not fields["second"] and not fields["suffix"] and fields["prefix"] is not None
    return hour if whole and hour in (0, 12) else None


def _contracted_word(prefix: str, hour: int, request: Request) -> str:
    """The word of `prefix` with the article of the noun at `hour`, and the white space after it as written. The
    word keeps the case of its first letter: `às` gives `à`, and `Às`, `À` and `ÀS` give `Ao` before "meio-dia"."""
    word = prefix.rstrip()
    if not word:
        return prefix
    article = request.data["time_contractions"][word.lower()][str(hour)]
    if word[0].isupper():
        article = article.capitalize()
    return article + prefix[len(word):]


def speak_time(span: Span, context: SpanContext) -> str:
    """`catorze e trinta` for `14:30`, `vinte e uma horas` for `21:00`, and `meia-noite` for `0:00`. A time that
    writes the hour symbol `h` reads its units, so `17h30` reads `dezassete horas e trinta minutos` (Ciberdúvidas
    14648; Ciberdúvidas 3267: "às onze horas e trinta minutos"), and its seconds (Ciberdúvidas 14586: "vinte horas,
    trinta minutos e vinte e quatro segundos"). The parser gives words with no comma, so `17 h 34 min 25 s` reads
    `dezassete horas trinta e quatro minutos e vinte e cinco segundos`. A written zero second is not read."""
    from ovos_date_parser.spoken import spoken_time

    fields = span.fields
    request = context.request
    tag = request.variety.tag
    hour, minute = day_hour(fields["hour"], fields["period"]), fields["minute"]
    try:
        if _day_point(fields) is not None:
            reading = spoken_time(tag, hour, clock="12h", period=True)
            return _contracted_word(fields["prefix"], hour, request) + reading
        if fields["suffix"]:
            return spoken_time(tag, hour, minute, fields["second"] or None, style="units")
        return spoken_time(tag, hour, minute)
    except ValueError as error:
        raise DeclinedReading(f"ovos-date-parser reads no time {hour}:{minute:02}: {error}") from error


def _currency(currency: FrozenMap, category: str) -> str:
    """The name of a currency in a plural category, with a small first letter. A number of the category `many`, a
    scale word from `milhão` up, takes `de` before the name, as it does before a unit: `um milhão de euros`."""
    name = currency_name(currency, category)
    name = name[:1].lower() + name[1:]
    return f"de {name}" if category == "many" and "many" not in currency else name


def speak_money(span: Span, context: SpanContext) -> str:
    """Two decimals are the minor unit, when the currency names one: `dois euros e cinquenta cêntimos`. A scale
    word that the text writes reads before the plural name: `dois milhões de reais`. The number agrees with the
    first word of the currency name, so `2 £` reads `duas libras`; before a scale word from `milhão` up it stays
    masculine, and before `mil` it agrees with the name: `duas mil libras`."""
    request = context.request
    fields = span.fields
    amount = FrozenMap({**fields["amount"], "sign": ""})
    currency = currency_table(request)[fields["currency"]]
    gender = _gender_of(_currency(currency, "one").split()[0], request)
    integer, fraction = amount["integer"] or "0", amount["fraction"]
    if fields["scale"]:
        scale = request.data["scales"][fields["scale"]]
        number = amount_words(amount, request, Features(gender=gender if fields["scale"] == "mil" else None))
        words = f"{number} {scale} {_currency(currency, 'other')}"
    elif len(fraction) == 2 and "minor" in currency:
        major = f"{_cardinal(integer, request, gender)} {_currency(currency, _plural(request, integer))}"
        cents = str(int(fraction))
        minor = f"{_cardinal(cents, request)} {currency['minor'][_plural(request, cents)]}"
        if int(fraction) == 0:
            words = major
        else:
            words = minor if bounded_integer(integer) == 0 else f"{major} e {minor}"
    else:
        category = _plural(request, written_amount(amount))
        words = f"{amount_words(amount, request, Features(gender=gender))} {_currency(currency, category)}"
    return signed(words, fields["amount"]["sign"], request)


def speak_measure(span: Span, context: SpanContext) -> str:
    """The number agrees with the gender of the unit in CLDR: `2 h` reads `duas horas`. CLDR gives no gender for
    some units, such as `area-square-inch`, and then the unit name is the noun that the number counts, so `2 in²`
    reads `duas polegadas quadradas`. A number of the category `many`, a scale word from `milhão` up, takes `de`
    before the unit, as in `um milhão de quilogramas`."""
    request = context.request
    amounts = span.fields["amount"]
    amounts = amounts if isinstance(amounts, tuple) else (amounts,)
    category = _plural(request, written_amount(amounts[-1]))
    pattern, gender = unit_reading(request, span.fields["unit"], category)
    if gender is None:
        gender = _gender_of(pattern.replace("{0}", "").split()[0], request)
    else:
        gender = GrammaticalGender(gender)
    if category == "many":
        pattern = pattern.replace("{0}", "{0} de", 1)
    link = request.data["range_word" if span.fields["relation"] == "range" else "dimension_word"]
    features = Features(gender=gender)
    return pattern.replace("{0}", f" {link} ".join(amount_words(a, request, features) for a in amounts))


def speak_abbreviation(span: Span, context: SpanContext) -> str:
    """A title keeps the case of the written form: `Dr.` reads `Doutor`, and `dr.` reads `doutor`. `D.` reads `Dom`
    or `Dona` by the gender of the name after it (Priberam, "D.": "Abreviatura de dom e de dona")."""
    data = context.request.data
    key = span.fields["key"]
    honorific = data["honorific_before_name"].get(key)
    if honorific is not None:
        name = context.after[0] if context.after else ""
        return honorific[str(_gender_of(name, context.request) or MASCULINE)]
    titles = {**data["titles"], **{k.lower(): v.lower() for k, v in data["titles"].items()
                                   if k.lower() in data["abbreviations_any_case"]}}
    for table in (titles, data["abbreviations"], data["number_abbreviations"]):
        if table.get(key) is not None:
            return table[key]
    raise LookupError(f"no abbreviation {key!r} for {context.request.tag}")


def speak_roman(span: Span, context: SpanContext) -> str:
    """Ordinal to ten and cardinal from eleven (Ciberdúvidas 14167, for kings and popes; 12370, for centuries).
    After a name, the ordinal agrees with the name and the reading takes a capital, as the name does."""
    request = context.request
    value = str(span.fields["value"])
    before = context.before[-1] if context.before else ""
    if before.lower() in request.data["century_words"]:
        gender, capital = MASCULINE, False
    else:
        gender, capital = _gender_of(before, request) or MASCULINE, True
    if span.fields["role"] == "ordinal":
        words = SPELLER.ordinal(value, Features(gender=gender), request)
    else:
        words = _cardinal(value, request)
    return words[0].upper() + words[1:] if capital else words


TELEPHONE = Telephone(reach=3, content_words=True, names_shaped=True, names_short_codes=True)
"""The shared telephone recognizer, where a phone word also names a run up to three words back, and a function word
does not count, as in `Ligue para o 112.` The window names a run with the shape of a phone number, and a short code
that ends its clause or that a function word follows. Two years that a dash joins have no phone shape
(`no_phone_shapes`), so `Os telemóveis de 2010-2020` reads a range."""


@dataclass(frozen=True)
class Clock(TimeClock):
    """The times of the core, and two Portuguese forms that it leaves. One is the unit symbols `h`, `min` and `s`
    around the digits, spaced or not: `17 h`, `17h30 min`, `17h30min`, `17:30 h` (Ciberdúvidas 14648: "17h30 min";
    "Considero perfeitamente aceitável 17:30 h") and `17 h 34 min 25 s` (Ciberdúvidas 3267). The other is two times
    that a range mark joins, as in `das 9h-17h` and `das 9:00-17:00`, where the second time takes the article of the
    first (Ciberdúvidas 22241: "das cinco às seis horas"). A chain of three times or more stays as written. A time
    that writes `h` keeps it in the `suffix` field, so it reads its units.

    Before "meia-noite" or "meio-dia", a word of `time_contractions` right before the time takes the article of that
    noun, when only white space stands between them. The span then starts at the word and holds the word and the
    white space in its `prefix` field, and the reading writes the contracted word: `às 0:00` reads `à meia-noite`.
    The time span that starts at the digits follows it, with a `prefix` of None. It reads when a lexicon entry
    claims the word first, and then the word stays as written and the time reads its 24-hour form: `às zero horas`.
    A word with two characters right before it that are no white space, as in `5(às 0:00`, gives only that span,
    because the span at the word would wait on the digit that the word touches (design section 4.2). So does a
    character between the word and the time, such as the `§` of `às § 0:00`, so that the span claims no character
    that another form reads. So does a word of `time_article_prepositions` with no preposition of its list right
    before it, as in `Almoçamos as 12:00`. In a range, the range word of the first time takes the article: `das
    9:00-12:00` reads `das nove horas ao meio-dia`."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        own = list(self._ranges(text, tokens, request))
        for span in self._symbols(text, request):
            if not any(span.start < other.end and other.start < span.end for other in own):
                own.append(span)
        for span in super().find(text, tokens, request):
            if not any(span.start < other.end and other.start < span.end for other in own):
                own.append(self._with_symbol(span, text))
        yield from self._contracted(text, tokens, sorted(own, key=lambda span: span.start), request)

    @staticmethod
    def _contracted(text: str, tokens: Sequence[Token], spans: list[Span], request: Request) -> list[Span]:
        contractions = request.data["time_contractions"]
        words = context_words(tokens)
        out: list[Span] = []
        for span in spans:
            hour = _day_point(span.fields)
            if hour is None:
                out.append(span)
                continue
            if out and out[-1].end == span.start and out[-1].trail:
                forms = contractions.get(out[-1].trail.strip().lower())
                if forms is not None:
                    out = [replace(first, trail=f" {forms[str(hour)]} ") if first.end == span.start else first
                           for first in out]
                out.append(span)
                continue
            index = bisect_right(words, span.start, key=lambda word: word.end)
            word = words[index - 1] if index else None
            if word is None or word.text.lower() not in contractions:
                out.append(span)
                continue
            edge = text[max(word.start - 2, 0):word.start]
            free = len(edge) < 2 or edge[0].isspace() or edge[1].isspace()
            needed = request.data["time_article_prepositions"].get(word.text.lower())
            previous = words[index - 2] if index > 1 else None
            governed = needed is None or (previous is not None and previous.text.lower() in needed
                                          and text[previous.end:word.start].isspace())
            if free and governed and text[word.end:span.start].isspace():
                out.append(replace(span, start=word.start,
                                   fields=FrozenMap({**span.fields, "prefix": text[word.start:span.start]})))
            out.append(replace(span, fields=FrozenMap({**span.fields, "prefix": None})))
        return out

    @staticmethod
    def _with_symbol(span: Span, text: str) -> Span:
        if span.fields["suffix"] or "h" not in text[span.start:span.end]:
            return span
        return replace(span, fields=FrozenMap({**span.fields, "suffix": "h"}))

    def _time(self, start: int, hour: str, minute: str | None, symbol: str, second: str | None = None) -> Span | None:
        fields = clock_fields(hour, minute or "00", second)
        if fields is None:
            return None
        return Span(start, start, Form.TIME, FrozenMap({"hour": fields[0], "minute": fields[1], "second": fields[2],
                                                        "period": None, "prefix": "", "suffix": symbol}),
                    recognizer=self.name)

    def _symbols(self, text: str, request: Request) -> Iterator[Span]:
        """`17 h`, `17h30 min`, `17h 30min`, `17 h 34 min 25 s` and `17:30 h`. Minutes after a space take `min`.
        The core reads `17h`, `17h30` and `17:30h`, so they are left to it."""
        hour, minute, second = (re.escape(unit) + "(?![^\\W\\d_])" for unit in ("h", "min", "s"))
        minutes = f"(?:([0-9][0-9])(?: ?{minute})?| ([0-9][0-9]) ?{minute})(?: ([0-9][0-9]) ?{second})?"
        pattern = re.compile(f"([0-9][0-9]?)(?: ?{hour}(?:{minutes})?|:([0-9][0-9]) {hour})")
        core_form = re.compile(f"[0-9][0-9]?{hour}(?:[0-9][0-9])?")
        for match in pattern.finditer(text):
            h, glued, spaced, seconds, colon = match.groups()
            if core_form.fullmatch(match.group()) or not is_bounded(text, *match.span()):
                continue
            if span := self._time(match.start(), h, glued or spaced or colon, "h", seconds):
                yield replace(span, end=match.end())

    def _ranges(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        data = request.data
        time = "([0-9][0-9]?)(?:h([0-9][0-9])?|:([0-9][0-9]))"
        marks = "|".join(map(re.escape, data["range_marks"]))
        words = context_words(tokens)
        time_words = frozenset(word.lower() for word in data["time_words"])
        pair = re.compile(f"{time}(?:{marks}){time}")
        for chain in re.finditer(f"{time}(?:(?:{marks}){time})+", text):
            if not is_bounded(text, *chain.span()):
                continue
            match = pair.fullmatch(text, *chain.span())
            if match is None:
                h, m, c = re.match(time, text[chain.start():]).groups()
                if first := self._time(chain.start(), h, m or c, "h" if c is None else ""):
                    yield replace(first, end=chain.end(), keep=True)
                continue
            h1, m1, c1, h2, m2, c2 = match.groups()
            before = clause_window(text, words, match.start(), match.end(), -1, limit=1)
            glued = c1 is None or c2 is None
            if not glued and not (before and before[0].lower() in time_words):
                continue
            first = self._time(match.start(), h1, m1 or c1, "h" if c1 is None else "")
            second_start = match.start(4)
            second = self._time(second_start, h2, m2 or c2, "h" if c2 is None else "")
            if first is None or second is None:
                continue
            word = _range_word(before, str(second.fields["hour"]), request)
            yield replace(first, end=second_start, trail=f" {word} ")
            yield replace(second, end=match.end())


@dataclass(frozen=True)
class Money(CoreMoney):
    """The money of the core. A `$` after the number is the cifrão of the escudo, which Portugal wrote to the right
    of the digits (Priberam, "cifrão": "antes do euro, indicava escudos, e escrevia-se à direita do algarismo"), so
    `100$` stays as written. A scale word may stand between the number and a symbol after it, so `180 mil €` reads
    "cento e oitenta mil euros" and `2 milhões €` "dois milhões de euros"."""
    scale_before_symbol: bool = True

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        before_only = request.data["symbols_before_only"]
        for span in super().find(text, tokens, request):
            symbol = span.fields["written_symbol"]
            written = text[span.start:span.end]
            first_digit = next(index for index, char in enumerate(written) if char.isdigit())
            yield replace(span, keep=True) if symbol in before_only and symbol not in written[:first_digit] else span


_SPACE_GROUPS = re.compile("[0-9]{1,3}(?:[ \u00a0\u202f][0-9]{3})+(?:,[0-9]{1,2})?")


@dataclass(frozen=True)
class SpacedMoney(Money):
    """`250 000 €`: a currency symbol next to digits in groups of three with a space between them, where the
    variety writes the space as its group mark. CLDR 49 pt-PT gives the no-break space as the group mark
    (`numbers.json`, `group`: U+00A0, currency format `#,##0.00 ¤`), and the SI Brochure, 9th edition, 5.4.4, divides
    the digits of a number into groups of three with a space. The claim order puts this recognizer before the
    telephone, which keeps a run of such groups as written. A run that the telephone reads, as in
    `+351 912 345 678 €`, is no amount."""
    name: str = "money_space_groups"

    def _amounts(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        """A sign before the digits reads with the amount, as before a symbol that comes first, and with the rule
        of a written number: no word character touches the sign. So `-1 500 €` and `−1 500 €` read "menos mil e
        quinhentos euros", and `+1 500 €` "mais mil e quinhentos euros"."""
        for span in super()._amounts(text, tokens, request):
            start = span.start
            if start and text[start].isdigit() and text[start - 1] in SIGNS \
                    and (start == 1 or not is_word_char(text[start - 2])):
                amount = FrozenMap({**span.fields["amount"], "sign": SIGNS[text[start - 1]]})
                span = replace(span, start=start - 1, fields=FrozenMap({**span.fields, "amount": amount}))
            yield span

    def numbers(self, text: str, tokens: Sequence[Token], request: Request) -> Sequence[Number]:
        if not request.data.get("space_group_money"):
            return ()
        phones = [span for span in TELEPHONE.find(text, tokens, request) if not span.keep]
        found = []
        for match in _SPACE_GROUPS.finditer(fold_digits(text)):
            start, end = match.span()
            if is_bounded(text, start, end) and one_digit_set(text[start:end]) \
                    and not any(phone.start < end and start < phone.end for phone in phones):
                integer, _, fraction = re.sub("[ \u00a0\u202f]", "", match.group()).partition(",")
                found.append(Number(start, end, "", integer, fraction or None, digit_script(text[start:end])))
        return found


@dataclass(frozen=True)
class Ordinal:
    """`1.º`, `2.ª`, `3º`: a whole number and the ordinal indicator, with or without the full stop."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        marks = "".join(request.data["ordinal_marks"])
        for match in re.finditer(f"[0-9]+([.]?[{marks}])", fold_digits(text)):
            start, end = match.span()
            if not is_bounded(text, start, end) or not one_digit_set(text[start:match.start(1)]):
                continue
            digits = match.group()[:match.start(1) - start]
            script = digit_script(text[start:match.start(1)])
            if len(digits) > 1 and digits[0] == "0":
                continue
            yield Span(start, end, Form.ORDINAL,
                       FrozenMap({"digits": digits, "marker": match.group(1), "prefix": "", "suffix": "",
                                  "script": script}), recognizer=self.name)


@dataclass(frozen=True)
class DateNamed:
    """`1 de março de 2024`, `15 de maio`: a day, `de`, a month name and perhaps `de` and a year."""
    name: str = "date_named"
    form: Form = Form.DATE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        months = [month.lower() for month in request.data["months"]]
        for match in re.finditer(request.data["patterns"]["date_named"], fold_digits(text)):
            start, end = match.span()
            if not is_bounded(text, start, end) or not one_digit_set(text[start:end]):
                continue
            day, month_name, year = match.groups()
            month = months.index(month_name.lower()) + 1
            year_value = int(year) if year is not None else None
            if not is_valid(year_value, month, int(day)):
                continue
            yield Span(start, end, Form.DATE,
                       FrozenMap({"year": year_value, "month": month, "day": int(day),
                                  "written_order": "DMY", "month_written": "name",
                                  "prefix": "", "suffix": ""}), recognizer=self.name)


def _regnal_title(text: str, word: Word, titles: frozenset[str]) -> bool:
    """Whether `word` is a regnal title, or ends one with a full stop inside, such as `D.ª`, whose last word is `ª`."""
    return word.text in titles or any(text.endswith(title, 0, word.end)
                                      and is_bounded(text, word.end - len(title), word.end)
                                      for title in titles if "." in title)


@dataclass(frozen=True)
class Roman:
    """A Roman numeral after a name or after `século`: `D. Maria II`, `Luís XIV`, `século XIX`.

    A numeral right after a title, as in `D. XIV` or `Dom XIV`, has no name and stays as written. After a name, a
    value from 1 to 30 reads when a regnal title comes right before the name, as in `D. João V`
    and `papa Pio X`, or when the numeral has two letters or more and a value from 11, which reads as a cardinal with
    no gender, as in `Luís XIV`. A short numeral after another capitalised word, as in `Malcolm X` or `Classe II`,
    stays as written."""
    name: str = "roman"
    form: Form = Form.ROMAN

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        from text2spoken.core.roman import value as roman_value

        data = request.data
        titles = frozenset(data["regnal_titles"])
        not_names = titles | {key.rstrip(".") for key in data["titles"]} | frozenset(data["titles"].values())
        centuries = frozenset(data["century_words"])
        words = context_words(tokens)
        breaks = clause_breaks(text)
        for match in re.finditer("[IVXLCDM]+", text):
            start, end = match.span()
            value = roman_value(match.group())
            if value is None or not is_bounded(text, start, end) or not text.endswith(" ", 0, start):
                continue
            before = clause_window(text, words, start, end, -1, limit=1, breaks=breaks)
            if not before:
                continue
            index = bisect_right(words, start, key=lambda word: word.end)
            if index >= 1 and words[index - 1].text in not_names:
                continue
            title = index >= 2 and _regnal_title(text, words[index - 2], titles) \
                and text[words[index - 2].end:words[index - 1].start] in (" ", ". ")
            if before[-1].lower() in centuries:
                reads = value <= 30
            elif before[-1][0].isupper() and value <= 30:
                reads = title or (len(match.group()) >= 2 and value >= 11)
            else:
                reads = False
            if reads:
                yield Span(start, end, Form.ROMAN,
                           FrozenMap({"value": value, "role": "ordinal" if value <= 10 else "cardinal",
                                      "suffix": ""}), recognizer=self.name)


@dataclass(frozen=True)
class Abbreviation(CoreAbbreviation):
    """The shared abbreviations, with `D.` before a name and the keys of `abbreviations_any_case`, which also read
    in lowercase, as in `dr. Silva`. A title whose full stop is the last character of the text or of its line also
    ends the sentence, so it keeps the full stop as the trail of the span: `Falei com a sra.` reads "Falei com a
    senhora." (Dicio, "Quando usar ponto final": "Quando o período termina com uma abreviatura, o ponto acumula duas
    funções: indicá-la e finalizar a frase")."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        titles = {*request.data["titles"], *request.data["abbreviations_any_case"]}
        for span in super().find(text, tokens, request):
            if span.fields["key"] in titles and text[span.end:].lstrip(" \t")[:1] in ("", "\n", "\r"):
                span = replace(span, trail=".")
            yield span

    def tables(self, data) -> tuple[tuple[str, Iterable[str], Callable[[str], bool]], ...]:
        return (("titles", data["titles"], str.isupper),
                ("honorific_before_name", data["honorific_before_name"], str.isupper),
                ("number_abbreviations", data["number_abbreviations"], str.isdigit),
                ("abbreviations_any_case", dict.fromkeys(data["abbreviations_any_case"]), lambda _: True),
                ("abbreviations", data["abbreviations"], lambda _: True))


LANGUAGE = LanguageSpec(
    code="pt",
    serves=(),
    cldr_aliases=(),
    varieties=VARIETIES,
    data=DATA,
    recognizers=(SHARED["lexicon"], SHARED["color"], DateNamed(), SHARED["date_numeric"], Clock(),
                 SpacedMoney(), TELEPHONE, Money(), SHARED["percent"], SHARED["measure"], SHARED["expression"],
                 SHARED["fraction"], SHARED["range"], Ordinal(), Roman(), Abbreviation(), SHARED["letters"],
                 SHARED["decimal"], SHARED["cardinal"], SHARED["emoji"], SHARED["symbol"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.COLOR: speak_color, Form.DATE: speak_date, Form.TIME: speak_time,
        Form.TELEPHONE: speak_telephone, Form.MONEY: speak_money, Form.PERCENT: speak_percent,
        Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression, Form.FRACTION: speak_fraction,
        Form.RANGE: speak_range,
        Form.ORDINAL: speak_ordinal, Form.ROMAN: speak_roman, Form.ABBREVIATION: speak_abbreviation,
        Form.DECIMAL: speak_decimal, Form.CARDINAL: speak_cardinal, Form.LETTERS: speak_letters,
        Form.SYMBOL: speak_symbol, Form.EMOJI: speak_emoji,
    },
    spellers={Form.CARDINAL: SPELLER, Form.ORDINAL: SPELLER, Form.DECIMAL: SPELLER, Form.FRACTION: SPELLER},
    attach=drop_affixes,  # the one suffix, the `h` of `14:30h`, is a word of the time reading
    genders=frozenset({MASCULINE, FEMININE}),
    default_gender=MASCULINE,
    animacies=frozenset(),
    noun_classes=frozenset(),
    numeral_systems=frozenset(),
    context_words=True,
    options={
        "date_order": frozenset({"DMY", "MDY", "YMD"}),
        "clock": frozenset({"24h"}),
        "minute_style": frozenset({"number"}),
        "decimal_mark": frozenset({",", "."}),
        "scale": frozenset({"long", "short"}),
        "default_gender": frozenset({"masculine", "feminine"}),
        "phone_regions": frozenset(PHONE_PLANS),
    },
    not_applicable=frozenset({"register"}),
)
