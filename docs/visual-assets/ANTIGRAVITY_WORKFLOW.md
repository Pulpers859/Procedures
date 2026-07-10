# Antigravity Visual Asset Workflow

Google Antigravity is a second render lane for draft procedure illustrations, alongside the Gemini API lane in `GEMINI_WORKFLOW.md`. Both lanes share the same prompt spec (`docs/visual-assets/gemini_prompts.json`), the same style standard (`docs/ai-instructions/VISUAL_ASSET_PRODUCTION_GUIDE.md`), and the same promotion rule: nothing ships without clinician review.

Antigravity is a **render lab only**. It generates and saves images. It does not score its own work, does not edit source code, and does not decide what gets bundled.

## How it works

Antigravity is a desktop app that exposes a localhost-only HTTP language server (`language_server.exe`) with an `agentapi` CLI. There is no cloud API and no stable port — the server picks a fresh port and CSRF token on every app restart, so every session starts with discovery.

Hard prerequisites:

1. The Antigravity desktop app must already be running. A human launches it once; agents cannot boot it headlessly.
2. Shell access on the same machine. Cloud or remote agents cannot reach it.

## Discovery

Never hard-code the address or token. The repo helper automates discovery (process scan, CSRF token parse, highest listening port = HTTPS port) and sets the env vars:

```powershell
.\tools\Invoke-AntigravityAgentApi.ps1 -Command PrintEnv
```

Machine-specific values (flag these when handing off to another machine):

- `ANTIGRAVITY_PROJECT_ID` env var (or `-ProjectId`). Required — `new-conversation` fails with `project_id is required` without it. The CLI cannot create or list projects; the id comes from a project created in the Antigravity app. On the current dev machine the working id (shared with the Mnemorized repo's render project) is `79655949-1be7-444b-817e-c0ecd5768c5c`; swap in a dedicated Procedures project id if one is created later.
- agentapi CLI path, default `%USERPROFILE%\.gemini\antigravity\bin\agentapi.bat` (override with `-AgentApiPath`)

Manual fallback if the helper is unavailable:

```powershell
tasklist | findstr language_server
netstat -ano | findstr <PID>          # use the HIGHER listening port
wmic process where "processid=<PID>" get CommandLine   # extract --csrf_token
```

## CLI verbs

Three verbs matter, all wrapped by the helper:

```powershell
# Start a render; returns a conversation_id — keep it.
.\tools\Invoke-AntigravityAgentApi.ps1 -Command NewConversation `
  -Title "Cric Membrane Draft 1" `
  -PromptFile "tmp\visual-drafts\antigravity\cric_membrane\01_image_prompt.txt" `
  -PassPromptFileAsAtPath

# Repair / regenerate in the same conversation.
.\tools\Invoke-AntigravityAgentApi.ps1 -Command SendMessage `
  -ConversationId "<id>" `
  -PromptFile "tmp\visual-drafts\antigravity\cric_membrane\02_repair.txt" `
  -PassPromptFileAsAtPath

# Check conversation state.
.\tools\Invoke-AntigravityAgentApi.ps1 -Command GetConversationMetadata -ConversationId "<id>"
```

**Critical gotcha:** a multi-line prompt passed as a plain string arrives as its first line only. Always write prompts to a file and pass them with `-PromptFile ... -PassPromptFileAsAtPath` (which sends `@C:\...\01_image_prompt.txt`).

Do not use the raw RPC / `StartCascade` coding-agent lane for image runs — it drifts into repo inspection instead of rendering. Use the `agentapi` chat/image lane above.

## Operating loop

1. Export the prompt file from the shared spec:

   ```powershell
   python scripts/export_antigravity_prompts.py cric_membrane
   ```

   This writes `tmp/visual-drafts/antigravity/<assetId>/01_image_prompt.txt`, including the exact save path Antigravity must use (`<assetId>_iter1.png` in the same folder).

2. `NewConversation` with the prompt file → capture the `conversation_id`.
3. Poll the topic folder for the output image.
4. The controlling agent reads the saved image itself and audits it against the rubric below. Antigravity never audits its own output — its self-audits inflate scores.
5. On FAIL: write a numbered repair file (`02_repair.txt`, `03_repair.txt`, …) stating only what must change, `SendMessage` it as an `@`-path, and instruct saving as `<assetId>_iter2.png`, etc.
6. Stop after ~5 attempts. Write a short result note (or `blocked.txt`) into the topic folder either way.

## Sandbox rules

- Antigravity writes only under `tmp/visual-drafts/antigravity/` (gitignored). Never `Procedures/`, `scripts/`, `docs/`, `tools/`, project files, or resources — and it never commits or pushes.
- The controlling agent owns prompt architecture, the audit, and all integration.
- Drafts stay out of the app bundle and out of git.

## Audit rubric

The controlling agent applies this after every render. DECISION is PASS only if every critical check passes; otherwise FAIL with a specific repair instruction.

Critical checks:

1. Every required label from the prompt spec is present, verbatim, correctly spelled. Any garbled, extra, or invented text is an automatic FAIL.
2. Anatomy is schematic, plausible, and consistent with the claims in `Procedures/Resources/procedures.json` for that procedure. No invented structures or relationships.
3. One clear teaching point — the miss this visual prevents is unmistakable at a glance.
4. Color semantics: red/orange only for danger, incision, or warning; blue/cyan for ultrasound/landmark guidance; green only for confirmation.
5. Labels readable at iPhone width; critical labels inside a safe margin; roughly 4:3 composition.
6. No gore, no photorealistic patient, no faces, no watermark, no decorative clutter.

A PASS makes the image a **reviewable draft**, nothing more. It then enters the normal pipeline: clinical review, then the promotion steps in `GEMINI_WORKFLOW.md` (move to `Procedures/Resources/Visuals`, add to the Xcode target, set `visualAssets.assetName`, run `python scripts/validate_procedures.py`). Structural validation and rubric passes never substitute for clinician approval.
