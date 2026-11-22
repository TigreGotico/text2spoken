# Chinese

<!-- agent-hint
covers: what the Chinese file reads, its varieties, options, sources and limits.
source: text2spoken/lang/zh.py, tests/data/zh.tsv
generated: no
verify: `python scripts/check_doc_page.py docs/languages/zh.md`
see: ../adding-a-language.md, ../how-it-reads.md
-->

The file `text2spoken/lang/zh.py` reads Mandarin Chinese, in Simplified characters for `zh-CN` and in Traditional characters for `zh-TW`. Its number words come from the CLDR RBNF rule sets of `zh` and `zh_Hant`, which `unicode-rbnf` holds. The base install holds it.

## What it reads

The file reads cardinals, ordinals, years, decimals, fractions, percentages, dates, money, measures and lexicon entries. Chinese writes a number next to the word that follows it, with no space, and the file reads the number there. The word after the number chooses its reading:

| Written | Tag | Spoken |
| --- | --- | --- |
| `我有23个苹果。` | `zh-CN` | 我有二十三个苹果。 |
| `我有2个苹果。` | `zh-CN` | 我有两个苹果。 |
| `他在这里住了2年。` | `zh-CN` | 他在这里住了两年。 |
| `我们走了200公里。` | `zh-CN` | 我们走了两百公里。 |
| `他赢了2万元。` | `zh-CN` | 他赢了两万元。 |
| `房间号是102。` | `zh-CN` | 房间号是一百零二。 |
| `气温是-5度。` | `zh-CN` | 气温是负五度。 |
| `会议在3月4日举行。` | `zh-CN` | 会议在三月四日举行。 |
| `现在2点。` | `zh-CN` | 现在两点。 |
| `火车3点30分开。` | `zh-CN` | 火车三点三十分开。 |
| `这是第2次。` | `zh-CN` | 这是第二次。 |
| `我2023年毕业。` | `zh-CN` | 我二〇二三年毕业。 |
| `他2000年5月出生。` | `zh-CN` | 他二〇〇〇年五月出生。 |
| `汉朝建于公元前202年。` | `zh-CN` | 汉朝建于公元前二百〇二年。 |
| `日期是2023-05-01。` | `zh-CN` | 日期是二〇二三年五月一日。 |
| `圆周率约是3.14。` | `zh-CN` | 圆周率约是三点一四。 |
| `价格上涨了50%。` | `zh-CN` | 价格上涨了百分之五十。 |
| `只有1/3的人来了。` | `zh-CN` | 只有三分之一的人来了。 |
| `这本书¥100。` | `zh-CN` | 这本书一百元。 |
| `价格：US$5。` | `zh-CN` | 价格：五美元。 |
| `这袋米2kg。` | `zh-CN` | 这袋米两千克。 |
| `今天气温25°C。` | `zh-CN` | 今天气温二十五摄氏度。 |

Before a measure word, such as 个, 年, 本, 点 or 公里, the digit 2 reads 两, as in 两个 and 两百. In other positions it reads 二, as in 二十二, 第二 and 三月. The measure words are the entries of `number_words` with the value `counter`. A word that names an item, as 月, 号 and 年代, takes the plain number.

A year in four digits reads digit by digit, with 〇 for zero. A number before 年 is a year when a year word such as 公元 or 民国 comes before it. A number of four digits before 年 is a year too, unless it is a round hundred with no month after it. Any other number before 年 counts years. A numeric date with the year first takes the order of the CLDR long date, year, month and day.

A percentage reads 百分之 and the number, and a fraction reads the denominator, 分之 and the numerator. An amount reads its number before the name of the currency. The renminbi and the New Taiwan dollar read 元.

## Varieties

| Tag | Notes |
| --- | --- |
| `zh-CN` | Simplified characters. The default variety, for `zh` and `cmn`. |
| `zh-TW` | Traditional characters. Number words, currency names, unit names and the round thousands of years follow CLDR `zh_Hant`. |

| Written | Tag | Spoken |
| --- | --- | --- |
| `門票$300。` | `zh-TW` | 門票三百元。 |
| `這個¥100。` | `zh-TW` | 這個一百日圓。 |
| `今天氣溫25°C。` | `zh-TW` | 今天氣溫攝氏 二十五 度。 |
| `他2000年5月出生。` | `zh-TW` | 他二千年五月出生。 |
| `我有2個蘋果。` | `zh-Hant-TW` | 我有兩個蘋果。 |
| `圓周率約是3.14。` | `zh-Hant-TW` | 圓周率約是三點一四。 |

The number words of a tag come from the CLDR locale of its script. A tag that names no script takes the script that CLDR 49 likely subtags give for its language and region. So `zh-TW`, `zh-HK` and `zh-MO` take the words of `zh_Hant`, as `zh-Hant-TW` does: 兩, 點, 萬, 億 and 負. `我有2個蘋果。` reads 我有兩個蘋果。 for both `zh-TW` and `zh-Hant-TW`. A bare `yue` takes its motherland region, CN, so it reads Simplified number words, and `yue-HK` reads Traditional number words.

## Options

| Option | Values | Default (`zh-CN`) |
| --- | --- | --- |
| `date_order` | changes nothing | - |
| `clock` | changes nothing | - |
| `minute_style` | changes nothing | - |
| `decimal_mark` | changes nothing | - |
| `scale` | changes nothing | - |
| `default_gender` | changes nothing | - |
| `phone_regions` | changes nothing | - |
| `register` | changes nothing | - |

Chinese numbers have no gender. A numeric date reads only with the year first, so `date_order` has no date to choose for. The file always reads the full stop as the decimal mark and the comma as the group mark, as CLDR `zh` writes them.

## Sources

The number words come from the CLDR 49 RBNF rule sets `spellout-cardinal`, `spellout-cardinal-alternate2`, `spellout-numbering`, `spellout-numbering-year` and `spellout-ordinal` of `zh` and `zh_Hant`. The rule for 两 and 二 comes from the usage notes of the English Wiktionary entry 兩. The measure words come from the classifier senses of their Wiktionary entries. The entries 第, 百分之, 分之, 點, 年, 年代, 月, 日, 號, 公元, 西元 and 民國 give the other rules. Currency names, unit names and the long date pattern come from CLDR 49. The docstring of [`zh.py`](../../text2spoken/lang/zh.py) quotes the source of each rule.

Each of the 72 rows in `tests/data/zh.tsv` cites a source. 13 guard rows pin text that the file leaves as written, because a wrong reading is worse than none. No native speaker has checked the rows.

## Limits

The file reads no times, ranges, telephone numbers, Roman numerals, symbols, emoji, colours, expressions or web and email addresses. `supports("zh")` lists the forms it reads. Chinese also leaves these forms as written:

| Written | Tag | Spoken | Limit |
| --- | --- | --- | --- |
| `会议12:30开始。` | `zh-CN` | stays as written | A time stays as written. ovos-date-parser has no Chinese module. |
| `我们2人一起去。` | `zh-CN` | stays as written | Before a word that is not in `number_words`, a number reads only when 二 and 两 give the same words. 2人 and 20000人 stay as written, and 3人 reads 三人. |
| `他身高2米。` | `zh-CN` | stays as written | 米 is not in `number_words`, so the metre after 2 stays as written. |
| `这座城有2000年的历史。` | `zh-CN` | stays as written | A round hundred of four digits before 年 can be a year or a count of years. It reads only when a month follows. |
| `公司市值¥3亿。` | `zh-CN` | stays as written | An amount with a numeral after it stays as written. |
| `价格是¥3.50。` | `zh-CN` | stays as written | An amount with decimals stays as written. |
| `这袋米5kg。` | `zh-TW` | stays as written | CLDR `zh_Hant` writes the kilogram 公斤, so `kg` is no unit of `zh-TW`. |
| `屏幕比例是16:9。` | `zh-CN` | stays as written | A colon between two numbers can be a ratio, a verse or a time. |

---
[← Tetun Dili](tdt.md) · [Home](../index.md) · [Adding a language →](../adding-a-language.md)
