# High-Yield Next Steps for AI Agents

These are the highest-yield improvements to pursue after MVP 0.2. Prioritize them before cosmetic features, accounts, videos, subscriptions, cloud sync, or AI-generated clinical content.

## 1. Expand the Core Procedure Library

Target the procedures most likely to be urgently reviewed on shift:

- Cordis / introducer sheath
- Vas Cath / dialysis catheter
- Arterial line
- Ultrasound-guided peripheral IV
- Paracentesis
- Thoracentesis
- Lateral canthotomy
- Abscess incision and drainage
- Suture repair
- Shoulder reduction
- Fascia iliaca block
- Femoral nerve block
- Median nerve block
- Wrist/forearm blocks
- Resuscitative thoracotomy, if the app is explicitly supporting trauma-critical workflows

Rules:
- Do not add procedures as thin stubs.
- Every procedure must pass content validation.
- High-risk procedures need explicit rescue/failure plans.
- Keep Shift Mode short enough to read under pressure.

## 2. Build Rescue Cards as First-Class Clinical Objects

The Complications tab should become a problem-first rescue system, not merely a list of procedure complications.

Add rescue cards for:
- Post-intubation hypotension
- Failed airway
- Sedation apnea
- Local anesthetic systemic toxicity
- Pneumothorax after central line
- Arterial cannulation during central line
- Lost guidewire
- Failed transvenous pacer capture
- Chest tube malposition
- Post-LP neurologic symptoms
- Bleeding after thoracentesis/paracentesis
- Laryngospasm

Each rescue card should include:
- Trigger
- Immediate moves
- Reassessment targets
- Things to avoid
- Related procedures
- Local policy notes, if applicable

## 3. Make Content Governance Hard to Ignore

Medical content is the product. Treat missing metadata and thin sections like build failures.

Add:
- XCTest target for JSON decoding and validation
- CI script or local script that fails if content has blockers
- Last-reviewed aging warnings
- Reviewer status: Draft / Internally Reviewed / Externally Reviewed / Institution-Specific
- Clinical owner/reviewer fields
- Reference quality tiers

## 4. Elevate the Home Screen

The current Procedures tab works, but a premium app should open like a clinical command center.

Suggested home modules:
- Search bar
- Recently viewed
- Crash procedures
- Rescue cards
- Favorites
- Content health if in developer/editor mode

Do not bury the things clinicians need during the first 30 seconds of a crisis.

## 5. Improve Data Modeling Before Scaling Too Far

Before adding 50+ procedures, consider evolving the schema:

- Equipment groups instead of one flat equipment array
- Medication objects with dose ranges, cautions, and pediatric flags
- Anatomy image references
- Procedure-specific checklist groups
- Rescue card references
- Documentation snippets separated from educational bullets
- Local/institution overlay fields

Flat arrays are acceptable for MVP, but they will become limiting.

## 6. Add Premium Polish Only After Workflow Works

Worthwhile polish:
- Haptics for checklist completion
- Better typography hierarchy
- Procedure iconography
- Section progress indicators
- One-tap copy documentation
- Share/export procedure notes
- Offline update packs

Avoid early distractions:
- Chatbot UI
- Login/account system
- Fancy animations
- Videos before content governance
- Unreviewed AI-generated procedure recommendations

## Current Product Judgment

The app is now moving from scaffold to serious prototype. It is not ready for clinical release until the content library, validation tests, rescue cards, and reviewer workflow are stronger.

The right next milestone is not “more features.” It is:

> A physician can open the app during a shift, search a procedure or complication using normal clinical shorthand, and get a safe, readable, useful answer in under 10 seconds.

## 7. Current Design North Star: Simple Bedside Apps, More Premium

The desired product direction is inspired by simple, clean, bedside-first iOS medical apps such as focused fracture and nerve block references: fast routing, minimal friction, readable cards, and no textbook bloat.

ProcedureSTAT should move in that direction, but with a more premium EM/ICU identity:

- Open to a Guide-first command center, not a generic library.
- Let clinicians enter through the problem, procedure, body region, kit, or complication.
- Use one-question-at-a-time clinical routing.
- Keep screens sparse, readable, and action-oriented.
- Make Shift Mode the default mental model for procedure pages.
- Treat Rescue Cards as first-class clinical objects.
- Treat Kits as physical room setup, not a passive equipment list.
- Add one high-yield visual per procedure: landmark, probe position, safe zone, danger zone, or confirmation image.
- Avoid galleries, long chapters, excess animations, and decorative medical clip art.

Premium does not mean flashy. Premium means the clinician reaches the right, trustworthy answer faster.

## 8. Immediate Product Direction After MVP 0.3

Build toward this tab structure:

1. Guide — command center, search, clinical pathways, recent, crash, rescue
2. Procedures — A-Z reference library
3. Rescue — problem-first complication response cards
4. Kits — physical setup and equipment checklists
5. Saved — favorites, notes, local preferences, content health

Do not reintroduce a separate Shift Mode tab unless analytics show clinicians need it. Shift Mode should live at the top of every procedure page and inside Guide routing.

## 9. Visual Landmark System

Every procedure should eventually have a visual landmark slot. Start with placeholder metadata before final illustrations exist.

Examples:

- Cricothyrotomy: membrane landmark and incision path
- Chest tube: safe triangle and rib neurovascular bundle warning
- IJ central line: probe orientation, vessel relationship, needle path
- LP: positioning and interspace landmarking
- Pericardiocentesis: approach options and probe/needle orientation
- Transvenous pacer: waveform/capture confirmation
- Digital block: injection sites and sensory distribution

Rules:

- One visual that prevents a miss is better than five pretty images.
- Visuals must be clinically reviewed like text.
- Diagrams should be local/offline assets.
- Do not use unreviewed AI-generated medical anatomy in release builds.
