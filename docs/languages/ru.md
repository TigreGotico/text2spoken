# Russian

The file `text2spoken/lang/ru.py` reads Russian. Its number words come from `ovos-number-parser`, which the base install holds.

## What it reads

The file reads cardinals, ordinals, decimals, fractions, dates, times, years, money, measures, percentages, abbreviations and lexicon entries. A sign reads "плюс" or "минус". Number words take the letter ё, as in "трёх" and "четырёх".

| Written | Spoken (`ru-RU`) |
| --- | --- |
| `Он купил 2 книги.` | Он купил две книги. |
| `Температура -5 градусов.` | Температура минус пять градусов. |
| `Для 3 детей.` | Для трёх детей. |
| `Он родился 12 марта.` | Он родился двенадцатого марта. |
| `Встреча в 14:30.` | Встреча в четырнадцать тридцать. |
| `Это было в 1999 году.` | Это было в тысяча девятьсот девяносто девятом году. |

### Agreement

A number agrees in gender and case with the noun after it, and the preposition before it gives the case. A noun in the prepositional in `-е` or `-ии` does not show its gender, so the number reads the masculine. A `default_gender` param of feminine gives the feminine:

| Written | Spoken (`ru-RU`) | Spoken (`ru-RU`, `default_gender=FrozenMap({"ru": GrammaticalGender.FEMININE})`) |
| --- | --- | --- |
| `в 1 квартире` | в одном квартире | в одной квартире |

For a cardinal, a hint replaces the features that the context gives, so a hint gives the feminine only when it holds the case too:

```python
>>> from text2spoken import Features, GrammaticalGender, analyze, render
>>> analysis = analyze("в 1 квартире", "ru-RU")
>>> render(analysis, {2: Features(gender=GrammaticalGender.FEMININE, case="prepositional")})
'в одной квартире'
>>> render(analysis, {2: Features(gender=GrammaticalGender.FEMININE)})
'в одна квартире'
```

After 2, 3 and 4, a noun that has only plural forms takes "двое", "трое" or "четверо" (Розенталь 1985, § 165). The nouns "детей", "ребят" and "людей" take them only where the number is the subject: first in the clause, after a form of "быть" ("был", "была", "было", "будет", "есть"), and after a phrase with "у", "в" or "во" that opens the clause (Грамматика-80, § 2455). After a verb or a preposition of the accusative, the number stays as written. Another preposition takes the cardinal in its case (Грамматика-80, § 1366).

| Written | Spoken (`ru-RU`) |
| --- | --- |
| `2 суток` | двое суток |
| `У моей сестры 2 детей` | У моей сестры двое детей |
| `В семье 3 детей` | В семье трое детей |
| `Я видел 2 детей` | stays as written |
| `Я видел в парке 2 детей` | stays as written |
| `Для 2 детей` | Для двух детей |

### Dates

A date with no preposition says when something happens, so it reads in the genitive (Грамматика-80, § 1168, and Розенталь 1985, § 94). A date that closes its clause reads in the nominative in two places. Only "года", closing quotes and one of the marks ". ! ? …", or the end of the clause, follow such a date. A date before a comma reads in the genitive, because the clause often goes on after the comma.

| Written | Spoken (`ru-RU`) |
| --- | --- |
| `Он родился 12 марта` | Он родился двенадцатого марта |
| `Экзамен был 3 июня` | Экзамен был третьего июня |
| `1 мая, в субботу, мы поехали на дачу` | первого мая, в субботу, мы поехали на дачу |
| `Тогда, 1 мая, мы уехали` | Тогда, первого мая, мы уехали |

The first place is after a label colon, where the date names the day (§ 1167). The second place is where the date is the subject of "был", "была", "было", "будет", "есть" or a form of "наступить" (§ 2536, § 2539, § 2681). In that clause only these verbs, and words such as "а", "но", "ведь", "вот", "и", "ли", "наконец", "уже", "сегодня" and "завтра", come before the date.

| Written | Spoken (`ru-RU`) |
| --- | --- |
| `Дата: 9 мая.` | Дата: девятое мая. |
| `Вот и наступило 1 сентября` | Вот и наступило первое сентября |
| `Сегодня уже 1 мая` | Сегодня уже первое мая |

A date alone in its clause is a nominative sentence (§ 2522, § 2524). After only "да" or "а", the date reads in the genitive, because a reply takes its form from the question (§ 1954). Only the words after the last colon or opening quote count.

| Written | Spoken (`ru-RU`) |
| --- | --- |
| `1 мая.` | первое мая. |
| `Почему магазин закрыт? Ведь 1 мая!` | Почему магазин закрыт? Ведь первое мая! |
| `Да, 1 мая.` | Да, первого мая. |
| `Он сказал: «Сегодня 1 мая».` | Он сказал: «Сегодня первое мая». |

A subject before the verb, or a word after the date, makes the date a time again. The pronoun "это" is a subject too (Розенталь 1985, § 189).

| Written | Spoken (`ru-RU`) |
| --- | --- |
| `Лето наступило 1 июня` | Лето наступило первого июня |
| `Было 1 мая подписано соглашение` | Было первого мая подписано соглашение |
| `Это было 1 мая` | Это было первого мая |

## Varieties

| Tag | Notes |
| --- | --- |
| `ru-RU` | The one variety. Every other `ru-*` tag selects it |

## Options

| Option | Values | Default (`ru-RU`) |
| --- | --- | --- |
| `date_order` | `DMY`, `MDY`, `YMD` | `DMY` |
| `clock` | `24h` | `24h` |
| `minute_style` | `number` | `number` |
| `decimal_mark` | `,`, `.` | `,` |
| `scale` | `short` | `short` |
| `default_gender` | `feminine`, `masculine`, `neuter` | `masculine` |
| `phone_regions` | changes nothing | - |
| `register` | changes nothing | - |

## Sources

The rules cite Грамматика-80 (Русская грамматика, АН СССР, 1980), Д. Э. Розенталь, Справочник по правописанию и литературной правке (1985), and the Правила русской орфографии и пунктуации (2006), by paragraph. The unit names and the digit groups cite ru.wikipedia.org. The docstring of [`ru.py`](../../text2spoken/lang/ru.py) lists them.

Most test rows in `tests/data/ru.tsv` cite Грамматика-80, Розенталь or the 2006 spelling rules. Some cite Кузнецов's Большой толковый словарь, CLDR 49 or the design of text2spoken. No native speaker has checked them. Of the 178 rows, 3 are marked silver, because no source gives their reading.

## Limits

Some Russian readings are wrong:

| Written | Spoken (`ru-RU`) | Limit |
| --- | --- | --- |
| `Нас было 2` | Нас было два | This reads "два", not "двое". |
| `3 детей я видел` | трое детей я видел | An object before the verb reads "трое", not "троих". |
| `2 очень маленьких детей` | два очень маленьких детей | An adverb before the adjective hides the noun, so the number reads "два". |
| `Сегодня 1 мая — День весны` | Сегодня первого мая — День весны | A date before a dash reads in the genitive, also after "сегодня". |
| `Было 1 мая, шёл дождь` | Было первого мая, шёл дождь | A date before a comma, a colon or a bracket reads in the genitive, also where it is the subject. |
| `Сегодня 1 мая, в субботу, мы идём на парад` | Сегодня первого мая, в субботу, мы идём на парад | The same rule. |
| `«Сегодня 1 мая», — сказал он` | «Сегодня первого мая», — сказал он | The same rule. |
| `Сегодня (1 мая) праздник` | Сегодня (первого мая) праздник | The same rule. |
| `1 мая, вторник` | первого мая, вторник | A dateline reads in the genitive too. |
| `Дата: 9 мая, вторник` | Дата: девятого мая, вторник | A label before a comma reads in the genitive too. |
| `Да здравствует 1 мая!` | Да здравствует первого мая! | This reads the genitive, although the date is the subject of "здравствует". |
| `В семье у нас 3 детей` | stays as written | A phrase with "у", "в" or "во" that does not open the clause stays as written. |
| `У нас в семье 3 детей` | stays as written | So does a phrase that the three words before the number do not show whole. |

The prepositional in `-е` or `-ии`, and some nouns in `-ь`, read masculine without a gender hint. A count after a verb reads the nominative, and an animate accusative reads the cardinal.

## Edge cases

These cases come from tests that feed the library unusual text. A reader of ordinary prose rarely meets them.

| Written | Spoken (`ru-RU`) | Why |
| --- | --- | --- |
| `«Завтра» 1 мая.` | «Завтра» первое мая. | A quoted title of a date word before the date makes the date read in the nominative. |
| `Я купил «Завтра» и «Сегодня» 1 мая.` | Я купил «Завтра» и «Сегодня» первое мая. | The same rule. |
| `Он сказал: «Сегодня,1 мая».` | Он сказал: «Сегодня,одна мая». | A date after a comma with no space is not taken as a date, so the number reads as a cardinal. |

---
[← Portuguese](pt.md) · [Home](../index.md) · [Adding a language →](../adding-a-language.md)
