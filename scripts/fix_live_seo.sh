#!/usr/bin/env bash
#
# Fix critical SEO bugs on the LIVE per-site GitHub Pages repos:
#   1. Canonical/JSON-LD URLs point to a DEAD domain ({site}.github.io -> 404).
#      Rewrite to the real served URL: tusharlimbasiya-200-silveroak.github.io/{site}/
#      (covers .html, .xml, .json AND robots.txt Sitemap: lines)
#   2. "Usa" -> "USA" brand capitalization (news/travel/recipe sites).
#
# Uses YOUR existing git credentials. Run from anywhere.
# Safe to re-run (idempotent). Review the diff it prints before it pushes.
#
# BRANCH: GitHub Pages serves these repos from the `gh-pages` branch (see
# .github/workflows/deploy-sites.yml, which force-pushes there). This script
# patches and pushes gh-pages — NOT main.
#
# EMERGENCY FALLBACK ONLY. The normal/correct fix is to edit the committed
# `sites/<slug>/` HTML in this repo and push to main: deploy-sites.yml then
# force-pushes the corrected content to each live gh-pages. That is permanent
# and self-healing. Use this script only to patch live repos out-of-band when
# you can't wait for (or don't want to trigger) a full redeploy — note the next
# deploy-sites.yml run will overwrite gh-pages with whatever is in sites/.

set -euo pipefail
USER_GH="Tusharlimbasiya-200-silveroak"
WORK="${TMPDIR:-/tmp}/live-seo-fix"
SITES=(tech-gadget-hub health-wellness-daily smart-money-guide \
       usa-travel-explorer recipe-kitchen-usa usa-news-digest the-trading-blueprint)

# per-site brand capitalization fixes (site:bad:good); sites not listed get only the URL fix
declare -A BRAND=(
  [usa-news-digest]="Usa News Digest|USA News Digest"
  [usa-travel-explorer]="Usa Travel Explorer|USA Travel Explorer"
  [recipe-kitchen-usa]="Recipe Kitchen Usa|Recipe Kitchen USA"
)

rm -rf "$WORK"; mkdir -p "$WORK"; cd "$WORK"

for SITE in "${SITES[@]}"; do
  echo "============================================================"
  echo "  $SITE"
  echo "============================================================"
  git clone --quiet "https://github.com/${USER_GH}/${SITE}.git" "$SITE" || { echo "  ! clone failed, skipping"; continue; }
  cd "$SITE"
  # GitHub Pages serves from gh-pages — patch that branch, not the default.
  git checkout --quiet gh-pages 2>/dev/null || { echo "  ! no gh-pages branch, skipping"; cd ..; continue; }

  BAD="https://${SITE}.github.io/"
  GOOD="https://${USER_GH}.github.io/${SITE}/"
  brand="${BRAND[$SITE]:-}"

  python3 - "$BAD" "$GOOD" "$brand" <<'PY'
import sys, glob
bad, good, brand = sys.argv[1], sys.argv[2], sys.argv[3]
bsrc, bdst = (brand.split("|", 1) if brand else ("", ""))
changed = 0
for f in (glob.glob("**/*.html", recursive=True) + glob.glob("**/*.xml", recursive=True)
          + glob.glob("**/*.json", recursive=True) + glob.glob("**/*.txt", recursive=True)):
    s = open(f, encoding="utf-8").read(); o = s
    s = s.replace(bad, good)
    if bsrc:
        s = s.replace(bsrc, bdst)
    if s != o:
        open(f, "w", encoding="utf-8").write(s); changed += 1
print(f"  files changed: {changed}")
PY

  if [ -z "$(git status --porcelain)" ]; then
    echo "  already clean (nothing to fix)"; cd ..; continue
  fi
  git add -A
  git -c user.name="$USER_GH" -c user.email="bot@uscontenthub" \
      commit --quiet -m "fix(seo): canonical -> real domain; USA branding"
  echo "  pushing to gh-pages..."
  git push --quiet origin HEAD:gh-pages && echo "  ✓ pushed" || echo "  ! push failed (check auth / branch protection)"
  cd ..
done
echo ""
echo "Done. Verify in ~2 min:"
echo "  curl -sI https://${USER_GH}.github.io/usa-news-digest/ | grep last-modified"
