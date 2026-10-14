# Handoff prompt: Codex agent (procedure images)

Paste everything below the line into a new Codex task or session that has this repo checked out.

---

You are taking over an image-production workflow for **Procedures**, a single-user iOS app. Its one user is the repo owner, an emergency-medicine and critical-care physician. Each procedure record in `Procedures/Resources/procedures.json` has image slots. Your job is to fill the remaining slots with owner-approved images, using the exact pipeline the previous agent (Claude Code) used. Pick up exactly where it stopped.

## Read these first, in this order

1. `AGENTS.md` and `CLAUDE.md`: repo rules. `CLAUDE.md` was written for Claude, but its rules apply to you too.
2. `visuals/STATUS.md`: goal, progress, what is waiting, what is next. Update it whenever a block ships.
3. `visuals/PLAYBOOK.md`: the full workflow, prompt templates, review rules, the house style for nerve-block sections, and traps. Follow it literally.
4. `visuals/README.md`: the tools and the spec check types.
5. One finished example, end to end: `visuals/supraclavicular_anatomy/` and `visuals/supraclavicular_patient_position/`. Each folder holds `draw.py`, `spec.json` with the approval, `provenance.json` with every prompt and repair, and `base.jpg`. This pair is the quality bar the owner liked best. For a photo that needed code compositing, see `visuals/supraorbital_patient_position/`, which has `place_finger.py` and `green_eyes.py`.

## Hard rules

- **Work on `main` and push to `origin/main`. Never open a pull request or push a branch.** `.github/workflows/main-only-policy.yml` closes any PR automatically, and branches have to be deleted by hand. If your environment can only deliver work as a PR, stop and tell the owner. Do not try anyway.
- **Never ship an image the owner has not explicitly approved.** "Approve" or "approve both" in their own words is the only gate. Checks passing is not approval.
- **Never invent clinical claims.** Images show what the record's steps say. If you add standard anatomy the record doesn't state, list it in `spec.json` claims and tell the owner.
- **Do not edit clinical content to make an image or a test fit.** Reviewed edits are final; see `CLAUDE.md`, section Audience.
- **Third-party plates (NYSORA) are concept references only.** Never commit them. Note them in `provenance.json` (`thirdPartyConcept`). Reject any painting that copies their drawing.
- **Run the gate before every push:**
  ```
  python3 scripts/validate_procedures.py
  python3 scripts/check_search_ranking.py
  python3 scripts/check_review_state_sources.py
  python3 -m pytest scripts/tests -q
  ```
  On Windows use `python`. All four must be clean.
- **Commit messages** describe the change. Never include a model name.
- **Query content, don't read it whole:** `python3 scripts/pq.py visuals`, `pq visuals <procedure_id> --full`, `pq show <id> steps equipment troubleshooting`. `procedures.json` is about 146k tokens.

## Environment setup (check this before anything else)

- `scripts/render_visuals.py` renders SVG and runs the checks in headless Chromium through Playwright:
  ```
  pip install playwright pillow numpy
  python -m playwright install chromium
  ```
  If Chromium lives somewhere unusual, set `VISUALS_CHROMIUM` to its binary path.
- Smoke test: `python3 scripts/render_visuals.py supraclavicular_anatomy` must print `112/112 checks pass`. If it doesn't, fix the environment first.

## The pipeline, per image (detail in PLAYBOOK.md)

1. **Pick the slot.** Take the next `empty` slot from `pq.py visuals` that isn't on a skip list (`STATUS.md`). Read the record. Nerve blocks always get two images: `<block>_patient_position` (probe or needle on the patient, painted as a photo) and `<block>_anatomy` (the section or skull under it).
2. **Draw the layout.** Write `visuals/<id>/draw.py` and `spec.json`. Start from the nearest finished plate's layout in git history: `provenance.json` → `reference` names the commit, and `git show <commit>:visuals/<id>/draw.py` recovers it. Rules for the layout:
   - true adult scale in mm, with px/mm stated;
   - flat colour only;
   - every structure Gemini might otherwise invent is drawn;
   - house laterality: the patient's right side, drawn on the image left; sections seen from the feet, lateral on the left;
   - needle in-plane from lateral for ultrasound blocks;
   - code-drawn markings (needle, probe, injectate, rings, dashed lines) get `class="marking"`.
3. **Check, export, push.** Run `python3 scripts/render_visuals.py <id>` until every check passes, and look at `render/<id>.png` yourself. Export the reference with `--reference`. Run the gate, commit, push. Note the commit hash: it goes in `provenance.json` later.
4. **Hand the owner the reference and prompt.** Give the reference PNG with the matching Gemini prompt from PLAYBOOK.md section 3:
   - prompt A for a first paint;
   - prompt B when a NYSORA concept plate is attached;
   - the house-style layer lines for nerve-block sections.

   Each prompt says **new chat or same chat** and **which image to attach**, described by what it shows. The owner asked for both of a block's references at once, numbered "reference 1 of 2" and "reference 2 of 2" to match their prompts.
5. **The owner paints in the Gemini app** and returns the painting. Insist on Gemini's **Download** (full size, 1200×896). A copy from the chat arrives at 512×382 and looks soft.
6. **Review the painting.**
   - Run `python3 scripts/visual_patch.py overlay <id> <painting>` and look at `render/overlay.png`. The painting path is positional.
   - Judge the anatomy against the record and against NYSORA if supplied. Report plainly: what's right, what's wrong, and one fix per item.
   - Repairs are one change per turn (prompt C, same chat) or a crop repaint (`visual_patch.py crop` / `merge`, prompt D).
   - Diff each repair against the previous image. Gemini repairs can delete things they weren't asked to touch; take the lost area back with `crop` and `merge`.
7. **Build the plate on the painting.**
   - Copy it to `visuals/<id>/base.jpg`.
   - Add the painted mode to `draw.py`: a `BASE` path, an `<image>` element, the `data-base-sha256` stamp, and the layout layer hidden. Copy the pattern from `supraclavicular_anatomy/draw.py`.
   - Trace every code-drawn element from the painting's pixels, not the layout.
   - Write `provenance.json` with: base, generator, date, sourceSize, reference commit, the prompt as sent, each repair, rejected attempts, knownLimits, and any thirdPartyConcept.
   - All checks must pass. Commit as a "review draft" and give the owner the rendered `render/<id>.png`.
8. **On "approve":**
   - Run `python3 scripts/render_visuals.py <id> --record-approval --promote`.
   - Set `assetName` and a short `caption` for the slot in `procedures.json`. Edit just those two fields, then re-query with `pq visuals <proc>` to confirm. Keep "ultrasound" out of captions: it shifted the search-ranking test once.
   - Run the gate, commit, push.
9. **Build for the phone.**
   - Trigger `.github/workflows/build-sideload-ipa.yml` on `main`, for example `gh workflow run build-sideload-ipa.yml --ref main`.
   - Wait for it to succeed, then give the owner `https://github.com/Pulpers859/Procedures/releases/download/sideload-<run_number>/Procedures.ipa`.
   - Update `visuals/STATUS.md`.

## Where things stand (2026-10-14, HEAD 34aae86, build sideload-34)

- **Progress:** 57 slots bundled, 32 empty. Twelve of those are on skip lists, which leaves **20 to make**.
- **Waiting on the owner's paintings:** layouts are pushed, references and prompts were sent in an older session. That previous agent does not have those prompts. To resume, re-export with `--reference` and write fresh prompts from PLAYBOOK.md.
  - `sc_plexus_patient_position` (layout `f36ebf5`);
  - `superficial_peroneal_patient_position` and `superficial_peroneal_anatomy` (`ea89b92`);
  - `superior_alveolar_patient_position` and `superior_alveolar_anatomy` (`3818c3f`).
- **Next new block: Sural nerve block.** After it, in order: thoracentesis (`thoracentesis_site`), thoracic ESP, chest tube (`chest_tube_safe_triangle`, `chest_tube_rib_anatomy`), tibial, transgluteal sciatic, TAP, ulnar.

## What the owner has taught us (honour these)

- Nerve blocks always get **both** images. Forgetting the anatomy image annoyed them.
- Needles for ultrasound blocks come **in-plane from lateral**.
- **Teal injectate shows where the full volume ends up**, not just the first bolus. For example, the supraclavicular plate shows the corner-pocket bolus plus the spread around every trunk, and a dashed second needle position for a redirect.
- **Fascia is drawn, never "nerves floating in fat":**
  - nerve bundles sit inside a sheath;
  - fascial planes are white lines;
  - a muscle near the target tapers onto its bone.
  - Muscles must show fibres. Gemini often paints them lumpy, like a gland or liver; repair with the PLAYBOOK line.
- **NYSORA comparison is welcome.** The owner sends screenshots and expects you to compare and say honestly what differs and whether it matters.
- **Photos:** when Gemini won't place a finger or hand, have it removed and composite the photo's own object back in code (`place_finger.py`). Simple recolours, such as eye colour, are done in code (`green_eyes.py`).
- **When asked to audit:** rank findings, separate must-fix from optional, and give each fix as a paste-ready prompt. A second, independent review pass before calling something final caught real issues last time.
- **Communication:** the owner reads on a phone.
  - Keep messages short and plain, one prompt per image, and say which chat and which attachment.
  - Be blunt about limits. Never claim something was done or checked that wasn't.

## Honest limits you will hit

- **You can't use Gemini.** The owner runs it. Your outputs are layouts, prompts, reviews and plates.
- **Viewing images:** if your environment can't show images inline, say so. Tell the owner where the PNG is (repo path, or the GitHub file view after you push), and still review the image yourself with whatever image input you have.
- **Sideload builds** need GitHub Actions dispatch rights (`gh` authenticated). If you lack them, the owner can press "Run workflow" on that workflow in GitHub; then give them the release link.
- **Git hooks:** the `.claude/hooks` guard and `.git/hooks/pre-push` don't run for you. The main-only rule is on your honour, plus the server-side PR closer.
