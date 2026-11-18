"""Arabic readings that need params or hints, which a row of tests/data cannot give. Each expected value comes from
the cited source, never from a run of the code."""
import random
import re
from importlib.metadata import requires

import pytest
from ovos_number_parser import pronounce_number
from packaging.requirements import Requirement
from packaging.version import Version

from text2spoken import Features, NormalizationParams, analyze, effective_params, normalize, render
from text2spoken.lang.ar import LECT_REGIONS, SERVES
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
def test_the_writer_reads_each_lect(code):
    """ovos-number-parser reads each member of the macrolanguage `ara` from 0.25.1a1, so no digit stays as written."""
    spoken = normalize("الطقس 13 جميل 250 جدا", code)
    assert not any(char.isdigit() for char in spoken), spoken


# The rows of issue #166. A lect reads each number as ovos-number-parser writes it for the code of the lect in the
# oblique case, called here directly, and so with no case ending: colloquial Arabic has no case marking (Ryding 2005,
# p. 166), and the nominative endings -aan and -uun of اثنان, مئتان and ثلاثون never appear.
ISSUE_166 = [
    ("acm", "mama 7 ana 42 sule 1234"),
    ("acw", "mama 7 ana 42 sule 1234"),
    ("aeb", "الكتاب 7 الجديد 42 على 1234"),
    ("afb", "mama 7 ana 42 sule 1234"),
    ("apc", "الكتاب 7 الجديد 42 على 1234"),
    ("arq", "الكتاب 7 الجديد 42 على 1234"),
    ("ars", "الكتاب 7 الجديد 42 على 1234"),
    ("ary", "الكتاب 7 الجديد 42 على 1234"),
    ("arz", "الكتاب 7 الجديد 42 على 1234"),
    ("ayl", "mama 7 ana 42 sule 1234"),
]
NOMINATIVE_ENDING = re.compile(r"(?:ان|ون)(?=\s|$)")


@pytest.mark.parametrize(("tag", "text"), ISSUE_166)
def test_a_lect_reads_its_numbers_without_case_endings(tag, text):
    expected = re.sub(r"[0-9]+", lambda number: pronounce_number(int(number[0]), lang=tag, case="oblique"), text)
    spoken = normalize(text, tag)
    assert spoken == expected
    assert NOMINATIVE_ENDING.search(spoken) is None, spoken
    assert normalize(expected, tag) == expected


# English Wikipedia, "Levantine Arabic grammar", Numerals, revision 1368977674: the cells of the table that the apc
# table of ovos-number-parser cites, written with no vowel marks.
LEVANTINE_CELLS = [("30", "تلاتين"), ("102", "مية وتنين"), ("200", "ميتين"), ("300", "تلتمية")]


@pytest.mark.parametrize(("digits", "words"), LEVANTINE_CELLS)
def test_levantine_reads_its_own_number_words(digits, words):
    assert normalize(f"الطقس {digits} جدا", "apc") == f"الطقس {words} جدا"


def test_the_retired_south_levantine_code_reads_as_levantine():
    # ISO 639-3 change request 2022-006 merged ajp into apc (iso639-3.sil.org, code ajp).
    text = "الطقس 13 جميل 250 جدا 25/7/1930"
    assert normalize(text, "ajp") == normalize(text, "apc")


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


def test_the_base_install_holds_the_speller_that_writes_the_construct_dual():
    """ar.py reads numbers with ovos-number-parser, which the base install holds (design section 12). Row ar-040
    needs مئتا ألف for 200,000 (Ryding 2005, p. 350), which ovos-number-parser writes from 0.24.3a1."""
    lines = [Requirement(line) for line in requires("text2spoken")]
    base = [line for line in lines if line.marker is None and line.name == "ovos-number-parser"]
    assert len(base) == 1
    assert not base[0].specifier.contains(Version("0.24.2a1"), prereleases=True)
