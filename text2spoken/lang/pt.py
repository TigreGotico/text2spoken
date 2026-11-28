"""Portuguese: pt-PT, the default variety, and pt-BR. Every other `pt-*` tag reads the variety that
`linguatag.closest_lang` gives it, so `pt-AO` and `pt-MZ` read pt-PT.

Number words come from numtag, read with the variety tag. pt-PT follows the
official norm: the long scale (Priberam, "bilião": "Um milhão de milhões"), "dezanove" (Priberam, "dezanove":
"Grafia no Brasil: dezenove"), and lowercase month names (AO1990, Base XIX, 1.º b). pt-BR reads 14 as "quatorze"
and pt-PT as "catorze". Dicio, "Catorze ou quatorze": "As duas palavras existem na língua portuguesa e estão
corretas", and "Já no português falado em Portugal, a palavra quatorze está em desuso, sendo mais correto o uso
da palavra catorze."

A fraction reads `um meio`, `três quartos`, `três onze avos` (Priberam, "avo": "doze vinte e cinco avos = 12/25").
A mixed number of a half reads the whole part, `e` and `meio`, as `2 1/2` reads `dois e meio`. The half agrees with
the noun that the expression leaves out (Ciberdúvidas 38523, "A expressão meio-dia e meia (II)": "Esta concordância
é determinada pelo elemento que está omitido", as in «pé-de-cabra e meio», «pé-de-cabra e meio pé-de-cabra»), so
with no noun the whole part and the half take the gender of `default_gender`. A counted noun stands between the
whole part and the half (Ciberdúvidas 38528, "Concordância com «página e meia»": "Falta uma página e meia para
acabar de escrever o livro."), so `2 1/2 maçãs` stays as written. No source gives the reading of a mixed number of
another fraction, so it stays as written.

A number agrees with the noun that it counts. The hint of a frontend decides first, then the noun after the
number, then a determiner before it, then `default_gender`. `um`, `dois` and the hundreds from `duzentos` have a
feminine form; a scale word from `milhão` up is a masculine noun, so the words before it stay masculine (Priberam,
"duas": "uma mesa e duas cadeiras"; "uma": "Flexão feminina de um"; "milhão": "nome masculino"; "trilhão": "nome
masculino"; "trilião": "nome masculino").

A number with no sign that starts a line, with optional spaces, one of `-`, `–`, `—`, `.` or `)` and a space after it,
as in `2 - Casa de campo`, numbers an item of a list. It counts no noun, so it reads in the masculine whatever word
follows the mark. Priberam, "dois": under "nome masculino de dois números", "O algarismo 2."; under
"quantificador numeral cardinal", "Um mais um.", the count with no noun. The Cunha and Cintra passage below feels "a
omissão da palavra
número" in a numbered item, and `número` is masculine. No source names the list marks; the rule rests on these
entries and on a corpus measure.

A number right after a noun of `label_nouns` or `roman_letter_nouns` names one item of a series, and it reads in the
masculine whatever word follows it, a verb as in `o capítulo 2 trata disso` included: `sala 2, porta 4` reads "sala
dois, porta quatro" and `o artigo 2 das disposições` "o artigo dois das disposições". Only a plural word after the
number, as `semanas` in `em casa 2 semanas`, is a counted noun and gives the number its gender: "duas semanas". A
number above one counts a plural noun, and a verb after the number is rarely a plural in `s`. No source gives the part
of speech of a word and tugalex reads any word as a noun, so a plural word that is no word of `function_words`,
`label_nouns` or `roman_letter_nouns` counts as a noun; the rule rests on a corpus measure. Priberam, "mas":
"conjunção adversativa", and "cada": "quantificador universal", join the words of `function_words`. So do the
demonstratives and their contractions with `em` and `de`, which are no noun that a number counts: Priberam, "nesta":
"Contracção da preposição em
e do pronome ou determinante esta."; "desta": "Contracção da preposição de e do pronome demonstrativo esta."; "naquela":
"Contracção da preposição em com o determinante ou pronome demonstrativo aquela." `ganhou 1 nesta terça-feira` reads
"ganhou um nesta terça-feira". So do `à`, `às`, `pelas` and `numa`: Priberam, "à": "Contracção da preposição a com o
artigo ou pronome a"; "às": "Contracção da preposição a com o artigo ou pronome as."; "pela", of which `pelas` is the
plural: "Contracção da preposição per e do artigo la."; "numa": "Contracção da preposição em e do artigo uma."
`domingo (2), às 16h` reads "domingo (dois), às dezasseis horas", and `em 2019 numa cela` reads "em dois mil e
dezanove numa cela". A plural contraction with `de` right after the number is a partitive, as `das` is, so `2
destas maçãs` reads "duas destas maçãs". Cunha and Cintra, Nova Gramática do Português Contemporâneo, p. 374, quoted in
Ciberdúvidas 33468: "Na enumeração de páginas e de folhas de um livro, assim como na de casas, apartamentos, quartos de
hotel, cabines de navio, poltronas de casas de diversões e equivalentes, empregam-se os CARDINAIS. Nestes casos sente-se
a omissão da palavra número: Página 3 (três) [...] Cabine 2 (dois)". The Gramática do Português (Fundação Calouste
Gulbenkian, 2013, p. 929), quoted in the same answer, names the class: such a cardinal occurs "em forma invariável à
direita do nome" and serves "para especificar um exemplar único do tipo denotado pelo nome". So `label_nouns` holds the
nouns of Cunha and Cintra and the nouns that name one numbered room, door, figure, table, line, row or seat; `fig` is
the abbreviation of "figura" in `Fig. 2`. The parts of a work of `roman_letter_nouns` take the same reading
(Ciberdúvidas 9067: "parte doze [mas: na página cinco; na página trinta e dois]"). After the preposition `a` and the
plural `páginas` or `folhas` of `plural_labels`, the number agrees with the noun: Bechara, Moderna Gramática Portuguesa,
37.ª ed., quoted in Ciberdúvidas 33527: "Com a preposição a, usa-se o substantivo no plural [...] "a páginas duas", "a
páginas vinte e uma" [...] com páginas, no plural, o cardinal se flexiona em gênero". So `a páginas 21 da obra` reads "a
páginas vinte e uma da obra".

A number before `da` and a word of `hour_periods` counts hours that the text leaves out, so it reads in the
feminine: `são 2 da tarde` reads "são duas da tarde". Senado Federal, Manual de Comunicação, "Hora": "diga "são duas
da tarde", e não "são 14 horas"", and "às dez da noite, e não às vinte e duas horas".

A number of four digits with a comma, a colon or a closing bracket right after it names a year, and so does a number
from 1000 to 2099 after a word of `year_words` and before a capitalised word, a word that is no plural or a mark, as
`1998` in `Em 1998 Lisboa recebeu a Expo` and `2003` in `o relatório de 2003 sublinha`. A number above one counts a
plural noun, so a lowercase word that does not end in `s` is no noun that the year counts. Priberam, "desde":
"preposição 1. A começar de; a contar de; a datar de."; "até": "preposição 1. Indica limite ou termo espacial, temporal
ou quantitativo"; "em": "preposição 2. Usa-se para indicar tempo". No source gives
the list of `year_words` or the bound of 2099; they rest on a corpus measure. The word after the year is no noun that
it counts, so a year reads in the masculine: `Braga 2012: Capital Europeia` reads "Braga dois mil e
doze: Capital Europeia", and `(2014) capital nacional` "(dois mil e catorze) capital nacional". A semicolon ends the
clause, so the word after it gives no number its gender. A year reads as a cardinal: Ciberdúvidas 32700
(https://ciberduvidas.iscte-iul.pt/consultorio/perguntas/numerais-em-datas/32700), after Cunha and Cintra, Nova
Gramática do Português Contemporâneo, p. 374: "Também na indicação dos anos e das horas se empregam os cardinais." The
cardinal of a year is masculine: Ciberdúvidas 10879
(https://ciberduvidas.iscte-iul.pt/consultorio/perguntas/como-se-designam-os-artigos-nas-leis-e-os-seculos/10879): "o
século vinte e um vai de dois mil e um a dois mil e cem". The year names the noun "ano": Ciberdúvidas 33377
(https://ciberduvidas.iscte-iul.pt/consultorio/perguntas/ano-de-2015/33377): "sendo alternativa a «o ano 2015»";
Priberam, "ano": "nome masculino".

A number alone between `[` and `]` marks a note or a reference, as in `intervenção.[22] Gente`. It counts no noun, so
it reads in the masculine whatever word follows the bracket (Priberam, "dois": "nome masculino de dois números", "O
algarismo 2."). No source names the brackets; the rule rests on a corpus measure.

`outro`, `outra`, `outros` and `outras` before a number agree with the noun that the number counts, as `as` does
(Priberam, "outras": "A forma outras é [ feminino plural de outro ]"; "outro": "determinante e pronome indefinido";
"outros": "pronome indefinido masculino plural"), so `outras 2 ficaram` reads "outras duas ficaram".

A number before `mil e` and a second number counts the noun that follows the second number, as `2 mil e 500 pessoas`
reads "duas mil e quinhentas pessoas". Cunha and Cintra, Nova Gramática do Português Contemporâneo, 7.ª ed., p. 384,
item 1: "Os NUMERAIS CARDINAIS um, dois, e as centenas a partir de duzentos variam em gênero"; p. 385, item 4: "Os
outros
CARDINAIS são invariáveis."

A number before a word of `number_links` and a second number reads in the masculine. Before `vezes`, it is a factor of a
product: `2 vezes 2` reads "dois vezes dois". When a noun that the number counts follows the second number, as `frases`
in `2 vezes 3 frases`, `vezes` is the feminine noun "vez" and the number agrees with it: "duas vezes três frases".
Priberam, "vez", sense 7: "Usa-se a seguir a um numeral e antes de outro numeral para indicar multiplicação (ex.: dois
vezes dois são quatro)". The dictionary of the Academia das Ciências de Lisboa, quoted in Ciberdúvidas 33489, gives the
same reading: "Mat. Designação de um operador de multiplicação [...] Um vezes três (1x3)". The same answer recommends
"duas vezes dois" after Botelho de Amaral (1958) and Sá Nogueira (1989); the Academy dictionary and Priberam are the
more reputable sources, and the masculine is also the reading of `2×2`. Before `vírgula`, it is the whole part of a
decimal written with the word: `(1) vírgula 5 m` reads "(um) vírgula cinco metros". Ciberdúvidas 25561 quotes "dois
vírgula cinco milhões de euros" and answers "Não se pode considerar errado". Digits with a leading zero after the number
and `vírgula` are the digits of the decimal part, and they read as the digits after a decimal mark: `0 vírgula 02` reads
"zero vírgula zero dois", as `0,02` does.

The comma is the decimal mark, and the full stop is the decimal mark of the English convention. Norma Portuguesa 9
(IPQ, 2006), quoted in Ciberdúvidas 12873: "Esses sinais são o ponto e a vírgula, sendo o primeiro empregado nos
países de língua inglesa, e o segundo, nos restantes." So a full stop with one, two, or four or more digits after
it, which no group of three explains, is a decimal mark, and `1.500` still reads as a number grouped with the full
stop. A number with the full stop reads as a decimal only when something shows the decimal: a sign before it, as
`-10.4`, or a percent sign, a currency, the symbol of a unit that `Measure` reads or the CLDR 49 name of such a unit
after it, as in `3.1416 graus`. With nothing of that, as in `o valor é 10.4`, the number stays as written, because in
running text it writes a version, a section, a reference or an engine size as often as an amount.

After a word of `point_version_words`, as `versão`, and after the name of a product or a standard, as `iOS 17.4` and
`Python 3.12`, the full stop parts the levels of a version and reads "ponto" (Priberam, "ponto", sense 7: "Sinal
gráfico (.)"): `versão 2.10` reads "versão dois ponto dez". No source states that reading of a version number. A
section number stays as written after a word of `point_section_words`, as `artigo 10.4` and `secção 3.2`: ISO
2145:1978, clause 4, says "When a division or subdivision number is spoken, full stops are not expressed.", and no
source gives the Portuguese words of the levels. An hour and its minutes may take the full
stop, so a number with a sign that may write one stays as written after a word of `time_words` and before a unit of
the hour, the minute or the second. So does a section number: one that opens a line before a capital, as
`2.1 Se cancelarmos`, and one that a full stop and a lowercase word close, as `10.10. licitação`.

Two numbers that `a`, `e` or `ou` join, as in `de 1 a 3 semanas` and `entre 1 e 2 semanas`, stay as written when the
noun after the second number gives the first number another reading. No source gives the gender of the first number
of such a pair, so the pair declines (design section 10).

The gender of a common noun comes from the noun lexicon of `tugalex`, behind the `pt` extra (design section 16).
Without the extra, the `noun_gender` table and the endings of `gender_suffixes` give it. A noun of two genders
(`mf` in tugalex) takes the determiner before the number, else the common sense that `two_gender_feminine` names:
Priberam, "caixa", sense 1: "Qualquer recipiente rígido usado para guardar ou transportar alguma coisa.", "nome
feminino"; sense 16, the employee: "Empregado que tem a caixa a seu cargo", "nome de dois géneros". So `Comprei 2
caixas.` reads "Comprei duas caixas.", and `os 2 caixas` still reads "os dois caixas".

Unit words and the gender of each unit come from CLDR 49 (`cldr-units-full`, the `long` patterns of pt-PT and pt):
`5 µm` reads `cinco micrómetros` in pt-PT and `cinco micrômetros` in pt-BR, and `2 h` reads `duas horas`, because CLDR
gives `duration-hour` the feminine gender. A symbol that cannot be a plain word, such as `km/h`, `°C` or `µm`, reads
with no list. `unit_symbols` names the symbols made only of letters that read as units: the SI symbols `kg`, `g`, `mg`,
`km`, `m`, `cm`, `mm`, `l`, `ml`, `cl` and `dl` of CLDR 49 pt-PT (`mass-milligram` `mg`, `volume-centiliter` `cl`,
`volume-deciliter` `dl`), and `h`, `min` and `s` (Ciberdúvidas 14648: "a abreviatura da unidade hora é h e a abreviatura
de minuto é min"). The litre symbol also has the capital form `L` (Priberam, "litro": "Unidade de medida de
capacidade (símbolo: l ou L)"), so `cL` and `dL` read as the CLDR units `cl` and `dl`, the case fallback of
`core/units.py`, as in `mg/dL`. DL 128/2010, note (a), gives both: "Os dois símbolos «l» e «L» podem ser usados para a unidade
litro". `decimal_unit_symbols` holds `L`, which reads as the litre only after a number with a decimal part and before
a space, a punctuation mark or the end of the text, so `1,8 L` reads "um vírgula oito litros". After a whole number a
bare `L` stays as written, because it also names a lot (`Q.30 L.6`), a model (`L-200`, `402 L`) or a lens (`f/4L`),
and a lot, model or lens number has no decimal part. A litre reading after any number was wrong in more than one
changed line in ten of natural text. `mL` stays as written, because CLDR also names `ML` (pt-PT) or `Ml` (pt-BR) the megalitre, and the case of
the prefix alone tells the two apart. A unit of `line_power_symbols` right after a number with `2` or `3` after it
writes the exponent on the line, as a text with no superscript does, so `80 m2` reads as `80 m²`: "oitenta metros
quadrados" (Priberam, "metro": "metro quadrado [...] Unidade de medida de superfície do Sistema Internacional (símbolo:
m²)"). `unjoined_symbols` holds `ML`, the CLDR symbol of the megalitre, because CLDR also names `mL` the millilitre, so
`ML` in capitals may be either unit, and `2ML` stays as written.

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
(design section 7.1), because no source names the centavo of the euro. An amount with one decimal reads the decimal
as tens of the minor unit: `2,5 €` reads "dois euros e cinquenta cêntimos" and pt-BR `R$ 2,5` "dois reais e
cinquenta centavos". Ciberdúvidas 25561, asked about "cinquenta vírgula três euros": "não é habitual referir a vírgula
numa representação por extenso dum numeral", and "Escreveria também: «o casaco custou cinquenta euros e trinta
cêntimos»".

A character that no other form claims reads by its CLDR 49 annotation name (`cldr-annotations-full` and
`cldr-annotations-derived-full`). A name of pt-PT wins over the pt name, so `©` reads "direitos de autor" in pt-PT
and "símbolo de copyright" in pt-BR, and `¶` reads "marca de parágrafo" in pt-PT and "pé de mosca" in pt-BR. pt-PT
takes a name that its locale does not give from pt, so `†` reads "obelisco" in both. `symbol_names` replaces the
CLDR name "secção" and "seção" of `§` with the name of the sign: Priberam, "parágrafo", sense 3: "Sinal desta divisão
(§)." So `Veja o § 5` reads "Veja o parágrafo cinco".

An e-mail or web address reads by the `ELECTRONIC` form (design section 4.5), with the tables of
`lang/_pt_electronic.py`, whose docstring quotes their sources.

A run of capital letters reads by the `LETTERS` form (design section 4.6) when the caller turns the form on.
Correia and San Payo de Lemos, Inovação Lexical em Português (2005, p. 46), quoted in Ciberdúvidas answer 26164,
give the rule: "aquilo que distingue uma sigla de um acrónimo é apenas a sua concordância/não-concordância com a
estrutura silábica da língua em causa". The Gramática do Português (Fundação Calouste Gulbenkian, p. 222), quoted in
Ciberdúvidas answer 39064, gives the two readings: a sigla such as IRS has "a sua pronúncia ... feita letra a
letra", and acronyms such as IVA and ETAR "têm estrutura silábica, isto é, são pronunciados como uma palavra da
língua". A run that splits into syllables stays as written. Any other run reads each letter by its name in
`lang/_pt_electronic.py`. A single capital letter after a noun of `letter_label_nouns` reads by its letter name too,
so with the `LETTERS` form on, `Tome vitamina C.` reads "Tome vitamina cê.": Dicio names "vitamina C" (see the
titles below).

The vowels are a, e, i, o and u, with the acute and the circumflex of AO1990, Bases VIII to XI, the grave of Base XII,
and the tilde of "ã" ("representa-se a nasalidade pelo til, se essa vogal é de timbre a", Base VI, 1) and of "õ"
("ditongos representados por vogal com til e semivogal", Base VII, 3). A diphthong of Base VII is two vowel letters,
which already form two syllables of the rule, so the set holds single vowels only. An onset is a consonant letter of
Base I other than k, w and y, which "usam-se nos seguintes casos especiais" (Base I, 2), or ç and the digraphs ch, lh
and nh (Base I, Obs. 1), which open a syllable in "ca-cho, lha-no, ma-lha, ma-nha" (Base XX). An onset of two consonants
is a group of Base XX, 1, where "a primeira consoante é uma labial, uma velar, uma dental ou uma labiodental e a segunda
um l ou um r" (p, b; c, g; t, d; f, v). A coda is one consonant: "Syllables ending in a consonant generally end in one
of the single consonants /S/, /l/, /R/, /N/" (Cristófaro Silva 2024, p. 98, quoted in Wikipedia, "Portuguese phonology",
a secondary source). The letters are s, z and x for /S/ ("nas-cer", "atroz-mente", "bissex-to", Base XX, 2), l, r, and m
and n "com valor de nasalidade" (Base XX, 2). n and s also close a syllable together: Base XX, 3 divides "As sucessões
de mais de duas consoantes ou de m ou n, com o valor de nasalidade, e duas ou mais consoantes" as in "in- cluir, ins-
crição, subs- crever, trans- gredir", so INSTITUTO reads ins-ti-tu-to. So IRS, with the coda rs, reads letter by letter.

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
12:00 takes the masculine too: "à 12:00" reads "ao meio-dia". Any time in the hour 1 reads "uma", which is singular, so
the word before it takes the singular article in the same way: "às 1:00" reads "à uma hora", "das 1:30" "da uma e
trinta" and "até às 1h" "até à uma hora". Ciberdúvidas 5175 writes "na frase «espero até à 1 hora»". João Luiz Ney,
"Curso de Português", Revista do Serviço Público, October 1952, p. 62, after the lessons of José Oiticica: "Escreve-se
porém: “à uma hora estarei lá (porque uma, aí, é adjetivo numeral; compare “às duas horas”, “às três”, “à meia
noite”)". `time_contractions` gives the words: Priberam,
"meia-noite": "nome feminino"; "meio-dia": "nome masculino"; "as": "feminino plural de o"; "ao": "Contracção da
preposição a e do artigo ou pronome o"; "do": "Contracção da preposição de e artigo ou pronome o"; "pelo":
"Aglutinação da preposição antiga per e do artigo ou pronome lo". The word keeps the case of its first letter only,
so "DAS 12:00" reads "Do meio-dia": an all-caps "DO" would be a two-letter word that the input did not write, which
the LETTERS form spells. A time that writes `h`, such as `0h` or `12h`, reads the hour unit as written, as the
ruling keeps it: "zero horas" in pt-PT and "zero hora" in pt-BR (Dicio, "Zero grau ou zero graus": "No Brasil, o
zero é encarado como singular: zero grau; zero real; zero hora. Em Portugal, o zero é encarado como plural: zero
graus; zero reais; zero horas.").

A clock with a colon reads after a word of `time_words`. `são`, the verb that tells the time, is one: Priberam, "ser",
sense 14: "Indica o momento, o dia, a estação, o ano, a época (ex.: já é noite; são 18h00)". In the "meio milhão de
frases" sentence set, each of the 148 clocks after `são` is a time, as mmf-286695 "São 17:30. Está na hora de ir buscar
o Pedro à escola." `são` is plural and agrees with the hours, so 12:00 after it reads the 24-hour form, as after `as`:
`São 12:00` reads "São doze horas". A clock 0:00 or 24:00 after `são` stays as written, because pt-BR reads the hour
zero in the singular, "zero hora" (Dicio, above), which does not agree with `são`. A clock after `são` with `h` or
`horas` after it stays as written, because the reading of a whole hour ends in "horas": `Já são 11:00 horas!`. So does a
clock with a mark between it and `são`, as in mmf-178704 "Os lotes proibidos são: 17:00, de geleia de uva", where the
clocks are lot numbers. A clock `24:00` is midnight, the end of the day: Priberam, "meia-noite": "Fim da vigésima quarta
hora do dia civil que acaba às 24h00 (ou 00h00, o mesmo momento em que começa a primeira hora do dia seguinte)". So it
reads as `0:00` does, with the ruling above: `Fecha às 24:00` reads "Fecha à meia-noite".

A clock right after a verb of `article_time_verbs`, an event at a time such as `começa` or `fecha`, reads with the
article `às`, or the word of `time_contractions` for "uma", "meia-noite" and "meio-dia": Ciberdúvidas 32865: «ocorre
o artigo definido, quando se pretende referir uma hora precisa ou uma hora marcada: «o comboio chegou às [= a + as]
quatro e cinquenta»». So `O jogo começa 20:45.` reads "O jogo começa às vinte e quarenta e cinco." and `Abre 1:00`
reads "Abre à uma hora". A verb of `singular_time_verbs` right before a clock takes the number of the hour:
Ciberdúvidas 37265, after Raposo et al., Gramática do Português, pp. 2482–2483: «o verbo ser concorda em número com o
constituinte que desempenha a função de predicativo do sujeito: (2) «São duas horas.» (3) «É uma da tarde.»». So
`É 16:30.` reads "São dezasseis e trinta.", and `É 1:30.` "É uma e trinta.". "meia-noite" and "meio-dia" are
singular, so `É 0:00` reads "É meia-noite". The verb keeps the case of its first letter. Any other time in the hour 0
after `é` stays as written, because pt-BR reads the hour zero in the singular (Dicio, above). The `é` that tells the
time has no subject, so a word right before it other than an adverb of `time_verb_adverbs` keeps the clock as
written: in `A proporção da tela é 16:10.` the clock is a ratio.

A time that `h`, `hora` or `horas` follows, with only spaces or tabs between, reads that word once. The word is the
unit that `h` stands for (Ciberdúvidas 14648: "17:30 h"; "escrita por extenso da unidade"), and the reading of a whole
hour or of a time with `h` already holds the unit once: "às onze horas e trinta minutos" (Ciberdúvidas, O nosso idioma,
article 3267). So the time claims the written word: `Fecha às 16:00 horas` reads "Fecha às dezasseis horas", and
`Fecha às 24:00 horas` reads "Fecha à meia-noite", because "meia-noite" and "meio-dia" name the hour with no unit
(Priberam, "meia-noite" and "meio-dia"). A singular `hora` is claimed only after "uma hora", the reading of `1:00`.
After any other reading it stays, as in `às 16:00 hora local`. A time with minutes and no `h`, as `10:30`, reads
"dez e trinta" with no unit, so a written `horas` after it stays: "dez e trinta horas". A line break between the time
and the word keeps both. No source rules on the doubled word itself; the rule follows from the readings cited above.

An hour and its minutes may also take a full stop. Ciberdúvidas 14648, "A grafia das horas": "Há quem prefira a
notação 17.30 h ou 17h 30´", and it warns that "17.30 h pode ser interpretado como 17,3 h". The page gives the full
stop only, so a comma between the hour and the minutes keeps the decimal reading. A time with the full stop reads only
right after a word that names the hours. `às`, `das` and `pelas` of `point_time_words` join a preposition and the
article of the hours, so the number after them names a time of day. `à` of `point_one_words` joins the preposition and
the singular article, which agrees with "uma" only: Ciberdúvidas 5175 writes "espero até à 1 hora", and Ney writes "à
uma hora estarei lá" against "às duas horas" (above). So `até à 1.30` reads and `quanto à 8.14` stays. The article
`as` reads after a preposition of `point_article_prepositions`: Dicio, Flávia Neves, "Crase antes de horas: quando
usar?", gives "A reunião foi marcada para as seis horas.", "Já está tudo preparado desde as nove horas.", "Ele apenas
poderá entrar após as 16h.", "O ônibus chegará entre as 15h e as 16h." and "O prazo de candidatura vai até as 18h de
hoje.", and Ciberdúvidas 22241 writes "desde as cinco até às seis horas". The `as` after `e` reads when a time of
this form ends right before `e`, as the second hour of `entre as 15h e as 16h` does. A bare `as`, `a`, `até` or
`entre` also comes before an amount, so the number after it stays. A time reads as the colon form does: `Chego às
10.30 horas.` reads "Chego às dez e trinta horas.", `às 9.30h` "às nove horas e trinta minutos", `às 10.30 da manhã`
"às dez e trinta da manhã", `até à 1.30` "até à uma e trinta" and `às 24.00` "à meia-noite". With no such word, the
number may write a decimal and stays as written (design section 10), as `Durou 1.30 h.` and `O índice fechou em
10.30.` do. A word or a sign after the number that shows an amount keeps the reading of the number without the rule:
a scale word, a currency code, sign or name, `%`, `por cento`, a word of `amount_words`, and a symbol or the first
word of a name of a CLDR unit of the variety, with `2` or `3` after it too (`m2`, `cm3`). This holds every CLDR unit
but the hour itself, so the units of duration count too: `às 2.30 t` and `das 2.30 anos` stay as written. A CLDR
symbol that is a word of `function_words` or `letter_words`, or a day period with no full stop, as the picometre
`pm`, does not count. `ºC` counts as `°C`, because `º` is the masculine ordinal indicator that a text writes for the
degree sign (Unicode: U+00BA MASCULINE ORDINAL INDICATOR, U+00B0 DEGREE SIGN). `amount_words` holds the abbreviations
and nouns that count an amount and that CLDR does not name: Priberam, "vez": "Usa-se a seguir a um numeral"; "valor":
"valores nome masculino plural 8. Grau do aproveitamento escolar de um estudante."; "pp.": "Abreviatura de
páginas"; Ipea, Manual Editorial, "Abreviaturas": "registrou 5 pontos percentuais (p.p.) a menos". So `das 3.20 kg`
reads "das três vírgula vinte quilogramas", and `das 10.30 euros`, `pelas 10.30 ha` and `perto das 8.37 milhões` stay
as written. `a.m.` and `p.m.` keep that reading too, because this rule does not read them.

A clock with a colon after `é` or another verb stays as written. `é` comes before a ratio as well as a time, as in `A
proporção do ecrã é 16:10`, and design section 4.2 of text2spoken says: "A word that also comes before a ratio or a
quantity, such as `to`, `by` or `about`, is no time word". No source gives the reading of a clock after `começa`.

`letter_runs` holds five runs that the rule reads wrong. EUA reads letter by letter against the syllable rule:
Ciberdúvidas answer 9355 lists EUA among the "Siglas (siglóides)", with "letras em que é típico (mas não
obrigatório) serem soletradas independentemente". APPO and OCDE read letter by letter against the free consonant
inside the run: Mendes, Oliveira and Teixeira, p. 10: "A estrutura VCCV admite também algumas excepções à leitura:
OSCE, OCDE e APPO." ANS and ONS read letter by letter against the coda ns: a measurement over "meio milhão de
frases" found the coda changes three runs, and two are initialisms, ANS (mmf-095745, "A ANS irá propor", the Agência
Nacional de Saúde Suplementar) and ONS (mmf-288035, "no ONS (Operador Nacional do Sistema Elétrico)").

A Roman numeral after its noun reads as an ordinal up to ten and as a cardinal from eleven. Ciberdúvidas 14167: "O
hábito é considerar a numeração romana ordinal até X (décimo/a), e cardinal a partir daí. Assim, o papa Bento XVI
será «dezasseis», tal como o único papa português, João XXI, é «vinte e um», tal como Luís XIV é «catorze», tal como
o século XV é o século «quinze»", and "João Paulo II (segundo), Paulo VI (sexto), Clemente X (décimo), D. Pedro IV
(quarto), D. João V (quinto), Eduardo VII (sétimo)". Ciberdúvidas 14284 gives the source: "na fala, até 10 (Celso
Cunha e Lindley Cintra) inclusive, usam-se os ordinais e depois os cardinais, sempre que o numeral vier depois do
substantivo." Ciberdúvidas 11716 gives the parts of a work, after the Nova Gramática do Português Contemporâneo:
"indica que se deve aplicar a regra a todas as partes em que se divide uma obra. Ora a regra, aplicada normalmente
para papas, soberanos e séculos, é: usar ordinais até dez inclusive [...] cardinais depois (ex.: artigo terceiro,
cláusula vinte e três)". Ciberdúvidas 9067: "(para papas, soberanos, séculos, partes duma obra) [...] (ex.: D.
Afonso III [terceiro]; o papa João XXIII [vinte e três]; capítulo quarto, parte doze". So a numeral reads after a
noun of `roman_nouns`: the parts of a work and of a law (capítulo, volume, tomo, artigo, cláusula, parte, livro,
título, secção, seção, canto, ato, acto, cena), and, by a ruling of the maintainer, the nouns that name a class, a
rank or a member of a series (classe, fase, grupo, nível, categoria) and the name "Guerra Mundial". The reading
takes the gender of the noun, which Priberam gives: "classe", "parte", "fase", "categoria", "cláusula", "secção",
"seção" and "guerra" and "cena" are "nome feminino", and "capítulo", "volume", "tomo", "artigo", "livro", "título",
"canto", "ato", "acto", "grupo" and "nível" are "nome masculino". So `Classe II` reads "Classe segunda" and `o
capítulo XV` "o capítulo quinze". A numeral of two letters or more, up to XXX, also reads after any other
capitalised word, as in `João Paulo II` and `Isabel II`, and right after a title and its full stop, with the gender
of the title, as in `D. XIV`, which reads "Dom Catorze". `roman_ordinal_limit` holds the last value that reads as
an ordinal, ten in both varieties, and `roman_noun_ordinal_limits` of a variety holds another limit after a noun. In
pt-BR the ordinal after `artigo` stops at nine. Two Brazilian works, both quoted in Migalhas, Gramatigalhas,
"Numeral", give ten for kings, popes, centuries and chapters. Luís A. P. Vitória, Dicionário de Dificuldades, Erros
e Definições de Português (1969), p. 174: "para indicar a ordem dos séculos, ou a ordem de sucessão de soberanos,
usa-se o ordinal até dez e o cardinal de onze em diante". Francisco da Silveira Bueno, Questões de Português (1957),
vol. II, p. 318: "de 1 a 10, usam-se os ordinais [...] Pio X (décimo), século VIII (oitavo), capítulo V (quinto)".
The same column quotes Celso Cunha for the articles of a law: "na numeração dos artigos de leis, decretos e
portarias, usa-se o ordinal até nove, e o cardinal de dez em diante". So `Pio X` reads "Pio Décimo" in both
varieties, and `artigo X` reads "artigo décimo" in pt-PT and "artigo dez" in pt-BR. Ciberdúvidas 9067 gives nine for
every noun in Brazil ("no Brasil até ao nono"), but cites no grammar.

A numeral of one letter reads after `século`, after a regnal title and a name, as in `D. João V`, and after a noun of
`roman_letter_nouns` when the letter is `I`, `V` or `X`, as in `o capítulo V`. These nouns take numbers and never
letters: the parts of a work and of a law (capítulo, volume, tomo, livro, parte, ato, acto, cena, título, artigo,
secção, seção), as Ciberdúvidas 11716 applies the rule "a todas as partes em que se divide uma obra". A group, a class,
a category, a level and a phase are labelled with letters as well as numbers: the measurement below found `Grupo C` and
`classe C`, and "meio milhão de frases" holds `No Grupo I, houve duas goleadas` (mmf-210324), a group of a series from
A. So `Grupo I`, `Fase I`, `classe A` and `vitamina E` stay as written, and `Grupo II` reads "Grupo segundo".

After a capitalised word that is no noun of `roman_nouns`, the value is at most 30, as after a regnal title, because an
acronym in capitals looks like a numeral. A measurement ran the recognizer, with no such limit, over the FLORES+ devtest
and the 500,000 sentences of "meio milhão de frases": of 1,050 runs, 25 are acronyms (CD, DC, DL, MC, MI, MV and MX),
and each has a value above 30, as `O DJ MIX` and `A Rádio MIX FM` do. Each run is judged in
`knowledge/wiki/audits/text2spoken-langs/letters-limits/evidence/roman-runs.tsv`. These rules read a numeral only when
spaces alone part it from the word before it. When a comma or another mark parts them, a numeral from 11 to 30 after a
capitalised word reads as a cardinal, as `XX` in `No século XIX, XX pessoas`, and a smaller one stays as written, as the
volume of a citation in `Port., VII`. In a code that a hyphen joins to digits, the cap leaves `CX` in `Mazda CX-5`, so
the digits read and the code reads "CX cinco", and a numeral up to 30, as in `Bell XV-15`, keeps the code as written,
because the digits wait on it.

`roman_words` holds the numerals that are also an acronym or a word. After a noun of `roman_nouns`, a numeral of
`roman_words` reads only after a noun of `roman_letter_nouns`, and only when no word in lowercase follows it, because
the word that follows a size or an acronym names the thing it qualifies: `capítulo XL,` reads "capítulo quarenta", and
`capítulo XL e XLI` and `categoria XL masculina` stay as written. A class, a group, a category, a level and a phase are
labelled with letters too, as above, so after such a noun a numeral of `roman_words` is a label as often as a number,
and it stays as written, as in `A Classe CL.` and `O grupo MC.`. A member of `roman_words` ends a list, as `MDC` in
`capítulo IV, MDC e MMC`. Any other numeral after a noun of `roman_nouns` reads with no cap. Each entry names a sentence
of the measurement, or a source: CC (Wiktionary, "CC", Portuguese: "init of cartão de cidadão"), CD (mmf-135478 "Qual CD
você quer escutar?"), CDI (mmf-493941 "O CDI varia"), CDL (mmf-065245 "O CDL alega"), CI (mmf-358222 "A
CI-Distribuição"), CL (mmf-091888 "O CL Financial"), CM (mmf-407703 "O CM aprovou"), CML (mmf-044814 "A CML mandou";
Wiktionary, "CML", Portuguese: "Câmara Municipal de Lisboa"), CV (mmf-110811 "O CV está organizado"), DC (mmf-089621
"Washington DC"), DL (mmf-128115 "O DL 66/2011"), MC (mmf-074274 "Racionais MC's"), MCI (mmf-102234 "O MCI quer"), MD
(mmf-199580 "dezenas de minidiscos (MD)"), MDC (mmf-093312 "Os MDC"), MI (mmf-376946 "Pode MI-me"; Priberam, "mi":
"Terceira nota musical"), MIX (Priberam, "mix": "nome masculino", "Mistura de coisas diversas"), ML (Wikipedia,
"Mercedes-Benz M-Class": "ML" badging, "e.g. ML 320"), MM (mmf-053612 "O MM."), MV (mmf-294652 "Porquê MV ( máquina
virtual)"), MX (mmf-028904 "Behringer MX 882") and XL (mmf-281415 "Os XL medem").

The ordinal after a capitalised word takes its gender from a list, never from the ending of the word: the regnal
title before the name, as `rainha` in `Rainha Elizabeth II`, then the common noun, as `região` in `Região III` and
`lei` in `Lei III`, which the `noun_gender` table or the word list of tugalex holds as a feminine noun, then the
given-name list of tugalex (`TugaLexicon.get_given_name_gender`, which holds regnal names, the Brazilian census
names that match a Wikidata given name, and the Wikidata given names marked Portuguese), else the masculine. So
`Elizabeth II` reads "Segunda", and `Nicholas II` and `Godzilla II` "Segundo". `noun_gender` comes before tugalex,
so it names a name that is also a common noun of another gender: "Lula", the name by which Luiz Inácio Lula da Silva
is known (Wikipedia, "Luiz Inácio Lula da Silva": "known mononymously as Lula"), so `Lula III` reads "Terceiro". The
word list of tugalex holds no plural, so `noun_gender` names the plurals of the feminine nouns of `roman_nouns`,
which Priberam gives as "nome feminino": `nas Seções IV e VI` reads "Seções Quarta". Without the extra, the gender
after a name comes from the regnal title and the `noun_gender` table alone, else the masculine.

A numeral right after a word of `letter_words`, such as a pronoun, does not read, because a numeral follows a noun
or a name: `Eu LI o livro` stays as written. In a clause in capitals, the word before the numeral does not decide
this, and the numeral itself does: it is a word of the clause only when `letter_words` holds it or tugalex knows it.
`letter_words` holds "vi", the verb form of "ver" (Priberam, "vi": "primeira pessoa singular do pretérito perfeito
do indicativo de ver"), and "li", of "ler" (Priberam, "li": "primeira pessoa singular do pretérito perfeito do
indicativo de ler"), so `EU VI` and `EU LI` stay as written with or without tugalex, and `Paulo VI` still reads.

A numeral between a singular demonstrative contracted with `em` or `de` (`nesta`, `deste`, `naquele`) and a common noun
of the same gender orders that noun, so it reads as an ordinal that agrees with the noun, also above
`roman_ordinal_limit`: `Nesta XV edição` reads "Nesta décima quinta edição" and `Deste III Congresso` "Deste Terceiro
Congresso", with a capital when the noun has one. Ciberdúvidas 11716, "A numeração ordinal e cardinal na prática
jurídica": "Se o numeral antecede o substantivo, é usual continuar a usar-se o ordinal, mesmo depois de dez".
Ciberdúvidas 28509, "Plurais com números romanos": "«II directriz», «III directriz», etc. (os símbolos são lidos:
«segunda», «terceira», etc.)". Migalhas, Gramatigalhas, "Numeral", after José de Nicola and Ernani Terra: "O numeral
anteposto ao substantivo deve ser lido como ordinal, concordando com esse substantivo." The ordinal reads only between a
singular demonstrative contracted with `em` or `de` and with a capital, as `Nesta`, `Deste` or `Daquele`, and a common
noun of the same gender that is no word of `function_words`, and only for a numeral of two letters or more up to C. The
contraction starts a prepositional phrase, so the word after the numeral is its noun. An article or a demonstrative
alone gives no such evidence, because `O XV segundo a imprensa` and `ESTE XV NUNCA PERDEU` are sentences about the XV de
Portugal, so `A II Guerra Mundial` stays as written. The gender of the noun comes from `noun_gender` or tugalex, which
guesses from the ending of a word that it does not list, so a verb form such as `joga` gets a gender too. That is one
more reason why an article alone, as in `O XV joga`, keeps the cardinal reading. A plural article, as in `As II partes`,
keeps it too, because the ordinal would be plural. After any other word of `function_words` in any case, which starts
many sentences in capitals, as the article in `O XV de Portugal`, a numeral reads only from 11 to 30, as a cardinal, so
`O XV` and `O XV DE PORTUGAL VENCEU` read "O Quinze". A function word is never the capitalised word before a numeral.

In a clause in capitals, a run of `letter_words` reads as a word, so `SAIA DA SALA` keeps `DA`. A clause in capitals
is the text between two marks of a clause, a full stop, a comma, a semicolon, a colon, a bracket, a quote or the
edge of the text, where every word with a letter is in capitals, and that holds two words or more. A word is a run
that reads as a word, so a code that reads letter by letter, such as `AGR` in `AO 1334 AGR`, does not count. The
capitals alone "a", "e", "o", "à" and "é" are words of `letter_words` too (Priberam: "a", "o" an "artigo definido",
"e" a "conjunção", "à" a "contracção", "é" the "terceira pessoa singular do presente do indicativo de ser"), so `O
AR` keeps `AR`. A text with words in lower case holds no clause in capitals, so in `A EM é uma doença`, `O IR dos
funcionários` and `A AR não aprovou`, the initialisms read letter by letter, as the article alone makes no clause.
Priberam gives each word its class: "da", "do" and "ao" are a "contracção" ("Contracção da preposição de e do artigo
ou pronome a"), "no" and "na" a "contração" or a "pronome pessoal", "os" the "masculino plural de o", "as" the
"feminino plural de o", "às" a "contracção", "um" an "artigo", "em" and "de" a "preposição", "se" a "conjunção" and
a "pronome pessoal", "ou" a "conjunção", and "eu", "tu", "me", "te" and "lhe" a "pronome pessoal". "vi" is the verb
form of "ver" (Priberam, "vi": "primeira pessoa singular do pretérito perfeito do indicativo de ver"), so `EU VI O
FILME` keeps `VI`. A run of two letters that tugalex knows as a word form of the variety also reads as a word in a
clause in capitals: the word list of `TugaLexicon.get_wordlist`, which tugalex takes from the Portal da Língua
Portuguesa, holds "ar", so `AR CONDICIONADO` keeps `AR`. When a part of the clause reads letter by letter, as `RTP`
in `A RTP NO AR`, or a number form reads it, the words of the clause are written in lower case, "A érre tê pê no
ar", so a second pass reads them as words. A run of three letters or more that tugalex knows reads as a word
anywhere, unless `letter_runs` lists it, so `a AIDS` stays as written. Two letters need the clause: in "meio milhão
de frases", 17 of the 18 two-letter runs that tugalex knows are initialisms (AL, IR, TI, DE, SE, EL, ME, AA, EM, FI,
UI, EH, TE, UM, LI, AZ, and the word OU), 335 of 336 times. Of the 371 longer runs that it knows, the syllable rule
already reads all but AIDS as words. Without the `pt` extra, only `letter_words` reads, and one log warning names
the missing extra (design section 10). Outside a clause in capitals, a run of two letters reads letter by letter, so
`Vi a TV` spells `TV`.

`ç` has a name for a run that reads letter by letter: Priberam, "cê": "cê cedilhado • Nome da letra Ç ou ç". A run
with `ç` that splits into syllables, such as `ÇAÇA`, stays as written, as any other word does.

The digits of a run read as a cardinal when the letters read as a word, as in `COVID19`, or when they are one to
three digits with no leading zero, as in `A25` ("á vinte e cinco") and `B52`. No usage source gives the reading of a
road name such as `A25`, so this reading is a ruling of the maintainer. Digits with a leading zero, and four digits
or more after letters that read letter by letter, read one by one.

The titles: Priberam, "Sr.": "Abreviatura de senhor"; "Sr.ª": "Abreviatura de senhora"; "Dra.": "Abreviatura de
doutora"; "D.": "Abreviatura de dom e de dona". Dicio, "Abreviaturas: lista de abreviações": "senhora - Sr.ª, Sr.a ou
Sra.", "doutora - Dra. ou Dr.ª", "dona - D., d., D.ª ou Da.". The Manual de Comunicação of the Senado Federal writes the
titles before a name in lowercase: "prefira abreviá-las: sr. e sra. (use com inicial minúscula)". Dicio, "Abreviação de
senhora e senhor": "O ponto abreviativo deverá ser grafado no fim da abreviatura (como em Sr. e Sra.) ou antes das
letras em expoente (como em Sr.ª)", so `Drª.` and `Dª` are no titles. After a noun of `letter_label_nouns`, `D.` is the
letter D and a full stop, so `a vitamina D. Boa noite.` stays as written: Priberam, "vitamina", names "vitamina A",
"vitamina B", "vitamina D" and "vitamina E", and Dicio, "vitamina C" (dicio.com.br, fetched 2026-11-18): "substantivo
feminino [Bioquímica] O ácido ascórbico (C6H8O6), molécula hidrossolúvel essencial ao funcionamento do corpo humano",
names the most common vitamin. A group and a class are labelled with letters, as the Roman numerals above show.

pt-PT writes the space as the group mark of an amount: CLDR 49 pt-PT gives the group mark U+00A0 and the currency format
`#,##0.00 ¤`, so `250 000 €` reads "duzentos e cinquenta mil euros". pt-BR takes the full stop (CLDR 49 pt) and the
space as a second group mark. The SI Brochure in its Portuguese edition (Inmetro and IPQ, 2021), 5.4.4, which replaces
the earlier translation in Brazil, says "os números com muitos algarismos podem ser divididos em grupos de três
algarismos, separados por um espaço", so pt-BR reads a spaced number by the same rules as pt-PT. Norma Portuguesa 9
(IPQ, 2006), quoted in Ciberdúvidas 12873, gives the same mark to any number: "Os grupos de três algarismos serão
separados por um espaço em branco", as in «Assistiram ao jogo 109 456 espectadores.» A run of spaced groups is also a
code: a tax number, a Multibanco entity or reference, a number of utente or a service line, as `509 876 543` and
`800 112 233` in the authored pt prompt pool, or a CPF written with spaces, as `123 456 789`. A cardinal of such a code
is a wrong reading, so a spaced number reads only with evidence of a quantity: a last group `000`, as in
`100 000 habitantes`, or a decimal part, as in `1 250 000,50`. In the "meio milhão de frases" set and the authored pool,
each of the 85 runs with a last group `000` is a count, as `130 000 anos` and `3 000 toneladas`. NP 9 also groups the
digits of the decimal part, as in `78 890,322 14`, and no source gives the spoken form of such a part, so that number
stays as written. A run with no such evidence, as `109 456 espectadores`, stays as written.
"""
from __future__ import annotations

import logging
import re
from bisect import bisect_left, bisect_right
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, replace
from functools import cache

from text2spoken.core import parsers
from text2spoken.core.color import speak_color
from text2spoken.core.currencies import currency_name, currency_table
from text2spoken.core.dates import is_valid
from text2spoken.core.electronic import speak_electronic
from text2spoken.core.language import LanguageSpec, Request, Variety, drop_affixes, plural_category
from text2spoken.core.letters import Letters, capital_clauses, speak_letters
from text2spoken.core.numbers import SIGNS, Number, number_marks, written_amount
from text2spoken.core.recognizers import Abbreviation as CoreAbbreviation
from text2spoken.core.recognizers import Cardinal as CoreCardinal
from text2spoken.core.recognizers import Decimal as CoreDecimal
from text2spoken.core.recognizers import Measure as CoreMeasure
from text2spoken.core.recognizers import Money as CoreMoney
from text2spoken.core.recognizers import (PHONE_PLANS, SHARED, Telephone, TimeClock, amount_words, digit_run_matches,
                                          numbers_in, signed, speak_decimal, speak_expression, speak_fraction,
                                          speak_lexicon, speak_percent, speak_telephone)
from text2spoken.core.spans import (Features, Span, SpanContext, Word, clause_breaks, clause_window,
                                    context_words)
from text2spoken.core.spellers import NumtagSpeller, bounded_integer, spell_digits
from text2spoken.core.symbols import speak_emoji, speak_symbol
from text2spoken.core.times import clock_fields, day_hour
from text2spoken.core.tokens import Token, digit_script, fold_digits, is_bounded, is_word_char, one_digit_set
from text2spoken.core.units import cldr_data, joined_table, unit_reading, unit_table
from text2spoken.errors import DeclinedReading
from text2spoken.lang import _pt_electronic
from text2spoken.params import FrozenMap, Form, GrammaticalGender, freeze

MASCULINE, FEMININE = GrammaticalGender.MASCULINE, GrammaticalGender.FEMININE
MONTHS = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
          "novembro", "dezembro"]
_MONTH = "(" + "|".join(f"[{m[0]}{m[0].upper()}]{m[1:]}" for m in MONTHS) + ")"

DATA = freeze({
    **_pt_electronic.ELECTRONIC,
    "number_marks": {"Latn": [{"decimal": ",.", "group": "."}, {"decimal": ".", "group": ","}]},
    "decimal_word": "vírgula",
    "point_word": "ponto",
    "point_version_words": ["versão", "atualização", "v"],
    "point_section_words": ["artigo", "art.", "cláusula", "secção", "seção", "capítulo", "cap.", "alínea", "ponto",
                            "figura", "fig.", "gráfico", "tabela", "quadro", "anexo", "item", "itens", "subitem",
                            "subitens", "n.º", "nº", "rcl"],
    "bible_books": ["gênesis", "génesis", "gn", "êxodo", "êx", "levítico", "lv", "números", "nm", "deuteronômio",
                    "deuteronómio", "dt", "josué", "js", "juízes", "jz", "rute", "rt", "samuel", "sm", "reis", "rs",
                    "crônicas", "crónicas", "cr", "esdras", "ed", "neemias", "ne", "ester", "et", "jó", "salmos",
                    "salmo", "sl", "provérbios", "pv", "eclesiastes", "ec", "cânticos", "ct", "isaías", "is",
                    "jeremias", "jr", "lamentações", "lm", "ezequiel", "ez", "daniel", "dn", "oseias", "os", "joel",
                    "jl", "amós", "am", "obadias", "ob", "jonas", "jn", "miqueias", "mq", "naum", "na", "habacuque",
                    "hc", "sofonias", "sf", "ageu", "ag", "zacarias", "zc", "malaquias", "ml", "mateus", "mt", "marcos",
                    "mc", "lucas", "lc", "joão", "jo", "atos", "at", "romanos", "rm", "coríntios", "co", "gálatas",
                    "gl", "efésios", "ef", "filipenses", "fp", "colossenses", "cl", "tessalonicenses", "ts",
                    "timóteo", "tm", "tito", "tt", "filemom", "fm", "hebreus", "hb", "tiago", "tg", "pedro", "pe",
                    "judas", "jd", "apocalipse", "ap", "tobias", "tb", "judite", "jt", "macabeus", "mc", "sabedoria",
                    "sb", "eclesiástico", "eclo", "baruc", "br"],
    "sign_words": {"-": "menos", "+": "mais"},
    "digit_words": ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"],
    "leads": {"#": "número", "-": ""},
    "range_word": "a",
    "range_marks": ["-", "–"],
    "clock_marks": [{"mark": ":", "seconds": False, "needs": "evidence"},
                    {"mark": "h", "seconds": False, "needs": "none", "closes_hour": True}],
    "time_words": ["às", "as", "à", "pelas", "das", "até", "desde", "são", "é", "começa", "começam", "termina",
                   "terminam", "abre", "fecha", "parte", "chega", "chegam", "sai"],
    "point_time_words": ["às", "das", "pelas"],
    "point_one_words": ["à"],
    "point_article_prepositions": {"as": ["até", "desde", "após", "para", "entre"]},
    "amount_words": ["vezes", "valores", "pp.", "p.p."],
    "plural_time_verbs": ["são"],
    "singular_time_verbs": {"é": "são"},
    "time_verb_adverbs": ["já", "agora", "ainda"],
    "article_time_verbs": ["começa", "começam", "termina", "terminam", "abre", "fecha", "parte", "chega", "chegam",
                           "sai"],
    "time_suffixes": ["h"],
    "time_units": {"h": {"one": "hora", "other": "horas"}},
    "time_contractions": {"às": {"0": "à", "1": "à", "12": "ao"}, "à": {"0": "à", "1": "à", "12": "ao"},
                          "as": {"0": "a", "1": "a", "12": "o"}, "das": {"0": "da", "1": "da", "12": "do"},
                          "da": {"0": "da", "1": "da", "12": "do"}, "pelas": {"0": "pela", "1": "pela", "12": "pelo"}},
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
               "bilhões": "bilhões de", "bilião": "bilião de", "biliões": "biliões de",
               "trilhão": "trilhão de", "trilhões": "trilhões de", "trilião": "trilião de",
               "triliões": "triliões de"},
    "symbols_before_only": ["$"],
    "percent": {"signs": ["%"], "position": "after", "word": "por cento"},
    "fraction_denominators": ("1000",),
    "label_nouns": ["página", "folha", "casa", "apartamento", "quarto", "cabine", "poltrona", "sala", "porta",
                    "figura", "fig", "tabela", "linha", "fila", "lugar", "número"],
    "plural_labels": {"a páginas": "feminine", "a folhas": "feminine"},
    "year_words": ["em", "desde", "até", "de"],
    "hour_periods": ["manhã", "tarde", "noite", "madrugada"],
    "number_links": ["vezes", "vírgula"],
    "letter_label_nouns": ["vitamina", "grupo", "classe"],
    "mixed_word": "e",
    "mixed_half": {"feminine": "meia", "other": "meio"},
    "unit_symbols": ["kg", "g", "mg", "km", "m", "cm", "mm", "l", "ml", "cl", "cL", "dl", "dL", "h", "min", "s"],
    "line_power_symbols": ["km", "m", "cm", "mm"],
    "unjoined_symbols": ["ML"],
    "decimal_unit_symbols": ["L"],
    "phone_words": ["telefone", "tel", "telemóvel", "telemóveis", "ligue", "ligar", "liga", "telefona", "fax",
                    "contacto", "contato", "celular"],
    "short_codes": ["112", "190", "192", "193", "199"],
    "list_links": ["e", "ou"],
    "phone_shapes": [],
    "phone_unit_shapes": ["[29][0-9]{2} [0-9]{3} [0-9]{3}"],
    "phone_kept_shapes": ["[1-9][0-9]{0,2}(?: [0-9]{3})+"],
    "no_phone_shapes": ["(?:1[0-9]{3}|20[0-9]{2})-(?:1[0-9]{3}|20[0-9]{2})"],
    "function_words": ["o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na", "nos",
                       "nas", "para", "pelo", "pela", "por", "e", "ou", "com", "ao", "que", "agora", "já", "hoje",
                       "mas", "cada", "este", "esta", "estes", "estas", "esse", "essa", "esses", "essas", "aquele",
                       "aquela", "aqueles", "aquelas", "neste", "nesta", "nestes", "nestas", "nesse", "nessa", "nesses",
                       "nessas", "naquele", "naquela", "naqueles", "naquelas", "deste", "desta", "desse", "dessa",
                       "daquele", "daquela", "à", "às", "pelas", "numa"],
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
    "roman_ordinal_limit": 10,
    "roman_nouns": {"classe": "feminine", "capítulo": "masculine", "volume": "masculine", "tomo": "masculine",
                    "artigo": "masculine", "cláusula": "feminine", "parte": "feminine", "livro": "masculine",
                    "título": "masculine", "secção": "feminine", "seção": "feminine", "canto": "masculine",
                    "ato": "masculine", "acto": "masculine", "cena": "feminine", "fase": "feminine",
                    "grupo": "masculine", "nível": "masculine", "categoria": "feminine", "guerra mundial": "feminine"},
    "roman_words": ["CC", "CD", "CDI", "CDL", "CI", "CL", "CM", "CML", "CV", "DC", "DL", "MC", "MCI", "MD", "MDC",
                    "MI", "MIX", "ML", "MM", "MV", "MX", "XL"],
    "roman_letter_nouns": ["capítulo", "volume", "tomo", "livro", "parte", "ato", "acto", "cena", "título", "artigo",
                           "secção", "seção", "canto", "cláusula"],
    "determiners": {"as": "feminine", "das": "feminine", "nas": "feminine", "pelas": "feminine", "às": "feminine",
                    "à": "feminine", "os": "masculine", "dos": "masculine", "nos": "masculine", "pelos": "masculine",
                    "destas": "feminine", "dessas": "feminine", "daquelas": "feminine", "destes": "masculine",
                    "desses": "masculine", "daqueles": "masculine", "outra": "feminine", "outras": "feminine",
                    "outro": "masculine", "outros": "masculine"},
    "noun_gender": {
        "dia": "masculine", "dias": "masculine", "mapa": "masculine", "mapas": "masculine",
        "problema": "masculine", "problemas": "masculine", "sistema": "masculine", "sistemas": "masculine",
        "programa": "masculine", "programas": "masculine", "tema": "masculine", "temas": "masculine",
        "grama": "masculine", "gramas": "masculine", "quilograma": "masculine", "quilogramas": "masculine",
        "lei": "feminine", "leis": "feminine", "vez": "feminine", "vezes": "feminine", "noite": "feminine",
        "noites": "feminine", "tarde": "feminine", "tardes": "feminine", "parte": "feminine", "partes": "feminine",
        "mulher": "feminine", "mulheres": "feminine", "flor": "feminine", "flores": "feminine",
        "frase": "feminine", "frases": "feminine",
        "Isabel": "feminine", "Leonor": "feminine", "Beatriz": "feminine", "Inês": "feminine", "Maria": "feminine",
        "Lula": "masculine",
        "rainha": "feminine", "imperatriz": "feminine", "princesa": "feminine", "infanta": "feminine",
        "dona": "feminine", "doutora": "feminine", "secções": "feminine", "seções": "feminine",
        "classes": "feminine", "fases": "feminine", "cenas": "feminine", "cláusulas": "feminine",
        "categorias": "feminine",
    },
    "currency_noun_gender": {"taka": "masculine", "takas": "masculine", "córdoba": "masculine",
                             "córdobas": "masculine"},
    "two_gender_feminine": ["caixa", "caixas"],
    "gender_suffixes": [["dade", "feminine"], ["dades", "feminine"], ["agem", "feminine"], ["agens", "feminine"],
                        ["ção", "feminine"], ["ções", "feminine"], ["a", "feminine"], ["as", "feminine"]],
    "symbols": {"%": "percent", "€": "money", "$": "money", "°": "measure", "×": "measure"},
    "letter_names": {**_pt_electronic.ELECTRONIC["letter_names"], "ç": "cê cedilhado"},
    "letter_words": ["A", "E", "O", "À", "É", "DA", "DO", "AO", "NO", "NA", "OS", "AS", "ÀS", "UM", "EM", "DE", "SE",
                     "OU", "EU", "TU", "ME", "TE", "LHE", "VI", "LI"],
    "letter_vowels": [*"aeiouáéíóúâêôàãõ"],
    "letter_onsets": [*"bcçdfghjlmnpqrstvxz", "ch", "lh", "nh",
                      *(first + second for first in "pbcgtdfv" for second in "lr")],
    "letter_codas": [*"lrszxmn", "ns"],
    "letter_free_consonants": [*"bcçdfgjklmnpqrstvwxz"],
    "letter_runs": {"EUA": "letters", "APPO": "letters", "OCDE": "letters", "ANS": "letters", "ONS": "letters"},
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
                             **_pt_electronic.VARIETIES["pt-PT"]})),
    Variety("pt-BR", freeze({
        "defaults": {**DEFAULTS, "scale": "short"},
        "space_group_money": True,
        **_pt_electronic.VARIETIES["pt-BR"],
        "roman_noun_ordinal_limits": {"artigo": 9},
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
    """numtag, read with the variety tag and the gender of the noun."""

    def __init__(self):
        self.numtag = NumtagSpeller({MASCULINE: "masculine", FEMININE: "feminine"})

    def cardinal(self, digits: str, features: Features, request: Request) -> str:
        gender = FEMININE if features.gender is FEMININE else MASCULINE
        return self.numtag.cardinal(digits, Features(gender=gender), at_variety(request))

    def ordinal(self, digits: str, features: Features, request: Request) -> str:
        """From 2000 up, the first element is a cardinal: `2022.º` reads `dois milésimo vigésimo segundo` (Teyssier,
        Manual de Língua Portuguesa, p. 183)."""
        gender = FEMININE if features.gender is FEMININE else MASCULINE
        return self.numtag.ordinal(digits, Features(gender=gender), at_variety(request))

    def decimal(self, integer: str, fraction: str, features: Features, request: Request) -> str:
        """The decimals as one number with their written zeros: `1,80` reads "um vírgula oitenta" and `1,05` "um
        vírgula zero cinco". A decimal part of zeros only reads one `zero`: `1,00` reads "um vírgula zero"."""
        if fraction.strip("0"):
            return self.numtag.decimal(integer, fraction, Features(), at_variety(request))
        return " ".join([self.cardinal(integer or "0", Features(), request), request.data["decimal_word"],
                         request.data["digit_words"][0]])

    def decimal_part(self, fraction: str, request: Request) -> str:
        """The digits after the decimal mark: each leading zero as `zero`, and the rest as a cardinal."""
        rest = fraction.lstrip("0")
        zeros = [request.data["digit_words"][0]] * (len(fraction) - len(rest))
        return " ".join([*zeros, self.cardinal(rest, Features(), request)] if rest else zeros)

    def fraction(self, numerator: str, denominator: str, features: Features, request: Request) -> str:
        """`um meio`, `três quartos`, `dois onze avos`, and the one-word ordinal where the denominator has one:
        `três vigésimos`, `sete milésimos` (Ciberdúvidas 3242, 11493, 35323). A field with a leading zero, as in
        `01/02`, may be a day and a month, so the fraction stays as written."""
        if numerator.startswith("0") or denominator.startswith("0"):
            raise DeclinedReading("a fraction with a leading zero may be a day and a month")
        return self.numtag.fraction(numerator, denominator, Features(), at_variety(request))


SPELLER = PortugueseSpeller()


def _cardinal(digits: str, request: Request, gender: GrammaticalGender | None = None) -> str:
    return SPELLER.cardinal(digits, Features(gender=gender), request)


def _plural(request: Request, written: str) -> str:
    return plural_category(at_variety(request), written)


def _counted(forms: FrozenMap, request: Request, written: str) -> str:
    """The word of `forms` for the plural category of the written number: `hora` or `horas`."""
    return forms.get(_plural(request, written), forms["other"])


_LEXICON_GENDERS = {"m": "masculine", "f": "feminine"}
_PARTITIVES = ("das", "dos", "destas", "destes", "dessas", "desses", "daquelas", "daqueles")


def _tugalex_installed() -> bool:
    """Whether tugalex imports. A package that is on the path and fails to import is no tugalex."""
    try:
        import tugalex  # noqa: F401
    except ImportError:
        return False
    return True


def _lexicon_gender(word: str) -> str | None:
    """The gender code that `tugalex` gives a word read as a common noun: "m", "f", "mf" for a noun of two genders,
    or None when tugalex does not know the word or is not installed."""
    if not _tugalex_installed():
        return None
    from tugalex import TugaLexicon
    return TugaLexicon.get_noun_gender(word)


@cache
def _tugalex_words(region: str) -> frozenset[str]:
    """The word forms that tugalex knows for a region."""
    from tugalex import TugaLexicon
    return frozenset(TugaLexicon().get_wordlist(region))


@cache
def _warn_no_extra() -> None:
    logging.getLogger("text2spoken").warning(
        "the pt extra is not installed, so a word in capitals reads as a word only when letter_words holds it; "
        "install text2spoken[pt]")


@cache
def _warn_no_noun_lexicon() -> None:
    logging.getLogger("text2spoken").warning(
        "the pt extra is not installed, so the gender of a noun comes from noun_gender and gender_suffixes alone, "
        "else the default gender; install text2spoken[pt]")


def _known_word(word: str, request: Request) -> bool:
    """Whether tugalex knows `word`, in lower case, as a word form of the variety (design section 4.6). tugalex names
    the pt-BR forms by the region `rjx` and the pt-PT forms by `lbx`. Without tugalex, it knows no word, and one
    warning names the extra."""
    if not _tugalex_installed():
        _warn_no_extra()
        return False
    return word in _tugalex_words("rjx" if request.variety.tag == "pt-BR" else "lbx")


def _listed_gender(word: str, data: FrozenMap) -> str | None:
    """The gender that the tables name: `currency_noun_gender` for the word as written, then `noun_gender` for the
    word or its lower case. A currency noun matches only in lower case, because the word with a capital is a proper
    noun, as the city Córdoba is."""
    return data["currency_noun_gender"].get(word) or data["noun_gender"].get(word) \
        or data["noun_gender"].get(word.lower())


def _gender_of(word: str, request: Request, endings: bool = True) -> GrammaticalGender | None:
    """The gender of a noun or a given name: the tables of `_listed_gender`, then, if `endings`, the endings of
    `gender_suffixes`."""
    data = request.data
    if word.lower() in data["function_words"]:
        return None
    entry = _listed_gender(word, data)
    if entry is not None:
        return GrammaticalGender(entry)
    if not endings:
        return None
    for suffix, gender in data["gender_suffixes"]:
        if word.lower().endswith(suffix):
            return GrammaticalGender(gender)
    return None


_UNCOUNTED = ("year", "list", "reference", "label")


def _label_role(context: SpanContext) -> str | None:
    """`label` for a number after a noun of `label_nouns` or `roman_letter_nouns`, which names an item. The number
    counts the noun after it only when that noun is a plural, as `semanas` in `em casa 2 semanas`, and not a word of
    `function_words`, `label_nouns` or `roman_letter_nouns`. A number after `a páginas` or `a folhas` agrees with that
    noun (the module docstring gives the sources)."""
    data = context.request.data
    before = [word.lower() for word in context.before]
    if before and before[-1] in (*data["label_nouns"], *data["roman_letter_nouns"]):
        following = [word.lower() for word in context.after]
        if not following or not following[0].endswith("s") or following[0] in data["function_words"] \
                or following[0] in (*data["label_nouns"], *data["roman_letter_nouns"]):
            return "label"
    return None


def _counted_gender(context: SpanContext) -> GrammaticalGender:
    """The gender of the noun that the number counts, or of the noun that the text leaves out.

    A number before `da tarde` and the other words of `hour_periods` counts the hours that the text leaves out. A
    number before a word of `number_links` and a second number reads in the masculine, unless a noun that the number
    counts follows the second number, and then `vezes` is the feminine noun that the number counts.

    A written `mil` after the number is not the noun: `mil` has two genders (Priberam, "mil": "quantificador
    numeral cardinal de dois géneros"), so `2 mil pessoas` takes the gender of `pessoas`, as `2000 pessoas` does. A
    partitive `das`, `dos` or a plural contraction of `de` and a demonstrative right after the number gives the
    gender, as in `1 das casas` and `2 destas maçãs`.

    The tables of `_listed_gender` name a noun first. When tugalex knows the word after the number, a determiner comes
    before the answer of tugalex, because tugalex reads any word as a noun ("The caller decides whether the word is
    a noun"), and that word can be an adjective with no noun, as in `as 2 melhores`. A noun of two genders, such as
    `artista` (Priberam: "nome de dois géneros"), takes its gender from the determiner or the default. tugalex runs
    its own ending rules before it gives no gender, so a word that it gives none, as `ainda`, takes the gender of the
    determiner or the default. Without tugalex, the endings of `gender_suffixes` come before the determiner."""
    request = context.request
    data = request.data
    before = [word.lower() for word in context.before]
    if " ".join(before[-2:]) in data["plural_labels"]:
        return GrammaticalGender(data["plural_labels"][" ".join(before[-2:])])
    following = [word.lower() for word in context.after[:2]]
    if len(following) == 2 and following[0] == "da" and following[1] in data["hour_periods"]:
        return FEMININE
    if len(following) == 2 and following[0] in data["number_links"] and following[1].isdigit():
        third = context.after[2].lower() if len(context.after) > 2 else ""
        if not third or _gender_of(third, request) is None:
            return MASCULINE
        # A noun that the number counts follows the second number, so `vezes` is the noun, not a factor.
    after = list(context.after)
    if after and after[0].lower() == "mil":
        after = after[1:]
    noun = after[0] if after else ""
    if noun.lower() in _PARTITIVES:
        return GrammaticalGender(data["determiners"][noun.lower()])
    determiner = data["determiners"].get(context.before[-1].lower()) if context.before else None
    listed = _listed_gender(noun, data)
    code = _lexicon_gender(noun) if noun and listed is None and noun.lower() not in data["function_words"] else None
    if code is None:
        if noun and listed is None and not _tugalex_installed():
            _warn_no_noun_lexicon()
        found = _gender_of(noun, request, endings=not _tugalex_installed()) if noun else None
        gender = found or (GrammaticalGender(determiner) if determiner else None)
    else:
        if code == "mf" and noun.lower() in data["two_gender_feminine"]:
            name = determiner or "feminine"
        else:
            name = determiner or _LEXICON_GENDERS.get(code)
        gender = GrammaticalGender(name) if name else None
    return gender or request.params.default_gender.get(LANGUAGE.code) or LANGUAGE.default_gender


def agreement(context: SpanContext, role: str | None = None) -> GrammaticalGender:
    """The gender of a number (design section 5.6): the hint, then the masculine of a number that counts no noun,
    then the noun that it counts. The `role` is `year` or `list` when `Cardinal.find` found one (the module docstring
    gives the sources), and a number after a label noun has the role `label`."""
    if context.hint is not None and context.hint.gender is not None:
        return context.hint.gender
    if role not in _UNCOUNTED:
        role = _label_role(context)
    return MASCULINE if role in _UNCOUNTED else _counted_gender(context)


def speak_cardinal(span: Span, context: SpanContext) -> str:
    """A cardinal that agrees with its noun, with the sign and lead words of the data. A lead word of "" stands for
    a space. Digits with a leading zero, which only a lead admits, read one by one. A reading that ends in a scale
    word from `milhão` up takes `de` before the noun, because the scale word is a noun (Priberam, "milhão": "nome
    masculino"): `um milhão de pessoas`."""
    fields, request = span.fields, context.request
    digits = fields["digits"]
    if len(digits) > 1 and digits[0] == "0":
        after_mark = context.before and context.before[-1].lower() == request.data["decimal_word"]
        words = SPELLER.decimal_part(digits, request) if after_mark else spell_digits(digits, request)
    else:
        role = request.memo.get(_ROLES, {}).get(span.start)
        counted = request.memo.get(_SCALED_NOUNS, {}).get(span.start)
        words = _cardinal(digits, request, agreement(replace(context, after=(counted,)) if counted else context, role))
        _check_pair(digits, context, role == "after_phone")
        if _SCALE_WORD.fullmatch(words.split()[-1]) and context.after \
                and context.after[0].lower() not in request.data["function_words"]:
            words += " de"
    words = signed(words, fields["sign"], request)
    if fields["lead"]:
        lead = request.data["leads"][fields["lead"]]
        words = f"{lead} {words}" if lead else f" {words}"
    return words


def _pair_digits(token: str, request: Request) -> str | None:
    """The digits of `token` when it is a number: all digits, or digits with the group mark of the variety between
    groups, as `10.000` and `400.000`. None when the token is no number. The group marks come from `number_marks`."""
    if token.isdigit():
        return token
    for _, _, group in number_marks(request.data, request.params.decimal_mark):
        if group and group in token and token.replace(group, "").isdigit():
            return token.replace(group, "")
    return None


def _first_of_pair_differs(digits: str, before: Sequence[str], after: Sequence[str], context: SpanContext) -> bool:
    """Whether the number `digits`, which `before` and `after` surround, is the first of a pair that a link word of
    `list_links` or the `range_word`, written as in the data, joins to a second number, as `1` in `de 1 a 3
    semanas`, and the noun after the second number gives it another reading. The far reading is computed only when a
    noun comes right after the second number: a word of `function_words`, a conjunction or a punctuation mark ends
    the pair, and then the pair does not decline."""
    request = context.request
    data = request.data
    if len(after) < 3 or _pair_digits(after[1], request) is None \
            or after[0] not in (*data["list_links"], data["range_word"]):
        return False
    if after[2].lower() in data["function_words"]:
        return False
    near = agreement(replace(context, before=tuple(before), after=tuple(after)))
    far = agreement(replace(context, before=(*before, digits, after[0]), after=tuple(after[2:])))
    return _cardinal(digits, context.request, near) != _cardinal(digits, context.request, far)


def _check_pair(digits: str, context: SpanContext, after_phone: bool = False) -> None:
    """Decline both numbers of a pair such as `de 1 a 3 semanas` or `entre 1 e 2 semanas` when the noun after the
    second number gives the first number another gender. No source gives the gender of the first number, so the
    pair stays as written. The second number declines too, so a second pass leaves the text unchanged. A number
    `after_phone` is no second number: the phone number before it reads digit by digit, so a second pass sees words
    there."""
    if context.hint is not None:
        return
    before, after = context.before, context.after
    first = _first_of_pair_differs(digits, before, after, context)
    if not first and not after_phone and len(before) > 1:
        second = _pair_digits(before[-2], context.request)
        if second is not None:
            first = _first_of_pair_differs(second, before[:-2], (before[-1], digits, *after), context)
    if first:
        raise DeclinedReading("the noun after the second number of the pair may give the first another gender")


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
    fields = span.fields
    try:
        return parsers.spoken_date(context.request.variety.tag, day=fields["day"], month=fields["month"],
                                   year=fields["year"])
    except ValueError as error:
        raise DeclinedReading(f"ovos-date-parser reads no date {fields['day']}/{fields['month']}: {error}") from error


def _day_point(fields: FrozenMap) -> int | None:
    """0 or 12 for a whole hour that reads "meia-noite" or "meio-dia": a clock with no `h` and no seconds. A `prefix`
    of None marks a time whose word before it stays as written and agrees with plural hours, a word of
    `time_contractions` or a verb of `plural_time_verbs`, so its hour reads the 24-hour form. A written `a.m.` or
    `p.m.` gives the hour of the 24-hour clock (Priberam, "a.m.": "antes do meio-dia"; "p.m.": "depois do meio-dia")."""
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
    """`catorze e trinta` for `14:30`, `vinte e uma horas` for `21:00`, and `meia-noite` for `0:00`. A time that writes
    the hour symbol `h` reads its units, so `17h30` reads `dezassete horas e trinta minutos` (Ciberdúvidas 14648;
    Ciberdúvidas, O nosso idioma, article 3267: "às onze horas e trinta minutos"), and its seconds (Ciberdúvidas 14586:
    "vinte horas, trinta minutos e vinte e quatro segundos"). The parser gives words with no comma, so `17 h 34 min 25
    s` reads `dezassete horas trinta e quatro minutos e vinte e cinco segundos`. A written zero second is not read."""
    fields = span.fields
    request = context.request
    tag = request.variety.tag
    hour, minute = day_hour(fields["hour"], fields["period"]), fields["minute"]
    try:
        if _day_point(fields) is not None:
            reading = parsers.spoken_time(tag, hour, clock="12h", period=True)
        elif fields["suffix"]:
            reading = parsers.spoken_time(tag, hour, minute, fields["second"] or None, style="units")
        else:
            reading = parsers.spoken_time(tag, hour, minute)
    except ValueError as error:
        raise DeclinedReading(f"ovos-date-parser reads no time {hour}:{minute:02}: {error}") from error
    prefix = fields["prefix"] or ""
    verb = prefix.rstrip()
    if verb.lower() in request.data["article_time_verbs"]:
        contracted = hour == 1 or _day_point(fields) is not None
        return prefix + (request.data["time_contractions"]["às"][str(hour)] if contracted else "às") + " " + reading
    plural = request.data["singular_time_verbs"].get(verb.lower())
    if plural is not None:
        if hour != 1 and _day_point(fields) is None:
            plural = plural.capitalize() if verb[0].isupper() else plural
            prefix = plural + prefix[len(verb):]
        return prefix + reading
    return _contracted_word(prefix, hour, request) + reading


def _currency(currency: FrozenMap, category: str) -> str:
    """The name of a currency in a plural category, with a small first letter. A number of the category `many`, a
    scale word from `milhão` up, takes `de` before the name, as it does before a unit: `um milhão de euros`."""
    name = currency_name(currency, category)
    name = name[:1].lower() + name[1:]
    return f"de {name}" if category == "many" and "many" not in currency else name


def speak_money(span: Span, context: SpanContext) -> str:
    """One or two decimals are the minor unit, when the currency names one: `2,50 €` and `2,5 €` read `dois euros e
    cinquenta cêntimos` (Ciberdúvidas 25561). A scale word that the text writes reads before the plural name: `dois
    milhões de reais`. The number agrees with the first word of the currency name, so `2 £` reads `duas libras`;
    before a scale word from `milhão` up it stays masculine, and before `mil` it agrees with the name: `duas mil
    libras`. A scale word that the data gives with plural forms agrees with the amount, by the CLDR plural category:
    `um milhão`, `dois milhões`, `1,5 milhões`."""
    request = context.request
    fields = span.fields
    amount = FrozenMap({**fields["amount"], "sign": ""})
    currency = currency_table(request)[fields["currency"]]
    gender = _gender_of(_currency(currency, "one").split()[0], request)
    integer, fraction = amount["integer"] or "0", amount["fraction"]
    if fields["scale"]:
        scale = request.data["scales"][fields["scale"]]
        if isinstance(scale, FrozenMap):
            scale = _counted(scale, request, written_amount(amount))
        number = amount_words(amount, request, Features(gender=gender if fields["scale"] == "mil" else None))
        words = f"{number} {scale} {_currency(currency, 'other')}"
    elif len(fraction) in (1, 2) and "minor" in currency:
        major = f"{_cardinal(integer, request, gender)} {_currency(currency, _plural(request, integer))}"
        cents = str(int(fraction.ljust(2, "0")))
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
    """Ordinal up to `roman_ordinal_limit` and cardinal after it (Ciberdúvidas 14167, for kings and popes; 12370, for
    centuries; 11716, for the parts of a work; Vitória, Bueno and Cunha, for pt-BR, as the module docstring quotes).
    After `século` or a noun of `roman_nouns`, the reading takes the gender of the noun and a small letter, and so does
    each numeral of a list that follows it, as in `séculos XI, XII e XIII`. After a title and its full stop, which ends
    the context words, it takes the gender of the title that the recognizer keeps in the memo of the request, and a
    capital. After a name, it agrees with the name and takes a capital, as the name does. Between a singular article and
    a common noun, it takes the gender of both, which the recognizer keeps in the memo of the request, and a capital
    when the noun has one."""
    request = context.request
    data = request.data
    value = str(span.fields["value"])
    before = context.before
    last = before[-1] if before else ""
    noun = request.memo.get("pt_roman_series", {}).get(span.start) or _roman_noun(before, data["roman_nouns"])
    noun_after = request.memo.get("pt_roman_before_noun", {}).get(span.start)
    if noun_after is not None:
        gender, capital = noun_after
    elif noun in data["century_words"] or last.lower() in data["century_words"]:
        gender, capital = MASCULINE, False
    elif noun is not None:
        gender, capital = GrammaticalGender(data["roman_nouns"][noun]), False
    elif not before:
        title = request.memo.get("pt_roman_titles", {}).get(span.start, "")
        gender, capital = _title_gender(title, request), True
    else:
        gender, capital = _name_gender(before, request), True
    if span.fields["role"] == "ordinal":
        words = SPELLER.ordinal(value, Features(gender=gender), request)
    else:
        words = _cardinal(value, request)
    return words[0].upper() + words[1:] if capital else words


TELEPHONE = Telephone()
"""The shared telephone recognizer. Two years that a dash joins have no phone shape (`no_phone_shapes`), so
`Os telemóveis de 2010-2020` reads a range."""


@dataclass(frozen=True)
class Clock(TimeClock):
    """The times of the core, and two Portuguese forms that it leaves. One is the unit symbols `h`, `min` and `s` around
    the digits, spaced or not: `17 h`, `17h30 min`, `17h30min`, `17:30 h` (Ciberdúvidas 14648: "17h30 min"; "Considero
    perfeitamente aceitável 17:30 h") and `17 h 34 min 25 s` (Ciberdúvidas, O nosso idioma, article 3267: "às 17 h 34
    min 25 s"). The other is two times that a range mark joins, as in `das 9h-17h` and `das 9:00-17:00`, where the
    second time takes the article of the first (Ciberdúvidas 22241: "das cinco às seis horas"). A chain of three times
    or more stays as written. A time that writes `h` keeps it in the `suffix` field, so it reads its units.

    Before "meia-noite", "meio-dia" or a time in the hour 1, which reads "uma", a word of `time_contractions` right
    before the time takes the article of that noun, when only white space stands between them. The span then starts
    at the word and holds the word and the white space in its `prefix` field, and the reading writes the contracted
    word: `às 0:00` reads `à meia-noite`. The time span that starts at the digits follows it, with a `prefix` of
    None. It reads when a lexicon entry claims the word first, and then the word stays as written and the time reads
    its 24-hour form: `às zero horas`. A word with two characters right before it that are no white space, as in
    `5(às 0:00`, gives only that span, because the span at the word would wait on the digit that the word touches
    (design section 4.2). So does a character between the word and the time, such as the `§` of `às § 0:00`, so that
    the span claims no character that another form reads. So does a word of `time_article_prepositions` with no
    preposition of its list right before it, as in `Almoçamos as 12:00`. In a range, the range word of the first
    time takes the article: `das 9:00-12:00` reads `das nove horas ao meio-dia`. A time that reads its own hour
    unit, a whole hour or a time with `h`, claims a `h` or `horas` right after it, and a `hora` after `1:00`, with
    only spaces or tabs between, so that the word is read once: `16:00 horas` reads `dezasseis horas`."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        own = [*self._ranges(text, tokens, request), *self._marked(text, request)]
        words = context_words(tokens)
        day_ends = []
        for match in re.finditer("24:00", text):
            start, end = match.span()
            joined = text[end:end + 1] in (":", ".", ",") and text[end + 1:end + 2].isdigit()
            before = clause_window(text, words, start, end, -1, limit=1)
            if is_bounded(text, start, end) and not joined and before \
                    and before[0].lower() in request.data["time_words"]:
                day_ends.append(replace(self._time(start, "24", "00", ""), end=end))
        for span in (*self._symbols(text, request), *day_ends):
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
            index = bisect_right(words, span.start, key=lambda word: word.end)
            word = words[index - 1] if index else None
            verb = word is not None and word.text.lower() in request.data["plural_time_verbs"] \
                and not (span.fields["suffix"] or span.fields["period"])
            plural = verb and text[word.end:span.start].isspace()
            after = bisect_left(words, span.end, key=lambda word: word.start)
            hour_word = after < len(words) and re.fullmatch("[ \t]+", text[span.end:words[after].start]) is not None \
                and words[after].text.lower() in ("h", "hora", "horas")
            if verb and (not plural or hour_word):
                continue
            if hour_word:
                fields = span.fields
                one_hour = fields["minute"] == 0 and day_hour(fields["hour"], fields["period"]) == 1
                if (fields["suffix"] or fields["minute"] == 0) and (words[after].text.lower() != "hora" or one_hour):
                    span = replace(span, end=words[after].end)
            spaced = word is not None and text[word.end:span.start].isspace() \
                and not (span.fields["suffix"] or span.fields["period"])
            verb = word.text.lower() if spaced else ""
            if verb in request.data["singular_time_verbs"]:
                previous = words[index - 2] if index > 1 else None
                subject = previous is not None and text[previous.end:word.start].isspace() \
                    and previous.text.lower() not in request.data["time_verb_adverbs"]
                if not subject and (span.fields["hour"] != 0 or _day_point(span.fields) is not None):
                    out.append(replace(span, start=word.start,
                                       fields=FrozenMap({**span.fields, "prefix": text[word.start:span.start]})))
                continue
            if verb in request.data["article_time_verbs"]:
                out.append(replace(span, start=word.start,
                                   fields=FrozenMap({**span.fields, "prefix": text[word.start:span.start]})))
                continue
            # Any time in the hour 1 reads "uma", which is singular.
            hour = 1 if day_hour(span.fields["hour"], span.fields["period"]) == 1 else _day_point(span.fields)
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
            if plural:
                if hour != 0:
                    out.append(replace(span, fields=FrozenMap({**span.fields, "prefix": None})))
                continue
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
        """The time span at `start`. A clock `24:00` is the end of the day, which is midnight: hour 0."""
        if (hour, minute, symbol, second) == ("24", "00", "", None):
            hour = "0"
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

    def _marked(self, text: str, request: Request) -> Iterator[Span]:
        """`às 10.30`, `pelas 17.30 h`, `até à 1.30` and `entre as 9.30 e as 10.30`: a time with a full stop between
        the hour and the minutes, right after a word of `point_time_words`, a word of `point_one_words` before the
        hour 1, or a word of `point_article_prepositions` after one of its prepositions. The `as` after `e` reads
        when a time of this form ends right before `e`. A word or a sign after the time that shows an amount keeps it
        as written, as in `das 3.20 kg`, `às 2.30 t`, `das 2.30 anos` and `às 10.30 €`."""
        data, tag = request.data, request.variety.tag
        governed = data["point_article_prepositions"]
        words = "|".join([*data["point_time_words"], *data["point_one_words"], *governed])
        pattern = re.compile(f"(?<![\\w-])({words})[ \t]+([0-9][0-9]?)[.]([0-9][0-9])(?:( ?)h)?"
                             "(?![.,]?[0-9]|[^\\W\\d_])", re.IGNORECASE)
        last_end = None
        for match in pattern.finditer(text):
            word, hour, minute, gap = match.groups()
            word = word.lower()
            if word in data["point_one_words"] and int(hour) != 1:
                continue
            if word in governed:
                previous = re.search("([^\\W\\d_]+)([ \t]+)$", text[max(match.start() - 40, 0):match.start()])
                link = previous is not None and previous[1].lower() == "e" and last_end is not None \
                    and text[last_end:match.start() - len(previous[0])].isspace()
                if previous is None or not (previous[1].lower() in governed[word] or link):
                    continue
            rest = text[match.end():].lstrip(" \t")
            following = re.match("[^\\s,;:!?)\\]»”\"]*", rest)[0].rstrip(".").lower().replace("º", "°")
            units = [unit for unit in cldr_data(tag)["units"].values()
                     if not set(unit["symbols"]) & set(data["time_units"])]
            unit_words = {entry.lower() for unit in units for entry in (
                *unit["symbols"], *(name.replace("{0}", "").split()[0] for name in unit["names"].values()))}
            periods = [period for spellings in data["day_periods"].values() for period in spellings]
            amounts = {entry.lower().rstrip(".") for entry in (
                *data["scales"], *data["amount_words"],
                *(name for currency in currency_table(request).values()
                  for name in (currency["one"].split()[0], currency["other"].split()[0], *currency["symbols"])),
                *periods)}
            amounts |= unit_words - {entry.lower().replace(".", "")
                                     for entry in (*data["function_words"], *data["letter_words"], *periods)}
            if (following in amounts or following.rstrip("23²³") in amounts or following in data["percent"]["signs"]
                    or re.match(f"{data['percent']['word']}\\b", rest, re.IGNORECASE)):
                continue
            if span := self._time(match.start(2), hour, minute, "" if gap is None else "h"):
                last_end = match.end()
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
    """`250 000 €`: a currency symbol next to digits in groups of three with a space between them, where the variety
    writes the space as its group mark. CLDR 49 pt-PT gives the no-break space as the group mark (`numbers.json`,
    `group`: U+00A0, currency format `#,##0.00 ¤`), and the SI Brochure, 9th edition, 5.4.4, divides the digits of a
    number into groups of three with a space. The claim order puts this recognizer before the telephone, which keeps a
    run of such groups as written. A run that the telephone reads, as in `+351 912 345 678 €`, is no amount."""
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
        phones = _phones(text, tokens, request)
        found = []
        for match in _SPACE_GROUPS.finditer(fold_digits(text)):
            start, end = match.span()
            if is_bounded(text, start, end) and one_digit_set(text[start:end]) \
                    and not any(phone.start < end and start < phone.end for phone in phones):
                integer, _, fraction = re.sub("[ \u00a0\u202f]", "", match.group()).partition(",")
                found.append(Number(start, end, "", integer, fraction or None, digit_script(text[start:end])))
        return found


_SUPERSCRIPTS = {"2": "²", "3": "³"}


@dataclass(frozen=True)
class Measure(CoreMeasure):
    """The measures of the core, and a unit of `line_power_symbols` with its exponent on the line right after the
    number, as `80 m2` and `5cm3`, which read as `80 m²` and `5cm³`."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        lined = _line_powers(request.data["line_power_symbols"]).sub(
            lambda match: match.group() if text[match.end():match.end() + 1].isalnum()
            else match.group(1) + _SUPERSCRIPTS[match.group(2)], text)
        return super().find(lined, tokens, request)


@cache
def _line_powers(symbols: tuple[str, ...]) -> re.Pattern[str]:
    alternatives = "|".join(map(re.escape, sorted(symbols, key=len, reverse=True)))
    return re.compile(f"([0-9](?: |\u00a0)?(?:{alternatives}))([23])")


_GROUPED = "[1-9][0-9]{0,2}(?:[ \u00a0\u202f][0-9]{3})+"
_SPACED_NUMBER = re.compile(f"({_GROUPED})(?:,([0-9]+)((?:[ \u00a0\u202f][0-9]{{1,3}})*))?")
_SPACED_RANGE = re.compile(f"({_GROUPED})[-–]({_GROUPED})")


def _digits(written: str) -> str:
    return re.sub("[^0-9]", "", written)


def _phones(text: str, tokens: Sequence[Token], request: Request) -> list[Span]:
    """The telephone spans that read."""
    return [span for span in TELEPHONE.find(text, tokens, request) if not span.keep]


def _spaced(pattern: re.Pattern[str], text: str, tokens: Sequence[Token], request: Request) -> Iterator[re.Match[str]]:
    """The matches of `pattern` where the variety writes the space as its group mark (`space_group_money`), with no
    sign, digit or mark between digits next to them (`+351 912 000`, `1.200 000`) and no telephone run over them."""
    if not request.data.get("space_group_money"):
        return
    for match in pattern.finditer(fold_digits(text)):
        start, end = match.span()
        after = text[end:end + 2]
        if not is_bounded(text, start, end) or (start and text[start - 1] in "+-−–(.,") \
                or (after[:1] and after[:1] in ".,:/-–" and after[1:2].isdigit()) \
                or not one_digit_set(text[start:end]):
            continue
        if not any(phone.start < end and start < phone.end for phone in _phones(text, tokens, request)):
            yield match


_ROLES = "pt_roles"
_SCALED_NOUNS = "pt_scaled_nouns"
_AFTER_SCALE = re.compile("[ \u00a0]+mil[ \u00a0]+e[ \u00a0]+[0-9]+[ \u00a0]+([^ \t\n\u00a0,;:.!?()]+)")
_YEAR_MARKS = frozenset(",:)")
_FOUR_DIGITS = re.compile("[0-9]{4}")
_WORD_BEFORE = re.compile("([^ \t\n\u00a0,;:.!?()]+)[ \u00a0]+$")
_WORD_AFTER = re.compile("[ \u00a0]*([^ \t\n\u00a0,;:.!?()\\-–—]*)")
_LIST_MARK = re.compile(" *[-–—.)] ")
_ONE_WORD = re.compile("[,;:.!?)]*[ \t\n\u00a0]+[^ \t\n\u00a0,;:.!?()]+[ \t\n\u00a0]+")


@dataclass(frozen=True)
class Cardinal(CoreCardinal):
    """The shared cardinal recognizer. It gives a number the role that `agreement` reads, in `Request.memo` under
    `_ROLES`, by the start of the number. A number of four digits is a `year` with a mark of `_YEAR_MARKS` right after
    it, as `2012` in `Braga 2012: Capital Europeia`, and from 1000 to 2099 after a word of `year_words` and before a
    capitalised word, a word that is no plural or a mark, as `1998` in `Em 1998 Lisboa recebeu a Expo`.
    An unsigned number that starts a line, with optional spaces, one of `-`, `–`, `—`, `.` or `)` and a space after
    it, as in `2 - Casa de campo`, numbers an item of a `list`. A number alone in square brackets is a `reference`. A
number
    one word after a phone number that reads, as `2` in `912 345 678 ou 2 casas`, is `after_phone`, so that it is no
    second number of a pair. A number before `mil e` and a second number, as `2` in `2 mil e 500 pessoas`, counts the
    noun after the second number, which lies beyond the context words, so its start goes under `_SCALED_NOUNS` with
    that word."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        after_phone = {word.end() for phone in _phones(text, tokens, request)
                       if (word := _ONE_WORD.match(text, phone.end))}
        for span in super().find(text, tokens, request):
            role = None
            if _FOUR_DIGITS.fullmatch(text, span.start, span.end):
                before = _WORD_BEFORE.search(text, max(span.start - 12, 0), span.start)
                after = _WORD_AFTER.match(text, span.end).group(1)
                if text[span.end:span.end + 1] in _YEAR_MARKS or (
                        1000 <= int(span.fields["digits"]) <= 2099 and before
                        and before.group(1).lower() in request.data["year_words"]
                        and (not after or after[0].isupper() or not after.endswith("s"))):
                    role = "year"
            if role is None and text[span.start].isdigit() \
                    and not text[text.rfind("\n", 0, span.start) + 1:span.start].strip() \
                    and _LIST_MARK.match(text, span.end):
                role = "list"
            if role is None and text[span.start - 1:span.start] == "[" and text[span.end:span.end + 1] == "]":
                role = "reference"
            if role is None and span.start in after_phone:
                role = "after_phone"
            if role:
                request.memo.setdefault(_ROLES, {})[span.start] = role
            if scaled := _AFTER_SCALE.match(text, span.end):
                request.memo.setdefault(_SCALED_NOUNS, {})[span.start] = scaled.group(1)
            yield span


@dataclass(frozen=True)
class SpacedRange:
    """A range of two numbers grouped with spaces. It reads when both end in the group `000` and it goes up, as in
    `10 000-20 000`, and any other such range stays whole as written, so that no part of it reads."""
    name: str = "spaced_range"
    form: Form = Form.RANGE

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in _spaced(_SPACED_RANGE, text, tokens, request):
            low, high = (_digits(group) for group in match.groups())
            reads = low.endswith("000") and high.endswith("000") and int(low) < int(high)
            yield Span(*match.span(), Form.RANGE, FrozenMap({"low": low, "high": high, "prefix": "", "suffix": ""}),
                       recognizer=self.name, keep=not reads)


@dataclass(frozen=True)
class SpacedNumber:
    """A whole number grouped with spaces reads when its last group is `000`, as `100 000 habitantes`; a number with
    a decimal part grouped with spaces, as `78 890,322 14`, stays whole as written."""
    name: str = "spaced_number"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in _spaced(_SPACED_NUMBER, text, tokens, request):
            start, end = match.span()
            whole, fraction, grouped = match.groups()
            integer = _digits(whole)
            if grouped or (not fraction and integer.endswith("000")):
                yield Span(start, end, Form.CARDINAL,
                           FrozenMap({"digits": integer, "sign": "", "lead": "", "prefix": "", "suffix": "",
                                      "script": digit_script(text[start:end])}),
                           recognizer=self.name, keep=bool(grouped))


@dataclass(frozen=True)
class SpacedDecimal:
    """A decimal whose whole part is grouped with spaces, where the variety writes the space as its group mark: `1 250
    000,50` reads as `1250000,50` does. A decimal part grouped with a space is left to `SpacedNumber`."""
    name: str = "spaced_decimal"
    form: Form = Form.DECIMAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        for match in _spaced(_SPACED_NUMBER, text, tokens, request):
            whole, fraction, grouped = match.groups()
            if fraction and not grouped:
                start, end = match.span()
                yield Span(start, end, Form.DECIMAL,
                           Number(start, end, "", _digits(whole), fraction, digit_script(text[start:end])).amount(),
                           recognizer=self.name)


@dataclass(frozen=True)
class SpelledDecimal:
    """`0 vírgula 02`: digits with a leading zero after a number and the decimal word are a decimal part."""
    name: str = "spelled_decimal"
    form: Form = Form.CARDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        link = f" {request.data['decimal_word']} "
        numbers = numbers_in(text, request)
        ends = {number.end for number in numbers if number.fraction is None}
        for number in numbers:
            digits = number.integer
            if number.fraction is None and not number.sign and len(digits) > 1 and digits[0] == "0" \
                    and text[number.start - len(link):number.start].lower() == link \
                    and number.start - len(link) in ends \
                    and is_bounded(text, number.start, number.end):
                yield Span(number.start, number.end, Form.CARDINAL,
                           FrozenMap({"digits": digits, "sign": "", "lead": "", "prefix": "", "suffix": "",
                                      "script": number.script}), recognizer=self.name)


@dataclass(frozen=True)
class PointDecimal(CoreDecimal):
    """The decimals of the core. A decimal with the full stop reads before a word of `_unit_names`, as `10.4567 graus`,
    and, with one or two digits after the full stop, after a sign, as `-10.4`. After a word of `point_version_words`
    or a name of `_after_name`, the full stop parts the levels of a version, so the span reads through
    `speak_point_decimal`: `versão 2.10` reads "versão dois ponto dez", and so does each number of a list after the
    word, as `versão 4.6 ou 4.7`. These stay as written: a number with no sign and no unit, as `o valor é 10.4`; a
    number after a word of `point_section_words`, as `artigo 10.4`; a number that a full stop or a comma and a digit
    continue or that a full stop or a comma comes right before, as `1.2.3` and `A.4.3`; a number with no whole part,
    as `.50`, or whose whole part has a leading zero, which may write a day and a month, as `01.02`; and a number with
    a sign that opens a line before a capital, as `-1.3 Objeto`, that a full stop and a lowercase word close, or that
    may write an hour and minutes, after a word of `time_words` or before a unit of `_clock_units`, as
    `-3.30 horas`."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        points = _point_starts(text, request)
        words = context_words(tokens)
        names = _unit_names(request.variety.tag, unit_table(request), joined_table(request))
        for span in super().find(text, tokens, request):
            if span.start + len(span.fields["prefix"]) not in points:
                yield span
                continue
            before = text[:span.start]
            integer = span.fields["integer"]
            short = (integer == "0" or integer[:1] not in ("", "0")) and len(span.fields["fraction"]) <= 2 \
                and not before.endswith((".", ","))
            links = (",", *request.data["list_links"], request.data["range_word"], "à")
            index = bisect_left(words, span.end, key=lambda word: word.start)
            after = words[index].text if index < len(words) and text[span.end:words[index].start].isspace() else ""
            if after in names:
                yield span
                continue
            if _after_word(before, request.data["point_section_words"], links):
                continue
            if _after_word(before, request.data["point_version_words"], links) \
                    or _after_name(before, text[span.end:], request):
                if short and not span.fields["sign"]:
                    yield replace(span, recognizer=POINT_LABEL)
                continue
            heading = re.fullmatch("[-–•]?\\s*", before.rpartition("\n")[2]) \
                and re.match("[.]?\\s*(?:[-–:]\\s*)?[\"“]?[A-ZÀ-Ý]", text[span.end:])
            closed = re.match("[.]\\s+[a-zà-ý]", text[span.end:])
            clock = _clock_like(span.fields) and (after in _clock_units(request.variety.tag)
                                                  or _after_word(before, request.data["time_words"]))
            if short and span.fields["sign"] and not heading and not closed and not clock:
                yield span


POINT_LABEL = f"{PointDecimal.name}:label"


def _after_word(before: str, words: Sequence[str], links: Sequence[str] = ()) -> bool:
    """Whether `before` ends in one of `words`, perhaps a colon, and white space, as `versão `, `Versão: ` and `art. `,
    or also in a list of numbers with a full stop that `links` join, as `itens 4.6 e `."""
    pattern = "|".join(map(re.escape, words))
    chain = f"(?:[0-9]+[.][0-9]+\\s*(?:{'|'.join(map(re.escape, links))})\\s+)*" if links else ""
    return re.search(f"(?<![\\w.])(?:{pattern}):?\\s*{chain}$", before, re.IGNORECASE) is not None


def _after_name(before: str, rest: str, request: Request) -> bool:
    """Whether `before` ends in the name of a product or a standard and spaces, as `iOS ` and `Windows `, and `rest`,
    the text after the number, starts with a space, a mark of a clause or the end, but no dash between spaces and no
    full stop before a lowercase word, which a section number takes, as `Cidade 2.1 - Atração`. A name has a capital
    and a lowercase letter, and tugalex does not know it as a word, as it knows `Execução` in `Execução 5.1` and each
    weekday. It opens no sentence, is no month and no book of `bible_books`, and has no bracket before it, which a
    chapter and a verse take, as `(Rm 13.8)`."""
    match = re.search("(?<![\\w.])\\w[\\w-]*[^\\S\\n]+$", before)
    if match is None or not re.match("$|[\\s,;:!?)]|[.](?![0-9])", rest) \
            or re.match("[.]\\s+[a-zà-ý]|\\s+[-–]\\s", rest):
        return False
    word, head = match[0].rstrip(), before[:match.start()]
    lower = word.lower()
    return any(map(str.isupper, word)) and any(map(str.islower, word)) and not _known_word(lower, request) \
        and lower.lstrip("0123456789") not in (*request.data["months"], *request.data["bible_books"]) \
        and not re.search("(?:^|[.!?…]\\s|\\n)\\s*[\"“«]?$", head) \
        and not re.search("[(\\[]\\s*$", head)


def _clock_like(amount: FrozenMap) -> bool:
    """Whether a `DECIMAL` record may write an hour and minutes, as `9.30`: two digits under 60 after a whole part
    up to 24."""
    return len(amount["fraction"]) == 2 and int(amount["integer"] or "0") <= 24 and int(amount["fraction"]) < 60


@cache
def _clock_units(tag: str) -> frozenset[str]:
    """The first word of each CLDR name and each symbol of the hour, the minute and the second, as `horas` and
    `min`."""
    units = cldr_data(tag)["units"]
    return frozenset(word for key in ("duration-hour", "duration-minute", "duration-second")
                     for word in (*(name.replace("{0}", "").split()[0] for name in units[key]["names"].values()),
                                  *units[key]["symbols"]))


def speak_point_decimal(span: Span, context: SpanContext) -> str:
    """A decimal, and a version number of `PointDecimal`: the whole part, `point_word` and the part after the full
    stop, each as a cardinal in the masculine, as a number after a noun of `label_nouns` reads. Priberam, "ponto",
    sense 7, names the mark: "Sinal gráfico (.)"."""
    if span.recognizer != POINT_LABEL:
        return speak_decimal(span, context)
    fields, request = span.fields, context.request
    return " ".join([_cardinal(fields["integer"], request), request.data["point_word"],
                     SPELLER.decimal_part(fields["fraction"], request)])


@dataclass(frozen=True)
class PointMeasure(Measure):
    """The measures of `Measure`. A decimal with the full stop reads only with a unit whose name starts with a word of
    `_unit_names`, so `1.30 h` and `9.30h` stay as written."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        points = _point_starts(text, request)
        names = _unit_names(request.variety.tag, unit_table(request), joined_table(request))
        for span in super().find(text, tokens, request):
            if not any(span.start <= start < span.end for start in points) \
                    or unit_reading(request, span.fields["unit"], "other")[0].replace("{0}", "").split()[0] in names:
                yield span


def _point_starts(text: str, request: Request) -> set[int]:
    """The start of each number of the text with a full stop, not the canonical comma, before its decimal part."""
    canonical = number_marks(request.data, request.params.decimal_mark)[0][1][:1]
    return {number.start for number in numbers_in(text, request)
            if number.fraction and text[number.end - len(number.fraction) - 1] != canonical}


@cache
def _unit_names(tag: str, *tables: FrozenMap) -> frozenset[str]:
    """The first word of each CLDR name of the units of the tables that is no function word, as `quilómetros` and
    `graus`, apart from the units of duration."""
    durations = [unit for key, unit in cldr_data(tag)["units"].items() if key.startswith("duration-")]
    return frozenset(name.replace("{0}", "").split()[0] for table in tables for unit in table.values()
                     if unit not in durations for name in unit["names"].values()) - frozenset(DATA["function_words"])


@dataclass(frozen=True)
class Ordinal:
    """`1.º`, `2.ª`, `3º`: a whole number and the ordinal indicator, with or without the full stop."""
    name: str = "ordinal"
    form: Form = Form.ORDINAL

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        marks = "".join(request.data["ordinal_marks"])
        for match in digit_run_matches(f"[0-9]+([.]?[{marks}])", fold_digits(text)):
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
                                  "written_order": "DMY", "month_written": "name", "era": "",
                                  "prefix": "", "suffix": ""}), recognizer=self.name)


def _regnal_title(text: str, word: Word, titles: frozenset[str]) -> bool:
    """Whether `word` is a regnal title, or ends one with a full stop inside, such as `D.ª`, whose last word is `ª`."""
    return word.text in titles or any(text.endswith(title, 0, word.end)
                                      and is_bounded(text, word.end - len(title), word.end)
                                      for title in titles if "." in title)


def _roman_noun(before: Sequence[str], nouns: FrozenMap) -> str | None:
    """The entry of `roman_nouns` that the words before a numeral end with, in any case, or None."""
    for size in (2, 1):
        key = " ".join(before[-size:]).lower() if len(before) >= size else None
        if key in nouns:
            return key
    return None


def _list_members(text: str, end: int, links: frozenset[str]) -> list[tuple[int, int, str]]:
    """The numerals of a list that starts with the numeral that ends at `end`: `N1, N2, … e|ou Nk`, with a comma and a
    space between the members and a word of `list_links`, in any case, before the last one. Without that last link,
    the numerals after a comma are no list, so `No Grupo II, CD Tondela venceu.` gives none."""
    found: list[tuple[int, int, str]] = []
    position = end
    while (match := _LIST_COMMA.match(text, position)) and is_bounded(text, *match.span(1)):
        found.append((match.start(1), match.end(1), match.group(1)))
        position = match.end(1)
    match = _LIST_LINK.match(text, position)
    if match is None or match.group(1).lower() not in links or not is_bounded(text, *match.span(2)):
        return []
    return [*found, (match.start(2), match.end(2), match.group(2))]


_LIST_COMMA = re.compile(", ([IVXLCDM]+)")
_LIST_LINK = re.compile(",? ([A-Za-z]+) ([IVXLCDM]+)")


def _initial(text: str, end: int) -> bool:
    """Whether the letter that ends at `end` is an initial: a full stop, a space and a capital follow it, as in `V.
    Silva`."""
    return text.startswith(". ", end) and text[end + 2:end + 3].isupper()


def _title_gender(title: str, request: Request) -> GrammaticalGender:
    """The gender of a title with its full stop: the gender of its reading in `titles`, else masculine, as `D.`
    reads `Dom` with no name after it."""
    reading = request.data["titles"].get(title)
    return (_noun_gender(reading, request) if reading else None) or MASCULINE


def _noun_gender(word: str, request: Request) -> GrammaticalGender | None:
    """The gender of a common noun: the `noun_gender` table, else tugalex for a word that it knows. tugalex guesses
    from the ending of a word that its exceptions do not list, so a caller checks the gender against other evidence.
    A noun of two genders has none."""
    entry = _listed_gender(word, request.data)
    if entry:
        return GrammaticalGender(entry)
    if _known_word(word.lower(), request):
        name = _LEXICON_GENDERS.get(_lexicon_gender(word.lower()) or "")
        return GrammaticalGender(name) if name else None
    return None


_SINGULAR_CONTRACTIONS = {
    **dict.fromkeys(("neste", "nesse", "naquele", "deste", "desse", "daquele"), MASCULINE),
    **dict.fromkeys(("nesta", "nessa", "naquela", "desta", "dessa", "daquela"), FEMININE),
}
"""The singular demonstratives of `function_words` contracted with `em` or `de`, and their gender. Each starts a
prepositional phrase, so the word after the numeral is its noun."""


def _noun_after(text: str, end: int, article: str, request: Request) -> tuple[GrammaticalGender, bool] | None:
    """The gender of a singular demonstrative contracted with `em` or `de`, `article`, and of the common noun right
    after the numeral and one space, and whether the noun starts with a capital. The contraction starts a prepositional
    phrase, so the word after the numeral is its noun, as `edição` in `Nesta XV edição`. An article or a demonstrative
    alone may start a sentence about a team, as in `O XV segundo a imprensa` or `ESTE XV NUNCA PERDEU`, so it gives
    none. None also when the next word is a function word or no noun of the gender of the contraction
    (`_noun_gender`)."""
    gender = _SINGULAR_CONTRACTIONS.get(article.lower())
    match = re.match(r" (\w+)", text[end:])
    if gender is None or match is None:
        return None
    word = match.group(1)
    if word.lower() in request.data["function_words"] or _noun_gender(word, request) != gender:
        return None
    return gender, word[0].isupper()


def _given_name_gender(name: str, request: Request) -> GrammaticalGender | None:
    """The gender of a given name: the given-name list of tugalex, else the `noun_gender` table, which holds a few
    names. A name of both sexes reads masculine. None for a word that no list names."""
    try:
        from tugalex import TugaLexicon
    except ImportError:
        entry = request.data["noun_gender"].get(name)
        return GrammaticalGender(entry) if entry else None
    code = TugaLexicon.get_given_name_gender(name)
    if code is None:
        return None
    return FEMININE if code == "f" else MASCULINE


def _name_gender(before: Sequence[str], request: Request) -> GrammaticalGender:
    """The gender of a numeral after a capitalised word, with no guess from an ending (design section 4.2): the gender
    of a regnal title before the name, as `rainha` in `Rainha Elizabeth II`, then the common noun, as `Região` in
    `Região III`, then the given name, as `Isabel` in `Isabel II`, else masculine, as `Godzilla II`. `D.`, which reads
    `Dom` or `Dona`, gives no gender."""
    last = before[-1]
    if len(before) >= 2 and len(before[-2]) > 1 and before[-2].lower() in {
            title.lower() for title in request.data["regnal_titles"]}:
        title = _noun_gender(before[-2], request)
        if title is not None:
            return title
    return _noun_gender(last, request) or _given_name_gender(last, request) or MASCULINE


@dataclass(frozen=True)
class Roman:
    """A Roman numeral after a name, after `século`, after a noun of `roman_nouns` or after a title: `D. Maria II`,
    `Luís XIV`, `século XIX`, `capítulo V`, `Classe II`, `D. XIV`.

    After a noun of `century_words`, any well-formed numeral up to XXX reads. After a noun of `roman_nouns`, a numeral
    of two letters or more reads, and so do `I`, `V` and `X` after a noun of `roman_letter_nouns`, as in `o capítulo V`,
    but a numeral of `roman_words` reads only after a noun of `roman_letter_nouns` and when no word in lowercase follows
    it after a space, so `capítulo XL.` reads and `Classe CL usado` and `A Classe CL.` stay as written. After a
    capitalised name, a value up to 30 reads when a regnal title comes right before the name, as in `D. João V` and
    `papa Pio X`. A numeral of two letters or more also reads after any other capitalised word, as in `João Paulo II`
    and `Luís XIV`, and right after a title and its full stop, as in `D. XIV`. In these two cases the value is at most
    30, so an acronym such as `MIX` stays as written. These rules need spaces alone between the word before the numeral
    and the numeral. When a comma or another mark parts them, a numeral from 11 to 30 after a capitalised word reads as
    a cardinal, as `XX` in `No século XIX, XX pessoas`, and a smaller one stays as written, unless a regnal title comes
    before the word. Between a singular demonstrative contracted with `em` or `de` and a common noun of the same gender,
    a numeral of two letters or more up to C that is no word of `roman_words` reads as an ordinal that agrees with them,
    as in `Nesta XV edição`. After any other word of `function_words`, a numeral from 11 to 30 reads as a cardinal, as
    in `O XV`. Outside a clause in capitals, no numeral reads right after a word of `letter_words` that is no function
    word, as `LI` in `Eu LI`. In a clause in capitals, no numeral reads that is a word of `letter_words` or a word that
    tugalex knows, as `VI` in `EU VI`. A short numeral after another capitalised word, as in `Malcolm X`, stays as
    written.

    A list after `século` or a noun of `roman_nouns` reads with that noun: `N1, N2, … e Nk`, with a comma and a space
    between the members and a word of `list_links`, in any case, before the last one, as in `séculos XI, XII e XIII` and
    `capítulo V e VI`. Each member passes the test of the first numeral and holds a larger value than the numeral before
    it, and a letter that a full stop, a space and a capital follow is an initial, as `V.` in `V. Silva`. The list ends
    at the first numeral that fails, so `capítulo IV, MDC e MMC` reads only `IV`. A numeral after a comma with no
    closing link is no member. A numeral that is no member reads as the rule for a numeral after a mark gives, so `No
    Grupo II, CD Tondela venceu.` keeps `CD`, `485, V, III e VI` stays as written, and `O título II, XI capítulos` reads
    `XI` as a cardinal."""
    name: str = "roman"
    form: Form = Form.ROMAN

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        from text2spoken.core.roman import value as roman_value, word_follows

        data = request.data
        titles = frozenset(data["regnal_titles"])
        title_keys = {key.rstrip(".") for key in (*data["titles"], *data["honorific_before_name"])}
        not_names = titles | title_keys | frozenset(data["titles"].values())
        centuries = frozenset(data["century_words"])
        nouns = data["roman_nouns"]
        letter_words = frozenset(data["letter_words"])
        letter_nouns = frozenset(data["roman_letter_nouns"])
        function_words = frozenset(data["function_words"])
        numeral_words = frozenset(data["roman_words"])
        links = frozenset(link.lower() for link in data["list_links"])
        words = context_words(tokens)
        breaks = clause_breaks(text)
        clauses = capital_clauses(text, request)
        members: dict[int, str] = {}

        def in_series(numeral: str, value: int, key: str, end: int) -> bool:
            if key in centuries:
                return value <= 30
            return (len(numeral) >= 2 or (numeral in "IVX" and key in letter_nouns)) \
                and (numeral not in numeral_words or key in letter_nouns and not word_follows(text, end))

        for match in re.finditer("[IVXLCDM]+", text):
            start, end = match.span()
            numeral = match.group()
            value = roman_value(numeral)
            if value is None or not is_bounded(text, start, end) or not text.endswith(" ", 0, start):
                continue
            index = bisect_right(words, start, key=lambda word: word.end)
            if index < 1:
                continue
            previous = words[index - 1]
            if start in members:
                request.memo.setdefault("pt_roman_series", {})[start] = members[start]
                yield self._span(start, end, value, data, members[start])
                continue
            key = None
            in_clause = any(first <= previous.start and end <= last for first, last in clauses)
            function_word = previous.text.lower() in function_words
            is_word = previous.text.upper() in letter_words and not in_clause and not function_word \
                or in_clause and (numeral in letter_words or _known_word(numeral.lower(), request))
            if previous.text in title_keys and text[previous.end:start] == ". ":
                reads = len(numeral) >= 2 and not is_word and value <= 30
                if reads:
                    request.memo.setdefault("pt_roman_titles", {})[start] = previous.text + "."
            else:
                before = clause_window(text, words, start, end, -1, limit=2, breaks=breaks)
                if not before:
                    continue
                title = index >= 2 and _regnal_title(text, words[index - 2], titles) \
                    and text[words[index - 2].end:previous.start] in (" ", ". ")
                noun = _roman_noun(before, nouns)
                if not text[previous.end:start].isspace():
                    reads = previous.text not in not_names and before[-1][0].isupper() and value <= 30 \
                        and (title or len(numeral) >= 2 and value >= 11)
                elif before[-1].lower() in centuries or noun is not None:
                    key = before[-1].lower() if before[-1].lower() in centuries else noun
                    reads = in_series(numeral, value, key, end)
                elif previous.text in not_names or not before[-1][0].isupper():
                    reads = False
                elif function_word and len(numeral) >= 2 and value <= 100 \
                        and (noun_after := _noun_after(text, end, previous.text, request)) is not None:
                    reads = numeral not in numeral_words and not is_word
                    if reads:
                        request.memo.setdefault("pt_roman_before_noun", {})[start] = noun_after
                elif function_word:
                    reads = len(numeral) >= 2 and 11 <= value <= 30 and not is_word
                elif title:
                    reads = value <= 30
                else:
                    reads = len(numeral) >= 2 and not is_word and value <= 30
            if reads:
                if start in request.memo.get("pt_roman_before_noun", {}):
                    yield Span(start, end, Form.ROMAN, FrozenMap({"value": value, "role": "ordinal", "suffix": ""}),
                               recognizer=self.name)
                    continue
                yield self._span(start, end, value, data, key)
                if key is not None:
                    last_value = value
                    for member_start, member_end, member in _list_members(text, end, links):
                        member_value = roman_value(member) or 0
                        if member_value <= last_value or not in_series(member, member_value, key, member_end) \
                                or len(member) == 1 and _initial(text, member_end):
                            break
                        members[member_start] = key
                        last_value = member_value

    def _span(self, start: int, end: int, value: int, data, noun: str | None = None) -> Span:
        limit = data.get("roman_noun_ordinal_limits", {}).get(noun, data["roman_ordinal_limit"])
        role = "ordinal" if value <= limit else "cardinal"
        return Span(start, end, Form.ROMAN, FrozenMap({"value": value, "role": role, "suffix": ""}),
                    recognizer=self.name)


@dataclass(frozen=True)
class Abbreviation(CoreAbbreviation):
    """The shared abbreviations, with `D.` before a name and the keys of `abbreviations_any_case`, which also read
    in lowercase, as in `dr. Silva`. A title whose full stop ends the text also ends the sentence, so it keeps the
    full stop as the trail of the span: `Falei com a sra.` reads "Falei com a senhora." (Dicio, "Quando usar ponto
    final": "Quando o período termina com uma abreviatura, o ponto acumula duas funções: indicá-la e finalizar a
    frase"). A line break is no end of the text, because the name can follow on the next line."""

    def find(self, text: str, tokens: Sequence[Token], request: Request) -> Iterator[Span]:
        titles = {*request.data["titles"], *request.data["abbreviations_any_case"]}
        for span in super().find(text, tokens, request):
            if span.fields["key"] in titles and not text[span.end:].strip():
                span = replace(span, trail=".")
            yield span

    def refuses(self, text: str, position: int, table: str, data) -> bool:
        """`D.` after a noun of `letter_label_nouns` is the letter D and a full stop, as in `a vitamina D. Boa
        noite.`"""
        head = text[:position]
        words = head.split()
        return table == "honorific_before_name" and head[-1:].isspace() and bool(words) \
            and words[-1].lower() in data["letter_label_nouns"]

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
    recognizers=(SHARED["lexicon"], SHARED["electronic"], Telephone(declines=True), SHARED["color"], DateNamed(),
                 SHARED["date_numeric"],
                 Clock(), SpacedMoney(), SpacedRange(), SpacedNumber(), SpacedDecimal(), TELEPHONE, Money(),
                 SHARED["kept_money"], SHARED["percent"], PointMeasure(), SHARED["expression"], SHARED["fraction"],
                 SHARED["range"], Ordinal(), Roman(), Abbreviation(),
                 Letters(known_word=_known_word, titles=frozenset(DATA["honorific_before_name"])), PointDecimal(),
                 SpelledDecimal(), Cardinal(), SHARED["emoji"], SHARED["symbol"]),
    verbalizers={
        Form.LEXICON: speak_lexicon, Form.COLOR: speak_color, Form.DATE: speak_date, Form.TIME: speak_time,
        Form.TELEPHONE: speak_telephone, Form.MONEY: speak_money, Form.PERCENT: speak_percent,
        Form.MEASURE: speak_measure, Form.EXPRESSION: speak_expression, Form.FRACTION: speak_fraction,
        Form.RANGE: speak_range,
        Form.ORDINAL: speak_ordinal, Form.ROMAN: speak_roman, Form.ABBREVIATION: speak_abbreviation,
        Form.DECIMAL: speak_point_decimal, Form.CARDINAL: speak_cardinal, Form.LETTERS: speak_letters,
        Form.ELECTRONIC: speak_electronic, Form.SYMBOL: speak_symbol, Form.EMOJI: speak_emoji,
    },
    writers=("numtag", "tugalex", parsers.DATES),
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
