"""Regression tests for redaction on rotated (/Rotate) pages.

Bug: PDFs carrying a /Rotate flag (common in CAD exports and scans) redacted the
wrong region — the box landed rotated-away from where the user drew it. A4 files
"just worked" only because they carry rotation=0.

The two coordinate sources need opposite handling, which these tests pin down:

* Manual rectangles come from the rendered preview image (the *displayed*, rotated
  view the user draws on) and must be mapped back with ``page.derotation_matrix``
  before ``add_redact_annot``.
* ``search_for`` already returns *unrotated* page coordinates, so its rects are
  passed to ``add_redact_annot`` as-is.
"""

import fitz
import pytest

from app import Rect, apply_redactions_to_doc

ROTATIONS = [0, 90, 180, 270]


def _make_doc(rotation: int) -> fitz.Document:
    """A portrait page with two well-separated words, then rotated.

    Non-square dimensions make rotation observable: at 90/270 the page's
    width/height swap, so a coordinate-space bug can't hide.
    """
    doc = fitz.open()
    page = doc.new_page(width=400, height=600)
    page.insert_text((60, 60), "ALPHA", fontsize=24)  # near top of unrotated page
    page.insert_text((60, 560), "OMEGA", fontsize=24)  # near bottom of unrotated page
    page.set_rotation(rotation)
    return doc


def _displayed_norm_bbox(page: fitz.Page, word: str) -> tuple[float, float, float, float]:
    """Where ``word`` actually appears in the *rendered* image, normalized 0-1.

    This mirrors what the frontend has: it draws on the rendered preview, so a
    user box over ``word`` is this rect. Found by locating the word's dark glyph
    pixels in the rasterized (displayed-orientation) page.
    """
    only = fitz.open()
    p = only.new_page(width=page.mediabox.width, height=page.mediabox.height)
    p.insert_text((60, 60 if word == "ALPHA" else 560), word, fontsize=24)
    p.set_rotation(page.rotation)
    pix = p.get_pixmap(dpi=72)
    w, h, n, s = pix.width, pix.height, pix.n, pix.samples
    xs = ys = 10**9
    xe = ye = -1
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            i = (y * w + x) * n
            if s[i] < 80 and s[i + 1] < 80 and s[i + 2] < 80:  # dark glyph pixel
                xs, xe = min(xs, x), max(xe, x)
                ys, ye = min(ys, y), max(ye, y)
    assert xe >= 0, f"{word} not found in render"
    return xs / w, ys / h, xe / w, ye / h


@pytest.mark.parametrize("rotation", ROTATIONS)
def test_manual_redaction_hits_drawn_region_on_rotated_page(rotation: int):
    """A box drawn over ALPHA removes ALPHA — and only ALPHA — at every rotation."""
    doc = _make_doc(rotation)
    page = doc[0]

    # Simulate the user drawing over ALPHA's on-screen (displayed) position.
    x0, y0, x1, y1 = _displayed_norm_bbox(page, "ALPHA")
    pad = 0.03
    drawn = Rect(
        page=0,
        x=x0 - pad,
        y=y0 - pad,
        w=(x1 - x0) + 2 * pad,
        h=(y1 - y0) + 2 * pad,
    )

    n = apply_redactions_to_doc(doc, [drawn], "")
    assert n == 1

    text = doc[0].get_text()
    assert "ALPHA" not in text, f"rotation={rotation}: target text not redacted"
    assert "OMEGA" in text, f"rotation={rotation}: wrong region redacted"


@pytest.mark.parametrize("rotation", ROTATIONS)
def test_text_search_redaction_on_rotated_page(rotation: int):
    """Text-query redaction removes the matched word regardless of rotation."""
    doc = _make_doc(rotation)

    n = apply_redactions_to_doc(doc, [], "ALPHA")
    assert n >= 1

    text = doc[0].get_text()
    assert "ALPHA" not in text, f"rotation={rotation}: searched text not redacted"
    assert "OMEGA" in text, f"rotation={rotation}: non-matching text redacted"


def test_manual_redaction_visual_box_covers_target_on_rotated_page():
    """The white fill is burned in over the drawn region (not just text removed).

    Uses rotation=90 (width/height swap) — the case the original bug misplaced.
    """
    rotation = 90
    doc = _make_doc(rotation)
    page = doc[0]
    x0, y0, x1, y1 = _displayed_norm_bbox(page, "ALPHA")

    apply_redactions_to_doc(
        doc,
        [Rect(page=0, x=x0 - 0.03, y=y0 - 0.03, w=(x1 - x0) + 0.06, h=(y1 - y0) + 0.06)],
        "",
    )

    # ALPHA's glyphs should now be gone from the rendered image: no dark pixels
    # remain inside its (padded) displayed region.
    pix = doc[0].get_pixmap(dpi=72)
    w, h, n, s = pix.width, pix.height, pix.n, pix.samples
    rx0, ry0, rx1, ry1 = int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)
    dark = 0
    for y in range(ry0, ry1):
        for x in range(rx0, rx1):
            i = (y * w + x) * n
            if s[i] < 80 and s[i + 1] < 80 and s[i + 2] < 80:
                dark += 1
    assert dark == 0, "target glyphs still visible after redaction"
