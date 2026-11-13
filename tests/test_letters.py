"""The `LETTERS` form of design section 4.6: the default, the run that the recognizer takes, the syllable rule, the
exception table, and the properties of section 11. Each expected value comes from the clause and the tables of the
language file, worked out by hand."""
import random
import time
from dataclasses import replace

import pytest

from tests.conftest import DATA, LETTERS_ON, row_params, rows
from tests.known_limits import known_limit
from tests.test_review_rules import ATOMS
from text2spoken import Form, FrozenMap, InvalidLexiconError, NormalizationParams, analyze, normalize, supports
from text2spoken.core import language as loader
from text2spoken.core import letters
from text2spoken.core.language import language_file
from text2spoken.core.letters import reading, splits_into_syllables
from text2spoken.params import DEFAULT_FORMS

EN, PT = language_file("en"), language_file("pt")
ROW_FILES = sorted(p.stem for p in DATA.glob("*.tsv"))


def _sets(spec) -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
    return tuple(frozenset(spec.data[key]) for key in ("letter_vowels", "letter_onsets", "letter_codas"))


def _registry(monkeypatch, *specs) -> None:
    registry = dict(loader._registry())
    for spec in specs:
        registry.update(dict.fromkeys((spec.code, *spec.serves), spec))
    monkeypatch.setattr(loader, "_registry", lambda: registry)


def _without_letters(spec):
    return replace(spec, recognizers=tuple(r for r in spec.recognizers if r.form is not Form.LETTERS),
                   verbalizers={form: v for form, v in spec.verbalizers.items() if form is not Form.LETTERS})


def test_the_form_is_off_by_default():
    assert Form.LETTERS not in NormalizationParams().forms and DEFAULT_FORMS == frozenset(Form) - {Form.LETTERS}
    assert normalize("A NATO e a RTP.", "pt-PT") == "A NATO e a RTP."
    assert normalize("Call the BBC at 9 AM.", "en-US") == "Call the BBC at nine AM."


@pytest.mark.parametrize("spec", [EN, PT], ids=["en", "pt"])
def test_with_the_form_off_every_row_reads_as_in_a_file_without_the_form(monkeypatch, spec):
    """The text of every row of every row file, in each variety, with the default params, against the same file with
    the recognizer and the verbalizer of `LETTERS` removed."""
    texts = [(row["text"], variety.tag) for code in ROW_FILES for row in rows(code) for variety in spec.varieties]
    with_form = [normalize(text, tag) for text, tag in texts]
    _registry(monkeypatch, _without_letters(spec))
    assert [normalize(text, tag) for text, tag in texts] == with_form


@pytest.mark.parametrize("code", ["de", "ru", "fr"])
def test_a_language_with_no_letter_names_does_not_offer_the_form(code):
    text = "NATO, BMW, RTP und MP3."
    assert Form.LETTERS not in supports(code).forms
    assert normalize(text, code, LETTERS_ON) == normalize(text, code) == text


@pytest.mark.parametrize(("spec", "word"), [
    (PT, "nato"), (PT, "onu"), (PT, "iva"), (PT, "sida"), (PT, "uefa"), (PT, "etar"), (PT, "atenção"),
    (PT, "eua"), (EN, "nato"), (EN, "uefa"), (EN, "warning"), (EN, "first"), (EN, "help"), (EN, "irs"),
    (EN, "usa"), (EN, "cia"), (EN, "scuba"), (EN, "aids"), (EN, "sports"), (EN, "events"), (EN, "results"),
])
def test_a_run_that_splits_into_syllables(spec, word):
    """na-to, o-nu, i-va, si-da, u-e-fa, e-tar, a-ten-ção, e-u-a; war-ning, first with coda rst, help with coda lp,
    irs with coda rs, u-sa, ci-a; scu-ba with onset sc, and a-ids, sports, e-vents and re-sults with a coda that
    takes the s of the -s/-z morpheme."""
    assert splits_into_syllables(word, *_sets(spec))


@pytest.mark.parametrize(("spec", "word"), [
    (PT, "rtp"), (PT, "ctt"), (PT, "cplp"), (PT, "bmw"), (PT, "irs"), (PT, "pib"), (PT, "tap"), (EN, "bbc"),
    (EN, "fbi"), (EN, "ibm"), (EN, "bmw"), (EN, "zdf"),
])
def test_a_run_that_does_not_split_into_syllables(spec, word):
    """No vowel (rtp, ctt, cplp, bmw, bbc, zdf), no coda rs or b or p in Portuguese (irs, pib, tap), no onset fb, and
    no coda b before a lone m (fbi, ibm)."""
    assert not splits_into_syllables(word, *_sets(spec))


@pytest.mark.parametrize(("run", "expected"), [
    ("ONU", "word"), ("ON", "letters"), ("A", None), ("A1", "letters"), ("4G", "letters"), ("12AB34", "letters"),
    ("TAP", "word"), ("EUA", "letters"), ("UEFA2", None), ("ONGs", None), ("PhD", None), ("ÇX", None),
    ("ΒΓΔ", None), ("ATENÇÃO", None), ("A٣", None),
])
def test_the_reading_of_a_run(run, expected):
    """Two letters read letter by letter, and one letter needs a digit. A run that reads as a word and holds a digit
    is not taken. A letter with no name, a lowercase letter, a combining mark and a digit outside ASCII end the
    run."""
    assert reading(run, PT.data) == expected


def test_the_fields_and_a_word_reading_that_keeps_its_text():
    request = analyze("A NATO e os CTT.", "pt-PT", LETTERS_ON).request
    found = [(s.start, s.end, dict(s.fields), s.keep) for s in letters.LETTERS.find("A NATO e os CTT.", (), request)]
    assert found == [(2, 6, {"letters": "NATO", "reading": "word"}, True),
                     (12, 15, {"letters": "CTT", "reading": "letters"}, False)]
    assert [(s.form, dict(s.fields)) for s in analyze("A NATO e os CTT.", "pt-PT", LETTERS_ON).spans] == [
        (Form.LETTERS, {"letters": "CTT", "reading": "letters"})]


def test_a_lexicon_value_that_the_form_reads_raises_and_a_word_does_not():
    word = NormalizationParams(lexicon=FrozenMap({"pt": FrozenMap({"OTAN": "NATO"})})).plus(Form.LETTERS)
    assert normalize("A OTAN reuniu.", "pt-PT", word) == "A NATO reuniu."
    spelled = NormalizationParams(lexicon=FrozenMap({"pt": FrozenMap({"canal um": "RTP"})}))
    assert normalize("Vi o canal um.", "pt-PT", spelled) == "Vi o RTP."
    with pytest.raises(InvalidLexiconError):
        normalize("Vi o canal um.", "pt-PT", spelled.plus(Form.LETTERS))


WORD_ROWS = {"en-386", "en-387", "en-396", "en-402", "en-403", "pt-167", "pt-168", "pt-169", "pt-170", "pt-171",
             "pt-186"}
"""Rows whose run reads as a word by the syllable rule, and whose letters all have a name: NATO, UEFA, WARNING, ONU,
IVA, SIDA, ETAR, SCUBA and AIDS. ATENÇÃO holds Ç, which has no name, so it stays as written either way."""
LETTER_ROWS = {"en-386", "en-387", "en-393", "en-397", "pt-167", "pt-172", "pt-173", "pt-174"}
"""Rows whose run of three or more letters reads letter by letter by the syllable rule: BMW, BBC, FBI, ZDF, RTP and
CTT. A run of two letters, as in MP3, reads letter by letter before the rule."""


def _failing_rows() -> set[str]:
    return {row["id"] for code in ("en", "pt") for row in rows(code) if row["form"] == "letters"
            and normalize(row["text"], row["tag"], row_params(row)) != row["expected"]}


@pytest.mark.parametrize(("verdict", "expected"), [(False, WORD_ROWS), (True, LETTER_ROWS)])
def test_the_syllable_rule_bites(monkeypatch, verdict, expected):
    assert _failing_rows() == set()
    monkeypatch.setattr(letters, "splits_into_syllables", lambda *args: verdict)
    assert _failing_rows() >= expected


@pytest.mark.parametrize(("spec", "run", "row"), [(EN, "IRS", "en-390"), (EN, "CIA", "en-390"), (EN, "USA", "en-391"),
                                                  (EN, "IBS", "en-404"), (EN, "IDS", "en-405"),
                                                  (PT, "TAP", "pt-178"), (PT, "EUA", "pt-179")])
def test_each_exception_bites(monkeypatch, spec, run, row):
    assert row not in _failing_rows()
    table = FrozenMap({k: v for k, v in spec.data["letter_runs"].items() if k != run})
    _registry(monkeypatch, replace(spec, data=FrozenMap({**spec.data, "letter_runs": table})))
    assert row in _failing_rows()


@pytest.mark.parametrize("spec", [EN, PT])
def test_no_exception_repeats_the_rule(spec):
    """An entry of `letter_runs` that the rule reads right never goes into the table (design section 4.6)."""
    for run, read in spec.data["letter_runs"].items():
        word = len(run) > 2 and splits_into_syllables(run.lower(), *_sets(spec))
        assert ("word" if word else "letters") != read, run


CAPITALS = ["NATO", "BMW", "RTP", "IRS", "TAP", "EUA", "MP3", "4G", "T2", "AM", "PM", "XIV", "CD", "ONGs", "PhD",
            "E.U.A.", "ATENÇÃO", "CIA", "Ç", "Ã", "W", "Q", "século ", "D. ", "Luís ", "A", "B", "Z"]


@pytest.mark.parametrize("seed", range(4))
def test_normalize_with_the_form_on_is_idempotent_on_random_text(seed):
    """Section 11 with `LETTERS` on: a second pass changes nothing, except in the known limits of the README. A
    text whose second pass changes with the form off too holds a defect of another form, outside this form."""
    rng = random.Random(seed)
    for _ in range(2000):
        lang = rng.choice(["en", "en-US", "pt-PT", "pt-BR"])
        text = "".join(rng.choice(ATOMS + CAPITALS) for _ in range(rng.randint(1, 30)))
        once = normalize(text, lang, LETTERS_ON)
        if normalize(once, lang, LETTERS_ON) == once or known_limit(text, lang, LETTERS_ON):
            continue
        off = normalize(text, lang)
        assert normalize(off, lang) != off, (text, once)


@pytest.mark.parametrize(("text", "lang", "expected"), [
    ("Sala 9#D. RTP.", "pt-PT", "released by a spelled run"), ("Sala 9-D. RTP.", "pt-PT", "released by a spelled run"),
    ("00 $‍52a@b.com... CD", "en", None),
])
def test_the_limit_of_the_form_holds_only_a_text_that_the_form_breaks(text, lang, expected):
    """Each text changes on a second pass with the form on. The last one changes with the form off too, so the spelled
    run `CD` does not cause the change."""
    once = normalize(text, lang, LETTERS_ON)
    assert normalize(once, lang, LETTERS_ON) != once
    off = normalize(text, lang)
    assert (normalize(off, lang) != off) == (expected is None)
    assert known_limit(text, lang, LETTERS_ON) == expected


@pytest.mark.parametrize(("unit", "lang"), [("BA", "pt-PT"), ("BCD", "pt-PT"), ("MP3 ", "en"), ("NATO-", "en")])
def test_a_long_run_of_capitals_takes_linear_time(unit, lang):
    def seconds(count: int) -> float:
        start = time.perf_counter()
        normalize(unit * count, lang, LETTERS_ON)
        return time.perf_counter() - start

    normalize(unit, lang, LETTERS_ON)
    small, large = min(seconds(500) for _ in range(3)), min(seconds(4000) for _ in range(3))
    assert large < 20 * small, (small, large)
