# Money, units and symbols

This page shows how text2spoken reads sums of money, measures, percentages, symbols and colours. English and Portuguese take the words for units, currencies and symbols from the Unicode CLDR, release 49. The other languages give their own tables.

## Money

| Written | Tag | Spoken |
| --- | --- | --- |
| `Dr Smith paid £3.50.` | `en-GB` | Doctor Smith paid three pounds and fifty pence. |
| `It costs $5.` | `en-US` | It costs five dollars. |
| `Pagou 2,50 €.` | `pt-PT` | Pagou dois euros e cinquenta cêntimos. |
| `Paid R$ 500.` | `en-GB` | Paid five hundred Brazilian reals. |
| `Paguei ₹50.` | `pt-PT` | Paguei cinquenta rupias indianas. |
| `Paguei ₹50.` | `pt-BR` | Paguei cinquenta rupias indianas. |
| `Custou 180 mil €.` | `pt-PT` | Custou cento e oitenta mil euros. |
| `Pay CHF 20.` | `en-GB` | Pay twenty Swiss francs. |

A currency symbol before or after a number reads with the CLDR name of the currency. A scale word may stand between the number and a symbol after it, as `mil` does above. A symbol with a currency sign, such as `$`, `€` or `₹`, reads with no list. A symbol of letters, such as the ISO 4217 code `CHF`, reads only when the language file lists it in `currency_symbols`, so `L` and `TOP` stay as written here:

| Written | Spoken (`en-GB`) |
| --- | --- |
| `Buy 10 L of milk.` | Buy ten L of milk. |
| `The TOP 10 songs.` | The TOP ten songs. |

A symbol that two currencies share reads as the currency whose CLDR symbol it is. Where the CLDR name carries the country, as "US dollar", the language file names the currency, as "dollar", and gives its source. Portuguese writes each currency name with a small first letter. A currency whose CLDR name is no word, as the `¤` of "(unknown currency)", does not read.

An amount next to a currency sign that the language does not read stays as written, with its number, and the log names it. The number does not read alone, because the sign would then touch a word:

| Written | Tag | Spoken |
| --- | --- | --- |
| `Das kostet ¥5 und 5 €.` | `de-DE` | Das kostet ¥5 und fünf Euro. |

## Measures

| Written | Tag | Spoken |
| --- | --- | --- |
| `Drive at 5 km/h.` | `en-GB` | Drive at five kilometres per hour. |
| `It is 25°C.` | `en-GB` | It is twenty-five degrees Celsius. |
| `Load 10 kg/m².` | `en-GB` | Load ten kilograms per square metre. |
| `Pour 5 ml.` | `en-US` | Pour five milliliters. |
| `Um furo de 5 µm.` | `pt-PT` | Um furo de cinco micrómetros. |
| `Demora 2 h.` | `pt-PT` | Demora duas horas. |

A unit symbol that cannot be a word, such as `km/h`, `°C`, `kWh` or `µm`, reads with no list. A symbol made only of letters reads only when the language file lists it in `unit_symbols`, so `in` and `GB` stay as written here:

| Written | Spoken (`en-GB`) |
| --- | --- |
| `Only 1 in 3 passed.` | Only one in three passed. |
| `He won 29 GB golds.` | He won twenty-nine GB golds. |

A CLDR symbol of two capitals or more that touches the digits before it reads as a unit, with no list, because a run of capitals joined to digits is no word of running text. The `unjoined_symbols` table of the language holds the symbols that name something else when joined, as `CD` does in English, and `ML`, the CLDR megalitre, which a writer may mean as `mL`, the millilitre:

| Written | Tag | Spoken |
| --- | --- | --- |
| `I have 10GB free.` | `en-GB` | I have ten gigabytes free. |
| `Tenho 10GB livres.` | `pt-PT` | Tenho dez gigabytes livres. |
| `Uma central de 5MW.` | `pt-PT` | Uma central de cinco megawatts. |
| `A 2CD set.` | `en-US` | stays as written |
| `Usei 2ML de xarope.` | `pt-PT` | stays as written |

`a/b` reads with the CLDR `per` pattern, and `²` and `³` read with the square and cubic patterns. A listed symbol that differs from a CLDR symbol only in case reads as that unit: `ml` reads as the CLDR `mL`. A Portuguese number takes the gender of its unit, as `2 h` shows.

## Percentages

| Written | Tag | Spoken |
| --- | --- | --- |
| `Save 20%.` | `en-GB` | Save twenty per cent. |
| `Subiu 4,5 %.` | `pt-PT` | Subiu quatro vírgula cinco por cento. |

## Symbols

A character that no other form claims reads by its CLDR name. The character must be outside ASCII, with the Unicode general category `Sm`, `Sc`, `Sk` or `So`, or it must be one of `§ ¶ † ‡ •`. A language file may give its own name with a source: Portuguese reads `§` as "parágrafo".

| Written | Tag | Spoken |
| --- | --- | --- |
| `© 2024 ACME.` | `en-GB` | copyright two thousand and twenty-four ACME. |
| `Go → left.` | `en-GB` | Go right-pointing arrow left. |
| `See § 5.` | `pt-PT` | See parágrafo cinco. |

A name takes one space on each side where it touches a character that is no space. It takes no space after an opening bracket or quote, and none before a closing bracket or quote, a full stop or a comma. Before a phone number, a symbol counts as the words of its name:

| Written | Spoken (`en-GB`) |
| --- | --- |
| `See §§ 5.` | See section section five. |
| `Use ©-5.` | Use copyright minus five. |
| `Mark (©).` | Mark (copyright). |
| `Dial ☎000.` | Dial telephone zero zero zero. |
| `Dial telephone 000.` | Dial telephone zero zero zero. |

A character that a table of the language gives to another form, such as `°`, `‰`, `×` or a currency sign, belongs to that form wherever it stands. It stays as written when that form does not read it. An emoji with emoji presentation stays as written, and so does a character with U+FE0F, a skin tone or a zero width joiner after it. In an address, a character that the address tables do not name reads by its CLDR name.

| Written | Spoken (`en-GB`) |
| --- | --- |
| `Find the € sign.` | stays as written |
| `Add 3/4 ‰ now.` | stays as written |
| `Add 3/4 kg now.` | stays as written |
| `Mail a©b.com today.` | Mail a copyright bee dot com today. |

`NormalizationParams().without(Form.SYMBOL)` turns this form off.

## Colours

German, English and Portuguese read a hex colour code by the name of its colour:

| Written | Tag | Spoken |
| --- | --- | --- |
| `Use #FF0000 here.` | `en-GB` | Use red here. |
| `Usa #FF0000 aqui.` | `pt-PT` | Usa vermelho aqui. |

## Limits

These limits hold in English and in Portuguese. The limits of one language are on the [English](languages/en.md#limits) and [Portuguese](languages/pt.md#limits) pages.

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Espere 1/2 min.` | `pt-PT` | stays as written | A fraction before a unit stays as written. |
| `A 1/2 kWh cell.` | `en-GB` | stays as written | A fraction before a unit stays as written. |
| `In 2020 kWh prices rose.` | `en-GB` | In two thousand and twenty kilowatt-hours prices rose. | A year before a unit symbol in its CLDR case reads as a measure. |
| `Em 2020 kWh os preços subiram.` | `pt-PT` | Em dois mil e vinte quilowatts-hora os preços subiram. | A year before a unit symbol in its CLDR case reads as a measure. |
| `In 2019-2020 kWh were sold.` | `en-GB` | In two thousand and nineteen to two thousand and twenty kilowatt-hours were sold. | A list of years before such a symbol reads each year as a cardinal. |
| `₹10.50` | `en-GB` | ten point five zero Indian rupees | Two decimals read as a decimal when the language names no minor unit for the currency. |
| `₹10,50` | `pt-PT` | dez vírgula cinquenta rupias indianas | Two decimals read as a decimal when the language names no minor unit for the currency. |
| `₿1` | `en-GB` | bitcoin one | A sign that CLDR names before a number reads before the number. |
| `₿1` | `pt-PT` | bitcoin um | A sign that CLDR names before a number reads before the number. |
| `$5-10` | `en-US` | stays as written | A money range with a symbol at one end only stays as written. |
| `5–10 USD` | `en-GB` | stays as written | A money range with a symbol at one end only stays as written. |
| `CHF 5–10 per day` | `en-GB` | stays as written | A money range with a symbol at one end only stays as written. |
| `5–10 EUR` | `pt-PT` | stays as written | A money range with a symbol at one end only stays as written. |
| `See §§ 2 and 3.` | `en-GB` | See section section two and three. | A doubled mark reads its singular name twice. |
| `Veja os §§ 2 e 3.` | `pt-PT` | Veja os parágrafo parágrafo dois e três. | A doubled mark reads its singular name twice. |

A language file that reads units from CLDR cannot give its own word for a unit.

A currency sign between a range and another sign can keep the range as written, and a second pass then reads it. This is a known exception to the second-pass rule:

| Written | Tag | Spoken | Second pass |
| --- | --- | --- | --- |
| `0–2$€0` | `en-GB` | `0–2$zero euros` | `zero to two$zero euros` |
| `0–2$€0` | `pt-PT` | `0–2$zero euros` | `zero a dois$zero euros` |
| `0–2$₽0` | `en-US` | `0–2$zero Russian rubles` | `zero to two$zero Russian rubles` |
| `0–2$₽0` | `en-GB` | `0–2$zero Russian roubles` | `zero to two$zero Russian roubles` |

## The CLDR data

The data ships in `text2spoken/data/cldr/` under the Unicode License v3. `scripts/extract_cldr.py` writes it, and [Development](development.md#the-cldr-data) shows how to run it.

---
[← Dates and times](dates-and-times.md) · [Home](index.md) · [Addresses, letters and emoji →](addresses-letters-and-emoji.md)
