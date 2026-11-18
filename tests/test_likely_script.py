"""A tag with no script reads the CLDR locale of the script that CLDR likely-subtags gives for its region.

CLDR 49 likelySubtags.xml (unicode-org/cldr, tag release-49):
  <likelySubtag from="zh_TW" to="zh_Hant_TW"/>
  <likelySubtag from="zh_HK" to="zh_Hant_HK"/>
  <likelySubtag from="sr_ME" to="sr_Latn_ME"/>
"""
import pytest

from text2spoken import normalize


@pytest.mark.parametrize("tag, explicit", [("zh-TW", "zh-Hant-TW"), ("zh-HK", "zh-Hant-HK"), ("sr-ME", "sr-Latn-ME")])
def test_a_tag_with_no_script_reads_as_the_tag_with_its_likely_script(tag, explicit):
    text = "10.05 1999"
    assert normalize(text, tag) == normalize(text, explicit)


def test_zh_tw_reads_the_decimal_point_in_traditional_characters():
    assert normalize("10.05", "zh-TW") == "十點零五"
    assert normalize("10.05", "zh-CN") == "十点零五"


def test_sr_me_reads_numbers_in_latin_script():
    spoken = normalize("1999", "sr-ME")
    assert spoken and all(not "Ѐ" <= char <= "ӿ" for char in spoken)
    assert spoken != normalize("1999", "sr-RS")
