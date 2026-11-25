"""pt-PT number words come from numtag, and pt-BR words from ovos-number-parser."""
from numtag import SpokenForm, spell

from text2spoken.core.spellers import NumtagSpeller, OvosNumberSpeller, numtag_writes
from text2spoken.lang.pt import SPELLER


def test_numtag_writes_pt_pt_and_not_pt_br():
    assert numtag_writes("pt-PT")
    assert not numtag_writes("pt-BR")


def test_the_portuguese_speller_picks_the_writer_of_the_variety():
    assert isinstance(SPELLER._writer(_request("pt-PT")), NumtagSpeller)
    assert isinstance(SPELLER._writer(_request("pt-BR")), OvosNumberSpeller)


def test_a_pt_pt_ordinal_is_the_numtag_ordinal():
    from text2spoken.core.spans import Features
    assert SPELLER.ordinal("400", Features(), _request("pt-PT")) == spell("400", "pt-PT", form=SpokenForm.ORDINAL)[0].text


def _request(tag):
    from text2spoken.core.language import resolve
    from text2spoken.params import NormalizationParams
    return resolve(tag, NormalizationParams())
