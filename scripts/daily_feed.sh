#!/usr/bin/env bash
# Daily openings feed for Career Route sign-up emails.
# Pulls open federal student listings from USAJOBS, matches them to Career Route jobs and places,
# and publishes openings.json to GitHub Pages. Runs from Windows Task Scheduler (task "Career Route
# daily feed"), which also runs it at the next logon when the computer was off at the scheduled time.
#
# Run by hand: bash scripts/daily_feed.sh   Log: ~/.local/state/careerroute-feed/feed.log
#
# Safety: a failed USAJOBS call stops the run and the published feed stays as it was. An empty result
# is never published, and listings are never closed because a search came back without them.
set -euo pipefail

SITE=/mnt/d/internfeed/major-to-paycheck
SHORTS=/mnt/d/internfeed/internfeed-shorts
[ -f "$SHORTS/.env" ] || SHORTS=/mnt/d/internfeed/internfeed-shorts/internfeed-shorts  # older nested layout
PY="$HOME/.venvs/careerroute-feed/bin/python"
LOG_DIR="$HOME/.local/state/careerroute-feed"
LOCK="$LOG_DIR/lock"
mkdir -p "$LOG_DIR"
exec >>"$LOG_DIR/feed.log" 2>&1
echo "=== $(date '+%F %T') start"

# One run at a time (a logon catch-up can overlap a manual run).
exec 9>"$LOCK"
flock -n 9 || { echo "another run is in progress, stopping"; exit 0; }

# Already published today? Then nothing to do (Task Scheduler can fire twice: logon catch-up and daily).
if [ "${1:-}" != "--force" ] && [ -f "$SITE/openings.json" ] \
   && grep -Eq "\"generated\": *\"$(date +%F)" "$SITE/openings.json"; then
  echo "already published today, stopping"; exit 0
fi

cd "$SHORTS"
set -a; . <(tr -d '\r' < .env); set +a
"$PY" -m shortsgen usajobs --out data/careerroute_usajobs.xlsx
"$PY" -m shortsgen feed --input data/careerroute_usajobs.xlsx \
  --route "$SITE/careerroute.json" --out output/feed/openings.json

COUNT=$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["count"])' output/feed/openings.json)
if [ "$COUNT" -eq 0 ]; then
  echo "feed has 0 listings, not publishing (the live feed stays as it was)"; exit 1
fi

cd "$SITE"
git pull --rebase --autostash -q
cp "$SHORTS/output/feed/openings.json" openings.json
git add openings.json
if git diff --cached --quiet; then
  echo "no change to publish"
else
  git commit -q -m "Openings feed $(date +%F): $COUNT open listings" -- openings.json
  git push -q
  echo "published $COUNT listings"
fi
echo "=== $(date '+%F %T') done"
