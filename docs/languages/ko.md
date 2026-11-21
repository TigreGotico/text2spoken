# Korean

<!-- agent-hint
covers: what the Korean file reads, its varieties, options, sources and limits.
source: text2spoken/lang/ko.py, tests/data/ko.tsv
generated: no
verify: pytest tests/test_rows.py tests/test_docs_examples.py -k "ko- or ko.md"
see: nl.md, ../how-it-reads.md
-->

The file `text2spoken/lang/ko.py` reads Korean. It needs no extra, because its number words come from the CLDR spell-out rules.

## What it reads

The file reads cardinals and decimals in the Sino-Korean numerals, with a minus, and lexicon entries. A minus reads 마이너스 before the number.

| Written | Tag | Spoken |
| --- | --- | --- |
| `정답은 42` | `ko-KR` | 정답은 사십이 |
| `인구 51,740,000` | `ko-KR` | 인구 오천백칠십사만 |
| `오늘 -5 날씨가` | `ko-KR` | 오늘 마이너스 오 날씨가 |
| `비율 3.5` | `ko-KR` | 비율 삼점오 |
| `값 -3.5` | `ko-KR` | 값 마이너스 삼점오 |

A number before a counter reads in the numerals of the counter, and the counter reads after one space. The native counters 개, 명, 마리, 살 and 시간 take the native numerals 한, 두, 세, 네 and 스무 from 1 to 99, and the Sino-Korean numerals from 100 up. 시 takes the native numerals for an hour from 1 to 12. The counters 년, 일, 개월, 원 and 층 take the Sino-Korean numerals, and so does 분 right after an hour. 월 after a month number reads the month name. A particle after the counter stays as written. A minus right after a counter is no sign and marks no range, so both numbers read.

| Written | Tag | Spoken |
| --- | --- | --- |
| `저는 사과가 23개 있어요.` | `ko-KR` | 저는 사과가 스물세 개 있어요. |
| `학생 3명이 왔다.` | `ko-KR` | 학생 세 명이 왔다. |
| `저는 20살이에요.` | `ko-KR` | 저는 스무 살이에요. |
| `3시 20분` | `ko-KR` | 세 시 이십 분 |
| `6월에 만나요` | `ko-KR` | 유월에 만나요 |
| `1,000원` | `ko-KR` | 천 원 |
| `100 마리` | `ko-KR` | 백 마리 |
| `기온은 0~-5` | `ko-KR` | 기온은 공~마이너스 오 |
| `7명-5` | `ko-KR` | 일곱 명-오 |

## Say-as

A say-as `ordinal` reads the native ordinal, from 1 to 99. A say-as `date` reads the long date of CLDR, `y년 MMMM d일`, with the month names 유월 for June and 시월 for October.

```python
>>> from text2spoken import SayAs, normalize
>>> normalize("3", "ko-KR", say_as=SayAs(interpret_as="ordinal"))
'셋째'
>>> normalize("12", "ko-KR", say_as=SayAs(interpret_as="ordinal"))
'열두째'
>>> normalize("2026-06-10", "ko-KR", say_as=SayAs(interpret_as="date"))
'이천이십육년 유월 십일'
>>> normalize("2026-10-06", "ko-KR", say_as=SayAs(interpret_as="date"))
'이천이십육년 시월 육일'
```

An ordinal of 0 or of 100 and up reads as a cardinal, because the native numerals end at 99.

## Varieties

| Tag | Decimal mark | Group mark |
| --- | --- | --- |
| `ko-KR` (the default variety) | Full stop | Comma |

The marks come from CLDR. `ko` serves every Korean tag.

## Options

| Option | Values | Default (`ko-KR`) |
| --- | --- | --- |
| `date_order` | changes nothing | - |
| `clock` | changes nothing | - |
| `minute_style` | changes nothing | - |
| `decimal_mark` | changes nothing | - |
| `scale` | changes nothing | - |
| `default_gender` | changes nothing | - |
| `phone_regions` | changes nothing | - |
| `register` | changes nothing | - |

## Sources

The number words come from the CLDR RBNF rule sets of `ko`: `spellout-numbering` for a number and a decimal, and the rule `-x` of `spellout-cardinal-sinokorean` for the minus. The word 마이너스 has the senses "the sign -" and "a number below 0" in the Standard Korean Language Dictionary of the National Institute of Korean Language. The ordinal comes from the rule set `spellout-ordinal-native`. The Standard Korean Language Dictionary gives 첫째, 둘째, 셋째, 열한째, 열두째, 스무째 and 스물두째, and article 6 of the Standard Language Rules (표준어 규정) gives 열두째 and 스물두째. The month names 유월 and 시월 come from article 52 of the Hangul Orthography (한글 맞춤법) and from the dictionary entries 유월 and 시월. The native numerals before a counter come from the rule set `spellout-cardinal-native-attributive`, and the dictionary entry 백 gives the Sino-Korean 백 before 개 and 살. The dictionary entry of each counter names the numerals it takes, and article 43 of the Hangul Orthography writes a counter apart from its number, as in 두 시 삼십 분. The decimal mark and the group mark come from the CLDR number symbols of `ko`. The docstring of [`ko.py`](../../text2spoken/lang/ko.py) names the rule of each reading.

Each of the 60 test rows in `tests/data/ko.tsv` names a source for its reading. No native speaker has checked any row.

## Limits

Korean leaves these forms as written:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `가격 ₩5,000` | `ko-KR` | stays as written | Money, percentages, measures, numeric dates and fractions stay as written, as in a language with no file. |
| `3분 동안` | `ko-KR` | stays as written | 분 counts minutes and honoured persons, so it reads only right after an hour. |
| `13시` | `ko-KR` | stays as written | No source gives the reading of an hour of 13 and up before 시. |
| `3~4개` | `ko-KR` | stays as written | No source gives the reading of a range before a counter. |
| `가격 -50 ₩` | `ko-KR` | stays as written | An amount with a minus stays as written too. |
| `구간 5 -10` | `ko-KR` | stays as written | A minus after a number can mark a range, so both numbers stay as written. |

---
[← Japanese](ja.md) · [Home](../index.md) · [Dutch →](nl.md)
