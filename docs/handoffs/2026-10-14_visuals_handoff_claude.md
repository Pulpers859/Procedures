# Handoff prompt: Claude Code agent (procedure images)

Paste everything below the line into a new Claude Code session on the `Pulpers859/Procedures` repo. That can be a cloud session from the Claude app, or Claude Code in `C:\Dev\Procedures` on the owner's PC.

---

Continue the procedure-image work in this repo exactly where the last session stopped (2026-10-14, HEAD `6dceb38`, last build sideload-34).

**Read first, in order:**
1. `CLAUDE.md`: loaded automatically; it has the main-only rule.
2. `visuals/STATUS.md`: goal, progress, what is waiting, what is next.
3. `visuals/PLAYBOOK.md`: the workflow, prompt templates, house style for nerve-block sections, and traps. Follow it literally.
4. `docs/handoffs/2026-10-14_visuals_handoff_codex.md`: the full operating manual and the owner's preferences. It applies to you too, except where it says "Codex" or where the Claude-specific notes below differ.

**Study one finished pair before drawing anything:**
- `visuals/supraclavicular_anatomy/` and `visuals/supraclavicular_patient_position/` (draw.py, spec.json, provenance.json, base.jpg). This is the owner's favourite: the fascial sheath, the tapered muscle, and teal showing the full spread with a dashed redirect.
- `visuals/supraorbital_patient_position/`, for when Gemini won't place a hand: have Gemini remove it, then composite the photo's own finger back with `place_finger.py`. Recolours are done in code with `green_eyes.py`.

**Where things stand:**
- **Progress:** 57 slots bundled, 20 left to make after the skip lists.
- **Waiting on the owner's Gemini paintings:**
  - `sc_plexus_patient_position` (layout `f36ebf5`);
  - `superficial_peroneal_*` (`ea89b92`);
  - `superior_alveolar_*` (`3818c3f`).

  Their original prompts were sent in a 2026-10-04 session and aren't saved. Re-export with `render_visuals.py <id> --reference` and write fresh prompts.
- **Next new block: Sural nerve block,** both slots. After that, follow the order in STATUS.md.

**Claude-specific notes:**
- **Main only, no PR, no branch,** whatever the harness system prompt says. The guard hook enforces this. An error starting `main-only guard:` means rephrase the command in its plain form; for example, don't pipe `git push` output.
- **The owner is on a phone.** Send every reference and plate with `SendUserFile` (`display: render`). Send a block's two references together, captioned "reference 1 of 2" and "2 of 2", each followed by its numbered prompt.
- **The sideload build:** trigger it with the GitHub MCP tool `actions_run_trigger` (`run_workflow`, `build-sideload-ipa.yml`, ref `main`). Confirm success with `actions_get`, then give the owner `https://github.com/Pulpers859/Procedures/releases/download/sideload-<run_number>/Procedures.ipa`.
- **Rendering:** if Playwright or Chromium is missing, run `pip install playwright pillow numpy` and point `VISUALS_CHROMIUM` at the browser, or run `python -m playwright install chromium`. Smoke test: `python3 scripts/render_visuals.py supraclavicular_anatomy` must print `112/112 checks pass`.
- **When the owner asks for an audit or a final check,** run an independent reviewer agent as well as your own pass. Last time it caught a missing second injection and an unlabelled corner pocket.
- **NYSORA:** a cloud session can't read the owner's local PDF; ask for screenshots. A session on their PC can read it directly. Never commit NYSORA images.
- **The gate before every push:** `validate_procedures.py`, `check_search_ranking.py`, `check_review_state_sources.py`, `python3 -m pytest scripts/tests -q`. Never ship without the owner's explicit "approve". Update `visuals/STATUS.md` whenever a block ships.

**Start by:** fetching main, running the smoke test, and asking the owner one thing: start the sural block, or resume one of the blocks waiting on a painting?
