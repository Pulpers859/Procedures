"""Digital nerve block - the back of the hand, and the finger base in section.

Two panels, one plate. Left: the back of a right hand, fingers up, so the
thumb is on the left; the operator's view for a dorsal approach. The two red
dots are the entries at the dorsolateral base of the middle finger, at the
level of the webs (record step: "Insert needle at base of digit along
dorsal-lateral aspect"). The dashed line marks the section.

Right: the finger cut at the dashed line, back of the finger at the top and
the thumb side on the left, the same way round as the hand. Around the
proximal phalanx: the extensor mechanism on its back, the flexor tendons in
their sheath on its front, the two volar (proper palmar) digital nerves with
their arteries on the volar-lateral corners, the nerve on the volar side of
the artery, and the two small dorsal digital nerves on the dorsolateral
corners. That is why one dorsolateral entry can reach both branches on its
side (record anatomy): the needle passes down the side of the bone from the
dorsal nerve toward the volar bundle. The teal clouds are the two deposits
on each side, around each nerve; the needle itself ends beside the bundle.

Hand in millimetres from the middle-finger knuckle (x toward the little
finger, y toward the wrist) at 4.5 px/mm; section in millimetres from the
bone centre at 22 px/mm. Adult proportions; finger base about 20 x 17 mm.

Run: python3 visuals/digital_block_landmark/draw.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import Label, document, fmt, smooth_path  # noqa: E402

ASSET_ID = "digital_block_landmark"

HAND_PX_MM, HAND_ORIGIN = 4.5, (380.0, 690.0)
CUT_PX_MM, CUT_ORIGIN = 22.0, (1225.0, 575.0)


def h(p):
    return (HAND_ORIGIN[0] + p[0] * HAND_PX_MM, HAND_ORIGIN[1] + p[1] * HAND_PX_MM)


def s(p):
    return (CUT_ORIGIN[0] + p[0] * CUT_PX_MM, CUT_ORIGIN[1] + p[1] * CUT_PX_MM)


def hpath(points, closed=False, tension=1.0):
    return smooth_path([h(p) for p in points], closed=closed, tension=tension)


def spath(points, closed=False, tension=1.0):
    return smooth_path([s(p) for p in points], closed=closed, tension=tension)


# ---- Hand ------------------------------------------------------------------
# Fingers: knuckle (MCP), tip, width at the web, width near the tip, and the
# distance from the knuckle to the web on each side (dorsal view).
FINGERS = {
    "index":  dict(mcp=(-21, 3), tip=(-27, -80), w0=19.0, w1=15.5, pip=0.52, dip=0.80),
    "middle": dict(mcp=(0, 0), tip=(0, -92), w0=19.5, w1=16.0, pip=0.50, dip=0.79),
    "ring":   dict(mcp=(19, 3), tip=(25, -85), w0=18.0, w1=15.0, pip=0.51, dip=0.80),
    "little": dict(mcp=(35.5, 11), tip=(46, -59), w0=16.0, w1=13.0, pip=0.53, dip=0.81),
}
WEB_Y = {"index-middle": -19.5, "middle-ring": -19.0, "ring-little": -11.5}
CUT_Y = -21.0                     # the section, just distal to the webs


def finger_frame(f):
    (x0, y0), (x1, y1) = f["mcp"], f["tip"]
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length       # along the finger
    nx, ny = -uy, ux                                     # toward the little-finger side
    return (x0, y0), (ux, uy), (nx, ny), length


def finger_at(f, t, side):
    """Point on the finger edge at fraction t of MCP->tip; side +1 ulnar, -1 radial."""
    (x0, y0), (ux, uy), (nx, ny), length = finger_frame(f)
    w = f["w0"] + (f["w1"] - f["w0"]) * max(0.0, (t - 0.2) / 0.8)
    bulge = 0.5 * math.exp(-((t - f["pip"]) / 0.06) ** 2) + 0.35 * math.exp(-((t - f["dip"]) / 0.05) ** 2)
    half = w / 2 + bulge
    cx, cy = x0 + ux * length * t, y0 + uy * length * t
    return (cx + nx * half * side, cy + ny * half * side)


def t_at_y(f, y):
    (x0, y0), (ux, uy), _, length = finger_frame(f)
    return (y - y0) / (uy * length)


def finger_outline(f, t_radial, t_ulnar):
    """Radial edge up from t_radial, round the tip, ulnar edge down to t_ulnar."""
    (x0, y0), (ux, uy), (nx, ny), length = finger_frame(f)
    up = [finger_at(f, t, -1) for t in _steps(t_radial, 0.9)]
    cx, cy = x0 + ux * length * 0.94, y0 + uy * length * 0.94
    r = f["w1"] / 2
    tip = []
    for k in range(1, 8):
        a = math.pi * k / 8
        # from the radial side (-n) over the tip (+u) to the ulnar side (+n)
        dx = -nx * math.cos(a) + ux * math.sin(a) * 1.15
        dy = -ny * math.cos(a) + uy * math.sin(a) * 1.15
        tip.append((cx + dx * r, cy + dy * r))
    down = [finger_at(f, t, +1) for t in _steps(0.9, t_ulnar)]
    return up + tip + down


def _steps(a, b, n=6):
    return [a + (b - a) * i / n for i in range(n + 1)]


def hand_outline():
    fi, fm, fr, fl = (FINGERS[k] for k in ("index", "middle", "ring", "little"))
    pts_ = [(-31, 90), (-35, 76), (-40, 62)]
    # thumb, relaxed and abducted, coming off the radial side of the palm
    pts_ += [(-45, 50), (-55, 34), (-63, 18), (-70, 2), (-75, -12), (-76, -20), (-72, -25), (-66, -23),
             (-60, -14), (-53, -3), (-45, 8), (-37, 16), (-31, 16)]
    pts_ += finger_outline(fi, t_at_y(fi, 8), t_at_y(fi, WEB_Y["index-middle"]))
    pts_ += finger_outline(fm, t_at_y(fm, WEB_Y["index-middle"]), t_at_y(fm, WEB_Y["middle-ring"]))
    pts_ += finger_outline(fr, t_at_y(fr, WEB_Y["middle-ring"]), t_at_y(fr, WEB_Y["ring-little"]))
    pts_ += finger_outline(fl, t_at_y(fl, WEB_Y["ring-little"]), t_at_y(fl, 18))
    pts_ += [(46, 32), (45, 50), (41, 68), (35, 82), (33, 90), (0, 91)]
    return pts_


def nail(f):
    (x0, y0), (ux, uy), (nx, ny), length = finger_frame(f)
    cx, cy = x0 + ux * length * 0.90, y0 + uy * length * 0.90
    angle = math.degrees(math.atan2(uy, ux)) + 90
    c = h((cx, cy))
    return (f'<ellipse cx="{fmt(c[0])}" cy="{fmt(c[1])}" rx="{fmt(f["w1"] * 0.34 * HAND_PX_MM)}" '
            f'ry="{fmt(7.0 * HAND_PX_MM)}" transform="rotate({fmt(angle)} {fmt(c[0])} {fmt(c[1])})"/>')


def knuckle_creases(f):
    out = []
    for t, width in ((f["pip"], 0.55), (f["dip"], 0.45)):
        for dt in (-0.012, 0.012):
            a, b = finger_at(f, t + dt, -1), finger_at(f, t + dt, +1)
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            ca = (mid[0] + (a[0] - mid[0]) * width, mid[1] + (a[1] - mid[1]) * width)
            cb = (mid[0] + (b[0] - mid[0]) * width, mid[1] + (b[1] - mid[1]) * width)
            bend = (mid[0], mid[1] - 1.2)
            out.append(hpath([ca, bend, cb]))
    return out


# ---- Section ---------------------------------------------------------------
SKIN = [(0, -8), (5.8, -7.5), (9.2, -4.8), (10, 0), (9.4, 4.8), (6.8, 8.2), (0, 9.3),
        (-6.8, 8.2), (-9.4, 4.8), (-10, 0), (-9.2, -4.8), (-5.8, -7.5)]
BONE = [(0, -5.3), (3.8, -4.5), (5.6, -1.6), (5.2, 1.6), (3.0, 2.9), (0, 2.5), (-3.0, 2.9), (-5.2, 1.6),
        (-5.6, -1.6), (-3.8, -4.5)]
MARROW = [(x * 0.72, -0.9 + (y + 0.9) * 0.68) for x, y in BONE]
EXTENSOR = [(-5.7, -3.7), (-3.9, -5.7), (0, -6.6), (3.9, -5.7), (5.7, -3.7), (5.0, -3.6), (3.7, -4.9),
            (0, -5.6), (-3.7, -4.9), (-5.0, -3.6)]
SHEATH = ((0, 5.3), 4.4, 2.6)
FDP = ((0, 4.6), 2.6, 1.45)
FDS = ((0, 6.35), 3.3, 1.05)
VOLAR_NERVE, VOLAR_ARTERY = ((5.7, 6.1), 1.05), ((6.6, 4.7), 0.75)
DORSAL_NERVE = ((6.4, -5.2), 0.6)
DORSAL_VEIN = ((3.2, -6.9), 0.5)
# Needle, ulnar side: from outside the skin, in at the dorsolateral corner,
# down the side of the bone to lie dorsolateral to the volar bundle.
NEEDLE_OUT, NEEDLE_ENTRY, NEEDLE_TIP = (12.6, -10.2), (9.35, -4.3), (8.0, 3.2)
DEPOSITS = [((6.9, -4.9), 1.6, 1.4), ((6.8, 5.3), 2.0, 1.9)]


def mirror(p):
    return (-p[0], p[1])


def circle(center, r, px_mm, fn, attrs):
    c = fn(center)
    return f'<circle cx="{fmt(c[0])}" cy="{fmt(c[1])}" r="{fmt(r * px_mm)}" {attrs}/>'


def ellipse(spec_, attrs):
    (cx, cy), rx, ry = spec_
    c = s((cx, cy))
    return f'<ellipse cx="{fmt(c[0])}" cy="{fmt(c[1])}" rx="{fmt(rx * CUT_PX_MM)}" ry="{fmt(ry * CUT_PX_MM)}" {attrs}/>'


DEFS = """
<linearGradient id="skin" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E7C3AD"/><stop offset="0.35" stop-color="#F4DDCD"/>
  <stop offset="0.7" stop-color="#F3DACA"/><stop offset="1" stop-color="#E2BBA4"/></linearGradient>
<radialGradient id="cut-fat" cx="0.5" cy="0.5" r="0.6"><stop offset="0" stop-color="#F6E6B8"/><stop offset="1" stop-color="#EDD59A"/></radialGradient>
<radialGradient id="cut-bone" cx="0.45" cy="0.4" r="0.7"><stop offset="0" stop-color="#F3EBD7"/><stop offset="1" stop-color="#DCCDAA"/></radialGradient>
<filter id="lift" x="-10%" y="-10%" width="120%" height="120%"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#6B4A3C" flood-opacity="0.22"/></filter>
<clipPath id="hand-clip"><path d="{hand}"/></clipPath>
"""


def build() -> str:
    hand = hpath(hand_outline(), closed=True, tension=0.8)

    # Faint extensor tendons on the back of the hand, wrist to each knuckle.
    tendons = "".join(
        f'<path d="{hpath([(x_w, 88), ((x_w + f["mcp"][0]) / 2, 45), f["mcp"]])}"/>'
        for x_w, f in ((-10, FINGERS["index"]), (-2, FINGERS["middle"]), (8, FINGERS["ring"]), (16, FINGERS["little"])))
    knuckles = "".join(
        f'<ellipse cx="{fmt(h(f["mcp"])[0])}" cy="{fmt(h(f["mcp"])[1])}" rx="{fmt(7.5 * HAND_PX_MM)}" ry="{fmt(5 * HAND_PX_MM)}"/>'
        for f in FINGERS.values())
    creases = "".join(f'<path d="{d}"/>' for f in FINGERS.values() for d in knuckle_creases(f))
    nails = "".join(nail(f) for f in FINGERS.values())
    thumb_nail_c = h((-71.5, -17))

    fm = FINGERS["middle"]
    t_cut = t_at_y(fm, CUT_Y)
    cut_r, cut_u = finger_at(fm, t_cut, -1), finger_at(fm, t_cut, +1)
    entry_r = finger_at(fm, t_cut, -1)
    entry_u = finger_at(fm, t_cut, +1)
    inset = 1.6            # dorsolateral: just in from the edge seen from the back
    entry_r, entry_u = (entry_r[0] + inset, entry_r[1]), (entry_u[0] - inset, entry_u[1])
    cut_a, cut_b = h((cut_r[0] - 5, cut_r[1])), h((cut_u[0] + 5, cut_u[1]))

    def side(sign, suffix):
        m = (lambda p: p) if sign > 0 else mirror
        dn, dnr = DORSAL_NERVE
        vn, vnr = VOLAR_NERVE
        va, var = VOLAR_ARTERY
        dv, dvr = DORSAL_VEIN
        return f"""
    {circle(m(dv), dvr, CUT_PX_MM, s, 'fill="#5C7FA8" stroke="#3E5E86" stroke-width="2"')}
    {circle(m(va), var, CUT_PX_MM, s, f'id="volar-artery-{suffix}" fill="#C8322B" stroke="#8E211D" stroke-width="2.5"')}
    {circle(m(vn), vnr, CUT_PX_MM, s, f'id="volar-nerve-{suffix}" fill="#EFCB5A" stroke="#B8962E" stroke-width="3"')}
    {circle(m(dn), dnr, CUT_PX_MM, s, f'id="dorsal-nerve-{suffix}" fill="#EFCB5A" stroke="#B8962E" stroke-width="2.5"')}"""

    def deposits(sign, suffix):
        m = (lambda p: p) if sign > 0 else mirror
        return "".join(
            f'<ellipse id="deposit-{k}-{suffix}" class="marking" cx="{fmt(s(m(c))[0])}" cy="{fmt(s(m(c))[1])}" '
            f'rx="{fmt(rx * CUT_PX_MM)}" ry="{fmt(ry * CUT_PX_MM)}" fill="#0E8C98" fill-opacity="0.3" stroke="#0E8C98" stroke-width="4"/>'
            for k, (c, rx, ry) in zip(("dorsal", "volar"), DEPOSITS))

    def needle(sign, suffix):
        m = (lambda p: p) if sign > 0 else mirror
        a, e, t = s(m(NEEDLE_OUT)), s(m(NEEDLE_ENTRY)), s(m(NEEDLE_TIP))
        return f"""
    <line id="needle-{suffix}" x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#5E6670" stroke-width="10" stroke-linecap="butt"/>
    <line x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(t[0])}" y2="{fmt(t[1])}" stroke="#D9DEE3" stroke-width="5" stroke-linecap="butt"/>
    <circle id="entry-cut-{suffix}" cx="{fmt(e[0])}" cy="{fmt(e[1])}" r="9" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>"""

    labels = [
        Label(["Dorsal", "digital nerve"], anchor=(1190, 150), leader=[(1330, 238), s((6.4, -5.2))],
              target_id="dorsal-nerve-u"),
        Label(["Volar", "digital nerve"], anchor=(1150, 1060), leader=[(1300, 994), s((5.7, 6.2))],
              target_id="volar-nerve-u", emphasis=True),
    ]

    body = f"""
<g id="anatomy">
  <g id="hand-panel">
    <path id="hand" d="{hand}" fill="url(#skin)" stroke="#C9A08A" stroke-width="3" filter="url(#lift)"/>
    <g clip-path="url(#hand-clip)">
      <g fill="#E3B49C" opacity="0.28">{knuckles}</g>
      <g fill="none" stroke="#E9CDB9" stroke-width="{fmt(2.2 * HAND_PX_MM)}" stroke-linecap="round" opacity="0.8">{tendons}</g>
      <g fill="none" stroke="#C49580" stroke-width="3" stroke-linecap="round" opacity="0.75">{creases}</g>
      <g fill="#F3D9D0" stroke="#C99A8B" stroke-width="3">{nails}
        <ellipse cx="{fmt(thumb_nail_c[0])}" cy="{fmt(thumb_nail_c[1])}" rx="{fmt(5.5 * HAND_PX_MM)}" ry="{fmt(7.5 * HAND_PX_MM)}" transform="rotate(-24 {fmt(thumb_nail_c[0])} {fmt(thumb_nail_c[1])})"/>
      </g>
    </g>
    <path id="middle-finger" d="{hpath(finger_outline(fm, t_at_y(fm, 0), t_at_y(fm, 0)), closed=True)}" fill="#000" fill-opacity="0"/>
  </g>

  <g id="section-panel">
    <path id="skin-cut" d="{spath(SKIN, closed=True)}" fill="#E9C2AA" stroke="#B98A74" stroke-width="4" filter="url(#lift)"/>
    <path d="{spath([(x * 0.93, 0.35 + (y - 0.35) * 0.9) for x, y in SKIN], closed=True)}" fill="url(#cut-fat)"/>
    <path id="extensor" d="{spath(EXTENSOR, closed=True, tension=0.6)}" fill="#F5F2E8" stroke="#BDB4A0" stroke-width="2.5"/>
    {ellipse(SHEATH, 'id="flexor-sheath" fill="#F1E9DA" stroke="#B7A98E" stroke-width="3"')}
    {ellipse(FDS, 'fill="#F7F3EA" stroke="#BDB4A0" stroke-width="2.5"')}
    {ellipse(FDP, 'id="flexor-tendons" fill="#F7F3EA" stroke="#BDB4A0" stroke-width="2.5"')}
    <path id="phalanx" d="{spath(BONE, closed=True)}" fill="url(#cut-bone)" stroke="#A8977A" stroke-width="6"/>
    <path d="{spath(MARROW, closed=True)}" fill="#E9D9B4" opacity="0.8"/>
    {deposits(+1, "u")}
    {deposits(-1, "r")}
    {side(+1, "u")}
    {side(-1, "r")}
  </g>

  <g class="marking">
    <line id="section-line" x1="{fmt(cut_a[0])}" y1="{fmt(cut_a[1])}" x2="{fmt(cut_b[0])}" y2="{fmt(cut_b[1])}"
          stroke="#1C2530" stroke-width="4" stroke-dasharray="14 9" stroke-linecap="butt" opacity="0.8"/>
    {"".join(f'<circle id="entry-hand-{k}" cx="{fmt(h(p)[0])}" cy="{fmt(h(p)[1])}" r="10" fill="#D8432A" stroke="#F6F7F9" stroke-width="3"/>'
             for k, p in (("r", entry_r), ("u", entry_u)))}
    {needle(+1, "u")}
    {needle(-1, "r")}
  </g>
</g>

<g id="labels">{"".join(label.svg() for label in labels)}</g>
"""
    return document(body, defs=DEFS.replace("{hand}", hand), extra_style=".plate-bg { fill: #F4F1EA; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
