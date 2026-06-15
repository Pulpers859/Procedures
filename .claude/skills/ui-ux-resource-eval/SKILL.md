---
name: ui-ux-resource-eval
description: Evaluate external UI/UX resources, component libraries, design systems, visual reference sites, and design-oriented agent skills for the Procedures app using the repo playbook. Use when deciding whether outside UI/UX repos or websites should influence the product, when comparing design systems or component libraries, or when planning a redesign that depends on external reference sources. Do not use for routine styling tweaks or isolated visual bug fixes.
---

# Procedures UI/UX Resource Evaluation

Use this skill only for external UI/UX research and tooling decisions, not for ordinary small UI edits.

## Required Workflow

1. Read `docs/AI_UI_UX_RESOURCE_EVALUATION_PLAYBOOK.md`.
2. Inspect the actual Procedures app before making recommendations.
3. Record:
   - product purpose
   - primary users
   - critical workflows
   - target platform
   - implementation stack
   - current design maturity
   - current UI/UX weaknesses
   - technical and accessibility constraints
4. Classify the dominant need:
   - product-flow research
   - visual-direction research
   - component behavior
   - ready-made implementation
   - design-system structure
   - agent efficiency
   - quality assurance
5. Assess each resource with the repo playbook and assign one outcome:
   - `Adopt`
   - `Adapt`
   - `Reference`
   - `Skip`
6. Recommend the smallest useful non-overlapping system.

## Guardrails

- Do not inherit another app's style or platform assumptions.
- Do not recommend installing everything.
- Keep web-native inspiration from dictating iOS behavior.
- Distinguish clearly between research input and implementation authority.
- If multiple agents or machines are part of the context, follow `docs/EXTERNAL_AGENT_RECONCILIATION.md` before making sync claims.
