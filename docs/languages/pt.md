# Portuguese

The file `text2spoken/lang/pt.py` reads Portuguese. Install it with `text2spoken[pt]`, which adds `ovos-number-parser`, `ovos-date-parser` and `tugalex`.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, ranges, expressions, dates, times, money, measures, percentages, telephone numbers, abbreviations, Roman numerals, colours, symbols and lexicon entries. With the form on, it also reads runs of capital letters and emoji. It has no address form.

| Written | Tag | Spoken |
| --- | --- | --- |
| `O Dr. Silva pagou 2,50 € às 14:30.` | `pt-PT` | O Doutor Silva pagou dois euros e cinquenta cêntimos às catorze e trinta. |
| `Tenho 2 casas e 2 carros.` | `pt-PT` | Tenho duas casas e dois carros. |
| `Demora 2 h.` | `pt-PT` | Demora duas horas. |
| `Pagou 1000000000 €.` | `pt-PT` | Pagou mil milhões de euros. |
| `Pagou 1000000000 €.` | `pt-BR` | Pagou um bilhão de euros. |
| `Chega às 0:00.` | `pt-PT` | Chega à meia-noite. |
| `Fecha às 12:00.` | `pt-PT` | Fecha ao meio-dia. |
| `Abre das 12:00 às 14:00.` | `pt-PT` | Abre do meio-dia às catorze horas. |
| `Fica entre as 0:00 e as 2:00.` | `pt-PT` | Fica entre a meia-noite e as duas horas. |
| `Chega às 0h.` | `pt-PT` | Chega às zero horas. |
| `Luís XIV reinou no século XVII.` | `pt-PT` | Luís Catorze reinou no século dezassete. |
| `A Sra. Sousa e a Dr.ª Lima.` | `pt-PT` | A Senhora Sousa e a Doutora Lima. |
| `Custa 250 000 €.` | `pt-PT` | Custa duzentos e cinquenta mil euros. |
| `O saldo é de -1 500 €.` | `pt-PT` | O saldo é de menos mil e quinhentos euros. |
| `Falei com a sra.` | `pt-PT` | Falei com a senhora. |

A number agrees with the noun that it counts. The gender of a common noun comes from the noun lexicon of `tugalex`, and a number before a unit takes the gender of the unit.

The words of a date, a clock time and a year come from `ovos-date-parser`. A clock at 0:00 or 12:00 reads "meia-noite" or "meio-dia", and the article before it agrees with the noun. When the word stays as written, as after a lexicon entry for it, the time reads the hours that the word agrees with. A time with `h` reads the hours as written.

| Written | Spoken (`pt-PT`, `lexicon=FrozenMap({"pt": FrozenMap({"às": "às"})})`) |
| --- | --- |
| `Chega às 0:00.` | Chega às zero horas. |

[Money, units and symbols](../money-units-and-symbols.md) describes the units, currencies and symbols of CLDR, which Portuguese reads. [Addresses, letters and emoji](../addresses-letters-and-emoji.md) describes the emoji.

## Varieties

| Tag | Notes |
| --- | --- |
| `pt-PT` | The default variety. A bare `pt` reads as `pt-PT`. The long scale: `10^9` reads "mil milhões" |
| `pt-BR` | The short scale: `10^9` reads "um bilhão" |

Every other `pt-*` tag reads the variety that `linguatag.closest_lang` gives it, so `pt-AO` and `pt-MZ` read `pt-PT`.

## Options

| Option | Values | Default (`pt-PT`) | Default (`pt-BR`) |
| --- | --- | --- | --- |
| `date_order` | `DMY`, `MDY`, `YMD` | `DMY` | `DMY` |
| `clock` | `24h` | `24h` | `24h` |
| `minute_style` | `number` | `number` | `number` |
| `decimal_mark` | `,`, `.` | `,` | `,` |
| `scale` | `long`, `short` | `long` | `short` |
| `default_gender` | `feminine`, `masculine` | `masculine` | `masculine` |
| `phone_regions` | `AE`, `BR`, `EG`, `ES`, `FR`, `GB`, `PT`, `SA`, `US` | `PT` | `BR` |
| `register` | changes nothing | - | - |

## Sources

The rules cite the Acordo Ortográfico de 1990, Priberam, Ciberdúvidas, Dicio, the Gramática do Português, Correia and San Payo de Lemos, Mendes, Oliveira and Teixeira, Viana et al., Cristófaro Silva, and the CLDR 49 data of `pt-PT` and `pt`. The docstring of [`pt.py`](../../text2spoken/lang/pt.py) quotes each source.

The test rows in `tests/data/pt.tsv` and `tests/data/electronic/pt.tsv` name their source, and no native speaker has checked them. Of the 482 rows in `tests/data/pt.tsv`, 15 are marked silver.

## Roman numerals

A Roman numeral reads after a century word, after a noun of a part, a class or a series, after a capitalised word, and after a title and its full stop. It reads as an ordinal up to ten and as a cardinal from eleven. Ciberdúvidas 9067 gives the pt-BR limit: "os numerais se pronunciarem em Portugal como ordinais até ao décimo, inclusive (no Brasil até ao nono)". The noun or the title before the numeral gives the gender. After a name, the gender comes from the title before it, then from a common noun that tugalex knows, then from the given-name list of tugalex, and a name that no list holds takes the masculine. After a capitalised word that is no noun of a series, the value is at most 30, and the word reads the numeral only when spaces alone part them. When a comma or another mark parts them, a numeral from 11 to 30 after a capitalised word reads as a cardinal, and a smaller one stays as written. After an article, as in `O XV de Portugal`, a numeral from 11 to 30 reads as a cardinal. A numeral of one letter, `I`, `V` or `X`, reads only after a noun of the `roman_letter_nouns` table: the parts of a work, such as `capítulo`, `livro`, `parte`, `cena`, `secção`, `canto`, `cláusula` and `artigo`. Ciberdúvidas 11716 applies the ordinal rule "a todas as partes em que se divide uma obra". A group, a class or a phase is labelled with letters too, so `Grupo I` stays as written. A numeral of the `roman_words` table, such as `XL`, `CL` or `MC`, is also a word or an initialism. It reads only after a noun of `roman_letter_nouns`, and only when no word in lowercase follows it, so after `classe` or `grupo` it stays as written. No numeral reads after a word of the `letter_words` table, such as the pronoun `EU`. In a clause in capitals, a numeral is a word only when `letter_words` holds it or tugalex knows it, as `VI` in `EU VI`. A list after a century word or a noun of a series reads with that noun: a comma and a space part its numerals, and `e` or `ou`, in any case, comes before the last one. Each numeral of the list passes the same checks as the first and holds a larger value than the numeral before it, and the list ends at the first numeral that fails. A numeral after a comma with no closing link word is no member, and it reads as a numeral after a comma reads. A letter that a full stop and a capitalised word follow is an initial, as `V.` in `V. Silva`. Without the `pt` extra, a Roman numeral stays as written, and one log warning names the extra.

| Written | Tag | Spoken | Note |
| --- | --- | --- | --- |
| `A parte III do livro.` | `pt-PT` | A parte terceira do livro. | The noun gives the gender. |
| `Veja o artigo XXIII.` | `pt-PT` | Veja o artigo vinte e três. | A cardinal from eleven. |
| `Leia o capítulo V e VI.` | `pt-PT` | Leia o capítulo quinto e sexto. | A list after a noun of a series. |
| `Dos séculos XI, XII e XIII.` | `pt-PT` | Dos séculos onze, doze e treze. | A list after a century word. |
| `No Grupo II, CD Tondela venceu.` | `pt-PT` | No Grupo segundo, CD Tondela venceu. | No link word closes a list, so `CD` stays as written. |
| `Comprei um Mercedes Classe CL usado.` | `pt-PT` | stays as written | `CL` is an initialism of `roman_words`, and a word in lowercase follows it. |
| `Leia o capítulo XL.` | `pt-PT` | Leia o capítulo quarenta. | `XL` is a word of `roman_words`, and no word follows it. |
| `A Classe CL.` | `pt-PT` | stays as written | A class is labelled with letters too. |
| `No século XIX, XX pessoas morreram.` | `pt-PT` | No século dezanove, Vinte pessoas morreram. | `XX` is no member of a list, and it reads as a numeral from 11 to 30 after a comma. |
| `A cena V começa.` | `pt-PT` | A cena quinta começa. | One letter after a part of a work. |
| `O Grupo II joga hoje.` | `pt-PT` | O Grupo segundo joga hoje. | Two letters after a noun of a series. |
| `No Grupo I, houve duas goleadas.` | `pt-PT` | stays as written | A group is labelled with letters too. |
| `Veja o artigo X.` | `pt-PT` | Veja o artigo décimo. | pt-PT reads the tenth as an ordinal. |
| `Veja o artigo X.` | `pt-BR` | Veja o artigo dez. | pt-BR reads it as a cardinal. |
| `Isabel II reinou.` | `pt-PT` | Isabel Segunda reinou. | After a name, the numeral agrees with the name and takes a capital. |
| `A Dra. IV saiu.` | `pt-PT` | A Doutora Quarta saiu. | After a title and its full stop, the title gives the gender. |
| `A classe A viaja.` | `pt-PT` | stays as written | A class is labelled with letters. |
| `Fui a Washington DC.` | `pt-PT` | stays as written | After a capitalised word, a numeral reads only up to 30, so the acronym `DC` stays as written. |
| `O XV de Portugal venceu.` | `pt-PT` | O Quinze de Portugal venceu. | After an article, a numeral from 11 to 30 reads as a cardinal. |
| `Ligações para a Região III.` | `pt-PT` | Ligações para a Região Terceira. | tugalex gives the gender of the noun "região". |
| `Lei III foi aprovada.` | `pt-PT` | Lei Terceira foi aprovada. | A common noun gives the gender before the given-name list. |
| `Vi o Godzilla II no cinema.` | `pt-PT` | Vi o Godzilla Segundo no cinema. | A name that no list holds takes the masculine. |
| `EU LI O LIVRO` | `pt-PT` | stays as written | `LI` follows the pronoun `EU`, and `letter_words` holds it, the verb form of "ler". |

## Runs of capital letters

A run that splits into Portuguese syllables stays as written, and any other run reads each letter by its name. In Portuguese, a consonant can also stand where a reader adds a vowel. A table in the language file holds the runs that the rule reads wrong: `EUA`, `APPO`, `OCDE`, `ANS` and `ONS` read letter by letter. A syllable can close with `ns`, as AO1990 Base XX divides "ins- crição" and "trans- gredir".

A run of three letters or more that tugalex knows reads as a word anywhere. A clause in capitals is the text between two marks of a clause where every word with a letter is in capitals, and that holds two words or more. A word is a run that reads as a word, so a code that reads letter by letter, such as `AGR` in `AO 1334 AGR`, does not count. In a clause in capitals, a word of the `letter_words` table, or a two-letter word form that tugalex knows, reads as a word. Without the `pt` extra, only `letter_words` reads, and one log warning names the missing extra.

| Written | Spoken (`pt-PT`, `LETTERS` on) | Note |
| --- | --- | --- |
| `O PIB e a TAP.` | stays as written | A consonant stands where a reader adds a vowel. |
| `A CIAV, a OVNI e os PALOP.` | stays as written | The same rule. |
| `Os EUA e a OCDE.` | Os é u á e a ó cê dê é. | The table spells them. |
| `O IBGE.` | stays as written | Limit: no source in the language file names it, so the rule reads it as a word. |
| `O DIV, o CIV e o LIV.` | O dê i vê, o cê i vê e o éle i vê. | Limit: a well-formed Roman numeral that the `ROMAN` form does not read is spelled. |
| `A WEB.` | A dâblio é bê. | Limit: Portuguese has no onset or coda with `k`, `w` or `y`, which AO1990 keeps for foreign names. |
| `geral@RTP.pt` | geral@érre tê pê.pt | Limit: Portuguese has no address form, so the form spells only the run in an address. |
| `EU VI O FILME` | stays as written | A clause in capitals: `letter_words` holds `VI`, the verb form of "ver". |
| `AR CONDICIONADO` | stays as written | A clause in capitals: tugalex knows "ar". |
| `INSTITUTO DE ESTUDOS` | stays as written | The run splits into ins-ti-tu-to. |
| `Visitei o INSTITUTO.` | stays as written | The same rule, outside a clause. |
| `O AR` | stays as written | `O` counts as a word of the clause. |
| `A EM é uma doença.` | A é éme é uma doença. | Words in lower case make no clause, so the initialism is spelled. |
| `A ANS propõe regras.` | A á éne ésse propõe regras. | The table spells it. |
| `Eu LI o livro.` | Eu éle i o livro. | Limit: a run of two letters outside a clause in capitals reads letter by letter, so a word written in capitals for stress is spelled. |
| `DEPARTAMENTO DE TI` | stays as written | Limit: tugalex knows the pronoun "ti", so the acronym `TI` reads as the pronoun in a clause in capitals. |
| `EPI e ODE.` | stays as written | Limit: the rule reads some runs that Wiktionary spells, such as `EPI` ({{pt-IPA\|ê-pê-i}}) and `ODE` ({{pt-IPA\|ó-dê-é}}). |
| `A WAN.` | A dâblio á éne. | Limit: the rule spells some runs that Wiktionary reads as words, because `w` starts no Portuguese syllable. |

The limits that Portuguese shares with English are on the [Addresses, letters and emoji](../addresses-letters-and-emoji.md#runs-of-capital-letters) page.

## Limits

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `12 min e 20 máx.` | `pt-PT` | doze minutos e vinte máx. | `min` and `s` read as units also where they abbreviate other words. |
| `2 s/ uso` | `pt-PT` | dois segundos/ uso | The same rule. |
| `1,5 min` | `pt-BR` | um vírgula cinco minuto | A pt-BR decimal below 2 takes the singular, by the CLDR plural rule. |
| `2,5h` | `pt-PT` | dois vírgula cinco horas | A decimal takes no unit gender. |
| `1,5h` | `pt-PT` | um vírgula cinco horas | The unit `h` reads when it touches the number. |
| `1,5 h` | `pt-PT` | stays as written | With a space between the number and `h`, the measure stays as written. |
| `A Drª. Sousa.` | `pt-PT` | stays as written | The full stop of an abbreviation comes before the letter in superscript, as in `Dr.ª` (Dicio), so `Drª.` and `Dª` are no titles of the file. |
| `Custa 250 000 €.` | `pt-BR` | stays as written | A space reads as the group mark of an amount only in `pt-PT`, where CLDR gives it. CLDR gives the full stop for `pt-BR`. |
| `8 ÷ 2` | `pt-PT` | oito sinal de divisão dois | A symbol name is the CLDR name, with no agreement and no context. |
| `PAGUEI 2 CÓRDOBAS.` | `pt-PT` | PAGUEI duas CÓRDOBAS. | Text in capitals cannot tell the city Córdoba from the currency, because the currency gender entry matches the word as written. |
| `Paguei 2 córdobas.` | `pt-PT` | Paguei dois córdobas. | The comparison for the row above. |
| `Paguei 2 T$.` | `pt-PT` | Paguei duas paʻangas tonganesas. | The paʻanga reads as a feminine noun, and the CLDR adjective "tonganesas" agrees with it. Priberam gives a masculine noun: "paanga": "nome masculino [...] Unidade monetária de Tonga (código: TOP)". |

The limits that Portuguese shares with English are on the [Money, units and symbols](../money-units-and-symbols.md#limits) page.

## Edge cases

These cases come from tests that feed the library unusual text. A reader of ordinary prose rarely meets them.

| Written | Spoken (`pt-PT`, `LETTERS` on) | Second pass (`pt-PT`, `LETTERS` on) | Why |
| --- | --- | --- | --- |
| `Sala 9#D. RTP.` | Sala 9#D. érre tê pê. | Sala nove#D. érre tê pê. | A number that one character joins to other text stays as written on the first pass. It can read on a second pass, after the `LETTERS` form spells a run next to it. |

| Written | Spoken (`pt-PT`) | Why |
| --- | --- | --- |
| `Veja www.x.pt/5µm` | Veja www.x.pt/cinco micrómetros | Portuguese has no address form, so a unit inside a Portuguese address reads as a measure. |
| `x@a©b.pt` | x@a direitos de autor b.pt | For the same reason, a symbol inside a Portuguese address reads by its name. |

The edge cases that Portuguese shares with English are on the [Money, units and symbols](../money-units-and-symbols.md#limits) and [Addresses, letters and emoji](../addresses-letters-and-emoji.md#edge-cases) pages.

---
[← Basque](eu.md) · [Home](../index.md) · [Russian →](ru.md)
