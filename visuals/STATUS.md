# Procedure Images: Status

Last updated: 2026-10-15. Every slot outside the skip lists now has an owner-approved image.

How to make an image: `PLAYBOOK.md`. Live slot list: `python3 scripts/pq.py visuals`. Trust that over this page if they disagree.

## Goal

Every slot in `procedures.json` either has an owner-approved image or is on a skip list. Every nerve block gets two images: `<block>_patient_position` (probe or needle on the patient, painted as a photo) and `<block>_anatomy` (the section or skull under it).

## Progress

- **77 slots bundled, 12 empty (all on the skip lists).**
- **Skip; the owner adds real images (11):** ultrasound and rhythm strips (`aline_us_short_axis`, `ij_probe_orientation`, `cvc_wire_confirmation`, `ficb_subfascial_spread`, `fb_us_appearance`, `knee_us_effusion`, `pericardiocentesis_approach`, `pigtail_us_effusion`, `tvp_capture_confirmation`, `usgiv_short_axis`, `usgiv_needle_tracking`).
- **Skip as low value unless asked (1):** `abscess_technique`.
- **Nothing left to make.** New slots added to `procedures.json` start the workflow again.

### Shipped recently

| Block | Shipped | Build | Notes |
| --- | --- | --- | --- |
| Deep peroneal | 2026-10-01 | sideload-15 | |
| Femoral nerve | 2026-10-01 | (other session) | |
| Supraclavicular | 2026-10-14 | sideload-33 | The model for nerve-block sections (house style in `PLAYBOOK.md`). |
| Superficial cervical plexus | 2026-10-14 | sideload-35 | Section in the house style; probe at mid-SCM (mastoid-clavicle midpoint, NYSORA). |
| Superior alveolar | 2026-10-14 | sideload-35 | Canine as the default tooth. |
| Superficial peroneal | 2026-10-15 | sideload-36 | Positioning: Gemini removed the equipment from the owner's photo; the photo's own probe was moved into place in code (`place_probe.py`) and the needle is code-drawn. Needle from anterior per NYSORA. |
| Tibial | 2026-10-15 | sideload-40 | Mirror of the sural plates on the medial side; needle from the Achilles end per NYSORA. |
| TAP | 2026-10-15 | sideload-40/41 | Photo: probe rotated in Gemini to transverse, in plane with the needle (owner); dashed mid-axillary line in code. |
| Ulnar | 2026-10-15 | sideload-40/41 | Photo uses the approved median arm as a style reference. |
| Transgluteal / proximal sciatic | 2026-10-15 | sideload-40/41 | Probe below the gluteal fold (owner); section redrawn at the subgluteal level after NYSORA Fig-6 (no bones in view). |
| Sural | 2026-10-15 | sideload-38/39 | Section redrawn to true scale after independent review (malleolus subcutaneous); needle from anterior per NYSORA. |
| Thoracic ESP | 2026-10-15 | sideload-38 | Positioning: gloved hand added in Gemini (owner). |
| Thoracentesis site | 2026-10-15 | sideload-39 | ESP back with equipment removed, re-posed leaning forward over a table (record position); rib inset cropped from the chest tube painting. |
| Chest tube (both slots) | 2026-10-15 | sideload-37 | Safe triangle drawn in code on the approved serratus painting (patient's left side). Rib section: the tube turns cranially in the pleural space so every side hole, including the sentinel hole, is inside the pleura (owner). |
| Supraorbital | 2026-10-14 | sideload-34 | The finger is the photo's own glove, placed in code (`place_finger.py`), and the green eyes come from `green_eyes.py`. |

### In progress

- Nothing waiting on a painting.

### Not started

- None.

## Working notes that hold across sessions

- **Antigravity lane (Claude on the owner's PC):** `tools/Invoke-AntigravityAgentApi.ps1 -Command NewConversation ... -PassPromptFileAsAtPath` with a prompt file under `tmp/visual-drafts/antigravity/<slot>/`; about a minute per painting at 1200x896. It shares Gemini's image quota; a 429 is logged in the conversation's `transcript.jsonl`.
- **Gemini returns full size only via Download.** A copy from the chat comes back at 512×382. Always ask for the full-size download.
- **When Gemini will not move something, do it in code.** Gemini repairs can't place a hand or finger precisely. Have Gemini remove the object, then composite the photo's own object back in code (`supraorbital_patient_position/place_finger.py`). Small colour changes, such as eye colour, are also safer in code (`green_eyes.py`).
- **Check each Gemini repair against the image before it.** A repair can remove things it was not asked to touch. Take the lost area back with `visual_patch.py crop` and `merge`.
- **Approval hashes ignore line endings** (since 2026-10-08). Approvals recorded on Windows and on Linux agree.
- **The pause.** On resume, re-run `pq.py visuals`, confirm the slots above, and start with the sural block or a waiting painting, whichever the owner brings.
