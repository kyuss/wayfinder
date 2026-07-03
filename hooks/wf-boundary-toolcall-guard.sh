#!/bin/bash
# SubagentStop guard for the ticket-workflow boundary agents (wf-linear, wf-github).
# These agents exist ONLY to do real I/O against an external system. If one finishes
# having made zero tool calls, its answer was fabricated from context, not fetched —
# the exact failure that surfaces as `tool_uses: 0`. This blocks that finish and forces
# a real tool call (or an honest ERROR).
# Defense-in-depth behind the agent prompts — and it FAILS OPEN: on any parse/scope
# uncertainty it allows the stop, so it can never wedge a subagent.

input=$(cat 2>/dev/null) || exit 0

# Loop protection: if we already blocked once this turn, let it stop.
stop_active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false' 2>/dev/null) || exit 0
[ "$stop_active" = "true" ] && exit 0

# Scope to the boundary agents only — never govern reasoning/execution agents.
agent=$(printf '%s' "$input" | jq -r '.agent_type // empty' 2>/dev/null) || exit 0
case "$agent" in
  wf-linear|wf-github) : ;;
  *) exit 0 ;;
esac

# Need the transcript to judge; if unavailable, fail open.
transcript=$(printf '%s' "$input" | jq -r '.agent_transcript_path // empty' 2>/dev/null) || exit 0
{ [ -z "$transcript" ] || [ ! -f "$transcript" ]; } && exit 0

# Any tool_use block anywhere in the transcript means it actually called a tool → allow.
if grep -Eq '"type"[[:space:]]*:[[:space:]]*"tool_use"' "$transcript"; then
  exit 0
fi

# Zero tool calls → treat the answer as ungrounded and force a real attempt.
echo "Boundary-agent guard: '$agent' is finishing without having called any tool, so its answer is fabricated from context, not fetched from the external system. A real tool call is REQUIRED before answering. Make the call now; if the system is genuinely unreachable, return exactly 'ERROR: could not reach the external system' — never reconstruct data from memory." >&2
exit 2
