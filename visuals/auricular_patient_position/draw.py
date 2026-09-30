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


def arrowhead(ps, t=0.6, size=46.0):
    import math
    a, m, b = (canvas(p) for p in ps)
    def at(u):  # quadratic through a, m, b (m at u=0.5)
        c = (2 * m[0] - (a[0] + b[0]) / 2, 2 * m[1] - (a[1] + b[1]) / 2)
        return ((1 - u) ** 2 * a[0] + 2 * u * (1 - u) * c[0] + u * u * b[0],
                (1 - u) ** 2 * a[1] + 2 * u * (1 - u) * c[1] + u * u * b[1])
    (x0, y0), (x1, y1) = at(t - 0.03), at(t + 0.03)
    ang = math.atan2(y1 - y0, x1 - x0)
    tip = (x1 + math.cos(ang) * size * 0.5, y1 + math.sin(ang) * size * 0.5)
    l = (tip[0] - size * math.cos(ang - 0.45), tip[1] - size * math.sin(ang - 0.45))
    r = (tip[0] - size * math.cos(ang + 0.45), tip[1] - size * math.sin(ang + 0.45))
    return (f'<polygon class="arrow" points="{pts([tip, l, r])}" fill="#0E8C98" stroke="#FFFFFF" '
            f'stroke-width="3" stroke-linejoin="round"/>')


def second_leader(label_svg, points):
    """Give a label a second leader (one name, two identical sites)."""
    extra = (f'<polyline class="leader-halo" points="{pts(points)}"/><polyline class="leader leader-2" points="{pts(points)}"/>'
             f'<circle class="leader-dot" cx="{fmt(points[-1][0])}" cy="{fmt(points[-1][1])}" r="7"/>')
    return label_svg.replace("<text", extra + "<text", 1)


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
    # Direction of injection: an arrowhead on each track, pointing away from its puncture
    # toward the meeting point, placed about 60% of the way along.
    arrows = "".join(arrowhead(ps) for ps in TRACKS.values())
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
  {tracks}{arrows}{sites}
</g>

<g id="labels">{second_leader(labels[0].svg(), [(1440, 122), (1500, 122), (1500, 880), canvas((624, 652))])}{"".join(label.svg() for label in labels[1:])}</g>
"""
    return document(body, extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
