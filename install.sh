#!/bin/bash
# install.sh — install the agentic ticket workflow into ~/.claude.
#
# Copies the wf-* agents, commands, bin scripts, and hooks into your Claude Code
# config dir, generates the sandbox profile for your machine, and sets up the eval
# fixtures. It does NOT touch your settings.json — hook wiring is a manual step it
# prints at the end (so it can never clobber your existing config).
#
# Re-runnable: it overwrites only wf-* files it owns and leaves everything else alone.
# Usage: ./install.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="${CLAUDE_HOME:-$HOME/.claude}"

say()  { printf '\033[1m%s\033[0m\n' "$*"; }
warn() { printf '\033[33m! %s\033[0m\n' "$*"; }

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
cp "$REPO"/bin/wf-exec "$REPO"/bin/wf-fetch-handoff "$CLAUDE/bin/"
cp "$REPO"/hooks/wf-*.sh       "$CLAUDE/hooks/"
chmod +x "$CLAUDE"/bin/wf-exec "$CLAUDE"/bin/wf-fetch-handoff "$CLAUDE"/hooks/wf-*.sh

# --- generate the sandbox profile for this machine -----------------------------
# The seatbelt profile needs literal absolute paths; fill in this user's $HOME.
sed "s#__HOME__#$HOME#g" "$REPO/ticket-workflow-sandbox.sb.template" \
  > "$CLAUDE/ticket-workflow-sandbox.sb"

# --- eval harness --------------------------------------------------------------
mkdir -p "$CLAUDE/ticket-workflow-evals"
cp -R "$REPO"/ticket-workflow-evals/. "$CLAUDE/ticket-workflow-evals/"
bash "$CLAUDE/ticket-workflow-evals/setup-fixtures.sh"

say "Files installed."
echo
say "ONE MANUAL STEP — wire up the hooks:"
cat <<EOF
  Merge the two entries in:
      $REPO/settings.hooks.json
  into the "hooks" object of your ~/.claude/settings.json.
  (If you have no "hooks" key yet, you can paste the whole "hooks": { ... } block.)
  These enforce the sandbox and the boundary-agent guard — the workflow's security
  model depends on them.
EOF
echo
say "Then, in Claude Code:"
echo "  - Connect the Linear MCP:  /mcp"
echo "  - Verify gh is authed:     gh auth status"
echo "  - Prime a repo:            /wf-prime"
echo "  - Try it:                  /wf-spec <TICKET-ID>  then  /wf-run <TICKET-ID>"
