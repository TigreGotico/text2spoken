# Korean

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

The number words come from the CLDR RBNF rule sets of `ko`: `spellout-numbering` for a number and a decimal, and the rule `-x` of `spellout-cardinal-sinokorean` for the minus. The word 마이너스 has the senses "the sign -" and "a number below 0" in the Standard Korean Language Dictionary of the National Institute of Korean Language. The decimal mark and the group mark come from the CLDR number symbols of `ko`. The docstring of [`ko.py`](../../text2spoken/lang/ko.py) names the rule of each reading.

Each of the 20 test rows in `tests/data/ko.tsv` names a source for its reading. No native speaker has checked any row.

## Limits

Korean leaves these forms as written:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `가격 ₩5,000` | `ko-KR` | stays as written | Money, percentages, measures, numeric dates and fractions stay as written, as in a language with no file. |
| `사과가 23개 있어요.` | `ko-KR` | stays as written | A number with a word right after it, with no space, stays as written. |
| `가격 -50 ₩` | `ko-KR` | stays as written | An amount with a minus stays as written too. |
| `구간 5 -10` | `ko-KR` | stays as written | A minus after a number can mark a range, so both numbers stay as written. |

---
[← Italian](it.md) · [Home](../index.md) · [Dutch →](nl.md)
