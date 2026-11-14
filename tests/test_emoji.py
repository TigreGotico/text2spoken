"""The emoji data and the `EMOJI` form (design section 4.7).

Each expected value is read off the clause, the raw CLDR 49 JSON and the Unicode 17.0 emoji files, not off a run of the
code."""
import gc
import json
import random
import re
import tracemalloc
from dataclasses import replace
from importlib.resources import files

import pytest

from tests.conftest import EMOJI_ON, rows
from tests.known_limits import known_limit
from tests.test_cldr_currencies_symbols import Files, data, extractor
from text2spoken import (Form, FrozenMap, InvalidLexiconError, NormalizationParams, UnreadFormError, analyze,
                         normalize)
from text2spoken.core.emoji import emoji_view, name_reading, sequence_at, sequences_in
from text2spoken.core.tokens import STAND_IN, is_mark, is_word_char

TAGS = ("en-GB", "en-US", "pt-PT", "pt-BR")


def sequences() -> list[str]:
    path = files("text2spoken") / "data" / "cldr" / "emoji-sequences.json"
    return json.loads(path.read_text(encoding="utf-8"))["sequences"]


def test_the_sequence_file_records_unicode_17_and_its_two_inputs():
    source = json.loads((files("text2spoken") / "data" / "cldr" / "emoji-sequences.json")
                        .read_text(encoding="utf-8"))["source"]
    assert source["unicode"] == "17.0.0"
    assert set(source["files"]) == {"emoji/emoji-sequences.txt", "emoji/emoji-zwj-sequences.txt"}


def test_the_sequence_file_holds_the_sequences_as_unicode_writes_them():
    """Unicode 17.0 adds 🫩 (U+1FAE9) and the keycap `#️⃣` is 0023 FE0F 20E3 in emoji-sequences.txt."""
    written = set(sequences())
    assert {"\U0001fae9", "#️⃣", "❤️", "🇵🇹", "👍🏽", "👨‍👩‍👧‍👦"} <= written
    assert "❤" not in written and "#⃣" not in written


@pytest.mark.parametrize("tag", TAGS)
def test_each_tag_names_each_sequence_without_u_fe0f(tag):
    names = data(tag, "emoji")["names"]
    assert set(names) == {sequence.replace("️", "") for sequence in sequences()}
    assert data(tag, "emoji")["source"]["unicode"] == "17.0.0"


@pytest.mark.parametrize(("tag", "key", "name"), [
    ("en-GB", "👍🏽", "thumbs up: medium skin tone"),
    ("pt-PT", "👍🏽", "polegar para cima: tipo de pele 4"),
    ("pt-BR", "👍🏽", "polegar para cima: pele morena"),
    ("pt-PT", "🥇", "medalha de 1.º lugar"),
    ("en-US", "🕐", "one o’clock"),
])
def test_the_names_are_the_cldr_tts_names_of_the_parent_chain(tag, key, name):
    assert data(tag, "emoji")["names"][key] == name


def test_the_extractor_reads_ranges_and_sequences_and_keeps_only_the_names_of_sequences():
    module = extractor()
    emoji = Files({"emoji-sequences.txt": b"231A..231B ; Basic_Emoji ; watch..hourglass # x\n"
                                          b"00A9 FE0F ; Basic_Emoji ; copyright # x\n",
                   "emoji-zwj-sequences.txt": b"1F468 200D 1F4BB ; RGI_Emoji_ZWJ_Sequence ; man technologist # x\n"})
    found = module.emoji_sequences(emoji)
    assert found == sorted(["⌚", "⌛", "©️", "👨‍💻"])
    names = {key: {"tts": [f"name {key}"]} for key in ("⌚", "©", "👨‍💻", "→")}
    release = Files({"cldr-json/cldr-annotations-full/annotations/qq/annotations.json":
                     {"annotations": {"annotations": names}}})
    extracted = module.extract_emoji("qq", {}, release, {}, found)
    assert extracted["names"] == {"⌚": "name ⌚", "©": "name ©", "👨‍💻": "name 👨‍💻"}


@pytest.mark.parametrize(("name", "tag", "reading"), [
    ("one o’clock", "en-GB", "one o’clock"),
    ("pistola d’água", "pt-BR", "pistola d’água"),
    ("bandeira: Côte d’Ivoire (Costa do Marfim)", "pt-PT", "bandeira Côte d’Ivoire Costa do Marfim"),
    ("Japanese “here” button", "en-GB", "Japanese here button"),
    ("‘quoted’ sign", "en-GB", "quoted sign"),
    ("A button (blood type)", "en-GB", "A button blood type"),
    ("family: adult, adult, child", "en-US", "family adult adult child"),
    ("flag: Antigua & Barbuda", "en-GB", None),
    ("keycap: #", "en-GB", None),
    ("ON! arrow", "en-GB", None),
    ("flag: St. Lucia", "en-US", None),
    ("quadrado preto pequeno/médio", "pt-PT", None),
])
def test_a_name_reads_in_three_steps(name, tag, reading):
    """Quotes go, `: , ( )` become spaces, U+2019 between two letters stays as an apostrophe, and a reading that
    still holds another character than a letter, a mark, a space, `-`, `'` or U+2019 does not read."""
    assert name_reading(name, tag, NormalizationParams()) == reading


@pytest.mark.parametrize(("text", "end"), [
    ("😂😂", 1), ("👍🏽!", 2), ("❤️ x", 2), ("❤ x", None), ("❤‍🔥", 3), ("👍🏽‍🔥", 4), ("1️⃣", 3),
    ("1⃣", 2), ("a🏽", 2), ("⋂🏿", 2), (" 🏽", None), ("🇵🇹🇧🇷", 2), ("🇵🇵🇹", None),
])
def test_an_emoji_sequence_ends_after_its_skin_tones_selectors_and_joined_emoji(text, end):
    found = sequence_at(text, 0, {})
    assert (found and found[1]) == end


@pytest.mark.parametrize(("text", "found"), [
    ("🇵🇵🇹", []), ("🇸🇪🇸🇪🇸", [(0, 2), (2, 4)]), ("x🇵🇵🇵🇹", [(3, 5)]),
])
def test_regional_indicators_pair_from_the_start_of_a_run(text, found):
    """UAX #29 GB12 and GB13: "do not break between regional indicator (RI) symbols if there is an odd number of RI
    characters before the break point". So `🇵🇵🇹` is the pair `🇵🇵`, which names no flag, and a lone `🇹`."""
    assert list(sequences_in(text, {})) == found


def test_the_view_hides_each_character_of_a_sequence_that_an_emoji_mark_follows_and_is_no_symbol():
    text = "a 1️⃣ #️⃣ ❤️ 5🏽 ©️‍1️⃣ ❤︎"
    view = emoji_view(text, {})
    assert len(view) == len(text)
    hidden = [index for index, char in enumerate(view) if char != text[index]]
    assert [text[index] for index in hidden] == ["1", "#", "1"] and hidden[2] == text.index("‍") + 1
    assert {view[index] for index in hidden} == {STAND_IN}


@pytest.mark.parametrize("mark", ["️", "︎", "⃣"])
def test_an_emoji_mark_is_no_word_character(mark):
    assert not is_mark(mark) and not is_word_char(mark)
    assert is_mark("́")


@pytest.mark.parametrize("tag", TAGS)
@pytest.mark.parametrize("glyph", ["❤\ufe0f", "🙂\ufe0e", "🙂\u20e3", "🧜\u200d♂\ufe0f"])
def test_a_number_after_an_emoji_mark_reads_as_after_an_emoji_with_no_mark(tag, glyph):
    """`😀2 cats` reads the number on dev; `❤️2 cats` and the others read it the same way (design section 4.7)."""
    plain = normalize("😀2 cats", tag)
    assert normalize(f"{glyph}2 cats", tag) == plain.replace("😀", glyph, 1)


EMOJI_ROWS = [row for code in ("en", "pt") for row in rows(code) if row["form"] == "emoji"]


@pytest.mark.parametrize("row", [r for r in EMOJI_ROWS if not any(c.isdigit() or c == "@" for c in r["text"])],
                         ids=lambda row: row["id"])
def test_an_emoji_row_stays_as_written_with_the_form_off(row):
    """`❤` with no U+FE0F belongs to `SYMBOL`, so its rows read the same with the form off."""
    expected = row["expected"] if "❤" in row["text"] and "️" not in row["text"] else row["text"]
    assert normalize(row["text"], row["tag"]) == expected


@pytest.mark.parametrize("tag", ["en-GB", "en-US"])
def test_an_address_keeps_an_emoji_sequence_whole(tag):
    assert normalize("x@a👨‍💻b.com", tag) == "ex at ay 👨‍💻 bee dot com"
    assert normalize("x@a👨‍💻b.com", tag, EMOJI_ON) == "ex at ay man technologist bee dot com"
    assert normalize("x@a©️b.com", tag, EMOJI_ON) == "ex at ay copyright bee dot com"
    assert normalize("x@a🇦🇬b.com", tag, EMOJI_ON) == "ex at ay 🇦🇬 bee dot com"


def test_the_form_reads_inside_an_address_only_through_its_name():
    analysis = analyze("x@a😀b.com", "en-GB", EMOJI_ON)
    assert [span.form for span in analysis.spans] == [Form.ELECTRONIC]


@pytest.mark.parametrize("tag", TAGS)
def test_every_sequence_reads_the_same_on_a_second_pass(tag):
    """Section 11 over every sequence of the file, in sentences of 200 sequences."""
    written = sequences()
    for start in range(0, len(written), 200):
        text = " x ".join(written[start:start + 200]) + "."
        once = normalize(text, tag, EMOJI_ON)
        assert normalize(once, tag, EMOJI_ON) == once


EMOJI_ATOMS = ["😂", "👍🏽", "❤", "❤️", "©", "©️", "1️⃣", "#️⃣", "🇵🇹", "🇦🇬", "🇵", "🕐", "😀🏽", "a🏽", "⋂🏿", "️",
               "‍", "🏽", "⃣", "👨‍👩‍👧", "🧜‍♂️", "x@a", "b.com", ".org", " ", " ", "2", "+4",
               "3/4", "1.234,56", "Call", "Ligue", "(", ")", ".", ",", "$5", "€", "→", "May", "in",
               "Call 0800 123 456 ", "call 911", "555-123-4567", "(11) 91234-5678", "10+4 ₡", "₡-", "₴", "-", "A",
               "12️⃣", "1⃣"]
ADDRESS_ATOMS = ("x@a", "b.com", ".org")
KEYCAP_LEXICON = FrozenMap({code: FrozenMap({"#️⃣": "hash key", "1️⃣": "option one", "A1️⃣": "grade"})
                            for code in ("en", "pt")})


@pytest.mark.parametrize("seed", range(4))
def test_normalize_with_the_form_on_is_idempotent_on_random_text(seed):
    """Section 11 with `EMOJI` on: a second pass changes nothing, except in the known limits of the README and in a
    text that a second pass changes with the default params too, which is no break of this form. The same holds with
    a caller lexicon of keycap keys, on text with no address: an address puts a space after itself, and a key that a
    word character blocked on the first pass then matches, with the default forms too (`x.org😀` with a key `😀`). A
    break that the same text gives with a symbol key in place of each keycap key is excused (`symbol_twin_breaks`)."""
    rng = random.Random(seed)
    for _ in range(500):
        lang = rng.choice(TAGS)
        text = "".join(rng.choice(EMOJI_ATOMS) for _ in range(rng.randint(1, 12)))
        once, off = normalize(text, lang, EMOJI_ON), normalize(text, lang)
        assert (normalize(once, lang, EMOJI_ON) == once or known_limit(text, lang, EMOJI_ON)
                or normalize(off, lang) != off), (text, once)
        if any(atom in text for atom in ADDRESS_ATOMS):
            continue
        lexicon = replace(EMOJI_ON, lexicon=KEYCAP_LEXICON)
        once = normalize(text, lang, lexicon)
        assert (normalize(once, lang, lexicon) == once or known_limit(text, lang, EMOJI_ON)
                or normalize(off, lang) != off or symbol_twin_breaks(text, lang)), (text, once)


def symbol_twin_breaks(text: str, lang: str) -> bool:
    """Whether a second pass changes the text with `©` in place of each keycap key and a lexicon key `©`, with the
    default forms. A lexicon value of letters in place of a symbol can change how the spans around it join, so such a
    break is no break of this form."""
    for key in ("A1️⃣", "#️⃣", "1️⃣"):
        text = text.replace(key, "©")
    params = NormalizationParams(lexicon=FrozenMap({code: FrozenMap({"©": "hash key"}) for code in ("en", "pt")}))
    once = normalize(text, lang, params)
    return normalize(once, lang, params) != once


@pytest.mark.parametrize("sequence", ["😂", "👍🏽", "🧑🏿‍🦲"])
def test_an_emoji_sequence_joins_two_spans_as_one_character(sequence):
    """`4 ₡` waits on the joined `10`, so `+4` waits on the sequence that joins it to `₡`, whatever the length of the
    sequence, and a second pass reads the same."""
    text = f"10+4 ₡{sequence}+4 ₴ today."
    assert normalize(text, "pt-PT", EMOJI_ON) == text


@pytest.mark.parametrize("params", [None, EMOJI_ON], ids=["off", "on"])
@pytest.mark.parametrize(("tag", "text"), [("en-GB", "See x.org1️⃣ now."), ("en-GB", "Code 12️⃣ here."),
                                           ("en-GB", "x 12️⃣ y"), ("en-US", "Pay $51️⃣ now."),
                                           ("pt-PT", "Código 12️⃣ aqui."), ("en-GB", "O'Neil1️⃣ won"),
                                           ("en-GB", "well-known1️⃣ fact"), ("en-GB", "x.y12️⃣")])
def test_an_emoji_that_a_word_joins_on_the_left_stays_as_written(tag, text, params):
    """Design section 4.7: "An emoji sequence that starts with a letter or a digit and touches a letter or a digit on
    its left stays as written (`12️⃣`)." The word that it touches stays as written too, with the form on or off, and
    strict mode passes it. The word ends at a symbol, so `$` stays outside it, no form reads `$51️⃣`, and strict mode
    reports it."""
    assert normalize(text, tag, params) == text
    strict = replace(params or NormalizationParams(), strict=True)
    if "$" in text:
        with pytest.raises(UnreadFormError) as raised:
            normalize(text, tag, strict)
        assert raised.value.unread == ("$51️⃣",)
    else:
        assert normalize(text, tag, strict) == text


@pytest.mark.parametrize("params", [None, EMOJI_ON], ids=["off", "on"])
def test_a_digit_before_a_skin_tone_reads_next_to_a_digit(params):
    """The rule for a sequence that touches a word covers a sequence with U+FE0E, U+FE0F or U+20E3, the sequences
    that the view hides. A digit before a skin tone reads, as the README limit says, so `5🏽` after `1` reads with it,
    with the form on or off."""
    assert normalize("Room 15🏽 now", "en-GB", params) == "Room fifteen🏽 now"


@pytest.mark.parametrize(("text", "word"), [
    ("a 😀x.org1️⃣ b", "org1"), ("I have 2,cats1️⃣", "cats1"), ("on 12/03/2024.Next1️⃣", "Next1"),
    ("5km.Next1️⃣", "Next1"), ('He said "50%"great1️⃣', "great1"), ("Call me:07700 900123,ok1️⃣", "ok1"),
    ("Liga 912345678/ok1️⃣", "ok1"), ("From 9am-5pm,team2️⃣", "team2"), ("O'Neil1️⃣ won", "Neil1"),
    ("O’Neil1️⃣ won", "Neil1"), ("well-known1️⃣ fact", "known1"), ("x.y12️⃣", "y12"), ("Score 3-12️⃣", "12"),
    ("Total:100.Item12️⃣", "Item12"), ("1st.Place1️⃣", "Place1"), ("a; b1️⃣", "b1"), ("(x)y1️⃣", "y1"),
    ("a 👨\u200dℹy2️⃣", "y2")])
def test_the_view_hides_the_word_that_a_sequence_touches(text, word):
    """Design section 4.7: the sequence "stays as written, together with the word it touches". The word is the run of
    letters, digits and combining marks right before the sequence. A punctuation mark, a space, a symbol and the
    sequence before it end the word. `👨`, U+200D and `ℹ` make a sequence that ends in a letter, and that letter stays
    out of the word when `y2️⃣` follows."""
    start = text.index(word)
    assert emoji_view(text, {}) == text[:start] + STAND_IN * len(word) + text[start + len(word):]


MARKED = ["❤️", "☑️", "✈️", "1️⃣", "#️⃣", "1⃣", "©️", "🏳️‍🌈", "5️"]
CONTEXTS = {
    "en": ["Call 0800 123 456 {e} to cancel", "call 911{e} now", "Call (555) 123-4567{e} for sales",
           "Call me on 07700 900123{e}", "call {e}07700 900123 now", "ring +44 20 7946 0958{e}", "I paid £5{e} today.",
           "{e}£5 for you", "It costs 3.50{e}€", "about 50%{e} done", "run 5km{e} daily", "run 5{e}km", "the 3rd{e} place",
           "1{e}2{e}3", "10{e}-{e}20", "Score 2{e}1", "I have {e}2 cats", "£1.5m{e} deal", "{e}$5-$10", "10+4 ₡{e}+4 ₴",
           "10+4 ₡-{e}+4 ₴", "order #1{e}2", "at 3{e}:30", "Code 1{e} here."],
    "pt": ["Liga (11) 91234-5678 {e} agora", "Liga 21 123 4567{e} para vendas", "+351 912 345 678{e} é o meu",
           "liga 112{e}", "Paguei 5 €{e} hoje.", "{e}5 € para ti", "Custa 3,50{e} €", "cerca de 50%{e} feito",
           "corro 5 km{e} por dia", "o 3.º{e} lugar", "1{e}2{e}3", "Resultado 2{e}1", "Tenho {e}2 gatos",
           "1,5 milhões €{e} de negócio", "10+4 ₡{e}+4 ₴", "10+4 ₡-{e}+4 ₴", "às 3{e}:30"],
}


def touched_word(before: str) -> str:
    """The word at the end of `before`, by the clause: its run of letters and digits."""
    return re.search(r"[^\W_]*$", before).group()


@pytest.mark.parametrize("tag", TAGS)
@pytest.mark.parametrize("emoji", MARKED)
def test_with_the_form_off_a_marked_emoji_reads_as_a_plain_emoji(tag, emoji):
    """Design section 4.7: U+FE0F and U+20E3 are no word characters at the edge of another form, and the character
    before them belongs to the emoji. So with the form off, a phone, an amount or a number next to a keycap or a
    sequence with U+FE0F reads as it reads next to `😀`, and only the emoji differs. A sequence that starts with a
    digit and touches a letter or a digit on its left stays as written with that word instead."""
    for template in CONTEXTS[tag[:2]]:
        for space in ("", " "):
            text, plain = template.format(e=space + emoji + space), template.format(e=space + "😀" + space)
            before = template[:template.index("{e}")]
            if space or not (before[-1:].isalnum() and emoji[0].isalnum()):
                assert normalize(text, tag) == normalize(plain, tag).replace("😀", emoji), text
            else:
                word = touched_word(before)
                once = normalize(text, tag)
                assert word + emoji in once and normalize(once, tag) == once, text


@pytest.mark.parametrize("tag", TAGS)
@pytest.mark.parametrize("emoji", ["1️⃣", "#️⃣", "1⃣"])
def test_strict_mode_finds_no_unread_digit_in_a_keycap(tag, emoji):
    """The digit of a keycap belongs to the emoji, so with the form off strict mode passes the keycap as written, as it
    passes `😀`, and the phone number before it reads."""
    text = CONTEXTS[tag[:2]][0].format(e=emoji)
    assert normalize(text, tag, NormalizationParams(strict=True)) == normalize(text, tag)


@pytest.mark.parametrize("emoji", [False, True], ids=["off", "on"])
@pytest.mark.parametrize("value", ["ab1️⃣", "a1️⃣b", "12️⃣", "105️⃣"])
def test_the_lexicon_check_finds_what_a_second_pass_reads_next_to_a_keycap(value, emoji):
    """The lexicon check cuts the tokens of a value as `analyze` does (section 11). So a value that a second pass
    changes raises, as `12️⃣` does with the form off, because its `1` reads, and a value that a second pass keeps
    passes."""
    params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"X": value})}))
    params = params.plus(Form.EMOJI) if emoji else params
    if normalize(value, "en", EMOJI_ON if emoji else None) == value:
        assert normalize("X", "en", params) == value
    else:
        with pytest.raises(InvalidLexiconError):
            normalize("X", "en", params)


@pytest.mark.parametrize("params", [NormalizationParams(), EMOJI_ON], ids=["off", "on"])
@pytest.mark.parametrize(("key", "value", "text", "expected"), [
    ("#️⃣", "hash key", "Press #️⃣ now", "Press hash key now"),
    ("1️⃣", "option one", "Press 1️⃣ now", "Press option one now"),
    ("1⃣", "option one", "Press 1⃣ now", "Press option one now"),
    ("A1️⃣", "grade", "A1️⃣ ok", "grade ok"),
])
def test_a_caller_lexicon_key_with_an_emoji_mark_matches_as_written(key, value, text, expected, params):
    """The caller's lexicon claims first and matches the text as written, so a key that holds a keycap reads its
    value with the form on or off, as on dev."""
    lexicon = FrozenMap({"en": FrozenMap({key: value})})
    assert normalize(text, "en-GB", replace(params, lexicon=lexicon)) == expected


def test_a_caller_lexicon_key_ends_at_no_point_inside_an_emoji_sequence():
    """A key `1` claims a bare `1`, and leaves the `1` of `1️⃣`, which belongs to the sequence."""
    params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"1": "uno"})}))
    assert normalize("Press 1 now", "en-GB", params) == "Press uno now"
    assert normalize("Press 1️⃣ now", "en-GB", params) == "Press 1️⃣ now"


def test_a_caller_lexicon_key_meets_an_emoji_sequence_as_it_meets_a_plain_emoji():
    """A sequence with an emoji mark is one character, as `😀` is, so a key before `1️⃣` matches as it matches before
    `😀`. A key inside a word that a sequence touches does not match, so `A1️⃣` stays as written."""
    params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({"#️⃣": "hash key", "A": "ay"})}))
    assert normalize("#️⃣1️⃣ x", "en-GB", params) == normalize("#️⃣😀 x", "en-GB", params).replace("😀", "1️⃣")
    assert normalize("A1️⃣ x", "en-GB", params) == "A1️⃣ x"


@pytest.mark.parametrize(("key", "text", "expected"), [
    ("2", "I have 2,cats1️⃣", "I have two-key,cats1️⃣"), ("cats", "I have 2,cats1️⃣", "I have two,cats1️⃣"),
    ("org", "See x.org1️⃣ now.", "See x.org1️⃣ now."), ("x.org", "See x.org1️⃣ now.", "See x.org1️⃣ now."),
    ("x", "See x.org1️⃣ now.", "See word.org1️⃣ now."),
    ("Next", "on 12/03/2024.Next1️⃣", "on the twelfth of March twenty twenty-four.Next1️⃣"),
    ("known", "well-known1️⃣ fact", "well-known1️⃣ fact")])
def test_a_caller_lexicon_key_and_the_view_agree_on_the_touched_word(key, text, expected):
    """A key matches outside the word that a sequence touches and does not match inside it or across its edge, as the
    other forms read the view. The word of `2,cats1️⃣` is `cats`, so a key `2` matches, and the word of `x.org1️⃣` is
    `org`, so a key `x` matches, and the keys `org` and `x.org` do not."""
    params = NormalizationParams(lexicon=FrozenMap({"en": FrozenMap({key: "two-key" if key == "2" else "word"})}))
    assert normalize(text, "en-GB", params) == expected


@pytest.mark.parametrize("params", [None, EMOJI_ON], ids=["off", "on"])
def test_a_call_keeps_nothing_of_a_long_text_after_it_returns(params):
    """The pairs of regional indicators, the emoji sequences and the view of a text live in the memo of the request,
    which lives for one call. So after a call on a long run of flags, no set of indicators or other result of the
    text stays in memory."""
    label = "on" if params else "off"
    normalize(f"{label} 🇵🇹 x", "en-GB", params)
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        normalize(f"{label} " + "🇵🇹" * 5000, "en-GB", params)
        gc.collect()
        kept = tracemalloc.get_traced_memory()[0] - before
    finally:
        tracemalloc.stop()
    assert kept < 10_000


def test_a_run_of_regional_indicators_takes_linear_work(monkeypatch):
    """UAX #29 pairs regional indicators from the start of a run. The pairing reads each character of the run a
    bounded number of times, so twice the run takes about twice the work, with the form on or off."""
    from text2spoken.core import emoji

    checks = 0

    class Counted(frozenset):
        def __contains__(self, char):
            nonlocal checks
            checks += 1
            return frozenset.__contains__(self, char)

    monkeypatch.setattr(emoji, "REGIONAL_INDICATORS", Counted(emoji.REGIONAL_INDICATORS))

    def work(count, params, label):
        nonlocal checks
        checks = 0
        normalize(f"{label} {count} " + "🇵🇹" * count, "en-GB", params)
        return checks

    for params, label in ((None, "off"), (EMOJI_ON, "on")):
        small = work(2000, params, label)
        assert 0 < small and work(4000, params, label) <= 2.2 * small, label


@pytest.mark.parametrize("tag", TAGS)
@pytest.mark.parametrize("text", ["10+4 ₡-😂+4 ₴", "10+4 ₡🇵😂+4 ₴", "10+4 ₡🇵🇵🇹+4 ₴"])
def test_a_sequence_between_a_waiting_amount_and_a_number_reads_as_a_symbol_does(tag, text):
    """The `EMOJI` recognizer claims after every other form and before `SYMBOL`, so the sequence waits as `©` waits in
    `10+4 ₡-©+4 ₴`, and a second pass reads the same."""
    once = normalize(text, tag, EMOJI_ON)
    assert normalize(once, tag, EMOJI_ON) == once
    symbol = normalize("10+4 ₡-©+4 ₴", tag, EMOJI_ON)
    if text.startswith("10+4 ₡-"):
        assert once == symbol.replace("©", "😂")


@pytest.mark.parametrize("params", [None, EMOJI_ON], ids=["off", "on"])
def test_a_digit_before_a_skin_tone_in_an_address_reads_as_outside_it(params):
    once = normalize("x@a5🏽b.com", "en-GB", params)
    assert once == ("ex at ay five 🏽 bee dot com" if params is None else "ex at ay five medium skin tone bee dot com")
    assert normalize(once, "en-GB", params) == once
