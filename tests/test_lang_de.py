"""German readings outside the sentence rows: second passes, random text and strict mode."""
import random

import pytest

from text2spoken import FrozenMap, GrammaticalGender, NormalizationParams, UnreadFormError, normalize

SECOND_PASS = [
    ("de-CH", "Der Preis stieg um 2.50 Franken."),
    ("de-CH", "Der Preis sank von 4.20 auf 3.80 Franken."),
    ("de-CH", "Offen von 9.00 bis 17.30 Uhr."),
    ("de-CH", "Mit 1 Franken kommst du nicht weit."),
    ("de-DE", "Von 9:00 bis 17 Uhr offen."),
    ("de-DE", "Ab 16:10 ist das Bild breit."),
    ("de-DE", "Er lief 10 km in 1 Stunde."),
    ("de-DE", "Wir sehen uns in 1 Woche."),
    ("de-DE", "Während 1 Woche war er weg."),
    ("de-DE", "1/2 Liter Milch"),
    ("de-DE", "1/2 Dr. Schmidt"),
    ("de-CH", "3/4 CHF 4 Pizza"),
    ("de-AT", "Fr. #5 kam."),
    ("de-DE", "Dr. #fff Farbe"),
]


@pytest.mark.parametrize(("tag", "text"), SECOND_PASS)
def test_a_second_pass_changes_nothing(tag, text):
    once = normalize(text, tag)
    assert normalize(once, tag) == once


ATOMS = (list("abcxyzABCÄÖÜäöüß") + list("0123456789") + list("#-+$£€%°/:.,;!?()'×") + [" ", " ", "\t"]
         + ["Uhr", " Uhr", "um", "von", "bis", "gegen", "vor", "in", "an", "mit", "zu", "wegen", "der", "kostet",
            "Stunde", "Jahr", "Tag", "Ei", "Gebäude", "Kaffee", "Idee", "Pizza", "Liter", "Franken", "CHF", "Fr.",
            "Mio.", "Dr.", "z. B.", "1/2", "3/4", "14:30", "14.30", "9:00", "17:00", "1.15", "0.25", "12.03.2024",
            "1:25", "1000000.", "3.", "Mahnung", "1'000", "während", "Gemeinde", "Geschichte"])


@pytest.mark.parametrize("seed", range(4))
def test_random_german_text_never_raises_and_reads_the_same_on_a_second_pass(seed):
    rng = random.Random(seed)
    for _ in range(500):
        tag = rng.choice(["de", "de-DE", "de-AT", "de-CH"])
        text = "".join(rng.choice(ATOMS) + rng.choice(["", " "]) for _ in range(rng.randint(1, 25)))
        once = normalize(text, tag)
        assert normalize(once, tag) == once, (tag, text, once)


def test_a_fraction_before_a_noun_is_unread_like_a_fraction_before_a_unit():
    strict = NormalizationParams(strict=True)
    for text in ("Ich esse 1/2 Pizza.", "Es wiegt 3/4 kg."):
        with pytest.raises(UnreadFormError) as raised:
            normalize(text, "de-DE", strict)
        assert raised.value.unread == (text.split()[2],)


def test_a_noun_with_no_known_gender_takes_the_dative_of_the_default_gender():
    # Wikipedia, German declension (fetched): indefinite article table, dative feminine "einer".
    params = NormalizationParams(default_gender=FrozenMap({"de": GrammaticalGender.FEMININE}))
    assert normalize("Ich fahre mit 1 Freundin.", "de-DE", params) == "Ich fahre mit einer Freundin."
