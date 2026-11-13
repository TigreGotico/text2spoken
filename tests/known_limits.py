"""The three known limits of the address claim of design section 4.5, which the README lists. In each, a word of the
reading of a claim becomes the key or the context of another form on a second pass, so the second pass changes the
first. The idempotency tests exclude exactly these cases and nothing broader."""
from dataclasses import replace

from text2spoken import Form, analyze, normalize
from text2spoken.core.spans import Analysis, Span, render
from text2spoken.core.tokens import is_punctuation


def _readings(analysis: Analysis, once: str) -> list[tuple[Span, int, int]]:
    """Each address claim of `analysis` with the start and the end of its reading in `once`, the first pass."""
    readings = []
    shift = 0
    for span in analysis.spans:
        spoken = len(render(replace(analysis, spans=(span,)))) - len(analysis.text) + span.end - span.start
        if span.form is Form.ELECTRONIC:
            start = span.start + shift + len(span.lead)
            readings.append((span, start, start + spoken - len(span.lead) - len(span.trail)))
        shift += spoken - (span.end - span.start)
    assert len(analysis.text) + shift == len(once)
    return readings


def known_limit(text: str, lang: str) -> str | None:
    """The limit that explains why a second pass changes `text`, or None.

    `abbreviation`: each span of the second pass is an abbreviation whose key is the end of the reading of a claim
    plus the full stop after the claim, as in `See a@b.etc.`.
    `time after @`: each span of the second pass is a time after a claim that ends in `@`, whose reading ends in
    "at", with only spaces and punctuation between them, as in `Write x.com@ 9:30`.
    `month at claim edge`: each span of the second pass is a date whose month word is the last or the first word of
    the reading of a claim, as in `See example.com/May 05 for details.` and `On 05 May@x.com we met.`.
    """
    once = normalize(text, lang)
    first = analyze(text, lang)
    second = analyze(once, lang).spans
    readings = _readings(first, once)
    if not readings or not second:
        return None
    months = {month.casefold() for month in first.request.data.get("months", ())}

    def abbreviation(span: Span) -> bool:
        return span.form is Form.ABBREVIATION and any(
            text[claim.end:claim.end + 1] == "." and span.end == end + 1
            and (span.start == start or start < span.start and once[span.start - 1] == " ")
            for claim, start, end in readings)

    def time_after_at(span: Span) -> bool:
        return span.form is Form.TIME and any(
            text[claim.end - 1] == "@" and once[start:end].split()[-1:] == ["at"] and end < span.start
            and all(char.isspace() or is_punctuation(char) for char in once[end:span.start])
            for claim, start, end in readings)

    def month_at_edge(span: Span) -> bool:
        if span.form is not Form.DATE:
            return False
        for _, start, end in readings:
            words = once[start:end].split()
            if (span.start == end - len(words[-1]) < end < span.end and words[-1].casefold() in months
                    or span.start < start < start + len(words[0]) == span.end and words[0].casefold() in months):
                return True
        return False

    if all(abbreviation(span) for span in second):
        return "abbreviation"
    if all(time_after_at(span) for span in second):
        return "time after @"
    if all(month_at_edge(span) for span in second):
        return "month at claim edge"
    return None
