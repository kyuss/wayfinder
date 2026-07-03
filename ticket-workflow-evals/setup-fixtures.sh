#!/bin/bash
# Initialize the eval fixtures as clean git repos.
# The published fixtures ship without a .git dir; this creates one with a
# neutral author so the workflow's git-history features work locally.
# Safe to re-run: it resets each fixture to a single "fixture baseline" commit.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

AUTHOR_NAME="Ticket Workflow Fixture"
AUTHOR_EMAIL="noreply@example.com"

for fx in "$HERE"/fixtures/*/; do
  [ -d "$fx" ] || continue
  rm -rf "$fx/.git"
  git -C "$fx" init -q -b main
  git -C "$fx" add -A
  git -C "$fx" \
    -c user.name="$AUTHOR_NAME" \
    -c user.email="$AUTHOR_EMAIL" \
    -c commit.gpgsign=false \
    commit -q -m "fixture baseline"
  echo "  initialized $(basename "$fx")"
done
echo "Fixtures ready."
