# Japanese

The file `text2spoken/lang/ja.py` reads Japanese. It needs no extra, because its number words come from the CLDR spell-out rules.

## What it reads

The file reads what a language with no file reads: cardinals, decimals, a minus before them and lexicon entries. The number words are kanji numerals. The decimal mark reads 点, so `3.5` reads 三点五. Each digit after the mark reads alone.

| Written | Tag | Spoken |
| --- | --- | --- |
| `9.58` | `ja-JP` | 九点五八 |
| `19.19` | `ja-JP` | 十九点一九 |
| `円周率は「3.14」です。` | `ja-JP` | 円周率は「三点一四」です。 |
| `気温は（-3.5）度。` | `ja-JP` | 気温は（マイナス三点五）度。 |
| `23` | `ja-JP` | 二十三 |
| `-5` | `ja-JP` | マイナス五 |

## Varieties

| Tag | Decimal mark | Group mark |
| --- | --- | --- |
| `ja-JP` (the default variety) | Full stop | Comma |

The marks come from CLDR. `ja` serves every Japanese tag.

## Options

| Option | Values | Default (`ja-JP`) |
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

The number words come from the CLDR RBNF rule set `spellout-cardinal` of `ja`. The English Wiktionary entry "小数点" gives the reading of the decimal mark: "A decimal point itself is pronounced as てん". The docstring of [`ja.py`](../../text2spoken/lang/ja.py) quotes each source.

Each of the 23 rows in `tests/data/ja.tsv` cites a source. No native speaker has checked the rows.

## Limits

Japanese writes a number next to the word after it, with no space. The file keeps such a number as written. The Japanese phonemizer of the speech stack, pyopenjtalk-plus, reads it with the sound of its counter: `3本` gives サンボン and `1杯` gives イッパイ. In kanji numerals, pyopenjtalk-plus reads some numbers as other words, as 八百 as ヤオ.

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `私は23個のリンゴを持っています。` | `ja-JP` | stays as written | A number next to a kanji or a kana stays as written. |
| `3.5キロ` | `ja-JP` | stays as written | The same rule keeps a decimal before a word. |
| `2024年12月25日` | `ja-JP` | stays as written | A date with 年, 月 and 日 stays as written. |
| `3.0` | `ja-JP` | stays as written | A decimal whose digits after the mark are all zero stays as written. |
| `残高: -50 €` | `ja-JP` | stays as written | Money stays as written, as in a language with no file. |

---
[← Italian](it.md) · [Home](../index.md) · [Dutch →](nl.md)
