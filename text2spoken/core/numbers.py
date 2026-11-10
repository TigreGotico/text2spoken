"""Number parsing by the marks that a language declares for each digit script (design section 5.3)."""
from __future__ import annotations

from dataclasses import dataclass

from text2spoken.core.tokens import digit_script, fold_digits, is_digit, is_word_char, one_digit_set
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


def _separators(cluster: str, decimal: str | None, group: str | None) -> tuple[str | None, str] | None:
    """The decimal mark and the group marks that read `cluster`, or None when the marks do not say.

    `decimal` and `group` are runs of alternative marks. The first decimal mark is the canonical one, and the
    others are also accepted, as the dot is in French beside the comma. When the canonical mark and another mark
    both appear, the other one groups, as in `1.234,5`. A lone other mark with exactly three digits after it, as in
    `1.500`, could be a decimal or a group, so it reads as neither. A lone other mark with any other count of
    digits after it is a decimal mark, and one that repeats is a group, as in `1.000.000`."""
    decimal, group = decimal or "", group or ""
    if len(decimal) <= 1:
        return (decimal or None), group
    canonical, others = decimal[0], [mark for mark in decimal[1:] if mark in cluster]
    if canonical in cluster:
        return canonical, group + "".join(others)
    if not others:
        return canonical, group
    if len(others) > 1:
        return None
    mark = others[0]
    if cluster.count(mark) > 1:
        return None, group + mark
    tail = cluster.partition(mark)[2]
    return (None, group) if len(tail) == 3 and tail.isdigit() else (mark, group)


def _parse(cluster: str, decimal: str | None, group: str | None) -> tuple[str, str | None] | None:
    separators = _separators(cluster, decimal, group)
    if separators is None:
        return None
    mark, group = separators
    integer, _, fraction = cluster.partition(mark) if mark and mark in cluster else (cluster, "", None)
    if fraction is not None and (fraction == "" or not fraction.isdigit()):
        return None
    if group and any(m in integer for m in group):
        head, *rest = integer.translate({ord(m): group[0] for m in group}).split(group[0])
        if not (1 <= len(head) <= 3 and head.isdigit() and all(len(g) == 3 and g.isdigit() for g in rest)):
            return None
        integer = head + "".join(rest)
    if integer and not integer.isdigit():
        return None
    if not integer and fraction is None:
        return None
    return integer, fraction


def find_numbers(text: str, marks: Marks) -> tuple[Number, ...]:
    """Every written number in the text that parses whole by the declared marks.

    A cluster is a run of digits joined by single marks, colons or slashes. A cluster that does not parse
    whole, such as `16:9`, `1.2.3` or `1,23` in a language whose group mark is the comma, gives no number.
    """
    folded = fold_digits(text)
    by_script = {script: (decimal, group) for script, decimal, group in marks}
    joiners = _CLUSTER_JOINERS | {mark for _, decimal, group in marks for mark in decimal + group}
    leading = _CLUSTER_JOINERS | {mark for _, decimal, group in marks
                                  for mark in decimal + (group if len(group) == 1 else "")}
    numbers = []
    i = 0
    while i < len(text):
        leading_mark = (text[i] in leading and i + 1 < len(text) and is_digit(text[i + 1])
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
        if script is None or not one_digit_set(text[start:end]):
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
    """The marks of each declared script: the entry whose decimal marks start with `decimal_mark`, else the first
    entry. An entry may give several decimal marks, and several group marks: the first decimal mark is the
    canonical one, and each other mark is accepted too."""
    marks = []
    for script, entries in data.get("number_marks", {}).items():
        entry = next((e for e in entries if e["decimal"][:1] == decimal_mark), entries[0])
        marks.append((script, entry["decimal"], entry["group"]))
    return tuple(marks)


def declared_marks(data) -> frozenset[str]:
    """Every decimal and group mark that the language declares, for the tokenizer join. A space is no mark here,
    so the tokenizer keeps `1 000` as two tokens."""
    return frozenset(mark for entries in data.get("number_marks", {}).values() for entry in entries
                     for mark in entry["decimal"] + entry["group"] if not mark.isspace())
