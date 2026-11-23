# Portuguese

The file `text2spoken/lang/pt.py` reads Portuguese. Install it with `text2spoken[pt]`, which adds `tugalex` for the gender of nouns and given names.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, ranges, expressions, dates, times, money, measures, percentages, telephone numbers, abbreviations, Roman numerals, colours, e-mail and web addresses, symbols and lexicon entries, and with the form on, runs of capital letters and emoji.

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

A number right after a noun that names one item of a series, such as `sala`, `página`, `artigo` or `Fig.`, reads in the masculine when no noun that it counts follows, because the word "número" is left out (Cunha and Cintra, quoted in Ciberdúvidas 33468). After `a páginas`, the number agrees with the plural noun (Bechara, quoted in Ciberdúvidas 33527). A number before `da tarde` counts hours. A number before `vezes` or `vírgula` and a second number reads in the masculine, unless a noun follows the second number and then `vezes` is the noun it counts. Two numbers that `a`, `e` or `ou` join stay as written when the noun after the second number gives the first number another gender, because no source gives that gender. An amount of money with one decimal reads the decimal as tens of cents. After `vitamina`, `grupo` or `classe`, `D.` is a letter, not a title.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Fica na sala 2, porta 4.` | `pt-PT` | Fica na sala dois, porta quatro. |
| `Está a páginas 21 da obra.` | `pt-PT` | Está a páginas vinte e uma da obra. |
| `Já são 2 da tarde.` | `pt-BR` | Já são duas da tarde. |
| `2 vezes 2 são 4.` | `pt-PT` | dois vezes dois são quatro. |
| `Mede (1) vírgula 5 m.` | `pt-PT` | Mede (um) vírgula cinco metros. |
| `O prazo é de 1 a 3 semanas.` | `pt-PT` | stays as written |
| `O bilhete custa 12,5 €.` | `pt-PT` | O bilhete custa doze euros e cinquenta cêntimos. |
| `Tome a vitamina D. Boa noite.` | `pt-PT` | stays as written |

The comma is the decimal mark. The full stop is the decimal mark of the English convention (Norma Portuguesa 9, quoted in Ciberdúvidas 12873). A decimal with a full stop reads only when something shows an amount: a minus or plus sign before it, or a unit symbol, a percent sign, a currency or the name of a unit after it. A unit of duration is no evidence, because `1.30 h` may write one hour and thirty minutes. Elsewhere the number stays as written, because such digits are a version, a section, a reference or an engine size as often as an amount.

A version reads with "ponto": after `versão`, `atualização` or `v`, and after the name of a product or a standard, such as `iOS`, `Windows` or `Python`. Each part reads as a cardinal. No source gives that reading, so its rows are silver. A name has a capital and a lowercase letter, and tugalex does not know it as a word. A capital that opens the sentence, a month, a weekday and a book of the Bible are no names, and neither is a word after a bracket or a number. A section number stays as written, also after a word such as `artigo`, `secção`, `figura` or `item`. ISO 2145, clause 4, says that the full stops of a section number are not spoken, and no source gives the Portuguese words. Digits with a leading zero after `vírgula` read as the digits of a decimal part.

| Written | Tag | Spoken |
| --- | --- | --- |
| `A temperatura é de 10.4 graus.` | `pt-PT` | A temperatura é de dez vírgula quatro graus. |
| `Corri 1.5 km.` | `pt-PT` | Corri um vírgula cinco quilómetros. |
| `O valor é -10.4.` | `pt-PT` | O valor é menos dez vírgula quatro. |
| `O valor é 10.4.` | `pt-PT` | stays as written |
| `A versão 14.2 está pronta.` | `pt-PT` | A versão catorze ponto dois está pronta. |
| `O iOS 17.4 trouxe novos emojis.` | `pt-PT` | O iOS dezassete ponto quatro trouxe novos emojis. |
| `A secção 3.2 explica.` | `pt-PT` | stays as written |
| `Durou 1.30 h.` | `pt-PT` | stays as written |
| `A taxa é 0 vírgula 02.` | `pt-PT` | A taxa é zero vírgula zero dois. |

The words of a date, a clock time and a year come from `ovos-date-parser`. A clock at 0:00 or 12:00 reads "meia-noite" or "meio-dia", and the article before it agrees with the noun. When the word stays as written, as after a lexicon entry for it, the time reads the hours that the word agrees with. A time with `h` reads the hours as written.

| Written | Spoken (`pt-PT`, `lexicon=FrozenMap({"pt": FrozenMap({"às": "às"})})`) |
| --- | --- |
| `Chega às 0:00.` | Chega às zero horas. |

A clock with a colon reads after a time word, such as `às`, `das` or the verb `são` (Priberam, "ser": "são 18h00"). A clock with no time word before it stays as written, because `16:10` may also be a ratio. `24:00` is the end of the day, and it reads as midnight.

| Written | Tag | Spoken |
| --- | --- | --- |
| `São 16:30.` | `pt-PT` | São dezasseis e trinta. |
| `Já são 12:00!` | `pt-PT` | Já são doze horas! |
| `Fecha às 24:00.` | `pt-PT` | Fecha à meia-noite. |

A length unit with `2` or `3` right after it writes its exponent on the line, so `80 m2` reads as `80 m²`.

| Written | Tag | Spoken |
| --- | --- | --- |
| `A casa tem 80m2.` | `pt-PT` | A casa tem oitenta metros quadrados. |
| `Tomar 500 mg por dia.` | `pt-PT` | Tomar quinhentos miligramas por dia. |

In `pt-PT`, the space is the group mark (Norma Portuguesa 9, quoted in Ciberdúvidas 12873). A run of spaced groups is also a code, such as a tax number or a Multibanco reference, so a spaced number reads only when its last group is `000` or when it has a decimal part. Any other spaced run stays as written. In `pt-BR`, the group mark is the full stop.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Tem 100 000 habitantes.` | `pt-PT` | Tem cem mil habitantes. |
| `Custa 1 250 000,50.` | `pt-PT` | Custa um milhão duzentos e cinquenta mil vírgula cinquenta. |
| `O NIF é 509 876 543.` | `pt-PT` | stays as written |

[Money, units and symbols](../money-units-and-symbols.md) describes the units, currencies and symbols of CLDR, which Portuguese reads. [Addresses, letters and emoji](../addresses-letters-and-emoji.md) describes the addresses and the emoji.

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

The test rows in `tests/data/pt.tsv` name their source, and no native speaker has checked them. Of the 731 rows, 26 are marked silver.

## Roman numerals

A Roman numeral reads after a century word, after a noun of a part, a class or a series, after a capitalised word, and after a title and its full stop. It reads as an ordinal up to ten and as a cardinal from eleven. In pt-BR, a numeral after `artigo` reads as an ordinal only up to nine. Celso Cunha, quoted in Migalhas, Gramatigalhas, "Numeral", gives the rule: "na numeração dos artigos de leis, decretos e portarias, usa-se o ordinal até nove, e o cardinal de dez em diante". The noun or the title before the numeral gives the gender. After a name, the gender comes from the title before it, then from a common noun that tugalex knows, then from the given-name list of tugalex, and a name that no list holds takes the masculine. After a capitalised word that is no noun of a series, the value is at most 30, and the word reads the numeral only when spaces alone part them. When a comma or another mark parts them, a numeral from 11 to 30 after a capitalised word reads as a cardinal, and a smaller one stays as written. After an article, as in `O XV de Portugal`, a numeral from 11 to 30 reads as a cardinal. A numeral of one letter, `I`, `V` or `X`, reads only after a noun of the `roman_letter_nouns` table: the parts of a work, such as `capítulo`, `livro`, `parte`, `cena`, `secção`, `canto`, `cláusula` and `artigo`. Ciberdúvidas 11716 applies the ordinal rule "a todas as partes em que se divide uma obra". A group, a class or a phase is labelled with letters too, so `Grupo I` stays as written. A numeral of the `roman_words` table, such as `XL`, `CL` or `MC`, is also a word or an initialism. It reads only after a noun of `roman_letter_nouns`, and only when no word in lowercase follows it, so after `classe` or `grupo` it stays as written. No numeral reads after a word of the `letter_words` table, such as the pronoun `EU`. In a clause in capitals, a numeral is a word only when `letter_words` holds it or tugalex knows it, as `VI` in `EU VI`. A list after a century word or a noun of a series reads with that noun: a comma and a space part its numerals, and `e` or `ou`, in any case, comes before the last one. Each numeral of the list passes the same checks as the first and holds a larger value than the numeral before it, and the list ends at the first numeral that fails. A numeral after a comma with no closing link word is no member, and it reads as a numeral after a comma reads. A letter that a full stop and a capitalised word follow is an initial, as `V.` in `V. Silva`. Without the `pt` extra, a Roman numeral stays as written, and one log warning names the extra.

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

## E-mail and web addresses

An address reads piece by piece. Each symbol reads by the name that Priberam or Ciberdúvidas gives it, such as "arroba" for `@` and "ponto" for `.`. A label of three or more letters with a vowel reads as a word. Any other label reads each letter by its name in AO1990, Base I. So `com` reads as a word and `pt` reads letter by letter, as Ciberdúvidas 19059 advises. A digit reads by its digit word. Three names differ by variety:

| Sign | `pt-PT` | `pt-BR` |
| --- | --- | --- |
| `_` | traço inferior | sublinha |
| `#` | cardinal | cerquilha |
| `w` | dâblio | dáblio |

A full stop, a comma or another mark at the end of an address stays with the sentence. The docstring of [`_pt_electronic.py`](../../text2spoken/lang/_pt_electronic.py) quotes each source.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Escreva para joao.silva@exemplo.pt hoje.` | `pt-PT` | Escreva para joao ponto silva arroba exemplo ponto pê tê hoje. |
| `Escreva a maria_santos@exemplo.pt.` | `pt-PT` | Escreva a maria traço inferior santos arroba exemplo ponto pê tê. |
| `Escreva a maria_santos@exemplo.pt.` | `pt-BR` | Escreva a maria sublinha santos arroba exemplo ponto pê tê. |
| `Acesse www.gov.br hoje.` | `pt-BR` | Acesse dáblio dáblio dáblio ponto gov ponto bê érre hoje. |
| `O Sr. Silva escreveu a silva@exemplo.pt.` | `pt-PT` | O Senhor Silva escreveu a silva arroba exemplo ponto pê tê. |

To keep an address as written, pass `NormalizationParams().without(Form.ELECTRONIC)`.

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
| `geral@RTP.pt` | geral arroba érre tê pê ponto pê tê | The address form reads the whole address. `RTP` has no vowel, so it reads letter by letter. |
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
| `Veja www.x.pt/5µm` | Veja dâblio dâblio dâblio ponto xis ponto pê tê barra cinco µm | No unit reads inside an address. `µ` has no name in the address tables, so it stays as written. |
| `x@a©b.pt` | xis arroba á direitos de autor bê ponto pê tê | A symbol of CLDR inside an address reads by its CLDR name. |

The edge cases that Portuguese shares with English are on the [Money, units and symbols](../money-units-and-symbols.md#limits) and [Addresses, letters and emoji](../addresses-letters-and-emoji.md#edge-cases) pages.

---
[← Dutch](nl.md) · [Home](../index.md) · [Russian →](ru.md)
