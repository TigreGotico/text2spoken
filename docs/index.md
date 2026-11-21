# text2spoken documentation

<!-- agent-hint
covers: the list of every docs page in reading order.
source: docs/, tests/test_docs_examples.py:MINIMUM
generated: no
verify: for f in docs/*.md docs/languages/*.md; do grep -qF "(${f#docs/})" docs/index.md || echo "not listed: $f"; done (prints only docs/index.md)
see: quickstart.md
-->

text2spoken rewrites written forms, such as `12/03/2024`, `£3.50` or `Dr`, into the words that a speaker says. Find the page for your question below. The pages are in reading order, from a first call to the contract of a language file.

| Question | Page |
| --- | --- |
| How do I install it and get spoken text? | [Quickstart](quickstart.md) |
| How do I turn a form off or on, pick a variety, or add my own words? | [Usage](usage.md) |
| Why did a text read this way, and what stays as written? | [How it reads text](how-it-reads.md) |
| How does it read numbers? | [Numbers](numbers.md) |
| How does it read dates, times and years? | [Dates and times](dates-and-times.md) |
| How does it read money, units, percentages and symbols? | [Money, units and symbols](money-units-and-symbols.md) |
| How does it read addresses, capital letters, abbreviations and emoji? | [Addresses, letters and emoji](addresses-letters-and-emoji.md) |
| What does each function, param and field do? | [API](api.md) |
| What does each error and warning mean? | [Errors and warnings](errors.md) |
| How do I add my language? | [Adding a language](adding-a-language.md) |
| How do I run the tests, write the row files, or release? | [Development](development.md) |

## Languages

Each language page gives what the language reads, its varieties and the codes that it serves, its options, its sources and its limits.

| Language | Page |
| --- | --- |
| Arabic | [ar](languages/ar.md) |
| Catalan | [ca](languages/ca.md) |
| German | [de](languages/de.md) |
| Greek | [el](languages/el.md) |
| English | [en](languages/en.md) |
| Spanish | [es](languages/es.md) |
| Basque | [eu](languages/eu.md) |
| French | [fr](languages/fr.md) |
| Italian | [it](languages/it.md) |
| Japanese | [ja](languages/ja.md) |
| Korean | [ko](languages/ko.md) |
| Dutch | [nl](languages/nl.md) |
| Portuguese | [pt](languages/pt.md) |
| Russian | [ru](languages/ru.md) |
| Chinese | [zh](languages/zh.md) |

The language pages come after [Errors and warnings](errors.md) in the reading order.
