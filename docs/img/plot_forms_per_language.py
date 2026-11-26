"""docs/img/forms-per-language.svg: the forms that each language file reads.

    python docs/img/plot_forms_per_language.py

The forms come from supports(code).forms for each code in tests/data.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from leaders import leaders_first  # noqa: E402
from plot_style import save  # noqa: E402

from text2spoken import Form, supports  # noqa: E402

DATA = Path(__file__).resolve().parents[2] / "tests" / "data"


def matrix() -> dict:
    codes = sorted(path.stem for path in DATA.glob("*.tsv"))
    read = {code: sorted(form.value for form in supports(code).forms) for code in codes}
    forms = [form.value for form in Form if any(form.value in forms_of for forms_of in read.values())]
    order = leaders_first(codes, key=lambda code: (len(read[code]), code))
    return {"order": order, "forms": forms, "read": read}


def draw(fig, theme, data):
    order, forms, read = data["order"], data["forms"], data["read"]
    ax = fig.subplots()
    for row, code in enumerate(order):
        xs_on = [col for col, form in enumerate(forms) if form in read[code]]
        xs_off = [col for col, form in enumerate(forms) if form not in read[code]]
        ax.scatter(xs_on, [row] * len(xs_on), s=70, color=theme["series"][0], zorder=3)
        ax.scatter(xs_off, [row] * len(xs_off), s=8, color=theme["muted"], zorder=3)
        ax.text(len(forms) - 0.2, row, str(len(read[code])), va="center", color=theme["text"], fontsize=9)
    ax.set_yticks(range(len(order)), order)
    ax.set_xticks(range(len(forms)), forms, rotation=60, ha="right")
    ax.set_xlim(-0.6, len(forms) + 0.4)
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(length=0)
    ax.set_title(f"Forms that each of {len(order)} language files reads, of {len(forms)}")


if __name__ == "__main__":
    save("docs/img/forms-per-language", draw, matrix(), width=8.0, height=6.4)
