#!/usr/bin/env bash
# ============================================================================
# main-only-guard.sh  —  PreToolUse guard for the Procedures repo.
#
# POLICY: work on main, push to origin/main, never open a pull request.
#
# This is THE control, not defence in depth. The live session's --allowed-tools
# blanket-allows bare `Bash` and `mcp__github__*`, so anything this hook misses
# does not fall through to a permission prompt — it falls through to RUN.
# It therefore denies by default and allows only push forms it can prove are
# main-only.
#
# It exits 2 rather than emitting {"permissionDecision":"deny"}. Both block,
# but only exit 2 is documented to stop the call BEFORE permission rules are
# evaluated, which is what beats a blanket `Bash` allow rule.
#
# Self-contained on purpose: one file to checksum in CI, and no sibling .py
# that could be deleted while this file survives. No filename here may contain
# ".local" — .gitignore lines 35-36 are `*.local` and `*.local.*`, so a
# settings.local.json or guard.local.sh would work in-container and silently
# not exist on the next fresh clone.
# ============================================================================
GUARD_PY=$(cat <<'PYEOF'
import json, os, re, subprocess, sys

MAIN = "main"
ALLOWED_REMOTES = {"origin"}
ESCAPE = "main-only-escape"

def block(msg):
    sys.stderr.write("main-only guard: " + msg + "\n")
    sys.exit(2)

def ok():
    sys.exit(0)

try:
    data = json.load(sys.stdin)
except Exception:
    block("could not parse the PreToolUse payload; refusing to fail open.")

tool = data.get("tool_name") or ""
ti = data.get("tool_input") or {}
cwd = data.get("cwd") or os.getcwd()

def git(*a, repo=None):
    try:
        r = subprocess.run(("git",) + a, capture_output=True, text=True,
                           cwd=repo or cwd, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""

# --------------------------------------------------------------- guard files
# Paths whose modification would disarm this apparatus for the NEXT session.
# Hooks are snapshotted at session start so a session cannot un-hook itself
# mid-flight, but these are tracked files it can edit and commit.
PROTECTED = (".claude/settings.json", ".claude/hooks", ".git/hooks",
             ".githooks", "main-only-guard", "install-main-only",
             "main-only-escape")

# ------------------------------------------------------- non-Bash tool gates
PR_TOOL = re.compile(
    r"(?:^|__)(?:create_pull_request\w*|update_pull_request\w*"
    r"|merge_pull_request|enable_pr_auto_merge|request_copilot_review"
    r"|create_branch|push_files|fork_repository|create_or_update_file"
    r"|delete_file)$")

if PR_TOOL.search(tool):
    block("'%s' opens a pull request or writes to a branch without git. "
          "This repo is main-only and never uses pull requests." % tool)

if tool in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
    p = (ti.get("file_path") or ti.get("notebook_path") or "").replace("\\", "/")
    if any(x in p for x in PROTECTED):
        block("refusing to modify '%s'. That file is the main-only guard "
              "itself; changing it would disarm the next session. Raise it "
              "with the owner instead." % p)
    ok()

if tool != "Bash":
    ok()

command = (ti.get("command") or "").strip()
if not command:
    ok()

# ------------------------------------------------------------ normalisation
# Strip quote characters so `g''it push` and `"git" push` tokenise like the
# real thing, then split on every separator Claude Code treats as a command
# boundary. Splitting naively (inside strings too) only ever produces MORE
# fragments to inspect, which is the safe direction.
# Heredoc bodies are stdin data, not commands: `git commit -F - <<MSG` carries
# prose that happens to contain the words git and push, and parsing it as shell
# refused every commit message describing this guard. Dropped before splitting
# -- EXCEPT when the heredoc feeds a shell or interpreter, where the body
# really is executed and must still be inspected.
EXECUTES_STDIN = re.compile(
    r"(^|[|&;=(\s])(ba|z|k|da|fi)?sh\b|(^|[|&;(\s])(python3?|perl|ruby|node|"
    r"xargs|env|eval|source)\b")

def strip_heredocs(cmd):
    lines = cmd.split("\n")
    out, i = [], 0
    opener = re.compile(r"<<-?\s*([\'\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
    while i < len(lines):
        line = lines[i]
        m = opener.search(line)
        i += 1
        if not m:
            out.append(line)
            continue
        # Only the command immediately before `<<` receives the body. Testing
        # the whole line misfires on an unrelated shell earlier in a pipeline.
        reader = re.split(r"&&|\|\||;|\|", line[:m.start()])[-1]
        if EXECUTES_STDIN.search(reader):
            # A shell or interpreter is reading this body, so it really does
            # execute. Leave everything intact and inspect it as commands.
            out.append(line)
            continue
        out.append(opener.sub("", line))
        delim = m.group(2)
        while i < len(lines) and lines[i].strip() != delim:
            i += 1
        i += 1
    return "\n".join(out)

flat = re.sub(r"\s+", " ", strip_heredocs(command).replace("\\\n", " ")).strip()
dequoted = flat.replace("'", "").replace('"', "")
segments = [s.strip() for s in re.split(r"&&|\|\||;|\|&|\||&|\n", dequoted)
            if s.strip()]

GIT_OPT_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace",
                 "--exec-path", "--super-prefix", "--config-env"}
# Prefixes that are transparent: the real command follows.
PASS_WRAPPERS = {"sudo", "env", "command", "nohup", "nice", "ionice", "time",
                 "timeout", "stdbuf", "builtin", "exec"}
# Read-only commands that may name a protected path.
READ_CMDS = {"cat", "less", "more", "head", "tail", "grep", "rg", "egrep",
             "ls", "stat", "wc", "diff", "file", "find", "md5sum", "sha256sum",
             "awk", "sed", "cut", "sort", "uniq", "python3", "python"}
GIT_READ_SUBS = {"diff", "show", "log", "status", "cat-file", "ls-files",
                 "rev-parse", "config", "for-each-ref", "show-ref", "blame",
                 # `commit` records already-staged content; it cannot modify a
                 # guard file. It is here because whitespace is collapsed
                 # before splitting, so a heredoc commit message arrives as one
                 # segment starting `git commit`, and any message that
                 # documents a change to the guard was refused as if it were
                 # editing it. `git add <path>` remains the gate that blocks.
                 "commit"}

GIT_BUILTINS = {
    "add", "am", "annotate", "apply", "archive", "bisect", "blame", "bundle",
    "cat-file", "check-attr", "check-ignore", "checkout", "cherry",
    "cherry-pick", "clean", "clone", "commit", "config", "count-objects",
    "describe", "diff", "difftool", "fetch", "for-each-ref", "format-patch",
    "fsck", "gc", "grep", "hash-object", "help", "init", "log", "ls-files",
    "ls-remote", "ls-tree", "maintenance", "merge", "merge-base", "mktree",
    "mv", "name-rev", "notes", "pull", "range-diff", "rebase", "reflog",
    "remote", "repack", "replace", "rerere", "reset", "restore", "rev-list",
    "rev-parse", "revert", "rm", "shortlog", "show", "show-ref",
    "sparse-checkout", "stash", "status", "stripspace", "submodule", "switch",
    "symbolic-ref", "tag", "update-index", "update-ref", "var",
    "verify-commit", "verify-pack", "version", "whatchanged", "worktree",
    "write-tree", "branch", "push", "gui", "citool", "instaweb",
}

def escape_active():
    d = git("rev-parse", "--git-common-dir")
    if not d:
        return False
    if not os.path.isabs(d):
        d = os.path.join(cwd, d)
    return os.path.exists(os.path.join(d, ESCAPE))

def refname(s):
    return re.sub(r"^refs/heads/", "", s.lstrip("+"))

def resolve_git(tokens):
    """(subcommand, args, inline_aliases) or None if not a plain git call."""
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t):
            # GIT_DIR=/elsewhere relocates the repo out from under us.
            if t.split("=")[0].startswith(("GIT_DIR", "GIT_WORK_TREE",
                                           "GIT_CONFIG", "GIT_OBJECT",
                                           "GIT_COMMON_DIR", "GIT_INDEX")):
                block("this command relocates the git repository via %s. "
                      "Run the plain form from the repo root." % t.split("=")[0])
            i += 1
            continue
        if os.path.basename(t) in PASS_WRAPPERS:
            i += 1
            while i < len(tokens) and (tokens[i].startswith("-") or
                                       re.match(r"^[0-9.]+[smhd]?$", tokens[i])):
                i += 1
            continue
        break
    if i >= len(tokens) or os.path.basename(tokens[i]) != "git":
        return None
    i += 1
    aliases = {}
    while i < len(tokens) and tokens[i].startswith("-"):
        t = tokens[i]
        if "=" in t and not t.startswith("--"):
            i += 1
            continue
        if t in GIT_OPT_VALUE:
            if i + 1 < len(tokens):
                v = tokens[i + 1]
                if t == "-c" and v.startswith("alias."):
                    k, _, expansion = v.partition("=")
                    aliases[k[len("alias."):]] = expansion
                if t in ("-C", "--git-dir", "--work-tree") and v not in (".", "./"):
                    block("this command retargets git at '%s'. Run it from "
                          "the repository root without -C/--git-dir." % v)
            i += 2
            continue
        name, eq, val = t.partition("=")
        if eq and name in ("--git-dir", "--work-tree") and val not in (".", "./", ".git"):
            block("this command retargets git at '%s'." % val)
        i += 1
    if i >= len(tokens):
        return None
    return tokens[i], tokens[i + 1:], aliases

def as_push(sub, aliases):
    """Resolve a subcommand through inline and configured aliases."""
    seen = set()
    cur = sub
    for _ in range(5):
        if cur == "push":
            return True, cur
        if cur in seen:
            break
        seen.add(cur)
        exp = aliases.get(cur) or git("config", "--get", "alias." + cur)
        if not exp:
            break
        cur = exp.split()[0] if exp.split() else ""
        if cur.startswith("!"):
            return True, cur   # shell alias: unknowable, treat as push
    return (cur == "push"), cur

for seg in segments:
    tokens = seg.split()
    if not tokens:
        continue
    low = seg.lower()

    # ------------------------------------------- tampering with the guard
    if any(x in seg for x in PROTECTED):
        base = os.path.basename(tokens[0])
        is_read = base in READ_CMDS and not re.search(r">|>>|-i\b", seg)
        if base == "git":
            r = resolve_git(tokens)
            is_read = bool(r) and r[0] in GIT_READ_SUBS
        if not is_read:
            block("this command writes to or removes part of the main-only "
                  "guard (%s). Refusing: that would disarm the next session."
                  % seg[:70])
        continue

    # ------------------------------------------------ pull-request creation
    if re.search(r"\bgh\s+pr\s+(create|ready|reopen|merge)\b", low):
        block("pull requests are never used in this repo. Commit on main and "
              "push to origin/main.")
    if re.search(r"\bgh\s+api\b", low) and "pulls" in low:
        block("this creates or modifies a pull request via the GitHub API.")
    if re.search(r"api\.github\.com/repos/[^ ]+/pulls", low):
        block("this creates a pull request via the GitHub API.")

    mentions_git = re.search(r"\bgit\b", low) is not None
    mentions_push = "push" in low

    resolved = resolve_git(tokens)

    if resolved is None:
        # Not a plain git invocation. If it still smells of pushing — a nested
        # shell, xargs, a python subprocess, a script it just wrote — we
        # cannot verify it, so we refuse it.
        if mentions_git and mentions_push:
            block("cannot verify this is a main-only push: git is being "
                  "invoked indirectly (nested shell, xargs, subprocess, or a "
                  "generated script). Run the plain form: "
                  "'git push origin main'.")
        continue

    sub, args, aliases = resolved

    if "$" in sub or "`" in sub:
        block("the git subcommand is supplied by a shell variable or "
              "substitution ('%s'), so it cannot be verified. Run the plain "
              "form." % sub)

    # ------------------------------------------------ branch creation/moves
    if sub in ("checkout", "switch", "branch", "worktree"):
        for a in args:
            if a.startswith("-"):
                continue
            if refname(a).startswith("claude/"):
                block("'%s' is a harness branch. This repo is main-only: "
                      "work on main. Moving onto or creating a claude/* "
                      "branch also strands commits that can never be pushed, "
                      "which deadlocks the session against the harness Stop "
                      "hook." % refname(a))
        continue

    if sub == "remote" and any(a in ("add", "set-url") for a in args):
        block("changing where pushes go is not permitted; origin must stay "
              "the only push target.")

    is_push, resolved_name = as_push(sub, aliases)
    if not is_push:
        if sub in GIT_BUILTINS:
            continue
        block("unrecognised git subcommand '%s'. If it is an alias, it could "
              "expand to a push, so it is refused rather than guessed at."
              % sub)

    # ------------------------------------------------------------- pushes
    if escape_active():
        sys.stderr.write(
            "main-only: escape marker present — allowing this push so the "
            "session can terminate. HEAD could not be parked on main "
            "automatically; tell the owner.\n")
        continue

    if any(a in ("--all", "--mirror", "--prune") for a in args):
        block("'git push %s' publishes or deletes refs beyond main. "
              "Push only main: 'git push origin main'."
              % next(a for a in args if a in ("--all", "--mirror", "--prune")))
    if "--delete" in args or "-d" in args:
        block("refusing to delete remote refs. Branch cleanup is handled "
              "server-side by .github/workflows/main-only-policy.yml.")

    positional, skip = [], False
    for a in args:
        if skip:
            skip = False
            continue
        if a in ("-o", "--push-option", "--repo", "--receive-pack", "--exec"):
            skip = True
            continue
        if a.startswith("-"):
            continue
        positional.append(a)

    remote = positional[0] if positional else "origin"
    if remote not in ALLOWED_REMOTES:
        block("push target '%s' is not origin. A second remote (or a bare "
              "URL) can carry a branch off-policy even when the ref is "
              "called main." % remote)

    current = git("branch", "--show-current")
    refspecs = positional[1:]

    if not refspecs:
        if current != MAIN:
            block("HEAD is on '%s', not main. This repo is main-only. Move "
                  "the work onto main first: 'git checkout main && git merge "
                  "--ff-only %s && git push origin main'." % (current, current))
        continue

    for rs in refspecs:
        if re.search(r"[*$`?\[]", rs):
            block("refspec '%s' is a wildcard or is built by the shell, so "
                  "the refs it would push cannot be enumerated." % rs)
        src, sep, dst = rs.partition(":")
        target = refname(dst) if sep else refname(src)
        if target in ("HEAD", ""):
            target = current
        if target != MAIN:
            block("this push targets '%s'. Only origin/main may be pushed "
                  "(see CLAUDE.md); pull requests are never used." % target)
        source = refname(src) if sep else target
        if source in ("HEAD", ""):
            source = current
        if sep and source != MAIN:
            block("refusing to push '%s' onto main. Merge it into local main "
                  "first, then push main." % source)

ok()
PYEOF
)
exec python3 -c "$GUARD_PY"
