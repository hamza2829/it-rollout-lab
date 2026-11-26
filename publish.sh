#!/usr/bin/env bash
# One-time publish: repo, push, wait for CI. Needs git + gh (run `gh auth login` once).
set -euo pipefail
REPO=hamza2829/it-rollout-lab
export GIT_AUTHOR_NAME="Hamza Sohail" GIT_AUTHOR_EMAIL="hamzashiekh2829@gmail.com"
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME" GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
git init -b main && git add -A && git commit -m "Inventory, Ansible, PowerShell, rollout simulation, docs, CI"
gh repo create "$REPO" --public --source=. --push
sleep 15
RUN=$(gh run list -R $REPO -b main -L1 --json databaseId -q '.[0].databaseId')
gh run watch -R $REPO --exit-status "$RUN" | tail -n 20
