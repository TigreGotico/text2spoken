"""Write text2spoken/data/wiktionary/it_noun_genders.json from the Italian noun categories of the English Wiktionary.

    python scripts/extract_noun_genders.py

The MediaWiki API lists the members of "Italian masculine nouns" and "Italian feminine nouns". A noun that is in
both categories has no single gender, and the file leaves it out. `function_words` lists the nouns of the file that
are also a preposition, a conjunction, an adverb, a pronoun, a determiner or an article: after a number such a word
may be a word that the number does not count, as "oggi" in `pagina 1 oggi`. The file keeps lowercase words of two or
more letters only. The Italian Wiktionary has no category for the gender of a noun, only "Sostantivi in
italiano", so the English Wiktionary is the source. The Wiktionary text is under CC BY-SA 4.0.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

API = "https://en.wiktionary.org/w/api.php"
HEADERS = {"User-Agent": "text2spoken-data/0.1 (noun gender list)"}
GENDERS = {"masculine": "Italian masculine nouns", "feminine": "Italian feminine nouns"}
FUNCTION_WORDS = ("Italian prepositions", "Italian conjunctions", "Italian adverbs", "Italian pronouns",
                  "Italian determiners", "Italian articles")
OUT = Path(__file__).resolve().parent.parent / "text2spoken" / "data" / "wiktionary" / "it_noun_genders.json"


def members(category: str) -> list[str]:
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
            return titles
        cont = data["continue"]
        time.sleep(1)


def main() -> None:
    lists = {name: set(members(category)) for name, category in GENDERS.items()}
    function = set().union(*(members(category) for category in FUNCTION_WORDS))
    both = lists["masculine"] & lists["feminine"]
    kept = {name: sorted(w for w in words - both if len(w) > 1 and w.isalpha() and w.islower())
            for name, words in lists.items()}
    nouns = set(kept["masculine"]) | set(kept["feminine"])
    OUT.write_text(json.dumps({
        "source": {
            "name": "English Wiktionary",
            "url": API,
            "categories": [*GENDERS.values()],
            "excluded": "words in both gender categories",
            "function_words": FUNCTION_WORDS,
            "licence": "CC BY-SA 4.0",
            "retrieved": date.today().isoformat(),
            "members": {name: len(words) for name, words in lists.items()},
        },
        **kept,
        "function_words": sorted(nouns & function),
    }, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"in masculine {len(lists['masculine'])} feminine {len(lists['feminine'])} both {len(both)} "
          f"function {len(function)}; out masculine {len(kept['masculine'])} feminine {len(kept['feminine'])} "
          f"function_words {len(nouns & function)}")


if __name__ == "__main__":
    main()
