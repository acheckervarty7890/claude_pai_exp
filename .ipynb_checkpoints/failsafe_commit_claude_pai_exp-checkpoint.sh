#!/usr/bin/env bash
#
# failsafe_commit_claude_pai_exp.sh — periodically commit + push EVERYTHING in a
# claude_pai_exp checkout so work survives the container being wiped.
#
# Much simpler than this repo's failsafe_commit.sh: there are no stages, no
# markers and no finish signal to detect. It just snapshots the whole working
# tree on a timer until you stop it.
#
# WHAT IS COMMITTED
#   Everything under the repo root, force-added — so the run outputs .gitignore
#   hides (*.log, *.baseline.pkl, *.baseline.csv, .claude/settings.local.json)
#   ARE captured. That is the point: those are the artifacts a wiped container
#   would otherwise lose.
#
# WHAT IS EXCLUDED  (and why — the first two are the ones you asked for, the
# rest would break or leak if force-added)
#   kaggle.json     Kaggle API credentials.       <- requested
#   *.pt / *.pth    Activation blobs; GBs each.   <- requested
#   .venv/          The virtualenv: ~GBs, tens of thousands of files, and
#                   rebuildable from setup_env_claude_pai_exp.sh.
#   __pycache__/    Build noise.
#   *.pyc           Build noise.
#   .env            Holds HF_TOKEN. .gitignore excludes it deliberately, and a
#                   force-add would push the secret to the remote. Override with
#                   --include-env if you really want it committed.
#   >30 MB files    Any single file over --max-size-mb (default 30) is dropped
#                   from the commit, whatever its name. The name-based rules
#                   above only catch the big artifacts we already know about;
#                   this catches the ones we don't, before a 2 GB checkpoint
#                   ends up permanently in the repo history (GitHub rejects a
#                   push over 100 MB per file outright, which would strand every
#                   later snapshot too). The check is on the file as it is on
#                   disk, so deletions are never blocked, and a file that was
#                   committed while small simply stops being updated once it
#                   grows past the limit.
#
# The exclusions are applied TWICE on purpose: directory pathspecs keep the big
# trees out of the index in the first place (staging .venv then unstaging it
# would still walk every file), and a `git reset` of the file globs afterwards
# is the belt-and-suspenders pass — the same two-step this repo's
# failsafe_commit.sh uses, because an unanchored `:(exclude,glob)**/*.pt` on the
# add side silently drops every file rather than just the .pt ones.
#
# BRANCH MODEL
#   Commits and pushes onto the branch ALREADY checked out; it never creates or
#   switches branches. Make a branch for the run first if you want isolation.
#
# USAGE
#   # from anywhere (defaults to ~/Documents/claude_pai_exp)
#   nohup bash failsafe_commit_claude_pai_exp.sh > /tmp/failsafe_pai.out 2>&1 &
#
#   # one-shot snapshot, no loop
#   bash failsafe_commit_claude_pai_exp.sh --once
#
#   # different checkout / cadence / local-only
#   bash failsafe_commit_claude_pai_exp.sh --repo /path/to/claude_pai_exp \
#        --interval 300 --no-push
#
#   Stop it with Ctrl-C or `kill` — the trap takes one final snapshot first.

set -uo pipefail

REPO_ROOT="${REPO_ROOT:-/workspace/claude_pai_exp}"
REMOTE="origin"
INTERVAL=900        # seconds between snapshots
DO_PUSH=1
ONCE=0
INCLUDE_ENV=0
MAX_SIZE_MB=30      # per-file ceiling; anything bigger is left out of the commit

usage() {
    grep '^# ' "$0" | sed 's/^# \{0,1\}//'
    cat <<EOF

Flags:
  --repo DIR        claude_pai_exp checkout (default: $REPO_ROOT)
  --interval SEC    seconds between snapshots (default: $INTERVAL)
  --remote NAME     git remote to push to (default: $REMOTE)
  --no-push         commit locally only
  --once            take one snapshot and exit (no polling)
  --include-env     ALSO commit .env — it contains HF_TOKEN; off by default
  --max-size-mb N   skip any file larger than N MB (default: $MAX_SIZE_MB; 0 = no limit)
  -h, --help        show this help
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)        REPO_ROOT="$2"; shift 2;;
        --interval)    INTERVAL="$2"; shift 2;;
        --remote)      REMOTE="$2"; shift 2;;
        --no-push)     DO_PUSH=0; shift;;
        --once)        ONCE=1; shift;;
        --include-env) INCLUDE_ENV=1; shift;;
        --max-size-mb) MAX_SIZE_MB="$2"; shift 2;;
        -h|--help)     usage; exit 0;;
        *) echo "Unknown arg: $1" >&2; usage; exit 2;;
    esac
done

log() { echo "[failsafe-pai $(date '+%Y-%m-%d %H:%M:%S')] $*"; }

[[ "$MAX_SIZE_MB" =~ ^[0-9]+$ ]] || { log "ERROR: --max-size-mb wants a whole number, got '$MAX_SIZE_MB'"; exit 2; }
MAX_SIZE_BYTES=$(( MAX_SIZE_MB * 1024 * 1024 ))

[[ -d "$REPO_ROOT" ]] || { log "ERROR: no such directory: $REPO_ROOT"; exit 1; }
cd "$REPO_ROOT" || exit 1
git rev-parse --git-dir >/dev/null 2>&1 || { log "ERROR: $REPO_ROOT is not a git repo"; exit 1; }
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT" || exit 1

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
if [[ -z "$BRANCH" || "$BRANCH" == "HEAD" ]]; then
    log "ERROR: detached HEAD — check out a branch first"; exit 1
fi

# Directory pathspecs, applied at `git add` time so these trees are never walked
# into the index. A plain pathspec matches everything beneath the directory.
ADD_EXCLUDES=(
    ':(exclude).venv'
    ':(exclude)__pycache__'
)
# File globs, applied as a `git reset` after the add. Anchor-free globs are safe
# on the reset side (they are not on the add side — see the header).
RESET_EXCLUDES=(
    ':(glob)**/*.pt'
    ':(glob)**/*.pth'
    ':(glob)**/kaggle.json'
    ':(glob)**/*.pyc'
    ':(glob)**/__pycache__/**'
)
if [[ "$INCLUDE_ENV" -eq 0 ]]; then
    RESET_EXCLUDES+=(':(glob)**/.env')
else
    log "WARNING: --include-env given — .env (HF_TOKEN) WILL be committed and pushed"
fi

log "repo:     $REPO_ROOT"
log "branch:   $BRANCH$([[ "$DO_PUSH" -eq 1 ]] && echo " -> $REMOTE" || echo " (local only)")"
log "interval: $([[ "$ONCE" -eq 1 ]] && echo "one-shot" || echo "${INTERVAL}s")"
log "excluded: kaggle.json, *.pt, *.pth, .venv/, __pycache__/, *.pyc$([[ "$INCLUDE_ENV" -eq 0 ]] && echo ", .env")"
log "size cap: $([[ "$MAX_SIZE_MB" -eq 0 ]] && echo "none" || echo "${MAX_SIZE_MB} MB per file")"

# Third exclusion pass, by SIZE rather than by name. The two pathspec passes above
# only know about file types we anticipated; this one is the backstop for the ones we
# did not — a checkpoint, a merged dataset, an unexpectedly fat log. It runs on the
# staged set, so it costs one stat per changed file, not a tree walk.
#
# Deliberately reads the size from DISK, not from the index: it must not fire on
# deletions (nothing to be big) and `git diff --cached --diff-filter=d` already drops
# those. GNU stat lstat()s, so a symlink is measured as the link, which is also what
# git would store.
LAST_OVERSIZE=""
drop_oversize() {
    (( MAX_SIZE_BYTES > 0 )) || return 0
    local f sz n=0 report=""
    while IFS= read -r -d '' f; do
        [[ -f "$f" ]] || continue
        sz=$(stat -c %s -- "$f" 2>/dev/null) || continue
        (( sz > MAX_SIZE_BYTES )) || continue
        git reset -q -- "$f" >/dev/null 2>&1 || true
        n=$(( n + 1 ))
        report+="$(printf '\n    %s (%s MB)' "$f" "$(( (sz + 1048575) / 1048576 ))")"
    done < <(git diff --cached --name-only -z --diff-filter=d)

    (( n > 0 )) || { LAST_OVERSIZE=""; return 0; }
    # Report the full list when it changes, a one-liner when it is the same files
    # again — otherwise a single stranded 2 GB checkpoint reprints forever.
    if [[ "$report" != "$LAST_OVERSIZE" ]]; then
        log "skipping $n file(s) over ${MAX_SIZE_MB} MB:$report"
        LAST_OVERSIZE="$report"
    else
        log "skipping the same $n file(s) over ${MAX_SIZE_MB} MB"
    fi
}

PUSHED_UPSTREAM=0
snapshot() {
    local reason="$1"
    # Claude transcripts for this run, if this is the cloud box they live on.
    # Non-fatal everywhere else (there is no /home/ubuntu on a local checkout).
    mkdir -p conversation_history 2>/dev/null
    cp /home/ubuntu/.claude/projects/-workspace-claude-pai-exp/*jsonl \
       conversation_history/ 2>/dev/null || true
    # -A so deletions are recorded too; -f so .gitignore'd run outputs are kept.
    git add -f -A -- . "${ADD_EXCLUDES[@]}" >/dev/null 2>&1
    git reset -q -- "${RESET_EXCLUDES[@]}" >/dev/null 2>&1 || true
    drop_oversize

    if git diff --cached --quiet; then
        return 0   # nothing changed since the last snapshot
    fi

    local msg="failsafe: $reason @ $(date '+%Y-%m-%dT%H:%M:%S')"
    if ! git commit -q -m "$msg" >/dev/null 2>&1; then
        log "WARN: git commit failed ($reason)"; return 0
    fi
    log "committed: $msg  ($(git rev-parse --short HEAD))"

    [[ "$DO_PUSH" -eq 1 ]] || return 0
    local push_args=("$REMOTE" "$BRANCH")
    [[ "$PUSHED_UPSTREAM" -eq 0 ]] && push_args=(-u "$REMOTE" "$BRANCH")
    if git push -q "${push_args[@]}" >/dev/null 2>&1; then
        PUSHED_UPSTREAM=1
        log "pushed to $REMOTE/$BRANCH"
    else
        sleep 5
        if git push -q "${push_args[@]}" >/dev/null 2>&1; then
            PUSHED_UPSTREAM=1
            log "pushed to $REMOTE/$BRANCH on retry"
        else
            log "WARN: push failed; commit is local, will retry next snapshot"
        fi
    fi
}

FINALIZED=0
finalize() {
    [[ "$FINALIZED" -eq 1 ]] && return
    FINALIZED=1
    log "finalizing: capturing latest state before exit"
    snapshot "final snapshot"
    log "done."
}
trap 'finalize; exit 0' INT TERM
trap 'finalize' EXIT

snapshot "startup snapshot"
if [[ "$ONCE" -eq 1 ]]; then
    FINALIZED=1   # startup snapshot already covered it; skip the EXIT-trap repeat
    log "done (--once)."
    exit 0
fi

# Sleep in short chunks. bash defers a trap until the running foreground command
# returns, so a plain `sleep $INTERVAL` would delay the final snapshot by up to
# INTERVAL seconds after a `kill` — 15 minutes at the default, and `kill` is the
# normal way to stop a nohup'd poller. (Ctrl-C is unaffected: it signals the whole
# process group, so sleep dies with it.)
interruptible_sleep() {
    local left="$1"
    while (( left > 0 )); do
        (( left < 5 )) && { sleep "$left"; return; }
        sleep 5
        left=$(( left - 5 ))
    done
}

log "polling every ${INTERVAL}s — Ctrl-C or kill to stop (a final snapshot is taken)"
while true; do
    interruptible_sleep "$INTERVAL"
    snapshot "periodic snapshot"
done
