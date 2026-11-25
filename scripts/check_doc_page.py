"""Check one page of README.md or docs/ against the code.

Usage: python scripts/check_doc_page.py PAGE

PAGE is a path from the checkout root, such as `docs/numbers.md`. The script runs the docs test of the page. Then
the check of the page compares the values of the sentences and tables below with the code. It exits 0 when they
are true, and 1 with the first mismatch. The `verify` line of each agent hint calls it.

- README.md: the variety tags of the Languages table, and the sentence "A tag with no language file reads ...".
- docs/index.md: the page links, the sentence that places the language pages, and the footer of each page.
- docs/quickstart.md: the empty extras and the Python floor.
- docs/how-it-reads.md: the Default column of the forms table.
- docs/numbers.md, docs/dates-and-times.md: each "the `FORM` form, such as ..., reads" sentence, and in
  numbers.md the `IDENTIFIER` sentence.
- docs/money-units-and-symbols.md: the "such as" sentence of `COLOR`, and the languages and release of the CLDR
  sentence.
- docs/addresses-letters-and-emoji.md: the "... offer the form" sentences of `ELECTRONIC` and `LETTERS`.
- docs/api.md: `PROBE_TIMEOUT`.
- docs/errors.md: each class name in backticks, and each sentence that names a subclass.
- docs/how-it-works.md: that the committed timing figure is current, and that the stage list of the page names each
  stage.
- docs/coverage.md: that the committed figures are current, and the sentences that name the languages with the
  most forms, the fewest forms, the most rows and the silver rows.
- docs/development.md: the CI Python versions, the CLDR and Unicode pins, the scripts/ and tests/ paths, and the
  test extra.
- docs/languages/<code>.md: the forms of the sentence "The file reads ...", and the forms that each sentence
  "The file reads no ..." names. Such a sentence is no full list, so a form that it leaves out is not checked.

The script reads no other prose. The docs test runs the examples of every page, and nothing checks the rest:
for example the signature table of docs/api.md, the rows of the case table of docs/errors.md, and docs/usage.md,
which has no check of its own.
"""
import builtins
import csv
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import NoReturn

import text2spoken
from text2spoken import Form, NormalizationParams, supports
from text2spoken.core import parsers
from text2spoken.core.language import _registry, core_language, rbnf_locales
from text2spoken.core.revision import PROBE_TIMEOUT

ROOT = Path(__file__).resolve().parent.parent

# The word that a "The file reads" sentence of a language page uses for each form, as a regex. `mentions` adds the
# word boundaries and a plural ending.
FORM_WORDS = {
    Form.CARDINAL: "cardinal", Form.ORDINAL: "ordinal", Form.DECIMAL: "decimal", Form.FRACTION: "fraction",
    Form.RANGE: "range", Form.EXPRESSION: "expression", Form.DATE: "date", Form.TIME: "time", Form.YEAR: "year",
    Form.MONEY: "money", Form.MEASURE: "measure", Form.PERCENT: "percentage",
    Form.TELEPHONE: "telephone|phone number", Form.IDENTIFIER: "identifier", Form.LETTERS: "capital|letter",
    Form.ABBREVIATION: "abbreviation", Form.IDIOM: "idiom", Form.ROMAN: "Roman", Form.COLOR: "colou?r",
    Form.ELECTRONIC: "address|e-mail", Form.SYMBOL: "symbol", Form.EMOJI: "emoji", Form.LEXICON: "lexicon",
}


def fail(page: str, message: str) -> NoReturn:
    sys.exit(f"{page}: {message}")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def language_code(page: str, name: str) -> str:
    """The code of a language name, from the Languages table of README.md."""
    codes = dict(re.findall(r"\[(\w+)\]\(docs/languages/(\w+)\.md\)", read("README.md")))
    if name not in codes:
        fail(page, f"{name!r} is not a language of the README Languages table")
    return codes[name]


def names(listed: str) -> list[str]:
    return re.split(r", | or | and ", listed)


def offers(code: str, form: Form) -> bool:
    return form in supports(code).forms


def mentions(sentence: str, form: Form) -> bool:
    return bool(re.search(rf"\b(?:{FORM_WORDS[form]})(?:s|es)?\b", sentence))


def check_such_as(page: str, text: str):
    """Each "the `FORM` form, such as A, B or C, reads" sentence names languages that offer the form."""
    sentences = re.findall(r"the `(\w+)` form, such as (.+?), reads", text)
    if not sentences:
        fail(page, "no 'the `FORM` form, such as ..., reads' sentence")
    for form, listed in sentences:
        for name in names(listed):
            if not offers(language_code(page, name), Form[form]):
                fail(page, f"{name} does not offer {form}")


def check_readme(page: str, text: str):
    registry = _registry()
    for code, cell in re.findall(r"languages/(\w+)\.md\) \| (.*) \|", text):
        tags = {variety.tag for variety in registry[code].varieties}
        for tag in re.findall(r"`([a-z]{2,3}(?:-[\w-]+)?)`", cell):
            if tag not in tags and tag not in registry:
                fail(page, f"{tag} is no variety of {code}")

    match = re.search(r"^A tag with no language file reads (.+?)\. ", text, re.M)
    if not match:
        fail(page, "no 'A tag with no language file reads' sentence")
    sentence = match[1]
    # Each code with CLDR spell-out rules or an ovos-number-parser writer, and no language file.
    no_file = ({re.split("[-_]", locale)[0] for locale in rbnf_locales()}
               | set(parsers.number_writer_languages())) - set(registry)
    sources = {"OvosNumberSpeller": "ovos-number-parser", "RbnfSpeller": "CLDR spell-out"}
    for code in sorted(no_file):
        source = sources[type(core_language(code).spellers[Form.CARDINAL]).__name__]
        if source not in sentence:
            fail(page, f"{code} reads with the words of {source}, which the no-file sentence does not name")
        for form in supports(code).forms:
            word = {Form.CARDINAL: "cardinal numbers", Form.DECIMAL: "decimals", Form.LEXICON: ""}.get(form)
            if word is None or word not in sentence:
                fail(page, f"{code} reads {form.name}, which the no-file sentence does not name")


def check_index(page: str, text: str):
    listed = list(dict.fromkeys(re.findall(r"\]\(([\w/-]+\.md)\)", text)))
    for path in sorted((ROOT / "docs").glob("*.md")) + sorted((ROOT / "docs/languages").glob("*.md")):
        name = path.relative_to(ROOT / "docs").as_posix()
        if name != "index.md" and name not in listed:
            fail(page, f"{name} is not listed")

    # The reading order: the pages of the first table, with the language pages after the page that the
    # index names.
    after = re.search(r"^The language pages come after \[.+?\]\(([\w-]+\.md)\) in the reading order\.", text, re.M)
    if not after:
        fail(page, "no sentence that places the language pages in the reading order")
    guides = [name for name in listed if not name.startswith("languages/")]
    languages = [name for name in listed if name.startswith("languages/")]
    at = guides.index(after[1]) + 1
    order = guides[:at] + languages + guides[at:]
    for before, next_page in zip(order, order[1:]):
        footer = read(f"docs/{before}").rstrip().splitlines()[-1]
        link = os.path.relpath(ROOT / "docs" / next_page, (ROOT / "docs" / before).parent)
        if f"]({link})" not in footer.split("[Home]")[-1]:
            fail(page, f"the footer of {before} does not lead to {next_page}")
        footer = read(f"docs/{next_page}").rstrip().splitlines()[-1]
        link = os.path.relpath(ROOT / "docs" / before, (ROOT / "docs" / next_page).parent)
        if f"]({link})" not in footer.split("[Home]")[0]:
            fail(page, f"the footer of {next_page} does not lead back to {before}")


def check_quickstart(page: str, text: str):
    project = tomllib.loads(read("pyproject.toml"))["project"]
    empty = sorted(name for name, requirements in project["optional-dependencies"].items() if not requirements)
    listed = ", ".join(f"`{name}`" for name in empty[:-1]) + f" and `{empty[-1]}`"
    if f"The extras {listed} add nothing" not in text:
        fail(page, f"the empty extras are {listed}")
    floor = project["requires-python"].removeprefix(">=")
    if f"Python {floor} or later" not in text:
        fail(page, f"the Python floor is {floor}")


def check_how_it_reads(page: str, text: str):
    stated = dict(re.findall(r"^\| `([A-Z]+)` \|.*\| (On|Off) \|$", text, re.M))
    defaults = NormalizationParams().forms
    for form in Form:
        default = "On" if form in defaults else "Off"
        if stated.get(form.name) != default:
            fail(page, f"the default of {form.name} is {default}")


def check_numbers(page: str, text: str):
    check_such_as(page, text)
    if not re.search(r"^The `IDENTIFIER` form .* No language file has a recognizer for it", text, re.M):
        fail(page, "no sentence that says no language file reads IDENTIFIER")
    readers = [code for code in _registry() if offers(code, Form.IDENTIFIER)]
    if readers:
        fail(page, f"{readers} offer IDENTIFIER")


def check_money(page: str, text: str):
    check_such_as(page, text)
    match = re.search(r"Some language files, such as (.+?), take the words for units, currencies and symbols "
                      r"from the Unicode CLDR, release (\d+)\.", text)
    if not match:
        fail(page, "no sentence that names the CLDR release")
    listed, release = match.groups()
    if not re.search(rf'^RELEASE = "{release}\.', read("scripts/extract_cldr.py"), re.M):
        fail(page, f"scripts/extract_cldr.py does not extract CLDR release {release}")
    for name in names(listed):
        for variety in _registry()[language_code(page, name)].varieties:
            for kind in ("", ".currencies", ".symbols"):
                if not (ROOT / f"text2spoken/data/cldr/{variety.tag}{kind}.json").exists():
                    fail(page, f"{name} has no CLDR file {variety.tag}{kind}.json")


def check_addresses(page: str, text: str):
    sections = {section.split("\n", 1)[0]: section for section in text.split("\n## ")[1:]}
    for heading, form in [("E-mail and web addresses", Form.ELECTRONIC), ("Runs of capital letters", Form.LETTERS)]:
        match = re.search(r"([A-Z]\w+(?:, [A-Z]\w+)*(?: and [A-Z]\w+)?) offers? (?:the|this) form", sections[heading])
        if not match:
            fail(page, f"no sentence in {heading!r} that names the languages that offer {form.name}")
        stated = {language_code(page, name) for name in names(match[1])}
        actual = {code for code in _registry() if offers(code, form)}
        if stated != actual:
            fail(page, f"{sorted(actual)} offer {form.name}, the page names {sorted(stated)}")


def check_api(page: str, text: str):
    if f"longer than {PROBE_TIMEOUT} seconds" not in text:
        fail(page, f"PROBE_TIMEOUT is {PROBE_TIMEOUT} seconds")


def check_errors(page: str, text: str):
    classes = vars(builtins) | vars(text2spoken)
    for name in re.findall(r"`(\w+(?:Error|Warning|Gender))`", text):
        if name not in classes:
            fail(page, f"{name} is not a class of text2spoken or of Python")

    errors = re.search(r"Every error in this page is a subclass of `(\w+)`, and so of `(\w+)`", text)
    warnings = re.search(r"Every warning is a subclass of `(\w+)`, which is a `(\w+)`", text)
    if not errors or not warnings:
        fail(page, "no sentence that gives the base class of every error and every warning")
    pairs = re.findall(r"`(\w+)` is (?:also )?a subclass of `(\w+)`", text) + [errors.groups(), warnings.groups()]
    for name in set(re.findall(r"`(\w+(?:Error|Warning|Gender))`", text)) & set(vars(text2spoken)):
        pairs.append((name, warnings[1] if name.endswith("Warning") else errors[1]))
    for child, parent in pairs:
        if child != parent and not issubclass(classes[child], classes[parent]):
            fail(page, f"{child} is not a subclass of {parent}")


def check_figures(page: str):
    """The committed figures equal the figures that `scripts/docs_figures.py` writes from the current data."""
    run = subprocess.run([sys.executable, "scripts/docs_figures.py", "--check"], cwd=ROOT, capture_output=True,
                         text=True)
    if run.returncode:
        fail(page, "a figure is out of date: " + run.stderr.strip())
    for alt in re.findall(r"!\[(.*?)\]\(figures/[\w-]+\.svg\)", read(page)):
        if len(alt) < 40:
            fail(page, f"the alt text {alt!r} holds no numbers")


def check_how_it_works(page: str, text: str):
    check_figures(page)
    for stage in ("Resolve", "Tokenize", "Recognize", "Claim", "Read"):
        if f"**{stage}.**" not in text:
            fail(page, f"no stage {stage}")


def rows_by_language() -> dict[str, tuple[int, int]]:
    counts = {}
    for path in sorted((ROOT / "tests/data").glob("*.tsv")):
        with open(path, encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t", quoting=csv.QUOTE_NONE))
        counts[path.stem] = (len(rows), sum(bool(re.search(r"\bsilver\b", row["source"])) for row in rows))
    return counts


def check_coverage(page: str, text: str):
    check_figures(page)
    forms = {code: len(supports(code).forms) for code in rows_by_language()}
    read = {form for code in forms for form in supports(code).forms}
    top = [code for code, count in forms.items() if count == len(read)]
    if not re.search(rf"^English reads all {len(read)} forms that any file reads\.", text, re.M) or top != ["en"]:
        fail(page, f"the files that read all {len(read)} forms are {top}")
    least = sorted(code for code, count in forms.items() if count == min(forms.values()))
    if least != ["ja", "ko"] or "Japanese and Korean read three" not in text or min(forms.values()) != 3:
        fail(page, f"the files with the fewest forms are {least}, with {min(forms.values())}")
    counts = rows_by_language()
    biggest = sorted(counts, key=lambda code: -counts[code][0])[:3]
    if biggest != ["pt", "en", "fr"] or "Portuguese, English and French hold the most rows" not in text:
        fail(page, f"the files with the most rows are {biggest}")
    cited_only = [code for code, (_, silver) in counts.items() if not silver]
    if len(cited_only) != 9 or "nine files hold only cited rows" not in text:
        fail(page, f"{len(cited_only)} files hold only cited rows")
    silver_names = {"nl": "Dutch", "de": "German", "it": "Italian", "pt": "Portuguese", "ru": "Russian",
                    "es": "Spanish", "tdt": "Tetun Dili"}
    silvered = sorted(code for code, (_, silver) in counts.items() if silver)
    if silvered != sorted(silver_names) or "Seven files hold silver rows" not in text:
        fail(page, f"the files with silver rows are {silvered}")
    listed = re.search(r"^Seven files hold silver rows: those of (.+?)\.", text, re.M)[1]
    if sorted(re.split(r", | and ", listed)) != sorted(silver_names.values()):
        fail(page, "the silver sentence names other languages")
    if "(22, 3)" not in text or (len(supports("en-GB").forms), len(supports("ja").forms)) != (22, 3):
        fail(page, "the doctest counts of en-GB and ja are not 22 and 3")


def check_development(page: str, text: str):
    workflow = read(".github/workflows/build-tests.yml")
    versions = json.loads(re.search(r"python_versions: '(.*)'", workflow)[1])
    project = tomllib.loads(read("pyproject.toml"))["project"]
    if project["requires-python"] != f">={versions[0]}":
        fail(page, f"requires-python is {project['requires-python']}, CI starts at {versions[0]}")
    if "on Python " + ", ".join(versions[:-1]) + " and " + versions[-1] not in text:
        fail(page, f"CI tests on Python {versions}")
    script = read("scripts/extract_cldr.py")
    for constant, word in [("RELEASE", "release"), ("UNICODE", "Unicode")]:
        pin = re.search(rf'^{constant} = "(.*)"', script, re.M)[1]
        if f"{word} {pin}" not in text:
            fail(page, f"scripts/extract_cldr.py pins {word} {pin}")
    # tests/data/id.tsv is the file that the walk-through of adding-a-language.md writes.
    for path in re.findall(r"(?:scripts|tests)/[\w/]+\.(?:py|tsv)", text):
        if "/id." not in path and not (ROOT / path).exists():
            fail(page, f"{path} does not exist")
    if "test" not in project["optional-dependencies"]:
        fail(page, "pyproject.toml has no test extra")


def check_language(page: str, text: str):
    code = Path(page).stem
    match = re.search(r"^The file reads (.*?)\.( |$)", text, re.M)
    if not match:
        fail(page, "no 'The file reads' sentence")
    if set(FORM_WORDS) != set(Form):
        fail(page, f"FORM_WORDS has no word for {set(Form) - set(FORM_WORDS)}")
    forms = supports(code).forms
    for form in Form:
        named = mentions(match[1], form)
        if named and form not in forms:
            fail(page, f"the sentence names {form.name}, which the file does not offer")
        if form in forms and not named:
            fail(page, f"the file offers {form.name}, which the sentence does not name")
    for sentence in re.findall(r"^The file reads no (.*?)\.(?: |$)", text, re.M):
        for form in forms:
            if mentions(sentence, form):
                fail(page, f"the file offers {form.name}, which a 'The file reads no' sentence names")


CHECKS = {
    "README.md": check_readme,
    "docs/index.md": check_index,
    "docs/quickstart.md": check_quickstart,
    "docs/how-it-reads.md": check_how_it_reads,
    "docs/numbers.md": check_numbers,
    "docs/dates-and-times.md": check_such_as,
    "docs/money-units-and-symbols.md": check_money,
    "docs/addresses-letters-and-emoji.md": check_addresses,
    "docs/how-it-works.md": check_how_it_works,
    "docs/coverage.md": check_coverage,
    "docs/api.md": check_api,
    "docs/errors.md": check_errors,
    "docs/development.md": check_development,
}


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    page = (ROOT / sys.argv[1]).resolve().relative_to(ROOT).as_posix()
    text = read(page)

    name = Path(page).name
    if page.startswith("docs/languages/"):
        code = Path(page).stem
        tests = ["tests/test_rows.py", "tests/test_docs_examples.py", "-k", f"{code}- or {name}"]
    else:
        tests = ["tests/test_docs_examples.py", "-k", name]
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *tests], cwd=ROOT,
                         capture_output=True, text=True)
    if run.returncode:
        fail(page, "the docs test fails:\n" + run.stdout[-3000:])

    check = check_language if page.startswith("docs/languages/") else CHECKS.get(page)
    if check:
        check(page, text)


if __name__ == "__main__":
    main()
