#!/bin/bash
# PreToolUse(Bash) guard for the ticket workflow.
# Requires project build/test/install commands that run INSIDE a workflow worktree
# (ROOT/.worktrees/...) to go through the sandbox wrapper (wf-exec / sandbox-exec).
# Defense-in-depth behind the agent instructions — and it FAILS OPEN: on any parse
# uncertainty it allows the command, so it can never brick the shell.

input=$(cat 2>/dev/null) || exit 0
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
[ -z "$cmd" ] && exit 0

# Only govern commands operating inside a workflow worktree.
case "$cmd" in
  *"/.worktrees/"*) : ;;
  *) exit 0 ;;
esac

# Already sandboxed → allow.
case "$cmd" in
  *wf-exec*|*sandbox-exec*) exit 0 ;;
esac

# Risky execution patterns: package managers, test runners, build tools, interpreters.
# git/gh are intentionally NOT listed — they need network and run unsandboxed.
if printf '%s' "$cmd" | grep -Eq '(^|[ &|;(`$])(npm|pnpm|yarn|bun|npx|node|deno|python|python3|pip|pip3|pytest|tox|jest|vitest|mocha|go|cargo|make|cmake|mvn|gradle|bundle|rake|composer|dotnet|ruby|rails|flutter|dart)([ ]|$)'; then
  echo "Blocked by workflow sandbox guard: run project build/test/install commands through the sandbox so they cannot exfiltrate or read credentials. Wrap with: $HOME/.claude/bin/wf-exec <command>" >&2
  exit 2
fi

exit 0
