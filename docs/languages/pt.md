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

The test rows in `tests/data/pt.tsv` and `tests/data/electronic/pt.tsv` name their source, and no native speaker has checked them. Of the 293 rows in `tests/data/pt.tsv`, 13 are marked silver.

## Runs of capital letters

A run that splits into Portuguese syllables stays as written, and any other run reads each letter by its name. In Portuguese, a consonant can also stand where a reader adds a vowel. A table in the language file holds the runs that the rule reads wrong: `EUA`, `APPO` and `OCDE` read letter by letter.

| Written | Spoken (`pt-PT`, `LETTERS` on) | Note |
| --- | --- | --- |
| `O PIB e a TAP.` | stays as written | A consonant stands where a reader adds a vowel. |
| `A CIAV, a OVNI e os PALOP.` | stays as written | The same rule. |
| `Os EUA e a OCDE.` | Os é u á e a ó cê dê é. | The table spells them. |
| `O IBGE.` | stays as written | Limit: no source in the language file names it, so the rule reads it as a word. |
| `DIV, CIV e LIV.` | dê i vê, cê i vê e éle i vê. | Limit: a well-formed Roman numeral is spelled. |
| `A WEB.` | A dâblio é bê. | Limit: Portuguese has no onset or coda with `k`, `w` or `y`, which AO1990 keeps for foreign names. |
| `geral@RTP.pt` | geral@érre tê pê.pt | Limit: Portuguese has no address form, so the form spells only the run in an address. |
| `INSTITUTO` | i éne ésse tê i tê u tê ó | Limit: a syllable inside a run closes with one consonant, so a word that needs two consonants at the end of a syllable (ins-ti-tu-to) reads letter by letter. |
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
