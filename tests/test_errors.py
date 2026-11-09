"""The failure policy (design section 10) and the lexicon (sections 2.2 and 11)."""
import logging

import pytest

from text2spoken import (Features, Form, FrozenMap, HintWarning, InvalidHintError, InvalidLanguageTagError,
                         InvalidLexiconError, NormalizationParams, UnreadFormError, analyze, normalize, render)


def lexicon(**by_tag):
    return NormalizationParams(lexicon=FrozenMap({tag: FrozenMap(entries) for tag, entries in by_tag.items()}))


def test_the_lexicon_claims_before_every_recognizer():
    assert normalize("ACME sold 3 tins.", "en", lexicon(en={"ACME": "acme"})) == "acme sold three tins."


def test_the_lexicon_matches_a_whole_form_with_its_case_and_an_apostrophe_limit():
    p = lexicon(en={"ACME": "acme"})
    assert normalize("ACME's tins and l'ACME", "en", p) == "acme's tins and l'acme"
    assert normalize("ACMES and acme", "en", p) == "ACMES and acme"


def test_the_longer_key_wins():
    p = lexicon(en={"New": "nu", "New York": "nu york"})
    assert normalize("New York and New Delhi", "en", p) == "nu york and nu Delhi"


def test_full_tag_entries_replace_primary_entries():
    p = lexicon(en={"Ltd": "limited", "Inc": "incorporated"}, **{"en-US": {"Ltd": "L T D"}})
    assert normalize("Ltd and Inc", "en-US", p) == "L T D and incorporated"
    assert normalize("Ltd and Inc", "en-GB", p) == "limited and incorporated"


def test_without_lexicon_switches_it_off():
    assert normalize("ACME", "en", lexicon(en={"ACME": "acme"}).without(Form.LEXICON)) == "ACME"


@pytest.mark.parametrize("value", ["GPT four", "WD 40", "costs $5"])
def test_a_lexicon_value_that_a_recognizer_claims_raises(value):
    key = value.split()[0] if value.startswith("GPT") else "x"
    entries = {"GPT-4": "GPT four", "GPT": "gee pee tee"} if value == "GPT four" else {key: value}
    with pytest.raises(InvalidLexiconError):
        normalize("hello", "en", lexicon(en=entries))


def test_a_lexicon_key_that_is_not_a_tag_raises():
    with pytest.raises(InvalidLanguageTagError):
        normalize("hello", "en", lexicon(**{"not a tag": {"a": "b"}}))


def test_a_hint_key_with_no_span_warns_and_strict_raises():
    analysis = analyze("I have 3 cats.", "en")
    with pytest.warns(HintWarning):
        assert render(analysis, {0: Features()}) == "I have three cats."
    strict = analyze("I have 3 cats.", "en", NormalizationParams(strict=True))
    with pytest.raises(InvalidHintError):
        render(strict, {0: Features()})


def test_a_hint_must_be_features():
    analysis = analyze("I have 3 cats.", "en")
    with pytest.raises(TypeError):
        render(analysis, {analysis.spans[0].start: "feminine"})


def test_a_speller_that_raises_keeps_the_written_form_and_logs(caplog):
    # RBNF has no rule for 10^21 in en (section 5.4), so the cardinal stays as written.
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        assert normalize("It is 1000000000000000000000 now.", "en") == "It is 1000000000000000000000 now."
    assert any("unread cardinal" in r.message for r in caplog.records)


def test_a_speller_that_raises_in_strict_mode_raises_chained():
    with pytest.raises(UnreadFormError) as raised:
        normalize("It is 1000000000000000000000 now.", "en", NormalizationParams(strict=True))
    assert raised.value.__cause__ is not None


def test_an_unread_digit_logs_each_run(caplog):
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        normalize("Ratios 16:9 and 4:3 here.", "en")
    assert [r.args[0] for r in caplog.records if r.message.startswith("unread written form")] == ["16:9", "4:3"]


def test_an_unread_symbol_logs_only_when_its_form_is_asked(caplog):
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        normalize("Pay in $ or €.", "en")
        assert len(caplog.records) == 2
        caplog.clear()
        normalize("Pay in $ or €.", "en", NormalizationParams().without(Form.MONEY))
        assert caplog.records == []


def test_an_unread_alpha_logs(caplog):
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        assert normalize("The colour is #ff000080.", "en") == "The colour is red."
    assert any("alpha" in r.message for r in caplog.records)


def test_a_colour_with_no_table_entry_spells_its_digits():
    assert normalize("The colour is #12ab34.", "en") == "The colour is one two A B three four."

