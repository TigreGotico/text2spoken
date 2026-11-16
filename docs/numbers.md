# Numbers

This page shows how text2spoken reads numbers: cardinals, ordinals, decimals, fractions, ranges, expressions, Roman numerals, telephone numbers, identifiers and idioms. The tables of [How it reads text](how-it-reads.md#the-forms) give the languages that offer each form.

## Cardinal numbers

| Written | Tag | Spoken |
| --- | --- | --- |
| `I have 12 cats and 1,234 dogs.` | `en-GB` | I have twelve cats and one thousand two hundred and thirty-four dogs. |
| `Room 101.` | `en-GB` | Room one hundred and one. |
| `Room 101.` | `en-US` | Room one hundred one. |
| `Score -5 points.` | `en-GB` | Score minus five points. |
| `Tenho 12 gatos e 1.234 cães.` | `pt-PT` | Tenho doze gatos e mil duzentos e trinta e quatro cães. |
| `Tenho 2 casas.` | `pt-PT` | Tenho duas casas. |
| `Hay 21 casas.` | `es-ES` | Hay veintiuna casas. |
| `Он купил 2 книги.` | `ru-RU` | Он купил две книги. |

The group mark and the decimal mark come from the language variety, so `1,234` is one number in English and `1.234` is one number in Portuguese. A number agrees with its noun in the languages that have grammatical gender or case. The language pages give the rules of each language, and [API](api.md#grammatical-agreement) shows how a caller gives the gender.

The `scale` option chooses the word for 10^9 where the language has both:

| Written | Spoken (`pt-PT`) | Spoken (`pt-PT`, `scale="short"`) |
| --- | --- | --- |
| `Pagou 1000000000 €.` | Pagou mil milhões de euros. | Pagou um bilião de euros. |

## Ordinal numbers

| Written | Tag | Spoken |
| --- | --- | --- |
| `She came 1st.` | `en-GB` | She came first. |
| `Ficou em 3.º lugar.` | `pt-PT` | Ficou em terceiro lugar. |
| `Am 3. Mai.` | `de-DE` | Am dritten Mai. |

## Decimals

| Written | Tag | Spoken |
| --- | --- | --- |
| `It weighs 3.5 kg.` | `en-GB` | It weighs three point five kilograms. |
| `Add .5 cups.` | `en-US` | Add zero point five cups. |
| `Mede 3,5 metros.` | `pt-PT` | Mede três vírgula cinco metros. |

The `decimal_mark` option sets the decimal mark of the written numbers, where the language offers more than one.

## Fractions

| Written | Tag | Spoken |
| --- | --- | --- |
| `Eat 1/2 of it.` | `en-GB` | Eat one-half of it. |
| `Coma 3/4 do bolo.` | `pt-PT` | Coma três quartos do bolo. |

## Ranges

| Written | Tag | Spoken |
| --- | --- | --- |
| `Ages 18-25 only.` | `en-GB` | Ages eighteen to twenty-five only. |
| `Dos 18-25 anos.` | `pt-PT` | Dos dezoito a vinte e cinco anos. |

## Expressions

| Written | Tag | Spoken |
| --- | --- | --- |
| `Compute 5+3 now.` | `en-GB` | Compute five plus three now. |
| `Calcula 2 × 2.` | `pt-PT` | Calcula dois vezes dois. |

## Roman numerals

English, Portuguese and Basque read a Roman numeral when the text around it shows that it is a number, such as a name, a century, or a noun of a series:

| Written | Tag | Spoken |
| --- | --- | --- |
| `Luís XIV reinou.` | `pt-PT` | Luís Catorze reinou. |
| `No século XIX.` | `pt-PT` | No século dezanove. |
| `Leia o capítulo V.` | `pt-PT` | Leia o capítulo quinto. |
| `A D. XIV.` | `pt-PT` | A Dom Catorze. |
| `O papa Pio X reinou.` | `pt-PT` | O papa Pio Décimo reinou. |
| `O papa Pio X reinou.` | `pt-BR` | O papa Pio Dez reinou. |
| `Henry VIII had six wives.` | `en-GB` | Henry the Eighth had six wives. |
| `John Smith III spoke.` | `en-US` | John Smith the Third spoke. |
| `World War II ended.` | `en-GB` | World War Two ended. |
| `Super Bowl LVII was close.` | `en-US` | Super Bowl Fifty-Seven was close. |
| `XX. mendean.` | `eu-ES` | hogeigarren mendean. |

Portuguese reads an ordinal up to ten and a cardinal from eleven, and pt-BR stops the ordinal at nine, as Ciberdúvidas gives the rule. English reads "the" and an ordinal after a name, and a cardinal after a noun of a series. The [English](languages/en.md#roman-numerals) and [Portuguese](languages/pt.md#roman-numerals) pages give the rules and their sources.

A numeral stays as written when the text does not show that it is a number:

| Written | Tag | Spoken | Why |
| --- | --- | --- | --- |
| `Malcolm X spoke.` | `en-GB` | stays as written | A numeral of one letter after a name needs a regnal title before the name. |
| `The book I read.` | `en-GB` | stays as written | `I` is the pronoun. |
| `Fly to Washington DC.` | `en-GB` | stays as written | `DC` is an acronym, in the `roman_words` table. |
| `Tome vitamina C.` | `pt-PT` | stays as written | One letter reads only as `I`, `V` or `X` after a noun of a series. |
| `EU VI O FILME.` | `pt-PT` | stays as written | `VI` is a word after a word in capitals. |

A title of a work reads its numeral as a name does, because telling a title from a name needs context that the library does not have:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `Rocky II was a hit.` | `en-US` | Rocky the Second was a hit. | A title of a work reads as a name. |
| `Vi o Avatar II.` | `pt-PT` | Vi o Avatar Segundo. | A title of a work reads as a name. |

## Telephone numbers

A telephone number reads digit by digit:

| Written | Tag | Spoken |
| --- | --- | --- |
| `Call +44 20 7946 0958.` | `en-GB` | Call plus four four two zero seven nine four six zero nine five eight. |
| `Call +351 912 345 678.` | `pt-PT` | Call mais três cinco um nove um dois três quatro cinco seis sete oito. |

A run of digits reads as a telephone number on any of four kinds of evidence:

- a `+` or `00` prefix and a country code;
- a trunk prefix of a region in the `phone_regions` param;
- a phone shape of the language, such as `(212) 555-0123`;
- a phone word before the run, such as `Call`.

`phone_regions=None` takes the region of the tag, when the language has a numbering plan for it. With no plan for a region, the other three kinds of evidence still apply:

| Written | Spoken (`en-GB`) | Spoken (`en-GB`, `phone_regions=frozenset()`) |
| --- | --- | --- |
| `Room 02079460958.` | Room zero two zero seven nine four six zero nine five eight. | stays as written |
| `Call 02079460958.` | Call zero two zero seven nine four six zero nine five eight. | Call zero two zero seven nine four six zero nine five eight. |

## Identifiers

The `IDENTIFIER` form is for a digit run after a word that names a code, read digit by digit. No language file has a recognizer for it, so no text reads as an identifier.

## Idioms

An idiom is a written form that a table of the language reads as a whole:

| Written | Tag | Spoken |
| --- | --- | --- |
| `Open 24/7.` | `en-GB` | Open twenty-four seven. |
| `It is 50/50.` | `en-GB` | It is fifty-fifty. |

---
[← How it reads text](how-it-reads.md) · [Home](index.md) · [Dates and times →](dates-and-times.md)
