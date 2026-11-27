"""`distributions(lang)` names the distributions on the output path of a language, and `revision(lang)` gives their
installed versions (design section 12.1)."""
import importlib.metadata

import pytest

from text2spoken import ArgumentTypeError, InvalidLanguageTagError, distributions, revision

CORE = ("text2spoken", "linguatag", "quebra-frases", "unicode-rbnf")


def pinned(*names: str) -> str:
    return "t2s2:" + ";".join(f"{name}=={importlib.metadata.version(name)}" for name in names)


def test_pt_pt_reads_through_numtag_tugalex_and_chronologia():
    assert distributions("pt-PT") == (*CORE, "numtag", "tugalex", "chronologia")
    assert revision("pt-PT") == pinned(*CORE, "numtag", "tugalex", "chronologia")


def test_pt_br_dates_read_through_chronologia():
    assert distributions("pt-BR") == (*CORE, "numtag", "tugalex", "chronologia")
    assert revision("pt-BR") == pinned(*CORE, "numtag", "tugalex", "chronologia")


@pytest.mark.parametrize("lang", ["pt-AO", "pt-MZ", "pt-PT-x-lisbon", "pt-PT-x-coimbra"])
def test_a_tag_of_the_pt_pt_variety_reads_dates_through_chronologia(lang):
    assert distributions(lang) == (*CORE, "numtag", "tugalex", "chronologia")


def test_tetun_reads_through_the_pt_pt_writers():
    assert distributions("tdt") == (*CORE, "numtag", "chronologia")


def test_en_us_reads_numbers_through_numtag_and_no_date_writer():
    assert distributions("en-US") == (*CORE, "numtag")
    assert revision("en-US") == pinned(*CORE, "numtag")


def test_a_language_with_no_file_reads_through_its_number_writer():
    assert distributions("pl-PL") == (*CORE, "ovos-number-parser")
    assert distributions("th-TH") == CORE


def test_a_tag_with_no_region_has_the_revision_of_its_default_variety():
    assert revision("pt") == revision("pt-PT")


def test_a_writer_that_is_not_installed_is_not_listed(monkeypatch):
    real = importlib.metadata.version

    def version(name):
        if name == "tugalex":
            raise importlib.metadata.PackageNotFoundError(name)
        return real(name)

    monkeypatch.setattr(importlib.metadata, "version", version)
    assert distributions("pt-PT") == (*CORE, "numtag", "chronologia")


def test_a_new_version_of_a_listed_distribution_changes_the_revision(monkeypatch):
    before = revision("pt-PT")
    real = importlib.metadata.version
    monkeypatch.setattr(importlib.metadata, "version",
                        lambda name: "99.0.0" if name == "chronologia" else real(name))
    after = revision("pt-PT")
    assert after != before
    assert after == before.replace(f"chronologia=={real('chronologia')}", "chronologia==99.0.0")


def test_lang_must_be_a_tag():
    with pytest.raises(ArgumentTypeError):
        revision(5)
    with pytest.raises(InvalidLanguageTagError):
        revision("not a tag")
    with pytest.raises(ArgumentTypeError):
        distributions(5)
