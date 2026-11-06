"""Number parsing by the marks that a language declares for each digit script (design section 5.3)."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from text2spoken.core.tokens import digit_script, fold_digits, is_digit, is_word_char
from text2spoken.params import FrozenMap

SIGNS = {"-": "-", "−": "-", "+": "+"}
_CLUSTER_JOINERS = frozenset(":/")


@dataclass(frozen=True)
class Number:
    """A written number: offsets into the text, the sign, and ASCII digit strings."""
    start: int
    end: int
    sign: str
    integer: str
    fraction: str | None
    script: str

    def amount(self, prefix: str = "", suffix: str = "") -> FrozenMap:
        """The `DECIMAL` record of section 4.4; `fraction` is empty for an integer."""
        return FrozenMap({"integer": self.integer, "fraction": self.fraction or "", "sign": self.sign,
                          "prefix": prefix, "suffix": suffix, "script": self.script})


Marks = tuple[tuple[str, str, str], ...]
"""(script, decimal mark, group mark) for each script that a language declares."""


def _parse(cluster: str, decimal: str | None, group: str | None) -> tuple[str, str | None] | None:
    integer, _, fraction = cluster.partition(decimal) if decimal and decimal in cluster else (cluster, "", None)
    if fraction is not None and (fraction == "" or not fraction.isdigit()):
        return None
    if group and group in integer:
        head, *rest = integer.split(group)
        if not (1 <= len(head) <= 3 and head.isdigit() and all(len(g) == 3 and g.isdigit() for g in rest)):
            return None
        integer = head + "".join(rest)
    if integer and not integer.isdigit():
        return None
    if not integer and fraction is None:
        return None
    return integer, fraction


@lru_cache(maxsize=256)
def find_numbers(text: str, marks: Marks) -> tuple[Number, ...]:
    """Every written number in the text that parses whole by the declared marks.

    A cluster is a run of digits joined by single marks, colons or slashes. A cluster that does not parse
    whole, such as `16:9`, `1.2.3` or `1,23` in a language whose group mark is the comma, gives no number.
    """
    folded = fold_digits(text)
    by_script = {script: (decimal, group) for script, decimal, group in marks}
    joiners = _CLUSTER_JOINERS | {mark for _, decimal, group in marks for mark in (decimal, group) if mark}
    numbers = []
    i = 0
    while i < len(text):
        leading_mark = (text[i] in joiners and i + 1 < len(text) and is_digit(text[i + 1])
                        and (i == 0 or not (is_word_char(text[i - 1]) or text[i - 1] in joiners)))
        if not (is_digit(text[i]) or leading_mark):
            i += 1
            continue
        start = end = i
        end += 1
        while end < len(text):
            if is_digit(text[end]):
                end += 1
            elif text[end] in joiners and end + 1 < len(text) and is_digit(text[end + 1]):
                end += 1
            else:
                break
        i = end
        script = digit_script(text[start:end])
        if script is None:
            continue
        decimal, group = by_script.get(script, (None, None))
        cluster = folded[start:end]
        parsed = _parse(cluster, decimal, group)
        if parsed is None:
            continue
        sign = ""
        if start > 0 and text[start - 1] in SIGNS and (start == 1 or not is_word_char(text[start - 2])):
            sign = SIGNS[text[start - 1]]
            start -= 1
        numbers.append(Number(start, end, sign, parsed[0], parsed[1], script))
    return tuple(numbers)


def number_marks(data, decimal_mark: str | None) -> Marks:
    """The marks of each declared script: the entry whose decimal mark is `decimal_mark`, else the first entry."""
    marks = []
    for script, entries in data.get("number_marks", {}).items():
        entry = next((e for e in entries if e["decimal"] == decimal_mark), entries[0])
        marks.append((script, entry["decimal"], entry["group"]))
    return tuple(marks)


def declared_marks(data) -> frozenset[str]:
    """Every decimal and group mark that the language declares, for the tokenizer join."""
    return frozenset(mark for entries in data.get("number_marks", {}).values() for entry in entries
                     for mark in (entry["decimal"], entry["group"]))
