"""Auricular block - needle entry on the patient, right ear from the side.

Painted base plus code-drawn markings. The art is a Gemini Nano Banana Pro
photo repaint of the flat layout in commit a80ec1b (see provenance.json).
Regions below are hand-traced over the base in base-image pixels; the two
puncture sites, the four subcutaneous tracks and the labels are drawn here so
they are exact. Re-trace everything if the base is replaced.

Seated patient, right side of the head seen from the right: head up, face to
the right. Punctures just below the lobe and just above the ear (record,
steps 2 and 4); tracks run in front of the tragus and behind the ear over the
mastoid and meet, closing a ring round the base of the ear. Base scale is
about 7.5 px/mm (layout 10 px/mm at 1600 wide; the traced ear is ~62 mm tall).

Run: python3 visuals/auricular_patient_position/draw.py   (DEBUG=1 shows the traced regions)
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import HEIGHT, WIDTH, Label, document, fmt, pts, smooth_path  # noqa: E402

ASSET_ID = "auricular_patient_position"
BASE = "base.jpg"
BASE_SIZE = (1200.0, 896.0)
SCALE = WIDTH / BASE_SIZE[0]
OFFSET_Y = (HEIGHT - BASE_SIZE[1] * SCALE) / 2


def canvas(p):
    return (p[0] * SCALE, p[1] * SCALE + OFFSET_Y)


# Traced in base-image pixels.
EAR = [(555, 140), (600, 142), (640, 165), (665, 215), (668, 280), (660, 330), (672, 380), (680, 440),
       (672, 500), (668, 560), (650, 600), (615, 606), (585, 585), (550, 540), (515, 480), (485, 420),
       (460, 350), (452, 280), (465, 210), (510, 160)]
TRAGUS = [(645, 345), (668, 340), (680, 380), (676, 420), (655, 428), (642, 390)]
MASTOID = [(415, 430), (470, 445), (505, 530), (525, 610), (470, 640), (405, 560)]

INFERIOR_SITE = (608, 650)
SUPERIOR_SITE = (570, 100)
ANTERIOR_MEET = (728, 368)
POSTERIOR_MEET = (412, 375)
TRACKS = {
    "track-inf-ant": [INFERIOR_SITE, (700, 540), ANTERIOR_MEET],
    "track-inf-post": [INFERIOR_SITE, (470, 545), POSTERIOR_MEET],
    "track-sup-ant": [SUPERIOR_SITE, (690, 200), ANTERIOR_MEET],
    "track-sup-post": [SUPERIOR_SITE, (440, 190), POSTERIOR_MEET],
}


def build() -> str:
    debug = os.environ.get("DEBUG") == "1"
    region = 'fill="#ff00ff" fill-opacity="0.35"' if debug else 'fill="#000" fill-opacity="0"'
    base_sha = hashlib.sha256(Path(__file__).with_name(BASE).read_bytes()).hexdigest()

    def poly(points):
        return pts([canvas(p) for p in points])

    tracks = "".join(
        f'<path id="{tid}" d="{smooth_path([canvas(p) for p in ps])}" fill="none" stroke="#0E8C98" '
        f'stroke-width="9" stroke-linecap="round" stroke-dasharray="1 16" opacity="0"/>'
        f'<path d="{smooth_path([canvas(p) for p in ps])}" fill="none" stroke="#FFFFFF" stroke-width="12" stroke-linecap="round" opacity="0.55"/>'
        f'<path d="{smooth_path([canvas(p) for p in ps])}" fill="none" stroke="#0E8C98" stroke-width="7" stroke-linecap="round"/>'
        for tid, ps in TRACKS.items())
    sites = "".join(
        f'<circle id="{sid}" cx="{fmt(canvas(p)[0])}" cy="{fmt(canvas(p)[1])}" r="15" fill="#C8322B" stroke="#FFFFFF" stroke-width="4"/>'
        for sid, p in (("site-inferior", INFERIOR_SITE), ("site-superior", SUPERIOR_SITE)))

    labels = [
        Label(["Puncture sites"], anchor=(1040, 110), leader=[(1130, 135), canvas(SUPERIOR_SITE)],
              target_id="site-superior", emphasis=True),
        Label(["Tragus"], anchor=(1180, 560), leader=[(1180, 540), canvas((666, 395))], target_id="tragus"),
        Label(["Mastoid"], anchor=(60, 960), leader=[(250, 915), canvas((460, 540))], target_id="mastoid"),
    ]

    body = f"""
<g id="anatomy" data-base-sha256="{base_sha}">
  <image href="{BASE}" x="0" y="{fmt(OFFSET_Y)}" width="{fmt(WIDTH)}" height="{fmt(BASE_SIZE[1] * SCALE)}" preserveAspectRatio="none"/>
  <polygon id="ear" points="{poly(EAR)}" {region}/>
  <polygon id="tragus" points="{poly(TRAGUS)}" {region}/>
  <polygon id="mastoid" points="{poly(MASTOID)}" {region}/>
  {tracks}{sites}
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
