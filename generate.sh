#!/bin/bash
# Helper to generate + commit to both dev branch and master
MASTER_DIR="$1"
if [ "$MASTER_DIR" == "" ]; then
	echo "Usage: "
	echo "\t$0" "<master_worktree_path>"
	exit 1
fi

if git diff --cached --quiet; then
	echo "No changes"
	exit 0
fi

./generate.py "$MASTER_DIR" || exit 1

git commit -a || exit 1

REF_SHORT=$(git rev-parse @ | head -c8)

cd "$MASTER_DIR"
if git diff --cached --quiet ; then
	echo "Cannot commit to" "'$MASTER_DIR'" ": no changes"
	exit 1
else
	git commit -a -m "Sync with $REF_SHORT"
fi
