"""Properties of section 13: determinism, blocks, text outside spans, independent params, and the import."""
import json
import subprocess
import sys

from tests.conftest import rows
from text2spoken import Form, NormalizationParams, analyze, normalize

TEXTS = [(r["text"], r["tag"]) for r in rows("en")]


def test_deterministic_across_two_processes():
    script = ("import json, sys; from text2spoken import normalize; "
              "print(json.dumps([normalize(t, l) for t, l in json.loads(sys.stdin.read())]))")
    runs = [subprocess.run([sys.executable, "-c", script], input=json.dumps(TEXTS), capture_output=True, text=True,
                           check=True).stdout for _ in range(2)]
    assert runs[0] == runs[1] and json.loads(runs[0]) == [normalize(t, l) for t, l in TEXTS]


def test_text_outside_spans_stays_byte_for_byte():
    text = "  It   costs\t$5,\n\nand  3   cats . "
    analysis = analyze(text, "en")
    out = normalize(text, "en")
    assert out == "  It   costs\tfive dollars,\n\nand  three   cats . "
    kept = [text[a.end:b.start] for a, b in zip(analysis.spans, analysis.spans[1:])]
    assert all(piece in out for piece in kept)


def test_inline_blocks_pass_through():
    text = "Read [[$5 at 14:30]] at 14:30."
    assert normalize(text, "en-US") == "Read [[$5 at 14:30]] at two thirty PM."


def test_two_params_in_one_process_do_not_affect_each_other():
    text = "at 14:30 on 12/03/2024"
    a = NormalizationParams(clock="24h")
    b = NormalizationParams(date_order="MDY")
    first = normalize(text, "en-GB", a)
    normalize(text, "en-GB", b)
    assert normalize(text, "en-GB", a) == first
    assert normalize(text, "en-GB", b) != first


def test_a_form_outside_forms_stays_as_written_on_every_row():
    for text, tag in TEXTS:
        assert normalize(text, tag, NormalizationParams(forms=frozenset())) == text


def test_spans_are_in_order_with_no_overlap():
    for text, tag in TEXTS:
        spans = analyze(text, tag).spans
        assert all(a.end <= b.start for a, b in zip(spans, spans[1:]))


def test_import_loads_no_language_file_and_no_dependency():
    script = ("import sys, text2spoken; "
              "print(sorted(m for m in sys.modules if m.split('.')[0] in {'quebra_frases', 'linguatag', "
              "'unicode_rbnf', 'ovos_number_parser', 'ovos_date_parser', 'ovos_color_parser', 'langcodes'} "
              "or m.startswith('text2spoken.lang.')))")
    out = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True).stdout
    assert out.strip() == "[]"


def test_no_core_path_imports_ovos_date_parser():
    script = ("import sys; from text2spoken import normalize; "
              "[normalize(t, l) for t, l in " + repr(TEXTS) + "]; print('ovos_date_parser' in sys.modules)")
    out = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True).stdout
    assert out.strip() == "False"


def test_analysis_params_drive_the_forms():
    analysis = analyze("It costs $5.", "en", NormalizationParams().only(Form.CARDINAL))
    assert analysis.spans == ()
