#!/usr/bin/env bash
# Deploy htma.mobile to GitHub Pages via the gh-pages branch.
#
# Requires: gh auth login -h github.com   (see README)
set -euo pipefail

cd "$(dirname "$0")"

REPO="lucasmcducas/htma_mobile_site"
BRANCH="gh-pages"

if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh is not authenticated."
  echo "  run:  gh auth login -h github.com"
  echo "  then: gh auth setup-git"
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: uncommitted changes. Commit them first."
  git status --short
  exit 1
fi

echo "→ publishing $(git rev-parse --short HEAD) to $BRANCH"

# GitHub Pages serves the branch root, so only the site files go across.
git subtree push --prefix=. origin "$BRANCH" 2>/dev/null \
  || {
    # First run: branch does not exist yet.
    git checkout -q --orphan "$BRANCH"
    git rm -rq --cached . 2>/dev/null || true
    git add index.html README.md
    git commit -q -m "Deploy $(git rev-parse --short HEAD)"
    git push -q origin "$BRANCH"
    git checkout -q main
  }

echo "→ pushed. Live within ~1 minute at:"
echo "    https://lucasmcducas.github.io/htma_mobile_site/"
echo "    (then point the htma.mobile A record at GitHub Pages IPs)"