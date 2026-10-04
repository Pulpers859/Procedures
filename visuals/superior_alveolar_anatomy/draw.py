"""Superior alveolar (supraperiosteal) block - the right maxillary canine in sagittal section (layout).

A sagittal section through the right maxillary canine, seen from the
patient's right: anterior (the lip) on the image right, posterior (the
palate) on the left, the nasal floor at the top, the crown at the bottom. The
upper lip is lifted forward, opening the vestibule down to the mucobuccal
fold. Drawn from scratch.

Record: the roots of the maxillary teeth sit just above the mucobuccal fold;
the porous maxilla lets fluid injected there reach the nerve; insert at the
height of the fold, angled toward the apex of the tooth; advance a few
millimetres until the tip is near the bone; 1-2 mL.

Standard anatomy added: canine about 28 mm long (crown 10, root 18), its
apex about 3 mm below the nasal floor; a thin labial cortical plate over the
root and cancellous (porous) bone around it; a branch of the anterior
superior alveolar nerve reaching the apex; the fold about 11 mm above the
crown margin.

Code-drawn over the painting: the needle (tip at the bone surface level
with the apex, outside the bone), the injectate along the bone surface.

Millimetres from the canine's cusp tip along and across its long axis, at
24 px/mm.

Run: python3 visuals/superior_alveolar_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import SYRINGE_DEFS, Label, document, fmt, smooth_path, syringe  # noqa: E402

ASSET_ID = "superior_alveolar_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 24.0
TIP = (900.0, 1160.0)                       # canvas of the cusp tip
AXIS = (-5.0, -27.5)                          # tip to apex, mm
LEN = math.hypot(*AXIS)
V = (AXIS[0] / LEN, AXIS[1] / LEN)            # along the tooth, toward the apex
N = (-V[1], V[0])                             # across, toward the labial side (image right)
if N[0] < 0:
    N = (-N[0], -N[1])


def at(s, t):
    """Canvas point s mm along the axis from the cusp tip, t mm toward labial."""
    return (TIP[0] + (V[0] * s + N[0] * t) * PX_MM, TIP[1] + (V[1] * s + N[1] * t) * PX_MM)


WIDTH = [(0, 1.0), (3, 6.0), (7, 8.0), (10, 7.2), (17, 5.4), (24, 3.0), (LEN - 0.4, 1.0), (LEN, 0.0)]


def half(s):
    for (s0, w0), (s1, w1) in zip(WIDTH, WIDTH[1:]):
        if s0 <= s <= s1:
            return (w0 + (w1 - w0) * (s - s0) / (s1 - s0)) / 2
    return 0.0


CEJ, CREST, FOLD_S, NASAL_S = 10.0, 11.5, 21.0, LEN + 3.0
PLATE = 1.1                                   # labial cortical plate
MUCOSA = 1.0
SS = [CREST + (NASAL_S - CREST) * k / 20 for k in range(21)]


def tooth_outline():
    ss = [LEN * k / 40 for k in range(41)]
    return [at(s, half(s)) for s in ss] + [at(s, -half(s)) for s in reversed(ss)]


def labial_surface():
    pts = [at(sv, half(sv) + PLATE) for sv in SS[:-2]] + [at(LEN + 1.5, half(LEN) + PLATE + 0.3)]
    return pts + [(pts[-1][0] + 26, 300.0), (pts[-1][0] + 44, -20.0)]


PALATE_ORAL = [(-20.0, 640.0), (380.0, 660.0), (600.0, 740.0)]


def bone_outline():
    palatal_crest = [at(CREST + 4, -half(CREST + 4) - 2.2), at(CREST, -half(CREST) - 0.4)]
    return labial_surface() + [(-20.0, -20.0)] + PALATE_ORAL + palatal_crest


def nasal_outline():
    floor_y = at(NASAL_S, 0)[1]
    return [(-20.0, -20.0), (640.0, -20.0), (668.0, 160.0), (664.0, floor_y - 30), (600.0, floor_y), (-20.0, floor_y - 18)]


def labial_soft_tissue():
    """Mucosa on the bone from the crest to the fold, then the lifted lip's inner surface."""
    gum = [at(s, half(s) + PLATE + MUCOSA) for s in [CEJ - 0.6] + [CREST + (FOLD_S - CREST) * k / 8 for k in range(9)]]
    fold = at(FOLD_S + 0.6, half(FOLD_S) + PLATE + MUCOSA + 0.8)
    f = at(FOLD_S + 0.6, half(FOLD_S) + PLATE + MUCOSA + 0.8)
    lip_inner = [(f[0] + 120, f[1] + 70), (f[0] + 330, f[1] + 120), (1700.0, f[1] + 150)]
    return gum, fold, lip_inner


NERVE = None


def build() -> str:
    gum, fold, lip_inner = labial_soft_tissue()
    apex = at(LEN, 0)
    face_top = [(x - 4, y) for x, y in labial_surface() if y < fold[1]]
    lip = [fold] + lip_inner + [(1700.0, -20.0)] + list(reversed(face_top))
    g_ss = [CEJ - 0.6] + [CREST + (FOLD_S + 0.6 - CREST) * k / 8 for k in range(9)]
    g_in = [at(sv, half(sv) + (PLATE - 0.3 if sv >= CREST else 0.0)) for sv in g_ss]
    gingiva = gum + [fold] + list(reversed(g_in))
    pulp = [at(s, 0.9 * (1 - s / LEN)) for s in [8 + (LEN - 8.6) * k / 12 for k in range(13)]]
    pulp += [at(s, -0.9 * (1 - s / LEN)) for s in reversed([8 + (LEN - 8.6) * k / 12 for k in range(13)])]
    nerve = [(746.0, -20.0), (752.0, 200.0), (768.0, 400.0), (apex[0] - 2, apex[1] - 30), apex]
    tip_n = at(LEN - 2.0, half(LEN - 2.0) + PLATE + 0.5)
    entry = at(FOLD_S + 0.6, half(FOLD_S) + PLATE + MUCOSA + 0.8)
    u = (tip_n[0] - entry[0], tip_n[1] - entry[1]); n = math.hypot(*u); u = (u[0] / n, u[1] / n)
    hub = (entry[0] - u[0] * 15 * PX_MM, entry[1] - u[1] * 15 * PX_MM)
    spread = [at(LEN + 1.0, half(LEN) + PLATE + 0.3), at(LEN - 1.0, half(LEN - 1) + PLATE + 1.8), at(LEN - 4.5, half(LEN - 4.5) + PLATE + 1.6),
              at(LEN - 6.0, half(LEN - 6) + PLATE + 0.3), at(LEN - 3.0, half(LEN - 3) + PLATE + 0.1)]
    labels = [
        Label(["Root apex"], anchor=(1000, 470), leader=[(990, 454), (apex[0] + 16, apex[1])], target_id="apex-mark", emphasis=True),
        Label(["Superior alveolar", "nerve"], anchor=(960, 150), leader=[(950, 134), nerve[1]], target_id="nerve"),
        Label(["Mucobuccal fold"], anchor=(1060, 640), leader=[(1050, 626), (fold[0] + 16, fold[1])], target_id="fold-mark"),
        Label(["Porous maxilla"], anchor=(60, 560), leader=[(420, 546), (560, 560)], target_id="bone"),
        Label(["Upper lip"], anchor=(1300, 380), leader=[(1380, 340), (1440, 260)], target_id="lip"),
    ]
    painted = BASE.exists()
    debug = os.environ.get("DEBUG") == "1"
    scale = 1600 / BASE_SIZE[0]
    if painted:
        sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
        base_attr = f' data-base-sha256="{sha}"'
        base_image = (f'<image href="{BASE.name}" x="0" y="{fmt((1200 - BASE_SIZE[1] * scale) / 2)}" width="1600" '
                      f'height="{fmt(BASE_SIZE[1] * scale)}" preserveAspectRatio="none"/>')
        layout_attr = f' opacity="{0.35 if debug else 0}"'
    else:
        base_attr = base_image = layout_attr = ""

    def poly(pts, closed=True, tension=0.3):
        return smooth_path([(float(x), float(y)) for x, y in pts], closed=closed, tension=tension)

    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="#4A2328"/>
  <path id="bone" d="{poly(bone_outline())}" fill="#EADFC6" stroke="#B8A47E" stroke-width="8"/>
  <path id="nasal-cavity" d="{poly(nasal_outline(), tension=0.4)}" fill="#C9B9B4" stroke="#C98F8F" stroke-width="8"/>
  <path id="palatal-mucosa" d="{poly([(-20.0, 640.0)] + PALATE_ORAL[1:] + [at(CREST + 4, -half(CREST + 4) - 2.2), at(CEJ - 0.6, -half(CEJ) - 0.3)], closed=False, tension=0.4)}" fill="none" stroke="#D9878A" stroke-width="22"/>
  <path id="lip" d="{poly(lip, tension=0.4)}" fill="#D99A86" stroke="#A55C5E" stroke-width="4"/>
  <path id="lip-mucosa" d="{poly([fold] + lip_inner, closed=False, tension=0.5)}" fill="none" stroke="#C6656C" stroke-width="14"/>
  <path id="gingiva" d="{poly(gingiva, tension=0.3)}" fill="#E58C8C" stroke="#C46A6C" stroke-width="3"/>
  <path id="canine" d="{poly(tooth_outline(), tension=0.3)}" fill="#F3EEE1" stroke="#B5AA90" stroke-width="5"/>
  <path id="enamel" d="{poly([at(s, half(s)) for s in [0, 2, 5, CEJ]] + [at(s, -half(s)) for s in [CEJ, 5, 2, 0]], tension=0.3)}" fill="#FBF9F3" stroke="#B5AA90" stroke-width="3"/>
  <path id="pulp" d="{poly(pulp, tension=0.3)}" fill="#E3868C"/>
  <path id="nerve" d="{poly(nerve, closed=False, tension=0.6)}" fill="none" stroke="#E9C44E" stroke-width="9" stroke-linecap="round"/>
</g>

<g class="marking">
  <path id="spread" d="{poly(spread, tension=0.7)}" fill="#6CCBD2" fill-opacity="0.6" stroke="#0E8C98" stroke-width="3"/>
  <circle id="apex-mark" cx="{fmt(apex[0])}" cy="{fmt(apex[1])}" r="14" fill="none" stroke="#0E8C98" stroke-width="4"/>
  <circle id="fold-mark" cx="{fmt(fold[0])}" cy="{fmt(fold[1])}" r="14" fill="none" stroke="#4A2F7A" stroke-width="4"/>
  {syringe(hub, u, PX_MM * 0.6, shadow=False)}
  <line id="needle" x1="{fmt(hub[0])}" y1="{fmt(hub[1])}" x2="{fmt(tip_n[0])}" y2="{fmt(tip_n[1])}" stroke="url(#syr-steel)" stroke-width="6" stroke-linecap="round"/>
  <circle id="needle-tip" cx="{fmt(tip_n[0])}" cy="{fmt(tip_n[1])}" r="4" fill="#000" opacity="0"/>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=SYRINGE_DEFS, extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
