# Addresses, letters and emoji

<!-- agent-hint
covers: how addresses, runs of capital letters, abbreviations and emoji read.
source: text2spoken/core/electronic.py, text2spoken/core/letters.py, text2spoken/core/emoji.py
generated: no
verify: `python scripts/check_doc_page.py docs/addresses-letters-and-emoji.md`
see: api.md, languages/en.md, languages/pt.md
-->

This page shows how text2spoken reads e-mail and web addresses, runs of capital letters, abbreviations and emoji. Runs of capital letters and emoji are off by default.

## E-mail and web addresses

English and Portuguese read an address symbol by symbol. A word with `@`, `www.`, `://` or a top-level domain such as `.com` is spoken in full, even when it is not one valid address:

| Written | Spoken (`en-GB`) |
| --- | --- |
| `Write to ann@example.com today.` | Write to ann at example dot com today. |
| `Mail me@x.com,2 copies.` | Mail em e at ex dot com , two copies. |
| `Have you seen www.example.com?!` | Have you seen double-u double-u double-u dot example dot com?! |
| `See 20%.com` | See two zero % dot com |

The closing punctuation at the end of the word stays with the sentence, as `?!` does above. A character with no word in the address tables stays as written, between spaces, as `%` does above. English and Portuguese offer this form. The [Portuguese page](languages/pt.md#e-mail-and-web-addresses) gives the Portuguese names. The English limits are on the [English page](languages/en.md#edge-cases).

## Runs of capital letters

The `LETTERS` form reads a run of capital letters, such as `NATO`, `BMW` or `MP3`. The form is off by default, so a run stays as written and a phonemizer reads it. Turn it on with `plus`:

```python
>>> from text2spoken import Form, NormalizationParams, normalize
>>> letters = NormalizationParams().plus(Form.LETTERS)
>>> normalize("A NATO reuniu-se com a RTP.", "pt-PT", letters)
'A NATO reuniu-se com a érre tê pê.'
```

A run is two or more capital letters that touch no other letter, or one capital letter with digits. Digits can come before or after the letters, as in `MP3`, `4G` and `T2`. The form reads a run in one of three ways:

- A run of two letters, or of one letter and digits, reads letter by letter.
- A longer run that splits into syllables of the language reads as a word, so it stays as written.
- Any other run reads each letter by its name.

The digits of a run read as a number when they can name one. After letters that read as a word, they read as a cardinal. After spelled letters, one to three digits with no leading zero read as a cardinal, as the name of a road does. Any other digits read one by one. No usage source gives the reading of a road name, so this part is a ruling of the maintainer.

| Written | Tag | Spoken, `LETTERS` on |
| --- | --- | --- |
| `COVID19 spread.` | `en-GB` | COVID nineteen spread. |
| `Siga pela A25.` | `pt-PT` | Siga pela á vinte e cinco. |
| `Take the M25.` | `en-GB` | Take the em twenty-five. |
| `Agent B007.` | `en-GB` | Agent bee zero zero seven. |
| `A sigla ÇB.` | `pt-PT` | A sigla cê cedilhado bê. |

A clause in capitals is the text between two marks of a clause. Every word with a letter in it is in capitals, and the clause holds two words or more. A word is a run that reads as a word, so a code that reads letter by letter, such as `AGR` in `AO 1334 AGR`, does not count. The marks are the edges of the text and these signs: `. , ; : ! ? ( )` and the quotes. The full stop of a title, as in `D. ANA DA SILVA`, is no mark.

A capital alone that the `letter_words` table holds counts as a word, such as `I` and `A` in English or `A`, `E` and `O` in Portuguese. A text with words in lower case holds no clause, so `A EM é uma doença` spells `EM`. In a clause, a word of the `letter_words` table reads as a word, and so does a two-letter word that the word check of the language knows. Portuguese asks tugalex, behind the `pt` extra, and English has `letter_words` only. A two-letter acronym in no such list stays an acronym:

| Written | Tag | Spoken, `LETTERS` on |
| --- | --- | --- |
| `SAIA DA SALA` | `pt-PT` | stays as written |
| `DO NOT ENTER` | `en-GB` | stays as written |
| `IF IT IS` | `en-GB` | stays as written |
| `THE US AND UK` | `en-GB` | THE u ess AND u kay |
| `I DO` | `en-US` | stays as written |
| `ÇAÇA` | `pt-PT` | stays as written |

A word of a clause stays in capitals while a part next to it stays in capitals. When another form reads the parts next to it, or they read letter by letter, it is written in lower case. Their reading is in lower case too, so a second pass sees no clause there, and the word must already read as a word:

| Written | Tag | Spoken, `LETTERS` on |
| --- | --- | --- |
| `CAPÍTULO VI DE` | `pt-PT` | CAPÍTULO sexto de |
| `A RTP NO` | `pt-PT` | A érre tê pê no |
| `A RTP NO AR` | `pt-PT` | A érre tê pê no ar |
| `IF XIV IS` | `en-US` | if ex i vee is |

A Roman numeral right after a word of `letter_words` does not read, because a numeral follows a name or a noun. So `XIV` in `IF XIV IS` is a run, and it is spelled. A run that reads letter by letter is no word of a clause. So `IF XIV` alone is no clause, and `AO 1334 AGR` spells `AO`.

English and Portuguese offer the form. A language with no letter names keeps each run as written. The rules of each language are on the [English](languages/en.md#runs-of-capital-letters) and [Portuguese](languages/pt.md#runs-of-capital-letters) pages.

The form does not take a run with a lowercase letter (`ONGs`, `PhD`), a run with full stops (`E.U.A.`), a capital alone (`plano B`), or a Roman numeral that the `ROMAN` form reads (`século XIV`). With the form on, a run of capitals inside the reading of another form reads as this form reads it:

| Written | Tag | Spoken, `LETTERS` on |
| --- | --- | --- |
| `Call the BBC at 9 AM.` | `en-US` | Call the bee bee see at nine a em. |
| `Mail help@IRS.gov now.` | `en-US` | Mail help at i ar ess dot gov now. |

Digits joined to a unit symbol in capitals read as a measure when two conditions hold. The lowercase form is a unit symbol of the language, and no other CLDR unit symbol differs from it only in case:

| Written | Tag | Spoken, `LETTERS` on |
| --- | --- | --- |
| `Corri 5KM.` | `pt-PT` | Corri cinco quilómetros. |
| `Pesa 3KG.` | `pt-PT` | Pesa três quilogramas. |
| `I ran 5KM today.` | `en-GB` | I ran five kilometres today. |

## Abbreviations

| Written | Tag | Spoken |
| --- | --- | --- |
| `Dr Smith arrived.` | `en-GB` | Doctor Smith arrived. |
| `Bring pens, paper, etc.` | `en-GB` | Bring pens, paper, et cetera. |
| `Mora no n.º 5.` | `pt-PT` | Mora no número cinco. |
| `Kommen Sie z. B. morgen.` | `de-DE` | Kommen Sie zum Beispiel morgen. |

## Emoji

The `EMOJI` form reads an emoji by its CLDR name. It is off by default, because a chat reader wants the names and a book reader does not. Turn it on with `plus`:

```python
>>> emoji = NormalizationParams().plus(Form.EMOJI)
>>> normalize("Nice 👍🏽!", "en-GB", emoji)
'Nice thumbs up medium skin tone!'
```

| Case | Written | Spoken (`en-GB`, `EMOJI` on) | Spoken (`pt-PT`, `EMOJI` on) |
| --- | --- | --- | --- |
| Skin tone | `👍🏽` | thumbs up medium skin tone | polegar para cima tipo de pele quatro |
| Family | `👨‍👩‍👧‍👦` | family man woman girl boy | família homem mulher rapariga e rapaz |
| Flag | `🇵🇹` | flag Portugal | bandeira Portugal |
| Keycap | `1️⃣` | keycap one | tecla um |
| Repeated | `😂😂` | face with tears of joy face with tears of joy | cara com lágrimas de felicidade cara com lágrimas de felicidade |
| A sequence with no name | `😀🏽` | grinning face | cara sorridente |
| A name that cannot be read | `#️⃣` | stays as written | stays as written |

The form reads a whole emoji sequence as one emoji: an emoji with its skin tone, its U+FE0F, and the emoji that zero width joiners add to it. A sequence with no name of its own reads by the name of its first emoji. A name whose reading would hold a character that is no word stays as written, because a second pass would read that character.

Details for maintainers: the sequences come from the Unicode 17.0 emoji files, the version whose emoji CLDR 49 names. A name drops its quote marks, and its colons, commas and brackets become spaces. The language reads the digits and abbreviations of a name as in a sentence, and U+2019 between two letters is an apostrophe. The spacing of a name follows the `SYMBOL` form. [Development](development.md#the-emoji-data) gives the kinds of names that stay as written.

| Written | Tag | Spoken, `EMOJI` on |
| --- | --- | --- |
| `🥇` | `en-GB` | first place medal |
| `🕐` | `en-GB` | one o’clock |
| `(😂).` | `en-GB` | (face with tears of joy). |
| `🇦🇬` | `en-GB` | stays as written |

The emoji edge cases are at the [end of this page](#emoji-next-to-other-text).

## Edge cases

These cases come from tests that feed the library unusual text. A reader of ordinary prose rarely meets them.

### Emoji next to other text

An emoji sequence is one character for every other form, with the `EMOJI` form on or off. U+FE0F, U+FE0E and U+20E3 are no part of a word next to another form, and the character before such a mark belongs to the emoji. The `EMOJI` form claims after every other form and before `SYMBOL`.

| Written | Spoken (`en-GB`) | Spoken (`en-GB`, `EMOJI` on) | Why |
| --- | --- | --- | --- |
| `I ❤ it` | I red heart it | I red heart it | `❤` with no U+FE0F belongs to `SYMBOL`. |
| `I ❤️ it` | stays as written | I red heart it | `❤️` belongs to `EMOJI`. |
| `x@a👍🏽b.com` | ex at a 👍🏽 bee dot com | ex at a thumbs up medium skin tone bee dot com | In an address, an emoji sequence is one piece. |
| `❤️2 cats` | `❤️two cats` | red heart two cats | The number reads as it does after `😀`. |
| `😀2 cats` | 😀two cats | grinning face two cats | The number reads after the emoji. |
| `Call 0800 123 456 2️⃣ to cancel` | `Call zero eight zero zero one two three four five six 2️⃣ to cancel` | Call zero eight zero zero one two three four five six keycap two to cancel | The digit of a keycap joins no number. |
| `Code 12️⃣ here.` | stays as written | stays as written | A sequence with U+FE0E, U+FE0F or U+20E3 that starts with a letter or a digit, and touches a letter or a digit on its left, stays as written together with the word that it touches. |
| `See x.org1️⃣ now.` | stays as written | stays as written | The same rule: the word is the run of letters, digits and combining marks right before the sequence. |
| `O'Neil1️⃣` | stays as written | stays as written | Nothing reads the `O'` before the word, so it stays as written too. |
| `well-known1️⃣` | stays as written | stays as written | Nothing reads the `well-` before the word, so it stays as written too. |
| `I have 2,cats1️⃣` | `I have two,cats1️⃣` | `I have two,cats1️⃣` | A number before a punctuation mark still reads. |
| `on 12/03/2024.Next1️⃣` | `on the twelfth of March twenty twenty-four.Next1️⃣` | `on the twelfth of March twenty twenty-four.Next1️⃣` | A date before a punctuation mark still reads. |
| `15🏽` | fifteen🏽 | fifteen🏽 | A digit before a skin tone is outside the rule, so the number reads. |
| `1❤️2❤️3` | stays as written | one red heart two red heart three | A sequence between two spans joins them as one character, as `1😀2😀3` does. |
| `1😀2😀3` | stays as written | one grinning face two grinning face three | A sequence between two spans joins them as one character. |
| `10+4 ₡👍🏽+4 ₴` | 10+4 ₡👍🏽plus four ₴ | stays as written | With the form on, it stays as `10+4 ₡😂+4 ₴` does. |
| `10+4 ₡😂+4 ₴` | stays as written | stays as written | The comparison for the row above. |
| `10+4 ₡-😂+4 ₴` | 10+4 ₡-😂plus four ₴ | 10+4 ₡-😂plus four ₴ | The `EMOJI` form takes its characters before `SYMBOL` does, so this reads as `10+4 ₡-©+4 ₴` does. |
| `10+4 ₡-©+4 ₴` | 10+4 ₡-©plus four ₴ | 10+4 ₡-©plus four ₴ | The comparison for the row above. |
| `🇵🇵🇹` | stays as written | stays as written | Regional indicators pair from the start of a run, so `🇵🇵` names no flag and `🇹` is alone. |

The pairing of regional indicators follows rules GB12 and GB13 of UAX #29: "Do not break within emoji flag sequences. That is, do not break between regional indicator (RI) symbols if there is an odd number of RI characters before the break point."

### Limits of the emoji form

| Written | Spoken (`en-GB`) | Spoken (`en-GB`, `EMOJI` on) | Limit |
| --- | --- | --- | --- |
| `a🏽` | stays as written | stays as written | A character other than a space before a skin tone, U+FE0F or a zero width joiner belongs to the form. |
| `5🏽` | five🏽 | five🏽 | A digit before a skin tone still reads. |
| `😂︎` | stays as written | `face with tears of joy ︎` | U+FE0E after an emoji asks for text presentation, and the form does not read it. The U+FE0E stays after a space. |
| `❤︎` | `red heart ︎` | `red heart ︎` | `❤︎` is no emoji sequence, so `SYMBOL` reads it. |
| `🏴󠁧󠁢󠁸󠁸󠁿` | stays as written | `black flag 󠁧󠁢󠁸󠁸󠁿` | A tag sequence that Unicode does not list, here `🏴` with the tags `gbxx`, reads by the name of its first emoji. The tag characters stay, and they are invisible. |
| `Score 3-12️⃣` | `Score three-12️⃣` | `Score three-12️⃣` | The word that an emoji sequence touches stays as written, and the text before it reads on its own. |
| `Score 3-12😀` | Score three to twelve😀 | Score three to twelve grinning face | With `😀` after the last digit, the range reads. |
| `Call (555) 123-45671️⃣` | `Call (five hundred and fifty-five) one hundred and twenty-three-45671️⃣` | `Call (five hundred and fifty-five) one hundred and twenty-three-45671️⃣` | The word that the keycap touches stays as written. |
| `Call (555) 123-45671😀` | Call five five five one two three four five six seven one😀 | Call five five five one two three four five six seven one grinning face | With `😀` after the last digit, the phone number reads. |
| `5km/next1️⃣` | `five kilometres/next1️⃣` | `five kilometres/next1️⃣` | The measure reads. |
| `5km/next😀` | stays as written | 5km/next grinning face | The text stays as written. |

A digit that touches a name, such as the `1` of `1😀`, reads as the last group of a phone run before it, and a second pass changes nothing. The `EMOJI` form has this rule from `SYMBOL`, which does the same with the default params:

| Written | Spoken (`en-GB`, `EMOJI` on) | Second pass (`en-GB`, `EMOJI` on) |
| --- | --- | --- |
| `10½+44 20 7946 0958 1😀.` | ten½plus four four two zero seven nine four six zero nine five eight one grinning face. | ten½plus four four two zero seven nine four six zero nine five eight one grinning face. |
| `10½+44 20 7946 0958 1©.` | ten½plus four four two zero seven nine four six zero nine five eight one copyright. | ten½plus four four two zero seven nine four six zero nine five eight one copyright. |

A caller lexicon matches the text as written, so a key `#️⃣` reads its value. No match starts or ends inside an emoji sequence or inside the word that it touches:

```python
>>> from text2spoken import FrozenMap
>>> keycap = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"#️⃣": "hash key"})}))
>>> normalize("Press #️⃣ now.", "en-GB", keycap)
'Press hash key now.'
```

An address keeps an emoji sequence whole, so a lexicon key for that sequence does not match in it. The output puts a space between the address and the sequence, and a second pass then reads the key. A keycap key such as `1⃣` in `1⃣mail.com` breaks in the same way. With the form on, the address reads the name of the sequence:

```python
>>> grin = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"😀": "grin"})}))
>>> once = normalize("x.org😀", "en-GB", grin)
>>> once
'ex dot org 😀'
>>> normalize(once, "en-GB", grin)
'ex dot org grin'
>>> normalize("x.org😀", "en-GB", grin.plus(Form.EMOJI))
'ex dot org grinning face'
```

---
[← Money, units and symbols](money-units-and-symbols.md) · [Home](index.md) · [API →](api.md)
