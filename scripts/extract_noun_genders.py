"""Write text2spoken/data/wiktionary/it_noun_genders.json from the Italian noun categories of the English Wiktionary,
or text2spoken/data/wiktionary/fr_noun_genders.json from the French ones.

    python scripts/extract_noun_genders.py        # Italian
    python scripts/extract_noun_genders.py fr     # French

The MediaWiki API lists the members of "Italian masculine nouns" and "Italian feminine nouns". A noun that is in both
categories has no single gender, and the file lists it in `both`, as "cantante" and "abitante". `function_words` lists
the prepositions, conjunctions, adverbs, pronouns, determiners and articles: after a scale word such a word is no noun,
also when the noun list holds it, as "ieri" in `2.000.000 ieri`. The file keeps lowercase words of two or more letters
only. The Italian Wiktionary has no category for the gender of a noun, only "Sostantivi in italiano", so the English
Wiktionary is the source. The Wiktionary text is under CC BY-SA 4.0.

The French file reads "French masculine nouns" and "French feminine nouns" the same way, and lists in `both` the
words of both categories and the members of "French nouns with multiple genders", as "élève" and "enfant". It keeps
the words with a capital letter, such as the demonyms "Parisienne" and "Québécois", and the words with a hyphen, such
as "grand-mère", and leaves out the words with a space or another mark. It reads no function words, which the French
file takes from the French Wiktionary.
"""
import json
import sys
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
DATA = Path(__file__).resolve().parent.parent / "text2spoken" / "data" / "wiktionary"
OUT = DATA / "it_noun_genders.json"
FRENCH_GENDERS = {"masculine": "French masculine nouns", "feminine": "French feminine nouns"}
FRENCH_BOTH = "French nouns with multiple genders"
FRENCH_OUT = DATA / "fr_noun_genders.json"


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
    function = {word for category in FUNCTION_WORDS for word in members(category)
                if len(word) > 1 and word.isalpha() and word.islower()}
    both = lists["masculine"] & lists["feminine"]
    kept = {name: sorted(w for w in words if len(w) > 1 and w.isalpha() and w.islower())
            for name, words in {"masculine": lists["masculine"] - both, "feminine": lists["feminine"] - both,
                                "both": both}.items()}
    OUT.write_text(json.dumps({
        "source": {
            "name": "English Wiktionary",
            "url": API,
            "categories": [*GENDERS.values()],
            "both": "words in both gender categories, listed apart",
            "function_words": FUNCTION_WORDS,
            "licence": "CC BY-SA 4.0",
            "retrieved": date.today().isoformat(),
            "members": {name: len(words) for name, words in lists.items()},
        },
        **kept,
        "function_words": sorted(function),
    }, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"in masculine {len(lists['masculine'])} feminine {len(lists['feminine'])} both {len(both)}; "
          f"out masculine {len(kept['masculine'])} feminine {len(kept['feminine'])} both {len(kept['both'])} "
          f"function_words {len(function)}")


def french_word(word: str) -> bool:
    """A word of two or more letters, which may hold a hyphen between letters, in any case."""
    parts = word.split("-")
    return len(word) > 1 and all(part.isalpha() for part in parts)


def main_french() -> None:
    lists = {name: set(members(category)) for name, category in FRENCH_GENDERS.items()}
    several = set(members(FRENCH_BOTH))
    both = (lists["masculine"] & lists["feminine"]) | several
    kept = {name: sorted(w for w in words if french_word(w))
            for name, words in {"masculine": lists["masculine"] - both, "feminine": lists["feminine"] - both,
                                "both": both}.items()}
    FRENCH_OUT.write_text(json.dumps({
        "source": {
            "name": "English Wiktionary",
            "url": API,
            "categories": [*FRENCH_GENDERS.values(), FRENCH_BOTH],
            "both": "words in both gender categories or in the category of several genders, listed apart",
            "licence": "CC BY-SA 4.0",
            "retrieved": date.today().isoformat(),
            "members": {**{name: len(words) for name, words in lists.items()}, "several": len(several)},
        },
        **kept,
    }, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"in masculine {len(lists['masculine'])} feminine {len(lists['feminine'])} several {len(several)}; "
          f"out masculine {len(kept['masculine'])} feminine {len(kept['feminine'])} both {len(kept['both'])}")


if __name__ == "__main__":
    main_french() if sys.argv[1:] == ["fr"] else main()
