"""A parameter that a language cannot honour (design section 2.3), and effective_params (section 2)."""
import warnings

import pytest

from text2spoken import (Form, NormalizationParams, ParameterNotHonouredWarning, UnreadFormError,
                         UnsupportedParameterError, analyze, effective_params, normalize)


def test_none_becomes_the_variety_default():
    assert effective_params("en-US").date_order == "MDY"
    assert effective_params("en-GB").date_order == "DMY"
    assert effective_params("en").clock == "12h" and effective_params("en").decimal_mark == "."


def test_effective_params_equal_the_analysis_params():
    params = NormalizationParams(clock="24h", scale="long")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert analyze("at 14:30", "en-US", params).request.params == effective_params("en-US", params)


def test_an_option_that_changes_nothing_has_no_effect():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert normalize("I have 3 cats.", "en", NormalizationParams(register="formal")) == "I have three cats."


def test_a_value_the_language_cannot_produce_warns_and_the_default_applies():
    with pytest.warns(ParameterNotHonouredWarning, match="scale='long'"):
        assert effective_params("en", NormalizationParams(scale="long")).scale == "short"
    with pytest.warns(ParameterNotHonouredWarning):
        assert normalize("It is 1000000000.", "en", NormalizationParams(scale="long")) == "It is one billion."


def test_strict_raises_for_a_value_the_language_cannot_produce():
    with pytest.raises(UnsupportedParameterError):
        normalize("It is 3.", "en", NormalizationParams(scale="long", strict=True))


def test_a_declared_decimal_mark_changes_the_reading():
    assert normalize("It is 3,5 metres.", "en", NormalizationParams(decimal_mark=",")) == \
        "It is three point five metres."
    assert normalize("It is 1.234 metres.", "en", NormalizationParams(decimal_mark=",")) == \
        "It is one thousand two hundred and thirty-four metres."


def test_an_undeclared_decimal_mark_warns():
    with pytest.warns(ParameterNotHonouredWarning):
        assert effective_params("en", NormalizationParams(decimal_mark=";")).decimal_mark == "."


def test_clock_and_minute_style():
    # Wikipedia, "12-hour clock": "fourteen thirty" style 24-hour reading, half past, quarter to.
    assert normalize("at 14:30", "en-US", NormalizationParams(clock="24h")) == "at fourteen thirty"
    assert normalize("at 14:30", "en-US", NormalizationParams(minute_style="phrase")) == "at half past two PM"
    assert normalize("at 8:45", "en-US", NormalizationParams(minute_style="phrase")) == "at quarter to nine"
    assert normalize("at 5:15", "en-US", NormalizationParams(minute_style="phrase")) == "at quarter past five"
    assert normalize("at 14:37", "en-US", NormalizationParams(minute_style="phrase")) == "at two thirty-seven PM"


def test_date_order_decides_only_an_ambiguous_date():
    ymd = NormalizationParams(date_order="MDY")
    assert normalize("on 12/03/2024", "en-GB", ymd) == "on the third of December twenty twenty-four"
    assert normalize("on 25/03/2024", "en-GB", ymd) == "on the twenty-fifth of March twenty twenty-four"


def test_phone_regions_give_trunk_evidence():
    text = "Try 02079460018 now."
    spoken = "Try zero two zero seven nine four six zero zero one eight now."
    assert normalize(text, "en-US", NormalizationParams(phone_regions=frozenset({"GB"}))) == spoken
    assert normalize(text, "en-GB", NormalizationParams(phone_regions=frozenset({"US"}))) != spoken


def test_a_region_with_no_numbering_plan_warns():
    with pytest.warns(ParameterNotHonouredWarning):
        effective_params("en", NormalizationParams(phone_regions=frozenset({"ZZ"})))


def test_a_form_outside_forms_stays_as_written():
    assert normalize("It costs $5 at 14:30.", "en-US", NormalizationParams().without(Form.MONEY, Form.TIME)) == \
        "It costs $5 at 14:30."
    assert normalize("Add 1/2 cup.", "en", NormalizationParams().only(Form.CARDINAL)) == "Add 1/2 cup."


def test_strict_raises_for_a_written_form_that_stays():
    with pytest.raises(UnreadFormError) as raised:
        normalize("The ratio is 16:9 here.", "en", NormalizationParams(strict=True))
    assert raised.value.unread == ("16:9",)
