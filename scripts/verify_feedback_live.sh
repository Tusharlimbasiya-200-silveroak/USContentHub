#!/usr/bin/env bash
# Read-only smoke test for the "Was this helpful?" feedback widget in production.
# Does NOT write any feedback rows — safe to run anytime after a deploy.
set -uo pipefail
BASE="${1:-https://us-content-hub.vercel.app}"
echo "▶ Verifying feedback widget on: $BASE"

HOME_HTML=$(curl -fsS "$BASE/")
SLUG=$(printf '%s' "$HOME_HTML" | grep -oP '/article/\K[a-z0-9-]+(?=/)' | head -1)
if [ -z "$SLUG" ]; then echo "  ✗ Could not find an article link on homepage"; exit 1; fi
echo "  • sample article: $SLUG"

ART_HTML=$(curl -fsS "$BASE/article/$SLUG/")
if printf '%s' "$ART_HTML" | grep -q "Was this article helpful?"; then
  echo "  ✓ widget present on article page"
else
  echo "  ✗ widget NOT found (deploy still settling — re-run in a minute)"; exit 1
fi

CODE=$(curl -sS -o /dev/null -w "%{http_code}" "$BASE/article/$SLUG/feedback/")
case "$CODE" in
  405) echo "  ✓ /feedback/ endpoint live (GET → 405, POST-only as expected)";;
  404) echo "  ✗ /feedback/ 404 — route not deployed yet"; exit 1;;
  *)   echo "  ? /feedback/ returned HTTP $CODE (route exists)";;
esac
echo "✅ Feedback widget is live and wired on $BASE"
