# French

The file `text2spoken/lang/fr.py` reads French. Its number words come from the CLDR spell-out rules, which the core dependency `unicode-rbnf` holds.

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
| `Il y a 1.000.000 habitants.` | `fr-FR` | Il y a un million d'habitants. |
| `Il y a 1'000 habitants.` | `fr-CH` | Il y a mille habitants. |

### A noun after a million or a milliard

*Million* and *milliard* are nouns, so they take *de* before the noun that they count. A range whose high end is a round million takes it too. A number with a lower part, such as 1 200 000, ends in no noun and takes no *de*.

Only the counted noun takes *de*. A determiner, pronoun, preposition, conjunction or adverb after the number takes none: the table `no_de_words` holds each such word of the Wiktionnaire categories that ends in *s*, *x* or *z*, such as *ailleurs* and *là-bas*. An adjective after the number takes none if the table `no_de_adjectives` holds it, and a participle after a sum of money takes none if the table `no_de_participles` holds it. A verb with an inverted subject, such as *disent-ils* or *vois-tu*, takes none. An imperative with an object pronoun, such as *croyez-moi*, *allez-y* or *donnez-m'en*, takes none either. A word of one letter, a mark or the end of the text takes none either. The counted noun is plural, so a word that does not end in *s*, *x* or *z*, such as a verb, takes no *de*, unless the table `invariable_plurals` holds it. A word with a hyphen counts as one word, and it is plural when any of its parts is, as in *années-lumière*.

*De* becomes *d'* before a vowel or a mute h. It stays *de* before a word that starts as a word of the OQLF list of aspirated h does, before a y and a vowel other than in *yeux* and *yeuse*, and before *oui* and *ouistiti*. A y before a consonant is a vowel, so *de* elides before it. It also stays *de* before a capitalised h, because most proper nouns with h take no elision. The OQLF calls this a tendency with exceptions, and *Haïti* and its derived words elide. A word all in capitals follows the rules of its lowercase form.

| Written | Tag | Spoken |
| --- | --- | --- |
| `Il y a 1 000 000 habitants.` | `fr-FR` | Il y a un million d'habitants. |
| `La Terre comptait 3 000 000 000 personnes.` | `fr-FR` | La Terre comptait trois milliards de personnes. |
| `On a récolté 2 000 000 haricots.` | `fr-FR` | On a récolté deux millions de haricots. |
| `Il y a 1,5 million habitants.` | `fr-FR` | Il y a un virgule cinq million d'habitants. |
| `Cela coûte 3 000 000 €.` | `fr-FR` | Cela coûte trois millions d'euros. |
| `Il y a 1 200 000 habitants.` | `fr-FR` | Il y a un million deux cent mille habitants. |
| `Ils étaient 1 000 000 environ.` | `fr-FR` | Ils étaient un million environ. |
| `Il en a vendu 3 000 000 depuis 2010.` | `fr-FR` | Il en a vendu trois millions depuis deux mille dix. |
| `Il faut 2 000 000 supplémentaires pour finir.` | `fr-FR` | Il faut deux millions supplémentaires pour finir. |
| `Il a reçu 2 000 000 versés en deux fois.` | `fr-FR` | Il a reçu deux millions versés en deux fois. |
| `Ils étaient 2 000 000 là-bas.` | `fr-FR` | Ils étaient deux millions là-bas. |
| `Ils étaient 2 000 000 disent-ils.` | `fr-FR` | Ils étaient deux millions disent-ils. |
| `Il y en a 2 000 000 croyez-moi.` | `fr-FR` | Il y en a deux millions croyez-moi. |
| `Il faut 1 000 000-2 000 000 personnes.` | `fr-FR` | Il faut un million à deux millions de personnes. |
| `Il y a 2 000 000 handicapés.` | `fr-FR` | Il y a deux millions de handicapés. |
| `Il y a 2 000 000 Hongrois.` | `fr-FR` | Il y a deux millions de Hongrois. |
| `Il y a 2 000 000 Haïtiens.` | `fr-FR` | Il y a deux millions d'Haïtiens. |
| `Il y a 2 000 000 HABITANTS.` | `fr-FR` | Il y a deux millions d'HABITANTS. |
| `Il y a 2 000 000 yachts.` | `fr-FR` | Il y a deux millions de yachts. |
| `Il y a 2 000 000 yeux.` | `fr-FR` | Il y a deux millions d'yeux. |
| `Il y a 2 000 000 Yvelinois.` | `fr-FR` | Il y a deux millions d'Yvelinois. |
| `Il y a 2 000 000 sans-abri.` | `fr-FR` | Il y a deux millions de sans-abri. |
| `La galaxie est à 2 000 000 années-lumière.` | `fr-FR` | La galaxie est à deux millions d'années-lumière. |
| `On attend 2 000 000 de visiteurs.` | `fr-FR` | On attend deux millions de visiteurs. |
| `Selon la police, 2 000 000 manifestent.` | `fr-FR` | Selon la police, deux millions manifestent. |

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

The rules cite the Académie française (Questions de langue, "Nombres" and "Deuxième, second", and the Dictionnaire, "unième"), the Office québécois de la langue française for the plural, the aspirated h and the imperative, the Wiktionnaire, the Lexique des règles typographiques en usage à l'Imprimerie nationale, the SI Brochure of the BIPM, CLDR, ITU-T E.164 and the ARCEP numbering plan. The docstring of [`fr.py`](../../text2spoken/lang/fr.py) gives each rule family its source.

Of the 572 test rows in `tests/data/fr.tsv`, 168 quote a source that was fetched. 369 say that a rule comes from memory, and 6 more say that no source was fetched for a guard row. No native speaker has checked any row. The cited rows are the check for numbers. No other number engine checks them.

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
| `Il en reste 2 000 000 entiers.` | `fr-FR` | Il en reste deux millions d'entiers. | An adjective after a round million that `no_de_adjectives` lacks takes *de*, as a noun does. The class is open, and the table holds the adjectives that a count of Tatoeba and FLORES+ found after a number. |
| `Il a 2 000 000 hérités de son père.` | `fr-FR` | Il a deux millions d'hérités de son père. | A participle after a round million that `no_de_participles` lacks takes *de*. The class is open, and the table holds the common participles after a sum of money. |
| `Il a écrit 1 000 000 vers.` | `fr-FR` | Il a écrit un million vers. | *Vers* (verses) is also a preposition of `no_de_words`, so it takes no *de*, where French says *un million de vers*. |
| `Il a gagné 2 000 000 sous.` | `fr-FR` | Il a gagné deux millions sous. | *Sous* (coins) is also a preposition of `no_de_words`, so it takes no *de*, where French says *deux millions de sous*. |
| `Il y a 2 000 000 Hommes.` | `fr-FR` | Il y a deux millions de Hommes. | A common noun with a capital letter takes no elision, as a proper noun with h does. |
| `Il y a 2 000 000 très grandes villes.` | `fr-FR` | Il y a deux millions très grandes villes. | An adverb of `no_de_words` before a preposed adjective takes no *de*, where French says *deux millions de très grandes villes*. |
| `Il y a 2 000 000 harkis.` | `fr-FR` | Il y a deux millions d'harkis. | *De* elides before an aspirated h that the OQLF list does not reach. Of 415 Tatoeba words that the Wiktionnaire marks as aspirated, the list reaches 245. |
| `Il y a 1/2 million habitants.` | `fr-FR` | Il y a un demi million habitants. | A fraction before *million* takes no *de*. |
| `Il y a 2 000 000 chez-moi.` | `fr-FR` | Il y a deux millions chez-moi. | A noun whose last part is an object pronoun, such as *chez-moi*, *chez-toi*, *revenez-y* or *aimez-moi* (the forget-me-not), reads as an imperative and takes no *de* if `invariable_plurals` lacks it. |
| `Il y a 2 000 000 chromosomes-Y.` | `fr-FR` | Il y a deux millions chromosomes-Y. | A letter label after a hyphen that is also the pronoun *y* reads as an imperative and takes no *de*. Other letter labels, such as *lymphocytes-T* and *chromosomes-X*, keep it. |
| `Il y a 2 000 000 tête-à-tête.` | `fr-FR` | Il y a deux millions tête-à-tête. | A noun with an invariable plural and no part in *s*, *x* or *z* takes no *de* if `invariable_plurals` lacks it. |
| `Une page 300 mots.` | `fr-FR` | Une page trois cent mots. | A number right after *page* takes the invariable form, also where it counts the next noun. |

The *de* rule reads only spaces between a number and the noun that it counts. A line break between them stops the rule, and the noun on the next line takes no *de*.

---
[← Basque](eu.md) · [Home](../index.md) · [Italian →](it.md)
