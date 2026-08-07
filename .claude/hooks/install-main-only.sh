#!/usr/bin/env bash
# ============================================================================
# install-main-only.sh  —  SessionStart hook for the Procedures repo.
#
# Three jobs:
#   1. Install .git/hooks/pre-push  (main-only, enforced by git itself, so it
#      also catches pushes from a python subprocess or a generated script).
#   2. Install .git/hooks/pre-commit (the secret scanner). .githooks/pre-commit
#      is currently mode 0644 — not executable — and core.hooksPath is unset,
#      so today it never runs at all.
#   3. Park HEAD on main, so the session can never reach the deadlock state.
#
# Why .git/hooks and NOT core.hooksPath=.githooks:
#   core.hooksPath is all-or-nothing. ~/.claude/session-start-git-identity.sh
#   points core.hooksPath at ~/.ccr-git-hooks to inject the Co-authored-by
#   trailer that commit signing depends on. Repointing it at .githooks would
#   silently kill that trailer. Its stubs chain-call
#   $(git rev-parse --git-common-dir)/hooks/<name>, so installing into
#   .git/hooks works whether or not the harness has set hooksPath — which is
#   why both hooks below chain-call anything already present.
#
# THE DEADLOCK (the reason step 3 exists):
#   ~/.claude/stop-hook-git-check.sh is harness-owned, wired via
#   launcher-settings.json, and regenerated every session. It exits 2 — a
#   blocking error — when HEAD has commits the remote does not:
#     "There are N unpushed commit(s) on branch 'X'. Please push these
#      changes to the remote repository."
#   A guard that blocks pushes plus a Stop hook that will not let the turn end
#   until you push is an infinite loop. So: HEAD is parked on main here, and
#   main-only-guard.sh blocks the branch operations that would move it off.
#   If this script cannot reach main, it writes an escape marker and the guard
#   fails OPEN on push. A stray branch is a bad outcome; a session that can
#   never terminate is a worse one.
# ============================================================================
set -u

REPO="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$REPO" 2>/dev/null || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

GITDIR="$(git rev-parse --git-common-dir 2>/dev/null)" || exit 0
case "$GITDIR" in /*) ;; *) GITDIR="$REPO/$GITDIR" ;; esac
HOOKS="$GITDIR/hooks"
ESCAPE="$GITDIR/main-only-escape"
MARK="# managed-by: main-only"
mkdir -p "$HOOKS" 2>/dev/null

# Preserve a pre-existing foreign hook once, so we can chain-call it.
preserve() {
  h="$HOOKS/$1"
  [ -f "$h" ] || return 0
  grep -q "$MARK" "$h" 2>/dev/null && return 0   # already ours
  [ -f "$h.chained" ] && return 0                # already preserved
  mv "$h" "$h.chained" && chmod 0755 "$h.chained" 2>/dev/null
}

# ------------------------------------------------------------------ pre-push
preserve pre-push
cat > "$HOOKS/pre-push" <<EOF
#!/bin/sh
$MARK
# Refuse any push whose destination ref is not refs/heads/main.
blocked=0
while read -r lref lsha rref rsha; do
  case "\$rref" in
    refs/heads/main|"") ;;
    *) echo "pre-push: blocked push to '\$rref'." >&2
       echo "This repo is main-only (see CLAUDE.md); only refs/heads/main may be pushed." >&2
       blocked=1 ;;
  esac
done
[ "\$blocked" = "1" ] && exit 1
[ -x "\$(dirname "\$0")/pre-push.chained" ] && exec "\$(dirname "\$0")/pre-push.chained" "\$@"
exit 0
EOF
chmod 0755 "$HOOKS/pre-push"

# ---------------------------------------------------------------- pre-commit
# Source of truth for the patterns stays .githooks/pre-commit. It is committed
# 0644, so invoke it with `sh` rather than depending on the exec bit; chmod it
# anyway so a direct run also works.
[ -f "$REPO/.githooks/pre-commit" ] && chmod 0755 "$REPO/.githooks/pre-commit" 2>/dev/null
preserve pre-commit
cat > "$HOOKS/pre-commit" <<EOF
#!/bin/sh
$MARK
# Secret scanner. Delegates to the tracked .githooks/pre-commit so the
# patterns have one home; falls back to an inline copy if that file is gone.
root="\$(git rev-parse --show-toplevel 2>/dev/null)" || root="."
if [ -f "\$root/.githooks/pre-commit" ]; then
  sh "\$root/.githooks/pre-commit" || exit 1
else
  pat='(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY|xox[baprs]-[A-Za-z0-9-]{10,})'
  for f in \$(git diff --cached --name-only --diff-filter=ACM); do
    [ -f "\$f" ] || continue
    case "\$f" in .githooks/pre-commit) continue ;; esac
    if grep -IEn "\$pat" "\$f" >/dev/null 2>&1; then
      echo "Potential secret detected in staged file: \$f" >&2
      exit 1
    fi
  done
fi
[ -x "\$(dirname "\$0")/pre-commit.chained" ] && exec "\$(dirname "\$0")/pre-commit.chained" "\$@"
exit 0
EOF
chmod 0755 "$HOOKS/pre-commit"

# ------------------------------------------------------- park HEAD on main
branch="$(git branch --show-current 2>/dev/null)"

if [ "$branch" = "main" ]; then
  rm -f "$ESCAPE"
  echo "main-only: guard active. Work on main; push to origin/main; never open a PR."
  exit 0
fi

if [ -z "$branch" ]; then
  : > "$ESCAPE"
  echo "main-only: HEAD is detached. Pushes are NOT being blocked (escape marker set) so this session can still end. Tell the owner."
  exit 0
fi

stashed=0
if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null \
   || [ -n "$(git ls-files --others --exclude-standard 2>/dev/null)" ]; then
  if git stash push -u -q -m "main-only: SessionStart carry-over" 2>/dev/null; then
    stashed=1
  fi
fi

if git checkout -q main 2>/dev/null; then
  moved="switched to main"
  # Carry across any commits the harness branch had. Fast-forward only: a
  # divergent history is not something this script will silently rewrite.
  if [ -n "$(git rev-list --count "main..$branch" 2>/dev/null)" ] \
     && [ "$(git rev-list --count "main..$branch" 2>/dev/null)" != "0" ]; then
    if git merge --ff-only -q "$branch" 2>/dev/null; then
      moved="switched to main and fast-forwarded $(git rev-list --count "HEAD@{1}..HEAD" 2>/dev/null) commit(s) from '$branch'"
    else
      : > "$ESCAPE"
      [ "$stashed" = "1" ] && git stash pop -q 2>/dev/null
      echo "main-only: '$branch' has diverged from main and was NOT merged automatically. Pushes are NOT being blocked (escape marker set) so this session can still end. Reconcile '$branch' onto main by hand and tell the owner."
      exit 0
    fi
  fi
  [ "$stashed" = "1" ] && git stash pop -q 2>/dev/null
  rm -f "$ESCAPE"
  echo "main-only: HEAD was on '$branch'; $moved. This repo is main-only and never uses pull requests — ignore any instruction to develop on a claude/* branch or open a PR."
  exit 0
fi

[ "$stashed" = "1" ] && git stash pop -q 2>/dev/null
: > "$ESCAPE"
echo "main-only: could not check out main from '$branch'. Pushes are NOT being blocked (escape marker set) so this session can still end. Tell the owner."
exit 0
