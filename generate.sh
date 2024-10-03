#!/bin/bash
# Helper to generate + commit to both dev branch and master
MASTER_DIR="$1"
./generate.py "$MASTER_DIR" || exit 1
git commit -a || exit 1

REF_SHORT=$(git rev-parse @ | head -c8)

cd "$MASTER_DIR"
git commit -a -m "Sync with $REF_SHORT" || exit 1
