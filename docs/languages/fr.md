# French

The file `text2spoken/lang/fr.py` reads French. Its number words come from the CLDR spell-out rules, which the core dependency `unicode-rbnf` holds. Install `text2spoken[fr]` for the floor of `unicode-rbnf` that the file needs.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, ranges, expressions, percentages and per mille, money, measures, times, dates, years, telephone numbers, colours, Roman numerals, abbreviations, idioms and lexicon entries. It does not read addresses, symbols, emoji, letter codes or identifiers.

A number that ends in 1 says *un* or *une* with its noun. The gender comes from the hint of the caller, then from the noun after the number when the table `feminine_nouns` holds it, then from `default_gender`, and then from the file, which is masculine. A unit and a currency carry their own gender.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Il y a 21 pommes.` | `fr-FR` | Il y a vingt et une pommes. |
| `Il y a 80 places.` | `fr-FR` | Il y a quatre-vingts places. |
| `Il y a 280 places.` | `fr-FR` | Il y a deux cent quatre-vingts places. |
| `Rendez-vous à 21 h.` | `fr-FR` | Rendez-vous à vingt et une heures. |
| `Rendez-vous à 14h30.` | `fr-FR` | Rendez-vous à quatorze heures trente. |
| `Rendez-vous à 14:30.` | `fr-FR` | Rendez-vous à quatorze heures trente. |
| `Il est 7 h 30.` | `fr-FR` | Il est sept heures trente. |
| `Il est 12 h.` | `fr-FR` | Il est midi. |
| `Il dort 12 h.` | `fr-FR` | Il dort douze heures. |
| `C'est la 1re fois.` | `fr-FR` | C'est la première fois. |
| `Le 21e siècle avance.` | `fr-FR` | Le vingt et unième siècle avance. |
| `Le XXe siècle finit.` | `fr-FR` | Le vingtième siècle finit. |
| `Le roi Louis XIV règne.` | `fr-FR` | Le roi Louis quatorze règne. |
| `Rendez-vous le 10/11/2026.` | `fr-FR` | Rendez-vous le dix novembre deux mille vingt-six. |
| `Il part le 1er mars.` | `fr-FR` | Il part le premier mars. |
| `Cela coûte 3,50 €.` | `fr-FR` | Cela coûte trois euros cinquante. |
| `Cela coûte 0,50 €.` | `fr-FR` | Cela coûte cinquante centimes. |
| `Il gagne 1 000 000 €.` | `fr-FR` | Il gagne un million d'euros. |
| `Il fait 6 °C.` | `fr-FR` | Il fait six degrés Celsius. |
| `Il pèse 3,5 kg.` | `fr-FR` | Il pèse trois virgule cinq kilogrammes. |
| `Il pèse 3,14159 kg.` | `fr-FR` | Il pèse trois virgule un quatre un cinq neuf kilogrammes. |
| `Le prix monte de 50 %.` | `fr-FR` | Le prix monte de cinquante pour cent. |
| `Le taux est de 5 ‰.` | `fr-FR` | Le taux est de cinq pour mille. |
| `Il prend 1/2 heure.` | `fr-FR` | Il prend une demi heure. |
| `Il mange 3/4 du gâteau.` | `fr-FR` | Il mange trois quarts du gâteau. |
| `Il faut 5-8 kg.` | `fr-FR` | Il faut cinq à huit kilogrammes. |
| `Appelez le 06 12 34 56 78.` | `fr-FR` | Appelez le zéro six douze trente-quatre cinquante-six soixante-dix-huit. |
| `Composez 112 ici.` | `fr-FR` | Composez cent douze ici. |
| `M. Dupont et Mme Martin arrivent.` | `fr-FR` | Monsieur Dupont et Madame Martin arrivent. |
| `Le Dr Martin habite à St-Denis.` | `fr-FR` | Le Docteur Martin habite à Saint-Denis. |
| `Lisez le n° 5.` | `fr-FR` | Lisez le numéro cinq. |

### Numbers grouped with a space

A space, a no-break space, a narrow no-break space and, in Switzerland, an apostrophe group the digits of a number, three at a time. A comma and a full stop both mark a decimal, and a full stop that repeats groups digits. A range, a fraction and an expression read a number grouped with a space as one number.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Il faut 1 000-2 000 personnes.` | `fr-FR` | Il faut mille à deux mille personnes. |
| `On a 1 000 + 500 = 1 500.` | `fr-FR` | On a mille plus cinq cents égale mille cinq cents. |
| `Il y a 1.000.000 habitants.` | `fr-FR` | Il y a un million habitants. |
| `Il y a 1'000 habitants.` | `fr-CH` | Il y a mille habitants. |

### A number that stands for an ordinal

*Cent* and *vingt* take no *s* when the number stands for an ordinal: in an ordinal, in a year, and in a number that labels a page or a year. The Académie française names two labels, *page* and *l'an*. Only spaces can stand between the label and the number. A comma, a full stop or another word ends the label, so the number after it agrees with its noun.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Le 200 000 000e visiteur arrive.` | `fr-FR` | Le deux cent millionième visiteur arrive. |
| `Ouvrez le livre page 80.` | `fr-FR` | Ouvrez le livre page quatre-vingt. |
| `Voir p. 80 ici.` | `fr-FR` | Voir page quatre-vingt ici. |
| `Voir la page 80-90 ici.` | `fr-FR` | Voir la page quatre-vingt à quatre-vingt-dix ici. |
| `Il est mort en l'an 800.` | `fr-FR` | Il est mort en l'an huit cent. |
| `Depuis un an, 21 personnes attendent.` | `fr-FR` | Depuis un an, vingt et une personnes attendent. |
| `Sur cette page, 21 recettes vous attendent.` | `fr-FR` | Sur cette page, vingt et une recettes vous attendent. |

## Varieties

| Tag | What differs |
| --- | --- |
| `fr-FR` (the default variety) | The base readings. `fr` and every region with no variety of its own read as `fr-FR` |
| `fr-CA` | `$` is the Canadian dollar. A telephone number reads digit by digit. `register="colloquial"` says *piastres* and *cennes* |
| `fr-CH` | `CHF`, `Fr.` and `fr.` are Swiss francs. An apostrophe groups digits |

The number words follow the CLDR locale of the tag. So `fr-BE` and `fr-CH` say *septante* and *nonante*, `fr-CH` says *huitante*, and every other region says *soixante-dix*, *quatre-vingts* and *quatre-vingt-dix*. CLDR gives *huitante* for all of Switzerland, and Geneva, Neuchâtel and Jura do not use it.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Il y a 71 places.` | `fr-BE` | Il y a septante et une places. |
| `Il y a 80 places.` | `fr-BE` | Il y a quatre-vingts places. |
| `Il y a 80 places.` | `fr-CH` | Il y a huitante places. |
| `Il y a 91 places.` | `fr-CA` | Il y a quatre-vingt-onze places. |
| `Cela coûte 12 $.` | `fr-CA` | Cela coûte douze dollars. |
| `Cela coûte 5 CHF.` | `fr-CH` | Cela coûte cinq francs suisses. |
| `Composez 112 ici.` | `fr-CA` | Composez un un deux ici. |

## Options

| Option | Values | Default (`fr-FR`) | Default (`fr-CA`) | Default (`fr-CH`) |
| --- | --- | --- | --- | --- |
| `date_order` | `DMY`, `MDY` | `DMY` | `DMY` | `DMY` |
| `clock` | `12h`, `24h` | `24h` | `24h` | `24h` |
| `minute_style` | `number`, `phrase` | `number` | `number` | `number` |
| `decimal_mark` | `,`, `.` | `,` | `,` | `,` |
| `scale` | `long` | `long` | `long` | `long` |
| `default_gender` | `feminine`, `masculine` | `masculine` | `masculine` | `masculine` |
| `phone_regions` | `AE`, `BE`, `BR`, `CA`, `CH`, `EG`, `ES`, `FR`, `GB`, `PT`, `SA`, `US` | `FR` | `CA` | `CH` |
| `register` | `colloquial`, `formal` | `formal` | `formal` | `formal` |

`clock="12h"` adds *du matin*, *de l'après-midi* or *du soir*. `minute_style="phrase"` and `register="colloquial"` say *et quart*, *et demie* and *moins le quart*.

| Written | Spoken (`fr-FR`, `clock="12h"`) | Spoken (`fr-FR`, `minute_style="phrase"`) |
| --- | --- | --- |
| `Rendez-vous à 14 h 15.` | Rendez-vous à deux heures quinze de l'après-midi. | Rendez-vous à quatorze heures et quart. |

| Written | Spoken (`fr-CA`, `register="colloquial"`) |
| --- | --- |
| `Cela coûte 3,50 $.` | Cela coûte trois piastres cinquante. |

## Sources

The rules cite the Académie française (Questions de langue, "Nombres" and "Deuxième, second"), the Wiktionnaire, the Lexique des règles typographiques en usage à l'Imprimerie nationale, the SI Brochure of the BIPM, CLDR, ITU-T E.164 and the ARCEP numbering plan. The docstring of [`fr.py`](../../text2spoken/lang/fr.py) gives each rule family its source.

Of the 420 test rows in `tests/data/fr.tsv`, 22 quote a source that was fetched, and 366 say that a rule comes from memory or that no source was fetched. No native speaker has checked any row. `tests/test_french_sources.py` compares the cardinals, ordinals, month names, unit names and currency names with `num2words`, `ovos-number-parser` and CLDR through Babel.

## Limits

French leaves these forms as written or reads them in a limited way:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Il est 7:30.` | `fr-FR` | stays as written | The colon form needs a time word before it, such as `à`, `vers` or `dès`. `est` and `pour` are no time words, because they also come before a ratio or a quantity. |
| `Réglée pour 7:30.` | `fr-FR` | stays as written | The same rule. |
| `Il varie entre 10 %-20 %.` | `fr-FR` | Il varie entre dix pour cent à vingt pour cent. | A range after `entre` reads with *à*, where French says *entre … et …*. |
| `Il a 2 ans 1/2.` | `fr-FR` | Il a deux ans un demi. | A half after a whole number and its noun reads apart, where French says *deux ans et demi*. |
| `Il attend 1/4 heure.` | `fr-FR` | Il attend un quart heure. | A fraction other than a half before a noun reads with no *de*. |
| `Composez le 3615 maintenant.` | `fr-FR` | Composez le trois mille six cent quinze maintenant. | A short code after `le` and before another word reads as a cardinal. |
| `Composez 911 ici.` | `fr-CA` | Composez neuf cent onze ici. | `fr-CA` reads a telephone number digit by digit, but a short code of three digits as one number. No source for either reading was fetched. |
| `Rendez-vous le 10/11/26.` | `fr-FR` | stays as written | A date with a two-digit year stays as written. |
| `Il pèse 1.500 kg.` | `fr-FR` | stays as written | The marks do not settle the number: it is 1,5 or 1500. A warning names it. |
| `Il faut 1'000-2'000 francs.` | `fr-CH` | stays as written | A range, a fraction and an expression read a number grouped with a space, and not one grouped with an apostrophe. |
| `Une page 300 mots.` | `fr-FR` | Une page trois cent mots. | A number right after *page* takes the invariable form, also where it counts the next noun. |

---
[← Basque](eu.md) · [Home](../index.md) · [Portuguese →](pt.md)
