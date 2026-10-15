# Procedure Images: Status

Last updated: 2026-10-15. Superficial peroneal pair complete (positioning plate on the owner's photo, probe composited in code).

How to make an image: `PLAYBOOK.md`. Live slot list: `python3 scripts/pq.py visuals`. Trust that over this page if they disagree.

## Goal

Every slot in `procedures.json` either has an owner-approved image or is on a skip list. Every nerve block gets two images: `<block>_patient_position` (probe or needle on the patient, painted as a photo) and `<block>_anatomy` (the section or skull under it).

## Progress

- **64 slots bundled, 25 empty.**
- **Skip; the owner adds real images (11):** ultrasound and rhythm strips (`aline_us_short_axis`, `ij_probe_orientation`, `cvc_wire_confirmation`, `ficb_subfascial_spread`, `fb_us_appearance`, `knee_us_effusion`, `pericardiocentesis_approach`, `pigtail_us_effusion`, `tvp_capture_confirmation`, `usgiv_short_axis`, `usgiv_needle_tracking`).
- **Skip as low value unless asked (1):** `abscess_technique`.
- **That leaves 13 slots to make.**

### Shipped recently

| Block | Shipped | Build | Notes |
| --- | --- | --- | --- |
| Deep peroneal | 2026-10-01 | sideload-15 | |
| Femoral nerve | 2026-10-01 | (other session) | |
| Supraclavicular | 2026-10-14 | sideload-33 | The model for nerve-block sections (house style in `PLAYBOOK.md`). |
| Superficial cervical plexus | 2026-10-14 | sideload-35 | Section in the house style; probe at mid-SCM (mastoid-clavicle midpoint, NYSORA). |
| Superior alveolar | 2026-10-14 | sideload-35 | Canine as the default tooth. |
| Superficial peroneal | 2026-10-15 | sideload-36 | Positioning: Gemini removed the equipment from the owner's photo; the photo's own probe was moved into place in code (`place_probe.py`) and the needle is code-drawn. Needle from anterior per NYSORA. |
| Chest tube (both slots) | 2026-10-15 | sideload-37 | Safe triangle drawn in code on the approved serratus painting (patient's left side). Rib section: the tube turns cranially in the pleural space so every side hole, including the sentinel hole, is inside the pleura (owner). |
| Supraorbital | 2026-10-14 | sideload-34 | The finger is the photo's own glove, placed in code (`place_finger.py`), and the green eyes come from `green_eyes.py`. |

### In progress

- Review drafts awaiting approval (2026-10-15): `sural_patient_position`, `sural_anatomy` (true-scale relayout), `esp_patient_position` (gloved hand), `esp_anatomy`, `thoracentesis_site` (ESP back with equipment removed + rib inset; a leaning-forward repaint was offered).

### Not started (A–Z order, both slots each unless noted)

1. Sural nerve block (**next**)
2. Thoracentesis: `thoracentesis_site`
3. Thoracic erector spinae plane (ESP)
4. Thoracostomy / chest tube: `chest_tube_safe_triangle`, `chest_tube_rib_anatomy`
5. Tibial nerve block
6. Transgluteal / proximal sciatic block
7. Transversus abdominis plane (TAP)
8. Ulnar nerve block

## Working notes that hold across sessions

- **Antigravity lane (Claude on the owner's PC):** `tools/Invoke-AntigravityAgentApi.ps1 -Command NewConversation ... -PassPromptFileAsAtPath` with a prompt file under `tmp/visual-drafts/antigravity/<slot>/`; about a minute per painting at 1200x896. It shares Gemini's image quota; a 429 is logged in the conversation's `transcript.jsonl`.
- **Gemini returns full size only via Download.** A copy from the chat comes back at 512×382. Always ask for the full-size download.
- **When Gemini will not move something, do it in code.** Gemini repairs can't place a hand or finger precisely. Have Gemini remove the object, then composite the photo's own object back in code (`supraorbital_patient_position/place_finger.py`). Small colour changes, such as eye colour, are also safer in code (`green_eyes.py`).
- **Check each Gemini repair against the image before it.** A repair can remove things it was not asked to touch. Take the lost area back with `visual_patch.py crop` and `merge`.
- **Approval hashes ignore line endings** (since 2026-10-08). Approvals recorded on Windows and on Linux agree.
- **The pause.** On resume, re-run `pq.py visuals`, confirm the slots above, and start with the sural block or a waiting painting, whichever the owner brings.
