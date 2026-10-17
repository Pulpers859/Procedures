"""Layouts for the distribution base paintings that are not the full figure.

The front base was painted from `ficb_distribution/draw.py` and the back base
from the front painting. This draws the head-and-neck, hand and foot
layouts, 1200 x 896 base px, flat shapes that only fix where each figure
sits and how big it is; the painting supplies the anatomy, and the masks are
traced from the painting, never from these shapes.

Laterality: always the patient's RIGHT side.
- head: two busts turned three-quarters to the patient's left (face toward
  image right), so the right cheek, right ear and right neck face the viewer.
- hand: palm view (thumb image left), then back-of-hand view (thumb image
  right); the skeleton is the palm view.
- side: head to upper thighs from the patient's right, facing image right,
  the right upper arm raised beside the head with the hand behind it (the
  serratus and chest tube position).
- head_back: two busts seen straight from behind, large, from the crown to
  the upper back (greater occipital block); the patient's right is on the
  image RIGHT.
- foot: top of the foot and sole with the toes up (big toe image right on
  the top view, image left on the sole), skeleton of the top view, and the
  outer side of the foot (toes image right).

Run: python3 visuals/distribution_bases/layouts.py  (writes <view>/layout.png)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import smooth_path  # noqa: E402

HERE = Path(__file__).resolve().parent
W, H = 1200, 896
BONE = 'fill="#EFE8D8" stroke="#BDB29A" stroke-width="2.5"'
SKIN = 'fill="#B9BDC2" stroke="#8C9196" stroke-width="2"'


def doc(body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7F6F3"/>'
            f'<stop offset="1" stop-color="#ECEAE5"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#bg)"/>{body}</svg>')


def path(points, attrs, tension=0.5):
    return f'<path d="{smooth_path(points, closed=True, tension=tension)}" {attrs}/>'


def head() -> str:
    out = []
    for cx, attrs, skel in ((330, BONE, True), (870, SKIN, False)):
        # shoulders and upper chest to the bottom edge
        out.append(path([(cx - 250, 896), (cx - 250, 760), (cx - 200, 690), (cx - 90, 660), (cx - 50, 600),
                         (cx + 60, 600), (cx + 100, 660), (cx + 210, 690), (cx + 250, 760), (cx + 250, 896)],
                        SKIN if not skel else 'fill="none" stroke="#D9D6CF" stroke-width="2" stroke-dasharray="6 8"'))
        if skel:
            out.append(f'<rect x="{cx - 22}" y="470" width="44" height="300" rx="14" {BONE}/>')
            out.append(f'<path d="M{cx - 10},700 Q{cx - 120},680 {cx - 215},705" fill="none" stroke="#E9E1CF" stroke-width="18" stroke-linecap="round"/>')
            out.append(f'<path d="M{cx + 10},700 Q{cx + 120},680 {cx + 215},705" fill="none" stroke="#E9E1CF" stroke-width="18" stroke-linecap="round"/>')
            for y in (770, 820, 865):
                out.append(f'<path d="M{cx},{y - 20} C{cx - 140},{y - 30} {cx - 210},{y} {cx - 230},{y + 30}" fill="none" stroke="#E9E1CF" stroke-width="12"/>')
                out.append(f'<path d="M{cx},{y - 20} C{cx + 140},{y - 30} {cx + 210},{y} {cx + 230},{y + 30}" fill="none" stroke="#E9E1CF" stroke-width="12"/>')
            out.append(f'<rect x="{cx - 16}" y="735" width="32" height="161" rx="10" {BONE}/>')
        else:
            out.append(path([(cx - 55, 640), (cx - 60, 470), (cx + 55, 470), (cx + 60, 640)], SKIN, 0.2))
        # cranium turned three-quarters toward image right: face on the right
        out.append(f'<ellipse cx="{cx - 10}" cy="300" rx="128" ry="160" {attrs}/>')
        out.append(path([(cx + 70, 330), (cx + 118, 340), (cx + 112, 430), (cx + 80, 488), (cx + 20, 512),
                         (cx - 40, 490), (cx - 70, 420)], attrs, 0.5))
        # right ear (or the opening for it) on the image-left side of the head
        ear = 'fill="#8E8A80"' if skel else SKIN
        out.append(f'<ellipse cx="{cx - 88}" cy="{345 if skel else 330}" rx="{16 if skel else 26}" ry="{16 if skel else 46}" {ear}/>')
        # nose
        out.append(f'<path d="M{cx + 70},300 L{cx + 112},380 L{cx + 80},392 Z" {attrs}/>')
        if skel:
            out.append(f'<ellipse cx="{cx + 25}" cy="285" rx="28" ry="24" fill="#8E8A80"/>')
            out.append(f'<ellipse cx="{cx + 92}" cy="285" rx="20" ry="24" fill="#8E8A80"/>')
            out.append(f'<rect x="{cx + 5}" y="420" width="105" height="28" rx="8" fill="#F7F2E6" stroke="#BDB29A"/>')
    return doc("".join(out))


def hand_outline(cx, thumb_side):
    s = -1 if thumb_side == "left" else 1     # thumb toward image left (palm view) or right (back view)
    pts = [(cx - 70, 896), (cx - 72, 640), (cx - 92, 540), (cx - 98, 420),
           (cx - 92, 250), (cx - 78, 245), (cx - 66, 410),
           (cx - 50, 180), (cx - 30, 175), (cx - 20, 395),
           (cx - 6, 130), (cx + 16, 128), (cx + 26, 395),
           (cx + 40, 160), (cx + 60, 165), (cx + 66, 410),
           (cx + 78, 520), (cx + 120, 450), (cx + 150, 380), (cx + 168, 390), (cx + 140, 500), (cx + 96, 600),
           (cx + 72, 650), (cx + 70, 896)]
    # Built with the thumb on image right; flip it for the palm view.
    return pts if s > 0 else [(2 * cx - x, y) for x, y in pts]


def hand() -> str:
    out = []
    # skeleton: palm view, thumb image left
    cx = 230
    out.append(path(hand_outline(cx, "left"), 'fill="none" stroke="#D9D6CF" stroke-width="2" stroke-dasharray="6 8"', 0.3))
    out.append(f'<rect x="{cx - 52}" y="600" width="26" height="296" rx="10" {BONE}/>')
    out.append(f'<rect x="{cx + 22}" y="600" width="34" height="296" rx="10" {BONE}/>')
    out.append(f'<ellipse cx="{cx}" cy="560" rx="70" ry="38" {BONE}/>')
    for i, (x, top) in enumerate([(cx + 48, 180), (cx + 18, 140), (cx - 14, 132), (cx - 46, 170)]):
        out.append(f'<line x1="{x}" y1="520" x2="{x}" y2="{top}" stroke="#E9E1CF" stroke-width="16" stroke-linecap="round"/>')
    out.append(f'<line x1="{cx - 60}" y1="530" x2="{cx - 140}" y2="390" stroke="#E9E1CF" stroke-width="18" stroke-linecap="round"/>')
    # skin: palm view and back-of-hand view
    out.append(path(hand_outline(600, "left"), SKIN, 0.3))
    out.append(path(hand_outline(960, "right"), SKIN, 0.3))
    for x in (600, 960, 230):
        out.append(f'<ellipse cx="{x}" cy="880" rx="110" ry="10" fill="#000" opacity="0.05"/>')
    return doc("".join(out))


def foot_top(cx, big_toe_right=True):
    pts = [(cx - 50, 140), (cx + 50, 140), (cx + 60, 300), (cx + 95, 520), (cx + 110, 660), (cx + 108, 740),
           (cx + 70, 790), (cx + 30, 800), (cx - 10, 790), (cx - 45, 780), (cx - 80, 760), (cx - 105, 700),
           (cx - 100, 600), (cx - 80, 430), (cx - 60, 300)]
    # toes point down the image? No: toes up. Flip vertically about the foot centre.
    pts = [(x, 940 - y) for x, y in pts]
    return pts if big_toe_right else [(2 * cx - x, y) for x, y in pts]


def foot() -> str:
    out = []
    # top-of-foot skeleton, skin top, skin sole; toes up
    cx = 170
    out.append(path(foot_top(cx), 'fill="none" stroke="#D9D6CF" stroke-width="2" stroke-dasharray="6 8"', 0.4))
    out.append(f'<ellipse cx="{cx}" cy="700" rx="48" ry="90" {BONE}/>')     # heel bone
    out.append(f'<ellipse cx="{cx + 5}" cy="560" rx="75" ry="55" {BONE}/>')  # tarsals
    for i, x in enumerate((cx + 70, cx + 36, cx + 6, cx - 24, cx - 54)):
        out.append(f'<line x1="{x * 0.6 + cx * 0.4}" y1="520" x2="{x}" y2="{170 + i * 18}" stroke="#E9E1CF" stroke-width="{24 if i == 0 else 15}" stroke-linecap="round"/>')
    out.append(path(foot_top(440), SKIN, 0.4))
    out.append(path(foot_top(710, big_toe_right=False), SKIN, 0.4))
    # outer side of the foot, toes to image right, with the lower leg
    lat = [(860, 150), (960, 150), (965, 520), (985, 600), (1060, 640), (1150, 680), (1180, 720), (1170, 760),
           (1080, 775), (960, 780), (880, 770), (850, 730), (848, 640), (858, 520)]
    out.append(path(lat, SKIN, 0.4))
    for x in (170, 440, 710, 1010):
        out.append(f'<ellipse cx="{x}" cy="{872}" rx="110" ry="9" fill="#000" opacity="0.05"/>')
    return doc("".join(out))


def side_torso(cx):
    """Head to upper thighs seen from the right, facing image right."""
    return [(cx + 20, 30), (cx + 70, 50), (cx + 92, 100), (cx + 100, 140), (cx + 88, 172), (cx + 70, 190),
            (cx + 60, 220), (cx + 66, 250), (cx + 110, 300), (cx + 132, 360), (cx + 128, 430), (cx + 104, 470),
            (cx + 100, 530), (cx + 112, 600), (cx + 116, 680), (cx + 100, 740), (cx + 96, 800), (cx + 92, 896),
            (cx - 70, 896), (cx - 80, 800), (cx - 110, 740), (cx - 116, 680), (cx - 92, 600), (cx - 76, 530),
            (cx - 86, 450), (cx - 104, 360), (cx - 100, 290), (cx - 70, 230), (cx - 46, 200),
            (cx - 50, 150), (cx - 40, 80), (cx - 14, 40)]


def side_arm(cx):
    """Right upper arm raised beside the head, the hand behind the head."""
    return [(cx - 70, 300), (cx - 92, 230), (cx - 96, 150), (cx - 84, 60), (cx - 66, 26), (cx - 30, 22),
            (cx - 16, 50), (cx - 30, 110), (cx - 40, 190), (cx - 6, 300)]


def side() -> str:
    out = []
    sk, bd = 330, 870
    out.append(path(side_torso(sk), 'fill="none" stroke="#D9D6CF" stroke-width="2" stroke-dasharray="6 8"', 0.5))
    out.append(f'<ellipse cx="{sk + 24}" cy="112" rx="70" ry="76" {BONE}/>')
    out.append(f'<path d="M{sk - 20},190 C{sk - 40},300 {sk - 60},420 {sk - 50},520 C{sk - 44},580 {sk - 56},640 {sk - 70},680" '
               f'fill="none" stroke="#E9E1CF" stroke-width="20" stroke-linecap="round"/>')
    for y in range(270, 520, 30):
        out.append(f'<path d="M{sk - 40},{y} C{sk + 20},{y - 6} {sk + 100},{y + 20} {sk + 110},{y + 70}" fill="none" stroke="#E9E1CF" stroke-width="10"/>')
    out.append(path([(sk - 90, 620), (sk + 40, 600), (sk + 90, 680), (sk + 40, 760), (sk - 60, 740)], BONE, 0.5))
    out.append(f'<line x1="{sk}" y1="730" x2="{sk + 10}" y2="896" stroke="#E9E1CF" stroke-width="26" stroke-linecap="round"/>')
    out.append(f'<line x1="{sk - 50}" y1="270" x2="{sk - 70}" y2="50" stroke="#E9E1CF" stroke-width="20" stroke-linecap="round"/>')
    out.append(path([(sk - 90, 230), (sk - 30, 220), (sk - 30, 380), (sk - 80, 360)], BONE, 0.3))   # scapula
    out.append(path(side_torso(bd), SKIN, 0.5))
    out.append(path(side_arm(bd), SKIN, 0.4))
    return doc("".join(out))


def head_back() -> str:
    """Two large busts from behind: skull and cervical spine, then the head."""
    out = []
    for cx, skel in ((320, True), (880, False)):
        # Upper back and shoulders to the bottom edge.
        shoulders = [(cx - 270, 896), (cx - 270, 800), (cx - 220, 740), (cx - 110, 712), (cx - 70, 640),
                     (cx + 70, 640), (cx + 110, 712), (cx + 220, 740), (cx + 270, 800), (cx + 270, 896)]
        if skel:
            out.append(path(shoulders, 'fill="none" stroke="#D9D6CF" stroke-width="2" stroke-dasharray="6 8"'))
            # cranium from behind with the occipital bone, mastoids, spine
            out.append(f'<ellipse cx="{cx}" cy="330" rx="190" ry="230" {BONE}/>')
            out.append(f'<ellipse cx="{cx - 150}" cy="520" rx="28" ry="46" {BONE}/>')   # right mastoid (image left)
            out.append(f'<ellipse cx="{cx + 150}" cy="520" rx="28" ry="46" {BONE}/>')
            out.append(f'<path d="M{cx - 160},470 Q{cx},430 {cx + 160},470" fill="none" stroke="#BDB29A" stroke-width="3"/>')  # nuchal line
            out.append(f'<circle cx="{cx}" cy="452" r="12" {BONE}/>')   # external occipital protuberance
            out.append(f'<rect x="{cx - 26}" y="540" width="52" height="300" rx="16" {BONE}/>')
            for y in (590, 640, 690, 740, 790):
                out.append(f'<line x1="{cx - 60}" y1="{y}" x2="{cx + 60}" y2="{y}" stroke="#E9E1CF" stroke-width="12" stroke-linecap="round"/>')
            out.append(f'<path d="M{cx - 30},760 Q{cx - 160},740 {cx - 250},780" fill="none" stroke="#E9E1CF" stroke-width="16"/>')
            out.append(f'<path d="M{cx + 30},760 Q{cx + 160},740 {cx + 250},780" fill="none" stroke="#E9E1CF" stroke-width="16"/>')
        else:
            out.append(path(shoulders, SKIN))
            out.append(path([(cx - 80, 700), (cx - 95, 520), (cx + 95, 520), (cx + 80, 700)], SKIN, 0.2))   # neck
            out.append(f'<ellipse cx="{cx}" cy="330" rx="190" ry="230" {SKIN}/>')
            out.append(f'<ellipse cx="{cx - 192}" cy="380" rx="20" ry="52" {SKIN}/>')   # ears from behind
            out.append(f'<ellipse cx="{cx + 192}" cy="380" rx="20" ry="52" {SKIN}/>')
    return doc("".join(out))


def main() -> int:
    from playwright.sync_api import sync_playwright
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    from render_visuals import chromium_path
    with sync_playwright() as pw:
        exe = chromium_path()
        browser = pw.chromium.launch(**({"executable_path": exe} if exe else {}))
        for view, fn in (("head", head), ("hand", hand), ("foot", foot), ("side", side), ("head_back", head_back)):
            svg = HERE / view / "layout.svg"
            svg.write_text(fn(), encoding="utf-8")
            page = browser.new_page(viewport={"width": W, "height": H})
            page.goto(svg.as_uri())
            page.screenshot(path=str(HERE / view / "layout.png"))
            page.close()
            print(HERE / view / "layout.png")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
