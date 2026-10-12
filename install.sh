#!/bin/bash
# install.sh — install the agentic ticket workflow into ~/.claude.
#
# Copies the wf-* agents, commands, bin scripts, and hooks into your Claude Code
# config dir, generates the sandbox profile for your machine, and sets up the eval
# fixtures. It does NOT touch your settings.json — hook wiring stays a manual step
# (so it can never clobber your existing config), but the installer now DETECTS
# whether the two guard hooks are wired and warns loudly until they are.
#
# Re-runnable: it overwrites only wf-* files it owns and leaves everything else alone.
# Usage: ./install.sh [--enable-tick <repo-path> | --disable-tick <repo-path>]
#   --enable-tick  also schedule an unattended /wf-tick sweep for that repo (one launchd agent per repo,
#                  every 300 s). Nothing is scheduled unless you ask. --disable-tick removes it.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="${CLAUDE_HOME:-$HOME/.claude}"

say()  { printf '\033[1m%s\033[0m\n' "$*"; }
warn() { printf '\033[33m! %s\033[0m\n' "$*"; }
err()  { printf '\033[1;31m!! %s\033[0m\n' "$*"; }

usage() { echo "usage: ./install.sh [--enable-tick <repo-path> | --disable-tick <repo-path>]" >&2; exit 2; }

# --- optional unattended-tick flags (parsed first; plain ./install.sh never touches launchd) ---
TICK_MODE=""; TICK_PATH=""
case "${1:-}" in
  "")                            ;;
  --enable-tick|--disable-tick)  [ $# -eq 2 ] || usage; TICK_MODE="${1#--}"; TICK_PATH="$2" ;;
  *)                             usage ;;
esac

# Per-repo key: readable basename + path hash (two repos can share a basename).
# KEEP IN SYNC with the KEY derivation in bin/wf-tick — log, lock and launchd label all derive from it.
tick_key() { printf '%s' "${1##*/}" | tr -c 'A-Za-z0-9._-' '_'; printf -- '-%s' "$(printf '%s' "$1" | shasum | cut -c1-8)"; }

if [ -n "$TICK_MODE" ]; then
  if [ "$TICK_MODE" = disable-tick ]; then
    # The repo may be gone by now; fall back to the path as given.
    TICK_REPO="$(git -C "$TICK_PATH" rev-parse --show-toplevel 2>/dev/null || (cd "$TICK_PATH" 2>/dev/null && pwd) || echo "$TICK_PATH")"
  else
    TICK_REPO="$(git -C "$TICK_PATH" rev-parse --show-toplevel)" || { err "not a git repo: $TICK_PATH"; exit 1; }
  fi
  TICK_KEY="$(tick_key "$TICK_REPO")"
  TICK_LABEL="com.wayfinder.wf-tick.$TICK_KEY"
  TICK_PLIST="$HOME/Library/LaunchAgents/$TICK_LABEL.plist"
fi

if [ "$TICK_MODE" = disable-tick ]; then
  # Runs before the copy step: disabling must not require (or perform) a reinstall.
  launchctl bootout "gui/$(id -u)/$TICK_LABEL" 2>/dev/null || true
  if [ -f "$TICK_PLIST" ]; then rm -f "$TICK_PLIST"; say "Removed $TICK_LABEL"; else say "Tick not enabled for $TICK_REPO"; fi
  exit 0
fi

say "Installing Wayfinder into $CLAUDE"

# --- platform + dependency checks (warn, don't block) --------------------------
if [ "$(uname)" != "Darwin" ]; then
  warn "Not macOS: the execution sandbox uses macOS 'sandbox-exec' (seatbelt) and"
  warn "will not work here. The agents/commands still install, but /wf-run's"
  warn "sandboxed test/build execution is macOS-only. See README > Platform support."
fi
for dep in git jq gh; do
  command -v "$dep" >/dev/null 2>&1 || warn "missing dependency: $dep (see README > Prerequisites)"
done
command -v node    >/dev/null 2>&1 || warn "node not found — the node eval fixture won't run"
command -v python3 >/dev/null 2>&1 || warn "python3 not found — the py eval fixture won't run"

# --- copy the pieces -----------------------------------------------------------
mkdir -p "$CLAUDE"/{agents,commands,bin,hooks}

cp "$REPO"/agents/wf-*.md      "$CLAUDE/agents/"
cp "$REPO"/commands/wf-*.md    "$CLAUDE/commands/"
cp "$REPO"/bin/wf-exec "$REPO"/bin/wf-fetch-handoff "$REPO"/bin/wf-tick "$CLAUDE/bin/"
cp "$REPO"/hooks/wf-*.sh       "$CLAUDE/hooks/"
chmod +x "$CLAUDE"/bin/wf-exec "$CLAUDE"/bin/wf-fetch-handoff "$CLAUDE"/bin/wf-tick "$CLAUDE"/hooks/wf-*.sh

# --- generate the sandbox profile for this machine -----------------------------
# The seatbelt profile needs literal absolute paths; fill in this machine's dirs —
# __HOME__ = your home, __CLAUDE__ = the Claude config dir (CLAUDE_HOME may relocate it).
sed -e "s#__CLAUDE__#$CLAUDE#g" -e "s#__HOME__#$HOME#g" "$REPO/ticket-workflow-sandbox.sb.template" \
  > "$CLAUDE/ticket-workflow-sandbox.sb"

# --- learned-gaps data log (append-only; never clobber an existing one) ---------
# wf-spec-builder reads this as reference examples; /wf-run appends to it when a planner
# reports SPEC_GAPS. It holds ticket-derived text, so it is DATA, never an agent prompt —
# seed it empty, once, and leave any existing log (a user's accumulated history) untouched.
[ -f "$CLAUDE/wf-spec-gaps.md" ] || cp "$REPO/wf-spec-gaps.md" "$CLAUDE/wf-spec-gaps.md"

# --- eval harness --------------------------------------------------------------
mkdir -p "$CLAUDE/ticket-workflow-evals"
cp -R "$REPO"/ticket-workflow-evals/. "$CLAUDE/ticket-workflow-evals/"
bash "$CLAUDE/ticket-workflow-evals/setup-fixtures.sh"

say "Files installed."
echo

# --- hook wiring check (detect-and-warn; never touches settings.json) ----------
# The guards are the workflow's enforcement layer: the PreToolUse hook blocks
# unsandboxed project commands in worktrees, the SubagentStop hook blocks
# boundary agents that answer without making a tool call. The workflow RUNS
# without them (agents follow their prompts voluntarily), so a skipped wiring
# step fails silently — this check makes that state loud on every install run.
SETTINGS="$CLAUDE/settings.json"
hooks_wired=false
if command -v jq >/dev/null 2>&1 && [ -f "$SETTINGS" ] && jq -e . "$SETTINGS" >/dev/null 2>&1; then
  if jq -e '.hooks.PreToolUse[]?.hooks[]?.command | select(contains("wf-sandbox-guard.sh"))' "$SETTINGS" >/dev/null 2>&1 \
  && jq -e '.hooks.SubagentStop[]?.hooks[]?.command | select(contains("wf-boundary-toolcall-guard.sh"))' "$SETTINGS" >/dev/null 2>&1; then
    hooks_wired=true
  fi
fi

if [ "$hooks_wired" = true ]; then
  say "Guard hooks: wired in $SETTINGS — sandbox + boundary enforcement active."
else
  err "GUARD HOOKS NOT WIRED — the workflow's security model is NOT enforced."
  err "Nothing currently blocks unsandboxed project commands in worktrees, or a"
  err "boundary agent fabricating an answer without a real API call. Fix it now:"
  cat <<EOF
  Merge the two entries in:
      $REPO/settings.hooks.json
  into the "hooks" object of:
      $SETTINGS
  (If you have no "hooks" key yet, you can paste the whole "hooks": { ... } block.)
  Then re-run ./install.sh — this warning repeats until both hooks are detected.
EOF
fi
echo

# --- optional: schedule the unattended tick for one repo (launchd, macOS) ---------
if [ "$TICK_MODE" = enable-tick ]; then
  [ "$(uname)" = Darwin ] || { err "--enable-tick needs macOS launchd"; exit 1; }
  command -v claude >/dev/null 2>&1 || { err "--enable-tick needs the claude CLI on PATH"; exit 1; }

  TICK_MANUAL="$(ls "$TICK_REPO"/CONTEXT.md "$TICK_REPO"/CLAUDE.md "$TICK_REPO"/AGENTS.md 2>/dev/null | head -n 1)"
  # Uncommented 'enabled: true' under '## Automation' (lines inside <!-- --> don't count).
  if [ -z "$TICK_MANUAL" ] || ! awk '
        /<!--/ { c = 1 } c { if (/-->/) c = 0; next }
        /^## /  { a = ($0 ~ /^## Automation/) }
        a && /^- *enabled: *true/ { f = 1 }
        END { exit !f }' "$TICK_MANUAL"; then
    warn "$TICK_REPO has no uncommented 'enabled: true' under '## Automation' — ticks will no-op until you add it."
  fi

  # launchd starts jobs with a minimal PATH; give it the dir of 'claude' plus this shell's PATH.
  TICK_PATHENV="$(dirname "$(command -v claude)"):$PATH"
  xml() { printf '%s' "$1" | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'; }
  TICK_LOG="$CLAUDE/wf-tick/logs/$TICK_KEY.launchd.log"
  mkdir -p "$HOME/Library/LaunchAgents" "$CLAUDE/wf-tick/logs"

  cat >"$TICK_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$(xml "$TICK_LABEL")</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$(xml "$CLAUDE/bin/wf-tick")</string>
    <string>$(xml "$TICK_REPO")</string>
  </array>
  <key>StartInterval</key><integer>300</integer>
  <key>RunAtLoad</key><false/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>$(xml "$TICK_PATHENV")</string>
    <key>HOME</key><string>$(xml "$HOME")</string>
    <key>CLAUDE_HOME</key><string>$(xml "$CLAUDE")</string>
  </dict>
  <key>StandardOutPath</key><string>$(xml "$TICK_LOG")</string>
  <key>StandardErrorPath</key><string>$(xml "$TICK_LOG")</string>
</dict>
</plist>
PLIST
  plutil -lint "$TICK_PLIST" >/dev/null || { err "generated plist is invalid: $TICK_PLIST"; exit 1; }

  launchctl bootout "gui/$(id -u)/$TICK_LABEL" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$TICK_PLIST"
  say "Tick enabled: $TICK_LABEL (every 300 s) for $TICK_REPO"
  echo "  log: $CLAUDE/wf-tick/logs/$TICK_KEY.log"
  echo "  Ticks run with your existing Claude Code permission settings and must not need prompts"
  echo "  (claude -p cannot answer them) — pre-approve what /wf-spec and /wf-run need."
  echo
fi

say "Then, in Claude Code:"
echo "  - Connect the Linear MCP:  /mcp"
echo "  - Verify gh is authed:     gh auth status"
echo "  - Prime a repo:            /wf-prime"
echo "  - Try it:                  /wf-spec <TICKET-ID>  then  /wf-run <TICKET-ID>"
