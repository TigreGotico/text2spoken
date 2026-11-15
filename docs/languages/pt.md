# Portuguese

The file `text2spoken/lang/pt.py` reads Portuguese. Install it with `text2spoken[pt]`, which adds `ovos-number-parser`, `ovos-date-parser` and `tugalex`.

## Varieties and codes

| Tag | Notes |
| --- | --- |
| `pt-PT` | The default variety. A bare `pt` reads as `pt-PT`. The long scale: `10^9` reads "mil milhões" |
| `pt-BR` | The short scale: `10^9` reads "um bilhão" |

Every other `pt-*` tag reads the variety that `linguatag.closest_lang` gives it, so `pt-AO` and `pt-MZ` read `pt-PT`.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, ranges, expressions, dates, times, money, measures, percentages, telephone numbers, abbreviations, Roman numerals, colours, symbols and lexicon entries. With the form on, it also reads runs of capital letters and emoji. It has no address form.

A number agrees with the noun that it counts: `Tenho 2 casas e 2 carros.` reads "Tenho duas casas e dois carros." The gender of a common noun comes from the noun lexicon of `tugalex`. A Portuguese number takes the gender of its unit, so `2 h` reads "duas horas".

The words of a date, a clock time and a year come from `ovos-date-parser`. A clock at 0:00 or 12:00 reads "meia-noite" or "meio-dia", and the article before it agrees with the noun: `às 0:00` reads "à meia-noite", `das 12:00` reads "do meio-dia", and `entre as 0:00` reads "entre a meia-noite". When the word stays as written, as after a lexicon entry for it, the time reads the hours that the word agrees with: "às zero horas". A time with `h` reads the hours as written, so `às 0h` reads "às zero horas" in `pt-PT`.

[How it reads text](../how-it-reads.md) describes the emoji, and the units, currencies and symbols of CLDR, which Portuguese reads.

## Sources

The rules cite the Acordo Ortográfico de 1990, Priberam, Ciberdúvidas, Dicio, the Gramática do Português and the CLDR 49 data of `pt-PT` and `pt`. The docstring of [`pt.py`](../../text2spoken/lang/pt.py) quotes each source.

The test rows in `tests/data/pt.tsv` and `tests/data/electronic/pt.tsv` name their source, and no native speaker has checked them. Of the 283 rows in `tests/data/pt.tsv`, 13 are marked silver.

## Runs of capital letters

A run that splits into Portuguese syllables stays as written, and any other run reads each letter by its name. In Portuguese, a consonant can also stand where a reader adds a vowel, so `PIB`, `TAP`, `CIAV`, `OVNI` and `PALOP` read as words. A table in the language file holds the runs that the rule reads wrong: `EUA`, `APPO` and `OCDE` read letter by letter in Portuguese.

Known limits of the form in Portuguese:

- Portuguese reads some initialisms as words that a reader spells, because no source in the language file names them: `IBGE` stays as written. A well-formed Roman numeral is spelled, so `DIV`, `CIV` and `LIV` read letter by letter.
- Portuguese has no onset or coda with `k`, `w` or `y`, which AO1990 keeps for foreign names. So `WEB` reads "dâblio é bê" in pt-PT.
- Portuguese has no address form, so the form spells only the run in an address. `geral@RTP.pt` reads "geral@érre tê pê.pt" in pt-PT.
- A Portuguese syllable inside a run closes with one consonant. So a word in capitals that needs two consonants at the end of a syllable reads letter by letter: `INSTITUTO` (ins-ti-tu-to) reads "i éne ésse tê i tê u tê ó".
- The Portuguese rule reads some runs that Wiktionary spells, such as `EPI` ({{pt-IPA|ê-pê-i}}) and `ODE` ({{pt-IPA|ó-dê-é}}). It spells some runs that Wiktionary reads as words, such as `WAN`, because `w` starts no Portuguese syllable.
- A span that waits on a joined character on the first pass can read on a second pass, after the form spells a run next to it. `Sala 9#D. RTP.` reads "Sala 9#D. érre tê pê.", and a second pass reads "nove".

The limits that Portuguese shares with English are on the [How it reads text](../how-it-reads.md#runs-of-capital-letters) page.

## Limits of units, currencies and symbols

Some unit readings are wrong or stay as written:

- Portuguese `min` and `s` read as units also where they abbreviate other words. `12 min e 20 máx.` reads "doze minutos", and `2 s/ uso` reads "dois segundos/ uso".
- A pt-BR decimal below 2 takes the singular, by the CLDR plural rule. `1,5 min` reads "um vírgula cinco minuto".
- A decimal takes no unit gender. `2,5h` reads "dois vírgula cinco horas".
- `1,5h` reads, but `1,5 h` with a space stays as written.
- Portuguese has no address form, so a unit inside a Portuguese address reads as a measure. `Veja www.x.pt/5µm` reads "www.x.pt/cinco micrómetros".
- For the same reason, a symbol inside a Portuguese address reads by its name. `x@a©b.pt` reads "x@a direitos de autor b.pt".

Some currency and symbol readings are wrong or stay as written:

- A symbol name is the CLDR name, with no agreement and no context. `8 ÷ 2` reads "oito sinal de divisão dois" in Portuguese.
- Portuguese text in capitals cannot tell the city Córdoba from the currency, because the currency gender entry matches the word as written. So `PAGUEI 2 CÓRDOBAS.` reads "duas", and `Paguei 2 córdobas.` reads "dois".
- The Portuguese paʻanga reads as a feminine noun, so `2 T$` reads "duas paʻangas tonganesas". The CLDR adjective "tonganesas" agrees with it, but Priberam gives a masculine noun: "paanga": "nome masculino [...] Unidade monetária de Tonga (código: TOP)".
- A doubled mark reads its singular name twice. `Veja os §§ 2 e 3.` reads "Veja os parágrafo parágrafo dois e três".

The limits that Portuguese shares with English are on the [How it reads text](../how-it-reads.md#units-currencies-and-symbols) page.

---
[← Basque](eu.md) · [Home](../index.md) · [Russian →](ru.md)
