"""The two known limits of the address claim of design section 4.5, which the README lists. In these two cases a
second pass changes the first, because a context word or an abbreviation key does not see that a word belongs to
the reading of a span. The idempotency tests exclude exactly these cases and nothing broader."""
from text2spoken import Form, analyze, normalize
from text2spoken.core.tokens import is_punctuation


def known_limit(text: str, lang: str) -> str | None:
    """The limit that explains why a second pass changes `text`, or None.

    `abbreviation`: each span of the second pass is an abbreviation whose key is the last label of an address claim
    of the first pass with the full stop after the claim, as in `See a@b.etc.`.
    `time after @`: each span of the second pass is a time after the word "at" that a claim ending in `@` read,
    with only the same spaces and punctuation between them as in the text, as in `Write x.com@ 9:30`.
    """
    once = normalize(text, lang)
    claims = [span for span in analyze(text, lang).spans if span.form is Form.ELECTRONIC]
    second = analyze(once, lang).spans
    if not claims or not second:
        return None

    def abbreviation(span) -> bool:
        key = once[span.start:span.end]
        return span.form is Form.ABBREVIATION and key.endswith(".") and any(
            text[claim.end:claim.end + 1] == "." and text[claim.start:claim.end].endswith(key[:-1])
            and not text[claim.end - len(key):claim.end - len(key) + 1].isalpha() for claim in claims)

    def time_after_at(span) -> bool:
        before = once[:span.start]
        cut = len(before)
        while cut and (before[cut - 1].isspace() or is_punctuation(before[cut - 1])):
            cut -= 1
        words, between = before[:cut], before[cut:]
        return (span.form is Form.TIME and between != "" and words.split()[-1:] == ["at"]
                and any(text[claim.end - 1] == "@" and text.startswith(between + once[span.start:span.end], claim.end)
                        for claim in claims))

    if all(abbreviation(span) for span in second):
        return "abbreviation"
    if all(time_after_at(span) for span in second):
        return "time after @"
    return None
