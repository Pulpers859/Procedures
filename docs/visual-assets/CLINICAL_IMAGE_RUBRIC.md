# Clinical Image Correctness Rubric

This is the authoritative rubric for grading generated procedure visuals. It supersedes the lightweight rubric that previously lived in `ANTIGRAVITY_WORKFLOW.md`. The controlling agent — not the render tool — grades every image against this before any image is bundled or promoted.

The earlier grading pass failed because it scored spelling, labels, and layout while treating anatomy as a "reviewer note." For a bedside clinical tool that is backwards. **Clinical correctness is the gate. Everything else is secondary.**

## The gate

An image may only be called PASS when **both** are true:

1. **Zero critical clinical errors** (see the critical-error list below), and
2. **Weighted correctness score ≥ 99 / 100.**

Anything else is FAIL and must be repaired or rejected. There is no "PASS with a clinical note." A clinical inaccuracy is a FAIL, full stop. "Looks plausible" is not a pass condition — the depicted anatomy, spatial relationships, and landmarks must be *correct*.

The controlling agent grades depiction correctness against the per-image answer key. This does not replace Patrick's final clinical sign-off; a rubric PASS makes an image *eligible* for clinician review, not clinically approved. `reviewerStatus` and the promotion rule in `GEMINI_WORKFLOW.md` still apply.

## Critical errors (any one → automatic FAIL)

- **Wrong anatomical plane or view** for the procedure (e.g., a sagittal globe cross-section for a lateral canthotomy, which is performed and taught in frontal view).
- **A key structure in the wrong position** relative to the others (e.g., IJ vein drawn medial to the carotid; thyroid isthmus drawn at the membrane instead of over the upper tracheal rings).
- **Wrong or misplaced procedure target / entry site / landmark** (e.g., decompression crosshair not at the taught intercostal space and line).
- **Danger structure omitted, mislabeled, or drawn in the wrong place.**
- **A label that points to the wrong structure**, or garbled/duplicated/invented text, or any added title/caption/watermark.
- **Modality misrepresented** (e.g., a B-mode ultrasound window drawn with saturated red/blue vessels — real B-mode is grayscale with anechoic/black lumens; color implies Doppler).
- **An implied action that is unsafe** (e.g., cut direction toward the globe, entry below the rib into the neurovascular bundle).

## Scoring dimensions (weighted, 100 total)

Grade only after the critical-error check. If any critical error exists, stop — the image is FAIL; the score is diagnostic only.

| Dimension | Weight | What it measures |
| --- | --- | --- |
| Anatomical accuracy | 25 | Correct structures, correctly shaped, none invented or omitted. |
| Spatial relationships | 20 | Relative position, depth, and orientation of the key structures. |
| Landmark / site correctness | 20 | The taught target, entry site, or landmark is in the right place. |
| Danger-zone depiction | 15 | What to avoid is present and correctly located. |
| View / plane + modality | 10 | Right anatomical plane, orientation, and imaging modality. |
| Label correctness | 5 | Verbatim spelling and each label points to the correct structure. |
| Teaching clarity at phone size | 5 | The single "miss this prevents" reads unambiguously on iPhone. |

Deductions are per defect, judged against the per-image answer key. Because the pass bar is 99, essentially any real error in a weighted dimension fails the image. That is intended: these are safety-critical references.

## Per-image answer key

Each key lists the ground truth the image must satisfy and the most likely failure modes. Facts are grounded in the procedure's own `anatomy` content in `Procedures/Resources/procedures.json` and standard EM references already cited there (Roberts & Hedges, Tintinalli). Keys are themselves subject to Patrick's ratification.

### cric_membrane — Cricothyrotomy, landmark
Must show: anterior neck, midline, thyroid cartilage superior → **cricothyroid membrane** in the soft gap → cricoid cartilage ring → upper tracheal rings. Membrane is the target, sitting **between** thyroid and cricoid. Vertical skin incision **over the membrane** (not high on the thyroid cartilage, not a long tail down the trachea); short horizontal membrane incision.
Auto-fail: membrane placed above the thyroid cartilage or below the cricoid; incision not over the membrane.

### cric_danger_zone — Cricothyrotomy, danger zone
Must show: same midline column; **midline safe zone** over the airway; anterior jugular veins running vertically **lateral** to midline; **thyroid isthmus crossing the upper tracheal rings, below the cricoid** (not at the membrane); laryngeal artery branches near the lateral membrane edges. Message: stay midline.
Auto-fail: isthmus drawn at or above the membrane instead of over the upper trachea (current draft error); veins drawn midline.

### chest_tube_safe_triangle — Thoracostomy, danger zone
Ground truth (procedures.json): "lateral border pectoralis major, anterior border latissimus dorsi, line above nipple / 5th intercostal space, apex axilla. Neurovascular bundle runs under rib; enter over the superior aspect of the rib." Lateral chest wall view. Safe triangle bordered **anteriorly by the lateral edge of pectoralis major, posteriorly by the anterior edge of latissimus dorsi, inferiorly by the 5th ICS / nipple line, apex at the axilla.** Entry in the triangle at the 4th–5th ICS. Inset: NVB in the **inferior** groove of the upper rib; needle passes **over the top of the lower rib**.
Auto-fail: pec and lat on the wrong sides; triangle boundaries wrong; NVB drawn at the superior rib margin; entry shown under the rib.

### ij_probe_orientation — CVC, probe position
Ground truth: "IJ: vein is commonly **lateral/anterior to carotid**"; "distinguish **compressible** vein from **pulsatile/noncompressible** artery." Short-axis (transverse) view. **Grayscale B-mode window** (black lumens on gray tissue — no saturated color fill). IJ **lateral and superficial**, larger, thin-walled, oval/compressible; carotid **medial and slightly deeper**, round, thick-walled. Probe marker orientation indicated. Needle enters the IJ lumen. Optionally a small compression sub-panel.
Auto-fail: vein medial to artery; vein and artery co-planar and far apart with no lateral/superficial offset; vessels drawn as bright red/blue rings in a B-mode window.

### needle_decompression_landmarks — Needle Decompression, landmark
Ground truth: two sites — **2nd ICS at the midclavicular line** and the lateral **4th–5th ICS at the anterior/mid axillary line**; "2nd ICS MCL … risks malposition if too medial" (internal mammary). Anterior chest. Crosshairs at the correct rib spaces and lines. **Internal mammary artery danger zone** ~3–6 cm lateral to the sternal edge. Enter **over the top of the rib**.
Auto-fail: crosshairs not at the named ICS/line; MCL site too medial (over the internal mammary); entry under the rib.

### pericardiocentesis_approach — Pericardiocentesis, probe position
Ground truth: subxiphoid approach; needle **toward the left shoulder** at a **shallow** angle; target the effusion, not the myocardium; avoid a steep angle. Subxiphoid probe, ultrasound window showing pericardial effusion around the heart, shallow needle path, explicit steep-angle warning. **No title/caption text.**
Auto-fail: any added title banner; steep near-vertical needle path shown as correct; needle aimed away from the left shoulder.

### canthotomy_inferior_crus — Lateral Canthotomy, landmark
Ground truth: "lateral canthal tendon … superior and inferior crus; **cantholysis of the inferior crus**; aim toward the **lateral orbital rim, away from the globe**; lacrimal apparatus medial." **Frontal (anterior) view of the eye and lateral canthus** — not a sagittal globe cross-section. Show the lateral canthus, the horizontal canthotomy incision, the **inferior crus** of the lateral canthal tendon as the release target, and scissors/cut direction **inferolaterally toward the orbital rim, away from the globe.**
Auto-fail: sagittal globe cutaway or any non-frontal view (current draft error); cut direction toward the globe; superior crus shown as the target; duplicated/garbled labels.

### lp_position_landmark — Lumbar Puncture, landmark
Ground truth: "line between iliac crests ≈ L4 spinous process; needle midline … ; conus ends above adult L3; use lower lumbar spaces." Posterior view of the lumbar spine and pelvis. **Tuffier's / intercristal line at ≈ L4**; iliac crests; target interspaces **L3–L4 and L4–L5**, both **below the conus**; midline needle trajectory angled slightly cephalad.
Auto-fail: intercristal line at the wrong level; targets above L3; trajectory off midline.

### paracentesis_liq_site — Paracentesis, landmark
Ground truth: "LLQ **4–6 cm lateral to the midline, midway between umbilicus and ASIS**; avoid the midline; **inferior epigastric vessels run cephalocaudally ~3–5 cm medial to the ASIS**." Anterior abdomen, correctly oriented. LLQ entry marked at the midpoint of the umbilicus–ASIS line, lateral to midline; inferior epigastric vessels shown **medial to** the entry (between entry and midline); bowel-avoidance concept.
Auto-fail: entry at or near midline; inferior epigastric vessels lateral to the entry; wrong quadrant; anatomy uncentered/unreadable.

### thoracentesis_site — Thoracentesis, landmark
Ground truth: "NAV superior-to-inferior in the inferior groove of each rib; **puncture over the superior margin of the lower rib**; diaphragm rises in expiration; right liver below the 9th rib, left spleen." Posterior-lateral chest. Pleural fluid above the diaphragm; entry **over the top of the rib**; NVB at the **inferior** rib margin; diaphragm boundary shown to prevent too-low entry.
Auto-fail: entry under the rib; NVB at the superior margin; entry below the diaphragm; extra parenthetical text on labels.

### usgiv_needle_tracking — US-Guided PIV, confirmation
Ground truth: short-axis view; the risk is tracking the **shaft** and losing the **tip**. **Grayscale B-mode window.** Compressible vein lumen (black), needle **shaft** as a bright segment, needle **tip** as a distinct bright dot, **anterior wall tenting** as the vein wall indents ahead of the tip. Message: do not lose the tip.
Auto-fail: tip and shaft indistinguishable; colorized B-mode; no tenting shown.

## Audit record

For each image, the controlling agent writes `result.txt` in the topic folder with: iteration, conversation id, **critical-error check (pass/fail with specifics)**, the seven dimension scores and total, DECISION (PASS/FAIL), and the exact repair instruction if FAIL. The image is only eligible for promotion at DECISION = PASS, and even then enters clinical review before `assetName` is treated as release-final.

## Reality note

AI image generation is unreliable at precise anatomy and exact landmark placement. Expect multiple repair iterations, and expect that some images will not reach 99% by generation alone. When an image cannot pass after ~5 iterations, mark it blocked and escalate to a medical illustrator — which the production guide already lists as the preferred source for the high-risk set. Do not lower the bar to make an image pass.
