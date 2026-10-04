"""Superficial cervical plexus block - the right neck in section at mid-SCM under a linear probe (layout).

Transverse section of the right neck at the midpoint of the
sternocleidomastoid, as on the screen with the probe transverse over the
mid-SCM: posterior (lateral) on the image left, anterior (medial) on the
right, skin at the top. The same way round as the interscalene plate.

Owner, 2026-10-04: follow NYSORA's cervical plexus plate (concept only, not
committed; drawn from scratch and mirrored to the house laterality). The
first painting was rejected: muscles cut like separate cylinders with fat
between them, and the nerves not inside an identifiable fascia. Now:
- the deep muscles are packed together in section, separated only by thin
  white fascial septa, with no fat between them;
- the cervical fascia is a distinct white two-layered sheet running under
  the SCM and on past its posterior border over the deep muscles, with a thin
  layer of fat inside it;
- the plexus nerves lie inside that sheet, from under the SCM's posterior
  edge to just beyond it.

Record: the plexus wraps around the posterior border of the SCM at about its
midpoint; the external jugular vein crosses the SCM near this level; the SCM
is the large superficial muscle, with the levator scapulae or scalenes deep
to it. Needle in-plane from posterior to anterior; inject in the fascial
plane immediately deep to the posterior border of the SCM; spread along the
posterior border, separating the fascial layers.

Standard anatomy added (after NYSORA): levator scapulae posteriorly, the
middle scalene and longus capitis deep, the cervical transverse process with
the nerve root in its groove and the vertebral artery and vein deep to it,
the external jugular vein superficial on the SCM.

Millimetres from the skin over the SCM's posterior border (x anterior =
image right, y deep) at 26 px/mm.

Run: python3 visuals/sc_plexus_anatomy/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "sc_plexus_anatomy"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
PX_MM = 26.0
ORIGIN = (760.0, 110.0)
X0, X1 = -29.2, 32.3
L, R = X0 - 3, X1 + 3
HALF = 0.9                                    # half thickness of the fascial sheet


def c(p):
    return (ORIGIN[0] + p[0] * PX_MM, ORIGIN[1] + p[1] * PX_MM)


def path(points, closed=False, tension=1.0):
    return smooth_path([c(p) for p in points], closed=closed, tension=tension)


def band(top, bottom, n=40):
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    return [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]


# Centre line of the cervical fascia: under the SCM (right), rising to its posterior tip, on over the
# deep muscles (left).
PLANE = [(L, 8.4), (-22, 8.4), (-12, 8.6), (-4, 9.2), (2, 10.8), (10, 12.8), (20, 14.2), (R, 14.6)]


def plane_y(x):
    for (x0, y0), (x1, y1) in zip(PLANE, PLANE[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def plane_band(x0, x1, dy0, dy1, n=40):
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    return [(x, plane_y(x) + dy0) for x in xs] + [(x, plane_y(x) + dy1) for x in reversed(xs)]


def under_plane(x0, x1, n=12):
    return [(x0 + (x1 - x0) * i / n, plane_y(x0 + (x1 - x0) * i / n) + HALF) for i in range(n + 1)]


SCM = [(-4, 7.2), (2, 5.0), (10, 4.2), (20, 4.0), (R, 4.0), (R, 13.6), (20, 13.2), (10, 11.8), (2, 9.8)]
LEVATOR = under_plane(L, -10) + [(-11.4, 20), (-12.6, 32), (-11, 44), (L, 44)]
MSM = under_plane(-10, 4) + [(3.4, 20), (1.2, 25.6), (-2, 26.4), (-6, 29), (-12.6, 32), (-11.4, 20)]
LONGUS = under_plane(4, R) + [(R, 44), (17, 44), (15.6, 31), (11.6, 27.4), (7.6, 27.6), (5.4, 22)]
BONE = [(-12, 44), (-8, 30.4), (-4, 26.6), (0, 25.8), (2.2, 28.4), (3.0, 33.2), (5.6, 33.4), (6.4, 28.6), (8.4, 27.2),
        (12.4, 27.4), (15.8, 31), (17.4, 44)]
ROOT = ((4.3, 30.4), 1.5, 2.0)
VERTEBRAL_A = ((5.6, 38.6), 1.7)
VERTEBRAL_V = ((2.4, 38.2), 1.4, 1.9)
EJV = ((14.0, 2.9), 2.6, 1.2)
NERVE_XS = [5.0, -0.6, -8.0, -16.0]
NERVES = [((x, plane_y(x)), 0.72) for x in NERVE_XS]
NEEDLE_ENTRY = (-22.0, 0.0)
NEEDLE_TIP = (-3.4, plane_y(-3.4) - 0.1)


def spread():
    return plane_band(-12.0, 5.6, -1.15, 1.15, n=24)


DEFS = """
<linearGradient id="fat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DC8E"/><stop offset="1" stop-color="#EBC565"/></linearGradient>
<linearGradient id="muscle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9E3A33"/><stop offset="1" stop-color="#6E211D"/></linearGradient>
<radialGradient id="artery" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#E26B61"/><stop offset="1" stop-color="#A82A24"/></radialGradient>
<radialGradient id="vein" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#6F8FC0"/><stop offset="1" stop-color="#34528A"/></radialGradient>
<linearGradient id="probe-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA2AB"/><stop offset="1" stop-color="#6E7780"/></linearGradient>
<clipPath id="frame"><rect x="0" y="0" width="1600" height="1200"/></clipPath>
"""


def ell(el_id, e, attrs):
    p = c(e[0])
    ry = e[2] if len(e) > 2 else e[1]
    id_attr = f'id="{el_id}" ' if el_id else ""
    return f'<ellipse {id_attr}cx="{fmt(p[0])}" cy="{fmt(p[1])}" rx="{fmt(e[1] * PX_MM)}" ry="{fmt(ry * PX_MM)}" {attrs}/>'


def build() -> str:
    e, t = c(NEEDLE_ENTRY), c(NEEDLE_TIP)
    dx, dy = t[0] - e[0], t[1] - e[1]
    a = (e[0] - dx * 0.4, e[1] - dy * 0.4)
    probe_x0 = c((X0 + 10.0, 0))[0]
    M = 'fill="url(#muscle)" stroke="#F4EFE6" stroke-width="5"'
    labels = [
        Label(["Sternocleidomastoid"], anchor=(1010, 300), leader=[(1100, 320), c((18, 8))], target_id="scm"),
        Label(["External jugular vein"], anchor=(470, 215), leader=[(1010, 200), c((12.0, 2.9))], target_id="ejv"),
        Label(["Superficial", "cervical plexus"], anchor=(900, 600), leader=[(920, 550), c(NERVES[1][0])], target_id="plexus",
              emphasis=True),
        Label(["Cervical fascia"], anchor=(40, 470), leader=[(300, 430), c((-20, plane_y(-20) + 0.5))], target_id="cervical-fascia"),
        Label(["Levator scapulae"], anchor=(40, 1080), leader=[(200, 1030), c((-20, 24))], target_id="levator"),
        Label(["Middle scalene"], anchor=(330, 800), leader=[(560, 760), c((-3, 18))], target_id="msm"),
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

    nerves = "".join(ell("plexus" if i == 1 else "", n, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')
                     for i, n in enumerate(NERVES))
    fascia = path(plane_band(L, R, -HALF, HALF, n=60), closed=True, tension=0.2)
    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr} clip-path="url(#frame)">
  <path id="skin" d="{path(band(0, 60), closed=True, tension=0.2)}" fill="#E7BFA7"/>
  <path id="subcutaneous-fat" d="{path(band(1.6, 60), closed=True, tension=0.2)}" fill="url(#fat)"/>
  <path id="deep-compartment" d="{path(under_plane(L, R, n=40) + [(R, 60), (L, 60)], closed=True, tension=0.2)}" fill="url(#muscle)"/>
  <path id="levator" d="{path(LEVATOR, closed=True, tension=0.3)}" {M}/>
  <path id="msm" d="{path(MSM, closed=True, tension=0.3)}" {M}/>
  <path id="longus" d="{path(LONGUS, closed=True, tension=0.3)}" {M}/>
  <path id="bone" d="{path(BONE, closed=True, tension=0.4)}" fill="#EFE6D2" stroke="#A8977A" stroke-width="6"/>
  {ell("root", ROOT, 'fill="#EFCB5A" stroke="#B8962E" stroke-width="4"')}
  {ell("vertebral-vein", VERTEBRAL_V, 'fill="url(#vein)" stroke="#2F4A78" stroke-width="4"')}
  {ell("vertebral-artery", VERTEBRAL_A, 'fill="url(#artery)" stroke="#8E211D" stroke-width="4"')}
  <path id="scm" d="{path(SCM, closed=True, tension=0.5)}" {M}/>
  <path id="cervical-fascia" d="{fascia}" fill="#F3E3B0" stroke="#FFFFFF" stroke-width="6"/>
  {nerves}
  {ell("ejv", EJV, 'fill="url(#vein)" stroke="#2F4A78" stroke-width="4"')}
  <line x1="0" y1="{fmt(ORIGIN[1])}" x2="1600" y2="{fmt(ORIGIN[1])}" stroke="#B98A74" stroke-width="4"/>
</g>

<g class="marking">
  <path id="spread" d="{path(spread(), closed=True, tension=0.6)}" fill="#6CCBD2" fill-opacity="0.5" stroke="#0E8C98" stroke-width="3"/>
  <rect id="probe" x="{fmt(probe_x0)}" y="-60" width="{fmt(1700 - probe_x0)}" height="{fmt(ORIGIN[1] + 60)}" rx="34" fill="url(#probe-grad)" stroke="#4E565E" stroke-width="3"/>
  <rect x="{fmt(probe_x0 + 18)}" y="{fmt(ORIGIN[1] - 16)}" width="{fmt(1700 - probe_x0)}" height="14" rx="6" fill="#3E454C"/>
  <line id="needle" x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="10"/>
  <line x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="5"/>
  <circle id="needle-entry" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>
  <circle id="needle-tip" cx="{fmt(t[0])}" cy="{fmt(t[1])}" r="4" fill="#000" opacity="0"/>
</g>

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
