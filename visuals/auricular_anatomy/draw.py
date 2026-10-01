"""Auricular block - target anatomy, right ear from the side.

Same view, scale and ear as auricular_patient_position (layout commit
a80ec1b): right side of the head, head up, face to the right. Skin is drawn
see-through so the superficial nerves show.

The nerves and the artery are drawn in code, not painted (2026-10-01).
Gemini twice joined the auriculotemporal nerve to the great auricular nerve,
once also fanning the anterior GAN branch across the face like the facial
nerve and once turning the jaw line into a nerve, dropping the artery and
moving the lesser occipital. Per the playbook, an element failed twice is
drawn in code. The reference for Gemini therefore shows only the head and ear.

Standard adult anatomy, not from the record (listed in spec.json):
- auriculotemporal nerve (V3) rising just in front of the tragus, behind the
  superficial temporal artery, with twigs to the tragus and the front of the
  helix;
- great auricular nerve (C2-C3) rising obliquely from below toward the lobe,
  splitting into an anterior branch (lobe) and a posterior branch (back of the
  ear);
- lesser occipital nerve (C2) rising behind the ear, with a twig to the upper
  back of the auricle;
- auricular branch of the vagus (concha and canal): deep, drawn in code as a
  zone over the concha, not in the layout.

Markings (code, over the painting): the nerves and the superficial temporal
artery, the diamond ring of subcutaneous anaesthetic through the two puncture
sites, and the concha zone.

Scale: 10 px per mm.

Plate (2026-10-01): base.jpg is the owner's Gemini repaint of the head-and-ear
reference (commit a2e7504). Its ear lies within a few px of the layout, so the
layout outlines serve as the traced regions (checked with DEBUG=1). Base
1200x896 scales to 1600 wide with a 2.7 px vertical offset; 10 px/mm holds.

Run: python3 visuals/auricular_anatomy/draw.py   (DEBUG=1 shows the traced regions)
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "auricular_anatomy"
PX_PER_MM = 10.0
OX, OY = 800.0, 500.0
OFFSET_Y = (1200 - 896 * 1600 / 1200) / 2   # base.jpg letterbox     # canvas position of the ear centre


def c(p):
    return (OX + p[0] * PX_PER_MM, OY - p[1] * PX_PER_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


EAR = [(8, 21), (3, 28.5), (-4, 31.5), (-11, 29.5), (-16, 21), (-18.5, 9), (-17, -4), (-13, -15), (-9, -23),
       (-6, -29.5), (-1.5, -32), (3, -29.5), (5.5, -23), (7.5, -17), (9.5, -9), (10.5, -2), (9.5, 6), (8.5, 14)]
HELIX_INNER = [(6, 19), (2, 25.5), (-4, 28), (-10, 26), (-14, 19), (-15.5, 8), (-14, -4), (-10.5, -13), (-7, -19)]
ANTIHELIX = [(4, 15), (-1, 20), (-7, 21), (-11.5, 14), (-12.5, 3), (-10.5, -8), (-6.5, -15), (-1, -16),
             (2, -12), (-4, -9), (-6.5, 0), (-5, 9), (0, 12)]
CONCHA = [(4.5, 8), (-1, 10), (-4.5, 4), (-5.5, -4), (-2.5, -11), (3, -11), (6.5, -6), (7, 2)]
CANAL = (4.5, -2)
TRAGUS = [(10.5, 3), (7.5, 2.5), (5.5, -1), (6, -6), (8.5, -8), (10.5, -6)]
ANTITRAGUS = [(1, -12), (-3, -13), (-5.5, -11), (-3, -9), (0.5, -9.5)]
LOBE = [(-6, -23), (-5, -29.5), (-1.5, -31.5), (2.5, -29), (4, -23), (-1, -20)]

HAIR = [(-90, 70), (-90, -8), (-70, -6), (-50, 4), (-36, 22), (-24, 40), (-8, 47), (10, 48), (28, 45),
        (46, 50), (90, 56), (90, 70)]
JAW = [(14, -17), (13, -32), (11, -46), (12, -56), (19, -63), (35, -68), (60, -74), (95, -80)]
NECK = [(-90, -72), (-40, -68), (-10, -62), (12, -56), (19, -63), (35, -68), (60, -74), (95, -80), (95, -90), (-90, -90)]

# Nerve courses: standard anatomy, branching checked against two third-party
# concept plates the owner shared on 2026-09-30 (Anesthesia Key / Aneskey scalp
# and face innervation). Used for understanding only; not copied, not committed.
# Each branch starts with a lead-in point on its parent a few mm before the
# junction, so it peels off along the parent's line instead of at an angle.
STA = [(17.5, -14), (16.6, -4), (16.2, 8), (16.8, 20), (18, 28)]
STA_BRANCHES = [[(17.4, 24), (18, 28), (22, 36), (27, 44), (33.5, 52)],
                [(17.4, 24), (18, 28), (18.4, 36), (18.9, 44), (19.8, 52)]]
ATN = [(12.6, -9), (12.1, -2), (11.7, 6), (11.5, 15), (11.8, 23), (12.2, 28)]
ATN_BRANCHES = [[(11.9, 24.5), (12.2, 28), (15.5, 34), (20.5, 41), (27, 52)],
                [(11.9, 24.5), (12.2, 28), (13.2, 35), (14, 43), (14.6, 52)],
                [(11.9, 24.5), (12.2, 28), (11, 35), (8.6, 43), (6, 52)]]
ATN_TWIGS = [[(11.9, 3), (11.7, 0.5), (10.6, 0.6), (9.8, 1.4)], [(11.6, 19), (11.5, 16.5), (10, 17.8), (8.5, 19.4)]]
GAN = [(-40, -80), (-31.5, -69.5), (-23, -60), (-15.5, -51.5), (-9.5, -45.2), (-6, -42)]
GAN_BRANCHES = [[(-8.5, -44.2), (-6, -42), (-1, -43.4), (5, -45.2), (13, -47)],          # anterior: short, over the angle and parotid
                [(-8.5, -44.2), (-6, -42), (-3.8, -39.2), (-2.3, -36.8), (-1.5, -34.5)],  # to the lobe
                [(-8.5, -44.2), (-6, -42), (-10.5, -37), (-15.5, -29.5), (-19.3, -20), (-21.3, -11), (-22, -4)]]  # posterior
LON = [(-62, -80), (-55, -64), (-48.5, -48), (-43, -32), (-38.5, -15), (-35.4, 2), (-33.8, 13), (-33, 20)]
LON_BRANCHES = [[(-33.4, 16), (-33, 20), (-34.6, 28), (-37.3, 37), (-39.5, 45), (-41, 52)],
                [(-33.4, 16), (-33, 20), (-30.4, 28), (-27.5, 36.5), (-25, 44.5), (-23, 52)]]
LON_TWIG = [(-35.2, 4), (-35, 8), (-31, 10.6), (-26.5, 13.8), (-22.3, 16.3), (-18.5, 18)]

INFERIOR_SITE = (-1.5, -37.5)
SUPERIOR_SITE = (-4, 37.5)
ANTERIOR_MEET = (17, 1)
POSTERIOR_MEET = (-26, 0)
TRACKS = {
    "track-inf-ant": [INFERIOR_SITE, (11, -22), ANTERIOR_MEET],
    "track-inf-post": [INFERIOR_SITE, (-17, -22), POSTERIOR_MEET],
    "track-sup-ant": [SUPERIOR_SITE, (10, 24), ANTERIOR_MEET],
    "track-sup-post": [SUPERIOR_SITE, (-19, 25), POSTERIOR_MEET],
}

DEFS = '<filter id="soft" x="-20%" y="-20%" width="140%" height="140%" filterUnits="userSpaceOnUse"><feGaussianBlur stdDeviation="2.2"/></filter>'


def build() -> str:
    tracks = "".join(
        f'<path id="{tid}" d="{path(pts)}" fill="none" stroke="#0E8C98" stroke-width="9" stroke-linecap="round" opacity="0.8"/>'
        for tid, pts in TRACKS.items())
    def taper(ps, w0, w1):
        """Closed outline of a cord that narrows from w0 to w1 mm along a smooth spline."""
        import math
        pts_ = [c(p) for p in ps]
        ext = [pts_[0]] + pts_ + [pts_[-1]]
        line = []
        for i in range(1, len(ext) - 2):
            p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
            for k in range(12):
                t = k / 12
                line.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                         + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
        line.append(pts_[-1])
        n = len(line) - 1
        left, right = [], []
        for i, (x, y) in enumerate(line):
            a_, b_ = line[max(i - 1, 0)], line[min(i + 1, n)]
            dx, dy = b_[0] - a_[0], b_[1] - a_[1]
            L = math.hypot(dx, dy) or 1
            hw = (w0 + (w1 - w0) * (i / n) ** 0.8) * PX_PER_MM / 2
            left.append((x - dy / L * hw, y + dx / L * hw))
            right.append((x + dy / L * hw, y - dx / L * hw))
        ring = left + right[::-1]
        return "M" + " L".join(f"{fmt(x)} {fmt(y)}" for x, y in ring) + " Z"

    shadow, body, shine = [], [], []

    def cord(pid, ps, w, colour, w_end=None):
        """A soft painted cord, tapered, drawn into three shared layers (owner, 2026-10-01:
        hard, uniform cords looked pasted on and rigid)."""
        d = taper(ps, w, w_end if w_end is not None else w * 0.45)
        ident = f' id="{pid}"' if pid else ""
        shadow.append(f'<path d="{d}" fill="{colour[1]}"/>')
        body.append(f'<path{ident} d="{d}" fill="{colour[0]}"/>')
        shine.append(f'<path d="{taper(ps, w * 0.28, w * 0.1)}" fill="{colour[2]}"/>')
        return ""

    NERVE, ARTERY = ("#E8D08A", "#7A5A2A", "#FFF8E0"), ("#B8423A", "#5E1A16", "#F0B0A6")

    def nerve(pid, ps, w, w_end=None):
        return cord(pid, ps, w, NERVE, w_end)

    def vessel(pid, ps, w, w_end=None):
        return cord(pid, ps, w, ARTERY, w_end)

    nerves = (vessel("sta", STA, 2.3, 1.8) + "".join(vessel(None, b, 1.6) for b in STA_BRANCHES)
              + nerve("auriculotemporal-nerve", ATN, 1.7, 1.3)
              + "".join(nerve(f"atn-branch-{i}", t, 1.1) for i, t in enumerate(ATN_BRANCHES))
              + "".join(nerve(f"atn-twig-{i}", t, 0.9) for i, t in enumerate(ATN_TWIGS))
              + nerve("great-auricular-nerve", GAN, 2.2, 1.6)
              + "".join(nerve(pid, t, 1.3) for pid, t in zip(("gan-anterior", "gan-lobe", "gan-posterior"), GAN_BRANCHES))
              + nerve("lesser-occipital-nerve", LON, 1.8, 1.2)
              + "".join(nerve(f"lon-branch-{i}", t, 1.1) for i, t in enumerate(LON_BRANCHES))
              + nerve("lon-twig", LON_TWIG, 0.9))
    nerves = (f'<g opacity="0.3" filter="url(#soft)" transform="translate(1.5 2)">{"".join(shadow)}</g>'
              f'<g opacity="0.85">{"".join(body)}</g>'
              f'<g opacity="0.5" filter="url(#soft)" transform="translate(-0.8 -1)">{"".join(shine)}</g>')
    concha_zone = f'<path id="concha-zone" class="marking" d="{path(CONCHA, closed=True, tension=0.8)}" fill="#7A5AA8" fill-opacity="0.35" stroke="#7A5AA8" stroke-width="4" stroke-dasharray="14 10"/>'
    sites = "".join(
        f'<circle id="{sid}" cx="{fmt(c(p)[0])}" cy="{fmt(c(p)[1])}" r="16" fill="#C8322B" stroke="#FFFFFF" stroke-width="4"/>'
        for sid, p in (("site-inferior", INFERIOR_SITE), ("site-superior", SUPERIOR_SITE)))
    debug = os.environ.get("DEBUG") == "1"
    region = 'fill="#ff00ff" fill-opacity="0.35"' if debug else 'fill="#000" fill-opacity="0"'
    base_sha = hashlib.sha256(Path(__file__).with_name("base.jpg").read_bytes()).hexdigest()

    labels = [
        Label(["Auriculotemporal n."], anchor=(1030, 110), leader=[(1100, 130), c((11.5, 18))], target_id="auriculotemporal-nerve"),
        Label(["Great auricular n."], anchor=(1010, 1130), leader=[(1060, 1085), c((-12, -48))], target_id="great-auricular-nerve"),
        Label(["Lesser occipital n."], anchor=(40, 1130), leader=[(260, 1085), c((-49, -50))], target_id="lesser-occipital-nerve"),
        Label(["Concha"], anchor=(1180, 640), leader=[(1180, 620), c((-1, -6))], target_id="concha-zone"),
    ]

    body = f"""
<g id="anatomy" data-base-sha256="{base_sha}">
  <image href="base.jpg" x="0" y="{fmt(OFFSET_Y)}" width="1600" height="{fmt(896 * 1600 / 1200)}" preserveAspectRatio="none"/>
  <rect id="head" x="0" y="0" width="1600" height="1200" fill="none"/>
  <path id="ear" d="{path(EAR, closed=True, tension=0.8)}" {region}/>
  <path id="concha" d="{path(CONCHA, closed=True, tension=0.8)}" {region}/>
  <path id="tragus" d="{path(TRAGUS, closed=True, tension=0.8)}" {region}/>
  <path id="lobe" d="{path(LOBE, closed=True, tension=0.8)}" {region}/>
</g>
<g id="nerves" class="marking">{nerves}</g>
<g id="markings" class="marking">{tracks}{concha_zone}</g>
<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
