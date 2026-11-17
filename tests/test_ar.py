"""Arabic readings that need params or hints, which a row of tests/data cannot give. Each expected value comes from
the cited source, never from a run of the code."""
import random
from importlib.metadata import requires

import pytest
from packaging.requirements import Requirement
from packaging.version import Version

from text2spoken import Features, NormalizationParams, analyze, effective_params, normalize, render
from text2spoken.lang.ar import LECT_REGIONS, PARSER_REFUSES, SERVES
from text2spoken.params import FrozenMap, GrammaticalGender


def test_the_colloquial_register_reads_every_number_oblique():
    # Ryding 2005, p. 343, note 11: spoken Arabic reduces the tens to the genitive-accusative form in -iina.
    params = NormalizationParams(register="colloquial")
    assert normalize("الطقس 20% جميل", "ar", params) == "الطقس عشرين في المئة جميل"


def test_default_gender_counts_a_feminine_noun():
    # Ryding 2005, p. 334: three before a feminine noun is thalaath.
    params = NormalizationParams(default_gender=FrozenMap({"ar": GrammaticalGender.FEMININE}))
    assert normalize("العدد 3", "ar", params) == "العدد ثلاث"


def test_a_hint_gives_the_gender_of_the_counted_noun():
    # Ryding 2005, p. 334: three before a feminine noun is thalaath.
    assert render(analyze("العدد 3", "ar"), {6: Features(gender=GrammaticalGender.FEMININE)}) == "العدد ثلاث"


def test_the_colloquial_register_reads_a_rank_ordinal_and_a_construct_oblique():
    # The README lists this reading as a choice with no source: Ryding 2005, p. 343, note 11, gives the spoken
    # genitive-accusative for the tens only. The oblique forms are those of p. 359, l-Haadii wa-l-'ishriina in the
    # genitive, and p. 350, mi'ataa 'alf-in, with -ay in the oblique.
    params = NormalizationParams(register="colloquial")
    assert normalize("القرن 21", "ar", params) == "القرن الحادي والعشرين"
    assert normalize("سعرها 200,000 ريال", "ar", params) == "سعرها مئتي ألف ريال"


@pytest.mark.parametrize("code", SERVES)
def test_a_spoken_lect_reads_in_the_colloquial_register(code):
    # Ryding 2005, p. 166: "colloquial forms of Arabic do not have case marking". arb is Standard Arabic (ISO 639-3).
    assert effective_params(code).register == ("formal" if code == "arb" else "colloquial")


@pytest.mark.parametrize("tag", ["ar", "ar-001", "ar-EG", "ar-MA", "ar-SA"])
def test_standard_arabic_reads_in_the_formal_register(tag):
    assert effective_params(tag).register == "formal"


def test_each_lect_but_standard_arabic_has_a_region():
    assert set(LECT_REGIONS) == set(SERVES) - {"arb"}


@pytest.mark.parametrize("code", SERVES)
def test_ovos_number_parser_refuses_each_lect_of_parser_refuses_and_no_other(code):
    """A lect that ovos-number-parser starts to read fails here, so that it leaves PARSER_REFUSES."""
    from ovos_number_parser import pronounce_number

    if code in PARSER_REFUSES:
        with pytest.raises(NotImplementedError):
            pronounce_number(13, code)
    else:
        assert pronounce_number(13, code)


# The rows of issue #166. Number words: the output of ovos-number-parser 0.25.0a1 for the code of the lect in the
# oblique case (acw, afb, ars and arz: the dialect tables of AR_LECT_FORMS); colloquial Arabic has no case marking
# (Ryding 2005, p. 166).
ISSUE_166 = [
    ("acm", "mama 7 ana 42 sule 1234", "mama سبعة ana اثنين وأربعين sule ألف ومئتين وأربعة وثلاثين"),
    ("acw", "mama 7 ana 42 sule 1234", "mama سبعة ana اتنين وأربعين sule ألف وميتين وأربعة وتلاتين"),
    ("aeb", "الكتاب 7 الجديد 42 على 1234", "الكتاب سبعة الجديد اثنين وأربعين على ألف ومئتين وأربعة وثلاثين"),
    ("afb", "mama 7 ana 42 sule 1234", "mama سبعة ana اثنين وأربعين sule ألف وميتين وأربعة وثلاثين"),
    ("ars", "الكتاب 7 الجديد 42 على 1234", "الكتاب سبعة الجديد اثنين وأربعين على ألف وميتين وأربعة وثلاثين"),
    ("ary", "الكتاب 7 الجديد 42 على 1234", "الكتاب سبعة الجديد اثنين وأربعين على ألف ومئتين وأربعة وثلاثين"),
    ("arz", "الكتاب 7 الجديد 42 على 1234", "الكتاب سبعة الجديد اتنين وأربعين على ألف وميتين وأربعة وتلاتين"),
    ("ayl", "mama 7 ana 42 sule 1234", "mama سبعة ana اثنين وأربعين sule ألف ومئتين وأربعة وثلاثين"),
]


@pytest.mark.parametrize(("tag", "text", "expected"), ISSUE_166)
def test_a_lect_reads_its_numbers_without_case_endings(tag, text, expected):
    assert normalize(text, tag) == expected
    assert normalize(expected, tag) == expected


def test_a_lect_in_the_formal_register_reads_the_literary_words():
    # Ryding 2005, pp. 329 and 348: thalaathat-a 'ashar-a and mi'ataani, the nominative citation forms.
    params = NormalizationParams(register="formal")
    assert normalize("الطقس 13 جميل 250 جدا", "arz", params) == "الطقس ثلاثة عشر جميل مئتان وخمسون جدا"


def test_a_lect_tag_with_its_region_reads_as_the_bare_lect():
    for code, region in LECT_REGIONS.items():
        assert normalize("الطقس 13 جميل 250 جدا 25/7/1930", f"{code}-{region}") == \
            normalize("الطقس 13 جميل 250 جدا 25/7/1930", code)



ATOMS = (list("0123456789٠١٢٣٤٥٦٧٨٩") + list("#-+$%٪°/:.,;!?()×–−٫٬") + [" ", " ", "\t"]
         + ["الساعة", "في", "من", "إلى", "على", "عن", "حتى", "منذ", "ب", "بـ", "لـ", "و", "عام", "سنة", "سيارة",
            "سيارات", "ساعات", "دقائق", "سنوات", "كتاب", "الطابق", "بالمرتبة", "القرن", "الفئة", "مليون", "ريال",
            "ر.س", "SAR", "US$", "كم", "km", "صباحًا", "صباحا", "مساءً", "مساء", "مارس", "يونيو", "تموز",
            "تشرين الثاني", "غشت", "جويلية", "رقم", "سالب", "1/2", "2/3", "3/4", "14:30", "9:30", "0:15", "1:00",
            "12/03/2024", "13/13/2024", "16:9", "3:16", "1.5", "0.05", "200,000", "45,000", "١٢٫٥", "20-30",
            "10 × 20", "#decade", "الكعكة", "أشخاص", "طلاب", "جميل", "سؤال"])
TAGS = ["ar", "ar-001", "ar-EG", "ar-SA", "ar-MA", "ar-DZ", "ar-TN", "ar-IQ", "ar-LB", "ar-LY", "ar-MR", "arz",
        "ars-SA", "ary", "acw", "afb", "acm", "aeb", "ayl", "arq-DZ", "apd", "shu"]


@pytest.mark.parametrize("seed", range(4))
def test_random_arabic_text_never_raises_and_reads_the_same_on_a_second_pass(seed):
    """Design section 11, on random text built from the written forms, the tables and the varieties of ar.py."""
    rng = random.Random(seed)
    for _ in range(500):
        tag = rng.choice(TAGS)
        text = "".join(rng.choice(ATOMS) + rng.choice(["", " "]) for _ in range(rng.randint(1, 25)))
        once = normalize(text, tag)
        assert normalize(once, tag) == once, (tag, text, once)


def test_the_ar_extra_installs_the_speller_that_writes_the_construct_dual():
    """ar.py reads numbers with ovos-number-parser, which design section 12 keeps out of the base install. Row ar-040
    needs مئتا ألف for 200,000 (Ryding 2005, p. 350), which ovos-number-parser writes from 0.24.3a1."""
    lines = [Requirement(line) for line in requires("text2spoken")]
    extra = [line for line in lines if line.marker is not None and line.marker.evaluate({"extra": "ar"})]
    assert [line.name for line in extra] == ["ovos-number-parser"]
    assert not extra[0].specifier.contains(Version("0.24.2a1"), prereleases=True)
    assert extra[0].specifier.contains(Version("0.24.3a1"), prereleases=True)
