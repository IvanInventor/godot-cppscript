#!/bin/bash
# Helper to generate + commit to both dev branch and master
MASTER_DIR="$1"
if [ "$MASTER_DIR" == "" ]; then
	echo "Usage: "
	echo "\t$0" "<master_worktree_path>"
	exit 1
fi

if git diff --quiet; then
	echo "$(pwd): No changes"
fi

./generate.py "$MASTER_DIR" || exit 1

git diff --quiet  || git commit -a

REF_SHORT=$(git rev-parse @ | head -c8)

cd "$MASTER_DIR"
if git diff --quiet ; then
	echo "$(pwd): No changes"
	exit 1
else
	git commit -a -m "Sync with $REF_SHORT"
fi
