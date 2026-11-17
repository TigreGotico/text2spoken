"""Write text2spoken/data/wiktionary/el_nouns.json from the Greek noun and adjective entries of the English Wiktionary.

    curl -o kaikki-el.jsonl https://kaikki.org/dictionary/Greek/kaikki.org-dictionary-Greek.jsonl
    python scripts/extract_el_nouns.py kaikki-el.jsonl

The MediaWiki API lists the members of "Greek masculine nouns", "Greek feminine nouns", "Greek neuter nouns" and
"Greek adjectives". These categories give the gender of a noun and say which words are adjectives. The inflected
forms come from the Wiktextract dump of the same Wiktionary at kaikki.org, which expands the declension table of each
entry into forms with case and number tags. A noun form takes the gender of its entry, when the page of the entry is in
the category of that gender, and the cases of its tags. A page of a noun form that is in no gender category, as
"χρόνια", the neuter plural of "χρόνος", or "χρονών", the colloquial genitive plural of "χρόνος", gives its word the
gender of its head line, when no declension table of a noun holds the word. Its case comes from the tags of its sense,
as the genitive of "χρονών", and a page with no case tag, as "χρόνια", gives the nominative. An adjective
form takes the gender and the case of its tags. The vocative is left out, because no number stands before a noun in
the vocative. A word of an entry or a form of an article, a pronoun, a determiner, a preposition, a conjunction, a
particle or a contraction is no noun and no adjective, as "του" and "τους": the dump gives such a word as a form of a
noun table, as "του" in the table of "βάτος". The file keeps the lowercase forms of Greek letters only. The Wiktionary
text is under CC BY-SA 4.0.
"""
import json
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

API = "https://en.wiktionary.org/w/api.php"
DUMP = "https://kaikki.org/dictionary/Greek/kaikki.org-dictionary-Greek.jsonl"
HEADERS = {"User-Agent": "text2spoken-data/0.1 (noun gender list)"}
GENDERS = {"masculine": "Greek masculine nouns", "feminine": "Greek feminine nouns", "neuter": "Greek neuter nouns"}
ADJECTIVES = "Greek adjectives"
CODES = {"m": "masculine", "f": "feminine", "n": "neuter"}
CASES = {"nominative", "accusative", "genitive"}
FUNCTION_POS = ("article", "pron", "det", "prep", "prep_phrase", "conj", "particle", "contraction")
OUT = Path(__file__).resolve().parent.parent / "text2spoken" / "data" / "wiktionary" / "el_nouns.json"


def members(category: str) -> set[str]:
    titles, cont = [], {}
    while True:
        params = {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{category}", "cmlimit": "500",
                  "cmnamespace": "0", "format": "json", **cont}
        for attempt in range(8):
            try:
                request = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=HEADERS)
                with urllib.request.urlopen(request, timeout=60) as response:
                    data = json.load(response)
                break
            except urllib.error.HTTPError as error:
                if error.code != 429:
                    raise
                time.sleep(int(error.headers.get("retry-after", 5)) + 2 * attempt)
        else:
            raise RuntimeError(f"rate limited: {category}")
        titles += [member["title"] for member in data["query"]["categorymembers"]]
        if "continue" not in data:
            return set(titles)
        cont = data["continue"]
        time.sleep(1)


def greek_word(form: str) -> bool:
    return form.islower() and all(unicodedata.name(c, "").startswith("GREEK") for c in form)


def entry_genders(entry: dict) -> set[str]:
    """The genders that the head templates of a noun entry give, as `{{el-noun|m|...}}` and `g=f`."""
    found = set()
    for template in entry.get("head_templates", ()):
        args = template.get("args", {})
        values = [args.get("1", "")] if template.get("name") == "el-noun" else []
        values += [args.get(key, "") for key in ("g", "g2", "g3")]
        found |= {CODES[code] for value in values for code in value.split("-") if code in CODES}
    return found


def tagged(entry: dict) -> list[tuple[str, set[str]]]:
    """Each form of the declension table of an entry, with its tags."""
    return [(form["form"], set(form.get("tags", ()))) for form in entry.get("forms", ())
            if form.get("source") == "declension" and "tags" in form]


def main(dump: str) -> None:
    pages = {name: members(category) for name, category in GENDERS.items()}
    adjective_pages = members(ADJECTIVES)
    nouns = {g: {c: set() for c in sorted(CASES)} for g in GENDERS}
    adjectives = {g: {c: set() for c in sorted(CASES)} for g in GENDERS}
    with open(dump, encoding="utf-8") as lines:
        entries = [json.loads(line) for line in lines]
    function_words = {form for entry in entries if entry.get("pos") in FUNCTION_POS
                      for form in (entry.get("word", ""), *(f["form"] for f in entry.get("forms", ())))}
    noun_entries = adjective_entries = 0
    form_pages: dict[str, set[tuple[str, str]]] = {}
    for entry in entries:
        word = entry.get("word", "")
        if entry.get("pos") == "noun":
            genders = {g for g in GENDERS if word in pages[g]}
            if not genders:
                if len(entry_genders(entry)) == 1:
                    cases = {case for sense in entry.get("senses", ()) for case in CASES & set(sense.get("tags", ()))}
                    form_pages.setdefault(word, set()).update(
                        (gender, case) for gender in entry_genders(entry) for case in cases or {"nominative"})
                continue
            genders = (entry_genders(entry) & genders) or (genders if len(genders) == 1 else set())
            forms = [(word, {"nominative"}), *((f["form"], {"nominative"}) for f in entry.get("forms", ())
                                               if f.get("tags") == ["plural"] and "source" not in f),
                     *tagged(entry)]
            noun_entries += bool(genders)
            for gender in genders:
                for form, tags in forms:
                    if greek_word(form) and form not in function_words:
                        for case in CASES & tags:
                            nouns[gender][case].add(form)
        elif entry.get("pos") == "adj" and word in adjective_pages:
            adjective_entries += 1
            for form, tags in tagged(entry):
                if greek_word(form) and form not in function_words:
                    for gender in GENDERS.keys() & tags:
                        for case in CASES & tags:
                            adjectives[gender][case].add(form)
    known = {form for by_case in nouns.values() for forms in by_case.values() for form in forms}
    added = {word: readings for word, readings in form_pages.items()
             if word not in known and greek_word(word) and word not in function_words}
    for word, readings in added.items():
        for gender, case in readings:
            nouns[gender][case].add(word)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": {
            "name": "English Wiktionary",
            "categories": {"url": API, "names": [*GENDERS.values(), ADJECTIVES],
                           "members": {**{g: len(p) for g, p in pages.items()}, "adjectives": len(adjective_pages)}},
            "forms": {"url": DUMP, "name": "Wiktextract dump at kaikki.org", "entries": len(entries),
                      "noun_entries": noun_entries, "noun_form_pages": len(added),
                      "adjective_entries": adjective_entries, "function_words": len(function_words)},
            "licence": "CC BY-SA 4.0",
            "retrieved": date.today().isoformat(),
        },
        "nouns": {g: {c: sorted(forms) for c, forms in by_case.items()} for g, by_case in nouns.items()},
        "adjectives": {g: {c: sorted(forms) for c, forms in by_case.items()} for g, by_case in adjectives.items()},
    }, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    counts = {kind: {g: {c: len(f) for c, f in by_case.items()} for g, by_case in table.items()}
              for kind, table in (("nouns", nouns), ("adjectives", adjectives))}
    print(f"in: entries {len(entries)}, category members {[len(p) for p in pages.values()]} adjectives "
          f"{len(adjective_pages)}; used: noun entries {noun_entries}, noun form pages added {len(added)}, "
          f"adjective entries {adjective_entries}, function words {len(function_words)}; "
          f"out: {json.dumps(counts, ensure_ascii=False)}")


if __name__ == "__main__":
    main(sys.argv[1])
