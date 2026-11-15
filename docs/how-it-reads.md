# How it reads text

The library finds each written form that it can read, and replaces it with words. It does not guess. A form that it cannot read for sure stays as written, and the library logs a WARNING on the `text2spoken` logger:

```python
from text2spoken import Form, NormalizationParams, normalize

normalize("The run took 1:23:45.", "en-GB")
# 'The run took 1:23:45.'  (a duration, not a clock time)
```

A second pass changes nothing: `normalize(normalize(text, lang), lang)` gives the same text as one pass. Output depends only on the text, the tag and the params. The known exceptions to the second-pass rule are on the pages of the forms and the languages that have them.

## The forms

Each written form has a `Form` value. `NormalizationParams().forms` holds every form except `LETTERS` and `EMOJI`, which are off by default. A language reads only the forms that its file offers: `supports(lang).forms` lists them.

| Form | What it reads | Default | Languages |
| --- | --- | --- | --- |
| `LEXICON` | An entry of the `lexicon` param | On | All |
| `CARDINAL` | A whole number: `12`, `1.234`, `-5` | On | All |
| `ORDINAL` | `1º`, `3.ª`, `1st` | On | de, en, es, eu, pt, ru |
| `DECIMAL` | `3,5`, `0.5`, `.5` | On | All |
| `FRACTION` | `1/2`, `3/4` | On | All |
| `RANGE` | `18-25`, `10-20` | On | ar, de, en, es, pt |
| `EXPRESSION` | `5+3`, `2 × 2` | On | de, en, es, eu, pt |
| `DATE` | `12/03/2024`, `2024-03-12`, `15 de maio de 2025` | On | All |
| `TIME` | `às 14:30`, `14h30`, `9am`, `10 p.m.` | On | All |
| `YEAR` | A year that a word or a suffix marks: `in 1999`, `im Jahr 1999` | On | de, en, ru |
| `MONEY` | `$5`, `2,50 €` | On | All |
| `MEASURE` | `10kg`, `25°C`, `5 km/h` | On | All |
| `PERCENT` | `20%`, `4,5 %` | On | All |
| `TELEPHONE` | `+351 912 345 678`, read digit by digit | On | de, en, es, pt |
| `IDENTIFIER` | A digit run after a word that names a code, read digit by digit | On | None |
| `LETTERS` | A run of capital letters: `NATO`, `BMW`, `MP3` | Off | en, pt |
| `ABBREVIATION` | `Dr.`, `n.º`, `etc.` | On | de, en, es, eu, pt, ru |
| `IDIOM` | `24/7`, `50/50`, from a table of the language | On | de, en |
| `ROMAN` | `Luís XIV`, `XX. mendea`, `século XIX` | On | eu, pt |
| `COLOR` | `#FF0000` | On | de, en, pt |
| `ELECTRONIC` | An e-mail or web address: `ann@example.com`, `www.example.org` | On | en |
| `SYMBOL` | A character with a CLDR name, such as `©`, `§` or `→`, when no other form claims it | On | en, pt |
| `EMOJI` | An emoji, by its CLDR name | Off | en, pt |

A language with no file reads cardinal numbers from the CLDR spell-out rules, and keeps all other forms as written. A language that CLDR has no spell-out rules for reads only the lexicon.

To read only some forms, select them:

```python
normalize("Pay $5 on 12/03/2024 for 3 items.", "en-US", NormalizationParams().only(Form.CARDINAL))
# 'Pay $5 on 12/03/2024 for three items.'
```

`NormalizationParams().without(Form.SYMBOL)` turns one form off, and `NormalizationParams().plus(Form.LETTERS)` turns one on.

## E-mail and web addresses

A word with `@`, `www.`, `://` or a top-level domain such as `.com` is spoken in full, even when it is not one valid address. `Mail me@x.com,2 copies.` reads "Mail em e at ex dot com , two copies." The closing punctuation at the end of the word stays with the sentence: `Have you seen www.example.com?!` keeps `?!`. A character with no word in the address tables stays as written, between spaces: `See 20%.com` reads "See two zero % dot com".

English offers this form. Its limits are on the [English page](languages/en.md#edge-cases).

## Runs of capital letters

The `LETTERS` form reads a run of capital letters, such as `NATO`, `BMW` or `MP3`. The form is off by default, so a run stays as written and the phonemizer reads it. Turn it on with `plus`:

```python
normalize("A NATO reuniu-se com a RTP.", "pt-PT", NormalizationParams().plus(Form.LETTERS))
# 'A NATO reuniu-se com a érre tê pê.'
```

A run is two or more capital letters that touch no other letter. Digits can come before or after the letters, as in `MP3`, `4G` and `T2`. A run of two letters, or of one letter and digits, reads letter by letter. A longer run reads as a word when it splits into syllables of the language, and then it stays as written. Any other run reads each letter by its name and each digit by its word.

English and Portuguese offer the form. A language with no letter names keeps each run as written. The rules of each language, and the limits that belong to one language, are on the [English](languages/en.md#runs-of-capital-letters) and [Portuguese](languages/pt.md#runs-of-capital-letters) pages.

The form does not take a run with a lowercase letter (`ONGs`, `PhD`), a run with full stops (`E.U.A.`), a capital alone (`plano B`), or a Roman numeral that the `ROMAN` form reads (`século XIV`). With the form on, a run of capitals in the reading of another form reads as this form reads it. So `Call the BBC at 9 AM.` reads "Call the bee bee see at nine a em." in `en-US`, and `help@IRS.gov` reads "help at i ar ess dot gov".

These limits hold in both languages:

- A Roman numeral that the `ROMAN` form does not read is a run. `Classe II` reads "Classe i i", and `World War II` reads "World War i i". Portuguese gives such a run no free consonant, so `A D. XIV.` reads "A Dom xis i vê."
- A run that reads as a word and holds a digit stays as written, as `COVID19` does with the form off.
- A run with a letter that has no name, such as `Ç`, stays as written when it does not split into syllables.
- Text in capitals spells its two-letter words, because a run of two letters reads letter by letter. `SAIA DA SALA` reads "SAIA dê á SALA" in pt-PT, and `DO NOT ENTER` reads "dee o NOT ENTER". The rule stays, because two-letter acronyms such as `TV`, `PC`, `UE` and `IA` are frequent.
- A run of digits joined to a run reads digit by digit. `10GB` reads "one zero gee bee", and `A25` reads "á dois cinco" in pt-PT.

## Emoji

The `EMOJI` form reads an emoji by its CLDR name. A chat reader wants it and a book reader does not, so the form is off by default, and each emoji stays as written. Turn it on with `plus`:

```python
normalize("Nice 👍🏽!", "pt-PT", NormalizationParams().plus(Form.EMOJI))
# 'Nice polegar para cima tipo de pele quatro!'
```

The form reads each emoji sequence: an emoji with its skin tone, its U+FE0F and the emoji that zero width joiners add to it. The sequences come from the Unicode 17.0 emoji files, the version whose emoji CLDR 49 names. `😂😂` reads the name twice, `👨‍👩‍👧‍👦` reads "family man woman girl boy", `🇵🇹` reads "flag Portugal", and `1️⃣` reads "keycap one". A sequence with no name reads by the name of its first emoji, so `😀🏽` reads "grinning face".

A name drops its quote marks, its colons, commas and brackets become spaces, and the language reads its digits and abbreviations as in a sentence: en `1st place medal` reads "first place medal", and pt-PT `tipo de pele 4` reads "tipo de pele quatro". U+2019 between two letters is an apostrophe, so `🕐` reads "one o’clock". The spacing follows the `SYMBOL` form, so `(😂).` reads "(face with tears of joy).".

A name that still holds a character that is no word after the reading stays as written, because a second pass would read that character. So `🇦🇬` stays as written in English, and `#️⃣` stays as written in every tag. [Edge cases](#edge-cases) gives the count of such names in each tag, and the rules for an emoji next to another form.

## Units, currencies and symbols

English and Portuguese take the words for units from the Unicode CLDR, release 49. The data ships in `text2spoken/data/cldr/` under the Unicode License v3, and `scripts/extract_cldr.py` writes it. A unit symbol that cannot be a word, such as `km/h`, `°C`, `kWh` or `µm`, reads with no list. A symbol made only of letters reads only when the language file lists it in `unit_symbols`, so `1 in 3` and `29 GB golds` keep `in` and `GB`.

`a/b` reads with the `per` pattern, and `²` and `³` read with the square and cubic patterns: `10 kg/m²` reads "ten kilograms per square metre", and `5 µm` reads "cinco micrómetros" in `pt-PT`. A Portuguese number takes the gender of its unit, so `2 h` reads "duas horas". A listed symbol that differs from a CLDR symbol only in case reads as that unit, so `5 ml` reads "five milliliters" in `en-US`, where CLDR writes `mL`.

Currency names and symbols come from the same release. A currency symbol before or after a number reads with the CLDR name of the currency, so `R$ 500` reads "five hundred Brazilian reals" and `₹50` reads "cinquenta rupias indianas" in `pt-PT`. A scale word may stand between the number and a symbol after it: `180 mil €` reads "cento e oitenta mil euros". A symbol with a currency sign, such as `$`, `€` or `₹`, reads with no list.

A symbol of letters, as an ISO 4217 code such as `CHF`, reads only when the language file lists it in `currency_symbols`, so `10 L` and `TOP 10` keep `L` and `TOP`. A symbol that two currencies share reads as the currency whose CLDR symbol it is. The language file names a currency where the CLDR name carries the country, as "dollar" for "US dollar", and gives its source. Portuguese writes each currency name with a small first letter, so `₹50` reads "cinquenta rupias indianas" in `pt-BR` too. A currency whose CLDR name is no word, as the `¤` of "(unknown currency)", does not read.

A character that no other form claims reads by its CLDR name, if it is outside ASCII and its Unicode general category is `Sm`, `Sc`, `Sk` or `So`, or if it is one of `§ ¶ † ‡ •`. `© 2024` reads "copyright two thousand and twenty-four", and `→` reads "right-pointing arrow". The language file may give its own name with a source: Portuguese reads `§` as "parágrafo". `NormalizationParams().without(Form.SYMBOL)` turns this off.

A name takes one space on each side where it touches a character that is no space. It takes none after an opening bracket or quote, and none before a closing bracket or quote, a full stop or a comma. So `§§ 5` reads "section section five", `©-5` reads "copyright minus five", and `(©)` reads "(copyright)". Before a phone number, a symbol counts as the words of its name, so `☎000` reads "telephone zero zero zero", as `telephone 000` does.

A character that a table of the language gives to another form, such as `°`, `‰`, `×` or a currency sign, belongs to that form wherever it stands. It stays as written when that form does not read it, so `the € sign` stays as written, and `3/4 ‰` stays as written as `3/4 kg` does. An emoji with emoji presentation, and a character with U+FE0F, a skin tone or a zero width joiner after it, stays as written. In an address, a character that the address tables do not name reads by its CLDR name: `a©b.com` reads "a copyright bee dot com".

These limits hold in English and in Portuguese. The limits of one language are on the [English](languages/en.md#limits-of-units-currencies-and-symbols) and [Portuguese](languages/pt.md#limits-of-units-currencies-and-symbols) pages.

- A fraction before a unit stays as written. `Espere 1/2 min.` and `A 1/2 kWh cell.` keep `1/2`.
- A language file that reads units from CLDR cannot give its own word for a unit.
- A year before a unit symbol in its CLDR case reads as a measure. `In 2020 kWh prices rose.` reads "two thousand and twenty kilowatt-hours prices", and `Em 2020 kWh os preços subiram.` reads "dois mil e vinte quilowatts-hora" in pt-PT. A list of years before such a symbol reads each year as a cardinal: `In 2019-2020 kWh were sold.`
- Two decimals read as a decimal when the language names no minor unit for the currency. `₹10.50` reads "ten point five zero Indian rupees", and `₹10,50` reads "dez vírgula cinco rupias indianas" in pt-PT.
- A sign that CLDR names before a number reads before the number. `₿1` reads "bitcoin one", and "bitcoin um" in pt-PT.
- A money range with a symbol at one end only stays as written, as `$5-10` does. `5–10 USD` and `CHF 5–10 per day` stay as written, and so does `5–10 EUR` in Portuguese.
- A doubled mark reads its singular name twice. `See §§ 2 and 3.` reads "See section section two and three.", and `Veja os §§ 2 e 3.` reads "Veja os parágrafo parágrafo dois e três".

## Edge cases

These cases come from tests that feed the library unusual text. A reader of ordinary prose rarely meets them.

### Emoji names that stay as written

The names hold `&` (en-GB 14, en-US 14), `!` (2 in each tag), `#` and `*` (the keycaps, 1 each in each tag), `/` (pt-PT 2), or a full stop that no abbreviation reads (en-US 9, as in `flag: St. Lucia` and `flag: U.S. Virgin Islands`, and pt-PT 6, in `Sra. Natal`). `scripts/extract_cldr.py` prints each such name.

### Emoji next to other forms

`❤` with no U+FE0F stays with `SYMBOL`, and `❤️` reads through the `EMOJI` form. In an address, an emoji sequence is one piece: `x@a👍🏽b.com` reads "ex at a thumbs up medium skin tone bee dot com", and with the form off "ex at a 👍🏽 bee dot com".

Every other form reads an emoji sequence as one character, as it reads `😀`, with the form on or off. U+FE0F, U+FE0E and U+20E3 are no part of a word next to another form, and the character before such a mark belongs to the emoji. So `❤️2 cats` reads "❤️two cats" with the form off, as `😀2 cats` does. The digit of a keycap joins no number: `Call 0800 123 456 2️⃣ to cancel` reads the phone number, as it does with `😀`, and the keycap stays as written with the form off.

An emoji sequence that holds U+FE0E, U+FE0F or U+20E3, starts with a letter or a digit and touches a letter or a digit on its left stays as written, together with the word it touches, with the form on or off: `Code 12️⃣ here.` and `See x.org1️⃣ now.` stay as written. The word is the run of letters, digits and combining marks right before the sequence, and a punctuation mark, a space or a symbol ends it. Nothing reads `O'` of `O'Neil1️⃣` or `well-` of `well-known1️⃣`, so they stay as written too.

A number, a measure or a date before a punctuation mark still reads, so `I have 2,cats1️⃣` reads "I have two,cats1️⃣", and `on 12/03/2024.Next1️⃣` reads the date. A digit before a skin tone is outside this rule, so `15🏽` reads the number.

A caller lexicon matches the text as written, so a key `#️⃣` reads its value. No match starts or ends inside an emoji sequence or inside the word that it touches. A sequence between two other spans joins them as one character, so `1❤️2❤️3` stays as written with the form off, as `1😀2😀3` does. With the form on, `10+4 ₡👍🏽+4 ₴` stays as written, as `10+4 ₡😂+4 ₴` does. With the form off, it reads "10+4 ₡👍🏽plus four ₴". The form claims after every other form and before `SYMBOL`, so `10+4 ₡-😂+4 ₴` reads as `10+4 ₡-©+4 ₴` does.

Regional indicators pair from the start of a run, as rules GB12 and GB13 of UAX #29 say: "Do not break within emoji flag sequences. That is, do not break between regional indicator (RI) symbols if there is an odd number of RI characters before the break point." So `🇵🇵🇹` is the pair `🇵🇵`, which names no flag, and a lone `🇹`, and it stays as written.

### Limits of the emoji form

- A character other than a space before a skin tone, U+FE0F or a zero width joiner belongs to the form, so `a🏽` stays as written. A digit before a skin tone still reads, as without the form: `5🏽` reads "five🏽".
- U+FE0E after an emoji asks for text presentation, and the form does not read it. `😂︎` reads "face with tears of joy ︎", and the U+FE0E stays after a space. `❤︎` is no emoji sequence, so `SYMBOL` reads it as "red heart ︎", with the form on or off.
- A tag sequence that Unicode does not list, such as `🏴` with the tags `gbxx`, reads by the name of its first emoji, "black flag", and the tag characters stay. They are invisible.
- An address keeps an emoji sequence whole, so a caller lexicon key for that sequence does not match in it. The output puts a space between the address and the sequence, and a second pass then reads the key. With a key `😀`, `x.org😀` reads "ex dot org 😀" with the form off. With the form on, the address reads the name of the sequence. A keycap key such as `1⃣` in `1⃣mail.com` breaks in the same way.
- The word that an emoji sequence touches stays as written, and the text before it reads on its own. So `Score 3-12️⃣` reads "Score three-12️⃣", and `Call (555) 123-45671️⃣` reads "Call (five hundred and fifty-five) one hundred and twenty-three-45671️⃣". With `😀` after the last digit, `Score 3-12😀` reads the range, and `Call (555) 123-45671😀` reads the phone number. `5km/next1️⃣` reads the measure, and `5km/next😀` stays as written.
- The join check of the core reads `10½+44 20 7946 0958 1😀.` as "10½+44 20 7946 0958 1 grinning face.", and a second pass reads the `1`. The form inherits this from `SYMBOL`: with the default params, `10½+44 20 7946 0958 1©.` breaks in the same way.

### A currency sign between a range and another sign

A currency sign between a range and another sign can keep the range as written, in English and in Portuguese. `0–2$€0` reads "0–2$zero euros", and a second pass reads "zero to two$zero euros", or "zero a dois$zero euros" in pt-PT. In `en-US`, `0–2$₽0` reads "0–2$zero Russian rubles", and a second pass reads "zero to two$zero Russian rubles". `en-GB` reads "roubles".

---
[← Usage](usage.md) · [Home](index.md) · [API →](api.md)
