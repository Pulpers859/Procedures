"""Lateral canthotomy and inferior cantholysis - frontal view, patient's RIGHT eye.

Teaching point: where the inferior crus is. It is deep, it runs from the
lateral end of the lower lid out to the inner face of the lateral orbital rim,
and it lies along the LOWER edge of the canthotomy wound - not under the middle
of the lid, which is what the removed Gemini image drew. The cut goes down
toward the rim, away from the globe.

Orientation: frontal view of the patient's right eye, so lateral is image-left
and the caruncle (medial) is image-right. Scale: the palpebral fissure is drawn
about 30 mm wide, roughly 20 px/mm, which puts the rim about 1 cm lateral to
the lateral canthus - inside the 1-2 cm incision the procedure steps give.

Run: python3 visuals/canthotomy_inferior_crus/draw.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import (  # noqa: E402
    Label, document, ellipse_band, ellipse_point, fmt, hair_strokes, lerp, pts, smooth_path,
)

ASSET_ID = "canthotomy_inferior_crus"

# --- Landmarks ---------------------------------------------------------------
LATERAL_CANTHUS = (640.0, 548.0)   # slightly higher than the medial canthus
MEDIAL_CANTHUS = (1250.0, 572.0)

ORBIT_CENTER = (870.0, 560.0)       # bony orbital margin
ORBIT_RX, ORBIT_RY = 470.0, 400.0   # lateral rim at x=400, ~1 cm from the canthus
RIM_THICKNESS = 56.0

UPPER_MARGIN = [LATERAL_CANTHUS, (760, 452), (930, 410), (1100, 440), (1210, 518), MEDIAL_CANTHUS]
LOWER_MARGIN = [LATERAL_CANTHUS, (770, 606), (935, 628), (1100, 616), (1210, 594), MEDIAL_CANTHUS]
UPPER_CREASE = [(676, 486), (790, 386), (955, 346), (1115, 372), (1236, 470)]

IRIS_CENTER = (930.0, 528.0)
IRIS_R = 122.0
PUPIL_R = 46.0

# Lateral canthal tendon crura, both deep. They insert on the inner face of
# the lateral orbital rim; after the canthotomy they sit above and below the
# wound. The inferior crus is the target.
INSERTION_X = 432.0
INFERIOR_CRUS = ((628.0, 566.0), (INSERTION_X, 604.0))
SUPERIOR_CRUS = ((628.0, 530.0), (INSERTION_X, 494.0))

# Canthotomy: horizontal from the lateral canthus to the rim.
INCISION = (LATERAL_CANTHUS, (418.0, LATERAL_CANTHUS[1]))

# The anatomy is drawn in its own coordinates, then zoomed so the lateral
# canthus-to-rim region fills the card. Labels stay unscaled, so their leader
# endpoints are mapped through the same view.
VIEW_SCALE = 1.5
VIEW_SHIFT = (-390.0, -240.0)


def view(p):
    return (p[0] * VIEW_SCALE + VIEW_SHIFT[0], p[1] * VIEW_SCALE + VIEW_SHIFT[1])


def tendon(a, b, width_a, width_b, sag):
    """Outline of a tapered, gently curved tendon from a to b."""
    top = [(a[0], a[1] - width_a / 2), (lerp(a, b, 0.5)[0], lerp(a, b, 0.5)[1] + sag - (width_a + width_b) / 4), (b[0], b[1] - width_b / 2)]
    bottom = [(b[0], b[1] + width_b / 2), (lerp(a, b, 0.5)[0], lerp(a, b, 0.5)[1] + sag + (width_a + width_b) / 4), (a[0], a[1] + width_a / 2)]
    return smooth_path(top) + " L" + smooth_path(bottom)[1:] + " Z"


def fibres(a, b, width_a, width_b, sag, count):
    lines = []
    for i in range(count):
        f = (i + 1) / (count + 1) - 0.5
        pts_ = [(a[0], a[1] + f * width_a * 0.8), (lerp(a, b, 0.5)[0], lerp(a, b, 0.5)[1] + sag + f * (width_a + width_b) * 0.4), (b[0], b[1] + f * width_b * 0.8)]
        lines.append(smooth_path(pts_))
    return " ".join(lines)


# Cantholysis: a cut across the inferior crus near the rim, scissors directed
# inferiorly (and posteriorly, which a frontal view cannot show), away from the globe.
CUT_T = 0.78


def build() -> str:
    crus_a, crus_b = INFERIOR_CRUS
    cut_center = lerp(crus_a, crus_b, CUT_T)
    cut = [(cut_center[0] - 5, cut_center[1] - 30), (cut_center[0] + 5, cut_center[1] + 30)]
    arrow_start = (cut_center[0] + 8, cut_center[1] + 52)
    arrow_end = (cut_center[0] + 2, cut_center[1] + 176)

    almond = smooth_path(UPPER_MARGIN) + " L" + smooth_path(list(reversed(LOWER_MARGIN)))[1:] + " Z"

    defs = f"""
<radialGradient id="skinGrad" cx="{fmt(ORBIT_CENTER[0])}" cy="{fmt(ORBIT_CENTER[1])}" r="820" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="var(--skin-hi)"/><stop offset="0.55" stop-color="var(--skin)"/><stop offset="1" stop-color="var(--skin-lo)"/>
</radialGradient>
<radialGradient id="hollow" cx="{fmt(ORBIT_CENTER[0])}" cy="{fmt(ORBIT_CENTER[1] - 20)}" r="430" gradientUnits="userSpaceOnUse">
  <stop offset="0.45" stop-color="var(--skin-deep)" stop-opacity="0.32"/><stop offset="1" stop-color="var(--skin-deep)" stop-opacity="0"/>
</radialGradient>
<radialGradient id="plateFade" cx="800" cy="600" r="760" gradientUnits="userSpaceOnUse">
  <stop offset="0.72" stop-color="#fff"/><stop offset="1" stop-color="#000"/>
</radialGradient>
<mask id="plateMask"><rect width="1600" height="1200" fill="url(#plateFade)"/></mask>
<radialGradient id="scleraGrad" cx="{fmt(IRIS_CENTER[0])}" cy="{fmt(IRIS_CENTER[1])}" r="360" gradientUnits="userSpaceOnUse">
  <stop offset="0.3" stop-color="var(--sclera)"/><stop offset="1" stop-color="var(--sclera-shade)"/>
</radialGradient>
<radialGradient id="irisGrad" cx="{fmt(IRIS_CENTER[0])}" cy="{fmt(IRIS_CENTER[1])}" r="{fmt(IRIS_R)}" gradientUnits="userSpaceOnUse">
  <stop offset="0.35" stop-color="var(--iris-hi)"/><stop offset="0.8" stop-color="var(--iris)"/><stop offset="1" stop-color="var(--iris-lo)"/>
</radialGradient>
<linearGradient id="lidShadow" x1="0" y1="{fmt(UPPER_MARGIN[2][1])}" x2="0" y2="{fmt(UPPER_MARGIN[2][1] + 70)}" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#000" stop-opacity="0.22"/><stop offset="1" stop-color="#000" stop-opacity="0"/>
</linearGradient>
<clipPath id="almond"><path d="{almond}"/></clipPath>
<pattern id="deepHatch" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <rect width="14" height="14" fill="var(--target-fill)"/><line x1="0" y1="0" x2="0" y2="14" stroke="var(--target)" stroke-width="3" stroke-opacity="0.55"/>
</pattern>
<marker id="arrowHead" viewBox="0 0 12 12" refX="6" refY="6" markerWidth="4.2" markerHeight="4.2" orient="auto-start-reverse">
  <path d="M0,0 L12,6 L0,12 Z" fill="var(--danger)"/>
</marker>
"""

    iris_fibres = "".join(
        f'<line x1="{fmt(ellipse_point(IRIS_CENTER, PUPIL_R + 6, PUPIL_R + 6, a)[0])}" '
        f'y1="{fmt(ellipse_point(IRIS_CENTER, PUPIL_R + 6, PUPIL_R + 6, a)[1])}" '
        f'x2="{fmt(ellipse_point(IRIS_CENTER, IRIS_R - 10, IRIS_R - 10, a + 4)[0])}" '
        f'y2="{fmt(ellipse_point(IRIS_CENTER, IRIS_R - 10, IRIS_R - 10, a + 4)[1])}"/>'
        for a in range(0, 360, 9)
    )

    brow_line = [(430, 262), (620, 196), (840, 168), (1060, 180), (1300, 236)]
    brow = hair_strokes(seed=7, along=brow_line, count=150, length=40, spread=20, lean=-0.22)

    upper_lashes = hair_strokes(seed=11, along=UPPER_MARGIN[1:-1], count=70, length=26, spread=2, lean=-1.2)

    rim = ellipse_band(ORBIT_CENTER, ORBIT_RX, ORBIT_RY, RIM_THICKNESS, 146, 214)
    orbit_margin = ellipse_band(ORBIT_CENTER, ORBIT_RX, ORBIT_RY, RIM_THICKNESS, 214, 506, steps=60)

    labels = [
        Label(["Lateral", "orbital rim"], anchor=(56, 118),
              leader=[(206, 206), view(ellipse_point(ORBIT_CENTER, ORBIT_RX, ORBIT_RY, 202))],
              target_id="lateral-orbital-rim"),
        Label(["Inferior crus"], anchor=(470, 1010),
              leader=[(560, 955), view(lerp(crus_a, crus_b, 0.3))],
              target_id="inferior-crus", emphasis=True),
    ]

    body = f"""
<g id="anatomy" transform="translate({fmt(VIEW_SHIFT[0])} {fmt(VIEW_SHIFT[1])}) scale({VIEW_SCALE})">
<g id="face" mask="url(#plateMask)">
  <rect width="1600" height="1200" fill="url(#skinGrad)"/>
  <ellipse cx="{fmt(ORBIT_CENTER[0])}" cy="{fmt(ORBIT_CENTER[1])}" rx="{fmt(ORBIT_RX + 30)}" ry="{fmt(ORBIT_RY + 20)}" fill="url(#hollow)"/>
  <path d="{smooth_path(brow_line)}" fill="none" stroke="var(--brow)" stroke-width="54" stroke-linecap="round" opacity="0.22"/>
  <path id="brow" d="{brow}" fill="none" stroke="var(--brow)" stroke-width="3" stroke-linecap="round" opacity="0.6"/>
</g>

<g id="deep-bone" opacity="0.62">
  <polygon points="{pts(orbit_margin)}" fill="var(--bone)" opacity="0.45"/>
  <polygon id="lateral-orbital-rim" points="{pts(rim)}" fill="var(--bone)" stroke="var(--bone-edge)" stroke-width="3" stroke-dasharray="14 9"/>
</g>

<path d="{smooth_path(UPPER_CREASE)}" fill="none" stroke="var(--lid-line)" stroke-width="4" stroke-linecap="round" opacity="0.45"/>

<g id="globe" clip-path="url(#almond)">
  <path d="{almond}" fill="url(#scleraGrad)"/>
  <circle id="iris" cx="{fmt(IRIS_CENTER[0])}" cy="{fmt(IRIS_CENTER[1])}" r="{fmt(IRIS_R)}" fill="url(#irisGrad)"/>
  <g stroke="var(--iris-lo)" stroke-width="2" opacity="0.35">{iris_fibres}</g>
  <circle cx="{fmt(IRIS_CENTER[0])}" cy="{fmt(IRIS_CENTER[1])}" r="{fmt(IRIS_R)}" fill="none" stroke="var(--iris-lo)" stroke-width="6"/>
  <circle cx="{fmt(IRIS_CENTER[0])}" cy="{fmt(IRIS_CENTER[1])}" r="{fmt(PUPIL_R)}" fill="var(--pupil)"/>
  <ellipse cx="{fmt(IRIS_CENTER[0] - 40)}" cy="{fmt(IRIS_CENTER[1] - 44)}" rx="24" ry="17" fill="#fff" opacity="0.85"/>
  <ellipse id="caruncle" cx="{fmt(MEDIAL_CANTHUS[0] - 28)}" cy="{fmt(MEDIAL_CANTHUS[1] - 4)}" rx="26" ry="19" fill="var(--caruncle)"/>
  <path d="{smooth_path(UPPER_MARGIN)} L1600,0 L0,0 Z" fill="url(#lidShadow)"/>
</g>

<path id="lower-lid-margin" d="{smooth_path(LOWER_MARGIN)}" fill="none" stroke="var(--lid-line)" stroke-width="5" stroke-linecap="round"/>
<path id="upper-lid-margin" d="{smooth_path(UPPER_MARGIN)}" fill="none" stroke="var(--lash)" stroke-width="9" stroke-linecap="round"/>
<path d="{upper_lashes}" fill="none" stroke="var(--lash)" stroke-width="4" stroke-linecap="round"/>
<circle id="lateral-canthus" cx="{fmt(LATERAL_CANTHUS[0])}" cy="{fmt(LATERAL_CANTHUS[1])}" r="6" fill="var(--lash)"/>
<circle id="medial-canthus" cx="{fmt(MEDIAL_CANTHUS[0])}" cy="{fmt(MEDIAL_CANTHUS[1])}" r="5" fill="var(--lid-line)"/>

<g id="tendon" data-depth="deep">
  <path id="superior-crus" d="{tendon(*SUPERIOR_CRUS, 16, 30, -4)}" fill="var(--deep-grey)" fill-opacity="0.2" stroke="var(--deep-grey)" stroke-width="3" stroke-dasharray="10 8"/>
  <path d="{fibres(*SUPERIOR_CRUS, 16, 30, -4, 3)}" fill="none" stroke="var(--deep-grey)" stroke-width="1.5" opacity="0.5"/>
  <path id="inferior-crus" d="{tendon(crus_a, crus_b, 18, 36, 5)}" fill="var(--target-fill)" stroke="var(--target)" stroke-width="4" stroke-dasharray="12 7"/>
  <path d="{fibres(crus_a, crus_b, 18, 36, 5, 4)}" fill="none" stroke="var(--target)" stroke-width="2" opacity="0.55"/>
</g>

<g id="canthotomy">
  <line id="canthotomy-incision" x1="{fmt(INCISION[0][0])}" y1="{fmt(INCISION[0][1])}" x2="{fmt(INCISION[1][0])}" y2="{fmt(INCISION[1][1])}" stroke="var(--danger)" stroke-width="10" stroke-linecap="round"/>
  <line x1="{fmt(INCISION[0][0])}" y1="{fmt(INCISION[0][1] + 5)}" x2="{fmt(INCISION[1][0])}" y2="{fmt(INCISION[1][1] + 5)}" stroke="var(--danger-soft)" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
</g>

<g id="cantholysis">
  <line id="cantholysis-cut" x1="{fmt(cut[0][0])}" y1="{fmt(cut[0][1])}" x2="{fmt(cut[1][0])}" y2="{fmt(cut[1][1])}" stroke="var(--danger)" stroke-width="9" stroke-linecap="round"/>
  <line id="cut-direction" x1="{fmt(arrow_start[0])}" y1="{fmt(arrow_start[1])}" x2="{fmt(arrow_end[0])}" y2="{fmt(arrow_end[1])}" stroke="var(--danger)" stroke-width="9" stroke-linecap="round" marker-end="url(#arrowHead)"/>
</g>

</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=defs)


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
