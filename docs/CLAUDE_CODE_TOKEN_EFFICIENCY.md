# Claude Code Token Efficiency

## Why this exists

The goal is to make Claude Code more efficient in this repo without bloating the repo with more permanent instructions than the savings are worth.

This is a native SwiftUI iOS app, not a web app. That matters. A lot of the flashy external UI tooling is useful for visual research, but most of it does not directly reduce token use on ordinary Procedures work.

## Brutally Honest Verdict

### BuilderIO/skills

Decision: `Adapt`

This is the only resource in the list with a clear, direct path to better Claude Code token efficiency.

Useful ideas to adapt:

- preserve the expensive model for planning, tradeoffs, and final review
- use bounded work waves instead of unstructured long sessions
- avoid loading every file and every log into the same context
- write short recaps before switching domains or resuming later

Important limitation:

- `stay-within-limits` is mostly about usage-window control, not magical per-task token reduction
- installing the whole external set would add overlap and instruction weight

What to keep from it for this repo:

- workflow patterns, not wholesale installation
- repo-specific rules that point agents to the real source-of-truth files fast

### nextlevelbuilder/ui-ux-pro-max-skill

Decision: `Reference`

This can help with explicit UI/UX design tasks, but it is not a token-efficiency tool.

Potential value:

- visual-direction brainstorming
- design-system starting points
- anti-pattern reminders

Why it is not an `Adopt` for this goal:

- it is design-heavy, not efficiency-heavy
- it can easily create more context than it saves
- it is broad enough that careless use would increase token burn on a focused SwiftUI task

### 21st.dev community components

Decision: `Skip`

For token efficiency in this repo, this is mostly the wrong tool.

Why:

- it is strongly web and React oriented
- this app is native SwiftUI
- browsing web-component catalogs is likely to consume attention and tokens without helping the actual implementation path

Use it only if a future task is explicitly about high-level visual inspiration, and even then keep it secondary.

### UX Components design systems

Decision: `Reference`

This is useful as occasional component-behavior and pattern education, not as a permanent repo dependency and not as a direct token saver.

Potential value:

- checking whether a component pattern is structurally sound
- thinking through states, anatomy, and accessibility expectations

Why not more:

- it does not understand the project automatically
- it does not reduce routine repo context load by itself

### Refero

Decision: `Reference`

Refero is good for occasional flow and hierarchy research. It is not a core efficiency tool.

Potential value:

- screen-flow research
- hierarchy comparison
- identifying repeated patterns across good products

Why not more:

- screenshot browsing can become expensive quickly
- references are easy to over-collect and under-use

## Recommended Combined System

Keep the system small:

1. Adapt BuilderIO-style efficiency patterns into local repo instructions.
2. Keep UI UX Pro Max, UX Components, and Refero as on-demand research inputs only.
3. Skip 21st.dev for normal Procedures work.

That gives real value without turning this repo into a warehouse of generic agent tooling.

## Repo-Specific Efficiency Rules

Use these defaults in Claude Code for Procedures:

1. Start with targeted discovery.
   - Use focused search to find the exact symbol, file, or feature surface first.
   - Do not open large files until the task proves they matter.

2. Read the minimum stable context.
   - Start with `PROJECT_HANDOFF.md` and `docs/ai-instructions/AGENTS.md` only when repo orientation is needed.
   - Avoid rereading long stable docs mid-task unless the task changed.

3. Respect source-of-truth paths.
   - App code lives in `Procedures/`
   - Procedure content lives in `Procedures/Resources/procedures.json`
   - Rescue-card content lives in `Procedures/Resources/rescue_cards.json`
   - Do not scan old exports, screenshots, or unrelated folders unless the task explicitly requires them.

4. Do not load content blobs casually.
   - Avoid opening full JSON content files for ordinary UI or bug-fix work.
   - Read only the relevant fragment or validate with the script when possible.

5. Work in bounded waves.
   - Inspect
   - edit
   - verify
   - recap
   - commit and push

6. Keep external research narrow.
   - Use at most one or two external resources in a pass.
   - Choose them by need, not by availability.
   - Stop once the answer is good enough to implement.

7. Prefer recaps over rehydration.
   - When a task grows, write a short factual recap instead of rereading everything.
   - Summaries are cheaper than repeated broad context loading.

8. Use the narrowest verification that proves the change.
   - Run `python scripts/validate_procedures.py` after content changes.
   - Be explicit when iOS or Xcode verification could not be performed from Windows.

## Good Uses For External Resources

- BuilderIO patterns: large, multi-step, repo-spanning work
- UI UX Pro Max: explicit design-system or visual-direction tasks
- UX Components: component-state and interaction-pattern questions
- Refero: focused flow or hierarchy research

## Bad Uses For External Resources

- opening design catalogs for a localized Swift fix
- using web-component libraries to steer native iOS implementation
- collecting more references after the implementation direction is already clear
- permanently installing broad skills that rarely activate

## What was implemented here

This repo now keeps the adaptation small:

- this document records the repo-specific efficiency rules
- a lightweight local Claude skill points agents to these rules when a task is broad or context-hungry

That is the useful part. The rest is best kept as optional reference material.
