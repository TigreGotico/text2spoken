"""Arabic readings that need params or hints, which a row of tests/data cannot give. Each expected value comes from
the cited source, never from a run of the code."""
import random
from importlib.metadata import requires

import pytest
from packaging.requirements import Requirement
from packaging.version import Version

from text2spoken import Features, NormalizationParams, analyze, normalize, render
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



ATOMS = (list("0123456789٠١٢٣٤٥٦٧٨٩") + list("#-+$%٪°/:.,;!?()×–−٫٬") + [" ", " ", "\t"]
         + ["الساعة", "في", "من", "إلى", "على", "عن", "حتى", "منذ", "ب", "بـ", "لـ", "و", "عام", "سنة", "سيارة",
            "سيارات", "ساعات", "دقائق", "سنوات", "كتاب", "الطابق", "بالمرتبة", "القرن", "الفئة", "مليون", "ريال",
            "ر.س", "SAR", "US$", "كم", "km", "صباحًا", "صباحا", "مساءً", "مساء", "مارس", "يونيو", "تموز",
            "تشرين الثاني", "غشت", "جويلية", "رقم", "سالب", "1/2", "2/3", "3/4", "14:30", "9:30", "0:15", "1:00",
            "12/03/2024", "13/13/2024", "16:9", "3:16", "1.5", "0.05", "200,000", "45,000", "١٢٫٥", "20-30",
            "10 × 20", "#decade", "الكعكة", "أشخاص", "طلاب", "جميل", "سؤال"])
TAGS = ["ar", "ar-001", "ar-EG", "ar-SA", "ar-MA", "ar-DZ", "ar-TN", "ar-IQ", "ar-LB", "ar-LY", "ar-MR", "arz",
        "ars-SA", "ary"]


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
