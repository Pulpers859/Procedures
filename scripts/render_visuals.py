"""Render and check the code-drawn procedure visuals in `visuals/`.

    python3 scripts/render_visuals.py canthotomy_inferior_crus
    python3 scripts/render_visuals.py --all
    python3 scripts/render_visuals.py canthotomy_inferior_crus --record-approval
    python3 scripts/render_visuals.py canthotomy_inferior_crus --promote

For each asset this regenerates the SVG from `draw.py`, renders it in headless
Chromium (light, dark, and at iPhone card width), and checks `spec.json`
against the geometry the browser actually drew: every label's leader ends
inside the structure it names, laterality and relative position hold, and no
text appears that the spec does not list. Output goes to
`visuals/<id>/render/` (gitignored), including `review.png`, a single sheet
meant to be read on a phone.

A passing check means the drawing matches its spec. It does not mean the spec
is clinically right - that is the owner's review, recorded with
`--record-approval` only when they approve. Approval is tied to the SHA-256 of
the SVG, so any later edit voids it, and `--promote` refuses an unapproved or
changed drawing.

Needs: pip install playwright (uses the preinstalled Chromium; set
VISUALS_CHROMIUM to point at another binary).
"""

from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VISUALS = REPO / "visuals"
ASSETS = REPO / "Assets.xcassets"
CARD_WIDTH_PT = 350
CHROMIUM_CANDIDATES = [
    os.environ.get("VISUALS_CHROMIUM", ""),
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
]

CHECK_JS = r"""
(spec) => {
  const svg = document.documentElement;
  const results = [];
  const el = (id) => document.getElementById(id);
  const pass = (name, ok, detail) => results.push({ name, ok: !!ok, detail });
  // Every measurement is in canvas coordinates, so anatomy drawn inside a
  // zoomed group and labels drawn outside it are compared like for like.
  const point = (x, y) => { const p = svg.createSVGPoint(); p.x = x; p.y = y; return p; };
  const toCanvas = (e, x, y) => { const p = point(x, y).matrixTransform(e.getCTM()); return { x: p.x, y: p.y }; };
  const toLocal = (e, x, y) => point(x, y).matrixTransform(e.getCTM().inverse());
  const box = (id) => {
    const e = el(id), b = e.getBBox();
    const c = [toCanvas(e, b.x, b.y), toCanvas(e, b.x + b.width, b.y), toCanvas(e, b.x, b.y + b.height), toCanvas(e, b.x + b.width, b.y + b.height)];
    const xs = c.map((q) => q.x), ys = c.map((q) => q.y);
    return { x: Math.min(...xs), y: Math.min(...ys), width: Math.max(...xs) - Math.min(...xs), height: Math.max(...ys) - Math.min(...ys) };
  };
  const center = (id) => { const b = box(id); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; };
  const inside = (id, x, y) => {
    const target = el(id), p = toLocal(target, x, y);
    if (target.isPointInFill && target.isPointInFill(p)) return true;
    return !!(target.isPointInStroke && target.isPointInStroke(p));
  };
  const localEnds = (e) => {
    if (e.tagName === 'line') {
      return [{ x: e.x1.baseVal.value, y: e.y1.baseVal.value }, { x: e.x2.baseVal.value, y: e.y2.baseVal.value }];
    }
    const len = e.getTotalLength();
    return [e.getPointAtLength(0), e.getPointAtLength(len)];
  };
  const lineEnds = (id) => { const e = el(id); return localEnds(e).map((q) => toCanvas(e, q.x, q.y)); };
  const samples = (id, n) => {
    const e = el(id);
    if (e.tagName === 'line') {
      // At least one sample every 4 px here too: a long needle sampled 41
      // times stepped over a 10 px fascia.
      const [a, b] = lineEnds(id);
      const m = Math.max(n, Math.ceil(Math.hypot(b.x - a.x, b.y - a.y) / 4));
      return Array.from({ length: m + 1 }, (_, i) => ({ x: a.x + (b.x - a.x) * i / m, y: a.y + (b.y - a.y) * i / m }));
    }
    // At least one sample every 4 px, so a long path cannot step over a thin
    // structure (a 1700 px bougie crossing a 16 px membrane).
    const len = e.getTotalLength();
    const m = Math.max(n, Math.ceil(len / 4));
    return Array.from({ length: m + 1 }, (_, i) => { const q = e.getPointAtLength(len * i / m); return toCanvas(e, q.x, q.y); });
  };
  const f = (v) => Math.round(v);

  for (const id of spec.requiredElements || []) {
    pass(`element #${id} exists`, !!el(id), '');
  }
  if (results.some((r) => !r.ok)) return results;

  const labelGroups = Array.from(document.querySelectorAll('g.label'));
  const expected = spec.labels || {};
  const seen = labelGroups.map((g) => g.dataset.label);
  pass('labels are exactly the spec list, once each',
       JSON.stringify([...seen].sort()) === JSON.stringify(Object.keys(expected).sort()),
       `drawn: ${JSON.stringify(seen)}`);
  for (const g of labelGroups) {
    const name = g.dataset.label;
    const target = expected[name];
    const leader = g.querySelector('polyline.leader'), pl = leader.points;
    const last = pl.getItem(pl.numberOfItems - 1), end = toCanvas(leader, last.x, last.y);
    pass(`"${name}" leader lands inside #${target}`,
         target && g.dataset.target === target && inside(target, end.x, end.y),
         `end (${f(end.x)}, ${f(end.y)})`);
    const text = g.querySelector('text'), raw = text.getBBox(), o = toCanvas(text, raw.x, raw.y);
    const tb = { x: o.x, y: o.y, width: raw.width, height: raw.height };
    const m = spec.labelMargin ?? 24;
    pass(`"${name}" text sits inside the frame`,
         tb.x >= m && tb.y >= m && tb.x + tb.width <= 1600 - m && tb.y + tb.height <= 1200 - m,
         `box (${f(tb.x)}, ${f(tb.y)}, ${f(tb.width)}x${f(tb.height)})`);
  }
  const stray = Array.from(document.querySelectorAll('text')).filter((t) => !t.closest('g.label'));
  pass('no text outside the labels', stray.length === 0, stray.map((t) => t.textContent).join(' | '));

  for (const c of spec.geometry || []) {
    let ok = false, detail = '';
    if (c.check === 'leftOf') {
      const a = center(c.a), b = center(c.b);
      ok = a.x < b.x; detail = `${f(a.x)} < ${f(b.x)}`;
    } else if (c.check === 'below') {
      const a = center(c.a), b = center(c.b);
      ok = a.y > b.y; detail = `${f(a.y)} > ${f(b.y)}`;
    } else if (c.check === 'crosses') {
      const hits = samples(c.a, 40).filter((p) => inside(c.b, p.x, p.y)).length;
      ok = hits > 0; detail = `${hits} samples of #${c.a} inside #${c.b}`;
    } else if (c.check === 'endNear') {
      const ends = lineEnds(c.a);
      const p = c.end === 'start' ? ends[0] : ends[1];
      const b = box(c.b);
      const dx = Math.max(b.x - p.x, 0, p.x - (b.x + b.width));
      const dy = Math.max(b.y - p.y, 0, p.y - (b.y + b.height));
      const d = Math.hypot(dx, dy);
      ok = d <= c.maxPx; detail = `${f(d)} px from #${c.b} (max ${c.maxPx})`;
    } else if (c.check === 'pointsDown') {
      const [a, b] = lineEnds(c.a);
      const dy = b.y - a.y, dx = b.x - a.x;
      ok = dy > 0 && Math.abs(dx) <= dy * (c.maxLean ?? 0.36);
      detail = `dx ${f(dx)}, dy ${f(dy)}`;
    } else if (c.check === 'awayFrom') {
      const [a, b] = lineEnds(c.a);
      const t = center(c.b);
      const da = Math.hypot(a.x - t.x, a.y - t.y), db = Math.hypot(b.x - t.x, b.y - t.y);
      ok = db > da; detail = `start ${f(da)} px, end ${f(db)} px from #${c.b}`;
    } else if (c.check === 'lengthRange') {
      const [a, b] = lineEnds(c.a);
      const d = Math.hypot(b.x - a.x, b.y - a.y);
      ok = d >= c.min && d <= c.max; detail = `${f(d)} px (allowed ${c.min}-${c.max})`;
    } else if (c.check === 'pathLengthRange') {
      // Along the path, not end to end: a catheter's in-body length.
      const e = el(c.a), m = e.getCTM(), k = Math.hypot(m.a, m.b);
      const d = e.getTotalLength() * k;
      ok = d >= c.min && d <= c.max; detail = `${f(d)} px along the path (allowed ${c.min}-${c.max})`;
    } else if (c.check === 'noOverlap') {
      const hits = samples(c.a, 40).filter((p) => inside(c.b, p.x, p.y)).length;
      ok = hits === 0; detail = `${hits} samples of #${c.a} inside #${c.b}`;
    } else {
      detail = `unknown check ${c.check}`;
    }
    pass(c.why || `${c.check} ${c.a} ${c.b || ''}`, ok, detail);
  }
  return results;
}
"""


def chromium_path() -> str | None:
    for candidate in CHROMIUM_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_spec(asset_id: str) -> dict:
    return json.loads((VISUALS / asset_id / "spec.json").read_text(encoding="utf-8"))


def regenerate(asset_id: str) -> Path:
    draw = VISUALS / asset_id / "draw.py"
    module_spec = importlib.util.spec_from_file_location(f"draw_{asset_id}", draw)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    text = module.build()
    # A gradient or clip sharing an element's id makes getElementById return
    # the wrong node and the checks die with an opaque browser error.
    ids = re.findall(r'\sid="([^"]+)"', text)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise SystemExit(f"{asset_id}: duplicate element ids {dupes}; rename one of each")
    svg = VISUALS / asset_id / f"{asset_id}.svg"
    svg.write_text(text, encoding="utf-8")
    return svg


def render(asset_id: str, browser) -> tuple[list[dict], Path]:
    spec = load_spec(asset_id)
    svg = regenerate(asset_id)
    out = VISUALS / asset_id / "render"
    out.mkdir(exist_ok=True)

    page = browser.new_page(viewport={"width": 1600, "height": 1200})
    page.goto(svg.as_uri())
    page.evaluate("document.fonts.ready")
    results = page.evaluate(CHECK_JS, spec)
    page.screenshot(path=str(out / f"{asset_id}.png"))
    page.evaluate("document.documentElement.classList.add('dark')")
    page.screenshot(path=str(out / f"{asset_id}-dark.png"))
    page.close()

    phone = browser.new_page(viewport={"width": CARD_WIDTH_PT, "height": round(CARD_WIDTH_PT * 0.75)},
                             device_scale_factor=3)
    phone_html = out / "phone.html"
    phone_html.write_text(f'<body style="margin:0"><img src="{asset_id}.png" '
                          f'style="width:{CARD_WIDTH_PT}px;display:block"></body>', encoding="utf-8")
    phone.goto(phone_html.as_uri())
    phone.screenshot(path=str(out / f"{asset_id}-phone.png"))
    phone.close()

    (out / "check.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    review_sheet(asset_id, spec, results, out, browser, sha256(svg))
    return results, out


def review_sheet(asset_id: str, spec: dict, results: list[dict], out: Path, browser, digest: str) -> None:
    """One tall image to read on a phone: the card at real size, light and
    dark, then the claims to confirm, then the automatic checks."""
    claims = "".join(f"<li>{html.escape(c)}</li>" for c in spec.get("claims", []))
    checks = "".join(
        f'<li class="{"ok" if r["ok"] else "bad"}">{"PASS" if r["ok"] else "FAIL"} &middot; '
        f'{html.escape(r["name"])}<span>{html.escape(str(r.get("detail") or ""))}</span></li>'
        for r in results
    )
    status = spec.get("review", {}).get("status", "draft")
    sheet = out / "review.html"
    sheet.write_text(f"""<!doctype html><html><head><style>
      body {{ margin:0; padding:16px 20px 28px; font:15px/1.4 -apple-system, "Liberation Sans", sans-serif; background:#fff; color:#1c2530; }}
      h1 {{ font-size:19px; margin:0 0 2px; }} h2 {{ font-size:15px; margin:18px 0 6px; }}
      .meta {{ color:#5b6572; font-size:12px; margin-bottom:10px; }}
      img {{ width:350px; display:block; border-radius:10px; margin:6px 0; }}
      .dark {{ background:#16191e; padding:6px; border-radius:12px; width:350px; box-sizing:content-box; margin-left:-6px; }}
      ul {{ padding-left:18px; margin:0; }} li {{ margin:4px 0; }}
      .ok {{ color:#1f7a3a; }} .bad {{ color:#b3261e; font-weight:600; }}
      li span {{ display:block; color:#6b7480; font-size:11px; font-weight:400; }}
    </style></head><body>
      <h1>{html.escape(spec.get("title", asset_id))}</h1>
      <div class="meta">{html.escape(asset_id)} &middot; {html.escape(status)} &middot; svg {digest[:12]}</div>
      <div>{html.escape(spec.get("teachingPoint", ""))}</div>
      <h2>Card size, light</h2><img src="{asset_id}.png">
      <h2>Card size, dark</h2><div class="dark"><img src="{asset_id}-dark.png"></div>
      <h2>Confirm each claim</h2><ul>{claims}</ul>
      <h2>Automatic checks</h2><ul>{checks}</ul>
    </body></html>""", encoding="utf-8")
    page = browser.new_page(viewport={"width": 390, "height": 800}, device_scale_factor=3)
    page.goto(sheet.as_uri())
    page.screenshot(path=str(out / "review.png"), full_page=True)
    page.close()


def reference(asset_id: str, browser, out: Path) -> None:
    """The layout Gemini repaints: the drawing without labels or markings.

    Markings (incisions, needle paths, target highlights) carry class
    "marking" in draw.py. They are drawn again in code over the painted
    base, so they must not be in the painting."""
    svg = VISUALS / asset_id / f"{asset_id}.svg"
    page = browser.new_page(viewport={"width": 1600, "height": 1200})
    page.goto(svg.as_uri())
    page.evaluate("document.fonts.ready")
    page.evaluate("document.querySelectorAll('#labels, .marking').forEach(e => e.style.display = 'none')")
    page.screenshot(path=str(out / f"{asset_id}-reference.png"))
    page.close()
    print(f"{asset_id}: reference for Gemini -> {(out / f'{asset_id}-reference.png').relative_to(REPO)}")


def record_approval(asset_id: str) -> None:
    spec_path = VISUALS / asset_id / "spec.json"
    spec = load_spec(asset_id)
    svg = regenerate(asset_id)
    spec["review"] = {"status": "approved", "sourceSha256": sha256(svg), "reviewedOn": date.today().isoformat()}
    spec_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    print(f"{asset_id}: approval recorded against svg {spec['review']['sourceSha256'][:12]}")


def promote(asset_id: str, out: Path) -> None:
    spec = load_spec(asset_id)
    svg = VISUALS / asset_id / f"{asset_id}.svg"
    review = spec.get("review", {})
    if review.get("status") != "approved":
        raise SystemExit(f"{asset_id}: not approved; refusing to promote")
    if review.get("sourceSha256") != sha256(svg):
        raise SystemExit(f"{asset_id}: drawing changed since approval; re-review before promoting")
    imageset = ASSETS / f"{asset_id}.imageset"
    imageset.mkdir(exist_ok=True)
    shutil.copyfile(out / f"{asset_id}.png", imageset / f"{asset_id}.png")
    shutil.copyfile(out / f"{asset_id}-dark.png", imageset / f"{asset_id}-dark.png")
    contents = {
        "images": [
            {"filename": f"{asset_id}.png", "idiom": "universal"},
            {"appearances": [{"appearance": "luminosity", "value": "dark"}],
             "filename": f"{asset_id}-dark.png", "idiom": "universal"},
        ],
        "info": {"author": "xcode", "version": 1},
    }
    (imageset / "Contents.json").write_text(json.dumps(contents, indent=2) + "\n", encoding="utf-8")
    print(f"{asset_id}: promoted to {imageset.relative_to(REPO)}. "
          f"Set visualAssets.assetName to \"{asset_id}\" and run validate_procedures.py.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("asset_ids", nargs="*")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--record-approval", action="store_true", help="Owner approved: record it against the current SVG.")
    parser.add_argument("--promote", action="store_true", help="Copy an approved render into Assets.xcassets.")
    parser.add_argument("--reference", action="store_true",
                        help="Also write render/<id>-reference.png: no labels and no .marking elements, for Gemini to repaint.")
    args = parser.parse_args()

    ids = sorted(p.name for p in VISUALS.iterdir() if (p / "draw.py").exists()) if args.all else args.asset_ids
    if not ids:
        parser.error("name an asset id or pass --all")

    if args.record_approval:
        for asset_id in ids:
            record_approval(asset_id)

    from playwright.sync_api import sync_playwright

    failed = False
    with sync_playwright() as pw:
        exe = chromium_path()
        browser = pw.chromium.launch(**({"executable_path": exe} if exe else {}))
        for asset_id in ids:
            results, out = render(asset_id, browser)
            if args.reference:
                reference(asset_id, browser, out)
            bad = [r for r in results if not r["ok"]]
            failed |= bool(bad)
            print(f"{asset_id}: {len(results) - len(bad)}/{len(results)} checks pass -> {out.relative_to(REPO)}/review.png")
            for r in bad:
                print(f"  FAIL {r['name']}: {r.get('detail', '')}")
            if args.promote and not bad:
                promote(asset_id, out)
            elif args.promote:
                print(f"{asset_id}: checks failing; not promoted")
        browser.close()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
