# UI / UX Rules

## Philosophy

This app should feel like a fast clinical tool, not a course module.

## Audience: one user

There is exactly one reader, and it is the person who owns the repo. Write copy
accordingly.

- Never attribute an action back to the reader. `Reviewed`, not `Reviewed by you`.
  `Edits`, not `My Edits`. `Changed Since Review`, not `Changed Since Your Review`.
- Do not narrate what the reader already knows they did. They recorded the
  sign-off; restating whose it is costs a line and adds nothing.
- Second person is still fine when it is genuinely instructional
  (`Before You Start`, `Calculate Before You Draw Up`). The rule is about
  attribution, not about the word "you".
- `scripts/check_review_state_sources.py` fails the build on the banned phrasing.
- The local-versus-upstream review distinction stays in the code because it drives
  export and validation. Only the visible text collapses to one word.

## Main tabs

1. Guide — command center, pathway routing, search, rescue preview
2. Procedures — A-Z library with category quick access
3. Rescue — problem-first rescue cards and procedure-specific complication reviews
4. Kits — physical room setup and equipment checklists
5. Saved — favorites, recents, and local notes

Review Center is an optional editor workspace, not part of the default bedside flow.

## Procedure screen

Default to Shift Mode.

Use the segmented control for:

- Shift Mode
- Equipment
- Steps
- Complications
- Documentation
- Deep Review

## Formatting

- Bullets for high-yield review
- Numbered lists for procedural steps
- Checklists for equipment
- Warning cards for critical content
- Dark-mode friendly materials and high contrast

## Premium Bedside Direction

The UI should feel simple, fast, and calm. Premium means high trust and low friction, not decoration.

Updated navigation model:

- Guide: command center and pathway routing
- Procedures: A-Z library
- Rescue: complication response cards
- Kits: physical room setup
- Saved: favorites, recents, notes
- Review Center: optional editor workspace for review queue, validator issues, and local reviewer notes

Procedure pages should feel like focused cards, not articles. The top of every detail page should quickly show:

- Risk level
- Review time
- Shift Mode
- Visual Landmark slot
- Failure plan
- Kit/setup
- Rescue moves

Visuals should be restrained and clinically purposeful. A single landmark/probe/danger-zone diagram is preferred over broad image galleries.

## External UI/UX Resource Decisions

When the task is about evaluating outside UI/UX repos, component libraries, design systems, reference sites, or design-oriented agent skills, use `docs/AI_UI_UX_RESOURCE_EVALUATION_PLAYBOOK.md` as the decision framework.

Do not trigger that process for ordinary small UI fixes. Use it for design-system decisions, redesign planning, tooling comparison, and external-inspiration evaluation.
