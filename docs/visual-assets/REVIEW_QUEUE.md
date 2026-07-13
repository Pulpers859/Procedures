# Visual Review Queue

Last reconciled: 2026-07-13

This queue tracks generated procedure visuals that are ready for clinician review or already bundled. A `DECISION: PASS` in a draft folder means the controlling agent found no rubric-critical error and the image is eligible for review. It is not clinical approval.

## Already Bundled

These assets are wired in `Procedures/Resources/procedures.json` and live in `Procedures/Assets.xcassets`.

| Asset id | Procedure | Bundle status | Evidence |
| --- | --- | --- | --- |
| `cric_membrane` | Cricothyrotomy | Bundled and wired | `cric_membrane.imageset`, `assetName: cric_membrane` |
| `cric_danger_zone` | Cricothyrotomy | Bundled and wired | `cric_danger_zone.imageset`, `assetName: cric_danger_zone` |
| `canthotomy_inferior_crus` | Lateral Canthotomy & Cantholysis | Bundled and wired | `canthotomy_inferior_crus.imageset`, `assetName: canthotomy_inferior_crus`, commit `b46ab1e` |

## Reviewable Drafts

Do not promote these until Patrick has reviewed clinical accuracy, label spelling, layout, and phone readability.

| Asset id | Candidate file | Status | Review note |
| --- | --- | --- | --- |
| `chest_tube_safe_triangle` | `tmp/visual-drafts/antigravity/chest_tube_safe_triangle/chest_tube_safe_triangle_iter2.png` | PASS with cosmetic note | Near-square rather than strict 4:3; re-crop or light re-render if needed. |
| `ij_probe_orientation` | `tmp/visual-drafts/antigravity/ij_probe_orientation/ij_probe_orientation_iter3.png` | PASS | Clean review candidate. |
| `lp_position_landmark` | `tmp/visual-drafts/antigravity/lp_position_landmark/lp_position_landmark_iter3.png` | PASS | Clean review candidate. |
| `needle_decompression_landmarks` | `tmp/visual-drafts/antigravity/needle_decompression_landmarks/needle_decompression_landmarks_iter3.png` | PASS | Confirm the 2nd intercostal-space marker reads midclavicular, not parasternal. |
| `paracentesis_liq_site` | `tmp/visual-drafts/antigravity/paracentesis_liq_site/paracentesis_liq_site_iter6.png` | PASS with cosmetic note | Near-square and slightly sketchier than earlier drafts; clinically correct per audit. |
| `thoracentesis_site` | `tmp/visual-drafts/antigravity/thoracentesis_site/thoracentesis_site_iter3.png` | PASS | Confirm entry height is safely above the diaphragm. |
| `usgiv_needle_tracking` | `tmp/visual-drafts/antigravity/usgiv_needle_tracking/usgiv_needle_tracking_iter3.png` | PASS | Confirm the long visible shaft is acceptable as a short-axis teaching simplification. |

## Needs Regeneration

| Asset id | Prior file | Status | Reason |
| --- | --- | --- | --- |
| `pericardiocentesis_needle_path` | `tmp/visual-drafts/gemini-web/pericardiocentesis_needle_path/pericardiocentesis_needle_path_iter19_reference_image_guided_FAILED_crop.png` | Needs hybrid regeneration | Reference-guided Gemini finally corrected the lower-left to upper-right needle direction but routed the path through/over the liver. Next pass should generate an unlabeled anatomy plate and add the syringe/needle with a deterministic overlay controlling angle, liver clearance, and inset target. |
| `pericardiocentesis_approach` | `tmp/visual-drafts/antigravity/pericardiocentesis_approach/pericardiocentesis_approach_review_candidate_cropped.png` | Retired | Prior draft passed a narrow geometry audit but read like a subxiphoid TTE view rather than a procedural teaching image. This slot now owns ultrasound target confirmation only. |

## Promotion Checklist

1. Clinician reviews the candidate image against the procedure and the visual rubric.
2. Any cosmetic cleanup is done in the draft lane, not directly over a bundled asset.
3. Add the final PNG as `Procedures/Assets.xcassets/<assetId>.imageset/<assetId>.png`.
4. Add or confirm `Contents.json` for the imageset.
5. Set the matching `visualAssets.assetName` in `Procedures/Resources/procedures.json`.
6. Run `python scripts/validate_procedures.py`.

Keep generated drafts out of git until they are clinically reviewed and promoted.
