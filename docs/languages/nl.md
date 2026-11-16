# Dutch

The file `text2spoken/lang/nl.py` reads Dutch. Install `text2spoken[nl]` for its number words, which come from `ovos-number-parser`.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, expressions, money, measures, percentages, abbreviations, symbols, emoji and lexicon entries. Dutch has no grammatical gender that changes a number word, so the file declares none.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Er zijn 21 katten en 43 honden.` | `nl-NL` | Er zijn eenentwintig katten en drieënveertig honden. |
| `Ik moet rijden, dus ik neem maar 1 biertje.` | `nl-NL` | Ik moet rijden, dus ik neem maar één biertje. |
| `Hij werd 1e en zij werd 3de.` | `nl-NL` | Hij werd eerste en zij werd derde. |
| `Het is haar 101ste overwinning.` | `nl-NL` | Het is haar honderdeerste overwinning. |
| `Er is sprake van 6,3 procent huurstijging.` | `nl-BE` | Er is sprake van zes komma drie procent huurstijging. |
| `Ongeveer 2/3 van de tekst werd herschreven.` | `nl-NL` | Ongeveer twee derde van de tekst werd herschreven. |
| `Een percentage van 25%.` | `nl-NL` | Een percentage van vijfentwintig procent. |
| `Het kost € 5,–.` | `nl-NL` | Het kost vijf euro. |
| `Het budget is € 25 miljoen.` | `nl-NL` | Het budget is vijfentwintig miljoen euro. |
| `Het saldo is € -12.` | `nl-NL` | Het saldo is min twaalf euro. |
| `Het kost € 2,50.` | `nl-NL` | Het kost twee euro vijftig. |
| `Een blikje kost € 0,50.` | `nl-NL` | Een blikje kost vijftig cent. |
| `Er zijn 10 000 mensen.` | `nl-BE` | Er zijn tienduizend mensen. |
| `De grens is 10 000 km lang.` | `nl-NL` | De grens is tienduizend kilometer lang. |
| `Hij liep 5 km.` | `nl-NL` | Hij liep vijf kilometer. |
| `Het is 25 °C.` | `nl-SR` | Het is vijfentwintig graden Celsius. |
| `2 + 2 = 4` | `nl-NL` | twee plus twee is vier |
| `Ik sprak prof. dr. Jansen.` | `nl-NL` | Ik sprak professor doctor Jansen. |
| `Mevr. de Vries is 60 jaar.` | `nl-NL` | Mevrouw de Vries is zestig jaar. |
| `Ik heb appels, peren, enz.` | `nl-NL` | Ik heb appels, peren, enzovoort. |
| `Zie blz. 12.` | `nl-NL` | Zie bladzijde twaalf. |

An ordinal takes the ending `e`, or the ending `de` or `ste` of its ordinal word, so `3de` and `21ste` read and `3ste` stays as written. An amount in euros with cents reads the euros, the currency name and then the cents, the short form that Onze Taal gives. Below one euro it reads in cents. A number can have a full stop or a space between its groups of three digits. A first group that starts with 0, as in the phone number `020 123 456`, is no group of a number, so the text stays as written. The titles `dr.`, `drs.`, `ir.`, `prof.` and `mr.` read as their full words anywhere, and `ing.` only before a capital, because it also abbreviates "ingenaaid" and "ingeënt".

## Varieties

| Tag | Notes |
| --- | --- |
| `nl-NL` (the default variety) | `$` reads "dollar". |
| `nl-BE` | `$` reads "dollar". |
| `nl-SR` | `$` reads "Surinaamse dollar", the currency that CLDR gives to `$` in Suriname. |

| Written | Tag | Spoken |
| --- | --- | --- |
| `Het kost $ 5.` | `nl-NL` | Het kost vijf dollar. |
| `Het kost $ 5.` | `nl-SR` | Het kost vijf Surinaamse dollar. |

The varieties also take their currency and unit names from the CLDR data of their own locale.

## Options

| Option | Values | Default (`nl-NL`) |
| --- | --- | --- |
| `date_order` | changes nothing | - |
| `clock` | changes nothing | - |
| `minute_style` | changes nothing | - |
| `decimal_mark` | changes nothing | - |
| `scale` | changes nothing | - |
| `default_gender` | changes nothing | - |
| `phone_regions` | changes nothing | - |
| `register` | changes nothing | - |

The file always reads the comma as the decimal mark and the full stop as the group mark. For every value of `scale`, ovos-number-parser reads 10^9 as "miljard" and 10^12 as "biljoen".

## Sources

The rules cite the advice pages of the Nederlandse Taalunie (taaladvies.net), the advice pages of Genootschap Onze Taal and the Dutch Wiktionary. Currency names, unit names and the names of symbols and emoji come from CLDR 49. The docstring of [`nl.py`](../../text2spoken/lang/nl.py) quotes the page of each rule.

Each of the 83 rows in `tests/data/nl.tsv` cites a source. 13 guard rows pin text that the file leaves as written, because a wrong reading is worse than none. No native speaker has checked the rows.

## Limits

Dutch leaves these forms as written or reads them in a limited way:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `In 2350 wonen 4002 mensen.` | `nl-NL` | In tweeduizenddriehonderdvijftig wonen vierduizendtwee mensen. | Taaladvies.net writes a space after "duizend", as in "vierduizend twee". ovos-number-parser writes none. The sound is the same. |
| `De 2022e keer.` | `nl-NL` | De tweeduizendtweeëntwintigste keer. | The same rule for an ordinal: Onze Taal writes "tweeduizend tweeëntwintigste". |
| `De 1000000e bezoeker.` | `nl-NL` | stays as written | An ordinal above 999999 stays as written. CLDR writes "eenmiljoenste", and Taaladvies.net writes "vier miljoenste" with no "een" before a million. |
| `Het 3ste boek.` | `nl-NL` | stays as written | The ordinal word of 3 is "derde", so the ending `ste` does not fit it. |
| `Ik had nog maar 1/2 fles water over.` | `nl-NL` | stays as written | The word for a half takes the form "halve" before some nouns, and the file does not know the noun. |
| `Het kost $ 2,50.` | `nl-NL` | Het kost twee komma vijf nul dollar. | Only an amount in euros reads its cents, because the source gives the spoken form for the euro only. |
| `Hij is 1,80 m lang.` | `nl-NL` | Hij is één komma acht nul meter lang. | Each digit after the decimal comma reads alone, as the CLDR spell-out rule of Dutch gives. |
| `In 1998.` | `nl-NL` | In duizendnegenhonderdachtennegentig. | A year reads as a cardinal, because ovos-date-parser reads no Dutch year. Onze Taal gives the year reading "negentienhonderdachtennegentig". |
| `Op 12-03-2024 om 14.30 uur.` | `nl-NL` | stays as written | ovos-date-parser reads no Dutch date or time, so a numeric date and a clock time stay as written. |
| `Een groei van 12 000 %.` | `nl-NL` | stays as written | A number with spaces between its groups stays as written before a percent sign, a dimension mark or a decimal comma. |
| `Bel 020 123 456.` | `nl-NL` | stays as written | A phone number stays as written. |
| `Een kamer van 3 × 4 m.` | `nl-NL` | stays as written | No source gives the Dutch word for the dimension mark. |
| `Het is 5 min lopen.` | `nl-NL` | Het is vijf min lopen. | `min` is also the word "min", so the file does not read it as a unit. |
| `Het kost 20 DKK.` | `nl-NL` | Het kost twintig DKK. | A currency code other than `EUR` stays as written. |
| `Ik sprak Mr. Smith.` | `nl-NL` | stays as written | `Mr.` with a capital is also the English title, so only the lowercase `mr.` reads "meester". |

---
[← French](fr.md) · [Home](../index.md) · [Portuguese →](pt.md)
