"""French: the variety matrix, agreement, params, edge cases and cross-checks that the sentence rows of
tests/data/fr.tsv do not show. Every expected string is written by hand from the grammar of French."""

import logging
import warnings

import pytest

from text2spoken import (
    Features,
    FrozenMap,
    Form,
    GrammaticalGender,
    NormalizationParams,
    ParameterNotHonouredWarning,
    UnreadFormError,
    analyze,
    effective_params,
    normalize,
    render,
    supports,
)

F, M = GrammaticalGender.FEMININE, GrammaticalGender.MASCULINE
NB, NN = " ", " "

FRENCH_FORMS = set(Form) - {Form.IDENTIFIER, Form.LETTERS}
FRANCE_TAGS = [
    "fr",
    "fr-FR",
    "fr-CA",
    "fr-LU",
    "fr-MC",
    "fr-SN",
    "fr-CI",
    "fr-CD",
    "fr-CM",
    "fr-MA",
    "fr-TN",
    "fr-DZ",
    "fr-HT",
    "fr-GP",
    "fr-RE",
    "fr-ZZ",
    "fr_CA",
    "FR-ca",
    "fr-Latn-CA",
    "fr-CA-x-private",
]
"""Tags that say soixante-dix, quatre-vingts and quatre-vingt-dix."""
ALL_TAGS = FRANCE_TAGS + ["fr-BE", "fr-CH", "fr-CH-1996"]
SEVENTY_NINETY = {
    "fr-BE": "septante nonante quatre-vingts",
    "fr-CH": "septante nonante huitante",
    "fr-CH-1996": "septante nonante huitante",
}


def words_for(tag: str) -> str:
    return SEVENTY_NINETY.get(tag, "soixante-dix quatre-vingt-dix quatre-vingts")


@pytest.mark.parametrize("tag", ALL_TAGS)
def test_every_french_tag_reads_the_same_forms(tag):
    support = supports(tag)
    assert support.code == "fr" and support.forms == FRENCH_FORMS and support.genders == {M, F}
    assert support.context_words


@pytest.mark.parametrize("tag", ALL_TAGS)
def test_the_tens_of_each_region(tag):
    assert normalize("70 90 80", tag) == words_for(tag)


def test_belgium_and_switzerland_say_septante_and_nonante_with_et_un():
    assert normalize("71 91 81", "fr-BE") == "septante et un nonante et un quatre-vingt-un"
    assert normalize("71 91 81", "fr-CH") == "septante et un nonante et un huitante et un"
    assert normalize("71 91 81", "fr-FR") == "soixante et onze quatre-vingt-onze quatre-vingt-un"


@pytest.mark.parametrize("tag", ALL_TAGS)
def test_a_time_a_date_and_a_measure_read_in_every_region(tag):
    assert normalize("Le 10 novembre 2026 à 14 h 30, il fait 6 °C.", tag) == (
        "Le dix novembre deux mille vingt-six à quatorze heures trente, il fait six degrés Celsius."
    )


@pytest.mark.parametrize("tag", ALL_TAGS)
@pytest.mark.parametrize("written", ["1 000", f"1{NB}000", f"1{NN}000", "1'000", "1’000"])
def test_a_thousand_with_every_group_mark(tag, written):
    assert normalize(f"{written} euros", tag) == "mille euros"


@pytest.mark.parametrize("tag", ALL_TAGS)
@pytest.mark.parametrize(
    "written,spoken",
    [
        ("1.000.000", "un million"),
        ("1 234 567", "un million deux cent trente-quatre mille cinq cent soixante-sept"),
        ("1.234,5", "mille deux cent trente-quatre virgule cinq"),
        ("1 234.5", "mille deux cent trente-quatre virgule cinq"),
    ],
)
def test_grouped_numbers_in_every_region(tag, written, spoken):
    assert normalize(written, tag) == spoken


@pytest.mark.parametrize("tag", ALL_TAGS)
@pytest.mark.parametrize("written", ["3,5", "3.5"])
def test_a_comma_and_a_dot_are_both_decimal_marks(tag, written):
    assert normalize(f"Il a {written} de moyenne.", tag) == "Il a trois virgule cinq de moyenne."


@pytest.mark.parametrize("written", ["1.500", "10.000", "3.141", "1,5,2", "1.5.2"])
def test_a_number_that_the_marks_do_not_settle_stays_as_written(written, caplog):
    text = f"La valeur {written} reste."
    assert normalize(text, "fr") == text
    assert "unread written form" in caplog.text
    with pytest.raises(UnreadFormError):
        normalize(text, "fr", NormalizationParams(strict=True))


def test_the_decimal_mark_param_makes_the_dot_the_canonical_mark():
    dot = NormalizationParams(decimal_mark=".")
    assert (
        normalize("3.5 et 3,5 et 1 234.5", "fr", dot)
        == "trois virgule cinq et trois virgule cinq et mille deux cent trente-quatre virgule cinq"
    )
    assert normalize("1,500", "fr", dot) == "1,500" and normalize("1,500", "fr") == "un virgule cinq zéro zéro"


@pytest.mark.parametrize(
    "tag,written,spoken",
    [
        ("fr-FR", "12 $", "douze dollars"),
        ("fr-CA", "12 $", "douze dollars"),
        ("fr-BE", "12 $", "douze dollars"),
        ("fr-CH", "12 $", "douze dollars"),
        ("fr-SN", "12 $", "douze dollars"),
        ("fr-FR", "5 US$", "cinq dollars"),
        ("fr-CA", "5 US$", "cinq dollars américains"),
        ("fr-FR", "5 CA$", "cinq dollars canadiens"),
        ("fr-CA", "5 CA$", "cinq dollars"),
        ("fr-FR", "3,50 €", "trois euros cinquante"),
        ("fr-BE", "€ 3,50", "trois euros cinquante"),
        ("fr-CH", "3,50 CHF", "trois francs suisses cinquante"),
        ("fr-FR", "3,50 CHF", "trois francs suisses cinquante"),
        ("fr-CH", "Fr. 3.50", "trois francs suisses cinquante"),
        ("fr-CH", "fr. 3.50", "trois francs suisses cinquante"),
        ("fr-CH", "1 CHF", "un franc suisse"),
        ("fr-CI", "5 £", "cinq livres"),
    ],
)
def test_money_of_each_region(tag, written, spoken):
    assert normalize(f"Ça coûte {written} ici.", tag) == f"Ça coûte {spoken} ici."


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("5 $", "cinq piastres"),
        ("1 $", "une piastre"),
        ("3,50 $", "trois piastres cinquante"),
        ("0,50 $", "cinquante cennes"),
        ("0,01 $", "une cenne"),
        ("21 $", "vingt et une piastres"),
        ("2 000 000 $", "deux millions de piastres"),
        ("5 CA$", "cinq piastres"),
    ],
)
def test_the_colloquial_register_says_piastres_in_quebec(written, spoken):
    colloquial = NormalizationParams(register="colloquial")
    assert normalize(f"Ça coûte {written} ici.", "fr-CA", colloquial) == f"Ça coûte {spoken} ici."


def test_the_colloquial_register_changes_no_other_currency_and_no_other_region():
    colloquial = NormalizationParams(register="colloquial")
    assert normalize("5 € et 5 $", "fr-CA", colloquial) == "cinq euros et cinq piastres"
    assert normalize("5 $", "fr-FR", colloquial) == "cinq dollars"


@pytest.mark.parametrize("tag", ALL_TAGS)
def test_dates_read_in_every_region(tag):
    for written, spoken in [
        ("10/11/2026", "dix novembre deux mille vingt-six"),
        ("2026-11-10", "dix novembre deux mille vingt-six"),
        ("1er mars", "premier mars"),
        ("1/3/2026", "premier mars deux mille vingt-six"),
        ("30/04/2026", "trente avril deux mille vingt-six"),
    ]:
        assert normalize(written, tag) == spoken


def test_the_date_order_param_reads_month_first_only_when_it_is_asked():
    assert normalize("03/04/2025", "fr") == "trois avril deux mille vingt-cinq"
    assert normalize("03/04/2025", "fr", NormalizationParams(date_order="MDY")) == "quatre mars deux mille vingt-cinq"
    assert normalize("13/04/2025", "fr", NormalizationParams(date_order="MDY")) == "treize avril deux mille vingt-cinq"


@pytest.mark.parametrize("written", ["31/04/2026", "29/02/2025", "00/01/2026"])
def test_a_date_that_does_not_exist_stays_as_written(written, caplog):
    assert normalize(f"Le {written}.", "fr").startswith("Le ") and "unread written form" in caplog.text
    assert "dix" not in normalize(f"Le {written}.", "fr")


@pytest.mark.parametrize("tag", ALL_TAGS)
def test_the_defaults_of_each_region(tag):
    params = effective_params(tag)
    assert (
        params.clock,
        params.minute_style,
        params.date_order,
        params.decimal_mark,
        params.scale,
        params.register,
    ) == ("24h", "number", "DMY", ",", "long", "formal")


def test_a_param_that_french_cannot_produce_falls_back_with_a_warning():
    with pytest.warns(ParameterNotHonouredWarning):
        assert normalize("12 h", "fr", NormalizationParams(scale="short")) == "douze heures"
    with pytest.warns(ParameterNotHonouredWarning):
        effective_params("fr", NormalizationParams(date_order="YMD"))


# times


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("à 14h30", "à quatorze heures trente"),
        ("à 14 h 30", "à quatorze heures trente"),
        ("à 14 h 30", "à quatorze heures trente"),
        ("à 14 h30", "à quatorze heures trente"),
        ("à 14H30", "à quatorze heures trente"),
        ("à 21 h", "à vingt et une heures"),
        ("à 7 h 15", "à sept heures quinze"),
        ("à 7 h 5", "à sept heures cinq"),
        ("à 0 h", "à minuit"),
        ("à 00 h", "à minuit"),
        ("à 12 h", "à midi"),
        ("à 12 h 00", "à midi"),
        ("à 24 h", "à minuit"),
        ("à 24 h 00", "à minuit"),
        ("à 00:05", "à minuit cinq"),
        ("à 23:59", "à vingt-trois heures cinquante-neuf"),
        ("à 1:00", "à une heure"),
        ("vers 13 h 01", "vers treize heures une"),
        ("dès 6 h", "dès six heures"),
        ("jusqu'à 22 h 30", "jusqu'à vingt-deux heures trente"),
        ("il est 12 h 10", "il est midi dix"),
        ("avant 0 h 59", "avant minuit cinquante-neuf"),
    ],
)
def test_clock_times(written, spoken):
    assert normalize(written, "fr") == spoken


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("il dort 12 h", "il dort douze heures"),
        ("il dort 0 h", "il dort zéro heure"),
        ("il dort 24 h", "il dort vingt-quatre heures"),
        ("il dort 1 h", "il dort une heure"),
        ("il dort 100 h", "il dort cent heures"),
        ("il dort 21 h", "il dort vingt et une heures"),
        ("il dort 12 h 30", "il dort douze heures trente"),
        ("il dort 1 h 30 min", "il dort une heure trente minutes"),
    ],
)
def test_a_duration_never_reads_midi_or_minuit(written, spoken):
    assert normalize(written, "fr") == spoken


@pytest.mark.parametrize(
    "written", ["25 h 99", "12 h 60", "24 h 30", "99 h 99", "13 h 75", "à 25 h 99", "à 7:60", "à 24:00", "à 25:00"]
)
def test_a_time_that_cannot_be_one_stays_as_written_with_a_warning(written, caplog):
    text = f"Rendez-vous {written}."
    with caplog.at_level(logging.WARNING, logger="text2spoken"):
        assert normalize(text, "fr") == text
    assert "unread written form" in caplog.text
    with pytest.raises(UnreadFormError):
        normalize(text, "fr", NormalizationParams(strict=True))


@pytest.mark.parametrize("written", ["14h30", "14 h 30", "21 h", "à 7:30", "midi", "à 12 h", "1er", "21 h 31"])
def test_a_second_pass_changes_nothing(written):
    once = normalize(f"Rendez-vous {written}.", "fr")
    assert normalize(once, "fr") == once


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("à 14 h 30", "à deux heures trente de l'après-midi"),
        ("à 7 h 30", "à sept heures trente du matin"),
        ("à 12 h 30", "à midi trente"),
        ("à 20 h", "à huit heures du soir"),
        ("à 0 h 30", "à minuit trente"),
        ("à 13 h", "à une heure de l'après-midi"),
        ("à 23 h 59", "à onze heures cinquante-neuf du soir"),
        ("à 12 h", "à midi"),
        ("à 6 h", "à six heures du matin"),
        ("à 17 h 45", "à cinq heures quarante-cinq de l'après-midi"),
        ("à 18 h", "à six heures du soir"),
        ("à 1 h", "à une heure du matin"),
    ],
)
def test_the_12_hour_clock(written, spoken):
    assert normalize(written, "fr", NormalizationParams(clock="12h")) == spoken


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("à 14 h 15", "à quatorze heures et quart"),
        ("à 14 h 30", "à quatorze heures et demie"),
        ("à 14 h 45", "à quinze heures moins le quart"),
        ("à 14 h 20", "à quatorze heures vingt"),
        ("à 12 h 15", "à midi et quart"),
        ("à 12 h 30", "à midi et demi"),
        ("à 11 h 45", "à midi moins le quart"),
        ("à 0 h 30", "à minuit et demi"),
        ("à 23 h 45", "à minuit moins le quart"),
        ("à 0 h 15", "à minuit et quart"),
        ("à 1 h 30", "à une heure et demie"),
        ("à 1 h 15", "à une heure et quart"),
        ("à 0 h 45", "à une heure moins le quart"),
        ("à 21 h 30", "à vingt et une heures et demie"),
        ("à 12 h 45", "à treize heures moins le quart"),
        ("à 8 h", "à huit heures"),
    ],
)
def test_the_phrase_style(written, spoken):
    assert normalize(written, "fr", NormalizationParams(minute_style="phrase")) == spoken


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("à 14 h 30", "à deux heures et demie de l'après-midi"),
        ("à 14 h 45", "à trois heures moins le quart de l'après-midi"),
        ("à 12 h 45", "à une heure moins le quart de l'après-midi"),
        ("à 11 h 45", "à midi moins le quart"),
        ("à 8 h 15", "à huit heures et quart du matin"),
        ("à 20 h 30", "à huit heures et demie du soir"),
    ],
)
def test_the_phrase_style_on_the_12_hour_clock(written, spoken):
    params = NormalizationParams(clock="12h", minute_style="phrase")
    assert normalize(written, "fr-CA", params) == spoken


def test_the_colloquial_register_says_the_quarters_and_the_half_hour():
    colloquial = NormalizationParams(register="colloquial")
    assert normalize("à 14 h 30 et à 7 h 15 et à 7 h 20", "fr-CA", colloquial) == (
        "à quatorze heures et demie et à sept heures et quart et à sept heures vingt"
    )


def test_seconds_read_with_the_minutes():
    assert normalize("à 14:30:05", "fr") == "à quatorze heures trente minutes et cinq secondes"
    assert normalize("à 14:00:01", "fr") == "à quatorze heures zéro minute et une seconde"
    assert normalize("à 12:01:21", "fr") == "à midi une minute et vingt et une secondes"


def test_a_range_of_times_reads_each_time():
    assert normalize("de 9 h à 17 h 30", "fr") == "de neuf heures à dix-sept heures trente"
    assert normalize("de 9h-17h", "fr") == "de neuf heures à dix-sept heures"
    assert normalize("de 9h–17h30", "fr") == "de neuf heures à dix-sept heures trente"


@pytest.mark.parametrize("text", ["Il a 14 heures de retard.", "Il y a 21 hommes.", "Le 5h5 reste.", "14 hm"])
def test_a_letter_after_the_h_is_no_time(text):
    assert "heures trente" not in normalize(text, "fr") and "heure " not in normalize(text, "fr")


def test_a_bare_colon_time_needs_a_time_word():
    assert normalize("Le score final 7:30 reste.", "fr") == "Le score final 7:30 reste."
    assert normalize("Réglée pour 7:30 demain matin.", "fr") == "Réglée pour sept heures trente demain matin."


# agreement


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("21 heures", "vingt et une heures"),
        ("21 minutes", "vingt et une minutes"),
        ("31 fois", "trente et une fois"),
        ("1 personne", "une personne"),
        ("101 pages", "cent une pages"),
        ("81 semaines", "quatre-vingt-une semaines"),
        ("71 années", "soixante et onze années"),
        ("21 pommes", "vingt et une pommes"),
        ("21 kilos", "vingt et un kilos"),
        ("1 euro", "un euro"),
        ("21 jours", "vingt et un jours"),
        ("1 million de fois", "un million de fois"),
    ],
)
def test_a_number_agrees_with_the_noun_after_it(written, spoken):
    assert normalize(written, "fr") == spoken


def test_default_gender_decides_when_no_noun_does():
    feminine = NormalizationParams(default_gender=FrozenMap({"fr": F}))
    assert normalize("21 chats et 21 heures", "fr", feminine) == "vingt et une chats et vingt et une heures"
    assert normalize("21 chats et 21 heures", "fr") == "vingt et un chats et vingt et une heures"


def test_a_hint_decides_before_the_noun_and_the_params():
    analysis = analyze("Il y a 21 heures et 21 chats.", "fr")
    first, second = (span.start for span in analysis.spans)
    assert render(analysis) == "Il y a vingt et une heures et vingt et un chats."
    assert render(analysis, {first: Features(gender=M), second: Features(gender=F)}) == (
        "Il y a vingt et un heures et vingt et une chats."
    )


def test_a_gender_that_french_lacks_raises():
    from text2spoken import UndefinedGrammaticalGender

    with pytest.raises(UndefinedGrammaticalGender):
        normalize("21 chats", "fr", NormalizationParams(default_gender=FrozenMap({"fr": GrammaticalGender.NEUTER})))


def test_a_unit_carries_its_own_gender():
    assert normalize("21 h, 21 min, 21 s, 21 kg, 21 l, 21 °C", "fr") == (
        "vingt et une heures, vingt et une minutes, vingt et une secondes, vingt et un kilogrammes, "
        "vingt et un litres, vingt et un degrés Celsius"
    )


def test_a_range_takes_the_gender_of_the_noun_after_it():
    assert normalize("1-2 heures et 1-2 jours", "fr") == "une à deux heures et un à deux jours"


# cardinals and the plural of cent, vingt and mille


@pytest.mark.parametrize(
    "number,spoken",
    [
        (0, "zéro"),
        (1, "un"),
        (16, "seize"),
        (17, "dix-sept"),
        (21, "vingt et un"),
        (22, "vingt-deux"),
        (31, "trente et un"),
        (70, "soixante-dix"),
        (71, "soixante et onze"),
        (72, "soixante-douze"),
        (80, "quatre-vingts"),
        (81, "quatre-vingt-un"),
        (82, "quatre-vingt-deux"),
        (90, "quatre-vingt-dix"),
        (91, "quatre-vingt-onze"),
        (99, "quatre-vingt-dix-neuf"),
        (100, "cent"),
        (101, "cent un"),
        (110, "cent dix"),
        (180, "cent quatre-vingts"),
        (199, "cent quatre-vingt-dix-neuf"),
        (200, "deux cents"),
        (201, "deux cent un"),
        (280, "deux cent quatre-vingts"),
        (300, "trois cents"),
        (999, "neuf cent quatre-vingt-dix-neuf"),
        (1000, "mille"),
        (1001, "mille un"),
        (1100, "mille cent"),
        (1200, "mille deux cents"),
        (2000, "deux mille"),
        (2021, "deux mille vingt et un"),
        (2080, "deux mille quatre-vingts"),
        (10000, "dix mille"),
        (80000, "quatre-vingt mille"),
        (100000, "cent mille"),
        (200000, "deux cent mille"),
        (201000, "deux cent un mille"),
        (1000000, "un million"),
        (2000000, "deux millions"),
        (80000, "quatre-vingt mille"),
        (80001, "quatre-vingt mille un"),
        (80000000, "quatre-vingts millions"),
        (200000000, "deux cents millions"),
        (1000000000, "un milliard"),
        (3000000000, "trois milliards"),
        (1000000000000, "un billion"),
    ],
)
def test_cardinals(number, spoken):
    assert normalize(str(number), "fr") == spoken


@pytest.mark.parametrize(
    "number,spoken",
    [
        (1, "une"),
        (21, "vingt et une"),
        (71, "soixante et onze"),
        (81, "quatre-vingt-une"),
        (101, "cent une"),
        (201, "deux cent une"),
        (1001, "mille une"),
        (2081, "deux mille quatre-vingt-une"),
        (80, "quatre-vingts"),
    ],
)
def test_feminine_cardinals(number, spoken):
    analysis = analyze(str(number), "fr")
    assert render(analysis, {0: Features(gender=F)}) == spoken


def test_cardinals_agree_with_ovos_number_parser_up_to_a_thousand():
    from ovos_number_parser import pronounce_number
    from ovos_number_parser.util import GrammaticalGender as OvosGender

    for tag in ("fr-FR", "fr-CA"):
        for number in range(0, 1001):
            expected = pronounce_number(number, tag).replace("-et-", " et ")
            assert normalize(str(number), tag) == expected, number
            if number % 10 == 1 or number % 100 == 1:
                feminine = pronounce_number(number, tag, gender=OvosGender.FEMININE).replace("-et-", " et ")
                analysis = analyze(str(number), tag)
                assert render(analysis, {0: Features(gender=F)}) == feminine, number


@pytest.mark.parametrize(
    "number,spoken",
    [
        (2, "deuxième"),
        (3, "troisième"),
        (4, "quatrième"),
        (5, "cinquième"),
        (6, "sixième"),
        (7, "septième"),
        (8, "huitième"),
        (9, "neuvième"),
        (10, "dixième"),
        (11, "onzième"),
        (12, "douzième"),
        (13, "treizième"),
        (14, "quatorzième"),
        (15, "quinzième"),
        (16, "seizième"),
        (17, "dix-septième"),
        (18, "dix-huitième"),
        (19, "dix-neuvième"),
        (20, "vingtième"),
        (21, "vingt et unième"),
        (22, "vingt-deuxième"),
        (30, "trentième"),
        (31, "trente et unième"),
        (50, "cinquantième"),
        (60, "soixantième"),
        (70, "soixante-dixième"),
        (71, "soixante et onzième"),
        (80, "quatre-vingtième"),
        (81, "quatre-vingt-unième"),
        (90, "quatre-vingt-dixième"),
        (99, "quatre-vingt-dix-neuvième"),
        (100, "centième"),
        (101, "cent unième"),
        (200, "deux centième"),
        (1000, "millième"),
        (1001, "mille unième"),
        (2000, "deux millième"),
        (1000000, "millionième"),
        (2000000, "deux millionième"),
        (1000000000, "milliardième"),
    ],
)
def test_ordinals(number, spoken):
    assert normalize(f"{number}e", "fr") == spoken


def test_ordinals_agree_with_the_cldr_rules_where_cldr_is_right():
    from unicode_rbnf import RbnfEngine

    engine = RbnfEngine.for_language("fr")
    for number in range(2, 100):
        if number in (81, 91):
            continue  # CLDR writes "quatre-vingt-et-unième"; the Académie writes "quatre-vingt-unième"
        cldr = (
            engine.format_number(number, ruleset_names=["spellout-ordinal-masculine"])
            .text_by_ruleset["spellout-ordinal-masculine"]
            .replace("-et-", " et ")
        )
        assert normalize(f"{number}e", "fr") == cldr, number


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("1er", "premier"),
        ("1re", "première"),
        ("1ère", "première"),
        ("1ere", "première"),
        ("1ers", "premiers"),
        ("1res", "premières"),
        ("1ères", "premières"),
        ("2e", "deuxième"),
        ("2ème", "deuxième"),
        ("2eme", "deuxième"),
        ("2es", "deuxièmes"),
        ("2èmes", "deuxièmes"),
        ("2nd", "second"),
        ("2nde", "seconde"),
        ("2nds", "seconds"),
        ("2ndes", "secondes"),
        ("1 000e", "millième"),
        ("12e", "douzième"),
    ],
)
def test_ordinal_markers(written, spoken):
    assert normalize(written, "fr") == spoken


@pytest.mark.parametrize("written", ["0e", "1e", "2er", "21er", "3nd", "1nd", "2re", "11er", "5ds", "1 er"])
def test_an_ordinal_marker_that_does_not_fit_the_number_stays_as_written(written):
    assert normalize(f"le {written} ici", "fr").startswith("le ")
    assert written.split()[-1] in normalize(f"le {written} ici", "fr")


# decimals, percent, fractions, ranges


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("0,5", "zéro virgule cinq"),
        ("0,05", "zéro virgule zéro cinq"),
        ("0,005", "zéro virgule zéro zéro cinq"),
        ("3,14", "trois virgule quatorze"),
        ("3,10", "trois virgule dix"),
        ("3,01", "trois virgule zéro un"),
        ("3,00", "trois virgule zéro zéro"),
        ("3,100", "trois virgule un zéro zéro"),
        ("21,21", "vingt et un virgule vingt et un"),
        ("-0,5", "moins zéro virgule cinq"),
        ("+2,5", "plus deux virgule cinq"),
        ("1 234,567", "mille deux cent trente-quatre virgule cinq six sept"),
        (",5", "zéro virgule cinq"),
    ],
)
def test_decimals(written, spoken):
    assert normalize(written, "fr") == spoken


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("0,5 kg", "zéro virgule cinq kilogramme"),
        ("1,5 kg", "un virgule cinq kilogramme"),
        ("1,99 kg", "un virgule quatre-vingt-dix-neuf kilogramme"),
        ("2,0 kg", "deux virgule zéro kilogrammes"),
        ("1,5 €", "un euro cinquante"),
        ("2,5 %", "deux virgule cinq pour cent"),
    ],
)
def test_the_unit_after_a_decimal_is_singular_below_two(written, spoken):
    assert normalize(written, "fr") == spoken


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("1/2", "un demi"),
        ("1/3", "un tiers"),
        ("2/3", "deux tiers"),
        ("1/4", "un quart"),
        ("3/4", "trois quarts"),
        ("1/6", "un sixième"),
        ("5/6", "cinq sixièmes"),
        ("1/20", "un vingtième"),
        ("1/80", "un quatre-vingtième"),
        ("7/10", "sept dixièmes"),
        ("-1/2", "moins un demi"),
        ("1/100", "un centième"),
        ("99/100", "quatre-vingt-dix-neuf centièmes"),
    ],
)
def test_fractions(written, spoken):
    assert normalize(f"Il reste {written} ici.", "fr") == f"Il reste {spoken} ici."


@pytest.mark.parametrize("written", ["3/2", "1/1", "1/0", "1/2 kg", "1/2 l", "$1/2", "2/2"])
def test_a_fraction_that_is_not_one_stays_as_written(written):
    assert written in normalize(f"Il reste {written} ici.", "fr")


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("0 %", "zéro pour cent"),
        ("1 %", "un pour cent"),
        ("21 %", "vingt et un pour cent"),
        ("100%", "cent pour cent"),
        ("12,5 %", "douze virgule cinq pour cent"),
        ("-3 %", "moins trois pour cent"),
        ("+3 %", "plus trois pour cent"),
        ("1 200 %", "mille deux cents pour cent"),
    ],
)
def test_percentages(written, spoken):
    assert normalize(f"Un taux de {written} ici.", "fr") == f"Un taux de {spoken} ici."


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("5-8", "cinq à huit"),
        ("5 - 8", "cinq - huit"),
        ("5–8", "cinq à huit"),
        ("de 5 à 8", "de cinq à huit"),
        ("2-3 fois", "deux à trois fois"),
        ("21-31 heures", "vingt et une à trente et une heures"),
        ("100-200", "cent à deux cents"),
    ],
)
def test_ranges(written, spoken):
    assert normalize(written, "fr") == spoken


@pytest.mark.parametrize("written", ["8-5", "5-5", "2025-2024"])
def test_a_range_that_does_not_go_up_stays_as_written(written):
    assert normalize(f"Le {written} ici.", "fr") == f"Le {written} ici."


# measures, money, abbreviations


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("0 °C", "zéro degré Celsius"),
        ("-0,5 °C", "moins zéro virgule cinq degré Celsius"),
        ("100 °C", "cent degrés Celsius"),
        ("451 °F", "quatre cent cinquante et un degrés Fahrenheit"),
        ("-3°", "moins trois degrés"),
        ("3°", "trois degrés"),
        ("15-25 °C", "quinze à vingt-cinq degrés Celsius"),
        ("1 000 000 °C", "un million de degrés Celsius"),
        ("1 km", "un kilomètre"),
        ("0,3 km", "zéro virgule trois kilomètre"),
        ("2 000 000 km", "deux millions de kilomètres"),
        ("120 km/h", "cent vingt kilomètres par heure"),
        ("3 tr/min", "trois tours par minute"),
        ("12 m²", "douze mètres carrés"),
        ("1 m³", "un mètre cube"),
        ("2 ha", "deux hectares"),
        ("3 kWh", "trois kilowattheures"),
        ("50 Hz", "cinquante hertz"),
        ("1 013 hPa", "mille treize hectopascals"),
        ("500 Mo", "cinq cents mégaoctets"),
        ("2 To", "deux téraoctets"),
        ("2 kcal", "deux kilocalories"),
        ("1 kcal", "une kilocalorie"),
        ("2 mL", "deux millilitres"),
        ("5 dl", "cinq décilitres"),
        ("3 x 4 m", "trois par quatre mètres"),
        ("3 × 4 m", "trois par quatre mètres"),
        ("3 x 4 x 5 cm", "trois par quatre par cinq centimètres"),
    ],
)
def test_measures(written, spoken):
    assert normalize(f"Il y a {written} ici.", "fr") == f"Il y a {spoken} ici."


@pytest.mark.parametrize("text", ["Il y en a 3 l'un.", "Il y en a 2 m'ont dit.", "Il y en a 5 s'en vont."])
def test_a_unit_that_an_elision_continues_is_no_unit(text):
    assert "litre" not in normalize(text, "fr") and "mètre" not in normalize(text, "fr")
    assert "seconde" not in normalize(text, "fr")


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("2 minutes", "deux minutes"),
        ("5 mm", "cinq millimètres"),
        ("5 minutes", "cinq minutes"),
    ],
)
def test_a_unit_that_a_letter_continues_is_no_unit(written, spoken):
    assert normalize(written, "fr") == spoken


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("0,99 €", "quatre-vingt-dix-neuf centimes"),
        ("1,00 €", "un euro"),
        ("0 €", "zéro euro"),
        ("1 234,56 €", "mille deux cent trente-quatre euros cinquante-six"),
        ("21,21 €", "vingt et un euros vingt et un"),
        ("0,21 €", "vingt et un centimes"),
        ("1,21 €", "un euro vingt et un"),
        ("100 €", "cent euros"),
        ("1 000 000 000 €", "un milliard d'euros"),
        ("3 000 000 €", "trois millions d'euros"),
        ("1 000 001 €", "un million un euros"),
        ("-5 €", "moins cinq euros"),
        ("€5", "cinq euros"),
        ("5€", "cinq euros"),
        ("5 euros", "cinq euros"),
        ("0,05 £", "cinq pence"),
        ("1,01 £", "une livre un"),
        ("0,01 £", "un penny"),
        ("2,50 £", "deux livres cinquante"),
        ("1 000 000 £", "un million de livres"),
        ("10 CHF", "dix francs suisses"),
        ("1 000 000 CHF", "un million de francs suisses"),
        ("1,50 $", "un dollar cinquante"),
        ("0,01 $", "un cent"),
    ],
)
def test_money(written, spoken):
    assert normalize(f"Cela coûte {written} ici.", "fr") == f"Cela coûte {spoken} ici."


@pytest.mark.parametrize(
    "written,spoken",
    [
        ("M. Dupont", "Monsieur Dupont"),
        ("M. de Villepin", "Monsieur de Villepin"),
        ("M. d'Artagnan", "Monsieur d'Artagnan"),
        ("MM. Dupont", "Messieurs Dupont"),
        ("Mme de Sévigné", "Madame de Sévigné"),
        ("Mme Du Pont", "Madame Du Pont"),
        ("Dr Martin", "Docteur Martin"),
        ("Pr. Martin", "Professeur Martin"),
        ("Mgr Martin", "Monseigneur Martin"),
        ("St Pierre", "Saint Pierre"),
        ("St-Pierre", "Saint-Pierre"),
        ("Ste-Anne-de-Beaupré", "Sainte-Anne-de-Beaupré"),
        ("n° 5", "numéro cinq"),
        ("n°5", "numéro cinq"),
        ("N°5", "numéro cinq"),
        ("nº 5", "numéro cinq"),
    ],
)
def test_abbreviations(written, spoken):
    assert normalize(f"Voir {written} ici.", "fr") == f"Voir {spoken} ici."


@pytest.mark.parametrize("written", ["M. J. Dupont", "m. dupont", "Mme", "Dr", "St", "Mme.", "n° ", "n° a", "Pr."])
def test_an_abbreviation_with_no_name_after_it_stays_as_written(written):
    assert written.strip() in normalize(f"Voir {written} ici.", "fr")


def test_etc_keeps_the_period_that_ends_a_sentence():
    assert normalize("Des pommes, etc.", "fr") == "Des pommes, et cetera."
    assert normalize("Des pommes, etc. Puis des poires.", "fr") == "Des pommes, et cetera. Puis des poires."
    assert normalize("Des pommes, etc. et des poires.", "fr") == "Des pommes, et cetera et des poires."
    assert normalize("Des pommes (etc.), puis", "fr") == "Des pommes (et cetera), puis"
    assert normalize("Des pommes, etc.…", "fr") == "Des pommes, et cetera…"


# the whole text


def test_a_sentence_of_a_voice_assistant():
    text = "Votre rendez-vous du 10/11/2026 est à 14 h 30, au 3e étage, pour 3,50 € ou 12 $."
    assert normalize(text, "fr-FR") == (
        "Votre rendez-vous du dix novembre deux mille vingt-six est à quatorze heures trente, au troisième étage, "
        "pour trois euros cinquante ou douze dollars."
    )


def test_an_alarm_sentence():
    assert normalize("Votre prochaine alarme est réglée pour 7:30 demain matin.", "fr-CA") == (
        "Votre prochaine alarme est réglée pour sept heures trente demain matin."
    )


def test_text_with_no_written_form_does_not_change():
    text = "Bonjour, comment allez-vous aujourd'hui ? Très bien, merci !"
    assert normalize(text, "fr") == text


def test_blocks_pass_through():
    assert normalize("Il a [[21 h 30]] et 21 h.", "fr") == "Il a [[21 h 30]] et vingt et une heures."


@pytest.mark.parametrize(
    "params",
    [
        NormalizationParams().only(Form.CARDINAL),
        NormalizationParams().without(Form.TIME),
        NormalizationParams().only(Form.TIME, Form.DATE),
    ],
)
def test_forms_can_be_selected(params):
    out = normalize("Le 10 novembre à 14 h 30, 3,50 €.", "fr", params)
    assert (
        out
        == {
            0: "Le dix novembre à quatorze h trente, 3,50 €.",
            1: "Le dix novembre à quatorze heures trente, trois euros cinquante.",
            2: "Le dix novembre à quatorze heures trente, 3,50 €.",
        }[
            [
                NormalizationParams().only(Form.CARDINAL),
                NormalizationParams().without(Form.TIME),
                NormalizationParams().only(Form.TIME, Form.DATE),
            ].index(params)
        ]
    )
    assert normalize(out, "fr", params) == out


def test_the_lexicon_wins():
    params = NormalizationParams(lexicon=FrozenMap({"fr": FrozenMap({"SNCF": "S N C F"})}))
    assert normalize("La SNCF part à 14 h.", "fr-BE", params) == "La S N C F part à quatorze heures."


def test_no_warning_is_raised_for_a_plain_french_text():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert normalize("Il est 21 h.", "fr-CH") == "Il est vingt et une heures."


@pytest.mark.parametrize("tag", ALL_TAGS)
def test_a_second_pass_changes_nothing_in_any_region(tag):
    text = (
        "Le 1er novembre 2026 à 21 h 30, 3,50 € ou 12 $, 50 %, 6 °C, 1/2, 5-8 kg, M. Dupont, le 21e, n° 5, "
        "70 et 90 et 80 ans, 1 000, etc."
    )
    once = normalize(text, tag)
    assert normalize(once, tag) == once
    assert not any(c.isdigit() for c in once)


@pytest.mark.parametrize(
    "tag,written,spoken",
    [
        ("fr-BE", "81", "quatre-vingt-un"),
        ("fr-BE", "89", "quatre-vingt-neuf"),
        ("fr-BE", "181", "cent quatre-vingt-un"),
        ("fr-BE", "80000", "quatre-vingt mille"),
        ("fr-BE", "80001", "quatre-vingt mille un"),
        ("fr-BE", "80000000", "quatre-vingts millions"),
        ("fr-BE", "200000000", "deux cents millions"),
        ("fr-CH", "81", "huitante et un"),
        ("fr-CH", "80000", "huitante mille"),
        ("fr-CH", "80000000", "huitante millions"),
        ("fr-CH", "91", "nonante et un"),
        ("fr-CH", "99", "nonante-neuf"),
        ("fr-BE", "99", "nonante-neuf"),
        ("fr-FR", "200000000", "deux cents millions"),
        ("fr-FR", "100000000", "cent millions"),
        ("fr-FR", "280000000", "deux cent quatre-vingts millions"),
        ("fr-FR", "1200000000", "un milliard deux cents millions"),
        ("fr-FR", "300000000000", "trois cents milliards"),
        ("fr-FR", "80000000000", "quatre-vingts milliards"),
        ("fr-FR", "200000", "deux cent mille"),
        ("fr-FR", "2000000", "deux millions"),
    ],
)
def test_the_plural_of_cent_and_quatre_vingt_before_a_noun_that_counts_millions(tag, written, spoken):
    assert normalize(written, tag) == spoken


def test_the_examples_of_the_readme():
    assert normalize("Rendez-vous le 10/11/2026 à 14 h 30, pour 3,50 € ou 21 h 5.", "fr") == (
        "Rendez-vous le dix novembre deux mille vingt-six à quatorze heures trente, pour trois euros cinquante "
        "ou vingt et une heures cinq."
    )
    assert normalize("Il a 71 ans et 6 °C.", "fr-BE") == "Il a septante et un ans et six degrés Celsius."


@pytest.mark.parametrize(
    "year,spoken",
    [
        (1980, "mille neuf cent quatre-vingt"),
        (2080, "deux mille quatre-vingt"),
        (1780, "mille sept cent quatre-vingt"),
        (1880, "mille huit cent quatre-vingt"),
        (1981, "mille neuf cent quatre-vingt-un"),
        (1900, "mille neuf cent"),
        (2000, "deux mille"),
        (1200, "mille deux cent"),
        (1700, "mille sept cent"),
        (1100, "mille cent"),
        (1000, "mille"),
        (1500, "mille cinq cent"),
        (2200, "deux mille deux cent"),
        (1999, "mille neuf cent quatre-vingt-dix-neuf"),
        (2026, "deux mille vingt-six"),
    ],
)
def test_a_year_in_a_date_keeps_cent_and_quatre_vingt_singular_after_a_month(year, spoken):
    assert normalize(f"Le 10 mars {year}", "fr") == f"Le dix mars {spoken}"


@pytest.mark.parametrize("tag", ["fr", "fr-BE", "fr-CA"])
@pytest.mark.parametrize(
    "written,spoken",
    [
        ("10/11/1980", "dix novembre mille neuf cent quatre-vingt"),
        ("1980-11-10", "dix novembre mille neuf cent quatre-vingt"),
        ("le 5 mai 2080", "le cinq mai deux mille quatre-vingt"),
        ("mai 1980", "mai mille neuf cent quatre-vingt"),
        ("10/11/1900", "dix novembre mille neuf cent"),
        ("10/11/1200", "dix novembre mille deux cent"),
    ],
)
def test_a_year_in_a_date_keeps_cent_and_quatre_vingt_singular(tag, written, spoken):
    assert normalize(written, tag) == spoken


@pytest.mark.parametrize("tag", ["fr", "fr-BE", "fr-CA"])
@pytest.mark.parametrize(
    "year,spoken",
    [
        ("80", "quatre-vingt"),
        ("100", "cent"),
        ("200", "deux cent"),
        ("300", "trois cent"),
        ("900", "neuf cent"),
        ("1980", "mille neuf cent quatre-vingt"),
        ("1200", "mille deux cent"),
        ("1700", "mille sept cent"),
        ("2000", "deux mille"),
        ("1000", "mille"),
        ("2080", "deux mille quatre-vingt"),
        ("1981", "mille neuf cent quatre-vingt-un"),
    ],
)
def test_the_year_speller_keeps_cent_and_quatre_vingt_singular(tag, year, spoken):
    from text2spoken.core.language import resolve
    from text2spoken.lang.fr import SPELLER

    assert SPELLER.year(year, Features(), resolve(tag, NormalizationParams())) == spoken


def test_a_swiss_year_says_huitante():
    assert normalize("10/11/1980 et le 5 mai 2080", "fr-CH") == (
        "dix novembre mille neuf cent huitante et le cinq mai deux mille huitante"
    )
