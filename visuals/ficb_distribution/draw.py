"""Fascia iliaca block - expected distribution, skeleton and body side by side (layout).

The shared base for every distribution plate: two gender-neutral adult
figures in the anatomical position, seen from the front (the patient's right
on the image left): on the left a skeleton, on the right a smooth grey
mannequin-like body. Owner, 2026-10-15: a first tile for each nerve block
showing the expected anaesthetic distribution, the skeleton for the bones
and joints, the body for the skin, in one pleasant highlight colour, premium
rather than bolted on; grey silhouette skin. Concept after NYSORA's block
distribution figures (concept only, not committed).

This file draws the layout for the base painting. Once the painting exists,
the distribution is code-drawn over it: a soft, feathered tint clipped to the
traced bones and body.

Canvas px; figure height 1080 px (heel to vertex), about 8 head heights.

Run: python3 visuals/ficb_distribution/draw.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from visuals_lib import document, fmt, smooth_path  # noqa: E402

ASSET_ID = "ficb_distribution"
BASE = Path(__file__).with_name("base.jpg")
BASE_SIZE = (1200.0, 896.0)
SK_X, BODY_X = 470.0, 1130.0       # figure midlines


def mirror(points, cx):
    return [(2 * cx - x, y) for x, y in reversed(points)]


def body_outline(cx):
    """Right half (image left) from the vertex down, mirrored for the other half."""
    half = [(cx, 60), (cx - 44, 72), (cx - 56, 120), (cx - 50, 172), (cx - 34, 200), (cx - 28, 232),
            (cx - 70, 250), (cx - 118, 262), (cx - 138, 290), (cx - 146, 340), (cx - 154, 420),
            (cx - 166, 500), (cx - 178, 580), (cx - 190, 640), (cx - 198, 700), (cx - 186, 742),
            (cx - 168, 722), (cx - 158, 650), (cx - 140, 560), (cx - 128, 470), (cx - 114, 380),
            (cx - 104, 350), (cx - 96, 420), (cx - 100, 500), (cx - 110, 560), (cx - 108, 640),
            (cx - 98, 760), (cx - 84, 860), (cx - 80, 900), (cx - 74, 1000), (cx - 62, 1090),
            (cx - 70, 1124), (cx - 66, 1140), (cx - 16, 1140), (cx - 22, 1100), (cx - 24, 1000),
            (cx - 26, 900), (cx - 22, 760), (cx - 10, 640), (cx, 625)]
    return half + mirror(half[1:-1], cx)


def bone(a, b, w, attrs, el_id=""):
    idattr = f' id="{el_id}"' if el_id else ""
    return (f'<line{idattr} x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(b[0])}" y2="{fmt(b[1])}" '
            f'stroke-width="{fmt(w)}" stroke-linecap="round" {attrs}/>')


def skeleton(cx):
    B = 'stroke="#E9E1CF"'
    out = []
    # skull and mandible
    out.append(f'<ellipse id="skull" cx="{cx}" cy="128" rx="54" ry="66" fill="#EFE8D8" stroke="#BDB29A" stroke-width="3"/>')
    out.append(f'<path d="M{cx - 36},170 Q{cx},214 {cx + 36},170" fill="#EFE8D8" stroke="#BDB29A" stroke-width="3"/>')
    # spine
    out.append(bone((cx, 200), (cx, 620), 18, B, "spine"))
    # clavicles
    out.append(bone((cx - 12, 252), (cx - 118, 246), 12, B, "clavicle-r"))
    out.append(bone((cx + 12, 252), (cx + 118, 246), 12, B, "clavicle-l"))
    # rib cage
    for i, y in enumerate(range(280, 470, 26)):
        w = 104 - abs(i - 3) * 6 - (i > 5) * 10
        out.append(f'<path d="M{cx},{y} C{cx - w},{y - 10} {cx - w - 6},{y + 30} {cx - w + 14},{y + 44}" fill="none" stroke="#E9E1CF" stroke-width="9"/>')
        out.append(f'<path d="M{cx},{y} C{cx + w},{y - 10} {cx + w + 6},{y + 30} {cx + w - 14},{y + 44}" fill="none" stroke="#E9E1CF" stroke-width="9"/>')
    out.append(bone((cx, 272), (cx, 420), 22, B, "sternum"))
    # pelvis
    out.append(f'<path id="pelvis" d="M{cx - 20},540 C{cx - 60},520 {cx - 112},520 {cx - 118},560 C{cx - 112},600 {cx - 80},622 '
               f'{cx - 40},640 L{cx},632 L{cx + 40},640 C{cx + 80},622 {cx + 112},600 {cx + 118},560 '
               f'C{cx + 112},520 {cx + 60},520 {cx + 20},540 Z" fill="#EFE8D8" stroke="#BDB29A" stroke-width="3"/>')
    for s in (-1, 1):
        side = "r" if s < 0 else "l"
        hip, knee, ankle = (cx + s * 72, 600), (cx + s * 60, 880), (cx + s * 50, 1100)
        out.append(f'<circle id="femoral-head-{side}" cx="{fmt(hip[0])}" cy="{fmt(hip[1])}" r="20" fill="#EFE8D8" stroke="#BDB29A" stroke-width="3"/>')
        out.append(bone((cx + s * 92, 612), knee, 22, B, f"femur-{side}"))
        out.append(f'<ellipse id="patella-{side}" cx="{fmt(knee[0])}" cy="{fmt(knee[1] - 6)}" rx="16" ry="20" fill="#EFE8D8" stroke="#BDB29A" stroke-width="3"/>')
        out.append(bone((knee[0] - s * 6, knee[1] + 22), (ankle[0] - s * 6, ankle[1]), 18, B, f"tibia-{side}"))
        out.append(bone((knee[0] + s * 18, knee[1] + 30), (ankle[0] + s * 16, ankle[1] + 4), 9, B, f"fibula-{side}"))
        out.append(f'<path id="foot-{side}" d="M{fmt(ankle[0] - 22)},{ankle[1] + 6} L{fmt(ankle[0] + 22)},{ankle[1] + 6} '
                   f'L{fmt(ankle[0] + s * 8 + 26)},1138 L{fmt(ankle[0] + s * 8 - 26)},1138 Z" fill="#EFE8D8" stroke="#BDB29A" stroke-width="3"/>')
        sh, el, wr = (cx + s * 128, 262), (cx + s * 150, 470), (cx + s * 172, 620)
        out.append(f'<circle cx="{fmt(sh[0])}" cy="{fmt(sh[1])}" r="18" fill="#EFE8D8" stroke="#BDB29A" stroke-width="3"/>')
        out.append(bone(sh, el, 18, B, f"humerus-{side}"))
        out.append(bone((el[0] - s * 8, el[1]), (wr[0] - s * 8, wr[1]), 10, B, f"ulna-{side}"))
        out.append(bone((el[0] + s * 8, el[1]), (wr[0] + s * 8, wr[1]), 10, B, f"radius-{side}"))
        out.append(f'<path id="hand-{side}" d="M{fmt(wr[0] - 18)},{wr[1] + 6} L{fmt(wr[0] + 18)},{wr[1] + 6} '
                   f'L{fmt(wr[0] + s * 4 + 16)},{wr[1] + 120} L{fmt(wr[0] + s * 4 - 16)},{wr[1] + 120} Z" fill="#EFE8D8" stroke="#BDB29A" stroke-width="3"/>')
    return "\n  ".join(out)


MASK_Y = (1200 - 896 * 1600 / 1200) / 2


def defs() -> str:
    return f"""
<filter id="feather" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="feather-bone" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.5"/></filter>
<clipPath id="c-right-leg"><path d="{smooth_path(RIGHT_LEG, closed=True, tension=0.2)}"/></clipPath>
<linearGradient id="lig-fade" gradientUnits="userSpaceOnUse" x1="1083" y1="582" x2="1050" y2="626"><stop offset="0" stop-color="#000"/>
  <stop offset="1" stop-color="#FFF"/></linearGradient>
<mask id="m-lig" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="1200"><rect width="1600" height="1200" fill="url(#lig-fade)"/></mask>
<mask id="m-body" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="1200"><image href="mask_body.png" x="0" y="{MASK_Y:.2f}" width="1600" height="{896 * 1600 / 1200:.2f}" preserveAspectRatio="none"/></mask>
<mask id="m-bone" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="1200"><image href="mask_bone.png" x="0" y="{MASK_Y:.2f}" width="1600" height="{896 * 1600 / 1200:.2f}" preserveAspectRatio="none"/></mask>
<linearGradient id="bg-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7F6F3"/><stop offset="1" stop-color="#ECEAE5"/></linearGradient>
<linearGradient id="body-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9EA3A8"/><stop offset="0.5" stop-color="#C4C8CC"/>
  <stop offset="1" stop-color="#9EA3A8"/></linearGradient>
"""


# Territories, canvas px, traced on the painting (patient's right = image left).
# Polygons may run past the figure: the masks (make_masks.py) clip them to the
# painted bone or skin; only their internal borders matter.
# Audit 2026-10-15: the upper medial thigh stays grey (obturator, genitofemoral,
# ilioinguinal skin), the knee border runs diagonally from the end of the
# lateral femoral cutaneous zone across the patella (lateral knee and upper
# lateral leg are lateral sural cutaneous), and the saphenous strip stops near
# the first MTP joint (the dorsum and the hallux are superficial peroneal).
FEMORAL_SKIN = [(1040, 553), (1072, 572), (1092, 606), (1098, 640), (1101, 680), (1108, 730), (1116, 780), (1117, 840),
                (1119, 905), (1115, 960), (1113, 1040), (1114, 1100), (1118, 1122), (1110, 1132), (1100, 1112),
                (1096, 1090), (1090, 1040), (1088, 965), (1080, 920), (1062, 888), (1044, 862), (1034, 836),
                (1058, 832), (1058, 790), (1055, 700), (1051, 600)]
LFC_SKIN = [(985, 580), (1028, 580), (1040, 582), (1051, 600), (1055, 700), (1058, 790), (1058, 828), (985, 832)]
# The femur only (head, neck, trochanters, shaft, condyles) and the patella:
# traced on 6x zooms of the painting; the pelvis and tibia stay unshaded
# (owner, 2026-10-15: be strict). The femoral head is in, as the femoral
# nerve's articular branches supply the hip joint.
FEMORAL_BONE = [(361, 633), (362, 622), (366, 616), (372, 614), (379, 616), (382, 619), (388, 614), (391, 606),
                (394, 601), (402, 599), (410, 605), (416, 612), (418, 620), (413, 626), (406, 629), (401, 634),
                (399, 648), (399, 662), (402, 690), (410, 730), (420, 770), (430, 810), (434, 832), (442, 851),
                (445, 862), (442, 872), (441, 878), (428, 879), (420, 881), (414, 882), (406, 880), (400, 879),
                (391, 878), (388, 868), (387, 858), (391, 846), (395, 838), (392, 820), (387, 780), (382, 730),
                (377, 690), (370, 660), (364, 645)]
# Saphenous periosteal branches (owner, 2026-10-15: realistic coverage, checked
# against the literature): the anteromedial proximal tibia (femoral branches
# supply the proximal tibia anteriorly; the lateral side and fibula are common
# peroneal) and the medial distal tibia and medial malleolus (saphenous
# branches 3.9-8.2 cm above the malleolus to the periosteum and the medial
# ankle capsule; Lundblad et al. 2013, Local Reg Anesth 6:13, histology of the
# medial malleolar periosteum). The
# mid-shaft is tibial nerve and stays unshaded.
SAPH_BONE_PROX = [(414, 880), (444, 880), (445, 895), (438, 910), (432, 922), (430, 928), (418, 928), (417, 915), (414, 900)]
SAPH_BONE_DIST = [(421, 1045), (432, 1045), (434, 1060), (440, 1075), (443, 1093), (441, 1101), (430, 1100), (424, 1088), (420, 1070)]
# The patient's right leg on the body, between the hanging hand and the other
# leg: the tint never reaches the arm, the trunk or the left leg.
RIGHT_LEG = [(1022, 500), (1129, 500), (1129, 1200), (995, 1200), (1000, 760), (1005, 650), (1015, 600), (1022, 560)]
TONES = {"teal": "#2E9C97", "violet": "#8A78C2", "amber": "#D99A3A", "rose": "#D0707A", "blue": "#4A8FD0"}


def territory(points):
    return smooth_path(points, closed=True, tension=0.35)


def build() -> str:
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

    marks = ""
    if painted:
        marks = f"""
<g class="marking">
  <g clip-path="url(#c-right-leg)" style="mix-blend-mode:multiply"><g mask="url(#m-body)">
    <g mask="url(#m-lig)"><g filter="url(#feather)" fill-opacity="0.58">
      <path id="lfc-skin" d="{territory(LFC_SKIN)}" fill="{TONES['violet']}"/>
      <path id="femoral-skin" d="{territory(FEMORAL_SKIN)}" fill="{TONES['teal']}"/>
    </g></g>
  </g></g>
  <g mask="url(#m-bone)" style="mix-blend-mode:multiply">
    <path id="femoral-bone" d="{smooth_path(FEMORAL_BONE, closed=True, tension=0.3)}" fill="{TONES['teal']}" fill-opacity="0.5"/>
    <g filter="url(#feather-bone)">
      <path id="saphenous-bone-prox" d="{smooth_path(SAPH_BONE_PROX, closed=True, tension=0.3)}" fill="{TONES['teal']}" fill-opacity="0.5"/>
      <path id="saphenous-bone-dist" d="{smooth_path(SAPH_BONE_DIST, closed=True, tension=0.3)}" fill="{TONES['teal']}" fill-opacity="0.5"/>
    </g>
  </g>
</g>"""

    body = f"""
<g id="painting"{base_attr}>{base_image}</g>
<g id="anatomy"{layout_attr}>
  <rect x="0" y="0" width="1600" height="1200" fill="url(#bg-grad)"/>
  <ellipse cx="{SK_X}" cy="1146" rx="150" ry="14" fill="#000" opacity="0.06"/>
  <ellipse cx="{BODY_X}" cy="1146" rx="150" ry="14" fill="#000" opacity="0.06"/>
  <path id="skeleton-outline" d="{smooth_path(body_outline(SK_X), closed=True, tension=0.5)}" fill="none" stroke="#D9D6CF" stroke-width="2" stroke-dasharray="6 8"/>
  {skeleton(SK_X)}
  <path id="body" d="{smooth_path(body_outline(BODY_X), closed=True, tension=0.5)}" fill="url(#body-grad)" stroke="#8C9196" stroke-width="2"/>
</g>
{marks}
"""
    return document(body, defs=defs(), extra_style=".plate-bg { fill: #F4F3EF; }")


def main() -> int:
    out = Path(__file__).with_name(f"{ASSET_ID}.svg")
    out.write_text(build(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
