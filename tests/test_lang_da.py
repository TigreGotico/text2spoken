"""Danish readings that the rows of tests/data/da.tsv cannot hold."""
import pytest

from text2spoken import normalize


@pytest.mark.xfail(strict=True, reason="da.py reads no noun gender: `noun_one` gives 1 before any word the neuter et")
def test_one_before_a_common_gender_noun_reads_en():
    """sproget.dk, Den 101. dalmatiner: mængdetal "én/ét"; a common-gender noun takes én."""
    assert normalize("Han har 1 bil.", "da-DK") == "Han har en bil."
