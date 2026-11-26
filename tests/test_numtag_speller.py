"""Portuguese number words come from numtag, for pt-PT and pt-BR."""
import pytest
from numtag import SpokenForm, spell

from text2spoken.core.spans import Features
from text2spoken.lang.pt import SPELLER


@pytest.mark.parametrize(("tag", "ordinal"), [("pt-PT", "quadringentésimo"), ("pt-BR", "quadringentésimo")])
def test_a_portuguese_ordinal_is_the_numtag_ordinal(tag, ordinal):
    assert SPELLER.ordinal("400", Features(), _request(tag)) == spell("400", tag, form=SpokenForm.ORDINAL)[0].text \
        == ordinal


def test_pt_br_reads_its_own_spellings():
    assert SPELLER.cardinal("16", Features(), _request("pt-BR")) == "dezesseis"
    assert SPELLER.cardinal("16", Features(), _request("pt-PT")) == "dezasseis"


def test_a_decimal_of_zeros_reads_one_zero():
    assert SPELLER.decimal("1", "00", Features(), _request("pt-BR")) == "um vírgula zero"


def _request(tag):
    from text2spoken.core.language import resolve
    from text2spoken.params import NormalizationParams
    return resolve(tag, NormalizationParams())
