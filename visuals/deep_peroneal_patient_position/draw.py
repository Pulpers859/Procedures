"""Deep peroneal nerve block - probe and needle on the patient.

Painted base plus code-drawn markings. base.jpg is the owner's Gemini photo
of this file's flat layout (commit 0191e0c), repaired in the same chat in
two single-change turns: the painted syringe (upright along the leg, needle
pointing at the toes) was removed, and the probe, first painted on the
dorsum of the foot, was moved up to the ankle crease (provenance.json). The
leg and foot lie on the layout within a few pixels, so those layout shapes
stay as the invisible regions; the probe, the hand-free cover it makes and
the malleoli are traced in base pixels (DEBUG=1 shows them). Re-trace them
if the base is replaced.

The positioning half of the pair; deep_peroneal_anatomy is the section under
this probe.

Right ankle and foot of a supine patient, seen from the front with the leg
at the top and the toes at the bottom: the patient's right on the image
left, so lateral (the little toe, the lateral malleolus) is left and medial
(the big toe, the medial malleolus) is right - the same way round as a
transverse ultrasound and the anatomy plate.

Record: supine; transducer transverse over the anterior ankle; the nerve
runs with the anterior tibial artery (dorsalis pedis), usually lateral to
it. Added, not in the record: the probe lies across the front of the ankle
at the joint line, between the malleoli (the layout put it level with them;
Gemini placed it about 2 cm lower twice, and the record's "anterior ankle"
still holds, so it stays); the dashed red artery course runs from the ankle
to the first intermetatarsal space (standard anatomy). In-plane from lateral
is the owner's choice (2026-10-01: "I want the needle coming in plane"): the
needle is drawn here, entering just beyond the lateral end of the probe face
and running along its long axis.

Code-drawn markings: the needle and syringe, and the dashed artery course,
hidden where the probe covers the skin.

Millimetres from the mid-point of the anterior ankle between the malleoli
(x toward medial = image right, y toward the toes) at 3.6 px/mm in the
layout. Adult foot, about 255 mm long and 95 mm across the metatarsal heads.

Run: python3 visuals/deep_peroneal_patient_position/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "deep_peroneal_patient_position"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
BASE_SCALE = 1600 / BASE_SIZE[0]
BASE_Y0 = (1200 - BASE_SIZE[1] * BASE_SCALE) / 2

# Traced on the painting, in base pixels.
PROBE_OUTLINE = [(606, 0), (626, 0), (622, 88), (636, 96), (638, 236), (688, 246), (694, 270), (686, 314),
                 (512, 316), (502, 300), (503, 250), (512, 240), (554, 236), (556, 96), (600, 88)]
PROBE_FACE = [(513, 281), (680, 281), (683, 300), (678, 313), (516, 313), (512, 300)]
LAT_MALLEOLUS_PX, LAT_MALLEOLUS_R = (494.0, 282.0), (12.0, 34.0)
MED_MALLEOLUS_PX, MED_MALLEOLUS_R = (691.0, 198.0), (12.0, 38.0)
NEEDLE_ENTRY_PX = (500.0, 303.0)     # just beyond the face's lateral end, on its long axis
NEEDLE_HUB_PX = (418.0, 301.0)
SYRINGE_END_PX = (300.0, 298.0)


def b(p):
    """base pixels -> canvas"""
    return (p[0] * BASE_SCALE, p[1] * BASE_SCALE + BASE_Y0)


def based(points):
    return " ".join(f"{fmt(b(p)[0])},{fmt(b(p)[1])}" for p in points)
PX_MM = 3.6
ORIGIN = (780.0, 290.0)


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


LAT_MALLEOLUS = (-37.0, 6.0)      # lower and further back than the medial
MED_MALLEOLUS = (35.0, -6.0)

# Outline clockwise from the top of the leg, lateral side first.
LATERAL = [(-28, -100), (-25, -50), (-28, -20), (-37, 2), (-38, 18), (-36, 40), (-41, 80), (-46, 125), (-48, 150), (-47, 172)]
TOES = [  # little toe to big toe: (x0, x1, tip y)
    (-47, -33, 196), (-33, -19, 206), (-19, -4, 214), (-4, 12, 220), (13, 45, 232),
]
MEDIAL = [(47, 170), (50, 140), (47, 100), (42, 60), (38, 25), (36, 0), (28, -25), (25, -50), (27, -100)]

ARTERY = [(4, -20), (5, 10), (10, 50), (15, 90), (19, 118)]

PROBE_CENTRE, PROBE_LEN, PROBE_W = (0.0, -2.0), 38.0, 12.0
PROBE_X0 = PROBE_CENTRE[0] - PROBE_LEN / 2
NEEDLE_ENTRY = (PROBE_X0 - 6, PROBE_CENTRE[1])
NEEDLE_HUB = (PROBE_X0 - 40, PROBE_CENTRE[1] - 6)

DEFS = """
<linearGradient id="skin-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9A88C"/><stop offset="0.3" stop-color="#EBC3AA"/>
  <stop offset="0.7" stop-color="#F0CDB6"/><stop offset="1" stop-color="#E2B69C"/></linearGradient>
<linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8EEF3"/><stop offset="1" stop-color="#D3DDE6"/></linearGradient>
<filter id="soft" x="-20%" y="-80%" width="140%" height="260%"><feGaussianBlur stdDeviation="5"/></filter>
<linearGradient id="barrel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/>
  <stop offset="0.4" stop-color="#EEF2F5" stop-opacity="0.85"/><stop offset="0.8" stop-color="#CDD5DC" stop-opacity="0.85"/><stop offset="1" stop-color="#A9B3BC"/></linearGradient>
<linearGradient id="plastic" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.6" stop-color="#E9EDF0"/><stop offset="1" stop-color="#BCC4CB"/></linearGradient>
<linearGradient id="stopper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6A717A"/><stop offset="0.5" stop-color="#3B4148"/><stop offset="1" stop-color="#22272C"/></linearGradient>
<linearGradient id="hub" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/><stop offset="1" stop-color="#C6CED5" stop-opacity="0.95"/></linearGradient>
<linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4F6F8"/><stop offset="0.45" stop-color="#B9C1C8"/><stop offset="1" stop-color="#6E777F"/></linearGradient>
"""


def foot_outline():
    pts = list(LATERAL)
    for x0, x1, tip in TOES:
        base = 172 if x0 < 0 else 176
        pts += [(x0 + 1, base + 4), (x0 + 2, tip - 6), ((x0 + x1) / 2, tip), (x1 - 2, tip - 6), (x1 - 1, base + 4)]
    return pts + MEDIAL


def needle_and_syringe():
    """A 1.5-inch needle on a 5 mL syringe at the foot's scale (3.6 px/mm:
    barrel about 12 mm across), level with the probe's long axis and coming
    from lateral over the sheet. Drawn along a local axis from the skin entry
    back toward the plunger, shaded as a lit cylinder with the light from the
    upper left, and seated on the sheet by a soft shadow down and right."""
    ex, ey = b(NEEDLE_ENTRY_PX)
    shaft = 72.0                        # visible needle, canvas px (about 20 mm)
    hub0 = -shaft - 24                  # hub, then the luer tip, then the barrel
    tip0 = hub0 - 14
    barrel0, barrel_len, r = tip0 - 200, 200.0, 21.0
    rod0 = barrel0 - 84
    shadow = (f'<g transform="translate(9 15)" filter="url(#soft)" opacity="0.34" fill="#1B2733">'
              f'<rect x="{fmt(rod0 - 8)}" y="-9" width="{fmt(barrel0 - rod0 + 8)}" height="18" rx="6"/>'
              f'<rect x="{fmt(barrel0)}" y="{fmt(-r)}" width="{fmt(barrel_len + 14)}" height="{fmt(2 * r)}" rx="9"/>'
              f'<rect x="{fmt(hub0)}" y="-8" width="24" height="16" rx="4"/>'
              f'<rect x="{fmt(-shaft)}" y="-2" width="{fmt(shaft)}" height="4"/></g>')
    parts = [
        # plunger rod and thumb press
        f'<rect x="{fmt(rod0)}" y="-7" width="{fmt(barrel0 - rod0 + 30)}" height="14" rx="2" fill="url(#plastic)" stroke="#9AA3AB" stroke-width="1.5"/>',
        f'<rect x="{fmt(rod0 - 10)}" y="-27" width="12" height="54" rx="5" fill="url(#plastic)" stroke="#9AA3AB" stroke-width="1.5"/>',
        # barrel with clear fluid ahead of the rubber stopper
        f'<rect x="{fmt(barrel0)}" y="{fmt(-r)}" width="{fmt(barrel_len)}" height="{fmt(2 * r)}" rx="8" fill="url(#barrel)" stroke="#A7B0B8" stroke-width="2"/>',
        f'<rect x="{fmt(barrel0 + 50)}" y="{fmt(-r + 4)}" width="{fmt(barrel_len - 56)}" height="{fmt(2 * r - 8)}" rx="5" fill="#BFD8E6" fill-opacity="0.35"/>',
        f'<rect x="{fmt(barrel0 + 30)}" y="{fmt(-r + 2)}" width="20" height="{fmt(2 * r - 4)}" rx="3" fill="url(#stopper)"/>',
        f'<line x1="{fmt(barrel0 + 37)}" y1="{fmt(-r + 3)}" x2="{fmt(barrel0 + 37)}" y2="{fmt(r - 3)}" stroke="#2A2F35" stroke-width="2"/>',
        f'<line x1="{fmt(barrel0 + 44)}" y1="{fmt(-r + 3)}" x2="{fmt(barrel0 + 44)}" y2="{fmt(r - 3)}" stroke="#2A2F35" stroke-width="2"/>',
        f'<line x1="{fmt(barrel0 + 6)}" y1="{fmt(-r + 6)}" x2="{fmt(barrel0 + barrel_len - 8)}" y2="{fmt(-r + 6)}" stroke="#FFFFFF" stroke-width="3" stroke-opacity="0.8" stroke-linecap="round"/>',
        # finger flange
        f'<rect x="{fmt(barrel0 - 6)}" y="{fmt(-r - 14)}" width="9" height="{fmt(2 * r + 28)}" rx="4" fill="url(#plastic)" stroke="#9AA3AB" stroke-width="1.5"/>',
        # luer tip and hub
        f'<rect x="{fmt(tip0)}" y="-5" width="16" height="10" rx="2" fill="url(#barrel)" stroke="#A7B0B8" stroke-width="1.5"/>',
        f'<path d="M{fmt(hub0)},-9 H{fmt(hub0 + 16)} L{fmt(hub0 + 24)},-3 V3 L{fmt(hub0 + 16)},9 H{fmt(hub0)} Z" fill="url(#hub)" stroke="#9AA3AB" stroke-width="1.5"/>',
        # needle shaft
        f'<rect x="{fmt(-shaft)}" y="-1.8" width="{fmt(shaft)}" height="3.6" fill="url(#steel)"/>',
    ]
    return (f'<g id="syringe" transform="translate({fmt(ex)} {fmt(ey)})">{shadow}{"".join(parts)}</g>'
            f'<line id="needle" x1="{fmt(ex - shaft)}" y1="{fmt(ey)}" x2="{fmt(ex)}" y2="{fmt(ey)}" stroke="#000" stroke-opacity="0" stroke-width="4"/>'
            f'<circle id="needle-entry" cx="{fmt(ex)}" cy="{fmt(ey)}" r="3" fill="#8E5446" fill-opacity="0.8"/>')


def ellipse_px(el_id, centre, r, debug):
    p = b(centre)
    return (f'<ellipse id="{el_id}" cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(r[0] * BASE_SCALE)}" ry="{fmt(r[1] * BASE_SCALE)}" '
            f'fill="#ff00ff" opacity="{0.35 if debug else 0}"/>')


def build() -> str:
    debug = os.environ.get("DEBUG") == "1"
    skin = path(foot_outline(), closed=True, tension=0.5)
    sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
    lm, mm = b(LAT_MALLEOLUS_PX), b(MED_MALLEOLUS_PX)
    hidden = 0.35 if debug else 0

    labels = [
        Label(["Lateral", "malleolus"], anchor=(150, 190), leader=[(330, 230), (lm[0] - 6, lm[1] - 6)], target_id="lat-malleolus"),
        Label(["Medial", "malleolus"], anchor=(1250, 200), leader=[(1240, 245), (mm[0] + 5, mm[1])], target_id="med-malleolus"),
        Label(["Dorsalis pedis"], anchor=(1150, 900), leader=[(1140, 880), c((15, 92))], target_id="artery-course", emphasis=True),
    ]

    body = f"""
<mask id="skin-visible" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="1200">
  <rect width="1600" height="1200" fill="#fff"/><polygon points="{based(PROBE_OUTLINE)}" fill="#000"/></mask>
<g id="anatomy" data-base-sha256="{sha}">
  <image href="{BASE.name}" x="0" y="{fmt(BASE_Y0)}" width="1600" height="{fmt(BASE_SIZE[1] * BASE_SCALE)}" preserveAspectRatio="none"/>
  <g id="layout" opacity="{hidden}">
    <path id="skin" d="{skin}" fill="#ff00ff"/>
  </g>
  <g id="traced">
    <polygon id="probe" points="{based(PROBE_FACE)}" fill="#ff00ff" opacity="{hidden}"/>
    <polygon id="probe-cover" points="{based(PROBE_OUTLINE)}" fill="#00ffff" opacity="{hidden * 0.6}"/>
    {ellipse_px("lat-malleolus", LAT_MALLEOLUS_PX, LAT_MALLEOLUS_R, debug)}
    {ellipse_px("med-malleolus", MED_MALLEOLUS_PX, MED_MALLEOLUS_R, debug)}
  </g>
</g>

<g class="marking" fill="none" mask="url(#skin-visible)">
  <path id="artery-course" d="{path(ARTERY)}" stroke="#C8322B" stroke-width="7" stroke-dasharray="16 11"/>
</g>
<g class="marking">{needle_and_syringe()}</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS, extra_style=".plate-bg { fill: #C9D3DC; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
