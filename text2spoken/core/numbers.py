"""Number parsing by the marks that a language declares for each digit script (design section 5.3)."""
from __future__ import annotations

from collections.abc import Iterator, Mapping
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


def written_amount(amount: FrozenMap) -> str:
    """The `DECIMAL` record as plain digits, with a full stop before the fraction, for `plural_category`."""
    return (amount["integer"] or "0") + ("." + amount["fraction"] if amount["fraction"] else "")


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


def _parse(cluster: str, decimal: str | None, group: str | None,
           secondary: int | None = None) -> tuple[str, str | None] | None:
    """The integer and fraction digits of a cluster. Groups have three digits, or, with a secondary grouping size,
    three digits last and groups of that size before them, as `12,34,567` (UTS #35, Part 3, "Number Patterns")."""
    separators = _separators(cluster, decimal, group)
    if separators is None:
        return None
    mark, group = separators
    integer, _, fraction = cluster.partition(mark) if mark and mark in cluster else (cluster, "", None)
    if fraction is not None and (fraction == "" or not fraction.isdigit()):
        return None
    if group and any(m in integer for m in group):
        head, *rest = integer.translate({ord(m): group[0] for m in group}).split(group[0])
        sizes = [len(g) for g in rest]
        if not ((1 <= len(head) <= 3 and set(sizes) == {3})
                or (secondary and 1 <= len(head) <= secondary and sizes[-1] == 3 and set(sizes[:-1]) <= {secondary})):
            return None
        integer = head + "".join(rest)
    if integer and not integer.isdigit():
        return None
    if not integer and fraction is None:
        return None
    return integer, fraction


def _grouped(text: str, start: int, end: int) -> bool:
    """Whether the space at text[end] groups the digits of a number that starts at `start`: three digits follow it
    and no more, and the digits before it are one to three at the start of the number, else exactly three. So
    `1 000` is one number and `70 90 80` is three."""
    after = text[end + 1:end + 4]
    if len(after) < 3 or not all(map(is_digit, after)) or (end + 4 < len(text) and is_digit(text[end + 4])):
        return False
    first = end
    while first > start and is_digit(text[first - 1]):
        first -= 1
    return end - first <= 3 if first == start else end - first == 3


def _spaces(marks: Marks) -> frozenset[str]:
    """The spaces of each run of group marks: a space joins only groups of three digits (`_grouped`), it is no
    leading mark, and the tokenizer does not join at it. A single group mark that is a space, as the no-break space
    of `ru`, joins every cluster."""
    return frozenset(mark for _, _, group in marks if group and len(group) > 1 for mark in group if mark.isspace())


def _clusters(text: str, marks: Marks, declared: frozenset[str]) -> Iterator[tuple[int, int, tuple[int, ...]]]:
    """Each cluster of the text: its start, its end, and the offset of each space in it that groups digits.

    A cluster is a run of digits joined by single marks, colons or slashes. A mark of `marks` or of `declared`
    joins a cluster. A space of a run of group marks joins it only between groups of three (`_grouped`). The group
    mark `'` joins only digits on both sides: before digits it is an apostrophe, as in `anni '60`, so `60` is a
    number."""
    joiners = _CLUSTER_JOINERS | declared | {mark for _, decimal, group in marks
                                             for mark in (decimal or "") + (group or "")}
    spaces = _spaces(marks)
    leading = joiners - {mark for _, _, group in marks if group and len(group) > 1 for mark in group}
    i = 0
    while i < len(text):
        leading_mark = (text[i] in leading and text[i] != "'" and i + 1 < len(text) and is_digit(text[i + 1])
                        and (i == 0 or text[i - 1] in spaces
                             or not (is_word_char(text[i - 1]) or text[i - 1] in joiners)))
        if not (is_digit(text[i]) or leading_mark):
            i += 1
            continue
        start = end = i
        end += 1
        grouping = []
        while end < len(text):
            if is_digit(text[end]):
                end += 1
            elif text[end] in joiners and end + 1 < len(text) and is_digit(text[end + 1]):
                if text[end] in spaces:
                    if not _grouped(text, start, end):
                        break
                    grouping.append(end)
                end += 1
            else:
                break
        i = end
        yield start, end, tuple(grouping)


def group_spaces(text: str, marks: Marks, declared: frozenset[str] = frozenset()) -> tuple[int, ...]:
    """The offset of each space that `find_numbers` reads as a group mark between two groups of digits, as in
    `1 000`. A recognizer that reads digits with a pattern of its own drops these spaces first, so that it reads
    `1 000` whole, as `find_numbers` does. A language with no run of group marks that holds a space has none."""
    if not _spaces(marks):
        return ()
    return tuple(offset for _, _, grouping in _clusters(text, marks, declared) for offset in grouping)


def find_numbers(text: str, marks: Marks, declared: frozenset[str] = frozenset(),
                 grouping: Mapping[str, int] = FrozenMap()) -> tuple[Number, ...]:
    """Every written number in the text that parses whole by `marks`.

    A cluster (`_clusters`) that does not parse whole by `marks`, such as `16:9`, `1.2.3` or `1,23` in a
    language whose group mark is the comma, gives no number. So in a variety that declares a second set of marks,
    such as de-CH, `,5` gives no number when the comma is not a mark of `marks`, as `0,5` gives none.

    `grouping` gives the secondary grouping size of each script that has one, as 2 for `Latn` in `hi`.
    """
    folded = fold_digits(text)
    by_script = {script: (decimal, group) for script, decimal, group in marks}
    numbers = []
    for start, end, _ in _clusters(text, marks, declared):
        script = digit_script(text[start:end])
        if script is None or not one_digit_set(text[start:end]):
            continue
        decimal, group = by_script.get(script, (None, None))
        cluster = folded[start:end]
        parsed = _parse(cluster, decimal, group, grouping.get(script))
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
    """Every decimal and group mark that the language declares, for the tokenizer join. A space of a run of group
    marks is no mark here, so the tokenizer keeps `1 000` as two tokens in French."""
    return frozenset(mark for entries in data.get("number_marks", {}).values() for entry in entries
                     for mark in entry["decimal"] + entry["group"]
                     if not (mark.isspace() and len(entry["group"]) > 1))
