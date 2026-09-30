"""Auricular block - target anatomy, right ear from the side.

Same view, scale and ear as auricular_patient_position (layout commit
a80ec1b): right side of the head, head up, face to the right. Skin is drawn
see-through so the superficial nerves show.

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

Markings (code, over the painting): the diamond ring of subcutaneous
anaesthetic through the two puncture sites, and the concha zone.

Scale: 10 px per mm.

Run: python3 visuals/auricular_anatomy/draw.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "auricular_anatomy"
PX_PER_MM = 10.0
OX, OY = 800.0, 500.0     # canvas position of the ear centre


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
STA = [(17, -22), (16.5, -10), (16.5, 10), (17.5, 28)]
STA_BRANCHES = [[(17.5, 28), (24, 40), (33, 52)], [(17.5, 28), (18.5, 40), (19.5, 52)]]
ATN = [(12.5, -18), (12, -5), (11.8, 5), (11.5, 18), (12, 28)]
ATN_BRANCHES = [[(12, 28), (19, 38), (27, 52)], [(12, 28), (14, 40), (14.5, 52)], [(12, 28), (9, 40), (6, 52)]]
ATN_TWIGS = [[(11.9, 0), (10, 1)], [(11.6, 16), (8.5, 19)]]
GAN = [(-40, -80), (-25, -62), (-12, -48), (-6, -42)]
GAN_BRANCHES = [[(-6, -42), (5, -44), (15, -45), (26, -42)],          # anterior: over the parotid
                [(-6, -42), (-2, -37), (1, -32)],                     # to the lobe
                [(-6, -42), (-14, -32), (-20, -18), (-22, -4)]]       # posterior: back of the ear, mastoid
LON = [(-62, -80), (-49, -50), (-39, -20), (-35, 5), (-33, 20)]
LON_BRANCHES = [[(-33, 20), (-37, 35), (-41, 52)], [(-33, 20), (-27, 36), (-23, 52)]]
LON_TWIG = [(-35, 8), (-27, 14), (-18.5, 18)]

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

DEFS = ""


def build() -> str:
    tracks = "".join(
        f'<path id="{tid}" d="{path(pts)}" fill="none" stroke="#0E8C98" stroke-width="9" stroke-linecap="round" opacity="0.8"/>'
        for tid, pts in TRACKS.items())
    def nerve(pid, ps, w):
        return f'<path id="{pid}" d="{path(ps)}" fill="none" stroke="#E8C23A" stroke-width="{fmt(w * PX_PER_MM)}" stroke-linecap="round" stroke-opacity="1"/>'
    nerves = (f'<path id="sta" d="{path(STA)}" fill="none" stroke="#C8322B" stroke-width="{fmt(2.2 * PX_PER_MM)}" stroke-linecap="round"/>'
              + "".join(f'<path d="{path(b)}" fill="none" stroke="#C8322B" stroke-width="{fmt(1.6 * PX_PER_MM)}" stroke-linecap="round"/>' for b in STA_BRANCHES)
              + nerve("auriculotemporal-nerve", ATN, 1.6)
              + "".join(nerve(f"atn-branch-{i}", t, 1.1) for i, t in enumerate(ATN_BRANCHES))
              + "".join(nerve(f"atn-twig-{i}", t, 0.9) for i, t in enumerate(ATN_TWIGS))
              + nerve("great-auricular-nerve", GAN, 2.0)
              + "".join(nerve(pid, t, 1.3) for pid, t in zip(("gan-anterior", "gan-lobe", "gan-posterior"), GAN_BRANCHES))
              + nerve("lesser-occipital-nerve", LON, 1.6)
              + "".join(nerve(f"lon-branch-{i}", t, 1.1) for i, t in enumerate(LON_BRANCHES))
              + nerve("lon-twig", LON_TWIG, 0.9))
    concha_zone = f'<path id="concha-zone" class="marking" d="{path(CONCHA, closed=True, tension=0.8)}" fill="#7A5AA8" fill-opacity="0.35" stroke="#7A5AA8" stroke-width="4" stroke-dasharray="14 10"/>'
    sites = "".join(
        f'<circle id="{sid}" cx="{fmt(c(p)[0])}" cy="{fmt(c(p)[1])}" r="16" fill="#C8322B" stroke="#FFFFFF" stroke-width="4"/>'
        for sid, p in (("site-inferior", INFERIOR_SITE), ("site-superior", SUPERIOR_SITE)))
    cx, cy = c(CANAL)

    labels = [
        Label(["Auriculotemporal n."], anchor=(1030, 110), leader=[(1100, 130), c((11.5, 18))], target_id="auriculotemporal-nerve"),
        Label(["Great auricular n."], anchor=(1010, 1130), leader=[(1060, 1085), c((-12, -48))], target_id="great-auricular-nerve"),
        Label(["Lesser occipital n."], anchor=(40, 1130), leader=[(260, 1085), c((-49, -50))], target_id="lesser-occipital-nerve"),
        Label(["Concha"], anchor=(1180, 640), leader=[(1180, 620), c((-1, -6))], target_id="concha-zone"),
    ]

    body = f"""
<g id="anatomy" stroke-linejoin="round">
  <rect id="head" x="0" y="0" width="1600" height="1200" fill="#EFCDB6"/>
  <path id="neck" d="{path(NECK, closed=True, tension=0.6)}" fill="#E2B79D"/>
  <path id="jaw" d="{path(JAW)}" fill="none" stroke="#C99A80" stroke-width="5"/>
  <path id="hair" d="{path(HAIR, closed=True, tension=0.6)}" fill="#5A4030"/>
  <path id="ear" d="{path(EAR, closed=True, tension=0.8)}" fill="#EDBBA3" stroke="#B98468" stroke-width="4"/>
  <path id="helix-rim" d="{path(HELIX_INNER, tension=0.8)}" fill="none" stroke="#B98468" stroke-width="4"/>
  <path id="antihelix" d="{path(ANTIHELIX, closed=True, tension=0.8)}" fill="#F3CDB8" stroke="#B98468" stroke-width="3"/>
  <path id="concha" d="{path(CONCHA, closed=True, tension=0.8)}" fill="#D99A83" stroke="#B98468" stroke-width="3"/>
  <ellipse id="ear-canal" cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(2.2 * PX_PER_MM)}" ry="{fmt(3.2 * PX_PER_MM)}" fill="#6E3A2E"/>
  <path id="tragus" d="{path(TRAGUS, closed=True, tension=0.8)}" fill="#EDBBA3" stroke="#B98468" stroke-width="3"/>
  <path id="antitragus" d="{path(ANTITRAGUS, closed=True, tension=0.8)}" fill="#EDBBA3" stroke="#B98468" stroke-width="3"/>
  <path id="lobe" d="{path(LOBE, closed=True, tension=0.8)}" fill="#EDB39B" stroke="none"/>
</g>
<g id="nerves">{nerves}</g>
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
