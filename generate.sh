#!/bin/bash
# Helper to generate + commit to both dev branch and master
MASTER_DIR="$1"
./generate.py "$MASTER_DIR" || exit 1
if ! git diff --cached --quiet; then
	echo "No changes"
	exit 0
fi

git commit -a || true

REF_SHORT=$(git rev-parse @ | head -c8)

cd "$MASTER_DIR"
git diff --cached --quiet || git commit -a -m "Sync with $REF_SHORT" || exit 1
