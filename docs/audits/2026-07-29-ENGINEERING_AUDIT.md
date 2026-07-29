# Engineering Audit — 2026-07-29

An engineering and UX audit of the whole app, plus a bedside stress test of the
search and review paths. Everything here was verified directly against the
files, not taken on report.

This document does **not** authorize content changes and makes no clinical
assertion. The clinical items below are internal contradictions and structural
gaps found by arithmetic and grep; each is a question for the clinical owner.
The fingerprinted adjudication queue in `procedure-verification/` is untouched.

---

## Fixed in this pass

Every item below shipped with a test, and each guard was confirmed to fail on
the state that preceded it.

### Data loss and identity

- **Two bundle identifiers.** Debug was `Patrick-App.ProceduresSTAT`, Release
  `com.pjkane859.ProcedureSTAT`. A bundle identifier is the app's identity to
  iOS: `UserDefaults` and `Documents/` both live in a per-identifier container,
  so moving from an Xcode install to TestFlight would have presented as a
  factory-fresh app and stranded every sign-off, note, favourite and local
  edit. Unified on the Debug identifier — where the existing on-device data
  actually lives — at the repo owner's direction. `verify_xcode_project.py`
  now fails when configurations diverge.
- **Silent total loss on a decode failure.** Every persisted collection is one
  whole-blob key, loaded with `try?` and saved by rewriting the blob entirely,
  so a single undecodable record left the collection empty in memory and the
  next sign-off wrote one record over all of them. Undecodable bytes are now
  quarantined to a `.unreadable` sidecar and surfaced on Home.
- **A review could be silently retired.** The section editor saves on
  `onDisappear` whether or not anything was typed, and the re-baseline adopted
  the current fingerprint without asking why it differed — so opening any
  section of a procedure whose bundled text had changed since sign-off, reading
  nothing, and tapping Back turned "Review out of date" back into "Reviewed".

### Review integrity

- **The fingerprint did not cover Shift Mode** — the section the detail page
  opens on, and the condensed crash-path text. A bundled rewrite of it left
  every sign-off reading a plain "Reviewed". Now covered, along with equipment,
  confirmation and troubleshooting.
- **Section boundaries were invisible.** Lists were concatenated flat, so a line
  moving from the end of one section to the start of the next produced a
  byte-identical digest. Most likely on kits: moving an item from "in the kit"
  to "outside the kit" changed nothing.
- **The Swift/Python fingerprint mirror was locked on one side only.** The
  Python suite built its expected value by calling the function under test — a
  tautology. Drift would have refused every exported sign-off as stale, about
  content that never changed. Both sides are now locked together, and the lock
  caught a real drift during this pass.
- Widening the field set is versioned, so existing sign-offs read as an unknown
  baseline rather than falsely reading "out of date".

### Retrieval

- **Sentence queries did not work.** The procedure path kept the filler words
  the rescue path dropped, and scoring is substring-based, so "the" matched
  *ca-**the**-ter*. "the patient is hypotensive after intubation" scored all 55
  procedures and did not rank intubation in the top five.
- **Typo recovery rewrote real words.** "lost" is one edit from "last", so a
  query about a *lost airway* was rewritten into the LAST group and answered
  with local anaesthetic systemic toxicity, ranking nerve blocks above
  intubation. Recovery now skips any word the shipped content actually uses.
- **"Crashing" resolved to nothing** — absent from every card and from the
  synonym map. The existing test passed only because "my" and "is" were
  matching *my-ocardial* and *ep-is-taxis*.
- **The rescue list was in file order** while `RescueAppIntents` told Siri and
  Action-button users it was "Crash-acuity problems first". An Urgent card sat
  above four Crash cards.

### Disclosure and UX

- Home never reported a procedure or kit load failure; a failed decode rendered
  a normal-looking dashboard of zeros, the pathway screen affirmatively
  reassured that the emptiness was deliberate, and search blamed the query.
- Seven sites tinted warning text and glyphs with raw `.orange` (~2.2:1 on
  light), including the danger-zone caption on visual assets at `.caption`.
- The editor promised "Other reviewers will be asked to take another look".
  There is one reader.
- Checklist session gates were cleared only on cold launch, so ticks from a
  case two days earlier could render as the current room's state.
- "Show Disclaimer Again" set the flag and dismissed in the same frame, which
  drops the presentation — the disclaimer then ambushed the reader at next
  launch instead.
- The badge policy hashed the whole library twice per rendered row.

---

## For clinical adjudication

C1 and C4 were adjudicated by the clinical owner on 2026-07-29 and are
corrected; both are marked RESOLVED below with the original finding retained.
Everything else here is unactioned and still needs a decision.

Note on provenance: the two corrected records keep
`reviewerStatus: Needs Clinical Review` and `contentSource: ai-draft`. A
directed correction is not a sign-off — recording that belongs in the app's
review flow, which is what carries it back through
`scripts/apply_local_reviews.py`. Both edits change the material fingerprint,
so any existing local review of them will correctly read "Review out of date".

### C1. RESOLVED — a procedure's own recommendation exceeded its own ceiling

**Adjudicated by the clinical owner on 2026-07-29 and corrected.** The chosen
fix caps volume by concentration rather than removing an option: the 20-30 mL
range now names 0.25% bupivacaine or 0.2% ropivacaine, and 0.5% is capped at
20 mL (100 mg) with an explicit weight check. The worked example now shows the
0.5% arithmetic that made the contradiction invisible. `block_raptir` moved to
version 0.2.0; its `reviewerStatus` remains `Needs Clinical Review` because the
sign-off belongs in the app's review flow, not in an edit.

`prose_dose_ceiling_issues` now returns nothing across all 55, and a test locks
that. The original finding is kept below for the record.

### C1 (original finding). A procedure's own recommendation exceeds its own ceiling

`block_raptir` (RAPTIR / Infraclavicular Block) states, in equipment and again
in steps, **"20-30 mL of 0.25% or 0.5% bupivacaine"**. Its own
`concentrationNote` defines 0.5% as 5 mg/mL, so the top of that range is
**150 mg**, against the **2.0 mg/kg** ceiling the same record states — 140 mg
at 70 kg, 100 mg at 50 kg. The `workedExample` computes only the 0.25% case
(75 mg), so the arithmetic that would reveal it is never shown.

Verified by hand and now caught by `prose_dose_ceiling_issues`, which fires on
this and nothing else across the 55.

Adjacent, not flagged because they do not breach: `block_supraclavicular` and
`block_femoral_nerve` both land at exactly 100 mg at 0.5%, which is precisely
the 50 kg ceiling and leaves no margin for a skin wheal or prior infiltration.
Whether zero margin is acceptable is a clinical judgement, so the rule reports
only strict breaches.

### C2. Ten blocks state a volume with no drug

Ten regional blocks say "Local anesthetic (5-10 mL)" — or 20-30 mL — and never
name an agent or concentration in equipment or steps, while listing two agents
with different ceilings in `dosing`. "20-30 mL" in `block_popliteal_sciatic` is
50-75 mg as 0.25% bupivacaine or 200-300 mg as 1% lidocaine, a fourfold spread
the reader must close from memory.

Now reported once per procedure by `uncomputable_injectate_issues`:
deep peroneal, median, popliteal sciatic, radial, saphenous, superficial
peroneal, sural, tibial, transgluteal sciatic, ulnar.

### C3. A named drug with no stated maximum

`block_inferior_alveolar` offers **"lidocaine/articaine"** and has no articaine
entry in its dosing table — or anywhere in `procedures.json`. Caught by
`unbounded_agent_issues`.

### C4. RESOLVED — the LAST card did not describe the LAST prodrome

**Adjudicated by the clinical owner on 2026-07-29 and corrected.** The trigger
now leads with the early warning signs — perioral/lip/tongue numbness or
tingling, tinnitus, metallic taste, light-headedness, visual disturbance,
agitation or confusion — before the established presentation, which is
unchanged. A third line states that the prodrome may be absent under sedation
or general anaesthesia and that its absence does not exclude LAST; without it,
adding early signs would have created a new hazard by reading as a gate. Tags
gained the prodrome terms.

No dose, immediate move, avoid item or reassess line was touched. Six prodrome
queries now return the card first, and tests lock both the retrieval and the
caveat. The original finding is kept below for the record.

### C4 (original finding). The LAST card does not describe the LAST prodrome

Found by stress-testing the rescue path: typing **"ringing in ears numb lips"**
does not surface the LAST card. Its `trigger` names only seizure, altered
mental status, dysrhythmia and cardiac arrest, and the words *tinnitus*,
*ringing*, *perioral*, *numbness*, *metallic* and *taste* appear nowhere on
the card — not in trigger, not in tags.

This is the moment intervention is most effective, and it is the one the card
cannot be found by. Adding the early signs is authoring clinical recognition
criteria, so it is left here rather than done. A clinician decision on the
trigger text would fix both the content and the retrieval in one edit.

### C5. Failure plans that are not failure plans

`sections.troubleshooting` renders under the heading **"If It Fails"**. Twenty
procedures have exactly one entry there, and most of those are scanning or
technique pearls rather than failure paths — for example
`block_popliteal_sciatic` reads *"Injecting just as the nerve bifurcates
provides the most rapid onset."* No regional block states what to do when the
block does not take, except `block_supraorbital` and `block_superior_alveolar`.

The non-regional core (chest tube, CVC, LP, canthotomy, cric, needle
decompression) has genuinely good troubleshooting; the gap is concentrated in
the regional set. Explicit failure planning is the product's stated premise.

### C6. Complications as word lists

150 of 252 complication entries are noun phrases of four words or fewer with no
action. `"Intravascular injection"` appears verbatim in 17 procedures.
Eighteen procedures have no actionable complication entry at all, including
`cricothyrotomy` (6 of 6), `thoracostomy_chest_tube` (7 of 7),
`transvenous_pacemaker` and `procedural_sedation`.
`PROCEDURE_SCHEMA.md` asks for "practical rescue thinking"; nothing enforces it.

### C7. Complications named with no rescue card

Seventeen procedures have no rescue-card coverage. Complications named in
procedure text with no card anywhere: intravascular injection (25 procedures),
bleeding (16), nerve injury (15), infection (15), hematoma (13), air embolism
(5), phrenic nerve palsy (4). Three Rare-Crash procedures have no card at all:
`pericardiocentesis`, `lateral_canthotomy`, `resuscitative_thoracotomy`.

### C8. Coverage gaps for the stated audience

Regional anaesthesia is 28 of 55; Airway is 2, Neuro 1, Sedation 1. Absent
entirely from both content files: malignant hyperthermia and dantrolene,
anaphylaxis, any neuraxial procedure, high/total spinal, awake intubation,
videolaryngoscopy, supraglottic airway insertion, lung isolation, sugammadex
and residual paralysis. Several of these are complications the existing text
names.

### C9. Schema drift in `reviewTime`

Twenty-six procedures carry `reviewTime: "standard"`, which is not in
`PROCEDURE_SCHEMA.md`'s list. `Procedure.reviewTime` is a bare `String`, so
nothing rejects it, and the chip renders "standard" beside "2 min". All 26 are
the bulk-added `block_*` records.

---

## Audit baseline

`verify_procedure_audit.py` fails on all three content files. It was already
failing on all three before this session — including `kits.json`, which nothing
here touched — which matches the integrity hold already recorded at the top of
`procedure-verification/CLINICAL_OWNER_QUEUE.md`. The C1 and C4 corrections
moved two of those hashes further. Re-baselining the audit is a clinical-owner
decision, not an engineering one, so the expected values are left alone. The
script runs only on tag pushes (`release-readiness.yml`), so `main` CI is
unaffected.

## Known and deliberately not done

- `apply_local_reviews.py` reformats `kits.json` wholesale on write, so a
  one-field promotion produces a ~400-line diff and the change cannot be
  reviewed. Worth fixing before the first real promotion.
- Review dates are stamped in UTC, so a sign-off on an evening shift can carry
  tomorrow's date.
- Local overrides mask bundled corrections: if a section is overridden and
  upstream later fixes that same section, the fix is never displayed and
  nothing compares the two. `bundledSections` holds the data needed to detect
  it.
- Renaming a procedure `id` silently deletes its review, note, favourite,
  checklist state and local edits, with no alias table and no migration. IDs
  should be treated as permanent; nothing currently enforces that.
- No widget extension exists — absent rather than half-wired.
- Navigation state is not restored; the app returns to the right tab but the
  root of it.
