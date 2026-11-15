# Russian

The file `text2spoken/lang/ru.py` reads Russian. Install it with `text2spoken[ru]`, which adds `ovos-number-parser`.

## Varieties and codes

| Tag | Notes |
| --- | --- |
| `ru-RU` | The one variety. Every other `ru-*` tag selects it |

## What it reads

The file reads cardinals, ordinals, decimals, fractions, dates, times, years, money, measures, percentages, abbreviations and lexicon entries. A sign reads "плюс" or "минус". Number words take the letter ё, as in "трёх" and "четырёх".

### Agreement

A number agrees in gender and case with the noun after it, and the preposition before it gives the case. A noun in the prepositional in `-е` or `-ии` does not show its gender, so `в 1 квартире` reads the masculine "одном". A `default_gender` param of feminine gives "одной". A hint replaces the features that the context gives, so a hint gives "одной" only when it holds the case too: `Features(gender=GrammaticalGender.FEMININE, case="prepositional")`. A hint with the gender alone gives "одна".

After 2, 3 and 4, a noun that has only plural forms takes "двое", "трое" or "четверо": `2 суток` reads "двое суток" (Розенталь 1985, § 165). The nouns "детей", "ребят" and "людей" take them only where the number is the subject. That is the case first in the clause, after "было", and after a phrase with "у", "в" or "во" that opens the clause: `У моей сестры 2 детей` reads "двое детей", and `В семье 3 детей` reads "трое детей" (Грамматика-80, § 2455). After a verb or a preposition of the accusative, as in `Я видел 2 детей` and `Я видел в парке 2 детей`, the number stays as written. Another preposition takes the cardinal in its case: `Для 2 детей` reads "для двух детей" (Грамматика-80, § 1366).

### Dates

A date with no preposition says when something happens, so it reads in the genitive: `Он родился 12 марта` reads "двенадцатого марта", and `Экзамен был 3 июня` reads "третьего июня" (Грамматика-80, § 1168, and Розенталь 1985, § 94). A date that closes its clause reads in the nominative in two places. Only "года", closing quotes and one of the marks ". ! ? …", or the end of the clause, follow such a date. A date before a comma reads in the genitive, because the clause often goes on after the comma: `1 мая, в субботу, мы поехали на дачу` and `Тогда, 1 мая, мы уехали` read "первого мая".

The first place is after a label colon, where the date names the day (§ 1167): `Дата: 9 мая.` reads "девятое мая". The second place is where the date is the subject of "был", "была", "было", "будет", "есть" or a form of "наступить" (§ 2536, § 2539, § 2681). In that clause only these verbs and words such as "а", "но", "ведь", "вот", "и", "ли", "наконец", "уже", "сегодня" and "завтра" come before the date. So `Вот и наступило 1 сентября` reads "первое сентября", and `Сегодня уже 1 мая` reads "первое мая".

A date alone in its clause is a nominative sentence (§ 2522, § 2524), so `1 мая.` and `Почему магазин закрыт? Ведь 1 мая!` read "первое мая". After only "да" or "а", the date reads in the genitive, because a reply takes its form from the question (§ 1954): `Да, 1 мая.` reads "первого мая". Only the words after the last colon or opening quote count, so `Он сказал: «Сегодня 1 мая».` reads "первое мая".

A subject before the verb, or a word after the date, makes the date a time again: `Лето наступило 1 июня` and `Было 1 мая подписано соглашение` read the genitive. The pronoun "это" is a subject too (Розенталь 1985, § 189), so `Это было 1 мая` reads "первого мая".

## Sources

The rules cite Грамматика-80 (Русская грамматика, АН СССР, 1980), Д. Э. Розенталь, Справочник по правописанию и литературной правке (1985), and the Правила русской орфографии и пунктуации (2006), by paragraph. The docstring of [`ru.py`](../../text2spoken/lang/ru.py) lists them.

The test rows in `tests/data/ru.tsv` cite Грамматика-80, Розенталь or the 2006 spelling rules, and no native speaker has checked them. Of the 177 rows, 3 are marked silver, because no source gives their reading.

## Limits

Some Russian readings are wrong:

- `Нас было 2` reads "два", not "двое".
- An object before the verb, as in `3 детей я видел`, reads "трое", not "троих".
- An adverb before the adjective, as in `2 очень маленьких детей`, hides the noun, so the number reads "два".
- A date before a dash reads in the genitive, also after "сегодня": `Сегодня 1 мая — День весны` reads "первого мая".
- A date before a comma, a colon or a bracket reads in the genitive, also where it is the subject: `Было 1 мая, шёл дождь`, `Сегодня 1 мая, в субботу, мы идём на парад`, `«Сегодня 1 мая», — сказал он` and `Сегодня (1 мая) праздник`. A dateline such as `1 мая, вторник` and a label before a comma such as `Дата: 9 мая, вторник` read in the genitive too.
- `Да здравствует 1 мая!` reads "первого", although the date is the subject of "здравствует".
- A phrase with "у", "в" or "во" that does not open the clause stays as written: `В семье у нас 3 детей`. So does a phrase that the three words before the number do not show whole: `У нас в семье 3 детей`.
- The prepositional in `-е` or `-ии` and some nouns in `-ь` read masculine without a gender hint.
- A count after a verb reads the nominative, and an animate accusative reads the cardinal.

## Edge cases

These cases come from tests that feed the library unusual text. A reader of ordinary prose rarely meets them.

- A quoted title of a date word before the date makes the date read in the nominative: `«Завтра» 1 мая.` and `Я купил «Завтра» и «Сегодня» 1 мая.` read "первое".
- A date after a comma with no space is not taken as a date, so the number reads as a cardinal: `Он сказал: «Сегодня,1 мая».` reads "Сегодня,одна мая".

---
[← Portuguese](pt.md) · [Home](../index.md) · [Adding a language →](../adding-a-language.md)
