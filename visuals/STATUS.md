# Procedure Images: Status

Last updated: 2026-10-14. Paused at the owner's request after the supraorbital block shipped.

How to make an image: `PLAYBOOK.md`. Live slot list: `python3 scripts/pq.py visuals`. Trust that over this page if they disagree.

## Goal

Every slot in `procedures.json` either has an owner-approved image or is on a skip list. Every nerve block gets two images: `<block>_patient_position` (probe or needle on the patient, painted as a photo) and `<block>_anatomy` (the section or skull under it).

## Progress

- **57 slots bundled, 32 empty.**
- **Skip; the owner adds real images (11):** ultrasound and rhythm strips (`aline_us_short_axis`, `ij_probe_orientation`, `cvc_wire_confirmation`, `ficb_subfascial_spread`, `fb_us_appearance`, `knee_us_effusion`, `pericardiocentesis_approach`, `pigtail_us_effusion`, `tvp_capture_confirmation`, `usgiv_short_axis`, `usgiv_needle_tracking`).
- **Skip as low value unless asked (1):** `abscess_technique`.
- **That leaves 20 slots to make.**

### Shipped recently

| Block | Shipped | Build | Notes |
| --- | --- | --- | --- |
| Deep peroneal | 2026-10-01 | sideload-15 | |
| Femoral nerve | 2026-10-01 | (other session) | |
| Supraclavicular | 2026-10-14 | sideload-33 | The model for nerve-block sections (house style in `PLAYBOOK.md`). |
| Supraorbital | 2026-10-14 | sideload-34 | The finger is the photo's own glove, placed in code (`place_finger.py`), and the green eyes come from `green_eyes.py`. |

### In progress: layouts pushed, waiting on the owner's Gemini paintings

These were started in another session on 2026-10-04. Their references and prompts were sent there.

- `sc_plexus_patient_position`: layout `f36ebf5`. Its section plate is already shipped.
- `superficial_peroneal_patient_position` and `superficial_peroneal_anatomy`: layouts `ea89b92`.
- `superior_alveolar_patient_position` and `superior_alveolar_anatomy`: layouts `3818c3f`.

To resume one: `python3 scripts/render_visuals.py <id> --reference`, resend it with the prompt, and continue from `PLAYBOOK.md` section 4.

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

- **Gemini returns full size only via Download.** A copy from the chat comes back at 512×382. Always ask for the full-size download.
- **When Gemini will not move something, do it in code.** Gemini repairs can't place a hand or finger precisely. Have Gemini remove the object, then composite the photo's own object back in code (`supraorbital_patient_position/place_finger.py`). Small colour changes, such as eye colour, are also safer in code (`green_eyes.py`).
- **Check each Gemini repair against the image before it.** A repair can remove things it was not asked to touch. Take the lost area back with `visual_patch.py crop` and `merge`.
- **Approval hashes ignore line endings** (since 2026-10-08). Approvals recorded on Windows and on Linux agree.
- **The pause.** On resume, re-run `pq.py visuals`, confirm the slots above, and start with the sural block or a waiting painting, whichever the owner brings.
